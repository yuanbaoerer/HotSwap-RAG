"""Knowledge base management API routes."""

import logging
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.api.dependencies import get_db
from backend.db.models import KnowledgeBase, Document

logger = logging.getLogger(__name__)
router = APIRouter()


class KnowledgeBaseCreate(BaseModel):
    """Request model for creating a knowledge base."""

    name: str
    description: Optional[str] = None
    parser_type: str = "pdf"
    store_type: str = "chromadb"
    llm_type: str = "openai"


class KnowledgeBaseUpdate(BaseModel):
    """Request model for updating a knowledge base."""

    name: Optional[str] = None
    description: Optional[str] = None
    parser_type: Optional[str] = None
    store_type: Optional[str] = None
    llm_type: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """Response model for knowledge base."""

    id: str
    name: str
    description: Optional[str]
    parser_type: str
    store_type: str
    llm_type: str
    document_count: int
    created_at: str
    updated_at: str


class KnowledgeBaseListResponse(BaseModel):
    """Response model for knowledge base list."""

    knowledge_bases: List[KnowledgeBaseResponse]
    total: int


def kb_to_response(kb: KnowledgeBase, document_count: int = 0) -> KnowledgeBaseResponse:
    """Convert KnowledgeBase model to response model.

    Args:
        kb: KnowledgeBase database model.
        document_count: Number of documents in the knowledge base.

    Returns:
        KnowledgeBaseResponse model.
    """
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        parser_type=kb.parser_type,
        store_type=kb.store_type,
        llm_type=kb.llm_type,
        document_count=document_count,
        created_at=kb.created_at.isoformat() if kb.created_at else "",
        updated_at=kb.updated_at.isoformat() if kb.updated_at else "",
    )


@router.get("/", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all knowledge bases with document counts."""
    # Get total count
    total = db.query(KnowledgeBase).count()

    # Get knowledge bases with document counts
    kbs = db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).offset(skip).limit(limit).all()

    # Build response with document counts
    kb_responses = []
    for kb in kbs:
        doc_count = db.query(Document).filter(Document.kb_id == kb.id).count()
        kb_responses.append(kb_to_response(kb, doc_count))

    return KnowledgeBaseListResponse(knowledge_bases=kb_responses, total=total)


@router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
):
    """Create a new knowledge base."""
    logger.info(f"Creating knowledge base: {request.name}")

    # Generate ID
    kb_id = str(uuid.uuid4())

    # Create knowledge base
    kb = KnowledgeBase(
        id=kb_id,
        name=request.name,
        description=request.description,
        parser_type=request.parser_type,
        store_type=request.store_type,
        llm_type=request.llm_type,
    )

    try:
        db.add(kb)
        db.commit()
        db.refresh(kb)
        logger.info(f"Created knowledge base: {kb_id}")
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create knowledge base: {e}")

    return kb_to_response(kb, 0)


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db),
):
    """Get knowledge base details by ID."""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Get document count
    doc_count = db.query(Document).filter(Document.kb_id == kb_id).count()

    return kb_to_response(kb, doc_count)


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
):
    """Update knowledge base settings."""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Update fields if provided
    if request.name is not None:
        kb.name = request.name
    if request.description is not None:
        kb.description = request.description
    if request.parser_type is not None:
        kb.parser_type = request.parser_type
    if request.store_type is not None:
        kb.store_type = request.store_type
    if request.llm_type is not None:
        kb.llm_type = request.llm_type

    kb.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(kb)
        logger.info(f"Updated knowledge base: {kb_id}")
    except Exception as e:
        logger.error(f"Failed to update knowledge base: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update knowledge base: {e}")

    # Get document count
    doc_count = db.query(Document).filter(Document.kb_id == kb_id).count()

    return kb_to_response(kb, doc_count)


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db),
):
    """Delete a knowledge base and all its documents.

    This will:
    1. Delete all documents associated with the knowledge base
    2. Delete the knowledge base record
    3. Note: Vector store data should be cleaned up separately if needed
    """
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Get documents to delete their files
    documents = db.query(Document).filter(Document.kb_id == kb_id).all()

    # Delete document files
    from pathlib import Path
    deleted_files = 0
    for doc in documents:
        if doc.file_path:
            file_path = Path(doc.file_path)
            if file_path.exists():
                file_path.unlink()
                deleted_files += 1

    # Delete knowledge base (documents will be cascade deleted)
    try:
        db.delete(kb)
        db.commit()
        logger.info(f"Deleted knowledge base: {kb_id}, removed {deleted_files} files")
    except Exception as e:
        logger.error(f"Failed to delete knowledge base: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge base: {e}")

    return {
        "status": "deleted",
        "id": kb_id,
        "documents_removed": len(documents),
        "files_deleted": deleted_files,
    }