"""Chatbot adapter - formats CognitiveArtifact as chat messages.

Designed for progressive disclosure in conversational UIs.
"""

from typing import Any, Dict, List

from cognitive_scaffolding.adapters.base import BaseAdapter
from cognitive_scaffolding.core.models import ArtifactRecord, LayerName


class ChatbotAdapter(BaseAdapter):
    """Formats artifacts as a sequence of chat messages with progressive disclosure."""

    def format(self, record: ArtifactRecord) -> List[Dict[str, Any]]:
        """Convert artifact to a list of chat messages.

        Returns list of dicts with 'role', 'content', 'layer', 'metadata'.
        Messages are ordered for progressive disclosure:
        activation → metaphor → structure → interrogation → encoding → transfer → reflection
        """
        artifact = record.artifact
        messages: List[Dict[str, Any]] = []

        # Layer ordering for progressive disclosure
        layer_order = [
            LayerName.ACTIVATION,
            LayerName.METAPHOR,
            LayerName.STRUCTURE,
            LayerName.INTERROGATION,
            LayerName.ENCODING,
            LayerName.TRANSFER,
            LayerName.REFLECTION,
        ]

        for layer in layer_order:
            output = artifact.get_layer(layer)
            if output is None:
                continue

            content = self._format_layer_content(layer, output.content)
            messages.append({
                "role": "assistant",
                "content": content,
                "layer": layer.value,
                "confidence": output.confidence,
                "metadata": {
                    "topic": artifact.topic,
                    "audience": artifact.audience.audience_id,
                },
            })

        # Append evaluation summary if available
        if artifact.evaluation:
            messages.append({
                "role": "system",
                "content": f"Understanding score: {artifact.evaluation.overall_score:.0%}",
                "layer": "evaluation",
                "confidence": 1.0,
                "metadata": {
                    "layer_scores": artifact.evaluation.layer_scores,
                    "penalty": artifact.evaluation.penalty_applied,
                },
            })

        return messages

    def _format_layer_content(self, layer: LayerName, content: Dict[str, Any]) -> str:
        """Format a layer's content as readable chat text."""
        formatters = {
            LayerName.ACTIVATION: self._format_activation,
            LayerName.METAPHOR: self._format_metaphor,
            LayerName.STRUCTURE: self._format_structure,
            LayerName.INTERROGATION: self._format_interrogation,
            LayerName.ENCODING: self._format_encoding,
            LayerName.TRANSFER: self._format_transfer,
            LayerName.REFLECTION: self._format_reflection,
        }
        formatter = formatters.get(layer)
        if formatter:
            return formatter(content)
        return str(content)

    @staticmethod
    def _format_activation(c: Dict) -> str:
        parts = []
        if hook := c.get("hook"):
            parts.append(hook)
        if gap := c.get("curiosity_gap"):
            parts.append(f"\n{gap}")
        if stakes := c.get("stakes"):
            parts.append(f"\n{stakes}")
        if trigger := c.get("emotional_trigger"):
            parts.append(f"\n**Emotional trigger:** {trigger}")
        if bridge := c.get("prior_knowledge_bridge"):
            parts.append(f"\n**Build on what you know:** {bridge}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_metaphor(c: Dict) -> str:
        parts = []
        if metaphor := c.get("metaphor"):
            parts.append(metaphor)
        if source := c.get("source_domain"):
            parts.append(f"\n**Source domain:** {source}")
        if mapping := c.get("mapping"):
            parts.append("\n**Key mappings:**")
            for k, v in mapping.items():
                parts.append(f"  - {k} → {v}")
        if limitations := c.get("limitations"):
            parts.append("\n**Where the analogy breaks down:**")
            if isinstance(limitations, list):
                for lim in limitations:
                    parts.append(f"  - {lim}")
            else:
                parts.append(f"  {limitations}")
        if extension := c.get("extension"):
            parts.append(f"\n**Taking it further:** {extension}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_structure(c: Dict) -> str:
        parts = []
        if defn := c.get("definition"):
            parts.append(f"**Definition:** {defn}")
        if taxonomy := c.get("taxonomy"):
            parts.append(f"\n**Taxonomy:** {taxonomy}")
        if terms := c.get("key_terms"):
            parts.append("\n**Key Terms:**")
            for k, v in terms.items():
                parts.append(f"  - **{k}**: {v}")
        if rels := c.get("relationships"):
            parts.append("\n**Relationships:**")
            if isinstance(rels, list):
                for r in rels:
                    parts.append(f"  - {r}")
            elif isinstance(rels, dict):
                for k, v in rels.items():
                    parts.append(f"  - **{k}**: {v}")
        if diagram := c.get("diagram_description"):
            parts.append(f"\n**Diagram:** {diagram}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_interrogation(c: Dict) -> str:
        parts = []
        if qs := c.get("socratic_questions"):
            parts.append("**Think about this:**")
            for q in qs:
                parts.append(f"  - {q}")
        if cex := c.get("counterexamples"):
            parts.append("\n**Counterexamples:**")
            for ex in cex:
                parts.append(f"  - {ex}")
        if edge := c.get("edge_cases"):
            parts.append("\n**Edge cases:**")
            for e in edge:
                parts.append(f"  - {e}")
        if probes := c.get("misconception_probes"):
            parts.append("\n**Common misconceptions to watch for:**")
            for p in probes:
                parts.append(f"  - {p}")
        if synth := c.get("synthesis_prompt"):
            parts.append(f"\n**Synthesis:** {synth}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_encoding(c: Dict) -> str:
        parts = []
        if mnemonic := c.get("mnemonic"):
            parts.append(f"**Remember:** {mnemonic}")
        if chunks := c.get("chunks"):
            parts.append("\n**Key chunks:**")
            for chunk in chunks:
                if isinstance(chunk, dict):
                    parts.append(f"  - **{chunk.get('label', '')}**: {chunk.get('summary', '')}")
                else:
                    parts.append(f"  - {chunk}")
        if cues := c.get("retrieval_cues"):
            parts.append("\n**Quick recall:**")
            for cue in cues:
                parts.append(f"  - {cue}")
        if sr := c.get("spaced_repetition"):
            parts.append("\n**Spaced repetition:**")
            for item in sr:
                if isinstance(item, dict):
                    parts.append(f"  - Q: {item.get('question', '')}  A: {item.get('answer', '')}")
                else:
                    parts.append(f"  - {item}")
        if anchor := c.get("visual_anchor"):
            parts.append(f"\n**Visual anchor:** {anchor}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_transfer(c: Dict) -> str:
        parts = []
        if ex := c.get("worked_example"):
            if isinstance(ex, dict):
                parts.append(f"**Example:** {ex.get('problem', '')}")
                for step in ex.get("steps", []):
                    parts.append(f"  1. {step}")
        if problems := c.get("practice_problems"):
            parts.append("\n**Practice problems:**")
            for prob in problems:
                parts.append(f"  - {prob}")
        if apps := c.get("real_world_applications"):
            parts.append("\n**Real-world uses:**")
            for app in apps:
                parts.append(f"  - {app}")
        if sim := c.get("simulation_prompt"):
            parts.append(f"\n**Try this simulation:** {sim}")
        if cross := c.get("cross_domain_transfer"):
            parts.append(f"\n**Cross-domain connection:** {cross}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_reflection(c: Dict) -> str:
        parts = []
        if check := c.get("confidence_check"):
            parts.append(check)
        if cal := c.get("calibration_questions"):
            parts.append("\n**Calibration questions:**")
            for q in cal:
                parts.append(f"  - {q}")
        if alerts := c.get("misconception_alerts"):
            parts.append("\n**Watch out for:**")
            for a in alerts:
                parts.append(f"  - {a}")
        if prompts := c.get("connection_prompts"):
            parts.append("\n**Connections to explore:**")
            for p in prompts:
                parts.append(f"  - {p}")
        if steps := c.get("next_steps"):
            parts.append("\n**Next steps:**")
            for s in steps:
                parts.append(f"  - {s}")
        return "\n".join(parts) if parts else str(c)
