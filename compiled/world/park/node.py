"""
Park AGENTESE Node: world.park

Auto-generated from: spec/world/park.md
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Affordances
# =============================================================================


PARK_AFFORDANCES: tuple[str, ...] = ("manifest", "scenario", "mask", "force")


# =============================================================================
# Node Implementation
# =============================================================================


@node("world.park", description="Park service")
@dataclass
class ParkNode(BaseLogosNode):
    """
    world.park - Park AGENTESE node.

    TODO: Implement aspect methods.
    """

    _handle: str = "world.park"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PARK_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Manifest aspect",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Manifest aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Manifest",
            content="TODO: Implement manifest",
            metadata={},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Scenario aspect",
    )
    async def scenario(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Scenario aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Scenario",
            content="TODO: Implement scenario",
            metadata={},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Mask aspect",
    )
    async def mask(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Mask aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Mask",
            content="TODO: Implement mask",
            metadata={},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Force aspect",
    )
    async def force(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Force aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Force",
            content="TODO: Implement force",
            metadata={},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        aspect_methods: dict[str, Any] = {
            "manifest": self.manifest,
            "scenario": self.scenario,
            "mask": self.mask,
            "force": self.force,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "PARK_AFFORDANCES",
    "ParkNode",
]
