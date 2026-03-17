"""Document management API routes."""

import logging
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.db.models import Document
from backend.utils.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class DocumentResponse(BaseModel):
    """Response model for document operations."""

    id: str
    filename: str
    status: str
    size: int
    file_type: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response model for document list."""

    documents: List[DocumentResponse]
    total: int


def process_document(document_id: str, file_path: Path, db_url: str):
    """Background task to process a document.

    Args:
        document_id: Document ID in database.
        file_path: Path to the uploaded file.
        db_url: Database URL for creating new session.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                logger.error(f"Document not found: {document_id}")
                return

            doc.status = "processing"
            db.commit()

            # TODO: Parse document and add to vector store
            # For now, just mark as completed
            doc.status = "completed"
            doc.chunk_count = 0
            db.commit()

            logger.info(f"Document processed: {document_id}")

        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)
                db.commit()


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    kb_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all documents, optionally filtered by knowledge base."""
    query = db.query(Document)

    if kb_id:
        query = query.filter(Document.kb_id == kb_id)

    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                status=doc.status,
                size=doc.file_size,
                file_type=doc.file_type,
                created_at=doc.created_at.isoformat() if doc.created_at else "",
            )
            for doc in documents
        ],
        total=total,
    )


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    kb_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Upload a document for processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    logger.info(f"Uploading document: {file.filename}")

    # Generate document ID
    doc_id = str(uuid.uuid4())

    # Determine file type
    file_ext = Path(file.filename).suffix.lower()
    file_type = file_ext.lstrip(".") if file_ext else "unknown"

    # Create documents directory if not exists
    documents_dir = settings.documents_dir
    documents_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = documents_dir / f"{doc_id}{file_ext}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Create database record
    doc = Document(
        id=doc_id,
        kb_id=kb_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_type=file_type,
        status="uploaded",
    )

    try:
        db.add(doc)
        db.commit()
        db.refresh(doc)
    except Exception as e:
        logger.error(f"Failed to create document record: {e}")
        # Clean up file
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to create document record: {e}")

    # Schedule background processing
    background_tasks.add_task(
        process_document,
        doc_id,
        file_path,
        settings.database_url,
    )

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        size=doc.file_size,
        file_type=doc.file_type,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get document details by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        size=doc.file_size,
        file_type=doc.file_type,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    file_path = Path(doc.file_path) if doc.file_path else None
    if file_path and file_path.exists():
        file_path.unlink()

    # Delete database record
    db.delete(doc)
    db.commit()

    return {"status": "deleted", "id": document_id}