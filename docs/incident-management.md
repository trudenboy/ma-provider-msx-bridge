
[← README](../README.md)

# MSX Bridge — Incident Management

## Labels

All issues use a standardized label taxonomy:

### Incident Labels

| Label | Color | Description |
|-------|-------|-------------|
| `incident:ci` | 🔴 | CI/CD failure |
| `incident:release` | 🔴 | Release pipeline failure |
| `incident:sync` | 🟠 | Fork sync failure |
| `incident:bug` | 🔴 | User-reported bug |
| `incident:security` | 🟣 | Security vulnerability |
| `incident:upstream` | 🔵 | Upstream API change |
| `incident:proposal` | 🟢 | Improvement proposal or feature request |

### Priority Labels

| Label | Description |
|-------|-------------|
| `priority:critical` | Blocking, immediate action required |
| `priority:high` | Important, address soon |
| `priority:medium` | Normal queue |
| `priority:low` | Nice to have |

### Special Labels

| Label | Description |
|-------|-------------|
| `copilot` | Route issue to GitHub Copilot agent |

## Automatic Incident Pipeline

Many incidents are created automatically without manual intervention:

### CI Failures

1. Tests or linters fail in `test.yml`
2. `reusable-report-incident.yml` creates an issue with `incident:ci` + `priority:high` labels
3. If an open issue for this failure type already exists — a comment is added (no duplicate created)
4. The issue is automatically added to the MA Ecosystem project board

### Other Automatic Incidents

| Event | Label |
|-------|-------|
| Fork sync failure | `incident:sync` |
| Security audit failure | `incident:security` |
| Release pipeline failure | `incident:release` |

## GitHub Project Board (MA Ecosystem)

All issues labeled `incident:*` are automatically added to the project board:

- **Addition**: `issue-project.yml` triggers when an issue is opened or labeled
- **Provider field**: Set automatically for MSX Bridge
- **Release tracking**: `reusable-release.yml` creates a draft issue in the project on each release

## Copilot Triage

Any issue can be routed to the GitHub Copilot agent for automated analysis:

1. Add the `copilot` label to an issue
2. `copilot-triage.yml` automatically assigns `@copilot`
3. Copilot analyzes the issue and may submit a PR with a fix

This is useful for routine bugs, documentation typos, and small improvements.

## Manual Incident Reporting

Use issue templates to create incidents manually:

| Template | When to use |
|----------|-------------|
| **Bug report** | Reproducible bug — attach `incident:bug` label |
| **Upstream API change** | Upstream API changed — attach `incident:upstream` label |
| **Improvement proposal** | New feature request — attach `incident:proposal` label |

After creating the issue, add a priority label as appropriate.

