"""
DependencyGraph - Utilities for dependency analysis in the Weave.

A DependencyGraph represents the causal structure of events.
It enables:
- Checking if events are concurrent (independent)
- Finding valid linear orderings (topological sort)
- Identifying critical paths
- Computing transitive closures
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterator, Set


@dataclass
class DependencyGraph:
    """
    A directed acyclic graph (DAG) of event dependencies.

    Nodes are event IDs, edges represent "depends on" relations.
    If there's an edge A -> B, then A depends on B (B must precede A).

    Properties:
    - Acyclic (invariant maintained on construction)
    - Edges point from dependent to dependency
    """

    # Maps event_id -> set of events it depends on
    _dependencies: dict[str, set[str]] = field(default_factory=dict)

    # Cache for transitive closure
    _transitive_closure: dict[str, set[str]] | None = field(
        default=None, repr=False, compare=False
    )

    def add_node(self, event_id: str, depends_on: set[str] | None = None) -> None:
        """
        Add a node to the dependency graph.

        Args:
            event_id: The event ID to add
            depends_on: Set of event IDs this event depends on

        Raises:
            ValueError: If adding would create a cycle
        """
        deps = depends_on or set()

        # Check for self-dependency
        if event_id in deps:
            raise ValueError(f"Event {event_id} cannot depend on itself")

        # Check that dependencies exist
        for dep in deps:
            if dep not in self._dependencies and dep != event_id:
                # Auto-create missing dependency nodes
                self._dependencies[dep] = set()

        # Check for cycles
        if self._would_create_cycle(event_id, deps):
            raise ValueError(f"Adding {event_id} with deps {deps} would create cycle")

        self._dependencies[event_id] = deps
        self._transitive_closure = None  # Invalidate cache

    def _would_create_cycle(self, event_id: str, new_deps: set[str]) -> bool:
        """Check if adding these dependencies would create a cycle."""
        if event_id not in self._dependencies:
            return False

        # BFS to find if event_id is reachable from any new dependency
        for dep in new_deps:
            if self._is_reachable(dep, event_id):
                return True
        return False

    def _is_reachable(self, from_id: str, to_id: str) -> bool:
        """Check if to_id is reachable from from_id following dependencies."""
        if from_id not in self._dependencies:
            return False

        visited: set[str] = set()
        queue = deque([from_id])

        while queue:
            current = queue.popleft()
            if current == to_id:
                return True
            if current in visited:
                continue
            visited.add(current)

            for dep in self._dependencies.get(current, set()):
                if dep not in visited:
                    queue.append(dep)

        return False

    def are_concurrent(self, event_a: str, event_b: str) -> bool:
        """
        Check if two events are concurrent (independent).

        Two events are concurrent if neither depends on the other,
        directly or transitively.

        Args:
            event_a: First event ID
            event_b: Second event ID

        Returns:
            True if events are concurrent, False if dependent
        """
        if event_a not in self._dependencies or event_b not in self._dependencies:
            return True  # Unknown events are considered concurrent

        # Check if either is reachable from the other
        a_reaches_b = self._is_reachable(event_a, event_b)
        b_reaches_a = self._is_reachable(event_b, event_a)

        return not (a_reaches_b or b_reaches_a)

    def get_dependencies(self, event_id: str) -> set[str]:
        """Get direct dependencies of an event."""
        return self._dependencies.get(event_id, set()).copy()

    def get_all_dependencies(self, event_id: str) -> set[str]:
        """Get transitive closure of dependencies."""
        if self._transitive_closure is None:
            self._compute_transitive_closure()

        assert self._transitive_closure is not None
        return self._transitive_closure.get(event_id, set()).copy()

    def _compute_transitive_closure(self) -> None:
        """Compute transitive closure using Floyd-Warshall-like approach."""
        closure: dict[str, set[str]] = {
            node: deps.copy() for node, deps in self._dependencies.items()
        }

        # Iterate until no changes
        changed = True
        while changed:
            changed = False
            for node in closure:
                current_deps = closure[node].copy()
                for dep in current_deps:
                    transitive = closure.get(dep, set())
                    new_deps = transitive - closure[node]
                    if new_deps:
                        closure[node].update(new_deps)
                        changed = True

        self._transitive_closure = closure

    def topological_sort(self) -> list[str]:
        """
        Return a valid linear ordering (topological sort).

        Uses Kahn's algorithm. Returns ONE valid ordering;
        multiple may exist due to concurrency.

        Returns:
            List of event IDs in valid execution order
        """
        # Compute in-degrees
        in_degree: dict[str, int] = {node: 0 for node in self._dependencies}
        for node, deps in self._dependencies.items():
            for dep in deps:
                # dep is depended upon by node, so dep's "out-degree" increases
                # Actually we need reverse mapping for in-degree
                pass

        # Build reverse mapping (dependents)
        dependents: dict[str, set[str]] = {node: set() for node in self._dependencies}
        for node, deps in self._dependencies.items():
            for dep in deps:
                if dep in dependents:
                    dependents[dep].add(node)

        # In-degree is number of things this node depends on
        in_degree = {node: len(deps) for node, deps in self._dependencies.items()}

        # Start with nodes that have no dependencies
        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        result: list[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            # For each node that depends on current
            for dependent in dependents.get(current, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._dependencies):
            raise ValueError("Graph has a cycle (topological sort failed)")

        return result

    def get_roots(self) -> set[str]:
        """Get events with no dependencies (roots of the DAG)."""
        return {node for node, deps in self._dependencies.items() if len(deps) == 0}

    def get_leaves(self) -> set[str]:
        """Get events that nothing depends on (leaves of the DAG)."""
        # Build reverse mapping
        depended_upon: set[str] = set()
        for deps in self._dependencies.values():
            depended_upon.update(deps)

        return set(self._dependencies.keys()) - depended_upon

    def nodes(self) -> Iterator[str]:
        """Iterate over all nodes."""
        yield from self._dependencies.keys()

    def __len__(self) -> int:
        """Number of nodes in the graph."""
        return len(self._dependencies)

    def __contains__(self, event_id: str) -> bool:
        """Check if event is in the graph."""
        return event_id in self._dependencies
