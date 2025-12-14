"""
Stigmergic Field Widget - Interactive canvas rendering of entities and pheromones.

This is the marimo-native equivalent of the Textual DensityField widget.
Entities move with Brownian motion, attracted to tasks, repelled by conflicts.

The field IS the garden made visible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import traitlets

from .base import KgentsWidget

# Block characters for ASCII fallback
DENSITY_CHARS = " ░▒▓█"
GLITCH_CHARS = "▚▞▛▜▙▟"

# Path to JS file
_JS_DIR = Path(__file__).parent / "js"


class StigmergicFieldWidget(KgentsWidget):
    """
    Stigmergic field rendered as interactive canvas.

    Features:
    - Canvas-based rendering with WebGL fallback
    - Entity symbols with color-coded phases
    - Pheromone trails as colored gradients
    - Click to select entity
    - Brownian motion animation
    - Entropy-based visual noise

    Data model matches impl/claude/agents/i/field.py for bidirectional sync.
    """

    _esm = _JS_DIR / "stigmergic_field.js"

    _css = """
    .kgents-field-container {
        user-select: none;
    }
    .kgents-entity:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    """

    # Field dimensions
    width = traitlets.Int(60).tag(sync=True)
    height = traitlets.Int(20).tag(sync=True)
    cell_size = traitlets.Int(12).tag(sync=True)  # Pixels per cell

    # Entities: list of dicts with {id, symbol, x, y, phase, heat}
    entities: list[dict[str, Any]] = traitlets.List([]).tag(sync=True)  # type: ignore[assignment]

    # Pheromones: list of dicts with {ptype, x, y, intensity, birth_tick}
    pheromones: list[dict[str, Any]] = traitlets.List([]).tag(sync=True)  # type: ignore[assignment]

    # Global metrics
    entropy = traitlets.Float(0.5).tag(sync=True)  # 0.0-1.0
    heat = traitlets.Float(0.0).tag(sync=True)  # 0-100
    tick = traitlets.Int(0).tag(sync=True)
    dialectic_phase = traitlets.Unicode("flux").tag(sync=True)

    # Interaction state
    focus_entity_id = traitlets.Unicode("").tag(sync=True)
    clicked_entity_id = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        width: int = 60,
        height: int = 20,
        cell_size: int = 12,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.cell_size = cell_size

    @classmethod
    def from_field_state(cls, field_state: Any) -> "StigmergicFieldWidget":
        """
        Create widget from impl/claude/agents/i/field.FieldState.

        This enables bidirectional sync between Textual TUI and marimo.
        """
        widget = cls(
            width=field_state.width,
            height=field_state.height,
        )

        # Convert entities
        widget.entities = [
            {
                "id": e.id,
                "symbol": e.entity_type.value,
                "x": e.x,
                "y": e.y,
                "phase": e.phase.value,
                "heat": e.heat,
            }
            for e in field_state.entities.values()
        ]

        # Convert pheromones
        widget.pheromones = [
            {
                "ptype": p.ptype.value,
                "x": p.x,
                "y": p.y,
                "intensity": p.intensity,
                "birth_tick": p.birth_tick,
            }
            for p in field_state.pheromones
        ]

        widget.entropy = field_state.entropy / 100.0  # Normalize to 0-1
        widget.heat = field_state.heat
        widget.tick = field_state.tick
        widget.dialectic_phase = field_state.dialectic_phase.value
        widget.focus_entity_id = field_state.focus or ""

        return widget

    def update_from_field_state(self, field_state: Any) -> None:
        """Update widget from FieldState (for live sync)."""
        self.entities = [
            {
                "id": e.id,
                "symbol": e.entity_type.value,
                "x": e.x,
                "y": e.y,
                "phase": e.phase.value,
                "heat": e.heat,
            }
            for e in field_state.entities.values()
        ]

        self.pheromones = [
            {
                "ptype": p.ptype.value,
                "x": p.x,
                "y": p.y,
                "intensity": p.intensity,
                "birth_tick": p.birth_tick,
            }
            for p in field_state.pheromones
        ]

        self.entropy = field_state.entropy / 100.0
        self.heat = field_state.heat
        self.tick = field_state.tick
        self.dialectic_phase = field_state.dialectic_phase.value

    def add_entity(
        self,
        entity_id: str,
        symbol: str,
        x: int,
        y: int,
        phase: str = "active",
        heat: float = 0.0,
    ) -> None:
        """Add an entity to the field."""
        self.entities = [
            *self.entities,
            {
                "id": entity_id,
                "symbol": symbol,
                "x": x,
                "y": y,
                "phase": phase,
                "heat": heat,
            },
        ]

    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from the field."""
        self.entities = [e for e in self.entities if e["id"] != entity_id]

    def emit_pheromone(
        self,
        ptype: str,
        x: int,
        y: int,
        intensity: float = 1.0,
    ) -> None:
        """Emit a pheromone at the given position."""
        self.pheromones = [
            *self.pheromones,
            {
                "ptype": ptype,
                "x": x,
                "y": y,
                "intensity": intensity,
                "birth_tick": self.tick,
            },
        ]
