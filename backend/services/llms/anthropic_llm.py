"""Anthropic LLM implementation."""

import logging
from typing import Iterator, Optional, List

from backend.core.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class AnthropicLLM(BaseLLM):
    """LLM implementation using Anthropic's Claude API."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the Anthropic LLM.

        Args:
            model: Model name (default: claude-3-5-sonnet).
            api_key: Anthropic API key (loaded from env if not provided).
        """
        self._model = model or self.DEFAULT_MODEL
        self._api_key = api_key
        self._client = None

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self._model

    def _ensure_initialized(self) -> None:
        """Ensure the Anthropic client is initialized."""
        if self._client is not None:
            return

        try:
            import os
            from anthropic import Anthropic

            api_key = self._api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY is required")

            self._client = Anthropic(api_key=api_key)
            logger.info(f"Initialized Anthropic client with model: {self._model}")

        except ImportError:
            raise ImportError("Anthropic requires: pip install anthropic")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a text response."""
        self._ensure_initialized()

        try:
            kwargs = {
                "model": self._model,
                "max_tokens": max_tokens or 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = self._client.messages.create(**kwargs)
            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
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

        try:
            kwargs = {
                "model": self._model,
                "max_tokens": max_tokens or 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            with self._client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
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