"""
Tests for Witness Reactor: Event-to-Workflow Mapping.

Covers:
- Event creation and matching
- Event-workflow mappings
- Reaction lifecycle (pending → approved → running → completed)
- Trust gating and approval
- Debouncing
- Reactor statistics
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import pytest

from services.kgentsd.reactor import (
    DEFAULT_MAPPINGS,
    Event,
    EventMapping,
    EventSource,
    Reaction,
    ReactionStatus,
    WitnessReactor,
    ci_status_event,
    create_reactor,
    create_test_failure_event,
    crystallization_ready_event,
    git_commit_event,
    health_tick_event,
    pr_opened_event,
    session_start_event,
)
from services.kgentsd.workflows import (
    CI_MONITOR,
    CODE_CHANGE_RESPONSE,
    HEALTH_CHECK,
    MORNING_STANDUP,
    TEST_FAILURE_RESPONSE,
)
from services.witness.polynomial import TrustLevel

# =============================================================================
# Event Creation Tests
# =============================================================================


class TestEventCreation:
    """Test event factory functions."""

    def test_git_commit_event(self) -> None:
        """Test git commit event creation."""
        event = git_commit_event(
            sha="abc123",
            message="Fix bug in auth",
            author="kent@example.com",
            files_changed=["src/auth.py", "tests/test_auth.py"],
        )

        assert event.source == EventSource.GIT
        assert event.event_type == "commit"
        assert event.data["sha"] == "abc123"
        assert event.data["message"] == "Fix bug in auth"
        assert event.data["author"] == "kent@example.com"
        assert len(event.data["files_changed"]) == 2
        assert event.event_id.startswith("evt-")

    def test_create_test_failure_event(self) -> None:
        """Test test failure event creation."""
        event = create_test_failure_event(
            test_file="tests/test_auth.py",
            test_name="test_login_fails_without_token",
            error_message="AssertionError: expected True",
            traceback="...",
        )

        assert event.source == EventSource.TEST
        assert event.event_type == "failure"
        assert event.data["test_file"] == "tests/test_auth.py"
        assert event.data["test_name"] == "test_login_fails_without_token"

    def test_pr_opened_event(self) -> None:
        """Test PR opened event creation."""
        event = pr_opened_event(
            pr_number=42,
            title="Add new feature",
            author="kent",
            base_branch="main",
            head_branch="feature/new",
        )

        assert event.source == EventSource.PR
        assert event.event_type == "opened"
        assert event.data["pr_number"] == 42
        assert event.data["title"] == "Add new feature"

    def test_ci_status_event(self) -> None:
        """Test CI status event creation."""
        event = ci_status_event(
            status="failing",
            pipeline_name="main-build",
            url="https://ci.example.com/build/123",
        )

        assert event.source == EventSource.CI
        assert event.event_type == "status"
        assert event.data["status"] == "failing"

    def test_session_start_event(self) -> None:
        """Test session start event creation."""
        event = session_start_event(
            session_id="sess-123",
            context="morning standup",
        )

        assert event.source == EventSource.SESSION
        assert event.event_type == "start"
        assert event.data["session_id"] == "sess-123"

    def test_health_tick_event(self) -> None:
        """Test health tick event creation."""
        event = health_tick_event()

        assert event.source == EventSource.HEALTH
        assert event.event_type == "tick"

    def test_crystallization_ready_event(self) -> None:
        """Test crystallization ready event creation."""
        event = crystallization_ready_event(
            session_id="sess-456",
            thought_count=25,
        )

        assert event.source == EventSource.CRYSTAL
        assert event.event_type == "ready"
        assert event.data["thought_count"] == 25


# =============================================================================
# Event Mapping Tests
# =============================================================================


class TestEventMapping:
    """Test event-workflow mapping logic."""

    def test_default_mappings_exist(self) -> None:
        """Test that default mappings are defined."""
        assert len(DEFAULT_MAPPINGS) > 0
        # Should have mappings for key event types
        sources = {m.source for m in DEFAULT_MAPPINGS}
        assert EventSource.GIT in sources
        assert EventSource.TEST in sources
        assert EventSource.CI in sources

    def test_mapping_matches_event(self) -> None:
        """Test that mappings correctly match events."""
        mapping = EventMapping(
            source=EventSource.GIT,
            event_type="commit",
            workflow=CODE_CHANGE_RESPONSE,
            required_trust=TrustLevel.BOUNDED,
        )

        # Should match git commit
        commit = git_commit_event("abc", "msg")
        assert mapping.matches(commit) is True

        # Should not match git push (different event type)
        push = Event(source=EventSource.GIT, event_type="push")
        assert mapping.matches(push) is False

        # Should not match test failure (different source)
        failure = create_test_failure_event("test.py", "test_foo")
        assert mapping.matches(failure) is False

    def test_wildcard_mapping(self) -> None:
        """Test wildcard event type matching."""
        mapping = EventMapping(
            source=EventSource.GIT,
            event_type="*",  # Match all git events
            workflow=CODE_CHANGE_RESPONSE,
            required_trust=TrustLevel.READ_ONLY,
        )

        # Should match any git event
        assert mapping.matches(git_commit_event("abc", "msg")) is True
        assert mapping.matches(Event(source=EventSource.GIT, event_type="push")) is True
        assert mapping.matches(Event(source=EventSource.GIT, event_type="branch")) is True

        # Should not match non-git events
        assert mapping.matches(create_test_failure_event("t.py", "test")) is False

    def test_disabled_mapping(self) -> None:
        """Test that disabled mappings don't match."""
        mapping = EventMapping(
            source=EventSource.GIT,
            event_type="commit",
            workflow=CODE_CHANGE_RESPONSE,
            required_trust=TrustLevel.BOUNDED,
            enabled=False,
        )

        commit = git_commit_event("abc", "msg")
        assert mapping.matches(commit) is False


# =============================================================================
# Reaction Tests
# =============================================================================


class TestReaction:
    """Test reaction lifecycle."""

    def test_reaction_creation(self) -> None:
        """Test reaction creation with defaults."""
        event = git_commit_event("abc", "msg")
        reaction = Reaction(
            event=event,
            workflow=CODE_CHANGE_RESPONSE,
            workflow_name="Code Change Response",
            required_trust=TrustLevel.BOUNDED,
        )

        assert reaction.reaction_id.startswith("rxn-")
        assert reaction.event == event
        assert reaction.workflow_name == "Code Change Response"
        assert reaction.status == ReactionStatus.PENDING
        assert reaction.is_approved is False
        assert reaction.can_run is False

    def test_reaction_approval(self) -> None:
        """Test reaction approval with trust level."""
        reaction = Reaction(
            event=git_commit_event("abc", "msg"),
            workflow=CODE_CHANGE_RESPONSE,
            required_trust=TrustLevel.BOUNDED,
            current_trust=TrustLevel.READ_ONLY,
        )

        # Insufficient trust
        assert reaction.is_approved is False
        result = reaction.approve(TrustLevel.READ_ONLY)
        assert result is False

        # Sufficient trust
        result = reaction.approve(TrustLevel.BOUNDED)
        assert result is True
        assert reaction.status == ReactionStatus.APPROVED
        assert reaction.is_approved is True
        assert reaction.can_run is True

    def test_reaction_rejection(self) -> None:
        """Test reaction rejection."""
        reaction = Reaction(
            event=git_commit_event("abc", "msg"),
            required_trust=TrustLevel.AUTONOMOUS,
        )

        reaction.reject("User declined")

        assert reaction.status == ReactionStatus.REJECTED
        assert reaction.error == "User declined"
        assert reaction.completed_at is not None
        assert reaction.can_run is False

    def test_reaction_expiry(self) -> None:
        """Test reaction expiry detection."""
        # Not expired
        reaction = Reaction(
            event=git_commit_event("abc", "msg"),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert reaction.is_expired is False

        # Expired
        reaction_old = Reaction(
            event=git_commit_event("abc", "msg"),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert reaction_old.is_expired is True
        assert reaction_old.can_run is False

    def test_reaction_to_dict(self) -> None:
        """Test reaction serialization."""
        event = git_commit_event("abc", "msg")
        reaction = Reaction(
            event=event,
            workflow_name="Test Workflow",
            required_trust=TrustLevel.BOUNDED,
        )

        data = reaction.to_dict()
        assert data["reaction_id"] == reaction.reaction_id
        assert data["event_id"] == event.event_id
        assert data["workflow_name"] == "Test Workflow"
        assert data["required_trust"] == "BOUNDED"
        assert data["status"] == "PENDING"


# =============================================================================
# Reactor Tests
# =============================================================================


class TestWitnessReactor:
    """Test the WitnessReactor."""

    def test_reactor_creation(self) -> None:
        """Test reactor creation with factory."""
        reactor = create_reactor()

        assert reactor is not None
        assert len(reactor.mappings) > 0
        assert reactor._reaction_count == 0

    @pytest.mark.asyncio
    async def test_react_to_event(self) -> None:
        """Test reacting to an event creates a reaction."""
        reactor = create_reactor()

        event = git_commit_event("abc123", "Fix bug")
        reaction = await reactor.react(event)

        assert reaction is not None
        assert reaction.event == event
        assert reaction.workflow_name == "Code Change Response"
        assert reactor._reaction_count == 1

    @pytest.mark.asyncio
    async def test_react_no_matching_mapping(self) -> None:
        """Test that unmatched events return None."""
        reactor = WitnessReactor(mappings=[])  # Empty mappings

        event = git_commit_event("abc", "msg")
        reaction = await reactor.react(event)

        assert reaction is None

    @pytest.mark.asyncio
    async def test_debouncing(self) -> None:
        """Test that rapid events are debounced."""
        reactor = WitnessReactor(
            mappings=[
                EventMapping(
                    source=EventSource.GIT,
                    event_type="commit",
                    workflow=CODE_CHANGE_RESPONSE,
                    required_trust=TrustLevel.BOUNDED,
                    debounce=timedelta(seconds=10),
                )
            ]
        )

        # First event should go through
        event1 = git_commit_event("abc", "msg1")
        reaction1 = await reactor.react(event1)
        assert reaction1 is not None

        # Second event within debounce window should be skipped
        event2 = git_commit_event("def", "msg2")
        reaction2 = await reactor.react(event2)
        assert reaction2 is None

    def test_add_custom_mapping(self) -> None:
        """Test adding custom mappings."""
        reactor = create_reactor()
        initial_count = len(reactor.mappings)

        custom_mapping = EventMapping(
            source=EventSource.TIMER,
            event_type="custom",
            workflow=HEALTH_CHECK,
            required_trust=TrustLevel.READ_ONLY,
        )
        reactor.add_mapping(custom_mapping)

        assert len(reactor.mappings) == initial_count + 1

    def test_remove_mapping(self) -> None:
        """Test removing mappings."""
        reactor = create_reactor()
        initial_count = len(reactor.mappings)

        # Remove git commit mapping
        removed = reactor.remove_mapping(EventSource.GIT, "commit")
        assert removed is True
        assert len(reactor.mappings) == initial_count - 1

        # Try to remove non-existent
        removed = reactor.remove_mapping(EventSource.GIT, "nonexistent")
        assert removed is False

    @pytest.mark.asyncio
    async def test_approve_reaction(self) -> None:
        """Test approving pending reactions."""
        reactor = create_reactor()

        # Create a pending reaction manually
        reaction = Reaction(
            event=git_commit_event("abc", "msg"),
            workflow=CODE_CHANGE_RESPONSE,
            workflow_name="Code Change Response",
            required_trust=TrustLevel.BOUNDED,
        )
        reactor._reactions[reaction.reaction_id] = reaction

        # Approve with sufficient trust
        result = reactor.approve(reaction.reaction_id, TrustLevel.AUTONOMOUS)
        assert result is True
        # Note: In real usage, this would queue execution
        # Give the async task time to be created
        import asyncio

        await asyncio.sleep(0.01)

    def test_reject_reaction(self) -> None:
        """Test rejecting reactions."""
        reactor = create_reactor()

        # Create a pending reaction
        reaction = Reaction(
            event=git_commit_event("abc", "msg"),
            required_trust=TrustLevel.AUTONOMOUS,
        )
        reactor._reactions[reaction.reaction_id] = reaction

        result = reactor.reject(reaction.reaction_id, "Not now")
        assert result is True
        assert reaction.status == ReactionStatus.REJECTED
        assert reaction.error == "Not now"

    def test_pending_reactions(self) -> None:
        """Test getting pending reactions."""
        reactor = create_reactor()

        # Add some reactions
        pending = Reaction(
            event=git_commit_event("a", "m"),
            status=ReactionStatus.PENDING,
        )
        completed = Reaction(
            event=git_commit_event("b", "m"),
            status=ReactionStatus.COMPLETED,
        )
        reactor._reactions[pending.reaction_id] = pending
        reactor._reactions[completed.reaction_id] = completed

        pending_list = reactor.pending_reactions
        assert len(pending_list) == 1
        assert pending_list[0] == pending

    def test_cleanup_expired(self) -> None:
        """Test cleaning up expired reactions."""
        reactor = create_reactor()

        # Add expired reaction
        expired = Reaction(
            event=git_commit_event("a", "m"),
            status=ReactionStatus.PENDING,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        # Add valid reaction
        valid = Reaction(
            event=git_commit_event("b", "m"),
            status=ReactionStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        reactor._reactions[expired.reaction_id] = expired
        reactor._reactions[valid.reaction_id] = valid

        removed = reactor.cleanup_expired()
        assert removed == 1
        assert valid.reaction_id in reactor._reactions
        assert expired.reaction_id not in reactor._reactions

    def test_get_stats(self) -> None:
        """Test reactor statistics."""
        reactor = create_reactor()

        # Add some reactions with different statuses
        reactor._reactions["r1"] = Reaction(status=ReactionStatus.PENDING)
        reactor._reactions["r2"] = Reaction(status=ReactionStatus.COMPLETED)
        reactor._reactions["r3"] = Reaction(status=ReactionStatus.PENDING)

        stats = reactor.get_stats()
        assert stats["stored_reactions"] == 3
        assert stats["pending"] == 2
        assert stats["by_status"]["PENDING"] == 2
        assert stats["by_status"]["COMPLETED"] == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestReactorIntegration:
    """Integration tests for reactor with other components."""

    @pytest.mark.asyncio
    async def test_reactor_creates_correct_reaction_for_event_type(self) -> None:
        """Test that different events map to correct workflows."""
        reactor = create_reactor()

        # Git commit → CODE_CHANGE_RESPONSE
        git_reaction = await reactor.react(git_commit_event("abc", "msg"))
        assert git_reaction is not None
        assert git_reaction.workflow_name == "Code Change Response"

        # Clear debounce for next test
        reactor._debounce_timers.clear()

        # Test failure → TEST_FAILURE_RESPONSE
        test_reaction = await reactor.react(create_test_failure_event("t.py", "test"))
        assert test_reaction is not None
        assert test_reaction.workflow_name == "Test Failure Response"

        # Health tick → HEALTH_CHECK
        health_reaction = await reactor.react(health_tick_event())
        assert health_reaction is not None
        assert health_reaction.workflow_name == "Health Check"

    @pytest.mark.asyncio
    async def test_trust_levels_propagate_from_mapping(self) -> None:
        """Test that required trust levels come from mappings."""
        reactor = create_reactor()

        # Test failure requires L3 (AUTONOMOUS)
        test_reaction = await reactor.react(create_test_failure_event("t.py", "test"))
        assert test_reaction is not None
        assert test_reaction.required_trust == TrustLevel.AUTONOMOUS

        # Health check requires L0 (READ_ONLY)
        health_reaction = await reactor.react(health_tick_event())
        assert health_reaction is not None
        assert health_reaction.required_trust == TrustLevel.READ_ONLY
