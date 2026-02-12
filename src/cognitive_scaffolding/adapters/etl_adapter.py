"""ETL adapter - formats CognitiveArtifact as structured records.

Designed for data pipeline ingestion with flat, queryable fields.
"""

from typing import Any, Dict, List

from cognitive_scaffolding.adapters.base import BaseAdapter
from cognitive_scaffolding.core.models import ArtifactRecord, LayerName


class ETLAdapter(BaseAdapter):
    """Formats artifacts as flat structured records for data pipelines."""

    def format(self, record: ArtifactRecord) -> Dict[str, Any]:
        """Convert artifact to a flat dictionary suitable for ETL pipelines.

        Returns a single dict with all fields flattened for database/warehouse ingestion.
        """
        artifact = record.artifact
        evaluation = artifact.evaluation

        result: Dict[str, Any] = {
            "artifact_id": artifact.artifact_id,
            "record_id": record.record_id,
            "topic": artifact.topic,
            "audience_id": artifact.audience.audience_id,
            "audience_name": artifact.audience.name,
            "expertise_level": artifact.audience.expertise_level,
            "profile_name": record.profile_name,
            "revision": record.current_revision,
            "created_at": artifact.created_at.isoformat(),
            "updated_at": artifact.updated_at.isoformat(),
        }

        # Control vector as flat fields
        cv = artifact.audience.control_vector
        result["cv_language_level"] = cv.language_level
        result["cv_abstraction"] = cv.abstraction
        result["cv_rigor"] = cv.rigor
        result["cv_math_density"] = cv.math_density
        result["cv_domain_specificity"] = cv.domain_specificity
        result["cv_cognitive_load"] = cv.cognitive_load
        result["cv_transfer_distance"] = cv.transfer_distance

        # Evaluation
        if evaluation:
            result["score"] = evaluation.overall_score
            result["penalty_applied"] = evaluation.penalty_applied
            result["penalty_reason"] = evaluation.penalty_reason
            result["missing_required"] = evaluation.missing_required
        else:
            result["score"] = None
            result["penalty_applied"] = False
            result["penalty_reason"] = None
            result["missing_required"] = []

        # Per-layer data: flatten to layer_<name>_confidence and layer_<name>_populated
        for layer in LayerName:
            output = artifact.get_layer(layer)
            result[f"layer_{layer.value}_populated"] = output is not None
            result[f"layer_{layer.value}_confidence"] = output.confidence if output else None

        # Layer content as JSON strings for warehouse storage
        populated = artifact.populated_layers()
        result["layers_populated"] = list(populated.keys())
        result["num_layers"] = len(populated)

        return result
