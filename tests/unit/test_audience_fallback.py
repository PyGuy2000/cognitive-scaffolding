"""Tests for audience-aware fallback templates.

Each operator should produce audience-specific output when audience_data is
in the config, and fall back to generic output when it's absent.
"""

import json

import pytest

from cognitive_scaffolding.core.models import (
    AudienceControlVector,
    AudienceProfile,
)
from cognitive_scaffolding.operators.activation import ActivationOperator
from cognitive_scaffolding.operators.metaphor import MetaphorOperator
from cognitive_scaffolding.operators.structure import StructureOperator
from cognitive_scaffolding.operators.interrogation import InterrogationOperator
from cognitive_scaffolding.operators.encoding import EncodingOperator
from cognitive_scaffolding.operators.transfer import TransferOperator
from cognitive_scaffolding.operators.reflection import ReflectionOperator


CONCEPT = {
    "concept_id": "neural_networks",
    "name": "Neural Networks",
    "category": "ai_fundamentals",
    "complexity": "medium",
    "description": "Interconnected nodes that process information",
    "key_components": ["nodes_neurons", "connections_weights", "layers", "activation_functions"],
    "properties": ["interconnected_processing", "pattern_recognition", "learning_from_data"],
    "common_misconceptions": ["works_like_human_brain", "conscious_understanding", "always_accurate"],
    "prerequisite_concepts": ["basic_statistics"],
    "related_concepts": ["deep_learning", "machine_learning"],
}

DATA_SCIENTIST_AUDIENCE = {
    "audience_id": "data_scientist",
    "name": "Data Scientist",
    "description": "Professionals who develop ML models and algorithms",
    "age_range": "25-45",
    "show_formulas": "full_mathematical",
    "show_code": "full_implementations",
    "complexity_preference": "very_high",
    "core_skills": ["Python", "R", "Machine_Learning", "Statistics"],
    "primary_tools": ["Python", "R", "Jupyter", "TensorFlow", "PyTorch"],
    "preferred_domains": ["statistical_learning", "experimental_design"],
    "learning_assets": ["python_notebooks", "model_implementations", "performance_benchmarks"],
    "expertise_level": "intermediate",
    "preferred_analogies": ["data_workflows", "analytical_processes"],
    "attention_span": "medium",
    "communication_style": "accessible_friendly",
}

TOPIC = "neural networks"


@pytest.fixture()
def audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="data_scientist",
        name="Data Scientist",
        expertise_level="expert",
        control_vector=AudienceControlVector(language_level=0.8),
    )


@pytest.fixture()
def config_with_audience() -> dict:
    return {"concept": CONCEPT, "audience_data": DATA_SCIENTIST_AUDIENCE}


@pytest.fixture()
def config_audience_only() -> dict:
    """Audience data without concept — tests generic branch with audience."""
    return {"audience_data": DATA_SCIENTIST_AUDIENCE}


def _parse(raw: str) -> dict:
    return json.loads(raw)


# ── ActivationOperator ────────────────────────────────────


class TestActivationAudienceFallback:
    def test_uses_preferred_analogies_in_bridge(self, audience, config_with_audience):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert "data workflows" in result["prior_knowledge_bridge"]

    def test_generic_branch_uses_preferred_analogies(self, audience, config_audience_only):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_audience_only))
        assert "data workflows" in result["prior_knowledge_bridge"]

    def test_without_audience_generic_bridge(self, audience):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {}))
        assert "basics that lead to" in result["prior_knowledge_bridge"]


# ── MetaphorOperator ──────────────────────────────────────


class TestMetaphorAudienceFallback:
    def test_uses_preferred_domains_as_source(self, audience, config_with_audience):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        # No preferred_metaphors so it falls to preferred_domains
        assert "statistical learning" in result["source_domain"] or "statistical learning" in result["metaphor"]

    def test_generic_without_audience_uses_kitchen(self, audience):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {}))
        assert result["source_domain"] == "restaurant_kitchen"

    def test_concept_with_audience_not_kitchen(self, audience, config_with_audience):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert result["source_domain"] != "restaurant_kitchen"


# ── StructureOperator ─────────────────────────────────────


class TestStructureAudienceFallback:
    def test_show_formulas_populates_notation(self, audience, config_with_audience):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert result["formal_notation"] != ""
        assert "transform" in result["formal_notation"]

    def test_high_complexity_enriches_definition(self, audience, config_with_audience):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert "interacting subsystems" in result["definition"]

    def test_without_audience_empty_notation(self, audience):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {"concept": CONCEPT}))
        assert result["formal_notation"] == ""


# ── InterrogationOperator ─────────────────────────────────


class TestInterrogationAudienceFallback:
    def test_uses_core_skills_in_questions(self, audience, config_with_audience):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        qs = " ".join(result["socratic_questions"])
        assert "Python" in qs

    def test_high_complexity_deeper_synthesis(self, audience, config_with_audience):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert "failure modes" in result["synthesis_prompt"]

    def test_generic_branch_uses_skills(self, audience, config_audience_only):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_audience_only))
        qs = " ".join(result["socratic_questions"])
        assert "Python" in qs


# ── EncodingOperator ──────────────────────────────────────


class TestEncodingAudienceFallback:
    def test_learning_assets_in_visual_anchor(self, audience, config_with_audience):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert "python notebooks" in result["visual_anchor"]

    def test_attention_span_limits_chunks(self, audience):
        short_aud = {**DATA_SCIENTIST_AUDIENCE, "attention_span": "short"}
        config = {"concept": CONCEPT, "audience_data": short_aud}
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config))
        assert len(result["chunks"]) <= 3

    def test_without_audience_default_visual(self, audience):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {"concept": CONCEPT}))
        assert "diagram" in result["visual_anchor"]


# ── TransferOperator ──────────────────────────────────────


class TestTransferAudienceFallback:
    def test_uses_primary_tools_in_steps(self, audience, config_with_audience):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        steps = " ".join(result["worked_example"]["steps"])
        assert "Python" in steps

    def test_uses_preferred_domains_in_cross_domain(self, audience, config_with_audience):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        assert "statistical learning" in result["cross_domain_transfer"]

    def test_without_audience_generic_steps(self, audience):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {"concept": CONCEPT}))
        steps = " ".join(result["worked_example"]["steps"])
        assert "Understand" in steps


# ── ReflectionOperator ────────────────────────────────────


class TestReflectionAudienceFallback:
    def test_uses_learning_assets_in_next_steps(self, audience, config_with_audience):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        steps = " ".join(result["next_steps"])
        assert "python notebooks" in steps

    def test_uses_preferred_domains_in_next_steps(self, audience, config_with_audience):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_audience))
        steps = " ".join(result["next_steps"])
        assert "statistical learning" in steps

    def test_without_audience_generic_next_steps(self, audience):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {"concept": CONCEPT}))
        steps = " ".join(result["next_steps"])
        assert "deep learning" in steps
