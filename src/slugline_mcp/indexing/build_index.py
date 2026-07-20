"""Build the reference scene index from rohitsaxena/MovieSum.

This is a maintainer-run script, not something end users of the MCP server
run themselves -- they fetch a prebuilt index via ``bootstrap.py`` instead.
Run it with:

    uv run --extra index python -m slugline_mcp.indexing.build_index

See ``docs/dataset.md`` for details on the dataset itself. Requires the
``index`` extra (``datasets``, ``transformers``), which the published
package does not depend on at runtime.

Each scene is also run through a local zero-shot mood classifier (see
``mood_tagging.py``) so ``find_mood_reference_scenes`` can filter by mood
later. This is the slowest part of indexing -- budget for it when indexing
the full dataset.
"""

from __future__ import annotations

import argparse
import logging

from datasets import concatenate_datasets, load_dataset

from slugline_mcp.indexing.chroma_client import DEFAULT_PERSIST_DIR, get_chroma_client, get_scenes_collection
from slugline_mcp.indexing.embeddings import embed_texts
from slugline_mcp.indexing.mood_tagging import tag_mood
from slugline_mcp.indexing.parser import parse_script_xml

logger = logging.getLogger(__name__)

MIN_SCENE_CHARS = 20  # skip near-empty scenes (e.g. a bare slugline with no body)
EMBED_BATCH_SIZE = 64


def _iter_scene_records(limit: int | None = None):
    """Yield (id, document, metadata) tuples for every scene in every movie."""
    dataset = load_dataset("rohitsaxena/MovieSum")
    combined = concatenate_datasets([dataset["train"], dataset["validation"], dataset["test"]])
    if limit is not None:
        combined = combined.select(range(min(limit, len(combined))))

    for movie in combined:
        try:
            scenes = parse_script_xml(movie["script"])
        except Exception:
            logger.warning("Skipping %s: failed to parse script XML", movie["movie_name"])
            continue

        for scene in scenes:
            text = scene.to_text()
            if len(text) < MIN_SCENE_CHARS:
                continue
            mood, mood_score = tag_mood(text)
            yield (
                f"{movie['imdb_id']}_{scene.index}",
                text,
                {
                    "movie_name": movie["movie_name"],
                    "imdb_id": movie["imdb_id"],
                    "scene_index": scene.index,
                    "slugline": scene.slugline or "",
                    "characters": ", ".join(scene.characters),
                    "mood": mood,
                    "mood_score": mood_score,
                },
            )


def build_index(persist_directory=DEFAULT_PERSIST_DIR, limit: int | None = None) -> int:
    """Parse, embed, and store reference scenes. Returns the number of scenes indexed."""
    client = get_chroma_client(persist_directory)
    collection = get_scenes_collection(client)

    batch_ids: list[str] = []
    batch_docs: list[str] = []
    batch_meta: list[dict] = []
    total = 0

    def flush():
        nonlocal total
        if not batch_ids:
            return
        embeddings = embed_texts(batch_docs)
        collection.add(ids=batch_ids, embeddings=embeddings, documents=batch_docs, metadatas=batch_meta)
        total += len(batch_ids)
        batch_ids.clear()
        batch_docs.clear()
        batch_meta.clear()

    for scene_id, text, metadata in _iter_scene_records(limit=limit):
        batch_ids.append(scene_id)
        batch_docs.append(text)
        batch_meta.append(metadata)
        if len(batch_ids) >= EMBED_BATCH_SIZE:
            flush()
            logger.info("Indexed %d scenes so far", total)

    flush()
    logger.info("Done. Indexed %d scenes into %s", total, persist_directory)
    return total


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only index the first N movies (for local testing; omit to index the full dataset).",
    )
    parser.add_argument(
        "--persist-directory",
        type=str,
        default=str(DEFAULT_PERSIST_DIR),
        help="Directory to store the Chroma index in.",
    )
    args = parser.parse_args()
    build_index(persist_directory=args.persist_directory, limit=args.limit)


if __name__ == "__main__":
    main()
