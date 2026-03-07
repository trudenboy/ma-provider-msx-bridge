# MSX Music Assistant Bridge

English | [Русский](README.ru.md)

📖 <a href="https://trudenboy.github.io/ma-provider-msx-bridge/">User Documentation</a>

> Stream your [Music Assistant](https://music-assistant.io/) library to Smart TVs through [Media Station X](https://msx.benzac.de/) with a native TV-optimized interface.
<img width="2752" height="1536" alt="msx_infographic" src="https://github.com/user-attachments/assets/287fb05b-6a15-49c0-bc46-2af3afbc11d4" />

## Quick Start

```bash
# Clone alongside the MA server
git clone https://github.com/trudenboy/msx-music-assistant.git
cd msx-music-assistant

# Setup venv, install deps, symlink provider into MA
./scripts/link-to-ma.sh

# Start the MA server
source ../ma-server/.venv/bin/activate
cd ../ma-server && python -m music_assistant
```

Then open the MSX app → **Settings → Start Parameter** → enter `http://<SERVER_IP>:8099/msx/start.json`.

## Features

- **MA Player Provider** — runs inside the MA server process, no containers or addons needed
- **MSX Native UI** — browse albums, artists, playlists, and tracks with remote-control navigation
- **Audio Playback** — PCM → ffmpeg → MP3/AAC/FLAC pipeline with MA queue integration
- **Browser Web Player** — full library browser + kiosk mode at `http://<SERVER_IP>:8099/web/`
- **WebSocket Push** — play/stop/pause/seek events pushed to TVs in real-time (bidirectional)
- **Multi-TV Support** — each TV gets its own MA player via MSX device ID
- **Dynamic Registration** — TVs register on-demand, cleaned up after idle timeout
- **Player Grouping** — synchronized playback across multiple TVs (experimental)
- **Universal** — Samsung Tizen, LG webOS, Android TV, Fire TV, Apple TV, web browsers

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, TV setup, first steps |
| [Architecture](docs/architecture.md) | Provider structure, navigation flow, audio pipeline, WebSocket protocol |
| [Web Player](docs/web-player.md) | Browser player, kiosk mode, Sendspin sync, URL parameters |
| [API Reference](docs/api.md) | All HTTP endpoints — MSX, audio, REST API, playback control |
| [Configuration](docs/configuration.md) | Port, output format, idle timeout, stop behavior, group streaming |
| [Development](docs/development.md) | Dev setup, tests, linting, commit format |
| [Contributing](docs/contributing.md) | Bug reports, feature requests, pull requests |
| [Testing](docs/testing.md) | Running tests locally, CI pipeline, coverage |
| [Incident Management](docs/incident-management.md) | Labels, automated issue tracking, Copilot triage |
| [Docker Dev Environment](docs/dev-docker.md) | Run MA + provider locally without dependencies |

## Credits

- [Music Assistant](https://music-assistant.io/) by Marcel Veldt
- [Media Station X](https://msx.benzac.de/) by Benjamin Zachey

## License

MIT — see [LICENSE](LICENSE). See [CHANGELOG.md](CHANGELOG.md) for version history.
