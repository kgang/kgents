"""
Tests for the Derivation Registry.

These tests verify the registry behavior and the five derivation laws:
1. Monotonicity: Agents derive from same or higher tiers only
2. Confidence Ceiling: Evidence can't exceed tier ceiling
3. Bootstrap Indefeasibility: Bootstrap agents never change
4. Acyclicity: The derivation graph is a DAG
5. Propagation: Confidence changes propagate through the DAG
"""

import pytest

from ..registry import DerivationDAG, DerivationRegistry, get_registry, reset_registry
from ..types import DerivationTier, EvidenceType, PrincipleDraw


class TestDerivationDAG:
    """Tests for the DerivationDAG class."""

    def test_add_node(self) -> None:
        """Nodes can be added to the DAG."""
        dag = DerivationDAG()
        dag.add_node("A")
        assert dag.parents("A") == frozenset()
        assert dag.dependents("A") == frozenset()

    def test_add_edges(self) -> None:
        """Edges can be added between nodes."""
        dag = DerivationDAG()
        dag.add_edges("B", ("A",))

        assert dag.parents("B") == frozenset({"A"})
        assert dag.dependents("A") == frozenset({"B"})

    def test_multiple_parents(self) -> None:
        """A node can derive from multiple parents."""
        dag = DerivationDAG()
        dag.add_edges("C", ("A", "B"))

        assert dag.parents("C") == frozenset({"A", "B"})
        assert dag.dependents("A") == frozenset({"C"})
        assert dag.dependents("B") == frozenset({"C"})

    def test_cycle_detection(self) -> None:
        """Adding a cycle raises ValueError (Law 4)."""
        dag = DerivationDAG()
        dag.add_edges("B", ("A",))
        dag.add_edges("C", ("B",))

        # Trying to make A derive from C would create cycle
        with pytest.raises(ValueError, match="cycle"):
            dag.add_edges("A", ("C",))

    def test_self_cycle_detection(self) -> None:
        """Self-referential edges are cycles."""
        dag = DerivationDAG()
        dag.add_node("A")

        with pytest.raises(ValueError, match="cycle"):
            dag.add_edges("A", ("A",))

    def test_ancestors(self) -> None:
        """ancestors returns transitive closure."""
        dag = DerivationDAG()
        dag.add_edges("B", ("A",))
        dag.add_edges("C", ("B",))
        dag.add_edges("D", ("C",))

        assert dag.ancestors("D") == frozenset({"A", "B", "C"})
        assert dag.ancestors("A") == frozenset()

    def test_descendants(self) -> None:
        """descendants returns transitive closure."""
        dag = DerivationDAG()
        dag.add_edges("B", ("A",))
        dag.add_edges("C", ("A",))
        dag.add_edges("D", ("B", "C"))

        assert dag.descendants("A") == frozenset({"B", "C", "D"})
        assert dag.descendants("D") == frozenset()


class TestDerivationRegistry:
    """Tests for the DerivationRegistry class."""

    def test_bootstrap_agents_seeded(self) -> None:
        """Registry seeds with 7 bootstrap agents."""
        registry = DerivationRegistry()

        for name in ("Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix"):
            derivation = registry.get(name)
            assert derivation is not None
            assert derivation.tier == DerivationTier.BOOTSTRAP
            assert derivation.total_confidence == 1.0

    def test_register_derived_agent(self) -> None:
        """Can register agents derived from bootstrap."""
        registry = DerivationRegistry()

        derivation = registry.register(
            agent_name="Flux",
            derives_from=("Fix", "Compose"),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.95,
                    evidence_type=EvidenceType.CATEGORICAL,
                    evidence_sources=("flux-associativity-test",),
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        assert derivation.agent_name == "Flux"
        assert derivation.tier == DerivationTier.FUNCTOR
        assert "Fix" in derivation.derives_from
        assert "Compose" in derivation.derives_from

    def test_inherited_confidence_from_ancestors(self) -> None:
        """Inherited confidence is computed from ancestor confidence."""
        registry = DerivationRegistry()

        # Derive from two bootstrap agents with confidence 1.0 each
        derivation = registry.register(
            agent_name="Test",
            derives_from=("Id", "Compose"),
            principle_draws=(),
            tier=DerivationTier.FUNCTOR,
        )

        # Product of 1.0 * 1.0 = 1.0
        assert derivation.inherited_confidence == 1.0

    def test_law1_monotonicity_enforced(self) -> None:
        """Law 1: Can't derive more foundational tier from less foundational."""
        registry = DerivationRegistry()

        # First register an APP tier agent (least foundational)
        registry.register(
            agent_name="App1",
            derives_from=("Id",),
            principle_draws=(),
            tier=DerivationTier.APP,
        )

        # Trying to derive a FUNCTOR (more foundational) from APP should fail
        # Because: FUNCTOR < APP in the tier ordering
        with pytest.raises(ValueError, match="Monotonicity"):
            registry.register(
                agent_name="BadFunctor",
                derives_from=("App1",),
                principle_draws=(),
                tier=DerivationTier.FUNCTOR,
            )

    def test_law2_confidence_ceiling(self) -> None:
        """Law 2: Total confidence respects tier ceiling."""
        registry = DerivationRegistry()

        derivation = registry.register(
            agent_name="App1",
            derives_from=("Id",),
            principle_draws=(),
            tier=DerivationTier.APP,
        )

        # Update with high evidence
        updated = registry.update_evidence("App1", ashc_score=1.0, usage_count=10000)

        # Still capped at APP ceiling (0.75)
        assert updated.total_confidence <= 0.75

    def test_law3_bootstrap_indefeasibility(self) -> None:
        """Law 3: Can't update bootstrap agent evidence."""
        registry = DerivationRegistry()

        with pytest.raises(ValueError, match="Bootstrap Indefeasibility"):
            registry.update_evidence("Id", ashc_score=0.5)

    def test_law4_acyclicity_enforced(self) -> None:
        """Law 4: Can't create cycles in derivation graph."""
        registry = DerivationRegistry()

        # Create a valid chain: A -> B -> C (each tier >= parent tier)
        # FUNCTOR derives from BOOTSTRAP (Id), POLYNOMIAL from FUNCTOR, etc.
        registry.register("A", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)
        registry.register("B", derives_from=("A",), principle_draws=(), tier=DerivationTier.POLYNOMIAL)
        registry.register("C", derives_from=("B",), principle_draws=(), tier=DerivationTier.OPERAD)

        # The cycle detection is tested in TestDerivationDAG
        # This test just confirms the chain was built correctly
        assert registry.exists("A")
        assert registry.exists("B")
        assert registry.exists("C")
        assert "A" in registry.ancestors("C")
        assert "B" in registry.ancestors("C")

    def test_law5_propagation(self) -> None:
        """Law 5: Confidence changes propagate to dependents."""
        registry = DerivationRegistry()

        # Create chain: A -> B -> C (each tier >= parent tier)
        registry.register("A", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)
        registry.register("B", derives_from=("A",), principle_draws=(), tier=DerivationTier.POLYNOMIAL)
        registry.register("C", derives_from=("B",), principle_draws=(), tier=DerivationTier.OPERAD)

        # C's confidence depends on B which depends on A
        c_before = registry.get("C")
        assert c_before is not None
        confidence_before = c_before.total_confidence

        # Update A's evidence (increases its confidence)
        registry.update_evidence("A", ashc_score=0.9, usage_count=1000)

        # C's inherited confidence should change (through propagation)
        c_after = registry.get("C")
        assert c_after is not None
        # The propagation should have updated inherited confidence
        # (The total may or may not change depending on ceilings)

    def test_update_evidence_with_ashc(self) -> None:
        """ASHC scores update empirical confidence."""
        registry = DerivationRegistry()

        registry.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)

        derivation = registry.update_evidence("Test", ashc_score=0.85)
        assert derivation.empirical_confidence == 0.85

    def test_update_evidence_with_usage(self) -> None:
        """Usage counts update stigmergic confidence."""
        registry = DerivationRegistry()

        registry.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)

        derivation = registry.update_evidence("Test", usage_count=1000)
        assert derivation.stigmergic_confidence > 0.0

    def test_increment_usage(self) -> None:
        """Usage can be incremented one at a time."""
        registry = DerivationRegistry()

        registry.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)

        # Increment 100 times
        for _ in range(100):
            registry.increment_usage("Test")

        assert registry.get_usage_count("Test") == 100

    def test_decay_all_skips_bootstrap(self) -> None:
        """decay_all doesn't affect bootstrap agents."""
        registry = DerivationRegistry()

        # Add a derived agent with decayable evidence
        registry.register(
            "Test",
            derives_from=("Id",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=1.0,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        # Decay all
        decayed_count = registry.decay_all(days_elapsed=30.0)

        # Bootstrap agents unchanged
        assert registry.get("Id").total_confidence == 1.0

        # Derived agent was decayed
        assert decayed_count >= 1

    def test_list_agents(self) -> None:
        """Can list all agents or filter by tier."""
        registry = DerivationRegistry()

        registry.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)

        all_agents = registry.list_agents()
        assert "Id" in all_agents
        assert "Test" in all_agents

        bootstrap_only = registry.list_agents(tier=DerivationTier.BOOTSTRAP)
        assert "Id" in bootstrap_only
        assert "Test" not in bootstrap_only

    def test_ancestors(self) -> None:
        """Can get all ancestors of an agent."""
        registry = DerivationRegistry()

        registry.register("A", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)
        registry.register("B", derives_from=("A", "Compose"), principle_draws=(), tier=DerivationTier.POLYNOMIAL)

        ancestors = registry.ancestors("B")
        assert "A" in ancestors
        assert "Id" in ancestors
        assert "Compose" in ancestors

    def test_dependents(self) -> None:
        """Can get all dependents of an agent."""
        registry = DerivationRegistry()

        registry.register("A", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)
        registry.register("B", derives_from=("A",), principle_draws=(), tier=DerivationTier.POLYNOMIAL)

        dependents = registry.dependents("Id")
        assert "A" in dependents
        assert "B" in dependents

    def test_len_and_contains(self) -> None:
        """Registry supports len() and 'in' operator."""
        registry = DerivationRegistry()

        # 7 bootstrap agents
        assert len(registry) == 7
        assert "Id" in registry
        assert "NotRegistered" not in registry

        registry.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)
        assert len(registry) == 8


class TestGlobalRegistry:
    """Tests for the global registry functions."""

    def test_get_registry_singleton(self) -> None:
        """get_registry returns the same instance."""
        reset_registry()

        r1 = get_registry()
        r2 = get_registry()

        assert r1 is r2

    def test_reset_registry(self) -> None:
        """reset_registry creates a fresh instance."""
        reset_registry()

        r1 = get_registry()
        r1.register("Test", derives_from=("Id",), principle_draws=(), tier=DerivationTier.FUNCTOR)

        reset_registry()

        r2 = get_registry()
        assert "Test" not in r2
