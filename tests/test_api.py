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
        assert "llm_model" in data

    def test_update_active_config(self, client):
        """Test updating active config."""
        # Update config
        new_config = {
            "parser_type": "docx",
            "store_type": "pinecone",
            "llm_type": "anthropic",
            "llm_model": "claude-3-5-sonnet",
        }
        response = client.put("/api/config/active", json=new_config)
        assert response.status_code == 200
        data = response.json()
        assert data["parser_type"] == "docx"
        assert data["store_type"] == "pinecone"
        assert data["llm_type"] == "anthropic"

        # Verify the update persisted
        response = client.get("/api/config/active")
        assert response.status_code == 200
        data = response.json()
        assert data["parser_type"] == "docx"

    def test_reset_config(self, client):
        """Test resetting config to defaults."""
        response = client.post("/api/config/reset")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"


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

    def test_create_knowledge_base(self, client):
        """Test creating a knowledge base."""
        kb_data = {
            "name": "Test KB",
            "description": "A test knowledge base",
            "parser_type": "pdf",
            "store_type": "chromadb",
            "llm_type": "openai",
        }
        response = client.post("/api/knowledge-bases/", json=kb_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test KB"
        assert data["description"] == "A test knowledge base"
        assert data["parser_type"] == "pdf"
        assert data["document_count"] == 0
        assert "id" in data
        assert data["id"] != "temp-id"  # Should be a real UUID

    def test_get_knowledge_base(self, client):
        """Test getting a knowledge base by ID."""
        # First create one
        kb_data = {"name": "KB to Get"}
        create_response = client.post("/api/knowledge-bases/", json=kb_data)
        kb_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/api/knowledge-bases/{kb_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == kb_id
        assert data["name"] == "KB to Get"

    def test_get_nonexistent_knowledge_base(self, client):
        """Test getting a non-existent knowledge base."""
        response = client.get("/api/knowledge-bases/nonexistent-id")
        assert response.status_code == 404

    def test_update_knowledge_base(self, client):
        """Test updating a knowledge base."""
        # First create one
        kb_data = {"name": "KB to Update"}
        create_response = client.post("/api/knowledge-bases/", json=kb_data)
        kb_id = create_response.json()["id"]

        # Update it
        update_data = {
            "name": "Updated KB",
            "description": "Updated description",
        }
        response = client.put(f"/api/knowledge-bases/{kb_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated KB"
        assert data["description"] == "Updated description"

    def test_update_nonexistent_knowledge_base(self, client):
        """Test updating a non-existent knowledge base."""
        update_data = {"name": "Won't work"}
        response = client.put("/api/knowledge-bases/nonexistent-id", json=update_data)
        assert response.status_code == 404

    def test_delete_knowledge_base(self, client):
        """Test deleting a knowledge base."""
        # First create one
        kb_data = {"name": "KB to Delete"}
        create_response = client.post("/api/knowledge-bases/", json=kb_data)
        kb_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/knowledge-bases/{kb_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"
        assert data["id"] == kb_id

        # Verify it's gone
        get_response = client.get(f"/api/knowledge-bases/{kb_id}")
        assert get_response.status_code == 404


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

    def test_chat_with_top_k(self, client):
        """Test chat with custom top_k parameter."""
        response = client.post(
            "/api/chat/",
            json={"question": "Test question", "top_k": 2}
        )
        assert response.status_code == 200