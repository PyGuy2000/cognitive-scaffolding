"""Encoding operator - Layer 5: Memory consolidation.

Creates mnemonics, spaced repetition prompts, chunking strategies, retrieval cues.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


class EncodingOperator(BaseOperator):
    """Generates memory-consolidation aids: mnemonics, chunking, retrieval cues."""

    layer_name = LayerName.ENCODING

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        key_terms = []
        if "structure" in context:
            key_terms = list(context["structure"].get("key_terms", {}).keys())

        terms_text = f"\nKey terms to encode: {key_terms}" if key_terms else ""

        return f"""Generate memory-consolidation aids for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Cognitive load: {cv.cognitive_load:.1f}, Language level: {cv.language_level:.1f}
{terms_text}

Produce a JSON object with:
- "mnemonic": A memorable acronym, phrase, or story (string)
- "chunks": The topic broken into 3-5 digestible chunks (list of dicts with "label" and "summary")
- "retrieval_cues": 3-5 prompts that trigger recall (list)
- "spaced_repetition": 3-5 flashcard-style Q&A pairs (list of dicts with "question" and "answer")
- "visual_anchor": A vivid mental image to associate with the concept

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self, topic: str, audience: AudienceProfile, context: Dict[str, Any], config: Dict[str, Any],
    ) -> str:
        concept = config.get("concept")
        if concept:
            components = concept.get("key_components", [])
            name = concept.get("name", topic)
            properties = concept.get("properties", [])
            chunks = [{"label": c.replace("_", " ").title(), "summary": f"A key aspect of {topic}"} for c in components] if components else [
                {"label": "What", "summary": f"What {topic} is"},
                {"label": "Why", "summary": f"Why {topic} matters"},
                {"label": "How", "summary": f"How {topic} works"},
            ]
            # First-letter acronym from the concept name words
            words = name.split()
            mnemonic = "".join(w[0].upper() for w in words) if len(words) > 1 else f"Remember {name} by its key components."
            retrieval_cues = [f"When you think of {p.replace('_', ' ')}, recall {topic}." for p in properties[:3]] if properties else [f"When you hear '{topic}', think of..."]
            return json.dumps({
                "mnemonic": mnemonic,
                "chunks": chunks,
                "retrieval_cues": retrieval_cues,
                "spaced_repetition": [{"question": f"What is {topic}?", "answer": concept.get("description", "A concept involving...")}],
                "visual_anchor": f"Picture a diagram of {topic}'s main components.",
            })
        return json.dumps({
            "mnemonic": f"Remember {topic} by its key components.",
            "chunks": [
                {"label": "What", "summary": f"What {topic} is"},
                {"label": "Why", "summary": f"Why {topic} matters"},
                {"label": "How", "summary": f"How {topic} works"},
            ],
            "retrieval_cues": [f"When you hear '{topic}', think of...", f"The key insight about {topic} is..."],
            "spaced_repetition": [{"question": f"What is {topic}?", "answer": "A concept involving..."}],
            "visual_anchor": f"Picture a diagram of {topic}'s main components.",
        })
