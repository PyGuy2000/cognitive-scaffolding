"""Weighted scoring for CognitiveArtifacts.

Score = sum(w_k * x_k) / sum(w_k)

- Disabled layers excluded from both numerator and denominator
- Required layers that are enabled but empty trigger penalty (0.7 multiplier)
"""

from typing import Dict, Optional
from cognitive_scaffolding.core.models import CognitiveArtifact, EvaluationResult, LayerName


REQUIRED_PENALTY = 0.7


class LayerConfig:
    """Configuration for a single layer in a profile."""
    def __init__(self, enabled: bool = True, required: bool = False, weight: float = 1.0):
        self.enabled = enabled
        self.required = required
        self.weight = weight


def score_artifact(
    artifact: CognitiveArtifact,
    layer_configs: Dict[str, LayerConfig],
) -> EvaluationResult:
    """Score an artifact based on its populated layers and profile configuration.

    Args:
        artifact: The cognitive artifact to score
        layer_configs: Per-layer configuration (enabled, required, weight)

    Returns:
        EvaluationResult with overall score and per-layer breakdown
    """
    numerator = 0.0
    denominator = 0.0
    layer_scores: Dict[str, float] = {}
    weights_used: Dict[str, float] = {}
    missing_required: list[str] = []
    penalty_applied = False
    penalty_reason = None

    for layer in LayerName:
        config = layer_configs.get(layer.value, LayerConfig(enabled=False))

        if not config.enabled:
            continue

        output = artifact.get_layer(layer)
        weight = config.weight

        if output is not None:
            confidence = output.confidence
            layer_scores[layer.value] = confidence
            numerator += weight * confidence
            denominator += weight
            weights_used[layer.value] = weight
        else:
            # Enabled but empty
            layer_scores[layer.value] = 0.0
            weights_used[layer.value] = weight
            if config.required:
                missing_required.append(layer.value)
            # Still include in denominator (it was expected)
            denominator += weight

    if denominator == 0.0:
        overall = 0.0
    else:
        overall = numerator / denominator

    # Apply penalty if any required layers are missing
    if missing_required:
        penalty_applied = True
        penalty_reason = f"Missing required layers: {', '.join(missing_required)}"
        overall *= REQUIRED_PENALTY

    return EvaluationResult(
        overall_score=round(overall, 4),
        layer_scores=layer_scores,
        penalty_applied=penalty_applied,
        penalty_reason=penalty_reason,
        missing_required=missing_required,
        weights_used=weights_used,
    )
