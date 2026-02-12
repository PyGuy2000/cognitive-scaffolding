"""Unit tests for scoring module."""

from cognitive_scaffolding.core.models import (
    AudienceProfile,
    CognitiveArtifact,
    LayerName,
    LayerOutput,
)
from cognitive_scaffolding.core.scoring import LayerConfig, score_artifact


def _make_artifact(*layers_with_confidence):
    """Helper to create an artifact with specified layers and confidences."""
    audience = AudienceProfile(audience_id="test", name="Test")
    artifact = CognitiveArtifact(topic="test", audience=audience)
    for layer_name, confidence in layers_with_confidence:
        artifact.set_layer(
            layer_name,
            LayerOutput(layer=layer_name, content={"data": "test"}, confidence=confidence),
        )
    return artifact


class TestScoring:
    def test_empty_artifact(self):
        artifact = _make_artifact()
        configs = {
            "activation": LayerConfig(enabled=True, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        assert result.overall_score == 0.0

    def test_single_layer(self):
        artifact = _make_artifact((LayerName.ACTIVATION, 0.8))
        configs = {
            "activation": LayerConfig(enabled=True, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        assert result.overall_score == 0.8

    def test_weighted_average(self):
        artifact = _make_artifact(
            (LayerName.ACTIVATION, 0.8),
            (LayerName.METAPHOR, 0.6),
        )
        configs = {
            "activation": LayerConfig(enabled=True, weight=2.0),
            "metaphor": LayerConfig(enabled=True, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        # (2.0*0.8 + 1.0*0.6) / (2.0 + 1.0) = 2.2/3.0 = 0.7333
        assert abs(result.overall_score - 0.7333) < 0.01

    def test_disabled_layers_excluded(self):
        artifact = _make_artifact(
            (LayerName.ACTIVATION, 0.8),
            (LayerName.METAPHOR, 0.2),  # present but disabled
        )
        configs = {
            "activation": LayerConfig(enabled=True, weight=1.0),
            "metaphor": LayerConfig(enabled=False, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        assert result.overall_score == 0.8
        assert "metaphor" not in result.layer_scores

    def test_required_missing_penalty(self):
        artifact = _make_artifact((LayerName.METAPHOR, 0.8))
        configs = {
            "activation": LayerConfig(enabled=True, required=True, weight=1.0),
            "metaphor": LayerConfig(enabled=True, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        assert result.penalty_applied is True
        assert "activation" in result.missing_required
        # Score = (0 + 0.8) / 2 * 0.7 = 0.28
        assert abs(result.overall_score - 0.28) < 0.01

    def test_all_layers_populated(self):
        artifact = _make_artifact(
            (LayerName.ACTIVATION, 0.9),
            (LayerName.METAPHOR, 0.8),
            (LayerName.STRUCTURE, 0.7),
        )
        configs = {
            "activation": LayerConfig(enabled=True, required=True, weight=1.0),
            "metaphor": LayerConfig(enabled=True, weight=1.0),
            "structure": LayerConfig(enabled=True, weight=1.0),
        }
        result = score_artifact(artifact, configs)
        assert result.penalty_applied is False
        expected = (0.9 + 0.8 + 0.7) / 3
        assert abs(result.overall_score - expected) < 0.01

    def test_no_enabled_layers(self):
        artifact = _make_artifact()
        configs = {
            "activation": LayerConfig(enabled=False),
        }
        result = score_artifact(artifact, configs)
        assert result.overall_score == 0.0
