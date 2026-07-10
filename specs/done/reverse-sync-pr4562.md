---
id: "reverse-sync-pr4562"
title: "Fix XSS and cross-host request issues in the web player"
size: S
status: done
priority: P0
effort_minutes: 10
---

# Reverse-sync: upstream PR #4562

Ported from music-assistant/server#4562 into `msx_bridge`.

## Problem Statement

The status dashboard reflected the request `Host` header into the page
without escaping, so a crafted header could inject markup (reflected
XSS). The web player also followed arbitrary absolute URLs from content
payloads, allowing audio/content requests to third-party hosts and
`javascript:` image URLs.

## Solution Summary

The host-derived base URL on the status dashboard is HTML-escaped before
being embedded. In the web player, content and audio URLs are resolved
only when they point at the bridge's own host, and image URLs are
accepted only with http(s) schemes (remote album-art CDNs keep working).

## Acceptance Criteria

1. A request with a crafted `Host` header does not reflect unescaped markup into the dashboard page.
2. Content/audio URLs targeting a different host are rejected by the web player.
3. Relative (`/...`) content and audio URLs keep resolving against the bridge base URL.
4. Album-art images hosted on remote http(s) CDNs still display.
5. Image URLs with non-http(s) schemes (e.g. `javascript:`) are ignored and the art element is hidden.

## Test Plan

- `tests/test_http_server.py::test_root_html_escapes_host_header` pins the Host-header XSS fix.
- Existing dashboard and MSX endpoint tests guard against regressions in page rendering.
- Manual: open the web player, confirm library art from remote CDNs renders and playback works.
