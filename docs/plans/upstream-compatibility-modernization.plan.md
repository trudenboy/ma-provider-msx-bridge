# Upstream Compatibility Modernization

## Goal

Keep this provider repository as the only source of truth while making an
official `music-assistant/server@dev` checkout the authoritative environment
for linting, type checking, repository checks, and tests.

## Non-negotiable Rules

- Source changes are made only in this repository.
- The MA checkout is disposable and must never be committed or edited as a
  source of truth.
- Provider code imports only
  `music_assistant.providers.msx_bridge.*`.
- Production code is written against real MA models and controllers; tests
  adapt to those contracts, never the reverse.
- MA dataclasses are real instances in tests. Mocks are reserved for I/O and
  explicitly behavioural collaborators.

## Authoritative Test Harness

`scripts/test-upstream.sh` creates a disposable official MA checkout in
`.cache/ma-upstream/server` by default and supports two mount modes:

- `link`: local edit/test loop. Provider and tests are symlinked.
- `copy`: CI/final verification. Provider and tests are copied so upstream
  filesystem checks that do not follow symlinked directories see them.

The supported commands are:

```bash
./scripts/test-upstream.sh setup
./scripts/test-upstream.sh update
./scripts/test-upstream.sh test
./scripts/test-upstream.sh type
./scripts/test-upstream.sh lint
./scripts/test-upstream.sh checks
./scripts/test-upstream.sh all
```

The final local gate is:

```bash
MA_REF=dev MA_MOUNT_MODE=copy ./scripts/test-upstream.sh all
```

The `upstream-compat` workflow runs the same copy-mode gate against the
official upstream `dev` branch on pull requests, pushes to `dev`, on a weekly
schedule, and on demand.

## Delivery Order

### 1. Harness and module identity

- Add the official upstream sandbox script and CI gate.
- Remove the root import bootstrap and its `sys.path`/`sys.modules` mutation.
- Remove tests that only protect that bootstrap.
- Convert every provider import to the canonical upstream package path.

**Exit criteria:** source and tests import once under the final upstream path;
provider import errors fail collection immediately.

### 2. Test foundations

- Add factories for `PlayerMedia`, `PlayerQueue`, `QueueItem`, media items,
  search results, image metadata, and audio output plans.
- Replace model `Mock`/`MagicMock` instances with those real models.
- Replace the permissive `mass = Mock()` graph with narrow controller fakes
  and upstream `mass_minimal` fixtures for controller/lifecycle contracts.
- Remove compatibility aliases for methods that do not exist in current MA.

**Exit criteria:** test data cannot manufacture missing attributes or truthy
child mocks, and misspelled MA controller calls fail tests.

### 3. Current review fixes and typed boundaries

- Delete `_queue_item_limit`; read `PlayerQueue.items` and
  `PlayerQueue.current_index` directly after a `None` guard.
- Type all audio-path media as `PlayerMedia`, including
  `AudioPipeline`, HTTP forwarding, stream URL resolution, and duration
  resolution. Type duration resolution's server as `MusicAssistant`.
- Delete the test-only `playlist_url` mapper branch and make `context_uri`
  mandatory.
- Read `mass.webserver.base_url` and `mass.streams.base_url` directly.
- Replace queue-item `SimpleNamespace` values with a typed playlist view.

**Exit criteria:** no `Any`, `getattr`, `hasattr`, or mock-derived fallback
remains around known MA model/controller contracts.

### 4. Module interfaces and MA integrations

- Remove test-facing aliases and forwarding layers from production modules.
- Localize private PlayerController no-redirect calls behind one typed group
  propagation path, always under `PlayerLockPurpose.PLAYBACK`.
- Add contract tests against real MA controller behaviour.
- Ensure unload enumerates disabled provider players, player availability
  reflects WebSocket lifecycle, and advertised features match device support.
- Track, cancel, await, and report every background task.
- Catch only expected MA/I/O errors and map MA errors to HTTP statuses at the
  HTTP boundary.
- Convert all docstrings to caller-facing Sphinx style.

**Exit criteria:** lifecycle, group commands, tasks, errors, and capabilities
match the active MA contracts.

### 5. Party exception

MA currently exposes no generic Party status contract. The Party feature stays
temporarily, but its named-provider lookup is isolated entirely in `party.py`,
uses a narrow local `Protocol`, has no `Any` or reflective fields, and is
covered by dedicated tests. This is the sole documented temporary deviation
from provider isolation until MA provides a generic capability or the feature
is removed.

### 6. Enforcement and completion

- Add contract tests for imports, queues, streams, group command routing,
  lifecycle, WebSocket availability, task teardown, and Party fallback.
- Add narrow regression checks forbidding legacy `provider.*` imports, model
  mocks, and explicit `Any` in critical modules.
- Run upstream lint, mypy, MA repository checks, unit tests, contract tests,
  and coverage in copy mode on one recorded MA SHA.

## Definition of Done

- Current repository remains the sole source of provider and test files.
- Official MA `dev` copy-mode gate passes.
- No root import bootstrap or dual module identity exists.
- Tests use real MA domain models.
- Production reflects real MA interfaces rather than test-double shapes.
- Current review comments are fixed and verified in the authoritative harness.
- Party integration is the only explicitly documented temporary exception.
