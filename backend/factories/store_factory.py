"""Factory for creating vector store instances."""

import logging
from typing import Literal, Optional, Dict, Any

from backend.core.base_store import BaseVectorStore

logger = logging.getLogger(__name__)

StoreType = Literal["chromadb", "pinecone", "milvus", "faiss"]

# Registry of available stores (lazy import to avoid dependency issues)
_STORE_REGISTRY: Dict[str, str] = {
    "chromadb": "backend.services.stores.chromadb_store.ChromaDBStore",
    "pinecone": "backend.services.stores.pinecone_store.PineconeStore",
    "milvus": "backend.services.stores.milvus_store.MilvusStore",
    "faiss": "backend.services.stores.faiss_store.FAISSStore",
}


def create_store(
    store_type: StoreType,
    collection_name: str = "default",
    embedding_model: str = "text-embedding-3-small",
    **kwargs,
) -> BaseVectorStore:
    """Create a vector store instance.

    Args:
        store_type: Type of store to create ('chromadb', 'pinecone', 'milvus', 'faiss').
        collection_name: Name of the collection to use.
        embedding_model: Name of the embedding model to use.
        **kwargs: Additional arguments passed to the store constructor.

    Returns:
        A vector store instance of the specified type.

    Raises:
        ValueError: If the store type is not recognized.
        ImportError: If required dependencies are not installed.

    Example:
        >>> store = create_store("chromadb", collection_name="my_docs")
        >>> store.add_documents(["Hello world"], [{"source": "test"}])
    """
    if store_type not in _STORE_REGISTRY:
        available = list(_STORE_REGISTRY.keys())
        raise ValueError(
            f"Unknown store type: '{store_type}'. "
            f"Available types: {available}"
        )

    logger.info(f"Creating store of type: {store_type}")

    # Lazy import to avoid loading unnecessary dependencies
    module_path = _STORE_REGISTRY[store_type]
    module_name, class_name = module_path.rsplit(".", 1)

    try:
        import importlib
        module = importlib.import_module(module_name)
        store_class = getattr(module, class_name)
    except ImportError as e:
        logger.error(f"Failed to import {store_type} store: {e}")
        raise ImportError(
            f"Failed to import {store_type} store. "
            f"Make sure required dependencies are installed: {e}"
        )

    return store_class(
        collection_name=collection_name,
        embedding_model=embedding_model,
        **kwargs,
    )


def get_available_stores() -> Dict[str, str]:
    """Get a dictionary of available store types.

    Returns:
        Dictionary mapping store types to their module paths.
    """
    return dict(_STORE_REGISTRY)


def register_store(name: str, module_path: str) -> None:
    """Register a custom store type.

    Args:
        name: Name to register the store under.
        module_path: Full Python path to the store class.
    """
    _STORE_REGISTRY[name] = module_path
    logger.info(f"Registered custom store: {name}")