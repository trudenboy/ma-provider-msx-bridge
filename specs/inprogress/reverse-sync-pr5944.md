# Reverse-sync: upstream PR #5944

Ported from music-assistant/server#5944 into `msx_bridge`.

## Summary

Routes group member playback through Music Assistant's internal player handlers
to release stale live-source sessions without redirecting back to the leader.
