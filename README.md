# slugline-mcp

A Model Context Protocol (MCP) server that gives screenwriters brutal, evidence-based script analysis — mood description, next-action suggestions, and "X meets Y" movie comparisons — by retrieving similar scenes from a reference database of real produced screenplays.

slugline-mcp is a retrieval-only server. It does not write or judge anything itself: it parses reference scripts into scenes, embeds them, and exposes semantic search over that index as MCP tools. All analysis and writing is done by the LLM you connect it to (e.g. your own Claude account via a custom connector) — slugline-mcp just supplies the evidence.

## How it works

1. A reference dataset of ~2,200 real movie screenplays ([rohitsaxena/MovieSum](https://huggingface.co/datasets/rohitsaxena/MovieSum)) is parsed into individual scenes and embedded with `sentence-transformers`.
2. Embeddings are stored in a local [Chroma](https://www.trychroma.com/) vector database.
3. The MCP server exposes tools (e.g. `search_similar_scenes`, `get_scene_details`, `list_indexed_movies`) that let a connected LLM query this index directly against scenes from the user's own script.

## Status

Early development. See `TASKS.md` for the build checklist.

## License

MIT — see `LICENSE`.
