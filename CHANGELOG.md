# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Reverse-synced upstream PR #4613 (WIP)
- Reverse-synced upstream PR #4693 (WIP)
