"""Generic OpenAI-compatible LLM implementation."""

import logging
from typing import Iterator, Optional, List

from backend.core.base_llm import BaseLLM

logger = logging.getLogger(__name__)


class OpenAICompatibleLLM(BaseLLM):
    """LLM implementation for OpenAI-compatible APIs.

    This can be used with various providers that implement the OpenAI API
    specification, such as:
    - vLLM
    - LocalAI
    - Ollama (via /v1 endpoint)
    - Custom endpoints
    """

    DEFAULT_MODEL = "default"

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the OpenAI-compatible LLM.

        Args:
            model: Model name.
            api_key: API key (optional for some providers).
            base_url: Base URL for the API (required).
        """
        self._model = model or self.DEFAULT_MODEL
        self._api_key = api_key or "sk-dummy"
        self._base_url = base_url
        self._client = None

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self._model

    def _ensure_initialized(self) -> None:
        """Ensure the client is initialized."""
        if self._client is not None:
            return

        if not self._base_url:
            raise ValueError("base_url is required for OpenAI-compatible LLM")

        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
            logger.info(f"Initialized OpenAI-compatible client: {self._base_url}")

        except ImportError:
            raise ImportError("OpenAI-compatible requires: pip install openai")

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
            logger.error(f"Generation failed: {e}")
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
            logger.error(f"Streaming failed: {e}")
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