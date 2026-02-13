"""Concept Prerequisite DAG - materializes the implicit graph in concept YAMLs.

Provides transitive prerequisite resolution, learning path generation,
related-concept clustering, and difficulty estimation based on DAG depth.
"""

from __future__ import annotations

import logging
from graphlib import CycleError, TopologicalSorter
from typing import Dict, List, Optional, Set

from cognitive_scaffolding.core.concept import Concept

logger = logging.getLogger(__name__)


class ConceptGraph:
    """A directed acyclic graph of concept prerequisites and relationships.

    Built from a dict of Concept objects (as returned by DataLoader).
    """

    def __init__(self, concepts: Dict[str, Concept]):
        self._concepts = concepts
        self._prereq_graph: Dict[str, Set[str]] = {}
        self._related_graph: Dict[str, Set[str]] = {}
        self._cycles: List[List[str]] = []
        self._build()

    def _build(self) -> None:
        """Build prerequisite and related-concept graphs from loaded concepts."""
        for cid, concept in self._concepts.items():
            # Prerequisites: concept depends on these
            prereqs = set()
            for p in concept.prerequisite_concepts:
                if p in self._concepts:
                    prereqs.add(p)
                else:
                    logger.debug(f"Prerequisite '{p}' of '{cid}' not in concept set")
            self._prereq_graph[cid] = prereqs

            # Related concepts: bidirectional
            related = set()
            for r in concept.related_concepts:
                if r in self._concepts:
                    related.add(r)
            self._related_graph[cid] = related

        # Detect cycles
        try:
            ts = TopologicalSorter(self._prereq_graph)
            list(ts.static_order())
        except CycleError as e:
            self._cycles.append(list(str(e)))
            logger.warning(f"Cycle detected in prerequisite graph: {e}")

    @property
    def concept_ids(self) -> List[str]:
        """All concept IDs in the graph."""
        return list(self._concepts.keys())

    @property
    def cycles(self) -> List[List[str]]:
        """Any cycles detected in the prerequisite graph."""
        return self._cycles

    def get_prerequisites(self, concept_id: str) -> Set[str]:
        """Get transitive closure of all prerequisites for a concept."""
        if concept_id not in self._prereq_graph:
            return set()

        visited: Set[str] = set()
        stack = list(self._prereq_graph.get(concept_id, set()))

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            stack.extend(self._prereq_graph.get(current, set()) - visited)

        return visited

    def get_direct_prerequisites(self, concept_id: str) -> Set[str]:
        """Get only direct (non-transitive) prerequisites."""
        return set(self._prereq_graph.get(concept_id, set()))

    def get_learning_path(self, concept_id: str) -> List[str]:
        """Get a topologically sorted learning path ending at concept_id.

        Returns the list of prerequisites in order they should be learned,
        followed by the target concept itself.
        """
        if concept_id not in self._prereq_graph:
            return [concept_id] if concept_id in self._concepts else []

        # Build subgraph of transitive prerequisites + target
        prereqs = self.get_prerequisites(concept_id)
        relevant = prereqs | {concept_id}

        subgraph = {
            cid: self._prereq_graph.get(cid, set()) & relevant
            for cid in relevant
        }

        try:
            ts = TopologicalSorter(subgraph)
            return list(ts.static_order())
        except CycleError:
            # If there's a cycle, return what we can
            return sorted(relevant)

    def get_related_cluster(self, concept_id: str, max_depth: int = 2) -> Set[str]:
        """Get related concepts up to max_depth hops away.

        Follows related_concepts links. max_depth=1 returns immediate neighbors,
        max_depth=2 returns neighbors of neighbors, etc.
        """
        if concept_id not in self._related_graph:
            return set()

        visited: Set[str] = {concept_id}
        result: Set[str] = set()
        frontier = {concept_id}

        for _ in range(max_depth):
            next_frontier: Set[str] = set()
            for cid in frontier:
                for neighbor in self._related_graph.get(cid, set()):
                    if neighbor not in visited:
                        result.add(neighbor)
                        visited.add(neighbor)
                        next_frontier.add(neighbor)
            frontier = next_frontier
            if not frontier:
                break

        return result

    def estimate_difficulty(self, concept_id: str) -> float:
        """Estimate concept difficulty based on DAG depth and prerequisite count.

        Returns a score from 0.0 (no prerequisites) to 1.0 (deep chain).
        """
        if concept_id not in self._prereq_graph:
            return 0.0

        prereqs = self.get_prerequisites(concept_id)
        if not prereqs:
            return 0.0

        # Depth = longest path to any root
        depth = self._max_depth(concept_id, set())
        count = len(prereqs)

        # Normalize: depth contributes 60%, count 40%
        # Assume max depth ~10 and max count ~20 for normalization
        depth_score = min(1.0, depth / 10.0)
        count_score = min(1.0, count / 20.0)

        return round(0.6 * depth_score + 0.4 * count_score, 3)

    def _max_depth(self, concept_id: str, visited: Set[str]) -> int:
        """Compute max depth from concept to any root (no prerequisites)."""
        if concept_id in visited:
            return 0  # Cycle guard
        visited = visited | {concept_id}

        prereqs = self._prereq_graph.get(concept_id, set())
        if not prereqs:
            return 0
        return 1 + max(self._max_depth(p, visited) for p in prereqs)

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID."""
        return self._concepts.get(concept_id)

    def get_dependents(self, concept_id: str) -> Set[str]:
        """Get concepts that directly depend on this concept (reverse lookup)."""
        dependents = set()
        for cid, prereqs in self._prereq_graph.items():
            if concept_id in prereqs:
                dependents.add(cid)
        return dependents
