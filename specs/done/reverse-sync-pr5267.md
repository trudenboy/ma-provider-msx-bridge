---
id: "reverse-sync-pr5267"
title: "Use the core Sendspin server port in generated links"
size: XS
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #5267

Ported from music-assistant/server#5267 into `msx_bridge`.

## Problem Statement

The provider duplicated the built-in Sendspin port as the literal `8927` when
building status-page links. That value could diverge from the Music Assistant
server constant, causing remote-access and reverse-proxy links to target the
wrong endpoint.

## Solution Summary

Generated Sendspin URLs and the status-page example now use
`SENDSPIN_SERVER_PORT` from `music_assistant.constants`, keeping the provider in
sync with the core server configuration.

## Acceptance Criteria

1. Generated Sendspin web and kiosk links use the core server port constant.
2. The custom URL example displays the same port.
3. Host escaping and URL encoding remain unchanged.

## Test Plan

- Patch the imported port constant and verify the generated root-page URL uses
  the patched value.
- Run the complete unit suite and lint/type-check workflow against current
  Music Assistant `dev`.
