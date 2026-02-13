"""Audience model - adapted from metaphor-mcp-server."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List


class Audience(BaseModel):
    """Model for an audience definition loaded from YAML."""
    model_config = ConfigDict(extra="allow")
    audience_id: str
    name: str
    description: str = ""
    age_range: str = "18-65"
    expertise_level: str = "intermediate"
    preferred_analogies: List[str] = Field(default_factory=lambda: ["everyday objects"])
    complexity_preference: str = "medium"
    attention_span: str = "medium"
