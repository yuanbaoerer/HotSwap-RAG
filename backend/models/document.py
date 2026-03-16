"""Document-related Pydantic models."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base model for documents."""

    filename: str = Field(..., description="Original filename")
    file_path: Optional[str] = Field(None, description="Path where file is stored")
    file_size: int = Field(0, description="File size in bytes")
    kb_id: Optional[str] = Field(None, description="Knowledge base ID")


class DocumentCreate(DocumentBase):
    """Model for creating a document."""

    pass


class DocumentUpdate(BaseModel):
    """Model for updating a document."""

    filename: Optional[str] = None
    status: Optional[str] = None


class Document(DocumentBase):
    """Full document model."""

    id: str = Field(..., description="Unique document ID")
    status: str = Field("pending", description="Processing status")
    chunk_count: int = Field(0, description="Number of text chunks")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    """Model for a document chunk."""

    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: dict = Field(default_factory=dict)