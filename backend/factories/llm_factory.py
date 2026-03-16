"""Factory for creating LLM instances."""

import logging
from typing import Literal, Optional, Dict, Any

from backend.core.base_llm import BaseLLM

logger = logging.getLogger(__name__)

LLMType = Literal["openai", "anthropic", "ollama", "openai_compatible"]

# Registry of available LLMs (lazy import)
_LLM_REGISTRY: Dict[str, str] = {
    "openai": "backend.services.llms.openai_llm.OpenAILLM",
    "anthropic": "backend.services.llms.anthropic_llm.AnthropicLLM",
    "ollama": "backend.services.llms.ollama_llm.OllamaLLM",
    "openai_compatible": "backend.services.llms.openai_compatible_llm.OpenAICompatibleLLM",
}


def create_llm(
    llm_type: LLMType,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> BaseLLM:
    """Create an LLM instance.

    Args:
        llm_type: Type of LLM to create ('openai', 'anthropic', 'ollama', 'openai_compatible').
        model: Name of the model to use (provider-specific default if not specified).
        api_key: API key for the provider (loaded from env if not specified).
        base_url: Base URL for the API (for Ollama or custom endpoints).
        **kwargs: Additional arguments passed to the LLM constructor.

    Returns:
        An LLM instance of the specified type.

    Raises:
        ValueError: If the LLM type is not recognized.
        ImportError: If required dependencies are not installed.

    Example:
        >>> llm = create_llm("openai", model="gpt-4")
        >>> response = llm.generate("Hello, world!")
    """
    if llm_type not in _LLM_REGISTRY:
        available = list(_LLM_REGISTRY.keys())
        raise ValueError(
            f"Unknown LLM type: '{llm_type}'. "
            f"Available types: {available}"
        )

    logger.info(f"Creating LLM of type: {llm_type}")

    # Lazy import to avoid loading unnecessary dependencies
    module_path = _LLM_REGISTRY[llm_type]
    module_name, class_name = module_path.rsplit(".", 1)

    try:
        import importlib
        module = importlib.import_module(module_name)
        llm_class = getattr(module, class_name)
    except ImportError as e:
        logger.error(f"Failed to import {llm_type} LLM: {e}")
        raise ImportError(
            f"Failed to import {llm_type} LLM. "
            f"Make sure required dependencies are installed: {e}"
        )

    return llm_class(
        model=model,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )


def get_available_llms() -> Dict[str, str]:
    """Get a dictionary of available LLM types.

    Returns:
        Dictionary mapping LLM types to their module paths.
    """
    return dict(_LLM_REGISTRY)


def register_llm(name: str, module_path: str) -> None:
    """Register a custom LLM type.

    Args:
        name: Name to register the LLM under.
        module_path: Full Python path to the LLM class.
    """
    _LLM_REGISTRY[name] = module_path
    logger.info(f"Registered custom LLM: {name}")