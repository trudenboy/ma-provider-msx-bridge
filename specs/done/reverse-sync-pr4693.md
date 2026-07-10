---
id: "reverse-sync-pr4693"
title: "Request full library items after MA's slim-summary default"
size: S
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #4693

Ported from music-assistant/server#4693 into `msx_bridge`.

## Problem Statement

Music Assistant changed its library list endpoints to return slim
summary items by default. The bridge renders artwork, artist strings and
playable URIs from those listings, so with summary items the MSX pages,
playlists and REST API would lose detail or break playback.

## Solution Summary

Every library listing call the bridge makes (MSX content pages, MSX
native playlists, recently played, and the REST API list endpoints) now
explicitly requests full items, preserving the exact behaviour from
before the upstream default changed.

## Acceptance Criteria

1. MSX album, artist, playlist and track pages render names, artwork and subtitles as before.
2. MSX native playlist endpoints produce playable entries with full track metadata.
3. The recently-played page and playlist keep working with full track details.
4. REST API list endpoints return the same item fields as before the upstream change.
5. The provider type-checks against current MA (the listing calls match the new signature).

## Test Plan

- `tests/test_http_server.py` list-endpoint tests cover the affected routes end to end.
- mypy over the provider pins the new `library_items` call signature.
- Manual: browse albums/artists/playlists from a TV and confirm artwork and playback.
