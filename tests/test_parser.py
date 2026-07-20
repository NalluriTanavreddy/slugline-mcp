from pathlib import Path

from slugline_mcp.indexing.parser import parse_script_xml

FIXTURE = (Path(__file__).parent / "fixtures" / "sample_script.xml").read_text()


def test_parses_all_scenes():
    scenes = parse_script_xml(FIXTURE)
    assert len(scenes) == 3


def test_slugline_and_action_lines():
    scenes = parse_script_xml(FIXTURE)
    scene = scenes[0]
    assert scene.slugline == "INT. DINER -- NIGHT"
    assert len(scene.action_lines) == 2


def test_dialogue_and_characters_in_order():
    scenes = parse_script_xml(FIXTURE)
    scene = scenes[0]
    assert scene.characters == ["MARA", "WAITER"]
    assert [line.character for line in scene.dialogue] == ["MARA", "WAITER", "WAITER"]


def test_parenthetical_attaches_to_preceding_dialogue_line():
    scenes = parse_script_xml(FIXTURE)
    dialogue = scenes[0].dialogue
    assert dialogue[1].text == "Kitchen's backed up."
    assert dialogue[1].parenthetical is None
    assert dialogue[2].text == "Always is on a Friday."
    assert dialogue[2].parenthetical == "not looking up"


def test_scene_without_dialogue():
    scenes = parse_script_xml(FIXTURE)
    scene = scenes[1]
    assert scene.slugline == "EXT. DINER PARKING LOT -- CONTINUOUS"
    assert scene.dialogue == []
    assert len(scene.action_lines) == 1


def test_scene_without_slugline_parses_defensively():
    scenes = parse_script_xml(FIXTURE)
    scene = scenes[2]
    assert scene.slugline is None
    assert scene.characters == ["UNKNOWN VOICE"]


def test_to_text_includes_slugline_and_dialogue():
    scenes = parse_script_xml(FIXTURE)
    text = scenes[0].to_text()
    assert text.startswith("INT. DINER -- NIGHT")
    assert "MARA: I've been waiting an hour." in text
    assert "WAITER: (not looking up) Always is on a Friday." in text
