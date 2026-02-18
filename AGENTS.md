# AGENTS.md

> Project map for AI agents. Keep this file up-to-date as the project evolves.

## Project Overview

MSX Music Assistant is a Music Assistant (MA) Player Provider that streams music to Smart TVs via the Media Station X (MSX) app. It runs inside the MA server process as a plugin, exposing an aiohttp HTTP server for MSX JSON API, WebSocket push, and audio streaming.

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** aiohttp (embedded HTTP server inside MA provider)
- **Platform:** Music Assistant server (plugin/provider model)
- **Testing:** pytest + pytest-asyncio (141 tests: 111 unit + 30 integration)
- **Linting:** ruff, mypy, pre-commit
- **Audio:** ffmpeg subprocess (PCM → MP3/AAC/FLAC)

## Project Structure

```
msx-music-assistant/
├── provider/msx_bridge/          # MA provider plugin — all core logic
│   ├── __init__.py               # setup() entry point, get_config_entries()
│   ├── provider.py               # MSXBridgeProvider(PlayerProvider) — lifecycle, player mgmt, WS broadcast
│   ├── player.py                 # MSXPlayer(Player) — per-TV player state, media events
│   ├── http_server.py            # MSXHTTPServer — aiohttp routes (MSX, audio, API, WS, web)
│   ├── constants.py              # Config keys and defaults (7 entries)
│   ├── models.py                 # Pydantic models for MSX JSON API (MsxTemplate, MsxItem, MsxContent)
│   ├── mappers.py                # MA object → MSX model converters
│   ├── manifest.json             # Provider metadata for MA
│   └── static/                  # Static files served by aiohttp
│       ├── plugin.html           # MSX interaction plugin (device ID detection, WebSocket client)
│       ├── input.html / input.js # MSX Input Plugin (search keyboard)
│       ├── tvx-plugin*.min.js    # TVX plugin library
│       └── web/                  # Browser-based web player (index.html, web.js)
│
├── tests/                        # All tests
│   ├── conftest.py               # MA mock fixtures (MockMusicAssistant, etc.)
│   ├── test_http_server.py       # 53 tests — HTTP routes
│   ├── test_player.py            # 42 tests — MSXPlayer state machine
│   ├── test_group_stream.py      # 20 tests — SharedGroupStream
│   ├── test_provider.py          # 9 tests — provider lifecycle
│   ├── test_playlist.py          # 5 tests — MSX playlist endpoints
│   ├── test_init.py              # 6 tests — config entries
│   ├── test_models.py            # 4 tests — Pydantic models
│   ├── test_mappers.py           # 2 tests — MA→MSX mappers
│   └── integration/              # 30 integration tests (require real MA server)
│
├── scripts/                      # Dev tooling
│   ├── link-to-ma.sh             # Setup venv, symlink provider into MA server, verify imports
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
├── CONTRIBUTING.md               # Contribution guidelines
├── CHANGELOG.md                  # Release history
└── README.md                     # Project landing page (EN + RU)
```

## Key Entry Points

| File | Purpose |
|------|---------|
| `provider/msx_bridge/__init__.py` | MA plugin entry point — `setup()` and `get_config_entries()` |
| `provider/msx_bridge/provider.py` | `MSXBridgeProvider` — lifecycle, player management, WebSocket broadcast, group streaming |
| `provider/msx_bridge/player.py` | `MSXPlayer` — per-TV player, media event signaling, seek/pause/resume |
| `provider/msx_bridge/http_server.py` | `MSXHTTPServer` — all HTTP routes (MSX JSON, audio, stream, API, WS, web) |
| `provider/msx_bridge/constants.py` | All config keys and default values |
| `tests/conftest.py` | Shared pytest fixtures: `MockMusicAssistant`, provider/server/player factories |
| `scripts/link-to-ma.sh` | One-command dev setup: venv + symlink + import verification |
| `scripts/test-server.sh` | Local MA dev server lifecycle management |

## Documentation

| Document | Path | Description |
|----------|------|-------------|
| README | README.md | Project landing page (EN) |
| README (RU) | README.ru.md | Project landing page (RU) |
| Getting Started | docs/getting-started.md | Installation, TV setup, first steps |
| Architecture | docs/architecture.md | Provider structure, flows, WebSocket protocol |
| Web Player | docs/web-player.md | Browser player, kiosk mode, URL parameters |
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
# Setup (one command — creates venv, installs deps, symlinks provider)
./scripts/link-to-ma.sh

# Activate MA venv (required for all commands)
source /tmp/msx-ma-server/ma-server/.venv/bin/activate

# Run tests
cd /tmp/msx-ma-server/ma-server && pytest

# Start local MA dev server
./scripts/test-server.sh start

# Lint / format
cd /tmp/msx-ma-server/ma-server && pre-commit run --all-files
```
