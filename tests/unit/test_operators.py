"""Unit tests for operators."""

import json

import pytest
from cognitive_scaffolding.core.models import AudienceControlVector, AudienceProfile, LayerName
from cognitive_scaffolding.operators.activation import ActivationOperator
from cognitive_scaffolding.operators.metaphor import MetaphorOperator
from cognitive_scaffolding.operators.structure import StructureOperator
from cognitive_scaffolding.operators.interrogation import InterrogationOperator
from cognitive_scaffolding.operators.encoding import EncodingOperator
from cognitive_scaffolding.operators.transfer import TransferOperator
from cognitive_scaffolding.operators.reflection import ReflectionOperator
from cognitive_scaffolding.operators.grading import GradingOperator


@pytest.fixture
def audience():
    return AudienceProfile(
        audience_id="child",
        name="Child",
        expertise_level="beginner",
        control_vector=AudienceControlVector(
            language_level=0.1, abstraction=0.1, rigor=0.1,
            math_density=0.0, cognitive_load=0.2,
        ),
    )


class TestActivationOperator:
    def test_fallback_execution(self, audience):
        op = ActivationOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.ACTIVATION
        assert "hook" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, audience):
        op = ActivationOperator()
        prompt = op.build_prompt("neural networks", audience, {}, {})
        assert "neural networks" in prompt
        assert "hook" in prompt


class TestMetaphorOperator:
    def test_fallback_execution(self, audience):
        op = MetaphorOperator(ai_client=None, engine=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.METAPHOR
        assert "metaphor" in output.content
        assert output.confidence > 0


class TestStructureOperator:
    def test_fallback_execution(self, audience):
        op = StructureOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.STRUCTURE
        assert "definition" in output.content


class TestInterrogationOperator:
    def test_fallback_execution(self, audience):
        op = InterrogationOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.INTERROGATION
        assert "socratic_questions" in output.content


class TestEncodingOperator:
    def test_fallback_execution(self, audience):
        op = EncodingOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.ENCODING
        assert "mnemonic" in output.content


class TestTransferOperator:
    def test_fallback_execution(self, audience):
        op = TransferOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.TRANSFER
        assert "worked_example" in output.content


class TestReflectionOperator:
    def test_fallback_execution(self, audience):
        op = ReflectionOperator(ai_client=None)
        output = op.execute("neural networks", audience, {})
        assert output.layer == LayerName.REFLECTION
        assert "calibration_questions" in output.content


class TestParseOutput:
    """Tests for BaseOperator.parse_output() inherited by all operators."""

    def test_plain_json(self):
        op = ActivationOperator(ai_client=None)
        raw = json.dumps({"hook": "Did you know?", "stakes": "very important"})
        result = op.parse_output(raw)
        assert result == {"hook": "Did you know?", "stakes": "very important"}

    def test_json_code_fence_with_language_tag(self):
        op = ActivationOperator(ai_client=None)
        payload = {"hook": "Did you know?", "stakes": "very important"}
        raw = f"```json\n{json.dumps(payload)}\n```"
        result = op.parse_output(raw)
        assert result == payload

    def test_json_code_fence_without_language_tag(self):
        op = ActivationOperator(ai_client=None)
        payload = {"hook": "Did you know?", "stakes": "very important"}
        raw = f"```\n{json.dumps(payload)}\n```"
        result = op.parse_output(raw)
        assert result == payload

    def test_non_json_text(self):
        op = ActivationOperator(ai_client=None)
        raw = "This is just plain text, not JSON at all."
        result = op.parse_output(raw)
        assert result == {"text": raw}


class TestGradingOperator:
    def test_grades_context(self, audience):
        op = GradingOperator(ai_client=None)
        context = {
            "activation": {"hook": "test hook", "stakes": "very important"},
            "metaphor": {"metaphor": "like a kitchen" * 50},
        }
        output = op.execute("neural networks", audience, context)
        assert "layer_grades" in output.content
        assert "gaps" in output.content
        assert "revision_plan" in output.content
