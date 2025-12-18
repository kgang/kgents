"""
Chat AGENTESE Node: self.chat

Auto-generated from: spec/self/chat.md
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


CHAT_AFFORDANCES: tuple[str, ...] = ("manifest", "converse", "research")


# =============================================================================
# Node Implementation
# =============================================================================


@node("self.chat", description="Chat service")
@dataclass
class ChatNode(BaseLogosNode):
    """
    self.chat - Chat AGENTESE node.

    TODO: Implement aspect methods.
    """

    _handle: str = "self.chat"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return CHAT_AFFORDANCES

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
        help="Converse aspect",
    )
    async def converse(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Converse aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Converse",
            content="TODO: Implement converse",
            metadata={},
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Research aspect",
    )
    async def research(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        Research aspect.

        TODO: Implement actual logic.
        """
        return BasicRendering(
            summary="Research",
            content="TODO: Implement research",
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
            "converse": self.converse,
            "research": self.research,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "CHAT_AFFORDANCES",
    "ChatNode",
]
