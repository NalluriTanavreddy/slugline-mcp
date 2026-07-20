from slugline_mcp.indexing.bootstrap import _index_exists, ensure_index
from slugline_mcp.indexing.chroma_client import get_chroma_client, get_scenes_collection
from slugline_mcp.indexing.embeddings import embed_texts


def test_empty_directory_is_not_an_index(tmp_path):
    assert _index_exists(tmp_path) is False


def test_chroma_sqlite3_alone_is_not_enough(tmp_path):
    # Merely instantiating a PersistentClient creates chroma.sqlite3 even
    # with zero collections/documents -- a file-existence check alone would
    # be fooled by this and never attempt a real download.
    get_chroma_client(tmp_path)
    assert (tmp_path / "chroma.sqlite3").exists()
    assert _index_exists(tmp_path) is False


def test_populated_collection_is_an_index(tmp_path):
    client = get_chroma_client(tmp_path)
    collection = get_scenes_collection(client)
    collection.add(ids=["1"], embeddings=embed_texts(["a scene"]), documents=["a scene"], metadatas=[{"movie_name": "Test"}])
    assert _index_exists(tmp_path) is True


def test_ensure_index_is_a_noop_when_already_populated(tmp_path):
    client = get_chroma_client(tmp_path)
    collection = get_scenes_collection(client)
    collection.add(ids=["1"], embeddings=embed_texts(["a scene"]), documents=["a scene"], metadatas=[{"movie_name": "Test"}])

    result = ensure_index(tmp_path, repo_id="this-repo-does-not-exist-anywhere/nope")
    assert result == tmp_path  # returned immediately, never attempted a download
