# Native MSX acceptance runner

The runner controls only the disposable `ma-msx-e2e` Docker container and an MSX player with an `msx_` ID. Its `/data` mount must be this repository's `.cache/ma-msx-e2e-data`; the provider mount must be this repository's `provider/`. Keep personal MA profiles separate.

Prerequisites: the normal isolated MA container, an unlocked ADB-authorized device with MSX connected to this stand, Docker/ADB access and a free fixture port reachable from the device. UI taps check Android topResumedActivity for the MSX package, then use bounds from one fresh accessibility dump. Python 3.11+ runs the device CLI; compatibility tests require the upstream-pinned Python 3.14 environment.

```bash
# Replace PLAYER_ID and LAN_HOST; use an unused fixture port.
rtk proxy python3 scripts/e2e-msx.py \
  --player PLAYER_ID --host LAN_HOST --port 8094 \
  --manage-observer --rounds 3 --output .cache/msx-repeat.json

# Thirty minutes of ordinary library playback, rather than synthetic tones.
rtk proxy python3 scripts/e2e-msx.py \
  --player PLAYER_ID --host LAN_HOST --port 8094 \
  --manage-observer --soak \
  --media library://track/1 --media library://track/2 \
  --output .cache/msx-ordinary-soak.json
```

`--manage-observer` temporarily starts `scripts/e2e/observer.py` through a private mode-0600 Unix socket. It opens no diagnostic TCP route. The fixed command allowlist restricts player/provider configuration to MSX and core configuration to queue defaults. The runner restores the original container image, command, mounts, environment, player codec/profile/enabled state, repeat/shuffle settings and Android screen timeout in `finally`, then checks normal server health. Assertions or keyboard interrupts do not convert a failed run into PASS. The timeline is attached before playback starts, so a failed or interrupted run retains its partial observations. The report includes the failure type; failure messages and raw server logs are not published. Fixture listeners shut down as their context exits. The disposable queue contents are intentionally replaced.

Without `--manage-observer`, an already-managed diagnostic session owns runtime cleanup. Do not use that mode to leave a diagnostic launcher running on a normal MA instance. A second managed session is rejected.

Repeat Off must play all three 8/11/7-second fixtures and settle idle; One must reset the same item's clock at least twice; All must wrap twice without settling idle. The ordinary soak checks the same queue and at least two wraps, so select a short enough ordinary playlist for that acceptance condition. Snapshots include monotonic timestamps, queue item and playback identity, queue source-time position, native decoder activity and socket count. They omit stream URLs, credentials and Party tokens. Repeat All also requires the native decoder active in at least 90% of samples. Physical audibility and camera QR scanning remain separate checks. A telephone call or user intervention invalidates an uninterrupted soak; record that interruption and rerun rather than silently discarding idle samples.

MA dev intentionally stops a queue after 30 seconds paused. Check that position remains fixed before auto-stop and that Resume restores the saved source position; remaining PAUSED indefinitely is not the current MA contract.

```bash
rtk proxy env MA_MOUNT_MODE=copy ./scripts/test-upstream.sh all
rtk proxy .cache/ma-upstream/server/.venv/bin/python \
  docs/e2e/live-http-checks.py --output .cache/msx-http.json
```

The upstream helper's `all` command updates its disposable checkout. Never point it at a checkout holding core edits. Validate core changes separately with controller tests and `pre-commit run --all-files` in the patched MA checkout. Local standalone mypy may resolve an older installed MA or namespace stubs; the mounted official checkout is the authoritative provider contract check.
