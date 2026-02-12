"""Metaphor operator - Layer 2: Anchoring and mapping.

Wraps the existing MetaphorEngine from metaphor-mcp-server as a fat operator.
Falls back to LLM-based metaphor generation if engine unavailable.
"""

import json
import logging
from typing import Any, Dict, Optional

from cognitive_scaffolding.core.models import AudienceProfile, LayerName
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
        from cognitive_scaffolding.core.models import LayerOutput
        from datetime import datetime

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
                "timestamp": datetime.utcnow().isoformat(),
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
        return json.dumps({
            "metaphor": f"Think of {topic} like a well-organized kitchen - each component has a specific role and they work together to produce a final result.",
            "source_domain": "restaurant_kitchen",
            "mapping": {"input": "ingredients", "process": "cooking", "output": "dish"},
            "limitations": ["Real systems are more complex", "Scale differs significantly"],
            "extension": f"To understand {topic} more deeply, consider how the kitchen handles peak hours.",
        })
