"""Unit tests for experiment runner."""

import pytest
from pathlib import Path

from cognitive_scaffolding.orchestrator.conductor import CognitiveConductor
from cognitive_scaffolding.orchestrator.experiment_runner import (
    ExperimentConfig,
    ExperimentReport,
    ExperimentRunner,
    LayerExperimentResult,
    VariantResult,
)


PROFILES_DIR = str(Path(__file__).parent.parent.parent / "profiles")


@pytest.fixture
def conductor():
    return CognitiveConductor(ai_client=None, profiles_dir=PROFILES_DIR)


@pytest.fixture
def runner(conductor):
    return ExperimentRunner(conductor)


class TestExperimentSingleLayer:
    def test_experiment_single_layer(self, runner):
        """Toggle one layer, verify score delta computed."""
        config = ExperimentConfig(
            topic="neural networks",
            audience_id="general",
            profile_name="chatbot_tutor",
            toggle_layers=["metaphor"],
        )
        report = runner.run(config)

        assert len(report.layer_results) == 1
        result = report.layer_results[0]
        assert result.layer == "metaphor"
        assert result.enabled_score >= 0.0
        assert result.disabled_score >= 0.0
        assert result.score_delta == pytest.approx(
            result.enabled_score - result.disabled_score, abs=1e-4
        )
        # Enabled variant should have metaphor populated
        assert "metaphor" in result.enabled_result.populated_layers
        # Disabled variant should NOT have metaphor populated
        assert "metaphor" not in result.disabled_result.populated_layers


class TestExperimentMultipleLayers:
    def test_experiment_multiple_layers(self, runner):
        """Toggle 2+ layers, verify each gets its own result."""
        config = ExperimentConfig(
            topic="transformers",
            audience_id="data_scientist",
            profile_name="chatbot_tutor",
            toggle_layers=["activation", "encoding"],
        )
        report = runner.run(config)

        assert len(report.layer_results) == 2
        layers_tested = [r.layer for r in report.layer_results]
        assert "activation" in layers_tested
        assert "encoding" in layers_tested

        # Each result should have distinct variant names
        for result in report.layer_results:
            assert result.enabled_result.variant_name == f"{result.layer}_enabled"
            assert result.disabled_result.variant_name == f"{result.layer}_disabled"


class TestExperimentBaseline:
    def test_experiment_baseline(self, runner, conductor):
        """Verify baseline matches unmodified compile."""
        config = ExperimentConfig(
            topic="gradient descent",
            audience_id="general",
            profile_name="chatbot_tutor",
            toggle_layers=["metaphor"],
        )
        report = runner.run(config)

        # Run an independent compile for comparison
        independent_record = conductor.compile(
            topic="gradient descent",
            audience_id="general",
            profile_name="chatbot_tutor",
        )
        assert report.baseline_score == pytest.approx(
            independent_record.artifact.evaluation.overall_score, abs=1e-4
        )


class TestExperimentReportStructure:
    def test_experiment_report_structure(self, runner):
        """All fields populated in report."""
        config = ExperimentConfig(
            topic="backpropagation",
            audience_id="child",
            profile_name="chatbot_tutor",
            toggle_layers=["activation"],
        )
        report = runner.run(config)

        # Top-level fields
        assert isinstance(report.experiment_id, str)
        assert len(report.experiment_id) > 0
        assert report.config is config
        assert report.baseline_score >= 0.0
        assert report.baseline_record is not None
        assert report.baseline_record.artifact.evaluation is not None
        assert report.timestamp is not None
        assert report.total_duration_ms > 0

        # Layer result fields
        result = report.layer_results[0]
        assert isinstance(result, LayerExperimentResult)
        assert isinstance(result.enabled_result, VariantResult)
        assert isinstance(result.disabled_result, VariantResult)
        assert isinstance(result.enabled_result.toggle_state, dict)
        assert result.enabled_result.toggle_state["activation"] is True
        assert result.disabled_result.toggle_state["activation"] is False
        assert isinstance(result.enabled_result.layer_scores, dict)
        assert isinstance(result.enabled_result.populated_layers, list)


class TestSummaryOutput:
    def test_summary_output(self, runner):
        """Summary dict format correct."""
        config = ExperimentConfig(
            topic="attention mechanism",
            audience_id="general",
            profile_name="chatbot_tutor",
            toggle_layers=["metaphor", "encoding"],
        )
        report = runner.run(config)
        summary = ExperimentRunner.summary(report)

        assert "experiment_id" in summary
        assert "baseline_score" in summary
        assert "layer_deltas" in summary
        assert "best_layer" in summary
        assert "worst_layer" in summary
        assert "total_duration_ms" in summary

        # layer_deltas should have one entry per toggled layer
        assert set(summary["layer_deltas"].keys()) == {"metaphor", "encoding"}
        # best/worst should be one of the tested layers
        assert summary["best_layer"] in {"metaphor", "encoding"}
        assert summary["worst_layer"] in {"metaphor", "encoding"}
