"""
Tests for Pilot Law Grammar (Amendment G).

Verifies that:
1. The five law schemas are correctly defined
2. Pilot laws properly derive from schemas
3. Verification functions correctly evaluate laws
4. Registry functions work as expected
"""

import pytest

from services.categorical.pilot_laws import (
    # Registry
    PILOT_LAWS,
    # Enums
    LawSchema,
    LawVerificationReport,
    LawVerificationResult,
    # Core types
    PilotLaw,
    # Schema predicates
    coherence_gate,
    compression_honesty,
    courage_preservation,
    drift_alert,
    get_all_pilots,
    get_law_by_name,
    # Registry utilities
    get_laws_by_pilot,
    get_laws_by_schema,
    ghost_preservation,
    summarize_pilot_laws,
    verify_all_laws,
    # Verification functions
    verify_law,
    verify_pilot_laws,
    verify_schema_laws,
)

# =============================================================================
# Test LawSchema
# =============================================================================


class TestLawSchema:
    """Test the five law schemas."""

    def test_all_schemas_defined(self):
        """All five schemas should be defined."""
        expected_schemas = {
            "coherence_gate",
            "drift_alert",
            "ghost_preservation",
            "courage_preservation",
            "compression_honesty",
        }
        actual_schemas = {s.value for s in LawSchema}
        assert actual_schemas == expected_schemas

    def test_schema_enum_values(self):
        """Schema enum values should match names."""
        assert LawSchema.COHERENCE_GATE.value == "coherence_gate"
        assert LawSchema.DRIFT_ALERT.value == "drift_alert"
        assert LawSchema.GHOST_PRESERVATION.value == "ghost_preservation"
        assert LawSchema.COURAGE_PRESERVATION.value == "courage_preservation"
        assert LawSchema.COMPRESSION_HONESTY.value == "compression_honesty"


# =============================================================================
# Test Schema Predicates
# =============================================================================


class TestCoherenceGate:
    """Test COHERENCE_GATE predicate."""

    def test_action_in_marked_types(self):
        """Action should pass if it's in marked types."""
        result = coherence_gate(
            action_type="build",
            marked_types=["build", "deploy"],
        )
        assert result is True

    def test_action_not_in_marked_types(self):
        """Action should fail if it's not in marked types."""
        result = coherence_gate(
            action_type="test",
            marked_types=["build", "deploy"],
        )
        assert result is False

    def test_has_prerequisite_true(self):
        """Direct prerequisite check should work."""
        result = coherence_gate(has_prerequisite=True)
        assert result is True

    def test_has_prerequisite_false(self):
        """Direct prerequisite check should work."""
        result = coherence_gate(has_prerequisite=False)
        assert result is False

    def test_empty_marked_types(self):
        """Empty marked types should fail any action type."""
        result = coherence_gate(
            action_type="build",
            marked_types=[],
        )
        assert result is False

    def test_no_arguments_defaults_true(self):
        """No valid arguments should default to True."""
        result = coherence_gate()
        assert result is True


class TestDriftAlert:
    """Test DRIFT_ALERT predicate."""

    def test_below_threshold_passes(self):
        """Loss below threshold should pass regardless of surfaced."""
        result = drift_alert(current_loss=0.3, threshold=0.5, surfaced=False)
        assert result is True

    def test_above_threshold_surfaced_passes(self):
        """Loss above threshold passes if surfaced."""
        result = drift_alert(current_loss=0.6, threshold=0.5, surfaced=True)
        assert result is True

    def test_above_threshold_not_surfaced_fails(self):
        """Loss above threshold fails if not surfaced."""
        result = drift_alert(current_loss=0.6, threshold=0.5, surfaced=False)
        assert result is False

    def test_canon_check_high_loss(self):
        """High loss cannot be in canon."""
        result = drift_alert(current_loss=0.6, threshold=0.5, in_canon=True)
        assert result is False

    def test_canon_check_high_loss_not_in_canon(self):
        """High loss not in canon is OK."""
        result = drift_alert(current_loss=0.6, threshold=0.5, in_canon=False)
        assert result is True

    def test_canon_check_low_loss(self):
        """Low loss can be in canon."""
        result = drift_alert(current_loss=0.3, threshold=0.5, in_canon=True)
        assert result is True


class TestGhostPreservation:
    """Test GHOST_PRESERVATION predicate."""

    def test_all_ghosts_inspectable(self):
        """All unchosen paths should be inspectable."""
        result = ghost_preservation(
            unchosen_paths=["path_a", "path_b"],
            inspectable_paths=["path_a", "path_b", "path_c"],
        )
        assert result is True

    def test_missing_ghost(self):
        """Missing ghost paths should fail."""
        result = ghost_preservation(
            unchosen_paths=["path_a", "path_b"],
            inspectable_paths=["path_a"],  # path_b missing
        )
        assert result is False

    def test_no_ghosts(self):
        """No unchosen paths is OK."""
        result = ghost_preservation(
            unchosen_paths=[],
            inspectable_paths=["path_a"],
        )
        assert result is True

    def test_direct_preserved_flag(self):
        """Direct ghosts_preserved flag should work."""
        assert ghost_preservation(ghosts_preserved=True) is True
        assert ghost_preservation(ghosts_preserved=False) is False


class TestCouragePreservation:
    """Test COURAGE_PRESERVATION predicate."""

    def test_high_risk_no_penalty(self):
        """High-risk actions should not receive penalties."""
        result = courage_preservation(
            risk_level=0.8,
            penalty_applied=0.0,
            risk_threshold=0.7,
        )
        assert result is True

    def test_high_risk_with_penalty_fails(self):
        """High-risk actions with penalties should fail."""
        result = courage_preservation(
            risk_level=0.8,
            penalty_applied=0.1,
            risk_threshold=0.7,
        )
        assert result is False

    def test_low_risk_with_penalty_ok(self):
        """Low-risk actions can have penalties."""
        result = courage_preservation(
            risk_level=0.3,
            penalty_applied=0.5,
            risk_threshold=0.7,
        )
        assert result is True

    def test_direct_protected_flag(self):
        """Direct is_protected flag should work."""
        assert courage_preservation(is_protected=True) is True
        assert courage_preservation(is_protected=False) is False


class TestCompressionHonesty:
    """Test COMPRESSION_HONESTY predicate."""

    def test_all_drops_disclosed(self):
        """All dropped elements should be disclosed."""
        result = compression_honesty(
            original_elements={"a", "b", "c"},
            crystal_elements={"a"},
            disclosed_elements={"b", "c"},
        )
        assert result is True

    def test_missing_disclosure(self):
        """Missing disclosures should fail."""
        result = compression_honesty(
            original_elements={"a", "b", "c"},
            crystal_elements={"a"},
            disclosed_elements={"b"},  # "c" not disclosed
        )
        assert result is False

    def test_nothing_dropped(self):
        """No drops means nothing to disclose."""
        result = compression_honesty(
            original_elements={"a", "b"},
            crystal_elements={"a", "b"},
            disclosed_elements=set(),
        )
        assert result is True

    def test_direct_drops_disclosed_flag(self):
        """Direct drops_disclosed flag should work."""
        assert compression_honesty(drops_disclosed=True) is True
        assert compression_honesty(drops_disclosed=False) is False


# =============================================================================
# Test PilotLaw
# =============================================================================


class TestPilotLaw:
    """Test PilotLaw data structure."""

    def test_verify_passes(self):
        """verify() should pass when predicate returns True."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test Law",
            description="A test law",
            predicate=lambda has_crystal=False: has_crystal,
        )

        assert law.verify(has_crystal=True) is True
        assert law.verify(has_crystal=False) is False

    def test_verify_handles_exception(self):
        """verify() should return False on exception."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test Law",
            description="A test law",
            predicate=lambda: 1 / 0,  # Will raise
        )

        assert law.verify() is False

    def test_to_dict(self):
        """to_dict() should serialize law (excluding predicate)."""
        law = PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="test-pilot",
            name="Test Law",
            description="Description",
            predicate=lambda: True,
            metadata={"key": "value"},
        )

        d = law.to_dict()

        assert d["schema"] == "drift_alert"
        assert d["pilot"] == "test-pilot"
        assert d["name"] == "Test Law"
        assert d["description"] == "Description"
        assert d["metadata"] == {"key": "value"}
        assert "predicate" not in d


# =============================================================================
# Test PILOT_LAWS Registry
# =============================================================================


class TestPilotLawsRegistry:
    """Test the PILOT_LAWS registry."""

    def test_registry_not_empty(self):
        """Registry should contain laws."""
        assert len(PILOT_LAWS) > 0

    def test_all_laws_are_pilot_laws(self):
        """All entries should be PilotLaw instances."""
        for law in PILOT_LAWS:
            assert isinstance(law, PilotLaw)

    def test_all_schemas_represented(self):
        """All five schemas should have at least one law."""
        schemas_used = {law.schema for law in PILOT_LAWS}
        assert LawSchema.COHERENCE_GATE in schemas_used
        assert LawSchema.DRIFT_ALERT in schemas_used
        assert LawSchema.GHOST_PRESERVATION in schemas_used
        assert LawSchema.COURAGE_PRESERVATION in schemas_used
        assert LawSchema.COMPRESSION_HONESTY in schemas_used

    def test_known_pilots_present(self):
        """Known pilots should be in the registry."""
        pilots = {law.pilot for law in PILOT_LAWS}
        expected_pilots = {
            "trail-to-crystal",
            "wasm-survivors",
            "disney-portal",
            "rap-coach",
            "sprite-procedural",
        }
        for pilot in expected_pilots:
            assert pilot in pilots, f"Missing pilot: {pilot}"


# =============================================================================
# Test Verification Functions
# =============================================================================


class TestVerifyLaw:
    """Test verify_law function."""

    def test_verify_passing_law(self):
        """verify_law should return passed=True for passing context."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test Law",
            description="Test",
            predicate=lambda has_crystal=False, **kw: has_crystal,
        )

        result = verify_law(law, {"has_crystal": True})

        assert result.passed is True
        assert result.law is law
        assert result.error_message is None

    def test_verify_failing_law(self):
        """verify_law should return passed=False for failing context."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test Law",
            description="Test",
            predicate=lambda has_crystal=False, **kw: has_crystal,
        )

        result = verify_law(law, {"has_crystal": False})

        assert result.passed is False

    def test_verify_with_exception(self):
        """verify_law should handle exceptions gracefully."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test Law",
            description="Test",
            predicate=lambda: 1 / 0,  # Will raise
        )

        result = verify_law(law, {})

        assert result.passed is False
        assert result.error_message is not None


class TestVerifyAllLaws:
    """Test verify_all_laws function."""

    def test_returns_dict(self):
        """verify_all_laws should return law name -> bool mapping."""
        context = {
            "trail-to-crystal": {"has_crystal": True},
            "wasm-survivors": {
                "action_type": "build",
                "marked_types": ["build"],
                "current_loss": 0.3,
                "threshold": 0.5,
                "surfaced": True,
            },
        }

        results = verify_all_laws(context)

        assert isinstance(results, dict)
        assert all(isinstance(k, str) for k in results.keys())
        assert all(isinstance(v, bool) for v in results.values())

    def test_all_laws_verified(self):
        """All registered laws should have verification results."""
        results = verify_all_laws({})

        law_names = {law.name for law in PILOT_LAWS}
        for name in law_names:
            assert name in results


class TestVerifyPilotLaws:
    """Test verify_pilot_laws function."""

    def test_filters_by_pilot(self):
        """Should only verify laws for specified pilot."""
        context = {"has_crystal": True}

        report = verify_pilot_laws("trail-to-crystal", context)

        for result in report.results:
            assert result.law.pilot == "trail-to-crystal"

    def test_returns_report(self):
        """Should return LawVerificationReport."""
        report = verify_pilot_laws("trail-to-crystal", {})

        assert isinstance(report, LawVerificationReport)


class TestVerifySchemaLaws:
    """Test verify_schema_laws function."""

    def test_filters_by_schema(self):
        """Should only verify laws for specified schema."""
        context = {"has_crystal": True}

        report = verify_schema_laws(LawSchema.COHERENCE_GATE, context)

        for result in report.results:
            assert result.law.schema == LawSchema.COHERENCE_GATE

    def test_returns_report(self):
        """Should return LawVerificationReport."""
        report = verify_schema_laws(LawSchema.DRIFT_ALERT, {})

        assert isinstance(report, LawVerificationReport)


# =============================================================================
# Test LawVerificationReport
# =============================================================================


class TestLawVerificationReport:
    """Test LawVerificationReport data structure."""

    def test_all_passed(self):
        """all_passed should be True if all laws pass."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test",
            description="Test",
            predicate=lambda: True,
        )
        results = [
            LawVerificationResult(law=law, passed=True),
            LawVerificationResult(law=law, passed=True),
        ]
        report = LawVerificationReport(results=results)

        assert report.all_passed is True

    def test_all_passed_with_failure(self):
        """all_passed should be False if any law fails."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test",
            description="Test",
            predicate=lambda: True,
        )
        results = [
            LawVerificationResult(law=law, passed=True),
            LawVerificationResult(law=law, passed=False),
        ]
        report = LawVerificationReport(results=results)

        assert report.all_passed is False

    def test_pass_fail_counts(self):
        """pass_count and fail_count should be correct."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test",
            description="Test",
            predicate=lambda: True,
        )
        results = [
            LawVerificationResult(law=law, passed=True),
            LawVerificationResult(law=law, passed=True),
            LawVerificationResult(law=law, passed=False),
        ]
        report = LawVerificationReport(results=results)

        assert report.pass_count == 2
        assert report.fail_count == 1

    def test_failures(self):
        """failures should return only failed verifications."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test",
            description="Test",
            predicate=lambda: True,
        )
        passed = LawVerificationResult(law=law, passed=True)
        failed = LawVerificationResult(law=law, passed=False)
        results = [passed, failed]
        report = LawVerificationReport(results=results)

        assert report.failures == [failed]

    def test_by_pilot(self):
        """by_pilot should group results by pilot."""
        law1 = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="pilot-a",
            name="Test1",
            description="Test",
            predicate=lambda: True,
        )
        law2 = PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="pilot-b",
            name="Test2",
            description="Test",
            predicate=lambda: True,
        )
        results = [
            LawVerificationResult(law=law1, passed=True),
            LawVerificationResult(law=law2, passed=True),
        ]
        report = LawVerificationReport(results=results)

        by_pilot = report.by_pilot
        assert "pilot-a" in by_pilot
        assert "pilot-b" in by_pilot

    def test_by_schema(self):
        """by_schema should group results by schema."""
        law1 = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test1",
            description="Test",
            predicate=lambda: True,
        )
        law2 = PilotLaw(
            schema=LawSchema.DRIFT_ALERT,
            pilot="test",
            name="Test2",
            description="Test",
            predicate=lambda: True,
        )
        results = [
            LawVerificationResult(law=law1, passed=True),
            LawVerificationResult(law=law2, passed=True),
        ]
        report = LawVerificationReport(results=results)

        by_schema = report.by_schema
        assert LawSchema.COHERENCE_GATE in by_schema
        assert LawSchema.DRIFT_ALERT in by_schema

    def test_to_dict(self):
        """to_dict should serialize report."""
        law = PilotLaw(
            schema=LawSchema.COHERENCE_GATE,
            pilot="test",
            name="Test",
            description="Test",
            predicate=lambda: True,
        )
        results = [LawVerificationResult(law=law, passed=True)]
        report = LawVerificationReport(results=results)

        d = report.to_dict()

        assert "verified_at" in d
        assert "all_passed" in d
        assert "pass_count" in d
        assert "fail_count" in d
        assert "results" in d


# =============================================================================
# Test Registry Utilities
# =============================================================================


class TestRegistryUtilities:
    """Test registry utility functions."""

    def test_get_laws_by_pilot(self):
        """get_laws_by_pilot should filter correctly."""
        laws = get_laws_by_pilot("trail-to-crystal")

        assert len(laws) > 0
        for law in laws:
            assert law.pilot == "trail-to-crystal"

    def test_get_laws_by_pilot_unknown(self):
        """Unknown pilot should return empty list."""
        laws = get_laws_by_pilot("unknown-pilot")
        assert laws == []

    def test_get_laws_by_schema(self):
        """get_laws_by_schema should filter correctly."""
        laws = get_laws_by_schema(LawSchema.DRIFT_ALERT)

        assert len(laws) > 0
        for law in laws:
            assert law.schema == LawSchema.DRIFT_ALERT

    def test_get_all_pilots(self):
        """get_all_pilots should return sorted unique pilot names."""
        pilots = get_all_pilots()

        assert len(pilots) > 0
        assert len(pilots) == len(set(pilots))  # No duplicates
        assert pilots == sorted(pilots)  # Sorted

    def test_get_law_by_name(self):
        """get_law_by_name should find law by exact name."""
        law = get_law_by_name("L1 Day Closure Law")

        assert law is not None
        assert law.name == "L1 Day Closure Law"

    def test_get_law_by_name_not_found(self):
        """Unknown name should return None."""
        law = get_law_by_name("Unknown Law")
        assert law is None

    def test_summarize_pilot_laws(self):
        """summarize_pilot_laws should create nested structure."""
        summary = summarize_pilot_laws()

        assert isinstance(summary, dict)
        for pilot, schemas in summary.items():
            assert isinstance(schemas, dict)
            for schema_name, law_names in schemas.items():
                assert isinstance(law_names, list)


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for pilot law verification."""

    def test_trail_to_crystal_laws(self):
        """Test trail-to-crystal pilot laws."""
        context = {
            "has_crystal": True,
            "original_elements": {"a", "b", "c"},
            "crystal_elements": {"a"},
            "disclosed_elements": {"b", "c"},
        }

        report = verify_pilot_laws("trail-to-crystal", context)

        # Should have at least some passing laws
        assert report.pass_count > 0

    def test_wasm_survivors_laws(self):
        """Test wasm-survivors pilot laws."""
        context = {
            "action_type": "build",
            "marked_types": ["build", "deploy"],
            "current_loss": 0.3,
            "threshold": 0.5,
            "surfaced": True,
            "unchosen_paths": ["upgrade_a"],
            "inspectable_paths": ["upgrade_a", "upgrade_b"],
        }

        report = verify_pilot_laws("wasm-survivors", context)

        # Should have at least some passing laws
        assert report.pass_count > 0

    def test_rap_coach_laws(self):
        """Test rap-coach pilot laws."""
        context = {
            "intent_declared": True,
            "ghosts_preserved": True,
            "risk_level": 0.8,
            "penalty_applied": 0.0,
            "current_loss": 0.2,
            "threshold": 0.5,
            "surfaced": True,
        }

        report = verify_pilot_laws("rap-coach", context)

        # Should have at least some passing laws
        assert report.pass_count > 0

    def test_full_verification_pipeline(self):
        """Test full verification across all pilots."""
        # Minimal context that should pass most laws
        context = {
            "has_crystal": True,
            "has_prerequisite": True,
            "ghosts_preserved": True,
            "is_protected": True,
            "drops_disclosed": True,
            "intent_declared": True,
            "mutation_justified": True,
            "is_legible": True,
            "current_loss": 0.2,
            "threshold": 0.5,
            "surfaced": True,
        }

        results = verify_all_laws(context)

        # Should have more passes than failures with good context
        passes = sum(1 for v in results.values() if v)
        assert passes > len(results) // 2  # More than half pass


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Test edge case handling in schema predicates."""

    def test_coherence_gate_none_action_type(self):
        """None action_type should pass (no constraint)."""
        result = coherence_gate(action_type=None, marked_types=["build"])
        assert result is True

    def test_coherence_gate_none_marked_types(self):
        """None marked_types should pass (no requirements)."""
        result = coherence_gate(action_type="build", marked_types=None)
        assert result is True

    def test_drift_alert_none_loss(self):
        """None current_loss treated as 0.0."""
        result = drift_alert(current_loss=None, threshold=0.5, surfaced=False)
        assert result is True  # 0.0 < 0.5, so passes

    def test_drift_alert_none_threshold(self):
        """None threshold treated as 0.5."""
        result = drift_alert(current_loss=0.6, threshold=None, surfaced=True)
        assert result is True  # surfaced=True satisfies

    def test_drift_alert_negative_loss(self):
        """Negative loss treated as no drift."""
        result = drift_alert(current_loss=-0.5, threshold=0.5, surfaced=False)
        assert result is True  # normalized to 0.0, passes

    def test_ghost_preservation_none_inspectable(self):
        """None inspectable_paths with unchosen should fail."""
        result = ghost_preservation(
            unchosen_paths=["path_a"],
            inspectable_paths=None,
        )
        assert result is False  # ghosts lost

    def test_ghost_preservation_empty_unchosen(self):
        """Empty unchosen_paths should pass."""
        result = ghost_preservation(unchosen_paths=[], inspectable_paths=None)
        assert result is True  # nothing to preserve

    def test_courage_preservation_none_values(self):
        """None values normalized to defaults."""
        result = courage_preservation(
            risk_level=None,
            penalty_applied=None,
            risk_threshold=None,
        )
        assert result is True  # 0.0 < 0.7, low risk passes

    def test_courage_preservation_negative_risk(self):
        """Negative risk normalized to 0.0."""
        result = courage_preservation(
            risk_level=-0.5,
            penalty_applied=0.5,
            risk_threshold=0.7,
        )
        assert result is True  # normalized to low risk

    def test_compression_honesty_none_original(self):
        """None original_elements passes (nothing to compress)."""
        result = compression_honesty(
            original_elements=None,
            crystal_elements={"a"},
        )
        assert result is True

    def test_compression_honesty_empty_original(self):
        """Empty original_elements passes."""
        result = compression_honesty(
            original_elements=set(),
            crystal_elements={"a"},
        )
        assert result is True

    def test_compression_honesty_none_crystal(self):
        """None crystal_elements means all original must be disclosed."""
        result = compression_honesty(
            original_elements={"a", "b"},
            crystal_elements=None,
            disclosed_elements={"a", "b"},
        )
        assert result is True

    def test_compression_honesty_none_crystal_no_disclosure(self):
        """None crystal with no disclosure fails."""
        result = compression_honesty(
            original_elements={"a", "b"},
            crystal_elements=None,
            disclosed_elements=None,
        )
        assert result is False


# =============================================================================
# Test verify_all_pilot_laws
# =============================================================================


class TestVerifyAllPilotLaws:
    """Test the comprehensive verify_all_pilot_laws function."""

    def test_returns_report(self):
        """Should return LawVerificationReport."""
        from services.categorical.pilot_laws import verify_all_pilot_laws

        report = verify_all_pilot_laws()
        assert isinstance(report, LawVerificationReport)

    def test_covers_all_pilots(self):
        """Should include results for all pilots."""
        from services.categorical.pilot_laws import get_all_pilots, verify_all_pilot_laws

        report = verify_all_pilot_laws()
        pilots_in_results = set(r.law.pilot for r in report.results)
        expected_pilots = set(get_all_pilots())
        assert pilots_in_results == expected_pilots

    def test_covers_all_laws(self):
        """Should verify every registered law."""
        from services.categorical.pilot_laws import PILOT_LAWS, verify_all_pilot_laws

        report = verify_all_pilot_laws()
        assert len(report.results) == len(PILOT_LAWS)

    def test_with_pilot_contexts(self):
        """Should use provided pilot-specific contexts."""
        from services.categorical.pilot_laws import verify_all_pilot_laws

        contexts = {
            "trail-to-crystal": {
                "has_crystal": True,
                "drops_disclosed": True,
                "ghosts_preserved": True,
            },
            "wasm-survivors": {
                "has_prerequisite": True,
                "current_loss": 0.2,
                "ghosts_preserved": True,
                "is_protected": True,
                "drops_disclosed": True,
            },
        }

        report = verify_all_pilot_laws(contexts)

        # trail-to-crystal and wasm-survivors should have high pass rates
        by_pilot = report.by_pilot
        trail_passes = sum(1 for r in by_pilot.get("trail-to-crystal", []) if r.passed)
        wasm_passes = sum(1 for r in by_pilot.get("wasm-survivors", []) if r.passed)

        # With good context, most should pass
        assert trail_passes >= 2
        assert wasm_passes >= 3

    def test_by_schema_grouping(self):
        """Should correctly group results by schema."""
        from services.categorical.pilot_laws import LawSchema, verify_all_pilot_laws

        report = verify_all_pilot_laws()

        by_schema = report.by_schema
        # All schemas should be represented
        for schema in LawSchema:
            assert schema in by_schema
            assert len(by_schema[schema]) > 0

    def test_none_contexts_uses_empty(self):
        """None contexts should use empty dict for all pilots."""
        from services.categorical.pilot_laws import verify_all_pilot_laws

        report = verify_all_pilot_laws(None)
        # Should still produce results, just with defaults
        assert len(report.results) > 0
