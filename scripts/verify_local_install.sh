#!/usr/bin/env bash
# Verifies slugline-mcp installs and runs correctly via `uv pip install -e .`
# in a fresh, isolated virtual environment -- independent of the project's
# own dev venv (which uses `uv sync`, a different code path). Cleans up
# after itself either way.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work_dir="$(mktemp -d)"
venv_dir="$work_dir/venv"
trap 'rm -rf "$work_dir"' EXIT

echo "==> Creating isolated venv at $venv_dir"
uv venv "$venv_dir"

echo "==> Installing slugline-mcp in editable mode (uv pip install -e .)"
uv pip install --python "$venv_dir/bin/python" -e "$repo_root"

echo "==> Verifying the package is importable"
"$venv_dir/bin/python" -c "import slugline_mcp; print('slugline_mcp version:', slugline_mcp.__version__)"

echo "==> Verifying the server module and tool registration import cleanly"
"$venv_dir/bin/python" -c "import slugline_mcp.server as s; print('MCP server name:', s.mcp.name)"

echo "==> Verifying the slugline-mcp console script entry point runs"
echo -n "" | "$venv_dir/bin/slugline-mcp"

echo "==> OK: local editable install verified."
