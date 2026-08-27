# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Music Assistant (MA) Player Provider that streams music to Smart TVs via the Media Station X (MSX) app. Implemented as an MA provider plugin — runs inside the MA server process with direct access to internal APIs.

## Architecture

```
Smart TV (MSX App) --HTTP--> MSXBridgeProvider (inside MA, port 8099) --internal API--> MA core
```

**Provider** (`provider/msx_bridge/`): MA Player Provider with embedded HTTP server.
- `__init__.py` — `setup()`, `get_config_entries()` (6 config entries), provider entry point
- `provider.py` — `MSXBridgeProvider(PlayerProvider)`: manages lifecycle, dynamic player registration, idle timeout loop, WebSocket push notifications, starts HTTP server
- `player.py` — `MSXPlayer(Player)`: represents a Smart TV as an MA player. Stores stream URL from `play_media()` for the TV to fetch via HTTP.
- `http_server.py` — `MSXHTTPServer`: aiohttp server with routes for MSX bootstrap, library browsing, playback control, WebSocket, and stream proxy
- `constants.py` — config keys and defaults (6 config entries: `http_port`, `output_format`, `player_idle_timeout`, `show_stop_notification`, `enable_player_grouping`, `group_stream_mode`)
- `models.py` — Pydantic models for MSX JSON API (`MsxTemplate`, `MsxItem`, `MsxContent`)
- `mappers.py` — Converters from MA objects to MSX models (`map_track_to_msx`, `map_album_to_msx`, `map_artist_to_msx`, `map_playlist_to_msx`, `map_tracks_to_msx_playlist`)
- `manifest.json` — provider metadata for MA
- `static/` — static files served by aiohttp:
  - `plugin.html` — MSX interaction plugin (detects device ID, opens WebSocket, builds menu)
  - `input.html` — MSX Input Plugin wrapper (search keyboard)
  - `input.js` — Input Plugin logic
  - `tvx-plugin-module.min.js` — TVX plugin module library
  - `tvx-plugin.min.js` — TVX plugin library

### Key Flows

**MSX Bootstrap & Navigation:**
1. TV loads `/msx/start.json` → points to `/msx/plugin.html` as interaction plugin
2. Plugin detects device ID via `TVXVideoPlugin.requestDeviceId()` (falls back to IP)
3. Plugin opens WebSocket to `/ws?device_id=...` for push playback notifications
4. Plugin requests `/msx/menu.json?device_id=...` → returns menu items (Search, Albums, Artists, Playlists, Tracks)
5. Clicking a menu item loads a content page (e.g. `/msx/albums.json?device_id=...`) → MSX renders list
6. All URLs carry `device_id` param so the server maps requests to the correct player
7. Content items have `action: "content:..."` (drill to detail page), `action: "audio:..."` (single track), or `action: "playlist:..."` (MSX native playlist — loads URL, auto-starts, supports next/prev)

**Dynamic Player Registration:**
1. Any MSX request calls `_ensure_player_for_request()` → extracts `device_id` or IP → derives `player_id`
2. `provider.get_or_register_player(player_id)` creates an `MSXPlayer` on-demand if not already registered
3. Background idle timeout loop runs every 60s → unregisters players with no activity for `player_idle_timeout` minutes (default: 30)
4. Handles race conditions via `_pending_unregisters` events

**Audio Playback (via MSX native player):**
1. Track list items use `action: "playlist:/msx/playlist/album/{id}.json"` — MSX loads the playlist, auto-starts playback, tracks rotated so clicked track is first; native next/prev
2. Each playlist item has `action: "audio:/msx/audio/{player_id}?uri=<uri>&from_playlist=1"`
3. `GET /msx/audio/{player_id}?uri=...` → calls `mass.player_queues.play_media()` → waits for `MSXPlayer.wait_for_media()` (up to 10s)
4. Streams: `mass.streams.get_stream()` → raw PCM → `get_ffmpeg_stream()` → encoded MP3/AAC/FLAC → TV
5. `Content-Length: duration * bytes_per_sec` set for MP3 (40,000 B/s) and AAC (32,000 B/s) — FLAC omits it (non-deterministic size)
6. **MA queue → MSX playlist:** `notify_play_playlist()` sends WS `{type:"playlist", url:"/msx/queue-playlist/{player_id}.json"}` — TV loads MA queue as MSX native playlist; same-queue track changes use `{type:"goto_index", index:N}` instead of resending

**WebSocket Push (bidirectional MA ↔ MSX):**
1. Plugin connects to `/ws?device_id=...` on startup
2. MA → TV message types: `play` (title/artist/image/duration/next_action/prev_action), `stop` (sent twice for instant close), `pause`, `resume`, `playlist` (url to load), `goto_index` (index in current playlist), `seek` (position_seconds)
3. TV → MA message types: `position` (current playback seconds → `player.update_position()`), `pause` (with position), `resume` — bidirectional protocol
4. `_skip_ws_notify` flag prevents echo-back when MSX initiates pause/resume
5. WS position reports override wall-clock elapsed time for 10s (more accurate than polling)

**Direct Stream Proxy (for programmatic playback):**
1. MA calls `play_media(media)` on `MSXPlayer` → player stores `media.uri` as `current_stream_url`
2. TV fetches `GET /stream/{player_id}` → HTTP server streams audio via PCM → ffmpeg → encoded output

**Library REST API:**
- TV or external client calls `/api/albums`, `/api/artists`, etc. → server calls `mass.music.*` internally

## Development Setup

```bash
# Clone MA server fork alongside this project (if not already done)
# Use the integration branch with pending upstream PRs for the test environment
cd /tmp/msx-ma-server && git clone https://github.com/trudenboy/ma-server.git

# Setup venv, install deps, symlink provider — one command does it all
./scripts/link-to-ma.sh
```

### Working with the MA venv

All commands (server, tests, pre-commit, linting) must run inside the MA venv:

```bash
# Activate the venv
source /tmp/msx-ma-server/ma-server/.venv/bin/activate

# Start MA server (provider auto-loads)
cd /tmp/msx-ma-server/ma-server && python -m music_assistant --log-level debug

# Run tests
cd /tmp/msx-ma-server/ma-server && pytest

# Pre-commit (linting, formatting)
cd /tmp/msx-ma-server/ma-server && pre-commit run --all-files

# Verify provider imports
python -c "from music_assistant.providers.msx_bridge import setup; print('OK')"
```

## Code Standards

- **Python**: PEP 8, type hints on all functions, `from __future__ import annotations`
- **Commits**: `type(scope): description` — types: feat, fix, docs, style, refactor, test, chore
- **Async**: All I/O uses async/await (aiohttp)
- **MA conventions**: Follow patterns from `_demo_player_provider` and `sendspin` providers
- **DO NOT use subagents (Task tool) without explicit user instruction or confirmation!**

## Key Files Reference (MA Server)

| Path | Purpose |
|------|---------|
| `music_assistant/models/player.py` | `Player` base class |
| `music_assistant/models/player_provider.py` | `PlayerProvider` base class |
| `music_assistant/providers/_demo_player_provider/` | Template provider |
| `music_assistant/providers/sendspin/` | Reference: provider with embedded HTTP server |

## Project Status

`MSXBridgeProvider`, `MSXPlayer`, and `MSXHTTPServer` are implemented with:
- Dynamic player registration (device ID or IP-based) with idle timeout cleanup
- Multi-TV support (each TV gets its own player via device ID)
- WebSocket push notifications — bidirectional: MA→TV (play/stop/pause/resume/playlist/goto_index/seek) and TV→MA (position/pause/resume)
- Player state management (play, pause, stop, seek, volume, poll)
- Player grouping: `SET_MEMBERS` feature, `_propagate_to_group_members()` syncs play/pause/stop across group
- `SharedGroupStream` in `provider.py` — one ffmpeg, multiple TV readers (catch-up buffer, late-joiner support)
- `ProviderFeature.REMOVE_PLAYER` — user can remove a player from MA UI; `ProviderFeature.SYNC_PLAYERS` when grouping enabled
- MSX bootstrap (`/msx/start.json`, `/msx/plugin.html`, static assets)
- MSX interaction plugin with device ID detection and WebSocket client
- MSX native JSON content pages (`/msx/menu.json`, `/msx/albums.json`, `/msx/artists.json`, `/msx/playlists.json`, `/msx/tracks.json`, `/msx/recently-played.json`, `/msx/search.json`, `/msx/search-page.json`, `/msx/search-input.json`, `/msx/launcher.json`)
- MSX detail pages (`/msx/albums/{id}/tracks.json`, `/msx/artists/{id}/albums.json`, `/msx/playlists/{id}/tracks.json`)
- MSX native playlist endpoints (`/msx/playlist/album/{id}.json`, `/msx/playlist/playlist/{id}.json`, `/msx/playlist/tracks.json`, `/msx/playlist/recently-played.json`, `/msx/playlist/search.json`, `/msx/queue-playlist/{player_id}.json`)
- Audio playback endpoint (`/msx/audio/{player_id}`) via playlist action; Content-Length set for MP3/AAC from duration; FLAC omits it
- Stream proxy (`/stream/{player_id}`) with same PCM→ffmpeg chain
- Library REST API (`/api/albums`, `/api/artists`, `/api/playlists`, `/api/tracks`, `/api/search`, `/api/recently-played`, plus detail sub-routes)
- Playback control (`/api/play`, `/api/pause/{player_id}`, `/api/stop/{player_id}`, `/api/quick-stop/{player_id}`, `/api/next/{player_id}`, `/api/previous/{player_id}`)
- Health endpoint (`/health`)
- Status dashboard (`/`)
- 141 tests: 111 unit (test_http_server 53, test_player 42, test_group_stream 20, test_provider 9, test_init 6, test_models 4, test_playlist 5, test_mappers 2) + 30 integration
- `map_track_to_msx()` / `map_tracks_to_msx_playlist()` in `mappers.py` replace the old `_format_msx_track()` helper
- 6 config entries: `http_port`, `output_format`, `player_idle_timeout`, `show_stop_notification`, `enable_player_grouping`, `group_stream_mode`
- Group stream modes: Independent (separate ffmpeg per TV) or Shared Buffer (one ffmpeg, multiple readers)
- `on_player_disabled` override: does not unregister (player stays on Enable); still broadcasts stop for instant MSX close

Next steps: integration testing with real MA server + MSX app, full MSX TypeScript plugin.

## Gotchas

- **Album track ordering**: `_sort_album_tracks()` uses `(disc, track_number, name)` — without `name` as tiebreaker, tracks with identical disc/number get non-deterministic order between display page and playlist endpoint (causes mismatched play).
- **MSX `playlist:` action**: always starts from index 0 — rotate tracks so clicked track is index 0 (`msx_items[start_index:] + msx_items[:start_index]`).
- **MSX `playlist:` vs `playlist:auto:`**: `playlist:` shows player in foreground and auto-starts; `playlist:auto:` plays in background silently.
- **Content-Length for audio**: set for MP3 (40,000 B/s) and AAC (32,000 B/s) only — FLAC size is non-deterministic, omitting Content-Length for FLAC prevents MSX from hanging.
- **WS echo prevention**: set `_skip_ws_notify = True` before calling MA pause/resume when MSX initiates the action, to avoid MA echoing the WS command back to the TV.
