# Reverse-sync: upstream PR #5944

Ported from music-assistant/server#5944 into `msx_bridge`.

## Summary

Routes group member playback through Music Assistant's internal player handlers
to release stale live-source sessions without redirecting back to the leader.

## Completion

Merged in provider PR #226. The later Universal Groups migration in #261
retired provider-managed group propagation; this is completed historical work,
not a request to restore that code.
