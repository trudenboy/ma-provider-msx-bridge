"""Queue ↔ MSX native playlist handshake."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from music_assistant_models.errors import InvalidProviderURI

from music_assistant.helpers.uri import parse_uri

if TYPE_CHECKING:
    from music_assistant_models.player import PlayerMedia

    from .player import MSXPlayer
    from .provider import MSXBridgeProvider

logger = logging.getLogger(__name__)

_prepare_locks: dict[str, asyncio.Lock] = {}


def _lock_for(player_id: str) -> asyncio.Lock:
    lock = _prepare_locks.get(player_id)
    if lock is None:
        lock = asyncio.Lock()
        _prepare_locks[player_id] = lock
    return lock


@dataclass(frozen=True, slots=True)
class PrepareFailure:
    """HTTP-shaped failure from preparing MSX audio."""

    status: int
    text: str


async def is_media_item_uri(uri: str) -> bool:
    """Check whether a URI names a non-builtin media item."""
    if "://" not in uri:
        return False
    try:
        _, provider_instance_id_or_domain, _ = await parse_uri(uri)
    except InvalidProviderURI:
        return False
    return provider_instance_id_or_domain != "builtin"


def find_uri_in_active_queue(
    mass: Any,
    player_id: str,
    uri: str,
    queue_item_id: str | None = None,
) -> tuple[str, str] | None:
    """Return the active queue and item IDs matching the request."""
    queue = mass.player_queues.get_active_queue(player_id)
    if queue is None:
        return None
    items = mass.player_queues.items(queue.queue_id, limit=queue.items)
    for item in items:
        if (
            item.media_item is not None
            and item.media_item.uri == uri
            and (queue_item_id is None or item.queue_item_id == queue_item_id)
        ):
            return queue.queue_id, item.queue_item_id
    return None


def current_media_matches_uri(
    mass: Any,
    player: MSXPlayer,
    track_uri: str,
    queue_item_id: str | None = None,
) -> bool:
    """Check whether current media matches the requested queue item."""
    media = player.current_media
    if not media or not media.source_id or not media.queue_item_id:
        return False
    if queue_item_id is not None and media.queue_item_id != queue_item_id:
        return False
    queue_item = mass.player_queues.get_item(media.source_id, media.queue_item_id)
    if queue_item and queue_item.media_item:
        return getattr(queue_item.media_item, "uri", None) == track_uri
    return False


def queue_items_to_tracks(queue_items: Any) -> list[Any]:
    """Adapt MA queue items into track-like objects for the playlist mapper."""
    tracks: list[Any] = []
    for qi in queue_items:
        mi = getattr(qi, "media_item", None)
        tracks.append(
            SimpleNamespace(
                name=getattr(mi, "name", None) or getattr(qi, "name", "") or "",
                uri=getattr(mi, "uri", None) or "",
                duration=getattr(mi, "duration", None) or getattr(qi, "duration", 0) or 0,
                artist_str=getattr(mi, "artist_str", "") if mi else "",
                image=getattr(qi, "image", None),
                queue_item_id=getattr(qi, "queue_item_id", None),
            )
        )
    return tracks


async def prepare_msx_audio(
    provider: MSXBridgeProvider,
    player: MSXPlayer,
    uri: str,
    *,
    from_playlist: bool,
    queue_item_id: str | None,
) -> PlayerMedia | PrepareFailure:
    """
    Resolve the PlayerMedia MSX should stream for this URI.

    Owns the enqueue vs reuse decision so MA-driven play and MSX-driven
    /msx/audio share one implementation.
    """
    provider.on_player_activity(player.player_id)
    async with _lock_for(player.player_id):
        return await _prepare_msx_audio_locked(
            provider,
            player,
            uri,
            from_playlist=from_playlist,
            queue_item_id=queue_item_id,
        )


async def _prepare_msx_audio_locked(
    provider: MSXBridgeProvider,
    player: MSXPlayer,
    uri: str,
    *,
    from_playlist: bool,
    queue_item_id: str | None,
) -> PlayerMedia | PrepareFailure:
    """Enqueue or reuse under the per-player lock."""
    queue_item = find_uri_in_active_queue(provider.mass, player.player_id, uri, queue_item_id)
    if queue_item is None and not await is_media_item_uri(uri):
        return PrepareFailure(400, "Invalid uri parameter")

    if from_playlist and current_media_matches_uri(provider.mass, player, uri, queue_item_id):
        logger.debug("Queue-driven: using current_media for %s", uri)
        media = player.current_media
        if media is None:
            return PrepareFailure(504, "Playback setup timeout")
        return media

    player.expect_new_media()
    if from_playlist:
        player._skip_ws_notify = True
    try:
        if queue_item is not None:
            await provider.mass.player_queues.play_index(*queue_item)
        else:
            await provider.mass.player_queues.play_media(player.player_id, uri)
    finally:
        if from_playlist:
            player._skip_ws_notify = False

    media = await player.wait_for_media(timeout=10.0)
    if not media:
        return PrepareFailure(504, "Playback setup timeout")
    if media.source_id:
        player.mark_queue_playback(media.source_id)
    return media
