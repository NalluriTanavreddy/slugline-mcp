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
- [x] `feat: add one-time mood tagging step during indexing (local zero-shot classifier, stores mood metadata per scene)`
- [x] `docs: add instructions for downloading reference dataset (rohitsaxena/MovieSum)`
- [x] `feat: add bootstrap module to fetch prebuilt index on first run`
- [x] `chore: exclude generated db files from git`

## Phase 2 — MCP server core
- [x] `feat: scaffold MCP server`
- [x] `feat: add __main__ entry point`
- [x] `feat: wire up config/env var loading`
- [x] `feat: add vector retrieval logic`

## Phase 3 — Tools
- [x] `feat: add search_similar_scenes tool`
- [x] `test: add tests for search_similar_scenes`
- [x] `feat: add get_scene_details tool`
- [x] `test: add tests for get_scene_details`
- [x] `feat: add list_indexed_movies tool`
- [x] `test: add tests for list_indexed_movies`
- [x] `feat: add get_analysis_style tool for brutal-tone instructions`
- [x] `test: add tests for get_analysis_style`
- [x] `feat: add find_mood_reference_scenes tool`
- [x] `test: add tests for find_mood_reference_scenes`
- [x] `refactor: hybrid tag-match + semantic-fallback search for find_mood_reference_scenes`
- [x] `test: cover tag-match and semantic-fallback paths for find_mood_reference_scenes`
- [x] `feat: register all tools in server`
- [x] `refactor: clean up tool response formatting`

## Phase 4 — Local testing
- [x] `docs: add MCP inspector testing instructions`
- [x] `fix: correct tool schema validation errors`
- [x] `fix: handle empty retrieval results gracefully`
- [x] `docs: add Claude Desktop config example`
- [x] `docs: give README a proper badges/features/roadmap treatment`

## Phase 5 — Packaging
- [x] `chore: add project.scripts entry point (slugline-mcp)`
- [x] `chore: add build and twine as dev dependencies`
- [x] `chore: set up versioning scheme`
- [x] `test: verify local install via uv pip install -e .`
- [x] `test: verify uvx slugline-mcp run works end-to-end`

## Phase 6 — CI/CD
- [x] `ci: add GitHub Actions build + test workflow`
- [x] `ci: add GitHub Actions PyPI publish workflow`
- [x] `ci: add TestPyPI publish step for pre-release validation`

## Phase 7 — Docs & release
- [x] `docs: write full README usage guide`
- [ ] `docs: add CONTRIBUTING.md`
- [ ] `docs: add demo walkthrough`
- [ ] `chore: bump version to 0.1.0`
- [ ] `chore: tag v0.1.0 release`

## Phase 8 — Publish
- [ ] `chore: build distribution artifacts`
- [ ] `chore: publish slugline-mcp to TestPyPI and verify install`
- [ ] `chore: publish slugline-mcp to PyPI`
- [ ] `feat: rotate PyPI/TestPyPI tokens to project-scoped after first successful publish`
