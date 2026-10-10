# Reverse-sync: upstream PR #5498

Use typed sorting for the recently played content page, native playlist and REST endpoint, matching the current Music Assistant library API. Preserve all current MSX playback and error handling.

The import conflict combined an old inline provider layout with the newer split provider. Keep the current provider imports and add `SortField` and `SortDirection`; no old audio or error imports are restored.

Validation: compare the resolved HTTP server with the upstream MSX snapshot before Marcel's review commits, then run the provider against current official Music Assistant.
