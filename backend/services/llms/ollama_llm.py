"""Ollama LLM implementation for local models."""

import logging
from typing import Iterator, Optional, List

from backend.core.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OllamaLLM(BaseLLM):
    """LLM implementation using Ollama for local model inference."""

    DEFAULT_MODEL = "llama3.2"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,  # Not used, kept for interface compatibility
    ):
        """Initialize the Ollama LLM.

        Args:
            model: Model name (default: llama3.2).
            base_url: Ollama server URL (default: http://localhost:11434).
            api_key: Not used for Ollama.
        """
        self._model = model or self.DEFAULT_MODEL
        self._base_url = base_url or self.DEFAULT_BASE_URL
        self._client = None

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self._model

    def _ensure_initialized(self) -> None:
        """Ensure the Ollama client is initialized."""
        if self._client is not None:
            return

        try:
            from openai import OpenAI

            # Ollama is OpenAI-compatible
            self._client = OpenAI(
                base_url=f"{self._base_url}/v1",
                api_key="ollama",  # Required but not used
            )
            logger.info(f"Initialized Ollama client with model: {self._model}")

        except ImportError:
            raise ImportError("Ollama requires: pip install openai")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a text response."""
        self._ensure_initialized()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate a text response with streaming."""
        self._ensure_initialized()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

    def generate_with_context(
        self,
        prompt: str,
        contexts: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response using retrieved context."""
        context_text = "\n\n".join(f"[Context {i+1}]\n{ctx}" for i, ctx in enumerate(contexts))

        default_system = (
            "You are a helpful assistant. Use the provided context to answer "
            "the user's question. If the context doesn't contain relevant "
            "information, say so clearly."
        )

        full_prompt = f"Context:\n{context_text}\n\nQuestion: {prompt}"

        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt or default_system,
            temperature=temperature,
            max_tokens=max_tokens,
        )