"""
L-gent Lattice: Type Compatibility & Composition Planning

Phase 4 implementation: Type lattice operations for compositional verification.

The lattice is L-gent's type theory engine. It answers:
"Can these two agents compose?"

This enables static composition verification—proving compatibility
before any code runs. The mathematical backbone of composability.
"""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .registry import Registry


class TypeKind(Enum):
    """Classification of types in the lattice."""

    PRIMITIVE = "primitive"  # str, int, float, bool, None
    CONTAINER = "container"  # list, dict, set, tuple
    RECORD = "record"  # dataclass, TypedDict
    UNION = "union"  # A | B
    LITERAL = "literal"  # Literal["a", "b"]
    GENERIC = "generic"  # Generic[T]
    CONTRACT = "contract"  # Named interface with invariants
    ANY = "any"  # Top type
    NEVER = "never"  # Bottom type


@dataclass
class TypeNode:
    """A type in the lattice."""

    id: str  # Unique identifier
    kind: TypeKind
    name: str  # Human-readable name

    # For generics
    parameters: list[str] = field(default_factory=list)  # Type parameter names

    # For containers
    element_type: str | None = None  # e.g., list[X] → X

    # For records
    fields: dict[str, str] = field(default_factory=dict)  # field_name → type_id

    # For unions
    members: list[str] = field(default_factory=list)  # Union member type IDs

    # For contracts
    invariants: list[str] = field(default_factory=list)  # Behavioral guarantees

    # Metadata
    defined_at: str | None = None  # Where this type is defined

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "kind": self.kind.value,
            "name": self.name,
            "parameters": self.parameters,
            "element_type": self.element_type,
            "fields": self.fields,
            "members": self.members,
            "invariants": self.invariants,
            "defined_at": self.defined_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TypeNode":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            kind=TypeKind(data["kind"]),
            name=data["name"],
            parameters=data.get("parameters", []),
            element_type=data.get("element_type"),
            fields=data.get("fields", {}),
            members=data.get("members", []),
            invariants=data.get("invariants", []),
            defined_at=data.get("defined_at"),
        )


@dataclass
class SubtypeEdge:
    """A subtyping relationship in the lattice."""

    subtype_id: str  # The more specific type
    supertype_id: str  # The more general type
    reason: str  # Why this relationship holds
    covariant_positions: list[str] = field(default_factory=list)
    contravariant_positions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subtype_id": self.subtype_id,
            "supertype_id": self.supertype_id,
            "reason": self.reason,
            "covariant_positions": self.covariant_positions,
            "contravariant_positions": self.contravariant_positions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SubtypeEdge":
        """Create from dictionary."""
        return cls(
            subtype_id=data["subtype_id"],
            supertype_id=data["supertype_id"],
            reason=data["reason"],
            covariant_positions=data.get("covariant_positions", []),
            contravariant_positions=data.get("contravariant_positions", []),
        )


@dataclass
class CompositionResult:
    """Result of checking if two agents can compose."""

    compatible: bool
    reason: str
    output_type: str | None = None
    input_type: str | None = None
    requires_adapter: str | None = None
    suggested_fix: str | None = None


@dataclass
class CompositionStage:
    """One stage in a pipeline verification."""

    from_id: str
    to_id: str
    result: CompositionResult


@dataclass
class PipelineVerification:
    """Result of verifying a complete pipeline."""

    valid: bool
    stages: list[CompositionStage]


@dataclass
class CompositionSuggestion:
    """A suggested composition achieving a goal."""

    artifacts: list[str]
    input_type: str
    output_type: str
    length: int


class TypeLattice:
    """
    Layer 3: Type compatibility and composition planning.

    The lattice is a bounded meet-semilattice over types that enables:
    1. Subtype checking (is_subtype)
    2. Meet/join operations (greatest lower bound / least upper bound)
    3. Composition verification (can agents compose?)
    4. Pipeline planning (find paths between types)
    """

    def __init__(self, registry: Registry):
        self.types: dict[str, TypeNode] = {}
        self.edges: list[SubtypeEdge] = []
        self.registry = registry

        # Initialize with built-in types
        self._init_builtin_types()

    def _init_builtin_types(self) -> None:
        """Initialize built-in types (Any, Never, primitives)."""
        # Top type
        self.types["Any"] = TypeNode(
            id="Any", kind=TypeKind.ANY, name="Any", defined_at="builtin"
        )

        # Bottom type
        self.types["Never"] = TypeNode(
            id="Never", kind=TypeKind.NEVER, name="Never", defined_at="builtin"
        )

        # Common primitives
        for prim in ["str", "int", "float", "bool", "None"]:
            self.types[prim] = TypeNode(
                id=prim, kind=TypeKind.PRIMITIVE, name=prim, defined_at="builtin"
            )
            # All primitives are subtypes of Any
            self.edges.append(
                SubtypeEdge(
                    subtype_id=prim,
                    supertype_id="Any",
                    reason="primitive subtype of Any",
                )
            )

    # ─────────────────────────────────────────────────────────────
    # Core Operations
    # ─────────────────────────────────────────────────────────────

    def is_subtype(self, sub: str, super_: str) -> bool:
        """
        Check if sub ≤ super in the lattice.

        Rules:
        1. Reflexivity: A ≤ A
        2. Transitivity: If A ≤ B and B ≤ C then A ≤ C
        3. Any is top: A ≤ Any for all A
        4. Never is bottom: Never ≤ A for all A
        5. Structural subtyping for records
        6. Covariance/contravariance for generics
        """
        if sub == super_:
            return True  # Reflexivity

        if super_ == "Any":
            return True  # Any is top

        if sub == "Never":
            return True  # Never is bottom

        # Check direct edge
        if any(e.subtype_id == sub and e.supertype_id == super_ for e in self.edges):
            return True

        # Transitivity via BFS
        return self._reachable(sub, super_)

    def _reachable(self, start: str, target: str) -> bool:
        """Check if target is reachable from start via BFS on edges."""
        if start == target:
            return True

        visited = {start}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            # Find outgoing edges (current is subtype)
            for edge in self.edges:
                if edge.subtype_id == current:
                    next_type = edge.supertype_id
                    if next_type == target:
                        return True
                    if next_type not in visited:
                        visited.add(next_type)
                        queue.append(next_type)

        return False

    def _all_subtypes(self, type_id: str) -> set[str]:
        """Find all subtypes of a given type."""
        subtypes = {type_id}
        queue = deque([type_id])
        visited = {type_id}

        while queue:
            current = queue.popleft()

            # Find incoming edges (current is supertype)
            for edge in self.edges:
                if edge.supertype_id == current and edge.subtype_id not in visited:
                    visited.add(edge.subtype_id)
                    subtypes.add(edge.subtype_id)
                    queue.append(edge.subtype_id)

        return subtypes

    def _all_supertypes(self, type_id: str) -> set[str]:
        """Find all supertypes of a given type."""
        supertypes = {type_id}
        queue = deque([type_id])
        visited = {type_id}

        while queue:
            current = queue.popleft()

            # Find outgoing edges (current is subtype)
            for edge in self.edges:
                if edge.subtype_id == current and edge.supertype_id not in visited:
                    visited.add(edge.supertype_id)
                    supertypes.add(edge.supertype_id)
                    queue.append(edge.supertype_id)

        return supertypes

    def meet(self, type_a: str, type_b: str) -> str:
        """
        Compute the meet (greatest lower bound) of two types.

        meet(A, B) = largest type C such that C ≤ A and C ≤ B
        """
        if self.is_subtype(type_a, type_b):
            return type_a
        if self.is_subtype(type_b, type_a):
            return type_b

        # Find common subtypes and return the greatest
        subtypes_a = self._all_subtypes(type_a)
        subtypes_b = self._all_subtypes(type_b)
        common = subtypes_a & subtypes_b

        if not common:
            return "Never"  # No common subtype

        # Return the greatest (most general) common subtype
        # A type is greatest if it's a supertype of all others in common
        for candidate in common:
            if all(
                self.is_subtype(other, candidate) or candidate == other
                for other in common
            ):
                return candidate

        return "Never"

    def join(self, type_a: str, type_b: str) -> str:
        """
        Compute the join (least upper bound) of two types.

        join(A, B) = smallest type C such that A ≤ C and B ≤ C
        """
        if self.is_subtype(type_a, type_b):
            return type_b
        if self.is_subtype(type_b, type_a):
            return type_a

        # Find common supertypes and return the least
        supertypes_a = self._all_supertypes(type_a)
        supertypes_b = self._all_supertypes(type_b)
        common = supertypes_a & supertypes_b

        if not common:
            return "Any"  # No common supertype except Any

        # Return the least (most specific) common supertype
        # A type is least if it's a subtype of all others in common
        for candidate in common:
            if all(
                self.is_subtype(candidate, other) or candidate == other
                for other in common
            ):
                return candidate

        return "Any"

    # ─────────────────────────────────────────────────────────────
    # Type Registration
    # ─────────────────────────────────────────────────────────────

    def register_type(self, node: TypeNode) -> None:
        """Register a new type in the lattice."""
        self.types[node.id] = node

        # Auto-create edges to Any
        if node.kind != TypeKind.ANY and node.id != "Any":
            self.edges.append(
                SubtypeEdge(
                    subtype_id=node.id, supertype_id="Any", reason="all types ≤ Any"
                )
            )

        # Auto-create edges from Never
        if node.kind != TypeKind.NEVER and node.id != "Never":
            self.edges.append(
                SubtypeEdge(
                    subtype_id="Never", supertype_id=node.id, reason="Never ≤ all types"
                )
            )

    def add_subtype_edge(self, edge: SubtypeEdge) -> None:
        """Add a subtype relationship."""
        # Check if both types exist
        if edge.subtype_id not in self.types:
            raise ValueError(f"Subtype {edge.subtype_id} not registered")
        if edge.supertype_id not in self.types:
            raise ValueError(f"Supertype {edge.supertype_id} not registered")

        # Check for cycles (would violate antisymmetry)
        if self._would_create_cycle(edge):
            raise ValueError(
                f"Adding edge {edge.subtype_id} ≤ {edge.supertype_id} would create cycle"
            )

        self.edges.append(edge)

    def _would_create_cycle(self, new_edge: SubtypeEdge) -> bool:
        """Check if adding an edge would create a cycle."""
        # A cycle would mean: new_edge.supertype ≤ new_edge.subtype
        # which violates antisymmetry unless they're equal
        if new_edge.subtype_id == new_edge.supertype_id:
            return False  # Reflexive edge is fine

        return self._reachable(new_edge.supertype_id, new_edge.subtype_id)

    # ─────────────────────────────────────────────────────────────
    # Composition Verification
    # ─────────────────────────────────────────────────────────────

    async def can_compose(self, first_id: str, second_id: str) -> CompositionResult:
        """
        Check if two agents can compose: first >> second.

        Returns detailed result explaining why or why not.
        """
        first = await self.registry.get(first_id)
        second = await self.registry.get(second_id)

        if not first or not second:
            return CompositionResult(
                compatible=False, reason="One or both artifacts not found"
            )

        # Check type compatibility
        output_type = first.output_type
        input_type = second.input_type

        if not output_type or not input_type:
            return CompositionResult(
                compatible=False, reason="Missing type information"
            )

        if self.is_subtype(output_type, input_type):
            return CompositionResult(
                compatible=True,
                reason=f"Output type {output_type} is subtype of input type {input_type}",
                output_type=output_type,
                input_type=input_type,
            )
        else:
            # Check if there's a path via adapter
            adapter = await self._find_adapter(output_type, input_type)
            if adapter:
                return CompositionResult(
                    compatible=True,
                    reason=f"Compatible via adapter: {adapter.id}",
                    requires_adapter=adapter.id,
                )

            return CompositionResult(
                compatible=False,
                reason=f"Type mismatch: {output_type} is not subtype of {input_type}",
                output_type=output_type,
                input_type=input_type,
                suggested_fix=self._suggest_fix(output_type, input_type),
            )

    async def verify_pipeline(self, artifact_ids: list[str]) -> PipelineVerification:
        """
        Verify that a sequence of agents forms a valid pipeline.
        """
        if len(artifact_ids) < 2:
            return PipelineVerification(valid=True, stages=[])

        stages = []
        all_valid = True

        for i in range(len(artifact_ids) - 1):
            result = await self.can_compose(artifact_ids[i], artifact_ids[i + 1])
            stages.append(
                CompositionStage(
                    from_id=artifact_ids[i], to_id=artifact_ids[i + 1], result=result
                )
            )
            if not result.compatible:
                all_valid = False

        return PipelineVerification(valid=all_valid, stages=stages)

    async def _find_adapter(self, source_type: str, target_type: str) -> Any:
        """Find an agent that adapts source_type to target_type."""
        # Query registry for agents with matching input/output
        results = await self.registry.find(query="adapter")

        for result in results:
            entry = result.entry
            if (
                entry.input_type == source_type
                and entry.output_type
                and self.is_subtype(entry.output_type, target_type)
            ):
                return entry

        return None

    def _suggest_fix(self, output_type: str, input_type: str) -> str:
        """Suggest how to fix a type mismatch."""
        # Find common supertype
        common = self.join(output_type, input_type)

        if common != "Any":
            return f"Consider converting {output_type} to {common} which is compatible with {input_type}"

        # Check if there's a known adapter pattern
        if output_type == "str" and input_type in ["int", "float"]:
            return "Use a parsing adapter to convert string to numeric type"

        if output_type in ["int", "float"] and input_type == "str":
            return "Use a string formatting adapter"

        return f"No direct path from {output_type} to {input_type}. Consider creating an adapter agent."

    # ─────────────────────────────────────────────────────────────
    # Composition Planning
    # ─────────────────────────────────────────────────────────────

    async def find_path(
        self, source_type: str, target_type: str, max_length: int = 5
    ) -> list[list[str]] | None:
        """
        Find all artifact paths that transform source_type to target_type.

        Uses BFS over the agent graph, respecting type compatibility.
        """
        if self.is_subtype(source_type, target_type):
            return [[]]  # Direct compatibility, no agents needed

        paths = []
        queue: list[tuple[str, list[str]]] = [(source_type, [])]
        visited = {source_type}

        while queue:
            current_type, path = queue.pop(0)

            if len(path) >= max_length:
                continue

            # Find all agents that accept current_type
            candidates = await self._agents_accepting(current_type)

            for agent in candidates:
                new_path = path + [agent.id]
                output = agent.output_type

                if not output:
                    continue

                # Check if we've reached target
                if self.is_subtype(output, target_type):
                    paths.append(new_path)
                    continue

                # Continue search if not visited
                if output not in visited:
                    visited.add(output)
                    queue.append((output, new_path))

        # Sort by path length
        return sorted(paths, key=len) if paths else None

    async def suggest_composition(
        self, available: list[str], goal_input: str, goal_output: str
    ) -> list[CompositionSuggestion]:
        """
        Suggest how to compose available agents to achieve a goal.

        Given: A set of artifacts
        Goal: Transform goal_input to goal_output
        Output: Ranked composition suggestions
        """
        suggestions = []

        # Try all permutations up to length 4
        for length in range(1, min(5, len(available) + 1)):
            for perm in itertools.permutations(available, length):
                # Check if first accepts goal_input
                first = await self.registry.get(perm[0])
                if not first or not first.input_type:
                    continue
                if not self.is_subtype(goal_input, first.input_type):
                    continue

                # Check if last produces goal_output
                last = await self.registry.get(perm[-1])
                if not last or not last.output_type:
                    continue
                if not self.is_subtype(last.output_type, goal_output):
                    continue

                # Verify internal composition
                verification = await self.verify_pipeline(list(perm))
                if verification.valid:
                    suggestions.append(
                        CompositionSuggestion(
                            artifacts=list(perm),
                            input_type=first.input_type,
                            output_type=last.output_type,
                            length=length,
                        )
                    )

        # Sort by length (prefer shorter pipelines)
        return sorted(suggestions, key=lambda s: s.length)

    async def _agents_accepting(self, type_id: str) -> list[Any]:
        """Find all agents that accept type_id as input."""
        results = []
        all_entries = await self.registry.list_entries()

        for entry in all_entries:
            if entry.input_type and self.is_subtype(type_id, entry.input_type):
                results.append(entry)

        return results


# Convenience functions


def create_lattice(registry: Registry) -> TypeLattice:
    """Create a new type lattice with a registry."""
    return TypeLattice(registry)
