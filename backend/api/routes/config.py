"""Configuration management API routes."""

import json
import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.db.models import Config
from backend.factories import get_available_parsers, get_available_stores, get_available_llms

logger = logging.getLogger(__name__)
router = APIRouter()

# Default configuration
DEFAULT_CONFIG = {
    "parser_type": "pdf",
    "store_type": "chromadb",
    "llm_type": "openai",
    "llm_model": "gpt-4o-mini",
}

# Config keys
CONFIG_KEY = "active_config"


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


def get_config_from_db(db: Session) -> Dict[str, Any]:
    """Get configuration from database.

    Args:
        db: Database session.

    Returns:
        Configuration dictionary.
    """
    config_row = db.query(Config).filter(Config.key == CONFIG_KEY).first()

    if config_row and config_row.value:
        try:
            return json.loads(config_row.value)
        except json.JSONDecodeError:
            logger.warning("Failed to parse config JSON, using defaults")

    return DEFAULT_CONFIG.copy()


def save_config_to_db(db: Session, config: Dict[str, Any]) -> None:
    """Save configuration to database.

    Args:
        db: Database session.
        config: Configuration dictionary.
    """
    config_row = db.query(Config).filter(Config.key == CONFIG_KEY).first()

    config_json = json.dumps(config)

    if config_row:
        config_row.value = config_json
    else:
        config_row = Config(key=CONFIG_KEY, value=config_json)
        db.add(config_row)

    db.commit()


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
async def get_active_config(db: Session = Depends(get_db)):
    """Get the currently active configuration from database."""
    config = get_config_from_db(db)

    return ActiveConfig(
        parser_type=config.get("parser_type", DEFAULT_CONFIG["parser_type"]),
        store_type=config.get("store_type", DEFAULT_CONFIG["store_type"]),
        llm_type=config.get("llm_type", DEFAULT_CONFIG["llm_type"]),
        llm_model=config.get("llm_model", DEFAULT_CONFIG["llm_model"]),
    )


@router.put("/active", response_model=ActiveConfig)
async def update_active_config(
    config: ActiveConfig,
    db: Session = Depends(get_db),
):
    """Update the active configuration and persist to database."""
    logger.info(f"Updating active config: {config}")

    # Convert to dict and save
    config_dict = {
        "parser_type": config.parser_type,
        "store_type": config.store_type,
        "llm_type": config.llm_type,
        "llm_model": config.llm_model,
    }

    try:
        save_config_to_db(db, config_dict)
        logger.info("Configuration saved to database")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        # Still return the config even if save fails
        # In production, you might want to raise an error

    return config


@router.post("/reset")
async def reset_config(db: Session = Depends(get_db)):
    """Reset configuration to defaults."""
    logger.info("Resetting configuration to defaults")

    save_config_to_db(db, DEFAULT_CONFIG.copy())

    return {"status": "reset", "config": DEFAULT_CONFIG}