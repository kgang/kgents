"""
RefusalPanel: Semantic refusal display.

Renders agent refusals with:
- 🛑 icon (distinct from error icons)
- Reason explanation
- Consent requirement (if any)
- Appeal path (if any)
- Override cost (if any)

This is DISTINCT from ErrorPanel - refusals are semantic decisions
by the agent, not technical failures.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget
from protocols.projection.schema import RefusalInfo


@dataclass(frozen=True)
class RefusalPanelState:
    """State for refusal panel rendering."""

    refusal: RefusalInfo
    show_appeal: bool = True
    show_override: bool = True


class RefusalPanel(KgentsWidget[RefusalPanelState]):
    """
    Refusal display panel.

    Distinct from errors - refusals are semantic decisions.
    Uses purple/magenta styling to differentiate from red errors.

    Projections:
        - CLI: Text with 🛑 icon
        - TUI: Rich Panel with purple border
        - MARIMO: HTML with styled refusal box
        - JSON: Refusal info dict
    """

    def __init__(
        self,
        refusal: RefusalInfo,
        show_appeal: bool = True,
        show_override: bool = True,
    ) -> None:
        self.state = Signal.of(
            RefusalPanelState(
                refusal=refusal,
                show_appeal=show_appeal,
                show_override=show_override,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project refusal panel to target surface."""
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
        """CLI projection: formatted refusal text."""
        s = self.state.value
        refusal = s.refusal

        lines = [
            "",
            "🛑 Action Refused",
            f"   {refusal.reason}",
        ]

        if refusal.consent_required:
            lines.append(f"   Requires: {refusal.consent_required}")

        if s.show_appeal and refusal.appeal_to:
            lines.append(f"   Appeal: {refusal.appeal_to}")

        if s.show_override and refusal.override_cost is not None:
            lines.append(f"   Override cost: {refusal.override_cost} tokens")

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Panel."""
        try:
            from rich.panel import Panel
            from rich.text import Text

            s = self.state.value
            refusal = s.refusal

            content = Text()
            content.append("🛑 ", style="bold")
            content.append("Action Refused", style="bold magenta")
            content.append(f"\n\n{refusal.reason}", style="magenta")

            if refusal.consent_required:
                content.append("\n\nRequires: ", style="dim")
                content.append(refusal.consent_required, style="yellow")

            if s.show_appeal and refusal.appeal_to:
                content.append("\n\nAppeal path: ", style="dim")
                content.append(refusal.appeal_to, style="cyan")

            if s.show_override and refusal.override_cost is not None:
                content.append("\n\nOverride cost: ", style="dim")
                content.append(f"{refusal.override_cost} tokens", style="yellow")

            return Panel(content, title="Refused", border_style="magenta")

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML refusal box."""
        s = self.state.value
        refusal = s.refusal

        consent_html = ""
        if refusal.consent_required:
            consent_html = f"""
            <p style="color: #6b21a8; font-size: 14px; margin: 8px 0;">
                <strong>Requires:</strong> {refusal.consent_required}
            </p>
            """

        appeal_html = ""
        if s.show_appeal and refusal.appeal_to:
            appeal_html = f"""
            <p style="color: #6b21a8; font-size: 14px; margin: 8px 0;">
                <strong>Appeal path:</strong> <code>{refusal.appeal_to}</code>
            </p>
            """

        override_html = ""
        if s.show_override and refusal.override_cost is not None:
            override_html = f"""
            <p style="color: #6b21a8; font-size: 14px; margin: 8px 0;">
                <strong>Override cost:</strong> {refusal.override_cost} tokens
                <button class="kgents-override-btn" style="margin-left: 8px; padding: 4px 12px; background: #9333ea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Override
                </button>
            </p>
            """

        return f"""
        <div class="kgents-refusal-panel" style="border-left: 4px solid #a855f7; padding: 16px; background: #faf5ff; border-radius: 4px; margin: 8px 0;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 24px;">🛑</span>
                <span style="font-weight: 600; color: #6b21a8;">Action Refused</span>
            </div>
            <p style="color: #581c87; margin: 8px 0;">{refusal.reason}</p>
            {consent_html}
            {appeal_html}
            {override_html}
        </div>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: refusal info dict."""
        s = self.state.value
        refusal = s.refusal
        return {
            "type": "refusal_panel",
            "refusal": {
                "reason": refusal.reason,
                "consentRequired": refusal.consent_required,
                "appealTo": refusal.appeal_to,
                "overrideCost": refusal.override_cost,
            },
            "showAppeal": s.show_appeal,
            "showOverride": s.show_override,
        }


__all__ = ["RefusalPanel", "RefusalPanelState"]
