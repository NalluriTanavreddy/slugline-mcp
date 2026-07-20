"""Vector retrieval over the reference scene index.

Wraps the Chroma collection with a lazy, best-effort initializer: if no
local index exists yet, it tries to download the prebuilt one via
``bootstrap.ensure_index``; if that also fails (offline, no prebuilt index
published yet), retrieval methods degrade to returning empty results rather
than crashing the server, so the MCP server can still start and report a
clear "index unavailable" state to tools.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache

from slugline_mcp.config import Config, load_config
from slugline_mcp.indexing.bootstrap import ensure_index
from slugline_mcp.indexing.chroma_client import get_chroma_client, get_scenes_collection
from slugline_mcp.indexing.embeddings import embed_query

logger = logging.getLogger(__name__)


@dataclass
class RetrievedScene:
    id: str
    text: str
    movie_name: str
    imdb_id: str
    scene_index: int
    slugline: str
    characters: str
    distance: float
    mood: str = ""
    mood_score: float = 0.0


def _metadata_fields(meta: dict) -> dict:
    return {
        "movie_name": meta.get("movie_name", ""),
        "imdb_id": meta.get("imdb_id", ""),
        "scene_index": meta.get("scene_index", -1),
        "slugline": meta.get("slugline", ""),
        "characters": meta.get("characters", ""),
        "mood": meta.get("mood", ""),
        "mood_score": meta.get("mood_score", 0.0),
    }


def _query_results_to_scenes(results) -> list[RetrievedScene]:
    scenes: list[RetrievedScene] = []
    for id_, doc, meta, dist in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        scenes.append(RetrievedScene(id=id_, text=doc, distance=dist, **_metadata_fields(meta)))
    return scenes


class Retriever:
    """Lazily-initialized wrapper around the Chroma scenes collection."""

    def __init__(self, config: Config | None = None):
        self._config = config or load_config()
        self._collection = None
        self._unavailable_reason: str | None = None
        self._movies_cache: list[dict] | None = None

    def _get_collection(self):
        if self._collection is not None or self._unavailable_reason is not None:
            return self._collection
        try:
            ensure_index(self._config.persist_directory, repo_id=self._config.index_repo_id)
        except RuntimeError as e:
            self._unavailable_reason = str(e)
            logger.warning("Reference index unavailable: %s", e)
            return None
        client = get_chroma_client(self._config.persist_directory)
        self._collection = get_scenes_collection(client, self._config.collection_name)
        return self._collection

    @property
    def is_available(self) -> bool:
        return self._get_collection() is not None

    @property
    def unavailable_reason(self) -> str | None:
        self._get_collection()
        return self._unavailable_reason

    def search_similar_scenes(self, query_text: str, n_results: int = 5) -> list[RetrievedScene]:
        collection = self._get_collection()
        if collection is None:
            return []
        query_embedding = embed_query(query_text, model_name=self._config.embedding_model)
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return _query_results_to_scenes(results)

    def search_scenes_by_mood(self, target_mood: str, n_results: int = 3) -> list[RetrievedScene]:
        """Find scenes tagged with ``target_mood``, ranked by similarity to that mood label."""
        collection = self._get_collection()
        if collection is None:
            return []
        query_embedding = embed_query(target_mood, model_name=self._config.embedding_model)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"mood": target_mood},
        )
        return _query_results_to_scenes(results)

    def get_scene(self, scene_id: str) -> RetrievedScene | None:
        collection = self._get_collection()
        if collection is None:
            return None
        result = collection.get(ids=[scene_id], include=["documents", "metadatas"])
        if not result["ids"]:
            return None
        return RetrievedScene(
            id=result["ids"][0],
            text=result["documents"][0],
            distance=0.0,
            **_metadata_fields(result["metadatas"][0]),
        )

    def list_movies(self) -> list[dict]:
        if self._movies_cache is not None:
            return self._movies_cache
        collection = self._get_collection()
        if collection is None:
            return []
        result = collection.get(include=["metadatas"])
        seen: dict[str, dict] = {}
        for meta in result["metadatas"]:
            seen.setdefault(meta["imdb_id"], {"movie_name": meta["movie_name"], "imdb_id": meta["imdb_id"]})
        self._movies_cache = list(seen.values())
        return self._movies_cache


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever()
