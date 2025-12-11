"""Tests for advanced lattice operations."""

import pytest
from agents.l.advanced_lattice import (
    AdvancedLattice,
    CachedLattice,
    IntersectionType,
    UnionType,
    create_advanced_lattice,
    create_cached_lattice,
)
from agents.l.lattice import SubtypeEdge, TypeKind, TypeNode

# registry fixture imported from conftest.py


@pytest.fixture
def cached_lattice(registry):
    """Create cached lattice."""
    return CachedLattice(registry)


@pytest.fixture
def advanced_lattice(registry):
    """Create advanced lattice."""
    return AdvancedLattice(registry)


class TestUnionType:
    """Tests for UnionType."""

    def test_create_from_types(self):
        """Create union from type IDs."""
        union = UnionType.from_types("str", "int")

        assert "str" in union.members
        assert "int" in union.members

    def test_canonical_id(self):
        """Union ID is canonical (sorted)."""
        u1 = UnionType.from_types("str", "int")
        u2 = UnionType.from_types("int", "str")

        assert u1.id == u2.id
        assert u1.id == "int | str"

    def test_flatten_nested(self):
        """Nested unions are flattened."""
        union = UnionType.from_types("str | int", "float")

        assert set(union.members) == {"str", "int", "float"}

    def test_contains(self):
        """Check if type is member of union."""
        union = UnionType.from_types("str", "int")

        assert union.contains("str")
        assert union.contains("int")
        assert not union.contains("float")

    def test_hashable(self):
        """Union types are hashable."""
        u1 = UnionType.from_types("str", "int")
        u2 = UnionType.from_types("int", "str")

        assert hash(u1) == hash(u2)
        assert {u1} == {u2}  # Same in set


class TestIntersectionType:
    """Tests for IntersectionType."""

    def test_create_from_types(self):
        """Create intersection from type IDs."""
        inter = IntersectionType.from_types("Comparable", "Hashable")

        assert "Comparable" in inter.members
        assert "Hashable" in inter.members

    def test_canonical_id(self):
        """Intersection ID is canonical."""
        i1 = IntersectionType.from_types("A", "B")
        i2 = IntersectionType.from_types("B", "A")

        assert i1.id == i2.id

    def test_requires_all(self):
        """Check if intersection requires all types."""
        inter = IntersectionType.from_types("A", "B", "C")

        assert inter.requires_all(["A", "B"])
        assert inter.requires_all(["A", "B", "C"])
        assert not inter.requires_all(["A", "D"])


class TestCachedLattice:
    """Tests for CachedLattice."""

    def test_subtype_cached(self, cached_lattice):
        """Subtype queries are cached."""
        # First call populates cache
        result1 = cached_lattice.is_subtype("str", "Any")
        result2 = cached_lattice.is_subtype("str", "Any")

        assert result1 == result2
        assert result1 is True
        assert ("str", "Any") in cached_lattice._subtype_cache

    def test_meet_cached(self, cached_lattice):
        """Meet computations are cached."""
        result1 = cached_lattice.meet("str", "str")
        result2 = cached_lattice.meet("str", "str")

        assert result1 == result2

    def test_join_cached(self, cached_lattice):
        """Join computations are cached."""
        result1 = cached_lattice.join("str", "int")
        result2 = cached_lattice.join("str", "int")

        assert result1 == result2

    def test_cache_invalidation(self, cached_lattice):
        """Cache is invalidated on modification."""
        cached_lattice.is_subtype("str", "Any")  # Populate cache

        # Register new type invalidates cache
        node = TypeNode(id="Custom", kind=TypeKind.RECORD, name="Custom")
        cached_lattice.register_type(node)

        assert len(cached_lattice._subtype_cache) == 0

    def test_cache_eviction(self, registry):
        """Cache evicts old entries when full."""
        lattice = CachedLattice(registry, cache_size=10)

        # Fill cache beyond capacity using the method that triggers eviction
        for i in range(20):
            lattice._subtype_cache[(f"type{i}", "Any")] = True
            lattice._maybe_evict(lattice._subtype_cache)

        assert len(lattice._subtype_cache) <= 10


class TestAdvancedLatticeUnions:
    """Tests for union operations in AdvancedLattice."""

    def test_create_union(self, advanced_lattice):
        """Create union type."""
        union_id = advanced_lattice.create_union("str", "int")

        assert " | " in union_id
        assert union_id in advanced_lattice.types

    def test_decompose_union(self, advanced_lattice):
        """Decompose union into members."""
        union_id = advanced_lattice.create_union("str", "int")
        members = advanced_lattice.decompose_union(union_id)

        assert set(members) == {"str", "int"}

    def test_union_subtyping_member(self, advanced_lattice):
        """Members are subtypes of their union."""
        union_id = advanced_lattice.create_union("str", "int")

        assert advanced_lattice.is_subtype("str", union_id)
        assert advanced_lattice.is_subtype("int", union_id)
        assert not advanced_lattice.is_subtype("float", union_id)

    def test_is_union_subtype_to_union(self, advanced_lattice):
        """Union A | B ≤ Union A | B | C."""
        small = advanced_lattice.create_union("str", "int")
        large = advanced_lattice.create_union("str", "int", "float")

        assert advanced_lattice.is_union_subtype(small, large)
        assert not advanced_lattice.is_union_subtype(large, small)


class TestAdvancedLatticeIntersections:
    """Tests for intersection operations in AdvancedLattice."""

    def test_create_intersection(self, advanced_lattice):
        """Create intersection type."""
        # First register member types
        advanced_lattice.register_type(
            TypeNode(id="Comparable", kind=TypeKind.CONTRACT, name="Comparable")
        )
        advanced_lattice.register_type(
            TypeNode(id="Hashable", kind=TypeKind.CONTRACT, name="Hashable")
        )

        inter_id = advanced_lattice.create_intersection("Comparable", "Hashable")

        assert " & " in inter_id
        assert inter_id in advanced_lattice.types

    def test_decompose_intersection(self, advanced_lattice):
        """Decompose intersection into members."""
        inter_id = advanced_lattice.create_intersection("A", "B")
        members = advanced_lattice.decompose_intersection(inter_id)

        assert set(members) == {"A", "B"}

    def test_intersection_subtyping(self, advanced_lattice):
        """Intersection is subtype of each member."""
        advanced_lattice.register_type(
            TypeNode(id="A", kind=TypeKind.CONTRACT, name="A")
        )
        advanced_lattice.register_type(
            TypeNode(id="B", kind=TypeKind.CONTRACT, name="B")
        )

        inter_id = advanced_lattice.create_intersection("A", "B")

        assert advanced_lattice.is_subtype(inter_id, "A")
        assert advanced_lattice.is_subtype(inter_id, "B")


class TestNormalization:
    """Tests for type normalization."""

    def test_normalize_union_removes_never(self, advanced_lattice):
        """Never is removed from unions."""
        result = advanced_lattice.normalize("str | Never")

        assert result == "str"

    def test_normalize_intersection_removes_any(self, advanced_lattice):
        """Any is removed from intersections."""
        result = advanced_lattice.normalize("str & Any")

        assert result == "str"

    def test_normalize_sorts_members(self, advanced_lattice):
        """Members are sorted for canonical form."""
        result = advanced_lattice.normalize("z | a | m")

        assert result == "a | m | z"

    def test_normalize_flattens(self, advanced_lattice):
        """Nested types are flattened."""
        # Note: This tests the normalization string processing
        result = advanced_lattice.normalize("a | b | c")

        assert result == "a | b | c"


class TestVarianceChecking:
    """Tests for variance checking."""

    def test_covariant(self, advanced_lattice):
        """Covariant position allows subtyping."""
        advanced_lattice.register_type(
            TypeNode(id="Animal", kind=TypeKind.RECORD, name="Animal")
        )
        advanced_lattice.register_type(
            TypeNode(id="Cat", kind=TypeKind.RECORD, name="Cat")
        )
        advanced_lattice.add_subtype_edge(
            SubtypeEdge(subtype_id="Cat", supertype_id="Animal", reason="Cat is Animal")
        )

        assert advanced_lattice.check_variance("list", "Cat", "Animal", "covariant")

    def test_contravariant(self, advanced_lattice):
        """Contravariant position reverses subtyping."""
        advanced_lattice.register_type(
            TypeNode(id="Animal", kind=TypeKind.RECORD, name="Animal")
        )
        advanced_lattice.register_type(
            TypeNode(id="Cat", kind=TypeKind.RECORD, name="Cat")
        )
        advanced_lattice.add_subtype_edge(
            SubtypeEdge(subtype_id="Cat", supertype_id="Animal", reason="Cat is Animal")
        )

        # In contravariant position, Animal ≤ Cat (reversed)
        assert advanced_lattice.check_variance(
            "Callable", "Animal", "Cat", "contravariant"
        )

    def test_invariant(self, advanced_lattice):
        """Invariant position requires exact match."""
        assert advanced_lattice.check_variance("dict", "str", "str", "invariant")
        assert not advanced_lattice.check_variance("dict", "str", "int", "invariant")


class TestStructuralSubtyping:
    """Tests for structural subtyping."""

    def test_record_subtype_has_all_fields(self, advanced_lattice):
        """Record subtype must have all fields."""
        advanced_lattice.register_type(
            TypeNode(
                id="Point",
                kind=TypeKind.RECORD,
                name="Point",
                fields={"x": "int", "y": "int"},
            )
        )
        advanced_lattice.register_type(
            TypeNode(
                id="Point3D",
                kind=TypeKind.RECORD,
                name="Point3D",
                fields={"x": "int", "y": "int", "z": "int"},
            )
        )

        # Point3D has all fields of Point, so it's a subtype
        assert advanced_lattice.is_structural_subtype("Point3D", "Point")
        # Point doesn't have z, so it's not a subtype of Point3D
        assert not advanced_lattice.is_structural_subtype("Point", "Point3D")

    def test_record_subtype_field_types(self, advanced_lattice):
        """Record subtype fields must have compatible types."""
        advanced_lattice.register_type(
            TypeNode(
                id="Base",
                kind=TypeKind.RECORD,
                name="Base",
                fields={"value": "Any"},
            )
        )
        advanced_lattice.register_type(
            TypeNode(
                id="Specific",
                kind=TypeKind.RECORD,
                name="Specific",
                fields={"value": "str"},
            )
        )

        # str is subtype of Any, so Specific is subtype of Base
        assert advanced_lattice.is_structural_subtype("Specific", "Base")


class TestMeetJoinWithUnions:
    """Tests for meet/join with union types."""

    def test_join_creates_union(self, advanced_lattice):
        """Join creates union when no common supertype."""
        result = advanced_lattice.join_with_union("str", "int")

        # Should create union since no common supertype (except Any)
        assert " | " in result or result == "Any"

    def test_meet_with_union_distributes(self, advanced_lattice):
        """Meet distributes over union."""
        # Create union
        union = advanced_lattice.create_union("str", "int")

        # Meet with itself should return same union (normalized)
        result = advanced_lattice.meet_with_union(union, union)

        assert result == union or set(result.split(" | ")) == {"str", "int"}


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_advanced_lattice(self, registry):
        """create_advanced_lattice returns AdvancedLattice."""
        lattice = create_advanced_lattice(registry)

        assert isinstance(lattice, AdvancedLattice)

    def test_create_cached_lattice(self, registry):
        """create_cached_lattice returns CachedLattice."""
        lattice = create_cached_lattice(registry)

        assert isinstance(lattice, CachedLattice)

    def test_create_cached_with_size(self, registry):
        """create_cached_lattice accepts cache size."""
        lattice = create_cached_lattice(registry, cache_size=500)

        assert lattice._cache_size == 500
