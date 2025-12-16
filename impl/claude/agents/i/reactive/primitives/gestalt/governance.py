"""
GovernanceTableWidget: Agent governance state table.

Displays agent governance information including:
- Agent identity and status
- Consent levels (0-1 continuum)
- Permission states
- Governance decisions history

Integrates with the Projection Component Library for unified rendering.

Example:
    widget = GovernanceTableWidget(GovernanceTableState(
        entries=(
            GovernanceEntry(
                agent_id="kgent-soul",
                agent_name="K-gent Soul",
                consent_level=0.85,
                permissions=("read", "write", "execute"),
                status="active",
            ),
            GovernanceEntry(
                agent_id="mgent-memory",
                agent_name="M-gent Memory",
                consent_level=0.6,
                permissions=("read", "append"),
                status="idle",
            ),
        ),
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    from protocols.projection.schema import UIHint

GovernanceStatus = Literal["active", "idle", "suspended", "revoked", "pending"]


@dataclass(frozen=True)
class GovernanceEntry:
    """
    A single governance entry for an agent.

    Attributes:
        agent_id: Unique agent identifier
        agent_name: Human-readable agent name
        consent_level: Consent as continuum [0.0, 1.0]
        permissions: Granted permission flags
        status: Current governance status
        last_action: Description of last governance action
        last_action_time: ISO timestamp of last action
        appeal_path: AGENTESE path for appeals (if any)
    """

    agent_id: str
    agent_name: str
    consent_level: float = 1.0  # 0.0 = no consent, 1.0 = full consent
    permissions: tuple[str, ...] = ()
    status: GovernanceStatus = "active"
    last_action: str | None = None
    last_action_time: str | None = None
    appeal_path: str | None = None


@dataclass(frozen=True)
class GovernanceTableState:
    """
    Immutable governance table state.

    Attributes:
        entries: All governance entries
        title: Table title
        sort_by: Column to sort by
        sort_direction: Sort direction
        show_inactive: Whether to show inactive/revoked agents
        highlight_agent: Agent ID to highlight
    """

    entries: tuple[GovernanceEntry, ...] = ()
    title: str = "Agent Governance"
    sort_by: Literal["name", "consent", "status"] = "name"
    sort_direction: Literal["asc", "desc"] = "asc"
    show_inactive: bool = True
    highlight_agent: str | None = None

    @property
    def sorted_entries(self) -> tuple[GovernanceEntry, ...]:
        """Get entries sorted by current sort settings."""
        entries = self.entries
        if not self.show_inactive:
            entries = tuple(
                e for e in entries if e.status not in ("revoked", "suspended")
            )

        key_funcs = {
            "name": lambda e: e.agent_name.lower(),
            "consent": lambda e: e.consent_level,
            "status": lambda e: e.status,
        }

        reverse = self.sort_direction == "desc"
        return tuple(sorted(entries, key=key_funcs[self.sort_by], reverse=reverse))


# Status to indicator mapping
STATUS_INDICATORS: dict[GovernanceStatus, tuple[str, str]] = {
    "active": ("●", "green"),
    "idle": ("○", "yellow"),
    "suspended": ("⊘", "orange"),
    "revoked": ("✗", "red"),
    "pending": ("◔", "blue"),
}


def _consent_bar(level: float, width: int = 10) -> str:
    """Create an ASCII consent bar."""
    filled = int(level * width)
    empty = width - filled
    return f"{'█' * filled}{'░' * empty}"


def _consent_color(level: float) -> str:
    """Get color for consent level."""
    if level >= 0.8:
        return "green"
    elif level >= 0.5:
        return "yellow"
    elif level >= 0.2:
        return "orange"
    else:
        return "red"


class GovernanceTableWidget(KgentsWidget[GovernanceTableState]):
    """
    Agent governance state table widget.

    Displays agent governance information in a tabular format
    with consent visualization and permission lists.
    """

    def __init__(self, state: GovernanceTableState | None = None) -> None:
        self.state = Signal.of(state or GovernanceTableState())

    def project(self, target: RenderTarget) -> Any:
        """Project governance table to target surface."""
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
        """CLI projection: ASCII table."""
        s = self.state.value
        entries = s.sorted_entries

        if not entries:
            return "(no governance entries)"

        lines = []
        if s.title:
            lines.append(s.title)
            lines.append("=" * len(s.title))
            lines.append("")

        # Header
        header = f"{'Agent':<25} │ {'Status':<10} │ {'Consent':<12} │ Permissions"
        lines.append(header)
        lines.append("─" * 25 + "─┼─" + "─" * 10 + "─┼─" + "─" * 12 + "─┼─" + "─" * 20)

        # Rows
        for entry in entries:
            indicator, _ = STATUS_INDICATORS.get(entry.status, ("?", "white"))
            consent_bar = _consent_bar(entry.consent_level, 8)
            consent_pct = f"{entry.consent_level * 100:.0f}%"
            permissions = ", ".join(entry.permissions[:3])
            if len(entry.permissions) > 3:
                permissions += f" +{len(entry.permissions) - 3}"

            highlight = "→" if entry.agent_id == s.highlight_agent else " "
            name = entry.agent_name[:24]
            lines.append(
                f"{highlight}{name:<24} │ {indicator} {entry.status:<8} │ "
                f"{consent_bar} {consent_pct:>3} │ {permissions}"
            )

            # Show last action if present
            if entry.last_action:
                lines.append(f"  └─ Last: {entry.last_action}")

        # Summary
        active_count = sum(1 for e in entries if e.status == "active")
        avg_consent = (
            sum(e.consent_level for e in entries) / len(entries) if entries else 0
        )
        lines.append("")
        lines.append(
            f"Active: {active_count}/{len(entries)} | Avg Consent: {avg_consent:.0%}"
        )

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: Rich Table."""
        try:
            from rich.table import Table
            from rich.text import Text

            s = self.state.value
            entries = s.sorted_entries

            table = Table(title=s.title, show_header=True)
            table.add_column("Agent", style="bold")
            table.add_column("Status", justify="center")
            table.add_column("Consent", justify="center")
            table.add_column("Permissions")

            for entry in entries:
                indicator, color = STATUS_INDICATORS.get(entry.status, ("?", "white"))
                status_text = Text(f"{indicator} {entry.status}", style=color)

                # Consent bar with color
                consent_color = _consent_color(entry.consent_level)
                consent_text = Text()
                consent_text.append(
                    _consent_bar(entry.consent_level, 8), style=consent_color
                )
                consent_text.append(f" {entry.consent_level * 100:.0f}%", style="dim")

                permissions = ", ".join(entry.permissions[:4])
                if len(entry.permissions) > 4:
                    permissions += f" +{len(entry.permissions) - 4}"

                style = "bold" if entry.agent_id == s.highlight_agent else ""
                table.add_row(
                    entry.agent_name,
                    status_text,
                    consent_text,
                    permissions,
                    style=style,
                )

            return table

        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML table with consent visualization."""
        s = self.state.value
        entries = s.sorted_entries

        # Build HTML rows
        rows_html = []
        for entry in entries:
            indicator, color = STATUS_INDICATORS.get(entry.status, ("?", "gray"))
            consent_color = _consent_color(entry.consent_level)
            consent_pct = entry.consent_level * 100

            highlighted = (
                "kgents-highlighted" if entry.agent_id == s.highlight_agent else ""
            )
            permissions = ", ".join(entry.permissions)

            rows_html.append(f"""
            <tr class="{highlighted}">
                <td class="kgents-agent-name">{entry.agent_name}</td>
                <td class="kgents-status" style="color: {color};">
                    {indicator} {entry.status}
                </td>
                <td class="kgents-consent">
                    <div class="kgents-consent-bar" style="width: 100px;">
                        <div class="kgents-consent-fill" style="width: {consent_pct}%; background: {consent_color};"></div>
                    </div>
                    <span>{consent_pct:.0f}%</span>
                </td>
                <td class="kgents-permissions">{permissions}</td>
            </tr>
            """)

        return f"""
        <div class="kgents-governance-table">
            <h3>{s.title}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Status</th>
                        <th>Consent</th>
                        <th>Permissions</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows_html)}
                </tbody>
            </table>
            <style>
                .kgents-consent-bar {{
                    height: 8px;
                    background: #e5e7eb;
                    border-radius: 4px;
                    overflow: hidden;
                    display: inline-block;
                    vertical-align: middle;
                    margin-right: 8px;
                }}
                .kgents-consent-fill {{
                    height: 100%;
                    transition: width 0.3s;
                }}
                .kgents-highlighted {{
                    background: #fef3c7;
                }}
            </style>
        </div>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        entries = s.sorted_entries

        return {
            "type": "governance_table",
            "title": s.title,
            "entries": [
                {
                    "agentId": e.agent_id,
                    "agentName": e.agent_name,
                    "consentLevel": e.consent_level,
                    "permissions": list(e.permissions),
                    "status": e.status,
                    "lastAction": e.last_action,
                    "lastActionTime": e.last_action_time,
                    "appealPath": e.appeal_path,
                }
                for e in entries
            ],
            "sortBy": s.sort_by,
            "sortDirection": s.sort_direction,
            "showInactive": s.show_inactive,
            "highlightAgent": s.highlight_agent,
            "summary": {
                "total": len(entries),
                "active": sum(1 for e in entries if e.status == "active"),
                "avgConsent": sum(e.consent_level for e in entries) / len(entries)
                if entries
                else 0,
            },
        }

    def ui_hint(self) -> "UIHint":
        """Return 'table' UI hint for projection system."""
        return "table"

    def widget_type(self) -> str:
        """Return widget type identifier."""
        return "governance_table"


__all__ = [
    "GovernanceTableWidget",
    "GovernanceTableState",
    "GovernanceEntry",
    "GovernanceStatus",
]
