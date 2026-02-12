"""Targeted regeneration of weak layers.

After initial compilation, if any layers score below a threshold,
re-run those specific operators with enriched context.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cognitive_scaffolding.core.models import ArtifactRecord, LayerName
from cognitive_scaffolding.core.scoring import LayerConfig, score_artifact

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD = 0.5


def regenerate_weak_layers(
    record: ArtifactRecord,
    layer_configs: Dict[str, LayerConfig],
    conductor,  # CognitiveConductor - avoid circular import
    threshold: float = DEFAULT_THRESHOLD,
) -> ArtifactRecord:
    """Re-run operators for layers scoring below threshold.

    Args:
        record: The artifact record to improve
        layer_configs: Layer configurations from the profile
        conductor: The CognitiveConductor instance to use for re-execution
        threshold: Minimum acceptable confidence score

    Returns:
        Updated ArtifactRecord with improved layers
    """
    artifact = record.artifact
    evaluation = artifact.evaluation
    if evaluation is None:
        return record

    weak_layers = [
        layer_name
        for layer_name, score in evaluation.layer_scores.items()
        if score < threshold and layer_configs.get(layer_name, LayerConfig(enabled=False)).enabled
    ]

    if not weak_layers:
        logger.info("No weak layers to regenerate")
        return record

    logger.info(f"Regenerating weak layers: {weak_layers}")
    score_before = evaluation.overall_score
    context = artifact.context_dict()

    for layer_name_str in weak_layers:
        try:
            layer = LayerName(layer_name_str)
            # Get the operator class path from the standard mapping
            from cognitive_scaffolding.orchestrator.call_plan import CallPlan
            plan = CallPlan.from_layer_configs(layer_configs)
            step = next((s for s in plan.steps if s.layer == layer), None)
            if step is None:
                continue

            operator = conductor._get_operator(step.operator_class)
            output = operator.execute(
                artifact.topic,
                artifact.audience,
                context,
                {"regeneration": True, **step.config},
            )
            artifact.set_layer(layer, output)
            context[layer_name_str] = output.content
            logger.info(f"Regenerated {layer_name_str}: confidence={output.confidence:.2f}")
        except Exception as e:
            logger.error(f"Failed to regenerate {layer_name_str}: {e}")

    # Re-score
    new_eval = score_artifact(artifact, layer_configs)
    artifact.evaluation = new_eval

    record.add_revision(
        changed_layers=weak_layers,
        reason=f"Regenerated layers below threshold ({threshold})",
        score_before=score_before,
        score_after=new_eval.overall_score,
    )

    return record
