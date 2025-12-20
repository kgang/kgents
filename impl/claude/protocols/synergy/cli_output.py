"""
Synergy CLI Output: Unified notification formatting for cross-jewel events.

Wave 2: UI Integration - Make synergy notifications visible in CLI.

This module provides consistent formatting for synergy notifications
across all jewels, following the Orisinal aesthetic (gentle, hopeful).

Usage:
    from protocols.synergy.cli_output import display_synergy_notification

    # In a CLI handler after synergy event
    display_synergy_notification(result)

Output format:
    ↳ 🔗 Synergy: Architecture snapshot captured to Brain
    ↳ Crystal: "gestalt-impl-claude-2025-12-16"
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, TextIO

if TYPE_CHECKING:
    from .events import SynergyResult

# =============================================================================
# Formatting Constants
# =============================================================================

# Unicode characters for synergy output
ARROW = "↳"
LINK_ICON = "🔗"
CRYSTAL_ICON = "💎"
SUCCESS_ICON = "✓"
SKIP_ICON = "○"
FAIL_ICON = "✗"

# ANSI color codes (optional, gracefully degrade)
try:
    import os

    _COLORS_ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
except Exception:
    _COLORS_ENABLED = False

# Colors
_CYAN = "\033[36m" if _COLORS_ENABLED else ""
_GREEN = "\033[32m" if _COLORS_ENABLED else ""
_YELLOW = "\033[33m" if _COLORS_ENABLED else ""
_RED = "\033[31m" if _COLORS_ENABLED else ""
_DIM = "\033[2m" if _COLORS_ENABLED else ""
_RESET = "\033[0m" if _COLORS_ENABLED else ""


# =============================================================================
# Display Functions
# =============================================================================


def display_synergy_notification(
    result: "SynergyResult",
    stream: TextIO | None = None,
    indent: int = 2,
    show_skipped: bool = False,
    show_failures: bool = False,
) -> bool:
    """
    Display a synergy notification to the CLI.

    Args:
        result: The SynergyResult from a handler
        stream: Output stream (defaults to stdout)
        indent: Number of spaces to indent
        show_skipped: Whether to show skipped handlers
        show_failures: Whether to show failed handlers

    Returns:
        True if something was displayed, False otherwise
    """
    stream = stream or sys.stdout
    prefix = " " * indent

    if result.success and result.artifact_id:
        # Successful synergy with artifact
        stream.write(f"{prefix}{ARROW} {LINK_ICON} {_CYAN}Synergy:{_RESET} {result.message}\n")
        stream.write(f'{prefix}{ARROW} {CRYSTAL_ICON} Crystal: "{result.artifact_id}"\n')
        return True

    elif result.success and result.metadata.get("skipped"):
        if show_skipped:
            stream.write(f"{prefix}{ARROW} {SKIP_ICON} {_DIM}(skipped){_RESET}\n")
            return True
        return False

    elif result.success:
        # Successful but no artifact
        stream.write(f"{prefix}{ARROW} {SUCCESS_ICON} {_GREEN}{result.message}{_RESET}\n")
        return True

    elif not result.success:
        if show_failures:
            stream.write(
                f"{prefix}{ARROW} {FAIL_ICON} {_RED}Synergy failed: {result.message}{_RESET}\n"
            )
            return True
        return False

    return False


def display_synergy_results(
    results: list["SynergyResult"],
    stream: TextIO | None = None,
    indent: int = 2,
    show_skipped: bool = False,
    show_failures: bool = False,
) -> int:
    """
    Display multiple synergy results.

    Args:
        results: List of SynergyResults to display
        stream: Output stream
        indent: Indentation
        show_skipped: Show skipped handlers
        show_failures: Show failed handlers

    Returns:
        Number of notifications displayed
    """
    displayed = 0
    for result in results:
        if display_synergy_notification(result, stream, indent, show_skipped, show_failures):
            displayed += 1
    return displayed


# =============================================================================
# Synergy Notification Context Manager
# =============================================================================


@dataclass
class SynergyNotificationContext:
    """
    Context manager for collecting and displaying synergy notifications.

    Usage:
        with SynergyNotificationContext() as ctx:
            # ... emit synergy events ...

        # Notifications are displayed on exit
    """

    indent: int = 2
    stream: TextIO | None = None
    show_skipped: bool = False
    show_failures: bool = False
    _results: list["SynergyResult"] | None = None
    _unsubscribe: Callable[[], None] | None = None

    def __enter__(self) -> "SynergyNotificationContext":
        from .bus import get_synergy_bus

        self._results = []
        bus = get_synergy_bus()

        def on_result(event: Any, result: "SynergyResult") -> None:
            if self._results is not None:
                self._results.append(result)

        self._unsubscribe = bus.subscribe_results(on_result)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._unsubscribe:
            self._unsubscribe()

        if self._results:
            display_synergy_results(
                self._results,
                self.stream,
                self.indent,
                self.show_skipped,
                self.show_failures,
            )

    @property
    def results(self) -> list["SynergyResult"]:
        return self._results or []


def create_notification_context(
    indent: int = 2,
    stream: TextIO | None = None,
    show_skipped: bool = False,
    show_failures: bool = False,
) -> SynergyNotificationContext:
    """
    Create a synergy notification context.

    Usage:
        with create_notification_context() as ctx:
            await bus.emit(event)
        # Notifications displayed automatically
    """
    return SynergyNotificationContext(
        indent=indent,
        stream=stream,
        show_skipped=show_skipped,
        show_failures=show_failures,
    )


# =============================================================================
# Formatted Message Helpers
# =============================================================================


def format_synergy_header(source_jewel: str, target_jewel: str) -> str:
    """Format a synergy header for display."""
    return f"{_CYAN}Synergy: {source_jewel} → {target_jewel}{_RESET}"


def format_crystal_reference(crystal_id: str) -> str:
    """Format a crystal reference."""
    return f'{CRYSTAL_ICON} Crystal: "{crystal_id}"'


def format_synergy_arrow(message: str) -> str:
    """Format a message with synergy arrow prefix."""
    return f"  {ARROW} {message}"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Display functions
    "display_synergy_notification",
    "display_synergy_results",
    # Context manager
    "SynergyNotificationContext",
    "create_notification_context",
    # Formatting helpers
    "format_synergy_header",
    "format_crystal_reference",
    "format_synergy_arrow",
    # Constants
    "ARROW",
    "LINK_ICON",
    "CRYSTAL_ICON",
]
