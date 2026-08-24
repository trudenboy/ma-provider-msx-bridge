"""Audio pipeline: shared group stream plus the three serve modes."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from collections import deque
from collections.abc import AsyncIterator, Sequence
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlsplit, urlunsplit

from aiohttp import web
from music_assistant_models.enums import ContentType
from music_assistant_models.errors import MusicAssistantError
from music_assistant_models.media_items import AudioFormat

from music_assistant.controllers.streams.audio_processing import get_media_session_id
from music_assistant.controllers.streams.constants import (
    SINGLE_ITEM_READRATE,
    SINGLE_ITEM_READRATE_INITIAL_BURST,
)
from music_assistant.helpers.ffmpeg import get_ffmpeg_stream

from .constants import PRE_BUFFER_BYTES

if TYPE_CHECKING:
    from music_assistant_models.player import PlayerMedia

    from music_assistant.controllers.streams.audio_processing import AudioOutputPlan
    from music_assistant.helpers.dsp import ComplexFilter

    from .player import MSXPlayer
    from .provider import MSXBridgeProvider

logger = logging.getLogger(__name__)

READRATE_ARGS = [
    "-readrate",
    SINGLE_ITEM_READRATE,
    "-readrate_initial_burst",
    SINGLE_ITEM_READRATE_INITIAL_BURST,
]


class SharedGroupStream:
    """
    Shared audio stream for a player group.

    One ffmpeg process produces audio, multiple TV clients read from a shared buffer.
    Late joiners receive buffered data first (catch-up), then live chunks.
    """

    def __init__(self, group_id: str, media_uri: str) -> None:
        """Initialize shared stream for a group."""
        self.group_id = group_id
        self.media_uri = media_uri
        self.buffer: deque[bytes] = deque(maxlen=512)  # ~15s @ 40KB/s MP3
        self.subscribers: dict[str, asyncio.Queue[bytes | None]] = {}
        self.producer_task: asyncio.Task[None] | None = None
        self.started = asyncio.Event()
        self.finished = False
        self.producer_error: Exception | None = None
        self.output_plan: AudioOutputPlan | None = None
        self._lock = asyncio.Lock()
        self._total_bytes = 0
        self._start_time: float = 0

        logger.info(
            "[SharedStream:%s] Created for media_uri=%s",
            self.group_id,
            self.media_uri[:80] if self.media_uri else "N/A",
        )

    async def start(
        self,
        audio_chunks: AsyncIterator[bytes],
    ) -> None:
        """Start producing audio from the given chunk iterator."""
        logger.info(
            "[SharedStream:%s] Starting producer task",
            self.group_id,
        )
        self._start_time = time.monotonic()
        self.producer_task = asyncio.create_task(self._produce(audio_chunks))

    async def subscribe(self, player_id: str) -> AsyncIterator[bytes]:
        """
        Subscribe to stream, get buffered + live chunks.

        Yields:
            Audio chunks (bytes). First yields catch-up buffer, then live chunks.
        """
        q: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=512)

        bytes_sent = 0
        chunks_sent = 0

        try:
            try:
                await asyncio.wait_for(self.started.wait(), timeout=15.0)
            except TimeoutError:
                logger.error(
                    "[SharedStream:%s] Timeout waiting for stream start for %s",
                    self.group_id,
                    player_id,
                )
                raise

            if self.producer_error is not None:
                logger.error(
                    "[SharedStream:%s] Producer failed before subscriber %s could join: %s",
                    self.group_id,
                    player_id,
                    self.producer_error,
                )
                raise self.producer_error

            async with self._lock:
                buffer_snapshot = list(self.buffer)
                already_finished = self.finished
                self.subscribers[player_id] = q
                if already_finished:
                    q.put_nowait(None)
                subscriber_count = len(self.subscribers)

            logger.info(
                "[SharedStream:%s] Subscriber %s joined (total: %d)",
                self.group_id,
                player_id,
                subscriber_count,
            )

            buffer_bytes = sum(len(c) for c in buffer_snapshot)
            logger.debug(
                "[SharedStream:%s] Sending %d catch-up chunks (%d bytes) to %s",
                self.group_id,
                len(buffer_snapshot),
                buffer_bytes,
                player_id,
            )
            for chunk in buffer_snapshot:
                yield chunk
                bytes_sent += len(chunk)
                chunks_sent += 1

            while True:
                next_chunk = await q.get()
                if next_chunk is None:
                    logger.debug(
                        "[SharedStream:%s] EOF received for subscriber %s",
                        self.group_id,
                        player_id,
                    )
                    break
                yield next_chunk
                bytes_sent += len(next_chunk)
                chunks_sent += 1

        finally:
            async with self._lock:
                self.subscribers.pop(player_id, None)
                remaining = len(self.subscribers)

            logger.info(
                "[SharedStream:%s] Subscriber %s left after %d chunks, %d bytes (remaining: %d)",
                self.group_id,
                player_id,
                chunks_sent,
                bytes_sent,
                remaining,
            )

    async def stop(self) -> None:
        """Stop the stream and clean up."""
        logger.info(
            "[SharedStream:%s] Stopping (total: %d bytes)",
            self.group_id,
            self._total_bytes,
        )
        if self.producer_task and not self.producer_task.done():
            self.producer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.producer_task
        self.finished = True

    @property
    def subscriber_count(self) -> int:
        """Return current subscriber count."""
        return len(self.subscribers)

    async def _produce(self, audio_chunks: AsyncIterator[bytes]) -> None:
        """Read from ffmpeg and distribute to all subscribers."""
        try:
            chunk_count = 0
            async for chunk in audio_chunks:
                chunk_count += 1
                self._total_bytes += len(chunk)
                async with self._lock:
                    self.buffer.append(chunk)
                    for player_id, q in list(self.subscribers.items()):
                        try:
                            q.put_nowait(chunk)
                        except asyncio.QueueFull:
                            logger.warning(
                                "[SharedStream:%s] Queue full for subscriber %s, dropping chunk %d",
                                self.group_id,
                                player_id,
                                chunk_count,
                            )

                if not self.started.is_set():
                    self.started.set()
                    logger.debug(
                        "[SharedStream:%s] First chunk received, signaling started",
                        self.group_id,
                    )

            logger.info(
                "[SharedStream:%s] Producer finished: %d chunks, %d bytes, %.1fs",
                self.group_id,
                chunk_count,
                self._total_bytes,
                time.monotonic() - self._start_time,
            )
        except asyncio.CancelledError:
            logger.debug("[SharedStream:%s] Producer cancelled", self.group_id)
            raise
        except (MusicAssistantError, OSError, RuntimeError) as exc:
            logger.exception("[SharedStream:%s] Producer error", self.group_id)
            self.producer_error = exc
        finally:
            self.finished = True
            if not self.started.is_set():
                self.started.set()
                logger.debug(
                    "[SharedStream:%s] Producer completed without first chunk, signaling started",
                    self.group_id,
                )
            async with self._lock:
                for player_id, q in list(self.subscribers.items()):
                    await _queue_eof(q)
                    logger.debug(
                        "[SharedStream:%s] Sent EOF to subscriber %s",
                        self.group_id,
                        player_id,
                    )


class AudioPipeline:
    """Serve encoded audio for one request: redirect, shared, or independent."""

    def __init__(self, provider: MSXBridgeProvider) -> None:
        """Initialize the pipeline."""
        self.provider = provider
        self.active_stream_tasks: dict[str, set[asyncio.Task[None]]] = {}
        self.active_stream_transports: dict[str, set[Any]] = {}

    def cancel_streams_for_player(self, player_id: str) -> None:
        """Cancel stream tasks and abort connections for the given player."""
        tasks = self.active_stream_tasks.pop(player_id, set())
        transports = self.active_stream_transports.pop(player_id, set())
        for task in tasks:
            if not task.done():
                task.cancel()
        for transport in transports:
            with contextlib.suppress(OSError, RuntimeError):
                if transport and hasattr(transport, "abort"):
                    transport.abort()
        if tasks or transports:
            logger.debug(
                "Cancelled %d task(s), aborted %d transport(s) for player %s",
                len(tasks),
                len(transports),
                player_id,
            )

    async def serve(
        self,
        request: web.Request,
        player: MSXPlayer,
        media: Any,
        duration: int = 0,
    ) -> web.StreamResponse:
        """Serve this player's current media on this request."""
        player_id = player.player_id

        if self.provider.is_redirect_stream_mode():
            redirect_url = await self.provider.get_ma_stream_url(player_id, media)
            if redirect_url:
                redirect_url = rewrite_stream_host(request, redirect_url)
                logger.info(
                    "[StreamMode:redirect] Player %s -> MA Streamserver: %s",
                    player_id,
                    redirect_url,
                )
                raise web.HTTPFound(location=redirect_url)
            logger.warning(
                "[StreamMode:redirect] Failed to get MA URL for %s, "
                "falling back to independent mode",
                player_id,
            )

        effective_format = cast(
            "str",
            player.config.get_value("output_codec", player.output_format),
        )

        pcm_format, out_format, headers = build_audio_params(
            effective_format,
            duration,
        )

        group_id = self.provider.get_group_id_for_player(player)
        if group_id and self.provider.is_shared_stream_mode():
            logger.info(
                "[StreamMode:shared] Player %s in group %s, using shared stream",
                player_id,
                group_id,
            )
            return await self.serve_shared(
                request, player, media, group_id, pcm_format, out_format, headers
            )

        logger.debug(
            "[StreamMode:independent] Serving audio %s: format=%s, duration=%s",
            player_id,
            effective_format,
            duration,
        )
        return await self.serve_independent(request, player, media, pcm_format, out_format, headers)

    async def serve_shared(
        self,
        request: web.Request,
        player: MSXPlayer,
        media: Any,
        group_id: str,
        pcm_format: AudioFormat,
        out_format: AudioFormat,
        headers: dict[str, str],
    ) -> web.StreamResponse:
        """Serve audio from a shared group stream."""
        player_id = player.player_id
        media_uri = getattr(media, "uri", "") or str(media)

        existing_stream = self.provider.get_shared_stream(group_id)
        if existing_stream is not None and existing_stream.media_uri != media_uri:
            existing_stream = None
        is_leader = player_id == group_id

        if existing_stream is not None:
            logger.debug(
                "[SharedStream] Player %s subscribing to existing stream for group %s",
                player_id,
                group_id,
            )
            shared_stream = existing_stream
        elif is_leader:
            logger.info(
                "[SharedStream] Leader %s creating shared stream for group %s",
                player_id,
                group_id,
            )
            audio_source = self.provider.mass.streams.get_stream(
                media,
                pcm_format,
                force_flow_mode=False,
            )
            output_plan = self.provider.mass.streams.audio.get_player_output_plan(
                player_id,
                pcm_format,
                out_format,
                queue_id=getattr(media, "source_id", None),
                session_id=get_media_session_id(media),
                queue_item_id=getattr(media, "queue_item_id", None),
            )
            audio_chunks = get_ffmpeg_stream(
                audio_input=audio_source,
                input_format=pcm_format,
                output_format=out_format,
                filter_params=output_plan.filter_params,
                extra_input_args=READRATE_ARGS,
            )
            shared_stream = await self.provider.get_or_create_shared_stream(
                group_id, media_uri, audio_chunks
            )
            shared_stream.output_plan = output_plan
        else:
            logger.info(
                "[SharedStream] Member %s waiting for leader to create stream for group %s",
                player_id,
                group_id,
            )
            shared_stream = None
            for _ in range(30):
                await asyncio.sleep(0.1)
                shared_stream = self.provider.get_shared_stream(group_id)
                if shared_stream is not None and shared_stream.media_uri == media_uri:
                    break
                shared_stream = None
            if shared_stream is None:
                logger.warning(
                    "[SharedStream] Timeout waiting for leader stream, "
                    "falling back to independent for %s",
                    player_id,
                )
                return await self.serve_independent(
                    request, player, media, pcm_format, out_format, headers
                )

        if shared_stream is None:
            return await self.serve_independent(
                request, player, media, pcm_format, out_format, headers
            )

        queue_id = getattr(media, "source_id", None)
        session_id = get_media_session_id(media)
        if (
            shared_stream.output_plan is not None
            and queue_id is not None
            and session_id is not None
        ):
            self.provider.mass.streams.audio_processing.update_output(
                player_id,
                shared_stream.output_plan,
                queue_id=queue_id,
                session_id=session_id,
                queue_item_id=getattr(media, "queue_item_id", None),
            )

        response = web.StreamResponse(status=200, headers=headers)
        await response.prepare(request)

        total_bytes = 0
        try:
            async for chunk in shared_stream.subscribe(player_id):
                await response.write(chunk)
                total_bytes += len(chunk)
        except ConnectionResetError, BrokenPipeError, ConnectionAbortedError:
            logger.debug(
                "[SharedStream] Client %s disconnected after %d bytes",
                player_id,
                total_bytes,
            )
        except asyncio.CancelledError:
            logger.debug("[SharedStream] Stream cancelled for %s", player_id)
            raise

        logger.info(
            "[SharedStream] Player %s finished, wrote %d bytes",
            player_id,
            total_bytes,
        )
        return response

    async def serve_independent(
        self,
        request: web.Request,
        player: MSXPlayer,
        media: Any,
        pcm_format: AudioFormat,
        out_format: AudioFormat,
        headers: dict[str, str],
    ) -> web.StreamResponse:
        """Serve audio via independent ffmpeg stream."""
        player_id = player.player_id
        audio_source = self.provider.mass.streams.get_stream(
            media,
            pcm_format,
            force_flow_mode=False,
        )
        output_plan = self.provider.mass.streams.audio.get_player_output_plan(
            player_id,
            pcm_format,
            out_format,
            queue_id=getattr(media, "source_id", None),
            session_id=get_media_session_id(media),
            queue_item_id=getattr(media, "queue_item_id", None),
        )

        response = web.StreamResponse(status=200, headers=headers)
        stream_task: asyncio.Task[None] = asyncio.create_task(
            self.stream_with_prebuffer(
                request,
                response,
                player,
                headers,
                audio_source,
                pcm_format,
                out_format,
                output_plan.filter_params,
            )
        )
        transport = getattr(request, "transport", None)
        await self.run_stream_task(player_id, stream_task, transport)
        return response

    async def stream_with_prebuffer(
        self,
        request: web.Request,
        response: web.StreamResponse,
        player: MSXPlayer,
        headers: dict[str, str],
        audio_source: Any,
        pcm_format: AudioFormat,
        out_format: AudioFormat,
        filter_params: Sequence[str | ComplexFilter],
    ) -> None:
        """Pre-buffer audio chunks, then send HTTP headers and stream remaining data."""
        player_id = player.player_id
        chunk_queue: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=32)

        async def producer() -> None:
            try:
                async for chunk in get_ffmpeg_stream(
                    audio_input=audio_source,
                    input_format=pcm_format,
                    output_format=out_format,
                    filter_params=filter_params,
                    extra_input_args=READRATE_ARGS,
                ):
                    await chunk_queue.put(chunk)
            finally:
                await _queue_eof(chunk_queue)

        producer_task: asyncio.Task[None] | None = None
        total_bytes = 0
        try:
            producer_task = asyncio.create_task(producer())
            pre_buffer, ended = await _collect_prebuffer(chunk_queue)

            if not player.current_media and not pre_buffer:
                return

            await response.prepare(request)
            for buf_chunk in pre_buffer:
                await response.write(buf_chunk)
                total_bytes += len(buf_chunk)

            if ended:
                return

            while True:
                chunk = await chunk_queue.get()
                if chunk is None:
                    break
                await response.write(chunk)
                total_bytes += len(chunk)
        except ConnectionResetError, BrokenPipeError, ConnectionAbortedError:
            logger.debug("Client disconnected from stream %s", player_id)
        except asyncio.CancelledError:
            logger.debug("Stream cancelled for player %s", player_id)
            raise
        finally:
            if producer_task is not None:
                if not producer_task.done():
                    producer_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await producer_task
            content_length = headers.get("Content-Length")
            if content_length:
                logger.debug(
                    "Stream %s: wrote %d bytes, Content-Length=%s, diff=%d",
                    player_id,
                    total_bytes,
                    content_length,
                    total_bytes - int(content_length),
                )
            else:
                logger.debug("Stream %s finished: wrote %d bytes", player_id, total_bytes)

    async def run_stream_task(
        self,
        player_id: str,
        stream_task: asyncio.Task[None],
        transport: Any,
    ) -> None:
        """Run a stream task with registration and error handling."""
        self.register_stream(player_id, stream_task, transport)
        try:
            await stream_task
        except asyncio.CancelledError:
            raise
        except MusicAssistantError, OSError, RuntimeError:
            logger.exception("Stream error for player %s", player_id)
        finally:
            self.unregister_stream(player_id, stream_task, transport)

    def register_stream(self, player_id: str, task: asyncio.Task[None], transport: Any) -> None:
        """Register active stream task and transport for cancel on stop."""
        if player_id not in self.active_stream_tasks:
            self.active_stream_tasks[player_id] = set()
            self.active_stream_transports[player_id] = set()
        if task:
            self.active_stream_tasks[player_id].add(task)
        if transport:
            self.active_stream_transports[player_id].add(transport)

    def unregister_stream(self, player_id: str, task: asyncio.Task[None], transport: Any) -> None:
        """Unregister stream when done (from finally block)."""
        if player_id not in self.active_stream_tasks:
            return
        if task:
            self.active_stream_tasks[player_id].discard(task)
        if transport:
            self.active_stream_transports[player_id].discard(transport)
        if not self.active_stream_tasks[player_id]:
            del self.active_stream_tasks[player_id]
            del self.active_stream_transports[player_id]


async def _queue_eof(queue: asyncio.Queue[bytes | None]) -> None:
    """Enqueue the stream sentinel, waiting if the consumer is behind."""
    await queue.put(None)


def rewrite_stream_host(request: web.Request, url: str) -> str:
    """Point a stream URL at the host the client already uses to reach us."""
    client_host = request.url.host
    if not client_host:
        return url
    parts = urlsplit(url)
    if ":" in client_host:
        client_host = f"[{client_host}]"
    netloc = f"{client_host}:{parts.port}" if parts.port else client_host
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


async def _collect_prebuffer(
    chunk_queue: asyncio.Queue[bytes | None],
) -> tuple[list[bytes], bool]:
    """Collect chunks until PRE_BUFFER_BYTES or EOF. Returns (chunks, ended)."""
    pre_buffer: list[bytes] = []
    pre_buffer_size = 0
    while pre_buffer_size < PRE_BUFFER_BYTES:
        chunk = await chunk_queue.get()
        if chunk is None:
            return pre_buffer, True
        pre_buffer.append(chunk)
        pre_buffer_size += len(chunk)
    return pre_buffer, False


def build_audio_params(
    output_format_str: str, duration: int
) -> tuple[AudioFormat, AudioFormat, dict[str, str]]:
    """Build PCM input format, encoded output format, and HTTP headers."""
    pcm_format = AudioFormat(
        content_type=ContentType.PCM_S16LE,
        sample_rate=44100,
        bit_depth=16,
        channels=2,
    )
    content_type_map: dict[str, tuple[ContentType, str]] = {
        "mp3": (ContentType.MP3, "audio/mpeg"),
        "aac": (ContentType.AAC, "audio/aac"),
        "flac": (ContentType.FLAC, "audio/flac"),
    }
    codec, mime_type = content_type_map.get(output_format_str, (ContentType.MP3, "audio/mpeg"))
    out_format = AudioFormat(
        content_type=codec,
        sample_rate=44100,
        bit_depth=16,
        channels=2,
    )
    bitrate_map = {"mp3": 40_000, "aac": 32_000}
    bytes_per_sec = bitrate_map.get(output_format_str, 0)
    headers: dict[str, str] = {
        "Content-Type": mime_type,
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Accept-Ranges": "none",
    }
    if duration and bytes_per_sec:
        capped_duration = min(float(duration), 43200)
        headers["Content-Length"] = str(int(capped_duration * bytes_per_sec))
    return pcm_format, out_format, headers


def resolve_served_duration(mass: Any, media: PlayerMedia) -> int:
    """Return the length in seconds of the audio served for the given media."""
    duration = media.stream_duration or media.duration or 0
    if not duration and media.source_id and media.queue_item_id:
        queue_item = mass.player_queues.get_item(media.source_id, media.queue_item_id)
        if queue_item:
            if queue_item.media_item:
                duration = getattr(queue_item.media_item, "duration", None) or duration
            if not duration and queue_item.duration:
                duration = queue_item.duration
    return int(duration)
