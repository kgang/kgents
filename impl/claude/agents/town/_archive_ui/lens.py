"""
THE LENS: LOD Zoom Interface.

From Morton: The deeper you look, the less certain you become.
Higher LOD does not mean more transparency—it means encountering
the opacity more directly.

LOD Levels:
0: Silhouette - name, location, emoji
1: Posture - current action, mood
2: Dialogue - cosmotechnics, metaphor
3: Memory - eigenvectors, relationships
4: Psyche - accursed surplus, ID
5: Abyss - the irreducible mystery

Model Routing (for future LLM integration):
LOD 0-1: cache/haiku
LOD 2-3: haiku/sonnet
LOD 4-5: sonnet/opus
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from agents.town.ui.widgets import (
    citizen_badge,
    eigenvector_table,
    relationship_table,
)
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from agents.town.citizen import Citizen


# Model routing for LOD levels (future use with LLM calls)
LOD_MODEL_MAP = {
    0: "cache",  # No LLM call
    1: "haiku",  # Quick inference
    2: "haiku",  # Dialogue synthesis
    3: "sonnet",  # Memory retrieval
    4: "sonnet",  # Deep psychological
    5: "opus",  # The abyss
}


@dataclass
class LensView:
    """
    LOD zoom view for a single citizen.

    From Glissant: At LOD 5, you don't see clarity—you see
    the limit of knowability. The citizen's opacity reveals itself.
    """

    console: Console | None = None

    def __post_init__(self) -> None:
        if self.console is None:
            self.console = Console()

    def render(
        self,
        citizen: "Citizen",
        lod: int = 0,
        citizen_names: dict[str, str] | None = None,
    ) -> Panel:
        """Render the LENS view at specified LOD."""
        lod = max(0, min(5, lod))
        manifest = citizen.manifest(lod)

        content_parts: list[RenderableType] = []

        # LOD 0: Silhouette
        content_parts.append(self._render_silhouette(manifest))

        # LOD 1: Posture
        if lod >= 1:
            content_parts.append(Text())
            content_parts.append(self._render_posture(manifest))

        # LOD 2: Cosmotechnics
        if lod >= 2:
            content_parts.append(Text())
            content_parts.append(self._render_cosmotechnics(manifest))

        # LOD 3: Memory
        if lod >= 3:
            content_parts.append(Text())
            content_parts.append(self._render_memory(manifest, citizen_names))

        # LOD 4: Psyche
        if lod >= 4:
            content_parts.append(Text())
            content_parts.append(self._render_psyche(manifest))

        # LOD 5: Abyss
        if lod >= 5:
            content_parts.append(Text())
            content_parts.append(self._render_abyss(manifest))

        # LOD indicator and model hint
        model = LOD_MODEL_MAP.get(lod, "cache")
        footer = Text(f"\nLOD {lod} | Model: {model}", style="dim")
        content_parts.append(footer)

        return Panel(
            Group(*content_parts),
            title=f"[bold cyan]LENS: {citizen.name}[/bold cyan]",
            subtitle=f"LOD {lod}/5",
            border_style="cyan",
        )

    def _render_silhouette(self, manifest: dict[str, Any]) -> RenderableType:
        """LOD 0: Name, location, phase icon."""
        phase = manifest.get("phase", "IDLE")
        icons = {
            "IDLE": "🧍",
            "SOCIALIZING": "💬",
            "WORKING": "🔨",
            "REFLECTING": "💭",
            "RESTING": "😴",
        }
        icon = icons.get(phase, "❓")

        text = Text()
        text.append(f"{icon} ", style="bold")
        text.append(manifest["name"], style="cyan bold")
        text.append(f" @ {manifest['region']}", style="dim")

        return text

    def _render_posture(self, manifest: dict[str, Any]) -> RenderableType:
        """LOD 1: Archetype and mood."""
        text = Text()
        text.append("Archetype: ", style="bold")
        text.append(manifest.get("archetype", "unknown"), style="yellow")
        text.append("\n")
        text.append("Mood: ", style="bold")
        text.append(manifest.get("mood", "unknown"), style="green")

        return text

    def _render_cosmotechnics(self, manifest: dict[str, Any]) -> RenderableType:
        """LOD 2: Cosmotechnics and metaphor."""
        text = Text()
        text.append("Cosmotechnics: ", style="bold")
        text.append(manifest.get("cosmotechnics", "unknown"), style="magenta")
        text.append("\n")
        text.append("Metaphor: ", style="bold")
        text.append(f'"{manifest.get("metaphor", "")}"', style="italic")

        return text

    def _render_memory(
        self,
        manifest: dict[str, Any],
        citizen_names: dict[str, str] | None,
    ) -> RenderableType:
        """LOD 3: Eigenvectors and relationships."""
        parts: list[RenderableType] = []

        # Eigenvectors
        parts.append(Text("Eigenvectors:", style="bold"))
        eigenvectors = manifest.get("eigenvectors", {})
        if eigenvectors:
            parts.append(eigenvector_table(eigenvectors))
        else:
            parts.append(Text("  (not available)", style="dim"))

        parts.append(Text())

        # Relationships
        parts.append(Text("Relationships:", style="bold"))
        relationships = manifest.get("relationships", {})
        parts.append(relationship_table(relationships, citizen_names))

        return Group(*parts)

    def _render_psyche(self, manifest: dict[str, Any]) -> RenderableType:
        """LOD 4: Accursed surplus and ID."""
        text = Text()
        text.append("ID: ", style="bold")
        text.append(manifest.get("id", "unknown"), style="dim")
        text.append("\n")
        text.append("Accursed Surplus: ", style="bold")

        surplus = manifest.get("accursed_surplus", 0)
        surplus_style = "red bold" if surplus > 5 else "yellow" if surplus > 1 else "dim"
        text.append(f"{surplus:.2f}", style=surplus_style)

        if surplus > 5:
            text.append(" (NEEDS EXPENDITURE!)", style="red")

        return text

    def _render_abyss(self, manifest: dict[str, Any]) -> RenderableType:
        """LOD 5: The irreducible mystery."""
        opacity = manifest.get("opacity", {})

        parts: list[RenderableType] = []

        # Header
        parts.append(Text("─" * 40, style="dim"))
        parts.append(Text())
        parts.append(Text("THE ABYSS", style="bold red"))
        parts.append(Text())

        # Opacity statement
        statement = opacity.get("statement", "")
        if statement:
            parts.append(Text(f'"{statement}"', style="italic magenta"))
            parts.append(Text())

        # Message
        message = opacity.get("message", "")
        if message:
            parts.append(Text(message, style="dim"))

        return Group(*parts)

    def print(
        self,
        citizen: "Citizen",
        lod: int = 0,
        citizen_names: dict[str, str] | None = None,
    ) -> None:
        """Print the LENS view to console."""
        if self.console is None:
            self.console = Console()
        self.console.print(self.render(citizen, lod, citizen_names))


def render_lens(
    citizen: "Citizen",
    lod: int = 0,
    citizen_names: dict[str, str] | None = None,
) -> str:
    """Render LENS view as string (for testing)."""
    console = Console(force_terminal=True, width=60)
    view = LensView(console=console)

    with console.capture() as capture:
        view.print(citizen, lod, citizen_names)

    return capture.get()


__all__ = ["LensView", "render_lens", "LOD_MODEL_MAP"]
