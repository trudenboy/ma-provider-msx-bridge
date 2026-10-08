# PR #5868 — retired Sendspin setting, 2026-10-09

Live audit: 88 inline threads, 87 resolved, one new open Copilot thread: https://github.com/music-assistant/server/pull/5868#discussion_r4224254633.

The finding is valid. The existing raw-settings migration clears enable_player_grouping but omitted the removed enable_sendspin_bridge setting. Six new cases on actual persisted JSON failed before the correction, covering True/False/None and enabled/disabled MSX providers. The migration now clears both keys by membership, retaining unrelated config values and other provider domains. All six cases verify data equality and second-pass idempotency.

Validation against PR head 443b796 (official MA dev dedcfc906496feb005051e9878c00b50f78c0c26): 415 tests passed, one existing skip (provider tests, core migration tests and the existing config migration module). Root pre-commit passed. The updated full core patch was applied to a clean official dev worktree and its two files exactly matched the tested implementation. No provider code, VERSION or release tag changes are required.

The durable core patch is preserved in provider PR #275. Provider PR #275 merged after green CI; core scoped pre-commit (including mypy) passed. The correction was pushed normally to upstream/msx_bridge (faa413dca07cd13e2392a063c811debd6c46c514) and integration/dev (000c9d700e43a05797acd108a25c6e9959d65ec2). The integration checkout passed 347 tests (331 provider + 16 MSX migration), one existing skip. The [reply bundle](pr-5868-sendspin-reply.json) is prepared for final head faa413d; publication still requires successful final-head CI and owner review. The owner must read the draft before --reviewed-by-human. Earlier response bundles remain historical snapshots; do not reuse them for this thread.

Final-head upstream CI: https://github.com/music-assistant/server/actions/runs/37848407643 (running at preparation time).
