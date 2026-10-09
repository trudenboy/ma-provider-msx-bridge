# What does this implement/fix?

Makes native MSX playback follow the MA queue, including selected duplicate occurrences, natural EOF and Repeat Off/One/All. Streaming uses chunked delivery instead of estimated MP3/AAC sizes; disabled players reject new playback, and server restart recovers the native WebSocket automatically. Native seek rebuilds the MA stream with source-time labels; search cancellation, Party QR captions and immediate Stop are also corrected.

**Breaking migration:** removes provider-native grouping, shared producers, the embedded browser kiosk and bundled Sendspin client. Before provider loading, MA clears the retired switches and converts stored `shared` delivery to `independent`, including disabled instances. Recreate groups as Universal Groups; use the separate [Web Kiosk provider](https://github.com/trudenboy/ma-provider-web-kiosk) for browser playback. Explicit existing HTTP profiles are preserved; new MSX players default to chunked delivery.

Validation: official MA dev compatibility gate passes; patched MA provider/controller/migration tests: **1010 passed, 1 skipped**; full MA pre-commit passes. Pixel 8 repeat and MP3/AAC/FLAC delivery checks pass. Current Samsung Tizen/group compatibility, camera QR scanning and acoustic seek-marker confirmation remain unverified. No new release or tag is created.

Related issue: [music-assistant/support#6624](https://github.com/music-assistant/support/issues/6624).

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
