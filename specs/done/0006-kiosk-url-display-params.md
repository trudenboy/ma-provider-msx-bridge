---
id: "0006"
title: "Kiosk display toggles via URL params + URL builder on the status page"
size: S
status: done
priority: P2
effort_minutes: 10
feature_id:
---

## Problem Statement

The kiosk always shows everything: playback controls appear on interaction,
the party QR overlay pops up whenever a party is active, the visualizer and
karaoke lyrics occupy the center column. A dedicated display (bar TV, wall
panel) often wants a reduced view — e.g. art + visualizer only — and there
is no way to configure that. Composing a kiosk URL by hand also requires
reading the docs; the status page only offers fixed links.

## Solution Summary

The kiosk URL accepts four independent display toggles — `controls`,
`party`, `viz`, `lyrics` — each defaulting to on (`=0` disables). Disabled
features are not just hidden but skipped (no party polling, no lyrics
fetches, no analyzer). The status page gains a "Kiosk URL builder": pick
HTML5 or Sendspin variant, tick the four toggles, get a ready link and
copyable URL that update live.

## Acceptance Criteria

1. `controls=0` — the playback control panel never appears, including on
   mouse/touch interaction.
2. `party=0` — the party QR overlay never appears and the kiosk does not
   poll the party status endpoint.
3. `viz=0` — the equalizer/visualizer stays hidden and no Web Audio
   analyzer is started.
4. `lyrics=0` — lyrics are neither fetched nor shown; the center column
   behaves as if the track had no lyrics.
5. Omitted params keep today's behavior exactly (all features on).
6. The status page has a kiosk URL builder with the four toggles and a
   mode choice; the generated link and URL text update live and reflect
   only non-default choices.

## Test Plan

- Integration: `GET /` contains the URL builder (mode select, four named
  checkboxes, output link) — server-rendered markup test.
- Content guard: `web.js` reads all four params (pins the contract names).
- `node --check` smoke test on `web.js` (existing) stays green.
- Manual (browser): each toggle in the builder produces a URL that hides
  exactly the corresponding element; `controls=0` survives mouse move;
  `party=0` shows no requests to the party endpoint in devtools.
