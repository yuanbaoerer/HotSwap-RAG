"""Abstract base class for LLM providers.

All LLM implementations must inherit from this class and implement
its abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any, List


class BaseLLM(ABC):
    """Abstract base class for LLM providers.

    This class defines the interface that all LLM implementations
    must follow. LLMs are responsible for generating text responses
    from prompts.

    Attributes:
        model_name: Name of the model being used.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model.

        Returns:
            Name of the model being used.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a text response from a prompt.

        Args:
            prompt: The user prompt to generate a response for.
            system_prompt: Optional system prompt to set the context.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated text response.

        Raises:
            Exception: If generation fails.
        """
        pass

    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate a text response from a prompt with streaming.

        Args:
            prompt: The user prompt to generate a response for.
            system_prompt: Optional system prompt to set the context.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.

        Yields:
            Chunks of the generated text response.

        Raises:
            Exception: If generation fails.
        """
        pass

    @abstractmethod
    def generate_with_context(
        self,
        prompt: str,
        contexts: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response using retrieved context for RAG.

        Args:
            prompt: The user question.
            contexts: List of retrieved context strings.
            system_prompt: Optional system prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            The generated response with context.

        Raises:
            Exception: If generation fails.
        """
        pass

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text.

        Args:
            text: The text to count tokens for.

        Returns:
            Estimated number of tokens.
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4