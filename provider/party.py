"""Party plugin adapter: QR, cover stamp, SSRF allowlist."""

from __future__ import annotations

import asyncio
import functools
import hashlib
import io
import logging
import time
from typing import TYPE_CHECKING, Any, NamedTuple, cast
from urllib.parse import quote, urlsplit

import aiohttp
from aiohttp import web
from music_assistant_models.errors import MusicAssistantError

from music_assistant.helpers.util import join_task

if TYPE_CHECKING:
    from .provider import MSXBridgeProvider

logger = logging.getLogger(__name__)

PARTY_CACHE_TTL = 10.0
PARTY_CALL_TIMEOUT = 5.0
COVER_FETCH_MAX_BYTES = 2 * 1024 * 1024
COVER_MAX_PIXELS = 4096 * 4096


class PartyInfo(NamedTuple):
    """Active-party details resolved from the MA Party plugin."""

    join_url: str
    name: str | None
    qr_text: str | None
    qr_version: str


class PartyAdapter:
    """Answer whether a party is active and stamp its join QR onto covers."""

    def __init__(self, provider: MSXBridgeProvider) -> None:
        """Initialize the adapter."""
        self.provider = provider
        self.cache: tuple[float, PartyInfo | None] | None = None
        self.qr_cover_cache: dict[tuple[str, str], bytes] = {}
        self.qr_cover_inflight: dict[tuple[str, str], asyncio.Task[bytes]] = {}

    def cached_party(self) -> PartyInfo | None:
        """Return the last cached party state without refreshing (sync contexts)."""
        return self.cache[1] if self.cache else None

    async def qr_cover_base(self, prefix: str) -> str | None:
        """Return the QR-cover endpoint base when a party is active, else None."""
        if await self.get_active_party() is None:
            return None
        return f"{prefix}/api/party/qr-cover.png"

    def rewrite_play_image(self, image_url: str, client_prefix: str) -> str:
        """Route a play background through the QR compositor when a party is cached."""
        if not self.cached_party():
            return image_url
        return f"{client_prefix}/api/party/qr-cover.png?image={quote(image_url, safe='')}"

    async def get_active_party(self) -> PartyInfo | None:
        """
        Return details of the active party, or None when no party is active.

        Never raises: a broken or slow Party plugin degrades to "no party" so
        the core UI (menu) keeps working. Results are cached briefly.
        """
        now = time.monotonic()
        if self.cache is not None and now - self.cache[0] < PARTY_CACHE_TTL:
            return self.cache[1]
        info: PartyInfo | None = None
        try:
            party = cast("Any", self.provider.mass.get_provider("party"))
            if party is not None:
                join_url = await asyncio.wait_for(party.get_party_url(), PARTY_CALL_TIMEOUT)
                if join_url:
                    config = await asyncio.wait_for(party.get_party_config(), PARTY_CALL_TIMEOUT)
                    info = PartyInfo(
                        join_url=join_url,
                        name=getattr(config, "party_name", None),
                        qr_text=getattr(config, "qr_text", None),
                        qr_version=hashlib.sha256(join_url.encode()).hexdigest()[:12],
                    )
        except MusicAssistantError, RuntimeError, TimeoutError:
            logger.warning("Party plugin status check failed", exc_info=True)
        self.cache = (now, info)
        return info

    async def handle_status(self, _request: web.Request) -> web.Response:
        """Return party status for MSX party pages."""
        party = await self.get_active_party()
        if party is None:
            return web.json_response({"active": False})
        return web.json_response(
            {
                "active": True,
                "name": party.name,
                "qr_text": party.qr_text,
                "qr_url": "/api/party/qr.svg",
                "qr_version": party.qr_version,
            }
        )

    async def handle_qr(self, request: web.Request) -> web.Response:
        """Serve the guest join URL as a QR code image (SVG or PNG by route)."""
        party = await self.get_active_party()
        if party is None:
            return web.Response(status=404, text="No active party")
        kind = "png" if request.path.endswith(".png") else "svg"
        body = await asyncio.to_thread(render_qr, party.join_url, kind)
        return web.Response(
            body=body,
            content_type="image/png" if kind == "png" else "image/svg+xml",
            headers={"Cache-Control": "no-store"},
        )

    async def handle_qr_cover(
        self, request: web.Request, *, extra_bases: list[str]
    ) -> web.Response:
        """Serve a cover image with the party QR stamped into its corner (PNG)."""
        image_url = request.query.get("image", "")
        if not image_url:
            return web.Response(status=400, text="Missing image parameter")
        if not is_allowed_cover_source(image_url, extra_bases):
            return web.Response(status=400, text="Image source not permitted")
        party = await self.get_active_party()
        if party is None:
            raise web.HTTPFound(location=image_url)
        cache_key = (image_url, party.qr_version)
        if (cached := self.qr_cover_cache.get(cache_key)) is None:
            try:
                cached = await join_task(self.qr_cover_task(cache_key, image_url, party.join_url))
            except (aiohttp.ClientError, OSError, RuntimeError, ValueError) as err:
                logger.debug("QR cover composite failed for %s: %s", image_url, err)
                raise web.HTTPFound(location=image_url) from None
        return web.Response(
            body=cached,
            content_type="image/png",
            headers={"Cache-Control": "no-store"},
        )

    def qr_cover_task(
        self, cache_key: tuple[str, str], image_url: str, join_url: str
    ) -> asyncio.Task[bytes]:
        """Return the in-flight render task for this cover, starting one if needed."""
        if (task := self.qr_cover_inflight.get(cache_key)) is None:
            task = asyncio.create_task(self._fetch_and_render_cover(cache_key, image_url, join_url))
            self.qr_cover_inflight[cache_key] = task

            def _cleanup(finished: asyncio.Task[bytes]) -> None:
                self.qr_cover_inflight.pop(cache_key, None)
                if not finished.cancelled():
                    finished.exception()

            task.add_done_callback(_cleanup)
        return task

    async def _fetch_and_render_cover(
        self, cache_key: tuple[str, str], image_url: str, join_url: str
    ) -> bytes:
        """Fetch the cover, composite the QR onto it, and cache the PNG."""
        async with self.provider.mass.http_session.get(
            image_url,
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=False,
        ) as resp:
            if resp.status != 200:
                raise ValueError(f"cover fetch returned HTTP {resp.status}")
            raw_len = resp.headers.get("Content-Length")
            if isinstance(raw_len, (str, bytes, int)):
                try:
                    declared = int(raw_len)
                except TypeError, ValueError:
                    declared = 0
                if declared > COVER_FETCH_MAX_BYTES:
                    raise ValueError("cover exceeds size limit")
            cover_bytes = await _read_capped(resp, COVER_FETCH_MAX_BYTES)
        rendered = await asyncio.to_thread(render_qr_cover, join_url, cover_bytes)
        if len(self.qr_cover_cache) >= 32:
            self.qr_cover_cache.clear()
        self.qr_cover_cache[cache_key] = rendered
        return rendered


@functools.lru_cache(maxsize=4)
def render_qr(join_url: str, kind: str) -> bytes:
    """
    Render the join URL as a QR image (blocking on a miss; run in a worker thread).

    Results are memoized — the output only changes when the join code rotates.
    """
    import segno  # noqa: PLC0415

    buf = io.BytesIO()
    segno.make(join_url, error="m").save(buf, kind=kind, scale=8)
    return buf.getvalue()


def render_qr_cover(join_url: str, cover_bytes: bytes) -> bytes:
    """Render the QR and composite it onto the cover (blocking; run in a worker thread)."""
    return stamp_qr_on_cover(cover_bytes, render_qr(join_url, "png"))


async def _read_capped(resp: aiohttp.ClientResponse, max_bytes: int) -> bytes:
    """Read a response body, aborting if it exceeds max_bytes."""
    content = getattr(resp, "content", None)
    iter_chunked = getattr(content, "iter_chunked", None)
    if callable(iter_chunked):
        buf = bytearray()
        try:
            async for chunk in iter_chunked(65536):
                if not isinstance(chunk, (bytes, bytearray)):
                    raise TypeError
                buf.extend(chunk)
                if len(buf) > max_bytes:
                    raise ValueError("cover exceeds size limit")
            return bytes(buf)
        except TypeError:
            pass
    body = await resp.read()
    if len(body) > max_bytes:
        raise ValueError("cover exceeds size limit")
    return body


def stamp_qr_on_cover(cover_bytes: bytes, qr_bytes: bytes) -> bytes:
    """Composite the QR into the cover's bottom-right corner; returns PNG bytes."""
    import warnings  # noqa: PLC0415

    from PIL import Image  # noqa: PLC0415

    previous_limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = COVER_MAX_PIXELS
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            cover = Image.open(io.BytesIO(cover_bytes)).convert("RGB")
            qr = Image.open(io.BytesIO(qr_bytes)).convert("RGB")
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as err:
        raise ValueError("image exceeds Pillow decompression limit") from err
    finally:
        Image.MAX_IMAGE_PIXELS = previous_limit
    side = max(48, min(cover.width, cover.height) * 28 // 100)
    qr = qr.resize((side, side), Image.Resampling.NEAREST)
    margin = side // 8
    cover.paste(qr, (cover.width - side - margin, cover.height - side - margin))
    out = io.BytesIO()
    cover.save(out, format="PNG")
    return out.getvalue()


def url_origin(url: str) -> tuple[str, str | None, int | None]:
    """Return (scheme, hostname, port); raises ValueError on malformed URLs."""
    parts = urlsplit(url)
    return (parts.scheme, parts.hostname, parts.port)


def is_allowed_cover_source(image_url: str, allowed_bases: list[str]) -> bool:
    """Only composite covers served by this provider or MA itself (no open proxy)."""
    try:
        target_origin = url_origin(image_url)
    except ValueError:
        return False
    if target_origin[0] not in ("http", "https") or not target_origin[1]:
        return False
    for base in allowed_bases:
        try:
            if target_origin == url_origin(base):
                return True
        except ValueError:
            continue
    return False
