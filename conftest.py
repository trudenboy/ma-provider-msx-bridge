"""Root conftest: ensure provider/ is importable as music_assistant.providers.msx_bridge."""

from __future__ import annotations

import contextlib
import importlib
import importlib.util
import sys
import types
from pathlib import Path

# Make the provider/ directory importable as music_assistant.providers.msx_bridge
_provider_path = Path(__file__).parent / "provider"
_repo_root = Path(__file__).resolve().parent

# Reuse the real MA packages when installed so transitive imports can reach
# other providers. Fall back to namespace shims for lightweight test setups.
for _pkg in ("music_assistant", "music_assistant.providers"):
    try:
        importlib.import_module(_pkg)
    except ModuleNotFoundError:
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = []  # type: ignore[attr-defined]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

# The reusable upstream workflow checks out MA Server inside this repository.
# Add that deterministic location before executing the provider package, since
# its imports can reach sibling MA providers during module initialization.
_ma_pkg = sys.modules["music_assistant"]
for _ma_candidate in (
    Path.cwd() / "music_assistant",
    _repo_root / "ma-server" / "music_assistant",
):
    _ma_candidate_str = str(_ma_candidate)
    if (
        _ma_candidate.is_dir() and _ma_candidate_str not in _ma_pkg.__path__  # type: ignore[attr-defined]
    ):
        _ma_pkg.__path__.append(_ma_candidate_str)  # type: ignore[attr-defined]

# Pytest can load this repository's namespace shim before the MA server package.
# Propagate every discovered Music Assistant package root to the providers
# package so imports of sibling providers keep working in the upstream test
# harness (which symlinks this provider into a separate MA checkout).
_providers_pkg = sys.modules["music_assistant.providers"]
for _ma_package_root in _ma_pkg.__path__:  # type: ignore[attr-defined]
    _providers_root = str(Path(_ma_package_root) / "providers")
    if (
        Path(_providers_root).is_dir() and _providers_root not in _providers_pkg.__path__  # type: ignore[attr-defined]
    ):
        _providers_pkg.__path__.append(_providers_root)  # type: ignore[attr-defined]

# Standalone provider tests reuse shared helpers from the adjacent MA checkout.
# Keep this provider-repository bootstrap outside tests/, which is synchronized
# into the upstream repository and must rely on upstream's native test package.
_tests_pkg = importlib.import_module("tests")
for _ma_package_root in _ma_pkg.__path__:  # type: ignore[attr-defined]
    _shared_tests_root = str(Path(_ma_package_root).parent / "tests")
    if (
        Path(_shared_tests_root).is_dir() and _shared_tests_root not in _tests_pkg.__path__  # type: ignore[attr-defined]
    ):
        _tests_pkg.__path__.append(_shared_tests_root)  # type: ignore[attr-defined]

# Insert provider/ into sys.path so its modules are importable
if str(_provider_path) not in sys.path:
    sys.path.insert(0, str(_provider_path))

# Register a package alias so `from music_assistant.providers.msx_bridge.X import Y` works
_spec = importlib.util.spec_from_file_location(
    "music_assistant.providers.msx_bridge",
    _provider_path / "__init__.py",
    submodule_search_locations=[str(_provider_path)],
)
if _spec and "music_assistant.providers.msx_bridge" not in sys.modules:
    _pkg_mod = importlib.util.module_from_spec(_spec)
    _pkg_mod.__path__ = [str(_provider_path)]  # type: ignore[attr-defined]
    _pkg_mod.__package__ = "music_assistant.providers.msx_bridge"
    sys.modules["music_assistant.providers.msx_bridge"] = _pkg_mod
    with contextlib.suppress(
        Exception
    ):  # provider __init__ may have MA-specific imports; best-effort
        _spec.loader.exec_module(_pkg_mod)  # type: ignore[union-attr]
