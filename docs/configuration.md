[← API Reference](api.md) · [Back to README](../README.md) · [Development →](development.md)

# Configuration

The provider exposes these settings in the Music Assistant UI under **Settings → Providers → MSX Bridge**.

## Config Entries

| Key | Default | Description |
|-----|---------|-------------|
| `http_port` | `8099` | Port for the embedded HTTP server |
| `output_format` | `mp3` | Audio format sent to TVs: `mp3`, `aac`, or `flac` |
| `player_idle_timeout` | `30` | Minutes before an idle (unconnected) TV player is unregistered |
| `show_stop_notification` | `false` | Show a confirmation dialog on MSX when MA stops playback |
| `group_stream_mode` | `redirect` | Advanced: how audio is delivered to TVs (see Stream Delivery Mode below) |
| `include_content_length` | `true` | Advanced: include an estimated length on local MP3/AAC proxy responses |

## Output Format

| Format | Bitrate estimate | Content-Length | Notes |
|--------|-----------------|----------------|-------|
| `mp3` | ~320 kbps (40,000 B/s) | ✅ Set | Best compatibility; MSX progress bar works |
| `aac` | ~256 kbps (32,000 B/s) | ✅ Set | Good quality, slightly smaller |
| `flac` | varies | ❌ Omitted | Lossless; MSX progress bar may not work |

MP3 is recommended for most TVs because the estimated `Content-Length` header can improve the MSX progress bar and seek behavior. Disable `include_content_length` if a TV truncates or rejects local proxy streams. FLAC always omits the header because its encoded size is non-deterministic. Redirected responses are controlled by the Music Assistant Streamserver, not this option.

Each MSX player defaults to Music Assistant's `forced_content_length` HTTP profile. This gives redirected finite tracks an estimated length so MSX can display playback progress. The profile is available in the advanced per-player settings; Universal Group flow streams remain continuous and do not have a finite per-track HTTP length.

## Player Idle Timeout

TVs are registered as MA players on their first request. The idle timeout controls when those players are cleaned up:

- **Activity** resets the timer (any HTTP request from the TV)
- **WebSocket connection** counts as activity; disconnection starts the timer
- Values below one minute are clamped to one minute
- Any request from an active TV refreshes its activity timestamp

## Stream Delivery Mode

Controls how audio reaches the TVs (config key `group_stream_mode`):

| Mode | Description | CPU |
|------|-------------|-----|
| `redirect` | TVs are redirected to fetch audio directly from the Music Assistant streamserver | Lowest (no local ffmpeg) |
| `independent` | Each TV gets its own proxied ffmpeg process | Higher (one per TV) |

`redirect` mode lets Music Assistant apply the per-player codec setting and DSP itself. Notes:

- Falls back to `independent` automatically when the direct URL cannot be resolved.
- Tracks that require a continuous queue stream (e.g. crossfade enabled) are served through the local proxy instead, preserving per-track progress on the TV.
- Universal Group flow streams are passed through to each member TV.

The removed legacy `shared` value is migrated to `independent`. Recreate any old native MSX groups as Music Assistant Universal Groups.

## Stop and Pause Behavior

| Action | Effect on TV | Effect in MA |
|--------|-------------|--------------|
| **Stop** | Closes MSX player immediately | Sets player state to Stopped |
| **Pause** | Pauses playback, keeps MSX player open | Sets player state to Paused |
| **Play** (after pause) | Resumes from paused position | Sets player state to Playing |
| **Quick Stop** | Aborts stream + double WS stop broadcast | Stops immediately |

**`show_stop_notification`**: when enabled, MSX shows a confirmation dialog before closing the player. Useful to prevent accidental stops when controlling playback from MA.

## See Also

- [Getting Started](getting-started.md) — initial setup
- [Architecture](architecture.md) — how config values affect streaming behavior
- [API Reference](api.md) — quick-stop endpoint and playback control
