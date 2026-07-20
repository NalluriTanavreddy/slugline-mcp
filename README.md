<div align="center">

# 🎬 slugline-mcp

### Brutal, evidence-based screenplay analysis — grounded in real produced scripts.
**Mood, next-action suggestions, and "X meets Y" comparisons, backed by retrieval over ~2,200 real screenplays. One MCP server. Zero vibes-based feedback.**

slugline-mcp doesn't write or judge your scene itself — it retrieves real produced scenes
similar to yours (or matching a mood you're chasing) so *your own* connected Claude can
ground its feedback in evidence instead of guessing.

[![Status](https://img.shields.io/badge/status-pre--release-orange)](TASKS.md)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-server-black)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/NalluriTanavreddy/slugline-mcp?style=flat&color=yellow)](https://github.com/NalluriTanavreddy/slugline-mcp/stargazers)

⭐ Star this repo if you find it useful.

</div>

---

> **Try it once it's runnable end-to-end (see the roadmap below):**
>
> - 📦 **Clone it** — `git clone https://github.com/NalluriTanavreddy/slugline-mcp.git && cd slugline-mcp && uv sync`
> - 🔌 **Add it to Claude Desktop** — see [`docs/claude_desktop.md`](docs/claude_desktop.md) for the config
> - 🎬 **Ask about your scene** — "Find me real scenes similar to this one: [paste a scene]" and Claude
>   answers grounded in actual retrieved screenplay text, not general knowledge

---

## 🎥 Demo

*(Coming soon — a walkthrough recording is planned as part of the docs & release phase.
See the roadmap below.)*

---

## 🎯 What is this?

**slugline-mcp** is an MCP (Model Context Protocol) server for screenwriters. It's a
**retrieval-only** RAG pipeline: it parses a reference database of real movie screenplays
into scenes, embeds them, and exposes semantic search over that index as MCP tools. The
LLM doing the actual writing and judgment is *your own* Claude, connected locally — this
server never calls out to an LLM itself, it just supplies the evidence.

Reference data comes from
[rohitsaxena/MovieSum](https://huggingface.co/datasets/rohitsaxena/MovieSum), a public
Hugging Face dataset of ~2,200 movie screenplays, pre-structured into scenes with
dialogue and stage directions.

---

## ✨ Features

<details open>
<summary><strong>🔍 Evidence Retrieval</strong></summary>

- `search_similar_scenes` — semantic search for real produced scenes structurally or
  tonally similar to a scene you're writing
- `get_scene_details` — fetch the full text and metadata for one indexed scene by id
- `list_indexed_movies` — enumerate every movie currently in the reference index
- `find_mood_reference_scenes` — find scenes that strongly hit a *target* mood (e.g.
  "paranoid"), for when you want to rewrite toward a mood your scene doesn't have yet —
  filtered by a mood tag computed once at indexing time, not guessed at query time

</details>

<details open>
<summary><strong>🗣️ Analysis Guidance</strong></summary>

- `get_analysis_style` — instructs the connected LLM to be direct rather than
  encouraging, to gather evidence before writing anything, and to structure its
  feedback around mood, next action, and an "X meets Y" comparison — each one cited
  against specific retrieved scenes

</details>

<details>
<summary><strong>⚙️ Under the Hood</strong></summary>

- MovieSum's screenplay XML is parsed into structured `Scene` objects (slugline, action
  lines, dialogue, parentheticals); a separate plain-text splitter handles a user's own
  pasted script, which has no such structure
- Every reference scene is run once through a local, free zero-shot classifier
  (`facebook/bart-large-mnli`) at indexing time to tag its dominant mood — no per-query
  cost, no external API
- Embeddings use `sentence-transformers/all-MiniLM-L6-v2`, stored in a local
  [Chroma](https://www.trychroma.com/) index
- End users never build the index themselves: a `bootstrap` module downloads a prebuilt
  index from a Hugging Face Hub dataset repo on first run, falling back to clear "no
  index available" behavior (never a crash) if that fails

</details>

---

## 🧰 Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.10+ |
| MCP framework | Official `mcp` Python SDK (FastMCP) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector database | [Chroma](https://www.trychroma.com/) (persistent, local) |
| Mood classification | Local zero-shot `transformers` pipeline (`facebook/bart-large-mnli`), index-time only |
| Reference dataset | [rohitsaxena/MovieSum](https://huggingface.co/datasets/rohitsaxena/MovieSum) (~2,200 screenplays) |
| Prebuilt index hosting | Hugging Face Hub dataset repo, via `huggingface-hub` |
| Build backend | Hatchling (`src` layout) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Testing | pytest |

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Install

**From PyPI:** not yet published — see the roadmap below (Phase 8).

**From source (works today):**

```bash
git clone https://github.com/NalluriTanavreddy/slugline-mcp.git
cd slugline-mcp
uv sync
```

### Run the server

```bash
uv run python -m slugline_mcp
```

### Add it to Claude Desktop

See [`docs/claude_desktop.md`](docs/claude_desktop.md) for the full config example (dev
mode today; a simpler `uvx slugline-mcp` config once published).

### Build or fetch a reference index

The server needs a populated Chroma index to retrieve from. See
[`docs/dataset.md`](docs/dataset.md) for building one locally from MovieSum, and
`src/slugline_mcp/indexing/bootstrap.py` for how published builds will fetch a prebuilt
one automatically.

### Development setup

```bash
uv sync --extra index  # adds datasets + transformers, needed only for indexing
uv run --with pytest pytest tests/
```

See [`docs/testing.md`](docs/testing.md) for testing tools interactively with the MCP
Inspector.

---

## 🗂️ Project Structure

```
src/slugline_mcp/
├── server.py                       # FastMCP instance, tool registration
├── __main__.py                     # `python -m slugline_mcp` entry point
├── config.py                       # env var loading
├── retrieval.py                    # Chroma-backed retrieval (search, get, mood filter)
├── tools/
│   ├── search_similar_scenes.py
│   ├── get_scene_details.py
│   ├── list_indexed_movies.py
│   ├── get_analysis_style.py
│   ├── find_mood_reference_scenes.py
│   └── _formatting.py              # shared scene response shape
└── indexing/
    ├── parser.py                   # MovieSum XML -> Scene objects
    ├── plaintext_scene_splitter.py # raw pasted scripts -> scenes
    ├── embeddings.py                # sentence-transformers wrapper
    ├── mood_tagging.py              # local zero-shot mood classifier
    ├── chroma_client.py             # Chroma persistent client/collection
    ├── build_index.py               # maintainer script: parse + embed + tag + store
    └── bootstrap.py                 # download prebuilt index from HF Hub

tests/    # pytest suite, one file per tool/module
docs/     # dataset, MCP Inspector testing, Claude Desktop config
```

---

## 🗺️ Roadmap

- [x] **Phase 0** — Repo setup: README, license, `pyproject.toml`, package structure
- [x] **Phase 1** — Indexing pipeline: MovieSum XML parser, plain-text splitter,
      embeddings, Chroma, `build_index`, local mood tagging, HF Hub bootstrap
- [x] **Phase 2** — MCP server core: FastMCP scaffold, entry point, config, retrieval logic
- [x] **Phase 3** — Tools: all five tools implemented, registered, and tested
- [x] **Phase 4** — Local testing: MCP Inspector docs, schema fixes, graceful empty
      results, Claude Desktop config, this README
- [ ] **Phase 5** — Packaging: console entry point, versioning, `uvx` support
- [ ] **Phase 6** — CI/CD: GitHub Actions build/test + PyPI publish workflows
- [ ] **Phase 7** — Docs & release: full usage guide, CONTRIBUTING, demo walkthrough, v0.1.0
- [ ] **Phase 8** — Publish: TestPyPI, then PyPI

See [`TASKS.md`](TASKS.md) for the full task-by-task build checklist.

---

## 📄 License

MIT — see [LICENSE](LICENSE).

## 👤 Author

Built by [NalluriTanavreddy](https://github.com/NalluriTanavreddy).
