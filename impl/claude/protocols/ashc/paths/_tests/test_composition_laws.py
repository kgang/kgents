"""
Property-based tests for DerivationPath composition laws.

Tests the categorical properties of DerivationPath:
1. Left Identity: refl(source) ; p == p
2. Right Identity: p ; refl(target) == p
3. Associativity: (p ; q) ; r == p ; (q ; r)
4. Loss Accumulation: L(p;q) = 1 - (1-L(p))*(1-L(q))

Uses hypothesis for property-based testing to ensure laws hold
for arbitrary valid inputs.

Philosophy:
    "If the laws don't hold, it's not a category.
     If it's not a category, it's not ASHC."
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st

from protocols.ashc.paths.composition import (
    compose,
    compose_all,
    compute_accumulated_loss,
    loss_is_acceptable,
    verify_all_laws,
    verify_associativity,
    verify_identity_left,
    verify_identity_right,
)
from protocols.ashc.paths.types import (
    DerivationPath,
    DerivationWitness,
    PathKind,
    WitnessType,
)

# =============================================================================
# Strategies for generating test data
# =============================================================================

# Strategy for valid IDs (non-empty alphanumeric strings)
valid_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
    min_size=1,
    max_size=20,
)

# Strategy for valid Galois loss values [0, 1)
# Exclude 1.0 to avoid edge cases where 1.0 * anything = 0
galois_loss_strategy = st.floats(min_value=0.0, max_value=0.99, allow_nan=False)

# Strategy for confidence values [0, 1]
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


@st.composite
def witness_strategy(draw: st.DrawFn) -> DerivationWitness:
    """Generate a random DerivationWitness."""
    witness_type = draw(st.sampled_from(list(WitnessType)))
    confidence = draw(confidence_strategy)
    grounding = draw(st.one_of(st.none(), valid_id_strategy))

    return DerivationWitness.create(
        witness_type=witness_type,
        evidence={"test": draw(st.text(min_size=0, max_size=50))},
        confidence=confidence,
        grounding_principle=grounding,
    )


@st.composite
def derivation_path_strategy(
    draw: st.DrawFn,
    source_id: str | None = None,
    target_id: str | None = None,
) -> DerivationPath:
    """Generate a random DerivationPath with optional fixed endpoints."""
    src = source_id if source_id is not None else draw(valid_id_strategy)
    tgt = target_id if target_id is not None else draw(valid_id_strategy)
    loss = draw(galois_loss_strategy)
    witnesses = draw(st.lists(witness_strategy(), min_size=0, max_size=3))
    lineage = draw(st.lists(valid_id_strategy, min_size=0, max_size=3))

    return DerivationPath.derive(
        source_id=src,
        target_id=tgt,
        witnesses=witnesses,
        galois_loss=loss,
        kblock_lineage=lineage,
    )


@st.composite
def composable_path_pair_strategy(draw: st.DrawFn) -> tuple[DerivationPath, DerivationPath]:
    """Generate a pair of composable paths (p.target == q.source)."""
    # Draw three distinct IDs
    a = draw(valid_id_strategy)
    b = draw(valid_id_strategy)
    c = draw(valid_id_strategy)

    # Ensure distinctness
    assume(a != b and b != c)

    # Create paths with matching midpoint
    path1 = draw(derivation_path_strategy(source_id=a, target_id=b))
    path2 = draw(derivation_path_strategy(source_id=b, target_id=c))

    return (path1, path2)


@st.composite
def composable_path_triple_strategy(
    draw: st.DrawFn,
) -> tuple[DerivationPath, DerivationPath, DerivationPath]:
    """Generate a triple of composable paths for associativity testing."""
    # Draw four distinct IDs
    a = draw(valid_id_strategy)
    b = draw(valid_id_strategy)
    c = draw(valid_id_strategy)
    d = draw(valid_id_strategy)

    # Ensure distinctness
    assume(len({a, b, c, d}) == 4)

    # Create composable chain: a -> b -> c -> d
    path1 = draw(derivation_path_strategy(source_id=a, target_id=b))
    path2 = draw(derivation_path_strategy(source_id=b, target_id=c))
    path3 = draw(derivation_path_strategy(source_id=c, target_id=d))

    return (path1, path2, path3)


# =============================================================================
# Identity Law Tests
# =============================================================================


class TestIdentityLaws:
    """Tests for categorical identity laws."""

    @given(path=derivation_path_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_left_identity_holds(self, path: DerivationPath) -> None:
        """
        Test: refl(source) ; p == p

        The reflexive path on the source should act as left identity.
        """
        result = verify_identity_left(path)
        assert result.passed, f"Left identity failed: {result.message}"
        assert result.details["source_match"]
        assert result.details["target_match"]
        assert result.details["loss_match"]

    @given(path=derivation_path_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_right_identity_holds(self, path: DerivationPath) -> None:
        """
        Test: p ; refl(target) == p

        The reflexive path on the target should act as right identity.
        """
        result = verify_identity_right(path)
        assert result.passed, f"Right identity failed: {result.message}"
        assert result.details["source_match"]
        assert result.details["target_match"]
        assert result.details["loss_match"]

    @given(source_id=valid_id_strategy)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_refl_composes_with_refl(self, source_id: str) -> None:
        """
        Test: refl(a) ; refl(a) == refl(a)

        Composing identity with itself yields identity.
        """
        refl = DerivationPath.refl(source_id)
        composed = refl.compose(refl)

        assert composed.source_id == source_id
        assert composed.target_id == source_id
        assert composed.galois_loss == 0.0

    @given(path=derivation_path_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_identity_preserves_loss(self, path: DerivationPath) -> None:
        """
        Test: L(refl ; p) == L(p) == L(p ; refl)

        Identity composition doesn't change loss.
        """
        refl_source = DerivationPath.refl(path.source_id)
        refl_target = DerivationPath.refl(path.target_id)

        left = refl_source.compose(path)
        right = path.compose(refl_target)

        # Loss should be preserved
        assert abs(left.galois_loss - path.galois_loss) < 1e-10
        assert abs(right.galois_loss - path.galois_loss) < 1e-10


# =============================================================================
# Associativity Law Tests
# =============================================================================


class TestAssociativityLaw:
    """Tests for categorical associativity law."""

    @given(paths=composable_path_triple_strategy())
    @settings(max_examples=100)
    def test_associativity_holds(
        self, paths: tuple[DerivationPath, DerivationPath, DerivationPath]
    ) -> None:
        """
        Test: (p ; q) ; r == p ; (q ; r)

        Composition must be associative.
        """
        p, q, r = paths
        result = verify_associativity(p, q, r)
        assert result.passed, f"Associativity failed: {result.message}"

    @given(paths=composable_path_triple_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_associativity_source_target(
        self, paths: tuple[DerivationPath, DerivationPath, DerivationPath]
    ) -> None:
        """
        Test that associativity preserves source and target.

        (p ; q) ; r and p ; (q ; r) should have same endpoints.
        """
        p, q, r = paths

        left = (p.compose(q)).compose(r)
        right = p.compose(q.compose(r))

        assert left.source_id == right.source_id == p.source_id
        assert left.target_id == right.target_id == r.target_id

    @given(paths=composable_path_triple_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_associativity_loss_equality(
        self, paths: tuple[DerivationPath, DerivationPath, DerivationPath]
    ) -> None:
        """
        Test that associativity preserves loss.

        L((p;q);r) == L(p;(q;r))
        """
        p, q, r = paths

        left = (p.compose(q)).compose(r)
        right = p.compose(q.compose(r))

        # Loss should be equal (within floating point tolerance)
        assert abs(left.galois_loss - right.galois_loss) < 1e-10


# =============================================================================
# Loss Accumulation Tests
# =============================================================================


class TestLossAccumulation:
    """Tests for Galois loss accumulation formula."""

    @given(loss1=galois_loss_strategy, loss2=galois_loss_strategy)
    @settings(max_examples=100)
    def test_loss_accumulation_formula(self, loss1: float, loss2: float) -> None:
        """
        Test: L(p;q) = 1 - (1-L(p))*(1-L(q))

        The composition loss formula is computed correctly.
        """
        expected = 1.0 - (1.0 - loss1) * (1.0 - loss2)
        actual = compute_accumulated_loss([loss1, loss2])

        assert abs(actual - expected) < 1e-10

    @given(loss=galois_loss_strategy)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_identity_loss_is_neutral(self, loss: float) -> None:
        """
        Test: L([0, x]) == x

        Zero loss acts as identity for accumulation.
        """
        result = compute_accumulated_loss([0.0, loss])
        assert abs(result - loss) < 1e-10

    @given(losses=st.lists(galois_loss_strategy, min_size=1, max_size=5))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_loss_is_monotonically_increasing(self, losses: list[float]) -> None:
        """
        Test: L([x1, ..., xn]) >= max(x1, ..., xn)

        Composition never decreases loss.
        """
        accumulated = compute_accumulated_loss(losses)
        max_individual = max(losses)

        assert accumulated >= max_individual - 1e-10

    @given(paths=composable_path_pair_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_composition_increases_loss(self, paths: tuple[DerivationPath, DerivationPath]) -> None:
        """
        Test that composition never decreases loss.

        L(p;q) >= max(L(p), L(q))
        """
        p, q = paths
        composed = p.compose(q)

        max_input_loss = max(p.galois_loss, q.galois_loss)
        assert composed.galois_loss >= max_input_loss - 1e-10


# =============================================================================
# Composition Validity Tests
# =============================================================================


class TestCompositionValidity:
    """Tests for composition validity checks."""

    @given(path1=derivation_path_strategy(), path2=derivation_path_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_incompatible_paths_raise_error(
        self, path1: DerivationPath, path2: DerivationPath
    ) -> None:
        """
        Test that composing incompatible paths raises ValueError.

        p ; q requires p.target == q.source
        """
        # Only test if they're actually incompatible
        assume(path1.target_id != path2.source_id)

        with pytest.raises(ValueError, match="Cannot compose"):
            path1.compose(path2)

    @given(paths=composable_path_pair_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_compatible_paths_compose(self, paths: tuple[DerivationPath, DerivationPath]) -> None:
        """
        Test that compatible paths compose successfully.
        """
        p, q = paths
        composed = p.compose(q)

        assert composed.source_id == p.source_id
        assert composed.target_id == q.target_id


# =============================================================================
# Operator Tests
# =============================================================================


class TestOperators:
    """Tests for operator overloads."""

    @given(paths=composable_path_pair_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_rshift_equals_compose(self, paths: tuple[DerivationPath, DerivationPath]) -> None:
        """
        Test: p >> q == p.compose(q)

        The >> operator should be equivalent to compose.
        """
        p, q = paths

        via_method = p.compose(q)
        via_operator = p >> q

        assert via_method.source_id == via_operator.source_id
        assert via_method.target_id == via_operator.target_id
        assert abs(via_method.galois_loss - via_operator.galois_loss) < 1e-10


# =============================================================================
# All Laws Combined Test
# =============================================================================


class TestAllLaws:
    """Combined tests using verify_all_laws."""

    @given(paths=composable_path_triple_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_all_laws_pass(
        self, paths: tuple[DerivationPath, DerivationPath, DerivationPath]
    ) -> None:
        """
        Test that all categorical laws pass for valid paths.
        """
        p, q, r = paths
        results = verify_all_laws(p, q, r)

        for result in results:
            assert result.passed, f"Law '{result.law_name}' failed: {result.message}"


# =============================================================================
# Grounding Tests
# =============================================================================


class TestGrounding:
    """Tests for is_grounded() method."""

    def test_refl_is_always_grounded(self) -> None:
        """Reflexive paths are always grounded."""
        refl = DerivationPath.refl("any_id")
        assert refl.is_grounded()

    @given(path=derivation_path_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_high_loss_not_grounded(self, path: DerivationPath) -> None:
        """Paths with loss >= 0.5 are not grounded unless REFL."""
        if path.path_kind == PathKind.REFL:
            assert path.is_grounded()
        elif path.galois_loss >= 0.5:
            # Might still be grounded if has grounded witness
            has_grounded_witness = any(w.grounding_principle is not None for w in path.witnesses)
            if not has_grounded_witness:
                assert not path.is_grounded()


# =============================================================================
# Serialization Round-trip Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict/from_dict round-trips."""

    @given(path=derivation_path_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_path_serialization_roundtrip(self, path: DerivationPath) -> None:
        """DerivationPath survives to_dict/from_dict round-trip."""
        serialized = path.to_dict()
        restored = DerivationPath.from_dict(serialized)

        assert restored.path_id == path.path_id
        assert restored.path_kind == path.path_kind
        assert restored.source_id == path.source_id
        assert restored.target_id == path.target_id
        assert abs(restored.galois_loss - path.galois_loss) < 1e-10
        assert len(restored.witnesses) == len(path.witnesses)

    @given(witness=witness_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_witness_serialization_roundtrip(self, witness: DerivationWitness) -> None:
        """DerivationWitness survives to_dict/from_dict round-trip."""
        serialized = witness.to_dict()
        restored = DerivationWitness.from_dict(serialized)

        assert restored.witness_id == witness.witness_id
        assert restored.witness_type == witness.witness_type
        assert abs(restored.confidence - witness.confidence) < 1e-10
        assert restored.grounding_principle == witness.grounding_principle


# =============================================================================
# Loss Acceptability Tests
# =============================================================================


class TestLossAcceptability:
    """Tests for loss_is_acceptable helper."""

    @given(loss=st.floats(min_value=0.0, max_value=0.49))
    def test_low_loss_is_acceptable(self, loss: float) -> None:
        """Loss below threshold is acceptable."""
        assert loss_is_acceptable(loss, threshold=0.5)

    @given(loss=st.floats(min_value=0.51, max_value=1.0))
    def test_high_loss_not_acceptable(self, loss: float) -> None:
        """Loss above threshold is not acceptable."""
        assert not loss_is_acceptable(loss, threshold=0.5)


# =============================================================================
# Compose All Tests
# =============================================================================


class TestComposeAll:
    """Tests for compose_all helper function."""

    @given(paths=composable_path_triple_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_compose_all_matches_sequential(
        self, paths: tuple[DerivationPath, DerivationPath, DerivationPath]
    ) -> None:
        """compose_all should equal sequential composition."""
        p, q, r = paths

        via_compose_all = compose_all(p, q, r)
        via_sequential = p.compose(q).compose(r)

        assert via_compose_all.source_id == via_sequential.source_id
        assert via_compose_all.target_id == via_sequential.target_id
        assert abs(via_compose_all.galois_loss - via_sequential.galois_loss) < 1e-10

    def test_compose_all_requires_two_paths(self) -> None:
        """compose_all should raise for fewer than 2 paths."""
        path = DerivationPath.derive("a", "b")

        with pytest.raises(ValueError, match="at least 2 paths"):
            compose_all(path)
