"""Read-only live MSX HTTP checks; save statuses without tokens or credentials."""

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# Standalone diagnostic CLI: namespace packaging and console output are intentional.
# ruff: noqa: INP001, T201

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base-url", default="http://192.168.10.229:8099")
parser.add_argument("--output", type=Path, default=Path(".cache/pixel8-e2e/http-results.json"))
args = parser.parse_args()
BASE = args.base_url.rstrip("/")
if urllib.parse.urlsplit(BASE).scheme not in ("http", "https"):
    parser.error("--base-url must use http or https")
results = []


def check(
    path: str,
    expected: int = 200,
    *,
    method: str = "GET",
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """Check a live response status and record a token-free result."""
    req = urllib.request.Request(  # noqa: S310 - base scheme validated above
        BASE + path, data=data, headers=headers or {}, method=method
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310 - HTTP(S) only
            status, body = response.status, response.read()
    except urllib.error.HTTPError as err:
        status, body = err.code, err.read()
    try:
        payload = json.loads(body)
    except ValueError, UnicodeDecodeError:
        payload = None
    result = {
        "path": path,
        "method": method,
        "expected": expected,
        "status": status,
        "pass": status == expected,
        "seconds": round(time.monotonic() - started, 3),
        "bytes": len(body),
    }
    if isinstance(payload, dict):
        result["items"] = len(payload.get("items", []))
    results.append(result)
    print(json.dumps(result), flush=True)
    return payload


for path in (
    "/health",
    "/msx/start.json",
    "/msx/launcher.json",
    "/msx/menu.json",
    "/msx/albums.json",
    "/msx/artists.json",
    "/msx/playlists.json",
    "/msx/tracks.json",
    "/msx/recently-played.json",
    "/msx/party.json",
    "/api/party",
    "/msx/plugin.html",
    "/msx/input.html",
    "/msx/input.js",
):
    check(path)
for kind in ("albums", "artists", "playlists", "tracks", "recently-played"):
    payload = check("/api/" + kind)
    if kind in ("albums", "artists", "playlists") and payload and payload.get("items"):
        item = payload["items"][0]
        suffix = "albums" if kind == "artists" else "tracks"
        check("/api/" + kind + "/" + urllib.parse.quote(str(item["item_id"])) + "/" + suffix)
        check(
            "/msx/" + kind + "/" + urllib.parse.quote(str(item["item_id"])) + "/" + suffix + ".json"
        )
check("/api/search", 400)
for query in ("Trooper", "Браво", "msxe2e_no_hits_954786"):
    check("/api/search?q=" + urllib.parse.quote(query))
for body in (
    b"{",
    b"[]",
    b"{}",
    b'{"track_uri":17,"player_id":"unknown"}',
    b'{"track_uri":"http://example.invalid/audio.mp3","player_id":"unknown"}',
):
    check("/api/play", 400, method="POST", data=body, headers={"Content-Type": "application/json"})
check(
    "/api/play",
    404,
    method="POST",
    data=b'{"track_uri":"library://track/1","player_id":"msx_e2e_missing"}',
    headers={"Content-Type": "application/json"},
)
for action in ("pause", "stop", "quick-stop", "next", "previous", "complete"):
    check("/api/" + action + "/msx_e2e_missing", 404)
    check("/api/" + action + "/msx_e2e_missing", 403, headers={"Sec-Fetch-Site": "cross-site"})
check(
    "/api/play",
    403,
    method="POST",
    data=b"{}",
    headers={"Sec-Fetch-Site": "cross-site", "Content-Type": "application/json"},
)
check("/msx/audio/msx_e2e_missing?token=invalid", 400)
check("/msx/audio/msx_192_168_10_229?token=invalid&uri=library%3A%2F%2Ftrack%2F1", 403)
check("/msx/playlist/tracks.json", 403, headers={"Sec-Fetch-Site": "cross-site"})
check(
    "/ws",
    403,
    headers={
        "Origin": "https://example.invalid",
        "Upgrade": "websocket",
        "Connection": "Upgrade",
        "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
        "Sec-WebSocket-Version": "13",
    },
)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(results, indent=2))
print("TOTAL", len(results), "PASS", sum(r["pass"] for r in results))

raise SystemExit(0 if all(r["pass"] for r in results) else 1)
