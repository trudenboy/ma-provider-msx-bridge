# Features Guide

Detailed documentation for MSX Music Assistant Bridge advanced features.

## Browser Web Player

The browser web player and kiosk are no longer part of this provider.
Use the standalone Web Kiosk provider for always-on displays.

---

## Multi-TV Playback

Create a Music Assistant Universal Group and select the MSX TVs as members. Universal Group owns playback fan-out and serves one continuous flow timeline; MSX Bridge has no separate native grouping model.

The default `redirect` delivery mode passes each member's Universal Group URL directly to the TV. The advanced `independent` mode uses a local ffmpeg proxy and is intended only as a compatibility fallback.

Universal Groups coordinate playback but cannot provide sample-accurate synchronization through the native MSX audio player. TVs in the same room may produce audible timing differences.

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
