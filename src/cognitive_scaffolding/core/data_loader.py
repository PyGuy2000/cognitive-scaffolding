"""Data loader for YAML concepts, audiences, and domains."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cognitive_scaffolding.core.audience import Audience
from cognitive_scaffolding.core.concept import Concept
from cognitive_scaffolding.core.domain import Domain

logger = logging.getLogger(__name__)


def _safe_load_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely load a YAML file, returning None on error."""
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        if not data:
            logger.warning(f"Empty YAML file: {file_path.name}")
            return None
        return data
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return None


class DataLoader:
    """Loads and caches YAML data files for concepts, audiences, and domains."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._concepts: Optional[Dict[str, Concept]] = None
        self._audiences: Optional[Dict[str, Audience]] = None
        self._domains: Optional[Dict[str, Domain]] = None

    def _ensure_concepts(self) -> Dict[str, Concept]:
        if self._concepts is None:
            self._concepts = {}
            concepts_dir = self.data_dir / "concepts"
            if concepts_dir.exists():
                for f in concepts_dir.glob("*.yaml"):
                    data = _safe_load_yaml(f)
                    if data:
                        try:
                            concept = Concept(**data)
                            self._concepts[concept.concept_id] = concept
                        except Exception as e:
                            logger.warning(f"Invalid concept {f.name}: {e}")
        return self._concepts

    def _ensure_audiences(self) -> Dict[str, Audience]:
        if self._audiences is None:
            self._audiences = {}
            audiences_dir = self.data_dir / "audiences"
            if audiences_dir.exists():
                for f in audiences_dir.glob("*.yaml"):
                    data = _safe_load_yaml(f)
                    if data and isinstance(data, dict):
                        # Audience files may contain multiple audiences
                        if "audience_id" in data:
                            try:
                                aud = Audience(**data)
                                self._audiences[aud.audience_id] = aud
                            except Exception as e:
                                logger.warning(f"Invalid audience {f.name}: {e}")
                        else:
                            # File may be a dict of audiences
                            for key, val in data.items():
                                if isinstance(val, dict) and "audience_id" in val:
                                    try:
                                        aud = Audience(**val)
                                        self._audiences[aud.audience_id] = aud
                                    except Exception as e:
                                        logger.warning(f"Invalid audience {key} in {f.name}: {e}")
        return self._audiences

    def _ensure_domains(self) -> Dict[str, Domain]:
        if self._domains is None:
            self._domains = {}
            domains_dir = self.data_dir / "domains"
            if domains_dir.exists():
                for f in domains_dir.glob("*.yaml"):
                    data = _safe_load_yaml(f)
                    if data:
                        try:
                            domain = Domain(**data)
                            self._domains[domain.domain_id] = domain
                        except Exception as e:
                            logger.warning(f"Invalid domain {f.name}: {e}")
        return self._domains

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        return self._ensure_concepts().get(concept_id)

    def get_audience(self, audience_id: str) -> Optional[Audience]:
        return self._ensure_audiences().get(audience_id)

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        return self._ensure_domains().get(domain_id)

    def list_concepts(self) -> List[str]:
        return list(self._ensure_concepts().keys())

    def list_audiences(self) -> List[str]:
        return list(self._ensure_audiences().keys())

    def list_domains(self) -> List[str]:
        return list(self._ensure_domains().keys())
