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
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_metaphor(c: Dict) -> str:
        parts = []
        if metaphor := c.get("metaphor"):
            parts.append(metaphor)
        if mapping := c.get("mapping"):
            parts.append("\nKey mappings:")
            for k, v in mapping.items():
                parts.append(f"  - {k} → {v}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_structure(c: Dict) -> str:
        parts = []
        if defn := c.get("definition"):
            parts.append(f"**Definition:** {defn}")
        if terms := c.get("key_terms"):
            parts.append("\n**Key Terms:**")
            for k, v in terms.items():
                parts.append(f"  - **{k}**: {v}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_interrogation(c: Dict) -> str:
        parts = []
        if qs := c.get("socratic_questions"):
            parts.append("**Think about this:**")
            for q in qs:
                parts.append(f"  - {q}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_encoding(c: Dict) -> str:
        parts = []
        if mnemonic := c.get("mnemonic"):
            parts.append(f"**Remember:** {mnemonic}")
        if cues := c.get("retrieval_cues"):
            parts.append("\n**Quick recall:**")
            for cue in cues:
                parts.append(f"  - {cue}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_transfer(c: Dict) -> str:
        parts = []
        if ex := c.get("worked_example"):
            if isinstance(ex, dict):
                parts.append(f"**Example:** {ex.get('problem', '')}")
                for step in ex.get("steps", []):
                    parts.append(f"  1. {step}")
        if apps := c.get("real_world_applications"):
            parts.append("\n**Real-world uses:**")
            for app in apps:
                parts.append(f"  - {app}")
        return "\n".join(parts) if parts else str(c)

    @staticmethod
    def _format_reflection(c: Dict) -> str:
        parts = []
        if check := c.get("confidence_check"):
            parts.append(check)
        if steps := c.get("next_steps"):
            parts.append("\n**Next steps:**")
            for s in steps:
                parts.append(f"  - {s}")
        return "\n".join(parts) if parts else str(c)
