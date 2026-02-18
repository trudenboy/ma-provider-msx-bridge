[Back to README](../README.md) · [Architecture →](architecture.md)

# Getting Started

## Prerequisites

- [Music Assistant](https://music-assistant.io/) server (or the [MA server fork](https://github.com/trudenboy/ma-server))
- [Media Station X](https://msx.benzac.de/) app installed on your Smart TV
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (used by MA for venv management)

## Installation

```bash
# 1. Clone repos side by side
cd ~/Projects
git clone https://github.com/trudenboy/msx-music-assistant.git
git clone https://github.com/trudenboy/ma-server.git   # if not already done

# 2. One-command setup: creates venv, installs deps, symlinks provider
cd msx-music-assistant
./scripts/link-to-ma.sh

# 3. Start the MA server (provider auto-loads)
source ../ma-server/.venv/bin/activate
cd ../ma-server && python -m music_assistant --log-level debug
```

The provider starts an HTTP server on port `8099` by default. You can change this in MA Settings → MSX Bridge Provider.

## Configure Your TV

1. Open the **MSX app** on your Smart TV
2. Go to **Settings → Start Parameter**
3. Enter: `http://<YOUR_SERVER_IP>:8099/msx/start.json`
4. Restart MSX

The TV will load the menu automatically on next start.

## Verify It Works

Open the status dashboard in a browser:

```
http://<YOUR_SERVER_IP>:8099/
```

You should see:
- Provider status: **running**
- Registered players (appears after the TV connects for the first time)
- Quick-stop buttons per player

If the TV connected successfully, it will appear as a player in Music Assistant (under **Players**).

## What Happens Next

1. Browse your MA library on the TV (Albums, Artists, Playlists, Tracks, Search)
2. Click a track or album — playback starts on the TV
3. Control playback from the MA UI, the TV remote, or the [browser web player](web-player.md)

## See Also

- [Architecture](architecture.md) — how the provider and TV communicate
- [Configuration](configuration.md) — change port, audio format, timeout settings
- [Development](development.md) — run tests, lint, contribute code
