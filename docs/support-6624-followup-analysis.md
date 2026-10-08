# Support #6624 — Piertoro follow-up, 2026-10-08

Source: https://github.com/music-assistant/support/issues/6624#issuecomment-6067212411 (created 19:13:54 UTC).

The reporter remains on the Home Assistant add-on 2.10.5. They explicitly have not installed draft server PR #5868. Provider PR #270 is a server-side change, not something installed on the Xbox console. The comment is therefore readiness to test, not new evidence for or against the fixes.

The proposed acceptance test is sound and should remain unchanged:

1. Queue at least two ordinary tracks; the first is audible and HA media_position advances.
2. Let the first track end naturally; do not issue next, previous or pause.
3. Confirm the second is audible and HA media_position moves beyond zero. MA queue elapsed time alone is not sufficient evidence.
4. Confirm the second audio request has no InsufficientPermissions / Authentication is necessary to impersonate another user error in _handle_msx_audio.
5. Attach fresh diagnostics after that run, with the exact installed build identified.

Manual Next is not a recovery/verification step: on the reported version it skips past the silent current item and invalidates the automatic-transition check. No additional diagnostic request is warranted before an installable build exists.

Immediate handoff needed: identify or prepare a reproducible server build containing the verified PR revision that the reporter can actually install in their HA add-on setup. A provider release/PR link by itself is insufficient, and a generic Docker image must not be represented as an HA add-on installation. No build, release, stable backport or upstream merge is promised or initiated by this analysis.

Keep #6624 open until the actual Xbox acceptance test passes. The authentication defect has a code correction and regression evidence; audible queue progression on this console remains unverified. Preserve that distinction in the PR description.

## Draft talking points for an owner-written reply

- Thank the reporter for clarifying that the changes have not been installed.
- Confirm their automatic-transition test is the intended acceptance test; no manual Next.
- Explain that the update runs on the MA server, while the existing Xbox MSX app is used as the client.
- Provide a concrete installable HA add-on build/version and instructions only once verified; currently no such artifact is supplied by these PR links.
- Ask for diagnostics after the run they already offered, rather than repeating earlier requests now.

This is a human issue discussion. Per CLAUDE.md, AI may prepare these notes; the owner writes and posts the final reply.
