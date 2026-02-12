"""Unit tests for targeted regeneration of weak layers."""

from pathlib import Path

from cognitive_scaffolding.core.models import (
    ArtifactRecord,
    LayerName,
)
from cognitive_scaffolding.core.scoring import LayerConfig, score_artifact
from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor
from cognitive_scaffolding.orchestrator.regeneration import regenerate_weak_layers


PROFILES_DIR = str(Path(__file__).parent.parent.parent / "profiles")


def _make_conductor() -> CognitiveConductor:
    return CognitiveConductor(ai_client=None, profiles_dir=PROFILES_DIR)


def _all_enabled_configs() -> dict:
    return {
        layer.value: LayerConfig(enabled=True, required=False, weight=1.0)
        for layer in LayerName
    }


def _compile_record(conductor: CognitiveConductor) -> ArtifactRecord:
    return conductor.compile(
        topic="neural networks",
        audience_id="child",
        profile_name="chatbot_tutor",
    )


class TestRegenerateWeakLayers:
    def test_no_evaluation_returns_unchanged(self):
        conductor = _make_conductor()
        record = _compile_record(conductor)
        record.artifact.evaluation = None
        original_rev = record.current_revision

        result = regenerate_weak_layers(record, _all_enabled_configs(), conductor)
        assert result.current_revision == original_rev

    def test_no_weak_layers_returns_unchanged(self):
        conductor = _make_conductor()
        record = _compile_record(conductor)
        original_rev = record.current_revision

        # All layers have confidence > 0 from fallbacks; use a very low threshold
        result = regenerate_weak_layers(record, _all_enabled_configs(), conductor, threshold=0.0)
        assert result.current_revision == original_rev

    def test_weak_layer_gets_regenerated(self):
        conductor = _make_conductor()
        record = _compile_record(conductor)
        original_rev = record.current_revision

        # Force one layer to have very low confidence so it's below threshold
        record.artifact.activation.confidence = 0.1
        # Re-score to pick up the low confidence
        configs = _all_enabled_configs()
        record.artifact.evaluation = score_artifact(record.artifact, configs)

        result = regenerate_weak_layers(record, configs, conductor, threshold=0.5)
        # Should have added a revision
        assert result.current_revision > original_rev
        # The activation layer should have been regenerated
        last_rev = result.revision_history[-1]
        assert "activation" in last_rev.changed_layers

    def test_custom_threshold(self):
        conductor = _make_conductor()
        record = _compile_record(conductor)
        original_rev = record.current_revision

        # With a threshold of 1.0, ALL layers are weak
        configs = _all_enabled_configs()
        result = regenerate_weak_layers(record, configs, conductor, threshold=1.0)
        assert result.current_revision > original_rev
        last_rev = result.revision_history[-1]
        assert len(last_rev.changed_layers) == 7

    def test_disabled_layers_not_regenerated(self):
        conductor = _make_conductor()
        record = _compile_record(conductor)

        configs = _all_enabled_configs()
        # Disable activation
        configs["activation"] = LayerConfig(enabled=False, required=False, weight=1.0)
        # Force low scores to trigger regeneration on enabled layers
        record.artifact.evaluation = score_artifact(record.artifact, configs)

        result = regenerate_weak_layers(record, configs, conductor, threshold=1.0)
        last_rev = result.revision_history[-1]
        assert "activation" not in last_rev.changed_layers
