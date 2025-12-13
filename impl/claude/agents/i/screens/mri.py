"""
MRIScreen - The deepest zoom level (LOD 2).

Shows agent internals at the token level:
- Token context window visualization (mocked for now)
- Vector store retrieval visualization (mocked for now)
- Entropy panel (real-time uncertainty metrics)
- Memory crystal list
- Full state dump

This is the "MRI scan" of agent cognition - you see the raw machinery.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ..data.state import AgentSnapshot
from ..widgets.density_field import DensityField

if TYPE_CHECKING:
    pass


class MRIScreen(Screen[None]):
    """
    MRI View - LOD Level 2 (Internal).

    The deepest zoom showing raw agent internals.
    This is for debugging and deep inspection.
    """

    CSS = """
    MRIScreen {
        background: #1a1a1a;
    }

    MRIScreen #main-container {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        padding: 1;
    }

    MRIScreen .panel {
        border: solid #4a4a5c;
        padding: 1;
        background: #252525;
    }

    MRIScreen .panel-title {
        text-style: bold;
        color: #e6a352;
        margin-bottom: 1;
    }

    MRIScreen .agent-header {
        dock: top;
        height: 3;
        background: #252525;
        border-bottom: solid #4a4a5c;
        padding: 1 2;
        color: #f5f0e6;
    }

    MRIScreen .agent-name {
        text-style: bold;
        color: #f5d08a;
    }

    MRIScreen .metric-label {
        color: #b3a89a;
    }

    MRIScreen .metric-value {
        color: #f5d08a;
    }

    MRIScreen .warning {
        color: #c97b84;
    }

    MRIScreen .info {
        color: #8b7ba5;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh_data", "Refresh", show=True),
        Binding("e", "export", "Export", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        agent_snapshot: AgentSnapshot | None = None,
        agent_id: str = "",
        agent_name: str = "",
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._demo_mode = demo_mode

        # In demo mode, create a demo snapshot if none provided
        if demo_mode and agent_snapshot is None:
            from .cockpit import create_demo_snapshot

            agent_snapshot = create_demo_snapshot()

        self.agent_snapshot = agent_snapshot
        self.agent_id = agent_id or (agent_snapshot.id if agent_snapshot else "")
        self.agent_name = agent_name or (agent_snapshot.name if agent_snapshot else "")

    def compose(self) -> ComposeResult:
        """Compose the MRI screen."""
        yield Header()

        # Agent header
        with Container(classes="agent-header"):
            yield Static(
                f"[bold #f5d08a]MRI SCAN: {self.agent_name or self.agent_id or 'Unknown'}[/]"
            )
            if self.agent_snapshot:
                yield Static(
                    f"Phase: {self.agent_snapshot.phase.value}  │  "
                    f"Activity: {self.agent_snapshot.activity:.3f}  │  "
                    f"Position: ({self.agent_snapshot.grid_x}, {self.agent_snapshot.grid_y})"
                )

        # Main grid of panels
        with Container(id="main-container"):
            # Panel 1: Token Context Window
            with Container(classes="panel"):
                yield Static("[Token Context Window]", classes="panel-title")
                yield Static("")
                yield Static(
                    "[#8b7ba5]Token heatmap visualization - not yet implemented[/]"
                )
                yield Static("")
                yield Static("This would show:")
                yield Static("  • Token-by-token attention weights")
                yield Static("  • Context window utilization")
                yield Static("  • Token probability distribution")
                yield Static("  • Uncertainty per token")

            # Panel 2: Vector Store Retrieval
            with Container(classes="panel"):
                yield Static("[Vector Store Retrieval]", classes="panel-title")
                yield Static("")
                yield Static(
                    "[#8b7ba5]Retrieval visualization - not yet implemented[/]"
                )
                yield Static("")
                yield Static("This would show:")
                yield Static("  • Retrieved memory chunks")
                yield Static("  • Similarity scores")
                yield Static("  • Embedding space projection")
                yield Static("  • Retrieval frequency heatmap")

            # Panel 3: Entropy Panel
            with Container(classes="panel"):
                yield Static("[Entropy & Uncertainty]", classes="panel-title")
                yield Static("")
                if self.agent_snapshot:
                    # Derive entropy from activity (mock calculation)
                    entropy = self.agent_snapshot.activity * 0.3
                    yield Static(
                        f"[#b3a89a]Current entropy:[/] [#f5d08a]{entropy:.3f}[/]"
                    )
                    yield Static(
                        f"[#b3a89a]Activity level:[/] [#f5d08a]{self.agent_snapshot.activity:.3f}[/]"
                    )
                    yield Static("")
                    if entropy > 0.7:
                        yield Static("[#c97b84]⚠ High uncertainty detected[/]")
                    elif entropy < 0.2:
                        yield Static("[#8b7ba5]✓ High confidence[/]")
                    else:
                        yield Static("[#8b7ba5]○ Normal operating range[/]")
                else:
                    yield Static("[#c97b84]No snapshot data available[/]")

            # Panel 4: Memory Crystals
            with Container(classes="panel"):
                yield Static("[Memory Crystals]", classes="panel-title")
                yield Static("")
                yield Static("[#8b7ba5]Memory list - not yet implemented[/]")
                yield Static("")
                yield Static("This would show:")
                yield Static("  • Crystallized moments (from Loom)")
                yield Static("  • Long-term memory entries")
                yield Static("  • Memory formation timestamps")
                yield Static("  • Recall frequency")

            # Panel 5: Full State Dump
            with Container(classes="panel"):
                yield Static("[Full State]", classes="panel-title")
                yield Static("")
                if self.agent_snapshot:
                    yield Static(f"[#b3a89a]ID:[/] {self.agent_snapshot.id}")
                    yield Static(f"[#b3a89a]Name:[/] {self.agent_snapshot.name}")
                    yield Static(
                        f"[#b3a89a]Phase:[/] {self.agent_snapshot.phase.value}"
                    )
                    yield Static(
                        f"[#b3a89a]Activity:[/] {self.agent_snapshot.activity:.3f}"
                    )
                    yield Static(
                        f"[#b3a89a]Grid Position:[/] ({self.agent_snapshot.grid_x}, {self.agent_snapshot.grid_y})"
                    )
                    yield Static(
                        f"[#b3a89a]Children:[/] {len(self.agent_snapshot.children)}"
                    )
                    yield Static(
                        f"[#b3a89a]Connections:[/] {len(self.agent_snapshot.connections)}"
                    )
                    yield Static("")
                    yield Static(f"[#b3a89a]Summary:[/] {self.agent_snapshot.summary}")
                else:
                    yield Static("[#c97b84]No snapshot data[/]")

            # Panel 6: Live Density Field
            with Container(classes="panel"):
                yield Static("[Live Density Field]", classes="panel-title")
                yield Static("")
                if self.agent_snapshot:
                    yield DensityField(
                        agent_id=self.agent_snapshot.id,
                        agent_name=self.agent_snapshot.name,
                        activity=self.agent_snapshot.activity,
                        phase=self.agent_snapshot.phase,
                    )
                else:
                    yield Static("[#c97b84]No snapshot available[/]")

        yield Footer()

    def action_back(self) -> None:
        """Return to previous screen (Escape)."""
        self.dismiss()

    def action_refresh_data(self) -> None:
        """Refresh the MRI data (r key)."""
        self.notify("Refreshing MRI scan... (not yet implemented)")

    def action_export(self) -> None:
        """Export MRI data to file (e key)."""
        self.notify("Export MRI data (not yet implemented)")

    def action_quit(self) -> None:
        """Quit the application (q key)."""
        self.app.exit()

    def update_snapshot(self, snapshot: AgentSnapshot) -> None:
        """
        Update the displayed agent snapshot.

        Args:
            snapshot: New snapshot to display
        """
        self.agent_snapshot = snapshot
        self.agent_id = snapshot.id
        self.agent_name = snapshot.name
        # Trigger a re-render
        self.refresh()
