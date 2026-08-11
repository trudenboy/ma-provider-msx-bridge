---
id: "reverse-sync-pr5453"
title: "Observe shared QR render failures without duplicate loop errors"
size: S
status: done
priority: P1
effort_minutes: 10
---

# Reverse-sync: upstream PR #5453

Ported from music-assistant/server#5453 into `msx_bridge`.

## Problem Statement

Several TVs can wait for the same Party QR cover render. If one request was
cancelled and the shared render subsequently failed, Python 3.14 could report
the failure through the event loop as an additional `exception in shielded
future` traceback even though the remaining request and provider cleanup had
already observed it.

## Solution Summary

The shared render is now awaited with Music Assistant's `join_task` helper.
Cancelling one HTTP request still leaves the render alive for other TVs and the
cache, while a later result or failure is observed without creating an
unowned shield future.

## Acceptance Criteria

1. Multiple TV requests continue to share one QR cover render task.
2. Cancelling one request does not cancel the shared render.
3. A remaining request observes a render failure and falls back to the source cover.
4. The failed render is removed from the in-flight task registry.
5. The event loop receives no duplicate shielded-future error report.

## Test Plan

- `tests/test_party_qr_cover.py::test_qr_cover_render_failure_after_cancellation_logs_no_loop_error`
  cancels one waiter, fails the shared fetch, checks the surviving request's
  redirect, and asserts that the loop exception handler remains empty.
- Run the complete QR-cover and provider unit suites against current Music
  Assistant `dev`, followed by the pre-commit gate.
