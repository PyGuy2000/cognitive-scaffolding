"""Interrogation operator - Layer 4: Deep processing.

Generates Socratic questions, counterexamples, edge cases, misconception probes.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class InterrogationOperator(BaseOperator):
    """Generates Socratic questions and deep-processing prompts."""

    layer_name = LayerName.INTERROGATION
    expected_keys = ["socratic_questions", "counterexamples", "edge_cases", "misconception_probes", "synthesis_prompt"]

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        prior_layers = []
        if "metaphor" in context:
            limitations = context["metaphor"].get("limitations", [])
            if limitations:
                prior_layers.append(f"Metaphor limitations to probe: {limitations}")
        if "structure" in context:
            terms = list(context["structure"].get("key_terms", {}).keys())
            if terms:
                prior_layers.append(f"Key terms to question: {terms}")

        prior_text = "\n".join(prior_layers) if prior_layers else ""

        return f"""Generate deep-processing questions for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Rigor: {cv.rigor:.1f}, Cognitive load: {cv.cognitive_load:.1f}
{prior_text}

Produce a JSON object with:
- "socratic_questions": 3-5 progressively deeper questions (list)
- "counterexamples": 2-3 scenarios that challenge assumptions (list)
- "edge_cases": 2-3 boundary conditions or unusual scenarios (list)
- "misconception_probes": 2-3 common misconceptions phrased as questions (list)
- "synthesis_prompt": A question that requires integrating multiple aspects

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self, topic: str, audience: AudienceProfile, context: Dict[str, Any], config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        aud = config.get("audience_data")

        # Audience-aware: core_skills, complexity_preference
        core_skills = (aud.get("core_skills") or []) if aud else []
        complexity = (aud.get("complexity_preference") or "medium") if aud else "medium"

        if concept:
            misconceptions = concept.get("common_misconceptions", [])
            components = concept.get("key_components", [])
            properties = concept.get("properties", [])
            misconception_probes = [f"Is it true that '{m.replace('_', ' ')}'?" for m in misconceptions] if misconceptions else [f"Is it true that {topic} always works the same way?"]
            edge_cases = [f"What happens when {c.replace('_', ' ')} reaches its limits?" for c in components] if components else [f"What happens at the boundary conditions of {topic}?"]

            # Questions framed using familiar skills
            if core_skills:
                skill_ref = core_skills[0].replace("_", " ")
                socratic = [f"How does your experience with {skill_ref} help you understand {p.replace('_', ' ')} in {topic}?" for p in properties[:3]] if properties else [f"How does your {skill_ref} background inform your understanding of {topic}?"]
            else:
                socratic = [f"Why is {p.replace('_', ' ')} important for {topic}?" for p in properties[:3]] if properties else [f"What is the fundamental purpose of {topic}?"]

            # Deeper synthesis for high-complexity audiences
            if complexity in ("very_high", "high"):
                synthesis = f"How do all the components of {topic} interact, and where are the failure modes?"
            else:
                synthesis = f"How do all the components of {topic} work together as a system?"

            return json.dumps({
                "socratic_questions": socratic,
                "counterexamples": [f"Consider a scenario where {topic} produces unexpected results."],
                "edge_cases": edge_cases,
                "misconception_probes": misconception_probes,
                "synthesis_prompt": synthesis,
            })

        # Generic branch with audience awareness
        if core_skills:
            skill_ref = core_skills[0].replace("_", " ")
            socratic = [
                f"How does your {skill_ref} background inform your understanding of {topic}?",
                f"How would {topic} behave differently under extreme conditions?",
                f"What would happen if a key component of {topic} were removed?",
            ]
        else:
            socratic = [
                f"What is the fundamental purpose of {topic}?",
                f"How would {topic} behave differently under extreme conditions?",
                f"What would happen if a key component of {topic} were removed?",
            ]

        return json.dumps({
            "socratic_questions": socratic,
            "counterexamples": [f"Consider a scenario where {topic} produces unexpected results."],
            "edge_cases": [f"What happens at the boundary conditions of {topic}?"],
            "misconception_probes": [f"Is it true that {topic} always works the same way?"],
            "synthesis_prompt": f"How do all the components of {topic} work together as a system?",
        })
