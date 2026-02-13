"""Cognitive Conductor - the main compilation loop.

Takes a topic + audience + profile and orchestrates all operators
to produce a scored CognitiveArtifact.
"""

from __future__ import annotations

import importlib
import logging
import time
import uuid
from typing import Any, Dict, Optional

from cognitive_scaffolding.core.data_loader import DataLoader
from cognitive_scaffolding.core.models import (
    ArtifactRecord,
    AudienceControlVector,
    AudienceProfile,
    CognitiveArtifact,
)
from cognitive_scaffolding.core.scoring import score_artifact
from cognitive_scaffolding.orchestrator.call_plan import CallPlan
from cognitive_scaffolding.orchestrator.provenance import ProvenanceTracker
from cognitive_scaffolding.orchestrator.toggle_manager import ToggleManager

logger = logging.getLogger(__name__)


# Default audience control vectors for common audience types
DEFAULT_VECTORS = {
    "child": AudienceControlVector(
        language_level=0.1, abstraction=0.1, rigor=0.1, math_density=0.0,
        domain_specificity=0.0, cognitive_load=0.2, transfer_distance=0.2,
    ),
    "general": AudienceControlVector(),  # all defaults (0.5)
    "data_scientist": AudienceControlVector(
        language_level=0.8, abstraction=0.7, rigor=0.8, math_density=0.7,
        domain_specificity=0.8, cognitive_load=0.8, transfer_distance=0.6,
    ),
    "phd": AudienceControlVector(
        language_level=0.9, abstraction=0.9, rigor=0.95, math_density=0.9,
        domain_specificity=0.9, cognitive_load=0.9, transfer_distance=0.8,
    ),
}


class CognitiveConductor:
    """Main orchestrator that compiles CognitiveArtifacts.

    Compilation loop:
    1. Load profile → build CallPlan
    2. Apply runtime overrides
    3. Execute operators in sequence, accumulating context
    4. Score the result
    5. Return ArtifactRecord with provenance
    """

    def __init__(
        self,
        ai_client=None,
        toggle_manager: Optional[ToggleManager] = None,
        profiles_dir: str = "profiles",
        data_dir: str = "data",
    ):
        self.ai_client = ai_client
        self.toggle_manager = toggle_manager or ToggleManager(profiles_dir)
        self.data_dir = data_dir
        self._operator_cache: Dict[str, Any] = {}

    def compile(
        self,
        topic: str,
        audience_id: str,
        profile_name: str = "chatbot_tutor",
        overrides: Optional[Dict[str, Dict[str, Any]]] = None,
        audience_vector: Optional[AudienceControlVector] = None,
        domain_id: Optional[str] = None,
    ) -> ArtifactRecord:
        """Compile a CognitiveArtifact for the given topic and audience.

        Args:
            topic: The concept/topic to explain
            audience_id: Audience identifier (e.g., "child", "data_scientist")
            profile_name: Integration profile to use
            overrides: Runtime toggle overrides per layer
            audience_vector: Explicit audience control vector (overrides default)
            domain_id: Optional domain identifier for domain-aware metaphors
        """
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"[{run_id}] Compiling: topic='{topic}', audience='{audience_id}', profile='{profile_name}'")

        # Build audience profile
        vector = audience_vector or DEFAULT_VECTORS.get(audience_id, AudienceControlVector())
        audience = AudienceProfile(
            audience_id=audience_id,
            name=audience_id.replace("_", " ").title(),
            expertise_level=self._infer_expertise(audience_id),
            control_vector=vector,
        )

        # Load profile and apply overrides
        layer_configs = self.toggle_manager.load_profile(profile_name)
        if overrides:
            layer_configs = self.toggle_manager.apply_overrides(layer_configs, overrides)

        # Build call plan
        call_plan = CallPlan.from_layer_configs(layer_configs, profile_name)

        # Create artifact
        artifact = CognitiveArtifact(topic=topic, audience=audience)

        # Load concept data for topic-aware fallbacks
        if not hasattr(self, "_data_loader"):
            self._data_loader = DataLoader(self.data_dir)
        concept_id = topic.lower().replace(" ", "_")
        concept = self._data_loader.get_concept(concept_id)
        concept_dict = concept.model_dump() if concept else None

        # Load audience YAML data for audience-aware fallbacks
        audience_yaml = self._data_loader.get_audience(audience_id)
        audience_dict = audience_yaml.model_dump() if audience_yaml else None

        # Load domain data for domain-aware compilation
        domain = None
        if domain_id:
            domain = self._data_loader.get_domain(domain_id)
        elif audience_dict and audience_dict.get("preferred_domains"):
            for d_id in audience_dict["preferred_domains"]:
                domain = self._data_loader.get_domain(d_id)
                if domain:
                    break
        if not domain:
            domain = self._data_loader.get_domain("general")
        domain_dict = domain.model_dump() if domain else None

        # Execute operators
        provenance = ProvenanceTracker(run_id=run_id)
        context: Dict[str, Any] = {}

        for step in call_plan.enabled_steps():
            start = time.time()
            try:
                operator = self._get_operator(step.operator_class)
                step_config = dict(step.config)
                if concept_dict:
                    step_config["concept"] = concept_dict
                if audience_dict:
                    step_config["audience_data"] = audience_dict
                if domain_dict:
                    step_config["domain"] = domain_dict
                output = operator.execute(topic, audience, context, step_config)
                artifact.set_layer(step.layer, output)
                context[step.layer.value] = output.content
                provenance.record(
                    layer=step.layer.value,
                    operator=step.operator_class,
                    duration_ms=(time.time() - start) * 1000,
                    ai_available=bool(self.ai_client and self.ai_client.is_available()),
                    config=step.config,
                )
                logger.info(f"[{run_id}] {step.layer.value}: confidence={output.confidence:.2f}")
            except Exception as e:
                logger.error(f"[{run_id}] {step.layer.value} failed: {e}")
                provenance.record(
                    layer=step.layer.value,
                    operator=step.operator_class,
                    duration_ms=(time.time() - start) * 1000,
                    success=False,
                    error=str(e),
                )

        provenance.complete()

        # Score the artifact
        evaluation = score_artifact(artifact, layer_configs)
        artifact.evaluation = evaluation

        # Build record
        record = ArtifactRecord(
            artifact=artifact,
            profile_name=profile_name,
        )
        record.add_revision(
            changed_layers=list(context.keys()),
            reason="Initial compilation",
            score_after=evaluation.overall_score,
        )

        logger.info(f"[{run_id}] Done: score={evaluation.overall_score:.3f}, layers={len(context)}")
        return record

    def _get_operator(self, class_path: str):
        """Dynamically import and instantiate an operator."""
        if class_path in self._operator_cache:
            return self._operator_cache[class_path]

        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        operator_class = getattr(module, class_name)
        operator = operator_class(ai_client=self.ai_client)
        self._operator_cache[class_path] = operator
        return operator

    @staticmethod
    def _infer_expertise(audience_id: str) -> str:
        expertise_map = {
            "child": "beginner",
            "general": "intermediate",
            "data_analyst": "advanced",
            "data_scientist": "expert",
            "ml_engineer": "expert",
            "genai_engineer": "expert",
            "phd": "expert",
            "academics": "expert",
            "business_analyst": "intermediate",
        }
        return expertise_map.get(audience_id, "intermediate")
