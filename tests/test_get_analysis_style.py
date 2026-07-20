from slugline_mcp.tools.get_analysis_style import get_analysis_style


def test_returns_nonempty_string():
    result = get_analysis_style()
    assert isinstance(result, str)
    assert len(result) > 0


def test_mentions_the_other_tools():
    result = get_analysis_style()
    assert "search_similar_scenes" in result
    assert "get_scene_details" in result
    assert "find_mood_reference_scenes" in result


def test_mentions_the_three_analysis_components():
    result = get_analysis_style().lower()
    assert "mood" in result
    assert "next action" in result
    assert "meets" in result


def test_is_deterministic():
    assert get_analysis_style() == get_analysis_style()
