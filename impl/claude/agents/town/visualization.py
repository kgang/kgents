"""
Agent Town Visualization Contracts (Phase 5 DEVELOP).

Defines contracts for:
1. EigenvectorScatterWidget - 7D eigenvector scatter plot
2. TownSSEEndpoint - SSE stream of town events
3. TownNATSBridge - NATS subject schema for town events

These contracts establish the interface; implementation follows in IMPLEMENT phase.

Design Principles:
- All widgets extend KgentsWidget[S] with project() for all RenderTargets
- SSE uses async generators yielding TownEvent.to_dict()
- NATS subjects follow: town.{town_id}.{phase}.{operation}
- Functor law: scatter.map(f) ≡ scatter.with_state(f(state))

Heritage:
- S1: KgentsWidget pattern (agents/i/reactive/widget.py)
- S2: MarimoAdapter pattern (agents/i/reactive/adapters/marimo_widget.py)
- S3: NATSBridge pattern (protocols/streaming/nats_bridge.py)
- S4: TownEvent schema (agents/town/flux.py)
- S5: Eigenvectors (agents/town/citizen.py)
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncIterator, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from agents.i.reactive.signal import Signal
    from agents.i.reactive.widget import KgentsWidget, RenderTarget
    from agents.town.citizen import Citizen, Eigenvectors
    from agents.town.flux import TownEvent, TownPhase

# Note: Coalition module archived 2025-12-21
# Type alias for forward compatibility
Coalition = Any

# =============================================================================
# Type Variables
# =============================================================================

S = TypeVar("S")  # State type


# =============================================================================
# 1. EigenvectorScatterWidget Contract
# =============================================================================


@dataclass(frozen=True)
class ScatterPoint:
    """
    A single point in the 7D eigenvector scatter plot.

    Represents a citizen's position in personality space.
    The 7D eigenvectors are projected to 2D for visualization.
    """

    citizen_id: str
    citizen_name: str
    archetype: str

    # 7D eigenvector coordinates
    warmth: float
    curiosity: float
    trust: float
    creativity: float
    patience: float
    resilience: float
    ambition: float

    # 2D projected coordinates (set by projection function)
    x: float = 0.0
    y: float = 0.0

    # Visual properties
    color: str = "#3b82f6"  # Default blue
    size: float = 1.0  # Relative size
    is_evolving: bool = False
    is_selected: bool = False

    # Coalition membership (for coloring)
    coalition_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON projection."""
        return {
            "citizen_id": self.citizen_id,
            "citizen_name": self.citizen_name,
            "archetype": self.archetype,
            "eigenvectors": {
                "warmth": self.warmth,
                "curiosity": self.curiosity,
                "trust": self.trust,
                "creativity": self.creativity,
                "patience": self.patience,
                "resilience": self.resilience,
                "ambition": self.ambition,
            },
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "size": self.size,
            "is_evolving": self.is_evolving,
            "is_selected": self.is_selected,
            "coalition_ids": list(self.coalition_ids),
        }


class ProjectionMethod(Enum):
    """
    Methods for projecting 7D eigenvectors to 2D.

    Each method provides a different view into personality space.
    """

    # Principal Component Analysis (preserves variance)
    PCA = auto()

    # t-SNE (preserves local structure)
    TSNE = auto()

    # Simple pair projection (warmth vs trust, etc.)
    PAIR_WT = auto()  # Warmth vs Trust
    PAIR_CC = auto()  # Curiosity vs Creativity
    PAIR_PR = auto()  # Patience vs Resilience
    PAIR_RA = auto()  # Resilience vs Ambition

    # Custom axis (user-defined linear combination)
    CUSTOM = auto()


@dataclass(frozen=True)
class ScatterState:
    """
    State for the eigenvector scatter widget.

    Immutable state that captures all information needed to render
    a scatter plot of citizens in eigenvector space.
    """

    # Points to display
    points: tuple[ScatterPoint, ...] = ()

    # Projection method
    projection: ProjectionMethod = ProjectionMethod.PAIR_WT

    # Selection state
    selected_citizen_id: str | None = None
    hovered_citizen_id: str | None = None

    # Filter state
    show_evolving_only: bool = False
    archetype_filter: tuple[str, ...] = ()  # Empty = show all
    coalition_filter: str | None = None  # Filter by coalition

    # Display options
    show_labels: bool = True
    show_coalition_colors: bool = True
    animate_transitions: bool = True

    # Timestamp for tracking changes
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON projection."""
        return {
            "type": "eigenvector_scatter",
            "points": [p.to_dict() for p in self.points],
            "projection": self.projection.name,
            "selected_citizen_id": self.selected_citizen_id,
            "hovered_citizen_id": self.hovered_citizen_id,
            "show_evolving_only": self.show_evolving_only,
            "archetype_filter": list(self.archetype_filter),
            "coalition_filter": self.coalition_filter,
            "show_labels": self.show_labels,
            "show_coalition_colors": self.show_coalition_colors,
            "animate_transitions": self.animate_transitions,
            "updated_at": self.updated_at.isoformat(),
        }


class EigenvectorScatterWidgetProtocol(Protocol):
    """
    Protocol for the eigenvector scatter widget.

    Implements KgentsWidget[ScatterState] with target-agnostic rendering.

    Functor Law:
        scatter.map(f) ≡ scatter.with_state(f(state))

    This ensures that transforming the widget via map() is equivalent
    to transforming its internal state directly.
    """

    @property
    def state(self) -> "Signal[ScatterState]":
        """The reactive state signal."""
        ...

    def project(self, target: "RenderTarget") -> Any:
        """
        Project to rendering target.

        CLI: ASCII scatter plot with legend
        TUI: Rich/Textual scatter with interactivity
        MARIMO: anywidget scatter (plotly or custom)
        JSON: ScatterState.to_dict()
        """
        ...

    def with_state(self, new_state: ScatterState) -> "EigenvectorScatterWidgetProtocol":
        """
        Create new widget with transformed state.

        This is the lens-like operation that enables functor laws.
        """
        ...

    def map(
        self, f: "Callable[[ScatterState], ScatterState]"
    ) -> "EigenvectorScatterWidgetProtocol":
        """
        Functor map: transform the widget via a state transformation.

        Law: scatter.map(f) ≡ scatter.with_state(f(scatter.state.value))
        """
        ...

    # --- State Mutations ---

    def select_citizen(self, citizen_id: str | None) -> None:
        """Select a citizen (highlights in visualization)."""
        ...

    def hover_citizen(self, citizen_id: str | None) -> None:
        """Set hovered citizen (for tooltips)."""
        ...

    def set_projection(self, method: ProjectionMethod) -> None:
        """Change the projection method."""
        ...

    def filter_by_archetype(self, archetypes: tuple[str, ...]) -> None:
        """Filter to show only specified archetypes."""
        ...

    def filter_by_coalition(self, coalition_id: str | None) -> None:
        """Filter to show only members of a coalition."""
        ...

    def toggle_evolving_only(self) -> None:
        """Toggle showing only evolving citizens."""
        ...

    # --- Data Loading ---

    def load_from_citizens(
        self,
        citizens: dict[str, "Citizen"],
        coalitions: dict[str, "Coalition"] | None = None,
        evolving_ids: set[str] | None = None,
    ) -> None:
        """
        Load scatter points from citizen data.

        Computes 2D projections and assigns colors based on coalitions.
        """
        ...


# Type alias for implementation
from typing import Callable

EigenvectorScatterWidget = EigenvectorScatterWidgetProtocol


# =============================================================================
# 2. TownSSEEndpoint Contract
# =============================================================================


@dataclass(frozen=True)
class SSEEvent:
    """
    A Server-Sent Event for town updates.

    Follows the SSE specification:
    - event: Event type name
    - data: JSON payload
    - id: Optional event ID for resumption
    - retry: Optional reconnection time (ms)
    """

    event: str
    data: dict[str, Any]
    id: str | None = None
    retry: int | None = None

    def to_sse(self) -> str:
        """Format as SSE wire format."""
        lines = []
        if self.event:
            lines.append(f"event: {self.event}")
        if self.id:
            lines.append(f"id: {self.id}")
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        # Data must be last, can be multiline (each line prefixed with "data: ")
        import json

        data_str = json.dumps(self.data)
        lines.append(f"data: {data_str}")
        lines.append("")  # Empty line terminates event
        return "\n".join(lines) + "\n"


class TownSSEEndpointProtocol(Protocol):
    """
    Protocol for the town SSE endpoint.

    Streams TownEvents to clients as Server-Sent Events.

    Subject Schema:
        event: town.{phase}.{operation}
        data: TownEvent.to_dict()

    Usage in FastAPI:
        @router.get("/{town_id}/events")
        async def stream_events(town_id: str) -> StreamingResponse:
            endpoint = TownSSEEndpoint(town_id)
            return StreamingResponse(
                endpoint.generate(),
                media_type="text/event-stream",
            )
    """

    @property
    def town_id(self) -> str:
        """The town being streamed."""
        ...

    async def generate(self) -> AsyncIterator[str]:
        """
        Generate SSE events.

        Yields SSE-formatted strings for each town event.

        Event types:
        - town.status: Status updates (phase changes, day changes)
        - town.event: TownEvent (greet, gossip, trade, solo)
        - town.coalition: Coalition changes (formed, dissolved)
        - town.eigenvector: Eigenvector drift events
        - town.nphase: N-Phase compressed cycle transitions

        Example output:
            event: town.event
            data: {"phase": "MORNING", "operation": "greet", ...}

            event: town.status
            data: {"day": 2, "phase": "AFTERNOON", "tension": 0.3}

        """
        ...

    async def push_event(self, event: "TownEvent") -> None:
        """
        Push a town event to all connected clients.

        Used by TownFlux to stream events as they occur.
        """
        ...

    async def push_status(self, status: dict[str, Any]) -> None:
        """Push a status update."""
        ...

    async def push_coalition_change(
        self,
        coalition: "Coalition",
        change_type: str,  # "formed" | "dissolved" | "reinforced"
    ) -> None:
        """Push a coalition change event."""
        ...

    async def push_eigenvector_drift(
        self,
        citizen_id: str,
        old_eigenvectors: dict[str, float],
        new_eigenvectors: dict[str, float],
        drift_magnitude: float,
    ) -> None:
        """Push an eigenvector drift event (for scatter animation)."""
        ...

    def close(self) -> None:
        """Close the SSE endpoint and cleanup."""
        ...


# =============================================================================
# 3. TownNATSBridge Contract
# =============================================================================


class TownEventType(Enum):
    """Types of events in the town NATS stream."""

    # Core events
    EVENT = "event"  # TownEvent (greet, gossip, trade, solo)
    STATUS = "status"  # Status update
    PHASE_CHANGE = "phase_change"  # Phase transition

    # Coalition events
    COALITION_FORMED = "coalition.formed"
    COALITION_DISSOLVED = "coalition.dissolved"
    COALITION_REINFORCED = "coalition.reinforced"

    # Eigenvector events
    EIGENVECTOR_DRIFT = "eigenvector.drift"

    # Citizen events
    CITIZEN_EVOLVED = "citizen.evolved"
    CITIZEN_RESTED = "citizen.rested"
    CITIZEN_WOKE = "citizen.woke"
    # N-Phase events
    NPHASE_TRANSITION = "nphase.transition"


@dataclass(frozen=True)
class TownNATSSubject:
    """
    NATS subject for town events.

    Schema: town.{town_id}.{phase}.{operation}

    Examples:
        town.abc123.morning.greet
        town.abc123.afternoon.trade
        town.abc123.status.phase_change
        town.abc123.coalition.formed

    Wildcards:
        town.abc123.>         - All events for a town
        town.abc123.morning.> - All morning events
        town.*.status.>       - Status events for all towns
    """

    town_id: str
    phase: str  # TownPhase.name.lower() or special like "status", "coalition"
    operation: str  # Operation name or event type

    def to_subject(self) -> str:
        """Format as NATS subject string."""
        return f"town.{self.town_id}.{self.phase}.{self.operation}"

    @classmethod
    def from_subject(cls, subject: str) -> "TownNATSSubject":
        """Parse from NATS subject string."""
        parts = subject.split(".")
        if len(parts) != 4 or parts[0] != "town":
            raise ValueError(f"Invalid town subject: {subject}")
        return cls(town_id=parts[1], phase=parts[2], operation=parts[3])

    @classmethod
    def for_town_event(cls, town_id: str, event: "TownEvent") -> "TownNATSSubject":
        """Create subject for a TownEvent."""
        return cls(
            town_id=town_id,
            phase=event.phase.name.lower(),
            operation=event.operation,
        )

    @classmethod
    def for_status(cls, town_id: str, status_type: str) -> "TownNATSSubject":
        """Create subject for a status event."""
        return cls(
            town_id=town_id,
            phase="status",
            operation=status_type,
        )

    @classmethod
    def for_coalition(cls, town_id: str, change_type: str) -> "TownNATSSubject":
        """Create subject for a coalition event."""
        return cls(
            town_id=town_id,
            phase="coalition",
            operation=change_type,
        )

    @classmethod
    def for_nphase_transition(cls, town_id: str) -> "TownNATSSubject":
        """Create subject for N-Phase transition events."""
        return cls(
            town_id=town_id,
            phase="nphase",
            operation="transition",
        )

    @classmethod
    def wildcard_town(cls, town_id: str) -> str:
        """Get wildcard for all events in a town."""
        return f"town.{town_id}.>"

    @classmethod
    def wildcard_all_towns(cls) -> str:
        """Get wildcard for all town events."""
        return "town.>"


class TownNATSBridgeProtocol(Protocol):
    """
    Protocol for the town NATS bridge.

    Extends NATSBridge with town-specific publishing and subscribing.

    Stream configuration:
        - Stream name: town-events
        - Subjects: town.>
        - Max age: 7 days
        - Max messages per subject: 10000

    Consumer patterns:
        - SSE consumers: Pull subscription per town
        - Metering: Batch consumer for billing
        - Scatter widget: Pull subscription for eigenvector drift
    """

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        ...

    # --- Publishing ---

    async def publish_town_event(
        self,
        town_id: str,
        event: "TownEvent",
    ) -> None:
        """
        Publish a TownEvent to NATS.

        Subject: town.{town_id}.{phase}.{operation}
        Payload: event.to_dict()
        """
        ...

    async def publish_status(
        self,
        town_id: str,
        status: dict[str, Any],
    ) -> None:
        """Publish a status update."""
        ...

    async def publish_coalition_change(
        self,
        town_id: str,
        coalition: "Coalition",
        change_type: str,
    ) -> None:
        """Publish a coalition change."""
        ...

    async def publish_eigenvector_drift(
        self,
        town_id: str,
        citizen_id: str,
        old_eigenvectors: "Eigenvectors",
        new_eigenvectors: "Eigenvectors",
    ) -> None:
        """Publish an eigenvector drift event."""
        ...

    async def publish_nphase_transition(
        self,
        town_id: str,
        citizen_id: str,
        ledger: dict[str, Any],
    ) -> None:
        """Publish compressed N-Phase transition (SENSE/ACT/REFLECT)."""
        ...

    # --- Subscribing ---

    async def subscribe_town(
        self,
        town_id: str,
        from_beginning: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribe to all events for a town.

        Args:
            town_id: Town to subscribe to
            from_beginning: Replay from stream start

        Yields:
            Event payloads as dictionaries
        """
        ...

    async def subscribe_events(
        self,
        town_id: str,
        event_types: tuple[TownEventType, ...] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribe to specific event types for a town.

        Args:
            town_id: Town to subscribe to
            event_types: Filter to these types (None = all)

        Yields:
            Event payloads as dictionaries
        """
        ...

    # --- Batch Operations ---

    async def consume_events_batch(
        self,
        town_id: str,
        batch_size: int = 100,
        timeout: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Consume a batch of events (for metering/processing).

        Args:
            town_id: Town to consume from
            batch_size: Maximum events to fetch
            timeout: Fetch timeout in seconds

        Returns:
            List of event payloads
        """
        ...


# =============================================================================
# 4. Functor Laws Specification
# =============================================================================

"""
Functor Laws for Town Visualization Components

The scatter widget satisfies functor laws, enabling compositional transformations:

LAW 1: Identity Preservation
    scatter.map(id) ≡ scatter

    Transforming by identity function leaves widget unchanged.

LAW 2: Composition Preservation
    scatter.map(f).map(g) ≡ scatter.map(g . f)

    Sequential maps can be fused into a single map.

LAW 3: State-Map Equivalence
    scatter.map(f) ≡ scatter.with_state(f(scatter.state.value))

    Map is implemented in terms of state transformation.

These laws enable:
- Safe composition of filters (archetype, coalition, evolving)
- Projection chaining (PCA then highlight selection)
- Undo/redo via state history

Example:
    # Compose filters
    filter_arch = lambda s: s._replace(archetype_filter=("builder",))
    filter_evolving = lambda s: s._replace(show_evolving_only=True)

    # By LAW 2, these are equivalent:
    widget.map(filter_arch).map(filter_evolving)
    widget.map(lambda s: filter_evolving(filter_arch(s)))

    # By LAW 3, these are equivalent:
    widget.map(filter_arch)
    widget.with_state(filter_arch(widget.state.value))
"""


# =============================================================================
# 5. ASCII Projection Contract (for CLI target)
# =============================================================================


def project_scatter_to_ascii(
    state: ScatterState,
    width: int = 60,
    height: int = 20,
) -> str:
    """
    Project scatter state to ASCII art.

    Implementation for CLI rendering of eigenvector scatter.

    Layout:
        +------------------------------------------------------------+
        |                    Eigenvector Space (WT)                  |
        |                                                            |
        |         B                                                  |
        |     b       T                                              |
        |         H                                                  |
        |   E             S                                          |
        |                         W                                  |
        |                                                            |
        +------------------------------------------------------------+
        Legend: B=Builder T=Trader H=Healer S=Sage E=Explorer W=Witness

    Characters:
        - UPPER: Selected or hovered citizen
        - lower: Regular citizen
        - Special: ★ for K-gent projection, ● for bridge nodes

    Args:
        state: The scatter state to render
        width: ASCII grid width
        height: ASCII grid height

    Returns:
        ASCII art string
    """
    # Get axis labels based on projection
    axis_labels = _get_axis_labels(state.projection)

    # Create the grid
    grid: list[list[str]] = [[" " for _ in range(width)] for _ in range(height)]

    # Track legend entries
    legend_entries: dict[str, str] = {}

    # Project each point onto the 2D grid
    for point in state.points:
        # Apply filters
        if state.show_evolving_only and not point.is_evolving:
            continue
        if state.archetype_filter and point.archetype not in state.archetype_filter:
            continue
        if state.coalition_filter and state.coalition_filter not in point.coalition_ids:
            continue

        # Get 2D coordinates based on projection method
        x_val, y_val = _project_point_2d(point, state.projection)

        # Map to grid coordinates (0-1 range maps to grid)
        grid_x = int(x_val * (width - 3)) + 1
        grid_y = int((1 - y_val) * (height - 3)) + 1  # Invert Y for display

        # Clamp to grid bounds
        grid_x = max(1, min(width - 2, grid_x))
        grid_y = max(1, min(height - 2, grid_y))

        # Determine character
        char = _get_point_char(
            point,
            is_selected=point.citizen_id == state.selected_citizen_id,
            is_hovered=point.citizen_id == state.hovered_citizen_id,
        )

        # Place on grid (don't overwrite selected/hovered)
        if grid[grid_y][grid_x] == " " or (
            point.citizen_id == state.selected_citizen_id
            or point.citizen_id == state.hovered_citizen_id
        ):
            grid[grid_y][grid_x] = char

        # Track for legend
        legend_entries[char.upper()] = point.archetype.capitalize()[:7]

    # Build the output
    lines: list[str] = []

    # Title line
    title = f"Eigenvector Space ({axis_labels[0][0]}{axis_labels[1][0]})"
    border = "+" + "-" * (width - 2) + "+"
    lines.append(border)
    lines.append("|" + title.center(width - 2) + "|")

    # Grid lines
    for row in grid:
        lines.append("|" + "".join(row) + "|")

    # Bottom border
    lines.append(border)

    # Axis labels
    x_label = f"X: {axis_labels[0]}"
    y_label = f"Y: {axis_labels[1]}"
    lines.append(f"{x_label}  |  {y_label}")

    # Legend (compact)
    if legend_entries:
        legend_parts = [f"{k}={v}" for k, v in sorted(legend_entries.items())[:8]]
        legend_line = "Legend: " + " ".join(legend_parts)
        lines.append(legend_line)

    # Stats line
    visible_count = sum(
        1
        for p in state.points
        if (not state.show_evolving_only or p.is_evolving)
        and (not state.archetype_filter or p.archetype in state.archetype_filter)
        and (not state.coalition_filter or state.coalition_filter in p.coalition_ids)
    )
    stats = f"Citizens: {visible_count}/{len(state.points)}"
    if state.selected_citizen_id:
        stats += f" | Selected: {state.selected_citizen_id[:8]}"
    lines.append(stats)

    return "\n".join(lines)


def _get_axis_labels(projection: ProjectionMethod) -> tuple[str, str]:
    """Get axis labels for a projection method."""
    match projection:
        case ProjectionMethod.PAIR_WT:
            return ("Warmth", "Trust")
        case ProjectionMethod.PAIR_CC:
            return ("Curiosity", "Creativity")
        case ProjectionMethod.PAIR_PR:
            return ("Patience", "Resilience")
        case ProjectionMethod.PAIR_RA:
            return ("Resilience", "Ambition")
        case ProjectionMethod.PCA:
            return ("PC1", "PC2")
        case ProjectionMethod.TSNE:
            return ("t-SNE1", "t-SNE2")
        case ProjectionMethod.CUSTOM:
            return ("Custom1", "Custom2")
        case _:
            return ("X", "Y")


def _project_point_2d(point: ScatterPoint, projection: ProjectionMethod) -> tuple[float, float]:
    """
    Project a point to 2D coordinates.

    For simple pair projections, use the corresponding eigenvector values.
    For PCA/t-SNE, use pre-computed x, y if available.
    """
    match projection:
        case ProjectionMethod.PAIR_WT:
            return (point.warmth, point.trust)
        case ProjectionMethod.PAIR_CC:
            return (point.curiosity, point.creativity)
        case ProjectionMethod.PAIR_PR:
            return (point.patience, point.resilience)
        case ProjectionMethod.PAIR_RA:
            return (point.resilience, point.ambition)
        case ProjectionMethod.PCA | ProjectionMethod.TSNE | ProjectionMethod.CUSTOM:
            # Use pre-computed coordinates (normalized to 0-1)
            # If not pre-computed, fall back to warmth/trust
            if point.x == 0.0 and point.y == 0.0:
                return (point.warmth, point.trust)
            # Normalize from typical PCA/t-SNE range to 0-1
            # Assume coordinates are in [-2, 2] range
            x_norm = (point.x + 2) / 4
            y_norm = (point.y + 2) / 4
            return (max(0, min(1, x_norm)), max(0, min(1, y_norm)))
        case _:
            return (point.warmth, point.trust)


def _get_point_char(
    point: ScatterPoint,
    is_selected: bool = False,
    is_hovered: bool = False,
) -> str:
    """
    Get the character to display for a point.

    Uses first letter of archetype.
    UPPER for selected/hovered, lower for regular.
    Special characters for bridge nodes and K-gent.
    """
    # Bridge node (multiple coalitions)
    if len(point.coalition_ids) > 1:
        return "●" if is_selected or is_hovered else "○"

    # K-gent (special marker)
    if point.archetype.lower() == "kgent":
        return "★" if is_selected or is_hovered else "☆"

    # Evolving citizens get emphasis
    if point.is_evolving:
        char = point.archetype[0].upper() if point.archetype else "?"
        return char if is_selected or is_hovered else char.lower()

    # Regular citizens
    char = point.archetype[0].upper() if point.archetype else "·"
    if is_selected or is_hovered:
        return char.upper()
    return char.lower()


# =============================================================================
# 6. Concrete Implementations (Phase 5 IMPLEMENT)
# =============================================================================


class EigenvectorScatterWidgetImpl:
    """
    Concrete implementation of EigenvectorScatterWidget.

    Wraps a Signal[ScatterState] and provides target-agnostic projection.

    Satisfies functor laws:
    - LAW 1: map(id) = id
    - LAW 2: map(f).map(g) = map(g . f)
    - LAW 3: map(f) = with_state(f(state.value))
    """

    def __init__(self, initial_state: ScatterState | None = None) -> None:
        """Initialize with optional initial state."""
        from agents.i.reactive.signal import Signal

        self._signal: Signal[ScatterState] = Signal.of(initial_state or ScatterState())

    @property
    def state(self) -> "Signal[ScatterState]":
        """The reactive state signal."""
        from agents.i.reactive.signal import Signal

        return self._signal

    def project(self, target: "RenderTarget") -> Any:
        """
        Project to rendering target.

        CLI: ASCII scatter plot with legend
        TUI: Rich/Textual scatter (placeholder)
        MARIMO: anywidget scatter (placeholder)
        JSON: ScatterState.to_dict()
        """
        from agents.i.reactive.widget import RenderTarget

        state = self._signal.value
        match target:
            case RenderTarget.CLI:
                return project_scatter_to_ascii(state)
            case RenderTarget.JSON:
                return state.to_dict()
            case RenderTarget.TUI:
                # Placeholder - would return rich.text.Text or textual widget
                return project_scatter_to_ascii(state)
            case RenderTarget.MARIMO:
                # Placeholder - would return anywidget
                return state.to_dict()
            case _:
                return state.to_dict()

    def with_state(self, new_state: ScatterState) -> "EigenvectorScatterWidgetImpl":
        """Create new widget with transformed state (functor law)."""
        return EigenvectorScatterWidgetImpl(initial_state=new_state)

    def map(self, f: "Callable[[ScatterState], ScatterState]") -> "EigenvectorScatterWidgetImpl":
        """
        Functor map: transform the widget via a state transformation.

        Law: scatter.map(f) ≡ scatter.with_state(f(scatter.state.value))
        """
        return self.with_state(f(self._signal.value))

    # --- State Mutations ---

    def select_citizen(self, citizen_id: str | None) -> None:
        """Select a citizen (highlights in visualization)."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    def hover_citizen(self, citizen_id: str | None) -> None:
        """Set hovered citizen (for tooltips)."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    def set_projection(self, method: ProjectionMethod) -> None:
        """Change the projection method."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=method,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    def filter_by_archetype(self, archetypes: tuple[str, ...]) -> None:
        """Filter to show only specified archetypes."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=archetypes,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    def filter_by_coalition(self, coalition_id: str | None) -> None:
        """Filter to show only members of a coalition."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=coalition_id,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    def toggle_evolving_only(self) -> None:
        """Toggle showing only evolving citizens."""
        self._signal.update(
            lambda s: ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=not s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )

    # --- Data Loading ---

    def load_from_citizens(
        self,
        citizens: dict[str, "Citizen"],
        coalitions: dict[str, "Coalition"] | None = None,
        evolving_ids: set[str] | None = None,
    ) -> None:
        """
        Load scatter points from citizen data.

        Computes 2D projections and assigns colors based on coalitions.
        """
        points: list[ScatterPoint] = []
        coalition_colors = _generate_coalition_colors(coalitions or {})
        evolving = evolving_ids or set()

        for citizen_id, citizen in citizens.items():
            ev = citizen.eigenvectors
            coal_ids = _get_citizen_coalitions(citizen_id, coalitions or {})
            color = _get_color_for_citizen(citizen_id, coal_ids, coalition_colors)

            point = ScatterPoint(
                citizen_id=citizen_id,
                citizen_name=citizen.name,
                archetype=citizen.archetype,
                warmth=ev.warmth,
                curiosity=ev.curiosity,
                trust=ev.trust,
                creativity=ev.creativity,
                patience=ev.patience,
                resilience=ev.resilience,
                ambition=ev.ambition,
                color=color,
                is_evolving=citizen_id in evolving,
                coalition_ids=tuple(coal_ids),
            )
            points.append(point)

        self._signal.update(
            lambda s: ScatterState(
                points=tuple(points),
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )
        )


def _generate_coalition_colors(coalitions: dict[str, "Coalition"]) -> dict[str, str]:
    """Generate distinct colors for each coalition."""
    colors = [
        "#3b82f6",  # blue
        "#ef4444",  # red
        "#22c55e",  # green
        "#f59e0b",  # amber
        "#8b5cf6",  # purple
        "#ec4899",  # pink
        "#06b6d4",  # cyan
        "#f97316",  # orange
    ]
    return {coal_id: colors[i % len(colors)] for i, coal_id in enumerate(coalitions.keys())}


def _get_citizen_coalitions(citizen_id: str, coalitions: dict[str, "Coalition"]) -> list[str]:
    """Get all coalition IDs that a citizen belongs to."""
    result = []
    for coal_id, coal in coalitions.items():
        if hasattr(coal, "members") and citizen_id in coal.members:
            result.append(coal_id)
    return result


def _get_color_for_citizen(
    citizen_id: str, coal_ids: list[str], coalition_colors: dict[str, str]
) -> str:
    """Get color for a citizen based on coalition membership."""
    if len(coal_ids) > 1:
        return "#fbbf24"  # gold for bridge nodes
    elif len(coal_ids) == 1:
        return coalition_colors.get(coal_ids[0], "#3b82f6")
    return "#6b7280"  # gray for unaffiliated


# =============================================================================
# 7. TownSSEEndpoint Implementation
# =============================================================================


class TownSSEEndpoint:
    """
    Concrete implementation of the town SSE endpoint.

    Streams TownEvents to clients as Server-Sent Events.
    Uses an asyncio.Queue for in-memory event buffering.

    Usage in FastAPI:
        @router.get("/{town_id}/events")
        async def stream_events(town_id: str) -> StreamingResponse:
            endpoint = TownSSEEndpoint(town_id)
            return StreamingResponse(
                endpoint.generate(),
                media_type="text/event-stream",
            )
    """

    def __init__(self, town_id: str, max_queue_size: int = 1000) -> None:
        """Initialize SSE endpoint for a town."""
        import asyncio

        self._town_id = town_id
        self._queue: asyncio.Queue[SSEEvent | None] = asyncio.Queue(maxsize=max_queue_size)
        self._closed = False

    @property
    def town_id(self) -> str:
        """The town being streamed."""
        return self._town_id

    async def generate(self) -> AsyncIterator[str]:
        """
        Generate SSE events.

        Yields SSE-formatted strings for each town event.
        Runs until close() is called.
        """
        while not self._closed:
            try:
                import asyncio

                event = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                if event is None:
                    # Shutdown signal
                    break
                yield event.to_sse()
            except Exception:
                # Timeout - send keepalive
                yield ": keepalive\n\n"

    async def push_event(self, event: "TownEvent") -> None:
        """Push a town event to all connected clients."""
        sse = SSEEvent(
            event=f"town.{event.phase.name.lower()}.{event.operation}",
            data=event.to_dict(),
        )
        await self._queue.put(sse)

    async def push_status(self, status: dict[str, Any]) -> None:
        """Push a status update."""
        sse = SSEEvent(event="town.status", data=status)
        await self._queue.put(sse)

    async def push_coalition_change(
        self,
        coalition: "Coalition",
        change_type: str,
    ) -> None:
        """Push a coalition change event."""
        data = {
            "coalition_id": getattr(coalition, "id", str(coalition)),
            "change_type": change_type,
            "members": list(getattr(coalition, "members", [])),
        }
        sse = SSEEvent(event=f"town.coalition.{change_type}", data=data)
        await self._queue.put(sse)

    async def push_eigenvector_drift(
        self,
        citizen_id: str,
        old_eigenvectors: dict[str, float],
        new_eigenvectors: dict[str, float],
        drift_magnitude: float,
    ) -> None:
        """Push an eigenvector drift event (for scatter animation)."""
        data = {
            "citizen_id": citizen_id,
            "old": old_eigenvectors,
            "new": new_eigenvectors,
            "drift": drift_magnitude,
        }
        sse = SSEEvent(event="town.eigenvector.drift", data=data)
        await self._queue.put(sse)

    async def push_nphase_transition(
        self,
        citizen_id: str,
        ledger: dict[str, Any],
    ) -> None:
        """Push an N-Phase transition event (compressed SENSE/ACT/REFLECT)."""
        data = {"citizen_id": citizen_id, **ledger}
        sse = SSEEvent(event="town.nphase.transition", data=data)
        await self._queue.put(sse)

    def close(self) -> None:
        """Close the SSE endpoint and cleanup."""
        self._closed = True
        # Send shutdown signal
        import asyncio

        try:
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass


# =============================================================================
# 8. TownNATSBridge Implementation
# =============================================================================


class TownNATSBridge:
    """
    Concrete implementation of the town NATS bridge.

    Bridges TownEvents to NATS JetStream for distributed consumption.
    Falls back to in-memory queues when NATS is unavailable.

    Stream configuration:
        - Stream name: town-events
        - Subjects: town.>
        - Max age: 7 days
        - Max messages per subject: 10000
    """

    STREAM_NAME = "town-events"
    MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days
    MAX_MSGS_PER_SUBJECT = 10000

    def __init__(
        self,
        servers: list[str] | None = None,
        fallback_to_memory: bool = True,
    ) -> None:
        """
        Initialize NATS bridge.

        Args:
            servers: NATS server URLs (default: nats://localhost:4222)
            fallback_to_memory: Use in-memory fallback if NATS unavailable
        """
        import asyncio

        self._servers = servers or ["nats://localhost:4222"]
        self._fallback_to_memory = fallback_to_memory
        self._nc: Any = None  # nats.aio.client.Client
        self._js: Any = None  # nats.js.JetStreamContext
        self._connected = False

        # In-memory fallback: dict of town_id -> asyncio.Queue
        self._memory_queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._connected and self._nc is not None

    async def connect(self) -> None:
        """Connect to NATS and setup JetStream."""
        try:
            import nats
            from nats.js.api import StreamConfig

            self._nc = await nats.connect(servers=self._servers)
            self._js = self._nc.jetstream()

            # Create or update stream
            try:
                await self._js.add_stream(
                    config=StreamConfig(
                        name=self.STREAM_NAME,
                        subjects=["town.>"],
                        max_age=self.MAX_AGE_SECONDS * 1_000_000_000,  # nanoseconds
                        max_msgs_per_subject=self.MAX_MSGS_PER_SUBJECT,
                    )
                )
            except Exception as e:
                # Stream may already exist
                if "already" not in str(e).lower():
                    raise

            self._connected = True

        except ImportError:
            if self._fallback_to_memory:
                self._connected = False
            else:
                raise ImportError("nats-py required for NATS bridge")

        except Exception:
            if self._fallback_to_memory:
                self._connected = False
            else:
                raise

    async def close(self) -> None:
        """Close NATS connection."""
        if self._nc:
            await self._nc.close()
            self._nc = None
            self._js = None
        self._connected = False

    async def __aenter__(self) -> "TownNATSBridge":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    # --- Publishing ---

    async def publish_town_event(
        self,
        town_id: str,
        event: "TownEvent",
    ) -> None:
        """Publish a TownEvent."""
        subject = TownNATSSubject.for_town_event(town_id, event)
        await self._publish(subject.to_subject(), event.to_dict())

    async def publish_status(
        self,
        town_id: str,
        status: dict[str, Any],
    ) -> None:
        """Publish a status update."""
        subject = TownNATSSubject.for_status(town_id, "update")
        await self._publish(subject.to_subject(), status)

    async def publish_coalition_change(
        self,
        town_id: str,
        coalition: "Coalition",
        change_type: str,
    ) -> None:
        """Publish a coalition change."""
        subject = TownNATSSubject.for_coalition(town_id, change_type)
        data = {
            "coalition_id": getattr(coalition, "id", str(coalition)),
            "change_type": change_type,
            "members": list(getattr(coalition, "members", [])),
        }
        await self._publish(subject.to_subject(), data)

    async def publish_eigenvector_drift(
        self,
        town_id: str,
        citizen_id: str,
        old_eigenvectors: dict[str, float],
        new_eigenvectors: dict[str, float],
    ) -> None:
        """Publish an eigenvector drift event."""
        subject = f"town.{town_id}.eigenvector.drift"
        data = {
            "citizen_id": citizen_id,
            "old": old_eigenvectors,
            "new": new_eigenvectors,
            "drift": _compute_drift_magnitude(old_eigenvectors, new_eigenvectors),
        }
        await self._publish(subject, data)

    async def publish_nphase_transition(
        self,
        town_id: str,
        citizen_id: str,
        ledger: dict[str, Any],
    ) -> None:
        """Publish compressed N-Phase transition event."""
        subject = TownNATSSubject.for_nphase_transition(town_id).to_subject()
        data = {"citizen_id": citizen_id, **ledger}
        await self._publish(subject, data)

    async def _publish(self, subject: str, data: dict[str, Any]) -> None:
        """Internal publish with fallback."""
        import json

        if self.is_connected and self._js:
            # Publish to JetStream
            await self._js.publish(
                subject,
                json.dumps(data).encode(),
            )
        elif self._fallback_to_memory:
            # Fallback: publish to in-memory queue
            # Extract town_id from subject
            parts = subject.split(".")
            if len(parts) >= 2:
                town_id = parts[1]
                if town_id not in self._memory_queues:
                    import asyncio

                    self._memory_queues[town_id] = asyncio.Queue(maxsize=1000)
                try:
                    self._memory_queues[town_id].put_nowait({"subject": subject, "data": data})
                except Exception:
                    pass  # Queue full, drop message

    # --- Subscribing ---

    async def subscribe_town(
        self,
        town_id: str,
        from_beginning: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """Subscribe to all events for a town."""
        if self.is_connected and self._js:
            # JetStream subscription
            wildcard = TownNATSSubject.wildcard_town(town_id)
            async for msg in self._subscribe_jetstream(wildcard, from_beginning):
                yield msg
        elif self._fallback_to_memory:
            # Memory fallback
            async for msg in self._subscribe_memory(town_id):
                yield msg

    async def _subscribe_jetstream(
        self,
        subject: str,
        from_beginning: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """Subscribe via JetStream."""
        import json

        from nats.js.api import ConsumerConfig, DeliverPolicy

        deliver_policy = DeliverPolicy.ALL if from_beginning else DeliverPolicy.NEW

        psub = await self._js.pull_subscribe(
            subject,
            config=ConsumerConfig(
                deliver_policy=deliver_policy,
                ack_wait=30,  # 30 second ack window
            ),
        )

        while True:
            try:
                msgs = await psub.fetch(batch=10, timeout=30)
                for msg in msgs:
                    await msg.ack()
                    yield json.loads(msg.data.decode())
            except Exception:
                # Timeout or connection issue
                import asyncio

                await asyncio.sleep(0.1)

    async def _subscribe_memory(
        self,
        town_id: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """Subscribe via in-memory queue."""
        import asyncio

        if town_id not in self._memory_queues:
            self._memory_queues[town_id] = asyncio.Queue(maxsize=1000)

        queue = self._memory_queues[town_id]
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield msg["data"]
            except asyncio.TimeoutError:
                # Send keepalive indicator
                yield {"type": "keepalive"}


def _compute_drift_magnitude(
    old: dict[str, float],
    new: dict[str, float],
) -> float:
    """Compute Euclidean distance between eigenvector states."""
    import math

    total = 0.0
    for key in old:
        if key in new:
            diff = old[key] - new[key]
            total += diff * diff
    return math.sqrt(total)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Scatter Widget
    "ScatterPoint",
    "ScatterState",
    "ProjectionMethod",
    "EigenvectorScatterWidgetProtocol",
    "EigenvectorScatterWidget",
    "EigenvectorScatterWidgetImpl",
    # SSE Endpoint
    "SSEEvent",
    "TownSSEEndpointProtocol",
    "TownSSEEndpoint",
    # NATS Bridge
    "TownEventType",
    "TownNATSSubject",
    "TownNATSBridgeProtocol",
    "TownNATSBridge",
    # ASCII
    "project_scatter_to_ascii",
]
