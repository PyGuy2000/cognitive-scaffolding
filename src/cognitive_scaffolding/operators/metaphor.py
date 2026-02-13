"""Metaphor operator - Layer 2: Anchoring and mapping.

Wraps the existing MetaphorEngine from metaphor-mcp-server as a fat operator.
Falls back to LLM-based metaphor generation if engine unavailable.
"""

import json
import logging
from typing import Any, Dict, Optional

from cognitive_scaffolding.core.models import AudienceProfile, LayerName, LayerOutput
from cognitive_scaffolding.operators.base import BaseOperator

logger = logging.getLogger(__name__)

# Try to import the existing MetaphorEngine
_metaphor_engine = None
try:
    import sys
    sys.path.insert(0, "/home/robkacz/python/projects/metaphor-mcp-server")
    from src.core.engines.metaphor_engine import MetaphorEngine
    _metaphor_engine = MetaphorEngine()
    logger.info("MetaphorEngine loaded from metaphor-mcp-server")
except ImportError as e:
    logger.warning(f"MetaphorEngine not available, using LLM fallback: {e}")
except Exception as e:
    logger.warning(f"Failed to initialize MetaphorEngine: {e}")


class MetaphorOperator(BaseOperator):
    """Wraps existing MetaphorEngine or generates metaphors via LLM."""

    layer_name = LayerName.METAPHOR

    def __init__(self, ai_client=None, engine=None):
        super().__init__(ai_client)
        self.engine = engine or _metaphor_engine

    def execute(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> "LayerOutput":
        config = config or {}

        # Try the existing engine first
        if self.engine is not None:
            try:
                return self._execute_via_engine(topic, audience, context, config)
            except Exception as e:
                logger.warning(f"MetaphorEngine failed, falling back to LLM: {e}")

        # Fall back to base LLM execution
        return super().execute(topic, audience, context, config)

    def _execute_via_engine(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> "LayerOutput":
        """Execute using the existing MetaphorEngine."""
        from datetime import datetime, timezone

        concept_id = config.get("concept_id", topic.lower().replace(" ", "_"))
        domain_id = config.get("domain_id")
        audience_id = audience.audience_id

        if domain_id:
            result = self.engine.generate_explanation(concept_id, audience_id, domain_id)
        else:
            result = self.engine.generate_explanation(concept_id, audience_id, "restaurant_kitchen")

        content = {
            "metaphor": result if isinstance(result, str) else str(result),
            "source_domain": domain_id or "auto_selected",
            "concept_id": concept_id,
            "engine": "MetaphorEngine",
        }

        return LayerOutput(
            layer=self.layer_name,
            content=content,
            confidence=0.8,
            provenance={
                "operator": "MetaphorOperator",
                "engine": "MetaphorEngine",
                "ai_available": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": config,
            },
        )

    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        cv = audience.control_vector
        activation_context = ""
        if "activation" in context:
            hook = context["activation"].get("hook", "")
            if hook:
                activation_context = f"\nBuild on this hook: {hook}"

        return f"""Generate a rich metaphor/analogy for the topic "{topic}".

Target audience: {audience.name} (expertise: {audience.expertise_level})
Abstraction level: {cv.abstraction:.1f}, Language level: {cv.language_level:.1f}
{activation_context}

Produce a JSON object with:
- "metaphor": The core metaphor explanation (2-4 paragraphs)
- "source_domain": The domain the metaphor comes from (e.g., "restaurant kitchen")
- "mapping": Key concept-to-metaphor mappings (dict)
- "limitations": Where the metaphor breaks down (list)
- "extension": How to extend the metaphor for deeper understanding

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

        # Audience-aware: preferred metaphors/domains
        preferred_metaphors = (aud.get("preferred_metaphors") or []) if aud else []
        preferred_domains = (aud.get("preferred_domains") or []) if aud else []

        # Domain-aware: vocabulary, metaphor_types, name
        domain_name = (domain.get("name") or "").lower() if domain else ""
        domain_vocab = (domain.get("vocabulary") or []) if domain else []
        domain_metaphor_types = (domain.get("metaphor_types") or []) if domain else []

        if concept:
            components = concept.get("key_components", [])
            desc = concept.get("description", topic)
            mapping = {c.replace("_", " "): f"part of the system that handles {c.replace('_', ' ')}" for c in components} if components else {"input": "ingredients", "process": "cooking", "output": "dish"}

            # Source domain: domain > audience preference > default
            if domain_name and domain_name != "general":
                source = domain_name
                vocab_phrase = domain_vocab[0] if domain_vocab else f"like {domain_name}"
                metaphor = f"Think of {topic} as a system where {desc}. {vocab_phrase.capitalize()}, each part plays a role."
            elif preferred_metaphors:
                source = preferred_metaphors[0].replace("_", " ")
                metaphor = f"Think of {topic} through the lens of {source}: {desc}. Each part plays a role."
            elif preferred_domains:
                source = preferred_domains[0].replace("_", " ")
                metaphor = f"Think of {topic} as a system where {desc}. Each part plays a role, much like {source}."
            else:
                source = "organized_team"
                metaphor = f"Think of {topic} as a system where {desc}. Each part plays a role, much like a well-organized team."

            # Enrich mapping with domain metaphor types
            if domain_metaphor_types:
                mapping["metaphor_style"] = domain_metaphor_types[0].replace("_", " ")

            return json.dumps({
                "metaphor": metaphor,
                "source_domain": source,
                "mapping": mapping,
                "limitations": ["Real systems are more complex", "Scale differs significantly"],
                "extension": f"To understand {topic} more deeply, consider how these components interact under pressure.",
            })

        # Generic branch with audience/domain awareness
        if domain_name and domain_name != "general":
            vocab_phrase = domain_vocab[0] if domain_vocab else f"like {domain_name}"
            source = domain_name
            metaphor = f"Think of {topic} {vocab_phrase} — each component has a specific role and they work together to produce a final result."
        elif preferred_metaphors:
            source = preferred_metaphors[0].replace("_", " ")
            metaphor = f"Think of {topic} through the lens of {source} — each component has a specific role."
        else:
            source = "restaurant_kitchen"
            metaphor = f"Think of {topic} like a well-organized kitchen - each component has a specific role and they work together to produce a final result."

        mapping = {"input": "ingredients", "process": "cooking", "output": "dish"}
        if domain_metaphor_types:
            mapping["metaphor_style"] = domain_metaphor_types[0].replace("_", " ")

        return json.dumps({
            "metaphor": metaphor,
            "source_domain": source,
            "mapping": mapping,
            "limitations": ["Real systems are more complex", "Scale differs significantly"],
            "extension": f"To understand {topic} more deeply, consider how the system handles peak demand.",
        })
