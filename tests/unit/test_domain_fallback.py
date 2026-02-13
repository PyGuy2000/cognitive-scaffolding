"""Tests for domain-aware fallback templates.

Metaphor, activation, and transfer operators should produce domain-specific
output when domain data is in the config.
"""

import json

import pytest

from cognitive_scaffolding.core.models import (
    AudienceControlVector,
    AudienceProfile,
)
from cognitive_scaffolding.operators.activation import ActivationOperator
from cognitive_scaffolding.operators.metaphor import MetaphorOperator
from cognitive_scaffolding.operators.transfer import TransferOperator


CONCEPT = {
    "concept_id": "neural_networks",
    "name": "Neural Networks",
    "category": "ai_fundamentals",
    "complexity": "medium",
    "description": "Interconnected nodes that process information",
    "key_components": ["nodes_neurons", "connections_weights", "layers", "activation_functions"],
    "properties": ["interconnected_processing", "pattern_recognition", "learning_from_data"],
    "common_misconceptions": ["works_like_human_brain"],
    "prerequisite_concepts": ["basic_statistics"],
    "related_concepts": ["deep_learning", "machine_learning"],
}

COOKING_DOMAIN = {
    "domain_id": "cooking_culinary",
    "name": "Cooking Culinary",
    "description": "Metaphors based on cooking processes and culinary arts",
    "metaphor_types": ["recipe_processes", "ingredient_combination", "technique_application"],
    "vocabulary": ["like cooking", "similar to recipes", "think of ingredients", "imagine preparation"],
    "examples": ["recipe_following", "ingredient_mixing", "cooking_techniques", "flavor_balancing"],
    "properties": ["step_by_step_processes", "ingredient_combination"],
    "strengths": ["hands_on_workshop_style", "process_learning"],
    "suitable_for": ["general_audience", "creative_learners"],
}

TOPIC = "neural networks"


@pytest.fixture()
def audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="general",
        name="General",
        expertise_level="intermediate",
        control_vector=AudienceControlVector(),
    )


@pytest.fixture()
def config_with_domain() -> dict:
    return {"concept": CONCEPT, "domain": COOKING_DOMAIN}


@pytest.fixture()
def config_domain_only() -> dict:
    """Domain data without concept — tests generic branch with domain."""
    return {"domain": COOKING_DOMAIN}


def _parse(raw: str) -> dict:
    return json.loads(raw)


# ── MetaphorOperator ──────────────────────────────────────


class TestMetaphorDomainFallback:
    def test_uses_domain_name_as_source(self, audience, config_with_domain):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_domain))
        assert result["source_domain"] == "cooking culinary"

    def test_uses_domain_vocabulary(self, audience, config_with_domain):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_domain))
        assert "like cooking" in result["metaphor"].lower() or "Like cooking" in result["metaphor"]

    def test_generic_branch_uses_domain(self, audience, config_domain_only):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_domain_only))
        assert result["source_domain"] == "cooking culinary"


# ── ActivationOperator ────────────────────────────────────


class TestActivationDomainFallback:
    def test_uses_domain_vocabulary_in_hook(self, audience, config_with_domain):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_domain))
        assert "like cooking" in result["hook"].lower() or "Like cooking" in result["hook"]

    def test_generic_branch_uses_domain_vocab(self, audience, config_domain_only):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_domain_only))
        assert "like cooking" in result["hook"].lower() or "Like cooking" in result["hook"]

    def test_without_domain_generic_hook(self, audience):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, {}))
        assert "actually works" in result["hook"]


# ── TransferOperator ──────────────────────────────────────


class TestTransferDomainFallback:
    def test_uses_domain_examples_in_steps(self, audience, config_with_domain):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_domain))
        steps = " ".join(result["worked_example"]["steps"])
        assert "recipe following" in steps

    def test_uses_domain_name_in_cross_domain(self, audience, config_with_domain):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_domain))
        assert "Cooking Culinary" in result["cross_domain_transfer"]

    def test_generic_branch_uses_domain(self, audience, config_domain_only):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_domain_only))
        assert "Cooking Culinary" in result["cross_domain_transfer"]
