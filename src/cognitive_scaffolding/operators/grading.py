"""Grading operator - Evaluates artifact quality.

Rubric-based scoring, diagnostics, gap analysis, revision planning.
Note: This is NOT a cognitive layer in the 7-layer model. It operates on
the completed artifact to evaluate and suggest improvements.
"""

from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName, LayerOutput
from cognitive_scaffolding.operators.base import BaseOperator


class GradingOperator(BaseOperator):
    """Evaluates artifact quality and suggests revisions."""

    layer_name = LayerName.REFLECTION  # Grading operates as part of reflection

    def execute(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config=None,
    ) -> LayerOutput:
        """Override execute to perform rubric-based grading on accumulated context."""
        config = config or {}

        # Grade based on what's been produced
        grades = self._grade_layers(context)
        gaps = self._identify_gaps(context, config)
        revision_plan = self._build_revision_plan(grades, gaps)

        content = {
            "layer_grades": grades,
            "gaps": gaps,
            "revision_plan": revision_plan,
            "overall_quality": self._compute_quality(grades),
        }

        confidence = min(0.9, 0.5 + 0.1 * len(context))

        return LayerOutput(
            layer=self.layer_name,
            content=content,
            confidence=confidence,
            provenance={
                "operator": "GradingOperator",
                "ai_available": bool(self.ai_client and self.ai_client.is_available()),
                "layers_graded": list(context.keys()),
            },
        )

    def _grade_layers(self, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Grade each populated layer on completeness and richness."""
        grades = {}
        for layer_name, content in context.items():
            if not isinstance(content, dict):
                grades[layer_name] = {"score": 0.3, "reason": "Non-dict content"}
                continue

            num_keys = len(content)
            total_len = sum(len(str(v)) for v in content.values())

            if num_keys == 0:
                score = 0.0
            elif total_len < 100:
                score = 0.4
            elif total_len < 500:
                score = 0.6
            elif total_len < 1500:
                score = 0.8
            else:
                score = 0.9

            grades[layer_name] = {
                "score": score,
                "num_fields": num_keys,
                "content_length": total_len,
            }
        return grades

    def _identify_gaps(self, context: Dict[str, Any], config: Dict[str, Any]) -> list:
        """Identify missing or weak areas."""
        expected_layers = ["diagnostic", "activation", "contextualization", "metaphor",
                          "narrative", "structure", "interrogation", "encoding",
                          "transfer", "challenge", "reflection", "elaboration"]
        gaps = []
        for layer in expected_layers:
            if layer not in context:
                gaps.append({"layer": layer, "issue": "missing"})
            elif not context[layer]:
                gaps.append({"layer": layer, "issue": "empty"})
        return gaps

    def _build_revision_plan(self, grades: Dict, gaps: list) -> list:
        """Suggest revisions based on grades and gaps."""
        plan = []
        for gap in gaps:
            plan.append({"action": "generate", "layer": gap["layer"], "reason": gap["issue"]})
        for layer, grade in grades.items():
            if grade.get("score", 0) < 0.5:
                plan.append({"action": "regenerate", "layer": layer, "reason": f"Low score: {grade['score']}"})
        return plan

    def _compute_quality(self, grades: Dict) -> float:
        """Compute overall quality score from layer grades."""
        if not grades:
            return 0.0
        scores = [g.get("score", 0) for g in grades.values()]
        return round(sum(scores) / len(scores), 3)

    def build_prompt(self, topic, audience, context, config):
        """Not used - grading is rule-based, not LLM-based."""
        return ""
