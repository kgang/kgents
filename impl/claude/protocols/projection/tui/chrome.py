"""
TUI Chrome: Error, Refusal, and Cache badge components.

Provides consistent status chrome across TUI widgets.
"""

from __future__ import annotations

from typing import Any

from protocols.projection.schema import CacheMeta, ErrorInfo, RefusalInfo
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual.widgets import Static

# Error emoji mapping by category
ERROR_EMOJI = {
    "network": "📡",
    "notFound": "🔍",
    "permission": "🔐",
    "timeout": "⏱️",
    "validation": "❌",
    "unknown": "⚠️",
}


class TUIErrorPanel(Static):
    """
    TUI error display panel.

    Shows error with category-specific icon and retry info.
    """

    DEFAULT_CSS = """
    TUIErrorPanel {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(
        self, error: ErrorInfo, show_retry: bool = True, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._error = error
        self._show_retry = show_retry

    def render(self) -> RenderableType:
        emoji = ERROR_EMOJI.get(self._error.category, "⚠️")

        content = Text()
        content.append(f"{emoji} ", style="bold")
        content.append(self._error.message, style="bold red")
        content.append("\n")
        content.append(f"Code: {self._error.code}", style="dim")

        if self._error.trace_id:
            content.append(f"\nTrace: {self._error.trace_id}", style="dim")

        if self._show_retry and self._error.retry_after_seconds:
            content.append(
                f"\nRetry in {self._error.retry_after_seconds}s...",
                style="italic yellow",
            )

        if self._error.fallback_action:
            content.append(f"\n💡 {self._error.fallback_action}", style="italic")

        return Panel(
            content,
            title="Error",
            title_align="left",
            border_style="red",
            padding=(0, 1),
        )


class TUIRefusalPanel(Static):
    """
    TUI refusal display panel.

    Shows refusal with distinct styling from errors.
    """

    DEFAULT_CSS = """
    TUIRefusalPanel {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        refusal: RefusalInfo,
        show_appeal: bool = True,
        show_override: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._refusal = refusal
        self._show_appeal = show_appeal
        self._show_override = show_override

    def render(self) -> RenderableType:
        content = Text()
        content.append("🛑 ", style="bold")
        content.append("Action Refused", style="bold magenta")
        content.append("\n")
        content.append(self._refusal.reason, style="magenta")

        if self._refusal.consent_required:
            content.append(
                f"\nRequires: {self._refusal.consent_required}",
                style="bold magenta",
            )

        if self._show_appeal and self._refusal.appeal_to:
            content.append(
                f"\nAppeal path: {self._refusal.appeal_to}",
                style="italic cyan",
            )

        if self._show_override and self._refusal.override_cost is not None:
            content.append(
                f"\nOverride cost: {self._refusal.override_cost} tokens",
                style="italic yellow",
            )

        return Panel(
            content,
            title="Refused",
            title_align="left",
            border_style="magenta",
            padding=(0, 1),
        )


class TUICachedBadge(Static):
    """
    TUI cache badge indicator.

    Shows [CACHED] with age information.
    """

    DEFAULT_CSS = """
    TUICachedBadge {
        height: 1;
        width: auto;
    }
    """

    def __init__(self, cache: CacheMeta, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._cache = cache

    def _format_age(self) -> str:
        """Format cache age as human-readable string."""
        if not self._cache.cached_at:
            return ""

        from datetime import datetime, timezone

        cached = self._cache.cached_at
        now = datetime.now(timezone.utc)
        diff = now - cached

        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds}s ago"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    def render(self) -> RenderableType:
        age = self._format_age()
        text = Text()
        text.append("⚡ ", style="bold yellow")
        text.append("[CACHED", style="bold yellow on dark_orange3")
        if age:
            text.append(f" {age}", style="bold yellow on dark_orange3")
        text.append("]", style="bold yellow on dark_orange3")

        if self._cache.deterministic:
            text.append(" •", style="dim")

        return text
