"""FAISS vector store implementation."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class FAISSStore(BaseVectorStore):
    """Vector store implementation using FAISS.

    FAISS (Facebook AI Similarity Search) is a library for efficient
    similarity search and clustering of dense vectors.
    """

    def __init__(
        self,
        collection_name: str = "default",
        embedding_model: str = "text-embedding-3-small",
        index_path: Optional[str] = None,
    ):
        """Initialize the FAISS store.

        Args:
            collection_name: Name for the index.
            embedding_model: OpenAI embedding model name.
            index_path: Path to save/load the index.
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        self._index_path = index_path
        self._vector_store = None
        self._docstore = {}

    @property
    def collection_name(self) -> str:
        """Return the collection name."""
        return self._collection_name

    def _ensure_initialized(self) -> None:
        """Ensure the FAISS store is initialized."""
        if self._vector_store is not None:
            return

        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(model=self._embedding_model)

            if self._index_path and Path(self._index_path).exists():
                self._vector_store = FAISS.load_local(
                    self._index_path,
                    embeddings,
                    self._collection_name,
                )
            else:
                # Initialize with empty store
                self._vector_store = FAISS.from_texts(
                    ["_init_"],
                    embeddings,
                    metadatas=[{"_init": True}],
                )

            logger.info(f"Initialized FAISS store: {self._collection_name}")

        except ImportError:
            raise ImportError(
                "FAISS requires: pip install faiss-cpu langchain-community langchain-openai"
            )

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store."""
        raise NotImplementedError("FAISS store implementation pending")

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a similarity search."""
        raise NotImplementedError("FAISS store implementation pending")

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        raise NotImplementedError("FAISS does not support deletion")

    def delete_collection(self) -> None:
        """Delete the index."""
        self._vector_store = None
        self._docstore = {}
        logger.info(f"Cleared FAISS store: {self._collection_name}")

    def count(self) -> int:
        """Return the number of documents."""
        if self._vector_store is None:
            return 0
        return self._vector_store.index.ntotal