"""Unit tests for ConceptGraph (concept prerequisite DAG)."""

import pytest

from cognitive_scaffolding.core.concept import Concept
from cognitive_scaffolding.core.concept_graph import ConceptGraph


def _make_concept(cid: str, prereqs: list = None, related: list = None) -> Concept:
    return Concept(
        concept_id=cid,
        name=cid.replace("_", " ").title(),
        prerequisite_concepts=prereqs or [],
        related_concepts=related or [],
    )


@pytest.fixture()
def simple_graph() -> ConceptGraph:
    """A -> B -> C (C depends on B, B depends on A)."""
    concepts = {
        "A": _make_concept("A"),
        "B": _make_concept("B", prereqs=["A"]),
        "C": _make_concept("C", prereqs=["B"], related=["D"]),
        "D": _make_concept("D", related=["C"]),
    }
    return ConceptGraph(concepts)


@pytest.fixture()
def diamond_graph() -> ConceptGraph:
    """Diamond: D depends on B and C, both depend on A."""
    concepts = {
        "A": _make_concept("A"),
        "B": _make_concept("B", prereqs=["A"]),
        "C": _make_concept("C", prereqs=["A"]),
        "D": _make_concept("D", prereqs=["B", "C"]),
    }
    return ConceptGraph(concepts)


@pytest.fixture()
def isolated_graph() -> ConceptGraph:
    """No prerequisites, just related concepts."""
    concepts = {
        "X": _make_concept("X", related=["Y"]),
        "Y": _make_concept("Y", related=["X", "Z"]),
        "Z": _make_concept("Z", related=["Y"]),
    }
    return ConceptGraph(concepts)


class TestConceptGraphBasics:
    def test_concept_ids(self, simple_graph):
        assert set(simple_graph.concept_ids) == {"A", "B", "C", "D"}

    def test_no_cycles(self, simple_graph):
        assert simple_graph.cycles == []

    def test_get_concept(self, simple_graph):
        c = simple_graph.get_concept("B")
        assert c is not None
        assert c.concept_id == "B"

    def test_get_concept_missing(self, simple_graph):
        assert simple_graph.get_concept("nonexistent") is None


class TestDirectPrerequisites:
    def test_root_has_no_prereqs(self, simple_graph):
        assert simple_graph.get_direct_prerequisites("A") == set()

    def test_direct_prereqs(self, simple_graph):
        assert simple_graph.get_direct_prerequisites("B") == {"A"}
        assert simple_graph.get_direct_prerequisites("C") == {"B"}

    def test_diamond_prereqs(self, diamond_graph):
        assert diamond_graph.get_direct_prerequisites("D") == {"B", "C"}


class TestTransitivePrerequisites:
    def test_root_has_no_transitive(self, simple_graph):
        assert simple_graph.get_prerequisites("A") == set()

    def test_single_hop(self, simple_graph):
        assert simple_graph.get_prerequisites("B") == {"A"}

    def test_transitive_closure(self, simple_graph):
        assert simple_graph.get_prerequisites("C") == {"A", "B"}

    def test_diamond_transitive(self, diamond_graph):
        assert diamond_graph.get_prerequisites("D") == {"A", "B", "C"}

    def test_nonexistent_concept(self, simple_graph):
        assert simple_graph.get_prerequisites("nonexistent") == set()


class TestLearningPath:
    def test_root_path(self, simple_graph):
        path = simple_graph.get_learning_path("A")
        assert path == ["A"]

    def test_linear_path(self, simple_graph):
        path = simple_graph.get_learning_path("C")
        # Must be topological: A before B, B before C
        assert path.index("A") < path.index("B")
        assert path.index("B") < path.index("C")

    def test_diamond_path(self, diamond_graph):
        path = diamond_graph.get_learning_path("D")
        assert path[0] == "A"  # Root first
        assert path[-1] == "D"  # Target last
        assert len(path) == 4

    def test_nonexistent_concept(self, simple_graph):
        path = simple_graph.get_learning_path("nonexistent")
        assert path == []


class TestRelatedCluster:
    def test_immediate_related(self, simple_graph):
        cluster = simple_graph.get_related_cluster("C", max_depth=1)
        assert "D" in cluster
        assert "C" not in cluster  # Should not include self

    def test_two_hop_related(self, isolated_graph):
        cluster = isolated_graph.get_related_cluster("X", max_depth=2)
        assert "Y" in cluster
        assert "Z" in cluster

    def test_one_hop_related(self, isolated_graph):
        cluster = isolated_graph.get_related_cluster("X", max_depth=1)
        assert "Y" in cluster
        # Z is 2 hops away, should not be in 1-hop cluster
        assert "Z" not in cluster

    def test_no_related(self, diamond_graph):
        # Diamond graph concepts have no related_concepts set
        cluster = diamond_graph.get_related_cluster("A")
        assert cluster == set()


class TestDifficultyEstimation:
    def test_root_zero_difficulty(self, simple_graph):
        assert simple_graph.estimate_difficulty("A") == 0.0

    def test_deeper_is_harder(self, simple_graph):
        diff_b = simple_graph.estimate_difficulty("B")
        diff_c = simple_graph.estimate_difficulty("C")
        assert diff_c > diff_b

    def test_diamond_difficulty(self, diamond_graph):
        # D has depth 2 and 3 prereqs
        diff = diamond_graph.estimate_difficulty("D")
        assert diff > 0.0

    def test_nonexistent_zero(self, simple_graph):
        assert simple_graph.estimate_difficulty("nonexistent") == 0.0


class TestDependents:
    def test_root_has_dependents(self, simple_graph):
        assert simple_graph.get_dependents("A") == {"B"}

    def test_mid_has_dependent(self, simple_graph):
        assert simple_graph.get_dependents("B") == {"C"}

    def test_leaf_has_no_dependents(self, simple_graph):
        assert simple_graph.get_dependents("C") == set()

    def test_diamond_dependents(self, diamond_graph):
        assert diamond_graph.get_dependents("A") == {"B", "C"}
        assert diamond_graph.get_dependents("B") == {"D"}


class TestEdgeCases:
    def test_empty_graph(self):
        graph = ConceptGraph({})
        assert graph.concept_ids == []
        assert graph.get_prerequisites("anything") == set()

    def test_single_concept(self):
        concepts = {"solo": _make_concept("solo")}
        graph = ConceptGraph(concepts)
        assert graph.get_learning_path("solo") == ["solo"]
        assert graph.estimate_difficulty("solo") == 0.0

    def test_missing_prereq_reference(self):
        """Prerequisite references a concept not in the graph."""
        concepts = {
            "A": _make_concept("A", prereqs=["nonexistent"]),
        }
        graph = ConceptGraph(concepts)
        # Missing prereq should be silently skipped
        assert graph.get_prerequisites("A") == set()
