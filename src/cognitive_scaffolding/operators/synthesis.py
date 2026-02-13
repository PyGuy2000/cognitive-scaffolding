"""Synthesis operator - Layer 8: Unified response from all layers.

Reads all 7 layer outputs from context and produces one coherent,
integrated response instead of 7 separate outputs.
"""

import json
from typing import Any, Dict

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
from cognitive_scaffolding.operators.base import BaseOperator


# All content layers (everything except synthesis itself)
CONTENT_LAYERS = [
    LayerName.DIAGNOSTIC,
    LayerName.ACTIVATION,
    LayerName.CONTEXTUALIZATION,
    LayerName.METAPHOR,
    LayerName.NARRATIVE,
    LayerName.STRUCTURE,
    LayerName.INTERROGATION,
    LayerName.ENCODING,
    LayerName.TRANSFER,
    LayerName.CHALLENGE,
    LayerName.REFLECTION,
    LayerName.ELABORATION,
]


class SynthesisOperator(BaseOperator):
    """Synthesizes all 7 layer outputs into one unified response."""

    layer_name = LayerName.SYNTHESIS

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector

        # Build a summary of available layer outputs
        layer_summaries = []
        for layer in CONTENT_LAYERS:
            data = context.get(layer.value)
            if data:
                layer_summaries.append(f"### {layer.value.title()} Layer\n{json.dumps(data, indent=2)}")

        layers_text = "\n\n".join(layer_summaries) if layer_summaries else "(No layer outputs available)"

        return f"""You are synthesizing a cognitive scaffolding artifact about "{topic}" for a {audience.name} audience (expertise: {audience.expertise_level}).

Language level: {cv.language_level:.1f}, Abstraction: {cv.abstraction:.1f}, Cognitive load: {cv.cognitive_load:.1f}

Below are the outputs from individual cognitive layers. Your job is to weave them into ONE coherent, flowing response — not a list of sections. The layers are ingredients, not chapters.

{layers_text}

Produce a JSON object with these keys:
- "synthesized_response": A 2-4 paragraph unified explanation that naturally integrates the activation hook, metaphor, core structure, key questions, memory aids, applications, and reflection. Write it as a single flowing piece, not labeled sections.
- "key_takeaway": A single sentence capturing the most important insight.
- "layers_integrated": A list of which layer names contributed to the synthesis (e.g. ["activation", "metaphor", "structure"]).

Return ONLY valid JSON, no markdown."""

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        """Template-based synthesis when AI is unavailable.

        Pulls the strongest element from each populated layer
        and assembles them into a structured response.
        """
        parts = []
        layers_integrated = []

        # Diagnostic context (not displayed directly, but noted)
        diagnostic = context.get("diagnostic", {})
        if diagnostic:
            layers_integrated.append("diagnostic")
            depth = diagnostic.get("recommended_depth", "")
            if depth:
                parts.append(f"[Depth: {depth}]")

        # Open with activation hook
        activation = context.get("activation", {})
        if activation:
            layers_integrated.append("activation")
            hook = activation.get("hook", "")
            gap = activation.get("curiosity_gap", "")
            if hook:
                parts.append(hook)
            if gap:
                parts.append(gap)

        # Contextualization: big picture
        contextualization = context.get("contextualization", {})
        if contextualization:
            layers_integrated.append("contextualization")
            field_ctx = contextualization.get("field_context", "")
            if field_ctx:
                parts.append(field_ctx)
            why_now = contextualization.get("why_now", "")
            if why_now:
                parts.append(why_now)

        # Bridge with metaphor
        metaphor = context.get("metaphor", {})
        if metaphor:
            layers_integrated.append("metaphor")
            met_text = metaphor.get("metaphor", "")
            if met_text:
                parts.append(met_text)

        # Narrative story
        narrative = context.get("narrative", {})
        if narrative:
            layers_integrated.append("narrative")
            story = narrative.get("story", "")
            if story:
                parts.append(story)

        # Core explanation from structure
        structure = context.get("structure", {})
        if structure:
            layers_integrated.append("structure")
            defn = structure.get("definition", "")
            if defn:
                parts.append(defn)
            key_terms = structure.get("key_terms", {})
            if key_terms:
                terms_text = "; ".join(f"{k}: {v}" for k, v in key_terms.items())
                parts.append(f"Key concepts: {terms_text}.")

        # Weave in interrogation's synthesis prompt
        interrogation = context.get("interrogation", {})
        if interrogation:
            layers_integrated.append("interrogation")
            synth = interrogation.get("synthesis_prompt", "")
            if synth:
                parts.append(synth)

        # Add encoding mnemonic
        encoding = context.get("encoding", {})
        if encoding:
            layers_integrated.append("encoding")
            mnemonic = encoding.get("mnemonic", "")
            if mnemonic:
                parts.append(f"To remember this: {mnemonic}")

        # Close with transfer application
        transfer = context.get("transfer", {})
        if transfer:
            layers_integrated.append("transfer")
            apps = transfer.get("real_world_applications", [])
            if apps:
                parts.append(f"In practice, this applies to: {'; '.join(apps[:3])}.")
            cross = transfer.get("cross_domain_transfer", "")
            if cross:
                parts.append(cross)

        # Challenge prompt
        challenge = context.get("challenge", {})
        if challenge:
            layers_integrated.append("challenge")
            prompt = challenge.get("challenge_prompt", "")
            if prompt:
                parts.append(f"Challenge: {prompt}")

        # Reflection next steps
        reflection = context.get("reflection", {})
        if reflection:
            layers_integrated.append("reflection")
            next_steps = reflection.get("next_steps", [])
            if next_steps:
                parts.append(f"Next, explore: {'; '.join(next_steps[:3])}.")

        # Elaboration deep dive
        elaboration = context.get("elaboration", {})
        if elaboration:
            layers_integrated.append("elaboration")
            deep_dive = elaboration.get("deep_dive", "")
            if deep_dive:
                parts.append(deep_dive)

        if not parts:
            synthesized = (
                f"This is a synthesized overview of {topic}. "
                f"Enable individual layers to build a richer explanation."
            )
        else:
            synthesized = "\n\n".join(parts)

        # Key takeaway: use structure definition or generic
        key_takeaway = structure.get("definition", "") if structure else ""
        if not key_takeaway:
            key_takeaway = f"{topic} is a concept worth understanding deeply."

        return json.dumps({
            "synthesized_response": synthesized,
            "key_takeaway": key_takeaway,
            "layers_integrated": layers_integrated,
        })

    def estimate_confidence(self, content: Dict[str, Any]) -> float:
        """Confidence based on how many of the 7 content layers were integrated."""
        layers = content.get("layers_integrated", [])
        if not layers:
            return 0.2
        # Scale: 1 layer = 0.3, 4 layers = 0.6, 7 layers = 0.9
        return min(0.9, 0.2 + 0.1 * len(layers))
