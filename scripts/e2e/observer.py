"""Opt-in diagnostics for an isolated MA test instance, on a private Unix socket."""

import asyncio
import inspect
import json
from contextlib import suppress
from pathlib import Path

import music_assistant.__main__ as entry
from music_assistant.helpers.api import parse_arguments
from music_assistant.helpers.json import json_dumps

SOCKET = "/data/e2e-observer.sock"
Original = entry.MusicAssistant


class ObservedMA(Original):
    """Expose a finite diagnostic API only on a private Unix socket."""

    async def start(self) -> None:
        """Start the test instance and private observer listener."""
        await super().start()
        with suppress(FileNotFoundError):
            Path(SOCKET).unlink()
        self.e2e_server = await asyncio.start_unix_server(self.e2e_request, path=SOCKET)
        Path(SOCKET).chmod(0o600)

    async def stop(self) -> None:
        """Close the diagnostic listener before normal server shutdown."""
        if getattr(self, "e2e_server", None):
            self.e2e_server.close()
            await self.e2e_server.wait_closed()
        await super().stop()

    async def e2e_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle one bounded test-only request without exposing an admin TCP API."""
        try:
            req = json.loads(await asyncio.wait_for(reader.readline(), timeout=10))
            command = req.get("command", "snapshot")
            args = req.get("args", {})
            if command == "snapshot":
                players = self.players.all_player_states(
                    provider_filter="msx_bridge", return_disabled=True
                )
                ids = {p.player_id for p in players}
                result = {
                    "players": players,
                    "queues": [q for q in self.player_queues.all() if q.queue_id in ids],
                    "streams": self.streams._active_output_streams,
                    "playback_contexts": {
                        p.player_id: self.players.get_player(p.player_id).clock_context()
                        for p in players
                    },
                    "ws_counts": {
                        p.player_id: len(
                            getattr(
                                getattr(self.get_provider("msx_bridge"), "http_server", None),
                                "_ws_clients",
                                {},
                            ).get(p.player_id, set())
                        )
                        for p in players
                    },
                }
            else:
                allowed = {
                    "players/get",
                    "player_queues/get",
                    "player_queues/items",
                    "player_queues/play_media",
                    "player_queues/play_index",
                    "player_queues/shuffle",
                    "player_queues/repeat",
                    "config/players/get",
                    "config/players/save",
                    "config/players/remove",
                    "config/player_queues/get",
                    "config/player_queues/save",
                    "config/providers/get",
                    "config/providers/save",
                    "config/core/get",
                    "config/core/save",
                }
                allowed.update(
                    "players/cmd/" + x
                    for x in (
                        "stop",
                        "pause",
                        "resume",
                        "seek",
                        "next",
                        "previous",
                        "play",
                        "volume_set",
                    )
                )
                if command not in allowed:
                    raise ValueError("Command outside test scope")
                if command.startswith("config/core/") and args.get("domain") != "player_queues":
                    raise ValueError("Only queue defaults allowed")
                target = args.get("player_id") or args.get("queue_id")
                if target and not target.startswith("msx_"):
                    raise ValueError("Only MSX target allowed")
                if "provider_domain" in args and args["provider_domain"] != "msx_bridge":
                    raise ValueError("Only MSX provider allowed")
                if "instance_id" in args:
                    cfg = await self.config.get_provider_config(args["instance_id"])
                    if cfg.domain != "msx_bridge":
                        raise ValueError("Only MSX provider allowed")
                handler = self.command_handlers[command]
                result = handler.target(
                    **parse_arguments(handler.signature, handler.type_hints, args)
                )
                if inspect.isawaitable(result):
                    result = await result
                if hasattr(result, "__anext__"):
                    result = [x async for x in result]
            response = {"ok": True, "result": result}
        except Exception as err:
            response = {"ok": False, "error": type(err).__name__ + ": " + str(err)}
        writer.write((json_dumps(response) + "\n").encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    entry.MusicAssistant = ObservedMA
    entry.main()
