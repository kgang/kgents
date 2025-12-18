"""
Tests for DIRECTOR_OPERAD.

Verifies the composition grammar for Punchdrunk Park director operations:
- Operation registration
- Law verification
- OperadRegistry compliance
- Composition functions

See: agents/park/operad.py
"""

from __future__ import annotations

import pytest
from agents.operad.core import LawStatus, OperadRegistry
from agents.park.operad import (
    DIRECTOR_OPERAD,
    create_director_operad,
)
from agents.poly import from_function

# ============================================================================
# Operad Structure Tests
# ============================================================================


class TestDirectorOperadStructure:
    """Test DIRECTOR_OPERAD structure and registration."""

    def test_operad_name(self) -> None:
        """Operad has correct name."""
        assert DIRECTOR_OPERAD.name == "DirectorOperad"

    def test_operad_description(self) -> None:
        """Operad has description."""
        assert DIRECTOR_OPERAD.description is not None
        assert "director" in DIRECTOR_OPERAD.description.lower()

    def test_operad_registered(self) -> None:
        """Operad is registered in OperadRegistry."""
        retrieved = OperadRegistry.get("DirectorOperad")
        assert retrieved is not None, "DirectorOperad not found in registry"
        assert retrieved is DIRECTOR_OPERAD

    def test_factory_creates_equivalent(self) -> None:
        """Factory creates structurally equivalent operad."""
        created = create_director_operad()
        assert created.name == DIRECTOR_OPERAD.name
        assert set(created.operations.keys()) == set(DIRECTOR_OPERAD.operations.keys())
        assert len(created.laws) == len(DIRECTOR_OPERAD.laws)


# ============================================================================
# Operation Tests
# ============================================================================


class TestDirectorOperations:
    """Test DIRECTOR_OPERAD operations."""

    def test_inherits_agent_operad_operations(self) -> None:
        """Director operad inherits from AGENT_OPERAD."""
        # Universal operations should be present
        assert "seq" in DIRECTOR_OPERAD.operations
        assert "par" in DIRECTOR_OPERAD.operations
        assert "branch" in DIRECTOR_OPERAD.operations

    def test_observation_operations(self) -> None:
        """Operad has observation operations."""
        assert "observe" in DIRECTOR_OPERAD.operations
        assert "evaluate" in DIRECTOR_OPERAD.operations

        observe = DIRECTOR_OPERAD.operations["observe"]
        assert observe.arity == 1
        assert observe.signature is not None

        evaluate = DIRECTOR_OPERAD.operations["evaluate"]
        assert evaluate.arity == 2

    def test_injection_operations(self) -> None:
        """Operad has injection operations."""
        assert "build_tension" in DIRECTOR_OPERAD.operations
        assert "inject" in DIRECTOR_OPERAD.operations
        assert "cooldown" in DIRECTOR_OPERAD.operations

        build_tension = DIRECTOR_OPERAD.operations["build_tension"]
        assert build_tension.arity == 1

        inject = DIRECTOR_OPERAD.operations["inject"]
        assert inject.arity == 2

        cooldown = DIRECTOR_OPERAD.operations["cooldown"]
        assert cooldown.arity == 1

    def test_control_operations(self) -> None:
        """Operad has control operations."""
        assert "intervene" in DIRECTOR_OPERAD.operations
        assert "director_reset" in DIRECTOR_OPERAD.operations
        assert "abort" in DIRECTOR_OPERAD.operations

        intervene = DIRECTOR_OPERAD.operations["intervene"]
        assert intervene.arity == 1

        director_reset = DIRECTOR_OPERAD.operations["director_reset"]
        assert director_reset.arity == 0

        abort = DIRECTOR_OPERAD.operations["abort"]
        assert abort.arity == 0

    def test_operation_count(self) -> None:
        """Operad has expected number of operations."""
        # AGENT_OPERAD has 5 base operations
        # Director adds: observe, evaluate, build_tension, inject, cooldown,
        #                intervene, director_reset, abort = 8
        # Total: 13
        assert len(DIRECTOR_OPERAD.operations) >= 13


# ============================================================================
# Law Tests
# ============================================================================


class TestDirectorLaws:
    """Test DIRECTOR_OPERAD laws."""

    def test_has_director_specific_laws(self) -> None:
        """Operad has director-specific laws."""
        law_names = {law.name for law in DIRECTOR_OPERAD.laws}

        # Director-specific laws
        assert "consent_constraint" in law_names
        assert "cooldown_constraint" in law_names
        assert "tension_flow" in law_names
        assert "intervention_isolation" in law_names
        assert "observe_identity" in law_names
        assert "reset_to_observe" in law_names

    def test_inherits_agent_operad_laws(self) -> None:
        """Operad inherits from AGENT_OPERAD laws."""
        law_names = {law.name for law in DIRECTOR_OPERAD.laws}

        # Should have universal laws from AGENT_OPERAD
        # (identity, associativity are common)
        assert len(law_names) >= 6  # At least our 6 director laws

    def test_consent_constraint_law_verifies(self) -> None:
        """Consent constraint law passes verification."""
        law = next(l for l in DIRECTOR_OPERAD.laws if l.name == "consent_constraint")

        verification = law.verify()
        assert verification.status == LawStatus.PASSED
        assert verification.law_name == "consent_constraint"

    def test_cooldown_constraint_law_verifies(self) -> None:
        """Cooldown constraint law passes verification."""
        law = next(l for l in DIRECTOR_OPERAD.laws if l.name == "cooldown_constraint")

        verification = law.verify()
        assert verification.status == LawStatus.PASSED

    def test_tension_flow_law_verifies(self) -> None:
        """Tension flow law passes verification."""
        law = next(l for l in DIRECTOR_OPERAD.laws if l.name == "tension_flow")

        verification = law.verify()
        assert verification.status == LawStatus.PASSED

    def test_intervention_isolation_law_verifies(self) -> None:
        """Intervention isolation law passes verification."""
        law = next(
            l for l in DIRECTOR_OPERAD.laws if l.name == "intervention_isolation"
        )

        verification = law.verify()
        assert verification.status == LawStatus.PASSED

    def test_observe_identity_law_verifies(self) -> None:
        """Observe identity law passes verification."""
        law = next(l for l in DIRECTOR_OPERAD.laws if l.name == "observe_identity")

        verification = law.verify()
        assert verification.status == LawStatus.PASSED

    def test_reset_to_observe_law_verifies(self) -> None:
        """Reset to observe law passes verification."""
        law = next(l for l in DIRECTOR_OPERAD.laws if l.name == "reset_to_observe")

        verification = law.verify()
        assert verification.status == LawStatus.PASSED

    def test_all_laws_have_equations(self) -> None:
        """All laws have equation descriptions."""
        for law in DIRECTOR_OPERAD.laws:
            assert law.equation is not None, f"Law {law.name} missing equation"

    def test_all_laws_have_descriptions(self) -> None:
        """All laws have human-readable descriptions."""
        for law in DIRECTOR_OPERAD.laws:
            assert law.description is not None, f"Law {law.name} missing description"


# ============================================================================
# Composition Tests
# ============================================================================


class TestDirectorComposition:
    """Test DIRECTOR_OPERAD composition functions."""

    def test_observe_compose(self) -> None:
        """Observe operation composes correctly."""
        observe_op = DIRECTOR_OPERAD.operations["observe"]
        session = from_function("test_session", lambda x: x)

        composed = observe_op.compose(session)
        assert composed is not None
        assert "observe" in composed.name

        # from_function creates PolyAgent with "ready" state
        # invoke(state, input) returns (new_state, output)
        _, result = composed.invoke("ready", {"metrics": "test"})
        assert result["operation"] == "observe"
        assert result["session"] == "test_session"

    def test_inject_compose(self) -> None:
        """Inject operation composes correctly."""
        inject_op = DIRECTOR_OPERAD.operations["inject"]
        injection = from_function("test_injection", lambda x: x)
        session = from_function("test_session", lambda x: x)

        composed = inject_op.compose(injection, session)
        assert composed is not None
        assert "inject" in composed.name

        _, result = composed.invoke("ready", {})
        assert result["operation"] == "inject"
        assert result["injection"] == "test_injection"
        assert result["session"] == "test_session"

    def test_cooldown_compose(self) -> None:
        """Cooldown operation composes correctly."""
        cooldown_op = DIRECTOR_OPERAD.operations["cooldown"]
        duration = from_function("duration_60", lambda x: 60)

        composed = cooldown_op.compose(duration)
        assert composed is not None

        _, result = composed.invoke("ready", 60)
        assert result["operation"] == "cooldown"
        assert result["duration"] == 60

    def test_reset_compose_is_nullary(self) -> None:
        """Reset operation is nullary (takes no arguments)."""
        reset_op = DIRECTOR_OPERAD.operations["director_reset"]

        composed = reset_op.compose()
        assert composed is not None

        _, result = composed.invoke("ready", None)
        assert result["operation"] == "reset"
        assert result["signal"] == "observe"

    def test_evaluate_compose(self) -> None:
        """Evaluate operation composes correctly."""
        evaluate_op = DIRECTOR_OPERAD.operations["evaluate"]
        metrics = from_function("metrics", lambda x: x)
        config = from_function("config", lambda x: x)

        composed = evaluate_op.compose(metrics, config)
        assert composed is not None

        _, result = composed.invoke("ready", {})
        assert result["operation"] == "evaluate"
        assert result["metrics"] == "metrics"
        assert result["config"] == "config"


# ============================================================================
# Integration Tests
# ============================================================================


class TestDirectorOperadIntegration:
    """Test DIRECTOR_OPERAD integration with polynomial."""

    def test_operad_compatible_with_polynomial(self) -> None:
        """Operad operations align with DIRECTOR_POLYNOMIAL phases."""
        from agents.park.director import DirectorPhase

        # The operad should have operations for each major phase transition
        phases = set(DirectorPhase)
        ops = DIRECTOR_OPERAD.operations

        # OBSERVING: observe
        assert "observe" in ops
        # BUILDING_TENSION: build_tension, evaluate
        assert "build_tension" in ops
        assert "evaluate" in ops
        # INJECTING: inject
        assert "inject" in ops
        # COOLDOWN: cooldown
        assert "cooldown" in ops
        # INTERVENING: intervene
        assert "intervene" in ops
        # Reset: director_reset
        assert "director_reset" in ops

    def test_verify_all_laws(self) -> None:
        """All director-specific laws pass verification."""
        # Only test director-specific laws (which have no-arg verify functions)
        director_law_names = {
            "consent_constraint",
            "cooldown_constraint",
            "tension_flow",
            "intervention_isolation",
            "observe_identity",
            "reset_to_observe",
        }
        for law in DIRECTOR_OPERAD.laws:
            if law.name in director_law_names:
                verification = law.verify()
                assert verification.status in (LawStatus.PASSED, LawStatus.SKIPPED), (
                    f"Law {law.name} failed: {verification.message}"
                )


# ============================================================================
# Registry CI Gate Tests
# ============================================================================


class TestRegistryCIGate:
    """Tests that verify CI gate compliance."""

    def test_canonical_types_used(self) -> None:
        """Verify canonical types from operad/core.py are used."""
        from agents.operad.core import Law as CanonicalLaw
        from agents.operad.core import Operad as CanonicalOperad
        from agents.operad.core import Operation as CanonicalOperation

        # Check type of operad
        assert isinstance(DIRECTOR_OPERAD, CanonicalOperad)

        # Check type of operations
        for op in DIRECTOR_OPERAD.operations.values():
            assert isinstance(op, CanonicalOperation), (
                f"{op.name} not canonical Operation"
            )

        # Check type of laws
        for law in DIRECTOR_OPERAD.laws:
            assert isinstance(law, CanonicalLaw), f"{law.name} not canonical Law"

    def test_registry_lookup_idempotent(self) -> None:
        """Registry lookup returns same instance."""
        first = OperadRegistry.get("DirectorOperad")
        second = OperadRegistry.get("DirectorOperad")
        assert first is second

    def test_no_duplicate_registration(self) -> None:
        """Re-registration doesn't duplicate."""
        # This is already handled by OperadRegistry but verify
        initial_count = len(OperadRegistry.all_operads())

        # Re-import (would trigger re-registration if not guarded)
        from agents.park import operad as _  # noqa: F401

        final_count = len(OperadRegistry.all_operads())
        assert final_count == initial_count
