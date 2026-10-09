#!/usr/bin/env python3
"""
Run strict MSX device acceptance checks through the opt-in Unix observer.

Use --manage-observer to enable it temporarily in the isolated ma-msx-e2e container.
Never expose it through TCP. Config settings changed by this runner are restored
in finally; queue contents in the disposable test profile are replaced by fixtures.
"""

from __future__ import annotations

# Fixed executables; argparse values are passed as argv, never through a shell.
# ruff: noqa: S603, S607, T201
import argparse
import json
import math
import os
import re
import struct
import subprocess
import tempfile
import threading
import time
import urllib.request
import wave
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


class Stand:
    """Call a finite set of MA API commands in the isolated diagnostic instance."""

    def __init__(self, player_id: str) -> None:
        """Select the only player this runner will control."""
        self.player_id = player_id
        package = subprocess.check_output(
            ["adb", "shell", "dumpsys", "package", "de.benzac.msx"]
        ).decode()
        uid = re.search(r"(?:userId|appId)=(\d+)", package)
        if not uid:
            raise RuntimeError("Cannot identify the installed native MSX app")
        self.app_uid = uid.group(1)

    def command(self, command: str = "snapshot", **args: Any) -> Any:
        """Call the isolated Unix observer and fail on every rejected command."""
        code = "import socket,sys; s=socket.socket(socket.AF_UNIX); s.connect('/data/e2e-observer.sock'); s.sendall((sys.argv[1]+'\\n').encode()); print(s.makefile().readline())"
        completed = subprocess.run(
            [
                "docker",
                "exec",
                "ma-msx-e2e",
                "/app/venv/bin/python",
                "-c",
                code,
                json.dumps({"command": command, "args": args}),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=40,
        )
        result = json.loads(completed.stdout)
        if not result["ok"]:
            raise RuntimeError(result.get("error", "Observer command failed"))
        return result["result"]

    def queue(self) -> dict[str, Any]:
        """Return the selected queue from a fresh snapshot."""
        snapshot = self.command()
        return next(q for q in snapshot["queues"] if q["queue_id"] == self.player_id)

    def capture(self) -> dict[str, Any]:
        """Return a timestamped snapshot with no URLs or secrets."""
        snapshot = self.command()
        q = next(q for q in snapshot["queues"] if q["queue_id"] == self.player_id)
        # Never publish stream URLs, credentials, media tokens, or provider setup data.
        audio = subprocess.check_output(["adb", "shell", "dumpsys", "audio"]).decode(
            errors="replace"
        )
        decoder_active = bool(
            re.search(
                r"AudioPlaybackConfiguration[^\n]*" + self.app_uid + r"/[^\n]*state:started", audio
            )
        )
        return {
            "decoder_active": decoder_active,
            "playback_id": snapshot.get("playback_contexts", {})
            .get(self.player_id, {})
            .get("playback_id"),
            "time": time.monotonic(),
            "state": q["state"],
            "index": q["current_index"],
            "position": q["elapsed_time"],
            "repeat": q["repeat_mode"],
            "item": (q.get("current_item") or {}).get("queue_item_id"),
            "ws_count": snapshot["ws_counts"].get(self.player_id, 0),
        }


class QuietHandler(SimpleHTTPRequestHandler):
    """Keep fixture URLs out of the report."""

    def log_message(self, _format: str, *_args: Any) -> None:
        """Keep fixture access logs quiet."""


def make_fixture(path: Path, seconds: int, frequency: int) -> None:
    """Generate deterministic stereo PCM with distinguishable tone segments."""
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(44100)
        for second in range(seconds):
            hz = frequency if seconds < 180 else [440, 660, 880][(second // 15) % 3]
            output.writeframes(
                b"".join(
                    struct.pack("<hh", value, value)
                    for value in (
                        int(1200 * math.sin(2 * math.pi * hz * sample / 44100))
                        for sample in range(44100)
                    )
                )
            )


@contextmanager
def fixture_server(host: str, port: int) -> Iterator[list[str]]:
    """Serve only synthetic fixtures and close the listener even when a check fails."""
    with tempfile.TemporaryDirectory(prefix="msx-e2e-") as directory:
        for name, seconds, hz in [("a", 8, 440), ("b", 11, 660), ("c", 7, 880)]:
            make_fixture(Path(directory) / (name + ".wav"), seconds, hz)
        server = ThreadingHTTPServer((host, port), partial(QuietHandler, directory=directory))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield [f"http://{host}:{port}/{name}.wav" for name in ("a", "b", "c")]
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


def tap_text(text: str) -> None:
    """Tap bounds from one dump, only while the foreground application is MSX."""
    window = subprocess.check_output(["adb", "shell", "dumpsys", "activity", "activities"]).decode()
    focus = next((line for line in window.splitlines() if "topResumedActivity=" in line), "")
    if "de.benzac.msx" not in focus:
        raise RuntimeError("MSX is not the foreground application")
    subprocess.run(
        ["adb", "shell", "uiautomator", "dump", "/sdcard/msx-e2e.xml"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    xml = subprocess.check_output(["adb", "shell", "cat", "/sdcard/msx-e2e.xml"])
    root = ET.fromstring(xml)  # noqa: S314 - trusted local ADB-generated XML
    matches = [
        n for n in root.iter("node") if n.get("text") == text and n.get("bounds") != "[0,0][0,0]"
    ]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one visible native control")
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", matches[0].get("bounds", "")))
    subprocess.run(
        ["adb", "shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2)], check=True
    )


@contextmanager
def playback_settings(stand: Stand) -> Iterator[None]:
    """Restore original settings after assertions, exceptions and keyboard interrupts."""
    original = stand.command("config/players/get", player_id=stand.player_id)
    queue = stand.queue()
    try:
        stand.command(
            "config/players/save",
            player_id=stand.player_id,
            values={"http_profile": "chunked", "output_codec": "mp3", "enabled": True},
        )
        yield
    finally:
        # A failed restoration must not skip the remaining original settings.
        values = {key: original["values"][key]["value"] for key in ("http_profile", "output_codec")}
        values["enabled"] = original["enabled"]
        operations = [
            ("config/players/save", {"player_id": stand.player_id, "values": {"enabled": True}}),
            ("players/cmd/stop", {"player_id": stand.player_id}),
            (
                "player_queues/repeat",
                {"queue_id": stand.player_id, "repeat_mode": queue["repeat_mode"]},
            ),
            (
                "player_queues/shuffle",
                {"queue_id": stand.player_id, "shuffle_enabled": queue["shuffle_enabled"]},
            ),
            ("config/players/save", {"player_id": stand.player_id, "values": values}),
        ]
        failures = []
        for command, args in operations:
            try:
                stand.command(command, **args)
            except Exception as err:
                failures.append(err)
        if failures:
            raise ExceptionGroup("Unable to restore all original playback settings", failures)


def run_repeat(
    stand: Stand, urls: list[str], mode: str, seconds: int, records: list[dict[str, Any]]
) -> None:
    """Assert observed natural transitions; a decoder fetch alone does not pass this check."""
    stand.command("players/cmd/stop", player_id=stand.player_id)
    stand.command("player_queues/repeat", queue_id=stand.player_id, repeat_mode=mode)
    stand.command("player_queues/shuffle", queue_id=stand.player_id, shuffle_enabled=False)
    stand.command(
        "player_queues/play_media", queue_id=stand.player_id, media=urls, option="replace"
    )
    started = time.monotonic()
    next_progress = started + 60
    deadline = started + seconds
    while time.monotonic() < deadline:
        time.sleep(1)
        records.append(stand.capture())
        if seconds >= 1800 and time.monotonic() >= next_progress:
            print(
                "Soak",
                round((time.monotonic() - started) / 60),
                "min; index",
                records[-1]["index"],
                "decoder",
                records[-1]["decoder_active"],
                flush=True,
            )
            next_progress += 60
    if mode == "off":
        assert {r["index"] for r in records} == {0, 1, 2}
        assert records[-1]["state"] == "idle"
    elif mode == "one":
        assert all(r["index"] == 0 for r in records)
        assert (
            sum(
                records[i]["position"] < records[i - 1]["position"] - 2
                for i in range(1, len(records))
            )
            >= 2
        )
    else:
        assert all(r["state"] == "playing" for r in records)
        assert (
            sum(records[i]["index"] < records[i - 1]["index"] for i in range(1, len(records))) >= 2
        )
    assert any(r["decoder_active"] for r in records), "Native decoder did not start"
    assert all(r["ws_count"] == 1 for r in records), "Native socket count changed"
    if mode == "all":
        assert sum(r["decoder_active"] for r in records) >= len(records) * 0.9, (
            "Native decoder stalled"
        )


def recreate_container(config: dict[str, Any], command: list[str]) -> None:
    """Recreate only the fixed disposable container with its original mounts and image."""
    subprocess.run(
        ["docker", "stop", "--time", "30", "ma-msx-e2e"], check=True, capture_output=True
    )
    subprocess.run(["docker", "rm", "ma-msx-e2e"], check=True, capture_output=True)
    args = [
        "docker",
        "run",
        "-d",
        "--name",
        "ma-msx-e2e",
        "--network",
        config["HostConfig"]["NetworkMode"],
    ]
    for mount in config["Mounts"]:
        if mount["Type"] != "bind":
            raise RuntimeError("Only explicit bind-mounted isolated profiles are supported")
        value = "type=bind,src=" + mount["Source"] + ",dst=" + mount["Destination"]
        if not mount["RW"]:
            value += ",readonly"
        args.extend(["--mount", value])
    child_env = os.environ.copy()
    for entry in config["Config"]["Env"]:
        key, value = entry.split("=", 1)
        args.extend(["--env", key])
        child_env[key] = value
    if config["Config"]["User"]:
        args.extend(["--user", config["Config"]["User"]])
    args.extend(
        ["--entrypoint", config["Config"]["Entrypoint"][0], config["Config"]["Image"], *command]
    )
    subprocess.run(args, env=child_env, check=True, capture_output=True)


@contextmanager
def diagnostic_runtime(stand: Stand, enabled: bool, results: dict[str, Any]) -> Iterator[None]:
    """Opt in to the Unix observer and restore the normal isolated runtime in finally."""
    if not enabled:
        yield
        return
    config = json.loads(subprocess.check_output(["docker", "inspect", "ma-msx-e2e"]))[0]
    repo = Path(__file__).resolve().parents[1]
    data = repo / ".cache/ma-msx-e2e-data"
    mounts = {mount["Destination"]: Path(mount["Source"]).resolve() for mount in config["Mounts"]}
    if (
        mounts.get("/data") != data.resolve()
        or mounts.get("/opt/ma-source/music_assistant/providers/msx_bridge") != repo / "provider"
    ):
        raise RuntimeError("Refusing to change a container outside this isolated workspace stand")
    original = config["Config"]["Cmd"]
    if original[:1] != ["-c"] or len(original) != 2 or "-m music_assistant" not in original[1]:
        raise RuntimeError("The isolated container must start with the normal MA command")
    observer = data / "e2e-runtime.py"
    if observer.exists():
        raise RuntimeError(
            "A diagnostic launcher already exists; restore the previous session first"
        )
    try:
        observer.write_text((repo / "scripts/e2e/observer.py").read_text())
        observer.chmod(0o600)
        diagnostic = [
            original[0],
            original[1].replace("-m music_assistant", "/data/e2e-runtime.py"),
        ]
        recreate_container(config, diagnostic)
        for _ in range(60):
            time.sleep(1)
            try:
                if stand.capture()["ws_count"] == 1:
                    break
            except Exception:
                results["observer_startup_retries"] = results.get("observer_startup_retries", 0) + 1
        else:
            raise RuntimeError("MSX did not reconnect to the diagnostic runtime")
        yield
    finally:
        logs = subprocess.run(
            ["docker", "logs", "ma-msx-e2e"], capture_output=True, text=True, check=False
        )
        text = logs.stdout + logs.stderr
        results["diagnostic_log_counts"] = {
            label: text.count(label)
            for label in (
                "UnsupportedFeaturedException",
                "Task exception was never retrieved",
                "Unclosed client session",
                "Traceback (most recent call last)",
            )
        }
        recreate_container(config, original)
        observer.unlink(missing_ok=True)
        (data / "e2e-observer.sock").unlink(missing_ok=True)
        for _ in range(60):
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8099/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                continue
        else:
            raise RuntimeError("Restored normal MSX server is not healthy")
        results["normal_runtime_restored"] = True


@contextmanager
def phone_timeout() -> Iterator[None]:
    """Keep the device awake during the run and restore its original timeout."""
    original = (
        subprocess.check_output(["adb", "shell", "settings", "get", "system", "screen_off_timeout"])
        .decode()
        .strip()
    )
    if not original.isdecimal():
        raise RuntimeError("Cannot determine the original Android screen timeout")
    try:
        subprocess.run(
            ["adb", "shell", "settings", "put", "system", "screen_off_timeout", "3600000"],
            check=True,
        )
        yield
    finally:
        subprocess.run(
            ["adb", "shell", "settings", "put", "system", "screen_off_timeout", original],
            check=True,
        )


def main() -> None:
    """Run a matrix or a thirty-minute soak, with sanitized JSON results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--player", required=True)
    parser.add_argument("--host", required=True, help="LAN address reachable by the MSX device")
    parser.add_argument("--port", type=int, default=8098)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--soak", action="store_true")
    parser.add_argument(
        "--manage-observer",
        action="store_true",
        help="Enable diagnostic runtime temporarily; restore normal container in finally",
    )
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument(
        "--media", action="append", help="Ordinary library playlist/track URI for soak"
    )
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error("--rounds must be positive")
    if not args.player.startswith("msx_"):
        parser.error("Only an MSX player in the isolated stand is allowed")
    stand = Stand(args.player)
    results: dict[str, Any] = {"passed": False, "runs": []}
    try:
        with (
            phone_timeout(),
            diagnostic_runtime(stand, args.manage_observer, results),
            fixture_server(args.host, args.port) as urls,
            playback_settings(stand),
        ):
            if args.soak:
                rows: list[dict[str, Any]] = []
                results["runs"].append({"mode": "all", "timeline": rows})
                run_repeat(stand, args.media or urls, "all", 1800, rows)
            else:
                for round_no in range(args.rounds):
                    for mode, seconds in [("off", 34), ("one", 28), ("all", 58)]:
                        rows = []
                        results["runs"].append(
                            {"round": round_no + 1, "mode": mode, "timeline": rows}
                        )
                        run_repeat(stand, urls, mode, seconds, rows)
                        print(mode + " PASS", flush=True)
        results["passed"] = True
    except (Exception, KeyboardInterrupt) as err:
        results["failure_type"] = type(err).__name__
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2))
    print("PASS", flush=True)


if __name__ == "__main__":
    main()
