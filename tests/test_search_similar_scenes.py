from slugline_mcp.tools import search_similar_scenes as tool


def test_returns_most_similar_scene_first(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.search_similar_scenes("someone in a car chasing another vehicle", n_results=3)
    assert results[0]["imdb_id"] == "tt0001"
    assert results[0]["slugline"] == "INT. TAXI -- DAY"


def test_respects_n_results(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.search_similar_scenes("anything", n_results=1)
    assert len(results) == 1


def test_returns_expected_fields(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.search_similar_scenes("kitchen argument about inheritance", n_results=1)
    scene = results[0]
    assert set(scene.keys()) == {
        "id",
        "movie_name",
        "imdb_id",
        "scene_index",
        "slugline",
        "characters",
        "text",
        "similarity_distance",
    }
    assert scene["movie_name"] == "Another Movie"


def test_unavailable_index_returns_empty_list(unavailable_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: unavailable_retriever)
    assert tool.search_similar_scenes("anything") == []
