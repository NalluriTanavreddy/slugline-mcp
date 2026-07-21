# Demo walkthrough

No screen recording exists yet (see the roadmap in `README.md`) — this is a
text walkthrough instead, using **real tool output** captured against an
actual locally-built index (a small slice of MovieSum, including *8MM*
(1999) and *The Iron Lady* (2011)), not fabricated examples. Once a full
prebuilt index is published, the numbers/exact matches will differ, but the
shape of every response below is exactly what the tools return.

## 1. Finding a similar scene

You paste a scene into Claude and ask for feedback. Claude calls
`get_analysis_style` (not shown — it's plain instructional text, see
`tools/get_analysis_style.py`), then `search_similar_scenes`:

**Query:** `"A tense confrontation in a taxi cab, someone being followed"`

**Top result:**

```json
{
  "id": "tt0134273_59",
  "movie_name": "8MM_1999",
  "imdb_id": "tt0134273",
  "scene_index": 59,
  "slugline": "INT.  TAXI -- DAY",
  "characters": "CAB DRIVER, WELLES",
  "text": "INT.  TAXI -- DAY\nWelles gets in, turning in his seat to watch behind.\nCAB DRIVER: Where to?\n...",
  "similarity_distance": 0.5156
}
```

Claude now has a real, citable scene to ground its feedback in — it can say
"this reads like the taxi pursuit in *8MM*" because that's literally what
came back, not a guess.

## 2. Reading the full match

You ask: *"Show me that whole scene."* Claude calls `get_scene_details` with
the `id` from above:

```json
{
  "id": "tt0134273_59",
  "movie_name": "8MM_1999",
  "slugline": "INT.  TAXI -- DAY",
  "text": "INT.  TAXI -- DAY\nWelles gets in, turning in his seat to watch behind.\nCAB DRIVER: Where to?\nWelles keeps watching, sees the limo pull away and pass.\nWELLES: Follow that limousine. Don't get too close, don't let it get too far away. Just keep with it.\nCAB DRIVER: You kidding?\nWELLES: Nope.\n..."
}
```

## 3. Rewriting toward a specific mood

You ask: *"Make this scene feel more paranoid."* Claude calls
`find_mood_reference_scenes("paranoid")`:

```json
{
  "method": "tag_matched",
  "matched_tag": "paranoid",
  "tag_similarity": 1.0,
  "results": [
    {"movie_name": "8MM_1999", "slugline": "EXT.  QUEENS STREET -- DAY", "mood": "paranoid", "...": "..."},
    {"movie_name": "8MM_1999", "slugline": "EXT.  CHASE MANHATTAN BANK -- DAY", "mood": "paranoid", "...": "..."}
  ]
}
```

`method: "tag_matched"` means `"paranoid"` matched one of the seven precoded
mood tags almost exactly (`tag_similarity: 1.0`), so these results are
filtered precisely to scenes tagged `paranoid` at index time.

Now try a mood that *isn't* one of the seven tags — free text, no match
expected:

**Query:** `"a high-speed car chase through city streets"`

```json
{
  "method": "semantic_fallback",
  "matched_tag": "melancholic",
  "tag_similarity": 0.1527,
  "results": [
    {"movie_name": "8MM_1999", "slugline": "EXT.  MANHATTAN STREETS -- DAY", "mood": "melancholic"},
    {"movie_name": "8MM_1999", "slugline": "EXT.  134 FREEWAY -- DAY", "mood": "melancholic"},
    {"movie_name": "8MM_1999", "slugline": "EXT.  INTERSTATE HIGHWAY -- NIGHT", "mood": "melancholic"}
  ]
}
```

`tag_similarity: 0.15` is far below the match threshold, so `method` flips
to `"semantic_fallback"`: the tag filter is dropped entirely and results
come from raw nearest-neighbor search instead. Notice the results are still
genuinely relevant (highway/street chase scenes) even though their stored
mood tag (`melancholic`) has nothing to do with the query — proof the
fallback searches scene *content*, not mood metadata.

## 4. Checking what's indexed

You ask: *"What movies do you have indexed?"* Claude calls
`list_indexed_movies`:

```json
[
  {"movie_name": "8MM_1999", "imdb_id": "tt0134273"},
  {"movie_name": "The Iron Lady_2011", "imdb_id": "tt1007029"}
]
```

(Against the real published index this will list a couple thousand movies,
not two — this walkthrough used a `--limit 2` local test build; see
`docs/dataset.md`.)

## Try it yourself

```bash
uv run python -m slugline_mcp.indexing.build_index --limit 5 --persist-directory /tmp/demo-index
SLUGLINE_MCP_PERSIST_DIR=/tmp/demo-index uv run mcp dev src/slugline_mcp/server.py:mcp
```

Then call `search_similar_scenes` or `find_mood_reference_scenes` from the
Inspector UI with your own queries — see `docs/testing.md` for details.
