"""Activation operator - Layer 1: Attention and engagement.

Generates hooks, curiosity gaps, stakes framing, and emotional triggers.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class ActivationOperator(BaseOperator):
    """Generates attention hooks and engagement triggers."""

    layer_name = LayerName.ACTIVATION

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        return f"""Generate attention-activation content for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Language level: {cv.language_level:.1f}, Cognitive load: {cv.cognitive_load:.1f}

Produce a JSON object with these keys:
- "hook": A compelling opening hook (1-2 sentences)
- "curiosity_gap": A question or puzzle that creates curiosity
- "stakes": Why this topic matters (real-world consequences)
- "emotional_trigger": An emotional connection point
- "prior_knowledge_bridge": Connection to what the audience already knows

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        if concept:
            desc = concept.get("description", topic)
            misconceptions = concept.get("common_misconceptions", [])
            related = concept.get("related_concepts", [])
            prereqs = concept.get("prerequisite_concepts", [])
            gap = f"Most people think '{misconceptions[0].replace('_', ' ')}' — but the truth is more nuanced." if misconceptions else f"Most people misunderstand the key principle behind {topic}."
            stakes = f"Understanding {topic} connects to {', '.join(r.replace('_', ' ') for r in related)}." if related else f"Understanding {topic} is critical in today's world."
            bridge = f"You already know about {', '.join(p.replace('_', ' ') for p in prereqs)} — that's your foundation." if prereqs else f"You already understand the basics that lead to {topic}."
            return json.dumps({
                "hook": f"Have you ever wondered how {desc}?",
                "curiosity_gap": gap,
                "stakes": stakes,
                "emotional_trigger": f"Imagine being able to explain {topic} to anyone.",
                "prior_knowledge_bridge": bridge,
            })
        return json.dumps({
            "hook": f"Have you ever wondered how {topic} actually works?",
            "curiosity_gap": f"Most people misunderstand the key principle behind {topic}.",
            "stakes": f"Understanding {topic} is critical in today's world.",
            "emotional_trigger": f"Imagine being able to explain {topic} to anyone.",
            "prior_knowledge_bridge": f"You already understand the basics that lead to {topic}.",
        })
