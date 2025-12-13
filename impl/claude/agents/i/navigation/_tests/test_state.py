"""Tests for StateManager."""

import pytest

from ..state import StateManager


class TestStateManager:
    """Test suite for StateManager."""

    def test_save_and_get_focus(self) -> None:
        """Test saving and retrieving focus."""
        state = StateManager()

        # Save focus for observatory
        state.save_focus("observatory", "garden-123")

        # Retrieve it
        focus = state.get_focus("observatory")
        assert focus == "garden-123"

    def test_get_focus_none_when_not_set(self) -> None:
        """Test that get_focus returns None when not set."""
        state = StateManager()
        focus = state.get_focus("observatory")
        assert focus is None

    def test_clear_focus(self) -> None:
        """Test clearing focus."""
        state = StateManager()
        state.save_focus("observatory", "garden-123")

        # Clear it
        state.clear_focus("observatory")

        # Should return None now
        focus = state.get_focus("observatory")
        assert focus is None

    def test_save_and_get_selection(self) -> None:
        """Test saving and retrieving selection."""
        state = StateManager()

        # Save selection
        state.save_selection("observatory", ["garden-1", "garden-2"])

        # Retrieve it
        selection = state.get_selection("observatory")
        assert selection == ["garden-1", "garden-2"]

    def test_get_selection_empty_when_not_set(self) -> None:
        """Test that get_selection returns empty list when not set."""
        state = StateManager()
        selection = state.get_selection("observatory")
        assert selection == []

    def test_clear_selection(self) -> None:
        """Test clearing selection."""
        state = StateManager()
        state.save_selection("observatory", ["garden-1", "garden-2"])

        # Clear it
        state.clear_selection("observatory")

        # Should return empty list now
        selection = state.get_selection("observatory")
        assert selection == []

    def test_push_and_pop_history(self) -> None:
        """Test navigation history stack."""
        state = StateManager()

        # Push some navigation
        state.push_history("observatory", "garden-123")
        state.push_history("cockpit", "agent-456")

        # Pop them back
        entry = state.pop_history()
        assert entry == ("cockpit", "agent-456")

        entry = state.pop_history()
        assert entry == ("observatory", "garden-123")

    def test_pop_history_none_when_empty(self) -> None:
        """Test that pop_history returns None when empty."""
        state = StateManager()
        entry = state.pop_history()
        assert entry is None

    def test_get_history(self) -> None:
        """Test getting full history."""
        state = StateManager()

        # Push some navigation
        state.push_history("observatory", "garden-123")
        state.push_history("cockpit", "agent-456")

        # Get full history
        history = state.get_history()
        assert history == [
            ("observatory", "garden-123"),
            ("cockpit", "agent-456"),
        ]

    def test_clear_history(self) -> None:
        """Test clearing history."""
        state = StateManager()

        # Push some navigation
        state.push_history("observatory", "garden-123")
        state.push_history("cockpit", "agent-456")

        # Clear it
        state.clear_history()

        # Should be empty now
        history = state.get_history()
        assert history == []

    def test_reset(self) -> None:
        """Test resetting all state."""
        state = StateManager()

        # Set up various state
        state.save_focus("observatory", "garden-123")
        state.save_selection("observatory", ["garden-1", "garden-2"])
        state.push_history("observatory", "garden-123")

        # Reset
        state.reset()

        # Everything should be cleared
        assert state.get_focus("observatory") is None
        assert state.get_selection("observatory") == []
        assert state.get_history() == []

    def test_selection_returns_copy(self) -> None:
        """Test that get_selection returns a copy, not a reference."""
        state = StateManager()
        state.save_selection("observatory", ["garden-1", "garden-2"])

        # Get selection and modify it
        selection = state.get_selection("observatory")
        selection.append("garden-3")

        # Original should be unchanged
        original = state.get_selection("observatory")
        assert original == ["garden-1", "garden-2"]

    def test_history_returns_copy(self) -> None:
        """Test that get_history returns a copy, not a reference."""
        state = StateManager()
        state.push_history("observatory", "garden-123")

        # Get history and modify it
        history = state.get_history()
        history.append(("cockpit", "agent-456"))

        # Original should be unchanged
        original = state.get_history()
        assert original == [("observatory", "garden-123")]

    def test_multiple_screens(self) -> None:
        """Test managing state for multiple screens independently."""
        state = StateManager()

        # Save different focus for different screens
        state.save_focus("observatory", "garden-123")
        state.save_focus("cockpit", "agent-456")
        state.save_focus("debugger", "turn-789")

        # Retrieve them
        assert state.get_focus("observatory") == "garden-123"
        assert state.get_focus("cockpit") == "agent-456"
        assert state.get_focus("debugger") == "turn-789"

    def test_overwrite_focus(self) -> None:
        """Test that saving focus again overwrites previous value."""
        state = StateManager()

        # Save initial focus
        state.save_focus("observatory", "garden-123")

        # Overwrite with new focus
        state.save_focus("observatory", "garden-456")

        # Should have new value
        focus = state.get_focus("observatory")
        assert focus == "garden-456"

    def test_overwrite_selection(self) -> None:
        """Test that saving selection again overwrites previous value."""
        state = StateManager()

        # Save initial selection
        state.save_selection("observatory", ["garden-1", "garden-2"])

        # Overwrite with new selection
        state.save_selection("observatory", ["garden-3", "garden-4"])

        # Should have new value
        selection = state.get_selection("observatory")
        assert selection == ["garden-3", "garden-4"]
