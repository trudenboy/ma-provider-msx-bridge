# What does this implement/fix?

Updates the bundled MSX Bridge player provider from v1.4.9 to v1.6.0. This includes the changes across the intervening provider releases, not only the last three fixes.

### Changes from the bundled v1.4.9

- **Queue playback:** selecting an album or playlist in MSX prepares the Music Assistant queue. Playback uses existing queue-item identity instead of replacing or repeatedly appending to the queue. Duplicate tracks, URL-backed radio/audio sources, long queues and start indexes above 10,000 retain their intended position. Native next/previous and track completion follow the MA queue; a no-op at either end does not restart the current track, while repeat-one still restarts intentionally.
- **TV controls and progress:** native pause/resume and seek reports update MA state, including seeks while paused or before the first progress sample. Actual native item transitions reset the TV clock without reloading its playlist, while same-item resume retains the paused position. Playback resets and overlapping commands no longer leave stale clocks or clear another command's WebSocket notification suppression. These changes report native seek to MA; they do not rebuild an HTTP response already consumed by the TV.
- **Audio delivery and lifecycle:** the recommended default redirects playback to the MA Streamserver. An advanced independent proxy remains available for MP3/AAC/FLAC, with source-specific pacing, bounded buffering and cleanup on disconnect, stop or shutdown. Expected producer failures return HTTP 503 before audio headers and abort incomplete responses after startup. Optional MP3/AAC size estimates cover the full duration, including recordings longer than twelve hours. MSX players accept Universal Group member flow URLs. Finite redirected tracks use MA's `forced_content_length` profile for progress reporting; the independent MP3/AAC proxy has an option to omit estimated Content-Length, and FLAC omits it.
- **Authentication and request handling:** unauthenticated TV playback is treated as external hardware rather than impersonating a user. Audio URLs require the player's stream token and cannot select arbitrary stream addresses. Browser control, WebSocket and token-bearing playlist requests reject cross-origin requests; native Origin-less MSX remains supported. Malformed JSON and invalid position reports are rejected. Expected playback failures receive appropriate HTTP responses; unexpected programming errors remain visible.
- **Native menus and Party covers:** search retains the source provider and supports older MSX clients; album ordering is deterministic even when sort fields match. Party QR presentation remains available. Cover fetch origins, downloaded bytes, image dimensions, render concurrency and cached PNG bytes are bounded. The compositor no longer changes Pillow's global image limit, and shutdown cancels its owned work.
- **Removed modes:** provider-managed groups, shared audio producers, the browser kiosk, bundled Sendspin client and kiosk-only routes are removed. Their replacement and upgrade behavior are described below; improvements to retired implementations in intermediate releases are not features of this final snapshot.

### Migration and breaking changes

- **Shared buffer streaming enabled:** the stored `shared` delivery setting is migrated to `independent` in MA core before providers are loaded, including disabled instances. Each TV uses its own local proxy/encoder; one shared producer is no longer available. Individual-TV playback remains, but resource use and multi-TV delivery change. This migration does not recreate a group or promise the old shared-buffer synchronization behavior.
- **Provider-managed player grouping enabled:** the legacy grouping setting is removed from persisted config even when stored as false or null. Existing native MSX group membership is not converted automatically and the bridge no longer fans commands out to those groups. Recreate the desired membership as a Music Assistant Universal Group. The individual MSX players remain usable as regular players and group members.
- **Browser kiosk or Sendspin mode in use:** the embedded web player, kiosk launcher option, bundled Sendspin client and kiosk-only lyrics/queue endpoints are removed. Use the separate [Web Kiosk provider](https://github.com/trudenboy/ma-provider-web-kiosk) for browser playback. Native MSX menus, playlists and Party QR remain available.

The dominant change type is **breaking-change**, because existing grouping and shared-buffer setups require migration. The PR is not classified as a non-breaking enhancement.

### Fixed scope for this review

The provider VERSION is held at **1.6.0**. The code under review is head `c81e8cd0481b04368bd17f455b9f1b0581fe41f4`, based on official MA dev `d386236a5a1c359fcb2a54661fbbcdb1f6ccfb78`.

This snapshot starts from the [historical v1.6.0 release](https://github.com/trudenboy/ma-provider-msx-bridge/releases/tag/v1.6.0) and includes provider [#262](https://github.com/trudenboy/ma-provider-msx-bridge/pull/262) (current MA pacing compatibility), [#270](https://github.com/trudenboy/ma-provider-msx-bridge/pull/270) (previous/no-op) and [#271](https://github.com/trudenboy/ma-provider-msx-bridge/pull/271) (a regression guard against loading the same provider module twice), plus review-driven [#273](https://github.com/trudenboy/ma-provider-msx-bridge/pull/273) (startup failures, long-item lengths, native clock transitions and MA core settings migration). These later fixes are not claimed to be present in the published v1.6.0 tag; no new release/tag was created for them.

Review proceeds against this snapshot. Further features, version upgrades and module rewrites belong in follow-up PRs. Any correction required by this review should be identified with its regression/evidence rather than introducing another release's changes.

### Review evidence and remaining decisions

The [review audit](https://github.com/trudenboy/ma-provider-msx-bridge/blob/tooling/pr-5868-reviewed-replies/docs/pr-5868-review-evidence.md) maps all 83 inline threads to implemented behavior, removed paths or pending decisions. Resolution alone is not evidence that a concern was fixed. At the first-round audit, all 83 threads were marked resolved and had inline replies. Four additional Copilot threads were then reviewed and fixed in #273 and the accompanying MA core migration; their response drafts are prepared in the [follow-up audit](https://github.com/trudenboy/ma-provider-msx-bridge/blob/fix/msx-review-startup-clock-migration/docs/pr-5868-followup-review.md). The 47 previously unanswered threads received the owner-reviewed explanations on 2026-10-08; each published reply was checked against the reviewed text, with no duplicates. The previous/no-op thread also has an author reply. These explanations distinguish implemented fixes, removed paths and the remaining decisions below; a resolved flag does not establish that those decisions are complete.

The following limits remain explicit:

- Party discovery still needs an accepted generic contract; [#6184](https://github.com/music-assistant/server/pull/6184) was closed without merge.
- Cross-origin checks do not provide a control-pairing credential or complete DNS-rebinding protection.
- Native TV seek updates the MA clock without replacing an active progressive HTTP body. Seeking beyond buffered audio and audible Xbox queue progression need device confirmation.

**Related issue (if applicable):**

[music-assistant/support#6624](https://github.com/music-assistant/support/issues/6624) reports unauthenticated playback failure in MA 2.10.5. This PR includes the auth correction; it does not deliver a stable backport or establish successful playback on the affected Xbox.

## Types of changes

- [ ] Bugfix (non-breaking change which fixes an issue) — `bugfix`
- [ ] New feature (non-breaking change which adds functionality) — `new-feature`
- [ ] Enhancement to an existing feature — `enhancement`
- [ ] New music/player/metadata/plugin provider — `new-provider`
- [x] Breaking change (fix or feature that would cause existing functionality to not work as expected) — `breaking-change`
- [ ] Refactor (no behaviour change) — `refactor`
- [ ] Documentation only — `documentation`
- [ ] Maintenance / chore — `maintenance`
- [ ] CI / workflow change — `ci`
- [ ] Dependencies bump — `dependencies`

## Checklist

- [x] The code change is tested and works locally.
- [x] `pre-commit run --all-files` passes.
- [x] `pytest` passes, and tests have been added/updated under `tests/` where applicable.
- [ ] For changes to shared models, the companion PR in `music-assistant/models` is linked.
- [ ] For changes affecting the UI, the companion PR in `music-assistant/frontend` is linked.
- [x] I have read and complied with the project's [AI Policy](https://github.com/music-assistant/.github/blob/main/AI_POLICY.md) for any AI-assisted contributions.
- [ ] I have raised a PR against the documentation repository targeting the main or beta branch as appropriate.

Validation of the actual published snapshot: **341 passed, 1 skipped** (331 provider tests and 10 MA core migration tests) on both the PR and integration trees. The complete provider compatibility gate passed against official MA dev `d386236`; mypy and repository/scoped pre-commit passed. The MA config suite passed **569 tests**, and the standalone reply-publishing tool passed **17 tests**; that tool is outside the upstream provider snapshot. [Upstream Test on the final head](https://github.com/music-assistant/server/actions/runs/37833590467) completed successfully on this final head. The PR stays draft while review and the remaining decisions are completed.

The [latest Xbox reporter follow-up](https://github.com/music-assistant/support/issues/6624#issuecomment-6067212411) explicitly says these changes have not been installed on the reported HA add-on 2.10.5 setup. The reporter is ready to test an installable build by allowing an audible first track to end naturally and confirming that the second is audible, HA media_position advances, and the next audio request no longer logs InsufficientPermissions. Manual Next is excluded because it skips the silent queue item on the affected version. No device success or stable backport is claimed.
