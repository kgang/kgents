"""
Phase 6: Typed-Hypergraph → Derivation Bridge.

Derivation becomes a layer in the typed-hypergraph. This module provides
hyperedge resolvers that expose derivation relationships as navigable edges.

Three edge types:
- derives_from: Direct ancestry
- shares_principle: Agents that draw on the same principle
- confidence_flows_to: Confidence propagation path (dependents)

Law 6.3 (Hyperedge Consistency):
    |resolve(A, "derives_from")| == |A.derives_from|
    Hyperedge resolution is consistent with the derivation DAG.

See: spec/protocols/derivation-framework.md §6.3
See: spec/protocols/typed-hypergraph.md

Teaching:
    gotcha: shares_principle edges are observer-dependent. Architects and
            analysts see them; developers see only derives_from.
            (Evidence: test_hypergraph_bridge.py::test_observer_dependent)

    gotcha: The resolver should cache results. Invalidate on registry changes.
            (Evidence: test_hypergraph_bridge.py::test_cache_invalidation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .registry import DerivationRegistry
    from protocols.exploration.types import Observer


# =============================================================================
# Hyperedge Types
# =============================================================================


DERIVATION_EDGE_TYPES = frozenset({
    "derives_from",
    "shares_principle",
    "confidence_flows_to",
})


@dataclass(frozen=True)
class ContextNode:
    """
    A node in the typed-hypergraph (simplified for derivation).

    Full implementation in protocols/agentese/contexts/self_context.py.
    This is a minimal version for derivation-specific operations.
    """

    path: str  # AGENTESE path (e.g., "concept.agent.Flux")
    holon: str = ""  # Entity name

    def __hash__(self) -> int:
        return hash(self.path)

    @classmethod
    def for_agent(cls, agent_name: str) -> "ContextNode":
        """Create a context node for an agent."""
        return cls(
            path=f"concept.agent.{agent_name}",
            holon=agent_name,
        )


# =============================================================================
# Observer Protocol
# =============================================================================


@runtime_checkable
class ObserverLike(Protocol):
    """Protocol for observer-like objects."""

    @property
    def archetype(self) -> str:
        """The observer's archetype (developer, architect, etc.)."""
        ...


@dataclass(frozen=True)
class SimpleObserver:
    """Simple observer for testing and standalone use."""

    id: str = "default"
    archetype: str = "developer"
    capabilities: frozenset[str] = frozenset()


# =============================================================================
# Hyperedge Resolver
# =============================================================================


class DerivationHyperedgeResolver:
    """
    Hyperedge resolver for derivation relationships.

    Adds three edge types to the typed-hypergraph:
    - derives_from: Direct ancestry
    - shares_principle: Agents that draw on the same principle
    - confidence_flows_to: Confidence propagation path

    Observer-dependent:
    - developers see: derives_from, confidence_flows_to
    - architects see: all edges
    - analysts see: all edges
    """

    EDGE_TYPES = DERIVATION_EDGE_TYPES

    # Archetypes that can see shares_principle edges
    PRINCIPLE_VISIBLE_ARCHETYPES = frozenset({"architect", "analyst", "researcher"})

    def __init__(self, registry: "DerivationRegistry"):
        self._registry = registry
        self._cache_version = 0
        self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear internal caches. Call on registry changes."""
        self._derives_from_cache: dict[str, list[ContextNode]] = {}
        self._confidence_flows_cache: dict[str, list[ContextNode]] = {}
        self._shares_principle_cache: dict[str, list[ContextNode]] = {}
        self._cache_version += 1

    def invalidate_cache(self) -> None:
        """Public method to invalidate caches."""
        self._clear_cache()

    def resolve(
        self,
        source: str,
        edge_type: str,
        observer: ObserverLike | None = None,
    ) -> list[ContextNode]:
        """
        Resolve derivation hyperedges.

        Args:
            source: Agent name (not full path)
            edge_type: One of derives_from, shares_principle, confidence_flows_to
            observer: The observer (determines visible edges)

        Returns:
            List of destination ContextNodes

        Teaching:
            gotcha: Observer is optional; defaults to developer archetype.
        """
        if edge_type not in self.EDGE_TYPES:
            return []

        derivation = self._registry.get(source)
        if derivation is None:
            return []

        if observer is None:
            observer = SimpleObserver()

        if edge_type == "derives_from":
            return self._resolve_derives_from(source, derivation)

        if edge_type == "confidence_flows_to":
            return self._resolve_confidence_flows_to(source)

        if edge_type == "shares_principle":
            # Observer-dependent: only architects/analysts see this
            if observer.archetype not in self.PRINCIPLE_VISIBLE_ARCHETYPES:
                return []
            return self._resolve_shares_principle(source, derivation)

        return []

    def _resolve_derives_from(
        self,
        source: str,
        derivation: "Derivation",
    ) -> list[ContextNode]:
        """Resolve derives_from edges (direct ancestry)."""
        if source in self._derives_from_cache:
            return self._derives_from_cache[source]

        nodes = [
            ContextNode.for_agent(name)
            for name in derivation.derives_from
        ]
        self._derives_from_cache[source] = nodes
        return nodes

    def _resolve_confidence_flows_to(self, source: str) -> list[ContextNode]:
        """Resolve confidence_flows_to edges (dependents)."""
        if source in self._confidence_flows_cache:
            return self._confidence_flows_cache[source]

        dependents = self._registry.dependents(source)
        nodes = [ContextNode.for_agent(name) for name in dependents]
        self._confidence_flows_cache[source] = nodes
        return nodes

    def _resolve_shares_principle(
        self,
        source: str,
        derivation: "Derivation",
    ) -> list[ContextNode]:
        """Resolve shares_principle edges (agents sharing principles)."""
        if source in self._shares_principle_cache:
            return self._shares_principle_cache[source]

        # Get principles this agent draws on
        source_principles = {d.principle for d in derivation.principle_draws}
        if not source_principles:
            self._shares_principle_cache[source] = []
            return []

        # Find other agents sharing principles
        shared: set[str] = set()
        for other_name in self._registry.list_agents():
            if other_name == source:
                continue

            other = self._registry.get(other_name)
            if other is None:
                continue

            other_principles = {d.principle for d in other.principle_draws}
            if source_principles & other_principles:  # Intersection
                shared.add(other_name)

        nodes = [ContextNode.for_agent(name) for name in sorted(shared)]
        self._shares_principle_cache[source] = nodes
        return nodes

    async def resolve_async(
        self,
        source: str,
        edge_type: str,
        observer: ObserverLike | None = None,
    ) -> list[ContextNode]:
        """Async version for integration with typed-hypergraph."""
        return self.resolve(source, edge_type, observer)

    def available_edges(
        self,
        source: str,
        observer: ObserverLike | None = None,
    ) -> dict[str, int]:
        """
        Get available edges from a node with counts.

        Returns dict mapping edge_type → destination_count.
        """
        if not self._registry.exists(source):
            return {}

        if observer is None:
            observer = SimpleObserver()

        result: dict[str, int] = {}

        for edge_type in self.EDGE_TYPES:
            nodes = self.resolve(source, edge_type, observer)
            if nodes:
                result[edge_type] = len(nodes)

        return result


# =============================================================================
# Registration with Typed-Hypergraph
# =============================================================================


# Global resolver instance (initialized on first use)
_global_resolver: DerivationHyperedgeResolver | None = None


def get_derivation_resolver(registry: "DerivationRegistry") -> DerivationHyperedgeResolver:
    """
    Get or create the global derivation resolver.

    Creates a new resolver if registry has changed.
    """
    global _global_resolver
    if _global_resolver is None or _global_resolver._registry is not registry:
        _global_resolver = DerivationHyperedgeResolver(registry)
    return _global_resolver


def reset_derivation_resolver() -> None:
    """Reset the global resolver (for testing)."""
    global _global_resolver
    _global_resolver = None


def register_derivation_resolvers(
    registry: "DerivationRegistry",
    hypergraph_registry: dict[str, Any] | None = None,
) -> DerivationHyperedgeResolver:
    """
    Wire derivation edges into the typed-hypergraph.

    Args:
        registry: The derivation registry
        hypergraph_registry: Optional hypergraph resolver registry to register with

    Returns:
        The derivation resolver (for direct use or testing)

    Usage:
        # Standalone
        resolver = register_derivation_resolvers(get_registry())

        # With hypergraph
        register_derivation_resolvers(
            get_registry(),
            hyperedge_registry,
        )
    """
    resolver = get_derivation_resolver(registry)

    if hypergraph_registry is not None:
        # Register for concept.agent.* paths
        for edge_type in resolver.EDGE_TYPES:
            pattern = f"concept.agent.*:{edge_type}"
            hypergraph_registry[pattern] = resolver.resolve_async

    return resolver


# =============================================================================
# Convenience Functions
# =============================================================================


def resolve_derivation_edge(
    agent_name: str,
    edge_type: str,
    registry: "DerivationRegistry",
    observer: ObserverLike | None = None,
) -> list[ContextNode]:
    """
    One-shot edge resolution without managing resolver lifecycle.

    Convenience function for simple queries.
    """
    resolver = get_derivation_resolver(registry)
    return resolver.resolve(agent_name, edge_type, observer)


def get_derivation_graph_for_agent(
    agent_name: str,
    registry: "DerivationRegistry",
    max_depth: int = 3,
) -> dict[str, list[str | Any]]:
    """
    Get the local derivation graph around an agent.

    Returns edges reachable within max_depth hops.
    Useful for visualization.

    Args:
        agent_name: Starting agent
        registry: The derivation registry
        max_depth: Maximum traversal depth

    Returns:
        Dict mapping edge descriptions to destination names
    """
    resolver = get_derivation_resolver(registry)
    result: dict[str, list[str]] = {}

    # Use architect observer to see all edges
    architect = SimpleObserver(archetype="architect")

    def explore(name: str, depth: int, prefix: str = "") -> None:
        if depth > max_depth:
            return

        for edge_type in resolver.EDGE_TYPES:
            nodes = resolver.resolve(name, edge_type, architect)
            if nodes:
                key = f"{prefix}{name}.{edge_type}"
                result[key] = [n.holon for n in nodes]

                # Recurse for derives_from only (to avoid explosion)
                if edge_type == "derives_from":
                    for node in nodes:
                        explore(node.holon, depth + 1, f"{prefix}  ")

    explore(agent_name, 0)
    return result


# Import Derivation type for type hints
from .types import Derivation


__all__ = [
    # Edge types
    "DERIVATION_EDGE_TYPES",
    # Types
    "ContextNode",
    "SimpleObserver",
    "ObserverLike",
    # Resolver
    "DerivationHyperedgeResolver",
    # Global management
    "get_derivation_resolver",
    "reset_derivation_resolver",
    "register_derivation_resolvers",
    # Convenience
    "resolve_derivation_edge",
    "get_derivation_graph_for_agent",
]
