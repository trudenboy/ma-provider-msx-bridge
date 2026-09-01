"""MSX Bridge Player Provider implementation."""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import hmac
import logging
import secrets
import time
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, cast

from music_assistant_models.config_entries import ConfigEntry, ConfigValueOption
from music_assistant_models.enums import ConfigEntryType, ContentType
from music_assistant_models.errors import MusicAssistantError

from music_assistant.models.player_provider import PlayerProvider

from .audio_stream import SharedGroupStream

__all__ = ["MSXBridgeProvider", "SharedGroupStream"]
from .constants import (
    CONF_ENABLE_GROUPING,
    CONF_GROUP_STREAM_MODE,
    CONF_HTTP_PORT,
    CONF_OUTPUT_FORMAT,
    CONF_PLAYER_IDLE_TIMEOUT,
    CONF_SHOW_STOP_NOTIFICATION,
    DEFAULT_ENABLE_GROUPING,
    DEFAULT_GROUP_STREAM_MODE,
    DEFAULT_HTTP_PORT,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PLAYER_IDLE_TIMEOUT,
    DEFAULT_SHOW_STOP_NOTIFICATION,
    GROUP_STREAM_MODE_INDEPENDENT,
    GROUP_STREAM_MODE_REDIRECT,
    GROUP_STREAM_MODE_SHARED,
    MSX_PLAYER_ID_PREFIX,
)
from .http_server import MSXHTTPServer
from .player import MSXPlayer

if TYPE_CHECKING:
    from music_assistant.controllers.streams.audio_processing import AudioOutputPlan

logger = logging.getLogger(__name__)


class MSXBridgeProvider(PlayerProvider):
    """Player Provider that bridges Music Assistant to Smart TVs via MSX."""

    http_server: MSXHTTPServer | None = None
    grouping_enabled: bool = True
    group_stream_mode: str = DEFAULT_GROUP_STREAM_MODE
    _player_last_activity: dict[str, float]
    _pending_unregisters: dict[str, asyncio.Event]
    _stream_token_secret: bytes
    _timeout_task: asyncio.Task[None] | None = None
    _owner_username: str | None = None
    _shared_streams: dict[str, SharedGroupStream]  # group_id -> SharedGroupStream
    _shared_stream_lock: asyncio.Lock
    _background_tasks: set[asyncio.Task[None]]  # fire-and-forget tasks (unregister, stream stop)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the provider."""
        super().__init__(*args, **kwargs)
        self._player_last_activity = {}
        self._pending_unregisters = {}
        # one secret per provider instance; the per-player tokens derive from it
        self._stream_token_secret = secrets.token_bytes(32)
        self._shared_streams = {}
        self._shared_stream_lock = asyncio.Lock()
        self._background_tasks = set()

    async def get_config_entries(self) -> tuple[ConfigEntry, ...]:
        """Return Config entries to configure this provider."""
        return (
            ConfigEntry(
                key=CONF_HTTP_PORT,
                type=ConfigEntryType.INTEGER,
                required=True,
                default_value=str(DEFAULT_HTTP_PORT),
            ),
            ConfigEntry(
                key=CONF_OUTPUT_FORMAT,
                type=ConfigEntryType.STRING,
                required=True,
                default_value=DEFAULT_OUTPUT_FORMAT,
            ),
            ConfigEntry(
                key=CONF_PLAYER_IDLE_TIMEOUT,
                type=ConfigEntryType.INTEGER,
                required=False,
                default_value=str(DEFAULT_PLAYER_IDLE_TIMEOUT),
            ),
            ConfigEntry(
                key=CONF_SHOW_STOP_NOTIFICATION,
                type=ConfigEntryType.BOOLEAN,
                required=False,
                default_value=DEFAULT_SHOW_STOP_NOTIFICATION,
            ),
            ConfigEntry(
                key=CONF_ENABLE_GROUPING,
                type=ConfigEntryType.BOOLEAN,
                required=False,
                default_value=DEFAULT_ENABLE_GROUPING,
            ),
            ConfigEntry(
                key=CONF_GROUP_STREAM_MODE,
                type=ConfigEntryType.STRING,
                required=False,
                default_value=DEFAULT_GROUP_STREAM_MODE,
                options=[
                    ConfigValueOption(
                        GROUP_STREAM_MODE_INDEPENDENT,
                    ),
                    ConfigValueOption(
                        GROUP_STREAM_MODE_SHARED,
                    ),
                    ConfigValueOption(
                        GROUP_STREAM_MODE_REDIRECT,
                    ),
                ],
            ),
        )

    async def handle_async_init(self) -> None:
        """Handle async initialization — start embedded HTTP server."""
        raw_port = cast("int", self.config.get_value(CONF_HTTP_PORT, DEFAULT_HTTP_PORT))
        port = max(1, min(65535, int(raw_port)))
        self.grouping_enabled = bool(
            self.config.get_value(CONF_ENABLE_GROUPING, DEFAULT_ENABLE_GROUPING)
        )
        self.group_stream_mode = cast(
            "str",
            self.config.get_value(CONF_GROUP_STREAM_MODE, DEFAULT_GROUP_STREAM_MODE),
        )
        self.http_server = MSXHTTPServer(self, port)
        await self.http_server.start()
        self.logger.info(
            "MSX Bridge provider initialized, HTTP server on port %s, group_stream_mode=%s",
            port,
            self.group_stream_mode,
        )

    async def loaded_in_mass(self) -> None:
        """Start idle timeout task after provider is loaded."""
        await super().loaded_in_mass()
        self._timeout_task = self.mass.create_task(self._run_idle_timeout_loop())
        self.logger.info("MSX Bridge provider loaded — players register on demand")

    async def unload(self, is_removed: bool = False) -> None:
        """Handle unload — stop timeout task, HTTP server, then unregister players."""
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._timeout_task
            self._timeout_task = None

        # Cancel and await any in-flight unregister tasks before proceeding
        for task in list(self._background_tasks):
            if not task.done():
                task.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        # Cleanup shared streams
        await self.cleanup_shared_streams()

        if self.http_server:
            await self.http_server.stop()
        for player in list(self.players):
            try:
                self.logger.debug("Unloading player %s", player.display_name)
                await self.mass.players.unregister(player.player_id)
            except MusicAssistantError:
                self.logger.exception("Error unregistering player %s", player.player_id)
        self._player_last_activity.clear()
        self.logger.info("MSX Bridge provider unloaded")

    async def get_owner_username(self) -> str | None:
        """Resolve and cache the first enabled user's username for playlog attribution."""
        if self._owner_username is None:
            try:
                users = await self.mass.webserver.auth.list_users()
                for user in users:
                    if user.enabled and user.username:
                        self._owner_username = user.username
                        self.logger.debug("Resolved owner username: %s", self._owner_username)
                        break
            except MusicAssistantError as err:
                self.logger.warning("Could not resolve owner username: %s", err)
        return self._owner_username

    async def discover_players(self) -> None:
        """Discover players — MSX players are registered on demand when TVs connect."""

    async def get_or_register_player(
        self,
        player_id: str,
        display_name: str | None = None,
        ip_address: str | None = None,
    ) -> MSXPlayer | None:
        """
        Get or register an MSX player for the given player_id.

        Returns the player, or None if registration failed.
        """
        # Wait for any pending unregister to complete (race condition handling)
        if pending_event := self._pending_unregisters.get(player_id):
            self.logger.debug("Waiting for pending unregister of %s before registering", player_id)
            await pending_event.wait()
        existing = self.mass.players.get_player(player_id, raise_unavailable=False)
        if existing and isinstance(existing, MSXPlayer):
            if ip_address and not existing.device_info.ip_address:
                existing.device_info.ip_address = ip_address
            self.on_player_activity(player_id)
            return existing
        output_format = cast(
            "str", self.config.get_value(CONF_OUTPUT_FORMAT, DEFAULT_OUTPUT_FORMAT)
        )
        name = display_name or self.player_display_name(player_id)
        player = MSXPlayer(
            provider=self,
            player_id=player_id,
            name=name,
            output_format=output_format,
            grouping_enabled=self.grouping_enabled,
            ip_address=ip_address,
        )
        await self.mass.players.register(player)
        self._player_last_activity[player_id] = time.monotonic()
        self.logger.info("Registered MSX player: %s (%s)", name, player_id)
        return player

    def on_player_activity(self, player_id: str) -> None:
        """Record activity for a player (extends idle timeout)."""
        # Monotonic: a wall-clock NTP step must not age players past the cutoff
        self._player_last_activity[player_id] = time.monotonic()

    def on_player_disabled(self, player_id: str) -> None:
        """
        Handle player disabled: do not unregister (base would unregister).

        MSX players are registered on demand; unregister on disable would remove them
        from the list. On enable, discovery is empty so the player would not come back
        until the TV reconnects. We keep the player registered but disabled so it stays
        visible in the list when re-enabled.

        Still stop playback on TV by broadcasting stop and cancelling streams.
        """
        if self.http_server:
            self.http_server.broadcast_stop(player_id)
            self.http_server.cancel_streams_for_player(player_id)
        # Do NOT call super() — base PlayerProvider unregisters the player here.

    def on_player_enabled(self, player_id: str) -> None:
        """Handle player enabled: no-op, player already registered."""
        # Player was never unregistered (see on_player_disabled), so nothing to do.

    async def remove_player(self, player_id: str) -> None:
        """
        Remove (delete) a player from this provider.

        Called when user chooses to remove the player from MA.
        This fully unregisters the player. It will reappear if the TV reconnects.
        """
        if self.http_server:
            self.http_server.broadcast_stop(player_id)
            self.http_server.cancel_streams_for_player(player_id)
        await self._handle_player_unregister(player_id)
        self.logger.info("Player %s removed by user", player_id)

    def notify_play_started(
        self,
        player_id: str,
        *,
        title: str | None = None,
        artist: str | None = None,
        image_url: str | None = None,
        duration: int | None = None,
        next_action: str | None = None,
        prev_action: str | None = None,
    ) -> None:
        """Notify WebSocket clients that playback started (for MA -> MSX push)."""
        if self.http_server:
            self.http_server.broadcast_play(
                player_id,
                title=title,
                artist=artist,
                image_url=image_url,
                duration=duration,
                next_action=next_action,
                prev_action=prev_action,
            )

    def notify_play_playlist(
        self,
        player_id: str,
        start_index: int = 0,
        queue_id: str | None = None,
    ) -> None:
        """Notify WebSocket clients to play an MSX native playlist from the MA queue."""
        if self.http_server:
            qid = queue_id or player_id
            url = f"/msx/queue-playlist/{player_id}.json?start={start_index}&queue_id={qid}"
            self.http_server.broadcast_playlist(player_id, url)

    def notify_goto_index(self, player_id: str, index: int) -> None:
        """Notify WebSocket clients to jump to a specific playlist index."""
        if self.http_server:
            self.http_server.broadcast_goto_index(player_id, index)

    def notify_play_paused(self, player_id: str) -> None:
        """Notify WebSocket clients that playback is paused (MA pause -> MSX)."""
        if self.http_server:
            self.http_server.broadcast_pause(player_id)

    def notify_play_resumed(self, player_id: str) -> None:
        """Notify WebSocket clients that playback resumed (MA resume -> MSX)."""
        if self.http_server:
            self.http_server.broadcast_resume(player_id)

    def notify_play_stopped(self, player_id: str) -> None:
        """
        Notify WebSocket clients that playback stopped (MA stop -> MSX).

        Sends broadcast_stop + cancel_streams twice — same as Disable flow, which
        stops playback on MSX instantly (vs single signal with ~30s delay).
        """
        server = self.http_server
        if not server:
            return

        def _send() -> None:
            server.broadcast_stop(player_id)
            server.cancel_streams_for_player(player_id)

        _send()
        _send()

    def notify_seek(self, player_id: str, position_seconds: int) -> None:
        """Notify WebSocket clients to seek to position (MA seek -> MSX)."""
        if self.http_server:
            self.http_server.broadcast_seek(player_id, position_seconds)

    # --- Group Stream Management ---

    def is_shared_stream_mode(self) -> bool:
        """Check if shared buffer stream mode is enabled."""
        return self.group_stream_mode == GROUP_STREAM_MODE_SHARED

    def is_redirect_stream_mode(self) -> bool:
        """
        Check if MA redirect stream mode is enabled.

        In redirect mode the TV is 302-redirected to the MA Streamserver
        (``resolve_stream_url``) instead of being served by the local
        proxy/ffmpeg pipeline. See also ``get_ma_stream_url()``.
        """
        return self.group_stream_mode == GROUP_STREAM_MODE_REDIRECT

    def get_stream_token(self, player_id: str) -> str:
        """
        Return the token that authorizes the audio routes for the given player.

        Derived rather than stored, so a caller cannot grow provider state by asking for
        tokens under new player ids. It stays the same for the provider's lifetime: an
        idle TV is unregistered after the configured timeout, and changing the token there
        would strand the URLs a long-running TV session has already cached.

        :param player_id: The player to build an audio URL for.
        """
        digest = hmac.new(self._stream_token_secret, player_id.encode(), hashlib.sha256)
        return digest.hexdigest()[:32]

    def get_group_id_for_player(self, player: MSXPlayer) -> str | None:
        """
        Get group ID if player is in a group (as leader or member).

        Returns:
            group_id if player is grouped, None if solo player.
        """
        # If player is synced to another (member), use leader's ID as group
        if player.synced_to:
            logger.debug(
                "[GroupStream] Player %s is member of group %s",
                player.player_id,
                player.synced_to,
            )
            return player.synced_to

        # If player has group members (is leader), use own ID as group
        if player.group_members and len(player.group_members) > 1:
            logger.debug(
                "[GroupStream] Player %s is leader of group with %d members",
                player.player_id,
                len(player.group_members),
            )
            return player.player_id

        # Solo player
        return None

    async def get_or_create_shared_stream(
        self,
        group_id: str,
        media_uri: str,
        audio_chunks: AsyncIterator[bytes],
        session_id: str = "",
        content_type: ContentType | None = None,
        output_plan: AudioOutputPlan | None = None,
    ) -> SharedGroupStream:
        """
        Get existing shared stream or create new one for the group.

        :param group_id: ID of the group (leader's player_id).
        :param media_uri: URI of the media being streamed.
        :param audio_chunks: Async iterator yielding encoded audio chunks.
        :param session_id: Per-playback identity so restarts are not reused.
        :param content_type: Encoded codec of this producer, if known.
        :param output_plan: Filters used to encode this producer.
        """
        # Serialize check-and-create: without the lock, two concurrent callers
        # replacing an old stream both pass the "existing" check while awaiting
        # existing.stop(), creating two producers — one orphaned.
        async with self._shared_stream_lock:
            existing = self._shared_streams.get(group_id)

            # Reuse existing if same media and not finished
            if (
                existing
                and not existing.finished
                and existing.media_uri == media_uri
                and existing.session_id == session_id
                and (
                    content_type is None
                    or existing.content_type is None
                    or existing.content_type == content_type
                )
                and (
                    output_plan is None
                    or (
                        existing.output_plan is not None
                        and existing.output_plan.filter_params == output_plan.filter_params
                    )
                )
            ):
                logger.info(
                    "[GroupStream] Reusing existing shared stream for group %s (subscribers: %d)",
                    group_id,
                    existing.subscriber_count,
                )
                return existing

            # Clean up old stream if exists
            if existing:
                logger.info(
                    "[GroupStream] Replacing old shared stream for group %s "
                    "(old_uri=%s, new_uri=%s)",
                    group_id,
                    existing.media_uri[:50] if existing.media_uri else "N/A",
                    media_uri[:50] if media_uri else "N/A",
                )
                await existing.stop()

            # Create new shared stream
            logger.info(
                "[GroupStream] Creating new shared stream for group %s, uri=%s",
                group_id,
                media_uri[:80] if media_uri else "N/A",
            )
            stream = SharedGroupStream(group_id, media_uri, session_id, content_type=content_type)
            stream.output_plan = output_plan
            await stream.start(audio_chunks)
            self._shared_streams[group_id] = stream

            return stream

    def get_shared_stream(self, group_id: str) -> SharedGroupStream | None:
        """Return the live shared stream for a group, if one is running."""
        stream = self._shared_streams.get(group_id)
        if stream is None or stream.finished:
            return None
        return stream

    def remove_shared_stream(self, group_id: str) -> None:
        """Remove and cleanup shared stream for a group."""
        if stream := self._shared_streams.pop(group_id, None):
            logger.info("[GroupStream] Removed shared stream for group %s", group_id)
            task = self.mass.create_task(stream.stop())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

    async def get_ma_stream_url(self, player_id: str, media: Any) -> str | None:
        """
        Resolve the direct MA Streamserver URL for the given media.

        Used by redirect stream mode: the TV fetches audio straight from the
        MA Streamserver, which applies the player's own codec config and DSP —
        no local proxy/ffmpeg involved.

        :param player_id: The MSX player requesting the stream.
        :param media: PlayerMedia to resolve the stream URL for.
        :return: Direct URL to the MA Streamserver, or None when resolution
            fails (the caller falls back to the local proxy pipeline).
        """
        if not media:
            logger.debug("[MARedirect] No media provided")
            return None
        try:
            stream_url: str = await self.mass.streams.resolve_stream_url(player_id, media)
        except MusicAssistantError as err:
            logger.warning("[MARedirect] Failed to resolve MA stream URL: %s", err, exc_info=True)
            return None
        # MA returns a flow URL (continuous whole-queue stream) when e.g. crossfade
        # is enabled and the player lacks gapless support. That breaks the MSX
        # per-track model (progress display, auto-advance re-enqueue), so serve
        # such tracks through the local per-track proxy instead.
        if "/flow/" in stream_url:
            logger.debug(
                "[MARedirect] Flow-mode URL not usable for MSX per-track playback, "
                "falling back to proxy: %s",
                stream_url,
            )
            return None
        logger.debug("[MARedirect] Resolved MA stream URL: %s", stream_url)
        return stream_url

    async def cleanup_shared_streams(self) -> None:
        """Cleanup all shared streams (called on unload)."""
        for group_id, stream in list(self._shared_streams.items()):
            logger.debug("[GroupStream] Cleaning up stream for group %s", group_id)
            await stream.stop()
        self._shared_streams.clear()

    def player_display_name(
        self, player_id: str, prefix_label: str = "MSX TV", remote_ip: str | None = None
    ) -> str:
        """Build a unique display name from player_id for the MA UI."""
        prefix = MSX_PLAYER_ID_PREFIX
        suffix = player_id.removeprefix(prefix)
        if not suffix:
            return prefix_label
        # IP-based: msx_192_168_10_15 → "MSX TV (192.168.10.15)"
        if "_" in suffix:
            parts = suffix.split("_")
            if all(p.isdigit() for p in parts):
                return f"{prefix_label} ({'.'.join(parts)})"
        # UUID-based: msx_msx_bc93ce1d_491d_4d95_9430_2fbeabb5ce1b → "MSX TV (bc93)"
        # Show only first 4 chars of UUID for readability, plus IP if available
        if suffix.startswith("msx_") and len(suffix) > 12:
            uuid_part = suffix[4:8]  # First 4 chars after "msx_"
            if remote_ip:
                return f"{prefix_label} ({uuid_part}) [{remote_ip}]"
            return f"{prefix_label} ({uuid_part})"
        # Fallback: truncate long suffixes
        if len(suffix) > 12:
            if remote_ip:
                return f"{prefix_label} ({suffix[:8]}...) [{remote_ip}]"
            return f"{prefix_label} ({suffix[:8]}...)"
        if remote_ip:
            return f"{prefix_label} ({suffix}) [{remote_ip}]"
        return f"{prefix_label} ({suffix})"

    async def _handle_player_unregister(self, player_id: str) -> None:
        """Unregister a player with race-condition handling."""
        self.logger.debug("Unregistering MSX player %s", player_id)
        unregister_event = asyncio.Event()
        self._pending_unregisters[player_id] = unregister_event
        try:
            await self.mass.players.unregister(player_id)
        finally:
            self._pending_unregisters.pop(player_id, None)
            self._player_last_activity.pop(player_id, None)
            unregister_event.set()

    async def _run_idle_timeout_loop(self) -> None:
        """Background task: unregister players idle longer than configured timeout."""
        timeout_minutes = max(
            1,
            min(
                1440,
                int(
                    cast(
                        "int",
                        self.config.get_value(
                            CONF_PLAYER_IDLE_TIMEOUT, DEFAULT_PLAYER_IDLE_TIMEOUT
                        ),
                    )
                ),
            ),
        )
        interval_seconds = 60
        while not self.mass.closing:
            try:
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            now = time.monotonic()
            cutoff = now - (timeout_minutes * 60)
            for player in list(self.players):
                if not isinstance(player, MSXPlayer):
                    continue
                last = self._player_last_activity.get(player.player_id, 0)
                if last > 0 and last < cutoff:
                    self.logger.info(
                        "Unregistering idle MSX player %s (no activity for %d min)",
                        player.player_id,
                        timeout_minutes,
                    )
                    task = self.mass.create_task(self._handle_player_unregister(player.player_id))
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
