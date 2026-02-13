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
    expected_keys = ["worked_example", "practice_problems", "real_world_applications", "simulation_prompt", "cross_domain_transfer"]

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
        concept = config.get("concept")
        aud = config.get("audience_data")
        domain = config.get("domain")

        # Audience-aware: preferred_domains, primary_tools
        preferred_domains = (aud.get("preferred_domains") or []) if aud else []
        primary_tools = (aud.get("primary_tools") or []) if aud else []

        # Domain-aware: name, examples
        domain_name = (domain.get("name") or "") if domain else ""
        domain_examples = (domain.get("examples") or []) if domain else []

        if concept:
            related = concept.get("related_concepts", [])
            components = concept.get("key_components", [])

            # Steps use domain examples or audience tools when available
            if domain_examples:
                steps = [f"Apply {e.replace('_', ' ')} to understand {c.replace('_', ' ')}" for c, e in zip(components, domain_examples)] if components else [f"Use {e.replace('_', ' ')}" for e in domain_examples[:3]]
            elif primary_tools:
                tool = primary_tools[0].replace("_", " ")
                steps = [f"In {tool}, implement {c.replace('_', ' ')}" for c in components] if components else [f"Use {tool} to explore the concept"]
            else:
                steps = [f"Understand {c.replace('_', ' ')}" for c in components] if components else ["Identify the components", "Apply the principle", "Verify the result"]

            # Cross-domain: domain name > audience preferred_domains > related concepts
            if domain_name and domain_name.lower() != "general":
                cross_domain = f"{topic} can be understood through {domain_name} — the same principles apply."
            elif preferred_domains:
                domain_ref = preferred_domains[0].replace("_", " ")
                cross_domain = f"{topic} connects to {domain_ref} and {', '.join(r.replace('_', ' ') for r in related)}." if related else f"{topic} connects to {domain_ref}."
            elif related:
                cross_domain = f"{topic} connects to {', '.join(r.replace('_', ' ') for r in related)}."
            else:
                cross_domain = f"{topic} has parallels in natural systems."

            return json.dumps({
                "worked_example": {
                    "problem": f"Apply {topic} to a simple scenario",
                    "steps": steps,
                    "solution": "The result demonstrates the core principle.",
                },
                "practice_problems": [
                    {"problem": f"Given a basic scenario, apply {topic}", "hint": "Start with the definition", "difficulty": "easy"},
                ],
                "real_world_applications": [f"{topic} is used in industry for optimization."],
                "simulation_prompt": f"Imagine a system where {topic} is the key mechanism. What happens when you change one variable?",
                "cross_domain_transfer": cross_domain,
            })

        # Generic branch with audience/domain awareness
        if domain_examples:
            steps = [f"Use {e.replace('_', ' ')}" for e in domain_examples[:3]]
        elif primary_tools:
            tool = primary_tools[0].replace("_", " ")
            steps = [f"Use {tool} to identify the components", "Apply the principle", "Verify the result"]
        else:
            steps = ["Identify the components", "Apply the principle", "Verify the result"]

        if domain_name and domain_name.lower() != "general":
            cross_domain = f"{topic} can be understood through {domain_name} — the same principles apply."
        elif preferred_domains:
            cross_domain = f"{topic} connects to {preferred_domains[0].replace('_', ' ')}."
        else:
            cross_domain = f"{topic} has parallels in natural systems."

        return json.dumps({
            "worked_example": {
                "problem": f"Apply {topic} to a simple scenario",
                "steps": steps,
                "solution": "The result demonstrates the core principle.",
            },
            "practice_problems": [
                {"problem": f"Given a basic scenario, apply {topic}", "hint": "Start with the definition", "difficulty": "easy"},
            ],
            "real_world_applications": [f"{topic} is used in industry for optimization."],
            "simulation_prompt": f"Imagine a system where {topic} is the key mechanism. What happens when you change one variable?",
            "cross_domain_transfer": cross_domain,
        })
