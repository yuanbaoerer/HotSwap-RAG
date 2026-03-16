"""PDF document parser implementation."""

import logging
from pathlib import Path
from typing import List

from backend.core.base_parser import BaseDocumentParser

logger = logging.getLogger(__name__)


class PDFParser(BaseDocumentParser):
    """Parser for PDF documents using PyPDF2.

    This parser extracts text content from PDF files and splits it into
    manageable chunks for processing.

    Attributes:
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters to overlap between chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the PDF parser.

        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    @property
    def name(self) -> str:
        """Return the name of this parser."""
        return "PDF Parser"

    def parse(self, file_path: Path) -> List[str]:
        """Parse a PDF document and extract text chunks.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of text chunks extracted from the document.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a PDF.
            Exception: If parsing fails.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        logger.info(f"Parsing PDF file: {file_path}")

        try:
            import PyPDF2

            text_content = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                    logger.debug(f"Extracted text from page {page_num + 1}")

            full_text = "\n\n".join(text_content)
            chunks = self._split_text(full_text)

            logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
            return chunks

        except ImportError:
            logger.error("PyPDF2 not installed")
            raise ImportError(
                "PyPDF2 is required for PDF parsing. "
                "Install it with: pip install PyPDF2"
            )
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise

    def supported_formats(self) -> List[str]:
        """Return supported file formats.

        Returns:
            List containing '.pdf'.
        """
        return [".pdf"]

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.

        Args:
            text: The full text to split.

        Returns:
            List of text chunks.
        """
        if len(text) <= self._chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self._chunk_size
            chunk = text[start:end]

            # Try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                last_period = chunk.rfind(". ")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > start + self._chunk_size // 2:
                    chunk = text[start : break_point + 1]
                    end = start + len(chunk)

            if chunk.strip():
                chunks.append(chunk.strip())

            start = end - self._chunk_overlap

        return chunks