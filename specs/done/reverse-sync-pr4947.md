---
id: "reverse-sync-pr4947"
title: "Accept convolution filters in pre-buffered streams"
size: XS
status: done
priority: P1
effort_minutes: 5
---

# Reverse-sync: upstream PR #4947

Ported from music-assistant/server#4947 into `msx_bridge`.

## Problem Statement

Music Assistant output plans can contain both string-based ffmpeg filters and
`ComplexFilter` instances used for DSP convolution. The pre-buffer helper still
declared a mutable `list[str]`, which rejected the complete output-plan type in
static analysis even though the helper only forwards the sequence to ffmpeg.

## Solution Summary

The helper now accepts `Sequence[str | ComplexFilter]`, matching the current
Music Assistant DSP contract without changing runtime stream processing.

## Acceptance Criteria

1. Pre-buffered streams accept string and convolution filters.
2. Filter parameters are forwarded unchanged to `get_ffmpeg_stream`.
3. Existing string-only output plans remain compatible.

## Test Plan

- Run the complete unit suite and lint/type-check workflow against current
  Music Assistant `dev`.
