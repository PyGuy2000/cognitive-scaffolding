"""Reflection operator - Layer 7: Meta-cognition.

Calibration prompts, metacognitive checks, misconception detection, confidence assessment.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class ReflectionOperator(BaseOperator):
    """Generates metacognitive content: calibration, self-assessment, reflection."""

    layer_name = LayerName.REFLECTION

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        prior = []
        if "interrogation" in context:
            misconceptions = context["interrogation"].get("misconception_probes", [])
            if misconceptions:
                prior.append(f"Misconceptions identified: {misconceptions}")
        if "encoding" in context:
            chunks = context["encoding"].get("chunks", [])
            if chunks:
                labels = [c.get("label", "") for c in chunks if isinstance(c, dict)]
                prior.append(f"Key chunks: {labels}")

        prior_text = "\n".join(prior) if prior else ""

        return f"""Generate metacognitive reflection content for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Rigor: {cv.rigor:.1f}, Cognitive load: {cv.cognitive_load:.1f}
{prior_text}

Produce a JSON object with:
- "calibration_questions": 3-4 questions to assess understanding depth (list)
- "confidence_check": A prompt asking the learner to rate their understanding
- "misconception_alerts": 2-3 common mistakes to watch for (list)
- "connection_prompts": 2-3 prompts linking to prior knowledge or other topics (list)
- "next_steps": Suggested directions for deeper learning (list)

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self, topic: str, audience: AudienceProfile, context: Dict[str, Any], config: Dict[str, Any],
    ) -> str:
        return json.dumps({
            "calibration_questions": [
                f"Can you explain {topic} in your own words?",
                f"What's the most important aspect of {topic}?",
                f"How would you teach {topic} to someone else?",
            ],
            "confidence_check": f"On a scale of 1-10, how confident are you in your understanding of {topic}?",
            "misconception_alerts": [f"Don't confuse {topic} with similar-sounding concepts."],
            "connection_prompts": [f"How does {topic} relate to what you already know?"],
            "next_steps": [f"Explore advanced aspects of {topic}", "Try applying it to a real problem"],
        })
