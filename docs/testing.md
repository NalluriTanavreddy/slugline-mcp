# Testing locally with the MCP Inspector

The [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is
the standard way to interactively test an MCP server's tools before wiring it
into Claude Desktop or a custom connector. It requires Node.js (it shells out
to `npx`).

From the repo root:

```bash
uv run mcp dev src/slugline_mcp/server.py:mcp
```

This launches the Inspector's web UI (a URL is printed to the terminal). From
there you can:

- See all five registered tools (`get_analysis_style`, `search_similar_scenes`,
  `get_scene_details`, `list_indexed_movies`, `find_mood_reference_scenes`)
  and their input schemas.
- Call any tool directly with sample arguments and inspect the raw response.
- Check server logs/errors in real time.

## Useful things to try

- Call `search_similar_scenes` with a short scene description (e.g. "a
  detective interrogates a nervous suspect in a dim office") and confirm it
  returns ranked matches with `similarity_distance` ascending.
- Call `get_scene_details` with an `id` from a previous `search_similar_scenes`
  result to confirm it returns the same scene's full text.
- Call `list_indexed_movies` with no arguments and confirm it returns every
  movie currently in the index.
- Call `find_mood_reference_scenes` with a mood from `mood_tagging.CANDIDATE_MOODS`
  (e.g. `"paranoid"`) and confirm every result's `mood` field matches.
- Call any tool before an index exists locally (fresh `~/.slugline-mcp`) to
  confirm the server doesn't crash and instead returns empty results.

If you haven't built or downloaded a reference index yet, see
`docs/dataset.md` for how to build one locally with `--limit` for quick
testing.
