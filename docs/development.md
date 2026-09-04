[← Configuration](configuration.md) · [Back to README](../README.md) · [Contributing →](contributing.md)

# Development

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) — used by MA for venv and dependency management

## Setup

```bash
# Clone the provider
git clone https://github.com/trudenboy/msx-music-assistant.git

# Create the venv, MA checkout, dependencies, and provider symlink
cd msx-music-assistant
./scripts/setup.sh
```

`setup.sh` does the following:
1. Creates `.venv/` with uv
2. Installs MA and test dependencies
3. Symlinks `provider/` into `ma-server/music_assistant/providers/msx_bridge`

## Running the Server

```bash
source .venv/bin/activate
cd ma-server && python -m music_assistant --log-level debug
```

The test-server script provides start/stop/status/log commands:

```bash
./scripts/test-server.sh start
./scripts/test-server.sh status
./scripts/test-server.sh log
./scripts/test-server.sh stop
```

## Running Tests

Run the provider suite against the mounted upstream Music Assistant checkout:

```bash
./scripts/test-upstream.sh test
```

### Test Structure

| File | Covers |
|------|--------|
| `test_http_server.py` | HTTP routes, responses, and error cases |
| `test_player.py` | MSXPlayer state machine, media events, seek/pause |
| `test_provider.py` | Provider lifecycle, player registration, config migration |
| `test_playlist.py` | MSX native playlist endpoints |
| `test_init.py` | Config entry setup and capabilities |
| `test_models.py` | Pydantic model validation |
| `test_mappers.py` | MA → MSX JSON mappers |

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
| `provider/provider.py` | `MSXBridgeProvider` — main provider class |
| `provider/player.py` | `MSXPlayer` — per-TV player state |
| `provider/http_server.py` | All HTTP routes |
| `provider/constants.py` | Config keys and defaults |
| `tests/conftest.py` | `MockMusicAssistant` and shared fixtures |
| `scripts/setup.sh` | Dev environment setup |
| `scripts/test-upstream.sh` | Official MA compatibility gate |

See [CLAUDE.md](../CLAUDE.md) for detailed MA conventions, key flows, and gotchas.

## See Also

- [Architecture](architecture.md) — provider structure and key flows
- [Contributing](contributing.md) — PR process, review guidelines
- [API Reference](api.md) — all HTTP endpoints for testing manually
