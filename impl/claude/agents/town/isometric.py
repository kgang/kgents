"""
Isometric Visualization Contracts for Micro-Experience Factory.

This module defines contracts for the isometric "factory" visualization
that renders Agent Town as a pixelated foundry where pipelines self-attach.

Design Philosophy:
- Thin skin over existing substrate: Uses KgentsWidget, ScatterState, TownFlux
- SVG isometric projection via CSS transforms (not full 3D library)
- Functor law: isometric.map(f) ≡ isometric.with_state(f(state))

Heritage:
- S1: KgentsWidget pattern (agents/i/reactive/widget.py)
- S2: ScatterState (agents/town/visualization.py)
- S3: TownFlux events (agents/town/flux.py)
- S4: CSS isometric transforms (internet inspiration)

Crown Jewel: plans/micro-experience-factory.md
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar

if TYPE_CHECKING:
    from agents.i.reactive.signal import Signal
    from agents.i.reactive.widget import KgentsWidget, RenderTarget
    from agents.town.citizen import Citizen
    from agents.town.flux import TownEvent
    from agents.town.visualization import ScatterPoint, ScatterState

# =============================================================================
# Type Variables
# =============================================================================

S = TypeVar("S")


# =============================================================================
# Isometric Grid Configuration
# =============================================================================


class IsometricStyle(Enum):
    """Visual styles for the isometric grid."""

    PIXEL = auto()  # Chunky pixel art (default)
    VOXEL = auto()  # 3D cube-like
    FLAT = auto()  # Flat 2D with shadows
    NEON = auto()  # Cyberpunk glow


@dataclass(frozen=True)
class IsometricConfig:
    """
    Configuration for isometric rendering.

    Controls the visual appearance of the factory grid.
    """

    # Grid dimensions
    grid_width: int = 20  # Cells wide
    grid_height: int = 20  # Cells tall
    cell_size: int = 24  # Pixels per cell

    # Isometric transform angles
    rotation_x: float = 60.0  # degrees
    rotation_z: float = -45.0  # degrees

    # Visual style
    style: IsometricStyle = IsometricStyle.PIXEL

    # Colors (CSS format)
    background_color: str = "#1a1a2e"
    grid_color: str = "#16213e"
    highlight_color: str = "#e94560"
    citizen_color: str = "#0f3460"

    # Animation
    enable_animations: bool = True
    animation_duration_ms: int = 200

    def to_css_transform(self) -> str:
        """Generate CSS transform for isometric projection."""
        return f"rotateX({self.rotation_x}deg) rotateZ({self.rotation_z}deg)"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "cell_size": self.cell_size,
            "rotation_x": self.rotation_x,
            "rotation_z": self.rotation_z,
            "style": self.style.name,
            "background_color": self.background_color,
            "grid_color": self.grid_color,
            "highlight_color": self.highlight_color,
            "citizen_color": self.citizen_color,
            "enable_animations": self.enable_animations,
            "animation_duration_ms": self.animation_duration_ms,
            "css_transform": self.to_css_transform(),
        }


# =============================================================================
# Isometric Cell (Grid Position)
# =============================================================================


@dataclass(frozen=True)
class IsometricCell:
    """
    A single cell in the isometric grid.

    Each cell can contain:
    - A citizen (from ScatterPoint)
    - A pipeline segment (from trace)
    - A slot (for operad composition)
    - Nothing (empty cell)
    """

    # Grid coordinates (not screen coordinates)
    grid_x: int
    grid_y: int

    # Content type
    content_type: str = "empty"  # "citizen" | "pipeline" | "slot" | "empty"

    # Content data (depends on type)
    citizen_id: str | None = None
    pipeline_segment_id: str | None = None
    slot_id: str | None = None

    # Visual properties
    color: str = "#333333"
    glyph: str = "·"  # Unicode character for cell
    is_highlighted: bool = False
    is_selected: bool = False

    # Animation state
    animation_phase: float = 0.0  # 0.0 to 1.0 for tweening

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "content_type": self.content_type,
            "citizen_id": self.citizen_id,
            "pipeline_segment_id": self.pipeline_segment_id,
            "slot_id": self.slot_id,
            "color": self.color,
            "glyph": self.glyph,
            "is_highlighted": self.is_highlighted,
            "is_selected": self.is_selected,
            "animation_phase": self.animation_phase,
        }


# =============================================================================
# Isometric State (Full Grid State)
# =============================================================================


@dataclass(frozen=True)
class IsometricState:
    """
    State for the isometric factory visualization.

    Immutable state that captures all information needed to render
    the factory grid with citizens, pipelines, and slots.
    """

    # Grid configuration
    config: IsometricConfig = field(default_factory=IsometricConfig)

    # Grid cells (positioned content)
    cells: tuple[IsometricCell, ...] = ()

    # Citizens from ScatterState (projected onto grid)
    citizens: tuple["ScatterPoint", ...] = ()

    # Active pipelines (trace segments)
    active_pipelines: tuple[str, ...] = ()  # Pipeline IDs

    # Open slots (for operad composition)
    open_slots: tuple[str, ...] = ()  # Slot IDs

    # Selection state
    selected_cell: tuple[int, int] | None = None  # (grid_x, grid_y)
    hovered_cell: tuple[int, int] | None = None

    # Time state (for replay scrubber)
    current_tick: int = 0
    max_tick: int = 0

    # Entropy / slop state
    slop_bloom_active: bool = False
    entropy_level: float = 0.0

    # Timestamp
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON projection."""
        return {
            "type": "isometric_factory",
            "config": self.config.to_dict(),
            "cells": [c.to_dict() for c in self.cells],
            "citizens": [c.to_dict() for c in self.citizens] if self.citizens else [],
            "active_pipelines": list(self.active_pipelines),
            "open_slots": list(self.open_slots),
            "selected_cell": self.selected_cell,
            "hovered_cell": self.hovered_cell,
            "current_tick": self.current_tick,
            "max_tick": self.max_tick,
            "slop_bloom_active": self.slop_bloom_active,
            "entropy_level": self.entropy_level,
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# Isometric Widget Protocol
# =============================================================================


class IsometricWidgetProtocol(Protocol):
    """
    Protocol for the isometric factory widget.

    Implements KgentsWidget[IsometricState] with target-agnostic rendering.

    Functor Law:
        isometric.map(f) ≡ isometric.with_state(f(state))
    """

    @property
    def state(self) -> "Signal[IsometricState]":
        """The reactive state signal."""
        ...

    def project(self, target: "RenderTarget") -> Any:
        """
        Project to rendering target.

        CLI: ASCII isometric grid with glyphs
        TUI: Rich/Textual grid with borders and colors
        MARIMO: anywidget SVG isometric view
        JSON: IsometricState.to_dict()
        """
        ...

    def with_state(self, new_state: IsometricState) -> "IsometricWidgetProtocol":
        """Create new widget with transformed state."""
        ...

    def map(self, f: Callable[[IsometricState], IsometricState]) -> "IsometricWidgetProtocol":
        """
        Functor map: transform the widget via a state transformation.

        Law: isometric.map(f) ≡ isometric.with_state(f(isometric.state.value))
        """
        ...

    # --- State Mutations ---

    def select_cell(self, grid_x: int, grid_y: int) -> None:
        """Select a cell (highlights in visualization)."""
        ...

    def hover_cell(self, grid_x: int, grid_y: int) -> None:
        """Set hovered cell (for tooltips)."""
        ...

    def set_tick(self, tick: int) -> None:
        """Set current tick for replay scrubber."""
        ...

    def toggle_slop_bloom(self) -> None:
        """Toggle the Accursed Share slop bloom mode."""
        ...

    # --- Integration ---

    def update_from_scatter(self, scatter_state: "ScatterState") -> None:
        """Update citizens from scatter widget state."""
        ...

    def update_from_event(self, event: "TownEvent") -> None:
        """Update from a town event (add pipeline segment, etc.)."""
        ...


# =============================================================================
# Perturbation Pad Contract
# =============================================================================


@dataclass(frozen=True)
class PerturbationPad:
    """
    A HITL perturbation pad that triggers TownFlux operations.

    Pads are DJ-style controls that inject events into the flux
    without bypassing state (respects Perturbation Principle).
    """

    pad_id: str
    operation: str  # "greet" | "gossip" | "trade" | "solo"
    label: str
    color: str = "#3b82f6"
    hotkey: str | None = None  # Keyboard shortcut

    # Metabolics display
    token_cost: int = 100
    drama_potential: float = 0.1

    # Cooldown state
    cooldown_remaining_ms: int = 0
    is_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "pad_id": self.pad_id,
            "operation": self.operation,
            "label": self.label,
            "color": self.color,
            "hotkey": self.hotkey,
            "token_cost": self.token_cost,
            "drama_potential": self.drama_potential,
            "cooldown_remaining_ms": self.cooldown_remaining_ms,
            "is_enabled": self.is_enabled,
        }


@dataclass(frozen=True)
class PerturbationPadState:
    """State for the perturbation pad grid."""

    pads: tuple[PerturbationPad, ...] = ()
    selected_pad_id: str | None = None
    global_cooldown_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "perturbation_pads",
            "pads": [p.to_dict() for p in self.pads],
            "selected_pad_id": self.selected_pad_id,
            "global_cooldown_ms": self.global_cooldown_ms,
        }


# =============================================================================
# Default Pads
# =============================================================================


DEFAULT_PERTURBATION_PADS: tuple[PerturbationPad, ...] = (
    PerturbationPad(
        pad_id="greet",
        operation="greet",
        label="Greet",
        color="#22c55e",
        hotkey="g",
        token_cost=50,
        drama_potential=0.05,
    ),
    PerturbationPad(
        pad_id="gossip",
        operation="gossip",
        label="Gossip",
        color="#eab308",
        hotkey="s",
        token_cost=150,
        drama_potential=0.3,
    ),
    PerturbationPad(
        pad_id="trade",
        operation="trade",
        label="Trade",
        color="#3b82f6",
        hotkey="t",
        token_cost=200,
        drama_potential=0.15,
    ),
    PerturbationPad(
        pad_id="solo",
        operation="solo",
        label="Solo",
        color="#8b5cf6",
        hotkey="o",
        token_cost=75,
        drama_potential=0.02,
    ),
)


# =============================================================================
# ScatterState → IsometricState Mapping
# =============================================================================


def scatter_point_to_grid(
    point: "ScatterPoint",
    config: IsometricConfig,
    x_range: tuple[float, float] = (-1.0, 1.0),
    y_range: tuple[float, float] = (-1.0, 1.0),
) -> tuple[int, int]:
    """
    Map a ScatterPoint's (x, y) to grid coordinates.

    Args:
        point: The scatter point with x, y coordinates
        config: Isometric configuration with grid dimensions
        x_range: The expected range of x values (default -1 to 1)
        y_range: The expected range of y values (default -1 to 1)

    Returns:
        (grid_x, grid_y) tuple clamped to grid bounds
    """
    # Normalize to [0, 1]
    x_norm = (point.x - x_range[0]) / (x_range[1] - x_range[0])
    y_norm = (point.y - y_range[0]) / (y_range[1] - y_range[0])

    # Scale to grid dimensions
    grid_x = int(x_norm * (config.grid_width - 1))
    grid_y = int(y_norm * (config.grid_height - 1))

    # Clamp to grid bounds
    grid_x = max(0, min(config.grid_width - 1, grid_x))
    grid_y = max(0, min(config.grid_height - 1, grid_y))

    return (grid_x, grid_y)


def scatter_point_to_cell(
    point: "ScatterPoint",
    config: IsometricConfig,
    x_range: tuple[float, float] = (-1.0, 1.0),
    y_range: tuple[float, float] = (-1.0, 1.0),
) -> IsometricCell:
    """
    Convert a ScatterPoint to an IsometricCell.

    Maps the point's position to grid coordinates and preserves
    visual properties like color and selection state.
    """
    grid_x, grid_y = scatter_point_to_grid(point, config, x_range, y_range)

    # Determine glyph based on archetype (first letter uppercase)
    glyph = point.archetype[0].upper() if point.archetype else "@"

    return IsometricCell(
        grid_x=grid_x,
        grid_y=grid_y,
        content_type="citizen",
        citizen_id=point.citizen_id,
        color=point.color,
        glyph=glyph,
        is_highlighted=point.is_evolving,
        is_selected=point.is_selected,
    )


def scatter_to_isometric(
    scatter_state: "ScatterState",
    config: IsometricConfig | None = None,
    x_range: tuple[float, float] | None = None,
    y_range: tuple[float, float] | None = None,
) -> IsometricState:
    """
    Convert a ScatterState to an IsometricState.

    Maps all ScatterPoints to IsometricCells with grid positioning.
    This is the primary integration point between the 2D scatter visualization
    and the isometric factory view.

    Functor Law: This mapping preserves structure.
        scatter_to_isometric(scatter.with_points(f(points)))
        ≡ scatter_to_isometric(scatter).with_cells(map_cells(f))

    Args:
        scatter_state: The scatter state with citizen points
        config: Isometric configuration (uses default if None)
        x_range: Range of x coordinates (auto-computed if None)
        y_range: Range of y coordinates (auto-computed if None)

    Returns:
        IsometricState with cells mapped from scatter points
    """
    cfg = config or IsometricConfig()

    # Auto-compute coordinate ranges from points if not provided
    if scatter_state.points:
        if x_range is None:
            xs = [p.x for p in scatter_state.points]
            x_min, x_max = min(xs), max(xs)
            # Add padding to avoid edge cases
            x_padding = (x_max - x_min) * 0.1 if x_max > x_min else 0.5
            x_range = (x_min - x_padding, x_max + x_padding)
        if y_range is None:
            ys = [p.y for p in scatter_state.points]
            y_min, y_max = min(ys), max(ys)
            y_padding = (y_max - y_min) * 0.1 if y_max > y_min else 0.5
            y_range = (y_min - y_padding, y_max + y_padding)
    else:
        x_range = x_range or (-1.0, 1.0)
        y_range = y_range or (-1.0, 1.0)

    # Convert points to cells
    cells: list[IsometricCell] = []
    for point in scatter_state.points:
        cell = scatter_point_to_cell(point, cfg, x_range, y_range)
        cells.append(cell)

    # Determine selected cell from scatter state
    selected_cell: tuple[int, int] | None = None
    if scatter_state.selected_citizen_id:
        for point in scatter_state.points:
            if point.citizen_id == scatter_state.selected_citizen_id:
                selected_cell = scatter_point_to_grid(point, cfg, x_range, y_range)
                break

    # Determine hovered cell from scatter state
    hovered_cell: tuple[int, int] | None = None
    if scatter_state.hovered_citizen_id:
        for point in scatter_state.points:
            if point.citizen_id == scatter_state.hovered_citizen_id:
                hovered_cell = scatter_point_to_grid(point, cfg, x_range, y_range)
                break

    return IsometricState(
        config=cfg,
        cells=tuple(cells),
        citizens=scatter_state.points,
        selected_cell=selected_cell,
        hovered_cell=hovered_cell,
        updated_at=scatter_state.updated_at,
    )


# =============================================================================
# IsometricWidget Implementation
# =============================================================================


class IsometricWidget:
    """
    Isometric factory widget implementing IsometricWidgetProtocol.

    Renders Agent Town as an isometric grid visualization.
    Functor Law: isometric.map(f) ≡ isometric.with_state(f(state.value))

    Targets:
    - CLI: ASCII isometric grid with glyphs
    - JSON: IsometricState.to_dict()
    - TUI: Rich grid (delegates to JSON for now)
    - MARIMO: anywidget SVG (delegates to JSON for now)
    """

    def __init__(self, initial_state: IsometricState | None = None) -> None:
        """
        Create an IsometricWidget.

        Args:
            initial_state: Initial isometric state (uses empty default if None)
        """
        from agents.i.reactive.signal import Signal

        self._state: Signal[IsometricState] = Signal.of(initial_state or IsometricState())

    @property
    def state(self) -> "Signal[IsometricState]":
        """The reactive state signal."""
        from agents.i.reactive.signal import Signal

        return self._state

    def project(self, target: "RenderTarget") -> Any:
        """
        Project to rendering target.

        CLI: ASCII isometric grid with glyphs
        JSON: IsometricState.to_dict()
        TUI: Rich grid (delegates to CLI for MVP)
        MARIMO: anywidget (delegates to JSON for MVP)
        """
        from agents.i.reactive.widget import RenderTarget

        state = self._state.value

        if target == RenderTarget.CLI:
            return self._render_cli(state)
        elif target == RenderTarget.JSON:
            return state.to_dict()
        elif target == RenderTarget.TUI:
            # TUI delegates to CLI for MVP
            return self._render_cli(state)
        elif target == RenderTarget.MARIMO:
            # MARIMO delegates to JSON for MVP
            return state.to_dict()
        else:
            return state.to_dict()

    def _render_cli(self, state: IsometricState) -> str:
        """
        Render beautiful ASCII isometric grid with glyph grammar.

        Glyph Grammar (from Micro-Experience Factory spec):
        - Citizens: A(rtisan), E(xplorer), T(hinker), S(age), C(aretaker), W(itness), B(uilder)
        - Coalition edges: ─, │, ╱, ╲ (connecting members)
        - Evolving: *A* (asterisks around glyph)
        - Selected: [A] (brackets)
        - Slop blossoms: ❀, ✿, ✾ (when bloom active)
        - Empty cells: · (middle dot, not period)
        """
        config = state.config
        width = config.grid_width
        height = config.grid_height

        # Build grid as 2D array with spacing for multi-char glyphs
        grid: list[list[str]] = [["·" for _ in range(width)] for _ in range(height)]

        # Slop bloom characters (cycle through for variety)
        bloom_chars = ("❀", "✿", "✾")
        bloom_idx = 0

        # Place cells on grid
        for cell in state.cells:
            if 0 <= cell.grid_x < width and 0 <= cell.grid_y < height:
                glyph = cell.glyph
                # Mark highlighted/selected
                if cell.is_selected:
                    glyph = f"[{glyph}]"
                elif cell.is_highlighted:
                    glyph = f"*{glyph}*"
                grid[cell.grid_y][cell.grid_x] = glyph

        # Scatter slop blossoms if bloom is active
        if state.slop_bloom_active and len(state.cells) > 0:
            import random

            rng = random.Random(42)  # Deterministic for testing
            for _ in range(min(5, width * height // 20)):
                bx = rng.randint(0, width - 1)
                by = rng.randint(0, height - 1)
                if grid[by][bx] == "·":
                    grid[by][bx] = bloom_chars[bloom_idx % len(bloom_chars)]
                    bloom_idx += 1

        # Calculate display dimensions
        display_width = 58  # Fixed width for consistent output

        # Render frame
        lines: list[str] = []

        # Top border
        lines.append("═" * display_width)

        # Header: ISOMETRIC FACTORY
        title = "ISOMETRIC FACTORY"
        lines.append(f"{'═' * 19} {title} {'═' * 19}")

        # Status line: Day | Phase | Entropy bar
        phase_names = ["MORNING", "AFTERNOON", "EVENING", "NIGHT"]
        day = max(1, (state.current_tick // 4) + 1)
        phase_idx = state.current_tick % 4
        phase_name = phase_names[phase_idx] if phase_idx < len(phase_names) else "MORNING"

        # Entropy bar (10 chars: filled + empty)
        entropy_filled = int(state.entropy_level * 10)
        entropy_bar = "▓" * entropy_filled + "░" * (10 - entropy_filled)
        status_line = (
            f"Day {day:>2} │ {phase_name:<9} │ Entropy: {entropy_bar} {state.entropy_level:.2f}"
        )
        lines.append(status_line)

        # Separator
        lines.append("─" * display_width)

        # Slop bloom indicator
        if state.slop_bloom_active:
            bloom_line = "❀ ✿ ✾  SLOP BLOOM ACTIVE  ✾ ✿ ❀".center(display_width)
            lines.append(bloom_line)
            lines.append("")

        # Render grid with isometric offset
        # Use smaller viewport for cleaner display
        view_h = min(height, 12)
        view_w = min(width, 20)
        start_y = max(0, (height - view_h) // 2)
        start_x = max(0, (width - view_w) // 2)

        for y in range(view_h):
            # Isometric offset: each row shifts
            offset = "  " * (view_h - y - 1)
            row_glyphs: list[str] = []
            for x in range(view_w):
                gy = start_y + y
                gx = start_x + x
                if gy < height and gx < width:
                    cell_val = grid[gy][gx]
                    # Pad multi-char glyphs for alignment
                    if len(cell_val) == 1:
                        row_glyphs.append(f" {cell_val} ")
                    elif len(cell_val) == 3:  # *X* or [X]
                        row_glyphs.append(cell_val)
                    else:
                        row_glyphs.append(cell_val.center(3))
                else:
                    row_glyphs.append(" · ")
            line = offset + "".join(row_glyphs)
            lines.append(line)

        # Separator
        lines.append("")
        lines.append("─" * display_width)

        # Stats line
        num_citizens = len([c for c in state.cells if c.content_type == "citizen"])
        num_coalitions = 0  # TODO: Track coalitions
        num_pipelines = len(state.active_pipelines)
        tokens = state.current_tick * 100  # Approximate

        stats_line = (
            f"Citizens: {num_citizens} │ Coalitions: {num_coalitions} │ "
            f"Pipelines: {num_pipelines} │ Tokens: {tokens:,}"
        )
        lines.append(stats_line)

        # Perturbation pad footer (HITL controls)
        lines.append("")
        pads_line = "[G]reet  [S]gossip  [T]rade  [O]solo  │  [R]eplay  [B]loom"
        costs_line = "  50🪙     150🪙      200🪙    75🪙    │  ◀ ▶ ▮▮"
        lines.append(pads_line)
        lines.append(costs_line)

        # Bottom border
        lines.append("═" * display_width)

        return "\n".join(lines)

    def with_state(self, new_state: IsometricState) -> "IsometricWidget":
        """Create new widget with transformed state."""
        return IsometricWidget(new_state)

    def map(self, f: Callable[[IsometricState], IsometricState]) -> "IsometricWidget":
        """
        Functor map: transform the widget via a state transformation.

        Law: isometric.map(f) ≡ isometric.with_state(f(isometric.state.value))
        """
        return self.with_state(f(self._state.value))

    # --- State Mutations ---

    def select_cell(self, grid_x: int, grid_y: int) -> None:
        """Select a cell (highlights in visualization)."""
        current = self._state.value
        self._state.set(
            IsometricState(
                config=current.config,
                cells=current.cells,
                citizens=current.citizens,
                active_pipelines=current.active_pipelines,
                open_slots=current.open_slots,
                selected_cell=(grid_x, grid_y),
                hovered_cell=current.hovered_cell,
                current_tick=current.current_tick,
                max_tick=current.max_tick,
                slop_bloom_active=current.slop_bloom_active,
                entropy_level=current.entropy_level,
                updated_at=datetime.now(),
            )
        )

    def hover_cell(self, grid_x: int, grid_y: int) -> None:
        """Set hovered cell (for tooltips)."""
        current = self._state.value
        self._state.set(
            IsometricState(
                config=current.config,
                cells=current.cells,
                citizens=current.citizens,
                active_pipelines=current.active_pipelines,
                open_slots=current.open_slots,
                selected_cell=current.selected_cell,
                hovered_cell=(grid_x, grid_y),
                current_tick=current.current_tick,
                max_tick=current.max_tick,
                slop_bloom_active=current.slop_bloom_active,
                entropy_level=current.entropy_level,
                updated_at=datetime.now(),
            )
        )

    def set_tick(self, tick: int) -> None:
        """Set current tick for replay scrubber."""
        current = self._state.value
        self._state.set(
            IsometricState(
                config=current.config,
                cells=current.cells,
                citizens=current.citizens,
                active_pipelines=current.active_pipelines,
                open_slots=current.open_slots,
                selected_cell=current.selected_cell,
                hovered_cell=current.hovered_cell,
                current_tick=tick,
                max_tick=current.max_tick,
                slop_bloom_active=current.slop_bloom_active,
                entropy_level=current.entropy_level,
                updated_at=datetime.now(),
            )
        )

    def toggle_slop_bloom(self) -> None:
        """Toggle the Accursed Share slop bloom mode."""
        current = self._state.value
        self._state.set(
            IsometricState(
                config=current.config,
                cells=current.cells,
                citizens=current.citizens,
                active_pipelines=current.active_pipelines,
                open_slots=current.open_slots,
                selected_cell=current.selected_cell,
                hovered_cell=current.hovered_cell,
                current_tick=current.current_tick,
                max_tick=current.max_tick,
                slop_bloom_active=not current.slop_bloom_active,
                entropy_level=current.entropy_level,
                updated_at=datetime.now(),
            )
        )

    # --- Integration ---

    def update_from_scatter(self, scatter_state: "ScatterState") -> None:
        """Update citizens from scatter widget state."""
        new_isometric = scatter_to_isometric(
            scatter_state,
            self._state.value.config,
        )
        # Preserve non-scatter state
        current = self._state.value
        self._state.set(
            IsometricState(
                config=new_isometric.config,
                cells=new_isometric.cells,
                citizens=new_isometric.citizens,
                active_pipelines=current.active_pipelines,
                open_slots=current.open_slots,
                selected_cell=new_isometric.selected_cell,
                hovered_cell=new_isometric.hovered_cell,
                current_tick=current.current_tick,
                max_tick=current.max_tick,
                slop_bloom_active=current.slop_bloom_active,
                entropy_level=current.entropy_level,
                updated_at=datetime.now(),
            )
        )

    def update_from_event(self, event: "TownEvent") -> None:
        """Update from a town event (add pipeline segment, etc.)."""
        current = self._state.value
        # Add event metadata - track active pipelines
        new_pipelines = list(current.active_pipelines)
        if event.metadata.get("pipeline_id"):
            new_pipelines.append(event.metadata["pipeline_id"])

        # Update entropy based on drama contribution
        new_entropy = min(1.0, current.entropy_level + event.drama_contribution * 0.1)

        self._state.set(
            IsometricState(
                config=current.config,
                cells=current.cells,
                citizens=current.citizens,
                active_pipelines=tuple(new_pipelines),
                open_slots=current.open_slots,
                selected_cell=current.selected_cell,
                hovered_cell=current.hovered_cell,
                current_tick=current.current_tick + 1,  # Advance tick on event
                max_tick=current.max_tick + 1,
                slop_bloom_active=current.slop_bloom_active,
                entropy_level=new_entropy,
                updated_at=datetime.now(),
            )
        )

    # --- Convenience Methods ---

    def to_cli(self) -> str:
        """Convenience: project to CLI."""
        from agents.i.reactive.widget import RenderTarget

        result = self.project(RenderTarget.CLI)
        return str(result)

    def to_json(self) -> dict[str, Any]:
        """Convenience: project to JSON."""
        from agents.i.reactive.widget import RenderTarget

        result = self.project(RenderTarget.JSON)
        if isinstance(result, dict):
            return result
        return {"value": result}
