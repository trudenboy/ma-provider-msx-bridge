"""Tests for SharedGroupStream."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from music_assistant_models.enums import ContentType
from music_assistant_models.media_items import AudioFormat

from music_assistant.providers.msx_bridge.audio_stream import READRATE_ARGS, AudioPipeline
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


async def test_concurrent_leaders_do_not_relabel_an_incompatible_stream(
    provider: MSXBridgeProvider,
) -> None:
    """A reused producer must retain the output plan that encoded its bytes."""
    first_plan = Mock(filter_params=["pan=mono|c0=c0"])
    second_plan = Mock(filter_params=["pan=mono|c0=c1"])

    first, second = await asyncio.gather(
        provider.get_or_create_shared_stream(
            "g1",
            "uri://same",
            _chunks(b"first"),
            session_id="session",
            content_type=ContentType.MP3,
            output_plan=first_plan,
        ),
        provider.get_or_create_shared_stream(
            "g1",
            "uri://same",
            _chunks(b"second"),
            session_id="session",
            content_type=ContentType.MP3,
            output_plan=second_plan,
        ),
    )

    assert first is not second
    assert first.output_plan is first_plan
    assert second.output_plan is second_plan
    assert provider._shared_streams["g1"] is second
    await asyncio.gather(first.stop(), second.stop())


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


async def test_resubscribe_same_player_ends_prior_without_detaching_new() -> None:
    """A reconnect must EOF the old subscription and not pop the replacement."""

    async def live() -> AsyncIterator[bytes]:
        while True:
            yield b"x"
            await asyncio.sleep(0.01)

    stream = SharedGroupStream("g1", "uri://test")
    await stream.start(live())
    try:
        first_done = asyncio.Event()

        async def first() -> None:
            try:
                async for _chunk in stream.subscribe("tv1"):
                    pass
            finally:
                first_done.set()

        first_task = asyncio.create_task(first())
        await asyncio.sleep(0.05)
        assert "tv1" in stream.subscribers

        second_task = asyncio.create_task(_collect(stream, "tv1"))
        await asyncio.wait_for(first_done.wait(), timeout=2.0)
        assert first_task.done()
        await asyncio.sleep(0.05)
        assert "tv1" in stream.subscribers

        second_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await second_task
        assert "tv1" not in stream.subscribers
    finally:
        await stream.stop()


async def test_resubscribe_replaces_audio_with_eof_when_prior_queue_is_full() -> None:
    """A reconnect must terminate a replaced subscriber even at full backlog."""
    stream = SharedGroupStream("g1", "uri://test")
    stream.started.set()
    previous: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=2)
    previous.put_nowait(b"stale-1")
    previous.put_nowait(b"stale-2")
    stream.subscribers["tv1"] = previous

    replacement = stream.subscribe("tv1")
    next_chunk = asyncio.ensure_future(anext(replacement))
    while stream.subscribers.get("tv1") is previous:
        await asyncio.sleep(0)

    assert previous.get_nowait() == b"stale-2"
    assert previous.get_nowait() is None
    next_chunk.cancel()
    with pytest.raises(asyncio.CancelledError):
        await next_chunk


async def test_shared_stream_paces_output(provider: MSXBridgeProvider, mass_mock: Mock) -> None:
    """The shared group encoder carries the same pacing ceiling as the per-player one."""
    pipeline = AudioPipeline(provider)
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
        await pipeline.serve_shared(Mock(), player, media, "msx_leader", pcm, out, {})

    assert ffmpeg_mock.call_args.kwargs["extra_input_args"] == READRATE_ARGS


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
    stream.output_plan = Mock(filter_params=[])
    stream.subscribe = hanging_subscribe  # type: ignore[assignment]
    provider.get_shared_stream = Mock(return_value=stream)  # type: ignore[method-assign]
    cast("Any", provider.mass.streams.audio).get_player_output_plan = Mock(
        return_value=Mock(filter_params=[])
    )

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


async def test_serve_shared_falls_back_when_member_codec_differs(
    provider: MSXBridgeProvider,
) -> None:
    """A member whose codec differs from the shared encoder must not reuse those bytes."""
    stream = SharedGroupStream(
        "msx_leader", "library://track/1", session_id="", content_type=ContentType.MP3
    )
    provider._shared_streams["msx_leader"] = stream
    pipeline = AudioPipeline(provider)
    member = MagicMock(spec=MSXPlayer)
    member.player_id = "msx_member"
    media = Mock(uri="library://track/1", source_id=None, queue_item_id=None)
    pcm = AudioFormat(content_type=ContentType.PCM_S16LE)
    flac = AudioFormat(content_type=ContentType.FLAC)
    headers = {"Content-Type": "audio/flac"}
    independent = AsyncMock(return_value=Mock())
    with (
        patch(
            "music_assistant.providers.msx_bridge.audio_stream.get_media_session_id",
            return_value="",
        ),
        patch.object(pipeline, "serve_independent", independent),
        patch.object(pipeline, "_write_shared_response", AsyncMock()) as write_shared,
    ):
        await pipeline.serve_shared(Mock(), member, media, "msx_leader", pcm, flac, headers)

    independent.assert_awaited_once()
    write_shared.assert_not_awaited()


async def test_serve_shared_falls_back_when_member_filters_differ(
    provider: MSXBridgeProvider,
) -> None:
    """A member must not reuse audio encoded with another player's filters."""
    stream = SharedGroupStream(
        "msx_leader", "library://track/1", session_id="", content_type=ContentType.MP3
    )
    stream.output_plan = Mock(filter_params=["pan=mono|c0=c0"])
    provider._shared_streams["msx_leader"] = stream
    cast("Any", provider.mass.streams.audio).get_player_output_plan = Mock(
        return_value=Mock(filter_params=["pan=mono|c0=c1"])
    )
    pipeline = AudioPipeline(provider)
    member = MagicMock(spec=MSXPlayer)
    member.player_id = "msx_member"
    media = Mock(uri="library://track/1", source_id=None, queue_item_id=None)
    pcm = AudioFormat(content_type=ContentType.PCM_S16LE)
    mp3 = AudioFormat(content_type=ContentType.MP3)
    independent = AsyncMock(return_value=Mock())

    with (
        patch(
            "music_assistant.providers.msx_bridge.audio_stream.get_media_session_id",
            return_value="",
        ),
        patch.object(pipeline, "serve_independent", independent),
        patch.object(pipeline, "_write_shared_response", AsyncMock()) as write_shared,
    ):
        await pipeline.serve_shared(
            Mock(), member, media, "msx_leader", pcm, mp3, {"Content-Type": "audio/mpeg"}
        )

    independent.assert_awaited_once()
    write_shared.assert_not_awaited()


async def test_serve_shared_reuses_stream_when_member_codec_matches(
    provider: MSXBridgeProvider,
) -> None:
    """A member with the same codec as the shared encoder subscribes to it."""
    stream = SharedGroupStream(
        "msx_leader", "library://track/1", session_id="", content_type=ContentType.MP3
    )
    stream.output_plan = Mock(filter_params=[])
    provider._shared_streams["msx_leader"] = stream
    cast("Any", provider.mass.streams.audio).get_player_output_plan = Mock(
        return_value=Mock(filter_params=[])
    )
    pipeline = AudioPipeline(provider)
    member = MagicMock(spec=MSXPlayer)
    member.player_id = "msx_member"
    media = Mock(uri="library://track/1", source_id=None, queue_item_id=None)
    pcm = AudioFormat(content_type=ContentType.PCM_S16LE)
    mp3 = AudioFormat(content_type=ContentType.MP3)
    headers = {"Content-Type": "audio/mpeg"}
    independent = AsyncMock()
    write_shared = AsyncMock(return_value=Mock())
    with (
        patch(
            "music_assistant.providers.msx_bridge.audio_stream.get_media_session_id",
            return_value="",
        ),
        patch.object(pipeline, "serve_independent", independent),
        patch.object(pipeline, "_write_shared_response", write_shared),
    ):
        await pipeline.serve_shared(Mock(), member, media, "msx_leader", pcm, mp3, headers)

    write_shared.assert_awaited_once()
    independent.assert_not_awaited()


async def test_shared_response_omits_content_length(provider: MSXBridgeProvider) -> None:
    """A shared subscriber must not advertise a full-track byte count."""
    pipeline = AudioPipeline(provider)
    stream = SharedGroupStream("g1", "uri://test")
    stream.started.set()
    stream.finished = True

    with patch("music_assistant.providers.msx_bridge.audio_stream.web.StreamResponse") as response:
        response.return_value.prepare = AsyncMock()
        await pipeline._write_shared_response(
            Mock(transport=None),
            "tv1",
            stream,
            {"Content-Type": "audio/mpeg", "Content-Length": "40000"},
        )

    assert response.call_args.kwargs["headers"] == {"Content-Type": "audio/mpeg"}
