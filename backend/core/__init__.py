"""Core abstract base classes for the HotSwap RAG system.

This module defines the strategy pattern interfaces that all implementations must follow.
"""

from backend.core.base_parser import BaseDocumentParser
from backend.core.base_store import BaseVectorStore
from backend.core.base_llm import BaseLLM

__all__ = ["BaseDocumentParser", "BaseVectorStore", "BaseLLM"]