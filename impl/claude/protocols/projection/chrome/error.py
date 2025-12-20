"""
ErrorPanel: Technical error display with retry affordance.

Renders technical errors with:
- Category-specific emoji/icon
- Error code and message
- Optional retry countdown
- Fallback action suggestion

This is DISTINCT from RefusalPanel - errors are technical failures,
while refusals are semantic decisions by the agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget
from protocols.projection.schema import ErrorCategory, ErrorInfo

# Category to emoji mapping
ERROR_EMOJIS: dict[ErrorCategory, str] = {
    "network": "📡",
    "notFound": "🗺️",
    "permission": "🔐",
    "timeout": "⏰",
    "validation": "⚠️",
    "unknown": "🌀",
}

# Category to TUI color mapping
ERROR_COLORS: dict[ErrorCategory, str] = {
    "network": "yellow",
    "notFound": "blue",
    "permission": "red",
    "timeout": "yellow",
    "validation": "magenta",
    "unknown": "red",
}


@dataclass(frozen=True)
class ErrorPanelState:
    """State for error panel rendering."""

    error: ErrorInfo
    show_retry: bool = True
    retry_countdown: int | None = None  # Seconds until retry


class ErrorPanel(KgentsWidget[ErrorPanelState]):
    """
    Error display panel with retry affordance.

    Projections:
        - CLI: Text with emoji and formatting
        - TUI: Rich Panel with colored border
        - MARIMO: HTML with styled error box
        - JSON: Error info dict
    """

    def __init__(self, error: ErrorInfo, show_retry: bool = True) -> None:
        self.state = Signal.of(
            ErrorPanelState(
                error=error,
                show_retry=show_retry,
                retry_countdown=error.retry_after_seconds,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project error panel to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: formatted error text."""
        s = self.state.value
        error = s.error
        emoji = ERROR_EMOJIS.get(error.category, "❌")

        lines = [
            "",
            f"{emoji} Error: {error.message}",
            f"   Code: {error.code}",
        ]

        if error.trace_id:
            lines.append(f"   Trace: {error.trace_id}")

        if s.show_retry and error.is_retryable:
            if s.retry_countdown:
                lines.append(f"   Retry in {s.retry_countdown}s...")
            else:
                lines.append("   [Press 'r' to retry]")

        if error.fallback_action:
            lines.append(f"   Suggestion: {error.fallback_action}")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            s = self.state.value
            error = s.error
            emoji = ERROR_EMOJIS.get(error.category, "❌")
            color = ERROR_COLORS.get(error.category, "red")

            content = Text()
            content.append(f"{emoji} ", style="bold")
            content.append(error.message, style=f"bold {color}")
            content.append("\n\nCode: ", style="dim")
            content.append(error.code)

            if error.trace_id:
                content.append("\nTrace: ", style="dim")
                content.append(error.trace_id, style="dim")

            if s.show_retry and error.is_retryable:
                content.append("\n\n")
                if s.retry_countdown:
                    content.append(f"Retry in {s.retry_countdown}s", style="yellow")
                else:
                    content.append("[r] Retry", style="bold yellow")

            if error.fallback_action:
                content.append(f"\n\n💡 {error.fallback_action}", style="italic")

            return Panel(content, title="Error", border_style=color)

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML error box."""
        s = self.state.value
        error = s.error
        emoji = ERROR_EMOJIS.get(error.category, "❌")

        # Color mapping
        border_colors = {
            "network": "#f59e0b",  # amber
            "notFound": "#3b82f6",  # blue
            "permission": "#ef4444",  # red
            "timeout": "#f59e0b",  # amber
            "validation": "#a855f7",  # purple
            "unknown": "#ef4444",  # red
        }
        border_color = border_colors.get(error.category, "#ef4444")

        retry_html = ""
        if s.show_retry and error.is_retryable:
            if s.retry_countdown:
                retry_html = f'<p class="kgents-error-retry">Retry in {s.retry_countdown}s...</p>'
            else:
                retry_html = '<button class="kgents-error-retry-btn">Retry</button>'

        fallback_html = ""
        if error.fallback_action:
            fallback_html = f'<p class="kgents-error-fallback">💡 {error.fallback_action}</p>'

        trace_html = ""
        if error.trace_id:
            trace_html = f'<p class="kgents-error-trace">Trace: {error.trace_id}</p>'

        return f"""
        <div class="kgents-error-panel" style="border-left: 4px solid {border_color}; padding: 16px; background: #fef2f2; border-radius: 4px; margin: 8px 0;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 24px;">{emoji}</span>
                <span style="font-weight: 600; color: #991b1b;">{error.message}</span>
            </div>
            <p style="color: #7f1d1d; font-size: 14px; margin: 4px 0;">Code: <code>{error.code}</code></p>
            {trace_html}
            {retry_html}
            {fallback_html}
        </div>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: error info dict."""
        s = self.state.value
        error = s.error
        return {
            "type": "error_panel",
            "error": {
                "category": error.category,
                "code": error.code,
                "message": error.message,
                "retryAfterSeconds": error.retry_after_seconds,
                "fallbackAction": error.fallback_action,
                "traceId": error.trace_id,
                "isRetryable": error.is_retryable,
            },
            "showRetry": s.show_retry,
            "retryCountdown": s.retry_countdown,
            "emoji": ERROR_EMOJIS.get(error.category, "❌"),
        }


__all__ = ["ErrorPanel", "ErrorPanelState", "ERROR_EMOJIS", "ERROR_COLORS"]
