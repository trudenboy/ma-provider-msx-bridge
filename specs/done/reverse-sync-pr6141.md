---
id: "reverse-sync-pr6141"
title: "Use gapless-burst pacing for locally encoded MSX streams"
size: XS
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #6141

Ported from music-assistant/server#6141 into `msx_bridge`.

## Problem Statement

Upstream replaced the removed `SINGLE_ITEM_READRATE` constants with
`output_pacing_args("gapless_burst")` so locally encoded streams keep a large
opening burst for gapless players. This repository already moved that pipeline
into `audio_stream.py` and called `output_pacing_args()` with the default
profile, so reverse-sync against `http_server.py` produced conflict markers
and the wrong burst size.

## Solution Summary

`READRATE_ARGS` now calls `output_pacing_args("gapless_burst")`, matching the
upstream MSX proxy. Tests pin the profile instead of only checking that
ffmpeg received some `-readrate` flags.

## Acceptance Criteria

1. Independent proxy streams pass `output_pacing_args("gapless_burst")` to ffmpeg.
2. Shared-group streams use the same pacing arguments.
3. `provider/http_server.py` is unchanged and contains no conflict markers.

## Test Plan

- `tests/test_http_server.py::test_msx_audio_proxy_paces_output` pins the
  gapless-burst profile on the local proxy.
- `tests/test_group_stream.py::test_shared_stream_paces_output` pins the same
  profile on the shared encoder.
- Run the affected unit tests and ruff against current Music Assistant `dev`.
