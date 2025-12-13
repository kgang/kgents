"""
I-gent Types: Core abstractions for the Living Codex Garden.

This module defines:
- Phase: The five moon-cycle lifecycle states
- Glyph: The atomic unit of visualization
- Scale: Fractal zoom levels
- MarginNote: Timestamped observations
- AgentState: Complete agent visualization state
- GardenState: Multiple agents in spatial relationship
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class Phase(Enum):
    """
    Agent lifecycle phases, rendered as moon symbols.

    These map to spec/anatomy.md lifecycle states but add
    contemplative semantics—the interface invites pause
    and observation, not just status monitoring.
    """

    DORMANT = "dormant"  # ○ Defined but not instantiated; sleeping
    WAKING = "waking"  # ◐ Partially active; initializing or paused
    ACTIVE = "active"  # ● Fully alive; processing or ready
    WANING = "waning"  # ◑ Cooling down; completing or fading
    EMPTY = "empty"  # ◌ Error state or cleared; void

    @property
    def symbol(self) -> str:
        """Unicode moon phase symbol."""
        return {
            Phase.DORMANT: "○",
            Phase.WAKING: "◐",
            Phase.ACTIVE: "●",
            Phase.WANING: "◑",
            Phase.EMPTY: "◌",
        }[self]

    @property
    def description(self) -> str:
        """Human-readable phase description."""
        return {
            Phase.DORMANT: "sleeping",
            Phase.WAKING: "waking",
            Phase.ACTIVE: "active",
            Phase.WANING: "waning",
            Phase.EMPTY: "void",
        }[self]

    @classmethod
    def from_string(cls, s: str) -> Phase:
        """Parse phase from string (case-insensitive)."""
        s_lower = s.lower()
        for phase in cls:
            if phase.value == s_lower or phase.name.lower() == s_lower:
                return phase
        raise ValueError(f"Unknown phase: {s}")


class Scale(Enum):
    """
    Fractal zoom levels for visualization.

    The same visual grammar scales from one agent (glyph)
    to orchestrating multiple repositories (library).
    """

    GLYPH = "glyph"  # Single agent's phase: ● A
    CARD = "card"  # Glyph with context (metrics, time)
    PAGE = "page"  # Full view of a single agent (open book)
    GARDEN = "garden"  # Multiple agents in spatial relationship
    LIBRARY = "library"  # Multiple gardens (repos, instances)

    @property
    def depth(self) -> int:
        """Numeric depth for zoom operations."""
        return {
            Scale.GLYPH: 1,
            Scale.CARD: 2,
            Scale.PAGE: 3,
            Scale.GARDEN: 4,
            Scale.LIBRARY: 5,
        }[self]

    def zoom_in(self) -> Scale:
        """Go to more detailed scale (towards GLYPH)."""
        if self == Scale.GLYPH:
            return Scale.GLYPH
        depths = {s.depth: s for s in Scale}
        return depths.get(self.depth - 1, Scale.GLYPH)

    def zoom_out(self) -> Scale:
        """Go to broader scale (towards LIBRARY)."""
        if self == Scale.LIBRARY:
            return Scale.LIBRARY
        depths = {s.depth: s for s in Scale}
        return depths.get(self.depth + 1, Scale.LIBRARY)


class NoteSource(Enum):
    """Source of a margin note."""

    SYSTEM = "system"  # Automatic events (phase changes, errors)
    AI = "ai"  # LLM-generated reflections
    HUMAN = "human"  # User-added annotations
    WGENT = "w-gent"  # Exported from W-gent observation


@dataclass(frozen=True)
class MarginNote:
    """
    A timestamped observation that accumulates as agents run.

    Inspired by marginalia in old books, margin notes are the
    "living memory" of the garden.
    """

    timestamp: datetime
    source: NoteSource
    content: str
    agent_id: Optional[str] = None  # None means garden-wide note

    def render(self, show_agent: bool = False) -> str:
        """Render note in standard format: HH:MM:SS — [source] content"""
        time_str = self.timestamp.strftime("%H:%M:%S")
        source_str = f"[{self.source.value}]"
        agent_prefix = f"[{self.agent_id}] " if show_agent and self.agent_id else ""
        return f"{time_str} — {source_str} {agent_prefix}{self.content}"


@dataclass
class Glyph:
    """
    The atomic unit of visualization: a phase symbol + identity.

    From this seed, everything grows. One character for phase,
    one for identity.

    Example: ● A
    """

    agent_id: str
    phase: Phase

    def render(self) -> str:
        """Render glyph as: symbol + space + id"""
        return f"{self.phase.symbol} {self.agent_id}"

    def short(self) -> str:
        """Render compact form: symbol + first char of id"""
        return f"{self.phase.symbol}{self.agent_id[0].upper()}"


@dataclass
class AgentState:
    """
    Complete visualization state for a single agent.

    Contains everything needed to render at any scale.
    """

    agent_id: str
    phase: Phase
    birth_time: datetime
    current_time: datetime = field(default_factory=datetime.now)

    # Optional metadata
    epigraph: Optional[str] = None  # Agent's essence in one sentence
    joy: Optional[float] = None  # 0.0 - 1.0, principle alignment
    ethics: Optional[float] = None  # 0.0 - 1.0, principle alignment

    # Composition relationships
    composes_with: List[str] = field(default_factory=list)  # Outgoing edges
    composed_by: List[str] = field(default_factory=list)  # Incoming edges

    # History
    margin_notes: List[MarginNote] = field(default_factory=list)
    phase_history: List[tuple[datetime, Phase]] = field(default_factory=list)

    # Arbitrary metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def glyph(self) -> Glyph:
        """Create a Glyph from this state."""
        return Glyph(agent_id=self.agent_id, phase=self.phase)

    @property
    def elapsed(self) -> timedelta:
        """Time since agent birth."""
        return self.current_time - self.birth_time

    @property
    def elapsed_str(self) -> str:
        """Formatted elapsed time: HH:MM:SS"""
        total_seconds = int(self.elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def add_note(
        self,
        content: str,
        source: NoteSource = NoteSource.SYSTEM,
        timestamp: Optional[datetime] = None,
    ) -> MarginNote:
        """Add a margin note to this agent's history."""
        note = MarginNote(
            timestamp=timestamp or datetime.now(),
            source=source,
            content=content,
            agent_id=self.agent_id,
        )
        self.margin_notes.append(note)
        return note

    def transition_to(self, new_phase: Phase) -> None:
        """Record a phase transition."""
        now = datetime.now()
        self.phase_history.append((now, self.phase))
        self.phase = new_phase
        self.current_time = now
        self.add_note(
            f"phase transition: {self.phase_history[-1][1].value} → {new_phase.value}",
            NoteSource.SYSTEM,
            now,
        )


@dataclass
class GardenState:
    """
    Multiple agents in spatial relationship—the zen garden view.

    This is the "organism" level: agents positioned by relationship,
    not list order.
    """

    name: str
    session_start: datetime
    current_time: datetime = field(default_factory=datetime.now)

    # Agents in this garden
    agents: Dict[str, AgentState] = field(default_factory=dict)

    # Focus (currently selected agent)
    focus: Optional[str] = None

    # Garden-wide margin notes
    margin_notes: List[MarginNote] = field(default_factory=list)

    # Health metric (0.0 - 1.0)
    health: Optional[float] = None

    @property
    def elapsed(self) -> timedelta:
        """Time since session start."""
        return self.current_time - self.session_start

    @property
    def elapsed_str(self) -> str:
        """Formatted elapsed time: HH:MM:SS"""
        total_seconds = int(self.elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def add_agent(self, state: AgentState) -> None:
        """Add an agent to this garden."""
        self.agents[state.agent_id] = state

    def get_agent(self, agent_id: str) -> Optional[AgentState]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def set_focus(self, agent_id: Optional[str]) -> None:
        """Set the focused agent."""
        if agent_id is not None and agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not in garden")
        self.focus = agent_id

    def add_note(
        self,
        content: str,
        source: NoteSource = NoteSource.SYSTEM,
        timestamp: Optional[datetime] = None,
    ) -> MarginNote:
        """Add a garden-wide margin note."""
        note = MarginNote(
            timestamp=timestamp or datetime.now(),
            source=source,
            content=content,
            agent_id=None,  # Garden-wide
        )
        self.margin_notes.append(note)
        return note

    def glyph_summary(self) -> str:
        """Compact summary: ●A  ○B  ◐C"""
        parts = []
        for agent_id in sorted(self.agents.keys()):
            agent = self.agents[agent_id]
            parts.append(agent.glyph.short())
        return "  ".join(parts)


@dataclass
class LibraryState:
    """
    Multiple gardens (repos, instances, branches)—the ecosystem level.

    This is the "galaxy" view: orchestrating multiple repositories.
    """

    name: str
    system_start: datetime
    current_time: datetime = field(default_factory=datetime.now)

    # Gardens in this library
    gardens: Dict[str, GardenState] = field(default_factory=dict)

    # Focus (currently selected garden)
    focus: Optional[str] = None

    # Orchestration status
    orchestration_status: str = "converging"  # converging, stable, diverging

    @property
    def total_agents(self) -> int:
        """Total agents across all gardens."""
        return sum(len(g.agents) for g in self.gardens.values())

    def add_garden(self, garden: GardenState) -> None:
        """Add a garden to this library."""
        self.gardens[garden.name] = garden

    def get_garden(self, name: str) -> Optional[GardenState]:
        """Get a garden by name."""
        return self.gardens.get(name)
