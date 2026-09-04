# MSX Music Assistant Bridge


<!-- >>> ma-provider-tools sync (readme header) — DO NOT EDIT >>> -->
[![CI](https://github.com/trudenboy/ma-provider-msx-bridge/actions/workflows/test.yml/badge.svg)](https://github.com/trudenboy/ma-provider-msx-bridge/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/trudenboy/ma-provider-msx-bridge?display_name=tag)](https://github.com/trudenboy/ma-provider-msx-bridge/releases/latest)
[![License](https://img.shields.io/github/license/trudenboy/ma-provider-msx-bridge)](LICENSE)
[![Music Assistant](https://img.shields.io/badge/Music%20Assistant-9070B8?logo=python&logoColor=white)](https://www.music-assistant.io/)[![stable](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Fmsx_bridge-stable.json)](https://github.com/music-assistant/server/releases/latest)[![beta](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Fmsx_bridge-beta.json)](https://github.com/music-assistant/server/releases?q=prerelease)
[![Stars](https://img.shields.io/github/stars/trudenboy/ma-provider-msx-bridge?style=flat&logo=github)](https://github.com/trudenboy/ma-provider-msx-bridge/stargazers)

**📖 [Documentation](https://trudenboy.github.io/ma-provider-msx-bridge/)** · **🔄 [Changelog](CHANGELOG.md)** · **🐛 [Issues](https://github.com/trudenboy/ma-provider-msx-bridge/issues)** · **💬 [Discussions](https://github.com/trudenboy/ma-provider-msx-bridge/discussions)**
<!-- <<< ma-provider-tools sync (readme header) <<< -->

English | [Русский](README.ru.md)

📖 <a href="https://trudenboy.github.io/ma-provider-msx-bridge/">User Documentation</a>

> Stream your [Music Assistant](https://music-assistant.io/) library to Smart TVs through [Media Station X](https://msx.benzac.de/) with a native TV-optimized interface.
<img width="2752" height="1536" alt="msx_infographic" src="https://github.com/user-attachments/assets/287fb05b-6a15-49c0-bc46-2af3afbc11d4" />

## Quick Start

```bash
# Clone and set up the development environment
git clone https://github.com/trudenboy/msx-music-assistant.git
cd msx-music-assistant
./scripts/setup.sh

# Start the MA server
source .venv/bin/activate
cd ma-server && python -m music_assistant
```

Then open the MSX app → **Settings → Start Parameter** → enter `http://<SERVER_IP>:8099/msx/start.json`.

## Features

- **MA Player Provider** — runs inside the MA server process, no containers or addons needed
- **MSX Native UI** — browse albums, artists, playlists, and tracks with remote-control navigation
- **Audio Playback** — direct MA Streamserver delivery with a local ffmpeg compatibility fallback
- **WebSocket Push** — play/stop/pause/seek events pushed to TVs in real-time (bidirectional)
- **Multi-TV Support** — each TV gets its own MA player via MSX device ID
- **Dynamic Registration** — TVs register on-demand, cleaned up after idle timeout
- **Universal Groups** — use Music Assistant Universal Group for multi-TV playback
- **Universal** — Samsung Tizen, LG webOS, Android TV, Fire TV, Apple TV

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, TV setup, first steps |
| [Architecture](docs/architecture.md) | Provider structure, navigation flow, audio pipeline, WebSocket protocol |
| [API Reference](docs/api.md) | All HTTP endpoints — MSX, audio, REST API, playback control |
| [Configuration](docs/configuration.md) | Port, output format, idle timeout, stream delivery |
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
