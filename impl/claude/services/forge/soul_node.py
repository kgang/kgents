"""
Forge Soul AGENTESE Node: @node("world.forge.soul")

Exposes K-gent governance within the Forge context.

AGENTESE Paths:
- world.forge.soul.manifest - K-gent soul state
- world.forge.soul.vibe     - Personality eigenvectors

The Metaphysical Fullstack Pattern (AD-009):
- K-gent is the governance functor for the Forge
- Every Forge output passes through K-gent
- Soul presence is visible in the UI

See: spec/protocols/metaphysical-forge.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import SoulManifestResponse, SoulVibeResponse

if TYPE_CHECKING:
    from agents.k.soul import KgentSoul


# === Response Types ===


@dataclass(frozen=True)
class SoulManifestRendering:
    """Rendering for soul manifest."""

    mode: str
    eigenvectors: dict[str, float]
    session_interactions: int
    session_tokens: int
    has_llm: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "soul_manifest",
            "mode": self.mode,
            "eigenvectors": self.eigenvectors,
            "session_interactions": self.session_interactions,
            "session_tokens": self.session_tokens,
            "has_llm": self.has_llm,
        }

    def to_text(self) -> str:
        lines = [
            f"K-gent Soul: {self.mode}",
            f"Session: {self.session_interactions} interactions, {self.session_tokens} tokens",
            f"LLM: {'available' if self.has_llm else 'template mode'}",
            "Eigenvectors:",
        ]
        for key, value in self.eigenvectors.items():
            lines.append(f"  {key}: {value:.2f}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SoulVibeRendering:
    """Rendering for soul personality eigenvectors."""

    dimensions: dict[str, float]
    context: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "soul_vibe",
            "dimensions": self.dimensions,
            "context": self.context,
        }

    def to_text(self) -> str:
        lines = ["Kent's Personality Eigenvectors:", ""]
        for key, value in self.dimensions.items():
            bar = "=" * int(value * 20)
            lines.append(f"  {key:15} [{bar:<20}] {value:.2f}")
        lines.append("")
        lines.append(f"Context: {self.context[:100]}...")
        return "\n".join(lines)


# === ForgeSoulNode ===


@node(
    "world.forge.soul",
    description="K-gent governance for the Forge",
    contracts={
        "manifest": Response(SoulManifestResponse),
        "vibe": Response(SoulVibeResponse),
    },
)
class ForgeSoulNode(BaseLogosNode):
    """
    AGENTESE node for K-gent soul presence in the Forge.

    Provides:
    - Soul state manifest (mode, interactions, tokens)
    - Personality eigenvectors (6D Kent coordinates)

    This node is the UI entry point for K-gent presence in the Forge.
    """

    def __init__(self, kgent_soul: "KgentSoul | None" = None) -> None:
        """
        Initialize ForgeSoulNode.

        Args:
            kgent_soul: Optional KgentSoul instance. If None, returns dormant state.
        """
        self.soul = kgent_soul

    @property
    def handle(self) -> str:
        """The AGENTESE path for this node."""
        return "world.forge.soul"

    async def get_handle_info(self, observer: Observer) -> dict[str, Any]:
        """Return handle description for world.forge.soul."""
        meta = self._umwelt_to_meta(observer)
        return {
            "path": "world.forge.soul",
            "description": "K-gent governance soul for the Forge",
            "observer": {"archetype": observer.archetype},
            "affordances": self.affordances(meta),
            "features": {
                "soul_connected": self.soul is not None,
            },
        }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return available affordances."""
        # Soul state is readable by all archetypes
        return ("manifest", "vibe")

    async def manifest(self, observer: Observer) -> Renderable:
        """
        AGENTESE: world.forge.soul.manifest

        Returns K-gent soul state.
        """
        if self.soul is None:
            return BasicRendering(
                summary="K-gent soul not connected",
                metadata={
                    "type": "soul_manifest",
                    "mode": "dormant",
                    "eigenvectors": {},
                    "session_interactions": 0,
                    "session_tokens": 0,
                    "has_llm": False,
                },
            )

        # Get soul state
        state = self.soul.manifest_brief()
        eigenvectors = self.soul.eigenvectors.to_dict()

        return SoulManifestRendering(
            mode=state.get("active_mode", "unknown"),
            eigenvectors=eigenvectors,
            session_interactions=state.get("session_interactions", 0),
            session_tokens=state.get("session_tokens", 0),
            has_llm=state.get("has_llm", False),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "vibe":
            return await self._vibe(observer)

        # Unknown aspect
        return BasicRendering(
            summary=f"Unknown soul aspect: {aspect}",
            metadata={"error": "unknown_aspect", "aspect": aspect},
        )

    async def _vibe(self, observer: Observer) -> Renderable:
        """
        AGENTESE: world.forge.soul.vibe

        Returns personality eigenvectors with context prompt.
        """
        if self.soul is None:
            return BasicRendering(
                summary="K-gent soul not connected",
                metadata={
                    "type": "soul_vibe",
                    "dimensions": {},
                    "context": "",
                },
            )

        eigenvectors = self.soul.eigenvectors
        dimensions = eigenvectors.to_dict()
        context = eigenvectors.to_context_prompt()

        return SoulVibeRendering(
            dimensions=dimensions,
            context=context,
        )


__all__ = [
    "ForgeSoulNode",
    "SoulManifestRendering",
    "SoulVibeRendering",
]
