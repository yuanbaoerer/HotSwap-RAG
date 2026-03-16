"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.db.database import Base


class KnowledgeBase(Base):
    """Knowledge base model for organizing documents."""

    __tablename__ = "knowledge_bases"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parser_type = Column(String(50), default="pdf")
    store_type = Column(String(50), default="chromadb")
    llm_type = Column(String(50), default="openai")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    """Document model for storing uploaded files."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    kb_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


class Config(Base):
    """Configuration model for storing app settings."""

    __tablename__ = "configs"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)