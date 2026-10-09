[← API Reference](api.md) · [Back to README](../README.md) · [Development →](development.md)

# Configuration

The provider exposes these settings in the Music Assistant UI under **Settings → Providers → MSX Bridge**.

## Config Entries

| Key | Default | Description |
|-----|---------|-------------|
| `http_port` | `8099` | Port for the embedded HTTP server |
| `output_format` | `mp3` | Audio format sent to TVs: `mp3`, `aac`, or `flac` |
| `player_idle_timeout` | `30` | Minutes before an idle (unconnected) TV player is unregistered |
| `show_stop_notification` | `false` | Show an informational notice after MSX playback is stopped |
| `group_stream_mode` | `redirect` | Advanced: how audio is delivered to TVs (see Stream Delivery Mode below) |
| `include_content_length` | `false` | Deprecated compatibility key, hidden from new setup; independent streaming always omits estimated lengths |

## Output Format

| Format | Independent delivery | Notes |
|--------|----------------------|-------|
| `mp3` | Chunked, no estimated Content-Length | Broad decoder compatibility |
| `aac` | Chunked, no estimated Content-Length | Encoded size varies with content |
| `flac` | Chunked, no estimated Content-Length | Lossless |

Streaming encoders add headers and padding; a bitrate estimate is not an exact body size. Independent delivery therefore omits Content-Length even if the legacy `include_content_length` value remains saved as `true`.

New MSX players default to Music Assistant's `chunked` HTTP profile. Existing explicitly saved per-player `http_profile` values are preserved. If redirected MP3/AAC playback truncates or never reaches EOF, select `chunked` in the player's advanced settings; the provider-level legacy switch does not control MA Streamserver responses. Universal Group flow streams remain continuous.

The native position labels display source time, while MSX reports stream time to MA (MA adds the seek offset). Known durations are supplied to the native controls. Native rewind/forward buttons request a new MA stream at the source position; arbitrary HTTP Range seeking is unavailable for these chunked transcodes, so the native progress marker is disabled. Seek through MA remains available.

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

## Playback limitations

- Native progress-marker dragging is disabled for chunked transcodes. Forward/rewind and MA seek rebuild the stream at a source position; device and group compatibility still require verification.
- MA dev stops a paused queue after 30 seconds to release its stream. Resume uses MA's saved position.
