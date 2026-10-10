# MSX Bridge 1.6.1 platform validation

Evidence distinguishes direct native-device tests from maintainer and independent user reports. The Android matrix was not repeated on every platform.

## Android: Pixel 8, Android 17, Media Station X 0.1.165

Direct native-device coverage includes audible playback (confirmed by the person beside the phone); MA/native pause/resume, Stop with/without notice, next/previous and queue boundaries; natural completion with Repeat Off/One/All; album/playlist selection and queue replacement; duplicate occurrence identity through MA; redirected and independent MP3/AAC/FLAC (six combinations); library navigation and Latin search; retained-player disable/enable and idle lifecycle; restart/WebSocket recovery without reopening MSX; Party QR layout and screenshot decoding; forward/rewind, repeated seeks and beginning clamping.

See the [full remediation report](2026-10-09-msx-remediation.md). After the final progress fix, five playing/paused cases verify full-track time labels and bar position, including updates preserving PAUSED. Application-version detection is independent of TVX Framework 0.1.35 on this phone.

Limitations: seeking while paused still resumes, deliberately excluded from the requested fix. A phone call interrupted the long soak; automatic recovery after calls is not established. Physical QR camera scanning, multi-device group synchronization, acoustic seek-marker verification and a complete Cyrillic/error-path native search matrix are not claimed.

## Samsung Tizen: Media Station X 0.1.145

The maintainer confirmed playlist playback, natural transition and correct progress after the legacy compatibility fix for `Unknown player progress action: position:...`. The final application-version detection change has shipped-TVX runtime regressions for 0.1.145/0.1.146/0.1.165/unknown versions; a new physical Samsung run of that final change and the complete Android matrix have not been performed.

## Xbox One: independent support reporter

[Support issue #6624 verification](https://github.com/music-assistant/support/issues/6624#issuecomment-6089179478) reports DEV App 2.11.0.dev2026100903 using `trudenboy/ma-server@integration/dev`. Three natural transitions occurred about one minute apart without manual controls. Playback requests and redirected streams continued, without `InsufficientPermissions` or MSX audio-handler failures. Derived Home Assistant position reached 57.7 seconds on track three. Earlier stable-server authorization/transition failures were not reproduced.

The reporter could not independently listen to the console. This verifies requests, timing and position updates, not audible playback or complete Xbox codec/search/seek/group coverage. The MSX app version was not reported.
