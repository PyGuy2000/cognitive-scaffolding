"""Feature toggle system with 3 levels: profile defaults, runtime overrides, experiments.

Level 1: Profile YAML defaults (per-layer enabled/required/weight)
Level 2: Runtime overrides (API caller can override any toggle)
Level 3: A/B experiments (compare scores with different toggle combinations)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cognitive_scaffolding.core.models import LayerName
from cognitive_scaffolding.core.scoring import LayerConfig

logger = logging.getLogger(__name__)


class ToggleManager:
    """Manages feature toggles at 3 levels: profile, runtime, experiment."""

    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self._profiles_cache: Dict[str, Dict[str, LayerConfig]] = {}

    def load_profile(self, profile_name: str) -> Dict[str, LayerConfig]:
        """Load layer configs from a profile YAML file."""
        if profile_name in self._profiles_cache:
            return self._profiles_cache[profile_name]

        profile_path = self.profiles_dir / f"{profile_name}.yaml"
        if not profile_path.exists():
            logger.warning(f"Profile not found: {profile_path}")
            return self._default_configs()

        try:
            with open(profile_path, "r") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
            return self._default_configs()

        layers_data = data.get("layers", {})
        configs: Dict[str, LayerConfig] = {}
        for layer in LayerName:
            layer_data = layers_data.get(layer.value, {})
            configs[layer.value] = LayerConfig(
                enabled=layer_data.get("enabled", True),
                required=layer_data.get("required", False),
                weight=layer_data.get("weight", 1.0),
            )

        self._profiles_cache[profile_name] = configs
        return configs

    def apply_overrides(
        self,
        base_configs: Dict[str, LayerConfig],
        overrides: Dict[str, Dict[str, Any]],
    ) -> Dict[str, LayerConfig]:
        """Apply runtime overrides on top of profile defaults.

        overrides format: {"activation": {"enabled": false, "weight": 2.0}, ...}
        """
        merged = {}
        for layer_name, config in base_configs.items():
            override = overrides.get(layer_name, {})
            merged[layer_name] = LayerConfig(
                enabled=override.get("enabled", config.enabled),
                required=override.get("required", config.required),
                weight=override.get("weight", config.weight),
            )
        return merged

    def create_experiment_variants(
        self,
        base_configs: Dict[str, LayerConfig],
        toggle_layer: str,
    ) -> tuple[Dict[str, LayerConfig], Dict[str, LayerConfig]]:
        """Create two variants for A/B testing: one with layer enabled, one disabled."""
        variant_a = {k: LayerConfig(v.enabled, v.required, v.weight) for k, v in base_configs.items()}
        variant_b = {k: LayerConfig(v.enabled, v.required, v.weight) for k, v in base_configs.items()}

        if toggle_layer in variant_a:
            variant_a[toggle_layer] = LayerConfig(True, variant_a[toggle_layer].required, variant_a[toggle_layer].weight)
            variant_b[toggle_layer] = LayerConfig(False, False, variant_b[toggle_layer].weight)

        return variant_a, variant_b

    @staticmethod
    def _default_configs() -> Dict[str, LayerConfig]:
        """All layers enabled with equal weight, none required."""
        return {layer.value: LayerConfig(enabled=True, required=False, weight=1.0) for layer in LayerName}
