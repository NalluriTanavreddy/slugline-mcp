"""list_indexed_movies: enumerate which movies are in the reference index."""

from __future__ import annotations

from slugline_mcp.retrieval import get_retriever


def list_indexed_movies() -> list[dict]:
    """List every movie currently in the reference index.

    Returns:
        A list of ``{"movie_name": ..., "imdb_id": ...}`` dicts, one per
        indexed movie. Empty if the reference index is unavailable.
    """
    retriever = get_retriever()
    return retriever.list_movies()
