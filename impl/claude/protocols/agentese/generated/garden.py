"""
JIT-Generated LogosNode for world.garden

Generated from: spec/world/garden.md
Version: 1.0

A space for growing things.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from impl.claude.protocols.agentese.node import AgentMeta, Renderable

    from bootstrap.umwelt import Umwelt

# Archetype -> affordances mapping
AFFORDANCES: dict[str, tuple[str, ...]] = {
    "architect": ("blueprint", "measure",),
    "poet": ("describe", "contemplate",),
    "default": ("inspect",),
}


class JITGardenNode:
    """
    LogosNode for world.garden.

    A space for growing things.
    """

    @property
    def handle(self) -> str:
        return "world.garden"

    # Base affordances available to all
    _base_affordances: tuple[str, ...] = ("manifest", "witness", "affordances")

    def affordances(self, observer: "AgentMeta") -> list[str]:
        """Return observer-specific affordances."""
        base = list(self._base_affordances)
        extra = AFFORDANCES.get(observer.archetype, AFFORDANCES.get("default", ()))
        return base + list(extra)

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        return AFFORDANCES.get(archetype, AFFORDANCES.get("default", ()))

    def lens(self, aspect: str) -> Any:
        """Return composable agent for aspect."""
        from impl.claude.protocols.agentese.node import AspectAgent
        return AspectAgent(self, aspect)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> "Renderable":
        """Collapse to observer-appropriate representation."""
        from impl.claude.protocols.agentese.node import BasicRendering

        dna = observer.dna
        archetype = getattr(dna, "archetype", "default")
        if archetype == "architect":
            from impl.claude.protocols.agentese.node import BlueprintRendering
            return BlueprintRendering(
                dimensions={"entity": "A space for growing things."},
                materials=(),
                structural_analysis={},
            )
        if archetype == "poet":
            from impl.claude.protocols.agentese.node import PoeticRendering
            return PoeticRendering(
                description="A space for growing things.",
                metaphors=(),
                mood="contemplative",
            )

        # Default rendering
        return BasicRendering(
            summary="A space for growing things.",
            content="JIT-generated node for A space for growing things.",
        )

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Execute an aspect on this node."""
        if aspect == "manifest":
            return await self.manifest(observer)
        if aspect == "affordances":
            from impl.claude.protocols.agentese.node import AgentMeta
            dna = observer.dna
            meta = AgentMeta(
                name=getattr(dna, "name", "unknown"),
                archetype=getattr(dna, "archetype", "default"),
            )
            return self.affordances(meta)
        if aspect == "blueprint":
            return {"aspect": "blueprint", "behavior": "Execute blueprint operation", "kwargs": kwargs}
        if aspect == "contemplate":
            return {"aspect": "contemplate", "behavior": "Execute contemplate operation", "kwargs": kwargs}
        if aspect == "describe":
            return {"aspect": "describe", "behavior": "Execute describe operation", "kwargs": kwargs}
        if aspect == "inspect":
            return {"aspect": "inspect", "behavior": "Execute inspect operation", "kwargs": kwargs}
        if aspect == "measure":
            return {"aspect": "measure", "behavior": "Execute measure operation", "kwargs": kwargs}

        # Unknown aspect
        return {"aspect": aspect, "status": "not_implemented", "kwargs": kwargs}
