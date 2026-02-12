"""Base operator ABC - all cognitive operators extend this."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from cognitive_scaffolding.core.models import AudienceProfile, LayerName, LayerOutput

logger = logging.getLogger(__name__)


class BaseOperator(ABC):
    """Abstract base for all cognitive operators.

    Each operator implements one layer of the 7-layer architecture.
    Operators receive accumulated context from prior layers but never
    communicate directly with each other.
    """

    layer_name: LayerName  # Subclasses must set this

    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    def execute(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> LayerOutput:
        """Execute this operator to produce a LayerOutput.

        Args:
            topic: The concept/topic being explained
            audience: Target audience profile with control vector
            context: Accumulated context dict from all prior layers
            config: Optional operator-specific configuration
        """
        config = config or {}
        prompt = self.build_prompt(topic, audience, context, config)

        if self.ai_client and self.ai_client.is_available():
            raw = self.ai_client.generate(prompt)
        else:
            raw = self.generate_fallback(topic, audience, context, config)

        content = self.parse_output(raw)
        confidence = self.estimate_confidence(content)

        return LayerOutput(
            layer=self.layer_name,
            content=content,
            confidence=confidence,
            provenance={
                "operator": self.__class__.__name__,
                "ai_available": bool(self.ai_client and self.ai_client.is_available()),
                "timestamp": datetime.utcnow().isoformat(),
                "config": config,
            },
        )

    @abstractmethod
    def build_prompt(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        """Build the LLM prompt for this operator."""
        ...

    def parse_output(self, raw: str) -> Dict[str, Any]:
        """Parse raw LLM output into structured content dict.

        Default: try JSON parse, fall back to wrapping as text.
        Subclasses can override for custom parsing.
        """
        text = raw.strip()
        # Strip markdown code fences that LLMs often wrap JSON in
        match = re.match(r"^```\w*\n(.*?)```\s*$", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return {"text": raw}

    def estimate_confidence(self, content: Dict[str, Any]) -> float:
        """Estimate confidence in the output quality.

        Default heuristic: based on content richness.
        Subclasses can override for domain-specific estimation.
        """
        if not content:
            return 0.0
        text_content = str(content)
        if len(text_content) < 50:
            return 0.3
        if len(text_content) < 200:
            return 0.5
        if len(text_content) < 500:
            return 0.7
        return 0.8

    def generate_fallback(
        self,
        topic: str,
        audience: AudienceProfile,
        context: Dict[str, Any],
        config: Dict[str, Any],
    ) -> str:
        """Generate fallback output when AI is unavailable.

        Default returns minimal placeholder. Subclasses should override.
        """
        return json.dumps({
            "note": f"Fallback {self.layer_name.value} output for '{topic}'",
            "audience": audience.audience_id,
        })
