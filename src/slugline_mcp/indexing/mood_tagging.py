"""Local zero-shot mood classification for reference scenes.

Runs entirely locally via a Hugging Face ``transformers`` zero-shot
classification pipeline (``facebook/bart-large-mnli``) -- no external API
calls and no per-scene cost, matching the embedding step's "no API key
required" design. Used once per scene during indexing; the resulting label
is stored as Chroma metadata so ``find_mood_reference_scenes`` can filter by
it at query time.
"""

from __future__ import annotations

from functools import lru_cache

from transformers import pipeline

from slugline_mcp.indexing.embeddings import DEFAULT_MODEL_NAME, embed_texts

MOOD_MODEL_NAME = "facebook/bart-large-mnli"

CANDIDATE_MOODS = [
    "paranoid",
    "romantic tension",
    "tense",
    "comedic",
    "dread",
    "melancholic",
    "triumphant",
]


@lru_cache(maxsize=1)
def _get_classifier():
    return pipeline("zero-shot-classification", model=MOOD_MODEL_NAME)


def tag_mood(text: str) -> tuple[str, float]:
    """Classify a scene's single dominant mood.

    Returns (label, confidence_score), where label is the highest-scoring
    entry from ``CANDIDATE_MOODS``.
    """
    classifier = _get_classifier()
    result = classifier(text, candidate_labels=CANDIDATE_MOODS)
    return result["labels"][0], float(result["scores"][0])


@lru_cache(maxsize=4)
def get_candidate_mood_embeddings(model_name: str = DEFAULT_MODEL_NAME) -> dict[str, tuple[float, ...]]:
    """Embed each candidate mood label once, for matching a free-text query mood against them.

    Cached per embedding model. Used by ``retrieval.py`` to decide whether a
    user's free-text target mood is close enough to a precoded tag to use
    the precise tag-filtered search path, or should fall back to raw
    semantic search.
    """
    vectors = embed_texts(CANDIDATE_MOODS, model_name=model_name)
    return {label: tuple(vector) for label, vector in zip(CANDIDATE_MOODS, vectors)}
