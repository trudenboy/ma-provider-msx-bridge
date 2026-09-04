# Project: MSX Music Assistant

## Overview

A Music Assistant (MA) Player Provider that streams music from a MA server to Smart TVs running the Media Station X (MSX) app. Implemented as an MA plugin that runs inside the MA server process with direct access to internal APIs — no separate container needed.

## Core Features

- Dynamic player registration: TVs auto-register as MA players on first request (device ID or IP-based), with configurable idle timeout cleanup
- Multi-TV support: each TV gets its own `MSXPlayer` instance keyed by device ID
- MSX UI: Bootstrap, menu, library pages (albums, artists, playlists, tracks), detail pages, search (Input Plugin keyboard)
- Audio streaming: MA Streamserver redirect by default, with an independent PCM → ffmpeg → MP3/AAC/FLAC compatibility proxy
- WebSocket push (bidirectional): MA→TV (play/stop/pause/resume/playlist/goto_index/seek); TV→MA (position/pause/resume)
- Native MSX playlists: MA queue exposed as MSX native playlist with goto_index for seamless track switching
- Multi-TV playback through Music Assistant Universal Groups
- Library REST API for external clients
- Provider tests run against a mounted upstream Music Assistant checkout

## Tech Stack

- **Language:** Python 3.14+
- **Framework:** aiohttp (embedded async HTTP server inside MA provider)
- **Platform:** Music Assistant server (plugin/provider model)
- **Testing:** pytest + pytest-asyncio
- **Linting:** ruff, mypy, pre-commit
- **Audio:** ffmpeg (via subprocess, PCM → encoded output)
- **Integrations:** MSX app (JSON API + WebSocket), MA internal API (streams, queues, players, library)

## Architecture

```
Smart TV (MSX App)
    │ HTTP (port 8099)
    ▼
MSXHTTPServer (aiohttp)        ← provider/http_server.py
    │
MSXBridgeProvider              ← provider/provider.py
    │ internal Python API
    ▼
Music Assistant Core           ← mass.players / mass.streams / mass.music / mass.player_queues
```

**Provider lifecycle:** `handle_async_init()` → `loaded_in_mass()` → `discover_players()` → idle timeout loop → `unload()`

**Audio pipeline:** redirect to MA Streamserver, or independently proxy `mass.streams.get_stream()` → raw PCM → `get_ffmpeg_stream()` → TV

## Architecture Notes

- Provider runs inside MA server process — no Docker or separate service
- All I/O is async (aiohttp + asyncio)
- Players are ephemeral — created on demand, cleaned up after idle timeout
- ffmpeg is invoked per-stream only for independent delivery or redirect fallback
- MA config system manages provider settings
- Tests mock the MA `MusicAssistant` instance via conftest fixtures

## Non-Functional Requirements

- Logging: Python `logging` module, MA log-level propagated
- Error handling: aiohttp HTTP error responses; MA exceptions caught and translated
- Security: token-protected audio routes plus origin and cross-site request guards
- Performance: Pre-buffer 64KB before sending headers; chunk queue maxsize=32 for jitter tolerance
