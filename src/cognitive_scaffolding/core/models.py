"""Core data models for the Cognitive Scaffolding Layer."""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class LayerName(str, Enum):
    """The 7 cognitive layers + synthesis."""
    ACTIVATION = "activation"
    METAPHOR = "metaphor"
    STRUCTURE = "structure"
    INTERROGATION = "interrogation"
    ENCODING = "encoding"
    TRANSFER = "transfer"
    REFLECTION = "reflection"
    SYNTHESIS = "synthesis"


class AudienceControlVector(BaseModel):
    """7-dimensional audience control vector."""
    language_level: float = Field(0.5, ge=0.0, le=1.0, description="Vocabulary complexity (0=simple, 1=expert)")
    abstraction: float = Field(0.5, ge=0.0, le=1.0, description="Concrete vs abstract (0=concrete, 1=abstract)")
    rigor: float = Field(0.5, ge=0.0, le=1.0, description="Informal vs formal (0=casual, 1=rigorous)")
    math_density: float = Field(0.0, ge=0.0, le=1.0, description="Math notation density (0=none, 1=heavy)")
    domain_specificity: float = Field(0.5, ge=0.0, le=1.0, description="General vs domain-expert (0=general, 1=deep)")
    cognitive_load: float = Field(0.5, ge=0.0, le=1.0, description="Cognitive demand level (0=minimal, 1=heavy)")
    transfer_distance: float = Field(0.5, ge=0.0, le=1.0, description="Near vs far transfer (0=near, 1=far/novel)")

    def as_tuple(self) -> tuple:
        return (self.language_level, self.abstraction, self.rigor, self.math_density,
                self.domain_specificity, self.cognitive_load, self.transfer_distance)


class AudienceProfile(BaseModel):
    """Extended audience profile combining base audience data with control vector."""
    audience_id: str
    name: str
    description: str = ""
    expertise_level: str = "intermediate"
    control_vector: AudienceControlVector = Field(default_factory=AudienceControlVector)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LayerOutput(BaseModel):
    """Output from a single cognitive operator."""
    layer: LayerName
    content: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationResult(BaseModel):
    """Scoring result for a CognitiveArtifact."""
    overall_score: float = Field(0.0, ge=0.0, le=1.0)
    layer_scores: Dict[str, float] = Field(default_factory=dict)
    penalty_applied: bool = False
    penalty_reason: Optional[str] = None
    missing_required: List[str] = Field(default_factory=list)
    weights_used: Dict[str, float] = Field(default_factory=dict)


class CognitiveArtifact(BaseModel):
    """Core intermediate representation - a multi-layer understanding artifact.

    NOT a LessonArtifact - this is broader than education.
    Each of the 7 layer slots is optional, populated by its corresponding operator.
    """
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    audience: AudienceProfile

    # 7 optional layer slots
    activation: Optional[LayerOutput] = None
    metaphor: Optional[LayerOutput] = None
    structure: Optional[LayerOutput] = None
    interrogation: Optional[LayerOutput] = None
    encoding: Optional[LayerOutput] = None
    transfer: Optional[LayerOutput] = None
    reflection: Optional[LayerOutput] = None
    synthesis: Optional[LayerOutput] = None

    evaluation: Optional[EvaluationResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_layer(self, name: LayerName) -> Optional[LayerOutput]:
        return getattr(self, name.value, None)

    def set_layer(self, name: LayerName, output: LayerOutput) -> None:
        setattr(self, name.value, output)
        self.updated_at = datetime.now(timezone.utc)

    def populated_layers(self) -> Dict[str, LayerOutput]:
        result = {}
        for layer in LayerName:
            output = self.get_layer(layer)
            if output is not None:
                result[layer.value] = output
        return result

    def context_dict(self) -> Dict[str, Any]:
        """Build accumulated context dict from all populated layers."""
        ctx = {}
        for name, output in self.populated_layers().items():
            ctx[name] = output.content
        return ctx


class ArtifactRevision(BaseModel):
    """A single revision in an artifact's history."""
    revision_id: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_layers: List[str] = Field(default_factory=list)
    reason: str = ""
    score_before: Optional[float] = None
    score_after: Optional[float] = None


class ArtifactRecord(BaseModel):
    """Full artifact with revision history - the top-level container."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact: CognitiveArtifact
    revision_history: List[ArtifactRevision] = Field(default_factory=list)
    current_revision: int = 0
    profile_name: str = ""

    def add_revision(self, changed_layers: List[str], reason: str = "",
                     score_before: Optional[float] = None, score_after: Optional[float] = None) -> None:
        self.current_revision += 1
        self.revision_history.append(ArtifactRevision(
            revision_id=self.current_revision,
            changed_layers=changed_layers,
            reason=reason,
            score_before=score_before,
            score_after=score_after,
        ))
