"""Configuration-related Pydantic models."""

from typing import Optional

from pydantic import BaseModel, Field


class ParserConfig(BaseModel):
    """Configuration for document parser."""

    type: str = Field("pdf", description="Parser type")
    chunk_size: int = Field(1000, description="Chunk size in characters")
    chunk_overlap: int = Field(200, description="Chunk overlap in characters")


class StoreConfig(BaseModel):
    """Configuration for vector store."""

    type: str = Field("chromadb", description="Store type")
    collection_name: Optional[str] = Field(None, description="Collection name")
    persist_directory: Optional[str] = Field(None, description="Persistence directory")


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""

    type: str = Field("openai", description="LLM provider type")
    model: str = Field("gpt-4o-mini", description="Model name")
    temperature: float = Field(0.7, ge=0, le=2, description="Default temperature")
    max_tokens: Optional[int] = Field(None, description="Default max tokens")


class Config(BaseModel):
    """Full application configuration."""

    parser: ParserConfig = Field(default_factory=ParserConfig)
    store: StoreConfig = Field(default_factory=StoreConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


class ConfigUpdate(BaseModel):
    """Model for updating configuration."""

    parser_type: Optional[str] = None
    store_type: Optional[str] = None
    llm_type: Optional[str] = None
    llm_model: Optional[str] = None


class EnvironmentInfo(BaseModel):
    """Information about the environment."""

    python_version: str
    platform: str
    available_parsers: list[str]
    available_stores: list[str]
    available_llms: list[str]
    api_keys_configured: dict[str, bool]