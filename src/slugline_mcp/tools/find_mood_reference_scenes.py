"""find_mood_reference_scenes: reference scenes that strongly hit a target mood.

Different purpose from ``search_similar_scenes``: that tool finds scenes
structurally/tonally similar to a scene you already have. This tool is for
when the user wants to *rewrite* their scene to achieve a mood it doesn't
have yet (e.g. "make this more paranoid") -- it surfaces reference scenes
that strongly achieve that target mood, so the user can see how other
scripts pulled it off.

Uses a hybrid strategy (see ``retrieval.Retriever.search_scenes_by_mood``):
free-text moods close to one of the precoded tags computed during indexing
(see ``mood_tagging.py``) get precise tag-filtered results; anything else
falls back to raw semantic search over every scene, so an unusual target
mood still returns something reasonable instead of nothing. The response's
``method`` field says which path was used, for transparency about match
confidence.

Call `get_analysis_style` first, same as the other tools, before presenting
these results as feedback.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from slugline_mcp.retrieval import get_retriever
from slugline_mcp.tools._formatting import format_scene


def find_mood_reference_scenes(
    target_mood: Annotated[
        str,
        Field(
            description=(
                "The mood to rewrite toward, in free text (e.g. \"paranoid\", \"wistful\", "
                '"a creeping sense of being watched"). Doesn\'t need to match a precoded label -- '
                "close matches use a precise tag-filtered search, anything else falls back to raw "
                "semantic search so results are still returned."
            )
        ),
    ],
    top_k: Annotated[int, Field(description="Maximum number of matches to return.")] = 3,
) -> dict:
    """Find reference scenes that strongly achieve a target mood.

    Returns:
        A dict with:
        - ``method``: ``"tag_matched"`` if ``target_mood`` closely matched a
          precoded mood tag, ``"semantic_fallback"`` if it didn't and results
          came from raw nearest-neighbor search instead, or ``"unavailable"``
          if the reference index isn't available.
        - ``matched_tag`` / ``tag_similarity``: the closest precoded tag and
          its cosine similarity to ``target_mood``, regardless of which
          method was used -- lets the caller judge match confidence even on
          the fallback path.
        - ``results``: the ranked scene matches themselves. Empty if no
          scenes are available or the index is unavailable.
    """
    retriever = get_retriever()
    mood_result = retriever.search_scenes_by_mood(target_mood, n_results=top_k)
    return {
        "method": mood_result.method,
        "matched_tag": mood_result.matched_tag,
        "tag_similarity": mood_result.tag_similarity,
        "results": [
            format_scene(scene, mood=scene.mood, mood_score=round(scene.mood_score, 4))
            for scene in mood_result.scenes
        ],
    }
