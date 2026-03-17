"""Configuration management API routes."""

import json
import logging
import os
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
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
API_KEYS_KEY = "api_keys"

# API key field names (stored securely)
API_KEY_FIELDS = [
    "openai_api_key",
    "anthropic_api_key",
    "pinecone_api_key",
    "pinecone_environment",
    "ollama_base_url",
    "milvus_host",
    "milvus_port",
]


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


class APIKeysConfig(BaseModel):
    """Model for API keys configuration."""

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    ollama_base_url: Optional[str] = "http://localhost:11434"
    milvus_host: Optional[str] = "localhost"
    milvus_port: Optional[int] = 19530


class APIKeyUpdate(BaseModel):
    """Model for updating a single API key."""

    key_name: str
    key_value: str


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


def get_api_keys_from_db(db: Session) -> Dict[str, Any]:
    """Get API keys from database.

    Args:
        db: Database session.

    Returns:
        API keys dictionary.
    """
    config_row = db.query(Config).filter(Config.key == API_KEYS_KEY).first()

    if config_row and config_row.value:
        try:
            return json.loads(config_row.value)
        except json.JSONDecodeError:
            logger.warning("Failed to parse API keys JSON")

    return {}


def save_api_keys_to_db(db: Session, api_keys: Dict[str, Any]) -> None:
    """Save API keys to database.

    Args:
        db: Database session.
        api_keys: API keys dictionary.
    """
    config_row = db.query(Config).filter(Config.key == API_KEYS_KEY).first()

    # Only store non-empty values
    filtered_keys = {k: v for k, v in api_keys.items() if v}
    config_json = json.dumps(filtered_keys)

    if config_row:
        config_row.value = config_json
    else:
        config_row = Config(key=API_KEYS_KEY, value=config_json)
        db.add(config_row)

    db.commit()


def mask_api_key(key: str) -> str:
    """Mask an API key for display.

    Args:
        key: The API key to mask.

    Returns:
        Masked key (e.g., "sk-...abc123").
    """
    if not key or len(key) < 8:
        return ""
    return f"{key[:4]}...{key[-4:]}"


def get_env_with_fallback(db: Session, key: str) -> Optional[str]:
    """Get a value from DB first, fallback to environment variable.

    Args:
        db: Database session.
        key: The key to look up.

    Returns:
        The value or None.
    """
    # First check database
    api_keys = get_api_keys_from_db(db)
    if api_keys.get(key):
        return api_keys[key]

    # Fallback to environment variable
    return os.environ.get(key.upper())


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

    return config


@router.post("/reset")
async def reset_config(db: Session = Depends(get_db)):
    """Reset configuration to defaults."""
    logger.info("Resetting configuration to defaults")

    save_config_to_db(db, DEFAULT_CONFIG.copy())

    return {"status": "reset", "config": DEFAULT_CONFIG}


# API Keys management endpoints

@router.get("/api-keys")
async def get_api_keys(db: Session = Depends(get_db)):
    """Get API keys (masked for security).

    Returns the keys with masked values and status indicators.
    """
    api_keys = get_api_keys_from_db(db)

    result = {}
    for field in API_KEY_FIELDS:
        env_value = os.environ.get(field.upper())
        db_value = api_keys.get(field)

        # Prefer DB value over env value
        value = db_value or env_value

        result[field] = {
            "configured": bool(value),
            "masked_value": mask_api_key(value) if value else None,
            "source": "database" if db_value else ("environment" if env_value else None),
        }

    return result


@router.put("/api-keys")
async def update_api_keys(
    api_keys: APIKeysConfig,
    db: Session = Depends(get_db),
):
    """Update API keys in database.

    Only non-empty values will be stored.
    Empty strings will remove the key from storage.
    """
    logger.info("Updating API keys")

    # Get current keys
    current_keys = get_api_keys_from_db(db)

    # Update with new values
    update_data = api_keys.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if value == "" or value is None:
            # Remove empty keys
            current_keys.pop(key, None)
        else:
            current_keys[key] = value

    save_api_keys_to_db(db, current_keys)

    return {"status": "success", "message": "API keys updated"}


@router.delete("/api-keys/{key_name}")
async def delete_api_key(
    key_name: str,
    db: Session = Depends(get_db),
):
    """Delete a specific API key from database."""
    if key_name not in API_KEY_FIELDS:
        raise HTTPException(status_code=400, detail=f"Unknown key: {key_name}")

    current_keys = get_api_keys_from_db(db)

    if key_name in current_keys:
        del current_keys[key_name]
        save_api_keys_to_db(db, current_keys)
        return {"status": "deleted", "key": key_name}

    return {"status": "not_found", "key": key_name}


@router.get("/api-keys/{key_name}")
async def get_api_key(
    key_name: str,
    db: Session = Depends(get_db),
):
    """Get a specific API key value (for internal use by other services).

    This endpoint returns the actual key value, not masked.
    Should be used internally, not exposed to frontend.
    """
    if key_name not in API_KEY_FIELDS:
        raise HTTPException(status_code=400, detail=f"Unknown key: {key_name}")

    value = get_env_with_fallback(db, key_name)

    return {
        "key_name": key_name,
        "value": value,
        "configured": bool(value),
    }