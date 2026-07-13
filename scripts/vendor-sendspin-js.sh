#!/usr/bin/env bash
# Vendor the @sendspin/sendspin-js browser client into provider/static/web/sendspin-js/.
#
# The upstream dist is TypeScript ESM output with extensionless relative
# imports ("./core/core"), which only load through CDNs that rewrite
# specifiers. Browsers loading from our static server need exact paths, so
# this script appends ".js" to every relative import specifier.
#
# Usage: scripts/vendor-sendspin-js.sh [version]
set -euo pipefail

VERSION="${1:-3.2.0}"
PKG="@sendspin/sendspin-js"
DEST="$(cd "$(dirname "$0")/.." && pwd)/provider/static/web/sendspin-js"

echo "Vendoring ${PKG}@${VERSION} -> ${DEST}"
rm -rf "${DEST}"
mkdir -p "${DEST}"

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

for path in ${files}; do
    rel="${path#/dist/}"
    mkdir -p "${DEST}/$(dirname "${rel}")"
    curl -fsSL "https://unpkg.com/${PKG}@${VERSION}${path}" -o "${DEST}/${rel}"
    echo "  ${rel}"
done

python3 - "${DEST}" <<'EOF'
import pathlib
import re
import sys

pattern = re.compile(r"""((?:import|export)[^'"]*?from\s+['"])(\.\.?/[^'"]+?)(['"])""")
for js in pathlib.Path(sys.argv[1]).rglob("*.js"):
    src = js.read_text(encoding="utf-8")
    fixed = pattern.sub(
        lambda m: m.group(1) + (m.group(2) if m.group(2).endswith(".js") else m.group(2) + ".js") + m.group(3),
        src,
    )
    if fixed != src:
        js.write_text(fixed, encoding="utf-8")
        print(f"  rewrote imports: {js.name}")
EOF

echo "${PKG}@${VERSION}" > "${DEST}/VERSION.txt"
echo "Done: $(find "${DEST}" -name '*.js' | wc -l) js files"
