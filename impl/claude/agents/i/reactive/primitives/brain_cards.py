"""
Brain Cards: Reactive widgets for Holographic Brain visualization.

Part of Crown Jewel Brain (Session 5):
- BrainCartographyCard: Memory topology visualization
- GhostNotifierCard: Surfaced ghost memories display

These cards provide reactive UI for the Brain subsystem,
supporting CLI, JSON, and marimo targets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget, Phase
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import CompositeWidget, RenderTarget

if TYPE_CHECKING:
    pass


# =============================================================================
# Brain Cartography Card
# =============================================================================


@dataclass(frozen=True)
class CartographyState:
    """
    Immutable cartography state.

    Represents the topology of memory:
    - landmarks: High-importance memory regions
    - desire_lines: Frequently traversed paths
    - voids: Regions with low activity (potential for exploration)
    """

    landmarks: int = 0  # Count of important memory regions
    desire_lines: int = 0  # Frequently accessed paths
    voids: int = 0  # Low-activity regions
    resolution: Literal["low", "medium", "high", "adaptive"] = "adaptive"
    entropy: float = 0.0  # 0.0-1.0, visual chaos
    t: float = 0.0  # Time in milliseconds


class BrainCartographyCard(CompositeWidget[CartographyState]):
    """
    Memory topology visualization card.

    Shows the holographic brain's memory landscape:
    - Landmarks (◉) for important memories
    - Paths (─) for desire lines
    - Voids (○) for unexplored regions

    Example:
        card = BrainCartographyCard(CartographyState(
            landmarks=5,
            desire_lines=12,
            voids=3,
            resolution="high",
        ))

        print(card.project(RenderTarget.CLI))
        # ◉ Memory Topology
        # Landmarks: 5 | Paths: 12 | Voids: 3
        # ████████░░ (high resolution)
    """

    state: Signal[CartographyState]

    def __init__(self, initial: CartographyState | None = None) -> None:
        state = initial or CartographyState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets from current state."""
        state = self.state.value

        # Header: Brain glyph
        self.slots["glyph"] = GlyphWidget(
            GlyphState(
                phase="active" if state.landmarks > 0 else "idle",
                entropy=state.entropy,
                t=state.t,
            )
        )

        # Resolution bar
        resolution_value = {
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "adaptive": 0.9,
        }.get(state.resolution, 0.5)

        self.slots["resolution_bar"] = BarWidget(
            BarState(
                value=resolution_value,
                width=10,
                style="solid",
                entropy=state.entropy,
                t=state.t,
            )
        )

    def project(self, target: RenderTarget) -> Any:
        """Project cartography to target format."""
        state = self.state.value

        match target:
            case RenderTarget.CLI:
                glyph = self.slots["glyph"].project(target)
                bar = self.slots["resolution_bar"].project(target)
                return (
                    f"{glyph} Memory Topology\n"
                    f"  Landmarks: {state.landmarks} | "
                    f"Paths: {state.desire_lines} | "
                    f"Voids: {state.voids}\n"
                    f"  {bar} ({state.resolution} resolution)"
                )
            case RenderTarget.JSON:
                return {
                    "type": "cartography",
                    "landmarks": state.landmarks,
                    "desire_lines": state.desire_lines,
                    "voids": state.voids,
                    "resolution": state.resolution,
                    "glyph": self.slots["glyph"].project(target),
                    "resolution_bar": self.slots["resolution_bar"].project(target),
                }
            case RenderTarget.MARIMO:
                # For marimo, return structured data for rich rendering
                return {
                    "widget": "cartography",
                    "data": {
                        "landmarks": state.landmarks,
                        "desire_lines": state.desire_lines,
                        "voids": state.voids,
                        "resolution": state.resolution,
                    },
                }
            case _:
                return self.project(RenderTarget.CLI)

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "BrainCartographyCard":
        """Create card from manifest result."""
        return cls(
            CartographyState(
                landmarks=manifest.get("landmarks", 0),
                desire_lines=manifest.get("desire_lines", 0),
                voids=manifest.get("voids", 1),
                resolution=manifest.get("resolution", "adaptive"),
            )
        )


# =============================================================================
# Ghost Notifier Card
# =============================================================================


@dataclass(frozen=True)
class GhostState:
    """
    Immutable ghost notification state.

    Represents a surfaced memory ghost:
    - content: The memory content
    - relevance: How relevant to current context (0.0-1.0)
    - age: How old the memory is
    """

    content: str = ""
    relevance: float = 0.0  # 0.0-1.0 relevance to context
    concept_id: str = ""
    age: str = "unknown"  # "recent", "old", "ancient"
    entropy: float = 0.0
    t: float = 0.0


@dataclass(frozen=True)
class GhostListState:
    """State for a list of ghost notifications."""

    ghosts: tuple[GhostState, ...] = ()
    context: str = ""  # The context that triggered surfacing
    total_count: int = 0
    entropy: float = 0.0
    t: float = 0.0


class GhostNotifierCard(CompositeWidget[GhostListState]):
    """
    Surfaced ghost memories display.

    Shows memories that have "surfaced" based on context relevance:
    - Each ghost shows content preview and relevance score
    - Ghosts fade based on relevance (high entropy for low relevance)

    Example:
        card = GhostNotifierCard(GhostListState(
            ghosts=(
                GhostState(content="Python tutorial", relevance=0.85),
                GhostState(content="ML basics", relevance=0.62),
            ),
            context="programming",
            total_count=2,
        ))

        print(card.project(RenderTarget.CLI))
        # 👻 Surfaced Memories (2)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━
        # ▸ Python tutorial     [████████░░] 85%
        # ▸ ML basics          [██████░░░░] 62%
    """

    state: Signal[GhostListState]

    def __init__(self, initial: GhostListState | None = None) -> None:
        state = initial or GhostListState()
        super().__init__(state)
        self._rebuild_slots()

    def _rebuild_slots(self) -> None:
        """Rebuild child widgets for each ghost."""
        state = self.state.value

        # Create a bar widget for each ghost's relevance
        for i, ghost in enumerate(state.ghosts):
            self.slots[f"relevance_{i}"] = BarWidget(
                BarState(
                    value=ghost.relevance,
                    width=10,
                    style="solid",
                    entropy=ghost.entropy,
                    t=state.t,
                )
            )

    def project(self, target: RenderTarget) -> Any:
        """Project ghost list to target format."""
        state = self.state.value

        match target:
            case RenderTarget.CLI:
                if not state.ghosts:
                    return "👻 No memories surfaced"

                lines = [f"👻 Surfaced Memories ({state.total_count})"]
                lines.append("━" * 25)

                for i, ghost in enumerate(state.ghosts):
                    bar = self.slots.get(f"relevance_{i}")
                    bar_str = bar.project(target) if bar else "░" * 10
                    # Truncate content to 20 chars
                    content_preview = (
                        ghost.content[:20] + "..."
                        if len(ghost.content) > 20
                        else ghost.content.ljust(20)
                    )
                    pct = int(ghost.relevance * 100)
                    lines.append(f"▸ {content_preview} [{bar_str}] {pct}%")

                return "\n".join(lines)

            case RenderTarget.JSON:
                return {
                    "type": "ghost_notifier",
                    "context": state.context,
                    "total_count": state.total_count,
                    "ghosts": [
                        {
                            "content": g.content,
                            "relevance": g.relevance,
                            "concept_id": g.concept_id,
                            "age": g.age,
                        }
                        for g in state.ghosts
                    ],
                }

            case RenderTarget.MARIMO:
                return {
                    "widget": "ghost_notifier",
                    "data": {
                        "context": state.context,
                        "ghosts": [
                            {
                                "content": g.content,
                                "relevance": g.relevance,
                                "concept_id": g.concept_id,
                            }
                            for g in state.ghosts
                        ],
                    },
                }

            case _:
                return self.project(RenderTarget.CLI)

    @classmethod
    def from_surface_result(cls, result: dict[str, Any]) -> "GhostNotifierCard":
        """Create card from ghost.surface result."""
        ghosts = tuple(
            GhostState(
                content=g.get("content", g.get("concept_id", "")),
                relevance=g.get("relevance", g.get("similarity", 0.0)),
                concept_id=g.get("concept_id", ""),
            )
            for g in result.get("surfaced", [])
        )

        return cls(
            GhostListState(
                ghosts=ghosts,
                context=result.get("context", ""),
                total_count=result.get("count", len(ghosts)),
            )
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_cartography_card(
    landmarks: int = 0,
    desire_lines: int = 0,
    voids: int = 0,
    resolution: Literal["low", "medium", "high", "adaptive"] = "adaptive",
) -> BrainCartographyCard:
    """Create a cartography card with given parameters."""
    return BrainCartographyCard(
        CartographyState(
            landmarks=landmarks,
            desire_lines=desire_lines,
            voids=voids,
            resolution=resolution,
        )
    )


def create_ghost_card(
    ghosts: list[tuple[str, float]] | None = None,
    context: str = "",
) -> GhostNotifierCard:
    """Create a ghost notifier card from content/relevance pairs.

    Args:
        ghosts: List of (content, relevance) tuples
        context: The context that triggered surfacing

    Example:
        card = create_ghost_card([
            ("Python tutorial", 0.85),
            ("ML basics", 0.62),
        ], context="programming")
    """
    ghost_states = tuple(
        GhostState(content=content, relevance=relevance)
        for content, relevance in (ghosts or [])
    )

    return GhostNotifierCard(
        GhostListState(
            ghosts=ghost_states,
            context=context,
            total_count=len(ghost_states),
        )
    )
