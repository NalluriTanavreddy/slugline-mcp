"""Scene splitter for plain-text, user-submitted scripts.

Unlike MovieSum's pre-structured XML (see ``parser.py``), a script a user
pastes in has no markup at all -- just raw lines of a screenplay. This module
splits that raw text into scenes purely by detecting slugline (scene heading)
lines, without attempting to further classify each line as action, character
cue, or dialogue. That's a reasonable trade: slugline detection is reliable
via convention (INT./EXT.), while reconstructing dialogue structure from
indentation/case heuristics is not, and scene-level text is all retrieval
needs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SLUGLINE_RE = re.compile(
    r"^\s*(?:\d+[A-Z]?\.?\s+)?"  # optional leading scene number, e.g. "12." or "14A"
    r"(?:INT|EXT|I/E|INT\.?/EXT)\.?/?\s",
    re.IGNORECASE,
)


@dataclass
class PlainScene:
    index: int
    slugline: str | None
    text: str


def split_into_scenes(raw_text: str) -> list[PlainScene]:
    """Split a raw, unstructured script into scenes at slugline boundaries.

    Any text before the first detected slugline (e.g. a title page) becomes
    a leading scene with ``slugline=None``, if non-empty.
    """
    lines = raw_text.splitlines()

    boundaries: list[int] = [i for i, line in enumerate(lines) if _SLUGLINE_RE.match(line)]

    scenes: list[PlainScene] = []
    if boundaries and boundaries[0] > 0:
        preamble = "\n".join(lines[: boundaries[0]]).strip()
        if preamble:
            scenes.append(PlainScene(index=len(scenes), slugline=None, text=preamble))
    elif not boundaries:
        text = raw_text.strip()
        if text:
            scenes.append(PlainScene(index=0, slugline=None, text=text))
        return scenes

    for start, end in zip(boundaries, boundaries[1:] + [len(lines)]):
        slugline = lines[start].strip()
        body = "\n".join(lines[start:end]).strip()
        scenes.append(PlainScene(index=len(scenes), slugline=slugline, text=body))

    return scenes
