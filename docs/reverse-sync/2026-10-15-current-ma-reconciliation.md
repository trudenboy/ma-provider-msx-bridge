# Current Music Assistant reconciliation

The consolidated change incorporates the existing provider PR branches, retaining
their original commits and contributor attribution:

| Provider PR | Upstream source | Result |
|---|---|---|
| #285 | Shared config distribution | Current Ruff rules and stricter mypy settings |
| #288 | music-assistant/server#6848 | Full album track lists and cover fallback |
| #289 | music-assistant/server#6932 | Playlist iteration through `iter_tracks` |
| #291 | music-assistant/server#6935 | Full artist album lists |
| #290 | music-assistant/server#6997 | Remove redundant queue state and provider-side legacy migration |
| #294 | music-assistant/server#7003 | Remove unused goto-index WebSocket commands |

The S104 suppression from upstream #6886 is restored together with the synced
Ruff policy. The previous provider autofix removed that suppression while its
rule was globally ignored. The updated local policy keeps it, matching upstream.

Core owns stored MSX settings migration. Its 22 existing migration tests pass,
including `shared` to `independent`, disabled providers and retired settings.
This validation targets current MA; it does not establish compatibility with
older core versions lacking that migration or the current listing APIs.

## Initial reconciliation validation (before cleanup)

Official MA revision: `15003cae786a704959ce4f3933aea30329545cf0`.

- At the initial reconciliation snapshot, all 19 provider files matched the
  upstream Git blobs, excluding the generated upstream VERSION file.
- Nine new HTTP/mapper regressions use the real MA controllers. Against the
  old provider source they all fail: playlist HTTP 500, 500/501-item truncation,
  and missing late cover. After reconciliation all nine pass.
- The playlist regressions exercise real controller page walking; album and
  artist regressions retain the real listing/limit behavior while replacing
  data retrieval. They do not mock the public listing methods being tested.
- A further test verifies successive MA selections reload the native playlist
  at the current queue index after removing the obsolete queue state.
- Local helper imports that need static return types are relative, so stricter
  standalone mypy can resolve them as well as the canonical upstream layout.
- Local pre-commit and the complete `scripts/test-upstream.sh all` gate pass:
  353 provider tests, 18 standalone tests, mypy and upstream structural checks.
- The transform-aware upstream-ahead guard passes with the existing immutable
  baseline `73257004745c8b44be6ef43f0001d6230098020d`, without an override.

The first fresh dependency attempt failed resolving the PyTorch download host.
The isolated validation environment reuses cached audio dependencies; its full
gate subsequently installs the current requirements successfully. Models are
1.1.224, frontend 2.17.342, torch 2.13.0+cpu, torchaudio 2.11.0+cpu.

## Remaining runtime work

A minimal harness using the current real queue feeder and PlayerController
reproduces `UnsupportedFeaturedException: Player ... does not support enqueueing`
for a player without ENQUEUE. This is separate core work; the provider's
capabilities are unchanged.

ADB reports no connected devices and Docker reports no running containers at
the time of this validation. No new Samsung/Xbox/Pixel, radio, paused-seek,
reconnect or 30-minute device run is claimed.

The current provider VERSION stays at 1.6.2. The 1.6.3 changelog entry describes
the pending fixes; merge, a maintainer-owned version bump, release and delivery
remain separate steps. The source PRs should be retired after the consolidated
PR lands, then stale CI incidents can be closed against fresh evidence.
## Whole-codebase cleanup follow-up

The reconciled runtime was subsequently audited as a complete codebase, beyond
the six PR diffs. The maintainer selected per-TV codec configuration and removal
of the five obsolete library playlist endpoints. The current revision therefore
intentionally differs from the initial byte-identical upstream reconciliation
snapshot described above.

Library selections continue through `/api/play` and the active MA queue playlist.
The retired `/msx/playlist/...` routes return 404; library browsing REST routes
remain available. Global output format has been removed, while saved per-player
codec choices remain authoritative for both stream delivery modes.

Unused WS metadata/debug branches, the old stream-debug CLI and private wrappers
were removed. Test initialization requires the real MA framework and propagates
provider import errors. Older MSX client capability detection, device identity
fallbacks, native seek and generation/cleanup guards remain in use.

Shared template corrections cover the root VERSION guard, official MA dev setup,
configured Python selection and manifest-based Docker dependency installation.
Their source changes are prepared in ma-provider-tools; provider wrappers were
rendered from those templates.

The cleanup advances the reviewed sync baseline to official MA
`15003cae786a704959ce4f3933aea30329545cf0`. Before cleanup, all 19 provider files
matched that immutable tree byte-for-byte; the HTTP test file differed only in
equivalent helper import paths. The old baseline flagged the intentional removal
of library playlist handlers and their old success tests. The updated baseline
records this reviewed snapshot; the sync guard and its default refusal of future
unreviewed upstream edits remain enabled.

Validation of the cleanup against the same official MA dev revision:

- `scripts/test-upstream.sh all`: 349 provider tests and 18 standalone tests,
  upstream pre-commit, structural checks and mypy pass.
- Repository pre-commit and 367 local tests pass. The lower count reflects
  removed endpoint cases; retirement and saved/default codec cases are covered.
- New configuration/route regressions were red before implementation and green
  after it. The remaining real-controller library pagination cases stay enabled.
- A Node smoke harness exercises initialization/menu, WS connection, MA queue
  playlist actions, native pause/resume/seek, seek echo suppression and pagehide
  cleanup. This is not new physical TV or audible playback evidence.
