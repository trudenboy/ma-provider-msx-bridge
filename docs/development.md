[← Configuration](configuration.md) · [Back to README](../README.md) · [Contributing →](contributing.md)

# Development

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) — used by MA for venv and dependency management
- MA server fork cloned alongside this project (`../ma-server/`)

## Setup

```bash
# Clone repos side by side (if not already done)
cd ~/Projects
git clone https://github.com/trudenboy/msx-music-assistant.git
git clone https://github.com/trudenboy/ma-server.git

# One command: creates venv, installs deps, symlinks provider into MA
cd msx-music-assistant
./scripts/link-to-ma.sh
```

`link-to-ma.sh` does the following:
1. Creates `../ma-server/.venv/` with uv
2. Installs MA and test dependencies
3. Symlinks `provider/msx_bridge/` into `ma-server/music_assistant/providers/msx_bridge`
4. Verifies the import works

## Running the Server

```bash
source ../ma-server/.venv/bin/activate
cd ../ma-server && python -m music_assistant --log-level debug
```

The test-server script provides start/stop/status/log commands:

```bash
./scripts/test-server.sh start
./scripts/test-server.sh status
./scripts/test-server.sh log
./scripts/test-server.sh stop
```

## Running Tests

All commands require the MA venv:

```bash
source ../ma-server/.venv/bin/activate

# Unit tests (fast, no server needed)
pytest tests/ -v --ignore=tests/integration

# Integration tests (requires running MA server on port 8095)
pytest tests/integration/ -v

# Specific test file
pytest tests/test_http_server.py -v

# Run with output
pytest tests/ -v -s --ignore=tests/integration
```

### Test Structure

| File | Tests | Covers |
|------|-------|--------|
| `test_http_server.py` | 53 | All HTTP routes, responses, and error cases |
| `test_player.py` | 42 | MSXPlayer state machine, media events, seek/pause |
| `test_group_stream.py` | 20 | SharedGroupStream (shared ffmpeg, catch-up buffer) |
| `test_provider.py` | 9 | Provider lifecycle, player registration |
| `test_playlist.py` | 5 | MSX native playlist endpoints |
| `test_init.py` | 6 | Config entry setup |
| `test_models.py` | 4 | Pydantic model validation |
| `test_mappers.py` | 2 | MA → MSX JSON mappers |
| `tests/integration/` | 30 | End-to-end with real MA server |

## Linting & Type Checking

```bash
source ../ma-server/.venv/bin/activate
cd ../ma-server

# Lint + format check + type check (all-in-one via pre-commit)
pre-commit run --all-files

# Individual tools
ruff check provider/ tests/
ruff format --check provider/ tests/
mypy provider/ --ignore-missing-imports
```

## Code Standards

- `from __future__ import annotations` at the top of every file
- Type hints on all functions
- All I/O uses `async/await` (aiohttp)
- Follow patterns from MA reference providers (`_demo_player_provider`, `sendspin`)

### Commit Message Format

`type(scope): description`

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependency updates |

Examples:
```
feat(provider): add search endpoint for MSX content pages
fix(player): correct elapsed time calculation on pause
docs: update README with architecture diagrams
```

## Key Files

| File | Purpose |
|------|---------|
| `provider/msx_bridge/provider.py` | `MSXBridgeProvider` — main provider class |
| `provider/msx_bridge/player.py` | `MSXPlayer` — per-TV player state |
| `provider/msx_bridge/http_server.py` | All HTTP routes |
| `provider/msx_bridge/constants.py` | Config keys and defaults |
| `tests/conftest.py` | `MockMusicAssistant` and shared fixtures |
| `scripts/link-to-ma.sh` | Dev environment setup |

See [CLAUDE.md](../CLAUDE.md) for detailed MA conventions, key flows, and gotchas.

## See Also

- [Architecture](architecture.md) — provider structure and key flows
- [Contributing](contributing.md) — PR process, review guidelines
- [API Reference](api.md) — all HTTP endpoints for testing manually
