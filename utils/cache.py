"""Simple TTL cache for generated content - adapted from metaphor-mcp-server."""

import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


class ContentCache:
    """In-memory TTL cache keyed by arbitrary string components."""

    def __init__(self, ttl_minutes: int = 60):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl_minutes = ttl_minutes

    def _make_key(self, *parts: str) -> str:
        content = "-".join(str(p) for p in parts)
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, *key_parts: str) -> Optional[Any]:
        key = self._make_key(*key_parts)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(minutes=self.ttl_minutes):
                return value
            del self.cache[key]
        return None

    def set(self, *key_parts_and_value) -> None:
        """Last argument is the value, all preceding are key parts."""
        *key_parts, value = key_parts_and_value
        key = self._make_key(*key_parts)
        self.cache[key] = (value, datetime.now())

    def clear(self) -> None:
        self.cache.clear()

    def size(self) -> int:
        return len(self.cache)
