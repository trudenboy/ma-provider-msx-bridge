# Domain

**Queue handshake** — MA queue becomes an MSX native playlist; later `/msx/audio` fetches must reuse that queue instead of destroying it.

**Native playlist** — MSX `playlist:{url}` document built from MA queue or library tracks.

**Audio pipeline** — how encoded audio reaches the TV: redirect, shared group stream, or independent ffmpeg.

**Shared group stream** — one ffmpeg producer, multiple TV readers with a catch-up buffer.

**Party adapter** — the MA Party plugin seen from MSX: join QR, stamped covers, SSRF allowlist.
