[← Architecture](architecture.md) · [Back to README](../README.md) · [Configuration →](configuration.md)

# API Reference

Base URL: `http://<SERVER_IP>:8099`

All endpoints use HTTP/1.1. Audio streams use chunked transfer encoding. JSON endpoints return `application/json`.

## Status

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Status dashboard (HTML) — shows registered players, setup URL, quick-stop buttons |
| GET | `/health` | Health check — `{"status": "ok", "provider": "...", "players": [...]}` |

## MSX Bootstrap

These endpoints are consumed by the MSX app, not called directly.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/start.json` | MSX start configuration — entry point for the TV |
| GET | `/msx/plugin.html` | MSX interaction plugin (device ID detection, WebSocket, menu) |
| GET | `/msx/input.html` | MSX Input Plugin wrapper (search keyboard) |
| GET | `/msx/launcher.json` | Alternative launcher |

## MSX Content Pages

TV navigation pages — return MSX JSON with `action` fields for drill-down and playback.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/menu.json?device_id=...` | Main menu (Albums, Artists, Playlists, Tracks, Search) |
| GET | `/msx/albums.json?device_id=...` | Albums list |
| GET | `/msx/artists.json?device_id=...` | Artists list |
| GET | `/msx/playlists.json?device_id=...` | Playlists list |
| GET | `/msx/tracks.json?device_id=...` | Tracks list |
| GET | `/msx/recently-played.json?device_id=...` | Recently played tracks |
| GET | `/msx/search.json?q=...&device_id=...` | Search results |
| GET | `/msx/search-page.json?device_id=...` | Search page (opens Input Plugin keyboard) |
| GET | `/msx/search-input.json?q=...&device_id=...` | Search results from keyboard input |

## MSX Detail Pages

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/albums/{id}/tracks.json?device_id=...` | Tracks for a specific album |
| GET | `/msx/artists/{id}/albums.json?device_id=...` | Albums for a specific artist |
| GET | `/msx/playlists/{id}/tracks.json?device_id=...` | Tracks for a specific playlist |

## MSX Native Playlists

These return MSX native playlist JSON. MSX auto-starts playback when loaded via `playlist:` action.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/playlist/album/{id}.json?start=N&device_id=...` | Album tracks as playlist (rotated to start at index `N`) |
| GET | `/msx/playlist/playlist/{id}.json?start=N&device_id=...` | Playlist tracks as playlist |
| GET | `/msx/playlist/tracks.json?device_id=...` | All library tracks as playlist |
| GET | `/msx/playlist/recently-played.json?device_id=...` | Recently played as playlist |
| GET | `/msx/playlist/search.json?q=...&device_id=...` | Search results as playlist |
| GET | `/msx/queue-playlist/{player_id}.json` | Current MA queue as MSX native playlist |

## Audio & Stream

| Method | Path | Description |
|--------|------|-------------|
| GET | `/msx/audio/{player_id}?uri=<track_uri>&from_playlist=1` | Select the existing MA queue occurrence, wait for ready, stream audio |
| GET | `/stream/{player_id}` | Direct stream proxy for already-playing media |

**Audio response headers:**
- `Content-Type: audio/mpeg` (MP3), `audio/aac` (AAC), `audio/flac` (FLAC)
- `Content-Length`: omitted for independent MP3/AAC/FLAC; the encoded size is not known before EOF
- `Transfer-Encoding: chunked` when Content-Length is omitted

Redirected response headers are controlled by the Music Assistant Streamserver.

## REST Library API

Returns JSON. Useful for external clients (scripts, integrations).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/albums` | List all albums |
| GET | `/api/albums/{id}/tracks` | Tracks for an album |
| GET | `/api/artists` | List all artists |
| GET | `/api/artists/{id}/albums` | Albums for an artist |
| GET | `/api/playlists` | List all playlists |
| GET | `/api/playlists/{id}/tracks` | Tracks for a playlist |
| GET | `/api/tracks` | List all tracks |
| GET | `/api/search?q=...` | Search library (artists, albums, tracks) |
| GET | `/api/recently-played` | Recently played tracks |

## Playback Control

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/api/play` | `{"track_uri": "...", "player_id": "..."}` | Start playback |
| POST | `/api/pause/{player_id}` | — | Pause |
| POST | `/api/stop/{player_id}` | — | Stop and close MSX player |
| POST | `/api/quick-stop/{player_id}` | — | Instant stop (aborts stream + double WS broadcast) |
| GET/POST | `/api/next/{player_id}` | — | Manual Next track |
| GET/POST | `/api/complete/{player_id}?playback_id=<decoder_id>` | — | Consume current decoder completion using natural repeat semantics |
| POST | `/api/previous/{player_id}` | — | Previous track |

**Stop vs Quick Stop:** both eject/hide native MSX playback immediately. Quick stop additionally aborts the producer and broadcasts stop twice. With `show_stop_notification=true`, Stop shows an informational notice after eject; no Continue dialog can revive buffered playback.

Native queue audio URLs also carry the stream token, queue occurrence, decoder ID and playback generation. Old generations and disabled players cannot start a replacement stream; repeated completion callbacks are no-ops. Completion of a finite queue marks it ended so Play can restart it.

## WebSocket

`GET /ws?device_id=<id>`

See [Architecture — WebSocket Protocol](architecture.md#websocket-protocol) for full message type reference.

## See Also

- [Architecture](architecture.md) — how endpoints are wired to MA internals
- [Configuration](configuration.md) — port, output format, and other settings
- [Web Player](web-player.md) — browser client that consumes these endpoints
