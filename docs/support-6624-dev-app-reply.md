@Piertoro, you can test the updated server through the **Music Assistant DEV SERVER** app in Home Assistant:

1. Go to **Settings → Apps → App Store** and install **Music Assistant DEV SERVER**.
2. In its **Configuration**, set **Server repository** to `trudenboy/ma-server@integration/dev`. Leave **Frontend repository** empty.
3. Save, stop the regular Music Assistant app for the test, and start the DEV app (restart it if already running). Allow the server installation to finish.
4. Configure MSX Bridge in that server and make sure the Xbox and your Home Assistant integration are connected to the DEV instance.

Then run the automatic-transition check you described, without manual Next: confirm the second track is audible, HA `media_position` advances, and its audio request no longer logs `InsufficientPermissions`. Please attach the fresh diagnostics after that run.

This is a development fork for testing. Automatic track transition has worked on my Samsung Tizen setup; the Xbox result remains unconfirmed.
