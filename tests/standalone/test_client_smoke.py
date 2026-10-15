"""Run the MSX browser client smoke script under Node.js."""

# Exercise a fixed local script through a subprocess boundary.
# ruff: noqa: S603

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "e2e" / "client-smoke.cjs"
PLUGIN_PAGE = REPO_ROOT / "provider" / "static" / "plugin.html"


def test_client_smoke_passes() -> None:
    """The shared bridge client handles playback, Search handoff and cleanup."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is not installed")
    result = subprocess.run(
        [node, str(SMOKE_SCRIPT), str(PLUGIN_PAGE)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "Search clock handoff" in result.stdout
