"""Elaboration operator - Deep-Dive Sub-Topics layer.

When a topic has multiple key_components, the current pipeline gives equal
shallow treatment to each. This operator selects the 1-2 most relevant
sub-topics (based on audience interests and diagnostic gaps) and provides
much deeper treatment.
"""

import json
from typing import Any, Dict, List

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class ElaborationOperator(BaseOperator):
    """Selects and deeply elaborates on the most relevant sub-topics."""

    layer_name = LayerName.ELABORATION
    expected_keys = [
        "selected_subtopic", "deep_dive", "connections_to_main",
        "further_reading", "selection_rationale",
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
        components = concept.get("key_components", []) if concept else []

        # Select subtopic based on diagnostic gaps or audience interest
        subtopic = self._select_subtopic(components, audience, context)
        components_text = f"\nAvailable components: {', '.join(c.replace('_', ' ') for c in components)}" if components else ""
        subtopic_text = f"\nSelected subtopic for deep dive: {subtopic}" if subtopic else ""

        return f"""Provide an in-depth elaboration on a key subtopic of "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Domain specificity: {cv.domain_specificity:.1f}, Rigor: {cv.rigor:.1f}
{components_text}{subtopic_text}

Produce a JSON object with:
- "selected_subtopic": The subtopic being elaborated on
- "deep_dive": A thorough 3-5 paragraph explanation of this subtopic
- "connections_to_main": How this subtopic connects back to the main topic (1-2 sentences)
- "further_reading": 2-3 suggested directions for even deeper exploration (list)
- "selection_rationale": Why this subtopic was chosen for deep dive (1 sentence)

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        aud = config.get("audience_data")

        components = concept.get("key_components", []) if concept else []
        related = concept.get("related_concepts", []) if concept else []
        desc = concept.get("description", topic) if concept else topic

        subtopic = self._select_subtopic(components, audience, context)

        if subtopic:
            subtopic_name = subtopic.replace("_", " ")
            deep_dive = (
                f"{subtopic_name.capitalize()} is a central aspect of {topic}. "
                f"At its core, {topic} involves {desc}, and {subtopic_name} plays a crucial role in this process. "
                f"Understanding {subtopic_name} in depth reveals why {topic} works the way it does "
                f"and how it connects to the broader landscape."
            )
            connections = f"{subtopic_name.capitalize()} is essential to {topic} because it underpins the core mechanism."
            rationale = f"Selected based on its foundational importance to understanding {topic}."
        else:
            subtopic_name = f"core principles of {topic}"
            deep_dive = (
                f"The core principles of {topic} deserve deeper examination. "
                f"{desc.capitalize() if desc != topic else topic + ' involves multiple interacting concepts'}. "
                f"By examining these principles more closely, we can build a more robust understanding."
            )
            connections = f"These core principles are the foundation upon which all applications of {topic} are built."
            rationale = "Core principles selected as the most valuable focus area for deeper understanding."

        # Further reading from related concepts
        further = []
        if related:
            further = [f"Explore {r.replace('_', ' ')} to see how it connects" for r in related[:3]]
        else:
            further = [
                f"Research advanced applications of {topic}",
                f"Compare different approaches to {topic}",
            ]

        # Audience-aware suggestions
        if aud:
            primary_tools = aud.get("primary_tools") or []
            if primary_tools:
                tool = primary_tools[0].replace("_", " ")
                further.append(f"Try implementing {subtopic_name} using {tool}")

        return json.dumps({
            "selected_subtopic": subtopic_name,
            "deep_dive": deep_dive,
            "connections_to_main": connections,
            "further_reading": further,
            "selection_rationale": rationale,
        })

    @staticmethod
    def _select_subtopic(
        components: List[str],
        audience: AudienceProfile,
        context: Dict[str, Any],
    ) -> str:
        """Select the most relevant subtopic for deep dive.

        Priority:
        1. Diagnostic gaps — if learner has prerequisite gaps, elaborate on the
           component most related to those gaps
        2. First component — default to the first key component
        """
        if not components:
            return ""

        # Check diagnostic for prerequisite gaps
        diagnostic = context.get("diagnostic", {})
        if diagnostic:
            gaps = diagnostic.get("prerequisite_gaps", [])
            if gaps:
                # Try to find a component that relates to a gap
                gap_words = set()
                for g in gaps:
                    gap_words.update(g.lower().replace("_", " ").split())
                for comp in components:
                    comp_words = set(comp.lower().replace("_", " ").split())
                    if comp_words & gap_words:
                        return comp

        # Default: first component (usually the most foundational)
        return components[0]
