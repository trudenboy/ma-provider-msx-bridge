[← Getting Started](getting-started.md) · [Back to README](../README.md) · [Web Player →](web-player.md)

# Architecture

## Overview

MSX Music Assistant Bridge is a **Music Assistant Player Provider** — a plugin that runs inside the MA server process with direct access to internal APIs. No separate containers or services are needed.

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

## Components

| Component | Class | Role |
|-----------|-------|------|
| **Provider** | `MSXBridgeProvider` | MA `PlayerProvider` — lifecycle, player registration, idle timeout, WebSocket broadcast, group streaming |
| **Player** | `MSXPlayer` | MA `Player` — represents one Smart TV; stores stream URL, signals media-ready events |
| **HTTP Server** | `MSXHTTPServer` | aiohttp server — all routes: MSX JSON, audio, stream proxy, REST API, WebSocket, web player |

## Provider Lifecycle

```
handle_async_init()
    └─► loaded_in_mass()
            └─► discover_players()  (restores known players from storage)
                    └─► idle timeout loop  (runs every 60s, unregisters stale players)
                            └─► unload()
```

## Dynamic Player Registration

Each TV is identified by a **device ID** (from the MSX app) or falls back to IP address. Players are created on-demand on the first request and automatically removed after `player_idle_timeout` minutes of inactivity.

```
TV request arrives
    │
    ▼
_ensure_player_for_request()
    ├─► extract device_id or IP
    └─► provider.get_or_register_player(player_id)
            ├─► player exists → return it
            └─► new TV → create MSXPlayer → register with MA
```

## MSX Navigation Flow

```
start.json ──► plugin.html (interaction plugin)
                    │ detects device ID via TVXVideoPlugin.requestDeviceId()
                    │ opens WebSocket to /ws?device_id=...
                    ▼
               Main Menu (/msx/menu.json)
            ┌────┬────┬────┬────┐
            ▼    ▼    ▼    ▼    ▼
         Albums Artists Playlists Tracks Search
            │    │       │         │
            ▼    ▼       ▼         ▼
         Album  Artist  Playlist  ► Play
         Tracks Albums  Tracks
```

Content page items carry `action` fields:
- `"content:..."` — drill down to a detail page
- `"audio:..."` — play a single track (used inside MSX native playlists)
- `"playlist:..."` — load an MSX native playlist (auto-starts, TV-remote next/prev)

## Audio Playback Flow

```
TV clicks album track (action: "playlist:/msx/playlist/album/{id}.json")
    │
    ▼
MSX loads playlist JSON
    │ tracks rotated so clicked track is index 0 (MSX always plays from index 0)
    ▼
Each item: action: "audio:/msx/audio/{player_id}?uri=...&from_playlist=1"
    │
GET /msx/audio/{player_id}?uri=<track_uri>
    ├─► mass.player_queues.play_media() enqueues track
    ├─► wait for MSXPlayer.wait_for_media() (up to 10 s)
    └─► mass.streams.get_stream() → raw PCM
            └─► get_ffmpeg_stream() → MP3/AAC/FLAC → TV speakers
                (Content-Length set for MP3/AAC; omitted for FLAC)
```

## WebSocket Protocol

Connection: `GET /ws?device_id=<id>`

**MA → TV messages:**

| Type | Payload | Effect |
|------|---------|--------|
| `play` | `{title, artist, image, duration, next_action, prev_action}` | Start playback display |
| `stop` | — | Close MSX player immediately (sent twice) |
| `pause` | — | Pause display |
| `resume` | — | Resume display |
| `playlist` | `{url}` | Load MA queue as MSX native playlist |
| `goto_index` | `{index}` | Jump to track N in current playlist |
| `seek` | `{position_seconds}` | Seek to position |

**TV → MA messages:**

| Type | Payload | Effect |
|------|---------|--------|
| `position` | `{seconds}` | Update `player.current_position` (overrides wall-clock for 10 s) |
| `pause` | `{position}` | Pause player in MA |
| `resume` | — | Resume player in MA |

## Player Grouping

When `enable_player_grouping` is `true`, MSX players support the `SET_MEMBERS` feature. Play/pause/stop actions propagate to all group members.

**Stream modes** (configured per provider):
- `independent` — each TV gets its own ffmpeg process
- `shared` — one ffmpeg process, multiple readers with a catch-up buffer (less CPU, experimental)

## See Also

- [Getting Started](getting-started.md) — installation and TV setup
- [API Reference](api.md) — all HTTP endpoints
- [Configuration](configuration.md) — provider config entries
