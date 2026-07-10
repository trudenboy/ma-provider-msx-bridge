---
id: "reverse-sync-pr4613"
title: "Attribute bridge-initiated playback via MA impersonation"
size: S
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #4613

Ported from music-assistant/server#4613 into `msx_bridge`.

## Problem Statement

Music Assistant replaced the `username` keyword of the queue `play_media`
call with an impersonation context. With the old call signature the
provider no longer type-checks or runs against current MA, and playback
started from a TV would lose its owner attribution in the play log.

## Solution Summary

Playback requests coming from the MSX audio endpoint and the REST play
endpoint now wrap the queue call in the MA impersonation context for the
owner account, matching the new upstream API. Behaviour visible to the
user is unchanged: tracks started from the TV still appear in the play
log under the owner account.

## Acceptance Criteria

1. Starting a track from an MSX playlist plays it on the correct player.
2. Starting a track via the REST play endpoint plays it on the correct player.
3. Playback started from the bridge is attributed to the owner account in the MA play log.
4. The provider type-checks against current MA (no unknown keyword arguments).
5. Existing playback tests pass without asserting the removed keyword.

## Test Plan

- `tests/test_http_server.py::test_play_track` pins the new `play_media` call signature.
- Full `tests/test_http_server.py` suite covers the MSX audio endpoint flow.
- Manual: start a track from a TV and confirm it appears in the MA play log.
