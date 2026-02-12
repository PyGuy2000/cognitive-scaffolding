"""YAML loading utilities - adapted from metaphor-mcp-server."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def safe_load_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely load a YAML file, returning None on error."""
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        if not data:
            logger.warning(f"Empty YAML file: {file_path.name}")
            return None
        return data
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return None


def load_yaml_as_model(file_path: Path, model_class: Type[BaseModel]) -> Optional[BaseModel]:
    """Load a YAML file and instantiate as a Pydantic model."""
    data = safe_load_yaml(file_path)
    if data is None:
        return None
    try:
        return model_class(**data)
    except Exception as e:
        logger.warning(f"Invalid {model_class.__name__} in {file_path.name}: {e}")
        return None
