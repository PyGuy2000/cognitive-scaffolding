"""Unified AI client for Anthropic and OpenAI - adapted from metaphor-mcp-server."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIClient:
    """Unified AI client supporting Anthropic and OpenAI providers."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = (provider or os.getenv("AI_PROVIDER", "anthropic")).lower()
        self.model = model
        self.client = None
        self._initialized = False
        try:
            self._initialize_client()
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")

    def _initialize_client(self) -> None:
        if self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic not installed")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = self.model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        elif self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai not installed")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = openai.OpenAI(api_key=api_key)
            self.model = self.model or os.getenv("OPENAI_MODEL", "gpt-4")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        self._initialized = True

    def is_available(self) -> bool:
        return self._initialized and self.client is not None

    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Generate a response from the configured AI provider."""
        if not self.is_available():
            return self._fallback(f"AI client not initialized (provider={self.provider})")
        if not prompt or not prompt.strip():
            return ""
        try:
            if self.provider == "anthropic":
                return self._call_anthropic(prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return self._call_openai(prompt, max_tokens, temperature)
            return self._fallback(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self._fallback(str(e))

    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if message.content:
            return message.content[0].text
        return ""

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.choices:
            return response.choices[0].message.content or ""
        return ""

    @staticmethod
    def _fallback(error_msg: str) -> str:
        logger.warning(f"AI fallback: {error_msg}")
        return f"[AI unavailable: {error_msg}]"

    def get_status(self) -> dict:
        return {
            "initialized": self._initialized,
            "provider": self.provider,
            "model": self.model,
            "anthropic_available": ANTHROPIC_AVAILABLE,
            "openai_available": OPENAI_AVAILABLE,
        }
