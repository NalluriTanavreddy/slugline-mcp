"""search_similar_scenes: find real produced scenes similar to a query scene."""

from __future__ import annotations

from slugline_mcp.retrieval import RetrievedScene, get_retriever


def search_similar_scenes(query: str, n_results: int = 5) -> list[dict]:
    """Search the reference index for scenes similar to ``query``.

    Args:
        query: A scene's text (slugline, action, and/or dialogue) to find
            similar produced scenes for.
        n_results: Maximum number of matches to return (default 5).

    Returns:
        A list of matches, ranked most similar first. Empty if the reference
        index isn't available (see ``get_retriever().unavailable_reason``).
    """
    retriever = get_retriever()
    scenes = retriever.search_similar_scenes(query, n_results=n_results)
    return [_format_scene(scene) for scene in scenes]


def _format_scene(scene: RetrievedScene) -> dict:
    return {
        "id": scene.id,
        "movie_name": scene.movie_name,
        "imdb_id": scene.imdb_id,
        "slugline": scene.slugline,
        "characters": scene.characters,
        "text": scene.text,
        "similarity_distance": round(scene.distance, 4),
    }
