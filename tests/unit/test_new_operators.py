"""Unit tests for new operators: Diagnostic, Contextualization, Narrative, Challenge, Elaboration."""

import json

import pytest

from cognitive_scaffolding.core.models import (
    AudienceControlVector,
    AudienceProfile,
    LayerName,
)
from cognitive_scaffolding.operators.diagnostic import DiagnosticOperator
from cognitive_scaffolding.operators.contextualization import ContextualizationOperator
from cognitive_scaffolding.operators.narrative import NarrativeOperator
from cognitive_scaffolding.operators.challenge import ChallengeOperator
from cognitive_scaffolding.operators.elaboration import ElaborationOperator


CONCEPT = {
    "concept_id": "neural_networks",
    "name": "Neural Networks",
    "category": "ai_fundamentals",
    "complexity": "medium",
    "evolution_rate": "slow",
    "description": "Interconnected nodes that process information",
    "key_components": ["nodes_neurons", "connections_weights", "layers", "activation_functions"],
    "properties": ["interconnected_processing", "pattern_recognition", "learning_from_data"],
    "common_misconceptions": ["works_like_human_brain", "conscious_understanding"],
    "prerequisite_concepts": ["basic_statistics"],
    "related_concepts": ["deep_learning", "machine_learning"],
}

TOPIC = "neural networks"


@pytest.fixture()
def child_audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="child",
        name="Child",
        expertise_level="beginner",
        control_vector=AudienceControlVector(
            language_level=0.1, abstraction=0.1, rigor=0.1,
            math_density=0.0, cognitive_load=0.2,
        ),
    )


@pytest.fixture()
def expert_audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="data_scientist",
        name="Data Scientist",
        expertise_level="expert",
        control_vector=AudienceControlVector(
            language_level=0.8, abstraction=0.7, rigor=0.8,
            math_density=0.7, cognitive_load=0.8,
        ),
    )


@pytest.fixture()
def config_with_concept() -> dict:
    return {"concept": CONCEPT}


@pytest.fixture()
def config_without_concept() -> dict:
    return {}


def _parse(raw: str) -> dict:
    return json.loads(raw)


# ── DiagnosticOperator ───────────────────────────────────────


class TestDiagnosticOperator:
    def test_fallback_execution(self, child_audience):
        op = DiagnosticOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {})
        assert output.layer == LayerName.DIAGNOSTIC
        assert "knowledge_assessment" in output.content
        assert "prerequisite_gaps" in output.content
        assert "recommended_depth" in output.content
        assert "skip_basics" in output.content
        assert "estimated_familiarity" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, child_audience):
        op = DiagnosticOperator()
        prompt = op.build_prompt(TOPIC, child_audience, {}, {"concept": CONCEPT})
        assert "neural networks" in prompt
        assert "diagnostic" in prompt.lower() or "pre-assessment" in prompt.lower()

    def test_beginner_has_gaps(self, child_audience, config_with_concept):
        op = DiagnosticOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        assert len(result["prerequisite_gaps"]) > 0
        assert result["recommended_depth"] == "introductory"
        assert result["skip_basics"] is False
        assert result["estimated_familiarity"] < 0.5

    def test_expert_skips_basics(self, expert_audience, config_with_concept):
        op = DiagnosticOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, expert_audience, {}, config_with_concept))
        assert len(result["prerequisite_gaps"]) == 0
        assert result["skip_basics"] is True
        assert result["estimated_familiarity"] > 0.5
        assert result["recommended_depth"] in ("advanced", "expert")

    def test_without_concept_still_works(self, child_audience, config_without_concept):
        op = DiagnosticOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_without_concept))
        assert "recommended_depth" in result
        assert isinstance(result["knowledge_assessment"], dict)

    def test_schema_based_confidence(self, child_audience, config_with_concept):
        op = DiagnosticOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {}, config_with_concept)
        # With all expected keys present and non-empty, confidence should be decent
        assert output.confidence >= 0.5


# ── ContextualizationOperator ───────────────────────────────


class TestContextualizationOperator:
    def test_fallback_execution(self, child_audience):
        op = ContextualizationOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {})
        assert output.layer == LayerName.CONTEXTUALIZATION
        assert "field_context" in output.content
        assert "historical_timeline" in output.content
        assert "current_trends" in output.content
        assert "adjacent_topics" in output.content
        assert "why_now" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, child_audience):
        op = ContextualizationOperator()
        prompt = op.build_prompt(TOPIC, child_audience, {}, {"concept": CONCEPT})
        assert "neural networks" in prompt
        assert "big-picture" in prompt.lower() or "contextualization" in prompt.lower()

    def test_with_concept_uses_category(self, child_audience, config_with_concept):
        op = ContextualizationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        assert "ai fundamentals" in result["field_context"]

    def test_with_concept_uses_related(self, child_audience, config_with_concept):
        op = ContextualizationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        adjacent = result["adjacent_topics"]
        assert any("deep learning" in a for a in adjacent) or any("machine learning" in a for a in adjacent)

    def test_with_concept_uses_evolution_rate(self, child_audience, config_with_concept):
        op = ContextualizationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        # neural_networks has evolution_rate: slow
        assert "established" in result["current_trends"].lower() or "slow" in result["current_trends"].lower()

    def test_without_concept_generic(self, child_audience, config_without_concept):
        op = ContextualizationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_without_concept))
        assert "field_context" in result
        assert len(result["historical_timeline"]) > 0


# ── NarrativeOperator ───────────────────────────────────────


class TestNarrativeOperator:
    def test_fallback_execution(self, child_audience):
        op = NarrativeOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {})
        assert output.layer == LayerName.NARRATIVE
        assert "story" in output.content
        assert "characters" in output.content
        assert "conflict" in output.content
        assert "resolution" in output.content
        assert "concept_embedded_at" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, child_audience):
        op = NarrativeOperator()
        prompt = op.build_prompt(TOPIC, child_audience, {}, {"concept": CONCEPT})
        assert "neural networks" in prompt
        assert "narrative" in prompt.lower() or "story" in prompt.lower()

    def test_child_audience_gets_friendly_story(self, child_audience, config_with_concept):
        op = NarrativeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        # Child should get a friendly character
        assert any("explorer" in c.lower() or "curious" in c.lower() for c in result["characters"])

    def test_expert_audience_gets_professional_story(self, expert_audience, config_with_concept):
        op = NarrativeOperator(ai_client=None)
        config = dict(config_with_concept)
        config["audience_data"] = {
            "preferred_analogies": ["data_workflows"],
            "preferred_domains": ["statistical_learning"],
        }
        result = _parse(op.generate_fallback(TOPIC, expert_audience, {}, config))
        # Expert should get a professional character
        chars = " ".join(result["characters"]).lower()
        assert "professional" in chars or "specialist" in chars or "experienced" in chars

    def test_with_concept_uses_misconceptions_in_conflict(self, child_audience, config_with_concept):
        op = NarrativeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        assert "works like human brain" in result["conflict"]

    def test_without_concept_generic(self, child_audience, config_without_concept):
        op = NarrativeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_without_concept))
        assert "story" in result
        assert len(result["characters"]) > 0


# ── ChallengeOperator ───────────────────────────────────────


class TestChallengeOperator:
    def test_fallback_execution(self, child_audience):
        op = ChallengeOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {})
        assert output.layer == LayerName.CHALLENGE
        assert "bloom_level" in output.content
        assert "challenge_prompt" in output.content
        assert "scaffolded_hints" in output.content
        assert "difficulty_justification" in output.content
        assert "expected_struggle_points" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, child_audience):
        op = ChallengeOperator()
        prompt = op.build_prompt(TOPIC, child_audience, {}, {"concept": CONCEPT})
        assert "neural networks" in prompt
        assert "Bloom" in prompt or "bloom" in prompt

    def test_beginner_gets_low_bloom(self, child_audience, config_with_concept):
        op = ChallengeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        # Beginner + low cognitive_load => remember level
        assert result["bloom_level"] in ("remember", "understand")

    def test_expert_gets_high_bloom(self, expert_audience, config_with_concept):
        op = ChallengeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, expert_audience, {}, config_with_concept))
        assert result["bloom_level"] in ("evaluate", "create")

    def test_diagnostic_gaps_lower_bloom(self, config_with_concept):
        """Diagnostic gaps should pull Bloom's level down."""
        # Use moderate cognitive_load so it doesn't counteract the gap adjustment
        audience = AudienceProfile(
            audience_id="data_scientist",
            name="Data Scientist",
            expertise_level="expert",
            control_vector=AudienceControlVector(
                language_level=0.8, abstraction=0.7, rigor=0.8,
                math_density=0.7, cognitive_load=0.5,
            ),
        )
        op = ChallengeOperator(ai_client=None)
        context = {
            "diagnostic": {
                "prerequisite_gaps": ["basic_statistics", "linear_algebra"],
                "skip_basics": False,
            }
        }
        result = _parse(op.generate_fallback(TOPIC, audience, context, config_with_concept))
        # With 2+ gaps and moderate cognitive_load, level should be pulled down
        assert result["bloom_level"] in ("apply", "analyze")

    def test_scaffolded_hints_are_progressive(self, child_audience, config_with_concept):
        op = ChallengeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        hints = result["scaffolded_hints"]
        assert len(hints) >= 3
        # Last hint should be more explicit than first
        assert len(hints[-1]) >= len(hints[0]) or "systematic" in hints[-1].lower()

    def test_without_concept_generic(self, child_audience, config_without_concept):
        op = ChallengeOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_without_concept))
        assert "bloom_level" in result
        assert len(result["scaffolded_hints"]) >= 3


# ── ElaborationOperator ─────────────────────────────────────


class TestElaborationOperator:
    def test_fallback_execution(self, child_audience):
        op = ElaborationOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {})
        assert output.layer == LayerName.ELABORATION
        assert "selected_subtopic" in output.content
        assert "deep_dive" in output.content
        assert "connections_to_main" in output.content
        assert "further_reading" in output.content
        assert "selection_rationale" in output.content
        assert output.confidence > 0

    def test_builds_prompt(self, child_audience):
        op = ElaborationOperator()
        prompt = op.build_prompt(TOPIC, child_audience, {}, {"concept": CONCEPT})
        assert "neural networks" in prompt
        assert "elaboration" in prompt.lower() or "deep" in prompt.lower()

    def test_with_concept_selects_first_component(self, child_audience, config_with_concept):
        op = ElaborationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        # Default: selects first component
        assert "nodes neurons" in result["selected_subtopic"]

    def test_with_concept_uses_related_for_reading(self, child_audience, config_with_concept):
        op = ElaborationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_with_concept))
        further = " ".join(result["further_reading"])
        assert "deep learning" in further or "machine learning" in further

    def test_without_concept_generic(self, child_audience, config_without_concept):
        op = ElaborationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, child_audience, {}, config_without_concept))
        assert "deep_dive" in result
        assert "core principles" in result["selected_subtopic"]

    def test_diagnostic_gaps_influence_subtopic(self, child_audience, config_with_concept):
        """When diagnostic identifies gaps, elaboration should focus on related component."""
        op = ElaborationOperator(ai_client=None)
        # 'connections_weights' shares 'connections' with a gap keyword
        context = {
            "diagnostic": {
                "prerequisite_gaps": ["connections"],
                "skip_basics": False,
            }
        }
        result = _parse(op.generate_fallback(TOPIC, child_audience, context, config_with_concept))
        assert "connections weights" in result["selected_subtopic"]


# ── Schema-Based Confidence (C1) ────────────────────────────


class TestSchemaBasedConfidence:
    """Test the improved confidence estimation across all operators."""

    def test_full_keys_high_confidence(self, child_audience):
        """Operator with all expected keys present should have high confidence."""
        op = DiagnosticOperator(ai_client=None)
        output = op.execute(TOPIC, child_audience, {}, {"concept": CONCEPT})
        # All 5 expected keys should be present and non-empty
        assert output.confidence >= 0.6

    def test_empty_content_zero_confidence(self):
        """Empty content dict should return 0.0 confidence."""
        op = DiagnosticOperator(ai_client=None)
        assert op.estimate_confidence({}) == 0.0

    def test_partial_keys_moderate_confidence(self):
        """Content with some keys missing should have moderate confidence."""
        op = DiagnosticOperator(ai_client=None)
        # Only 2 of 5 expected keys
        content = {
            "knowledge_assessment": {"test": "basic"},
            "recommended_depth": "intermediate",
        }
        confidence = op.estimate_confidence(content)
        assert 0.2 < confidence < 0.7

    def test_operator_without_expected_keys_uses_legacy(self):
        """GradingOperator has no expected_keys, should use legacy heuristic."""
        from cognitive_scaffolding.operators.grading import GradingOperator
        op = GradingOperator(ai_client=None)
        # Short content should get low confidence
        assert op.estimate_confidence({"a": "b"}) == 0.3
        # Long content should get higher confidence
        assert op.estimate_confidence({"text": "x" * 600}) == 0.8
