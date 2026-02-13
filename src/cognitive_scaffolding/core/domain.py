"""Domain model - adapted from metaphor-mcp-server."""

from pydantic import BaseModel, ConfigDict, Field
from typing import List


class Domain(BaseModel):
    """Model for a metaphor domain loaded from YAML."""
    model_config = ConfigDict(extra="allow")
    domain_id: str
    name: str
    description: str = ""
    metaphor_types: List[str] = Field(default_factory=lambda: ["analogy", "comparison"])
    vocabulary: List[str] = Field(default_factory=lambda: ["like", "similar to", "think of"])
    suitable_for: List[str] = Field(default_factory=lambda: ["all"])
