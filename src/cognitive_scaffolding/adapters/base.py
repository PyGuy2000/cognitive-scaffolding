"""Base adapter - ABC for all integration adapters."""

from abc import ABC, abstractmethod
from typing import Any

from cognitive_scaffolding.core.models import ArtifactRecord


class BaseAdapter(ABC):
    """Abstract base for integration adapters.

    Adapters format a CognitiveArtifact/ArtifactRecord into the output
    format expected by the target integration (chatbot, RAG, ETL).
    """

    @abstractmethod
    def format(self, record: ArtifactRecord) -> Any:
        """Format the artifact record for the target integration."""
        ...
