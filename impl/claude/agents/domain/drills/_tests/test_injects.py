"""
Tests for Inject Framework: Runtime Crisis Escalation Events.

Verifies:
1. Inject specifications (predefined types, properties)
2. Inject state lifecycle (pending, triggered, active, resolved)
3. Inject sequences (time-based, state-based, manual triggers)
4. Auto-escalation behavior
"""

from datetime import datetime, timedelta

import pytest

from agents.domain.drills.injects import (
    CUSTOMER_ESCALATION_INJECT,
    EXECUTIVE_CALL_INJECT,
    MEDIA_STORY_INJECT,
    PREDEFINED_INJECTS,
    REGULATOR_INQUIRY_INJECT,
    SOCIAL_MEDIA_INJECT,
    TECHNICAL_COMPLICATION_INJECT,
    InjectSequence,
    InjectSpec,
    InjectState,
    InjectStatus,
    InjectTrigger,
    InjectType,
    create_data_breach_injects,
    create_inject,
    create_service_outage_injects,
)


class TestInjectTypes:
    """Tests for InjectType enum."""

    def test_has_nine_types(self) -> None:
        """All inject types exist."""
        assert len(InjectType) == 9
        assert InjectType.MEDIA_STORY is not None
        assert InjectType.EXECUTIVE_CALL is not None
        assert InjectType.REGULATOR_INQUIRY is not None
        assert InjectType.CUSTOMER_ESCALATION is not None
        assert InjectType.TECHNICAL_COMPLICATION is not None
        assert InjectType.PERSONNEL_ISSUE is not None
        assert InjectType.SOCIAL_MEDIA is not None
        assert InjectType.COMPETITOR_STATEMENT is not None
        assert InjectType.CUSTOM is not None


class TestInjectTrigger:
    """Tests for InjectTrigger enum."""

    def test_has_five_triggers(self) -> None:
        """All trigger types exist."""
        assert len(InjectTrigger) == 5
        assert InjectTrigger.MANUAL is not None
        assert InjectTrigger.TIME_BASED is not None
        assert InjectTrigger.STATE_BASED is not None
        assert InjectTrigger.RANDOM is not None
        assert InjectTrigger.CONDITIONAL is not None


class TestInjectStatus:
    """Tests for InjectStatus enum."""

    def test_has_six_statuses(self) -> None:
        """All inject statuses exist."""
        assert len(InjectStatus) == 6
        assert InjectStatus.PENDING is not None
        assert InjectStatus.TRIGGERED is not None
        assert InjectStatus.ACTIVE is not None
        assert InjectStatus.RESOLVED is not None
        assert InjectStatus.ESCALATED is not None
        assert InjectStatus.IGNORED is not None


class TestPredefinedInjects:
    """Tests for predefined inject specifications."""

    def test_media_story_inject(self) -> None:
        """MEDIA_STORY inject spec is correct."""
        spec = MEDIA_STORY_INJECT
        assert spec.inject_type == InjectType.MEDIA_STORY
        assert spec.name == "Media Story Published"
        assert "TechCrunch" in spec.headline
        assert spec.urgency == "critical"
        assert spec.stress_increase > 0
        assert "PR Director" in spec.target_roles

    def test_executive_call_inject(self) -> None:
        """EXECUTIVE_CALL inject spec is correct."""
        spec = EXECUTIVE_CALL_INJECT
        assert spec.inject_type == InjectType.EXECUTIVE_CALL
        assert "Board" in spec.headline
        assert spec.urgency == "critical"
        assert "Executive" in spec.target_roles

    def test_regulator_inquiry_inject(self) -> None:
        """REGULATOR_INQUIRY inject spec is correct."""
        spec = REGULATOR_INQUIRY_INJECT
        assert spec.inject_type == InjectType.REGULATOR_INQUIRY
        assert "DPA" in spec.headline
        assert "Legal Counsel" in spec.target_roles
        # Highest stress for regulatory issues
        assert spec.stress_increase >= 0.25

    def test_customer_escalation_inject(self) -> None:
        """CUSTOMER_ESCALATION inject spec is correct."""
        spec = CUSTOMER_ESCALATION_INJECT
        assert spec.inject_type == InjectType.CUSTOMER_ESCALATION
        assert "Customer Success" in spec.target_roles

    def test_technical_complication_inject(self) -> None:
        """TECHNICAL_COMPLICATION inject spec is correct."""
        spec = TECHNICAL_COMPLICATION_INJECT
        assert spec.inject_type == InjectType.TECHNICAL_COMPLICATION
        assert "backup" in spec.headline.lower() or "ALERT" in spec.headline
        assert "On-Call Engineer" in spec.target_roles

    def test_social_media_inject(self) -> None:
        """SOCIAL_MEDIA inject spec is correct."""
        spec = SOCIAL_MEDIA_INJECT
        assert spec.inject_type == InjectType.SOCIAL_MEDIA
        assert "tweet" in spec.headline.lower() or "TRENDING" in spec.headline
        assert spec.affects_all is True

    def test_all_predefined_in_registry(self) -> None:
        """All predefined specs are in registry."""
        assert InjectType.MEDIA_STORY in PREDEFINED_INJECTS
        assert InjectType.EXECUTIVE_CALL in PREDEFINED_INJECTS
        assert InjectType.REGULATOR_INQUIRY in PREDEFINED_INJECTS
        assert InjectType.CUSTOMER_ESCALATION in PREDEFINED_INJECTS
        assert InjectType.TECHNICAL_COMPLICATION in PREDEFINED_INJECTS
        assert InjectType.SOCIAL_MEDIA in PREDEFINED_INJECTS


class TestInjectState:
    """Tests for InjectState lifecycle."""

    def test_initial_state_is_pending(self) -> None:
        """Inject starts in PENDING status."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        assert inject.status == InjectStatus.PENDING
        assert inject.is_pending is True
        assert inject.triggered_at is None

    def test_trigger_transitions_to_triggered(self) -> None:
        """Triggering inject transitions to TRIGGERED."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()

        assert inject.status == InjectStatus.TRIGGERED
        assert inject.is_pending is False
        assert inject.triggered_at is not None

    def test_cannot_trigger_twice(self) -> None:
        """Cannot trigger an already-triggered inject."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()

        with pytest.raises(ValueError, match="Cannot trigger inject"):
            inject.trigger()

    def test_activate_transitions_to_active(self) -> None:
        """Activating inject transitions to ACTIVE."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()
        inject.activate()

        assert inject.status == InjectStatus.ACTIVE
        assert inject.is_active is True

    def test_resolve_transitions_to_resolved(self) -> None:
        """Resolving inject transitions to RESOLVED."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()
        inject.activate()
        inject.resolve(handler="PR Director", notes="Statement issued")

        assert inject.status == InjectStatus.RESOLVED
        assert inject.resolved_at is not None
        assert "PR Director" in inject.handled_by
        assert inject.resolution_notes == "Statement issued"

    def test_escalate_transitions_to_escalated(self) -> None:
        """Escalating inject transitions to ESCALATED."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()
        inject.activate()
        inject.escalate(reason="Response was inadequate")

        assert inject.status == InjectStatus.ESCALATED
        assert "inadequate" in inject.resolution_notes

    def test_ignore_transitions_to_ignored(self) -> None:
        """Ignoring inject transitions to IGNORED."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()
        inject.activate()
        inject.ignore()

        assert inject.status == InjectStatus.IGNORED

    def test_time_since_trigger(self) -> None:
        """time_since_trigger returns elapsed time."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        assert inject.time_since_trigger is None

        inject.trigger()
        elapsed = inject.time_since_trigger
        assert elapsed is not None
        assert elapsed.total_seconds() >= 0

    def test_should_auto_escalate(self) -> None:
        """should_auto_escalate returns True when time exceeded."""
        spec = InjectSpec(
            inject_type=InjectType.CUSTOM,
            name="Test Inject",
            description="For testing",
            headline="Test",
            target_roles=("Tester",),
            auto_escalate_minutes=1,  # Very short for testing
        )
        inject = InjectState(spec=spec)
        inject.trigger()
        inject.activate()

        # Just triggered - should not escalate
        assert inject.should_auto_escalate() is False

        # Simulate time passing
        inject.triggered_at = datetime.now() - timedelta(minutes=2)
        assert inject.should_auto_escalate() is True

    def test_manifest_contains_required_fields(self) -> None:
        """Manifest includes all required display fields."""
        inject = InjectState(spec=MEDIA_STORY_INJECT)
        inject.trigger()

        manifest = inject.manifest()

        assert "name" in manifest
        assert "type" in manifest
        assert "headline" in manifest
        assert "status" in manifest
        assert "urgency" in manifest
        assert "target_roles" in manifest
        assert "triggered_at" in manifest


class TestInjectSequence:
    """Tests for InjectSequence management."""

    def test_add_inject(self) -> None:
        """Can add inject to sequence."""
        sequence = InjectSequence()
        inject = sequence.add(InjectType.MEDIA_STORY)

        assert len(sequence.injects) == 1
        assert inject.spec == MEDIA_STORY_INJECT

    def test_add_time_based_inject(self) -> None:
        """Can add time-based inject."""
        sequence = InjectSequence()
        inject = sequence.add(
            InjectType.MEDIA_STORY,
            trigger_type=InjectTrigger.TIME_BASED,
            trigger_after_minutes=15,
        )

        assert inject.trigger_type == InjectTrigger.TIME_BASED
        assert inject.trigger_after_minutes == 15

    def test_add_state_based_inject(self) -> None:
        """Can add state-based inject."""
        sequence = InjectSequence()
        inject = sequence.add(
            InjectType.TECHNICAL_COMPLICATION,
            trigger_type=InjectTrigger.STATE_BASED,
            trigger_on_phase="RESPONSE",
        )

        assert inject.trigger_type == InjectTrigger.STATE_BASED
        assert inject.trigger_on_phase == "RESPONSE"

    def test_start_sequence(self) -> None:
        """Starting sequence sets start time."""
        sequence = InjectSequence()
        sequence.add(InjectType.MEDIA_STORY)
        sequence.start()

        assert sequence._started_at is not None

    def test_tick_triggers_time_based(self) -> None:
        """Tick triggers time-based injects when time elapsed."""
        sequence = InjectSequence()
        sequence.add(
            InjectType.MEDIA_STORY,
            trigger_type=InjectTrigger.TIME_BASED,
            trigger_after_minutes=0,  # Immediate for testing
        )
        sequence.start()

        # Should trigger immediately
        triggered = sequence.tick()
        assert len(triggered) == 1
        assert triggered[0].spec.inject_type == InjectType.MEDIA_STORY

    def test_tick_triggers_state_based(self) -> None:
        """Tick triggers state-based injects when phase matches."""
        sequence = InjectSequence()
        sequence.add(
            InjectType.TECHNICAL_COMPLICATION,
            trigger_type=InjectTrigger.STATE_BASED,
            trigger_on_phase="RESPONSE",
        )
        sequence.start()

        # Should not trigger in wrong phase
        triggered = sequence.tick(current_phase="INCIDENT")
        assert len(triggered) == 0

        # Should trigger in correct phase
        triggered = sequence.tick(current_phase="RESPONSE")
        assert len(triggered) == 1

    def test_manual_trigger(self) -> None:
        """Can manually trigger inject by index."""
        sequence = InjectSequence()
        sequence.add(InjectType.MEDIA_STORY, trigger_type=InjectTrigger.MANUAL)
        sequence.add(InjectType.EXECUTIVE_CALL, trigger_type=InjectTrigger.MANUAL)

        # Trigger second inject
        inject = sequence.trigger_manual(1)

        assert inject.status == InjectStatus.TRIGGERED
        assert inject.spec.inject_type == InjectType.EXECUTIVE_CALL

    def test_get_active_injects(self) -> None:
        """Can get all active injects."""
        sequence = InjectSequence()
        sequence.add(InjectType.MEDIA_STORY, trigger_type=InjectTrigger.MANUAL)
        sequence.add(InjectType.EXECUTIVE_CALL, trigger_type=InjectTrigger.MANUAL)

        assert len(sequence.get_active()) == 0

        inject1 = sequence.trigger_manual(0)
        inject1.activate()

        assert len(sequence.get_active()) == 1

    def test_get_pending_injects(self) -> None:
        """Can get all pending injects."""
        sequence = InjectSequence()
        sequence.add(InjectType.MEDIA_STORY)
        sequence.add(InjectType.EXECUTIVE_CALL)

        assert len(sequence.get_pending()) == 2

        sequence.trigger_manual(0)
        assert len(sequence.get_pending()) == 1

    def test_check_auto_escalations(self) -> None:
        """Auto-escalation check escalates overdue injects."""
        spec = InjectSpec(
            inject_type=InjectType.CUSTOM,
            name="Test",
            description="Test",
            headline="Test",
            target_roles=("Tester",),
            auto_escalate_minutes=1,
        )
        sequence = InjectSequence()
        state = InjectState(spec=spec)
        sequence.injects.append(state)

        state.trigger()
        state.activate()
        # Simulate time passing
        state.triggered_at = datetime.now() - timedelta(minutes=2)

        escalated = sequence.check_auto_escalations()
        assert len(escalated) == 1
        assert escalated[0].status == InjectStatus.ESCALATED


class TestInjectFactories:
    """Tests for inject factory functions."""

    def test_create_inject(self) -> None:
        """create_inject creates single inject."""
        inject = create_inject(InjectType.MEDIA_STORY)

        assert inject.spec.inject_type == InjectType.MEDIA_STORY
        assert inject.status == InjectStatus.PENDING

    def test_create_inject_with_trigger(self) -> None:
        """create_inject respects trigger configuration."""
        inject = create_inject(
            InjectType.EXECUTIVE_CALL,
            trigger_type=InjectTrigger.TIME_BASED,
            trigger_after_minutes=20,
        )

        assert inject.trigger_type == InjectTrigger.TIME_BASED
        assert inject.trigger_after_minutes == 20

    def test_create_service_outage_injects(self) -> None:
        """create_service_outage_injects creates standard sequence."""
        sequence = create_service_outage_injects()

        assert len(sequence.injects) >= 4
        # Should have media story and executive call
        types = [i.spec.inject_type for i in sequence.injects]
        assert InjectType.MEDIA_STORY in types
        assert InjectType.EXECUTIVE_CALL in types
        assert InjectType.TECHNICAL_COMPLICATION in types

    def test_create_data_breach_injects(self) -> None:
        """create_data_breach_injects creates standard sequence."""
        sequence = create_data_breach_injects()

        assert len(sequence.injects) >= 4
        # Should have regulator inquiry (important for breach)
        types = [i.spec.inject_type for i in sequence.injects]
        assert InjectType.MEDIA_STORY in types
        assert InjectType.REGULATOR_INQUIRY in types
        assert InjectType.EXECUTIVE_CALL in types
