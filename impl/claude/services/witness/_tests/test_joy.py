"""
Tests for the JoyPoly Functor.

Tests the categorical joy functor implementation:
- JoyMode enum validation
- JoyObservation creation and composition
- JoyFunctor domain weighting
- Composition law verification (associativity, identity)
- Trail-to-crystal calibration

Philosophy:
    "Joy is not a scalar metric to maximize. Joy is a behavioral pattern that composes."
"""

import pytest

from services.witness.joy import (
    TRAIL_TO_CRYSTAL_JOY,
    JoyCompositionLaws,
    JoyFunctor,
    JoyMode,
    JoyObservation,
    UniversalDelightPrimitive,
    warmth_response,
)

# =============================================================================
# JoyMode Tests
# =============================================================================


class TestJoyMode:
    """Tests for JoyMode enum."""

    def test_all_modes_exist(self) -> None:
        """All three joy modes are present."""
        assert JoyMode.WARMTH.value == "warmth"
        assert JoyMode.SURPRISE.value == "surprise"
        assert JoyMode.FLOW.value == "flow"

    def test_mode_count(self) -> None:
        """Exactly three joy modes exist (no more, no less)."""
        assert len(JoyMode) == 3


# =============================================================================
# JoyObservation Tests
# =============================================================================


class TestJoyObservation:
    """Tests for JoyObservation dataclass."""

    def test_create_observation(self) -> None:
        """Can create a joy observation."""
        obs = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.7,
            observer="user",
            trigger="collaboration",
        )
        assert obs.mode == JoyMode.WARMTH
        assert obs.intensity == 0.7
        assert obs.observer == "user"
        assert obs.trigger == "collaboration"

    def test_intensity_validation_lower_bound(self) -> None:
        """Intensity below 0 raises ValueError."""
        with pytest.raises(ValueError, match="intensity must be in"):
            JoyObservation(
                mode=JoyMode.FLOW,
                intensity=-0.1,
                observer="user",
                trigger="test",
            )

    def test_intensity_validation_upper_bound(self) -> None:
        """Intensity above 1 raises ValueError."""
        with pytest.raises(ValueError, match="intensity must be in"):
            JoyObservation(
                mode=JoyMode.FLOW,
                intensity=1.1,
                observer="user",
                trigger="test",
            )

    def test_intensity_boundary_values(self) -> None:
        """Intensity at boundaries (0 and 1) is valid."""
        low = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.0,
            observer="user",
            trigger="test",
        )
        high = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=1.0,
            observer="user",
            trigger="test",
        )
        assert low.intensity == 0.0
        assert high.intensity == 1.0

    def test_repr(self) -> None:
        """String representation is human-readable."""
        obs = JoyObservation(
            mode=JoyMode.SURPRISE,
            intensity=0.5,
            observer="user",
            trigger="discovery",
        )
        repr_str = repr(obs)
        assert "Joy(" in repr_str
        assert "surprise" in repr_str
        assert "0.50" in repr_str
        assert "discovery" in repr_str

    def test_identity_element(self) -> None:
        """Identity element has zero intensity (for max-based composition)."""
        identity = JoyObservation.identity("user")
        assert identity.intensity == 0.0  # Identity under max is 0
        assert identity.trigger == "identity"
        assert identity.observer == "user"

    def test_composition_operator(self) -> None:
        """The >> operator composes joy observations."""
        a = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.8,
            observer="user",
            trigger="connection",
        )
        b = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.6,
            observer="user",
            trigger="practice",
        )

        composed = a >> b
        assert isinstance(composed, JoyObservation)
        assert composed.observer == "user"
        assert ">>" in composed.trigger


# =============================================================================
# JoyFunctor Tests
# =============================================================================


class TestJoyFunctor:
    """Tests for JoyFunctor."""

    def test_create_functor_with_weights(self) -> None:
        """Can create a functor with domain weights."""
        functor = JoyFunctor({
            JoyMode.WARMTH: 0.5,
            JoyMode.SURPRISE: 0.3,
            JoyMode.FLOW: 0.2,
        })
        assert functor.domain_weights[JoyMode.WARMTH] == 0.5
        assert functor.domain_weights[JoyMode.SURPRISE] == 0.3
        assert functor.domain_weights[JoyMode.FLOW] == 0.2

    def test_create_functor_with_defaults(self) -> None:
        """Missing weights default to ~0.33."""
        functor = JoyFunctor({})
        assert functor.domain_weights[JoyMode.WARMTH] == 0.33
        assert functor.domain_weights[JoyMode.SURPRISE] == 0.33
        assert functor.domain_weights[JoyMode.FLOW] == 0.34

    def test_observe_returns_dominant_mode(self) -> None:
        """Observation returns the weighted-dominant mode."""
        # Flow-heavy functor
        functor = JoyFunctor({
            JoyMode.FLOW: 0.8,
            JoyMode.WARMTH: 0.1,
            JoyMode.SURPRISE: 0.1,
        })

        # Even with high warmth signal, flow dominates due to weights
        obs = functor.observe(
            observer="user",
            warmth=0.9,
            surprise=0.5,
            flow=0.6,
        )

        # Flow (0.6 * 0.8 = 0.48) beats warmth (0.9 * 0.1 = 0.09)
        assert obs.mode == JoyMode.FLOW

    def test_observe_with_trigger(self) -> None:
        """Observation can include custom trigger."""
        functor = JoyFunctor({})
        obs = functor.observe(
            observer="user",
            warmth=0.5,
            surprise=0.5,
            flow=0.5,
            trigger="custom event",
        )
        assert obs.trigger == "custom event"

    def test_compose_intensity_formula(self) -> None:
        """Composition uses max for associativity: max(a, b)."""
        functor = JoyFunctor({})

        domain_joy = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.8,
            observer="user",
            trigger="domain",
        )
        universal = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.4,
            observer="user",
            trigger="universal",
        )

        composed = functor.compose(domain_joy, universal)

        # max(0.8, 0.4) = 0.8
        assert abs(composed.intensity - 0.8) < 0.01

    def test_compose_mode_from_dominant(self) -> None:
        """Composed mode comes from higher intensity observation."""
        functor = JoyFunctor({})

        high_warmth = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.9,
            observer="user",
            trigger="high warmth",
        )
        low_flow = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.3,
            observer="user",
            trigger="low flow",
        )

        composed = functor.compose(high_warmth, low_flow)
        assert composed.mode == JoyMode.WARMTH  # Higher intensity wins

    def test_compose_preserves_observer(self) -> None:
        """Composition preserves the domain observer."""
        functor = JoyFunctor({})

        a = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.5,
            observer="alice",
            trigger="a",
        )
        b = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.5,
            observer="bob",  # Different observer
            trigger="b",
        )

        composed = functor.compose(a, b)
        assert composed.observer == "alice"  # Preserves domain observer

    def test_compose_builds_trigger_chain(self) -> None:
        """Composition builds a trigger chain."""
        functor = JoyFunctor({})

        a = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.5,
            observer="user",
            trigger="connection",
        )
        b = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.5,
            observer="user",
            trigger="practice",
        )

        composed = functor.compose(a, b)
        assert "connection" in composed.trigger
        assert "practice" in composed.trigger
        assert ">>" in composed.trigger


# =============================================================================
# Composition Law Tests
# =============================================================================


class TestJoyCompositionLaws:
    """Tests for joy composition laws."""

    def test_associativity(self) -> None:
        """
        Verify: (a >> b) >> c == a >> (b >> c).

        Associativity must hold for categorical composition.
        """
        a = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.7,
            observer="user",
            trigger="a",
        )
        b = JoyObservation(
            mode=JoyMode.SURPRISE,
            intensity=0.5,
            observer="user",
            trigger="b",
        )
        c = JoyObservation(
            mode=JoyMode.FLOW,
            intensity=0.8,
            observer="user",
            trigger="c",
        )

        assert JoyCompositionLaws.verify_associativity(a, b, c)

    def test_associativity_various_values(self) -> None:
        """Associativity holds for various intensity values."""
        test_cases = [
            (0.1, 0.2, 0.3),
            (0.9, 0.8, 0.7),
            (0.5, 0.5, 0.5),
            (0.0, 0.5, 1.0),
            (1.0, 0.0, 0.5),
        ]

        for i1, i2, i3 in test_cases:
            a = JoyObservation(JoyMode.WARMTH, i1, "user", "a")
            b = JoyObservation(JoyMode.SURPRISE, i2, "user", "b")
            c = JoyObservation(JoyMode.FLOW, i3, "user", "c")

            assert JoyCompositionLaws.verify_associativity(a, b, c), (
                f"Associativity failed for intensities ({i1}, {i2}, {i3})"
            )

    def test_identity_symmetry(self) -> None:
        """
        Verify: id >> a == a == a >> id.

        Under max-based composition:
        max(0, x) == x == max(x, 0)
        """
        a = JoyObservation(
            mode=JoyMode.WARMTH,
            intensity=0.7,
            observer="user",
            trigger="test",
        )

        assert JoyCompositionLaws.verify_identity(a)

    def test_joy_witness_identity(self) -> None:
        """Joy >> Witness = Witness (definitionally true)."""
        assert JoyCompositionLaws.joy_witness_identity()

    def test_compression_asymmetry(self) -> None:
        """Compression >> Joy != Joy >> Compression (intentionally asymmetric)."""
        # This law explicitly returns False to indicate asymmetry
        assert not JoyCompositionLaws.compression_asymmetry()


# =============================================================================
# Universal Delight Primitive Tests
# =============================================================================


class TestUniversalDelightPrimitive:
    """Tests for universal delight primitives."""

    def test_all_primitives_exist(self) -> None:
        """All five universal primitives are present."""
        assert UniversalDelightPrimitive.RECOGNITION.value == "recognition"
        assert UniversalDelightPrimitive.MASTERY.value == "mastery"
        assert UniversalDelightPrimitive.CLOSURE.value == "closure"
        assert UniversalDelightPrimitive.DISCOVERY.value == "discovery"
        assert UniversalDelightPrimitive.CONNECTION.value == "connection"

    def test_primitive_count(self) -> None:
        """Exactly five primitives exist."""
        assert len(UniversalDelightPrimitive) == 5

    def test_primitive_to_joy_mode(self) -> None:
        """Primitives map to expected joy modes."""
        assert (
            UniversalDelightPrimitive.RECOGNITION.to_joy_mode() == JoyMode.WARMTH
        )
        assert (
            UniversalDelightPrimitive.MASTERY.to_joy_mode() == JoyMode.FLOW
        )
        assert (
            UniversalDelightPrimitive.CLOSURE.to_joy_mode() == JoyMode.FLOW
        )
        assert (
            UniversalDelightPrimitive.DISCOVERY.to_joy_mode() == JoyMode.SURPRISE
        )
        assert (
            UniversalDelightPrimitive.CONNECTION.to_joy_mode() == JoyMode.WARMTH
        )


# =============================================================================
# Trail-to-Crystal Calibration Tests
# =============================================================================


class TestTrailToCrystalCalibration:
    """Tests for trail-to-crystal pilot joy calibration."""

    def test_calibration_exists(self) -> None:
        """TRAIL_TO_CRYSTAL_JOY functor is defined."""
        assert TRAIL_TO_CRYSTAL_JOY is not None
        assert isinstance(TRAIL_TO_CRYSTAL_JOY, JoyFunctor)

    def test_flow_is_primary(self) -> None:
        """Flow is the primary joy mode (highest weight)."""
        weights = TRAIL_TO_CRYSTAL_JOY.domain_weights
        assert weights[JoyMode.FLOW] == 0.5

    def test_warmth_is_secondary(self) -> None:
        """Warmth is the secondary joy mode."""
        weights = TRAIL_TO_CRYSTAL_JOY.domain_weights
        assert weights[JoyMode.WARMTH] == 0.35

    def test_surprise_is_tertiary(self) -> None:
        """Surprise is the tertiary joy mode."""
        weights = TRAIL_TO_CRYSTAL_JOY.domain_weights
        assert weights[JoyMode.SURPRISE] == 0.15

    def test_weights_sum_to_one(self) -> None:
        """All weights sum to 1.0."""
        weights = TRAIL_TO_CRYSTAL_JOY.domain_weights
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01

    def test_flow_dominates_observation(self) -> None:
        """With calibration, equal signals produce flow-dominant observation."""
        # Equal raw signals
        obs = TRAIL_TO_CRYSTAL_JOY.observe(
            observer="user",
            warmth=0.6,
            surprise=0.6,
            flow=0.6,
        )

        # Flow should dominate due to 0.5 weight
        # flow: 0.6 * 0.5 = 0.30
        # warmth: 0.6 * 0.35 = 0.21
        # surprise: 0.6 * 0.15 = 0.09
        assert obs.mode == JoyMode.FLOW


# =============================================================================
# Warmth Response Tests
# =============================================================================


class TestWarmthResponse:
    """Tests for warmth_response generator."""

    def test_high_intensity_warmth(self) -> None:
        """High warmth intensity produces connection response."""
        obs = JoyObservation(JoyMode.WARMTH, 0.8, "user", "test")
        response = warmth_response(obs)
        assert "connection" in response.lower()

    def test_high_intensity_surprise(self) -> None:
        """High surprise intensity produces unexpected response."""
        obs = JoyObservation(JoyMode.SURPRISE, 0.8, "user", "test")
        response = warmth_response(obs)
        assert "unexpected" in response.lower()

    def test_high_intensity_flow(self) -> None:
        """High flow intensity produces groove response."""
        obs = JoyObservation(JoyMode.FLOW, 0.8, "user", "test")
        response = warmth_response(obs)
        assert "groove" in response.lower()

    def test_medium_intensity_responses(self) -> None:
        """Medium intensity produces appropriate responses."""
        medium_warmth = JoyObservation(JoyMode.WARMTH, 0.5, "user", "test")
        medium_surprise = JoyObservation(JoyMode.SURPRISE, 0.5, "user", "test")
        medium_flow = JoyObservation(JoyMode.FLOW, 0.5, "user", "test")

        assert warmth_response(medium_warmth) != ""
        assert warmth_response(medium_surprise) != ""
        assert warmth_response(medium_flow) != ""

    def test_low_intensity_responses(self) -> None:
        """Low intensity produces minimal but warm responses."""
        low_warmth = JoyObservation(JoyMode.WARMTH, 0.2, "user", "test")
        low_surprise = JoyObservation(JoyMode.SURPRISE, 0.2, "user", "test")
        low_flow = JoyObservation(JoyMode.FLOW, 0.2, "user", "test")

        # Low responses should still be warm (not punitive)
        assert warmth_response(low_warmth) in ["Noted.", "Captured.", "Got it."]
        assert warmth_response(low_surprise) in ["Noted.", "Captured.", "Got it."]
        assert warmth_response(low_flow) in ["Noted.", "Captured.", "Got it."]

    def test_responses_not_punitive(self) -> None:
        """All responses avoid punitive language."""
        punitive_patterns = ["error", "failed", "invalid", "wrong", "bad"]

        for mode in JoyMode:
            for intensity in [0.1, 0.5, 0.9]:
                obs = JoyObservation(mode, intensity, "user", "test")
                response = warmth_response(obs).lower()

                for pattern in punitive_patterns:
                    assert pattern not in response, (
                        f"Punitive pattern '{pattern}' found in response for "
                        f"{mode.value} at intensity {intensity}: {response}"
                    )
