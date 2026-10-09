# PR #5868 core settings migration

The provider export workflow copies provider code and provider tests. This patch preserves the accompanying Music Assistant core migration and its stored-settings regression tests, which belong outside those exported directories.

Base: official `music-assistant/server` dev `d22d28c087ded4289c67c8121c7697f02d9f6e62`.

From a Music Assistant checkout, check and apply the patch once:

```bash
git apply --check --unidiff-zero /path/to/ma-provider-msx-bridge/docs/patches/pr-5868-config-migration.patch
git apply --unidiff-zero /path/to/ma-provider-msx-bridge/docs/patches/pr-5868-config-migration.patch
pytest tests/controllers/config/test_msx_bridge_migration.py
```

The patch uses zero context so repository whitespace hooks cannot corrupt blank context lines. Check that the `_migrate_msx_bridge_settings` call remains inside `migrate()` after applying to a newer base. Do not apply a second time if the migration is already present.

The migration clears both retired switches, `enable_player_grouping` and `enable_sendspin_bridge`, regardless of their values or whether the provider is enabled.

The private migration helper sits below the public functions, alongside the other private migration helpers.
