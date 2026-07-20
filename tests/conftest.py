import pytest

from slugline_mcp.config import Config
from slugline_mcp.indexing.chroma_client import get_chroma_client, get_scenes_collection
from slugline_mcp.indexing.embeddings import DEFAULT_MODEL_NAME, embed_texts
from slugline_mcp.retrieval import Retriever

SAMPLE_SCENES = [
    {
        "id": "tt0001_0",
        "text": "INT. TAXI -- DAY\nA passenger urges the driver to follow a limousine ahead.",
        "metadata": {
            "movie_name": "Test Movie",
            "imdb_id": "tt0001",
            "scene_index": 0,
            "slugline": "INT. TAXI -- DAY",
            "characters": "DRIVER, RIDER",
        },
    },
    {
        "id": "tt0001_1",
        "text": "EXT. FOREST -- NIGHT\nWolves circle a campfire while a lone hiker sharpens a knife.",
        "metadata": {
            "movie_name": "Test Movie",
            "imdb_id": "tt0001",
            "scene_index": 1,
            "slugline": "EXT. FOREST -- NIGHT",
            "characters": "HIKER",
        },
    },
    {
        "id": "tt0002_0",
        "text": "INT. KITCHEN -- MORNING\nTwo sisters argue quietly over coffee about their mother's will.",
        "metadata": {
            "movie_name": "Another Movie",
            "imdb_id": "tt0002",
            "scene_index": 0,
            "slugline": "INT. KITCHEN -- MORNING",
            "characters": "SISTER A, SISTER B",
        },
    },
]


def make_test_config(persist_directory) -> Config:
    return Config(
        persist_directory=persist_directory,
        collection_name="scenes",
        embedding_model=DEFAULT_MODEL_NAME,
        index_repo_id="unused/unused",
        log_level="INFO",
    )


@pytest.fixture
def populated_retriever(tmp_path):
    """A Retriever backed by a small synthetic index, with no network calls.

    Bypasses ``ensure_index``/HF entirely by populating and attaching the
    Chroma collection directly, so tool tests don't depend on the network or
    the real (multi-GB) reference dataset.
    """
    client = get_chroma_client(tmp_path)
    collection = get_scenes_collection(client)
    embeddings = embed_texts([s["text"] for s in SAMPLE_SCENES])
    collection.add(
        ids=[s["id"] for s in SAMPLE_SCENES],
        embeddings=embeddings,
        documents=[s["text"] for s in SAMPLE_SCENES],
        metadatas=[s["metadata"] for s in SAMPLE_SCENES],
    )

    retriever = Retriever(make_test_config(tmp_path))
    retriever._collection = collection
    return retriever


@pytest.fixture
def unavailable_retriever(tmp_path):
    """A Retriever simulating a missing/unreachable index, with no network calls."""
    retriever = Retriever(make_test_config(tmp_path / "missing"))
    retriever._unavailable_reason = "simulated: no index available"
    return retriever
