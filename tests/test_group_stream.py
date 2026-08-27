"""Tests for SharedGroupStream."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from music_assistant_models.enums import ContentType
from music_assistant_models.media_items import AudioFormat

from music_assistant.providers.msx_bridge.audio_stream import AudioPipeline
from music_assistant.providers.msx_bridge.http_server import MSXHTTPServer
from music_assistant.providers.msx_bridge.player import MSXPlayer
from music_assistant.providers.msx_bridge.provider import SharedGroupStream

if TYPE_CHECKING:
    from music_assistant.providers.msx_bridge.provider import MSXBridgeProvider


async def _chunks(*data: bytes) -> AsyncIterator[bytes]:
    """Yield bytes chunks as an async iterator."""
    for chunk in data:
        yield chunk


async def _collect(stream: SharedGroupStream, player_id: str) -> list[bytes]:
    """Subscribe and collect all chunks into a list."""
    result = []
    async for chunk in stream.subscribe(player_id):
        result.append(chunk)
    return result


async def test_subscribe_receives_all_chunks() -> None:
    """Subscriber should receive every chunk produced."""
    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(_chunks(b"a", b"b", b"c"))
    result = await _collect(stream, "tv1")
    assert result == [b"a", b"b", b"c"]


async def test_late_joiner_after_finish_does_not_hang() -> None:
    """
    subscribe() called after producer has already finished must not block indefinitely.

    Regression test for: https://github.com/music-assistant/server/pull/3123#discussion_r2842897555
    """
    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(_chunks(b"x", b"y"))

    # Wait for the producer to fully finish before subscribing.
    assert stream.producer_task is not None
    await asyncio.wait_for(stream.producer_task, timeout=5.0)
    assert stream.finished is True

    # Late subscriber: must get catch-up data and exit cleanly (no hang).
    result = await asyncio.wait_for(_collect(stream, "late"), timeout=5.0)
    assert result == [b"x", b"y"]


async def test_late_joiner_with_empty_stream_does_not_hang() -> None:
    """Late joiner on a stream that produced zero chunks must also exit cleanly."""
    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(_chunks())  # no chunks

    assert stream.producer_task is not None
    await asyncio.wait_for(stream.producer_task, timeout=5.0)
    assert stream.finished is True

    result = await asyncio.wait_for(_collect(stream, "late"), timeout=5.0)
    assert result == []


async def test_concurrent_subscribers_receive_live_chunks() -> None:
    """Multiple subscribers joining before stream starts all receive all chunks."""
    stream = SharedGroupStream("g1", "uri://test")

    async def slow_source() -> AsyncIterator[bytes]:
        for i in range(3):
            await asyncio.sleep(0)
            yield bytes([i])

    await stream.start(slow_source())

    results = await asyncio.gather(
        _collect(stream, "tv1"),
        _collect(stream, "tv2"),
    )
    assert results[0] == results[1]
    assert len(results[0]) == 3


async def test_concurrent_replace_yields_single_stream(provider: MSXBridgeProvider) -> None:
    """
    Concurrent replacing get_or_create_shared_stream calls must yield ONE stream.

    Without serialization, both callers pass the "existing" check while the old
    producer is being awaited, each creates its own stream, and the loser's
    ffmpeg producer is orphaned — consuming audio with zero subscribers.
    """

    async def infinite_source() -> AsyncIterator[bytes]:
        while True:
            await asyncio.sleep(0.01)
            yield b"chunk"

    old = await provider.get_or_create_shared_stream("g1", "uri://old", infinite_source())
    try:
        results = await asyncio.gather(
            provider.get_or_create_shared_stream("g1", "uri://new", infinite_source()),
            provider.get_or_create_shared_stream("g1", "uri://new", infinite_source()),
        )
        assert results[0] is results[1]
        assert provider._shared_streams["g1"] is results[0]
    finally:
        await old.stop()
        for stream in {id(s): s for s in provider._shared_streams.values()}.values():
            await stream.stop()
        await asyncio.gather(
            *(s.stop() for s in results),
            return_exceptions=True,
        )


async def test_cancel_stops_subscription() -> None:
    """Cancelling a subscriber's task cleans up the subscriber registry."""

    async def infinite_source() -> AsyncIterator[bytes]:
        while True:
            await asyncio.sleep(0.01)
            yield b"chunk"

    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(infinite_source())

    task = asyncio.create_task(_collect(stream, "tv1"))
    await asyncio.sleep(0.05)  # let subscriber register and receive some chunks
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    # After cancel, subscriber should be cleaned up
    assert "tv1" not in stream.subscribers

    # Cleanup
    if stream.producer_task:
        stream.producer_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await stream.producer_task


async def test_shared_stream_paces_output(provider: MSXBridgeProvider, mass_mock: Mock) -> None:
    """The shared group encoder carries the same pacing ceiling as the per-player one."""
    server = MSXHTTPServer(provider, 0)
    player = MagicMock(spec=MSXPlayer)
    player.player_id = "msx_leader"
    media = Mock(source_id=None, queue_item_id=None)

    mass_mock.streams = Mock()
    mass_mock.streams.get_stream = Mock(return_value=_chunks(b"pcm"))
    mass_mock.streams.resolve_stream_url = AsyncMock(side_effect=RuntimeError("no session"))
    mass_mock.streams.audio.get_player_output_plan = Mock(return_value=Mock(filter_params=[]))
    provider.get_or_create_shared_stream = AsyncMock(  # type: ignore[method-assign]
        side_effect=RuntimeError("stop here")
    )

    pcm = AudioFormat(content_type=ContentType.PCM_S16LE)
    out = AudioFormat(content_type=ContentType.MP3)
    with (
        patch(
            "music_assistant.providers.msx_bridge.audio_stream.get_ffmpeg_stream",
            return_value=_chunks(b"encoded"),
        ) as ffmpeg_mock,
        pytest.raises(RuntimeError),
    ):
        # leader path: player_id == group_id
        await server._serve_shared_stream(Mock(), player, media, "msx_leader", pcm, out, {})

    extra_args = ffmpeg_mock.call_args.kwargs["extra_input_args"]
    assert "-readrate" in extra_args
    assert "-readrate_initial_burst" in extra_args


async def _boom_after(chunk: bytes) -> AsyncIterator[bytes]:
    """Yield one chunk, then fail with an unexpected error."""
    yield chunk
    raise ValueError("producer boom")


async def test_stop_retrieves_already_failed_producer() -> None:
    """stop() must await a producer that already failed so the exception is not lost."""
    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(_boom_after(b"x"))
    assert stream.producer_task is not None
    await asyncio.wait({stream.producer_task}, timeout=5.0)
    assert stream.producer_task.done()

    await stream.stop()

    assert isinstance(stream.producer_error, ValueError)
    assert "producer boom" in str(stream.producer_error)


async def test_unexpected_producer_failure_is_recorded_immediately() -> None:
    """A producer crash outside the expected-error handler must be recorded without stop()."""
    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(_boom_after(b"x"))
    assert stream.producer_task is not None
    await asyncio.wait({stream.producer_task}, timeout=5.0)
    assert stream.producer_task.done()
    assert isinstance(stream.producer_error, ValueError)
    assert "producer boom" in str(stream.producer_error)


async def test_serve_shared_registers_stream_so_stop_can_cancel(
    provider: MSXBridgeProvider,
) -> None:
    """A shared-stream HTTP response must be cancellable via cancel_streams_for_player()."""
    pipeline = AudioPipeline(provider)
    player = MagicMock(spec=MSXPlayer)
    player.player_id = "msx_tv"
    media = Mock(uri="library://track/1", source_id=None, queue_item_id="")
    hanging = asyncio.Event()
    subscribed = asyncio.Event()

    async def hanging_subscribe(_player_id: str) -> AsyncIterator[bytes]:
        subscribed.set()
        await hanging.wait()
        yield b"x"

    stream = SharedGroupStream("msx_tv", "library://track/1", session_id="")
    stream.subscribe = hanging_subscribe  # type: ignore[assignment]
    provider.get_shared_stream = Mock(return_value=stream)  # type: ignore[method-assign]

    request = Mock()
    request.transport = Mock()
    pcm = AudioFormat(content_type=ContentType.PCM_S16LE)
    out = AudioFormat(content_type=ContentType.MP3)

    with patch("music_assistant.providers.msx_bridge.audio_stream.web.StreamResponse") as resp_cls:
        response = AsyncMock()
        resp_cls.return_value = response
        with patch(
            "music_assistant.providers.msx_bridge.audio_stream.get_media_session_id",
            return_value="",
        ):
            task = asyncio.create_task(
                pipeline.serve_shared(request, player, media, "msx_tv", pcm, out, {})
            )
            await asyncio.wait_for(subscribed.wait(), timeout=2.0)
            assert "msx_tv" in pipeline.active_stream_tasks
            pipeline.cancel_streams_for_player("msx_tv")
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=2.0)
            assert "msx_tv" not in pipeline.active_stream_tasks
