"""Structure operator - Layer 3: Precision and organization.

Produces definitions, taxonomies, diagrams, and formal notation.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class StructureOperator(BaseOperator):
    """Generates structured, precise content: definitions, taxonomies, diagrams."""

    layer_name = LayerName.STRUCTURE

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        prior = ""
        if "metaphor" in context:
            mapping = context["metaphor"].get("mapping", {})
            if mapping:
                prior = f"\nBuild on these metaphor mappings: {json.dumps(mapping)}"

        return f"""Generate structured content for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Rigor: {cv.rigor:.1f}, Math density: {cv.math_density:.1f}, Domain specificity: {cv.domain_specificity:.1f}
{prior}

Produce a JSON object with:
- "definition": A precise definition appropriate for the audience
- "taxonomy": Classification/categorization of key components (dict)
- "key_terms": Important terminology with brief definitions (dict)
- "relationships": How components relate to each other (list of dicts with "from", "to", "type")
- "diagram_description": A textual description of a diagram that would illustrate the concept
- "formal_notation": Formal/mathematical notation if appropriate (empty string if not)

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self, topic: str, audience: AudienceProfile, context: Dict[str, Any], config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        if concept:
            desc = concept.get("description", f"{topic} is a concept involving structured processes and components.")
            category = concept.get("category", "general").replace("_", " ")
            components = concept.get("key_components", [])
            related = concept.get("related_concepts", [])
            key_terms = {c.replace("_", " "): f"A key component of {topic}" for c in components} if components else {topic.lower(): "The primary concept under study"}
            relationships = [{"from": topic, "to": r.replace("_", " "), "type": "related_to"} for r in related] if related else [{"from": "input", "to": "output", "type": "transforms"}]
            return json.dumps({
                "definition": f"{topic} — {desc}.",
                "taxonomy": {"category": category, "subcategories": [c.replace("_", " ") for c in components[:3]]},
                "key_terms": key_terms,
                "relationships": relationships,
                "diagram_description": f"A flowchart showing the main components of {topic} and their connections.",
                "formal_notation": "",
            })
        return json.dumps({
            "definition": f"{topic} is a concept involving structured processes and components.",
            "taxonomy": {"category": "general", "subcategories": ["core", "supporting"]},
            "key_terms": {topic.lower(): "The primary concept under study"},
            "relationships": [{"from": "input", "to": "output", "type": "transforms"}],
            "diagram_description": f"A flowchart showing the main components of {topic} and their connections.",
            "formal_notation": "",
        })
