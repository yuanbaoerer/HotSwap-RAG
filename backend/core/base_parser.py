"""Abstract base class for document parsers.

All document parser implementations must inherit from this class and implement
its abstract methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseDocumentParser(ABC):
    """Abstract base class for document parsers.

    This class defines the interface that all document parser implementations
    must follow. Parsers are responsible for extracting text content from
    various document formats.

    Attributes:
        name: Human-readable name of the parser.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this parser.

        Returns:
            Human-readable name of the parser.
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> List[str]:
        """Parse a document and extract text chunks.

        Args:
            file_path: Path to the document file to parse.

        Returns:
            A list of text chunks extracted from the document.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
            Exception: If parsing fails for any other reason.
        """
        pass

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return a list of supported file formats.

        Returns:
            List of file extensions supported by this parser (e.g., ['.pdf', '.txt']).
        """
        pass

    def supports_format(self, file_path: Path) -> bool:
        """Check if this parser supports the given file format.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file format is supported, False otherwise.
        """
        return file_path.suffix.lower() in self.supported_formats()