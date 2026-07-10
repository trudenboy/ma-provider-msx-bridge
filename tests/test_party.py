"""Tests for the Party Mode endpoints (spec 0001)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock

if TYPE_CHECKING:
    from aiohttp.test_utils import TestClient

JOIN_URL = "http://ma.local:8095/?join=ABC123"


def _party_mock(
    url: str | None = JOIN_URL,
    name: str | None = "My Party",
    qr_text: str | None = "Scan to join!",
) -> Mock:
    """Return a mock Party plugin provider."""
    party = Mock()
    party.get_party_url = AsyncMock(return_value=url)
    config = Mock()
    config.party_name = name
    config.qr_text = qr_text
    party.get_party_config = AsyncMock(return_value=config)
    return party


# --- /api/party status endpoint ---


async def test_party_status_no_plugin(http_client: TestClient[Any, Any]) -> None:
    """GET /api/party should report inactive when the Party plugin is not loaded."""
    resp = await http_client.get("/api/party")
    assert resp.status == 200
    data = await resp.json()
    assert data == {"active": False}


async def test_party_status_guest_access_off(
    http_client: TestClient[Any, Any], mass_mock: Mock
) -> None:
    """GET /api/party should report inactive when guest access is disabled."""
    mass_mock.get_provider = Mock(return_value=_party_mock(url=None))
    resp = await http_client.get("/api/party")
    assert resp.status == 200
    data = await resp.json()
    assert data == {"active": False}


async def test_party_status_active(http_client: TestClient[Any, Any], mass_mock: Mock) -> None:
    """GET /api/party should return party name, caption and QR URL when active."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/api/party")
    assert resp.status == 200
    data = await resp.json()
    assert data["active"] is True
    assert data["name"] == "My Party"
    assert data["qr_text"] == "Scan to join!"
    assert data["qr_url"].endswith("/api/party/qr.svg")
    mass_mock.get_provider.assert_called_with("party")


async def test_party_status_active_without_custom_texts(
    http_client: TestClient[Any, Any], mass_mock: Mock
) -> None:
    """GET /api/party should tolerate unset party name and caption."""
    mass_mock.get_provider = Mock(return_value=_party_mock(name=None, qr_text=None))
    resp = await http_client.get("/api/party")
    assert resp.status == 200
    data = await resp.json()
    assert data["active"] is True
    assert data["name"] is None
    assert data["qr_text"] is None


async def test_party_status_does_not_leak_join_url(
    http_client: TestClient[Any, Any], mass_mock: Mock
) -> None:
    """GET /api/party must not include the raw join URL in the response."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/api/party")
    body = await resp.text()
    assert JOIN_URL not in body


# --- /api/party/qr.svg image endpoint ---


async def test_party_qr_svg_active(http_client: TestClient[Any, Any], mass_mock: Mock) -> None:
    """GET /api/party/qr.svg should return an SVG QR code of the join URL."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/api/party/qr.svg")
    assert resp.status == 200
    assert "image/svg+xml" in resp.headers["Content-Type"]
    body = await resp.text()
    assert "<svg" in body


async def test_party_qr_not_cached(http_client: TestClient[Any, Any], mass_mock: Mock) -> None:
    """The QR image must not be cacheable — the join code can rotate."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/api/party/qr.svg")
    assert resp.status == 200
    assert "no-store" in resp.headers.get("Cache-Control", "")


async def test_party_qr_404_no_plugin(http_client: TestClient[Any, Any]) -> None:
    """GET /api/party/qr.svg should 404 when the Party plugin is not loaded."""
    resp = await http_client.get("/api/party/qr.svg")
    assert resp.status == 404


async def test_party_qr_404_guest_access_off(
    http_client: TestClient[Any, Any], mass_mock: Mock
) -> None:
    """GET /api/party/qr.svg should 404 when guest access is disabled."""
    mass_mock.get_provider = Mock(return_value=_party_mock(url=None))
    resp = await http_client.get("/api/party/qr.svg")
    assert resp.status == 404


# --- /msx/party.json native MSX page ---


async def test_msx_party_page_active(http_client: TestClient[Any, Any], mass_mock: Mock) -> None:
    """GET /msx/party.json should show the QR image item when a party is active."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/msx/party.json")
    assert resp.status == 200
    data = await resp.json()
    assert data["headline"] == "My Party"
    items = data["items"]
    assert any(item.get("image", "").endswith("/api/party/qr.svg") for item in items)
    body = await resp.text()
    assert JOIN_URL not in body


async def test_msx_party_page_inactive(http_client: TestClient[Any, Any]) -> None:
    """GET /msx/party.json should render a page without a QR when no party is active."""
    resp = await http_client.get("/msx/party.json")
    assert resp.status == 200
    data = await resp.json()
    assert not any("/api/party/qr.svg" in (item.get("image") or "") for item in data["items"])


# --- MSX menu entry ---


async def test_msx_menu_shows_party_when_active(
    http_client: TestClient[Any, Any], mass_mock: Mock
) -> None:
    """The MSX menu should include a Party entry pointing at the party page when active."""
    mass_mock.get_provider = Mock(return_value=_party_mock())
    resp = await http_client.get("/msx/menu.json")
    assert resp.status == 200
    data = await resp.json()
    party_items = [i for i in data["items"] if i.get("label") == "Party"]
    assert len(party_items) == 1
    assert "/msx/party.json" in party_items[0]["content"]


async def test_msx_menu_hides_party_when_inactive(http_client: TestClient[Any, Any]) -> None:
    """The MSX menu should not show a Party entry when no party is active."""
    resp = await http_client.get("/msx/menu.json")
    assert resp.status == 200
    data = await resp.json()
    assert not any(i.get("label") == "Party" for i in data["items"])
