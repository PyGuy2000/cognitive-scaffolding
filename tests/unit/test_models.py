"""Unit tests for core models."""

import pytest
from cognitive_scaffolding.core.models import (
    ArtifactRecord,
    AudienceControlVector,
    AudienceProfile,
    CognitiveArtifact,
    EvaluationResult,
    LayerName,
    LayerOutput,
)


class TestAudienceControlVector:
    def test_defaults(self):
        v = AudienceControlVector()
        assert v.language_level == 0.5
        assert v.math_density == 0.0

    def test_as_tuple(self):
        v = AudienceControlVector(language_level=0.1, abstraction=0.2, rigor=0.3,
                                   math_density=0.4, domain_specificity=0.5,
                                   cognitive_load=0.6, transfer_distance=0.7)
        assert v.as_tuple() == (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)

    def test_validation_bounds(self):
        with pytest.raises(Exception):
            AudienceControlVector(language_level=1.5)
        with pytest.raises(Exception):
            AudienceControlVector(rigor=-0.1)


class TestLayerOutput:
    def test_creation(self):
        output = LayerOutput(
            layer=LayerName.ACTIVATION,
            content={"hook": "test hook"},
            confidence=0.8,
        )
        assert output.layer == LayerName.ACTIVATION
        assert output.confidence == 0.8
        assert output.content["hook"] == "test hook"

    def test_default_confidence(self):
        output = LayerOutput(layer=LayerName.METAPHOR)
        assert output.confidence == 0.0


class TestCognitiveArtifact:
    def test_creation(self):
        audience = AudienceProfile(audience_id="child", name="Child")
        artifact = CognitiveArtifact(topic="neural networks", audience=audience)
        assert artifact.topic == "neural networks"
        assert artifact.activation is None

    def test_set_and_get_layer(self):
        audience = AudienceProfile(audience_id="child", name="Child")
        artifact = CognitiveArtifact(topic="test", audience=audience)
        output = LayerOutput(layer=LayerName.ACTIVATION, content={"hook": "hi"}, confidence=0.9)
        artifact.set_layer(LayerName.ACTIVATION, output)
        assert artifact.get_layer(LayerName.ACTIVATION) is not None
        assert artifact.get_layer(LayerName.ACTIVATION).confidence == 0.9

    def test_populated_layers(self):
        audience = AudienceProfile(audience_id="test", name="Test")
        artifact = CognitiveArtifact(topic="test", audience=audience)
        assert len(artifact.populated_layers()) == 0

        artifact.set_layer(LayerName.METAPHOR,
                          LayerOutput(layer=LayerName.METAPHOR, content={"m": "test"}, confidence=0.7))
        artifact.set_layer(LayerName.STRUCTURE,
                          LayerOutput(layer=LayerName.STRUCTURE, content={"s": "test"}, confidence=0.6))
        assert len(artifact.populated_layers()) == 2

    def test_context_dict(self):
        audience = AudienceProfile(audience_id="test", name="Test")
        artifact = CognitiveArtifact(topic="test", audience=audience)
        artifact.set_layer(LayerName.ACTIVATION,
                          LayerOutput(layer=LayerName.ACTIVATION, content={"hook": "hi"}, confidence=0.8))
        ctx = artifact.context_dict()
        assert "activation" in ctx
        assert ctx["activation"]["hook"] == "hi"


class TestArtifactRecord:
    def test_revision_tracking(self):
        audience = AudienceProfile(audience_id="test", name="Test")
        artifact = CognitiveArtifact(topic="test", audience=audience)
        record = ArtifactRecord(artifact=artifact, profile_name="chatbot_tutor")
        assert record.current_revision == 0

        record.add_revision(["activation"], reason="initial", score_after=0.7)
        assert record.current_revision == 1
        assert len(record.revision_history) == 1
        assert record.revision_history[0].score_after == 0.7
