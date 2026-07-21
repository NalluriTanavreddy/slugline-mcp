# Contributing to slugline-mcp

Thanks for considering a contribution. This is a small, focused project —
most contributions will fall into one of: fixing a retrieval/parsing bug,
adding an MCP tool, or improving docs.

## Development setup

```bash
git clone https://github.com/NalluriTanavreddy/slugline-mcp.git
cd slugline-mcp
uv sync                # base dependencies
uv sync --extra index  # only needed if you're touching indexing/build_index.py
```

## Running tests

```bash
uv run pytest tests/ -q
```

Tests use a small synthetic in-memory index (see `tests/conftest.py`), not
the real MovieSum dataset, so they run fast and don't need network access
beyond downloading the embedding model on first run (cached after that).

## Testing tools interactively

```bash
uv run mcp dev src/slugline_mcp/server.py:mcp
```

See [`docs/testing.md`](docs/testing.md) for details, and
[`docs/dataset.md`](docs/dataset.md) if you need to build a local reference
index to test against real data.

## Adding a new MCP tool

The existing five tools in `src/slugline_mcp/tools/` follow a consistent
shape — new tools should too:

1. Add `src/slugline_mcp/tools/your_tool.py` with a single function. Use
   `Annotated[type, Field(description=...)]` for every parameter — FastMCP
   does **not** parse Google-style `Args:` docstrings into the tool schema,
   only `Field(description=...)` shows up there.
2. If it returns scenes, reuse `tools/_formatting.format_scene` for the
   canonical response shape instead of building result dicts by hand.
3. Add `mcp.add_tool(your_tool)` in `server.py`.
4. Add `tests/test_your_tool.py`. Reuse the `populated_retriever` /
   `unavailable_retriever` fixtures from `conftest.py` rather than hitting
   a real index — see any existing `tests/test_*.py` for the pattern.
5. Make sure it degrades gracefully (empty results, not an exception) when
   the reference index is unavailable, consistent with every other tool.

## Code style

- No comments explaining *what* code does — names should make that clear.
  Comments are for non-obvious *why* (a workaround, a calibrated constant,
  a subtle invariant) — see `retrieval.py`'s `MOOD_TAG_MATCH_THRESHOLD` for
  an example of the kind of comment that's worth keeping.
- Prefer small, focused functions/modules over centralizing logic — the
  existing `tools/` and `indexing/` layouts are the pattern to follow.
- No linter/formatter is enforced yet; match the style of the file you're
  editing.

## Commit messages

Keep them short and specific about *why*, not just *what*. Look at recent
`git log` output for the house style before opening a PR.

## Reporting issues

Open a GitHub issue with what you tried, what you expected, and what
actually happened. If it's a retrieval-quality issue (bad matches, wrong
mood tags), include the exact query text — embedding-based results are
sensitive to exact wording.
