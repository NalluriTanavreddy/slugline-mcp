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
