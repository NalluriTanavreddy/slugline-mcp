"""Sentence-transformers embedding wrapper used for both indexing and query time.

Uses ``sentence-transformers/all-MiniLM-L6-v2`` (384-dim, CPU-friendly) so
neither indexing the reference dataset nor running the MCP server locally
requires a GPU or an external API key.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedder(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """Load (and cache) the sentence-transformers model.

    Cached so the model is loaded once per process regardless of how many
    times indexing or retrieval code asks for it.
    """
    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL_NAME) -> list[list[float]]:
    """Embed a batch of scene texts into vectors."""
    embedder = get_embedder(model_name)
    vectors = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()


def embed_query(text: str, model_name: str = DEFAULT_MODEL_NAME) -> list[float]:
    """Embed a single query string (e.g. a scene from the user's script)."""
    return embed_texts([text], model_name=model_name)[0]
