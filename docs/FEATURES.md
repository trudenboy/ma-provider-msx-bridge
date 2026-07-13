# Features Guide

Detailed documentation for MSX Music Assistant Bridge advanced features.

## Browser Web Player

A lightweight web-based player that works in any modern browser without requiring the MSX app.

### Use Cases

- **Kitchen/Living Room** — Open on a tablet while cooking
- **Office/Coworking** — Background music on your laptop
- **Events** — Raspberry Pi + display in kiosk mode for parties
- **Gym/Fitness** — TV without MSX app — just open the URL in TV browser
- **Mobile Access** — Quick access from phone without installing apps

### Access

```
http://<SERVER_IP>:8099/web/
```

### Features

- Responsive design (desktop, tablet, mobile)
- Keyboard shortcuts:
  - `Space` — Play/Pause
  - `←` / `→` — Previous/Next track
  - `↑` / `↓` — Volume up/down
- Album art display
- Volume control
- Track progress bar
- Library browsing (Albums, Artists, Playlists, Tracks)
- Search functionality

### Kiosk Mode Setup (Raspberry Pi)

```bash
# Install Chromium
sudo apt install chromium-browser

# Create autostart script
cat > ~/.config/autostart/music-kiosk.desktop << EOF
[Desktop Entry]
Type=Application
Name=Music Kiosk
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars http://<SERVER_IP>:8099/web/
EOF
```

---

## Player Grouping (Experimental)

Synchronized playback control across multiple TVs. Note: this feature synchronizes play/pause/stop/next/prev commands, but does not sync the audio streams themselves — each TV fetches its own independent stream, so there may be slight timing differences between devices.

### Use Cases

- **Smart Home** — Same music in living room and kitchen simultaneously
- **Restaurant/Cafe** — Background music on all screens in sync
- **Retail Store** — Synchronized audio across store displays
- **Party** — Music playing in multiple rooms at once

### Setup

1. Enable `enable_player_grouping` in MA settings (default: enabled)
2. Open MA web interface
3. Go to Players section
4. Select multiple MSX players
5. Create a group
6. Play music — all grouped TVs play in sync

### How It Works

```
MA Group Command
      │
      ▼
┌─────────────┐
│ Group Leader│ (first TV in group)
│   msx_tv1   │
└──────┬──────┘
       │ propagate command
       ├─────────────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│   Member    │   │   Member    │
│   msx_tv2   │   │   msx_tv3   │
└─────────────┘   └─────────────┘
```

### Stream Delivery Modes

The `group_stream_mode` config option controls how audio is delivered to TVs:

| Mode | Description | Use Case |
|------|-------------|----------|
| `independent` (default) | Each TV gets its own proxied ffmpeg process | Maximum compatibility, slightly higher CPU |
| `shared` | One ffmpeg process, multiple readers | Lower CPU usage, better for many grouped TVs |
| `redirect` | TVs fetch audio directly from the MA streamserver (no local ffmpeg) | Lowest CPU; per-player codec and DSP applied by MA; no shared-buffer group sync |

```
Independent Mode:
┌─────────┐     ┌─────────┐     ┌─────────┐
│ ffmpeg  │     │ ffmpeg  │     │ ffmpeg  │
└────┬────┘     └────┬────┘     └────┬────┘
     │               │               │
     ▼               ▼               ▼
   TV 1            TV 2            TV 3

Shared Buffer Mode:
            ┌─────────┐
            │ ffmpeg  │
            └────┬────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      TV 1     TV 2     TV 3
```

### Limitations

- **No audio stream synchronization** — each TV receives its own independent audio stream, so playback timing may differ by 100-500ms+ between devices
- Volume syncs but may need individual adjustment on some TVs
- Experimental: may have issues with 3+ TVs in poor network conditions
- All TVs in group must be on the same MA server
- Not suitable for scenarios requiring precise audio sync (e.g., same room with multiple speakers)

### Troubleshooting

**Problem:** One TV in group doesn't play
- Check WebSocket connection in browser dev tools
- Verify TV is registered in MA Players list
- Try removing and re-adding TV to group

**Problem:** Significant delay between TVs
- Check network latency between server and TVs
- Use wired Ethernet if possible
- Reduce group size

---

## MSX Native Playlists

Seamless integration between MA queue and MSX playlist navigation for natural album/playlist playback.

### Use Cases

- **Album Listening** — Select album → all tracks added to MSX queue → next/prev work on TV remote
- **Playlist Playback** — Start playlist in MA → TV shows current track and allows navigation
- **MA UI Control** — Switch track in MA → TV automatically switches

### How It Works

When you play an album or playlist:

```
1. MA creates queue with all tracks
   [Track 1] [Track 2] [Track 3] ...

2. MSX Bridge generates native MSX playlist
   {
     "type": "list",
     "items": [
       {"title": "Track 1", "action": "audio:..."},
       {"title": "Track 2", "action": "audio:..."},
       ...
     ]
   }

3. MSX player loads playlist
   ┌─────────────────────┐
   │ ▶ Track 1  3:45     │
   │   Track 2  4:12     │
   │   Track 3  3:58     │
   └─────────────────────┘

4. TV remote navigation works naturally
   [◄ Prev] [▶ Play/Pause] [Next ►]
```

### Queue Synchronization

```
MA Queue ←→ MSX Playlist
   ↓              ↓
[Track 1]    [Track 1] ▶ Playing
[Track 2]    [Track 2]
[Track 3]    [Track 3]
```

When you change track in MA UI:
1. MA sends WebSocket message to MSX
2. MSX plugin receives `goto_index` command
3. MSX player jumps to correct track
4. Audio stream switches seamlessly

### Features

- Bidirectional sync between MA and MSX
- Track position preserved on pause/resume
- Support for shuffle and repeat modes (via MA)
- Album art displayed for each track

---

## Bidirectional WebSocket Sync (🚧 In Development)

Real-time synchronization between MA UI and MSX player state.

### Planned Features

- **Position Tracking** — Playback position displayed in MA UI in real-time
- **Pause/Resume Sync** — Pause on TV reflects in MA and vice versa
- **Real-time Updates** — Instant notifications without polling

### Current State

Currently implemented:
- MA → MSX: Play, Stop, Pause commands
- MA → MSX: Track change notifications
- MSX → MA: Player registration

In development:
- MSX → MA: Position updates
- MSX → MA: Playback state changes

---

## Sendspin Integration (Reserved)

Infrastructure for clock-synchronized audio playback using the Sendspin protocol.

### Current Status

**Disabled** — The Sendspin plugin infrastructure is implemented but disabled. It requires Music Assistant core to support streaming audio to specific Sendspin player IDs, which is not yet available.

### What's Implemented

- `sendspin-plugin.html` — TVX Video Plugin with:
  - Sync indicator UI (SYNC / CONNECTING / ERROR states)
  - Dynamic Sendspin SDK loading via ES modules
  - `SendspinMSXPlayer` class implementing TVX Video Plugin interface
  - Connection handling with error fallback

### Future Plans

When MA core adds support for Sendspin player targeting:
1. Enable `sendspin_enabled` config option
2. Action URLs will switch from `audio:http://...` to `audio:plugin:http://.../sendspin-plugin.html`
3. Clock-synchronized playback across multiple TVs

### Why Sendspin?

Sendspin protocol provides sample-accurate audio synchronization across devices. Unlike the current HTTP streaming approach (which has 100-500ms variance), Sendspin can achieve <10ms sync — ideal for multi-room setups where you can hear multiple speakers.

---

## WebSocket Reconnection with Jitter

Robust WebSocket connection handling with exponential backoff and jitter.

### How It Works

When WebSocket connection is lost:

```
Attempt 1: Wait 1s + random(0-500ms)
Attempt 2: Wait 2s + random(0-500ms)
Attempt 3: Wait 4s + random(0-500ms)
Attempt 4: Wait 8s + random(0-500ms)
...
Max wait: 30s + random(0-500ms)
```

### Benefits

- Prevents server overload when multiple TVs reconnect simultaneously
- Handles temporary network issues gracefully
- Automatic recovery without user intervention

### Configuration

The reconnection behavior is automatic and requires no configuration. If you need to manually reconnect:

1. Refresh MSX app on TV (usually: Menu → Reload)
2. Or restart MSX app completely
