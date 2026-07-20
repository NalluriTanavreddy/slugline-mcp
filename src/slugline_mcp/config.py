"""Central config/env var loading for the MCP server.

Every setting has a sensible local-first default (no external services
required to get something running), overridable via environment variables
for anyone customizing where the index lives or which embedding model to use.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from slugline_mcp.indexing.bootstrap import DEFAULT_INDEX_REPO_ID, INDEX_REPO_ID_ENV_VAR
from slugline_mcp.indexing.chroma_client import DEFAULT_PERSIST_DIR, SCENES_COLLECTION_NAME
from slugline_mcp.indexing.embeddings import DEFAULT_MODEL_NAME

PERSIST_DIR_ENV_VAR = "SLUGLINE_MCP_PERSIST_DIR"
EMBEDDING_MODEL_ENV_VAR = "SLUGLINE_MCP_EMBEDDING_MODEL"
LOG_LEVEL_ENV_VAR = "SLUGLINE_MCP_LOG_LEVEL"


@dataclass(frozen=True)
class Config:
    persist_directory: Path
    collection_name: str
    embedding_model: str
    index_repo_id: str
    log_level: str


def load_config() -> Config:
    return Config(
        persist_directory=Path(os.environ.get(PERSIST_DIR_ENV_VAR, str(DEFAULT_PERSIST_DIR))),
        collection_name=SCENES_COLLECTION_NAME,
        embedding_model=os.environ.get(EMBEDDING_MODEL_ENV_VAR, DEFAULT_MODEL_NAME),
        index_repo_id=os.environ.get(INDEX_REPO_ID_ENV_VAR, DEFAULT_INDEX_REPO_ID),
        log_level=os.environ.get(LOG_LEVEL_ENV_VAR, "INFO"),
    )
