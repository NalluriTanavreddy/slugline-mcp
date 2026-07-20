from slugline_mcp.tools import find_mood_reference_scenes as tool

# Calibrated against sentence-transformers/all-MiniLM-L6-v2: similarity to every
# CANDIDATE_MOODS tag stays well below MOOD_TAG_MATCH_THRESHOLD (0.45), so this
# reliably exercises the semantic_fallback path regardless of index contents.
OUT_OF_DOMAIN_MOOD = "quarterly earnings report"


def test_tag_matched_path_filters_by_mood_tag(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    response = tool.find_mood_reference_scenes("paranoid")
    assert response["method"] == "tag_matched"
    assert response["matched_tag"] == "paranoid"
    assert response["tag_similarity"] > 0.9  # near-exact match to the tag itself
    assert len(response["results"]) == 1
    assert response["results"][0]["imdb_id"] == "tt0002"
    assert response["results"][0]["mood"] == "paranoid"


def test_tag_matched_path_with_no_matching_scenes_returns_empty_results(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    response = tool.find_mood_reference_scenes("triumphant")
    assert response["method"] == "tag_matched"  # exact tag match, just nothing indexed under it
    assert response["results"] == []


def test_semantic_fallback_path_for_out_of_domain_mood(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    response = tool.find_mood_reference_scenes(OUT_OF_DOMAIN_MOOD, top_k=4)
    assert response["method"] == "semantic_fallback"
    assert response["tag_similarity"] < 0.45
    # Fallback ignores the mood filter entirely, so it can surface scenes
    # across more than one mood tag rather than being locked to one.
    moods_seen = {r["mood"] for r in response["results"]}
    assert len(response["results"]) > 0
    assert len(moods_seen) > 1


def test_respects_top_k(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    response = tool.find_mood_reference_scenes("tense", top_k=1)
    assert len(response["results"]) <= 1


def test_returns_expected_top_level_shape(populated_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: populated_retriever)
    response = tool.find_mood_reference_scenes("dread")
    assert response.keys() == {"method", "matched_tag", "tag_similarity", "results"}
    assert response["results"][0].keys() == {
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


def test_unavailable_index_returns_empty_results(unavailable_retriever, monkeypatch):
    monkeypatch.setattr(tool, "get_retriever", lambda: unavailable_retriever)
    response = tool.find_mood_reference_scenes("paranoid")
    assert response["method"] == "unavailable"
    assert response["results"] == []
