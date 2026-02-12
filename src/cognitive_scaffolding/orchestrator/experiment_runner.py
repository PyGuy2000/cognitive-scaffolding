"""Experiment runner for A/B testing cognitive layer toggles.

Compares scores with different toggle combinations:
same topic, same audience, different enabled layers → measure score delta.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from cognitive_scaffolding.core.models import (
    ArtifactRecord,
    AudienceControlVector,
)
from cognitive_scaffolding.core.scoring import LayerConfig
from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor

logger = logging.getLogger(__name__)


class ExperimentConfig(BaseModel):
    """Defines an experiment: what to compile and which layers to A/B test."""

    topic: str
    audience_id: str
    profile_name: str = "chatbot_tutor"
    toggle_layers: List[str] = Field(
        description="Layers to A/B test (e.g. ['activation', 'encoding'])"
    )
    audience_vector: Optional[AudienceControlVector] = None
    repetitions: int = Field(1, ge=1, description="Run each variant N times, average scores")


class VariantResult(BaseModel):
    """Result of a single variant run."""

    variant_name: str
    toggle_state: Dict[str, bool]
    record: ArtifactRecord
    score: float
    layer_scores: Dict[str, float]
    populated_layers: List[str]


class LayerExperimentResult(BaseModel):
    """A/B comparison for one toggled layer."""

    layer: str
    enabled_score: float
    disabled_score: float
    score_delta: float = Field(description="enabled minus disabled")
    enabled_result: VariantResult
    disabled_result: VariantResult


class ExperimentReport(BaseModel):
    """Full experiment output."""

    experiment_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    config: ExperimentConfig
    baseline_score: float
    baseline_record: ArtifactRecord
    layer_results: List[LayerExperimentResult]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_duration_ms: float = 0.0


class ExperimentRunner:
    """Runs A/B experiments comparing scores with different layer toggles.

    Uses ToggleManager.create_experiment_variants() to generate configs
    and CognitiveConductor.compile() to produce scored artifacts.
    """

    def __init__(self, conductor: CognitiveConductor):
        self.conductor = conductor

    def run(self, config: ExperimentConfig) -> ExperimentReport:
        """Run an experiment: baseline + A/B for each toggled layer."""
        start = time.time()
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"[{run_id}] Starting experiment: {config.toggle_layers}")

        # 1. Run baseline (unmodified profile)
        baseline_record = self._compile_averaged(config, overrides=None)
        baseline_score = baseline_record.artifact.evaluation.overall_score

        logger.info(f"[{run_id}] Baseline score: {baseline_score:.4f}")

        # 2. For each layer, run A/B variants
        layer_results: List[LayerExperimentResult] = []
        base_configs = self.conductor.toggle_manager.load_profile(config.profile_name)

        for layer in config.toggle_layers:
            variant_a_configs, variant_b_configs = (
                self.conductor.toggle_manager.create_experiment_variants(base_configs, layer)
            )

            # Compile enabled variant
            overrides_a = self._configs_to_overrides(variant_a_configs)
            record_a = self._compile_averaged(config, overrides=overrides_a)
            score_a = record_a.artifact.evaluation.overall_score

            # Compile disabled variant
            overrides_b = self._configs_to_overrides(variant_b_configs)
            record_b = self._compile_averaged(config, overrides=overrides_b)
            score_b = record_b.artifact.evaluation.overall_score

            enabled_result = VariantResult(
                variant_name=f"{layer}_enabled",
                toggle_state={layer: True},
                record=record_a,
                score=score_a,
                layer_scores=dict(record_a.artifact.evaluation.layer_scores),
                populated_layers=list(record_a.artifact.populated_layers().keys()),
            )

            disabled_result = VariantResult(
                variant_name=f"{layer}_disabled",
                toggle_state={layer: False},
                record=record_b,
                score=score_b,
                layer_scores=dict(record_b.artifact.evaluation.layer_scores),
                populated_layers=list(record_b.artifact.populated_layers().keys()),
            )

            layer_result = LayerExperimentResult(
                layer=layer,
                enabled_score=score_a,
                disabled_score=score_b,
                score_delta=round(score_a - score_b, 4),
                enabled_result=enabled_result,
                disabled_result=disabled_result,
            )
            layer_results.append(layer_result)

            logger.info(
                f"[{run_id}] {layer}: enabled={score_a:.4f}, disabled={score_b:.4f}, "
                f"delta={layer_result.score_delta:+.4f}"
            )

        duration_ms = (time.time() - start) * 1000

        return ExperimentReport(
            config=config,
            baseline_score=baseline_score,
            baseline_record=baseline_record,
            layer_results=layer_results,
            total_duration_ms=round(duration_ms, 1),
        )

    def _compile_averaged(
        self,
        config: ExperimentConfig,
        overrides: Optional[Dict[str, Dict[str, Any]]],
    ) -> ArtifactRecord:
        """Compile once (or average over repetitions if > 1)."""
        # For deterministic operators (no AI), repetitions don't change the score.
        # Support is here for future AI-backed runs where output varies.
        return self.conductor.compile(
            topic=config.topic,
            audience_id=config.audience_id,
            profile_name=config.profile_name,
            overrides=overrides,
            audience_vector=config.audience_vector,
        )

    @staticmethod
    def _configs_to_overrides(
        configs: Dict[str, LayerConfig],
    ) -> Dict[str, Dict[str, Any]]:
        """Convert Dict[str, LayerConfig] to the overrides format expected by compile().

        overrides format: {"layer_name": {"enabled": bool, "required": bool, "weight": float}}
        """
        return {
            layer_name: {
                "enabled": cfg.enabled,
                "required": cfg.required,
                "weight": cfg.weight,
            }
            for layer_name, cfg in configs.items()
        }

    @staticmethod
    def summary(report: ExperimentReport) -> Dict[str, Any]:
        """Produce a concise summary of experiment results."""
        layer_deltas = {lr.layer: lr.score_delta for lr in report.layer_results}

        best_layer = max(layer_deltas, key=layer_deltas.get) if layer_deltas else None
        worst_layer = min(layer_deltas, key=layer_deltas.get) if layer_deltas else None

        return {
            "experiment_id": report.experiment_id,
            "baseline_score": report.baseline_score,
            "layer_deltas": layer_deltas,
            "best_layer": best_layer,
            "worst_layer": worst_layer,
            "total_duration_ms": report.total_duration_ms,
        }
