---
id: "reverse-sync-pr5482"
title: "Keep player grouping independent of user visibility"
size: S
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #5482

Ported from music-assistant/server#5482 into `msx_bridge`.

## Problem Statement

Music Assistant now separates the player list exposed to an authenticated user
from the unscoped registry used by provider internals. Provider tests still
mocked the user-filtered lookup, so they no longer represented the ownership
contract used during MSX player teardown. This also made the reverse-sync gate
fail after the core API changed.

## Solution Summary

The MSX test environment now exposes the unscoped player iterator and provider
teardown tests populate that iterator. The provider therefore continues to
exercise its inherited ownership view rather than a user-filtered API.

## Acceptance Criteria

1. The shared Music Assistant mock exposes the unscoped player iterator.
2. Provider unload discovers every owned MSX player through that iterator.
3. Unload unregisters each discovered player after stopping the HTTP server.
4. Unload remains safe when no HTTP server or owned player exists.
5. Tests remain compatible with the current Music Assistant player-provider contract.

## Test Plan

- `tests/test_provider.py::test_unload_stops_server_first` verifies that the
  inherited provider ownership view discovers and unregisters the MSX player.
- `tests/test_provider.py::test_unload_no_server` verifies empty teardown.
- Run the complete provider unit suite and pre-commit gate against current
  Music Assistant `dev`.
