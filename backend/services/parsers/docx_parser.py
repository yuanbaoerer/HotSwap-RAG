"""Word document parser implementation."""

import logging
from pathlib import Path
from typing import List

from backend.core.base_parser import BaseDocumentParser

logger = logging.getLogger(__name__)


class DocxParser(BaseDocumentParser):
    """Parser for Word documents using python-docx.

    This parser extracts text content from .docx files and splits it into
    manageable chunks for processing.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the Docx parser.

        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    @property
    def name(self) -> str:
        """Return the name of this parser."""
        return "Word Document Parser"

    def parse(self, file_path: Path) -> List[str]:
        """Parse a Word document and extract text chunks.

        Args:
            file_path: Path to the .docx file.

        Returns:
            List of text chunks extracted from the document.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a .docx file.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        logger.info(f"Parsing Word document: {file_path}")

        try:
            from docx import Document

            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(paragraphs)

            chunks = self._split_text(full_text)
            logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
            return chunks

        except ImportError:
            logger.error("python-docx not installed")
            raise ImportError(
                "python-docx is required for Word document parsing. "
                "Install it with: pip install python-docx"
            )
        except Exception as e:
            logger.error(f"Failed to parse Word document {file_path}: {e}")
            raise

    def supported_formats(self) -> List[str]:
        """Return supported file formats.

        Returns:
            List containing '.docx'.
        """
        return [".docx"]

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self._chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self._chunk_size
            chunk = text[start:end]

            if end < len(text):
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