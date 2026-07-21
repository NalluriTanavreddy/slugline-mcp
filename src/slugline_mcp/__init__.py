"""slugline-mcp: retrieval-only MCP server for evidence-based screenplay analysis.

Versioning follows semver (https://semver.org): MAJOR.MINOR.PATCH, starting
at 0.x while the API is still pre-1.0 and may change between minor bumps.
``pyproject.toml``'s ``[project] version`` field is the single source of
truth -- read here via installed package metadata rather than duplicating
the string, so the two can never drift out of sync.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("slugline-mcp")
except PackageNotFoundError:
    # Not installed (e.g. running directly from a source checkout without
    # `pip install -e .` / `uv sync`).
    __version__ = "0.0.0+unknown"
