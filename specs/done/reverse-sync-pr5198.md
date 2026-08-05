---
id: "reverse-sync-pr5198"
title: "Report the served stream duration after seeking"
size: S
status: done
priority: P1
effort_minutes: 15
---

# Reverse-sync: upstream PR #5198

Ported from music-assistant/server#5198 into `msx_bridge`.

## Problem Statement

When Music Assistant starts playback from a seek position, the stream sent to
the TV contains only the remaining part of the track. The provider continued to
advertise and clamp progress against the original media duration, so MSX showed
an incorrect total length and could report progress beyond the served stream.

## Solution Summary

The HTTP routes and player state now prefer `PlayerMedia.stream_duration` over
the original media duration. Queue-item duration remains a fallback when the
stream metadata does not contain a usable duration.

## Acceptance Criteria

1. Audio responses advertise the shortened stream duration after a seek.
2. WebSocket position reports cannot exceed the served stream duration.
3. Wall-clock polling cannot advance beyond the served stream duration.
4. Original media and queue-item durations remain valid fallbacks.

## Test Plan

- HTTP tests cover media duration, stream-duration priority, and queue fallback.
- Player tests cover position-report and polling clamps after a seek.
- Run the complete unit suite and lint/type-check workflow.
