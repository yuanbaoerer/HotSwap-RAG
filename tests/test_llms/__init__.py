"""Tests for LLM providers."""

import pytest
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


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


class TestAnthropicLLM:
    """Tests for Anthropic LLM."""

    def test_model_name_property(self):
        """Test model name property."""
        from backend.services.llms.anthropic_llm import AnthropicLLM

        llm = AnthropicLLM(model="claude-3-opus")
        assert llm.model_name == "claude-3-opus"


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