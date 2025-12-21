"""
Property-based tests for HoTT Foundation.

Tests Properties 9-10 from design.md:
- Property 9: HoTT univalence (isomorphic structures are identical)
- Property 10: Constructive proof generation

Feature: formal-verification-metatheory
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.verification.hott import (
    HoTTContext,
    HoTTPath,
    HoTTType,
    HoTTVerificationResult,
    Isomorphism,
    PathType,
    UniverseLevel,
    construct_equality_path,
    verify_isomorphism,
)

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def type_name_strategy(draw: st.DrawFn) -> str:
    """Generate valid type names."""
    return draw(
        st.text(
            alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            min_size=1,
            max_size=20,
        )
    )


@st.composite
def hott_type_strategy(draw: st.DrawFn) -> HoTTType:
    """Generate random HoTT types."""
    name = draw(type_name_strategy())
    universe_level = draw(st.sampled_from(list(UniverseLevel)))
    constructors = draw(
        st.frozensets(
            st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=10),
            min_size=0,
            max_size=5,
        )
    )
    eliminators = draw(
        st.frozensets(
            st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=10),
            min_size=0,
            max_size=3,
        )
    )

    return HoTTType(
        name=name,
        universe_level=universe_level,
        constructors=constructors,
        eliminators=eliminators,
    )


@st.composite
def simple_value_strategy(draw: st.DrawFn) -> object:
    """Generate simple values for isomorphism testing."""
    return draw(
        st.one_of(
            st.integers(min_value=-100, max_value=100),
            st.text(min_size=0, max_size=20),
            st.lists(st.integers(), min_size=0, max_size=5),
            st.dictionaries(
                st.text(min_size=1, max_size=5),
                st.integers(),
                min_size=0,
                max_size=3,
            ),
        )
    )


@st.composite
def isomorphic_dict_pair_strategy(draw: st.DrawFn) -> tuple[dict[str, int], dict[str, int]]:
    """Generate pairs of isomorphic dictionaries (same keys AND same values)."""
    keys = draw(
        st.lists(
            st.text(min_size=1, max_size=5),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    # Use the SAME values for both dicts to ensure true isomorphism
    values = draw(st.lists(st.integers(), min_size=len(keys), max_size=len(keys)))

    dict1 = dict(zip(keys, values))
    dict2 = dict(zip(keys, values))  # Same values = truly isomorphic

    return dict1, dict2


@st.composite
def same_structure_dict_pair_strategy(draw: st.DrawFn) -> tuple[dict[str, int], dict[str, int]]:
    """Generate pairs of dicts with same keys but potentially different values."""
    keys = draw(
        st.lists(
            st.text(min_size=1, max_size=5),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    values1 = draw(st.lists(st.integers(), min_size=len(keys), max_size=len(keys)))
    values2 = draw(st.lists(st.integers(), min_size=len(keys), max_size=len(keys)))

    dict1 = dict(zip(keys, values1))
    dict2 = dict(zip(keys, values2))

    return dict1, dict2


# =============================================================================
# Property 9: HoTT Univalence
# =============================================================================


class TestUnivalence:
    """Tests for Property 9: HoTT univalence (isomorphic structures are identical)."""

    @pytest.mark.asyncio
    @given(value=simple_value_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_reflexive_isomorphism(self, value: object) -> None:
        """Property 9.1: Every value is isomorphic to itself."""
        context = HoTTContext()
        result = await context.are_isomorphic(value, value)
        assert result is True

    @pytest.mark.asyncio
    @given(pair=isomorphic_dict_pair_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_structural_isomorphism(
        self,
        pair: tuple[dict[str, int], dict[str, int]],
    ) -> None:
        """Property 9.2: Dictionaries with same keys AND values are isomorphic."""
        context = HoTTContext()
        dict1, dict2 = pair
        result = await context.are_isomorphic(dict1, dict2)
        # Same keys AND same values means truly isomorphic
        assert result is True

    @pytest.mark.asyncio
    async def test_different_types_not_isomorphic(self) -> None:
        """Property 9.3: Different types are not isomorphic."""
        context = HoTTContext()
        result = await context.are_isomorphic(42, "42")
        assert result is False

    @pytest.mark.asyncio
    async def test_different_structure_not_isomorphic(self) -> None:
        """Property 9.4: Different structures are not isomorphic."""
        context = HoTTContext()
        dict1 = {"a": 1, "b": 2}
        dict2 = {"x": 1, "y": 2}
        result = await context.are_isomorphic(dict1, dict2)
        assert result is False

    @pytest.mark.asyncio
    async def test_isomorphism_registration(self) -> None:
        """Property 9.5: Registered isomorphisms are recognized."""
        context = HoTTContext()
        iso = Isomorphism(
            source_type="TypeA",
            target_type="TypeB",
            forward_map={"transform": "a_to_b"},
            inverse_map={"transform": "b_to_a"},
            forward_inverse_proof="proof1",
            inverse_forward_proof="proof2",
        )
        context.register_isomorphism(iso)

        # Check that both directions are registered
        assert ("TypeA", "TypeB") in context.isomorphism_registry
        assert ("TypeB", "TypeA") in context.isomorphism_registry


# =============================================================================
# Property 10: Constructive Proof Generation
# =============================================================================


class TestConstructiveProofs:
    """Tests for Property 10: Constructive proof generation."""

    @pytest.mark.asyncio
    @given(value=simple_value_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_reflexivity_path(self, value: object) -> None:
        """Property 10.1: Reflexivity path is always constructible."""
        context = HoTTContext()
        path = await context.construct_path(value, value)

        assert path is not None
        assert path.path_type == PathType.REFL
        assert path.source == value
        assert path.target == value

    @pytest.mark.asyncio
    @given(pair=isomorphic_dict_pair_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_univalence_path(
        self,
        pair: tuple[dict[str, int], dict[str, int]],
    ) -> None:
        """Property 10.2: Univalence path is constructible for isomorphic structures."""
        context = HoTTContext()
        dict1, dict2 = pair
        path = await context.construct_path(dict1, dict2)

        assert path is not None
        # Should be REFL since dict1 == dict2 (same keys and values)
        assert path.path_type == PathType.REFL

    @pytest.mark.asyncio
    async def test_path_caching(self) -> None:
        """Property 10.3: Paths are cached for efficiency."""
        context = HoTTContext()
        value = {"test": 42}

        # Construct path twice
        path1 = await context.construct_path(value, value)
        path2 = await context.construct_path(value, value)

        # Should be the same cached path
        assert path1 is path2

    @pytest.mark.asyncio
    async def test_path_concatenation(self) -> None:
        """Property 10.4: Paths can be concatenated."""
        context = HoTTContext()
        a = {"value": 1}
        b = {"value": 1}  # Same structure
        c = {"value": 1}

        path_ab = await context.construct_path(a, b)
        path_bc = await context.construct_path(b, c)

        assert path_ab is not None
        assert path_bc is not None

        # Concatenate paths
        path_ac = context.concat_paths(path_ab, path_bc)
        assert path_ac is not None
        assert path_ac.path_type == PathType.CONCAT

    @pytest.mark.asyncio
    async def test_path_inverse(self) -> None:
        """Property 10.5: Paths can be inverted."""
        context = HoTTContext()
        a = {"value": 1}
        b = {"value": 1}

        path_ab = await context.construct_path(a, b)
        assert path_ab is not None

        # Invert path
        path_ba = context.inverse_path(path_ab)
        assert path_ba is not None
        assert path_ba.path_type == PathType.INVERSE
        assert path_ba.source == path_ab.target
        assert path_ba.target == path_ab.source


# =============================================================================
# HoTT Type Tests
# =============================================================================


class TestHoTTTypes:
    """Tests for HoTT type operations."""

    def test_base_types_registered(self) -> None:
        """Base types are registered in universe."""
        context = HoTTContext()
        assert "Unit" in context.type_universe
        assert "Empty" in context.type_universe
        assert "Bool" in context.type_universe
        assert "Nat" in context.type_universe

    @given(hott_type=hott_type_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_type_registration(self, hott_type: HoTTType) -> None:
        """Types can be registered in universe."""
        context = HoTTContext()
        context.register_type(hott_type)
        assert hott_type.name in context.type_universe

    def test_proposition_type_creation(self) -> None:
        """Proposition types are created correctly."""
        prop = HoTTType.proposition("TestProp")

        assert prop.name == "TestProp"
        assert prop.universe_level == UniverseLevel.PROP
        assert "intro" in prop.constructors
        assert "elim" in prop.eliminators

    def test_set_type_creation(self) -> None:
        """Set types are created correctly."""
        set_type = HoTTType.set_type("TestSet", frozenset(["zero", "succ"]))

        assert set_type.name == "TestSet"
        assert set_type.universe_level == UniverseLevel.SET
        assert "zero" in set_type.constructors
        assert "succ" in set_type.constructors

    def test_higher_inductive_type(self) -> None:
        """Higher inductive types can be defined."""
        context = HoTTContext()
        hit = context.define_higher_inductive_type(
            name="Circle",
            point_constructors=["base"],
            path_constructors=[{"name": "loop", "source": "base", "target": "base"}],
        )

        assert hit.name == "Circle"
        assert hit.universe_level == UniverseLevel.GROUPOID
        assert "base" in hit.constructors
        assert hit.metadata.get("is_hit") is True


# =============================================================================
# Verification Result Tests
# =============================================================================


class TestVerificationResults:
    """Tests for HoTT verification results."""

    def test_success_result(self) -> None:
        """Success results are created correctly."""
        path = HoTTPath.refl(42)
        result = HoTTVerificationResult.success(path, "test_verification")

        assert result.verified is True
        assert result.path == path
        assert result.verification_type == "test_verification"

    def test_failure_result(self) -> None:
        """Failure results are created correctly."""
        result = HoTTVerificationResult.failure("test_verification", "Test failed")

        assert result.verified is False
        assert result.path is None
        assert result.verification_type == "test_verification"
        assert "Test failed" in result.details.get("reason", "")


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_verify_isomorphism_function(self) -> None:
        """verify_isomorphism convenience function works."""
        result = await verify_isomorphism(42, 42)
        assert result is True

        result = await verify_isomorphism(42, "42")
        assert result is False

    @pytest.mark.asyncio
    async def test_construct_equality_path_function(self) -> None:
        """construct_equality_path convenience function works."""
        path = await construct_equality_path(42, 42)
        assert path is not None
        assert path.path_type == PathType.REFL
