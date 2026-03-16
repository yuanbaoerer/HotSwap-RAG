"""API dependencies for dependency injection."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.utils.config import settings

# Database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        Database session.

    Example:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()