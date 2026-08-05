# Reverse-sync upstream PR 5017 Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Port `music-assistant/server#5017` into the standalone MSX Bridge provider and restore forward-sync parity with both maintained downstream branches.

**Architecture:** Keep the standalone provider as the source of truth while matching the upstream inlined provider after the repository path transform. Move provider configuration entries from the module-level hook to `MSXBridgeProvider.get_config_entries()`, read the grouping option from raw stored configuration during `setup()`, and adopt the simplified per-player configuration method contract. Land the reverse-sync as a dedicated PR, then release the next patch version so both `integration/dev` and `upstream/msx_bridge` receive the corrected tree.

**Tech Stack:** Python 3.12+, Music Assistant provider APIs, pytest/pytest-asyncio, ruff, mypy, pre-commit, GitHub Actions, ma-provider-tools sync guards.

---

### Task 1: Capture the upstream contract in tests

**Files:**
- Modify: `tests/test_init.py`
- Modify: `tests/test_sendspin_bridge.py`

- [x] Port the upstream test calls from the removed module-level helper to the live provider instance.
- [x] Update the grouping-disabled setup fixture to expose the raw stored provider option used during construction.
- [x] Run the two focused test modules and confirm they fail against the old implementation for the expected missing instance method/raw-option behavior.

### Task 2: Port the provider configuration contract

**Files:**
- Modify: `provider/__init__.py`
- Modify: `provider/provider.py`
- Modify: `provider/player.py`

- [x] Move all provider option entries unchanged into `MSXBridgeProvider.get_config_entries()`.
- [x] Change `setup()` to read `CONF_ENABLE_GROUPING` through Music Assistant's raw provider-config accessor before option entries are resolved.
- [x] Simplify `MSXPlayer.get_config_entries()` to the current no-argument instance contract.
- [x] Run the focused tests and confirm they pass.

### Task 3: Document and verify the reverse-sync

**Files:**
- Modify: `CHANGELOG.md`

- [x] Add a `1.4.7` Changed entry crediting and linking upstream PR #5017 without changing `VERSION` in the reverse-sync PR.
- [x] Run the full local test suite, ruff format/check, mypy, and pre-commit.
- [x] Transform the standalone tree into upstream layout and run the exact upstream-ahead/parity check against `music-assistant/server:dev`.
- [x] Review the complete diff for unrelated changes and upstream semantic parity.

### Task 4: Publish and merge the reverse-sync PR

- [ ] Commit with upstream author credit (`Co-authored-by: Marcel van der Veldt`).
- [ ] Push `reverse-sync/msx_bridge-pr5017` and open a draft PR targeting `feat/msx-bridge-player-provider` with the upstream link and test evidence.
- [ ] Inspect CI and review threads, fix actionable feedback, mark ready, and merge under the maintainer authorization already given in this session.

### Task 5: Release and synchronize both maintained trees

**Files:**
- Modify: `VERSION`

- [ ] Create a separate maintainer release PR bumping `VERSION` from `1.4.6` to `1.4.7`.
- [ ] Verify the release PR and merge it after green checks.
- [ ] Monitor the release pipeline until the GitHub release, `integration/dev` sync, and `upstream/msx_bridge` sync all succeed.
- [ ] Re-run transformed-tree parity checks against both downstream branches and confirm no open reverse-sync PR remains.
