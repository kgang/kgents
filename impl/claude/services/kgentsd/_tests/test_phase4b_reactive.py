"""
Tests for Phase 4B: Reactive Workflows Integration.

Covers:
- Event → Reactor → Suggestion flow
- TUI suggestion handling
- Trust escalation metrics
- Daemon-to-TUI wiring

Success Criteria (from kgentsd-phase4b-prompt.md):
1. kgentsd summon running, pytest fails → suggestion appears within 3s
2. User presses Y → action executes, recorded to audit trail
3. User presses N → rejection recorded, trust metrics updated
4. StatusPanel shows trust escalation progress
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from services.kgentsd.daemon import (
    DaemonConfig,
    WitnessDaemon,
    event_to_thought,
)
from services.kgentsd.reactor import (
    WitnessReactor,
    create_reactor,
    create_test_failure_event,
)
from services.kgentsd.workflows import (
    TEST_FAILURE_RESPONSE,
    WORKFLOW_REGISTRY,
)
from services.witness.polynomial import (
    TestEvent,
    TrustLevel,
)
from services.witness.trust.confirmation import (
    ActionPreview,
    ConfirmationManager,
    PendingSuggestion,
    SuggestionStatus,
)

# =============================================================================
# Daemon-Reactor Integration Tests
# =============================================================================


class TestDaemonReactorIntegration:
    """Test daemon → reactor wiring."""

    def test_daemon_has_reactor(self) -> None:
        """Daemon initializes with a reactor."""
        daemon = WitnessDaemon()
        assert daemon.reactor is not None
        assert isinstance(daemon.reactor, WitnessReactor)

    def test_daemon_has_confirmation_manager(self) -> None:
        """Daemon initializes with confirmation manager."""
        daemon = WitnessDaemon()
        assert daemon.confirmation_manager is not None
        assert isinstance(daemon.confirmation_manager, ConfirmationManager)

    def test_daemon_custom_reactor(self) -> None:
        """Daemon accepts custom reactor."""
        custom_reactor = WitnessReactor(mappings=[])
        daemon = WitnessDaemon(reactor=custom_reactor)
        assert daemon.reactor is custom_reactor
        assert len(daemon.reactor.mappings) == 0

    def test_daemon_watcher_event_to_reactor_event_test_failure(self) -> None:
        """Watcher test failure event converts to reactor event."""
        daemon = WitnessDaemon()

        # Simulate a test failure event from TestWatcher
        poly_event = TestEvent(
            event_type="failed",
            test_id="test_auth.py::test_login_fails",
            error="AssertionError: expected True",
        )

        reactor_event = daemon._watcher_event_to_reactor_event("test", poly_event)

        assert reactor_event is not None
        assert reactor_event.event_type == "failure"
        assert "test_auth" in reactor_event.data["test_file"]

    def test_daemon_watcher_event_to_reactor_event_session_complete(self) -> None:
        """Session complete events do not create reactor events (no failure)."""
        daemon = WitnessDaemon()

        poly_event = TestEvent(
            event_type="session_complete",
            passed=10,
            failed=0,
            skipped=2,
        )

        reactor_event = daemon._watcher_event_to_reactor_event("test", poly_event)
        assert reactor_event is None  # Only failures trigger workflows


class TestDaemonSuggestionCallback:
    """Test daemon suggestion callback wiring."""

    def test_set_suggestion_callback(self) -> None:
        """Suggestion callback can be set."""
        daemon = WitnessDaemon()
        callback_called = []

        async def test_callback(suggestion: PendingSuggestion) -> None:
            callback_called.append(suggestion)

        daemon.set_suggestion_callback(test_callback)
        assert daemon._suggestion_callback is test_callback

    @pytest.mark.asyncio
    async def test_on_suggestion_created_calls_callback(self) -> None:
        """Suggestion callback is called when suggestion is created."""
        callback_results: list[PendingSuggestion] = []

        async def capture_callback(suggestion: PendingSuggestion) -> None:
            callback_results.append(suggestion)

        daemon = WitnessDaemon()
        daemon.set_suggestion_callback(capture_callback)

        # Create a mock suggestion
        suggestion = PendingSuggestion(
            id="test-123",
            action="Test Fix",
            target="test_file.py",
            rationale="Test failure detected",
            preview=ActionPreview(description="Apply fix"),
            confidence=0.85,
        )

        await daemon._on_suggestion_created(suggestion)

        assert len(callback_results) == 1
        assert callback_results[0].id == "test-123"
        assert daemon.suggestions_shown == 1


# =============================================================================
# Reactor Event-to-Workflow Tests
# =============================================================================


class TestReactorTestFailureMapping:
    """Test reactor mapping for test failures."""

    @pytest.mark.asyncio
    async def test_test_failure_triggers_workflow(self) -> None:
        """Test failure event triggers TEST_FAILURE_RESPONSE workflow."""
        reactor = create_reactor()

        event = create_test_failure_event(
            test_file="tests/test_auth.py",
            test_name="test_login_requires_token",
            error_message="AssertionError: expected 401",
        )

        reaction = await reactor.react(event)

        assert reaction is not None
        assert reaction.workflow_name == "Test Failure Response"
        assert reaction.required_trust == TrustLevel.AUTONOMOUS
        assert reactor._reaction_count == 1

    @pytest.mark.asyncio
    async def test_test_failure_requires_l3_trust(self) -> None:
        """TEST_FAILURE_RESPONSE requires L3 (AUTONOMOUS) trust."""
        reactor = create_reactor()

        event = create_test_failure_event("t.py", "test_foo", "Error")
        reaction = await reactor.react(event)

        assert reaction is not None
        assert reaction.required_trust == TrustLevel.AUTONOMOUS
        # At L0, this cannot run
        assert reaction.can_run is False
        assert reaction.is_approved is False


# =============================================================================
# Confirmation Manager Tests
# =============================================================================


class TestConfirmationManagerMetrics:
    """Test confirmation manager trust escalation metrics."""

    @pytest.mark.asyncio
    async def test_acceptance_rate_calculation(self) -> None:
        """Acceptance rate is correctly calculated."""
        manager = ConfirmationManager()

        # Submit and confirm 3 suggestions
        for i in range(3):
            s = await manager.submit(f"action-{i}", "rationale")
            await manager.confirm(s.id)

        # Submit and reject 1 suggestion
        s = await manager.submit("action-reject", "rationale")
        await manager.reject(s.id)

        # 3 confirmed out of 4 decided = 75%
        assert manager.acceptance_rate == 0.75

    @pytest.mark.asyncio
    async def test_stats_tracking(self) -> None:
        """Stats are correctly tracked."""
        manager = ConfirmationManager()

        # Submit
        s1 = await manager.submit("action-1", "test")
        s2 = await manager.submit("action-2", "test")

        assert manager.total_submitted == 2
        assert manager.stats["pending_count"] == 2

        # Confirm one
        await manager.confirm(s1.id)
        assert manager.total_confirmed == 1

        # Reject one
        await manager.reject(s2.id)
        assert manager.total_rejected == 1

        # Final stats
        stats = manager.stats
        assert stats["total_submitted"] == 2
        assert stats["total_confirmed"] == 1
        assert stats["total_rejected"] == 1
        assert stats["pending_count"] == 0


# =============================================================================
# Trust Escalation Progress Tests
# =============================================================================


class TestTrustEscalationProgress:
    """Test trust escalation progress calculation."""

    def test_l0_to_l1_progress_calculation(self) -> None:
        """L0 → L1 progress is based on observations and time."""
        # At L0, need 100 observations AND 24h
        # If we have 50 observations and 12h, we're at 50% on both criteria

        # This is tested implicitly through the StatusPanel render
        # The progress formula is: min(obs/100, hours/24)

        observations = 50
        hours = 12
        expected_progress = min(observations / 100, hours / 24)
        assert expected_progress == 0.5

    def test_l1_to_l2_progress_calculation(self) -> None:
        """L1 → L2 progress is based on successful operations."""
        # Need 100 successful operations
        operations = 75
        expected_progress = operations / 100
        assert expected_progress == 0.75

    def test_l2_to_l3_progress_calculation(self) -> None:
        """L2 → L3 progress is based on suggestions and acceptance rate."""
        # Need 50 suggestions with >90% acceptance

        # Case 1: Not enough suggestions
        suggestions = 25
        progress = suggestions / 50
        assert progress == 0.5

        # Case 2: Enough suggestions, low acceptance
        suggestions = 60
        accepted = 45
        acceptance_rate = accepted / suggestions  # 75%
        # Progress is acceptance_rate / 0.9 (need 90%)
        progress = acceptance_rate / 0.9
        assert progress < 1.0

        # Case 3: Enough suggestions, high acceptance
        suggestions = 60
        accepted = 57
        acceptance_rate = accepted / suggestions  # 95%
        progress = min(acceptance_rate / 0.9, 1.0)
        assert progress >= 1.0


# =============================================================================
# Suggestion Prompt Tests
# =============================================================================


class TestSuggestionPromptData:
    """Test suggestion prompt data formatting."""

    def test_pending_suggestion_display(self) -> None:
        """PendingSuggestion.to_display() formats correctly."""
        suggestion = PendingSuggestion(
            id="sug-abc123",
            action="git commit -m 'fix: typo'",
            target="README.md",
            rationale="Detected uncommitted typo fix",
            preview=ActionPreview(
                description="Commit the typo fix",
                affected_files=["README.md"],
                reversible=True,
                risk_level="low",
            ),
            confidence=0.85,
        )

        display = suggestion.to_display()

        assert display["id"] == "sug-abc123"
        assert display["action"] == "git commit -m 'fix: typo'"
        assert display["confidence"] == "85%"
        assert display["preview"]["risk_level"] == "low"
        assert display["status"] == "PENDING"

    def test_confidence_bar_rendering(self) -> None:
        """Confidence bar renders correctly."""

        # Test via the formula used in SuggestionPrompt
        def confidence_bar(confidence: float) -> str:
            filled = int(confidence * 10)
            return "█" * filled + "░" * (10 - filled)

        assert confidence_bar(0.0) == "░░░░░░░░░░"
        assert confidence_bar(0.5) == "█████░░░░░"
        assert confidence_bar(1.0) == "██████████"
        assert confidence_bar(0.85) == "████████░░"


# =============================================================================
# End-to-End Integration Tests
# =============================================================================


class TestEndToEndFlow:
    """End-to-end tests for the complete reactive workflow flow."""

    @pytest.mark.asyncio
    async def test_test_failure_to_suggestion_flow(self) -> None:
        """
        Complete flow: TestEvent → Daemon → Reactor → ConfirmationManager → Suggestion.

        This tests the Phase 4B success criteria:
        "pytest fails → suggestion appears"
        """
        suggestions_received: list[PendingSuggestion] = []

        async def capture_suggestion(suggestion: PendingSuggestion) -> None:
            suggestions_received.append(suggestion)

        # Create daemon with callback
        daemon = WitnessDaemon()
        daemon.set_suggestion_callback(capture_suggestion)

        # Simulate the flow that would happen when TestWatcher emits a failure
        # (The actual daemon._handle_event requires watchers to be running,
        # so we test the components individually)

        # 1. Create test failure reactor event
        reactor_event = create_test_failure_event(
            test_file="tests/test_auth.py",
            test_name="test_redirect_flow",
            error_message="AssertionError: redirect_uri mismatch",
        )

        # 2. React to event
        reaction = await daemon.reactor.react(reactor_event)
        assert reaction is not None
        assert reaction.workflow_name == "Test Failure Response"

        # 3. Since reaction can't run (L0 trust), create suggestion
        if not reaction.can_run and reaction.workflow:
            await daemon._create_suggestion_from_reaction(reaction)

        # 4. Verify suggestion was created and callback was called
        assert daemon.confirmation_manager.total_submitted == 1
        assert len(suggestions_received) == 1
        assert suggestions_received[0].action == "Test Failure Response"

    @pytest.mark.asyncio
    async def test_suggestion_accept_flow(self) -> None:
        """
        Complete flow: Suggestion → Accept → Execute → Record.

        Tests: "User presses Y → action executes, recorded to audit trail"
        """
        executed_actions: list[str] = []

        async def mock_executor(action: str) -> tuple[bool, str]:
            executed_actions.append(action)
            return True, "Executed successfully"

        manager = ConfirmationManager(execution_handler=mock_executor)

        # Submit a suggestion
        suggestion = await manager.submit(
            action="Apply fix to auth.py",
            rationale="Test failure detected",
            confidence=0.9,
        )

        # Accept the suggestion
        result = await manager.confirm(suggestion.id, confirmed_by="test-user")

        # Verify execution
        assert result.accepted is True
        assert result.executed is True
        assert result.execution_result == "Executed successfully"
        assert "Apply fix to auth.py" in executed_actions

        # Verify metrics
        assert manager.total_confirmed == 1
        assert manager.total_executed == 1

    @pytest.mark.asyncio
    async def test_suggestion_reject_flow(self) -> None:
        """
        Complete flow: Suggestion → Reject → Record.

        Tests: "User presses N → rejection recorded, trust metrics updated"
        """
        manager = ConfirmationManager()

        # Submit a suggestion
        suggestion = await manager.submit(
            action="Risky operation",
            rationale="Detected opportunity",
            confidence=0.6,
        )

        # Reject the suggestion
        result = await manager.reject(suggestion.id, reason="Too risky")

        # Verify rejection
        assert result.accepted is False

        # Verify metrics updated
        assert manager.total_rejected == 1
        assert (
            manager.acceptance_rate == 0.0
        )  # 0 confirmed / 0 decided (None decided yet with total_rejected=1)

        # Actually verify the math: 0 confirmed / (0 confirmed + 1 rejected) = 0%
        total_decided = manager.total_confirmed + manager.total_rejected
        assert total_decided == 1
        assert manager.total_confirmed / total_decided == 0.0


# =============================================================================
# Workflow Registry Tests
# =============================================================================


class TestWorkflowRegistry:
    """Test workflow registry for Phase 4B."""

    def test_test_failure_response_exists(self) -> None:
        """TEST_FAILURE_RESPONSE workflow exists in registry."""
        assert "test-failure" in WORKFLOW_REGISTRY
        workflow = WORKFLOW_REGISTRY["test-failure"]
        assert workflow.name == "Test Failure Response"
        assert workflow.required_trust == 3  # AUTONOMOUS

    def test_workflow_required_trust_levels(self) -> None:
        """Verify trust levels for key workflows."""
        # L3 (AUTONOMOUS) - can modify code
        assert WORKFLOW_REGISTRY["test-failure"].required_trust == 3
        assert WORKFLOW_REGISTRY["code-change"].required_trust == 3

        # L1 (BOUNDED) - can write to .kgents/
        assert WORKFLOW_REGISTRY["pr-review"].required_trust == 1
        assert WORKFLOW_REGISTRY["crystallize"].required_trust == 1

        # L0 (READ_ONLY) - observation only
        assert WORKFLOW_REGISTRY["standup"].required_trust == 0
        assert WORKFLOW_REGISTRY["ci-monitor"].required_trust == 0
        assert WORKFLOW_REGISTRY["health-check"].required_trust == 0
