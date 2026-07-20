"""Shared response formatting for tools that return scenes."""

from __future__ import annotations

from slugline_mcp.retrieval import RetrievedScene


def format_scene(scene: RetrievedScene, **extra) -> dict:
    """Canonical scene response shape, with any per-tool extra fields merged in."""
    return {
        "id": scene.id,
        "movie_name": scene.movie_name,
        "imdb_id": scene.imdb_id,
        "scene_index": scene.scene_index,
        "slugline": scene.slugline,
        "characters": scene.characters,
        "text": scene.text,
        **extra,
    }
