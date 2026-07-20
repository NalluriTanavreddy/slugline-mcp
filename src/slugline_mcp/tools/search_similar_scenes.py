"""search_similar_scenes: find real produced scenes similar to a query scene."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from slugline_mcp.retrieval import get_retriever
from slugline_mcp.tools._formatting import format_scene


def search_similar_scenes(
    query: Annotated[
        str,
        Field(description="A scene's text (slugline, action, and/or dialogue) to find similar produced scenes for."),
    ],
    n_results: Annotated[int, Field(description="Maximum number of matches to return.")] = 5,
) -> list[dict]:
    """Search the reference index for scenes similar to ``query``.

    Returns:
        A list of matches, ranked most similar first. Empty if the reference
        index isn't available (see ``get_retriever().unavailable_reason``).
    """
    retriever = get_retriever()
    scenes = retriever.search_similar_scenes(query, n_results=n_results)
    return [format_scene(scene, similarity_distance=round(scene.distance, 4)) for scene in scenes]
