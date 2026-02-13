"""End-to-end integration tests with a real AI client.

These tests are gated on ANTHROPIC_API_KEY being set in the environment.
They exercise the full pipeline with a real AI client and compare output
against fallback-only baselines.

Run:
    ANTHROPIC_API_KEY=sk-... python -m pytest tests/integration/test_ai_pipeline.py -v
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

HAS_API_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))
PROFILES_DIR = str(PROJECT_ROOT / "profiles")
DATA_DIR = str(PROJECT_ROOT / "data")

skip_no_key = pytest.mark.skipif(not HAS_API_KEY, reason="No ANTHROPIC_API_KEY set")
slow = pytest.mark.slow


def _build_ai_conductor():
    from utils.ai_client import AIClient
    ai_client = AIClient(provider="anthropic")
    return CognitiveConductor(
        ai_client=ai_client,
        profiles_dir=PROFILES_DIR,
        data_dir=DATA_DIR,
    )


def _build_fallback_conductor():
    return CognitiveConductor(
        ai_client=None,
        profiles_dir=PROFILES_DIR,
        data_dir=DATA_DIR,
    )


EXPECTED_LAYERS = {"activation", "metaphor", "structure", "interrogation", "encoding", "transfer", "reflection"}


@skip_no_key
@slow
class TestAIPipeline:

    def test_ai_produces_valid_artifact(self):
        conductor = _build_ai_conductor()
        record = conductor.compile("neural networks", "general")
        artifact = record.artifact

        assert artifact.evaluation is not None
        assert artifact.evaluation.overall_score > 0.5

        for layer_name in EXPECTED_LAYERS:
            layer_output = artifact.get_layer(layer_name)
            assert layer_output is not None, f"Missing layer: {layer_name}"
            assert isinstance(layer_output.content, dict), f"Layer {layer_name} content not a dict"

    def test_ai_scores_higher_than_fallback(self):
        ai_conductor = _build_ai_conductor()
        fb_conductor = _build_fallback_conductor()

        ai_record = ai_conductor.compile("neural networks", "general")
        fb_record = fb_conductor.compile("neural networks", "general")

        ai_score = ai_record.artifact.evaluation.overall_score
        fb_score = fb_record.artifact.evaluation.overall_score

        assert ai_score >= fb_score, (
            f"AI score ({ai_score:.3f}) should be >= fallback score ({fb_score:.3f})"
        )

    def test_ai_layers_have_rich_content(self):
        ai_conductor = _build_ai_conductor()
        fb_conductor = _build_fallback_conductor()

        ai_record = ai_conductor.compile("neural networks", "general")
        fb_record = fb_conductor.compile("neural networks", "general")

        for layer_name in EXPECTED_LAYERS:
            ai_layer = ai_record.artifact.get_layer(layer_name)
            fb_layer = fb_record.artifact.get_layer(layer_name)
            if ai_layer and fb_layer:
                ai_len = len(str(ai_layer.content))
                fb_len = len(str(fb_layer.content))
                assert ai_len >= fb_len, (
                    f"AI {layer_name} ({ai_len} chars) should be >= fallback ({fb_len} chars)"
                )

    def test_ai_with_concept_data(self):
        conductor = _build_ai_conductor()
        record = conductor.compile("neural networks", "data_scientist")
        artifact = record.artifact

        # Check that AI output references concept-specific terms
        all_content = str(artifact.model_dump())
        lower_content = all_content.lower()
        # Should reference neural-network-specific terms, not just generic
        assert any(term in lower_content for term in ["neuron", "node", "layer", "weight", "activation"]), (
            "AI output should reference neural network concepts"
        )
