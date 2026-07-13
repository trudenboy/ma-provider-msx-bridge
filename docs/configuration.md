[← API Reference](api.md) · [Back to README](../README.md) · [Development →](development.md)

# Configuration

The provider exposes seven settings in the Music Assistant UI under **Settings → Providers → MSX Bridge**.

## Config Entries

| Key | Default | Description |
|-----|---------|-------------|
| `http_port` | `8099` | Port for the embedded HTTP server |
| `output_format` | `mp3` | Audio format sent to TVs: `mp3`, `aac`, or `flac` |
| `player_idle_timeout` | `30` | Minutes before an idle (unconnected) TV player is unregistered |
| `show_stop_notification` | `false` | Show a confirmation dialog on MSX when MA stops playback |
| `abort_stream_first` | `false` | When stopping: abort the stream connection before sending the WebSocket stop signal (may reduce stop delay on some TVs) |
| `enable_player_grouping` | `true` | Allow grouping multiple MSX TVs for synchronized playback (experimental) |
| `enable_sendspin_bridge` | `false` | Register each TV as a Sendspin client for sample-synchronized playback with any MA players (experimental; requires a TV browser capable of running the Sendspin web client) |
| `group_stream_mode` | `independent` | How audio is delivered to TVs (see Stream Delivery Mode below) |

## Output Format

| Format | Bitrate estimate | Content-Length | Notes |
|--------|-----------------|----------------|-------|
| `mp3` | ~320 kbps (40,000 B/s) | ✅ Set | Best compatibility; MSX progress bar works |
| `aac` | ~256 kbps (32,000 B/s) | ✅ Set | Good quality, slightly smaller |
| `flac` | varies | ❌ Omitted | Lossless; MSX progress bar may not work |

MP3 is recommended for most TVs because the `Content-Length` header enables the MSX progress bar and seek. FLAC omits `Content-Length` (size is non-deterministic) which may prevent the progress bar from working.

## Player Idle Timeout

TVs are registered as MA players on their first request. The idle timeout controls when those players are cleaned up:

- **Activity** resets the timer (any HTTP request from the TV)
- **WebSocket connection** counts as activity; disconnection starts the timer
- **Playing** players are never cleaned up regardless of timeout
- Set to `0` to disable automatic cleanup (players persist until MA restarts)

## Stream Delivery Mode

Controls how audio reaches the TVs (config key `group_stream_mode`):

| Mode | Description | CPU |
|------|-------------|-----|
| `independent` | Each TV gets its own proxied ffmpeg process | Higher (one per TV) |
| `shared` | One ffmpeg process, output broadcast to all group members via a catch-up buffer | Lower |
| `redirect` | TVs are redirected to fetch audio directly from the Music Assistant streamserver | Lowest (no local ffmpeg) |

`shared` mode is experimental. Late-joining TVs receive buffered audio and may hear a brief gap at join time.

`redirect` mode lets Music Assistant apply the per-player codec setting and DSP itself. Notes:

- Falls back to `independent` automatically when the direct URL cannot be resolved.
- Tracks that require a continuous queue stream (e.g. crossfade enabled) are served through the local proxy instead, preserving per-track progress on the TV.
- Grouped TVs each fetch their own stream from MA — there is no shared-buffer synchronization in this mode.

## Stop and Pause Behavior

| Action | Effect on TV | Effect in MA |
|--------|-------------|--------------|
| **Stop** | Closes MSX player immediately | Sets player state to Stopped |
| **Pause** | Pauses playback, keeps MSX player open | Sets player state to Paused |
| **Play** (after pause) | Resumes from paused position | Sets player state to Playing |
| **Quick Stop** | Aborts stream + double WS stop broadcast | Stops immediately |

**`show_stop_notification`**: when enabled, MSX shows a confirmation dialog before closing the player. Useful to prevent accidental stops when controlling playback from MA.

**`abort_stream_first`**: if your TV takes ~30 seconds to close after a stop command, enable this. It aborts the HTTP stream connection first, then sends the WebSocket stop — some TVs respond faster to stream loss.

## See Also

- [Getting Started](getting-started.md) — initial setup
- [Architecture](architecture.md) — how config values affect streaming behavior
- [API Reference](api.md) — quick-stop endpoint and playback control
