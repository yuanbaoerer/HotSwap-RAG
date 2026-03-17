"""Tests for LLM providers."""

import pytest


class TestOpenAILLM:
    """Tests for OpenAI LLM."""

    def test_model_name_property(self):
        """Test model name property."""
        from backend.services.llms.openai_llm import OpenAILLM

        llm = OpenAILLM(model="gpt-4")
        assert llm.model_name == "gpt-4"

    def test_default_model(self):
        """Test default model."""
        from backend.services.llms.openai_llm import OpenAILLM

        llm = OpenAILLM()
        assert llm.model_name == OpenAILLM.DEFAULT_MODEL

    def test_count_tokens(self):
        """Test token counting."""
        from backend.services.llms.openai_llm import OpenAILLM

        llm = OpenAILLM()
        count = llm.count_tokens("Hello world")
        assert count > 0


class TestAnthropicLLM:
    """Tests for Anthropic LLM."""

    def test_model_name_property(self):
        """Test model name property."""
        from backend.services.llms.anthropic_llm import AnthropicLLM

        llm = AnthropicLLM(model="claude-3-opus")
        assert llm.model_name == "claude-3-opus"

    def test_default_model(self):
        """Test default model."""
        from backend.services.llms.anthropic_llm import AnthropicLLM

        llm = AnthropicLLM()
        assert llm.model_name == AnthropicLLM.DEFAULT_MODEL


class TestOllamaLLM:
    """Tests for Ollama LLM."""

    def test_model_name_property(self):
        """Test model name property."""
        from backend.services.llms.ollama_llm import OllamaLLM

        llm = OllamaLLM(model="llama3")
        assert llm.model_name == "llama3"

    def test_default_base_url(self):
        """Test default base URL."""
        from backend.services.llms.ollama_llm import OllamaLLM

        llm = OllamaLLM()
        assert "localhost:11434" in OllamaLLM.DEFAULT_BASE_URL


class TestOpenAICompatibleLLM:
    """Tests for OpenAI-compatible LLM."""

    def test_model_name_property(self):
        """Test model name property."""
        from backend.services.llms.openai_compatible_llm import OpenAICompatibleLLM

        llm = OpenAICompatibleLLM(model="custom-model", base_url="http://localhost:8080/v1")
        assert llm.model_name == "custom-model"


class TestLLMFactory:
    """Tests for LLM factory."""

    def test_create_openai_llm(self):
        """Test creating OpenAI LLM via factory."""
        from backend.factories import create_llm

        llm = create_llm("openai", model="gpt-4o-mini")
        assert llm.model_name == "gpt-4o-mini"

    def test_create_ollama_llm(self):
        """Test creating Ollama LLM via factory."""
        from backend.factories import create_llm

        llm = create_llm("ollama", model="llama3.2")
        assert llm.model_name == "llama3.2"

    def test_create_invalid_llm(self):
        """Test creating invalid LLM raises error."""
        from backend.factories import create_llm

        with pytest.raises(ValueError):
            create_llm("invalid")

    def test_get_available_llms(self):
        """Test getting available LLMs."""
        from backend.factories import get_available_llms

        llms = get_available_llms()
        assert "openai" in llms
        assert "anthropic" in llms
        assert "ollama" in llms