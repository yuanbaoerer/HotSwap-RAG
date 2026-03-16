"""Tests for vector stores."""

import pytest
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestChromaDBStore:
    """Tests for ChromaDB store."""

    def test_collection_name_property(self):
        """Test collection name property."""
        from backend.services.stores.chromadb_store import ChromaDBStore

        store = ChromaDBStore(collection_name="test_collection")
        assert store.collection_name == "test_collection"


class TestPineconeStore:
    """Tests for Pinecone store."""

    def test_collection_name_property(self):
        """Test index name property."""
        from backend.services.stores.pinecone_store import PineconeStore

        store = PineconeStore(collection_name="test_index")
        assert store.collection_name == "test_index"