"""
Tests for Phase 6: Typed-Hypergraph → Derivation Bridge.

Verifies:
- Hyperedge resolution for derivation relationships
- Law 6.3: Hyperedge Consistency
- Observer-dependent edges
- Cache management
- Registration with typed-hypergraph

See: spec/protocols/derivation-framework.md §6.3
"""

import pytest

from ..hypergraph_bridge import (
    DERIVATION_EDGE_TYPES,
    ContextNode,
    SimpleObserver,
    DerivationHyperedgeResolver,
    get_derivation_resolver,
    reset_derivation_resolver,
    register_derivation_resolvers,
    resolve_derivation_edge,
    get_derivation_graph_for_agent,
)
from ..types import Derivation, DerivationTier, PrincipleDraw, EvidenceType
from ..registry import DerivationRegistry


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry() -> DerivationRegistry:
    """Fresh registry for each test."""
    reset_derivation_resolver()  # Clear global resolver
    return DerivationRegistry()


@pytest.fixture
def populated_registry(registry: DerivationRegistry) -> DerivationRegistry:
    """Registry with a small agent hierarchy."""
    # Create a hierarchy: Compose <- Flux <- Brain
    registry.register(
        agent_name="Flux",
        derives_from=("Compose", "Fix"),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
            ),
        ),
        tier=DerivationTier.FUNCTOR,
    )
    registry.register(
        agent_name="Brain",
        derives_from=("Flux",),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.7,
                evidence_type=EvidenceType.EMPIRICAL,
            ),
            PrincipleDraw(
                principle="Curated",
                draw_strength=0.6,
                evidence_type=EvidenceType.AESTHETIC,
            ),
        ),
        tier=DerivationTier.JEWEL,
    )
    return registry


# =============================================================================
# ContextNode Tests
# =============================================================================


class TestContextNode:
    """Tests for ContextNode."""

    def test_for_agent_creates_concept_path(self):
        """for_agent creates concept.agent.* path."""
        node = ContextNode.for_agent("Flux")

        assert node.path == "concept.agent.Flux"
        assert node.holon == "Flux"

    def test_hash_by_path(self):
        """Nodes hash by path for set membership."""
        node1 = ContextNode(path="a", holon="A")
        node2 = ContextNode(path="a", holon="B")  # Same path, different holon

        assert hash(node1) == hash(node2)
        # Note: __eq__ is not overridden, so equality is object identity
        # But hash equality allows set membership to work with same-path nodes


# =============================================================================
# SimpleObserver Tests
# =============================================================================


class TestSimpleObserver:
    """Tests for SimpleObserver."""

    def test_default_archetype(self):
        """Default archetype is developer."""
        observer = SimpleObserver()
        assert observer.archetype == "developer"

    def test_custom_archetype(self):
        """Can create with custom archetype."""
        observer = SimpleObserver(archetype="architect")
        assert observer.archetype == "architect"


# =============================================================================
# DerivationHyperedgeResolver Tests
# =============================================================================


class TestDerivationHyperedgeResolver:
    """Tests for DerivationHyperedgeResolver."""

    def test_edge_types_constant(self):
        """EDGE_TYPES contains expected edge types."""
        assert "derives_from" in DERIVATION_EDGE_TYPES
        assert "shares_principle" in DERIVATION_EDGE_TYPES
        assert "confidence_flows_to" in DERIVATION_EDGE_TYPES

    def test_unknown_edge_type_returns_empty(self, populated_registry: DerivationRegistry):
        """Unknown edge type returns empty list."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("Brain", "unknown_edge", None)

        assert nodes == []

    def test_unknown_agent_returns_empty(self, populated_registry: DerivationRegistry):
        """Unknown agent returns empty list."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("UnknownAgent", "derives_from", None)

        assert nodes == []


class TestDerivesFromEdge:
    """Tests for derives_from edge resolution."""

    def test_derives_from_returns_parents(self, populated_registry: DerivationRegistry):
        """derives_from returns direct parents."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("Brain", "derives_from", None)

        assert len(nodes) == 1
        assert nodes[0].holon == "Flux"

    def test_law_6_3_consistency(self, populated_registry: DerivationRegistry):
        """Law 6.3: Hyperedge count matches DAG."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        for agent_name in populated_registry.list_agents():
            derivation = populated_registry.get(agent_name)
            if derivation:
                nodes = resolver.resolve(agent_name, "derives_from", None)
                assert len(nodes) == len(derivation.derives_from)

    def test_multiple_parents(self, populated_registry: DerivationRegistry):
        """Agent with multiple parents returns all."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("Flux", "derives_from", None)

        holons = {n.holon for n in nodes}
        assert "Compose" in holons
        assert "Fix" in holons


class TestConfidenceFlowsToEdge:
    """Tests for confidence_flows_to edge resolution."""

    def test_confidence_flows_to_returns_dependents(self, populated_registry: DerivationRegistry):
        """confidence_flows_to returns all dependents."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("Flux", "confidence_flows_to", None)

        holons = {n.holon for n in nodes}
        assert "Brain" in holons

    def test_bootstrap_has_many_dependents(self, populated_registry: DerivationRegistry):
        """Bootstrap agents have many dependents."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        nodes = resolver.resolve("Compose", "confidence_flows_to", None)

        # At least Flux depends on Compose
        assert len(nodes) >= 1


class TestSharesPrincipleEdge:
    """Tests for shares_principle edge resolution."""

    def test_shares_principle_hidden_from_developer(self, populated_registry: DerivationRegistry):
        """Developers don't see shares_principle edges."""
        resolver = DerivationHyperedgeResolver(populated_registry)
        developer = SimpleObserver(archetype="developer")

        nodes = resolver.resolve("Brain", "shares_principle", developer)

        assert nodes == []

    def test_shares_principle_visible_to_architect(self, populated_registry: DerivationRegistry):
        """Architects see shares_principle edges."""
        resolver = DerivationHyperedgeResolver(populated_registry)
        architect = SimpleObserver(archetype="architect")

        nodes = resolver.resolve("Brain", "shares_principle", architect)

        # Brain shares Composable with Flux
        holons = {n.holon for n in nodes}
        assert "Flux" in holons

    def test_shares_principle_visible_to_analyst(self, populated_registry: DerivationRegistry):
        """Analysts see shares_principle edges."""
        resolver = DerivationHyperedgeResolver(populated_registry)
        analyst = SimpleObserver(archetype="analyst")

        nodes = resolver.resolve("Brain", "shares_principle", analyst)

        assert len(nodes) > 0

    def test_observer_dependent(self, populated_registry: DerivationRegistry):
        """Same query, different observers, different results."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        developer_nodes = resolver.resolve(
            "Brain", "shares_principle", SimpleObserver(archetype="developer")
        )
        architect_nodes = resolver.resolve(
            "Brain", "shares_principle", SimpleObserver(archetype="architect")
        )

        assert len(developer_nodes) == 0
        assert len(architect_nodes) > 0


class TestResolverCache:
    """Tests for resolver caching."""

    def test_cache_invalidation(self, populated_registry: DerivationRegistry):
        """Cache clears on invalidate_cache()."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        # Populate cache
        resolver.resolve("Brain", "derives_from", None)
        assert "Brain" in resolver._derives_from_cache

        # Invalidate
        resolver.invalidate_cache()

        assert "Brain" not in resolver._derives_from_cache

    def test_cache_version_increments(self, populated_registry: DerivationRegistry):
        """Cache version increments on invalidation."""
        resolver = DerivationHyperedgeResolver(populated_registry)
        initial_version = resolver._cache_version

        resolver.invalidate_cache()

        assert resolver._cache_version > initial_version


class TestAvailableEdges:
    """Tests for available_edges()."""

    def test_available_edges_returns_counts(self, populated_registry: DerivationRegistry):
        """available_edges returns edge type → count mapping."""
        resolver = DerivationHyperedgeResolver(populated_registry)
        architect = SimpleObserver(archetype="architect")

        edges = resolver.available_edges("Brain", architect)

        assert "derives_from" in edges
        assert edges["derives_from"] == 1  # Brain derives from Flux

    def test_available_edges_observer_dependent(self, populated_registry: DerivationRegistry):
        """available_edges respects observer."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        dev_edges = resolver.available_edges("Brain", SimpleObserver(archetype="developer"))
        arch_edges = resolver.available_edges("Brain", SimpleObserver(archetype="architect"))

        # Developer doesn't see shares_principle
        assert "shares_principle" not in dev_edges or dev_edges.get("shares_principle", 0) == 0
        assert "shares_principle" in arch_edges and arch_edges["shares_principle"] > 0


# =============================================================================
# Global Resolver Management Tests
# =============================================================================


class TestGlobalResolverManagement:
    """Tests for global resolver functions."""

    def test_get_derivation_resolver_creates(self, registry: DerivationRegistry):
        """get_derivation_resolver creates resolver on first call."""
        reset_derivation_resolver()

        resolver = get_derivation_resolver(registry)

        assert resolver is not None
        assert resolver._registry is registry

    def test_get_derivation_resolver_caches(self, registry: DerivationRegistry):
        """get_derivation_resolver returns same instance."""
        resolver1 = get_derivation_resolver(registry)
        resolver2 = get_derivation_resolver(registry)

        assert resolver1 is resolver2

    def test_reset_derivation_resolver(self, registry: DerivationRegistry):
        """reset_derivation_resolver clears global instance."""
        resolver1 = get_derivation_resolver(registry)
        reset_derivation_resolver()
        resolver2 = get_derivation_resolver(registry)

        assert resolver1 is not resolver2


class TestRegisterDerivationResolvers:
    """Tests for register_derivation_resolvers()."""

    def test_returns_resolver(self, registry: DerivationRegistry):
        """Returns the resolver for direct use."""
        resolver = register_derivation_resolvers(registry)

        assert isinstance(resolver, DerivationHyperedgeResolver)

    def test_registers_with_hypergraph_registry(self, registry: DerivationRegistry):
        """Registers with provided hypergraph registry."""
        hypergraph_registry = {}

        register_derivation_resolvers(registry, hypergraph_registry)

        # Should have entries for each edge type
        assert any("derives_from" in k for k in hypergraph_registry.keys())


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_resolve_derivation_edge(self, populated_registry: DerivationRegistry):
        """resolve_derivation_edge works without managing resolver."""
        nodes = resolve_derivation_edge(
            "Brain",
            "derives_from",
            populated_registry,
        )

        assert len(nodes) == 1
        assert nodes[0].holon == "Flux"

    def test_get_derivation_graph_for_agent(self, populated_registry: DerivationRegistry):
        """get_derivation_graph_for_agent returns local graph."""
        graph = get_derivation_graph_for_agent(
            "Brain",
            populated_registry,
            max_depth=2,
        )

        # Should have Brain's derives_from
        assert any("Brain" in k and "derives_from" in k for k in graph.keys())


# =============================================================================
# Async Tests
# =============================================================================


class TestAsyncResolve:
    """Tests for async resolution."""

    @pytest.mark.asyncio
    async def test_resolve_async(self, populated_registry: DerivationRegistry):
        """resolve_async returns same results as sync."""
        resolver = DerivationHyperedgeResolver(populated_registry)

        sync_result = resolver.resolve("Brain", "derives_from", None)
        async_result = await resolver.resolve_async("Brain", "derives_from", None)

        assert sync_result == async_result
