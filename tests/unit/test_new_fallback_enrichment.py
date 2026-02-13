"""Tests for topic-aware fallback templates of new operators.

Each operator should produce richer output when a concept dict is in the config,
and fall back to generic output when it's absent.
"""

import json

import pytest

from cognitive_scaffolding.core.models import (
    AudienceControlVector,
    AudienceProfile,
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

AUDIENCE_DATA = {
    "preferred_analogies": ["data_workflows"],
    "preferred_domains": ["statistical_learning"],
    "primary_tools": ["Python", "Jupyter"],
    "learning_assets": ["python_notebooks"],
    "core_skills": ["Python", "Machine_Learning"],
    "communication_style": "accessible_friendly",
    "complexity_preference": "very_high",
    "attention_span": "medium",
}

DOMAIN = {
    "domain_id": "statistical_learning",
    "name": "Statistical Learning",
    "vocabulary": ["model", "training", "inference"],
    "metaphor_types": ["mathematical_analogy"],
    "suitable_for": ["data_scientist"],
}


@pytest.fixture()
def audience() -> AudienceProfile:
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
def full_config() -> dict:
    return {
        "concept": CONCEPT,
        "audience_data": AUDIENCE_DATA,
        "domain": DOMAIN,
    }


@pytest.fixture()
def config_without_concept() -> dict:
    return {}


def _parse(raw: str) -> dict:
    return json.loads(raw)


# ── DiagnosticOperator ───────────────────────────────────────


class TestDiagnosticFallbackEnrichment:
    def test_with_concept_assesses_prereqs(self, audience, full_config):
        result = _parse(DiagnosticOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert "basic statistics" in result["knowledge_assessment"]

    def test_expert_gets_high_familiarity(self, audience, full_config):
        result = _parse(DiagnosticOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert result["estimated_familiarity"] >= 0.8

    def test_audience_domain_boosts_familiarity(self, audience, full_config):
        """Audience with preferred domain matching concept category gets higher familiarity."""
        result = _parse(DiagnosticOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        result_base = _parse(DiagnosticOperator(ai_client=None).generate_fallback(
            TOPIC, audience, {}, {"concept": CONCEPT}))
        # With audience_data including preferred_domains, familiarity may be higher
        assert result["estimated_familiarity"] >= result_base["estimated_familiarity"]

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(DiagnosticOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert result["knowledge_assessment"] == {}
        assert result["prerequisite_gaps"] == []


# ── ContextualizationOperator ──────────────────────────────


class TestContextualizationFallbackEnrichment:
    def test_with_concept_uses_category(self, audience, full_config):
        result = _parse(ContextualizationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert "ai fundamentals" in result["field_context"]

    def test_with_concept_uses_related_concepts(self, audience, full_config):
        result = _parse(ContextualizationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        adjacent_str = " ".join(result["adjacent_topics"])
        assert "deep learning" in adjacent_str or "machine learning" in adjacent_str

    def test_with_concept_uses_prereqs_in_timeline(self, audience, full_config):
        result = _parse(ContextualizationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        timeline_str = " ".join(result["historical_timeline"])
        assert "basic statistics" in timeline_str

    def test_domain_aware_why_now(self, audience, full_config):
        result = _parse(ContextualizationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        # With domain, why_now should mention it
        assert "foundational" in result["why_now"].lower() or "statistical" in result["why_now"].lower() or "relevant" in result["why_now"].lower()

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(ContextualizationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "broad applications" in result["field_context"]


# ── NarrativeOperator ──────────────────────────────────────


class TestNarrativeFallbackEnrichment:
    def test_with_concept_uses_components(self, audience, full_config):
        result = _parse(NarrativeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert "nodes neurons" in result["story"] or "connections weights" in result["story"]

    def test_with_concept_uses_misconceptions(self, audience, full_config):
        result = _parse(NarrativeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert "works like human brain" in result["conflict"]

    def test_domain_aware_character(self, audience, full_config):
        result = _parse(NarrativeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        chars = " ".join(result["characters"]).lower()
        # With data_workflows analogy, should get a professional character
        assert "professional" in chars or "experienced" in chars or "data" in chars

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(NarrativeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "neural networks" in result["story"]


# ── ChallengeOperator ─────────────────────────────────────


class TestChallengeFallbackEnrichment:
    def test_with_concept_uses_components_in_hints(self, audience, full_config):
        result = _parse(ChallengeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        hints_str = " ".join(result["scaffolded_hints"])
        assert "nodes neurons" in hints_str

    def test_with_concept_uses_misconceptions_in_struggles(self, audience, full_config):
        result = _parse(ChallengeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        struggles_str = " ".join(result["expected_struggle_points"])
        assert "works like human brain" in struggles_str

    def test_expert_gets_high_bloom(self, audience, full_config):
        result = _parse(ChallengeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert result["bloom_level"] in ("evaluate", "create")

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(ChallengeOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert result["bloom_level"] in ("evaluate", "create")  # Expert default
        assert len(result["scaffolded_hints"]) >= 3


# ── ElaborationOperator ───────────────────────────────────


class TestElaborationFallbackEnrichment:
    def test_with_concept_selects_component(self, audience, full_config):
        result = _parse(ElaborationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        assert "nodes neurons" in result["selected_subtopic"]

    def test_with_concept_uses_related_for_reading(self, audience, full_config):
        result = _parse(ElaborationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        further_str = " ".join(result["further_reading"])
        assert "deep learning" in further_str or "machine learning" in further_str

    def test_audience_tools_in_reading(self, audience, full_config):
        result = _parse(ElaborationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, full_config))
        further_str = " ".join(result["further_reading"])
        assert "Python" in further_str

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(ElaborationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "core principles" in result["selected_subtopic"]
