"""Tests for ReentryContext."""

import pickle

import pytest

from agents.flux.semaphore import ReentryContext


class TestReentryContextCreation:
    """Test ReentryContext creation."""

    def test_creation_with_required_fields(self) -> None:
        """Can create with all required fields."""
        reentry = ReentryContext[str](
            token_id="sem-abc12345",
            frozen_state=b"pickled_state",
            human_input="Approve",
            original_event="delete_records",
        )
        assert reentry.token_id == "sem-abc12345"
        assert reentry.frozen_state == b"pickled_state"
        assert reentry.human_input == "Approve"
        assert reentry.original_event == "delete_records"

    def test_requires_token_id(self) -> None:
        """Raises ValueError if token_id is empty."""
        with pytest.raises(ValueError, match="requires token_id"):
            ReentryContext[str](
                token_id="",
                frozen_state=b"state",
                human_input="input",
                original_event=None,
            )


class TestReentryContextFrozenState:
    """Test frozen_state field."""

    def test_preserves_frozen_state_bytes(self) -> None:
        """frozen_state bytes are preserved exactly."""
        frozen = b"\x80\x04\x95\x1a\x00\x00\x00\x00\x00\x00\x00}"
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=frozen,
            human_input="input",
            original_event=None,
        )
        assert reentry.frozen_state == frozen

    def test_can_unpickle_frozen_state(self) -> None:
        """Can unpickle frozen_state to restore agent state."""
        state = {"partial_result": "halfway", "step": 3}
        frozen = pickle.dumps(state)

        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=frozen,
            human_input="input",
            original_event=None,
        )

        restored = pickle.loads(reentry.frozen_state)
        assert restored == state


class TestReentryContextHumanInput:
    """Test human_input field."""

    def test_preserves_string_input(self) -> None:
        """String human_input is preserved."""
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=b"",
            human_input="Approve",
            original_event=None,
        )
        assert reentry.human_input == "Approve"

    def test_preserves_dict_input(self) -> None:
        """Dict human_input is preserved."""
        input_dict = {"action": "approve", "comment": "Looks good"}
        reentry = ReentryContext[dict[str, str]](
            token_id="sem-test",
            frozen_state=b"",
            human_input=input_dict,
            original_event=None,
        )
        assert reentry.human_input == input_dict

    def test_preserves_int_input(self) -> None:
        """Int human_input is preserved."""
        reentry = ReentryContext[int](
            token_id="sem-test",
            frozen_state=b"",
            human_input=42,
            original_event=None,
        )
        assert reentry.human_input == 42

    def test_preserves_none_input(self) -> None:
        """None human_input is preserved."""
        reentry = ReentryContext[None](
            token_id="sem-test",
            frozen_state=b"",
            human_input=None,
            original_event=None,
        )
        assert reentry.human_input is None

    def test_preserves_list_input(self) -> None:
        """List human_input is preserved."""
        input_list = ["option1", "option2"]
        reentry = ReentryContext[list[str]](
            token_id="sem-test",
            frozen_state=b"",
            human_input=input_list,
            original_event=None,
        )
        assert reentry.human_input == input_list


class TestReentryContextOriginalEvent:
    """Test original_event field."""

    def test_preserves_string_event(self) -> None:
        """String original_event is preserved."""
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=b"",
            human_input="input",
            original_event="delete_records",
        )
        assert reentry.original_event == "delete_records"

    def test_preserves_dict_event(self) -> None:
        """Dict original_event is preserved."""
        event = {"type": "delete", "count": 47}
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=b"",
            human_input="input",
            original_event=event,
        )
        assert reentry.original_event == event

    def test_preserves_none_event(self) -> None:
        """None original_event is preserved."""
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=b"",
            human_input="input",
            original_event=None,
        )
        assert reentry.original_event is None

    def test_preserves_complex_event(self) -> None:
        """Complex object original_event is preserved."""

        class Event:
            def __init__(self, name: str, data: list[int]) -> None:
                self.name = name
                self.data = data

        event = Event("test", [1, 2, 3])
        reentry = ReentryContext[str](
            token_id="sem-test",
            frozen_state=b"",
            human_input="input",
            original_event=event,
        )
        assert reentry.original_event.name == "test"
        assert reentry.original_event.data == [1, 2, 3]


class TestReentryContextGenericType:
    """Test generic type parameter."""

    def test_typed_human_input(self) -> None:
        """Type parameter documents expected human_input type."""
        # String type
        str_reentry: ReentryContext[str] = ReentryContext(
            token_id="sem-test",
            frozen_state=b"",
            human_input="approve",
            original_event=None,
        )
        assert isinstance(str_reentry.human_input, str)

        # Int type
        int_reentry: ReentryContext[int] = ReentryContext(
            token_id="sem-test",
            frozen_state=b"",
            human_input=42,
            original_event=None,
        )
        assert isinstance(int_reentry.human_input, int)
