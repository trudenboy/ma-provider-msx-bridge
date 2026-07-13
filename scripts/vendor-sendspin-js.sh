#!/usr/bin/env bash
# Vendor the @sendspin/sendspin-js browser client into provider/static/web/sendspin-js/.
#
# The upstream dist is TypeScript ESM output with extensionless relative
# imports ("./core/core"), which only load through CDNs that rewrite
# specifiers. Browsers loading from our static server need exact paths, so
# this script appends ".js" to every relative import specifier and warns
# about specifier forms it cannot fix (bare or dynamic imports) — those are
# also guarded by test_vendored_sendspin_js_imports_are_browser_loadable,
# which resolves every specifier against the vendored tree.
#
# Usage: scripts/vendor-sendspin-js.sh [version]
set -euo pipefail

VERSION="${1:-3.2.0}"
PKG="@sendspin/sendspin-js"
DEST="$(cd "$(dirname "$0")/.." && pwd)/provider/static/web/sendspin-js"
STAGING="${DEST}.tmp"

echo "Vendoring ${PKG}@${VERSION} -> ${DEST}"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"

files=$(curl -fsSL "https://unpkg.com/${PKG}@${VERSION}/dist/?meta" | python3 -c '
import json, sys

def walk(node):
    for f in node.get("files", []):
        if f.get("type") == "directory":
            walk(f)
        elif f["path"].endswith(".js") and not f["path"].endswith(".js.map"):
            print(f["path"])

walk(json.load(sys.stdin))
')

if [ -z "${files}" ]; then
    echo "ERROR: no dist files found for ${PKG}@${VERSION} — unpkg meta shape changed?" >&2
    rm -rf "${STAGING}"
    exit 1
fi

for path in ${files}; do
    rel="${path#/dist/}"
    mkdir -p "${STAGING}/$(dirname "${rel}")"
    curl -fsSL "https://unpkg.com/${PKG}@${VERSION}${path}" -o "${STAGING}/${rel}"
    echo "  ${rel}"
done

python3 - "${STAGING}" <<'EOF'
import pathlib
import re
import sys

rewrite = re.compile(r"""((?:import|export)[^'"]*?from\s+['"])(\.\.?/[^'"]+?)(['"])""")
# specifier forms the rewriter cannot fix — surface them for manual review
unhandled = re.compile(r"""(?:import\s*\(\s*|import\s+)['"]([^'"]+)['"]""")
for js in pathlib.Path(sys.argv[1]).rglob("*.js"):
    src = js.read_text(encoding="utf-8")
    fixed = rewrite.sub(
        lambda m: m.group(1)
        + (m.group(2) if m.group(2).endswith(".js") else m.group(2) + ".js")
        + m.group(3),
        src,
    )
    # trailing newline keeps the files clean for the end-of-file-fixer hook
    if not fixed.endswith("\n"):
        fixed += "\n"
    if fixed != src:
        js.write_text(fixed, encoding="utf-8")
        print(f"  rewrote imports: {js.name}")
    for spec in unhandled.findall(fixed):
        print(f"  WARNING: unrewritable specifier in {js.name}: {spec}")
EOF

echo "${PKG}@${VERSION}" > "${STAGING}/VERSION.txt"
count=$(find "${STAGING}" -name '*.js' | wc -l)
if [ "${count}" -eq 0 ]; then
    echo "ERROR: staging is empty, keeping existing ${DEST}" >&2
    rm -rf "${STAGING}"
    exit 1
fi
rm -rf "${DEST}"
mv "${STAGING}" "${DEST}"
echo "Done: ${count} js files"
