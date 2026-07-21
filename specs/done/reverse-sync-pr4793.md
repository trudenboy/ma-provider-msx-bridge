---
id: "reverse-sync-pr4793"
title: "Apply and report complete MSX audio output processing"
size: S
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #4793

Ported from music-assistant/server#4793 into `msx_bridge`.

## Problem Statement

MSX streams served through the provider's local proxy or shared-buffer
pipeline did not apply Music Assistant's complete per-player output plan.
Configured DSP, channel mapping, and limiter filters could therefore be
missing from the encoded stream, while the UI could not show the effective
output processing path for TVs sharing a stream.

## Solution Summary

The provider now requests an output plan for every locally encoded stream,
passes its filters to ffmpeg, retains the leader's plan on a shared stream,
and registers that plan for each subscribing TV using the queue session and
item identifiers supplied by Music Assistant.

## Acceptance Criteria

1. Independent proxy streams pass the selected output-plan filters to ffmpeg.
2. Shared-buffer streams encode once with the leader's output-plan filters.
3. Each shared-stream subscriber reports the retained plan as its effective output.
4. Output reporting is scoped to the active queue session and queue item.
5. Streams without queue-session metadata continue playing without output reporting.

## Test Plan

- `tests/test_http_server.py::test_msx_audio_redirect_mode_falls_back_to_proxy` verifies that the local fallback passes output-plan filters to ffmpeg.
- Existing shared-stream tests cover producer reuse, concurrent subscribers, replacement serialization, and cleanup with the new retained-plan field present.
- Run the complete unit suite and lint/type-check workflow against current Music Assistant `dev`.
