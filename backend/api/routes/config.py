"""Configuration management API routes."""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel

from backend.factories import get_available_parsers, get_available_stores, get_available_llms

logger = logging.getLogger(__name__)
router = APIRouter()


class ActiveConfig(BaseModel):
    """Model for active configuration."""

    parser_type: str
    store_type: str
    llm_type: str
    llm_model: str


class ConfigOption(BaseModel):
    """Model for configuration option."""

    type: str
    name: str
    description: str = ""


@router.get("/parsers")
async def list_parsers() -> List[ConfigOption]:
    """List available document parsers."""
    parsers = get_available_parsers()
    return [
        ConfigOption(type=k, name=v, description=f"Parser for {k} files")
        for k, v in parsers.items()
    ]


@router.get("/stores")
async def list_stores() -> List[ConfigOption]:
    """List available vector stores."""
    stores = get_available_stores()
    return [
        ConfigOption(type=k, name=k.upper(), description=f"{k} vector database")
        for k in stores.keys()
    ]


@router.get("/llms")
async def list_llms() -> List[ConfigOption]:
    """List available LLM providers."""
    llms = get_available_llms()
    return [
        ConfigOption(type=k, name=k.upper(), description=f"{k} LLM provider")
        for k in llms.keys()
    ]


@router.get("/active", response_model=ActiveConfig)
async def get_active_config():
    """Get the currently active configuration."""
    # TODO: Implement config retrieval from database
    return ActiveConfig(
        parser_type="pdf",
        store_type="chromadb",
        llm_type="openai",
        llm_model="gpt-4o-mini",
    )


@router.put("/active", response_model=ActiveConfig)
async def update_active_config(config: ActiveConfig):
    """Update the active configuration."""
    # TODO: Implement config update
    logger.info(f"Updating active config: {config}")
    return config