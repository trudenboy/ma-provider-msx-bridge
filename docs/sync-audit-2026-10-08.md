# MSX Bridge sync audit — 2026-10-08

Upstream: music-assistant/server dev `73257004745c8b44be6ef43f0001d6230098020d`.
Provider pacing fix: `0a929012a514a2e3df6fdbd8ecc5115c4bd74399` (PR #262).

The transform-aware ma-provider-tools preflight was rerun without override.
It exits 1 and flags six files: provider/http_server.py, player.py, provider.py,
and the corresponding three test files. A successful runtime gate is not an
authorization to overwrite these upstream blobs.

## Examined source differences

AST method comparisons against provider release v1.4.11 isolate these upstream
changes in player.py and provider.py:

- `_propagate_single` acquires the MA playback lock and uses internal handlers.
  Ported in #226, then the provider-native group propagation path was removed
  by #261 in favor of Universal Groups. The completed #5944 spec records this.
- `get_owner_username` skips HOMEASSISTANT_SYSTEM_USER (#6296). Owner selection
  itself was removed in #259 to fix unauthenticated playback. Restoring the
  method would reintroduce the wrong attribution path; #264 is superseded.

The monolithic upstream HTTP server differs structurally from the local
queue-handshake/audio/Party modules. Examined method deltas include:

- active-queue identity handling, builtin/radio queue items and queue_item_id:
  local typed queue handshake retains token validation before queue access and
  distinguishes duplicate URIs; regression coverage exists;
- broad upstream Exception fallbacks versus narrowed local operational-error
  contracts: local hardening intentionally surfaces programming errors;
- kiosk lyrics/queue routes: deliberately removed in #231;
- shared buffers/group propagation: deliberately removed in #261;
- unauthenticated owner impersonation: deliberately removed in #259, and the
  tagged stable handler reproduces support #6624 until its minimal patch;
- pacing: current API ported to AudioPipeline in #262, with five source cases;
- Party image bounds/caching/cancellation: handled by the extracted Party
  adapter and its maintained tests rather than the old monolithic helpers.

The preflight identifies additional older files as matching historical provider
releases or already-ported edits, including the retired browser assets. Its
residual source/test differences still require maintainer review of the final
transformed snapshot. This memo is evidence for that review, not an override.

## Decisions prepared

1. Keep #264 open until maintainer agrees to close it as superseded. Its draft
   adds only the retired owner method/test plus conflict/scaffold artifacts.
2. Merge reviewed local fixes before producing a release snapshot.
3. Re-run the guard on the actual final release SHA and current upstream SHA;
   compare integration/dev separately before any dispatch.
4. Do not apply ack_upstream_ahead based on the old September failure or on
   this broad compatibility test result. If an override is eventually chosen,
   it must be explicitly approved for an immutable reviewed upstream snapshot.

## Executed remediation after maintainer instruction

On 2026-10-08 the maintainer explicitly requested repairing synchronization and
including the changes in server PR #5868. Hub PR #165 registers immutable
`upstream_guard_baseline: 73257004745c8b44be6ef43f0001d6230098020d` for MSX only.
The ordinary guard remains enabled: exactly unchanged reviewed blobs are
acknowledged; new/changed upstream blobs still block. Real preflight now passes;
65 guard/workflow tests, template validation and pre-commit passed. Distribution
updated provider PR #268, subsequently merged with fresh green checks.

The integration branch was separately audited at
`8c473be9b49045936718a19acda1dd3ea1a225ff`. Its 35 MSX source/test files largely
match exported provider v1.5.10 after source-path rewriting and AST/JSON
normalization. Three files differ: http_server.py has stale monolithic imports,
PartyInfo and default-pacing scaffolding; provider.py and test_provider.py restore
the superseded owner selection from #6296. These are already covered by the
source audit above, not new provider features to retain. Other provider/core
paths are outside the MSX rsync destination and are preserved.

The current source is synced from provider dev, retaining VERSION 1.6.0 and
without a new release/tag. The manual sync workflow's version input labels the
sync commit; it does not check out the historical tag. Do not use the separate
upstream-pr workflow to re-import historical v1.6.0 over the reviewed fixes.

## Verified result

Provider dev code snapshot: `9d172cf8ced23cd22239761bea7a5a0a25b5732e`.
Integration dev: `2733f8ecf30ecd6837ab65ccc056cca598d01039`.
PR #5868 head: `0281933ba52d863301cb3da561de874b06884fc5`; its merge base
is the reviewed official MA dev `73257004745c8b44be6ef43f0001d6230098020d`.
[Sync run 37801414031](https://github.com/trudenboy/ma-provider-msx-bridge/actions/runs/37801414031)
succeeded with `ack_upstream_ahead=false`. Provider #264 was closed as superseded.
The sync commit changes only audio_stream.py, http_server.py, test_contracts.py
and test_http_server.py. All 33 exported source/test files were compared with
the provider snapshot: no unexplained differences.

Verification of the actual published worktree: 324 passed, 1 skipped; mypy
and scoped pre-commit passed. [Full upstream Test](https://github.com/music-assistant/server/actions/runs/37801561191)
and [PR Checks](https://github.com/music-assistant/server/actions/runs/37802416184)
completed successfully. No new tag or release was created.
