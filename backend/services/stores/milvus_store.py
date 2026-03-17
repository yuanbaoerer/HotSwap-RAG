"""Milvus vector store implementation."""

import logging
import uuid
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class MilvusStore(BaseVectorStore):
    """Vector store implementation using Milvus.

    Milvus is an open-source vector database built for scalable similarity
    search and AI applications.

    Attributes:
        collection_name: Name of the collection.
        embedding_model: Name of the embedding model.
        host: Milvus server host.
        port: Milvus server port.
    """

    # Default embedding dimension for OpenAI text-embedding-3-small
    DEFAULT_DIMENSION = 1536

    def __init__(
        self,
        collection_name: str = "default",
        embedding_model: str = "text-embedding-3-small",
        host: str = "localhost",
        port: int = 19530,
        dimension: int = DEFAULT_DIMENSION,
    ):
        """Initialize the Milvus store.

        Args:
            collection_name: Name of the collection to use.
            embedding_model: OpenAI embedding model name.
            host: Milvus server host.
            port: Milvus server port.
            dimension: Embedding dimension.
        """
        self._collection_name = collection_name
        self._embedding_model = embedding_model
        self._host = host
        self._port = port
        self._dimension = dimension
        self._connections = None
        self._collection = None
        self._embeddings = None

    @property
    def collection_name(self) -> str:
        """Return the collection name."""
        return self._collection_name

    def _get_openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        import os

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for embeddings"
            )
        return api_key

    def _ensure_initialized(self) -> None:
        """Ensure Milvus connection is established."""
        if self._collection is not None:
            return

        try:
            from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
            from langchain_openai import OpenAIEmbeddings

            # Connect to Milvus
            connections.connect(
                alias="default",
                host=self._host,
                port=self._port,
            )
            self._connections = connections

            # Initialize embeddings
            self._embeddings = OpenAIEmbeddings(model=self._embedding_model)

            # Check if collection exists, create if not
            if utility.has_collection(self._collection_name):
                self._collection = Collection(self._collection_name)
            else:
                # Create collection schema
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self._dimension),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
                ]
                schema = CollectionSchema(fields, description=f"Collection for {self._collection_name}")
                self._collection = Collection(self._collection_name, schema)

                # Create index for vector field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "AUTOINDEX",
                }
                self._collection.create_index(field_name="embedding", index_params=index_params)

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
        """Add documents to the vector store.

        Args:
            documents: List of document text chunks.
            metadatas: Optional list of metadata dicts.
            ids: Optional list of document IDs.

        Returns:
            List of document IDs.
        """
        self._ensure_initialized()

        if not documents:
            raise ValueError("Documents list cannot be empty")

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        try:
            # Generate embeddings
            embeddings = self._embeddings.embed_documents(documents)

            # Prepare data for insertion
            data = [
                ids,
                embeddings,
                documents,  # Store content as well
            ]

            # Insert into collection
            self._collection.insert(data)
            self._collection.flush()

            logger.info(f"Added {len(documents)} documents to Milvus collection")
            return ids

        except Exception as e:
            logger.error(f"Failed to add documents to Milvus: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a similarity search.

        Args:
            query: Query text.
            k: Number of results.
            filter: Optional filter (not implemented for Milvus).

        Returns:
            List of search results.
        """
        self._ensure_initialized()

        try:
            # Generate query embedding
            query_embedding = self._embeddings.embed_query(query)

            # Load collection to memory for search
            self._collection.load()

            # Perform search
            search_params = {"metric_type": "COSINE", "params": {}}
            results = self._collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=k,
                output_fields=["id", "content"],
            )

            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "id": hit.id,
                        "content": hit.entity.get("content", ""),
                        "metadata": {},
                        "score": hit.score,
                    })

            logger.debug(f"Found {len(formatted_results)} results in Milvus")
            return formatted_results

        except Exception as e:
            logger.error(f"Milvus similarity search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete.
        """
        self._ensure_initialized()

        try:
            # Build filter expression
            expr = f'id in {ids}'
            self._collection.delete(expr)
            self._collection.flush()

            logger.info(f"Deleted {len(ids)} documents from Milvus")

        except Exception as e:
            logger.error(f"Failed to delete documents from Milvus: {e}")
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            from pymilvus import utility, connections

            if utility.has_collection(self._collection_name):
                utility.drop_collection(self._collection_name)
                logger.info(f"Deleted Milvus collection: {self._collection_name}")

            self._collection = None

            # Disconnect
            try:
                connections.disconnect("default")
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Failed to delete Milvus collection: {e}")
            raise

    def count(self) -> int:
        """Return the number of documents in the collection."""
        self._ensure_initialized()
        return self._collection.num_entities