"""Unit tests for toggle manager."""

import pytest

import yaml

from cognitive_scaffolding.core.models import LayerName
from cognitive_scaffolding.orchestrator.toggle_manager import ToggleManager


@pytest.fixture
def profiles_dir(tmp_path):
    """Create a temp profiles directory with a test profile."""
    profile = {
        "name": "test_profile",
        "layers": {
            "activation": {"enabled": True, "required": True, "weight": 1.2},
            "metaphor": {"enabled": True, "required": False, "weight": 1.5},
            "structure": {"enabled": True, "required": True, "weight": 1.0},
            "interrogation": {"enabled": False, "required": False, "weight": 0.5},
            "encoding": {"enabled": True, "required": False, "weight": 1.0},
            "transfer": {"enabled": False, "required": False, "weight": 0.5},
            "reflection": {"enabled": True, "required": False, "weight": 0.8},
        },
    }
    profile_path = tmp_path / "test_profile.yaml"
    with open(profile_path, "w") as f:
        yaml.dump(profile, f)
    return tmp_path


class TestToggleManager:
    def test_load_profile(self, profiles_dir):
        mgr = ToggleManager(str(profiles_dir))
        configs = mgr.load_profile("test_profile")
        assert configs["activation"].enabled is True
        assert configs["activation"].required is True
        assert configs["activation"].weight == 1.2
        assert configs["interrogation"].enabled is False

    def test_missing_profile_returns_defaults(self, profiles_dir):
        mgr = ToggleManager(str(profiles_dir))
        configs = mgr.load_profile("nonexistent")
        for layer in LayerName:
            assert configs[layer.value].enabled is True
            assert configs[layer.value].weight == 1.0

    def test_apply_overrides(self, profiles_dir):
        mgr = ToggleManager(str(profiles_dir))
        base = mgr.load_profile("test_profile")
        overrides = {"activation": {"enabled": False}, "metaphor": {"weight": 2.0}}
        merged = mgr.apply_overrides(base, overrides)
        assert merged["activation"].enabled is False
        assert merged["metaphor"].weight == 2.0
        assert merged["structure"].weight == 1.0  # unchanged

    def test_experiment_variants(self, profiles_dir):
        mgr = ToggleManager(str(profiles_dir))
        base = mgr.load_profile("test_profile")
        a, b = mgr.create_experiment_variants(base, "activation")
        assert a["activation"].enabled is True
        assert b["activation"].enabled is False
