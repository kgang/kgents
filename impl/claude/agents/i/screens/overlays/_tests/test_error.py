"""
Tests for ErrorOverlay.

Validates:
- Friendly error messaging
- Recovery hints
- Exception conversion
"""

from __future__ import annotations

import pytest

from ..error import ErrorOverlay, friendly_error_message


class TestErrorOverlay:
    """Test suite for ErrorOverlay."""

    def test_overlay_creation(self) -> None:
        """Can create error overlay with message."""
        overlay = ErrorOverlay(
            title="Test Error",
            message="Something went wrong",
        )
        assert overlay.title_text == "Test Error"
        assert overlay.message_text == "Something went wrong"
        assert overlay.details_text is None
        assert overlay.recovery_hints == []

    def test_overlay_with_details(self) -> None:
        """Can create error overlay with technical details."""
        overlay = ErrorOverlay(
            title="Database Error",
            message="Failed to connect",
            details="Connection timeout after 30s",
        )
        assert overlay.details_text == "Connection timeout after 30s"

    def test_overlay_with_recovery_hints(self) -> None:
        """Can create error overlay with recovery hints."""
        hints = [
            "Check your network connection",
            "Verify the service is running",
            "Try again in a moment",
        ]
        overlay = ErrorOverlay(
            title="Connection Error",
            message="Could not connect",
            recovery_hints=hints,
        )
        assert overlay.recovery_hints == hints
        assert len(overlay.recovery_hints) == 3

    @pytest.mark.asyncio
    async def test_overlay_rendering(self) -> None:
        """Overlay renders without errors."""
        from textual.app import App

        class TestApp(App[None]):
            pass

        app = TestApp()
        async with app.run_test() as pilot:
            overlay = ErrorOverlay(
                title="Test",
                message="Test message",
                details="Test details",
                recovery_hints=["Try this", "Or this"],
            )
            app.push_screen(overlay)

            await pilot.pause(0.05)

            # Should have rendered without crashing
            assert overlay.is_mounted


class TestFriendlyErrorMessage:
    """Test suite for friendly_error_message function."""

    def test_file_not_found_error(self) -> None:
        """FileNotFoundError gets friendly messaging."""
        exc = FileNotFoundError("config.json")
        title, message, hints = friendly_error_message(exc)

        assert "file" in title.lower() or "found" in title.lower()
        assert len(message) > 0
        assert len(hints) > 0
        assert any("file" in hint.lower() for hint in hints)

    def test_permission_error(self) -> None:
        """PermissionError gets friendly messaging."""
        exc = PermissionError("Access denied")
        title, message, hints = friendly_error_message(exc)

        assert "permission" in title.lower()
        assert len(message) > 0
        assert len(hints) > 0

    def test_value_error(self) -> None:
        """ValueError gets friendly messaging."""
        exc = ValueError("Invalid format")
        title, message, hints = friendly_error_message(exc)

        assert "invalid" in title.lower() or "data" in title.lower()
        assert len(message) > 0
        assert len(hints) > 0

    def test_generic_exception(self) -> None:
        """Generic exceptions get fallback messaging."""
        exc = RuntimeError("Unknown error")
        title, message, hints = friendly_error_message(exc)

        assert len(title) > 0
        assert len(message) > 0
        assert len(hints) > 0
        # Should suggest refreshing or reporting
        assert any("refresh" in hint.lower() or "report" in hint.lower() for hint in hints)

    def test_all_messages_have_hints(self) -> None:
        """All error types produce recovery hints."""
        exceptions = [
            FileNotFoundError("test"),
            PermissionError("test"),
            ValueError("test"),
            TypeError("test"),
            ConnectionError("test"),
            RuntimeError("test"),
        ]

        for exc in exceptions:
            _, _, hints = friendly_error_message(exc)
            assert len(hints) >= 1, f"No hints for {type(exc).__name__}"
            assert all(isinstance(h, str) for h in hints)
            assert all(len(h) > 0 for h in hints)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
