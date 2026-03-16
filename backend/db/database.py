"""SQLAlchemy database configuration."""

import logging
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "hotswap_rag.db"

# Create engine
engine = create_engine(
    f"sqlite:///{DEFAULT_DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        Database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database, creating all tables."""
    from backend.db.models import KnowledgeBase, Document, Config

    # Ensure data directory exists
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized at {DEFAULT_DB_PATH}")