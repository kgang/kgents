"""
AGENTESE Garden Context: Garden State + Seasons + Health.

self.garden.* handles garden state and lifecycle:
- self.garden.manifest     - View garden status
- self.garden.season       - Current season info
- self.garden.health       - Health metrics
- self.garden.init         - Initialize garden
- self.garden.transition   - Transition to new season
- self.garden.suggest      - Auto-inducer suggestion
- self.garden.accept       - Accept transition
- self.garden.dismiss      - Dismiss transition

The Garden is the unified state model for development sessions:
- Plots are focused regions (crown jewels, plans)
- Seasons affect how much change the garden accepts
- Gestures accumulate in momentum trace

Wave 2.5: Migrated from CLI handler to AGENTESE-native.
Per plans/cli/wave2.5-gardener-migration.md

AGENTESE: self.garden.*

Principle Alignment:
- Tasteful: Intentional development seasons
- Ethical: Human controls transitions
- Joy-Inducing: Visible garden state
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# Garden affordances
GARDEN_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "season",
    "health",
    "init",
    "transition",
    "suggest",
    "accept",
    "dismiss",
    "tend",  # Sub-node for tending gestures
    "persona",  # Sub-node for idea lifecycle
    "inducer",  # Sub-node for auto-inducer
)


def _progress_bar(value: float, length: int = 10) -> str:
    """Create a progress bar string."""
    filled = int(value * length)
    return "[" + "=" * filled + "-" * (length - filled) + "]"


def _season_description(season_name: str) -> str:
    """Get human-readable description for a season."""
    descriptions = {
        "DORMANT": "Garden is resting. Operations are cheap but prompts resist change.",
        "SPROUTING": "New ideas emerging. High plasticity, perfect for new additions.",
        "BLOOMING": "Ideas crystallizing. Lower plasticity, high visibility.",
        "HARVEST": "Time to gather and consolidate. Reflection-oriented.",
        "COMPOSTING": "Breaking down old patterns. High entropy tolerance.",
    }
    return descriptions.get(season_name, "Unknown season")


@node(
    "self.garden",
    description="Garden State Manager - seasons, plots, and tending gestures",
    dependencies=(),  # Uses protocols.gardener_logos directly
)
@dataclass
class GardenNode(BaseLogosNode):
    """
    self.garden - Garden state management.

    Provides AGENTESE handles for garden lifecycle:
    - Season transitions
    - Health metrics
    - Auto-inducer integration

    AGENTESE: self.garden.*

    Metaphysical Fullstack (AD-009):
    The protocol IS the API. This node replaces:
    - /v1/gardener/garden (legacy route)
    - /v1/gardener/tending/* (legacy routes)
    """

    _handle: str = "self.garden"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Garden affordances available to all archetypes."""
        return GARDEN_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="View garden status",
        long_help="Show garden overview with plots, season, and health.",
        examples=["kg garden", "kg garden --json"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View garden status."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.projections.json import project_garden_to_json

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        result = project_garden_to_json(garden)

        return BasicRendering(
            summary="Garden Status",
            content=(
                f"Garden: {garden.name}\n"
                f"Season: {garden.season.emoji} {garden.season.name}\n"
                f"Plots: {len(garden.plots)}\n"
                f"Health: {garden.metrics.health_score:.0%}"
            ),
            metadata=result,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle garden-specific aspects."""
        match aspect:
            case "season":
                return await self._season(observer, **kwargs)
            case "health":
                return await self._health(observer, **kwargs)
            case "init":
                return await self._init(observer, **kwargs)
            case "transition":
                return await self._transition(observer, **kwargs)
            case "suggest":
                return await self._suggest(observer, **kwargs)
            case "accept":
                return await self._accept(observer, **kwargs)
            case "dismiss":
                return await self._dismiss(observer, **kwargs)
            case "tend" | "persona" | "inducer":
                # Return sub-node info
                return {
                    "sub_node": aspect,
                    "hint": f"Use self.garden.{aspect}.*",
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Show current season info",
        examples=["kg garden season"],
    )
    async def _season(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Get current season information."""
        from protocols.gardener_logos import create_garden

        garden = create_garden(name="kgents")
        season = garden.season

        return {
            "name": season.name,
            "emoji": season.emoji,
            "plasticity": season.plasticity,
            "entropy_multiplier": season.entropy_multiplier,
            "since": garden.season_since.isoformat(),
            "description": _season_description(season.name),
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Show health metrics",
        examples=["kg garden health"],
    )
    async def _health(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Get garden health metrics."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()
        garden.metrics.active_plots = len([p for p in garden.plots.values() if p.is_active])

        metrics = garden.metrics
        return {
            "health_score": metrics.health_score,
            "total_prompts": metrics.total_prompts,
            "active_plots": metrics.active_plots,
            "recent_gestures": metrics.recent_gestures,
            "session_cycles": metrics.session_cycles,
            "entropy_spent": metrics.entropy_spent,
            "entropy_budget": metrics.entropy_budget,
            "entropy_remaining": metrics.entropy_budget - metrics.entropy_spent,
            "health_bar": _progress_bar(metrics.health_score, 20),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Initialize garden with default plots",
        examples=["kg garden init"],
    )
    async def _init(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Initialize garden with crown jewel plots."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        return {
            "status": "initialized",
            "garden_id": garden.garden_id,
            "name": garden.name,
            "season": garden.season.name,
            "plots": list(garden.plots.keys()),
            "plot_count": len(garden.plots),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Transition to new season",
        examples=["kg garden transition SPROUTING"],
    )
    async def _transition(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Transition garden to a new season."""
        from protocols.gardener_logos import GardenSeason, create_garden

        target = kwargs.get("target") or kwargs.get("to") or kwargs.get("season")
        reason = kwargs.get("reason", "Manual transition")

        if not target:
            return {
                "status": "error",
                "message": "Target season required. Valid: DORMANT|SPROUTING|BLOOMING|HARVEST|COMPOSTING",
            }

        try:
            new_season = GardenSeason[target.upper()]
        except KeyError:
            valid = "|".join(s.name for s in GardenSeason)
            return {
                "status": "error",
                "message": f"Invalid season: {target}. Valid: {valid}",
            }

        garden = create_garden(name="kgents")
        old_season = garden.season
        garden.transition_season(new_season, reason)

        return {
            "status": "transitioned",
            "from_season": old_season.name,
            "from_emoji": old_season.emoji,
            "to_season": new_season.name,
            "to_emoji": new_season.emoji,
            "reason": reason,
            "old_plasticity": old_season.plasticity,
            "new_plasticity": new_season.plasticity,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Check for auto-inducer season suggestion",
        examples=["kg garden suggest"],
    )
    async def _suggest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Check for season transition suggestion."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.seasons import (
            TransitionSignals,
            suggest_season_transition,
        )

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()
        garden.metrics.active_plots = len([p for p in garden.plots.values() if p.is_active])

        signals = TransitionSignals.gather(garden)
        suggestion = suggest_season_transition(garden)

        if suggestion is None:
            return {
                "status": "no_suggestion",
                "current_season": garden.season.name,
                "signals": signals.to_dict(),
                "message": "Garden is content in its current season.",
            }

        return {
            "status": "suggestion",
            "from_season": suggestion.from_season.name,
            "to_season": suggestion.to_season.name,
            "confidence": suggestion.confidence,
            "reason": suggestion.reason,
            "signals": suggestion.signals.to_dict(),
            "should_suggest": suggestion.should_suggest,
            "confidence_bar": _progress_bar(suggestion.confidence, 10),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Accept auto-inducer transition suggestion",
        examples=["kg garden accept"],
    )
    async def _accept(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Accept current transition suggestion."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.seasons import (
            clear_dismissals,
            suggest_season_transition,
        )

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        suggestion = suggest_season_transition(garden)

        if suggestion is None or not suggestion.should_suggest:
            return {
                "status": "no_suggestion",
                "message": "No pending transition suggestion to accept.",
            }

        old_season = suggestion.from_season
        new_season = suggestion.to_season
        garden.transition_season(
            new_season, f"Accepted auto-inducer suggestion: {suggestion.reason}"
        )
        clear_dismissals(garden.garden_id)

        return {
            "status": "accepted",
            "from_season": old_season.name,
            "to_season": new_season.name,
            "reason": suggestion.reason,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Dismiss auto-inducer transition suggestion (4h cooldown)",
        examples=["kg garden dismiss"],
    )
    async def _dismiss(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Dismiss current transition suggestion."""
        from protocols.gardener_logos import create_crown_jewel_plots, create_garden
        from protocols.gardener_logos.seasons import (
            dismiss_transition,
            suggest_season_transition,
        )

        garden = create_garden(name="kgents")
        garden.plots = create_crown_jewel_plots()

        suggestion = suggest_season_transition(garden)

        if suggestion is None or not suggestion.should_suggest:
            return {
                "status": "no_suggestion",
                "message": "No pending transition suggestion to dismiss.",
            }

        dismiss_transition(garden.garden_id, suggestion.from_season, suggestion.to_season)

        return {
            "status": "dismissed",
            "from_season": suggestion.from_season.name,
            "to_season": suggestion.to_season.name,
            "cooldown_hours": 4,
        }


# Factory function
def create_garden_node() -> GardenNode:
    """Create a GardenNode for self.garden.* paths."""
    return GardenNode()


__all__ = [
    "GardenNode",
    "GARDEN_AFFORDANCES",
    "create_garden_node",
]
