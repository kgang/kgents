"""
CachedBadge: Prominent cache indicator.

Renders a visible [CACHED] badge when data is stale.
Shows cache age for context.

Example:
    badge = CachedBadge(age_seconds=120)
    print(badge.to_cli())  # "[CACHED 2m ago]"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


def format_age(seconds: float) -> str:
    """Format age in human-readable form."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h"
    else:
        days = int(seconds / 86400)
        return f"{days}d"


@dataclass(frozen=True)
class CachedBadgeState:
    """State for cache badge rendering."""

    age_seconds: float
    show_age: bool = True
    deterministic: bool = True


class CachedBadge(KgentsWidget[CachedBadgeState]):
    """
    Prominent [CACHED] badge.

    Shows prominently when data is from cache, especially when stale.
    Includes age information for context.

    Projections:
        - CLI: "[CACHED 2m ago]" text
        - TUI: Rich Text with yellow styling
        - MARIMO: HTML badge with animation
        - JSON: Badge state dict
    """

    def __init__(
        self,
        age_seconds: float,
        show_age: bool = True,
        deterministic: bool = True,
    ) -> None:
        self.state = Signal.of(
            CachedBadgeState(
                age_seconds=age_seconds,
                show_age=show_age,
                deterministic=deterministic,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project cache badge to target surface."""
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
        """CLI projection: bracketed text."""
        s = self.state.value

        if s.show_age:
            age_str = format_age(s.age_seconds)
            return f"[CACHED {age_str} ago]"
        else:
            return "[CACHED]"

    def _to_tui(self) -> Any:
        """TUI projection: Rich Text."""
        try:
            from rich.text import Text

            s = self.state.value

            text = Text()
            text.append(" [CACHED", style="bold black on yellow")
            if s.show_age:
                age_str = format_age(s.age_seconds)
                text.append(f" {age_str} ago", style="bold black on yellow")
            text.append("] ", style="bold black on yellow")

            return text

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML badge."""
        s = self.state.value

        age_html = ""
        if s.show_age:
            age_str = format_age(s.age_seconds)
            age_html = f" {age_str} ago"

        # Subtle pulse animation for visibility
        return f"""
        <span class="kgents-cached-badge" style="
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            background: #fbbf24;
            color: #78350f;
            font-weight: 600;
            font-size: 12px;
            border-radius: 4px;
            animation: kgents-badge-pulse 2s ease-in-out infinite;
        ">
            [CACHED{age_html}]
        </span>
        <style>
            @keyframes kgents-badge-pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.8; }}
            }}
        </style>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: badge state dict."""
        s = self.state.value
        return {
            "type": "cached_badge",
            "ageSeconds": s.age_seconds,
            "ageFormatted": format_age(s.age_seconds),
            "showAge": s.show_age,
            "deterministic": s.deterministic,
        }


__all__ = ["CachedBadge", "CachedBadgeState", "format_age"]
