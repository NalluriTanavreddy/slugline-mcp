# slugline-mcp — resume notes

Read `TASKS.md` first — it's the authoritative build checklist (one commit per
task, top to bottom). This file is context to avoid re-deriving decisions
already made. As of this writing: **Phases 0–4 are complete and pushed to
`origin/main`.** Next up is Phase 5 (Packaging).

## Working agreement (from the user)

- One git commit per task in `TASKS.md`, using that task's commit message
  **verbatim**. Check the box in `TASKS.md` and commit that checkbox update
  in the *same* commit as the task's implementation.
- Work through tasks strictly in order, top to bottom.
- **Stop and ask before starting Phase 6 (CI/CD) and Phase 8 (Publish)** —
  both involve secrets / an irreversible public PyPI release.
- If anything is ambiguous or needs a judgment call (versioning, model
  choice, hosting, etc.), stop and ask rather than guessing.
- `git push` after finishing each phase (established during Phase 3/4).
- The user may interject mid-task with new requirements pasted inline. When
  that happens: insert the new task(s) into `TASKS.md` at the position they
  specify, and if the insertion point is *before* where work already is,
  implement it immediately (out of order) before continuing; if it's ahead
  of current progress, just queue it and reach it in normal order.

## Decisions already made (don't re-ask)

- License: MIT. Python: 3.10+. Embedding model:
  `sentence-transformers/all-MiniLM-L6-v2`.
- Prebuilt index hosting: a Hugging Face Hub **dataset repo**, id
  `NalluriTanavreddy/slugline-mcp-index` (default in
  `bootstrap.DEFAULT_INDEX_REPO_ID`, overridable via
  `SLUGLINE_MCP_INDEX_REPO`). **This repo does not exist yet / has nothing
  uploaded to it** — building and publishing the real full-dataset index
  (~2,200 movies) has not happened in any session so far; it's a long batch
  job. `bootstrap.ensure_index()` fails gracefully (returns empty results,
  doesn't crash the server) when it can't be reached, so this isn't blocking
  local dev/testing.
- Mood taxonomy (fixed 7 labels, from `mood_tagging.CANDIDATE_MOODS`):
  paranoid, romantic tension, tense, comedic, dread, melancholic, triumphant.
- GitHub remote already exists and is linked: `NalluriTanavreddy/slugline-mcp`
  (confirmed reachable, currently pushed through Phase 4).

## Architecture in one paragraph

Retrieval-only MCP server (official `mcp` SDK / FastMCP). Reference data is
`rohitsaxena/MovieSum` (HF `datasets`, ~2,200 screenplays, pre-structured
XML). `indexing/parser.py` parses that XML into `Scene` objects;
`indexing/plaintext_scene_splitter.py` is a separate, simpler splitter for a
user's own raw pasted script (added mid-build per user request — different
input format, not reference-data XML). `indexing/build_index.py` parses +
embeds (`indexing/embeddings.py`) + mood-tags (`indexing/mood_tagging.py`,
local zero-shot `facebook/bart-large-mnli`, index-time only, no runtime
cost) every scene and stores it in a local Chroma collection
(`indexing/chroma_client.py`). `retrieval.py`'s `Retriever` is a lazy
singleton wrapping that collection — on first use it calls
`bootstrap.ensure_index()` to fetch a prebuilt index if none exists locally,
and degrades to empty results (never raises) if that fails. Five tools in
`tools/` (thin wrappers around `Retriever`, sharing a canonical response
shape via `tools/_formatting.format_scene`) are registered onto the
`FastMCP` instance in `server.py`.

## Non-obvious bugs already found and fixed (context for why code looks this way)

- **Parenthetical/character parsing** (`parser.py`): MovieSum XML doesn't
  repeat `<character>` when the same speaker continues after a
  `<parenthetical>` — speaker must be "sticky" until the next `<character>`
  tag, and a `<parenthetical>` describes the *following* `<dialogue>`, not
  the preceding one. Caught by the fixture tests; don't revert this.
- **Bootstrap false-positive** (`bootstrap.py::_index_exists`): merely
  instantiating a Chroma `PersistentClient` creates `chroma.sqlite3` on disk
  even with zero collections/documents. Checking only for that file's
  existence would treat a partial/empty index as "already there" and
  permanently skip re-downloading. Fixed to check `collection.count() > 0`.
  Regression-tested in `tests/test_bootstrap.py`.
- **FastMCP does not parse Google-style `Args:` docstrings** into parameter
  descriptions in the generated tool schema — it only reads
  `Annotated[type, Field(description=...)]`. All tool functions use that
  pattern now instead of docstring `Args:` sections for parameters (return
  value docs are still fine as plain docstring prose).

## Useful commands

```bash
# run tests (pytest is a dev dependency group, not a base dependency)
uv run --with pytest pytest tests/ -q

# build a small local test index (fast, for manual smoke-testing)
uv run python -m slugline_mcp.indexing.build_index --limit 2 --persist-directory /tmp/some_dir
SLUGLINE_MCP_PERSIST_DIR=/tmp/some_dir uv run python3 -c "..."   # point the server at it

# needs the `index` extra (datasets, transformers) for anything indexing-related
uv sync --extra index

# interactive tool testing
uv run mcp dev src/slugline_mcp/server.py:mcp
```

## What's left (see TASKS.md for full detail)

- **Phase 5 — Packaging**: console entry point (`project.scripts`), build/twine
  dev deps, versioning scheme, verify `uv pip install -e .` and `uvx
  slugline-mcp run` work.
- **Phase 6 — CI/CD**: ASK FIRST. GitHub Actions build/test + PyPI/TestPyPI
  publish workflows — involves secrets.
- **Phase 7 — Docs & release**: full README usage guide (note: README
  already got a badges/roadmap pass in Phase 4 at the user's request — Phase
  7's task should extend/polish it, not redo it from scratch), CONTRIBUTING,
  demo walkthrough (no recording exists yet), bump to 0.1.0, tag release.
- **Phase 8 — Publish**: ASK FIRST. Build artifacts, TestPyPI, then PyPI —
  irreversible public release.

Also outstanding, not yet on `TASKS.md` because no task was ever specified for
it: **the real prebuilt index has never been built or uploaded** to the HF
Hub repo referenced by `bootstrap.py`. End-to-end testing (`uvx slugline-mcp`
actually returning real results out of the box) will need either that upload
to happen, or a documented manual `build_index.py` run. Flag this to the user
when Phase 5's "verify uvx slugline-mcp run works end-to-end" task comes up.
