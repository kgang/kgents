"""
DensityFieldWidget: 2D grid of glyphs with spatial entropy coherence.

The DensityField is the canvas where agents live. It's a 2D grid where:
- Each cell is a GlyphWidget
- Entropy flows spatially (nearby cells share entropy influence)
- "Wind" can affect distortion direction
- Entities can be placed at positions

This is the stigmergic field - the shared environment where agents
leave traces and perceive each other.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.entropy import (
    DENSITY_RUNES,
    PHI,
    entropy_to_distortion,
    entropy_to_rune,
)
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget, Phase
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Entity:
    """An entity placed on the density field."""

    id: str
    x: int
    y: int
    char: str = "◉"
    phase: Phase = "active"
    heat: float = 0.0  # Local entropy contribution


@dataclass(frozen=True)
class Wind:
    """
    Wind direction affecting distortion.

    Wind creates spatial coherence - glyphs "lean" in the wind direction.
    """

    dx: float = 0.0  # -1.0 to 1.0, west to east
    dy: float = 0.0  # -1.0 to 1.0, north to south
    strength: float = 0.0  # 0.0 to 1.0


@dataclass(frozen=True)
class DensityFieldState:
    """
    Immutable density field state.

    The field has:
    - Base entropy grid (background chaos level)
    - Entities at positions
    - Optional wind affecting distortion
    """

    width: int = 40
    height: int = 20
    base_entropy: float = 0.1  # Background entropy level
    entities: tuple[Entity, ...] = ()  # Entities on the field
    wind: Wind = field(default_factory=Wind)  # Wind direction
    seed: int = 0  # Deterministic seed
    t: float = 0.0  # Time in milliseconds
    show_grid: bool = False  # Show grid lines


class DensityFieldWidget(KgentsWidget[DensityFieldState]):
    """
    A 2D grid of glyphs with spatial entropy coherence.

    The density field is the canvas for agent visualization. Key features:

    1. **Spatial Entropy**: Entropy isn't uniform - entities radiate heat
       that decays with distance.

    2. **Wind Effect**: A wind vector causes glyphs to "lean" in a direction,
       creating visual flow.

    3. **Entity Placement**: Agents appear as special glyphs at positions.

    4. **Time Coherence**: All glyphs receive the same t for synchronized
       animation.

    Example:
        field = DensityFieldWidget(DensityFieldState(
            width=60,
            height=20,
            base_entropy=0.1,
            entities=(
                Entity(id="agent-1", x=10, y=5, phase="active", heat=0.8),
                Entity(id="agent-2", x=30, y=10, phase="waiting", heat=0.3),
            ),
            wind=Wind(dx=0.5, dy=-0.2, strength=0.3),
        ))

        print(field.project(RenderTarget.CLI))  # ASCII grid
    """

    state: Signal[DensityFieldState]

    def __init__(self, initial: DensityFieldState | None = None) -> None:
        self.state = Signal.of(initial or DensityFieldState())

    def with_time(self, t: float) -> DensityFieldWidget:
        """Return new field with updated time. Immutable."""
        current = self.state.value
        return DensityFieldWidget(
            DensityFieldState(
                width=current.width,
                height=current.height,
                base_entropy=current.base_entropy,
                entities=current.entities,
                wind=current.wind,
                seed=current.seed,
                t=t,
                show_grid=current.show_grid,
            )
        )

    def with_entropy(self, entropy: float) -> DensityFieldWidget:
        """Return new field with updated base entropy. Immutable."""
        current = self.state.value
        return DensityFieldWidget(
            DensityFieldState(
                width=current.width,
                height=current.height,
                base_entropy=max(0.0, min(1.0, entropy)),
                entities=current.entities,
                wind=current.wind,
                seed=current.seed,
                t=current.t,
                show_grid=current.show_grid,
            )
        )

    def with_wind(self, wind: Wind) -> DensityFieldWidget:
        """Return new field with updated wind. Immutable."""
        current = self.state.value
        return DensityFieldWidget(
            DensityFieldState(
                width=current.width,
                height=current.height,
                base_entropy=current.base_entropy,
                entities=current.entities,
                wind=wind,
                seed=current.seed,
                t=current.t,
                show_grid=current.show_grid,
            )
        )

    def add_entity(self, entity: Entity) -> DensityFieldWidget:
        """Add an entity to the field. Immutable."""
        current = self.state.value
        # Remove existing entity with same id if present
        filtered = tuple(e for e in current.entities if e.id != entity.id)
        return DensityFieldWidget(
            DensityFieldState(
                width=current.width,
                height=current.height,
                base_entropy=current.base_entropy,
                entities=(*filtered, entity),
                wind=current.wind,
                seed=current.seed,
                t=current.t,
                show_grid=current.show_grid,
            )
        )

    def remove_entity(self, entity_id: str) -> DensityFieldWidget:
        """Remove an entity from the field. Immutable."""
        current = self.state.value
        filtered = tuple(e for e in current.entities if e.id != entity_id)
        return DensityFieldWidget(
            DensityFieldState(
                width=current.width,
                height=current.height,
                base_entropy=current.base_entropy,
                entities=filtered,
                wind=current.wind,
                seed=current.seed,
                t=current.t,
                show_grid=current.show_grid,
            )
        )

    def _compute_entropy_at(self, x: int, y: int) -> float:
        """
        Compute entropy at a position.

        Entropy = base_entropy + sum of entity heat contributions.
        Heat decays with distance (inverse square law).
        """
        state = self.state.value
        entropy = state.base_entropy

        for entity in state.entities:
            # Distance from entity
            dx = x - entity.x
            dy = y - entity.y
            dist_sq = dx * dx + dy * dy

            if dist_sq == 0:
                # At entity position, full heat
                entropy += entity.heat
            else:
                # Inverse square decay with minimum distance of 1
                decay = 1.0 / (1.0 + dist_sq * 0.1)
                entropy += entity.heat * decay

        return min(1.0, entropy)

    def _entity_at(self, x: int, y: int) -> Entity | None:
        """Get entity at position, if any."""
        for entity in self.state.value.entities:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def _build_glyph_at(self, x: int, y: int) -> GlyphWidget:
        """Build a glyph for a specific position."""
        state = self.state.value

        # Check for entity at this position
        entity = self._entity_at(x, y)
        if entity:
            return GlyphWidget(
                GlyphState(
                    char=entity.char,
                    phase=entity.phase,
                    entropy=self._compute_entropy_at(x, y),
                    seed=state.seed + x * state.height + y,
                    t=state.t,
                )
            )

        # Background cell - show entropy as density rune
        entropy = self._compute_entropy_at(x, y)
        char = entropy_to_rune(entropy)

        return GlyphWidget(
            GlyphState(
                char=char,
                entropy=entropy,
                seed=state.seed + x * state.height + y,
                t=state.t,
            )
        )

    def _build_grid(self) -> list[list[GlyphWidget]]:
        """Build the 2D glyph grid."""
        state = self.state.value
        grid: list[list[GlyphWidget]] = []

        for y in range(state.height):
            row: list[GlyphWidget] = []
            for x in range(state.width):
                row.append(self._build_glyph_at(x, y))
            grid.append(row)

        return grid

    def project(self, target: RenderTarget) -> Any:
        """
        Project this density field to a rendering target.

        Args:
            target: Which rendering target

        Returns:
            - CLI: str (ASCII grid)
            - TUI: list of Rich Text rows
            - MARIMO: HTML grid
            - JSON: dict with field data
        """
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
        """CLI projection: ASCII grid."""
        grid = self._build_grid()
        lines: list[str] = []

        for row in grid:
            chars = [g.project(RenderTarget.CLI) for g in row]
            lines.append("".join(chars))

        return "\n".join(lines)

    def _to_tui(self) -> Any:
        """TUI projection: list of Rich Text rows."""
        try:
            from rich.text import Text

            grid = self._build_grid()
            rows: list[Text] = []

            for row in grid:
                row_text = Text()
                for glyph in row:
                    glyph_text = glyph.project(RenderTarget.TUI)
                    if isinstance(glyph_text, Text):
                        row_text.append_text(glyph_text)
                    else:
                        row_text.append(str(glyph_text))
                rows.append(row_text)

            return rows
        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML grid."""
        grid = self._build_grid()

        html = '<div class="kgents-density-field" style="font-family: monospace; line-height: 1;">'

        for row in grid:
            html += '<div class="kgents-field-row" style="white-space: pre;">'
            for glyph in row:
                html += glyph.project(RenderTarget.MARIMO)
            html += "</div>"

        html += "</div>"
        return html

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: field data."""
        state = self.state.value
        grid = self._build_grid()

        # Flatten grid for JSON
        cells: list[dict[str, Any]] = []
        for y, row in enumerate(grid):
            for x, glyph in enumerate(row):
                cell = glyph.project(RenderTarget.JSON)
                cell["x"] = x
                cell["y"] = y
                cells.append(cell)

        result: dict[str, Any] = {
            "type": "density_field",
            "width": state.width,
            "height": state.height,
            "base_entropy": state.base_entropy,
            "entity_count": len(state.entities),
            "entities": [
                {
                    "id": e.id,
                    "x": e.x,
                    "y": e.y,
                    "char": e.char,
                    "phase": e.phase,
                    "heat": e.heat,
                }
                for e in state.entities
            ],
            "cells": cells,
        }

        if state.wind.strength > 0:
            result["wind"] = {
                "dx": state.wind.dx,
                "dy": state.wind.dy,
                "strength": state.wind.strength,
            }

        return result
