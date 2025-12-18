"""Tests for SemaphoreToken."""

import pickle
from datetime import datetime, timedelta

import pytest

from agents.flux.semaphore import SemaphoreReason, SemaphoreToken


class TestSemaphoreTokenCreation:
    """Test SemaphoreToken creation and defaults."""

    def test_default_id_generation(self) -> None:
        """Creation with defaults generates valid ID."""
        token = SemaphoreToken[str]()
        assert token.id.startswith("sem-")
        assert len(token.id) == 12  # "sem-" + 8 hex chars

    def test_unique_ids(self) -> None:
        """Each token gets a unique ID."""
        tokens = [SemaphoreToken[str]() for _ in range(100)]
        ids = [t.id for t in tokens]
        assert len(set(ids)) == 100

    def test_default_reason(self) -> None:
        """Default reason is CONTEXT_REQUIRED."""
        token = SemaphoreToken[str]()
        assert token.reason == SemaphoreReason.CONTEXT_REQUIRED

    def test_default_severity(self) -> None:
        """Default severity is 'info'."""
        token = SemaphoreToken[str]()
        assert token.severity == "info"

    def test_default_timestamps(self) -> None:
        """created_at is set, resolved_at and cancelled_at are None."""
        token = SemaphoreToken[str]()
        assert token.created_at is not None
        assert token.resolved_at is None
        assert token.cancelled_at is None

    def test_default_options_empty_list(self) -> None:
        """Default options is empty list."""
        token = SemaphoreToken[str]()
        assert token.options == []

    def test_default_frozen_state_empty_bytes(self) -> None:
        """Default frozen_state is empty bytes."""
        token = SemaphoreToken[str]()
        assert token.frozen_state == b""


class TestSemaphoreTokenState:
    """Test SemaphoreToken state properties."""

    def test_is_pending_initially_true(self) -> None:
        """is_pending is True for new token."""
        token = SemaphoreToken[str]()
        assert token.is_pending is True

    def test_is_pending_false_after_resolve(self) -> None:
        """is_pending is False after resolved_at is set."""
        token = SemaphoreToken[str]()
        token.resolved_at = datetime.now()
        assert token.is_pending is False

    def test_is_pending_false_after_cancel(self) -> None:
        """is_pending is False after cancelled_at is set."""
        token = SemaphoreToken[str]()
        token.cancelled_at = datetime.now()
        assert token.is_pending is False

    def test_is_resolved_initially_false(self) -> None:
        """is_resolved is False for new token."""
        token = SemaphoreToken[str]()
        assert token.is_resolved is False

    def test_is_resolved_true_after_resolve(self) -> None:
        """is_resolved is True after resolved_at is set."""
        token = SemaphoreToken[str]()
        token.resolved_at = datetime.now()
        assert token.is_resolved is True

    def test_is_cancelled_initially_false(self) -> None:
        """is_cancelled is False for new token."""
        token = SemaphoreToken[str]()
        assert token.is_cancelled is False

    def test_is_cancelled_true_after_cancel(self) -> None:
        """is_cancelled is True after cancelled_at is set."""
        token = SemaphoreToken[str]()
        token.cancelled_at = datetime.now()
        assert token.is_cancelled is True

    def test_resolved_and_cancelled_mutually_exclusive(self) -> None:
        """A token shouldn't be both resolved and cancelled (logical constraint)."""
        # Test resolved
        resolved_token = SemaphoreToken[str]()
        resolved_token.resolved_at = datetime.now()
        assert resolved_token.is_resolved is True
        assert resolved_token.is_cancelled is False
        assert resolved_token.is_pending is False

        # Test cancelled
        cancelled_token = SemaphoreToken[str]()
        cancelled_token.cancelled_at = datetime.now()
        assert cancelled_token.is_cancelled is True
        assert cancelled_token.is_resolved is False
        assert cancelled_token.is_pending is False


class TestSemaphoreTokenSeverity:
    """Test severity field."""

    def test_severity_info(self) -> None:
        """Can set severity to 'info'."""
        token = SemaphoreToken[str](severity="info")
        assert token.severity == "info"

    def test_severity_warning(self) -> None:
        """Can set severity to 'warning'."""
        token = SemaphoreToken[str](severity="warning")
        assert token.severity == "warning"

    def test_severity_critical(self) -> None:
        """Can set severity to 'critical'."""
        token = SemaphoreToken[str](severity="critical")
        assert token.severity == "critical"


class TestSemaphoreTokenOptions:
    """Test options field."""

    def test_options_preserved(self) -> None:
        """Options list is preserved."""
        options = ["Approve", "Reject", "Review"]
        token = SemaphoreToken[str](options=options)
        assert token.options == options

    def test_options_mutable(self) -> None:
        """Options list can be modified after creation."""
        token = SemaphoreToken[str](options=["Approve"])
        token.options.append("Reject")
        assert token.options == ["Approve", "Reject"]


class TestSemaphoreTokenPrompt:
    """Test prompt field."""

    def test_prompt_preserved(self) -> None:
        """Prompt string is preserved."""
        prompt = "Delete 47 records?"
        token = SemaphoreToken[str](prompt=prompt)
        assert token.prompt == prompt

    def test_prompt_empty_default(self) -> None:
        """Default prompt is empty string."""
        token = SemaphoreToken[str]()
        assert token.prompt == ""


class TestSemaphoreTokenFrozenState:
    """Test frozen_state field."""

    def test_frozen_state_can_hold_pickled_data(self) -> None:
        """frozen_state can hold pickled data."""
        state = {"partial_result": "halfway there", "step": 3, "data": [1, 2, 3]}
        frozen = pickle.dumps(state)

        token = SemaphoreToken[str](frozen_state=frozen)
        assert token.frozen_state == frozen

        # Can restore
        restored = pickle.loads(token.frozen_state)
        assert restored == state

    def test_frozen_state_preserves_nested_objects(self) -> None:
        """frozen_state can preserve nested dict/list structures."""
        # Use nested dicts/lists instead of custom classes
        # (custom local classes can't be pickled)
        state = {
            "value": 42,
            "nested": {"inner": [1, 2, 3]},
            "tuple": (1, "a", 3.14),
        }
        frozen = pickle.dumps(state)

        token = SemaphoreToken[str](frozen_state=frozen)
        restored = pickle.loads(token.frozen_state)
        assert restored["value"] == 42
        assert restored["nested"]["inner"] == [1, 2, 3]
        assert restored["tuple"] == (1, "a", 3.14)


class TestSemaphoreTokenTiming:
    """Test deadline and escalation fields."""

    def test_deadline_none_by_default(self) -> None:
        """Deadline is None by default (Rodizio is indefinite)."""
        token = SemaphoreToken[str]()
        assert token.deadline is None

    def test_deadline_can_be_set(self) -> None:
        """Deadline can be set."""
        deadline = datetime.now() + timedelta(hours=1)
        token = SemaphoreToken[str](deadline=deadline)
        assert token.deadline == deadline

    def test_escalation_none_by_default(self) -> None:
        """Escalation is None by default."""
        token = SemaphoreToken[str]()
        assert token.escalation is None

    def test_escalation_can_be_set(self) -> None:
        """Escalation can be set."""
        token = SemaphoreToken[str](escalation="team-lead")
        assert token.escalation == "team-lead"


class TestSemaphoreTokenHashing:
    """Test hashing and equality."""

    def test_hash_based_on_id(self) -> None:
        """Hash is based on id."""
        token1 = SemaphoreToken[str](id="sem-test1234")
        token2 = SemaphoreToken[str](id="sem-test1234")
        assert hash(token1) == hash(token2)

    def test_different_ids_different_hashes(self) -> None:
        """Different ids produce different hashes."""
        token1 = SemaphoreToken[str]()
        token2 = SemaphoreToken[str]()
        # Very unlikely to collide, but technically possible
        # We test that the hash is computed from id
        assert hash(token1) == hash(token1.id)
        assert hash(token2) == hash(token2.id)

    def test_equality_based_on_id(self) -> None:
        """Equality is based on id."""
        token1 = SemaphoreToken[str](id="sem-test1234", prompt="A")
        token2 = SemaphoreToken[str](id="sem-test1234", prompt="B")
        assert token1 == token2

    def test_inequality_for_different_ids(self) -> None:
        """Different ids are not equal."""
        token1 = SemaphoreToken[str](id="sem-aaaaaaaa")
        token2 = SemaphoreToken[str](id="sem-bbbbbbbb")
        assert token1 != token2

    def test_can_use_in_set(self) -> None:
        """Tokens can be used in sets."""
        token1 = SemaphoreToken[str](id="sem-test1234")
        token2 = SemaphoreToken[str](id="sem-test1234")
        token3 = SemaphoreToken[str](id="sem-other567")

        token_set = {token1, token2, token3}
        assert len(token_set) == 2  # token1 and token2 are equal

    def test_can_use_as_dict_key(self) -> None:
        """Tokens can be used as dict keys."""
        token = SemaphoreToken[str](id="sem-test1234")
        d = {token: "value"}
        assert d[token] == "value"


class TestSemaphoreTokenReason:
    """Test all reason types."""

    @pytest.mark.parametrize(
        "reason",
        [
            SemaphoreReason.APPROVAL_NEEDED,
            SemaphoreReason.CONTEXT_REQUIRED,
            SemaphoreReason.SENSITIVE_ACTION,
            SemaphoreReason.AMBIGUOUS_CHOICE,
            SemaphoreReason.RESOURCE_DECISION,
            SemaphoreReason.ERROR_RECOVERY,
        ],
    )
    def test_all_reasons_work(self, reason: SemaphoreReason) -> None:
        """All SemaphoreReason values can be used."""
        token = SemaphoreToken[str](reason=reason)
        assert token.reason == reason


# === Phase 2 Tests: JSON Serialization ===


class TestSemaphoreTokenJsonSerialization:
    """Test to_json and from_json methods."""

    def test_to_json_basic(self) -> None:
        """to_json produces JSON-serializable dict."""
        import json

        token = SemaphoreToken[str](
            id="sem-test1234",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Delete records?",
            options=["Yes", "No"],
            severity="warning",
        )

        data = token.to_json()

        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

        # Check fields
        assert data["id"] == "sem-test1234"
        assert data["reason"] == "approval_needed"
        assert data["prompt"] == "Delete records?"
        assert data["options"] == ["Yes", "No"]
        assert data["severity"] == "warning"

    def test_to_json_frozen_state_base64(self) -> None:
        """frozen_state is base64-encoded."""
        import base64

        state = b"some binary data"
        token = SemaphoreToken[str](frozen_state=state)

        data = token.to_json()

        # Should be base64 string
        assert isinstance(data["frozen_state"], str)
        decoded = base64.b64decode(data["frozen_state"])
        assert decoded == state

    def test_to_json_datetimes_iso_format(self) -> None:
        """Datetime fields are ISO-formatted strings."""
        token = SemaphoreToken[str]()
        token.resolved_at = datetime.now()

        data = token.to_json()

        assert isinstance(data["created_at"], str)
        assert isinstance(data["resolved_at"], str)
        # Should be parseable
        datetime.fromisoformat(data["created_at"])
        datetime.fromisoformat(data["resolved_at"])

    def test_from_json_restores_token(self) -> None:
        """from_json restores token from dict."""
        import base64

        state = b"test state"
        data = {
            "id": "sem-restored",
            "reason": "approval_needed",
            "frozen_state": base64.b64encode(state).decode("utf-8"),
            "original_event": "test_event",
            "required_type": None,
            "deadline": None,
            "escalation": "team-lead",
            "prompt": "Restore test?",
            "options": ["A", "B"],
            "severity": "critical",
            "created_at": "2025-01-01T12:00:00",
            "resolved_at": None,
            "cancelled_at": None,
            "voided_at": None,
        }

        token = SemaphoreToken.from_json(data)

        assert token.id == "sem-restored"
        assert token.reason == SemaphoreReason.APPROVAL_NEEDED
        assert token.frozen_state == state
        assert token.original_event == "test_event"
        assert token.escalation == "team-lead"
        assert token.prompt == "Restore test?"
        assert token.options == ["A", "B"]
        assert token.severity == "critical"
        assert token.is_pending is True

    def test_roundtrip_json(self) -> None:
        """to_json then from_json preserves token."""
        import pickle

        state = {"partial": "result", "step": 5}
        original = SemaphoreToken[str](
            reason=SemaphoreReason.CONTEXT_REQUIRED,
            frozen_state=pickle.dumps(state),
            original_event="original",
            prompt="Question?",
            options=["One", "Two"],
            severity="info",
            deadline=datetime.now() + timedelta(hours=1),
            escalation="admin",
        )

        data = original.to_json()
        restored = SemaphoreToken.from_json(data)

        assert restored.id == original.id
        assert restored.reason == original.reason
        assert restored.frozen_state == original.frozen_state
        assert restored.prompt == original.prompt
        assert restored.options == original.options
        assert restored.severity == original.severity
        assert restored.escalation == original.escalation

    def test_from_json_with_terminal_states(self) -> None:
        """from_json handles resolved/cancelled/voided states."""
        import base64

        data: dict[str, object] = {
            "id": "sem-resolved",
            "reason": "approval_needed",
            "frozen_state": base64.b64encode(b"").decode("utf-8"),
            "original_event": None,
            "required_type": None,
            "deadline": None,
            "escalation": None,
            "prompt": "",
            "options": [],
            "severity": "info",
            "created_at": "2025-01-01T12:00:00",
            "resolved_at": "2025-01-01T13:00:00",
            "cancelled_at": None,
            "voided_at": None,
        }

        token = SemaphoreToken.from_json(data)

        assert token.is_resolved is True
        assert token.is_pending is False


# === Phase 2 Tests: Deadline and Voiding ===


class TestSemaphoreTokenDeadline:
    """Test deadline checking and voiding."""

    def test_is_voided_initially_false(self) -> None:
        """is_voided is False for new token."""
        token = SemaphoreToken[str]()
        assert token.is_voided is False

    def test_is_voided_true_after_voiding(self) -> None:
        """is_voided is True after voided_at is set."""
        token = SemaphoreToken[str]()
        token.voided_at = datetime.now()
        assert token.is_voided is True

    def test_is_pending_false_when_voided(self) -> None:
        """is_pending is False when token is voided."""
        token = SemaphoreToken[str]()
        token.voided_at = datetime.now()
        assert token.is_pending is False

    def test_check_deadline_no_deadline(self) -> None:
        """check_deadline returns False when no deadline."""
        token = SemaphoreToken[str](deadline=None)
        assert token.check_deadline() is False
        assert token.is_voided is False

    def test_check_deadline_future(self) -> None:
        """check_deadline returns False when deadline is in future."""
        token = SemaphoreToken[str](deadline=datetime.now() + timedelta(hours=1))
        assert token.check_deadline() is False
        assert token.is_voided is False

    def test_check_deadline_passed(self) -> None:
        """check_deadline voids token when deadline has passed."""
        token = SemaphoreToken[str](deadline=datetime.now() - timedelta(seconds=1))
        assert token.check_deadline() is True
        assert token.is_voided is True
        assert token.voided_at is not None

    def test_check_deadline_already_resolved(self) -> None:
        """check_deadline doesn't void already-resolved token."""
        token = SemaphoreToken[str](deadline=datetime.now() - timedelta(seconds=1))
        token.resolved_at = datetime.now()

        result = token.check_deadline()

        # Returns current voided state (False) but doesn't change anything
        assert result is False
        assert token.is_voided is False

    def test_check_deadline_already_cancelled(self) -> None:
        """check_deadline doesn't void already-cancelled token."""
        token = SemaphoreToken[str](deadline=datetime.now() - timedelta(seconds=1))
        token.cancelled_at = datetime.now()

        result = token.check_deadline()

        assert result is False
        assert token.is_voided is False

    def test_voided_resolved_cancelled_mutually_exclusive(self) -> None:
        """Only one terminal state should be set (logical constraint)."""
        # A well-behaved system won't set multiple terminal states
        # But we can verify the state properties work correctly

        # Voided token
        voided = SemaphoreToken[str]()
        voided.voided_at = datetime.now()
        assert voided.is_voided is True
        assert voided.is_resolved is False
        assert voided.is_cancelled is False
        assert voided.is_pending is False

    def test_json_roundtrip_voided_token(self) -> None:
        """JSON roundtrip preserves voided state."""
        token = SemaphoreToken[str](deadline=datetime.now() - timedelta(hours=1))
        token.check_deadline()  # Void it
        assert token.is_voided is True

        data = token.to_json()
        restored = SemaphoreToken.from_json(data)

        assert restored.is_voided is True
        assert restored.voided_at is not None
