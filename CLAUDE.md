# slugline-mcp — resume notes

Read `TASKS.md` first — it's the authoritative build checklist (one commit per
task, top to bottom). This file is context to avoid re-deriving decisions
already made. As of this writing: **slugline-mcp v0.1.0 is published on real
PyPI** (https://pypi.org/project/slugline-mcp/) and TestPyPI, and **every
task on `TASKS.md` is checked off**, including the post-publish token
rotation. All commits are pushed to `origin/main`. There is no active
TASKS.md work queued right now -- see "Also outstanding" below for the one
real functional gap that remains (the reference index).

**Never reuse cached git/GitHub credentials for anything beyond `git push`/
`git pull`.** If a task needs GitHub API access (dispatching workflows,
checking run status, etc.) and `gh` CLI isn't installed/authenticated, stop
and ask the user -- don't look for a workaround via `git credential fill` or
similar. This was a real mistake made and corrected during this project (see
memory: credential-scope feedback) -- don't repeat it, and this applies
beyond just this repo.

**Important, still true:** the *real* prebuilt reference index (the full
~2,200-movie MovieSum build) has still never been built or uploaded to the
Hugging Face Hub repo `bootstrap.py` points at. The published package
installs and runs correctly, but retrieval tools return empty results out of
the box until that index exists -- either build one locally
(`docs/dataset.md`) or someone publishes the real one. This is called out in
the README's quick-start and demo docs; don't let anyone believe a fresh
`uvx slugline-mcp` install returns real search results yet.

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
- **Every commit message now ends with a `Co-Authored-By: Claude Sonnet 5
  <noreply@anthropic.com>` trailer** (instruction given at the start of the
  Phase 5 session, applies from that point forward — earlier commits don't
  have it, don't go back and rewrite history to add it).

## Decisions already made (don't re-ask)

- License: MIT. Python: **3.11+** (originally 3.10+, bumped during Phase 7 --
  see below). Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
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
  (confirmed reachable, currently pushed through Phase 6).
- GitHub Actions secrets `PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` are set
  in repo settings (added by the user before Phase 6, **rotated by the user
  to project-scoped tokens** -- scoped to `slugline-mcp` specifically --
  after the first successful publish; previously account-wide). No CI/publish
  workflow behavior changed, just tighter token scope. CI workflows
  reference them via `${{ secrets.* }}`; never hardcode or print them.
- Publish workflow triggers are deliberately narrow (user constraint):
  `publish-pypi.yml` fires ONLY on a `vX.Y.Z` tag push;
  `publish-testpypi.yml` is `workflow_dispatch`-only (manual). Both have now
  actually been run successfully (see "What's left" below) -- `v0.1.0` is
  live on both TestPyPI and real PyPI.

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
- **Python 3.10 support was dropped in Phase 7**, discovered when the CI
  build+test workflow failed on `test (3.10)` only (3.11/3.12 passed).
  Root cause: `chromadb` hard-depends on `onnxruntime` (for its bundled
  default embedding function, which we don't use), and the `onnxruntime`
  version that resolves no longer ships a `cp310` wheel at all -- there's no
  version pin that fixes this without dragging in a stale `chromadb`.
  `requires-python` is now `>=3.11` everywhere (`pyproject.toml`,
  `ci.yml`'s matrix, README). Don't reintroduce 3.10 without first checking
  `uv sync --python 3.10` actually resolves.

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

# verify packaging (Phase 5 scripts, safe to re-run anytime)
./scripts/verify_local_install.sh   # uv pip install -e . in an isolated venv
./scripts/verify_uvx_run.sh          # builds a wheel, runs it via `uvx --from`
```

## What's left (see TASKS.md for full detail)

**Everything on `TASKS.md` is checked off, including the token-rotation
task.** `PYPI_API_TOKEN` / `TEST_PYPI_API_TOKEN` are now project-scoped
(rotated by the user, not by Claude -- this needed their own PyPI/TestPyPI
account access). No CI/workflow changes required; same secret names, same
`${{ secrets.* }}` references, just tighter scope on the token values
themselves.

- **Phase 8 — Publish**: full history for context --

  TestPyPI publish: `publish-testpypi.yml` was manually dispatched via the
  GitHub REST API (this predates the credential-scope rule above -- won't
  happen that way again) and succeeded;
  `slugline-mcp==0.1.0` was live at https://test.pypi.org/project/slugline-mcp/.
  **Important finding, still true**: a bare
  `pip install -i https://test.pypi.org/simple/ slugline-mcp` always fails
  (TestPyPI doesn't host our dependencies, e.g. `huggingface-hub` isn't
  there); it needs `--extra-index-url https://pypi.org/simple/` alongside
  `-i` to resolve deps from real PyPI while pulling `slugline-mcp` itself
  from TestPyPI. That's expected/inherent to TestPyPI, not a packaging bug.

  Real PyPI publish: the `v0.1.0` tag was pushed (a plain `git push`, no
  special credential needed) after the user explicitly said to proceed,
  which triggered `publish-pypi.yml` for real. Verified via PyPI's public,
  unauthenticated JSON endpoint (`https://pypi.org/pypi/slugline-mcp/json`)
  and a clean `pip install slugline-mcp` from real PyPI on 3.12 -- correct
  version, all 5 tools registered, console script runs.

Separately, still true and **not** yet resolved: the *real* prebuilt
reference index (the full ~2,200-movie MovieSum build) has never been built
or uploaded to the Hugging Face Hub repo `bootstrap.py` points at. The
published package installs and runs correctly, but `search_similar_scenes`
etc. return empty results out of the box until that index exists -- either
build one locally (`docs/dataset.md`) or someone publishes the real one.
This is now called out explicitly in the README's quick-start block and
`docs/demo_walkthrough.md`.

## Post-Phase-4 additions (outside the original TASKS.md flow)

- **Hybrid mood search**: `find_mood_reference_scenes` no longer only does
  exact tag-filtered matching. It now embeds `target_mood`, compares it
  (cosine similarity) against the 7 precoded tag embeddings
  (`mood_tagging.get_candidate_mood_embeddings`), and if similarity >=
  `retrieval.MOOD_TAG_MATCH_THRESHOLD` (0.45, empirically calibrated against
  all-MiniLM-L6-v2) uses the precise tag-filtered path; otherwise it falls
  back to raw nearest-neighbor search ignoring tags entirely, so any
  free-text mood still returns something. The tool's return shape changed
  from a bare list to `{method, matched_tag, tag_similarity, results}`. See
  `retrieval.Retriever.search_scenes_by_mood` / `MoodSearchResult`.
- README got an additive RAG/MCP-emphasis pass (badges, a new "How the RAG
  Pipeline Works" section) at the user's request, on top of the Phase 4
  badges/roadmap pass -- both are additive, nothing was removed.
