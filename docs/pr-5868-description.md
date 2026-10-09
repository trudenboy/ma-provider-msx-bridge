# What does this implement/fix?

Updates MSX Bridge from the bundled 1.4.9 to provider VERSION 1.6.0, with the later review fixes in this PR. TV selection and native playback follow the MA queue, including duplicate occurrences and no-op next/previous. Container selection explicitly replaces the queue regardless of the user's enqueue default. Pause/resume, native seek reports and track changes keep the playback clock and WebSocket suppression state consistent.

Audio delivery defaults to the MA Streamserver. The advanced independent MP3/AAC/FLAC proxy uses current MA pacing, bounded buffering and cancellation, returns 503 for startup failures, and aborts incomplete responses after startup. Optional MP3/AAC size estimates cover the full served duration. Unauthenticated TV playback uses the external-hardware context; audio URLs require a per-player token, and browser control and token-bearing playlists reject cross-origin requests.

**Breaking migration:** provider-native grouping, shared producers, the embedded browser kiosk and bundled Sendspin client are removed. Before provider loading, MA core clears both retired grouping/Sendspin switches and converts stored `shared` delivery to `independent`, including disabled instances and false/null values. Recreate native groups as Universal Groups; group membership is not converted automatically. Use the separate [Web Kiosk provider](https://github.com/trudenboy/ma-provider-web-kiosk) for browser playback. Native MSX menus, playlists and Party QR presentation remain.

**Reviewed snapshot:** `3b99570efe098e96e7ee7ee196443ebd2f8d6f3c`, based on official MA dev `d22d28c087ded4289c67c8121c7697f02d9f6e62`. Review corrections are recorded in [provider #276](https://github.com/trudenboy/ma-provider-msx-bridge/pull/276) and the [review evidence](https://github.com/trudenboy/ma-provider-msx-bridge/blob/fix/msx-ozgav-review-followup/docs/pr-5868-ozgav-followup-review.md). They are subsequent fixes to the historical 1.6.0 release; no new release or tag was created. Local validation: **420 passed, 1 skipped** (provider and core migrations), **352 passed, 1 skipped** on integration/dev, full provider and MA pre-commit including mypy, and documentation build.

Remaining limits: Party discovery still needs an accepted generic contract (#6184 closed without merge). Cross-origin checks do not provide control pairing or complete DNS-rebinding protection. Native seek reports update the MA clock; seeking into audio that has not loaded is untested and may not work. Indexed container selection still uses play_index after replacement to preserve duplicate occurrences. Automatic transition was observed on Samsung Tizen; audible Xbox progression, HA position reporting on that device and a stable backport remain unverified. The unloaded-audio seek note is included in provider docs; a matching official-site patch is prepared, with no documentation PR submitted yet.

**Related issue (if applicable):** [music-assistant/support#6624](https://github.com/music-assistant/support/issues/6624). The reporter can test the [DEV app build](https://github.com/music-assistant/support/issues/6624#issuecomment-6068187801) by allowing two tracks to transition naturally; manual Next does not reproduce the reported failure.

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
