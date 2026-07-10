---
id: "reverse-sync-pr4662"
title: "Harden MSX bridge against host-header XSS and cross-origin fetches"
size: S
status: done
priority: P0
effort_minutes: 10
---

# Reverse-sync: upstream PR #4662

Ported from music-assistant/server#4662 into `msx_bridge`.

## Problem Statement

Follow-up hardening on top of upstream PR #4562: the web player's
same-host URL check still returned the original URL string, so a
same-host URL whose path starts with `//` could be reinterpreted by the
browser as a different host. The status dashboard also escaped only the
base prefix of generated links, leaving the composed sendspin URLs
(query separators included) unescaped inside `href` attributes.

## Solution Summary

The web player rebuilds accepted content/audio URLs from their parsed
path and query against the bridge's own base URL, so the target host can
never be smuggled through the path. The status dashboard HTML-escapes
each composed sendspin link as a whole before embedding it.

## Acceptance Criteria

1. A same-host content URL with a `//host/path`-style path is fetched from the bridge, never a third-party host.
2. A crafted `Host` header cannot break out of `href` attributes on the dashboard (quotes are escaped).
3. Sendspin links on the dashboard render with `&amp;`-escaped query separators.
4. Relative (`/...`) content and audio URLs keep resolving against the bridge base URL.
5. Dashboard quick-stop forms and web/kiosk links keep working for registered players.

## Test Plan

- `tests/test_http_server.py::test_root_html_escapes_host_header` pins attribute breakout via the `Host` header.
- `tests/test_http_server.py::test_root_html_sendspin_urls_escaped` pins whole-URL escaping of sendspin links.
- Manual: open the dashboard and web player, confirm links and playback work.
