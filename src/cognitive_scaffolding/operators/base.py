"""Base operator ABC - all cognitive operators extend this."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cognitive_scaffolding.core.models import AudienceProfile, LayerName, LayerOutput

logger = logging.getLogger(__name__)


class BaseOperator(ABC):
    """Abstract base for all cognitive operators.

    Each operator implements one layer of the 7-layer architecture.
    Operators receive accumulated context from prior layers but never
    communicate directly with each other.
    """

    layer_name: LayerName  # Subclasses must set this
    expected_keys: List[str] = []  # Subclasses declare expected output keys

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
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
        """Estimate confidence using schema-based scoring.

        If the operator declares expected_keys, confidence is a weighted
        combination of: keys present, non-empty values, and content richness.
        Falls back to length heuristic if no expected_keys declared.
        """
        if not content:
            return 0.0

        if not self.expected_keys:
            # Legacy fallback for operators without expected_keys
            text_content = str(content)
            if len(text_content) < 50:
                return 0.3
            if len(text_content) < 200:
                return 0.5
            if len(text_content) < 500:
                return 0.7
            return 0.8

        total_keys = len(self.expected_keys)
        keys_present = 0
        keys_non_empty = 0

        for key in self.expected_keys:
            if key in content:
                keys_present += 1
                value = content[key]
                if self._is_non_empty(value):
                    keys_non_empty += 1

        # Weighted: 40% keys present, 40% non-empty, 20% content richness
        presence_score = keys_present / total_keys
        non_empty_score = keys_non_empty / total_keys
        richness_score = self._content_richness(content)

        confidence = (0.4 * presence_score) + (0.4 * non_empty_score) + (0.2 * richness_score)
        return round(min(0.95, confidence), 3)

    @staticmethod
    def _is_non_empty(value: Any) -> bool:
        """Check if a value has meaningful content."""
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    @staticmethod
    def _content_richness(content: Dict[str, Any]) -> float:
        """Score content richness based on total text length."""
        total = sum(len(str(v)) for v in content.values())
        if total < 50:
            return 0.2
        if total < 200:
            return 0.4
        if total < 500:
            return 0.6
        if total < 1000:
            return 0.8
        return 1.0

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
