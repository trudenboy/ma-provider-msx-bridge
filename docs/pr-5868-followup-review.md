# PR #5868 — four new review findings, 2026-10-08

Snapshot: 87 inline threads, 83 previously resolved and answered, four new open Copilot-only threads. Each of the four findings reproduced before its fix.

| Comment | Finding and correction | Regression evidence |
| --- | --- | --- |
| [4222110331](https://github.com/music-assistant/server/pull/5868#discussion_r4222110331) | Check producer failure before headers; return HTTP 503 on expected startup failures; abort an incomplete response after headers. | Four actual HTTP startup cases (MusicAssistantError/OSError, empty/partial prebuffer) failed with HTTP 200 before the fix. The midstream chunked-response test failed against the original implementation and now observes ClientPayloadError. |
| [4222110376](https://github.com/music-assistant/server/pull/5868#discussion_r4222110376) | Use full served duration for optional MP3/AAC Content-Length. | Both thirteen-hour cases failed against the twelve-hour clamp; expected full estimates are 1872000000 / 1497600000 bytes. |
| [4222110431](https://github.com/music-assistant/server/pull/5868#discussion_r4222110431) | Actual native item transitions send clock_reset, without a playlist command. Resume and no-op navigation preserve the paused position. | Execute the shipped plugin in Node.js with actual provider WebSocket frames: the old transition reported 20 seconds instead of 0; the fix starts at 0 and same-item resume stays at 20. |
| [4222110477](https://github.com/music-assistant/server/pull/5868#discussion_r4222110477) | Move persistent cleanup/conversion to MA core before provider loading. | Six stored-JSON cases failed before the fix. Enabled/disabled instances and true/false/null legacy values migrate; unrelated settings survive; a second pass returns unchanged. Four current-mode/missing-value cases also pass. |

Provider changes: [provider PR #273](https://github.com/trudenboy/ma-provider-msx-bridge/pull/273), commit aba9581. Core changes: commit 07773e2, preserved in [the core patch](patches/pr-5868-config-migration.patch) because the export workflow only copies provider directories. VERSION remains 1.6.0; no release/tag is created.

Validation on official MA dev 648b3538d0b94ee37c3a528e815b7d8703740c54: 331 provider tests passed, one existing skip; 17 standalone tool tests passed; 569 MA config tests passed. Repository pre-commit, scoped upstream pre-commit, core pre-commit, mypy and provider checks passed. MA subsequently advanced to d386236a5a1c359fcb2a54661fbbcdb1f6ccfb78 (audio probing/ffmpeg changes), so the full provider gate is being repeated on that current snapshot before export verification.

Publication: provider PR #273 merged; both guarded exports succeeded with ack_upstream_ahead=false. The core migration was then applied to both fork branches and pushed normally. Final heads:

- Upstream PR #5868: c81e8cd0481b04368bd17f455b9f1b0581fe41f4.
- integration/dev: 78b278e80e02c33b4096c7bf9ae8398432ce5626.
- Provider source dev: 1fb25fb (includes automatic Ruff formatting of the new runtime test).

Both actual exported checkouts passed 341 tests (331 provider + 10 core migration), one existing skip. The complete provider gate also passed on current official MA dev d386236. Config migrations/tests are unchanged between 648b353 and d386236. Upstream GitHub CI on the final head is pending. Reply text is prepared in [the follow-up bundle](pr-5868-followup-replies.json); publication is guarded by exact PR head, successful CI and unchanged discussion contents. The owner must read the new text before using --reviewed-by-human. The earlier 83-thread bundle and owner-edited human_authored flags are left intact.
