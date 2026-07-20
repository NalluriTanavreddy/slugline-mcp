"""Chroma vector database client setup.

The index lives on disk as a Chroma persistent collection, both when building
it from the reference dataset and when the MCP server queries it at runtime.
The default location is a per-user data directory so a `uvx`-installed server
has somewhere writable to keep (or download) its index without touching the
package installation itself.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

DEFAULT_PERSIST_DIR = Path.home() / ".slugline-mcp" / "chroma"
SCENES_COLLECTION_NAME = "scenes"


def get_chroma_client(persist_directory: Path | str = DEFAULT_PERSIST_DIR) -> chromadb.ClientAPI:
    """Return a persistent Chroma client rooted at ``persist_directory``."""
    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_directory))


def get_scenes_collection(
    client: chromadb.ClientAPI, name: str = SCENES_COLLECTION_NAME
) -> Collection:
    """Get or create the collection that stores embedded reference scenes."""
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
