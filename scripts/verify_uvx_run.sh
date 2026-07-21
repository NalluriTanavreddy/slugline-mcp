#!/usr/bin/env bash
# Verifies `uvx slugline-mcp` works end-to-end before the package is
# published to PyPI: builds a wheel locally, then has uvx install and run
# it from that wheel path (`uvx --from <wheel> slugline-mcp`) in an
# ephemeral environment, exactly like it would with a published package.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

echo "==> Building wheel"
rm -rf dist
uv build >/dev/null

wheel="$(ls dist/*.whl)"
echo "==> Built $wheel"

echo "==> Running slugline-mcp via uvx from that wheel"
echo -n "" | uvx --from "$wheel" slugline-mcp

echo "==> OK: uvx slugline-mcp ran end-to-end."
