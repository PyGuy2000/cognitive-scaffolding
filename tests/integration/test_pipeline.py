"""Integration tests for end-to-end pipeline."""

from pathlib import Path

from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor
from cognitive_scaffolding.adapters.chatbot_adapter import ChatbotAdapter
from cognitive_scaffolding.adapters.rag_adapter import RAGAdapter
from cognitive_scaffolding.adapters.etl_adapter import ETLAdapter


PROFILES_DIR = str(Path(__file__).parent.parent.parent / "profiles")


class TestChatbotPipeline:
    def test_compile_and_format(self):
        conductor = CognitiveConductor(
            ai_client=None,
            profiles_dir=PROFILES_DIR,
        )
        record = conductor.compile(
            topic="ancillary services",
            audience_id="child",
            profile_name="chatbot_tutor",
        )
        assert record.artifact.topic == "ancillary services"
        assert record.artifact.evaluation is not None
        assert record.artifact.evaluation.overall_score > 0

        adapter = ChatbotAdapter()
        messages = adapter.format(record)
        assert isinstance(messages, list)
        assert len(messages) > 0
        assert all("content" in m for m in messages)
        assert all("layer" in m for m in messages)


class TestRAGPipeline:
    def test_compile_and_format(self):
        conductor = CognitiveConductor(
            ai_client=None,
            profiles_dir=PROFILES_DIR,
        )
        record = conductor.compile(
            topic="neural networks",
            audience_id="data_scientist",
            profile_name="rag_explainer",
        )
        adapter = RAGAdapter()
        chunks = adapter.format(record)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "content" in chunk
            assert "metadata" in chunk
            assert chunk["metadata"]["topic"] == "neural networks"


class TestETLPipeline:
    def test_compile_and_format(self):
        conductor = CognitiveConductor(
            ai_client=None,
            profiles_dir=PROFILES_DIR,
        )
        record = conductor.compile(
            topic="transformers",
            audience_id="general",
            profile_name="etl_explain",
        )
        adapter = ETLAdapter()
        result = adapter.format(record)
        assert isinstance(result, dict)
        assert result["topic"] == "transformers"
        assert result["audience_id"] == "general"
        assert "score" in result
        assert "layers_populated" in result
        assert isinstance(result["num_layers"], int)


class TestOverrides:
    def test_runtime_overrides(self):
        conductor = CognitiveConductor(
            ai_client=None,
            profiles_dir=PROFILES_DIR,
        )
        # Disable all layers except structure
        overrides = {
            "activation": {"enabled": False},
            "metaphor": {"enabled": False},
            "interrogation": {"enabled": False},
            "encoding": {"enabled": False},
            "transfer": {"enabled": False},
            "reflection": {"enabled": False},
        }
        record = conductor.compile(
            topic="test",
            audience_id="general",
            profile_name="chatbot_tutor",
            overrides=overrides,
        )
        populated = record.artifact.populated_layers()
        assert "structure" in populated
        # Other layers should not be populated
        assert "activation" not in populated
