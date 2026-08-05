---
id: "reverse-sync-pr5201"
title: "Remove unreachable standalone queue metadata lookup"
size: XS
status: done
priority: P2
effort_minutes: 10
---

# Reverse-sync: upstream PR #5201

Ported from music-assistant/server#5201 into `msx_bridge`.

## Problem Statement

The standalone playback path called a queue metadata resolver even though
queue-backed media is handled by the native MSX playlist branches before that
path is reached. The resolver's queue lookup was therefore unreachable and made
the notification flow harder to follow.

## Solution Summary

Standalone playback now sends title, artist, artwork, and duration directly
from `PlayerMedia`. The unused resolver is removed while the served-duration
helper introduced by upstream PR #5198 remains in place for progress clamping.

## Acceptance Criteria

1. Standalone media sends its `PlayerMedia` metadata to the TV.
2. Queue-backed media continues to use native playlist notifications.
3. The unused queue metadata resolver and all conflict markers are removed.
4. Served-duration progress handling remains unchanged.

## Test Plan

- The standalone playback test verifies the complete notification payload.
- Existing queue tests verify playlist and goto-index routing.
- Run the complete unit suite and lint/type-check workflow.
