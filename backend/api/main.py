"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import documents, chat, knowledge_base, config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting HotSwap RAG API server")
    yield
    logger.info("Shutting down HotSwap RAG API server")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="HotSwap RAG API",
        description="API for HotSwap RAG - A hot-swappable document Q&A system",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(knowledge_base.router, prefix="/api/knowledge-bases", tags=["knowledge-bases"])
    app.include_router(config.router, prefix="/api/config", tags=["config"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )