"""Concept model - adapted from metaphor-mcp-server."""

from pydantic import BaseModel, Field
from typing import List


class Concept(BaseModel):
    """Model for a concept definition loaded from YAML."""
    concept_id: str
    name: str
    category: str = ""
    complexity: str = "medium"
    last_updated: str = ""
    evolution_rate: str = "medium"
    description: str = ""
    key_components: List[str] = Field(default_factory=list)
    properties: List[str] = Field(default_factory=list)
    common_misconceptions: List[str] = Field(default_factory=list)
    prerequisite_concepts: List[str] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
