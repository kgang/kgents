"""
Tests for Synergy CLI Output.

Wave 2: UI Integration - Make synergy notifications visible in CLI.
"""

from __future__ import annotations

import io

import pytest
from protocols.synergy.cli_output import (
    ARROW,
    CRYSTAL_ICON,
    LINK_ICON,
    SynergyNotificationContext,
    create_notification_context,
    display_synergy_notification,
    display_synergy_results,
    format_crystal_reference,
    format_synergy_arrow,
    format_synergy_header,
)
from protocols.synergy.events import SynergyResult


class TestDisplaySynergyNotification:
    """Tests for display_synergy_notification function."""

    def test_successful_with_artifact(self) -> None:
        """Display successful result with artifact ID."""
        result = SynergyResult(
            success=True,
            handler_name="GestaltToBrainHandler",
            message="Architecture snapshot captured to Brain",
            artifact_id="gestalt-impl-claude-2025-12-16",
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream)

        output = stream.getvalue()
        assert displayed is True
        assert "Synergy:" in output
        assert "Architecture snapshot captured to Brain" in output
        assert "gestalt-impl-claude-2025-12-16" in output
        assert "Crystal:" in output

    def test_successful_without_artifact(self) -> None:
        """Display successful result without artifact."""
        result = SynergyResult(
            success=True,
            handler_name="BrainToCoalitionHandler",
            message="Context enrichment complete",
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream)

        output = stream.getvalue()
        assert displayed is True
        assert "Context enrichment complete" in output
        assert "Crystal:" not in output

    def test_skipped_not_shown_by_default(self) -> None:
        """Skipped handlers are not shown by default."""
        result = SynergyResult(
            success=True,
            handler_name="SomeHandler",
            message="Handler skipped",
            metadata={"skipped": True},
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream)

        assert displayed is False
        assert stream.getvalue() == ""

    def test_skipped_shown_when_requested(self) -> None:
        """Skipped handlers shown when show_skipped=True."""
        result = SynergyResult(
            success=True,
            handler_name="SomeHandler",
            message="Handler skipped",
            metadata={"skipped": True},
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream, show_skipped=True)

        assert displayed is True
        assert "(skipped)" in stream.getvalue()

    def test_failure_not_shown_by_default(self) -> None:
        """Failed handlers are not shown by default."""
        result = SynergyResult(
            success=False,
            handler_name="FailingHandler",
            message="Brain capture failed: connection error",
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream)

        assert displayed is False
        assert stream.getvalue() == ""

    def test_failure_shown_when_requested(self) -> None:
        """Failed handlers shown when show_failures=True."""
        result = SynergyResult(
            success=False,
            handler_name="FailingHandler",
            message="Brain capture failed",
        )

        stream = io.StringIO()
        displayed = display_synergy_notification(result, stream, show_failures=True)

        assert displayed is True
        assert "Synergy failed" in stream.getvalue()

    def test_custom_indent(self) -> None:
        """Notifications respect custom indentation."""
        result = SynergyResult(
            success=True,
            handler_name="TestHandler",
            message="Test message",
            artifact_id="test-123",
        )

        stream = io.StringIO()
        display_synergy_notification(result, stream, indent=4)

        output = stream.getvalue()
        assert output.startswith("    ")  # 4-space indent


class TestDisplaySynergyResults:
    """Tests for display_synergy_results function."""

    def test_multiple_results(self) -> None:
        """Display multiple results."""
        results = [
            SynergyResult(
                success=True,
                handler_name="Handler1",
                message="Result 1",
                artifact_id="crystal-1",
            ),
            SynergyResult(
                success=True,
                handler_name="Handler2",
                message="Result 2",
                artifact_id="crystal-2",
            ),
        ]

        stream = io.StringIO()
        count = display_synergy_results(results, stream)

        assert count == 2
        output = stream.getvalue()
        assert "crystal-1" in output
        assert "crystal-2" in output

    def test_mixed_results(self) -> None:
        """Display mixed results with filtering."""
        results = [
            SynergyResult(
                success=True,
                handler_name="Handler1",
                message="Visible",
                artifact_id="visible-1",
            ),
            SynergyResult(
                success=True,
                handler_name="Handler2",
                message="Skipped",
                metadata={"skipped": True},
            ),
            SynergyResult(
                success=False,
                handler_name="Handler3",
                message="Failed",
            ),
        ]

        stream = io.StringIO()
        count = display_synergy_results(results, stream)

        assert count == 1  # Only first result shown
        output = stream.getvalue()
        assert "visible-1" in output
        assert "Skipped" not in output
        assert "Failed" not in output

    def test_empty_results(self) -> None:
        """Handle empty results list."""
        stream = io.StringIO()
        count = display_synergy_results([], stream)

        assert count == 0
        assert stream.getvalue() == ""


class TestSynergyNotificationContext:
    """Tests for SynergyNotificationContext context manager."""

    def test_context_creation(self) -> None:
        """Context can be created with defaults."""
        ctx = create_notification_context()
        assert ctx.indent == 2
        assert ctx.show_skipped is False
        assert ctx.show_failures is False

    def test_context_custom_options(self) -> None:
        """Context respects custom options."""
        ctx = create_notification_context(
            indent=4,
            show_skipped=True,
            show_failures=True,
        )
        assert ctx.indent == 4
        assert ctx.show_skipped is True
        assert ctx.show_failures is True

    def test_results_collected(self) -> None:
        """Context collects results during lifecycle."""
        stream = io.StringIO()
        ctx = SynergyNotificationContext(stream=stream)

        # Before entering, results should be None
        assert ctx._results is None

        with ctx:
            # During context, results should be an empty list
            assert ctx._results == []

        # After exiting, results property should return list
        assert ctx.results == []


class TestFormatHelpers:
    """Tests for formatting helper functions."""

    def test_format_synergy_header(self) -> None:
        """format_synergy_header creates proper header."""
        header = format_synergy_header("Gestalt", "Brain")
        assert "Gestalt" in header
        assert "Brain" in header
        assert "→" in header or "->" in header or "Synergy" in header

    def test_format_crystal_reference(self) -> None:
        """format_crystal_reference formats crystal ID."""
        ref = format_crystal_reference("my-crystal-123")
        assert "my-crystal-123" in ref
        assert "Crystal:" in ref

    def test_format_synergy_arrow(self) -> None:
        """format_synergy_arrow adds arrow prefix."""
        formatted = format_synergy_arrow("Test message")
        assert ARROW in formatted or "↳" in formatted
        assert "Test message" in formatted


class TestConstants:
    """Tests for module constants."""

    def test_arrow_is_string(self) -> None:
        """ARROW constant is a string."""
        assert isinstance(ARROW, str)
        assert len(ARROW) > 0

    def test_icons_are_strings(self) -> None:
        """Icon constants are strings."""
        assert isinstance(LINK_ICON, str)
        assert isinstance(CRYSTAL_ICON, str)
