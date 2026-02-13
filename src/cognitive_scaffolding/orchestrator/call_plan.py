"""Call plan - ordered sequence of operators to execute."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from cognitive_scaffolding.core.models import LayerName


class OperatorStep(BaseModel):
    """A single step in a call plan."""
    layer: LayerName
    operator_class: str  # Fully qualified class name
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    required: bool = False


class CallPlan(BaseModel):
    """Ordered list of operator steps to execute."""
    steps: List[OperatorStep] = Field(default_factory=list)
    profile_name: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def enabled_steps(self) -> List[OperatorStep]:
        """Return only enabled steps."""
        return [s for s in self.steps if s.enabled]

    def required_steps(self) -> List[OperatorStep]:
        """Return steps that are both enabled and required."""
        return [s for s in self.steps if s.enabled and s.required]

    @classmethod
    def from_layer_configs(cls, layer_configs: dict, profile_name: str = "") -> CallPlan:
        """Build a call plan from layer configurations.

        Uses the standard layer-to-operator mapping.
        """
        layer_operator_map = {
            LayerName.DIAGNOSTIC: "cognitive_scaffolding.operators.diagnostic.DiagnosticOperator",
            LayerName.ACTIVATION: "cognitive_scaffolding.operators.activation.ActivationOperator",
            LayerName.CONTEXTUALIZATION: "cognitive_scaffolding.operators.contextualization.ContextualizationOperator",
            LayerName.METAPHOR: "cognitive_scaffolding.operators.metaphor.MetaphorOperator",
            LayerName.NARRATIVE: "cognitive_scaffolding.operators.narrative.NarrativeOperator",
            LayerName.STRUCTURE: "cognitive_scaffolding.operators.structure.StructureOperator",
            LayerName.INTERROGATION: "cognitive_scaffolding.operators.interrogation.InterrogationOperator",
            LayerName.ENCODING: "cognitive_scaffolding.operators.encoding.EncodingOperator",
            LayerName.TRANSFER: "cognitive_scaffolding.operators.transfer.TransferOperator",
            LayerName.CHALLENGE: "cognitive_scaffolding.operators.challenge.ChallengeOperator",
            LayerName.REFLECTION: "cognitive_scaffolding.operators.reflection.ReflectionOperator",
            LayerName.ELABORATION: "cognitive_scaffolding.operators.elaboration.ElaborationOperator",
            LayerName.SYNTHESIS: "cognitive_scaffolding.operators.synthesis.SynthesisOperator",
        }

        steps = []
        for layer in LayerName:
            config = layer_configs.get(layer.value)
            if config is None:
                continue
            steps.append(OperatorStep(
                layer=layer,
                operator_class=layer_operator_map[layer],
                enabled=config.enabled,
                required=config.required,
            ))

        return cls(steps=steps, profile_name=profile_name)
