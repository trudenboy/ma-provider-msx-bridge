# Domain

**Queue handshake** — MA queue becomes an MSX native playlist; later `/msx/audio` fetches must reuse that queue instead of destroying it.

**Native playlist** — MSX `playlist:{url}` document built from MA queue or library tracks.

**Audio pipeline** — how encoded audio reaches the TV: MA Streamserver redirect or independent local ffmpeg proxy.

**Universal Group** — MA-owned multi-player flow session; MSX TVs participate as regular member players.

**Party adapter** — the MA Party plugin seen from MSX: join QR, stamped covers, SSRF allowlist.
