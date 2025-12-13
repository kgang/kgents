"""
Session State Persistence for I-gent v2.5.

Stores:
- Cursor position (focused agent)
- Layout preferences
- Agent positions in the flux view
- Connection visibility settings

HotData Integration (AD-004):
Demo functions use pre-computed fixtures when available,
with inline fallbacks for first-run scenarios.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shared.hotdata import FIXTURES_DIR, HotData, register_hotdata

from ..widgets.density_field import Phase


@dataclass
class AgentSnapshot:
    """
    Snapshot of an agent's state for visualization.

    This is what the FluxScreen uses to render agents.
    """

    id: str
    name: str
    phase: Phase = Phase.DORMANT
    activity: float = 0.0
    children: list[str] = field(default_factory=list)
    summary: str = ""

    # Position in the flux view (grid coordinates)
    grid_x: int = 0
    grid_y: int = 0

    # Connections to other agents (id -> throughput)
    connections: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase.value,
            "activity": self.activity,
            "children": self.children,
            "summary": self.summary,
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "connections": self.connections,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentSnapshot":
        """Create from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            phase=Phase(data.get("phase", "DORMANT")),
            activity=data.get("activity", 0.0),
            children=data.get("children", []),
            summary=data.get("summary", ""),
            grid_x=data.get("grid_x", 0),
            grid_y=data.get("grid_y", 0),
            connections=data.get("connections", {}),
        )


@dataclass
class FluxState:
    """
    State of the Flux view.

    Contains all agents and their positions/connections.
    """

    agents: dict[str, AgentSnapshot] = field(default_factory=dict)
    focused_id: str | None = None

    # Grid dimensions
    grid_width: int = 8
    grid_height: int = 6

    def add_agent(self, agent: AgentSnapshot) -> None:
        """Add an agent to the flux."""
        self.agents[agent.id] = agent

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the flux."""
        self.agents.pop(agent_id, None)
        if self.focused_id == agent_id:
            self.focused_id = None

    def get_agent(self, agent_id: str) -> AgentSnapshot | None:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def get_focused(self) -> AgentSnapshot | None:
        """Get the currently focused agent."""
        if self.focused_id:
            return self.agents.get(self.focused_id)
        return None

    def focus_next(self) -> None:
        """Focus the next agent (by ID order)."""
        if not self.agents:
            return
        ids = sorted(self.agents.keys())
        if self.focused_id is None:
            self.focused_id = ids[0]
        else:
            try:
                idx = ids.index(self.focused_id)
                self.focused_id = ids[(idx + 1) % len(ids)]
            except ValueError:
                self.focused_id = ids[0]

    def focus_prev(self) -> None:
        """Focus the previous agent (by ID order)."""
        if not self.agents:
            return
        ids = sorted(self.agents.keys())
        if self.focused_id is None:
            self.focused_id = ids[-1]
        else:
            try:
                idx = ids.index(self.focused_id)
                self.focused_id = ids[(idx - 1) % len(ids)]
            except ValueError:
                self.focused_id = ids[-1]

    def get_agent_at_grid(self, x: int, y: int) -> AgentSnapshot | None:
        """Get agent at grid position."""
        for agent in self.agents.values():
            if agent.grid_x == x and agent.grid_y == y:
                return agent
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "agents": {k: v.to_dict() for k, v in self.agents.items()},
            "focused_id": self.focused_id,
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FluxState":
        """Create from dict."""
        state = cls(
            focused_id=data.get("focused_id"),
            grid_width=data.get("grid_width", 8),
            grid_height=data.get("grid_height", 6),
        )
        for agent_data in data.get("agents", {}).values():
            state.add_agent(AgentSnapshot.from_dict(agent_data))
        return state


@dataclass
class SessionState:
    """
    Persistent session state.

    Stores user preferences and last known flux state.
    """

    flux: FluxState = field(default_factory=FluxState)

    # UI preferences
    show_connections: bool = True
    show_labels: bool = True
    animation_enabled: bool = True

    # Last known cursor position
    last_focused_id: str | None = None

    def save(self, path: Path) -> None:
        """Save session state to file."""
        data = {
            "flux": self.flux.to_dict(),
            "show_connections": self.show_connections,
            "show_labels": self.show_labels,
            "animation_enabled": self.animation_enabled,
            "last_focused_id": self.last_focused_id,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        """Load session state from file."""
        if not path.exists():
            return cls()

        try:
            data = json.loads(path.read_text())
            state = cls(
                flux=FluxState.from_dict(data.get("flux", {})),
                show_connections=data.get("show_connections", True),
                show_labels=data.get("show_labels", True),
                animation_enabled=data.get("animation_enabled", True),
                last_focused_id=data.get("last_focused_id"),
            )
            # Restore focus
            if state.last_focused_id and state.last_focused_id in state.flux.agents:
                state.flux.focused_id = state.last_focused_id
            return state
        except (json.JSONDecodeError, KeyError):
            return cls()


# ─────────────────────────────────────────────────────────────────────────────
# HotData Fixtures (AD-004: Pre-Computed Richness)
# ─────────────────────────────────────────────────────────────────────────────

DEMO_FLUX_STATE_HOTDATA = HotData(
    path=FIXTURES_DIR / "flux_states" / "demo.json",
    schema=FluxState,
)

# Register with global registry for CLI management
register_hotdata("demo_flux_state", DEMO_FLUX_STATE_HOTDATA)


def _create_fallback_flux_state() -> FluxState:
    """
    Create inline fallback flux state (used when fixture is missing).

    This is the inline definition preserved for first-run scenarios
    and test environments where fixtures may not be available.
    """
    state = FluxState()

    agents = [
        AgentSnapshot(
            id="g-gent",
            name="Grammar",
            phase=Phase.ACTIVE,
            activity=0.7,
            grid_x=0,
            grid_y=0,
            summary="Parsing morphisms",
            connections={"robin": 0.8},
        ),
        AgentSnapshot(
            id="robin",
            name="Robin",
            phase=Phase.ACTIVE,
            activity=0.9,
            grid_x=2,
            grid_y=1,
            summary="Hypothesis synthesis",
            connections={"summarizer": 0.6, "j-gent": 0.3},
        ),
        AgentSnapshot(
            id="j-gent",
            name="J-gent",
            phase=Phase.WAKING,
            activity=0.3,
            grid_x=4,
            grid_y=0,
            summary="Lazy evaluation",
            connections={},
        ),
        AgentSnapshot(
            id="summarizer",
            name="Summarizer",
            phase=Phase.DORMANT,
            activity=0.1,
            grid_x=4,
            grid_y=2,
            summary="Waiting for input",
            connections={},
        ),
        AgentSnapshot(
            id="o-gent",
            name="Observer",
            phase=Phase.ACTIVE,
            activity=0.5,
            grid_x=0,
            grid_y=2,
            summary="Monitoring XYZ",
            connections={"robin": 0.4, "g-gent": 0.2},
        ),
        AgentSnapshot(
            id="psi-gent",
            name="Psychopomp",
            phase=Phase.WANING,
            activity=0.2,
            grid_x=2,
            grid_y=3,
            summary="Metaphor engine idle",
            connections={},
        ),
    ]

    for agent in agents:
        state.add_agent(agent)

    state.focused_id = "robin"
    return state


def create_demo_flux_state() -> FluxState:
    """
    Create a demo flux state with sample agents.

    HotData Integration (AD-004):
    - Loads from pre-computed fixture when available
    - Falls back to inline definition for first-run scenarios

    The pre-computed fixture contains richer, LLM-generated data.
    """
    return DEMO_FLUX_STATE_HOTDATA.load_or_default(_create_fallback_flux_state())
