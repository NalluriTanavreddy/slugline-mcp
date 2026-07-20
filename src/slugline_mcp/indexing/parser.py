"""Parser for MovieSum's pre-structured screenplay XML.

MovieSum ships each script as a ``<script>`` document containing an ordered
sequence of ``<scene>`` elements. Each scene is itself an ordered sequence of:

- ``stage_direction``: the slugline (e.g. "INT. OFFICE -- DAY")
- ``scene_description``: an action/description line
- ``character``: the speaker for the dialogue line that follows
- ``dialogue``: a line of spoken dialogue
- ``parenthetical``: a mid-speech beat, attached to the preceding dialogue line

Scenes are not guaranteed to have a slugline or any dialogue at all
(action-only scenes are common), so every field below is parsed defensively.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class DialogueLine:
    character: str
    text: str
    parenthetical: str | None = None


@dataclass
class Scene:
    index: int
    slugline: str | None
    # Ordered ("action", str) | ("dialogue", DialogueLine) entries, in script order.
    body: list[tuple[str, object]] = field(default_factory=list)

    @property
    def action_lines(self) -> list[str]:
        return [value for tag, value in self.body if tag == "action"]

    @property
    def dialogue(self) -> list[DialogueLine]:
        return [value for tag, value in self.body if tag == "dialogue"]

    @property
    def characters(self) -> list[str]:
        seen: list[str] = []
        for line in self.dialogue:
            if line.character not in seen:
                seen.append(line.character)
        return seen

    def to_text(self) -> str:
        """Flatten the scene back into ordered screenplay-style text for embedding."""
        parts: list[str] = []
        if self.slugline:
            parts.append(self.slugline)
        for tag, value in self.body:
            if tag == "action":
                parts.append(value)
            else:
                prefix = f"{value.character}: "
                if value.parenthetical:
                    parts.append(f"{prefix}({value.parenthetical}) {value.text}")
                else:
                    parts.append(f"{prefix}{value.text}")
        return "\n".join(parts)


def parse_script_xml(xml_text: str) -> list[Scene]:
    """Parse a MovieSum ``<script>`` XML document into an ordered list of Scenes."""
    root = ET.fromstring(xml_text)
    scenes: list[Scene] = []

    for i, scene_el in enumerate(root.findall("scene")):
        stage_direction_el = scene_el.find("stage_direction")
        slugline = None
        if stage_direction_el is not None and stage_direction_el.text:
            slugline = stage_direction_el.text.strip()

        scene = Scene(index=i, slugline=slugline)
        pending_character: str | None = None

        for child in scene_el:
            text = (child.text or "").strip()
            if child.tag == "stage_direction":
                continue
            elif child.tag == "scene_description":
                if text:
                    scene.body.append(("action", text))
            elif child.tag == "character":
                pending_character = text
            elif child.tag == "dialogue":
                scene.body.append(
                    ("dialogue", DialogueLine(character=pending_character or "UNKNOWN", text=text))
                )
                pending_character = None
            elif child.tag == "parenthetical":
                for tag, value in reversed(scene.body):
                    if tag == "dialogue":
                        value.parenthetical = text
                        break

        scenes.append(scene)

    return scenes
