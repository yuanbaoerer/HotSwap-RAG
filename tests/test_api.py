"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client."""
    from backend.api.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestConfigEndpoints:
    """Tests for config endpoints."""

    def test_list_parsers(self, client):
        """Test listing parsers."""
        response = client.get("/api/config/parsers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        types = [item["type"] for item in data]
        assert "pdf" in types
        assert "docx" in types
        assert "ocr" in types

    def test_list_stores(self, client):
        """Test listing stores."""
        response = client.get("/api/config/stores")
        assert response.status_code == 200
        data = response.json()
        types = [item["type"] for item in data]
        assert "chromadb" in types
        assert "pinecone" in types

    def test_list_llms(self, client):
        """Test listing LLMs."""
        response = client.get("/api/config/llms")
        assert response.status_code == 200
        data = response.json()
        types = [item["type"] for item in data]
        assert "openai" in types
        assert "anthropic" in types
        assert "ollama" in types

    def test_get_active_config(self, client):
        """Test getting active config."""
        response = client.get("/api/config/active")
        assert response.status_code == 200
        data = response.json()
        assert "parser_type" in data
        assert "store_type" in data
        assert "llm_type" in data


class TestDocumentEndpoints:
    """Tests for document endpoints."""

    def test_list_documents(self, client):
        """Test listing documents."""
        response = client.get("/api/documents/")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data


class TestKnowledgeBaseEndpoints:
    """Tests for knowledge base endpoints."""

    def test_list_knowledge_bases(self, client):
        """Test listing knowledge bases."""
        response = client.get("/api/knowledge-bases/")
        assert response.status_code == 200
        data = response.json()
        assert "knowledge_bases" in data
        assert "total" in data


class TestChatEndpoint:
    """Tests for chat endpoint."""

    def test_chat(self, client):
        """Test chat endpoint."""
        response = client.post(
            "/api/chat/",
            json={"question": "What is this?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data