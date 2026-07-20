"""get_scene_details: fetch the full text and metadata for one indexed scene by id."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from slugline_mcp.retrieval import get_retriever
from slugline_mcp.tools._formatting import format_scene


def get_scene_details(
    scene_id: Annotated[
        str,
        Field(description='A scene id as returned by search_similar_scenes (format: "{imdb_id}_{scene_index}").'),
    ],
) -> dict | None:
    """Fetch full details for a specific reference scene.

    Returns:
        A dict with the scene's movie, slugline, characters, and full text,
        or ``None`` if the id doesn't exist (or the index is unavailable).
    """
    retriever = get_retriever()
    scene = retriever.get_scene(scene_id)
    if scene is None:
        return None
    return format_scene(scene)
