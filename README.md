<div align="center">

# 🎬 slugline-mcp

### Brutal, evidence-based screenplay analysis — grounded in real produced scripts.
**Mood, next-action suggestions, and "X meets Y" comparisons, backed by retrieval over ~2,200 real screenplays. One MCP server. Zero vibes-based feedback.**

**Under the hood: a full Retrieval-Augmented Generation (RAG) pipeline — chunking, vector
embeddings, semantic search, and local zero-shot classification — exposed entirely as
Model Context Protocol (MCP) tools, with zero LLM calls from the server itself.**

slugline-mcp doesn't write or judge your scene itself — it retrieves real produced scenes
similar to yours (or matching a mood you're chasing) so *your own* connected Claude can
ground its feedback in evidence instead of guessing. It's the *retrieval* half of RAG,
full stop: parse, embed, index, and semantically search real screenplays, then hand that
grounded evidence to Claude over MCP.

[![Status](https://img.shields.io/badge/status-pre--release-orange)](TASKS.md)
[![Architecture](https://img.shields.io/badge/architecture-RAG_pipeline-8a2be2)](#-how-the-rag-pipeline-works)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
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

Two engineering ideas this project is built around:

- **RAG, done properly**: real chunking (screenplay scenes, not arbitrary token
  windows), a purpose-fit embedding model, a persistent vector store, and metadata
  filtering (mood tags computed once at index time) layered on top of semantic
  similarity — not just "stuff everything into a prompt."
- **MCP, done properly**: five tools with schemas an LLM can actually reason about
  (`Annotated[..., Field(description=...)]` throughout `tools/`), including a dedicated
  `get_analysis_style` tool whose whole job is steering *how* the calling LLM uses the
  other four — prompt engineering expressed as a callable tool, not a static system prompt.

Reference data comes from
[rohitsaxena/MovieSum](https://huggingface.co/datasets/rohitsaxena/MovieSum), a public
Hugging Face dataset of ~2,200 movie screenplays, pre-structured into scenes with
dialogue and stage directions.

---

## 🧠 How the RAG Pipeline Works

**Index time** (once, offline, in `indexing/build_index.py`):

1. **Parse** — MovieSum's screenplay XML (or a user's raw pasted script, via a separate
   plain-text splitter) is split into scenes, not arbitrary chunks — a scene is the
   natural retrieval unit for screenplay feedback.
2. **Embed** — each scene's flattened text is encoded with
   `sentence-transformers/all-MiniLM-L6-v2` into a 384-dim vector.
3. **Classify** — each scene is also run once through a local zero-shot classifier
   (`facebook/bart-large-mnli`) against a fixed mood taxonomy, so mood becomes a stored
   metadata field instead of something re-inferred on every query.
4. **Store** — vectors + text + metadata land in a persistent
   [Chroma](https://www.trychroma.com/) collection.

**Query time** (every MCP tool call, in `retrieval.py`):

1. The incoming query (a scene, or a target mood) is embedded with the same model.
2. Chroma runs approximate nearest-neighbor search over the stored vectors — optionally
   pre-filtered by metadata (e.g. `mood == "paranoid"`) before ranking by similarity.
3. Results are formatted into a canonical scene shape and returned as MCP tool output —
   raw evidence, not a generated answer.

Retrieval and generation are fully decoupled here: this server only ever does the
retrieval half, and the MCP tool boundary is exactly where that handoff happens.

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
  a hybrid search: free-text moods close to a precoded tag get precise tag-filtered
  results, anything else falls back to raw semantic search, with the method used
  reported back for transparency

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
| Architecture pattern | RAG (retrieval-augmented generation), exposed entirely as MCP tools |
| Language | Python 3.11+ |
| MCP framework | Official `mcp` Python SDK (FastMCP) |
| Embeddings / vector search | sentence-transformers (`all-MiniLM-L6-v2`) + Chroma ANN search |
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

- Python 3.11+
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

## 📖 Usage

Once slugline-mcp is connected (see [Add it to Claude Desktop](#add-it-to-claude-desktop)
above), just talk to Claude normally — paste a scene, describe what you're stuck on, or ask
for a comparison. Claude decides which tools to call; you never call them directly.

### Typical workflow

1. **Paste a scene and ask for feedback.** Claude calls `get_analysis_style` first (it's
   designed to steer the whole interaction), then `search_similar_scenes` with your scene's
   text to pull real comparable scenes from the reference index.
2. **Claude cites specific movies and scenes**, not vague genre talk — if it says "this reads
   like a beat from *8MM*," that's because `search_similar_scenes` actually returned that scene.
3. **Ask to see the full match.** "Show me that whole scene" prompts Claude to call
   `get_scene_details` with the id from the earlier search result.
4. **Ask for a mood rewrite.** "Make this scene feel more paranoid" prompts
   `find_mood_reference_scenes("paranoid")` — Claude gets back real scenes that strongly hit
   that mood, plus whether the match was precise (`tag_matched`) or a broader semantic guess
   (`semantic_fallback`).
5. **Ask what's in the reference set.** "What movies do you have indexed?" calls
   `list_indexed_movies`.

### Example prompts

| You ask Claude... | Tool(s) it calls |
|---|---|
| "Here's my opening scene — what does this actually read like?" | `get_analysis_style`, `search_similar_scenes` |
| "Show me the full text of that Iron Lady scene you mentioned" | `get_scene_details` |
| "I want this argument to feel more like dread building, not just tense" | `find_mood_reference_scenes` |
| "What films are actually in your reference database?" | `list_indexed_movies` |
| "Give me an 'X meets Y' comparison for this whole script" | `get_analysis_style`, `search_similar_scenes` (called repeatedly across scenes) |

### Tools reference

| Tool | Purpose | Key parameters |
|---|---|---|
| `get_analysis_style` | Tone/structure instructions for the calling LLM | none |
| `search_similar_scenes` | Semantic search for structurally/tonally similar produced scenes | `query` (scene text), `n_results` |
| `get_scene_details` | Full text + metadata for one scene by id | `scene_id` |
| `list_indexed_movies` | Every movie currently in the index | none |
| `find_mood_reference_scenes` | Scenes that strongly hit a target mood, hybrid tag/semantic search | `target_mood`, `top_k` |

### If retrieval comes back empty

Every tool degrades gracefully instead of erroring if no reference index is available yet
(see `retrieval.py`) — you'll get empty results rather than a crash. If that happens:

- Confirm a Chroma index exists at `~/.slugline-mcp/chroma` (or wherever
  `SLUGLINE_MCP_PERSIST_DIR` points).
- If not, either wait for `bootstrap.py` to fetch the prebuilt index, or build one yourself
  (see [`docs/dataset.md`](docs/dataset.md)).

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
- [x] **Phase 5** — Packaging: console entry point, versioning, `uvx` support
- [x] **Phase 6** — CI/CD: GitHub Actions build/test + PyPI publish workflows
- [ ] **Phase 7** — Docs & release: full usage guide, CONTRIBUTING, demo walkthrough, v0.1.0
- [ ] **Phase 8** — Publish: TestPyPI, then PyPI

See [`TASKS.md`](TASKS.md) for the full task-by-task build checklist.

---

## 📄 License

MIT — see [LICENSE](LICENSE).

## 👤 Author

Built by [NalluriTanavreddy](https://github.com/NalluriTanavreddy).
