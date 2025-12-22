"""
Derivation Registry: The theorem database of agent derivations.

The registry maintains the DAG of agent derivations, tracing every agent
back to bootstrap axioms. It enforces the derivation laws:

1. Monotonicity: Agents can only derive from same or higher tiers
2. Confidence Ceiling: Evidence can't exceed tier ceiling
3. Bootstrap Indefeasibility: Bootstrap agents never decay
4. Acyclicity: The derivation graph is a DAG
5. Propagation: Confidence changes propagate through the DAG

Teaching:
    gotcha: The registry seeds itself with bootstrap agents on construction.
            You don't need to manually register Id, Compose, etc.

    gotcha: register() computes inherited_confidence from ancestors.
            Don't pass inherited_confidence directly to Derivation().

    gotcha: Confidence propagation is recursive but bounded by the DAG.
            Since there are no cycles (Law 4), it always terminates.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Callable

from .types import (
    BOOTSTRAP_PRINCIPLE_DRAWS,
    Derivation,
    DerivationTier,
    PrincipleDraw,
)


class DerivationDAG:
    """
    The derivation graph as a DAG.

    Maintains parent-child relationships and provides topological operations.
    Enforces acyclicity (Law 4) at edge addition time.
    """

    def __init__(self) -> None:
        # child -> parents (derives_from)
        self._parents: dict[str, set[str]] = {}
        # parent -> children (dependents)
        self._children: dict[str, set[str]] = {}

    def add_node(self, name: str) -> None:
        """Add a node to the DAG."""
        if name not in self._parents:
            self._parents[name] = set()
        if name not in self._children:
            self._children[name] = set()

    def add_edges(self, child: str, parents: tuple[str, ...]) -> None:
        """
        Add edges from parents to child (child derives_from parents).

        Raises ValueError if this would create a cycle.
        """
        self.add_node(child)
        for parent in parents:
            self.add_node(parent)

            # Check for cycle: would adding this edge make child reachable from itself?
            if self._would_create_cycle(child, parent):
                raise ValueError(
                    f"Adding edge {parent} -> {child} would create a cycle. "
                    f"Derivations must form a DAG (Law 4: Acyclicity)."
                )

            self._parents[child].add(parent)
            self._children[parent].add(child)

    def _would_create_cycle(self, child: str, new_parent: str) -> bool:
        """Check if adding edge new_parent -> child would create a cycle."""
        # If child can reach new_parent, adding new_parent -> child creates cycle
        visited: set[str] = set()
        stack = [child]

        while stack:
            current = stack.pop()
            if current == new_parent:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(self._children.get(current, set()))

        return False

    def parents(self, name: str) -> frozenset[str]:
        """Get direct parents (derives_from) of a node."""
        return frozenset(self._parents.get(name, set()))

    def dependents(self, name: str) -> frozenset[str]:
        """Get direct children (derived from this) of a node."""
        return frozenset(self._children.get(name, set()))

    def ancestors(self, name: str) -> frozenset[str]:
        """Get all ancestors (transitive closure of derives_from)."""
        result: set[str] = set()
        stack = list(self._parents.get(name, set()))

        while stack:
            current = stack.pop()
            if current not in result:
                result.add(current)
                stack.extend(self._parents.get(current, set()))

        return frozenset(result)

    def descendants(self, name: str) -> frozenset[str]:
        """Get all descendants (transitive closure of dependents)."""
        result: set[str] = set()
        stack = list(self._children.get(name, set()))

        while stack:
            current = stack.pop()
            if current not in result:
                result.add(current)
                stack.extend(self._children.get(current, set()))

        return frozenset(result)


class DerivationRegistry:
    """
    Global registry of agent derivations.

    Think of this as the theorem database—every agent has a derivation
    that traces back to bootstrap axioms. The registry:

    1. Seeds with bootstrap agents (confidence = 1.0)
    2. Computes inherited confidence when registering derived agents
    3. Propagates confidence changes through the DAG
    4. Enforces the five derivation laws

    Usage:
        registry = DerivationRegistry()

        # Register a derived agent
        derivation = registry.register(
            agent_name="Flux",
            derives_from=("Fix", "Compose"),
            principle_draws=(...),
            tier=DerivationTier.FUNCTOR,
        )

        # Update with evidence
        registry.update_evidence("Flux", ashc_score=0.88, usage_count=5000)

        # Query
        registry.get("Flux").total_confidence  # ~0.95
    """

    def __init__(self) -> None:
        self._derivations: dict[str, Derivation] = {}
        self._dag: DerivationDAG = DerivationDAG()
        self._usage_counts: dict[str, int] = {}
        self._seed_bootstrap()

    def _seed_bootstrap(self) -> None:
        """
        Seed registry with bootstrap axioms (confidence = 1.0).

        Bootstrap agents don't derive from anything—they ARE the axioms.
        This is Law 3: Bootstrap Indefeasibility.
        """
        bootstrap_agents = ("Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix")

        for name in bootstrap_agents:
            derivation = Derivation(
                agent_name=name,
                tier=DerivationTier.BOOTSTRAP,
                derives_from=(),
                principle_draws=BOOTSTRAP_PRINCIPLE_DRAWS.get(name, ()),
                inherited_confidence=1.0,
                empirical_confidence=1.0,
                stigmergic_confidence=1.0,
            )
            self._derivations[name] = derivation
            self._dag.add_node(name)
            self._usage_counts[name] = 0

    def register(
        self,
        agent_name: str,
        derives_from: tuple[str, ...],
        principle_draws: tuple[PrincipleDraw, ...],
        tier: DerivationTier,
    ) -> Derivation:
        """
        Register a new agent derivation.

        Computes inherited confidence from the derivation chain.
        Enforces derivation laws at registration time.

        Args:
            agent_name: Unique name for this agent
            derives_from: Names of agents this derives from (must exist)
            principle_draws: Evidence of principle instantiation
            tier: The derivation tier (determines confidence ceiling)

        Returns:
            The created Derivation

        Raises:
            ValueError: If registration would violate derivation laws
        """
        # Law 1: Monotonicity - can only derive from same or higher tiers
        self._validate_tier_monotonicity(agent_name, derives_from, tier)

        # Law 4: Acyclicity - enforced by DAG.add_edges
        self._dag.add_edges(agent_name, derives_from)

        # Compute inherited confidence from ancestors
        inherited = self._compute_inherited_confidence(derives_from)

        derivation = Derivation(
            agent_name=agent_name,
            tier=tier,
            derives_from=derives_from,
            principle_draws=principle_draws,
            inherited_confidence=inherited,
            empirical_confidence=0.0,  # Starts at zero, earned through evidence
            stigmergic_confidence=0.0,  # Starts at zero, earned through usage
        )

        self._derivations[agent_name] = derivation
        self._usage_counts[agent_name] = 0

        return derivation

    def _validate_tier_monotonicity(
        self,
        agent_name: str,
        derives_from: tuple[str, ...],
        tier: DerivationTier,
    ) -> None:
        """
        Validate Law 1: Monotonicity.

        Derived agents must be at the same or higher tier (less foundational)
        than their parents. A FUNCTOR can derive from BOOTSTRAP, APP can derive
        from JEWEL, but you can't derive a BOOTSTRAP from an APP.

        The spec says: tier(D) > tier(parent(D)) where BOOTSTRAP < FUNCTOR < ... < APP
        So: tier must be >= parent.tier (can be equal or greater rank)
        """
        for parent_name in derives_from:
            if parent_name not in self._derivations:
                raise ValueError(
                    f"Cannot derive '{agent_name}' from unknown agent '{parent_name}'. "
                    f"Parent must be registered first."
                )

            parent = self._derivations[parent_name]
            # tier.rank >= parent.tier.rank (derived tier must be same or higher number)
            # Remember: higher rank = less foundational
            if tier < parent.tier:
                raise ValueError(
                    f"Law 1 (Monotonicity) violated: '{agent_name}' (tier={tier.value}) "
                    f"cannot derive from '{parent_name}' (tier={parent.tier.value}). "
                    f"Derived agents must be at the same or higher tier than their parents."
                )

    def _compute_inherited_confidence(
        self,
        derives_from: tuple[str, ...],
    ) -> float:
        """
        Compute inherited confidence from derivation chain.

        Formula: product of ancestor confidences, with a floor of 0.3.
        The floor prevents vanishing confidence in deep derivation chains.

        If derives_from is empty (bootstrap), returns 1.0.
        If an ancestor is unknown, treats it as 0.5 (uncertain).
        """
        if not derives_from:
            return 1.0

        confidences = [
            self._derivations[name].total_confidence
            for name in derives_from
            if name in self._derivations
        ]

        if not confidences:
            return 0.5  # Unknown ancestors

        # Product with floor
        product = 1.0
        for c in confidences:
            product *= c

        return max(0.3, product)

    def get(self, agent_name: str) -> Derivation | None:
        """Get derivation for an agent, or None if not found."""
        return self._derivations.get(agent_name)

    def exists(self, agent_name: str) -> bool:
        """Check if an agent has a derivation."""
        return agent_name in self._derivations

    def list_agents(self, tier: DerivationTier | None = None) -> tuple[str, ...]:
        """
        List all registered agents, optionally filtered by tier.
        """
        if tier is None:
            return tuple(sorted(self._derivations.keys()))

        return tuple(
            name
            for name, d in sorted(self._derivations.items())
            if d.tier == tier
        )

    def get_usage_count(self, agent_name: str) -> int:
        """Get usage count for an agent."""
        return self._usage_counts.get(agent_name, 0)

    def update_evidence(
        self,
        agent_name: str,
        ashc_score: float | None = None,
        usage_count: int | None = None,
    ) -> Derivation:
        """
        Update derivation with new evidence.

        Propagates confidence changes to all dependents (Law 5).

        Args:
            agent_name: The agent to update
            ashc_score: New empirical confidence from ASHC (0.0-1.0)
            usage_count: New usage count for stigmergic confidence

        Returns:
            Updated derivation

        Raises:
            KeyError: If agent not found
            ValueError: If trying to update bootstrap agent
        """
        if agent_name not in self._derivations:
            raise KeyError(f"Agent '{agent_name}' not found in registry")

        derivation = self._derivations[agent_name]

        # Law 3: Bootstrap Indefeasibility
        if derivation.is_bootstrap:
            raise ValueError(
                f"Law 3 (Bootstrap Indefeasibility) violated: "
                f"Cannot update evidence for bootstrap agent '{agent_name}'. "
                f"Bootstrap agents have fixed confidence = 1.0."
            )

        # Update empirical confidence from ASHC
        if ashc_score is not None:
            derivation = replace(derivation, empirical_confidence=ashc_score)

        # Update stigmergic confidence from usage
        if usage_count is not None:
            self._usage_counts[agent_name] = usage_count
            # Logarithmic growth: 100 uses -> 0.5, 1000 uses -> 0.75, 10000 -> 1.0
            stigmergic = min(0.95, 0.25 * math.log10(max(1, usage_count)))
            derivation = replace(derivation, stigmergic_confidence=stigmergic)

        self._derivations[agent_name] = derivation

        # Law 5: Propagate confidence changes to dependents
        self._propagate_confidence(agent_name)

        return derivation

    def _propagate_confidence(self, source: str) -> None:
        """
        Propagate confidence changes through the DAG.

        When an agent's confidence changes, all its dependents need to
        recompute their inherited confidence. This is recursive but
        bounded by the DAG structure (no cycles = always terminates).
        """
        for dependent in self._dag.dependents(source):
            dep_derivation = self._derivations[dependent]

            # Recompute inherited confidence from all parents
            new_inherited = self._compute_inherited_confidence(dep_derivation.derives_from)
            updated = replace(dep_derivation, inherited_confidence=new_inherited)
            self._derivations[dependent] = updated

            # Recursive propagation to dependents of dependent
            self._propagate_confidence(dependent)

    def increment_usage(self, agent_name: str) -> int:
        """
        Increment usage count for an agent.

        Convenience method for Witness integration—each mark increments usage.
        Returns the new count.
        """
        if agent_name not in self._usage_counts:
            self._usage_counts[agent_name] = 0

        self._usage_counts[agent_name] += 1
        new_count = self._usage_counts[agent_name]

        # Update stigmergic confidence periodically (not every increment)
        if new_count % 10 == 0 and agent_name in self._derivations:
            derivation = self._derivations[agent_name]
            if not derivation.is_bootstrap:
                stigmergic = min(0.95, 0.25 * math.log10(max(1, new_count)))
                self._derivations[agent_name] = replace(
                    derivation, stigmergic_confidence=stigmergic
                )
                self._propagate_confidence(agent_name)

        return new_count

    def decay_all(self, days_elapsed: float) -> int:
        """
        Apply time-based decay to all non-categorical evidence.

        Returns the count of derivations that were decayed.
        Bootstrap agents are skipped (Law 3).
        """
        decayed_count = 0

        for name, derivation in self._derivations.items():
            if derivation.is_bootstrap:
                continue  # Law 3: Bootstrap Indefeasibility

            decayed = derivation.decay_evidence(days_elapsed)
            if decayed != derivation:
                self._derivations[name] = decayed
                decayed_count += 1

        return decayed_count

    def ancestors(self, agent_name: str) -> frozenset[str]:
        """Get all ancestors of an agent (full derivation chain)."""
        return self._dag.ancestors(agent_name)

    def dependents(self, agent_name: str) -> frozenset[str]:
        """Get all agents that derive from this one (directly or transitively)."""
        return self._dag.descendants(agent_name)

    def __len__(self) -> int:
        """Number of registered derivations."""
        return len(self._derivations)

    def __contains__(self, agent_name: str) -> bool:
        """Check if agent has a derivation."""
        return agent_name in self._derivations


# --- Global registry instance ---
# Following the pattern from AGENTESE registry

_global_registry: DerivationRegistry | None = None


def get_registry() -> DerivationRegistry:
    """
    Get the global derivation registry.

    Creates one if it doesn't exist. Use this for the shared registry.
    Create a new DerivationRegistry() for isolated testing.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DerivationRegistry()
    return _global_registry


def reset_registry() -> None:
    """
    Reset the global registry.

    For testing only. Production code should not call this.
    """
    global _global_registry
    _global_registry = None


__all__ = [
    "DerivationDAG",
    "DerivationRegistry",
    "get_registry",
    "reset_registry",
]
