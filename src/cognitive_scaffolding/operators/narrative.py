"""Narrative operator - Story-Based Explanation layer.

Distinct from MetaphorOperator (structural analogies), this embeds the concept
in a temporal sequence with characters, conflict, and resolution. Narrative
pedagogy research shows stories activate more brain regions and improve retention.

Natural home for the 'narrative_journey' explanation style from ADR-007.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class NarrativeOperator(BaseOperator):
    """Generates story-based explanations with characters, conflict, and resolution."""

    layer_name = LayerName.NARRATIVE
    expected_keys = [
        "story", "characters", "conflict", "resolution", "concept_embedded_at",
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
        desc = concept.get("description", topic) if concept else topic

        components_text = f"\nKey components to weave in: {', '.join(c.replace('_', ' ') for c in components)}" if components else ""

        # Adjust narrative style based on audience
        if cv.language_level < 0.3:
            style_hint = "Use simple language, a child-friendly story, and relatable characters."
        elif cv.rigor > 0.7:
            style_hint = "Use a professional scenario or historical narrative with accurate details."
        else:
            style_hint = "Use an engaging, accessible story that balances accuracy with readability."

        return f"""Create a narrative-based explanation for the topic "{topic}".
{desc}

Target audience: {audience.name} (expertise: {audience.expertise_level})
Language level: {cv.language_level:.1f}, Abstraction: {cv.abstraction:.1f}
Style guidance: {style_hint}
{components_text}

Produce a JSON object with:
- "story": A 2-4 paragraph story that embeds the concept in a temporal sequence
- "characters": List of characters/entities in the story (list of strings)
- "conflict": The central tension or problem that makes the concept necessary
- "resolution": How understanding the concept resolves the conflict
- "concept_embedded_at": Where in the story the core concept is introduced (1 sentence)

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
        domain = config.get("domain")
        cv = audience.control_vector

        desc = topic
        components = []
        prereqs = []

        if concept:
            desc = concept.get("description", topic)
            components = concept.get("key_components", [])
            prereqs = concept.get("prerequisite_concepts", [])

        # Choose character archetype based on audience
        preferred_analogies = (aud.get("preferred_analogies") or []) if aud else []
        domain_name = (domain.get("name") or "").replace("_", " ") if domain else ""

        if cv.language_level < 0.3:
            # Child-friendly story
            character = "Alex, a curious young explorer"
            setting = "a magical learning laboratory"
        elif preferred_analogies:
            analogy = preferred_analogies[0].replace("_", " ")
            character = f"Jordan, an experienced professional working with {analogy}"
            setting = f"a real-world {domain_name or analogy} project"
        elif domain_name and domain_name.lower() != "general":
            character = f"Sam, a {domain_name} specialist"
            setting = f"a {domain_name} team facing a critical challenge"
        else:
            character = "Morgan, a problem-solver"
            setting = "a team project with a looming deadline"

        # Build components into story elements
        if components:
            comp_names = [c.replace("_", " ") for c in components[:3]]
            component_elements = f"Along the way, {character.split(',')[0]} discovers the importance of {', '.join(comp_names)}."
        else:
            component_elements = f"Through exploration, {character.split(',')[0]} uncovers the key principles."

        story = (
            f"In {setting}, {character} faces a problem that seems impossible to solve. "
            f"The challenge: understanding how {desc}. "
            f"{component_elements} "
            f"Step by step, the pieces come together, revealing how {topic} actually works."
        )

        # Conflict based on prerequisites or misconceptions
        if concept and concept.get("common_misconceptions"):
            misconception = concept["common_misconceptions"][0].replace("_", " ")
            conflict = f"The initial assumption that '{misconception}' leads to a dead end, forcing a deeper investigation."
        elif prereqs:
            conflict = f"Without understanding {', '.join(p.replace('_', ' ') for p in prereqs)}, the problem seems unsolvable."
        else:
            conflict = f"The complexity of {topic} threatens to overwhelm — until a breakthrough insight emerges."

        resolution = f"By mastering {topic}, {character.split(',')[0]} solves the problem and gains a framework applicable to future challenges."
        embedded = f"The concept is introduced when {character.split(',')[0]} realizes the connection between the components."

        characters_list = [character]
        if prereqs:
            characters_list.append(f"A mentor who explains {prereqs[0].replace('_', ' ')}")

        return json.dumps({
            "story": story,
            "characters": characters_list,
            "conflict": conflict,
            "resolution": resolution,
            "concept_embedded_at": embedded,
        })
