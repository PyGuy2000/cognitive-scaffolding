"""Transfer operator - Layer 6: Application.

Produces worked examples, problem sets, simulations, real-world applications.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class TransferOperator(BaseOperator):
    """Generates application content: examples, problems, real-world scenarios."""

    layer_name = LayerName.TRANSFER

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        prior = ""
        if "structure" in context:
            definition = context["structure"].get("definition", "")
            if definition:
                prior = f"\nCore definition: {definition}"

        return f"""Generate application and transfer content for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Transfer distance: {cv.transfer_distance:.1f}, Domain specificity: {cv.domain_specificity:.1f}
{prior}

Produce a JSON object with:
- "worked_example": A step-by-step worked example (dict with "problem", "steps" list, "solution")
- "practice_problems": 2-3 practice problems of increasing difficulty (list of dicts with "problem", "hint", "difficulty")
- "real_world_applications": 2-3 real-world scenarios where this applies (list)
- "simulation_prompt": A thought experiment or simulation setup
- "cross_domain_transfer": How this concept applies in a different domain

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self, topic: str, audience: AudienceProfile, context: Dict[str, Any], config: Dict[str, Any],
    ) -> str:
        return json.dumps({
            "worked_example": {
                "problem": f"Apply {topic} to a simple scenario",
                "steps": ["Identify the components", "Apply the principle", "Verify the result"],
                "solution": "The result demonstrates the core principle.",
            },
            "practice_problems": [
                {"problem": f"Given a basic scenario, apply {topic}", "hint": "Start with the definition", "difficulty": "easy"},
            ],
            "real_world_applications": [f"{topic} is used in industry for optimization."],
            "simulation_prompt": f"Imagine a system where {topic} is the key mechanism. What happens when you change one variable?",
            "cross_domain_transfer": f"{topic} has parallels in natural systems.",
        })
