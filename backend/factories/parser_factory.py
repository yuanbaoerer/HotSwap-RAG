"""Factory for creating document parser instances."""

import logging
from typing import Literal, Optional, Dict, Any

from backend.core.base_parser import BaseDocumentParser
from backend.services.parsers.pdf_parser import PDFParser
from backend.services.parsers.docx_parser import DocxParser
from backend.services.parsers.ocr_parser import OCRParser

logger = logging.getLogger(__name__)

ParserType = Literal["pdf", "docx", "ocr"]

# Registry of available parsers
_PARSER_REGISTRY: Dict[str, type] = {
    "pdf": PDFParser,
    "docx": DocxParser,
    "ocr": OCRParser,
}


def create_parser(
    parser_type: ParserType,
    **kwargs,
) -> BaseDocumentParser:
    """Create a document parser instance.

    Args:
        parser_type: Type of parser to create ('pdf', 'docx', 'ocr').
        **kwargs: Additional arguments passed to the parser constructor.

    Returns:
        A parser instance of the specified type.

    Raises:
        ValueError: If the parser type is not recognized.

    Example:
        >>> parser = create_parser("pdf")
        >>> chunks = parser.parse(Path("document.pdf"))
    """
    if parser_type not in _PARSER_REGISTRY:
        available = list(_PARSER_REGISTRY.keys())
        raise ValueError(
            f"Unknown parser type: '{parser_type}'. "
            f"Available types: {available}"
        )

    parser_class = _PARSER_REGISTRY[parser_type]
    logger.info(f"Creating parser of type: {parser_type}")

    return parser_class(**kwargs)


def get_available_parsers() -> Dict[str, str]:
    """Get a dictionary of available parser types and their descriptions.

    Returns:
        Dictionary mapping parser types to their descriptions.
    """
    # Create temporary instances to get names
    return {
        parser_type: cls.__name__
        for parser_type, cls in _PARSER_REGISTRY.items()
    }


def register_parser(name: str, parser_class: type) -> None:
    """Register a custom parser type.

    Args:
        name: Name to register the parser under.
        parser_class: The parser class to register.

    Raises:
        TypeError: If the class doesn't inherit from BaseDocumentParser.
    """
    if not issubclass(parser_class, BaseDocumentParser):
        raise TypeError(
            f"Parser class must inherit from BaseDocumentParser"
        )
    _PARSER_REGISTRY[name] = parser_class
    logger.info(f"Registered custom parser: {name}")