"""Application configuration management."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "HotSwap RAG"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./data/hotswap_rag.db"

    # Paths
    data_dir: Path = Path("./data")
    documents_dir: Path = Path("./data/documents")
    vector_stores_dir: Path = Path("./data/vector_stores")

    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # Vector Store Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # Default Components
    default_parser: str = "pdf"
    default_store: str = "chromadb"
    default_llm: str = "openai"
    default_embedding_model: str = "text-embedding-3-small"
    embedding_model: str = "text-embedding-3-small"  # Alias for compatibility

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.vector_stores_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()