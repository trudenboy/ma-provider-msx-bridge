# PR #5868 core settings migration

The provider export workflow copies provider code and provider tests. This patch preserves the accompanying Music Assistant core migration and its stored-settings regression tests, which belong outside those exported directories.

Base: official `music-assistant/server` dev `648b3538d0b94ee37c3a528e815b7d8703740c54`.

From a Music Assistant checkout, check and apply the patch once:

```bash
git apply --check --unidiff-zero /path/to/ma-provider-msx-bridge/docs/patches/pr-5868-config-migration.patch
git apply --unidiff-zero /path/to/ma-provider-msx-bridge/docs/patches/pr-5868-config-migration.patch
pytest tests/controllers/config/test_msx_bridge_migration.py
```

The patch uses zero context so repository whitespace hooks cannot corrupt blank context lines. Check that the `_migrate_msx_bridge_settings` call remains inside `migrate()` after applying to a newer base. Do not apply a second time if the migration is already present.
