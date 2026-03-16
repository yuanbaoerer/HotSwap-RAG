"""Tests for document parsers."""

import pytest
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPDFParser:
    """Tests for PDF parser."""

    def test_supported_formats(self):
        """Test that PDF parser returns correct formats."""
        from backend.services.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        assert ".pdf" in parser.supported_formats()

    def test_name_property(self):
        """Test parser name."""
        from backend.services.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        assert parser.name == "PDF Parser"


class TestDocxParser:
    """Tests for DOCX parser."""

    def test_supported_formats(self):
        """Test that DOCX parser returns correct formats."""
        from backend.services.parsers.docx_parser import DocxParser

        parser = DocxParser()
        assert ".docx" in parser.supported_formats()


class TestOCRParser:
    """Tests for OCR parser."""

    def test_supported_formats(self):
        """Test that OCR parser returns correct formats."""
        from backend.services.parsers.ocr_parser import OCRParser

        parser = OCRParser()
        formats = parser.supported_formats()
        assert ".pdf" in formats
        assert ".png" in formats
        assert ".jpg" in formats