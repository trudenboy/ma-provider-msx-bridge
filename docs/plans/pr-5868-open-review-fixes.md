# PR #5868 Open Review Fixes

## Goal

Address the open review comments on `music-assistant/server#5868` without changing the MSX playback contract:

- only active queue items may be served by `/msx/audio`;
- duplicate URIs remain distinguishable by `queue_item_id`;
- invalid queue requests remain HTTP 400 and preparation timeouts remain HTTP 504;
- shared streams retain Music Assistant's ffmpeg pacing arguments;
- production code no longer accommodates impossible test-double shapes.

## Implementation

1. Replace queue item and player queue test doubles with real `QueueItem` and `PlayerQueue` models. Keep mocks only at controller boundaries.
2. Remove tests that assign to the read-only `QueueItem.uri` property. Cover the real no-media-item behavior instead.
3. Type `queue_handshake.py` with `MusicAssistant`, `QueueItem`, and concrete collections instead of `Any`.
4. Remove the fallback `_prepare_lock()` helper and use the lock created by `MSXPlayer.__init__` directly.
5. Replace the HTTP-shaped `PrepareFailure` return value with typed Music Assistant exceptions. Map those exceptions to HTTP 400/504 only in `MSXHTTPServer`.
6. Simplify queue URI and queue-length handling around the real model contracts. Do not catch `TypeError` or `AttributeError` caused by programming errors.
7. Remove the unreachable direct-audio branch from `map_track_to_msx`. Require either a playback context or a native playlist URL and update tests accordingly.
8. Remove unused `MSXHTTPServer._build_audio_params` and `_serve_shared_stream` wrappers. Exercise shared-stream pacing through `AudioPipeline` directly.
9. Preserve security regression coverage: validate the token before queue inspection, reject raw and unqueued URIs, match duplicate queue entries exactly, and use the leader queue for grouped playback.

## Verification

Run focused tests first:

```bash
uv run pytest tests/test_http_server.py -q
uv run pytest tests/test_mappers.py -q
uv run pytest tests/test_group_stream.py -q
uv run pytest tests/test_player.py -q
```

Then run static and full gates:

```bash
uv run ruff check provider/ tests/
uv run ruff format --check provider/ tests/
uv run mypy provider/ tests/
uv run pytest
pre-commit run --all-files
```

## Acceptance Criteria

- `PrepareFailure` and `_prepare_lock()` no longer exist.
- HTTP status codes are selected in `http_server.py`, not `queue_handshake.py`.
- Queue tests return real `QueueItem` and `PlayerQueue` objects.
- `queue_handshake.py` has no `mass: Any` parameters.
- `map_track_to_msx` cannot generate an audio URL that `/msx/audio` rejects.
- The two dead HTTP wrappers are removed and pacing is tested through `AudioPipeline`.
- Expected queue, HTTP, grouping, lint, typing, and full test gates pass.
