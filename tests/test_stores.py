"""Tests for vector stores."""

import pytest
from pathlib import Path


class TestChromaDBStore:
    """Tests for ChromaDB store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.chromadb_store import ChromaDBStore

        store = ChromaDBStore(collection_name="test_collection")
        assert store.collection_name == "test_collection"

    def test_default_collection_name(self):
        """Test default collection name."""
        from backend.services.stores.chromadb_store import ChromaDBStore

        store = ChromaDBStore()
        assert store.collection_name == "default"

    def test_custom_embedding_model(self):
        """Test custom embedding model."""
        from backend.services.stores.chromadb_store import ChromaDBStore

        store = ChromaDBStore(embedding_model="text-embedding-3-large")
        assert store._embedding_model == "text-embedding-3-large"

    def test_persist_directory(self):
        """Test persist directory configuration."""
        from backend.services.stores.chromadb_store import ChromaDBStore

        store = ChromaDBStore(persist_directory="./test_data")
        assert store._persist_directory == "./test_data"


class TestPineconeStore:
    """Tests for Pinecone store."""

    def test_collection_name_property(self):
        """Test index name property."""
        from backend.services.stores.pinecone_store import PineconeStore

        store = PineconeStore(collection_name="test_index")
        assert store.collection_name == "test_index"

    def test_default_collection_name(self):
        """Test default collection name."""
        from backend.services.stores.pinecone_store import PineconeStore

        store = PineconeStore()
        assert store.collection_name == "default"


class TestMilvusStore:
    """Tests for Milvus store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore(collection_name="test_milvus")
        assert store.collection_name == "test_milvus"

    def test_default_collection_name(self):
        """Test default collection name."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore()
        assert store.collection_name == "default"

    def test_custom_host_port(self):
        """Test custom host and port configuration."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore(host="milvus-server", port=19531)
        assert store._host == "milvus-server"
        assert store._port == 19531

    def test_custom_dimension(self):
        """Test custom embedding dimension."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore(dimension=768)
        assert store._dimension == 768

    def test_default_dimension(self):
        """Test default embedding dimension."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore()
        assert store._dimension == MilvusStore.DEFAULT_DIMENSION


class TestFAISSStore:
    """Tests for FAISS store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore(collection_name="test_faiss")
        assert store.collection_name == "test_faiss"

    def test_default_collection_name(self):
        """Test default collection name."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore()
        assert store.collection_name == "default"

    def test_custom_index_path(self):
        """Test custom index path."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore(index_path="./test_index")
        assert store._index_path == "./test_index"

    def test_delete_documents_not_supported(self):
        """Test that delete_documents raises NotImplementedError."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore()
        with pytest.raises(NotImplementedError) as exc_info:
            store.delete_documents(["id1", "id2"])

        assert "does not support document deletion" in str(exc_info.value)

    def test_count_returns_zero_when_not_initialized(self):
        """Test count returns 0 when not initialized."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore()
        assert store.count() == 0


class TestStoreFactory:
    """Tests for store factory."""

    def test_get_available_stores(self):
        """Test getting available stores."""
        from backend.factories import get_available_stores

        stores = get_available_stores()
        assert "chromadb" in stores
        assert "pinecone" in stores
        assert "milvus" in stores
        assert "faiss" in stores

    def test_available_stores_count(self):
        """Test that we have 4 store types."""
        from backend.factories import get_available_stores

        stores = get_available_stores()
        assert len(stores) >= 4


class TestBaseVectorStore:
    """Tests for base vector store interface."""

    def test_all_stores_inherit_from_base(self):
        """Test that all stores inherit from BaseVectorStore."""
        from backend.core.base_store import BaseVectorStore
        from backend.services.stores.chromadb_store import ChromaDBStore
        from backend.services.stores.pinecone_store import PineconeStore
        from backend.services.stores.milvus_store import MilvusStore
        from backend.services.stores.faiss_store import FAISSStore

        assert issubclass(ChromaDBStore, BaseVectorStore)
        assert issubclass(PineconeStore, BaseVectorStore)
        assert issubclass(MilvusStore, BaseVectorStore)
        assert issubclass(FAISSStore, BaseVectorStore)

    def test_all_stores_implement_required_methods(self):
        """Test that all stores implement required methods."""
        from backend.services.stores import ChromaDBStore, PineconeStore, MilvusStore, FAISSStore

        required_methods = [
            "add_documents",
            "similarity_search",
            "delete_documents",
            "delete_collection",
            "count",
        ]

        for store_class in [ChromaDBStore, PineconeStore, MilvusStore, FAISSStore]:
            for method in required_methods:
                assert hasattr(store_class, method), f"{store_class.__name__} missing {method}"
                assert callable(getattr(store_class, method)), f"{store_class.__name__}.{method} not callable"