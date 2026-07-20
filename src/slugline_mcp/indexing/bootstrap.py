"""Fetch a prebuilt reference index on first run.

Most end users of the MCP server should never have to run
``build_index.py`` themselves (it needs the ``index`` extra and takes a
while to embed ~2,200 scripts). Instead, a prebuilt Chroma index is
published to a Hugging Face Hub dataset repo, and this module downloads it
into the local persist directory the first time the server starts and finds
no local index yet.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError

from slugline_mcp.indexing.chroma_client import DEFAULT_PERSIST_DIR

logger = logging.getLogger(__name__)

DEFAULT_INDEX_REPO_ID = "NalluriTanavreddy/slugline-mcp-index"
INDEX_REPO_ID_ENV_VAR = "SLUGLINE_MCP_INDEX_REPO"


def _index_exists(persist_directory: Path) -> bool:
    """Whether a Chroma index already exists at this path."""
    return (persist_directory / "chroma.sqlite3").exists()


def ensure_index(
    persist_directory: Path | str = DEFAULT_PERSIST_DIR,
    repo_id: str | None = None,
) -> Path:
    """Ensure a reference index exists locally, downloading it if not.

    Returns the persist directory. If an index already exists there, this is
    a no-op. Raises ``RuntimeError`` if no local index exists and the
    download fails (e.g. no prebuilt index has been published yet, or the
    machine is offline) -- in that case, run ``build_index.py`` manually.
    """
    persist_directory = Path(persist_directory)
    if _index_exists(persist_directory):
        logger.info("Using existing index at %s", persist_directory)
        return persist_directory

    repo_id = repo_id or os.environ.get(INDEX_REPO_ID_ENV_VAR, DEFAULT_INDEX_REPO_ID)
    logger.info("No local index found. Downloading prebuilt index from %s ...", repo_id)
    persist_directory.mkdir(parents=True, exist_ok=True)

    try:
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=str(persist_directory),
        )
    except HfHubHTTPError as e:
        raise RuntimeError(
            f"Could not download prebuilt index from Hugging Face Hub repo '{repo_id}': {e}\n"
            "If you're developing locally, build the index yourself instead:\n"
            "  uv sync --extra index && uv run python -m slugline_mcp.indexing.build_index"
        ) from e

    if not _index_exists(persist_directory):
        raise RuntimeError(
            f"Downloaded from '{repo_id}' but no chroma.sqlite3 was found -- "
            "the repo may not contain a valid Chroma index."
        )

    logger.info("Downloaded index to %s", persist_directory)
    return persist_directory
