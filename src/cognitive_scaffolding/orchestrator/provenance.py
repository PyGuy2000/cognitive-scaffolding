"""Provenance tracking - records which operator produced what, with timestamps."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ProvenanceEntry(BaseModel):
    """A single provenance record."""
    layer: str
    operator: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    ai_available: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: str = ""


class ProvenanceTracker(BaseModel):
    """Tracks provenance for all operators in a compilation run."""
    entries: List[ProvenanceEntry] = Field(default_factory=list)
    run_id: str = ""
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def record(
        self,
        layer: str,
        operator: str,
        duration_ms: float,
        ai_available: bool = False,
        config: Dict[str, Any] | None = None,
        success: bool = True,
        error: str = "",
    ) -> None:
        self.entries.append(ProvenanceEntry(
            layer=layer,
            operator=operator,
            duration_ms=duration_ms,
            ai_available=ai_available,
            config=config or {},
            success=success,
            error=error,
        ))

    def complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc)

    def total_duration_ms(self) -> float:
        return sum(e.duration_ms for e in self.entries)

    def failed_layers(self) -> List[str]:
        return [e.layer for e in self.entries if not e.success]

    def summary(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "total_steps": len(self.entries),
            "total_duration_ms": self.total_duration_ms(),
            "failed": self.failed_layers(),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
