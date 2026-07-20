"""slugline-mcp MCP server.

Retrieval-only: this server parses, embeds, and searches a reference
database of real screenplay scenes. It exposes that search as MCP tools for
a connected LLM to use when analyzing the user's own script -- it does not
generate or judge writing itself.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from slugline_mcp.tools.find_mood_reference_scenes import find_mood_reference_scenes
from slugline_mcp.tools.get_analysis_style import get_analysis_style
from slugline_mcp.tools.get_scene_details import get_scene_details
from slugline_mcp.tools.list_indexed_movies import list_indexed_movies
from slugline_mcp.tools.search_similar_scenes import search_similar_scenes

mcp = FastMCP(
    name="slugline-mcp",
    instructions=(
        "Retrieval tools for evidence-based screenplay analysis. Use these tools to "
        "find real produced scenes similar to a scene the user is writing, then ground "
        "your mood/next-action/comparison analysis in that retrieved evidence rather "
        "than general knowledge."
    ),
)

mcp.add_tool(get_analysis_style)
mcp.add_tool(search_similar_scenes)
mcp.add_tool(get_scene_details)
mcp.add_tool(list_indexed_movies)
mcp.add_tool(find_mood_reference_scenes)
