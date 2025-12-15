"""Tests for base screen classes with key passthrough behavior.

This module tests the critical key passthrough mechanism that allows global
navigation keys to bubble up from nested screens to the parent DashboardApp.
"""

from unittest.mock import Mock, patch

import pytest
from agents.i.screens.base import KgentsModalScreen, KgentsScreen
from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Label


class TestKgentsScreen:
    """Test KgentsScreen base class."""

    def test_passthrough_keys_contains_expected_keys(self):
        """Verify PASSTHROUGH_KEYS contains all required navigation keys."""
        expected_keys = {
            # Number keys for screen navigation
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            # Screen cycling
            "tab",
            # Special screen shortcuts
            "d",  # Debugger
            "m",  # Memory map
            # Global commands
            "question_mark",  # Help
            "q",  # Quit
        }

        assert KgentsScreen.PASSTHROUGH_KEYS == expected_keys

    def test_passthrough_keys_is_set(self):
        """Verify PASSTHROUGH_KEYS is a set for O(1) lookup."""
        assert isinstance(KgentsScreen.PASSTHROUGH_KEYS, set)

    def test_on_key_does_not_stop_propagation_for_passthrough_keys(self):
        """Test that passthrough keys are allowed to bubble up."""
        screen = KgentsScreen()

        # Test each passthrough key
        passthrough_keys = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "tab",
            "f",
            "d",
            "m",
            "question_mark",
            "q",
        ]

        for key_name in passthrough_keys:
            event = Key(key=key_name, character=None)

            # Track whether event.stop() or event.prevent_default() was called
            original_stop = event.stop
            original_prevent = event.prevent_default
            stop_called = False
            prevent_called = False

            def track_stop() -> None:
                nonlocal stop_called
                stop_called = True
                original_stop()

            def track_prevent() -> None:
                nonlocal prevent_called
                prevent_called = True
                original_prevent()

            # Use object.__setattr__ to bypass mypy method-assign check
            object.__setattr__(event, "stop", track_stop)
            object.__setattr__(event, "prevent_default", track_prevent)

            # Call on_key - it should NOT stop propagation
            screen.on_key(event)

            # Verify the event was allowed to bubble
            assert not stop_called, f"Key '{key_name}' should not call event.stop()"
            assert not prevent_called, (
                f"Key '{key_name}' should not call event.prevent_default()"
            )

    def test_on_key_allows_normal_handling_for_non_passthrough_keys(self):
        """Test that non-passthrough keys are not in PASSTHROUGH_KEYS set."""
        # Simply verify that common non-navigation keys are not in the passthrough set
        # This ensures they will follow different code paths
        non_passthrough_keys = [
            "a",
            "b",
            "c",
            "x",
            "y",
            "z",
            "enter",
            "space",
            "escape",
        ]

        for key in non_passthrough_keys:
            assert key not in KgentsScreen.PASSTHROUGH_KEYS, (
                f"Key '{key}' should not be in PASSTHROUGH_KEYS"
            )

        # Verify that passthrough keys ARE in the set (sanity check)
        assert "1" in KgentsScreen.PASSTHROUGH_KEYS
        assert "q" in KgentsScreen.PASSTHROUGH_KEYS

    def test_anchor_class_attributes(self):
        """Test that anchor-related class attributes exist and have correct types."""
        assert hasattr(KgentsScreen, "ANCHOR")
        assert isinstance(KgentsScreen.ANCHOR, str)
        assert KgentsScreen.ANCHOR == ""  # Default is empty

        assert hasattr(KgentsScreen, "ANCHOR_MORPHS_TO")
        assert isinstance(KgentsScreen.ANCHOR_MORPHS_TO, dict)
        assert KgentsScreen.ANCHOR_MORPHS_TO == {}  # Default is empty

    def test_get_anchor_for_transition(self):
        """Test get_anchor_for_transition method."""

        # Create a custom screen with anchor mappings
        class CustomScreen(KgentsScreen):
            ANCHOR_MORPHS_TO = {
                "flux": "stream_panel",
                "debugger": "trace_view",
            }

        screen = CustomScreen()

        # Test known transitions
        assert screen.get_anchor_for_transition("flux") == "stream_panel"
        assert screen.get_anchor_for_transition("debugger") == "trace_view"

        # Test unknown transition
        assert screen.get_anchor_for_transition("unknown") == ""

    def test_get_anchor_classmethod(self):
        """Test get_anchor class method."""
        # Default screen has no anchor
        assert KgentsScreen.get_anchor() == ""

        # Custom screen with anchor
        class CustomScreen(KgentsScreen):
            ANCHOR = "main_panel"

        assert CustomScreen.get_anchor() == "main_panel"


class TestKgentsModalScreen:
    """Test KgentsModalScreen base class."""

    def test_escape_binding_exists(self):
        """Test that escape key binding is defined."""

        # Create instance to check bindings
        class TestModal(KgentsModalScreen[str]):
            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()

        # Check BINDINGS class variable
        assert hasattr(TestModal, "BINDINGS")
        bindings = TestModal.BINDINGS

        # Find the escape binding - handle both tuple and Binding object formats
        # Use Any to avoid mypy union type issues with Binding
        from typing import Any

        escape_binding: Any = None
        for binding in bindings:
            # BINDINGS can be tuple[str, str] | tuple[str, str, str] | Binding
            if isinstance(binding, tuple):
                if binding[0] == "escape":
                    escape_binding = binding
                    break
            elif hasattr(binding, "key") and binding.key == "escape":
                escape_binding = binding
                break

        assert escape_binding is not None
        # Handle both tuple and Binding object formats
        if isinstance(escape_binding, tuple):
            assert escape_binding[0] == "escape"
            assert escape_binding[1] == "dismiss_modal"
        else:
            assert escape_binding.key == "escape"
            assert escape_binding.action == "dismiss_modal"

    def test_action_dismiss_modal(self):
        """Test action_dismiss_modal dismisses with None."""

        class TestModal(KgentsModalScreen[str]):
            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()

        # Mock the dismiss method using object.__setattr__ to bypass mypy method-assign
        mock_dismiss = Mock()
        object.__setattr__(modal, "dismiss", mock_dismiss)

        # Call the action
        modal.action_dismiss_modal()

        # Verify dismiss was called with None
        mock_dismiss.assert_called_once_with(None)

    def test_dismiss_after_immediate(self):
        """Test dismiss_after with zero delay."""

        class TestModal(KgentsModalScreen[int]):
            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()
        mock_dismiss = Mock()
        object.__setattr__(modal, "dismiss", mock_dismiss)

        # Dismiss with zero delay should be immediate
        modal.dismiss_after(42, delay=0.0)

        # Should call dismiss immediately
        mock_dismiss.assert_called_once_with(42)

    def test_dismiss_after_with_delay(self):
        """Test dismiss_after schedules delayed dismissal."""

        class TestModal(KgentsModalScreen[str]):
            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()
        mock_dismiss = Mock()
        mock_set_timer = Mock()
        object.__setattr__(modal, "dismiss", mock_dismiss)
        object.__setattr__(modal, "set_timer", mock_set_timer)

        # Dismiss with delay
        modal.dismiss_after("result", delay=0.5)

        # Should NOT call dismiss immediately
        mock_dismiss.assert_not_called()

        # Should schedule a timer
        mock_set_timer.assert_called_once()
        call_args = mock_set_timer.call_args
        assert call_args[0][0] == 0.5  # First arg is delay
        assert callable(call_args[0][1])  # Second arg is callback

        # Execute the callback
        callback = call_args[0][1]
        callback()

        # Now dismiss should be called
        mock_dismiss.assert_called_once_with("result")

    def test_dismiss_after_uses_auto_dismiss_delay(self):
        """Test dismiss_after uses AUTO_DISMISS_DELAY when delay is None."""

        class TestModal(KgentsModalScreen[bool]):
            AUTO_DISMISS_DELAY = 0.3

            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()
        mock_set_timer = Mock()
        object.__setattr__(modal, "set_timer", mock_set_timer)

        # Call without explicit delay
        modal.dismiss_after(True)

        # Should use AUTO_DISMISS_DELAY
        mock_set_timer.assert_called_once()
        assert mock_set_timer.call_args[0][0] == 0.3

    def test_dismiss_immediate(self):
        """Test dismiss_immediate bypasses delay."""

        class TestModal(KgentsModalScreen[str]):
            AUTO_DISMISS_DELAY = 1.0  # Long default delay

            def compose(self) -> ComposeResult:
                yield Label("Test")

        modal = TestModal()
        mock_dismiss = Mock()
        object.__setattr__(modal, "dismiss", mock_dismiss)

        # Dismiss immediately
        modal.dismiss_immediate("fast")

        # Should call dismiss right away
        mock_dismiss.assert_called_once_with("fast")

    def test_auto_dismiss_delay_default(self):
        """Test AUTO_DISMISS_DELAY defaults to 0.0."""

        class TestModal(KgentsModalScreen[None]):
            def compose(self) -> ComposeResult:
                yield Label("Test")

        assert TestModal.AUTO_DISMISS_DELAY == 0.0

    def test_modal_screen_typing(self):
        """Test that modal screens can be typed with different result types."""

        # String result type
        class StringModal(KgentsModalScreen[str]):
            def compose(self) -> ComposeResult:
                yield Label("String")

        # Bool result type
        class BoolModal(KgentsModalScreen[bool]):
            def compose(self) -> ComposeResult:
                yield Label("Bool")

        # None result type
        class VoidModal(KgentsModalScreen[None]):
            def compose(self) -> ComposeResult:
                yield Label("Void")

        # Just verify they can be instantiated with different types
        string_modal = StringModal()
        bool_modal = BoolModal()
        void_modal = VoidModal()

        assert string_modal is not None
        assert bool_modal is not None
        assert void_modal is not None
