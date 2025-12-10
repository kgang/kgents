"""
Advanced Lattice Operations for L-gent.

This module extends the base TypeLattice with:
1. Union type construction and decomposition
2. Intersection type computation
3. Path caching for performance
4. Type normalization
5. Variance checking for generics

Philosophy:
> "Types are sets; the lattice is their algebra."
"""

from __future__ import annotations

from dataclasses import dataclass

from .lattice import (
    SubtypeEdge,
    TypeKind,
    TypeLattice,
    TypeNode,
)
from .registry import Registry


@dataclass
class UnionType:
    """
    A union type representing A | B | C...

    Union types are the join of their members in the lattice.
    """

    members: tuple[str, ...]  # Frozen for hashing
    id: str = ""

    def __post_init__(self):
        if not self.id:
            # Create canonical ID from sorted members
            self.id = " | ".join(sorted(self.members))

    def __hash__(self):
        return hash(self.members)

    def contains(self, type_id: str) -> bool:
        """Check if type_id is a member of this union."""
        return type_id in self.members

    @classmethod
    def from_types(cls, *type_ids: str) -> "UnionType":
        """Create union from type IDs."""
        # Flatten nested unions
        flat = []
        for t in type_ids:
            if " | " in t:
                flat.extend(t.split(" | "))
            else:
                flat.append(t)
        # Remove duplicates, sort for canonical form
        unique = tuple(sorted(set(flat)))
        return cls(members=unique)


@dataclass
class IntersectionType:
    """
    An intersection type representing A & B & C...

    Intersection types are the meet of their members in the lattice.
    A value of intersection type must satisfy ALL member types.
    """

    members: tuple[str, ...]
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = " & ".join(sorted(self.members))

    def __hash__(self):
        return hash(self.members)

    def requires_all(self, type_ids: list[str]) -> bool:
        """Check if this intersection requires all given types."""
        return all(t in self.members for t in type_ids)

    @classmethod
    def from_types(cls, *type_ids: str) -> "IntersectionType":
        """Create intersection from type IDs."""
        flat = []
        for t in type_ids:
            if " & " in t:
                flat.extend(t.split(" & "))
            else:
                flat.append(t)
        unique = tuple(sorted(set(flat)))
        return cls(members=unique)


@dataclass
class TypePath:
    """A path through the type lattice."""

    source: str
    target: str
    steps: tuple[str, ...]  # Type IDs visited
    cost: float = 1.0  # Total adaptation cost

    def __hash__(self):
        return hash((self.source, self.target, self.steps))


class CachedLattice(TypeLattice):
    """
    TypeLattice with caching for performance.

    Caches:
    - Subtype queries
    - Meet/join computations
    - Path searches
    """

    def __init__(self, registry: Registry, cache_size: int = 1000):
        super().__init__(registry)
        self._cache_size = cache_size
        self._subtype_cache: dict[tuple[str, str], bool] = {}
        self._meet_cache: dict[tuple[str, str], str] = {}
        self._join_cache: dict[tuple[str, str], str] = {}
        self._path_cache: dict[tuple[str, str], list[TypePath]] = {}

    def is_subtype(self, sub: str, super_: str) -> bool:
        """Cached subtype check."""
        key = (sub, super_)
        if key not in self._subtype_cache:
            result = super().is_subtype(sub, super_)
            self._subtype_cache[key] = result
            self._maybe_evict(self._subtype_cache)
        return self._subtype_cache[key]

    def meet(self, type_a: str, type_b: str) -> str:
        """Cached meet computation."""
        # Normalize order for cache key
        key = (min(type_a, type_b), max(type_a, type_b))
        if key not in self._meet_cache:
            result = super().meet(type_a, type_b)
            self._meet_cache[key] = result
            self._maybe_evict(self._meet_cache)
        return self._meet_cache[key]

    def join(self, type_a: str, type_b: str) -> str:
        """Cached join computation."""
        key = (min(type_a, type_b), max(type_a, type_b))
        if key not in self._join_cache:
            result = super().join(type_a, type_b)
            self._join_cache[key] = result
            self._maybe_evict(self._join_cache)
        return self._join_cache[key]

    def _maybe_evict(self, cache: dict) -> None:
        """Evict oldest entries if cache is too large."""
        if len(cache) > self._cache_size:
            # Simple FIFO eviction (dict maintains insertion order in Python 3.7+)
            keys_to_remove = list(cache.keys())[: len(cache) - self._cache_size // 2]
            for key in keys_to_remove:
                del cache[key]

    def invalidate_cache(self) -> None:
        """Clear all caches (call after lattice modifications)."""
        self._subtype_cache.clear()
        self._meet_cache.clear()
        self._join_cache.clear()
        self._path_cache.clear()

    def register_type(self, node: TypeNode) -> None:
        """Register type and invalidate affected caches."""
        super().register_type(node)
        self.invalidate_cache()

    def add_subtype_edge(self, edge: SubtypeEdge) -> None:
        """Add edge and invalidate caches."""
        super().add_subtype_edge(edge)
        self.invalidate_cache()


class AdvancedLattice(CachedLattice):
    """
    TypeLattice with advanced operations.

    Extends CachedLattice with:
    - Union/intersection type handling
    - Type normalization
    - Variance checking
    - Structural subtyping
    """

    def __init__(self, registry: Registry, cache_size: int = 1000):
        super().__init__(registry, cache_size)
        self._unions: dict[str, UnionType] = {}
        self._intersections: dict[str, IntersectionType] = {}

    # ─────────────────────────────────────────────────────────────
    # Union Type Operations
    # ─────────────────────────────────────────────────────────────

    def create_union(self, *type_ids: str) -> str:
        """
        Create a union type from member types.

        Returns the canonical ID of the union.

        Example:
            >>> lattice.create_union("str", "int")  # "int | str"
        """
        union = UnionType.from_types(*type_ids)

        if union.id not in self._unions:
            self._unions[union.id] = union

            # Register as type node
            node = TypeNode(
                id=union.id,
                kind=TypeKind.UNION,
                name=union.id,
                members=list(union.members),
            )
            self.register_type(node)

            # Add subtype edges: each member is subtype of union
            for member in union.members:
                if member in self.types:
                    self.edges.append(
                        SubtypeEdge(
                            subtype_id=member,
                            supertype_id=union.id,
                            reason=f"{member} is member of union",
                        )
                    )

        return union.id

    def decompose_union(self, union_id: str) -> list[str] | None:
        """
        Decompose a union type into its members.

        Returns None if not a union.
        """
        if union_id in self._unions:
            return list(self._unions[union_id].members)

        # Try parsing from ID
        if " | " in union_id:
            return union_id.split(" | ")

        return None

    def is_union_subtype(self, sub: str, super_: str) -> bool:
        """
        Check union subtyping.

        A | B ≤ C iff A ≤ C and B ≤ C
        A ≤ B | C iff A ≤ B or A ≤ C
        """
        sub_members = self.decompose_union(sub)
        super_members = self.decompose_union(super_)

        if sub_members and super_members:
            # Both are unions: every member of sub must be subtype of some member of super
            return all(
                any(self.is_subtype(sm, sp) for sp in super_members)
                for sm in sub_members
            )
        elif sub_members:
            # Sub is union: all members must be subtypes of super
            return all(self.is_subtype(m, super_) for m in sub_members)
        elif super_members:
            # Super is union: sub must be subtype of some member
            return any(self.is_subtype(sub, m) for m in super_members)
        else:
            # Neither is union, use base method
            return self.is_subtype(sub, super_)

    # ─────────────────────────────────────────────────────────────
    # Intersection Type Operations
    # ─────────────────────────────────────────────────────────────

    def create_intersection(self, *type_ids: str) -> str:
        """
        Create an intersection type from member types.

        Example:
            >>> lattice.create_intersection("Comparable", "Hashable")
            "Comparable & Hashable"
        """
        intersection = IntersectionType.from_types(*type_ids)

        if intersection.id not in self._intersections:
            self._intersections[intersection.id] = intersection

            # Register as type node
            node = TypeNode(
                id=intersection.id,
                kind=TypeKind.RECORD,  # Intersection is like a record with all fields
                name=intersection.id,
                members=list(intersection.members),
            )
            self.register_type(node)

            # Add subtype edges: intersection is subtype of each member
            for member in intersection.members:
                if member in self.types:
                    self.edges.append(
                        SubtypeEdge(
                            subtype_id=intersection.id,
                            supertype_id=member,
                            reason=f"intersection includes {member}",
                        )
                    )

        return intersection.id

    def decompose_intersection(self, inter_id: str) -> list[str] | None:
        """Decompose an intersection type into its members."""
        if inter_id in self._intersections:
            return list(self._intersections[inter_id].members)

        if " & " in inter_id:
            return inter_id.split(" & ")

        return None

    def is_intersection_subtype(self, sub: str, super_: str) -> bool:
        """
        Check intersection subtyping.

        A & B ≤ C iff A ≤ C or B ≤ C
        A ≤ B & C iff A ≤ B and A ≤ C
        """
        sub_members = self.decompose_intersection(sub)
        super_members = self.decompose_intersection(super_)

        if sub_members and super_members:
            # Both intersections: sub must have all requirements of super
            return all(
                any(self.is_subtype(sm, sp) for sm in sub_members)
                for sp in super_members
            )
        elif sub_members:
            # Sub is intersection: any member being subtype suffices
            return any(self.is_subtype(m, super_) for m in sub_members)
        elif super_members:
            # Super is intersection: sub must satisfy all
            return all(self.is_subtype(sub, m) for m in super_members)
        else:
            return self.is_subtype(sub, super_)

    # ─────────────────────────────────────────────────────────────
    # Type Normalization
    # ─────────────────────────────────────────────────────────────

    def normalize(self, type_id: str) -> str:
        """
        Normalize a type expression.

        Applies:
        - Remove Never from unions (A | Never = A)
        - Remove Any from intersections (A & Any = A)
        - Flatten nested unions/intersections
        - Sort members for canonical form
        """
        # Handle unions
        if " | " in type_id:
            members = type_id.split(" | ")
            # Remove Never
            members = [m.strip() for m in members if m.strip() != "Never"]
            if not members:
                return "Never"
            if len(members) == 1:
                return self.normalize(members[0])
            return " | ".join(sorted(set(self.normalize(m) for m in members)))

        # Handle intersections
        if " & " in type_id:
            members = type_id.split(" & ")
            # Remove Any
            members = [m.strip() for m in members if m.strip() != "Any"]
            if not members:
                return "Any"
            if len(members) == 1:
                return self.normalize(members[0])
            return " & ".join(sorted(set(self.normalize(m) for m in members)))

        return type_id.strip()

    # ─────────────────────────────────────────────────────────────
    # Variance Checking
    # ─────────────────────────────────────────────────────────────

    def check_variance(
        self,
        container: str,
        element_sub: str,
        element_super: str,
        position: str = "covariant",
    ) -> bool:
        """
        Check variance for generic types.

        Args:
            container: The container type (e.g., "list", "dict")
            element_sub: The subtype element
            element_super: The supertype element
            position: "covariant", "contravariant", or "invariant"

        Returns:
            True if the variance allows the subtyping relationship

        Example:
            # list is covariant: list[Cat] ≤ list[Animal]
            >>> lattice.check_variance("list", "Cat", "Animal", "covariant")
            True

            # function args are contravariant: Callable[[Animal], X] ≤ Callable[[Cat], X]
            >>> lattice.check_variance("Callable", "Animal", "Cat", "contravariant")
            True
        """
        is_sub = self.is_subtype(element_sub, element_super)

        match position:
            case "covariant":
                return is_sub
            case "contravariant":
                return self.is_subtype(element_super, element_sub)
            case "invariant":
                return element_sub == element_super
            case _:
                return False

    # ─────────────────────────────────────────────────────────────
    # Structural Subtyping
    # ─────────────────────────────────────────────────────────────

    def is_structural_subtype(self, sub: str, super_: str) -> bool:
        """
        Check structural subtyping for record types.

        A record is a subtype if it has all required fields with compatible types.
        """
        sub_node = self.types.get(sub)
        super_node = self.types.get(super_)

        if not sub_node or not super_node:
            return False

        if super_node.kind != TypeKind.RECORD:
            return self.is_subtype(sub, super_)

        if sub_node.kind != TypeKind.RECORD:
            return False

        # Check each field in super exists in sub with compatible type
        for field_name, field_type in super_node.fields.items():
            if field_name not in sub_node.fields:
                return False
            if not self.is_subtype(sub_node.fields[field_name], field_type):
                return False

        return True

    # ─────────────────────────────────────────────────────────────
    # Enhanced Meet/Join with Union/Intersection
    # ─────────────────────────────────────────────────────────────

    def meet_with_union(self, type_a: str, type_b: str) -> str:
        """
        Compute meet handling unions.

        meet(A | B, C) = meet(A, C) | meet(B, C)
        """
        a_members = self.decompose_union(type_a)
        b_members = self.decompose_union(type_b)

        if a_members and b_members:
            # Distribute: (A | B) ∧ (C | D) = (A ∧ C) | (A ∧ D) | (B ∧ C) | (B ∧ D)
            meets = []
            for a in a_members:
                for b in b_members:
                    m = self.meet(a, b)
                    if m != "Never":
                        meets.append(m)
            if not meets:
                return "Never"
            return self.normalize(" | ".join(meets))
        elif a_members:
            meets = [self.meet(a, type_b) for a in a_members]
            meets = [m for m in meets if m != "Never"]
            if not meets:
                return "Never"
            return self.normalize(" | ".join(meets))
        elif b_members:
            meets = [self.meet(type_a, b) for b in b_members]
            meets = [m for m in meets if m != "Never"]
            if not meets:
                return "Never"
            return self.normalize(" | ".join(meets))
        else:
            return self.meet(type_a, type_b)

    def join_with_union(self, type_a: str, type_b: str) -> str:
        """
        Compute join, creating union if needed.

        If no common supertype exists, create union.
        """
        # Check if there's a common supertype
        base_join = self.join(type_a, type_b)

        if base_join != "Any":
            return base_join

        # No common supertype, create union
        return self.create_union(type_a, type_b)


# ─────────────────────────────────────────────────────────────
# Factory Functions
# ─────────────────────────────────────────────────────────────


def create_advanced_lattice(registry: Registry) -> AdvancedLattice:
    """Create an advanced lattice with all features."""
    return AdvancedLattice(registry)


def create_cached_lattice(registry: Registry, cache_size: int = 1000) -> CachedLattice:
    """Create a cached lattice for performance."""
    return CachedLattice(registry, cache_size)
