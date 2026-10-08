# Support #6624 — maintainer draft (not published)

The reported authentication error matches a known difference between the MSX Bridge bundled in MA 2.10.5 and the provider update pending in server PR #5868.

In the 2.10.5 source, `/msx/audio` can enqueue a track inside `ImpersonatedUser(mass, await get_owner_username())`. An unauthenticated native MSX request cannot impersonate that user. The provider fix in #259 (released as 1.5.10 and included in 1.6.0) removes this owner selection and handles native playback as an external hardware request.

This explains the reported error, but successful automatic track advancement on Xbox still needs verification after the fix reaches the installed MA version. Codec, Content-Length and flow-mode settings do not resolve this authorization exception.

Sources:
- https://github.com/music-assistant/support/issues/6624
- https://github.com/music-assistant/server/blob/2.10.5/music_assistant/providers/msx_bridge/http_server.py
- https://github.com/trudenboy/ma-provider-msx-bridge/pull/259
- https://github.com/music-assistant/server/pull/5868

Suggested maintainer decision: backport the minimal unauthenticated-playback fix if completing the larger provider update would delay relief for stable users. Keep the backport separate from kiosk removal and grouping migration.

Verification needed: run two consecutive native queue items with the real MA auth helpers, then confirm audio delivery, audible playback, Xbox position updates and absence of InsufficientPermissions. Do not mark resolved from the MA elapsed-time counter alone.

The linked reminder did not identify a specific missing-data request. Once a build containing the fix is available, ask the reporter to confirm the installed build and retest automatic progression on Xbox.

## Prepared backport and evidence

A minimal patch against the exact MA 2.10.5 source is available at
`patches/support-6624-ma-2.10.5.patch`. It changes only the audio and direct-play
impersonation arguments to None, keeping the older provider architecture.

An isolated HTTP harness executed the actual `_handle_msx_audio` function
extracted from the tagged source, using the real current MA auth helpers:
original handler returns HTTP 500 with InsufficientPermissions; patched handler
returns HTTP 200 and serves two consecutive selected track URIs. Both expected
outcomes pass (2 harness cases). This isolates authorization and does not claim
full stable-stack compatibility, encoding correctness or audible Xbox playback.

The current provider additionally has a maintained HTTP regression for two
queued native requests without a user session, preserving queue items and IDs.
