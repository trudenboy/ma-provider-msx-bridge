#!/usr/bin/env bash
# Run this provider against a disposable official Music Assistant checkout.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MA_SERVER_DIR="${MA_SERVER_DIR:-$REPO_ROOT/.cache/ma-upstream/server}"
MA_REF="${MA_REF:-dev}"
MA_MOUNT_MODE="${MA_MOUNT_MODE:-link}"
PROVIDER_DOMAIN="msx_bridge"

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERROR: $1 is required" >&2
        exit 1
    fi
}

mount_sources() {
    local provider_dest="$MA_SERVER_DIR/music_assistant/providers/$PROVIDER_DOMAIN"
    local tests_dest="$MA_SERVER_DIR/tests/providers/$PROVIDER_DOMAIN"

    case "$MA_MOUNT_MODE" in
        link)
            rm -rf "$provider_dest" "$tests_dest"
            ln -s "$REPO_ROOT/provider" "$provider_dest"
            ln -s "$REPO_ROOT/tests" "$tests_dest"
            ;;
        copy)
            rm -rf "$provider_dest" "$tests_dest"
            mkdir -p "$provider_dest" "$tests_dest"
            rsync -a --delete "$REPO_ROOT/provider/" "$provider_dest/"
            rsync -a --delete "$REPO_ROOT/tests/" "$tests_dest/"
            ;;
        *)
            echo "ERROR: MA_MOUNT_MODE must be link or copy" >&2
            exit 1
            ;;
    esac
}

install_manifest_requirements() {
    local requirements
    requirements="$(python3 - "$REPO_ROOT/provider/manifest.json" <<'PY'
import json
import sys

print(" ".join(json.loads(open(sys.argv[1], encoding="utf-8").read()).get("requirements", [])))
PY
)"
    if [ -n "$requirements" ]; then
        VIRTUAL_ENV="$MA_SERVER_DIR/.venv" uv pip install --index-strategy unsafe-best-match $requirements
    fi
}

setup() {
    require_command git
    require_command rsync
    require_command uv
    require_command python3

    if [ ! -d "$MA_SERVER_DIR/.git" ]; then
        mkdir -p "$(dirname "$MA_SERVER_DIR")"
        git clone --depth=1 --branch "$MA_REF" https://github.com/music-assistant/server.git "$MA_SERVER_DIR"
    fi

    update
    if [ ! -x "$MA_SERVER_DIR/.venv/bin/python" ]; then
        (
            cd "$MA_SERVER_DIR"
            uv venv .venv --python 3.14
            VIRTUAL_ENV="$MA_SERVER_DIR/.venv" uv pip install --index-strategy unsafe-best-match -e "." -e ".[test]" -r requirements_all.txt
        )
    fi
    install_manifest_requirements
    mount_sources
}

update() {
    require_command git
    if [ ! -d "$MA_SERVER_DIR/.git" ]; then
        echo "ERROR: upstream checkout is missing; run setup first" >&2
        exit 1
    fi
    git -C "$MA_SERVER_DIR" fetch --depth=1 origin "$MA_REF"
    git -C "$MA_SERVER_DIR" reset --hard FETCH_HEAD
    git -C "$MA_SERVER_DIR" clean -ffd \
        "music_assistant/providers/$PROVIDER_DOMAIN" \
        "tests/providers/$PROVIDER_DOMAIN"
    echo "Music Assistant: $(git -C "$MA_SERVER_DIR" rev-parse HEAD)"
}

ensure_mounted() {
    if [ ! -x "$MA_SERVER_DIR/.venv/bin/python" ]; then
        setup
    else
        mount_sources
    fi
}

run_tests() {
    ensure_mounted
    (
        cd "$MA_SERVER_DIR"
        source .venv/bin/activate
        pytest --durations 10 --cov-report=term-missing \
            --cov="music_assistant/providers/$PROVIDER_DOMAIN" \
            "tests/providers/$PROVIDER_DOMAIN"
    )
}

run_type_check() {
    ensure_mounted
    (
        cd "$MA_SERVER_DIR"
        source .venv/bin/activate
        mypy \
            "music_assistant/providers/$PROVIDER_DOMAIN" \
            "tests/providers/$PROVIDER_DOMAIN"
    )
}

run_lint() {
    ensure_mounted
    (
        cd "$MA_SERVER_DIR"
        source .venv/bin/activate
        mapfile -t files < <(
            git ls-files --cached --others --exclude-standard -- \
                "music_assistant/providers/$PROVIDER_DOMAIN" \
                "tests/providers/$PROVIDER_DOMAIN"
        )
        # These hooks regenerate repository-wide artifacts unrelated to the mounted provider.
        SKIP=gen_requirements_all,build_translations_source pre-commit run --files "${files[@]}"
    )
}

run_checks() {
    ensure_mounted
    (
        cd "$MA_SERVER_DIR"
        source .venv/bin/activate
        for check in check_config_entries check_translatable_labels check_manifests check_test_layout; do
            if [ -f "scripts/$check.py" ]; then
                python -m "scripts.$check"
            fi
        done
    )
}

case "${1:-}" in
    setup) setup ;;
    update) update ;;
    test) run_tests ;;
    type) run_type_check ;;
    lint) run_lint ;;
    checks) run_checks ;;
    all)
        setup
        run_lint
        run_type_check
        run_checks
        run_tests
        ;;
    *)
        echo "Usage: $0 {setup|update|test|type|lint|checks|all}" >&2
        exit 1
        ;;
esac
