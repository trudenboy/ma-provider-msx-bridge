
[← Development](development.md) · [← Contributing](contributing.md) · [README](../README.md)

# MSX Bridge — Testing Guide

## Quick Start

```bash
./scripts/test-upstream.sh test
```

With coverage report:

```bash
./scripts/test-upstream.sh test
```

## CI Pipeline

Every push and pull request triggers two parallel jobs via `test.yml`:

| Job | What it does |
|-----|-------------|
| `test-*` | Runs pytest with coverage, uploads report to Codecov |
| `lint-*` | Runs ruff, mypy, codespell, pre-commit |


Local compatibility checks mount this provider into an official Music Assistant `dev` checkout. CI uses the repository's generated provider workflow.


## Tools

| Tool | Purpose |
|------|---------|
| `uv` | Virtual environment and dependency management |
| `Python 3.14` | Target Python version |
| `pytest` | Test framework |
| `pytest-cov` | Coverage collection |
| `Codecov` | Coverage report upload (automatic in CI) |
| `ruff` | Python linter and formatter |
| `mypy` | Static type checker |
| `codespell` | Spell-checking for source code |
| `pre-commit` | Pre-commit hook runner |

## Running Linters Locally

Run all pre-commit hooks (recommended before opening a PR):

```bash
./scripts/test-upstream.sh lint
```

Type checking only:

```bash
./scripts/test-upstream.sh type
```

Linting only:

```bash
./scripts/test-upstream.sh lint
```

## Coverage

Coverage reports are automatically uploaded to Codecov on every CI push.
To view coverage locally:

```bash
./scripts/test-upstream.sh test
```

## When CI Fails

When tests or linters fail in CI, a GitHub issue is automatically created with the `incident:ci` label.
See [Incident Management](incident-management.md) for how the incident workflow operates.
