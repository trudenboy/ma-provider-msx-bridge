---
id: "0002"
title: "MA Streamserver redirect stream delivery mode"
size: S
status: done
priority: P1
effort_minutes: 10
feature_id:
---

## Problem Statement

Every track played on a TV is transcoded twice: Music Assistant decodes the
source to PCM, and the provider then runs its own ffmpeg process to re-encode
it for the TV — per TV, per track. This burns CPU on the MA host, duplicates
logic MA already has (per-player codec choice, DSP), and relies on fragile
Content-Length heuristics. Music Assistant now exposes its own streamserver
URL for exactly this purpose, and every other HTTP-pull player (Chromecast,
Sonos, WiiM, Squeezelite) fetches audio from it directly. The provider's
"redirect" mode existed only as an inactive scaffold that pointed at a
non-existent endpoint and was hidden from the config UI.

## Solution Summary

The stream delivery mode option gains a third value, "MA Streamserver":
when selected, the TV's audio request is answered with a redirect to the URL
resolved by Music Assistant's streamserver, so the TV pulls audio straight
from MA with the player's own codec config and DSP applied by the core. When
the URL cannot be resolved, the provider transparently falls back to the
existing local proxy pipeline. The default mode stays unchanged until the
redirect path is validated on real TVs.

## Acceptance Criteria

1. The provider config UI offers a third stream delivery option ("MA
   Streamserver") alongside Independent and Shared Buffer.
2. With redirect mode selected, a TV audio request receives an HTTP 302
   whose Location is the URL resolved by the MA streamserver for that
   player and media.
3. The per-TV output codec setting keeps working in redirect mode (the MA
   streamserver reads the same per-player codec config).
4. When URL resolution fails (no queue session, streamserver error), the
   request is served by the local proxy pipeline instead of failing.
5. The default stream delivery mode remains Independent — existing
   installations see no behavior change without opting in.

## Test Plan

- Unit: `get_ma_stream_url` returns the URL from the MA streamserver API and
  passes the correct player id and media.
- Unit: `get_ma_stream_url` returns None when resolution raises, without
  propagating the error.
- Integration: with redirect mode enabled, `GET /msx/audio/...` responds 302
  with the resolved URL as Location.
- Integration: with redirect mode enabled and resolution failing, the same
  request streams audio through the proxy (200, body served).
- Config: the stream mode entry lists exactly independent/shared/redirect.
- Manual: real TV playback in redirect mode (verify MSX accepts the
  streamserver's chunked response without Content-Length).
