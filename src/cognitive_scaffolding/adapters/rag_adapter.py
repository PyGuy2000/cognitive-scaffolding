"""RAG adapter - formats CognitiveArtifact as enriched document chunks.

Designed for vector store ingestion with rich metadata.
"""

from typing import Any, Dict, List

from cognitive_scaffolding.adapters.base import BaseAdapter
from cognitive_scaffolding.core.models import ArtifactRecord, LayerName


class RAGAdapter(BaseAdapter):
    """Formats artifacts as document chunks with metadata for vector stores."""

    def format(self, record: ArtifactRecord) -> List[Dict[str, Any]]:
        """Convert artifact to a list of document chunks for RAG ingestion.

        Each chunk has 'content', 'metadata', and 'chunk_id'.
        """
        artifact = record.artifact
        chunks: List[Dict[str, Any]] = []

        base_metadata = {
            "topic": artifact.topic,
            "audience_id": artifact.audience.audience_id,
            "expertise_level": artifact.audience.expertise_level,
            "profile": record.profile_name,
            "artifact_id": artifact.artifact_id,
            "score": artifact.evaluation.overall_score if artifact.evaluation else None,
        }

        for layer in LayerName:
            output = artifact.get_layer(layer)
            if output is None:
                continue

            # Create one chunk per significant content field
            for field, value in output.content.items():
                text = self._to_text(value)
                if not text or len(text) < 10:
                    continue

                chunks.append({
                    "chunk_id": f"{artifact.artifact_id}_{layer.value}_{field}",
                    "content": text,
                    "metadata": {
                        **base_metadata,
                        "layer": layer.value,
                        "field": field,
                        "confidence": output.confidence,
                    },
                })

        return chunks

    @staticmethod
    def _to_text(value: Any) -> str:
        """Convert any value to a text string suitable for embedding."""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join(str(item) for item in value)
        if isinstance(value, dict):
            parts = []
            for k, v in value.items():
                parts.append(f"{k}: {v}")
            return "\n".join(parts)
        return str(value) if value else ""
