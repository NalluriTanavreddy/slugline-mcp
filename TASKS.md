# slugline-mcp — Build Tasks

Work through these in order, one commit per task. Each task = one commit.

## Phase 0 — Repo setup
- [x] `chore: initial commit — README, LICENSE`
- [x] `chore: add .gitignore`
- [x] `chore: scaffold pyproject.toml (package: slugline-mcp)`
- [x] `chore: create package folder structure`

## Phase 1 — Indexing pipeline
- [x] `feat: add MovieSum XML parser for splitting scripts into scenes`
- [x] `feat: add plain-text scene splitter for user-submitted scripts`
- [x] `test: add sample script fixtures for scene parser`
- [x] `feat: add embedding module (sentence-transformers)`
- [x] `feat: add Chroma client setup`
- [x] `feat: add build_index script (loads rohitsaxena/MovieSum)`
- [x] `docs: add instructions for downloading reference dataset (rohitsaxena/MovieSum)`
- [x] `feat: add bootstrap module to fetch prebuilt index on first run`
- [x] `chore: exclude generated db files from git`

## Phase 2 — MCP server core
- [x] `feat: scaffold MCP server`
- [x] `feat: add __main__ entry point`
- [x] `feat: wire up config/env var loading`
- [ ] `feat: add vector retrieval logic`

## Phase 3 — Tools
- [ ] `feat: add search_similar_scenes tool`
- [ ] `test: add tests for search_similar_scenes`
- [ ] `feat: add get_scene_details tool`
- [ ] `test: add tests for get_scene_details`
- [ ] `feat: add list_indexed_movies tool`
- [ ] `test: add tests for list_indexed_movies`
- [ ] `feat: add get_analysis_style tool for brutal-tone instructions`
- [ ] `test: add tests for get_analysis_style`
- [ ] `feat: register all tools in server`
- [ ] `refactor: clean up tool response formatting`

## Phase 4 — Local testing
- [ ] `docs: add MCP inspector testing instructions`
- [ ] `fix: correct tool schema validation errors`
- [ ] `fix: handle empty retrieval results gracefully`
- [ ] `docs: add Claude Desktop config example`

## Phase 5 — Packaging
- [ ] `chore: add project.scripts entry point (slugline-mcp)`
- [ ] `chore: add build and twine as dev dependencies`
- [ ] `chore: set up versioning scheme`
- [ ] `test: verify local install via uv pip install -e .`
- [ ] `test: verify uvx slugline-mcp run works end-to-end`

## Phase 6 — CI/CD
- [ ] `ci: add GitHub Actions build + test workflow`
- [ ] `ci: add GitHub Actions PyPI publish workflow`
- [ ] `ci: add TestPyPI publish step for pre-release validation`

## Phase 7 — Docs & release
- [ ] `docs: write full README usage guide`
- [ ] `docs: add CONTRIBUTING.md`
- [ ] `docs: add demo walkthrough`
- [ ] `chore: bump version to 0.1.0`
- [ ] `chore: tag v0.1.0 release`

## Phase 8 — Publish
- [ ] `chore: build distribution artifacts`
- [ ] `chore: publish slugline-mcp to TestPyPI and verify install`
- [ ] `chore: publish slugline-mcp to PyPI`
