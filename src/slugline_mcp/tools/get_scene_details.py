"""get_scene_details: fetch the full text and metadata for one indexed scene by id."""

from __future__ import annotations

from slugline_mcp.retrieval import get_retriever


def get_scene_details(scene_id: str) -> dict | None:
    """Fetch full details for a specific reference scene.

    Args:
        scene_id: A scene id as returned by ``search_similar_scenes``
            (format: ``"{imdb_id}_{scene_index}"``).

    Returns:
        A dict with the scene's movie, slugline, characters, and full text,
        or ``None`` if the id doesn't exist (or the index is unavailable).
    """
    retriever = get_retriever()
    scene = retriever.get_scene(scene_id)
    if scene is None:
        return None
    return {
        "id": scene.id,
        "movie_name": scene.movie_name,
        "imdb_id": scene.imdb_id,
        "scene_index": scene.scene_index,
        "slugline": scene.slugline,
        "characters": scene.characters,
        "text": scene.text,
    }
