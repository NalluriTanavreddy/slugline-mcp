from slugline_mcp.tools import get_scene_details as tool


def test_returns_full_scene_by_id(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    scene = tool.get_scene_details("tt0002_0")
    assert scene["movie_name"] == "Another Movie"
    assert scene["scene_index"] == 0
    assert "sisters argue" in scene["text"]


def test_unknown_id_returns_none(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    assert tool.get_scene_details("does-not-exist") is None


def test_unavailable_index_returns_none(unavailable_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: unavailable_retriever)
    assert tool.get_scene_details("tt0001_0") is None
