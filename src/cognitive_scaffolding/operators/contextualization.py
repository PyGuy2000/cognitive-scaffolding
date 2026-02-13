"""Contextualization operator - Big Picture layer.

Positioned between Activation and Metaphor. Addresses where a topic sits
in the larger landscape: historical development, current trends, adjacent
fields. Uses concept YAML fields (category, related_concepts, evolution_rate)
that are otherwise underutilized.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


# Evolution rate to trend description mapping
_EVOLUTION_TRENDS = {
    "rapid": "This field is evolving rapidly with frequent breakthroughs.",
    "fast": "This area sees frequent new developments and active research.",
    "medium": "This field evolves at a moderate pace with steady progress.",
    "slow": "This is a well-established area with foundational principles that change slowly.",
    "stable": "This topic represents stable, well-understood knowledge.",
}


class ContextualizationOperator(BaseOperator):
    """Provides big-picture context: field landscape, history, trends, adjacencies."""

    layer_name = LayerName.CONTEXTUALIZATION
    expected_keys = [
        "field_context", "historical_timeline", "current_trends",
        "adjacent_topics", "why_now",
    ]

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        concept = config.get("concept", {})
        category = (concept.get("category", "") if concept else "").replace("_", " ")
        related = concept.get("related_concepts", []) if concept else []
        evolution = concept.get("evolution_rate", "medium") if concept else "medium"

        category_text = f"\nField/category: {category}" if category else ""
        related_text = f"\nRelated concepts: {', '.join(r.replace('_', ' ') for r in related)}" if related else ""

        return f"""Generate big-picture contextualization for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Abstraction level: {cv.abstraction:.1f}, Domain specificity: {cv.domain_specificity:.1f}
Evolution rate: {evolution}
{category_text}{related_text}

Produce a JSON object with:
- "field_context": Where this topic sits in its broader field (1-2 paragraphs)
- "historical_timeline": Key milestones in this topic's development (list of strings, chronological)
- "current_trends": What's happening now in this area (1-2 sentences)
- "adjacent_topics": Neighboring fields/topics that interact with this one (list)
- "why_now": Why this topic is relevant right now (1-2 sentences)

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        domain = config.get("domain")

        category = ""
        related = []
        evolution_rate = "medium"
        prereqs = []

        if concept:
            category = concept.get("category", "").replace("_", " ")
            related = concept.get("related_concepts", [])
            evolution_rate = concept.get("evolution_rate", "medium")
            prereqs = concept.get("prerequisite_concepts", [])

        # Field context
        if category:
            field_context = f"{topic} is a key concept within {category}."
            if related:
                field_context += f" It connects to {', '.join(r.replace('_', ' ') for r in related[:3])}."
        else:
            field_context = f"{topic} is a concept with broad applications across multiple fields."

        # Historical timeline (template-based)
        timeline = []
        if prereqs:
            timeline.append(f"Foundation: {', '.join(p.replace('_', ' ') for p in prereqs)} established as prerequisites")
        timeline.append(f"Development: Core principles of {topic} formalized")
        if evolution_rate in ("rapid", "fast"):
            timeline.append("Recent: Rapid advances driven by new research and technology")
        else:
            timeline.append(f"Current: {topic} is a well-established area of study")

        # Current trends from evolution_rate
        current_trends = _EVOLUTION_TRENDS.get(
            evolution_rate,
            "This field evolves at a moderate pace with steady progress.",
        )

        # Adjacent topics
        adjacent = [r.replace("_", " ") for r in related[:4]] if related else []
        if category and category not in adjacent:
            adjacent.append(category)

        # Why now
        if evolution_rate in ("rapid", "fast"):
            why_now = f"{topic} is experiencing a surge of interest due to recent technological breakthroughs and growing practical applications."
        elif domain:
            domain_name = domain.get("name", "")
            why_now = f"Understanding {topic} is increasingly important in {domain_name} and related fields."
        else:
            why_now = f"{topic} continues to be relevant as foundational knowledge that underpins many modern developments."

        return json.dumps({
            "field_context": field_context,
            "historical_timeline": timeline,
            "current_trends": current_trends,
            "adjacent_topics": adjacent,
            "why_now": why_now,
        })
