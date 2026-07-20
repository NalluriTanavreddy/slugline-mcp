from slugline_mcp.tools import list_indexed_movies as tool


def test_lists_unique_movies(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    movies = tool.list_indexed_movies()
    assert {m["imdb_id"] for m in movies} == {"tt0001", "tt0002"}
    assert len(movies) == 2  # tt0001 has two indexed scenes but should appear once


def test_unavailable_index_returns_empty_list(unavailable_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: unavailable_retriever)
    assert tool.list_indexed_movies() == []
