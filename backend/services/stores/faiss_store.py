"""FAISS vector store implementation."""

import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)


class FAISSStore(BaseVectorStore):
    """Vector store implementation using FAISS.

    FAISS (Facebook AI Similarity Search) is a library for efficient
    similarity search and clustering of dense vectors.

    Note:
        FAISS does not support document deletion. Use delete_collection()
        to clear all documents.

    Attributes:
        collection_name: Name for the index.
        embedding_model: Name of the embedding model.
        index_path: Path to save/load the index.
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
        self._embeddings = None
        self._doc_ids: List[str] = []  # Track document IDs

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
        """Ensure the FAISS store is initialized."""
        if self._vector_store is not None:
            return

        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings

            # Initialize embeddings
            self._embeddings = OpenAIEmbeddings(model=self._embedding_model)

            # Try to load existing index
            if self._index_path:
                index_file = Path(self._index_path)
                if (index_file / f"{self._collection_name}.faiss").exists():
                    try:
                        self._vector_store = FAISS.load_local(
                            str(index_file),
                            self._embeddings,
                            self._collection_name,
                            allow_dangerous_deserialization=True,
                        )
                        logger.info(f"Loaded FAISS index from {index_file}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load FAISS index: {e}")

            # Create new empty store with a placeholder document
            # FAISS requires at least one document to initialize
            self._vector_store = FAISS.from_texts(
                ["__init__"],
                self._embeddings,
                metadatas=[{"_init": True, "_id": "__init__"}],
            )

            logger.info(f"Initialized new FAISS store: {self._collection_name}")

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

        # Create metadata with IDs
        if metadatas is None:
            metadatas = [{} for _ in documents]

        # Add ID to metadata for tracking
        for i, doc_id in enumerate(ids):
            metadatas[i]["_id"] = doc_id

        try:
            from langchain_core.documents import Document

            # Create Document objects
            docs = [
                Document(page_content=doc, metadata=meta)
                for doc, meta in zip(documents, metadatas)
            ]

            # Add to vector store
            self._vector_store.add_documents(docs)

            # Track IDs
            self._doc_ids.extend(ids)

            # Save if path is set
            self._save_index()

            logger.info(f"Added {len(documents)} documents to FAISS store")
            return ids

        except Exception as e:
            logger.error(f"Failed to add documents to FAISS: {e}")
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
            filter: Optional filter (not supported by FAISS).

        Returns:
            List of search results.
        """
        self._ensure_initialized()

        try:
            # Perform search with scores
            results = self._vector_store.similarity_search_with_score(query, k=k)

            # Format results
            formatted_results = []
            for doc, score in results:
                # Skip placeholder document
                if doc.metadata.get("_init") or doc.page_content == "__init__":
                    continue

                formatted_results.append({
                    "id": doc.metadata.get("_id", ""),
                    "content": doc.page_content,
                    "metadata": {k: v for k, v in doc.metadata.items() if k != "_id"},
                    "score": float(score),
                })

            logger.debug(f"Found {len(formatted_results)} results in FAISS")
            return formatted_results

        except Exception as e:
            logger.error(f"FAISS similarity search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs.

        Note:
            FAISS does not support document deletion.
            Use delete_collection() to clear all documents.

        Raises:
            NotImplementedError: Always, as FAISS doesn't support deletion.
        """
        raise NotImplementedError(
            "FAISS does not support document deletion. "
            "Use delete_collection() to clear all documents, or recreate the index."
        )

    def delete_collection(self) -> None:
        """Delete the entire index and clear all documents."""
        try:
            # Clear in-memory data
            self._vector_store = None
            self._doc_ids = []
            self._embeddings = None

            # Remove saved index files
            if self._index_path:
                index_dir = Path(self._index_path)
                if index_dir.exists():
                    for ext in [".faiss", ".pkl"]:
                        index_file = index_dir / f"{self._collection_name}{ext}"
                        if index_file.exists():
                            index_file.unlink()

            logger.info(f"Deleted FAISS store: {self._collection_name}")

        except Exception as e:
            logger.error(f"Failed to delete FAISS collection: {e}")
            raise

    def _save_index(self) -> None:
        """Save the index to disk if path is set."""
        if self._index_path and self._vector_store:
            try:
                index_dir = Path(self._index_path)
                index_dir.mkdir(parents=True, exist_ok=True)
                self._vector_store.save_local(str(index_dir), self._collection_name)
                logger.debug(f"Saved FAISS index to {index_dir}")
            except Exception as e:
                logger.warning(f"Failed to save FAISS index: {e}")

    def count(self) -> int:
        """Return the number of documents in the index.

        Returns:
            Number of documents (excluding placeholder).
        """
        if self._vector_store is None:
            return 0

        total = self._vector_store.index.ntotal
        # Subtract 1 for placeholder if present
        if total > 0 and len(self._doc_ids) == 0:
            return max(0, total - 1)
        return len(self._doc_ids)