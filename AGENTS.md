# AGENTS.md

> Project map for AI agents. Keep this file up-to-date as the project evolves.

## Project Overview

MSX Music Assistant is a Music Assistant (MA) Player Provider that streams music to Smart TVs via the Media Station X (MSX) app. It runs inside the MA server process as a plugin, exposing an aiohttp HTTP server for MSX JSON API, WebSocket push, and audio streaming.

## Tech Stack

- **Language:** Python 3.14+
- **Framework:** aiohttp (embedded HTTP server inside MA provider)
- **Platform:** Music Assistant server (plugin/provider model)
- **Testing:** pytest + pytest-asyncio against a mounted upstream MA checkout
- **Linting:** ruff, mypy, pre-commit
- **Audio:** ffmpeg subprocess (PCM → MP3/AAC/FLAC)

## Project Structure

```
msx-music-assistant/
├── provider/                     # MA provider plugin — mounted as music_assistant.providers.msx_bridge
│   ├── __init__.py               # setup() entry point
│   ├── provider.py               # MSXBridgeProvider(PlayerProvider) — lifecycle, player mgmt, WS broadcast
│   ├── player.py                 # MSXPlayer(Player) — per-TV player state, media events
│   ├── http_server.py            # MSXHTTPServer — aiohttp routes (MSX, audio, API, WS)
│   ├── constants.py              # Config keys and defaults
│   ├── models.py                 # Pydantic models for MSX JSON API (MsxTemplate, MsxItem, MsxContent)
│   ├── mappers.py                # MA object → MSX model converters
│   ├── manifest.json             # Provider metadata for MA
│   └── static/                  # Static files served by aiohttp
│       ├── plugin.html           # MSX interaction plugin (device ID detection, WebSocket client)
│       ├── input.html / input.js # MSX Input Plugin (search keyboard)
│       └── tvx-plugin*.min.js    # TVX plugin library
│
├── tests/                        # All tests
│   ├── conftest.py               # MA mock fixtures (MockMusicAssistant, etc.)
│   ├── test_http_server.py       # HTTP routes
│   ├── test_player.py            # MSXPlayer state machine
│   ├── test_provider.py          # Provider lifecycle and migration
│   ├── test_playlist.py          # MSX playlist endpoints
│   ├── test_init.py              # Config entries and capabilities
│   ├── test_models.py            # Pydantic models
│   └── test_mappers.py           # MA→MSX mappers
│
├── scripts/                      # Dev tooling
│   ├── setup.sh                  # Setup venv, MA checkout, dependencies, and provider symlink
│   ├── test-upstream.sh          # Official MA compatibility gate
│   ├── test-server.sh            # Start/stop/status/log for local MA dev server
│   └── debug-stream-stop.py      # Debug utility for stream lifecycle
│
├── docs/                         # Documentation and planning
│   ├── FEATURES.md               # Feature descriptions (EN)
│   ├── FEATURES.ru.md            # Feature descriptions (RU)
│   ├── TODO.md                   # Backlog
│   └── plans/                    # Completed implementation plans
│
├── music_assistant/              # MA framework stubs (for IDE/mypy support)
├── pyproject.toml                # pytest config, tool settings
├── CLAUDE.md                     # Claude Code instructions (architecture, gotchas, key flows)
├── docs/contributing.md          # Contribution guidelines
├── CHANGELOG.md                  # Release history
└── README.md                     # Project landing page (EN + RU)
```

## Key Entry Points

| File | Purpose |
|------|---------|
| `provider/__init__.py` | MA plugin entry point — `setup()` |
| `provider/provider.py` | `MSXBridgeProvider` — lifecycle, player management, WebSocket broadcast |
| `provider/player.py` | `MSXPlayer` — per-TV player, media event signaling, seek/pause/resume |
| `provider/http_server.py` | `MSXHTTPServer` — all HTTP routes (MSX JSON, audio, stream, API, WS, web) |
| `provider/constants.py` | All config keys and default values |
| `tests/conftest.py` | Shared pytest fixtures: `MockMusicAssistant`, provider/server/player factories |
| `scripts/setup.sh` | Development venv, MA checkout, dependencies, and provider symlink |
| `scripts/test-upstream.sh` | Full compatibility gate against official MA `dev` |
| `scripts/test-server.sh` | Local MA dev server lifecycle management |

## Documentation

| Document | Path | Description |
|----------|------|-------------|
| README | README.md | Project landing page (EN) |
| README (RU) | README.ru.md | Project landing page (RU) |
| Getting Started | docs/getting-started.md | Installation, TV setup, first steps |
| Architecture | docs/architecture.md | Provider structure, flows, WebSocket protocol |
| API Reference | docs/api.md | All HTTP endpoints |
| Configuration | docs/configuration.md | Config entries, output format, stop behavior |
| Development | docs/development.md | Dev setup, tests, linting, commit format |
| Contributing | docs/contributing.md | Bug reports, PRs, code of conduct |
| Features | docs/FEATURES.md | Detailed feature descriptions |
| Backlog | docs/TODO.md | Remaining tasks and known issues |
| CLAUDE.md | CLAUDE.md | Claude Code instructions, key flows, gotchas |

## AI Context Files

| File | Purpose |
|------|---------|
| AGENTS.md | This file — project structure map |
| .ai-factory/DESCRIPTION.md | Project specification and tech stack |
| CLAUDE.md | Claude Code instructions, architecture details, gotchas |

## Development Environment

```bash
# Setup local development environment
./scripts/setup.sh

# Run the full upstream compatibility gate
./scripts/test-upstream.sh all

# Start local MA dev server
./scripts/test-server.sh start

# Run one verification stage
./scripts/test-upstream.sh lint
```
