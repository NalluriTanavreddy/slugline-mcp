"""slugline-mcp MCP server.

Retrieval-only: this server parses, embeds, and searches a reference
database of real screenplay scenes. It exposes that search as MCP tools for
a connected LLM to use when analyzing the user's own script -- it does not
generate or judge writing itself.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="slugline-mcp",
    instructions=(
        "Retrieval tools for evidence-based screenplay analysis. Use these tools to "
        "find real produced scenes similar to a scene the user is writing, then ground "
        "your mood/next-action/comparison analysis in that retrieved evidence rather "
        "than general knowledge."
    ),
)
