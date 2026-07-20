from slugline_mcp.tools import find_mood_reference_scenes as tool


def test_filters_by_mood_tag(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.find_mood_reference_scenes("paranoid")
    assert len(results) == 1
    assert results[0]["imdb_id"] == "tt0002"
    assert results[0]["mood"] == "paranoid"


def test_no_scenes_tagged_with_mood_returns_empty(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    assert tool.find_mood_reference_scenes("triumphant") == []


def test_respects_top_k(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.find_mood_reference_scenes("tense", top_k=1)
    assert len(results) <= 1


def test_returns_expected_fields(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    results = tool.find_mood_reference_scenes("dread")
    assert results[0].keys() == {
        "id",
        "movie_name",
        "imdb_id",
        "scene_index",
        "slugline",
        "characters",
        "text",
        "mood",
        "mood_score",
    }


def test_unavailable_index_returns_empty_list(unavailable_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: unavailable_retriever)
    assert tool.find_mood_reference_scenes("paranoid") == []
