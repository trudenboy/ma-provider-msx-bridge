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

Verified installation route: the official Music Assistant DEV SERVER app supports server_repo in owner/repo@reference format, including branches containing a slash. The owner proposed `trudenboy/ma-server@integration/dev`; the branch currently points to `78b278e80e02c33b4096c7bf9ae8398432ce5626` and contains the fixes. Set Server repository to that value and leave Frontend repository empty. Save and start/restart the app; it installs the server source itself, so a separately published test image is not required. Stop the regular MA app during the test and connect the Xbox and HA integration to the DEV instance. This installation method is documented; installation/startup on the reporter's HA host has not yet been confirmed.

Sources checked live:

- https://github.com/music-assistant/home-assistant-addon/blob/main/music_assistant_dev/README.md
- https://github.com/music-assistant/home-assistant-addon/blob/main/music_assistant_dev/entrypoint.sh
- https://github.com/music-assistant/home-assistant-addon/blob/main/music_assistant_dev/translations/en.yaml

The owner subsequently observed a successful automatic transition on Samsung Tizen. That observation does not establish the Xbox result, HA position progression, or absence of auth errors in logs.

Upstream Test for final PR head c81e8cd completed successfully: https://github.com/music-assistant/server/actions/runs/37833590467.

Keep #6624 open until the actual Xbox acceptance test passes. The authentication defect has a code correction and regression evidence; audible queue progression on this console remains unverified. Preserve that distinction in the PR description.

## Draft talking points for an owner-written reply

- Thank the reporter for clarifying that the changes have not been installed.
- Confirm their automatic-transition test is the intended acceptance test; no manual Next.
- Explain that the update runs on the MA server, while the existing Xbox MSX app is used as the client.
- Give the verified DEV app repository setting and setup instructions in the [reply draft](support-6624-dev-app-reply.md).
- Ask for diagnostics after the run they already offered, rather than repeating earlier requests now.

The owner supplied the DEV app proposal. The reply draft is prepared for their review and has not been posted.
