"""
Tests for K-gent SoulEvent hierarchy.

K-gent Phase 2: These tests verify the SoulEvent types and factory
functions that form the vocabulary of K-gent streaming.
"""

from datetime import datetime, timezone

import pytest

from agents.k.events import (
    SoulEvent,
    SoulEventType,
    dialogue_end_event,
    dialogue_start_event,
    dialogue_turn_event,
    eigenvector_probe_event,
    error_event,
    feeling_event,
    gratitude_event,
    intercept_request_event,
    intercept_result_event,
    is_ambient_event,
    is_dialogue_event,
    is_external_event,
    is_intercept_event,
    is_request_event,
    is_system_event,
    mode_change_event,
    observation_event,
    perturbation_event,
    ping_event,
    pulse_event,
    self_challenge_event,
    state_snapshot_event,
    thought_event,
)


class TestSoulEventType:
    """Test SoulEventType enum."""

    def test_dialogue_events_exist(self) -> None:
        """Dialogue event types should exist."""
        assert SoulEventType.DIALOGUE_START.value == "dialogue_start"
        assert SoulEventType.DIALOGUE_TURN.value == "dialogue_turn"
        assert SoulEventType.DIALOGUE_END.value == "dialogue_end"

    def test_intercept_events_exist(self) -> None:
        """Intercept event types should exist."""
        assert SoulEventType.INTERCEPT_REQUEST.value == "intercept_request"
        assert SoulEventType.INTERCEPT_RESULT.value == "intercept_result"

    def test_system_events_exist(self) -> None:
        """System event types should exist."""
        assert SoulEventType.PULSE.value == "pulse"
        assert SoulEventType.PING.value == "ping"
        assert SoulEventType.STATE_SNAPSHOT.value == "state_snapshot"

    def test_mode_event_exists(self) -> None:
        """Mode change event type should exist."""
        assert SoulEventType.MODE_CHANGE.value == "mode_change"

    def test_error_event_exists(self) -> None:
        """Error event type should exist."""
        assert SoulEventType.ERROR.value == "error"


class TestSoulEvent:
    """Test SoulEvent dataclass."""

    def test_create_basic_event(self) -> None:
        """Should create a basic event."""
        now = datetime.now(timezone.utc)
        event = SoulEvent(
            event_type=SoulEventType.PING,
            timestamp=now,
            payload={},
        )

        assert event.event_type == SoulEventType.PING
        assert event.timestamp == now
        assert event.payload == {}
        assert event.soul_state is None
        assert event.correlation_id is None

    def test_create_event_with_state(self) -> None:
        """Should create event with soul state."""
        now = datetime.now(timezone.utc)
        state = {"mode": "reflect", "interactions": 5}
        event = SoulEvent(
            event_type=SoulEventType.DIALOGUE_TURN,
            timestamp=now,
            payload={"message": "hello"},
            soul_state=state,
        )

        assert event.soul_state == state

    def test_create_event_with_correlation_id(self) -> None:
        """Should create event with correlation ID."""
        now = datetime.now(timezone.utc)
        event = SoulEvent(
            event_type=SoulEventType.DIALOGUE_TURN,
            timestamp=now,
            payload={},
            correlation_id="test-123",
        )

        assert event.correlation_id == "test-123"

    def test_event_is_frozen(self) -> None:
        """Events should be immutable (frozen dataclass)."""
        event = ping_event()
        # Frozen dataclasses raise FrozenInstanceError on direct attribute assignment
        # (FrozenInstanceError is a subclass of AttributeError)
        with pytest.raises(AttributeError):
            event.event_type = SoulEventType.ERROR  # type: ignore[misc]

    def test_to_dict(self) -> None:
        """Should convert to dict."""
        event = dialogue_turn_event(
            message="test",
            mode="reflect",
            correlation_id="corr-123",
        )
        d = event.to_dict()

        assert d["type"] == "dialogue_turn"
        assert "timestamp" in d
        assert d["payload"]["message"] == "test"
        assert d["correlation_id"] == "corr-123"

    def test_from_dict(self) -> None:
        """Should create from dict."""
        original = dialogue_turn_event(message="test")
        d = original.to_dict()
        restored = SoulEvent.from_dict(d)

        assert restored.event_type == original.event_type
        assert restored.payload == original.payload

    def test_to_dict_excludes_none_state(self) -> None:
        """to_dict should exclude None soul_state."""
        event = ping_event()
        d = event.to_dict()
        assert "soul_state" not in d

    def test_to_dict_includes_state_when_present(self) -> None:
        """to_dict should include soul_state when present."""
        event = state_snapshot_event(state={"mode": "reflect"})
        d = event.to_dict()
        assert "soul_state" in d


class TestDialogueEventFactories:
    """Test dialogue event factory functions."""

    def test_dialogue_start_event(self) -> None:
        """Should create dialogue start event."""
        event = dialogue_start_event(mode="challenge", correlation_id="start-1")

        assert event.event_type == SoulEventType.DIALOGUE_START
        assert event.payload["mode"] == "challenge"
        assert event.correlation_id == "start-1"

    def test_dialogue_turn_event_request(self) -> None:
        """Should create dialogue turn request event."""
        event = dialogue_turn_event(
            message="What should I focus on?",
            mode="reflect",
            is_request=True,
        )

        assert event.event_type == SoulEventType.DIALOGUE_TURN
        assert event.payload["message"] == "What should I focus on?"
        assert event.payload["mode"] == "reflect"
        assert event.payload["is_request"] is True

    def test_dialogue_turn_event_response(self) -> None:
        """Should create dialogue turn response event."""
        event = dialogue_turn_event(
            message="What should I focus on?",
            response="Consider your priorities...",
            mode="reflect",
            is_request=False,
        )

        assert event.payload["is_request"] is False
        assert event.payload["response"] == "Consider your priorities..."

    def test_dialogue_end_event(self) -> None:
        """Should create dialogue end event."""
        event = dialogue_end_event(reason="user_ended")

        assert event.event_type == SoulEventType.DIALOGUE_END
        assert event.payload["reason"] == "user_ended"


class TestInterceptEventFactories:
    """Test intercept event factory functions."""

    def test_intercept_request_event(self) -> None:
        """Should create intercept request event."""
        event = intercept_request_event(
            token_id="token-123",
            prompt="Delete all files?",
            severity="critical",
            options=["yes", "no"],
        )

        assert event.event_type == SoulEventType.INTERCEPT_REQUEST
        assert event.payload["token_id"] == "token-123"
        assert event.payload["prompt"] == "Delete all files?"
        assert event.payload["severity"] == "critical"
        assert event.payload["options"] == ["yes", "no"]
        assert event.correlation_id == "token-123"

    def test_intercept_result_event(self) -> None:
        """Should create intercept result event."""
        event = intercept_result_event(
            token_id="token-123",
            handled=False,
            recommendation="escalate",
            confidence=0.3,
            reasoning="Dangerous operation detected",
        )

        assert event.event_type == SoulEventType.INTERCEPT_RESULT
        assert event.payload["handled"] is False
        assert event.payload["recommendation"] == "escalate"
        assert event.payload["confidence"] == 0.3
        assert event.correlation_id == "token-123"


class TestModeEventFactories:
    """Test mode change event factory."""

    def test_mode_change_event(self) -> None:
        """Should create mode change event."""
        event = mode_change_event(
            from_mode="reflect",
            to_mode="challenge",
            correlation_id="mode-1",
        )

        assert event.event_type == SoulEventType.MODE_CHANGE
        assert event.payload["from_mode"] == "reflect"
        assert event.payload["to_mode"] == "challenge"


class TestSystemEventFactories:
    """Test system event factory functions."""

    def test_pulse_event(self) -> None:
        """Should create pulse event."""
        event = pulse_event(
            interactions_count=10,
            tokens_used_session=500,
            active_mode="advise",
            is_healthy=True,
        )

        assert event.event_type == SoulEventType.PULSE
        assert event.payload["interactions_count"] == 10
        assert event.payload["tokens_used_session"] == 500
        assert event.payload["active_mode"] == "advise"
        assert event.payload["is_healthy"] is True

    def test_state_snapshot_event(self) -> None:
        """Should create state snapshot event."""
        state = {"mode": "explore", "eigenvectors": {"aesthetic": 0.15}}
        event = state_snapshot_event(state=state)

        assert event.event_type == SoulEventType.STATE_SNAPSHOT
        assert event.soul_state == state

    def test_ping_event(self) -> None:
        """Should create ping event."""
        event = ping_event()

        assert event.event_type == SoulEventType.PING
        assert event.payload == {}

    def test_eigenvector_probe_event(self) -> None:
        """Should create eigenvector probe event."""
        eigenvectors = {"aesthetic": 0.15, "categorical": 0.92}
        event = eigenvector_probe_event(eigenvectors=eigenvectors)

        assert event.event_type == SoulEventType.EIGENVECTOR_PROBE
        assert event.payload["eigenvectors"] == eigenvectors


class TestErrorEventFactory:
    """Test error event factory."""

    def test_error_event_basic(self) -> None:
        """Should create basic error event."""
        event = error_event(error="Something went wrong")

        assert event.event_type == SoulEventType.ERROR
        assert event.payload["error"] == "Something went wrong"

    def test_error_event_with_type(self) -> None:
        """Should create error event with type."""
        event = error_event(
            error="Connection failed",
            error_type="ConnectionError",
        )

        assert event.payload["error_type"] == "ConnectionError"

    def test_error_event_with_original_type(self) -> None:
        """Should create error event with original event type."""
        event = error_event(
            error="Processing failed",
            original_event_type="dialogue_turn",
            correlation_id="corr-123",
        )

        assert event.payload["original_event_type"] == "dialogue_turn"
        assert event.correlation_id == "corr-123"


class TestEventPredicates:
    """Test event predicate functions."""

    def test_is_dialogue_event(self) -> None:
        """Should identify dialogue events."""
        assert is_dialogue_event(dialogue_start_event(mode="reflect"))
        assert is_dialogue_event(dialogue_turn_event(message="hello"))
        assert is_dialogue_event(dialogue_end_event())

        assert not is_dialogue_event(pulse_event())
        assert not is_dialogue_event(intercept_request_event("t", "p"))

    def test_is_intercept_event(self) -> None:
        """Should identify intercept events."""
        assert is_intercept_event(intercept_request_event("t", "p"))
        assert is_intercept_event(intercept_result_event("t", True))

        assert not is_intercept_event(dialogue_turn_event(message="hello"))
        assert not is_intercept_event(pulse_event())

    def test_is_system_event(self) -> None:
        """Should identify system events."""
        assert is_system_event(pulse_event())
        assert is_system_event(ping_event())
        assert is_system_event(state_snapshot_event(state={}))

        assert not is_system_event(dialogue_turn_event(message="hello"))
        assert not is_system_event(intercept_request_event("t", "p"))

    def test_is_request_event(self) -> None:
        """Should identify request events."""
        assert is_request_event(dialogue_turn_event(message="hello", is_request=True))
        assert is_request_event(intercept_request_event("t", "p"))
        assert is_request_event(mode_change_event("a", "b"))

        # Response events should not be requests
        response = dialogue_turn_event(message="hi", is_request=False)
        assert not is_request_event(response)

        # System events are not requests
        assert not is_request_event(pulse_event())


class TestEventTimestamps:
    """Test event timestamp handling."""

    def test_event_has_utc_timestamp(self) -> None:
        """Events should have UTC timestamps."""
        event = ping_event()
        assert event.timestamp.tzinfo is not None

    def test_timestamp_is_recent(self) -> None:
        """Event timestamps should be recent."""
        before = datetime.now(timezone.utc)
        event = ping_event()
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after

    def test_timestamp_roundtrip(self) -> None:
        """Timestamps should survive serialization."""
        original = dialogue_turn_event(message="test")
        d = original.to_dict()
        restored = SoulEvent.from_dict(d)

        # Compare with some tolerance for formatting
        assert abs((restored.timestamp - original.timestamp).total_seconds()) < 1


class TestEventCorrelation:
    """Test event correlation ID handling."""

    def test_correlation_id_preserved(self) -> None:
        """Correlation IDs should be preserved."""
        event = dialogue_turn_event(
            message="test",
            correlation_id="my-correlation-id",
        )

        assert event.correlation_id == "my-correlation-id"
        assert event.to_dict()["correlation_id"] == "my-correlation-id"

    def test_intercept_uses_token_id_as_correlation(self) -> None:
        """Intercept events should use token_id as default correlation."""
        event = intercept_request_event(
            token_id="token-abc",
            prompt="test",
        )

        assert event.correlation_id == "token-abc"


# =============================================================================
# Ambient Event Tests: The Soul Present, Not Invoked
# =============================================================================


class TestAmbientEventTypes:
    """Test ambient event types exist."""

    def test_thought_event_exists(self) -> None:
        """THOUGHT event type should exist."""
        assert SoulEventType.THOUGHT.value == "thought"

    def test_feeling_event_exists(self) -> None:
        """FEELING event type should exist."""
        assert SoulEventType.FEELING.value == "feeling"

    def test_observation_event_exists(self) -> None:
        """OBSERVATION event type should exist."""
        assert SoulEventType.OBSERVATION.value == "observation"

    def test_self_challenge_event_exists(self) -> None:
        """SELF_CHALLENGE event type should exist."""
        assert SoulEventType.SELF_CHALLENGE.value == "self_challenge"

    def test_perturbation_event_exists(self) -> None:
        """PERTURBATION event type should exist."""
        assert SoulEventType.PERTURBATION.value == "perturbation"

    def test_gratitude_event_exists(self) -> None:
        """GRATITUDE event type should exist."""
        assert SoulEventType.GRATITUDE.value == "gratitude"


class TestThoughtEventFactory:
    """Test thought event factory."""

    def test_create_thought_event(self) -> None:
        """Should create thought event with content."""
        event = thought_event(content="What if composability is the key?")

        assert event.event_type == SoulEventType.THOUGHT
        assert event.payload["content"] == "What if composability is the key?"
        assert event.payload["depth"] == 1
        assert event.payload["triggered_by"] is None

    def test_thought_event_with_depth(self) -> None:
        """Should create thought event with depth."""
        event = thought_event(
            content="Deep rumination on category theory",
            depth=3,
            triggered_by="eigenvector_tension",
        )

        assert event.payload["depth"] == 3
        assert event.payload["triggered_by"] == "eigenvector_tension"

    def test_thought_event_with_correlation(self) -> None:
        """Should preserve correlation ID."""
        event = thought_event(
            content="Test thought",
            correlation_id="thought-123",
        )

        assert event.correlation_id == "thought-123"


class TestFeelingEventFactory:
    """Test feeling event factory."""

    def test_create_feeling_event(self) -> None:
        """Should create feeling event with valence."""
        event = feeling_event(valence="curious")

        assert event.event_type == SoulEventType.FEELING
        assert event.payload["valence"] == "curious"
        assert event.payload["intensity"] == 0.5

    def test_feeling_event_with_intensity(self) -> None:
        """Should create feeling event with intensity."""
        event = feeling_event(
            valence="delighted",
            intensity=0.9,
            cause="Test passed",
        )

        assert event.payload["intensity"] == 0.9
        assert event.payload["cause"] == "Test passed"

    def test_feeling_event_with_eigenvector_shift(self) -> None:
        """Should create feeling event with eigenvector shift."""
        shift = {"aesthetic": 0.05, "pragmatic": -0.02}
        event = feeling_event(
            valence="inspired",
            eigenvector_shift=shift,
        )

        assert event.payload["eigenvector_shift"] == shift


class TestObservationEventFactory:
    """Test observation event factory."""

    def test_create_observation_event(self) -> None:
        """Should create observation event with pattern."""
        event = observation_event(pattern="Functors compose freely")

        assert event.event_type == SoulEventType.OBSERVATION
        assert event.payload["pattern"] == "Functors compose freely"
        assert event.payload["confidence"] == 0.5
        assert event.payload["domain"] == "general"

    def test_observation_event_with_evidence(self) -> None:
        """Should create observation event with evidence."""
        evidence = ["test_functor_laws.py:62 passed", "all 10 functors registered"]
        event = observation_event(
            pattern="The categorical foundation is solid",
            confidence=0.95,
            domain="category_theory",
            evidence=evidence,
        )

        assert event.payload["confidence"] == 0.95
        assert event.payload["domain"] == "category_theory"
        assert event.payload["evidence"] == evidence


class TestSelfChallengeEventFactory:
    """Test self-challenge event factory."""

    def test_create_self_challenge_event(self) -> None:
        """Should create self-challenge with thesis and antithesis."""
        event = self_challenge_event(
            thesis="Composability is paramount",
            antithesis="But sometimes direct solutions are clearer",
        )

        assert event.event_type == SoulEventType.SELF_CHALLENGE
        assert event.payload["thesis"] == "Composability is paramount"
        assert event.payload["antithesis"] == "But sometimes direct solutions are clearer"
        assert "synthesis" not in event.payload

    def test_self_challenge_with_synthesis(self) -> None:
        """Should create self-challenge with synthesis."""
        event = self_challenge_event(
            thesis="Category theory is too abstract",
            antithesis="But it provides universal patterns",
            synthesis="Use categorical thinking for architecture, not implementation details",
            eigenvector="categorical",
        )

        assert (
            event.payload["synthesis"]
            == "Use categorical thinking for architecture, not implementation details"
        )
        assert event.payload["eigenvector"] == "categorical"


class TestPerturbationEventFactory:
    """Test perturbation event factory."""

    def test_create_perturbation_event(self) -> None:
        """Should create perturbation event."""
        event = perturbation_event(source="purgatory")

        assert event.event_type == SoulEventType.PERTURBATION
        assert event.payload["source"] == "purgatory"
        assert event.payload["intensity"] == 0.5
        assert event.payload["data"] == {}

    def test_perturbation_event_with_data(self) -> None:
        """Should create perturbation event with data."""
        data = {"token_id": "sem-123", "severity": "high"}
        event = perturbation_event(
            source="semaphore",
            intensity=0.8,
            data=data,
        )

        assert event.payload["intensity"] == 0.8
        assert event.payload["data"] == data


class TestGratitudeEventFactory:
    """Test gratitude event factory."""

    def test_create_gratitude_event(self) -> None:
        """Should create gratitude event."""
        event = gratitude_event(for_what="the categorical foundations")

        assert event.event_type == SoulEventType.GRATITUDE
        assert event.payload["for_what"] == "the categorical foundations"
        assert event.payload["depth"] == 1

    def test_gratitude_event_with_recipient(self) -> None:
        """Should create gratitude event with recipient."""
        event = gratitude_event(
            for_what="the elegant functor laws",
            to_whom="the category theorists",
            depth=3,
        )

        assert event.payload["to_whom"] == "the category theorists"
        assert event.payload["depth"] == 3


class TestAmbientEventPredicates:
    """Test ambient event predicates."""

    def test_is_ambient_event_positive(self) -> None:
        """Should identify ambient events."""
        assert is_ambient_event(thought_event(content="test"))
        assert is_ambient_event(feeling_event(valence="curious"))
        assert is_ambient_event(observation_event(pattern="test"))
        assert is_ambient_event(self_challenge_event(thesis="a", antithesis="b"))
        assert is_ambient_event(gratitude_event(for_what="test"))

    def test_is_ambient_event_negative(self) -> None:
        """Should reject non-ambient events."""
        assert not is_ambient_event(dialogue_turn_event(message="test"))
        assert not is_ambient_event(intercept_request_event("t", "p"))
        assert not is_ambient_event(pulse_event())
        assert not is_ambient_event(ping_event())
        assert not is_ambient_event(perturbation_event(source="external"))

    def test_is_external_event_positive(self) -> None:
        """Should identify external events."""
        assert is_external_event(dialogue_turn_event(message="test"))
        assert is_external_event(intercept_request_event("t", "p"))
        assert is_external_event(mode_change_event("a", "b"))
        assert is_external_event(perturbation_event(source="test"))
        assert is_external_event(ping_event())

    def test_is_external_event_negative(self) -> None:
        """Should reject non-external events."""
        assert not is_external_event(thought_event(content="test"))
        assert not is_external_event(feeling_event(valence="test"))
        assert not is_external_event(pulse_event())
        assert not is_external_event(gratitude_event(for_what="test"))


class TestEventHardening:
    """Test hardening: validation and edge cases."""

    def test_feeling_event_clamps_intensity_high(self) -> None:
        """Should clamp intensity > 1.0 to 1.0."""
        event = feeling_event(valence="excited", intensity=1.5)
        assert event.payload["intensity"] == 1.0

    def test_feeling_event_clamps_intensity_low(self) -> None:
        """Should clamp intensity < 0.0 to 0.0."""
        event = feeling_event(valence="calm", intensity=-0.5)
        assert event.payload["intensity"] == 0.0

    def test_thought_event_clamps_depth_high(self) -> None:
        """Should clamp depth > 3 to 3."""
        event = thought_event(content="deep", depth=10)
        assert event.payload["depth"] == 3

    def test_thought_event_clamps_depth_low(self) -> None:
        """Should clamp depth < 1 to 1."""
        event = thought_event(content="shallow", depth=0)
        assert event.payload["depth"] == 1

    def test_gratitude_event_clamps_depth(self) -> None:
        """Should clamp gratitude depth."""
        event = gratitude_event(for_what="the tests", depth=100)
        assert event.payload["depth"] == 3

        event2 = gratitude_event(for_what="the tests", depth=-1)
        assert event2.payload["depth"] == 1

    def test_observation_event_clamps_confidence(self) -> None:
        """Should clamp confidence to [0, 1]."""
        event = observation_event(pattern="test", confidence=1.5)
        assert event.payload["confidence"] == 1.0

        event2 = observation_event(pattern="test", confidence=-0.5)
        assert event2.payload["confidence"] == 0.0

    def test_perturbation_event_clamps_intensity(self) -> None:
        """Should clamp perturbation intensity."""
        event = perturbation_event(source="test", intensity=2.0)
        assert event.payload["intensity"] == 1.0

    def test_from_dict_requires_type(self) -> None:
        """Should raise KeyError for missing type."""
        from agents.k.events import SoulEvent

        with pytest.raises(KeyError) as excinfo:
            SoulEvent.from_dict({"timestamp": "2025-01-01T00:00:00+00:00"})
        assert "type" in str(excinfo.value)

    def test_from_dict_requires_timestamp(self) -> None:
        """Should raise KeyError for missing timestamp."""
        from agents.k.events import SoulEvent

        with pytest.raises(KeyError) as excinfo:
            SoulEvent.from_dict({"type": "thought"})
        assert "timestamp" in str(excinfo.value)

    def test_from_dict_validates_type(self) -> None:
        """Should raise ValueError for invalid type."""
        from agents.k.events import SoulEvent

        with pytest.raises(ValueError) as excinfo:
            SoulEvent.from_dict(
                {
                    "type": "invalid_event_type",
                    "timestamp": "2025-01-01T00:00:00+00:00",
                }
            )
        assert "Invalid event type" in str(excinfo.value)

    def test_from_dict_validates_timestamp(self) -> None:
        """Should raise ValueError for invalid timestamp."""
        from agents.k.events import SoulEvent

        with pytest.raises(ValueError) as excinfo:
            SoulEvent.from_dict(
                {
                    "type": "thought",
                    "timestamp": "not-a-date",
                }
            )
        assert "Invalid timestamp" in str(excinfo.value)
