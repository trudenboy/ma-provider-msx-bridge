[← Architecture](architecture.md) · [Back to README](../README.md) · [API Reference →](api.md)

# Browser Web Player

> **Deprecated.** The browser web kiosk is deprecated and will be removed in a
> future release. Use the standalone [Web Kiosk](https://github.com/trudenboy/ma-provider-web-kiosk)
> provider instead. This page documents the legacy behaviour only.

Open `http://<SERVER_IP>:8099/web/` in any browser — no MSX app or Smart TV required.

Each browser tab registers as its own MA player (device ID stored in `localStorage`). Playback is controlled independently per tab.

## Normal Mode (`/web/`)

Full library browser with sidebar navigation:

- **Sidebar** — Albums, Artists, Playlists, Tracks, Recently Played, Search
- **Content grid** — card view with album art; drill into album tracks / artist albums / playlist tracks
- **Bottom player bar** — prev / play-pause / next + progress scrubber
- **Full-screen player** (click the bar) — large album art, queue panel on the right, seek bar
- **HTML5 audio** — streams directly from the provider via the same `/msx/audio/` endpoint as the TV
- **WebSocket sync** — MA-initiated play/stop/pause/seek events reflected instantly

## Kiosk Mode (`/web/?kiosk=1`)

Immersive full-screen display for always-on screens (TV, kiosk, digital signage):

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

| Feature | Description |
|---------|-------------|
| **Three-column layout** | Album art + track info (left), lyrics / equalizer (center), queue (right) |
| **Karaoke lyrics** | LRC-synced scrolling from `/api/lyrics/{player_id}`; active line highlighted and enlarged |
| **CSS equalizer** | Animated bars shown when no lyrics are available |
| **Blurred background** | Album art fills screen, blurred + darkened via vignette overlay |
| **Auto-hiding controls** | Seek bar + prev/play/next fades out after inactivity; reappears on mouse move or touch |
| **Idle state** | Music note icon + "Waiting for playback…" when nothing is playing |
| **WebSocket push** | MA-initiated play/stop/pause/seek updates the display instantly |
| **Responsive** | Queue hidden on ≤ 900 px; single-column on mobile (≤ 640 px) |
| **4K support** | `@media (min-width: 1920px)` scales up fonts and controls |

## Kiosk + Sendspin Mode (`/web/?kiosk=1&sendspin=1`)

Same visuals as kiosk, but audio is delivered via the [Sendspin](https://github.com/music-assistant/sendspin) SDK for clock-synchronized multi-room playback:

- Sync indicator (top-right): `CONNECTING` → `SYNCING` → `SYNCED`
- Custom Sendspin server URL configurable via `?sendspin_url=http://<SERVER_IP>:8927`

## URL Parameters

| Parameter | Example | Effect |
|-----------|---------|--------|
| `kiosk` | `?kiosk=1` | Enable kiosk mode |
| `sendspin` | `?kiosk=1&sendspin=1` | Kiosk + Sendspin synchronized audio |
| `sendspin_url` | `?sendspin_url=http://ma:8927` | Override Sendspin server URL |

## See Also

- [API Reference](api.md) — `/api/lyrics/{player_id}`, `/api/queue/{player_id}` and other endpoints used by the web player
- [Architecture](architecture.md) — WebSocket protocol, player registration
- [Configuration](configuration.md) — output format affects web player audio quality
