"""Abstract base class for vector stores.

All vector store implementations must inherit from this class and implement
its abstract methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseVectorStore(ABC):
    """Abstract base class for vector stores.

    This class defines the interface that all vector store implementations
    must follow. Vector stores are responsible for storing document embeddings
    and performing similarity searches.

    Attributes:
        collection_name: Name of the collection in the vector store.
    """

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Return the name of the collection.

        Returns:
            Name of the collection in the vector store.
        """
        pass

    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store.

        Args:
            documents: List of document text chunks to add.
            metadatas: Optional list of metadata dicts for each document.
            ids: Optional list of IDs for each document.

        Returns:
            List of IDs for the added documents.

        Raises:
            ValueError: If documents list is empty.
            Exception: If adding documents fails.
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a similarity search.

        Args:
            query: The query text to search for.
            k: Number of results to return.
            filter: Optional metadata filter to apply.

        Returns:
            List of search results, each containing 'content', 'metadata', and 'score'.

        Raises:
            Exception: If the search fails.
        """
        pass

    @abstractmethod
    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete.

        Raises:
            Exception: If deletion fails.
        """
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the entire collection.

        Raises:
            Exception: If deletion fails.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of documents in the collection.

        Returns:
            Number of documents in the collection.
        """
        pass