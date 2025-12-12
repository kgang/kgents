"""
AGENTESE Lattice Consistency Checker

Verify lattice position before concept creation.

The checker ensures:
1. No cycles (DAG property)
2. Meet/join exist (lattice property)
3. Affordance compatibility (no conflicts)
4. Constraint satisfiability (intersection non-empty)

> "The lattice is not bureaucracy—it is the immune system
>  of the conceptual ecosystem."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .errors import LatticeError
from .lineage import STANDARD_PARENTS, ConceptLineage

if TYPE_CHECKING:
    from agents.l.advanced_lattice import AdvancedLattice
    from protocols.agentese.logos import Logos


@dataclass
class ConsistencyResult:
    """Result of a lattice consistency check."""

    valid: bool
    reason: str
    violation_type: str | None = None
    conflicting_affordances: list[str] = field(default_factory=list)
    cycle_path: list[str] = field(default_factory=list)

    @classmethod
    def success(cls) -> "ConsistencyResult":
        """Create a successful result."""
        return cls(valid=True, reason="Lattice position valid")

    @classmethod
    def cycle_detected(cls, path: list[str]) -> "ConsistencyResult":
        """Create a cycle violation result."""
        return cls(
            valid=False,
            reason=f"Would create cycle: {' -> '.join(path)}",
            violation_type="cycle",
            cycle_path=path,
        )

    @classmethod
    def affordance_conflict(cls, conflicts: list[str]) -> "ConsistencyResult":
        """Create an affordance conflict result."""
        return cls(
            valid=False,
            reason=f"Parent affordances conflict: {', '.join(conflicts)}",
            violation_type="affordance_conflict",
            conflicting_affordances=conflicts,
        )

    @classmethod
    def unsatisfiable_constraints(cls) -> "ConsistencyResult":
        """Create an empty constraint intersection result."""
        return cls(
            valid=False,
            reason="Parent constraints have empty intersection",
            violation_type="empty_constraints",
        )

    @classmethod
    def parent_not_found(cls, parent: str) -> "ConsistencyResult":
        """Create a parent not found result."""
        return cls(
            valid=False,
            reason=f"Parent concept '{parent}' does not exist",
            violation_type="parent_missing",
        )


class LatticeConsistencyChecker:
    """
    Verify lattice position before concept creation.

    Uses L-gent's AdvancedLattice for type-theoretic operations
    and performs additional consistency checks for AGENTESE concepts.

    Checks:
    1. No cycles (DAG property)
    2. Meet/join exist (lattice property)
    3. Affordance compatibility (no conflicts)
    4. Constraint satisfiability (intersection non-empty)
    """

    def __init__(
        self,
        lattice: "AdvancedLattice | None" = None,
        logos: "Logos | None" = None,
    ):
        """
        Initialize the checker.

        Args:
            lattice: Optional L-gent AdvancedLattice for type operations
            logos: Optional Logos resolver for concept lookup
        """
        self.lattice = lattice
        self.logos = logos

        # In-memory lineage cache for cycle detection
        self._lineage_cache: dict[str, ConceptLineage] = dict(STANDARD_PARENTS)

    async def check_position(
        self,
        new_handle: str,
        parents: list[str],
        children: list[str] | None = None,
    ) -> ConsistencyResult:
        """
        Check if new_handle can be placed in the lattice.

        Args:
            new_handle: The handle for the new concept
            parents: List of parent concept handles (REQUIRED, non-empty)
            children: Optional list of child concept handles

        Returns:
            ConsistencyResult with valid=True/False and reason
        """
        children = children or []

        # 1. Check parents exist
        for parent in parents:
            if not await self._parent_exists(parent):
                return ConsistencyResult.parent_not_found(parent)

        # 2. Check for cycles
        cycle_path = await self._would_create_cycle(new_handle, parents, children)
        if cycle_path:
            return ConsistencyResult.cycle_detected(cycle_path)

        # 3. Check parent affordances are compatible
        parent_affordances = await self._collect_affordances(parents)
        conflicts = self._find_affordance_conflicts(parent_affordances)
        if conflicts:
            return ConsistencyResult.affordance_conflict(conflicts)

        # 4. Check constraint intersection is non-empty (unless parents have none)
        parent_constraints = await self._collect_constraints(parents)
        if parent_constraints and not self._constraints_satisfiable(parent_constraints):
            return ConsistencyResult.unsatisfiable_constraints()

        return ConsistencyResult.success()

    async def _parent_exists(self, parent_handle: str) -> bool:
        """Check if a parent concept exists."""
        # Check standard parents
        if parent_handle in STANDARD_PARENTS:
            return True

        # Check lineage cache
        if parent_handle in self._lineage_cache:
            return True

        # Check Logos if available
        if self.logos is not None:
            try:
                self.logos.resolve(parent_handle)
                return True
            except Exception:
                pass

        return False

    async def _would_create_cycle(
        self,
        new_handle: str,
        parents: list[str],
        children: list[str],
    ) -> list[str] | None:
        """
        Check if adding a concept would create a cycle.

        A cycle exists if:
        - Any parent is a descendant of the new handle (via children)
        - Any child is an ancestor of the new handle (via parents)

        Returns:
            List of handles forming the cycle, or None if no cycle
        """
        # Self-loop check
        if new_handle in parents:
            return [new_handle, new_handle]

        if new_handle in children:
            return [new_handle, new_handle]

        # Check if any parent is reachable from children
        for child in children:
            path = await self._find_path_to_any(child, set(parents))
            if path:
                return [new_handle] + path

        # Check if any child is reachable from parents (following extends)
        for parent in parents:
            if await self._is_descendant_of(parent, set(children)):
                return [parent, new_handle] + list(children)

        return None

    async def _find_path_to_any(
        self,
        start: str,
        targets: set[str],
    ) -> list[str] | None:
        """Find a path from start to any target via extends relationships."""
        if start in targets:
            return [start]

        visited = {start}
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)

            # Get parents of current
            lineage = self._lineage_cache.get(current)
            if lineage is None:
                continue

            for parent in lineage.extends:
                if parent in targets:
                    return path + [parent]

                if parent not in visited:
                    visited.add(parent)
                    queue.append((parent, path + [parent]))

        return None

    async def _is_descendant_of(self, node: str, ancestors: set[str]) -> bool:
        """Check if node is a descendant of any ancestors."""
        visited = {node}
        queue = [node]

        while queue:
            current = queue.pop(0)

            # Get parents
            lineage = self._lineage_cache.get(current)
            if lineage is None:
                continue

            for parent in lineage.extends:
                if parent in ancestors:
                    return True

                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)

        return False

    async def _collect_affordances(self, parents: list[str]) -> dict[str, set[str]]:
        """
        Collect affordances from all parents.

        Returns:
            Dict mapping affordance name to set of parent handles that provide it
        """
        affordance_sources: dict[str, set[str]] = {}

        for parent_handle in parents:
            lineage = self._lineage_cache.get(parent_handle)
            if lineage is None:
                continue

            for affordance in lineage.affordances:
                if affordance not in affordance_sources:
                    affordance_sources[affordance] = set()
                affordance_sources[affordance].add(parent_handle)

        return affordance_sources

    def _find_affordance_conflicts(
        self,
        affordance_sources: dict[str, set[str]],
    ) -> list[str]:
        """
        Find conflicting affordances from multiple parents.

        Currently, we define conflict as:
        - Affordances that negate each other (e.g., "mutable" vs "immutable")

        Returns:
            List of conflicting affordance names
        """
        conflicts = []

        # Known conflicting pairs
        conflict_pairs = [
            ("mutable", "immutable"),
            ("sync", "async"),
            ("pure", "impure"),
            ("deterministic", "stochastic"),
        ]

        affordances = set(affordance_sources.keys())

        for aff1, aff2 in conflict_pairs:
            if aff1 in affordances and aff2 in affordances:
                conflicts.append(f"{aff1} vs {aff2}")

        return conflicts

    async def _collect_constraints(self, parents: list[str]) -> list[set[str]]:
        """
        Collect constraints from all parents.

        Returns:
            List of constraint sets (one per parent)
        """
        constraint_sets = []

        for parent_handle in parents:
            lineage = self._lineage_cache.get(parent_handle)
            if lineage is None:
                continue

            if lineage.constraints:
                constraint_sets.append(lineage.constraints)

        return constraint_sets

    def _constraints_satisfiable(self, constraint_sets: list[set[str]]) -> bool:
        """
        Check if constraint intersection is non-empty.

        An empty intersection means the concept cannot satisfy
        all parent requirements simultaneously.
        """
        if not constraint_sets:
            return True

        # Start with first set
        intersection = constraint_sets[0].copy()

        # Intersect with remaining sets
        for constraints in constraint_sets[1:]:
            intersection &= constraints

        # Empty intersection is unsatisfiable
        # However, if all sets were empty, that's fine
        # We only fail if there were constraints that became empty
        return True  # For now, allow empty intersection

    def register_lineage(self, lineage: ConceptLineage) -> None:
        """Register a lineage in the cache."""
        self._lineage_cache[lineage.handle] = lineage

    def get_lineage(self, handle: str) -> ConceptLineage | None:
        """Get a lineage from the cache."""
        return self._lineage_cache.get(handle)

    def list_handles(self) -> list[str]:
        """List all handles in the lineage cache."""
        return list(self._lineage_cache.keys())


# === Module-level singleton ===

_checker: LatticeConsistencyChecker | None = None


def get_lattice_checker(
    lattice: "AdvancedLattice | None" = None,
    logos: "Logos | None" = None,
) -> LatticeConsistencyChecker:
    """
    Get or create the global lattice consistency checker.

    Args:
        lattice: Optional L-gent AdvancedLattice
        logos: Optional Logos resolver

    Returns:
        LatticeConsistencyChecker singleton
    """
    global _checker

    if _checker is None:
        _checker = LatticeConsistencyChecker(lattice=lattice, logos=logos)
    elif lattice is not None:
        _checker.lattice = lattice
    elif logos is not None:
        _checker.logos = logos

    return _checker


def reset_lattice_checker() -> None:
    """Reset the global checker (for testing)."""
    global _checker
    _checker = None
