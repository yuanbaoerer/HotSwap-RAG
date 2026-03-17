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


class TestPineconeStore:
    """Tests for Pinecone store."""

    def test_collection_name_property(self):
        """Test index name property."""
        from backend.services.stores.pinecone_store import PineconeStore

        store = PineconeStore(collection_name="test_index")
        assert store.collection_name == "test_index"


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


class TestMilvusStore:
    """Tests for Milvus store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.milvus_store import MilvusStore

        store = MilvusStore(collection_name="test_milvus")
        assert store.collection_name == "test_milvus"


class TestFAISSStore:
    """Tests for FAISS store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.faiss_store import FAISSStore

        store = FAISSStore(collection_name="test_faiss")
        assert store.collection_name == "test_faiss"