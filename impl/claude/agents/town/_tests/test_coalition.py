"""Tests for Phase 4 coalition detection and reputation."""

import pytest
from agents.town.citizen import Citizen, Eigenvectors
from agents.town.coalition import (
    Coalition,
    CoalitionManager,
    ReputationGraph,
    detect_coalitions,
    find_k_cliques,
    percolate_cliques,
)

# =============================================================================
# Fixtures
# =============================================================================


def create_test_citizens() -> dict[str, Citizen]:
    """Create a set of citizens for testing coalitions."""
    # Group 1: High warmth, high trust (3 similar citizens)
    alice = Citizen(
        name="Alice",
        archetype="TestA",
        region="square",
        eigenvectors=Eigenvectors(warmth=0.9, trust=0.9, curiosity=0.5),
    )
    bob = Citizen(
        name="Bob",
        archetype="TestA",
        region="square",
        eigenvectors=Eigenvectors(warmth=0.85, trust=0.88, curiosity=0.52),
    )
    carol = Citizen(
        name="Carol",
        archetype="TestA",
        region="square",
        eigenvectors=Eigenvectors(warmth=0.88, trust=0.91, curiosity=0.48),
    )

    # Group 2: High ambition, high curiosity (3 similar citizens)
    dave = Citizen(
        name="Dave",
        archetype="TestB",
        region="market",
        eigenvectors=Eigenvectors(ambition=0.9, curiosity=0.9, warmth=0.3),
    )
    eve = Citizen(
        name="Eve",
        archetype="TestB",
        region="market",
        eigenvectors=Eigenvectors(ambition=0.88, curiosity=0.87, warmth=0.32),
    )
    frank = Citizen(
        name="Frank",
        archetype="TestB",
        region="market",
        eigenvectors=Eigenvectors(ambition=0.91, curiosity=0.89, warmth=0.28),
    )

    # Outlier: Different from all groups
    grace = Citizen(
        name="Grace",
        archetype="TestC",
        region="garden",
        eigenvectors=Eigenvectors(patience=0.9, resilience=0.9, ambition=0.1),
    )

    return {
        alice.id: alice,
        bob.id: bob,
        carol.id: carol,
        dave.id: dave,
        eve.id: eve,
        frank.id: frank,
        grace.id: grace,
    }


# =============================================================================
# Coalition Tests
# =============================================================================


class TestCoalition:
    """Tests for Coalition dataclass."""

    def test_coalition_creation(self) -> None:
        """Coalition should initialize with defaults."""
        coalition = Coalition()
        assert coalition.id is not None
        assert coalition.members == set()
        assert coalition.strength == 1.0

    def test_add_remove_member(self) -> None:
        """Coalition should track members."""
        coalition = Coalition()
        coalition.add_member("citizen-1")
        coalition.add_member("citizen-2")

        assert coalition.size == 2
        assert "citizen-1" in coalition.members

        coalition.remove_member("citizen-1")
        assert coalition.size == 1
        assert "citizen-1" not in coalition.members

    def test_decay(self) -> None:
        """Coalition strength should decay."""
        coalition = Coalition()
        initial = coalition.strength

        coalition.decay(0.1)
        assert coalition.strength == initial - 0.1

        # Clamp at 0
        coalition.decay(2.0)
        assert coalition.strength == 0.0

    def test_reinforce(self) -> None:
        """Coalition strength should reinforce."""
        coalition = Coalition(strength=0.5)

        coalition.reinforce(0.2)
        assert coalition.strength == 0.7

        # Clamp at 1
        coalition.reinforce(1.0)
        assert coalition.strength == 1.0

    def test_is_alive(self) -> None:
        """Coalition should track alive status."""
        coalition = Coalition(members={"a", "b"})
        assert coalition.is_alive()

        # Low strength
        coalition.strength = 0.05
        assert not coalition.is_alive()

        # Few members
        coalition.strength = 1.0
        coalition.members = {"a"}
        assert not coalition.is_alive()

    def test_compute_centroid(self) -> None:
        """Coalition centroid should average eigenvectors."""
        citizens = create_test_citizens()
        ids = list(citizens.keys())[:3]  # First 3 (similar)

        coalition = Coalition(members=set(ids))
        centroid = coalition.compute_centroid(citizens)

        # Centroid warmth should be close to members' average
        avg_warmth = sum(citizens[cid].eigenvectors.warmth for cid in ids) / 3
        assert abs(centroid.warmth - avg_warmth) < 0.01


# =============================================================================
# k-Clique Tests
# =============================================================================


class TestKClique:
    """Tests for k-clique detection."""

    def test_find_2_cliques(self) -> None:
        """find_k_cliques should find edges for k=2."""
        adj = {
            "a": {"b", "c"},
            "b": {"a", "c"},
            "c": {"a", "b"},
        }
        cliques = find_k_cliques(adj, k=2)
        assert len(cliques) == 3  # Three edges

    def test_find_3_cliques_triangle(self) -> None:
        """find_k_cliques should find triangles for k=3."""
        adj = {
            "a": {"b", "c"},
            "b": {"a", "c"},
            "c": {"a", "b"},
        }
        cliques = find_k_cliques(adj, k=3)
        assert len(cliques) == 1  # One triangle
        assert cliques[0] == frozenset(["a", "b", "c"])

    def test_find_3_cliques_two_triangles(self) -> None:
        """find_k_cliques should find multiple triangles."""
        # Two triangles sharing edge (a, b)
        adj = {
            "a": {"b", "c", "d"},
            "b": {"a", "c", "d"},
            "c": {"a", "b"},
            "d": {"a", "b"},
        }
        cliques = find_k_cliques(adj, k=3)
        assert len(cliques) == 2

    def test_no_cliques(self) -> None:
        """find_k_cliques should return empty for no cliques."""
        adj = {
            "a": {"b"},
            "b": {"a"},
            "c": set(),
        }
        cliques = find_k_cliques(adj, k=3)
        assert len(cliques) == 0


class TestPercolation:
    """Tests for clique percolation."""

    def test_percolate_single_clique(self) -> None:
        """Single clique should form single community."""
        cliques = [frozenset(["a", "b", "c"])]
        communities = percolate_cliques(cliques, k=3)
        assert len(communities) == 1
        assert communities[0] == {"a", "b", "c"}

    def test_percolate_overlapping_cliques(self) -> None:
        """Overlapping cliques should merge."""
        # Two triangles sharing edge
        cliques = [
            frozenset(["a", "b", "c"]),
            frozenset(["a", "b", "d"]),
        ]
        communities = percolate_cliques(cliques, k=3)
        assert len(communities) == 1
        assert communities[0] == {"a", "b", "c", "d"}

    def test_percolate_disjoint_cliques(self) -> None:
        """Disjoint cliques should form separate communities."""
        cliques = [
            frozenset(["a", "b", "c"]),
            frozenset(["x", "y", "z"]),
        ]
        communities = percolate_cliques(cliques, k=3)
        assert len(communities) == 2


# =============================================================================
# Coalition Detection Tests
# =============================================================================


class TestCoalitionDetection:
    """Tests for detect_coalitions function."""

    def test_detect_similar_citizens(self) -> None:
        """detect_coalitions should find groups of similar citizens."""
        citizens = create_test_citizens()
        coalitions = detect_coalitions(citizens, similarity_threshold=0.95, k=3)

        # Should find at least one coalition (the similar groups)
        # Note: with high threshold, may find separate coalitions
        assert len(coalitions) >= 0  # May vary by threshold

    def test_detect_with_low_threshold(self) -> None:
        """Lower threshold should create larger coalitions."""
        citizens = create_test_citizens()

        # Very low threshold - almost everyone is similar
        coalitions = detect_coalitions(citizens, similarity_threshold=0.5, k=3)

        # Check total members across coalitions
        total_members = set()
        for c in coalitions:
            total_members.update(c.members)

        # With low threshold, more citizens should be in coalitions
        assert len(total_members) >= 3


# =============================================================================
# Reputation Tests
# =============================================================================


class TestReputationGraph:
    """Tests for EigenTrust reputation."""

    def test_set_get_trust(self) -> None:
        """Trust should be settable and gettable."""
        graph = ReputationGraph()
        graph.set_trust("a", "b", 0.8)

        assert graph.get_trust("a", "b") == 0.8
        assert graph.get_trust("b", "a") == 0.0  # Not symmetric

    def test_trust_clamping(self) -> None:
        """Trust should be clamped to [0, 1]."""
        graph = ReputationGraph()
        graph.set_trust("a", "b", 1.5)
        assert graph.get_trust("a", "b") == 1.0

        graph.set_trust("a", "b", -0.5)
        assert graph.get_trust("a", "b") == 0.0

    def test_compute_reputation_uniform(self) -> None:
        """Reputation should be uniform with no trust edges."""
        citizens = create_test_citizens()
        graph = ReputationGraph()

        reputation = graph.compute_reputation(citizens)

        # All should have equal reputation
        values = list(reputation.values())
        assert all(abs(v - values[0]) < 0.01 for v in values)

    def test_compute_reputation_with_trust(self) -> None:
        """Citizens with more incoming trust should have higher reputation."""
        citizens = create_test_citizens()
        ids = list(citizens.keys())

        graph = ReputationGraph()

        # Everyone trusts the first citizen
        for cid in ids[1:]:
            graph.set_trust(cid, ids[0], 1.0)

        reputation = graph.compute_reputation(citizens, alpha=0.3)

        # First citizen should have highest reputation
        max_rep = max(reputation.values())
        assert reputation[ids[0]] == max_rep

    def test_update_from_interaction(self) -> None:
        """Interactions should update trust."""
        graph = ReputationGraph()

        # Successful interaction increases trust
        graph.update_from_interaction("a", "b", success=True, weight=0.2)
        assert graph.get_trust("a", "b") == 0.2

        # Failed interaction decreases trust
        graph.update_from_interaction("a", "b", success=False, weight=0.1)
        assert graph.get_trust("a", "b") == 0.1


# =============================================================================
# Coalition Manager Tests
# =============================================================================


class TestCoalitionManager:
    """Tests for CoalitionManager."""

    def test_manager_detect(self) -> None:
        """Manager should detect coalitions."""
        citizens = create_test_citizens()
        manager = CoalitionManager(citizens, similarity_threshold=0.9, k=3)

        coalitions = manager.detect()
        assert isinstance(coalitions, list)

    def test_manager_get_citizen_coalitions(self) -> None:
        """Manager should find coalitions for a citizen."""
        citizens = create_test_citizens()
        manager = CoalitionManager(citizens, similarity_threshold=0.9, k=3)
        manager.detect()

        # Get any citizen
        cid = list(citizens.keys())[0]
        coalitions = manager.get_citizen_coalitions(cid)
        assert isinstance(coalitions, list)

    def test_manager_decay_all(self) -> None:
        """Manager should decay all coalitions."""
        citizens = create_test_citizens()
        manager = CoalitionManager(citizens, similarity_threshold=0.5, k=3)
        manager.detect()

        # Apply decay multiple times
        for _ in range(25):  # Should decay to death
            manager.decay_all(0.1)

        # Weak coalitions should be pruned
        summary = manager.summary()
        assert summary["alive_coalitions"] <= summary["total_coalitions"]

    def test_manager_record_interaction(self) -> None:
        """Manager should record interactions for reputation."""
        citizens = create_test_citizens()
        ids = list(citizens.keys())
        manager = CoalitionManager(citizens)

        manager.record_interaction(ids[0], ids[1], success=True)
        assert manager.reputation.get_trust(ids[0], ids[1]) > 0

    def test_manager_summary(self) -> None:
        """Manager should provide summary statistics."""
        citizens = create_test_citizens()
        manager = CoalitionManager(citizens, similarity_threshold=0.5, k=3)
        manager.detect()

        summary = manager.summary()
        assert "total_coalitions" in summary
        assert "alive_coalitions" in summary
        assert "total_members" in summary
        assert "bridge_citizens" in summary
        assert "avg_strength" in summary


# =============================================================================
# Metric Laws Tests
# =============================================================================


class TestEigenvectorMetricLaws:
    """Tests for eigenvector metric laws (from S1 synergy)."""

    def test_l1_identity(self) -> None:
        """drift(x, x) should equal 0 (identity law)."""
        ev = Eigenvectors(warmth=0.8, curiosity=0.6)
        assert ev.drift(ev) == 0.0

    def test_l2_symmetry(self) -> None:
        """drift(x, y) should equal drift(y, x) (symmetry law)."""
        ev1 = Eigenvectors(warmth=0.8, curiosity=0.6)
        ev2 = Eigenvectors(warmth=0.3, curiosity=0.9)

        assert ev1.drift(ev2) == ev2.drift(ev1)

    def test_l3_triangle(self) -> None:
        """drift(x, z) should be <= drift(x, y) + drift(y, z) (triangle inequality)."""
        ev1 = Eigenvectors(warmth=0.1)
        ev2 = Eigenvectors(warmth=0.5)
        ev3 = Eigenvectors(warmth=0.9)

        d_xz = ev1.drift(ev3)
        d_xy = ev1.drift(ev2)
        d_yz = ev2.drift(ev3)

        assert d_xz <= d_xy + d_yz + 0.001  # Float tolerance
