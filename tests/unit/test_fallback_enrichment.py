"""Tests for topic-aware fallback templates.

Each operator should produce richer output when a concept dict is in the config,
and fall back to generic output when it's absent.
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

TOPIC = "neural networks"


@pytest.fixture()
def audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="child",
        name="Child",
        expertise_level="beginner",
        control_vector=AudienceControlVector(language_level=0.1),
    )


@pytest.fixture()
def config_with_concept() -> dict:
    return {"concept": CONCEPT}


@pytest.fixture()
def config_without_concept() -> dict:
    return {}


def _parse(raw: str) -> dict:
    return json.loads(raw)


# ── ActivationOperator ────────────────────────────────────


class TestActivationFallback:
    def test_with_concept_uses_description(self, audience, config_with_concept):
        op = ActivationOperator(ai_client=None)
        result = _parse(op.generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "Interconnected nodes" in result["hook"]

    def test_with_concept_uses_misconceptions(self, audience, config_with_concept):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "works like human brain" in result["curiosity_gap"]

    def test_with_concept_uses_related(self, audience, config_with_concept):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "deep learning" in result["stakes"]

    def test_with_concept_uses_prereqs(self, audience, config_with_concept):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "basic statistics" in result["prior_knowledge_bridge"]

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(ActivationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "actually works" in result["hook"]


# ── MetaphorOperator ──────────────────────────────────────


class TestMetaphorFallback:
    def test_with_concept_uses_components_in_mapping(self, audience, config_with_concept):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        mapping_keys = list(result["mapping"].keys())
        assert "nodes neurons" in mapping_keys

    def test_with_concept_uses_description(self, audience, config_with_concept):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "Interconnected nodes" in result["metaphor"] or "process information" in result["metaphor"]

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(MetaphorOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "kitchen" in result["metaphor"]
        assert result["source_domain"] == "restaurant_kitchen"


# ── StructureOperator ─────────────────────────────────────


class TestStructureFallback:
    def test_with_concept_uses_description(self, audience, config_with_concept):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "Interconnected nodes" in result["definition"]

    def test_with_concept_uses_category(self, audience, config_with_concept):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert result["taxonomy"]["category"] == "ai fundamentals"

    def test_with_concept_uses_components_as_terms(self, audience, config_with_concept):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "nodes neurons" in result["key_terms"]

    def test_with_concept_uses_related_as_relationships(self, audience, config_with_concept):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        rels = result["relationships"]
        to_values = [r["to"] for r in rels]
        assert "deep learning" in to_values

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(StructureOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "structured processes" in result["definition"]


# ── InterrogationOperator ─────────────────────────────────


class TestInterrogationFallback:
    def test_with_concept_uses_misconceptions(self, audience, config_with_concept):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        probes = " ".join(result["misconception_probes"])
        assert "works like human brain" in probes

    def test_with_concept_uses_components_as_edge_cases(self, audience, config_with_concept):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        edges = " ".join(result["edge_cases"])
        assert "nodes neurons" in edges

    def test_with_concept_uses_properties_as_questions(self, audience, config_with_concept):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        qs = " ".join(result["socratic_questions"])
        assert "interconnected processing" in qs

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(InterrogationOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "fundamental purpose" in result["socratic_questions"][0]


# ── EncodingOperator ──────────────────────────────────────


class TestEncodingFallback:
    def test_with_concept_uses_components_as_chunks(self, audience, config_with_concept):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        labels = [c["label"] for c in result["chunks"]]
        assert "Nodes Neurons" in labels

    def test_with_concept_first_letter_acronym(self, audience, config_with_concept):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        # "Neural Networks" → "NN"
        assert result["mnemonic"] == "NN"

    def test_with_concept_uses_properties_as_cues(self, audience, config_with_concept):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        cues = " ".join(result["retrieval_cues"])
        assert "interconnected processing" in cues

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(EncodingOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "Remember" in result["mnemonic"]


# ── TransferOperator ──────────────────────────────────────


class TestTransferFallback:
    def test_with_concept_uses_related_for_cross_domain(self, audience, config_with_concept):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        assert "deep learning" in result["cross_domain_transfer"]

    def test_with_concept_uses_components_as_steps(self, audience, config_with_concept):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        steps = result["worked_example"]["steps"]
        assert any("nodes neurons" in s for s in steps)

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(TransferOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "natural systems" in result["cross_domain_transfer"]


# ── ReflectionOperator ────────────────────────────────────


class TestReflectionFallback:
    def test_with_concept_uses_misconceptions_as_alerts(self, audience, config_with_concept):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        alerts = " ".join(result["misconception_alerts"])
        assert "works like human brain" in alerts

    def test_with_concept_uses_prereqs_as_connections(self, audience, config_with_concept):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        prompts = " ".join(result["connection_prompts"])
        assert "basic statistics" in prompts

    def test_with_concept_uses_related_as_next_steps(self, audience, config_with_concept):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_with_concept))
        steps = " ".join(result["next_steps"])
        assert "deep learning" in steps

    def test_without_concept_generic(self, audience, config_without_concept):
        result = _parse(ReflectionOperator(ai_client=None).generate_fallback(TOPIC, audience, {}, config_without_concept))
        assert "similar-sounding" in result["misconception_alerts"][0]
