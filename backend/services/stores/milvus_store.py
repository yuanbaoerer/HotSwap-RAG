"""Milvus vector store implementation."""

import logging
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class MilvusStore(BaseVectorStore):
    """Vector store implementation using Milvus.

    Milvus is an open-source vector database built for scalable similarity
    search and AI applications.
    """

    def __init__(
        self,
        collection_name: str = "default",
        embedding_model: str = "text-embedding-3-small",
        host: str = "localhost",
        port: int = 19530,
    ):
        """Initialize the Milvus store.

        Args:
            collection_name: Name of the collection to use.
            embedding_model: OpenAI embedding model name.
            host: Milvus server host.
            port: Milvus server port.
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        self._host = host
        self._port = port
        self._collection = None
        self._embeddings = None

    @property
    def collection_name(self) -> str:
        """Return the collection name."""
        return self._collection_name

    def _ensure_initialized(self) -> None:
        """Ensure Milvus connection is established."""
        if self._collection is not None:
            return

        try:
            from pymilvus import Collection, connections
            from langchain_openai import OpenAIEmbeddings

            connections.connect(
                alias="default",
                host=self._host,
                port=self._port,
            )

            self._collection = Collection(self._collection_name)
            self._embeddings = OpenAIEmbeddings(model=self._embedding_model)

            logger.info(f"Connected to Milvus collection: {self._collection_name}")

        except ImportError:
            raise ImportError(
                "Milvus requires: pip install pymilvus langchain-openai"
            )

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store."""
        raise NotImplementedError("Milvus store implementation pending")

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a similarity search."""
        raise NotImplementedError("Milvus store implementation pending")

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        raise NotImplementedError("Milvus store implementation pending")

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        raise NotImplementedError("Milvus store implementation pending")

    def count(self) -> int:
        """Return the number of documents in the collection."""
        self._ensure_initialized()
        return self._collection.num_entities