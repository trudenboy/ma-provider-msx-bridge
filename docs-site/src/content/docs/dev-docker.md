---
title: Docker
---

# MSX Bridge — Local Development with Docker

Run a full Music Assistant instance with MSX Bridge provider pre-loaded locally —
no Python, FFmpeg, or other dependencies required.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

## Quick Start

```bash
docker compose -f docker-compose.dev.yml up
```

Open **http://localhost:8095** in your browser.

## First Run: Create a User

On first launch, Music Assistant runs an onboarding wizard:

1. **Create a user** — set a username and password (stored locally in `.ma-data/`)
2. Skip the Home Assistant integration if prompted
3. Your login state persists between container restarts via the `.ma-data/` volume

## Adding the MSX Bridge Provider

After login:

1. Go to **Settings** → **Providers**
2. Find **MSX Bridge** in the list — it's already available, the code is pre-loaded
3. Click **Add** and enter your credentials
4. Provider configuration is saved to `.ma-data/` and persists across restarts

> 💡 If the provider doesn't appear, check the logs:
> `docker compose -f docker-compose.dev.yml logs`
> Any startup error will be visible there.

## Container Commands

| Action | Command |
|--------|---------|
| Start | `docker compose -f docker-compose.dev.yml up` |
| Start in background | `docker compose -f docker-compose.dev.yml up -d` |
| Stop | `docker compose -f docker-compose.dev.yml down` |
| Restart | `docker compose -f docker-compose.dev.yml restart` |
| Follow logs | `docker compose -f docker-compose.dev.yml logs -f` |
| Reset state | `rm -rf .ma-data/` then start again |

## Updating Provider Code

Provider code from `provider/` is mounted via symlink — no image rebuild needed.
Changes take effect after restarting the container:

```bash
docker compose -f docker-compose.dev.yml restart
```

## Persistent State

All MA configuration, credentials, and cache are stored in `.ma-data/` (add to `.gitignore`).
This directory is created automatically on first run.
