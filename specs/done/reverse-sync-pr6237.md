# Reverse-sync: upstream PR #6237

Ported from music-assistant/server#6237 into the extracted AudioPipeline.

## Summary

Replace the retired gapless_burst profile with current PacingProfile values.
Buffered tracks use DEFAULT, radio, continuous group flows and just-in-time tracks use NEAR_REALTIME,
and live AUDIO_SOURCE playback uses LOW_LATENCY. Preserve the local module
extraction and retired kiosk/group-buffer removal rather than restoring the
old upstream monolithic HTTP server.

The previous pacing regression test asserted a profile that upstream deleted;
it now checks the public HTTP audio response and source-specific arguments
passed to the external ffmpeg boundary against the actual MA pacing API.

The compatibility setup reinstalls current upstream dependencies when reusing
its disposable environment, so a source update cannot silently keep old model
contracts. VERSION remains maintainer-owned.

## Verification

Red: actual MA dev fails at import with KeyError: gapless_burst. After enabling
the current default, radio and realtime-track regression cases fail until
source-aware pacing is selected. Live-source coverage rejects a radio profile
for AUDIO_SOURCE playback. Full gate results are recorded in the PR body.
