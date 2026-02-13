"""Challenge operator - Productive Difficulty layer.

Creates structured challenges calibrated to Bloom's taxonomy levels.
Learning science shows "desirable difficulties" (interleaving, generation
effects) strengthen retention. Uses AudienceControlVector.cognitive_load
to calibrate and reads DiagnosticOperator output to adjust Bloom's level.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


# Bloom's taxonomy levels in order
_BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

# Map expertise levels to default Bloom's starting level
_EXPERTISE_TO_BLOOM = {
    "beginner": "remember",
    "intermediate": "apply",
    "advanced": "analyze",
    "expert": "evaluate",
}


class ChallengeOperator(BaseOperator):
    """Generates structured challenges calibrated to Bloom's taxonomy levels."""

    layer_name = LayerName.CHALLENGE
    expected_keys = [
        "bloom_level", "challenge_prompt", "scaffolded_hints",
        "difficulty_justification", "expected_struggle_points",
    ]

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        bloom = self._select_bloom_level(audience, context)
        concept = config.get("concept", {})
        components = concept.get("key_components", []) if concept else []

        components_text = f"\nKey components: {', '.join(c.replace('_', ' ') for c in components)}" if components else ""

        return f"""Design a structured challenge for the topic "{topic}" at Bloom's taxonomy level: {bloom}.

Target audience: {audience.name} (expertise: {audience.expertise_level})
Cognitive load tolerance: {cv.cognitive_load:.1f}
{components_text}

Produce a JSON object with:
- "bloom_level": The Bloom's taxonomy level ("{bloom}")
- "challenge_prompt": A clear, specific challenge that tests {bloom}-level understanding (2-4 sentences)
- "scaffolded_hints": 3-4 progressive hints from subtle to explicit (list)
- "difficulty_justification": Why this difficulty level is appropriate for this audience (1-2 sentences)
- "expected_struggle_points": 2-3 points where learners commonly get stuck (list)

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")

        bloom = self._select_bloom_level(audience, context)
        components = concept.get("key_components", []) if concept else []
        prereqs = concept.get("prerequisite_concepts", []) if concept else []
        misconceptions = concept.get("common_misconceptions", []) if concept else []

        # Challenge prompt varies by Bloom's level
        challenge_prompts = {
            "remember": f"List the key components of {topic} and define each one in your own words.",
            "understand": f"Explain how the different parts of {topic} work together. Use an example to illustrate.",
            "apply": f"Given a new scenario, apply the principles of {topic} to solve the problem. Show your reasoning step by step.",
            "analyze": f"Compare and contrast two different approaches to {topic}. What are the trade-offs of each?",
            "evaluate": f"Critically evaluate the effectiveness of {topic} in a real-world application. What are its strengths and limitations?",
            "create": f"Design a novel application or extension of {topic} that addresses a problem not covered in the standard treatment.",
        }

        prompt = challenge_prompts.get(bloom, challenge_prompts["apply"])

        # Scaffolded hints: from subtle to explicit
        hints = []
        if components:
            comp_names = [c.replace("_", " ") for c in components[:3]]
            hints.append(f"Start by thinking about the role of {comp_names[0]}.")
            if len(comp_names) > 1:
                hints.append(f"Consider how {comp_names[0]} and {comp_names[1]} interact.")
            hints.append(f"The key insight involves understanding all of: {', '.join(comp_names)}.")
        else:
            hints.append(f"Start by recalling the definition of {topic}.")
            hints.append(f"Think about what makes {topic} different from related concepts.")
            hints.append(f"Consider the underlying principles that drive {topic}.")
        hints.append(f"Review the core structure of {topic} and work through it systematically.")

        # Difficulty justification
        justification = f"This {bloom}-level challenge is appropriate for {audience.expertise_level} learners, "
        if bloom in ("remember", "understand"):
            justification += "building foundational knowledge before advancing to application."
        elif bloom in ("apply", "analyze"):
            justification += "pushing beyond memorization toward deeper understanding."
        else:
            justification += "engaging higher-order thinking to solidify expert-level mastery."

        # Struggle points
        struggles = []
        if misconceptions:
            struggles.append(f"Confusing {topic} with: {misconceptions[0].replace('_', ' ')}")
        if prereqs:
            struggles.append(f"Gaps in prerequisite knowledge: {prereqs[0].replace('_', ' ')}")
        struggles.append(f"Difficulty seeing how the components of {topic} connect to each other")

        return json.dumps({
            "bloom_level": bloom,
            "challenge_prompt": prompt,
            "scaffolded_hints": hints,
            "difficulty_justification": justification,
            "expected_struggle_points": struggles,
        })

    @staticmethod
    def _select_bloom_level(audience: AudienceProfile, context: Dict[str, Any]) -> str:
        """Select Bloom's level based on expertise and diagnostic output."""
        # Start from expertise-based default
        base_level = _EXPERTISE_TO_BLOOM.get(audience.expertise_level, "apply")
        base_idx = _BLOOM_LEVELS.index(base_level)

        # Adjust based on diagnostic output if available
        diagnostic = context.get("diagnostic", {})
        if diagnostic:
            if diagnostic.get("skip_basics"):
                # Push up one level
                base_idx = min(len(_BLOOM_LEVELS) - 1, base_idx + 1)
            gaps = diagnostic.get("prerequisite_gaps", [])
            if len(gaps) >= 2:
                # Pull down one level if many gaps
                base_idx = max(0, base_idx - 1)

        # Also consider cognitive load
        cv = audience.control_vector
        if cv.cognitive_load < 0.3:
            base_idx = max(0, base_idx - 1)
        elif cv.cognitive_load > 0.7:
            base_idx = min(len(_BLOOM_LEVELS) - 1, base_idx + 1)

        return _BLOOM_LEVELS[base_idx]
