#!/usr/bin/env bash
# Validate every ```mermaid block in the repo by rendering it with mermaid-cli.
# Usage: scripts/check-mermaid.sh   (exit 1 on any diagram that fails to render)
# Chrome runs without its sandbox (scripts/puppeteer-config.json): the input is our own
# diagrams, and CI runners and AppArmor-restricted hosts cannot start the sandbox.
set -euo pipefail
cd "$(dirname "$0")/.."

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# Extract each fenced mermaid block to <tmp>/<path-with-underscores>.<n>.mmd
while IFS= read -r file; do
  awk -v out="$tmp/$(echo "$file" | tr '/' '_')" '
    /^```mermaid/ { i++; f = 1; next }
    /^```/ && f   { f = 0; close(out "." i ".mmd"); next }
    f             { print > (out "." i ".mmd") }
  ' "$file"
done < <(grep -rl --include='*.md' '^```mermaid' . | grep -v node_modules | sed 's#^\./##')

status=0
n=0
for d in "$tmp"/*.mmd; do
  [ -e "$d" ] || continue
  n=$((n + 1))
  if ! npx -y @mermaid-js/mermaid-cli -q -p scripts/puppeteer-config.json -i "$d" -o "$d.svg" >"$d.log" 2>&1; then
    echo "FAIL: $(basename "$d")"
    cat "$d.log"
    status=1
  fi
done

echo "Checked $n Mermaid diagram(s)"
exit $status
