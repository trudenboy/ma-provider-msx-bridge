# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

<!-- changelog entries will be added here by release workflow -->
