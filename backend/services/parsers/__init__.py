"""Document parser implementations."""

from backend.services.parsers.pdf_parser import PDFParser
from backend.services.parsers.docx_parser import DocxParser
from backend.services.parsers.ocr_parser import OCRParser

__all__ = ["PDFParser", "DocxParser", "OCRParser"]