# MSX Music Assistant Bridge

English | [Русский](README.ru.md)

Stream your [Music Assistant](https://music-assistant.io/) library to Smart TVs through [Media Station X](https://msx.benzac.de/) with a native TV-optimized interface.

## Features

- **MA Player Provider** — runs inside the Music Assistant server process, no separate containers or addons
- **MSX Native UI** — browse albums, artists, playlists, and tracks with remote-control-friendly navigation
- **Library Browsing** — drill into album tracks, artist albums, playlist tracks, and search results
- **Audio Playback** — stream audio to the TV through MA's queue system with PCM→ffmpeg encoding
- **Browser Web Player** — lightweight browser-based player for kitchens, offices, kiosks, and mobile access (`http://<SERVER_IP>:8099/web/`)
- **Player Grouping** — synchronized playback control across multiple TVs (experimental; configurable stream modes)
- **Group Stream Modes** — Independent (each TV gets own ffmpeg) or Shared Buffer (one ffmpeg, less CPU)
- **Remove Player** — delete MSX players from MA UI
- **MSX Native Playlists** — seamless album/playlist playback with queue integration and TV remote navigation
- **Dynamic Player Registration** — TVs register as MA players on-demand via device ID or IP, with automatic idle timeout cleanup
- **Multi-TV Support** — each TV gets its own unique player, identified by MSX device ID
- **WebSocket Push** — MA-initiated playback (play/stop) pushed to TVs in real-time via WebSocket
- **Instant Stop** — Stop closes the MSX player immediately; Pause keeps the player open and pauses playback
- **Universal TV Support** — works on any TV/device running the MSX app (Samsung Tizen, LG webOS, Android TV, Fire TV, Apple TV, web browsers)
- **Configurable Output** — MP3, AAC, or FLAC output format
- **Local Network** — runs entirely on your LAN, no cloud dependencies


## Screenshots
<img width="1224" height="686" alt="MSX Album View" src="https://github.com/user-attachments/assets/a32e5ce6-af90-46cb-8062-255ab758c4d7" />
<img width="1525" height="923" alt="MSX Player View" src="https://github.com/user-attachments/assets/e504a370-dd83-4485-aba2-66e46c74b50a" />
<img width="960" height="540" alt="Screenshot 2026-02-18 at 16 34 49" src="https://github.com/user-attachments/assets/67e78b1a-3eb8-4c6c-accd-e5d2d8766763" />
<img width="960" height="540" alt="Screenshot 2026-02-18 at 16 36 01" src="https://github.com/user-attachments/assets/71c2bdc6-8605-4da2-a8e3-6a1a8b7b0408" />
<img width="960" height="540" alt="Screenshot 2026-02-18 at 16 32 12" src="https://github.com/user-attachments/assets/b6470645-8dc6-4687-a037-76a0d0ded039" />

## Architecture

```
┌─────────────┐         ┌───────────────────────────────────────┐
│  Smart TV   │         │        Music Assistant Server          │
│  (MSX App)  │  HTTP   │  ┌─────────────────────────────────┐  │
│             │ ◄─────► │  │   MSXBridgeProvider (port 8099) │  │
│ - JSON nav  │         │  │   ├── MSXHTTPServer (aiohttp)   │  │
│ - Audio     │         │  │   └── MSXPlayer                 │  │
│ - Plugin    │         │  └───────────┬──────────────────────┘  │
└─────────────┘         │              │ internal API             │
                        │              │                          │
┌─────────────┐         │  ┌───────────▼──────────────────────┐  │
│   Browser   │  HTTP   │  │        MA Core                    │  │
│ (Web Player)│ ◄─────► │  │  music, players, player_queues    │  │
└─────────────┘         │  └───────────────────────────────────┘  │
                        └───────────────────────────────────────┘
```

### Components

| Component | Class | Role |
|-----------|-------|------|
| **Provider** | `MSXBridgeProvider` | MA `PlayerProvider` — manages lifecycle, registers players, starts HTTP server |
| **Player** | `MSXPlayer` | MA `Player` — represents a Smart TV. Stores stream URL from `play_media()` for the TV to fetch |
| **HTTP Server** | `MSXHTTPServer` | aiohttp server — serves MSX bootstrap, content pages, audio proxy, and REST API |

### MSX Navigation Flow

```
start.json ──► plugin.html (interaction plugin)
                    │
                    ▼
               Main Menu
            ┌────┬────┬────┐
            ▼    ▼    ▼    ▼
         Albums Artists Playlists Tracks
            │    │       │         │
            ▼    ▼       ▼         ▼
         Album  Artist  Playlist  ► Play
         Tracks Albums  Tracks
            │    │       │
            ▼    ▼       ▼
          ► Play ► Drill ► Play
```

Content pages return MSX JSON with `action` fields:
- `"content:..."` — drill down to a detail page
- `"audio:..."` — start audio playback for a single track (used inside playlists)
- `"playlist:..."` — load an MSX native playlist URL (auto-starts, supports TV-remote next/prev)

### Audio Playback Flow

```
TV clicks track item (action: "playlist:/msx/playlist/album/{id}.json")
    │
    ▼
MSX loads playlist JSON ── tracks rotated so clicked track is index 0
    │
    ▼ (each item: action: "audio:/msx/audio/{player_id}?uri=...&from_playlist=1")
    │
GET /msx/audio/{player_id}?uri=<track_uri>
    │
    ├─► play_media() enqueues track in MA queue
    ├─► wait for MSXPlayer.wait_for_media() (up to 10s)
    └─► PCM → ffmpeg → MP3/AAC/FLAC → TV speakers
          (Content-Length set for MP3/AAC; omitted for FLAC)

MA queue track change (next/prev from MA UI or API):
    │
    ▼
notify_play_playlist() ── WS: {type:"playlist", url:"/msx/queue-playlist/{id}.json"}
    └─► same queue, different track → WS: {type:"goto_index", index:N}
```

## Browser Web Player

Open `http://<SERVER_IP>:8099/web/` in any browser — no MSX app required.

### Normal mode (`/web/`)

Full library browser with sidebar navigation:

- **Sidebar** — Albums, Artists, Playlists, Tracks, Recently Played, Search
- **Content grid** — card view with album art; drill into album tracks / artist albums / playlist tracks
- **Bottom player bar** — prev / play-pause / next + progress scrubber
- **Full-screen player** (click the bar) — large album art, queue panel on the right, seek bar
- **HTML5 audio** — streams directly from the provider; same `/msx/audio/` endpoint as the TV app
- **WebSocket sync** — MA-initiated play/stop events reflected instantly in the browser

### Kiosk mode (`/web/?kiosk=1`)

Immersive full-screen display designed for always-on screens (TV, kiosk, digital signage):

```
┌──────────────────────────────────────────────────┐
│  Blurred album art background + vignette overlay  │
│                                                    │
│ ┌────────────┐ ┌────────────────┐ ┌─────────────┐ │
│ │  Album art │ │  LRC Lyrics    │ │    Queue    │ │
│ │            │ │  (scrolling,   │ │  (up next)  │ │
│ │  Title     │ │   karaoke)     │ │             │ │
│ │  Artist    │ │  — or —        │ │             │ │
│ │            │ │  CSS equalizer │ │             │ │
│ └────────────┘ └────────────────┘ └─────────────┘ │
│                                                    │
│  [◄◄]  [▶▶]  [▶]  0:00 ──────────── 3:42          │  ← auto-hides
└──────────────────────────────────────────────────┘
```

- **Three-column layout**: album art + track info (left), lyrics / equalizer (center), queue (right)
- **Karaoke lyrics** — LRC-synced scrolling lines from `/api/lyrics/{player_id}`; active line highlighted and enlarged
- **CSS equalizer** — animated bars shown in the center column when no lyrics are available
- **Blurred background** — album art fills the screen, blurred + darkened
- **Auto-hiding controls** — seek bar + prev/play/next panel fades out after a few seconds of inactivity; reappears on mouse move or touch
- **Idle state** — music note icon + "Waiting for playback…" shown when nothing is playing
- **WebSocket push** — MA-initiated play/stop/pause/seek updates the display instantly
- **Device ID** — persisted in `localStorage`; each browser tab gets its own MA player
- **Responsive** — queue hidden on ≤ 900 px; single-column on mobile (≤ 640 px)
- **4K / large screen** — `@media (min-width: 1920px)` scales up fonts and controls

### Kiosk + Sendspin mode (`/web/?kiosk=1&sendspin=1`)

Same visuals as kiosk, but audio is delivered via the [Sendspin](https://github.com/music-assistant/sendspin) SDK for clock-synchronized multi-room playback:

- Sync indicator (top-right): `CONNECTING` → `SYNCING` → `SYNCED`
- Custom Sendspin server URL: `?sendspin_url=http://<SERVER_IP>:8927`

### URL parameters summary

| Parameter | Example | Effect |
|-----------|---------|--------|
| `kiosk` | `?kiosk=1` | Enable kiosk mode |
| `sendspin` | `?kiosk=1&sendspin=1` | Kiosk + Sendspin synchronized audio |
| `sendspin_url` | `?sendspin_url=http://ma:8927` | Override Sendspin server URL |

## Quick Start

### Prerequisites

- [Music Assistant](https://music-assistant.io/) server (or a fork of the [MA server repo](https://github.com/trudenboy/ma-server))
- [Media Station X](https://msx.benzac.de/) app on your Smart TV
- Python 3.12+

### Setup

```bash
# 1. Clone this repo alongside the MA server
cd ~/Projects
git clone https://github.com/trudenboy/msx-music-assistant.git
git clone https://github.com/trudenboy/ma-server.git  # if not already

# 2. Setup venv, install deps, symlink provider into MA
cd msx-music-assistant
./scripts/link-to-ma.sh

# 3. Start MA server (provider auto-loads)
source ../ma-server/.venv/bin/activate
cd ../ma-server && python -m music_assistant --log-level debug
```

### Configure your TV

1. Open the MSX app on your Smart TV
2. Go to **Settings > Start Parameter**
3. Enter: `http://<YOUR_SERVER_IP>:8099/msx/start.json`
4. Restart MSX

You can also visit `http://<YOUR_SERVER_IP>:8099/` in a browser for a status dashboard showing the setup URL, registered players, and a **Quick stop** button per player to stop playback on the TV immediately (same effect as disabling the player in MA).

## HTTP Endpoints

### Web Player

| Method | Path | Description |
|--------|------|-------------|
| GET | `/web/` | Browser-based web player (no MSX app required) |

### MSX Bootstrap & Static Files

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Status dashboard (HTML) |
| GET | `/msx/start.json` | MSX start configuration |
| GET | `/msx/plugin.html` | MSX interaction plugin (device ID detection, WebSocket, menu) |
| GET | `/msx/sendspin-plugin.html` | Sendspin TVX Video Plugin (reserved for future use) |
| GET | `/msx/input.html` | MSX Input Plugin wrapper (search keyboard) |
| GET | `/msx/input.js` | Input Plugin logic |
| GET | `/msx/tvx-plugin-module.min.js` | TVX plugin module library |
| GET | `/msx/tvx-plugin.min.js` | TVX plugin library |

### MSX Content Pages (native JSON navigation)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/menu.json` | Main library menu |
| GET | `/msx/albums.json` | Albums list with drill-down actions |
| GET | `/msx/artists.json` | Artists list with drill-down actions |
| GET | `/msx/playlists.json` | Playlists list with drill-down actions |
| GET | `/msx/tracks.json` | Tracks list with play actions |
| GET | `/msx/recently-played.json` | Recently played tracks |
| GET | `/msx/search-page.json` | Search page with Input Plugin keyboard trigger |
| GET | `/msx/search-input.json?q=...` | Search results from Input Plugin keyboard |
| GET | `/msx/launcher.json` | Alternative launcher (MSX launcher param) |
| GET | `/msx/search.json?q=...` | Search results (artists, albums, tracks) |

### MSX Detail Pages

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/albums/{id}/tracks.json` | Tracks for an album |
| GET | `/msx/artists/{id}/albums.json` | Albums for an artist |
| GET | `/msx/playlists/{id}/tracks.json` | Tracks for a playlist |

### MSX Native Playlists

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/playlist/album/{id}.json` | Album tracks as MSX native playlist |
| GET | `/msx/playlist/playlist/{id}.json` | Playlist tracks as MSX native playlist |
| GET | `/msx/playlist/tracks.json` | All tracks as MSX native playlist |
| GET | `/msx/playlist/recently-played.json` | Recently played as MSX native playlist |
| GET | `/msx/playlist/search.json?q=...` | Search results as MSX native playlist |
| GET | `/msx/queue-playlist/{player_id}.json` | Current MA queue as MSX native playlist |

### Audio & Stream

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/audio/{player_id}?uri=...` | Trigger playback via MA queue + proxy audio stream |
| GET | `/stream/{player_id}` | Direct stream proxy (for already-playing media) |

### REST API (JSON)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/albums` | List albums |
| GET | `/api/albums/{id}/tracks` | Album tracks |
| GET | `/api/artists` | List artists |
| GET | `/api/artists/{id}/albums` | Artist albums |
| GET | `/api/playlists` | List playlists |
| GET | `/api/playlists/{id}/tracks` | Playlist tracks |
| GET | `/api/tracks` | List tracks |
| GET | `/api/search?q=...` | Search library |
| GET | `/api/recently-played` | Recently played tracks |
| GET | `/api/lyrics/{player_id}` | Lyrics for the currently playing track |
| GET | `/api/queue/{player_id}` | Current queue state |

### Playback Control

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/play` | Start playback (`{track_uri, player_id}`) |
| POST | `/api/pause/{player_id}` | Pause |
| POST | `/api/stop/{player_id}` | Stop |
| POST | `/api/quick-stop/{player_id}` | Stop playback on MSX immediately (stop + extra broadcast/cancel; use when normal Stop has ~30s delay) |
| POST | `/api/next/{player_id}` | Next track |
| POST | `/api/previous/{player_id}` | Previous track |

### WebSocket

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ws?device_id=...` | Bidirectional WebSocket: MA→TV (play/stop/pause/resume/playlist/goto_index/seek), TV→MA (position/pause/resume) |

### Utility

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (`{status, provider, players}`) |

## Configuration

The provider exposes seven config entries in the MA UI:

| Key | Default | Description |
|-----|---------|-------------|
| `http_port` | `8099` | Port for the embedded HTTP server |
| `output_format` | `mp3` | Audio format for streaming (`mp3`, `aac`, `flac`) |
| `player_idle_timeout` | `30` | Unregister idle MSX players after this many minutes |
| `show_stop_notification` | `false` | Show confirmation dialog on MSX when stopping playback from MA |
| `abort_stream_first` | `false` | When stopping: abort stream connection first, then send WebSocket stop (may help on some TVs) |
| `enable_player_grouping` | `true` | Allow grouping multiple MSX TVs for synchronized playback (experimental) |
| `group_stream_mode` | `independent` | How to stream to grouped players: `independent` (each TV gets own ffmpeg) or `shared` (one ffmpeg, multiple readers — less CPU) |

### Stop, Pause, and Resume

- **Stop** — Closes the MSX player immediately via a double broadcast (same signal as Disable).
- **Pause** — Pauses playback while keeping the MSX player open; **Play** resumes from the paused position.
- **Quick stop** — Dashboard button or `POST /api/quick-stop/{player_id}` for direct HTTP control.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (used by MA for venv management)
- MA server fork cloned alongside this project

### Setup & Run

```bash
# One-command setup: creates venv, installs deps, symlinks provider
./scripts/link-to-ma.sh

# Activate venv (required for all commands)
source ../ma-server/.venv/bin/activate

# Start server
cd ../ma-server && python -m music_assistant --log-level debug

# Run tests
pytest tests/ -v --ignore=tests/integration

# Run linting
cd ../ma-server && pre-commit run --all-files

# Verify provider imports
python -c "from music_assistant.providers.msx_bridge import setup; print('OK')"
```

See [CLAUDE.md](CLAUDE.md) for detailed development guidance and MA conventions.

## Project Structure

```
provider/msx_bridge/
├── __init__.py        # setup(), get_config_entries() — provider entry point
├── provider.py        # MSXBridgeProvider(PlayerProvider) — lifecycle, dynamic player registration, idle timeout
├── player.py          # MSXPlayer(Player) — Smart TV as MA player, WebSocket push notifications
├── http_server.py     # MSXHTTPServer — aiohttp routes for MSX + API + WebSocket
├── constants.py       # Config keys and defaults (7 entries)
├── manifest.json      # Provider metadata for MA
├── mappers.py         # MSX JSON mappers for content pages
├── models.py          # Pydantic models for MSX responses
└── static/
    ├── web/                    # Browser-based web player
    │   ├── index.html          # Web player UI
    │   └── web.js              # Player logic
    ├── plugin.html             # MSX interaction plugin (device ID, WebSocket, menu)
    ├── sendspin-plugin.html    # Sendspin TVX Video Plugin (reserved for future use)
    ├── input.html              # MSX Input Plugin wrapper (search keyboard)
    ├── input.js                # Input Plugin logic
    ├── tvx-plugin-module.min.js # TVX plugin module library
    └── tvx-plugin.min.js       # TVX plugin library

tests/
├── conftest.py         # Shared fixtures (mock MA, players, HTTP server)
├── test_init.py        # Provider setup tests
├── test_player.py      # MSXPlayer unit tests (42)
├── test_provider.py    # MSXBridgeProvider unit tests (9)
├── test_http_server.py # HTTP route tests (53)
├── test_group_stream.py # SharedGroupStream tests (20)
├── test_models.py      # Pydantic model tests (4)
├── test_mappers.py     # Mapper function tests (2)
├── test_playlist.py    # Playlist integration tests (5)
└── integration/        # Integration tests — require running MA server (30)

scripts/
├── link-to-ma.sh      # Setup venv + symlink provider into MA server
└── test-server.sh     # Start/stop/status/log for local MA dev server
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE).

## Credits

- [Music Assistant](https://music-assistant.io/) by Marcel Veldt
- [Media Station X](https://msx.benzac.de/) by Benjamin Zachey

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
