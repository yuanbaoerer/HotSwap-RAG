"""Tests for document parsers."""

import pytest
from pathlib import Path


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

    def test_chunk_size_default(self):
        """Test default chunk size."""
        from backend.services.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        chunks = parser._split_text("Hello world")
        assert len(chunks) == 1

    def test_supports_format(self):
        """Test format detection."""
        from backend.services.parsers.pdf_parser import PDFParser

        parser = PDFParser()
        assert parser.supports_format(Path("test.pdf")) is True
        assert parser.supports_format(Path("test.txt")) is False


class TestDocxParser:
    """Tests for DOCX parser."""

    def test_supported_formats(self):
        """Test that DOCX parser returns correct formats."""
        from backend.services.parsers.docx_parser import DocxParser

        parser = DocxParser()
        assert ".docx" in parser.supported_formats()

    def test_name_property(self):
        """Test parser name."""
        from backend.services.parsers.docx_parser import DocxParser

        parser = DocxParser()
        assert parser.name == "Word Document Parser"


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

    def test_name_property(self):
        """Test parser name."""
        from backend.services.parsers.ocr_parser import OCRParser

        parser = OCRParser()
        assert "OCR" in parser.name


class TestParserFactory:
    """Tests for parser factory."""

    def test_create_pdf_parser(self):
        """Test creating PDF parser via factory."""
        from backend.factories import create_parser

        parser = create_parser("pdf")
        assert parser.name == "PDF Parser"

    def test_create_docx_parser(self):
        """Test creating DOCX parser via factory."""
        from backend.factories import create_parser

        parser = create_parser("docx")
        assert parser.name == "Word Document Parser"

    def test_create_invalid_parser(self):
        """Test creating invalid parser raises error."""
        from backend.factories import create_parser

        with pytest.raises(ValueError):
            create_parser("invalid")

    def test_get_available_parsers(self):
        """Test getting available parsers."""
        from backend.factories import get_available_parsers

        parsers = get_available_parsers()
        assert "pdf" in parsers
        assert "docx" in parsers
        assert "ocr" in parsers