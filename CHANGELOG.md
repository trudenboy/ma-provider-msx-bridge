# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Local proxy and shared-buffer streams now apply Music Assistant's complete per-player output plan, including DSP and output-channel filters, and report the effective output path for every shared-stream subscriber.

## [1.4.5] - 2026-07-16

- fix(tests): port upstream music-assistant/server#3938 into `tests/conftest.py` — drop the `mass.players.get_plugin_sources` mock (the API was removed upstream in the AudioSource MediaItems refactor; the mock was dead weight and, being unported, made the P0 forward-sync guard fail-closed on every release sync since 2026-05-22).

## [1.4.4] - 2026-07-16

### Changed

- The Sendspin bridge and the redirect stream mode are now enabled by default for new installations. Existing installations keep their stored settings; both can still be turned off in the provider settings.

## [1.4.3] - 2026-07-16

### Fixed

- Redirect stream mode: playback never started when Music Assistant runs behind Docker/NAT, because the TV was redirected to the stream server's internal IP address. The redirect now targets the same host the TV already uses to reach the provider.
- Reloading or disabling the provider could fail with an internal error while closing active TV connections; shutdown is now clean.

## [1.4.2] - 2026-07-16

### Changed

- During a party, simultaneous cover requests from several TVs now share a single fetch and composite instead of each doing the work separately, and the join QR image is rendered once per code rotation instead of on every request.

### Fixed

- Generating the party QR code and stamping it into cover art no longer runs on the server's event loop: a burst of TVs refetching covers right after the join code rotated could briefly stall audio streaming for every connected player. The image work now runs in a worker thread.

## [1.4.1] - 2026-07-13

### Fixed

- During an active party, cover art from streaming services (which resolves to a remote URL) stopped showing during MSX playback: the QR-cover compositor only accepts images hosted by Music Assistant and rejected the remote URL. Such covers are now routed through the Music Assistant image proxy first, so the artwork (with the party QR) shows again.

## [1.4.0] - 2026-07-13

### Added

- Sendspin bridge (experimental, off by default): each TV can be registered as a Sendspin client so it joins sample-synchronized playback groups together with any Music Assistant players — not just other MSX TVs. When a synchronized stream starts, the TV automatically opens the web kiosk in Sendspin mode; if the TV's browser cannot run the Sendspin client, playback transfers back to the regular HTTP player automatically and the failure is logged.
- During an active party, the join QR code is now stamped into the bottom-right corner of the cover art shown by the native MSX player, so guests can scan it without leaving playback. Covers return to normal automatically when the party ends.
- The web kiosk's center equalizer is now a real audio spectrum analyzer driven by the live playback signal (HTTP kiosk mode); the Sendspin kiosk keeps its decorative animation, and browsers without Web Audio fall back to it automatically.
- The kiosk URL accepts four display toggles (`controls`, `party`, `viz`, `lyrics` — on by default, `=0` disables), so dedicated displays can show a reduced view; disabled features are skipped entirely, not just hidden. The provider status page gained a Kiosk URL Builder that composes these links interactively.

### Changed

- The party QR overlay in the web kiosk is now centered at the top of the screen instead of sitting in the top-left corner.

## [1.3.0] - 2026-07-13

### Added

- New "MA Streamserver" stream delivery mode: TVs are redirected to fetch audio directly from the Music Assistant streamserver instead of the provider's own transcoding proxy — one less ffmpeg process per TV, with per-player codec settings and DSP applied by Music Assistant itself. Falls back to the proxy automatically when the direct URL cannot be resolved. The default mode is unchanged.

### Fixed

- Sendspin kiosk mode now works on TVs without internet access and matches current Music Assistant servers: the Sendspin client library is bundled with the provider (previously an outdated version was loaded from a CDN at runtime, which failed on LAN-only setups).

## [1.2.2] - 2026-07-13

### Fixed

- Selecting a track while another playback request was still being set up could serve the previous track's audio to the TV or fail with a spurious timeout; the bridge now explicitly waits for the newly requested track.
- In shared-buffer group mode, simultaneous stream requests from several TVs in the same group could spawn a duplicate audio encoder that kept running with no listeners until the track ended; stream creation is now serialized per group.
- Playback progress and player idle tracking are no longer affected by system clock adjustments: an NTP time step (common on devices without a hardware clock, right after boot) could corrupt the reported track position by hours or unregister all active TVs mid-session.

### Security

- Playback control endpoints now reject cross-site browser requests, so a malicious web page opened on the LAN can no longer pause, stop or skip tracks on TVs (CSRF). TVs, the web player, the dashboard and non-browser automations are unaffected. These endpoints also accept only GET and POST instead of any HTTP method.

## [1.2.1] - 2026-07-11

### Changed

- Provider configuration labels, descriptions and error messages moved to the standard Music Assistant localization file, so they can be translated like any other provider (ported from upstream PRs [#4200](https://github.com/music-assistant/server/pull/4200), [#4259](https://github.com/music-assistant/server/pull/4259), [#4310](https://github.com/music-assistant/server/pull/4310)).
- Album artwork pushed to TVs now uses the standard 512 px image size (ported from upstream).

## [1.2.0] - 2026-07-10

### Added

- Party Mode on the TV: when the Music Assistant Party plugin has guest access enabled, the kiosk shows a QR code with the party name and caption so guests can join from their phones, a Party entry appears in the MSX menu with the same QR on a native TV page, and the QR image plus a small party-status endpoint are exposed over HTTP. Requires no setup on the TV; everything hides automatically when no party is active.

## [1.1.4] - 2026-07-10

### Changed

- Playback started from a TV or the web player is attributed to the owner account using the new Music Assistant impersonation mechanism (ported from upstream PR [#4613](https://github.com/music-assistant/server/pull/4613)).
- Library lists keep showing full item details after Music Assistant switched its library listings to slim summary items by default (ported from upstream PR [#4693](https://github.com/music-assistant/server/pull/4693)).

### Security

- The status dashboard no longer reflects a crafted `Host` header unescaped into the page, closing a reflected-XSS vector (ported from upstream PR [#4562](https://github.com/music-assistant/server/pull/4562)).
- The web player now rejects audio and content URLs that point at a different host and ignores image URLs with non-http(s) schemes such as `javascript:` (ported from upstream PR [#4562](https://github.com/music-assistant/server/pull/4562)).
- Hardened the web player URL check so a same-host URL cannot smuggle a different target via its path, and the status dashboard now HTML-escapes generated player links as a whole (ported from upstream PR [#4662](https://github.com/music-assistant/server/pull/4662)).

## [1.1.3] - 2026-05-09

### Changed

- Rewrote 6 Google-style docstrings (`SharedGroupStream.subscribe`, `MSXBridgeProvider.get_group_id_for_player`, `MSXBridgeProvider.get_or_create_shared_stream`, `MSXBridgeProvider.get_ma_stream_url`) to Sphinx-style `:param:` / `:returns:` per the upstream music-assistant/server CLAUDE.md docstring rule.

## [1.1.2] - 2026-05-09

- fix(provider/models): switch `MsxTemplateType` from `class …(str, Enum)` to `class …(StrEnum)` to satisfy ruff `UP042` from the upstream-synced lint rules.
- fix(scripts/debug-stream-stop): mark standalone debug script with `# ruff: noqa` so upstream-synced lint rules from `ma-provider-tools` don't fail CI on it.
- chore: sync workflow wrappers from ma-provider-tools (CLAUDE.md, ruff/mypy/codespell from upstream music-assistant/server, config-sync CI guard).

## [1.1.1] - 2026-03-03

- chore: sync workflow wrappers from ma-provider-tools (#63) (`c44a0e9`)
- chore: reformat CHANGELOG — marker to top, releases newest-first [skip ci] (`aad1a0c`)
- docs: add user documentation link to README (`f4eff5a`)
- chore: sync workflow wrappers from ma-provider-tools (#62) (`fff6916`)
- docs: add provider icon emblem to index page (`383f974`)
- docs: add development.md (dev environment guide) (`e7d6301`)
- docs: add Starlight title frontmatter to contributing.md (`60719e0`)
- chore: add package-lock.json for npm cache (`1887e51`)
- chore: sync workflow wrappers from ma-provider-tools (#61) (`ab60e86`)
- docs: add contributing page (`95e94a7`)
- docs: add configuration page (`26b1bda`)
- docs: add Starlight docs.yml (`bb8fe80`)
- docs: add Starlight incident-management.md (`ad75ce1`)
- docs: add Starlight dev-docker.md (`43c48a9`)
- docs: add Starlight testing.md (`43f21df`)
- docs: add Starlight index.md (`6ad8bf3`)
- docs: add Starlight content.config.ts (`2d78ef4`)
- docs: add Starlight astro.config.mjs (`075bdf6`)
- docs: add Starlight tsconfig.json (`a3127ea`)
- docs: add Starlight package.json (`ba87c2a`)
- chore: sync workflow wrappers from ma-provider-tools (#60) (`21e211d`)
- docs: add pre-separation upstream PR history to CHANGELOG (`a3bf794`)
- chore: generate historical changelog [skip ci] (`67e3df3`)
- chore: sync workflow wrappers from ma-provider-tools (#59) (`efdc9cf`)
- chore: sync workflow wrappers from ma-provider-tools (#58) (`94dcc25`)
- chore: sync workflow wrappers from ma-provider-tools (#57) (`a65dc88`)
- chore: sync workflow wrappers from ma-provider-tools (#56) (`b9e2d61`)
- chore: sync workflow wrappers from ma-provider-tools (#55) (`861cf42`)
- chore: sync workflow wrappers from ma-provider-tools (#54) (`cbf03f7`)
- chore: sync workflow wrappers from ma-provider-tools (#53) (`7c54e3d`)
- chore: sync workflow wrappers from ma-provider-tools (#52) (`b97838d`)
- chore: sync workflow wrappers from ma-provider-tools (#51) (`25b6b0e`)
- chore: sync workflow wrappers from ma-provider-tools (#50) (`804e4cb`)
- chore: sync workflow wrappers from ma-provider-tools (#49) (`de99ac7`)
- chore: sync workflow wrappers from ma-provider-tools (#48) (`049c7d4`)

---

## [1.1.2] - 2026-05-09

- chore: sync workflow wrappers from ma-provider-tools (#86) (`5090ec7`)
- chore: sync workflow wrappers from ma-provider-tools (#84) (`7c60aed`)
- chore: sync workflow wrappers from ma-provider-tools (#78) (`c323c7b`)
- chore: sync workflow wrappers from ma-provider-tools (#76) (`8905424`)
- chore: sync workflow wrappers from ma-provider-tools (#72) (`dbbd25c`)
- chore: sync workflow wrappers from ma-provider-tools (#70) (`5f92017`)
- chore: add VERSION file (1.1.1) (`24934cc`)
- chore: sync workflow wrappers from ma-provider-tools (#66) (`9447264`)
- fix(http_server): clamp device_id length and correct _get_prefix docstring (`e2e4436`)
- fix(http_server): cancel active streams on stop and escape request.host in dashboard HTML (`ebfea30`)
- fix(lint): shorten _background_tasks comment and restore type: ignore[unreachable] (`f8947e9`)
- fix: address PR #3123 review comments (r2894314958, r2894314991, r2894315022) (`e40d206`)
- Add infographic to README for visual reference (`ea7419e`)
- fix(player): normalize group_members order in set_members (`50e4bd8`)
- fix(tests): remove unused mass_mock args (ruff ARG001) (`71083c4`)
- fix(http_server): address code review security issues from PR #3123 (`dc7626a`)
- fix: remove dead raw_timeout validation and fix XSS in web.js img src (`67c8725`)
- fix(http_server): handle None from request.url.host for mypy compatibility (`21a9f02`)
- fix: address PR review comments (IPv6, viewport, SharedGroupStream EOF hang) (`7198c8d`)
- chore: update changelog for v1.1.1 [skip ci] (`a3abd49`)

---

## [1.1.3] - 2026-05-09

- fix(provider): rewrite 6 Google-style docstrings to Sphinx style (#89) (`0b86afb`)
- chore: update changelog for v1.1.2 [skip ci] (`a02860c`)

---

<!-- changelog entries will be added here by release workflow -->

## 2026-02-22

- fix: address code review — security, correctness, and resource management (`839ba91`)
- Update documentation URL in manifest.json (`3a199f3`)
- fix: simplify IP suffix validation in _player_display_name_from_id() (`7f3a856`)
- fix: address PR #3123 review comments — started event, poll clamping, sdk pin, docstring (`c5dc244`)
- fix: fix mypy narrowing in update_position() bounds check (`c32b698`)
- fix: address PR #3123 review comments — race condition, flag lifecycle, position bounds (`0833ccf`)

## 2026-02-21

- fix: add root conftest.py to make provider importable as music_assistant.providers.msx_bridge (#38) (`e4995f4`)

## 2026-02-20

- Chore/update workflow wrappers (#13) (`0484e75`)
- fix(ci): add type annotations for elapsed_time attrs to satisfy mypy (`7d03d41`)
- fix(ci): ruff 0.14.13 formatting and robust conftest import workaround (#12) (`f8c0baf`)
- fix(ci): resolve all pre-commit lint failures and test import error (#11) (`2dbe200`)
- chore: flatten provider directory structure (#10) (`af4a5e9`)
- fix(shared-stream): skip Phase 2 when producer finished before subscriber registered (`c8c57a5`)

## 2026-02-19

- ci: add release workflow (`2e38dde`)
- ci: add sync-to-fork workflow (`5b45112`)
- fix(web): replace CSS comment separators to avoid false conflict marker detection (`f265267`)
- refactor(msx_bridge): simplify config — remove abort_stream_first, fix defaults (`3478b78`)

## 2026-02-18

- fix(msx_bridge): apply best-practices audit fixes (#6) (`08b3e18`)
- docs: split README into structured docs/ pages (#5) (`bb07013`)
- ci: add mypy type check step to lint job (`410c111`)
- Update README by removing Kiosk mode diagram (`28e4eb5`)
- Update README with images and architecture section (`4f8f189`)
- docs: sync CLAUDE.md and README with current implementation (`948c38b`)
- Add screenshots to README (`31dcec7`)
- sync(msx_bridge): apply all PR #3123 changes from ma-server (`11edf96`)
- fix(msx_bridge): apply pre-commit fixes from ma-server lint pass (`b121835`)
- feat(msx_bridge): apply Dashie Kiosk patterns from PR #3180 (`15f268d`)

## 2026-02-17

- refactor(msx_bridge): split _setup_routes, fix unused lambda arg (`19e8122`)
- fix: address 10 Copilot PR review comments (#3123) (`7d479c3`)
- feat(web): add playback queue panel and kiosk three-column layout (`94901c5`)
- fix(web): bypass autoplay restriction via muted-then-unmute trick (`520ba7e`)
- fix(web): lyrics display, autoplay, and player protocol issues (`f809b0c`)
- fix(msx_bridge): use get_player() for PlayerController compat (`c4fabf3`)
- feat(web): karaoke lyrics overlay in kiosk mode (`e06fa55`)
- feat(web): immersive kiosk mode with full-screen album art and auto-hiding controls (`841c4b6`)
- fix(msx_bridge): replace get_player() with get() for MA PlayerController compat (`eff266b`)
- feat(web): default kiosk mode to HTML5 Audio instead of Sendspin (`cabd6d2`)

## 2026-02-16

- fix(msx_bridge): use get_player() for upstream compat, type: ignore for local (`22f6ab2`)
- fix(tests): add missing mock methods for upstream CI compatibility (`ebfb528`)

## 2026-02-15

- refactor(kiosk): remove MSX kiosk mode, keep web player kiosk/sendspin (`c940389`)
- feat(kiosk): add Sendspin kiosk mode with bundled SDK (experimental) (`5f1612a`)
- feat(kiosk): simplified kiosk mode with hidden menu (`d35f7be`)
- feat(kiosk): use MSX native player like normal mode (`25a7575`)
- fix(kiosk): use content: instead of menu: for kiosk mode (`fcc9330`)
- fix(kiosk): get bridge URL in handleRequest before init (`f622d11`)


<!-- Pre-separation: development in trudenboy/ma-server monorepo -->
<!-- The following changes were developed in the `trudenboy/ma-server` monorepo before this provider was extracted into its own repository on 2026-02-15. -->

## 2026-02-12

- fix: fix playlist start index, foreground player, and MA next/prev

## 2026-02-11

- feat: switch to MSX native playlist playback with per-track streaming
- refactor: optimize player grouping with config toggle, recursion guard, and mypy fixes

## 2026-02-10

- fix: omit Content-Length for flow streams to fix queue playback

## 2026-02-09

- feat: update provider with full MSX UI, search, and audio streaming
- feat: open search keyboard from menu in one click
- feat: instant stop/pause, resume playback, disable fix, quick-stop API

## 2026-02-08

- feat: add MSX Bridge Player Provider
- Reverse-synced upstream PR #5198 (WIP)
