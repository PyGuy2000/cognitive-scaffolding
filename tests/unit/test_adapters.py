"""Unit tests for the three integration adapters."""

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
from cognitive_scaffolding.adapters.chatbot_adapter import ChatbotAdapter
from cognitive_scaffolding.adapters.rag_adapter import RAGAdapter
from cognitive_scaffolding.adapters.etl_adapter import ETLAdapter


def _make_audience() -> AudienceProfile:
    return AudienceProfile(
        audience_id="child",
        name="Child",
        expertise_level="beginner",
        control_vector=AudienceControlVector(
            language_level=0.1, abstraction=0.1, rigor=0.1,
        ),
    )


def _layer_content():
    """Return known content dicts for every layer."""
    return {
        LayerName.ACTIVATION: {
            "hook": "Ever wondered how brains learn?",
            "curiosity_gap": "Most people misunderstand neurons.",
            "stakes": "Understanding this changes everything.",
            "emotional_trigger": "Imagine explaining it to anyone.",
            "prior_knowledge_bridge": "You already know about patterns.",
        },
        LayerName.METAPHOR: {
            "metaphor": "Think of it like a kitchen brigade.",
            "source_domain": "restaurant_kitchen",
            "mapping": {"input": "ingredients", "process": "cooking", "output": "dish"},
            "limitations": ["Scale differs", "Complexity is higher"],
            "extension": "Consider how rush-hour affects the kitchen.",
        },
        LayerName.STRUCTURE: {
            "definition": "Neural networks are interconnected nodes.",
            "taxonomy": {"category": "ai_fundamentals", "subcategories": ["supervised", "unsupervised"]},
            "key_terms": {"neuron": "A computational unit", "weight": "Connection strength"},
            "relationships": [{"from": "input", "to": "hidden", "type": "feeds"}],
            "diagram_description": "A layered graph showing connections.",
            "formal_notation": "f(x) = sigma(Wx + b)",
        },
        LayerName.INTERROGATION: {
            "socratic_questions": [
                "What is the purpose of a neural network?",
                "How does depth affect learning?",
                "What if we removed hidden layers?",
            ],
            "counterexamples": ["Linear problems don't need depth."],
            "edge_cases": ["Single neuron perceptrons."],
            "misconception_probes": ["Do neural nets think like humans?"],
            "synthesis_prompt": "How do all layers cooperate?",
        },
        LayerName.ENCODING: {
            "mnemonic": "N-W-L-A: Nodes, Weights, Layers, Activation",
            "chunks": [
                {"label": "Nodes", "summary": "Processing units"},
                {"label": "Weights", "summary": "Connection strengths"},
                {"label": "Layers", "summary": "Organizational tiers"},
            ],
            "retrieval_cues": ["When you hear 'neural', think of nodes and weights."],
            "spaced_repetition": [{"question": "What is a neuron?", "answer": "A processing unit."}],
            "visual_anchor": "Picture a layered cake with connected dots.",
        },
        LayerName.TRANSFER: {
            "worked_example": {
                "problem": "Classify images of cats vs dogs",
                "steps": ["Prepare pixel data", "Feed through layers", "Read output"],
                "solution": "The network learns distinguishing features.",
            },
            "practice_problems": [
                {"problem": "Train a digit classifier", "hint": "Use MNIST", "difficulty": "easy"},
            ],
            "real_world_applications": ["Image recognition", "Language translation"],
            "simulation_prompt": "Try changing the learning rate.",
            "cross_domain_transfer": "Neural nets parallel biological neural pathways.",
        },
        LayerName.REFLECTION: {
            "calibration_questions": [
                "Explain neural networks in your own words.",
                "What is the most important component?",
                "How would you teach this?",
            ],
            "confidence_check": "Rate your understanding 1-10.",
            "misconception_alerts": ["They don't truly 'understand'.", "More layers != always better."],
            "connection_prompts": ["How does this relate to statistics?"],
            "next_steps": ["Explore deep learning", "Try a hands-on tutorial"],
        },
        LayerName.SYNTHESIS: {
            "synthesized_response": "Neural networks are computational models inspired by biological brains.",
            "key_takeaway": "Neural networks learn patterns from data through interconnected layers.",
            "layers_integrated": ["activation", "metaphor", "structure", "interrogation", "encoding", "transfer", "reflection"],
        },
    }


@pytest.fixture()
def full_record() -> ArtifactRecord:
    audience = _make_audience()
    artifact = CognitiveArtifact(topic="neural networks", audience=audience)

    layers = _layer_content()
    for layer, content in layers.items():
        artifact.set_layer(
            layer,
            LayerOutput(layer=layer, content=content, confidence=0.75),
        )

    artifact.evaluation = EvaluationResult(
        overall_score=0.72,
        layer_scores={ln.value: 0.75 for ln in LayerName},
        penalty_applied=False,
    )

    return ArtifactRecord(artifact=artifact, profile_name="chatbot_tutor")


@pytest.fixture()
def record_no_eval(full_record: ArtifactRecord) -> ArtifactRecord:
    full_record.artifact.evaluation = None
    return full_record


# ── ChatbotAdapter ─────────────────────────────────────────


class TestChatbotAdapter:
    def test_returns_list_of_messages(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        assert isinstance(messages, list)
        assert len(messages) > 0

    def test_message_ordering(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        layer_order = [m["layer"] for m in messages if m["layer"] != "evaluation"]
        # full_record fixture has original 8 layers populated
        expected = ["activation", "metaphor", "structure", "interrogation",
                    "encoding", "transfer", "reflection", "synthesis"]
        assert layer_order == expected

    def test_evaluation_message_appended(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        last = messages[-1]
        assert last["layer"] == "evaluation"
        assert last["role"] == "system"
        assert "72%" in last["content"]

    def test_no_evaluation_message_when_missing(self, record_no_eval):
        messages = ChatbotAdapter().format(record_no_eval)
        assert all(m["layer"] != "evaluation" for m in messages)

    def test_format_activation_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        activation_msg = next(m for m in messages if m["layer"] == "activation")
        text = activation_msg["content"]
        assert "Ever wondered" in text
        assert "misunderstand neurons" in text
        assert "changes everything" in text
        assert "Emotional trigger" in text
        assert "Build on what you know" in text

    def test_format_metaphor_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "metaphor")
        text = msg["content"]
        assert "kitchen brigade" in text
        assert "restaurant_kitchen" in text
        assert "ingredients" in text
        assert "Scale differs" in text
        assert "rush-hour" in text

    def test_format_structure_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "structure")
        text = msg["content"]
        assert "interconnected nodes" in text
        assert "neuron" in text
        assert "feeds" in text or "input" in text
        assert "layered graph" in text

    def test_format_interrogation_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "interrogation")
        text = msg["content"]
        assert "purpose of a neural network" in text
        assert "Linear problems" in text
        assert "perceptrons" in text
        assert "think like humans" in text
        assert "cooperate" in text

    def test_format_encoding_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "encoding")
        text = msg["content"]
        assert "N-W-L-A" in text
        assert "Nodes" in text
        assert "nodes and weights" in text
        assert "What is a neuron" in text
        assert "layered cake" in text

    def test_format_transfer_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "transfer")
        text = msg["content"]
        assert "cats vs dogs" in text
        assert "MNIST" in text or "digit" in text
        assert "Image recognition" in text
        assert "learning rate" in text
        assert "biological" in text

    def test_format_reflection_renders_all_fields(self, full_record):
        messages = ChatbotAdapter().format(full_record)
        msg = next(m for m in messages if m["layer"] == "reflection")
        text = msg["content"]
        assert "own words" in text
        assert "1-10" in text
        assert "truly" in text
        assert "statistics" in text
        assert "deep learning" in text

    def test_missing_layer_is_skipped(self):
        audience = _make_audience()
        artifact = CognitiveArtifact(topic="test", audience=audience)
        artifact.set_layer(
            LayerName.STRUCTURE,
            LayerOutput(layer=LayerName.STRUCTURE, content={"definition": "A test concept."}, confidence=0.5),
        )
        record = ArtifactRecord(artifact=artifact, profile_name="test")
        messages = ChatbotAdapter().format(record)
        layers = [m["layer"] for m in messages]
        assert "structure" in layers
        assert "activation" not in layers


# ── RAGAdapter ──────────────────────────────────────────────


class TestRAGAdapter:
    def test_returns_chunk_list(self, full_record):
        chunks = RAGAdapter().format(full_record)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_one_chunk_per_significant_field(self, full_record):
        chunks = RAGAdapter().format(full_record)
        # Every chunk should have required keys
        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "content" in chunk
            assert "metadata" in chunk

    def test_chunk_metadata_has_required_keys(self, full_record):
        chunks = RAGAdapter().format(full_record)
        for chunk in chunks:
            meta = chunk["metadata"]
            assert "topic" in meta
            assert "layer" in meta
            assert "field" in meta
            assert "confidence" in meta
            assert "score" in meta

    def test_to_text_handles_types(self):
        adapter = RAGAdapter()
        assert adapter._to_text("hello") == "hello"
        assert "a\nb" == adapter._to_text(["a", "b"])
        assert "k: v" in adapter._to_text({"k": "v"})

    def test_short_values_are_skipped(self, full_record):
        chunks = RAGAdapter().format(full_record)
        for chunk in chunks:
            assert len(chunk["content"]) >= 10


# ── ETLAdapter ──────────────────────────────────────────────


class TestETLAdapter:
    def test_returns_flat_dict(self, full_record):
        result = ETLAdapter().format(full_record)
        assert isinstance(result, dict)

    def test_has_artifact_and_cv_fields(self, full_record):
        result = ETLAdapter().format(full_record)
        assert result["topic"] == "neural networks"
        assert result["audience_id"] == "child"
        assert "cv_language_level" in result
        assert "cv_abstraction" in result
        assert "cv_rigor" in result
        assert "cv_math_density" in result
        assert "cv_domain_specificity" in result
        assert "cv_cognitive_load" in result
        assert "cv_transfer_distance" in result

    def test_per_layer_populated_and_confidence(self, full_record):
        result = ETLAdapter().format(full_record)
        # Check the original 8 layers populated in fixture
        original_layers = [
            LayerName.ACTIVATION, LayerName.METAPHOR, LayerName.STRUCTURE,
            LayerName.INTERROGATION, LayerName.ENCODING, LayerName.TRANSFER,
            LayerName.REFLECTION, LayerName.SYNTHESIS,
        ]
        for layer in original_layers:
            assert result[f"layer_{layer.value}_populated"] is True
            assert result[f"layer_{layer.value}_confidence"] == 0.75
        # New layers should not be populated in this fixture
        new_layers = [
            LayerName.DIAGNOSTIC, LayerName.CONTEXTUALIZATION,
            LayerName.NARRATIVE, LayerName.CHALLENGE, LayerName.ELABORATION,
        ]
        for layer in new_layers:
            assert result[f"layer_{layer.value}_populated"] is False
            assert result[f"layer_{layer.value}_confidence"] is None

    def test_score_and_evaluation_fields(self, full_record):
        result = ETLAdapter().format(full_record)
        assert result["score"] == 0.72
        assert result["penalty_applied"] is False

    def test_handles_missing_evaluation(self, record_no_eval):
        result = ETLAdapter().format(record_no_eval)
        assert result["score"] is None
        assert result["penalty_applied"] is False
        assert result["missing_required"] == []
