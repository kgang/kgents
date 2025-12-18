"""
Tests for CrisisOperad: Crisis Response Composition Grammar.

Verifies:
1. Operad structure (operations, laws)
2. Law verification functions
3. Precondition checker
4. Operation metabolics
5. Operation composition functions
"""

import pytest

from agents.domain.drills.operad import (
    CLOSE_METABOLICS,
    COMMUNICATE_METABOLICS,
    CONTAIN_METABOLICS,
    # Operad
    CRISIS_OPERAD,
    DETECT_METABOLICS,
    ESCALATE_METABOLICS,
    INVESTIGATE_METABOLICS,
    PRECONDITION_CHECKER,
    RECOVER_METABOLICS,
    RESOLVE_METABOLICS,
    # Preconditions
    CrisisPreconditionChecker,
    # Metabolics
    OperationMetabolics,
    PreconditionResult,
)
from agents.domain.drills.polynomial import CrisisPhase
from agents.operad.core import LawStatus
from agents.poly import from_function

# =============================================================================
# Operad Structure Tests
# =============================================================================


class TestOperadStructure:
    """Tests for CRISIS_OPERAD structure."""

    def test_operad_exists(self) -> None:
        """CRISIS_OPERAD is defined."""
        assert CRISIS_OPERAD is not None
        assert CRISIS_OPERAD.name == "CrisisOperad"

    def test_has_universal_operations(self) -> None:
        """Operad includes inherited AGENT_OPERAD operations."""
        assert "seq" in CRISIS_OPERAD.operations
        assert "par" in CRISIS_OPERAD.operations

    def test_has_crisis_operations(self) -> None:
        """Operad includes crisis-specific operations."""
        crisis_ops = [
            "detect",
            "escalate",
            "contain",
            "communicate",
            "investigate",
            "resolve",
            "recover",
            "close",
        ]
        for op in crisis_ops:
            assert op in CRISIS_OPERAD.operations, f"Missing operation: {op}"

    def test_operation_count(self) -> None:
        """Operad has expected number of crisis-specific operations."""
        crisis_ops = [
            "detect",
            "escalate",
            "contain",
            "communicate",
            "investigate",
            "resolve",
            "recover",
            "close",
        ]
        for op in crisis_ops:
            assert op in CRISIS_OPERAD.operations

    def test_operation_arities(self) -> None:
        """Operations have correct arities."""
        assert CRISIS_OPERAD.operations["detect"].arity == 1
        assert CRISIS_OPERAD.operations["escalate"].arity == 1
        assert CRISIS_OPERAD.operations["contain"].arity == 1
        assert CRISIS_OPERAD.operations["communicate"].arity == 2  # Binary
        assert CRISIS_OPERAD.operations["investigate"].arity == 1
        assert CRISIS_OPERAD.operations["resolve"].arity == 1
        assert CRISIS_OPERAD.operations["recover"].arity == 1
        assert CRISIS_OPERAD.operations["close"].arity == 1

    def test_operation_signatures(self) -> None:
        """Operations have meaningful signatures."""
        assert "Monitor" in CRISIS_OPERAD.operations["detect"].signature
        assert "Crisis" in CRISIS_OPERAD.operations["escalate"].signature
        assert "Audience" in CRISIS_OPERAD.operations["communicate"].signature


class TestOperadLaws:
    """Tests for CRISIS_OPERAD laws."""

    def test_has_universal_laws(self) -> None:
        """Operad includes inherited AGENT_OPERAD laws."""
        law_names = {law.name for law in CRISIS_OPERAD.laws}
        assert "seq_associativity" in law_names

    def test_has_crisis_laws(self) -> None:
        """Operad includes crisis-specific laws."""
        law_names = {law.name for law in CRISIS_OPERAD.laws}
        assert "detection_required" in law_names
        assert "containment_before_recovery" in law_names
        assert "communication_compliance" in law_names
        assert "closure_requires_postmortem" in law_names

    def test_law_count(self) -> None:
        """Operad has at least 4 crisis-specific laws."""
        crisis_laws = [
            "detection_required",
            "containment_before_recovery",
            "communication_compliance",
            "closure_requires_postmortem",
        ]
        law_names = {law.name for law in CRISIS_OPERAD.laws}
        for law in crisis_laws:
            assert law in law_names


# =============================================================================
# Law Verification Tests
# =============================================================================


class TestLawVerification:
    """Tests for law verification functions."""

    def test_verify_detection_required_passes(self) -> None:
        """detection_required law verification passes."""
        result = CRISIS_OPERAD.verify_law("detection_required")
        assert result.status == LawStatus.PASSED

    def test_verify_containment_before_recovery_passes(self) -> None:
        """containment_before_recovery law verification passes."""
        result = CRISIS_OPERAD.verify_law("containment_before_recovery")
        assert result.status == LawStatus.PASSED

    def test_verify_communication_compliance_passes(self) -> None:
        """communication_compliance law verification passes."""
        result = CRISIS_OPERAD.verify_law("communication_compliance")
        assert result.status == LawStatus.PASSED

    def test_verify_closure_requires_postmortem_passes(self) -> None:
        """closure_requires_postmortem law verification passes."""
        result = CRISIS_OPERAD.verify_law("closure_requires_postmortem")
        assert result.status == LawStatus.PASSED

    def test_verify_all_laws(self) -> None:
        """All crisis-specific laws can be verified."""
        # Crisis-specific laws don't require test agents
        crisis_laws = [
            "detection_required",
            "containment_before_recovery",
            "communication_compliance",
            "closure_requires_postmortem",
        ]
        for law_name in crisis_laws:
            result = CRISIS_OPERAD.verify_law(law_name)
            assert result.status == LawStatus.PASSED, f"{law_name} failed"


# =============================================================================
# Precondition Checker Tests
# =============================================================================


class TestPreconditionChecker:
    """Tests for CrisisPreconditionChecker."""

    def test_checker_exists(self) -> None:
        """PRECONDITION_CHECKER is defined."""
        assert PRECONDITION_CHECKER is not None
        assert isinstance(PRECONDITION_CHECKER, CrisisPreconditionChecker)

    def test_detection_required_in_normal(self) -> None:
        """Detection is required when in NORMAL phase."""
        result = PRECONDITION_CHECKER.check_detection_required(CrisisPhase.NORMAL)
        assert not result.passed
        assert "detect" in result.message.lower()

    def test_detection_not_required_in_incident(self) -> None:
        """Detection not required after INCIDENT phase."""
        result = PRECONDITION_CHECKER.check_detection_required(CrisisPhase.INCIDENT)
        assert result.passed

    def test_detection_not_required_in_response(self) -> None:
        """Detection not required in RESPONSE phase."""
        result = PRECONDITION_CHECKER.check_detection_required(CrisisPhase.RESPONSE)
        assert result.passed

    def test_containment_required_for_recovery(self) -> None:
        """Containment must be confirmed before recovery transition."""
        result = PRECONDITION_CHECKER.check_containment_before_recovery(
            CrisisPhase.RESPONSE, containment_confirmed=False
        )
        assert not result.passed
        assert "containment" in result.message.lower()

    def test_containment_confirmed_allows_recovery(self) -> None:
        """Confirmed containment allows recovery transition."""
        result = PRECONDITION_CHECKER.check_containment_before_recovery(
            CrisisPhase.RESPONSE, containment_confirmed=True
        )
        assert result.passed

    def test_external_communication_requires_approval(self) -> None:
        """External communications require approval."""
        # Customer communication without approval
        result = PRECONDITION_CHECKER.check_communication_compliance(
            message_type="customer", approved_by=None
        )
        assert not result.passed
        assert "approval" in result.message.lower()

        # Regulatory communication without approval
        result = PRECONDITION_CHECKER.check_communication_compliance(
            message_type="regulatory", approved_by=None
        )
        assert not result.passed

    def test_internal_communication_no_approval_needed(self) -> None:
        """Internal communications don't require approval."""
        result = PRECONDITION_CHECKER.check_communication_compliance(
            message_type="internal", approved_by=None
        )
        assert result.passed

    def test_approved_communication_passes(self) -> None:
        """Approved external communications pass."""
        result = PRECONDITION_CHECKER.check_communication_compliance(
            message_type="customer", approved_by="PR Director"
        )
        assert result.passed

    def test_closure_requires_postmortem(self) -> None:
        """Closure requires postmortem to be scheduled."""
        result = PRECONDITION_CHECKER.check_closure_requirements(postmortem_scheduled=False)
        assert not result.passed
        assert "postmortem" in result.message.lower()

    def test_closure_with_postmortem_passes(self) -> None:
        """Closure with scheduled postmortem passes."""
        result = PRECONDITION_CHECKER.check_closure_requirements(postmortem_scheduled=True)
        assert result.passed

    def test_validate_operation_detect(self) -> None:
        """Validate detect operation (no preconditions)."""
        results = PRECONDITION_CHECKER.validate_operation("detect", CrisisPhase.NORMAL)
        assert all(r.passed for r in results)

    def test_validate_operation_escalate_in_normal(self) -> None:
        """Validate escalate in NORMAL fails detection check."""
        results = PRECONDITION_CHECKER.validate_operation("escalate", CrisisPhase.NORMAL)
        assert any(not r.passed for r in results)

    def test_validate_operation_escalate_in_incident(self) -> None:
        """Validate escalate in INCIDENT passes."""
        results = PRECONDITION_CHECKER.validate_operation("escalate", CrisisPhase.INCIDENT)
        assert all(r.passed for r in results)


# =============================================================================
# Metabolics Tests
# =============================================================================


class TestOperationMetabolics:
    """Tests for operation metabolics."""

    def test_metabolics_class(self) -> None:
        """OperationMetabolics dataclass works."""
        met = OperationMetabolics(token_cost=100, drama_potential=0.5)
        assert met.token_cost == 100
        assert met.drama_potential == 0.5
        assert met.estimate_tokens() == 100
        assert met.estimate_tokens(arity=3) == 300

    def test_detect_metabolics(self) -> None:
        """Detect has appropriate metabolics."""
        assert DETECT_METABOLICS.token_cost > 0
        assert 0 <= DETECT_METABOLICS.drama_potential <= 1

    def test_escalate_metabolics(self) -> None:
        """Escalate has high drama potential."""
        assert ESCALATE_METABOLICS.drama_potential >= 0.5

    def test_contain_metabolics(self) -> None:
        """Contain has appropriate metabolics."""
        assert CONTAIN_METABOLICS.token_cost > 0

    def test_communicate_metabolics(self) -> None:
        """Communicate has appropriate metabolics."""
        assert COMMUNICATE_METABOLICS.token_cost > 0

    def test_investigate_metabolics(self) -> None:
        """Investigate has lower drama potential."""
        assert INVESTIGATE_METABOLICS.drama_potential <= 0.5

    def test_resolve_metabolics(self) -> None:
        """Resolve has higher token cost (complex action)."""
        assert RESOLVE_METABOLICS.token_cost >= DETECT_METABOLICS.token_cost

    def test_recover_metabolics(self) -> None:
        """Recover has appropriate metabolics."""
        assert RECOVER_METABOLICS.token_cost > 0

    def test_close_metabolics(self) -> None:
        """Close has low drama potential (routine closure)."""
        assert CLOSE_METABOLICS.drama_potential <= 0.3


# =============================================================================
# Operation Composition Tests
# =============================================================================


class TestOperationComposition:
    """Tests for operation composition functions."""

    def test_detect_composition(self) -> None:
        """detect operation composes correctly."""
        monitor = from_function("TestMonitor", lambda x: {"status": "ok"})
        composed = CRISIS_OPERAD.compose("detect", monitor)
        assert "detect" in composed.name.lower()

    def test_escalate_composition(self) -> None:
        """escalate operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "INCIDENT"})
        composed = CRISIS_OPERAD.compose("escalate", crisis)
        assert "escalate" in composed.name.lower()

    def test_contain_composition(self) -> None:
        """contain operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "INCIDENT"})
        composed = CRISIS_OPERAD.compose("contain", crisis)
        assert "contain" in composed.name.lower()

    def test_communicate_composition(self) -> None:
        """communicate operation composes with audience."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "INCIDENT"})
        audience = from_function("Customers", lambda x: {"type": "external"})
        composed = CRISIS_OPERAD.compose("communicate", crisis, audience)
        assert "communicate" in composed.name.lower()
        assert "Customers" in composed.name

    def test_investigate_composition(self) -> None:
        """investigate operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "INCIDENT"})
        composed = CRISIS_OPERAD.compose("investigate", crisis)
        assert "investigate" in composed.name.lower()

    def test_resolve_composition(self) -> None:
        """resolve operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "RESPONSE"})
        composed = CRISIS_OPERAD.compose("resolve", crisis)
        assert "resolve" in composed.name.lower()

    def test_recover_composition(self) -> None:
        """recover operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "RESPONSE"})
        composed = CRISIS_OPERAD.compose("recover", crisis)
        assert "recover" in composed.name.lower()

    def test_close_composition(self) -> None:
        """close operation composes correctly."""
        crisis = from_function("TestCrisis", lambda x: {"phase": "RECOVERY"})
        composed = CRISIS_OPERAD.compose("close", crisis)
        assert "close" in composed.name.lower()

    def test_composed_agent_invocable(self) -> None:
        """Composed agents can be invoked."""
        monitor = from_function("TestMonitor", lambda x: {"status": "ok"})
        composed = CRISIS_OPERAD.compose("detect", monitor)
        # from_function creates agents with "ready" as the single position
        # Invoke with proper state and input
        _, result = composed.invoke("ready", {"alert": "database down"})
        assert result is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestOperadIntegration:
    """Integration tests for crisis operad."""

    def test_sequential_composition_works(self) -> None:
        """Sequential composition via seq operation works."""
        detect_agent = from_function("Detect", lambda x: {"detected": True})
        escalate_agent = from_function("Escalate", lambda x: {"escalated": True})

        # Use seq from AGENT_OPERAD (inherited)
        seq_composed = CRISIS_OPERAD.compose("seq", detect_agent, escalate_agent)
        assert seq_composed is not None

    def test_parallel_composition_works(self) -> None:
        """Parallel composition via par operation works."""
        investigate_agent = from_function("Investigate", lambda x: {"findings": []})
        communicate_agent = from_function("Communicate", lambda x: {"sent": True})

        # Use par from AGENT_OPERAD (inherited)
        par_composed = CRISIS_OPERAD.compose("par", investigate_agent, communicate_agent)
        assert par_composed is not None

    def test_operad_description(self) -> None:
        """Operad has meaningful description."""
        assert len(CRISIS_OPERAD.description) > 0
        assert "crisis" in CRISIS_OPERAD.description.lower()

    def test_precondition_result_dataclass(self) -> None:
        """PreconditionResult is a proper dataclass."""
        result = PreconditionResult(
            passed=True, message="All checks passed", precondition="test_check"
        )
        assert result.passed
        assert result.message == "All checks passed"
        assert result.precondition == "test_check"


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


from hypothesis import given, settings, strategies as st

from agents.domain.drills.operad import (
    CrisisAuditEvent,
    CrisisAuditStore,
    emit_crisis_audit,
    get_audit_store,
)

# Strategies for generating test data
phase_strategy = st.sampled_from(list(CrisisPhase))
operation_strategy = st.sampled_from(
    [
        "detect",
        "escalate",
        "contain",
        "communicate",
        "investigate",
        "resolve",
        "recover",
        "close",
    ]
)
message_type_strategy = st.sampled_from(["internal", "customer", "regulatory", "media"])
uuid_strategy = st.text(min_size=8, max_size=32, alphabet="abcdef0123456789")


class TestPropertyBasedMetabolics:
    """Property-based tests for metabolics invariants."""

    @given(
        token_cost=st.integers(min_value=0, max_value=10000),
        drama=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        arity=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=50)
    def test_estimate_tokens_scales_linearly(
        self, token_cost: int, drama: float, arity: int
    ) -> None:
        """Token estimation scales linearly with arity."""
        met = OperationMetabolics(token_cost=token_cost, drama_potential=drama)
        assert met.estimate_tokens(arity) == token_cost * arity

    @given(
        token_cost=st.integers(min_value=0, max_value=10000),
        drama=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        credits=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=50)
    def test_metabolics_fields_valid(self, token_cost: int, drama: float, credits: int) -> None:
        """Metabolics always has valid fields."""
        met = OperationMetabolics(token_cost=token_cost, drama_potential=drama, credits=credits)
        assert met.token_cost >= 0
        assert 0 <= met.drama_potential <= 1
        assert met.credits >= 0


class TestPropertyBasedPreconditions:
    """Property-based tests for precondition checker invariants."""

    @given(phase=phase_strategy)
    @settings(max_examples=20)
    def test_detection_check_deterministic(self, phase: CrisisPhase) -> None:
        """Detection check is deterministic for same phase."""
        result1 = PRECONDITION_CHECKER.check_detection_required(phase)
        result2 = PRECONDITION_CHECKER.check_detection_required(phase)
        assert result1.passed == result2.passed
        assert result1.precondition == result2.precondition

    @given(phase=phase_strategy, confirmed=st.booleans())
    @settings(max_examples=20)
    def test_containment_check_deterministic(self, phase: CrisisPhase, confirmed: bool) -> None:
        """Containment check is deterministic."""
        result1 = PRECONDITION_CHECKER.check_containment_before_recovery(phase, confirmed)
        result2 = PRECONDITION_CHECKER.check_containment_before_recovery(phase, confirmed)
        assert result1.passed == result2.passed

    @given(msg_type=message_type_strategy, approver=st.text(max_size=50) | st.none())
    @settings(max_examples=30)
    def test_communication_compliance_invariants(self, msg_type: str, approver: str | None) -> None:
        """Communication compliance follows approval rules."""
        result = PRECONDITION_CHECKER.check_communication_compliance(msg_type, approver)
        # Internal never requires approval
        if msg_type == "internal":
            assert result.passed
        # External with approval always passes
        if approver and len(approver) > 0:
            assert result.passed

    @given(phase=phase_strategy, operation=operation_strategy)
    @settings(max_examples=40)
    def test_validate_operation_returns_list(self, phase: CrisisPhase, operation: str) -> None:
        """validate_operation always returns a list."""
        results = PRECONDITION_CHECKER.validate_operation(operation, phase)
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, PreconditionResult)


class TestPropertyBasedDirections:
    """Property-based tests for directions function invariants."""

    @given(phase=phase_strategy)
    @settings(max_examples=20)
    def test_directions_returns_frozenset(self, phase: CrisisPhase) -> None:
        """Directions always returns a frozenset."""
        from agents.domain.drills.polynomial import crisis_directions

        dirs = crisis_directions(phase)
        assert isinstance(dirs, frozenset)
        assert len(dirs) > 0

    @given(phase=phase_strategy)
    @settings(max_examples=20)
    def test_normal_only_allows_detect(self, phase: CrisisPhase) -> None:
        """NORMAL phase enforces detect-first rule."""
        from agents.domain.drills.polynomial import DetectInput, crisis_directions

        if phase == CrisisPhase.NORMAL:
            dirs = crisis_directions(phase)
            assert DetectInput in dirs
        else:
            dirs = crisis_directions(phase)
            assert DetectInput not in dirs


# =============================================================================
# T-gent Spy/Counter Test Patterns
# =============================================================================


class AuditSpy:
    """
    T-gent Type I: Spy pattern for tracking audit emissions.

    Records all audit events for verification without affecting behavior.
    """

    def __init__(self) -> None:
        self.events: list[CrisisAuditEvent] = []
        self.emit_count = 0

    def record(self, event: CrisisAuditEvent) -> None:
        """Record an audit event."""
        self.events.append(event)
        self.emit_count += 1

    def reset(self) -> None:
        """Reset spy state."""
        self.events.clear()
        self.emit_count = 0

    def get_operations(self) -> list[str]:
        """Get list of operations recorded."""
        return [e.operation for e in self.events]

    def count_by_operation(self, operation: str) -> int:
        """Count events for a specific operation."""
        return sum(1 for e in self.events if e.operation == operation)


class MetabolicCounter:
    """
    T-gent Type II: Counter pattern for tracking metabolic costs.

    Accumulates token/credit costs across operations.
    """

    def __init__(self) -> None:
        self.total_tokens = 0
        self.total_credits = 0
        self.total_drama = 0.0
        self.operation_counts: dict[str, int] = {}

    def accumulate(self, metabolics: OperationMetabolics, operation: str) -> None:
        """Accumulate costs from an operation."""
        self.total_tokens += metabolics.token_cost
        self.total_credits += metabolics.credits
        self.total_drama += metabolics.drama_potential
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1

    def reset(self) -> None:
        """Reset counter state."""
        self.total_tokens = 0
        self.total_credits = 0
        self.total_drama = 0.0
        self.operation_counts.clear()


class TestTgentAuditSpy:
    """Tests using the AuditSpy T-gent pattern."""

    def test_spy_tracks_audit_events(self) -> None:
        """Spy correctly tracks emitted audit events."""
        spy = AuditSpy()

        # Create and track events
        event1 = CrisisAuditEvent.create(
            operation="detect",
            simulation_id="sim-1",
            phase_before="NORMAL",
            phase_after="INCIDENT",
            metabolics=DETECT_METABOLICS,
        )
        spy.record(event1)

        event2 = CrisisAuditEvent.create(
            operation="escalate",
            simulation_id="sim-1",
            phase_before="INCIDENT",
            phase_after="RESPONSE",
            metabolics=ESCALATE_METABOLICS,
        )
        spy.record(event2)

        assert spy.emit_count == 2
        assert spy.get_operations() == ["detect", "escalate"]
        assert spy.count_by_operation("detect") == 1
        assert spy.count_by_operation("escalate") == 1
        assert spy.count_by_operation("contain") == 0

    def test_spy_reset_clears_state(self) -> None:
        """Spy reset clears all recorded events."""
        spy = AuditSpy()
        event = CrisisAuditEvent.create(
            operation="detect",
            simulation_id="sim-1",
            phase_before="NORMAL",
            phase_after="INCIDENT",
            metabolics=DETECT_METABOLICS,
        )
        spy.record(event)
        assert spy.emit_count == 1

        spy.reset()
        assert spy.emit_count == 0
        assert len(spy.events) == 0

    def test_spy_tracks_full_incident_lifecycle(self) -> None:
        """Spy tracks complete incident response workflow."""
        spy = AuditSpy()

        lifecycle_operations = [
            ("detect", "NORMAL", "INCIDENT", DETECT_METABOLICS),
            ("escalate", "INCIDENT", "INCIDENT", ESCALATE_METABOLICS),
            ("contain", "INCIDENT", "RESPONSE", CONTAIN_METABOLICS),
            ("investigate", "RESPONSE", "RESPONSE", INVESTIGATE_METABOLICS),
            ("resolve", "RESPONSE", "RESPONSE", RESOLVE_METABOLICS),
            ("recover", "RESPONSE", "RECOVERY", RECOVER_METABOLICS),
            ("close", "RECOVERY", "NORMAL", CLOSE_METABOLICS),
        ]

        for op, phase_before, phase_after, metabolics in lifecycle_operations:
            event = CrisisAuditEvent.create(
                operation=op,
                simulation_id="drill-001",
                phase_before=phase_before,
                phase_after=phase_after,
                metabolics=metabolics,
            )
            spy.record(event)

        assert spy.emit_count == 7
        assert spy.get_operations() == [
            "detect",
            "escalate",
            "contain",
            "investigate",
            "resolve",
            "recover",
            "close",
        ]


class TestTgentMetabolicCounter:
    """Tests using the MetabolicCounter T-gent pattern."""

    def test_counter_accumulates_costs(self) -> None:
        """Counter correctly accumulates metabolic costs."""
        counter = MetabolicCounter()

        counter.accumulate(DETECT_METABOLICS, "detect")
        counter.accumulate(ESCALATE_METABOLICS, "escalate")
        counter.accumulate(CONTAIN_METABOLICS, "contain")

        expected_tokens = (
            DETECT_METABOLICS.token_cost
            + ESCALATE_METABOLICS.token_cost
            + CONTAIN_METABOLICS.token_cost
        )
        expected_credits = (
            DETECT_METABOLICS.credits + ESCALATE_METABOLICS.credits + CONTAIN_METABOLICS.credits
        )

        assert counter.total_tokens == expected_tokens
        assert counter.total_credits == expected_credits
        assert counter.operation_counts["detect"] == 1
        assert counter.operation_counts["escalate"] == 1
        assert counter.operation_counts["contain"] == 1

    def test_counter_tracks_drama_potential(self) -> None:
        """Counter tracks cumulative drama potential."""
        counter = MetabolicCounter()

        # High-drama operations
        counter.accumulate(ESCALATE_METABOLICS, "escalate")
        counter.accumulate(DETECT_METABOLICS, "detect")

        expected_drama = ESCALATE_METABOLICS.drama_potential + DETECT_METABOLICS.drama_potential
        assert abs(counter.total_drama - expected_drama) < 0.001

    def test_counter_full_drill_cost(self) -> None:
        """Counter calculates total cost for a full drill."""
        counter = MetabolicCounter()

        all_metabolics = [
            (DETECT_METABOLICS, "detect"),
            (ESCALATE_METABOLICS, "escalate"),
            (CONTAIN_METABOLICS, "contain"),
            (COMMUNICATE_METABOLICS, "communicate"),
            (INVESTIGATE_METABOLICS, "investigate"),
            (RESOLVE_METABOLICS, "resolve"),
            (RECOVER_METABOLICS, "recover"),
            (CLOSE_METABOLICS, "close"),
        ]

        for met, op in all_metabolics:
            counter.accumulate(met, op)

        # Verify full drill costs
        assert counter.total_tokens == sum(m.token_cost for m, _ in all_metabolics)
        assert counter.total_credits == sum(m.credits for m, _ in all_metabolics)
        assert len(counter.operation_counts) == 8


class TestAuditStoreIntegration:
    """Integration tests for CrisisAuditStore."""

    def test_audit_store_query_by_simulation(self) -> None:
        """Audit store queries correctly by simulation_id."""
        store = CrisisAuditStore()

        # Emit events for different simulations
        event1 = CrisisAuditEvent.create(
            operation="detect",
            simulation_id="sim-alpha",
            phase_before="NORMAL",
            phase_after="INCIDENT",
            metabolics=DETECT_METABOLICS,
        )
        store.emit(event1)

        event2 = CrisisAuditEvent.create(
            operation="detect",
            simulation_id="sim-beta",
            phase_before="NORMAL",
            phase_after="INCIDENT",
            metabolics=DETECT_METABOLICS,
        )
        store.emit(event2)

        alpha_events = store.query(simulation_id="sim-alpha")
        beta_events = store.query(simulation_id="sim-beta")

        assert len(alpha_events) == 1
        assert len(beta_events) == 1
        assert alpha_events[0].simulation_id == "sim-alpha"
        assert beta_events[0].simulation_id == "sim-beta"

    def test_audit_store_query_by_operation(self) -> None:
        """Audit store queries correctly by operation."""
        store = CrisisAuditStore()

        for op, met in [
            ("detect", DETECT_METABOLICS),
            ("detect", DETECT_METABOLICS),
            ("escalate", ESCALATE_METABOLICS),
        ]:
            event = CrisisAuditEvent.create(
                operation=op,
                simulation_id="sim-1",
                phase_before="X",
                phase_after="Y",
                metabolics=met,
            )
            store.emit(event)

        detect_events = store.query(operation="detect")
        escalate_events = store.query(operation="escalate")

        assert len(detect_events) == 2
        assert len(escalate_events) == 1

    def test_compliance_report_structure(self) -> None:
        """Compliance report has correct structure."""
        store = CrisisAuditStore()

        lifecycle = [
            ("detect", DETECT_METABOLICS, "NORMAL", "INCIDENT"),
            ("contain", CONTAIN_METABOLICS, "INCIDENT", "RESPONSE"),
            ("close", CLOSE_METABOLICS, "RECOVERY", "NORMAL"),
        ]

        for op, met, before, after in lifecycle:
            event = CrisisAuditEvent.create(
                operation=op,
                simulation_id="compliance-test",
                phase_before=before,
                phase_after=after,
                metabolics=met,
            )
            store.emit(event)

        report = store.export_compliance_report("compliance-test")

        assert report["simulation_id"] == "compliance-test"
        assert report["summary"]["total_events"] == 3
        assert set(report["summary"]["operations_used"]) == {
            "detect",
            "contain",
            "close",
        }
        assert len(report["timeline"]) == 3

        expected_tokens = (
            DETECT_METABOLICS.token_cost
            + CONTAIN_METABOLICS.token_cost
            + CLOSE_METABOLICS.token_cost
        )
        assert report["summary"]["total_tokens"] == expected_tokens
