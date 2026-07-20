"""find_mood_reference_scenes: reference scenes that strongly hit a target mood.

Different purpose from ``search_similar_scenes``: that tool finds scenes
structurally/tonally similar to a scene you already have. This tool is for
when the user wants to *rewrite* their scene to achieve a mood it doesn't
have yet (e.g. "make this more paranoid") -- it surfaces reference scenes
that strongly achieve that target mood, tagged during indexing (see
``mood_tagging.py``), so the user can see how other scripts pulled it off.

Call `get_analysis_style` first, same as the other tools, before presenting
these results as feedback.
"""

from __future__ import annotations

from slugline_mcp.retrieval import get_retriever
from slugline_mcp.tools._formatting import format_scene


def find_mood_reference_scenes(target_mood: str, top_k: int = 3) -> list[dict]:
    """Find reference scenes that strongly achieve a target mood.

    Args:
        target_mood: The mood to rewrite toward (must match one of the moods
            tagged during indexing, e.g. "paranoid", "romantic tension",
            "tense", "comedic", "dread", "melancholic", "triumphant").
        top_k: Maximum number of matches to return (default 3).

    Returns:
        A list of matches ranked by embedding similarity to the mood label
        itself, each with the movie name, scene excerpt, and mood tag.
        Empty if no scenes are tagged with that mood, or if the reference
        index is unavailable.
    """
    retriever = get_retriever()
    scenes = retriever.search_scenes_by_mood(target_mood, n_results=top_k)
    return [format_scene(scene, mood=scene.mood, mood_score=round(scene.mood_score, 4)) for scene in scenes]
