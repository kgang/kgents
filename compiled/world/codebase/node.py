"""
Codebase AGENTESE Node: world.codebase

Auto-generated from: spec/world/codebase.md
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


CODEBASE_AFFORDANCES: tuple[str, ...] = ("manifest", "scan", "analyze")


# =============================================================================
# Node Implementation
# =============================================================================


@node("world.codebase", description="Codebase service")
@dataclass
class CodebaseNode(BaseLogosNode):
    """
    world.codebase - Codebase AGENTESE node.

    TODO: Implement aspect methods.
    """

    _handle: str = "world.codebase"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return CODEBASE_AFFORDANCES

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
        help="Scan aspect",
    )
    async def scan(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Scan aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Scan",
            content="TODO: Implement scan",
            metadata={},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Analyze aspect",
    )
    async def analyze(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Analyze aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Analyze",
            content="TODO: Implement analyze",
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
            "scan": self.scan,
            "analyze": self.analyze,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "CODEBASE_AFFORDANCES",
    "CodebaseNode",
]
