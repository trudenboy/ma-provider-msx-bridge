# What does this implement/fix?

Updates the MSX Bridge player provider from v1.4.9 to v1.6.0.

Source: [provider repository](https://github.com/trudenboy/ma-provider-msx-bridge), starting from [v1.6.0](https://github.com/trudenboy/ma-provider-msx-bridge/releases/tag/v1.6.0) with fixes [#262](https://github.com/trudenboy/ma-provider-msx-bridge/pull/262) and [#270](https://github.com/trudenboy/ma-provider-msx-bridge/pull/270).

Native MSX playback selects existing queue items instead of replacing the queue, preserves duplicate tracks and long-queue positions, and treats unauthenticated requests as external hardware. Audio delivery uses MA Streamserver redirects by default and an independent per-TV proxy with current source-specific pacing as fallback. Lifecycle, native position reporting, image bounds and cross-origin playlist checks are hardened.

Provider-managed grouping and shared buffers are removed in favor of Universal Groups. The browser kiosk, bundled Sendspin client and kiosk-only routes are removed; browser playback moves to Web Kiosk. Party QR presentation remains, with bounded cover processing and shutdown cleanup.

### Migration and breaking changes

- The legacy `shared` delivery setting migrates to `independent`, preserving individual-TV playback through a local proxy. One producer shared between TVs is no longer provided by MSX Bridge.
- The native grouping setting is removed. Users of provider-managed groups must recreate them as Music Assistant Universal Groups; existing native group membership is not automatically converted.
- The browser kiosk, bundled Sendspin client and kiosk-only routes are removed. Browser kiosk users must switch to the separate Web Kiosk provider. Native MSX menus, playlists and Party QR remain available.
- Redirected finite tracks default to MA’s `forced_content_length` profile for MSX progress reporting. Estimated Content-Length on the independent MP3/AAC proxy can be disabled through its advanced setting; FLAC omits it.

This description covers the complete v1.4.9 → v1.6.0 update. VERSION remains 1.6.0. The maintainer requested including the current compatibility fix (#262) and previous/no-op regression fix (#270) on 2026-10-08. Those follow-ups are not represented as already present in the historical v1.6.0 tag.

**Related issue (if applicable):**

[music-assistant/support#6624](https://github.com/music-assistant/support/issues/6624) reports the unauthenticated audio-path failure in MA 2.10.5. The auth fix is included here; successful Xbox playback still needs user confirmation after delivery.

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

Remaining review decisions are explicit: automatic Party lookup needs an accepted generic contract (#6184 was closed without merge); cross-origin checks are not a control-pairing credential or complete DNS-rebinding defense; native TV seek updates the clock without rebuilding an active progressive HTTP body. Device seek and audible Xbox progression still need runtime confirmation.

Validation: full provider compatibility gate and pre-commit pass against official MA dev 73257004745c8b44be6ef43f0001d6230098020d. The published PR snapshot 0281933ba52d863301cb3da561de874b06884fc5 was separately tested: 324 passed, 1 skipped, mypy passed, upstream lint passed. The PR owner has confirmed compliance with the AI Policy.
