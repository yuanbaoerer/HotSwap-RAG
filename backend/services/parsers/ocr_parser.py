"""OCR document parser implementation for scanned documents and images."""

import logging
from pathlib import Path
from typing import List

from backend.core.base_parser import BaseDocumentParser

logger = logging.getLogger(__name__)


class OCRParser(BaseDocumentParser):
    """Parser for scanned documents and images using OCR.

    This parser uses Tesseract OCR or other OCR engines to extract text
    from images and scanned PDF documents.

    Attributes:
        language: Language code for OCR (default: 'eng').
        ocr_engine: OCR engine to use ('tesseract', 'easyocr').
    """

    def __init__(
        self,
        language: str = "eng",
        ocr_engine: str = "tesseract",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """Initialize the OCR parser.

        Args:
            language: Language code for OCR (e.g., 'eng', 'chi_sim' for Chinese).
            ocr_engine: OCR engine to use ('tesseract' or 'easyocr').
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        self._language = language
        self._ocr_engine = ocr_engine
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    @property
    def name(self) -> str:
        """Return the name of this parser."""
        return f"OCR Parser ({self._ocr_engine})"

    def parse(self, file_path: Path) -> List[str]:
        """Parse a document or image using OCR.

        Args:
            file_path: Path to the file.

        Returns:
            List of text chunks extracted from the document.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_format(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        logger.info(f"Parsing file with OCR: {file_path}")

        try:
            if self._ocr_engine == "tesseract":
                text = self._parse_with_tesseract(file_path)
            elif self._ocr_engine == "easyocr":
                text = self._parse_with_easyocr(file_path)
            else:
                raise ValueError(f"Unknown OCR engine: {self._ocr_engine}")

            chunks = self._split_text(text)
            logger.info(f"Extracted {len(chunks)} chunks from {file_path}")
            return chunks

        except Exception as e:
            logger.error(f"Failed to parse {file_path} with OCR: {e}")
            raise

    def supported_formats(self) -> List[str]:
        """Return supported file formats.

        Returns:
            List of supported image and document formats.
        """
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]

    def _parse_with_tesseract(self, file_path: Path) -> str:
        """Parse using Tesseract OCR.

        Args:
            file_path: Path to the file.

        Returns:
            Extracted text.
        """
        try:
            import pytesseract
            from PIL import Image
            import pdf2image

            if file_path.suffix.lower() == ".pdf":
                # Convert PDF to images
                images = pdf2image.convert_from_path(file_path)
                text_parts = []
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image, lang=self._language)
                    text_parts.append(text)
                    logger.debug(f"OCR processed page {i + 1}")
                return "\n\n".join(text_parts)
            else:
                # Direct image OCR
                image = Image.open(file_path)
                return pytesseract.image_to_string(image, lang=self._language)

        except ImportError as e:
            logger.error(f"Required OCR dependencies not installed: {e}")
            raise ImportError(
                "OCR requires pytesseract, Pillow, and pdf2image. "
                "Install with: pip install pytesseract Pillow pdf2image. "
                "Also ensure Tesseract is installed on your system."
            )

    def _parse_with_easyocr(self, file_path: Path) -> str:
        """Parse using EasyOCR.

        Args:
            file_path: Path to the file.

        Returns:
            Extracted text.
        """
        try:
            import easyocr

            reader = easyocr.Reader([self._language])
            results = reader.readtext(str(file_path))
            return "\n".join([item[1] for item in results])

        except ImportError:
            raise ImportError(
                "EasyOCR is required. Install with: pip install easyocr"
            )

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