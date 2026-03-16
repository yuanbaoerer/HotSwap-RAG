"""ChromaDB vector store implementation."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class ChromaDBStore(BaseVectorStore):
    """Vector store implementation using ChromaDB.

    ChromaDB is a local, open-source vector database that's perfect for
    development and small-scale production use.

    Attributes:
        persist_directory: Directory to persist the database.
        embedding_model: Name of the embedding model to use.
    """

    def __init__(
        self,
        collection_name: str = "default",
        persist_directory: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
    ):
        """Initialize the ChromaDB store.

        Args:
            collection_name: Name of the collection to use.
            persist_directory: Directory to persist data (default: in-memory).
            embedding_model: OpenAI embedding model name.
        """
        self._collection_name = collection_name
        self._persist_directory = persist_directory
        self._embedding_model = embedding_model
        self._client = None
        self._collection = None
        self._embedding_function = None

    @property
    def collection_name(self) -> str:
        """Return the collection name."""
        return self._collection_name

    def _ensure_initialized(self) -> None:
        """Ensure the client and collection are initialized."""
        if self._collection is not None:
            return

        try:
            import chromadb
            from chromadb.utils import embedding_functions

            # Initialize client
            if self._persist_directory:
                self._client = chromadb.PersistentClient(
                    path=self._persist_directory
                )
            else:
                self._client = chromadb.Client()

            # Initialize embedding function
            self._embedding_function = (
                embedding_functions.OpenAIEmbeddingFunction(
                    api_key=self._get_openai_api_key(),
                    model_name=self._embedding_model,
                )
            )

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_function,
            )

            logger.info(f"Initialized ChromaDB collection: {self._collection_name}")

        except ImportError:
            raise ImportError(
                "ChromaDB is required. Install with: pip install chromadb"
            )

    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        import os

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for embeddings"
            )
        return api_key

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store."""
        self._ensure_initialized()

        if not documents:
            raise ValueError("Documents list cannot be empty")

        # Generate IDs if not provided
        if ids is None:
            import uuid

            ids = [str(uuid.uuid4()) for _ in documents]

        # Create empty metadata if not provided
        if metadatas is None:
            metadatas = [{} for _ in documents]

        try:
            self._collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(f"Added {len(documents)} documents to collection")
            return ids

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a similarity search."""
        self._ensure_initialized()

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=k,
                where=filter,
            )

            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": 1 - results["distances"][0][i] if results["distances"] else None,
                        "id": results["ids"][0][i] if results["ids"] else None,
                    }
                    formatted_results.append(result)

            logger.debug(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        self._ensure_initialized()

        try:
            self._collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        if self._client and self._collection:
            try:
                self._client.delete_collection(self._collection_name)
                self._collection = None
                logger.info(f"Deleted collection: {self._collection_name}")
            except Exception as e:
                logger.error(f"Failed to delete collection: {e}")
                raise

    def count(self) -> int:
        """Return the number of documents in the collection."""
        self._ensure_initialized()
        return self._collection.count()