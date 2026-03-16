"""Pinecone vector store implementation."""

import logging
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class PineconeStore(BaseVectorStore):
    """Vector store implementation using Pinecone.

    Pinecone is a managed vector database service, ideal for production
    deployments requiring scalability and reliability.

    Note:
        Requires PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables.
    """

    def __init__(
        self,
        collection_name: str = "default",
        embedding_model: str = "text-embedding-3-small",
        environment: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the Pinecone store.

        Args:
            collection_name: Name of the index to use.
            embedding_model: OpenAI embedding model name.
            environment: Pinecone environment (loaded from env if not provided).
            api_key: Pinecone API key (loaded from env if not provided).
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        self._environment = environment
        self._api_key = api_key
        self._index = None
        self._embeddings = None

    @property
    def collection_name(self) -> str:
        """Return the index name."""
        return self._collection_name

    def _ensure_initialized(self) -> None:
        """Ensure the Pinecone client is initialized."""
        if self._index is not None:
            return

        try:
            import os
            from pinecone import Pinecone

            # Get credentials
            api_key = self._api_key or os.environ.get("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY is required")

            # Initialize client
            pc = Pinecone(api_key=api_key)
            self._index = pc.Index(self._collection_name)

            # Initialize embeddings
            from langchain_openai import OpenAIEmbeddings
            self._embeddings = OpenAIEmbeddings(model=self._embedding_model)

            logger.info(f"Connected to Pinecone index: {self._collection_name}")

        except ImportError:
            raise ImportError(
                "Pinecone requires: pip install pinecone-client langchain-openai"
            )

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

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        if metadatas is None:
            metadatas = [{} for _ in documents]

        try:
            # Generate embeddings
            embeddings = self._embeddings.embed_documents(documents)

            # Prepare vectors
            vectors = [
                (ids[i], embeddings[i], metadatas[i])
                for i in range(len(documents))
            ]

            # Upsert to Pinecone
            self._index.upsert(vectors=vectors)
            logger.info(f"Added {len(documents)} documents to Pinecone")
            return ids

        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {e}")
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
            query_embedding = self._embeddings.embed_query(query)
            results = self._index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                include_values=False,
                filter=filter,
            )

            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "content": match.metadata.get("content", ""),
                    "metadata": match.metadata,
                    "score": match.score,
                    "id": match.id,
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        self._ensure_initialized()
        self._index.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from Pinecone")

    def delete_collection(self) -> None:
        """Delete the entire index.

        Note:
            This deletes the entire Pinecone index, which may affect other users.
        """
        import os
        from pinecone import Pinecone

        api_key = self._api_key or os.environ.get("PINECONE_API_KEY")
        pc = Pinecone(api_key=api_key)
        pc.delete_index(self._collection_name)
        self._index = None
        logger.info(f"Deleted Pinecone index: {self._collection_name}")

    def count(self) -> int:
        """Return the number of vectors in the index."""
        self._ensure_initialized()
        stats = self._index.describe_index_stats()
        return stats.total_vector_count