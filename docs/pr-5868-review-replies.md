# PR #5868 — proposed replies for every review thread

Prepared 2026-10-08. These are drafts; nothing has been posted or resolved by this document.
Replies to human reviewers must be written by the owner in their own words.
Verified against published head `0281933ba52d863301cb3da561de874b06884fc5`,
official MA dev `73257004745c8b44be6ef43f0001d6230098020d`; upstream CI is green.
The guarded publisher and machine-editable bundle are described in [pr-5868-publish.md](pr-5868-publish.md).
Threads 34/38, 71 and 73 explicitly retain limitations or pending design decisions; their resolved flags are not proof of a fix.

## Review threads

<a id="thread-1"></a>

### 1. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826439498)

Author: OzGav; GitHub state: resolved.

The docstrings now describe the caller-facing contract. Implementation notes were moved out of the public documentation; the updated HTTP helpers can be checked directly in the diff.

<a id="thread-2"></a>

### 2. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826440433)

Author: OzGav; GitHub state: resolved.

The docstrings now describe the caller-facing contract. Implementation notes were moved out of the public documentation; the updated HTTP helpers can be checked directly in the diff.

<a id="thread-3"></a>

### 3. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826442799)

Author: OzGav; GitHub state: resolved.

Native audio preparation now selects the existing queue item with play_index instead of re-enqueuing its URI with the default REPLACE policy. The queue handshake tests cover queued builtin sources and preserve queue identity; the new two-request unauthenticated regression also verifies that both queued items remain available.

<a id="thread-4"></a>

### 4. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826447522)

Author: OzGav; GitHub state: resolved.

The paging loop and scan-page constant were removed. Queue scans now use items(queue.queue_id, limit=queue.items), reading the complete in-memory queue once.

<a id="thread-5"></a>

### 5. [tests/providers/msx_bridge/test_http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826449590)

Author: OzGav; GitHub state: resolved.

The call-count assertion was removed. The long-queue regression asserts that the requested item remains playable, without constraining the scan implementation.

<a id="thread-6"></a>

### 6. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3826484434)

Author: OzGav; GitHub state: resolved.

The playback handlers catch MusicAssistantError, OSError and TimeoutError. Unexpected programming errors are allowed to surface; the HTTP regression tests assert HTTP 500 for those errors rather than a misleading availability response.

<a id="thread-7"></a>

### 7. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842161692)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-8"></a>

### 8. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842161745)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Context playback first checks the indexed queue item and uses it when its URI matches. URI lookup is only a fallback if ordering differs, so a duplicate URI at a later index retains its exact queue-item identity.

<a id="thread-9"></a>

### 9. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842161775)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Trusted TV seek reports explicitly rebase the player clock, including seeks received before the first ordinary position sample. The initial-sample guard continues to reject stale reports without imposing a permanent wall-clock ceiling on intentional seeks.

<a id="thread-10"></a>

### 10. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3842161806)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The plugin rebases its playback clock after a TV seek and sends an explicit seek event to the server. The player accepts that event as a trusted jump, including before the first position sample; it is not treated as a stale ordinary sample.

<a id="thread-11"></a>

### 11. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842161841)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The shared producer was removed with provider-native grouping. The remaining independent pipeline does not turn unexpected encoder failures into clean EOF: its producer task is awaited even when already finished, and unexpected failures propagate.

<a id="thread-12"></a>

### 12. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842161870)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

WebSocket notification suppression is now a per-player nesting counter. Playback preparation uses the same context manager, so one overlapping command cannot clear another command's suppression; the nesting regression covers restoration on exit.

<a id="thread-13"></a>

### 13. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3842161910)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-14"></a>

### 14. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842462618)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-15"></a>

### 15. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842462648)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

<a id="thread-16"></a>

### 16. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842462661)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The shared producer was removed with provider-native grouping. The remaining independent pipeline does not turn unexpected encoder failures into clean EOF: its producer task is awaited even when already finished, and unexpected failures propagate.

<a id="thread-17"></a>

### 17. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842462692)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Context playback first checks the indexed queue item and uses it when its URI matches. URI lookup is only a fallback if ordering differs, so a duplicate URI at a later index retains its exact queue-item identity.

<a id="thread-18"></a>

### 18. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842588748)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

After container enqueueing, the handler compares the target queue-item ID with the player's current media. play_index is called only when they differ, avoiding a second playback session for index zero or a single-track context.

<a id="thread-19"></a>

### 19. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842588799)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

<a id="thread-20"></a>

### 20. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842683961)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The QR cover allowlist no longer trusts the request Host-derived prefix. It uses the configured MA webserver/stream origins; arbitrary caller-selected hosts and redirect destinations cannot become fetch targets.

<a id="thread-21"></a>

### 21. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842683998)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

<a id="thread-22"></a>

### 22. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842684019)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Native queue playlists read limit=queue.items, including the current item beyond the old 500-item default. Long-queue tests exercise playlist rotation and a start index above ten thousand.

<a id="thread-23"></a>

### 23. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3842684032)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The plugin rebases its playback clock after a TV seek and sends an explicit seek event to the server. The player accepts that event as a trusted jump, including before the first position sample; it is not treated as a stale ordinary sample.

<a id="thread-24"></a>

### 24. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842815970)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Next records the queue index before calling MA and returns an empty MSX action when the index does not advance. Repeat-one remains an intentional reload. The previous handler now uses the same guard, with separate no-op, movement and repeat-one regressions.

<a id="thread-25"></a>

### 25. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842816012)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-26"></a>

### 26. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3842816053)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Cover fetches enforce a declared-size and incremental-read byte cap before image decoding. Image dimensions are checked before RGB conversion, and Pillow decompression-bomb warnings/errors are rejected rather than accepted as ordinary images.

<a id="thread-27"></a>

### 27. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3842816072)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The plugin reconnects listeners when the media element/source changes and rescans after playback actions. This prevents a reused media element from retaining a detached set of pause/play/seek listeners after a track change; real native-device confirmation is still required.

<a id="thread-28"></a>

### 28. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869277467)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-29"></a>

### 29. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869277515)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-30"></a>

### 30. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869277549)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The compositor no longer changes Pillow's process-global MAX_IMAGE_PIXELS. It checks the opened image dimensions locally before conversion and treats decompression warnings/errors as failures, avoiding cross-thread global-state changes.

<a id="thread-31"></a>

### 31. [music_assistant/providers/msx_bridge/queue_handshake.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869277596)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The module-global lock dictionary and fallback lock factory were removed. Queue preparation uses the MSXPlayer-owned _prepare_lock created in its constructor, so unregistering the player also releases ownership of that state.

<a id="thread-32"></a>

### 32. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3869277633)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Server-seek echo suppression tracks an expected target with a timeout and is cleared on playback reset. A missing seeked event cannot leave an unbounded latch that discards the next genuine TV seek.

<a id="thread-33"></a>

### 33. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3869277659)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-34"></a>

### 34. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869480847)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This intentionally reports the native player seek to the MA clock without rebuilding the active progressive HTTP response. Calling cmd_seek alone replaces the MA stream but does not replace the HTTP body already consumed by MSX. Seek beyond buffered native audio still needs device evidence; this response does not claim that the server stream was rebuilt. A complete stream-replacement seek contract remains a separate design decision.

<a id="thread-35"></a>

### 35. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869480887)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The compositor no longer changes Pillow's process-global MAX_IMAGE_PIXELS. It checks the opened image dimensions locally before conversion and treats decompression warnings/errors as failures, avoiding cross-thread global-state changes.

<a id="thread-36"></a>

### 36. [music_assistant/providers/msx_bridge/queue_handshake.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869734132)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Queue matching uses the canonical QueueItem.uri and falls back to media_item.uri where appropriate. Queue entries without a nested full media item are therefore selectable without re-enqueueing their URI.

<a id="thread-37"></a>

### 37. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3869734197)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-38"></a>

### 38. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3869922889)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This intentionally reports the native player seek to the MA clock without rebuilding the active progressive HTTP response. Calling cmd_seek alone replaces the MA stream but does not replace the HTTP body already consumed by MSX. Seek beyond buffered native audio still needs device evidence; this response does not claim that the server stream was rebuilt. A complete stream-replacement seek contract remains a separate design decision.

<a id="thread-39"></a>

### 39. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3870062407)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-40"></a>

### 40. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3870209242)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-41"></a>

### 41. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3870352916)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-42"></a>

### 42. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3879233681)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-43"></a>

### 43. [music_assistant/providers/msx_bridge/mappers.py](https://github.com/music-assistant/server/pull/5868#discussion_r3879233745)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The explicit-player queue route retains the player named in the path and reads only the optional device_id parameter. It no longer calls the request-derived registration helper, so next/previous cannot create an additional IP-derived player.

<a id="thread-44"></a>

### 44. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3879233804)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-45"></a>

### 45. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3879233870)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

<a id="thread-46"></a>

### 46. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3879233938)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-47"></a>

### 47. [music_assistant/providers/msx_bridge/queue_handshake.py](https://github.com/music-assistant/server/pull/5868#discussion_r3890904156)

Author: OzGav; GitHub state: resolved.

The module-global lock dictionary and fallback lock factory were removed. Queue preparation uses the MSXPlayer-owned _prepare_lock created in its constructor, so unregistering the player also releases ownership of that state.

<a id="thread-48"></a>

### 48. [music_assistant/providers/msx_bridge/mappers.py](https://github.com/music-assistant/server/pull/5868#discussion_r3890906436)

Author: OzGav; GitHub state: resolved.

context_uri is now a required mapper argument. The unreachable direct-audio and playlist_url branches were removed rather than replaced with a new unreachable exception path.

<a id="thread-49"></a>

### 49. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3890911097)

Author: OzGav; GitHub state: resolved.

The unused HTTP audio wrappers were removed. Production code calls AudioPipeline, and obsolete tests of the wrappers were removed or moved to the actual pipeline behavior.

<a id="thread-50"></a>

### 50. [music_assistant/providers/msx_bridge/queue_handshake.py](https://github.com/music-assistant/server/pull/5868#discussion_r3890915434)

Author: OzGav; GitHub state: resolved.

The queue handshake raises typed MA errors and contains no HTTP status policy. The HTTP handler maps those errors to response statuses at the transport boundary.

<a id="thread-51"></a>

### 51. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3903956159)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The explicit-player queue route retains the player named in the path and reads only the optional device_id parameter. It no longer calls the request-derived registration helper, so next/previous cannot create an additional IP-derived player.

<a id="thread-52"></a>

### 52. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3903956211)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type.

<a id="thread-53"></a>

### 53. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3904110252)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-54"></a>

### 54. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904110318)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-55"></a>

### 55. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904110376)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-56"></a>

### 56. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904110426)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-57"></a>

### 57. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904580658)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The docstring now promises fallback only for expected provider failures and timeouts. It no longer claims that the method never raises; unexpected programming errors remain visible.

<a id="thread-58"></a>

### 58. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3904794954)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-59"></a>

### 59. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904990919)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Browser WebSocket/control requests are checked before connection preparation or command dispatch. Sec-Fetch-Site permits only same-origin, none or absence for native MSX; an Origin header must match the expected origin. This protects ordinary cross-site/same-site browser requests, but is not presented as a pairing credential or complete DNS-rebinding protection; see the separate credential discussion.

<a id="thread-60"></a>

### 60. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3904990984)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Browser WebSocket/control requests are checked before connection preparation or command dispatch. Sec-Fetch-Site permits only same-origin, none or absence for native MSX; an Origin header must match the expected origin. This protects ordinary cross-site/same-site browser requests, but is not presented as a pairing credential or complete DNS-rebinding protection; see the separate credential discussion.

<a id="thread-61"></a>

### 61. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3904991049)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-62"></a>

### 62. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3905596864)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Covers are resized to a maximum of 1024 pixels before compositing. The rendered PNG LRU cache is capped at 16 MiB by actual byte length, so the cache cannot grow to the old entry-count-based multi-gigabyte bound.

<a id="thread-63"></a>

### 63. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3905596956)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-64"></a>

### 64. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3905597009)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type.

<a id="thread-65"></a>

### 65. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3908777354)

Author: OzGav; GitHub state: resolved.

The defensive queue-size helper was removed. The route uses the typed PlayerQueue.current_index and PlayerQueue.items fields directly after checking whether the queue exists.

<a id="thread-66"></a>

### 66. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3908791328)

Author: OzGav; GitHub state: resolved.

Audio serving methods now accept PlayerMedia and the duration helper accepts MusicAssistant. The corresponding getattr fallbacks were replaced with direct fields, and the upstream mypy gate checks the real MA types.

<a id="thread-67"></a>

### 67. [music_assistant/providers/msx_bridge/mappers.py](https://github.com/music-assistant/server/pull/5868#discussion_r3908808566)

Author: OzGav; GitHub state: resolved.

context_uri is now a required mapper argument. The unreachable direct-audio and playlist_url branches were removed rather than replaced with a new unreachable exception path.

<a id="thread-68"></a>

### 68. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3908822439)

Author: OzGav; GitHub state: resolved.

Configured cover origins now read mass.webserver.base_url and mass.streams.base_url directly. The getattr/isinstance/startswith guards around guaranteed controller fields were removed.

<a id="thread-69"></a>

### 69. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3917923040)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Native MSX video:seek events now forward data.position through reportTvSeek and the bounded server-seek echo guard. This covers playback outside the plugin DOM as well as DOM media events.

<a id="thread-70"></a>

### 70. [music_assistant/providers/msx_bridge/audio_stream.py](https://github.com/music-assistant/server/pull/5868#discussion_r3918111395)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

<a id="thread-71"></a>

### 71. [music_assistant/providers/msx_bridge/party.py](https://github.com/music-assistant/server/pull/5868#discussion_r3918111468)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

<a id="thread-72"></a>

### 72. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3918111516)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type.

<a id="thread-73"></a>

### 73. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3918265920)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The current cross-origin guard is not an unguessable control credential and does not fully address DNS rebinding. The previous out-of-scope reply did not establish a fix. Native MSX bootstrap/control pairing needs an agreed credential distribution and rotation contract; this remains a concrete security follow-up, not a claim of complete protection from Fetch Metadata alone.

<a id="thread-74"></a>

### 74. [music_assistant/providers/msx_bridge/player.py](https://github.com/music-assistant/server/pull/5868#discussion_r3918265989)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

Trusted TV seeks update the elapsed-time snapshot in both PLAYING and PAUSED states. Ordinary late position reports remain PLAYING-only, so paused state is not updated by stale periodic samples.

<a id="thread-75"></a>

### 75. [music_assistant/providers/msx_bridge/static/plugin.html](https://github.com/music-assistant/server/pull/5868#discussion_r3918266032)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

reportTvSeek updates pausedAtPosition before the server-seek echo early return. Resuming after a paused seek therefore starts reporting from the new native position.

<a id="thread-76"></a>

### 76. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3921001568)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The central middleware rejects cross-site requests to every token-bearing /msx/playlist/* and /msx/queue-playlist/* route before a handler reads queue data or serializes tokens. Parameterized HTTP tests cover all six playlist paths and verify rejection without token disclosure.

<a id="thread-77"></a>

### 77. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3921001590)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The playback handlers catch MusicAssistantError, OSError and TimeoutError. Unexpected programming errors are allowed to surface; the HTTP regression tests assert HTTP 500 for those errors rather than a misleading availability response.

<a id="thread-78"></a>

### 78. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3921001616)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The reviewed provider VERSION remains 1.6.0. The prepared description names that snapshot and explains the full change from the bundled 1.4.9 version; subsequent fixes are explicitly identified rather than represented as an older published tag.

<a id="thread-79"></a>

### 79. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3921032060)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The owner-attribution restoration was superseded by the later external-hardware fix. Unauthenticated MSX requests now use ImpersonatedUser(mass, None), with no first-enabled-user selection or cached owner. Restoring that heuristic would reintroduce the authorization failure reported in support #6624; authenticated attribution needs a separate supported identity contract.

<a id="thread-80"></a>

### 80. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3922050645)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The central middleware rejects cross-site requests to every token-bearing /msx/playlist/* and /msx/queue-playlist/* route before a handler reads queue data or serializes tokens. Parameterized HTTP tests cover all six playlist paths and verify rejection without token disclosure.

<a id="thread-81"></a>

### 81. [music_assistant/providers/msx_bridge/provider.py](https://github.com/music-assistant/server/pull/5868#discussion_r3922050699)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The owner-attribution restoration was superseded by the later external-hardware fix. Unauthenticated MSX requests now use ImpersonatedUser(mass, None), with no first-enabled-user selection or cached owner. Restoring that heuristic would reintroduce the authorization failure reported in support #6624; authenticated attribution needs a separate supported identity contract.

<a id="thread-82"></a>

### 82. [music_assistant/providers/msx_bridge/VERSION](https://github.com/music-assistant/server/pull/5868#discussion_r3932176208)

Author: copilot-pull-request-reviewer; GitHub state: resolved.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type.

<a id="thread-83"></a>

### 83. [music_assistant/providers/msx_bridge/http_server.py](https://github.com/music-assistant/server/pull/5868#discussion_r3946368654)

Author: OzGav; GitHub state: open.

The previous handler now captures the queue index, calls MA under notification suppression, and returns an empty action when _queue_advanced reports no movement. The red/green regression reproduces index zero with repeat off; additional cases preserve movement to the prior item and an intentional repeat-one restart. This is the three-line guard used by next, carried by provider PR #270.

## Coverage of every inline comment

118 inline comments are covered by the 83 consolidated thread replies. Existing contributor follow-ups are mapped to the same reply, including corrections of superseded earlier explanations.

| Comment | Author | Proposed thread reply |
|---|---|---|
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826439498) | OzGav | [reply 1](#thread-1) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866684982) | trudenboy | [reply 1](#thread-1) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826440433) | OzGav | [reply 2](#thread-2) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866690020) | trudenboy | [reply 2](#thread-2) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826442799) | OzGav | [reply 3](#thread-3) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866693793) | trudenboy | [reply 3](#thread-3) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826447522) | OzGav | [reply 4](#thread-4) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866698215) | trudenboy | [reply 4](#thread-4) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826449590) | OzGav | [reply 5](#thread-5) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866700704) | trudenboy | [reply 5](#thread-5) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3826484434) | OzGav | [reply 6](#thread-6) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3866705237) | trudenboy | [reply 6](#thread-6) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161692) | copilot-pull-request-reviewer | [reply 7](#thread-7) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161745) | copilot-pull-request-reviewer | [reply 8](#thread-8) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161775) | copilot-pull-request-reviewer | [reply 9](#thread-9) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161806) | copilot-pull-request-reviewer | [reply 10](#thread-10) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161841) | copilot-pull-request-reviewer | [reply 11](#thread-11) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161870) | copilot-pull-request-reviewer | [reply 12](#thread-12) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842161910) | copilot-pull-request-reviewer | [reply 13](#thread-13) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842462618) | copilot-pull-request-reviewer | [reply 14](#thread-14) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842462648) | copilot-pull-request-reviewer | [reply 15](#thread-15) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842462661) | copilot-pull-request-reviewer | [reply 16](#thread-16) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842462692) | copilot-pull-request-reviewer | [reply 17](#thread-17) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842588748) | copilot-pull-request-reviewer | [reply 18](#thread-18) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842588799) | copilot-pull-request-reviewer | [reply 19](#thread-19) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842683961) | copilot-pull-request-reviewer | [reply 20](#thread-20) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842683998) | copilot-pull-request-reviewer | [reply 21](#thread-21) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842684019) | copilot-pull-request-reviewer | [reply 22](#thread-22) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842684032) | copilot-pull-request-reviewer | [reply 23](#thread-23) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842815970) | copilot-pull-request-reviewer | [reply 24](#thread-24) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842816012) | copilot-pull-request-reviewer | [reply 25](#thread-25) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842816053) | copilot-pull-request-reviewer | [reply 26](#thread-26) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3842816072) | copilot-pull-request-reviewer | [reply 27](#thread-27) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277467) | copilot-pull-request-reviewer | [reply 28](#thread-28) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277515) | copilot-pull-request-reviewer | [reply 29](#thread-29) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277549) | copilot-pull-request-reviewer | [reply 30](#thread-30) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277596) | copilot-pull-request-reviewer | [reply 31](#thread-31) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277633) | copilot-pull-request-reviewer | [reply 32](#thread-32) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869277659) | copilot-pull-request-reviewer | [reply 33](#thread-33) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869480847) | copilot-pull-request-reviewer | [reply 34](#thread-34) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869480887) | copilot-pull-request-reviewer | [reply 35](#thread-35) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869734132) | copilot-pull-request-reviewer | [reply 36](#thread-36) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869734197) | copilot-pull-request-reviewer | [reply 37](#thread-37) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3869922889) | copilot-pull-request-reviewer | [reply 38](#thread-38) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870166467) | trudenboy | [reply 38](#thread-38) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870062407) | copilot-pull-request-reviewer | [reply 39](#thread-39) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870166717) | trudenboy | [reply 39](#thread-39) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870209242) | copilot-pull-request-reviewer | [reply 40](#thread-40) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870245203) | trudenboy | [reply 40](#thread-40) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3870352916) | copilot-pull-request-reviewer | [reply 41](#thread-41) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027936) | trudenboy | [reply 41](#thread-41) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3879233681) | copilot-pull-request-reviewer | [reply 42](#thread-42) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027946) | trudenboy | [reply 42](#thread-42) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3879233745) | copilot-pull-request-reviewer | [reply 43](#thread-43) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027953) | trudenboy | [reply 43](#thread-43) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3879233804) | copilot-pull-request-reviewer | [reply 44](#thread-44) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027952) | trudenboy | [reply 44](#thread-44) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3879233870) | copilot-pull-request-reviewer | [reply 45](#thread-45) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027955) | trudenboy | [reply 45](#thread-45) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3879233938) | copilot-pull-request-reviewer | [reply 46](#thread-46) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3886027963) | trudenboy | [reply 46](#thread-46) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3890904156) | OzGav | [reply 47](#thread-47) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904618299) | trudenboy | [reply 47](#thread-47) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3890906436) | OzGav | [reply 48](#thread-48) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904635400) | trudenboy | [reply 48](#thread-48) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3890911097) | OzGav | [reply 49](#thread-49) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904650612) | trudenboy | [reply 49](#thread-49) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3890915434) | OzGav | [reply 50](#thread-50) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904655643) | trudenboy | [reply 50](#thread-50) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3903956159) | copilot-pull-request-reviewer | [reply 51](#thread-51) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3903956211) | copilot-pull-request-reviewer | [reply 52](#thread-52) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904110252) | copilot-pull-request-reviewer | [reply 53](#thread-53) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904110318) | copilot-pull-request-reviewer | [reply 54](#thread-54) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904110376) | copilot-pull-request-reviewer | [reply 55](#thread-55) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904110426) | copilot-pull-request-reviewer | [reply 56](#thread-56) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904580658) | copilot-pull-request-reviewer | [reply 57](#thread-57) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904794954) | copilot-pull-request-reviewer | [reply 58](#thread-58) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904990919) | copilot-pull-request-reviewer | [reply 59](#thread-59) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904990984) | copilot-pull-request-reviewer | [reply 60](#thread-60) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3904991049) | copilot-pull-request-reviewer | [reply 61](#thread-61) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3905596864) | copilot-pull-request-reviewer | [reply 62](#thread-62) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3905596956) | copilot-pull-request-reviewer | [reply 63](#thread-63) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3905597009) | copilot-pull-request-reviewer | [reply 64](#thread-64) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3908777354) | OzGav | [reply 65](#thread-65) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921095387) | trudenboy | [reply 65](#thread-65) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3908791328) | OzGav | [reply 66](#thread-66) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921100912) | trudenboy | [reply 66](#thread-66) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3908808566) | OzGav | [reply 67](#thread-67) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921107057) | trudenboy | [reply 67](#thread-67) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3908822439) | OzGav | [reply 68](#thread-68) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921109921) | trudenboy | [reply 68](#thread-68) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3917923040) | copilot-pull-request-reviewer | [reply 69](#thread-69) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921031371) | trudenboy | [reply 69](#thread-69) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918111395) | copilot-pull-request-reviewer | [reply 70](#thread-70) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921031382) | trudenboy | [reply 70](#thread-70) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918111468) | copilot-pull-request-reviewer | [reply 71](#thread-71) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921423892) | trudenboy | [reply 71](#thread-71) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918111516) | copilot-pull-request-reviewer | [reply 72](#thread-72) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918265920) | copilot-pull-request-reviewer | [reply 73](#thread-73) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921778566) | trudenboy | [reply 73](#thread-73) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918265989) | copilot-pull-request-reviewer | [reply 74](#thread-74) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921031415) | trudenboy | [reply 74](#thread-74) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3918266032) | copilot-pull-request-reviewer | [reply 75](#thread-75) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921031414) | trudenboy | [reply 75](#thread-75) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921001568) | copilot-pull-request-reviewer | [reply 76](#thread-76) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922021960) | trudenboy | [reply 76](#thread-76) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921001590) | copilot-pull-request-reviewer | [reply 77](#thread-77) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922022025) | trudenboy | [reply 77](#thread-77) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921001616) | copilot-pull-request-reviewer | [reply 78](#thread-78) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3921032060) | copilot-pull-request-reviewer | [reply 79](#thread-79) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922021967) | trudenboy | [reply 79](#thread-79) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922050645) | copilot-pull-request-reviewer | [reply 80](#thread-80) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922259632) | trudenboy | [reply 80](#thread-80) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922050699) | copilot-pull-request-reviewer | [reply 81](#thread-81) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3922259628) | trudenboy | [reply 81](#thread-81) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3932176208) | copilot-pull-request-reviewer | [reply 82](#thread-82) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3932208121) | trudenboy | [reply 82](#thread-82) |
| [comment](https://github.com/music-assistant/server/pull/5868#discussion_r3946368654) | OzGav | [reply 83](#thread-83) |

## Review summaries, including suppressed findings

These review-level replies cover findings embedded in summaries as well as inline threads. Repeated historical findings are consolidated within each reply.

### Review [4985215965](https://github.com/music-assistant/server/pull/5868#pullrequestreview-4985215965) — copilot-pull-request-reviewer[bot]

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [4991458525](https://github.com/music-assistant/server/pull/5868#pullrequestreview-4991458525) — copilot-pull-request-reviewer[bot]

The JSON boundary catches LookupError as well as JSON/Unicode decode errors, returning HTTP 400 for an unknown request charset.

### Review [5006317867](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5006317867) — copilot-pull-request-reviewer[bot]

The shared producer was retired. Independent-stream cleanup awaits the producer even if it already finished, making exceptions observable.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

### Review [5006670095](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5006670095) — copilot-pull-request-reviewer[bot]

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

WebSocket notification suppression is now a per-player nesting counter. Playback preparation uses the same context manager, so one overlapping command cannot clear another command's suppression; the nesting regression covers restoration on exit.

The explicit-player queue route retains the player named in the path and reads only the optional device_id parameter. It no longer calls the request-derived registration helper, so next/previous cannot create an additional IP-derived player.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5006811862](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5006811862) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5006917788](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5006917788) — copilot-pull-request-reviewer[bot]

The shared producer was retired. Independent-stream cleanup awaits the producer even if it already finished, making exceptions observable.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

### Review [5007062235](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5007062235) — copilot-pull-request-reviewer[bot]

The shared producer was retired. Independent-stream cleanup awaits the producer even if it already finished, making exceptions observable.

### Review [5007063266](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5007063266) — copilot-pull-request-reviewer[bot]

No code finding was supplied in this review. A new review can be requested after the updated snapshot has passed CI.

### Review [5037867763](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5037867763) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5038109931](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038109931) — copilot-pull-request-reviewer[bot]

Album ordering now adds the stable URI/item ID after disc, track number and name, so equal titles do not leave ordering provider-dependent.

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5038161473](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038161473) — copilot-pull-request-reviewer[bot]

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

### Review [5038411000](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038411000) — copilot-pull-request-reviewer[bot]

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

Queue matching uses the canonical QueueItem.uri and falls back to media_item.uri where appropriate. Queue entries without a nested full media item are therefore selectable without re-enqueueing their URI.

### Review [5038635510](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038635510) — copilot-pull-request-reviewer[bot]

Decoded JSON is checked to be a dictionary before reading fields; the non-object JSON regression expects HTTP 400.

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

The shared subscriber method containing that docstring was removed; remaining docstrings use the project's caller-facing Sphinx style.

### Review [5038796430](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038796430) — copilot-pull-request-reviewer[bot]

resolve_stream_url fallback catches only MusicAssistantError. Playback HTTP boundaries catch the documented MA/I/O/timeout errors, and programming-error tests require unexpected failures to surface.

The queue-size helper and permissive model mocks were removed. QueueItem, PlayerQueue and PlayerMedia fixtures are concrete records; queue/audio helpers use MusicAssistant and known model fields directly. Controller/encoding boundaries remain mocked, so this is not a claim of a fully booted server test.

### Review [5038962070](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5038962070) — copilot-pull-request-reviewer[bot]

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

resolve_stream_url fallback catches only MusicAssistantError. Playback HTTP boundaries catch the documented MA/I/O/timeout errors, and programming-error tests require unexpected failures to surface.

### Review [5039134051](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5039134051) — copilot-pull-request-reviewer[bot]

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

### Review [5049472032](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5049472032) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5062239056](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5062239056) — OzGav

The queue-size helper and permissive model mocks were removed. QueueItem, PlayerQueue and PlayerMedia fixtures are concrete records; queue/audio helpers use MusicAssistant and known model fields directly. Controller/encoding boundaries remain mocked, so this is not a claim of a fully booted server test.

### Review [5077844016](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5077844016) — copilot-pull-request-reviewer[bot]

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

### Review [5078041078](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5078041078) — copilot-pull-request-reviewer[bot]

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

The explicit-player queue route retains the player named in the path and reads only the optional device_id parameter. It no longer calls the request-derived registration helper, so next/previous cannot create an additional IP-derived player.

### Review [5078624398](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5078624398) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5078883105](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5078883105) — copilot-pull-request-reviewer[bot]

HTTP server shutdown calls PartyAdapter.stop, which cancels and awaits the adapter-owned cover render tasks and clears the in-flight registry. Shielding an individual request no longer permits work to outlive provider shutdown.

Cover fetch/decode/render is limited by an adapter-level semaphore to two renders, and excess distinct in-flight requests redirect instead of accumulating unbounded tasks; the image/cache byte limits apply separately.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5079121208](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5079121208) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5079327616](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5079327616) — copilot-pull-request-reviewer[bot]

Queue and context start parameters are parsed without the arbitrary ten-thousand cap; regressions request start=12001 and verify the selected item/index.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5079841774](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5079841774) — copilot-pull-request-reviewer[bot]

The detailed findings are addressed individually in the numbered thread replies above. Reviews reporting no new findings need no additional code change; verification is tied to the final synced head rather than an older intermediate version.

### Review [5080505089](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5080505089) — copilot-pull-request-reviewer[bot]

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5094220661](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5094220661) — copilot-pull-request-reviewer[bot]

Native MSX video:seek events now forward data.position through reportTvSeek and the bounded server-seek echo guard. This covers playback outside the plugin DOM as well as DOM media events. Trusted TV seeks update the elapsed-time snapshot in both PLAYING and PAUSED states. Ordinary late position reports remain PLAYING-only, so paused state is not updated by stale periodic samples.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5094481375](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5094481375) — copilot-pull-request-reviewer[bot]

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

WebSocket notification suppression is now a per-player nesting counter. Playback preparation uses the same context manager, so one overlapping command cannot clear another command's suppression; the nesting regression covers restoration on exit.

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5094653442](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5094653442) — copilot-pull-request-reviewer[bot]

resolve_stream_url fallback catches only MusicAssistantError. Playback HTTP boundaries catch the documented MA/I/O/timeout errors, and programming-error tests require unexpected failures to surface.

The canonical-identity guard now inspects loaded module objects by resolved source path. A real alternate import of player.py demonstrated that the old check failed to detect duplicate loading; the new regression observes the guard rejecting it.

Native MSX video:seek events now forward data.position through reportTvSeek and the bounded server-seek echo guard. This covers playback outside the plugin DOM as well as DOM media events. Trusted TV seeks update the elapsed-time snapshot in both PLAYING and PAUSED states. Ordinary late position reports remain PLAYING-only, so paused state is not updated by stale periodic samples.

The central middleware rejects cross-site requests to every token-bearing /msx/playlist/* and /msx/queue-playlist/* route before a handler reads queue data or serializes tokens. Parameterized HTTP tests cover all six playlist paths and verify rejection without token disclosure. The current cross-origin guard is not an unguessable control credential and does not fully address DNS rebinding. The previous out-of-scope reply did not establish a fix. Native MSX bootstrap/control pairing needs an agreed credential distribution and rotation contract; this remains a concrete security follow-up, not a claim of complete protection from Fetch Metadata alone.

### Review [5097721041](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5097721041) — copilot-pull-request-reviewer[bot]

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

The central middleware rejects cross-site requests to every token-bearing /msx/playlist/* and /msx/queue-playlist/* route before a handler reads queue data or serializes tokens. Parameterized HTTP tests cover all six playlist paths and verify rejection without token disclosure. The current cross-origin guard is not an unguessable control credential and does not fully address DNS rebinding. The previous out-of-scope reply did not establish a fix. Native MSX bootstrap/control pairing needs an agreed credential distribution and rotation contract; this remains a concrete security follow-up, not a claim of complete protection from Fetch Metadata alone.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5097755027](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5097755027) — copilot-pull-request-reviewer[bot]

resolve_stream_url fallback catches only MusicAssistantError. Playback HTTP boundaries catch the documented MA/I/O/timeout errors, and programming-error tests require unexpected failures to surface.

The owner-attribution restoration was superseded by the later external-hardware fix. Unauthenticated MSX requests now use ImpersonatedUser(mass, None), with no first-enabled-user selection or cached owner. Restoring that heuristic would reintroduce the authorization failure reported in support #6624; authenticated attribution needs a separate supported identity contract.

### Review [5098947413](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5098947413) — copilot-pull-request-reviewer[bot]

The owner-attribution restoration was superseded by the later external-hardware fix. Unauthenticated MSX requests now use ImpersonatedUser(mass, None), with no first-enabled-user selection or cached owner. Restoring that heuristic would reintroduce the authorization failure reported in support #6624; authenticated attribution needs a separate supported identity contract.

The central middleware rejects cross-site requests to every token-bearing /msx/playlist/* and /msx/queue-playlist/* route before a handler reads queue data or serializes tokens. Parameterized HTTP tests cover all six playlist paths and verify rejection without token disclosure. The current cross-origin guard is not an unguessable control credential and does not fully address DNS rebinding. The previous out-of-scope reply did not establish a fix. Native MSX bootstrap/control pairing needs an agreed credential distribution and rotation contract; this remains a concrete security follow-up, not a claim of complete protection from Fetch Metadata alone.

### Review [5099324263](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5099324263) — copilot-pull-request-reviewer[bot]

The provider-specific Party lookup is still present; the earlier link to #6184 is not evidence of a completed fix because that PR was closed without merge. Current MA has no accepted get_active_guest_session contract to consume. The remaining choice is to land that generic contract and migrate this adapter, or remove the automatic Party integration; this item should not be treated as fixed by its current resolved flag.

This provider-managed shared/group path was removed in the 1.6.0 Universal Groups migration. Its old producer/subscriber registry and propagation logic are absent from the current snapshot. Existing provider-native groups must be recreated as Universal Groups; the PR description explains that migration rather than claiming a repair of the retired mode.

### Review [5110736531](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5110736531) — copilot-pull-request-reviewer[bot]

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

### Review [5127855090](https://github.com/music-assistant/server/pull/5868#pullrequestreview-5127855090) — OzGav

The independent pipeline now uses an out-of-band producer_done event as well as the optional queue sentinel. If the queue is full, buffered audio is preserved and the consumer exits after draining it; cleanup cancels and awaits the producer, without waiting to enqueue EOF into an abandoned queue. Shared subscriber handling was removed with provider-native grouping.

The prepared PR description covers the full 1.4.9 to 1.6.0 update: queue-native playback, streaming/auth/position fixes, Party presentation, kiosk/Sendspin removal and the Universal Groups migration. It explicitly describes what happens to users of the removed grouping/shared-buffer modes, with breaking-change as the dominant change type. VERSION remains 1.6.0; the maintainer requested the current bug/compatibility follow-ups on 2026-10-08, and they are identified explicitly.

A proposed reply and evidence pointer are now prepared for all 83 inline threads. No human-reviewer response has been posted automatically and no resolved flag is used as proof of a completed fix.

## General PR comments

### [marcelveldt](https://github.com/music-assistant/server/pull/5868#issuecomment-5429323852)

The review audit now distinguishes implemented fixes, removed paths and pending decisions. Each inline thread has a proposed response with evidence instead of relying on its resolved flag; the PR stays draft until the remaining decisions and human responses are complete.

### [musicassistant-bot[bot]](https://github.com/music-assistant/server/pull/5868#issuecomment-5461222268)

This is an automated title/description check. The updated body retains the required template and exactly one dominant breaking-change type; verify the refreshed check after the metadata update.

### [MarvinSchenkel](https://github.com/music-assistant/server/pull/5868#issuecomment-5567272830)

The PR remains draft while the updated snapshot, review replies and outstanding design/security decisions are verified. Ready-for-review will be set only after the contributor is ready for another human review.
