"""
Jewel-Flow AGENTESE Context

Integrates F-gent Flow modalities with Crown Jewels via AGENTESE paths.
Each jewel gets flow-specific paths for its natural modality:

- Brain + ChatFlow: `self.jewel.brain.flow.chat.*`

Note: Gestalt, Coalition, Park, Domain flow paths removed 2025-12-21.
Note: Gardener deprecated 2025-12-21. See spec/protocols/_archive/gardener-evergreen-heritage.md

See: plans/_continuations/f-gent-flow-implementation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Path Definitions
# =============================================================================

# Brain + ChatFlow paths (Hero Path Phase 2)
BRAIN_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.brain.flow.chat.manifest": {
        "aspect": "manifest",
        "description": "View Brain chat flow state",
        "effects": [],
    },
    "self.jewel.brain.flow.chat.query": {
        "aspect": "define",
        "description": "Query memory via conversational chat",
        "effects": ["TURN_COMPLETED", "MEMORY_SURFACED"],
    },
    "self.jewel.brain.flow.chat.history": {
        "aspect": "manifest",
        "description": "View chat query history",
        "effects": [],
    },
    "self.jewel.brain.flow.chat.reset": {
        "aspect": "define",
        "description": "Reset chat context",
        "effects": ["FLOW_COMPLETED"],
    },
}

# Gardener + ChatFlow paths - DEPRECATED 2025-12-21
GARDENER_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# Gestalt + ResearchFlow paths - REMOVED 2025-12-21
GESTALT_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# Atelier + ChatFlow + CollaborationFlow - DEPRECATED 2025-12-21
ATELIER_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# Coalition + CollaborationFlow - REMOVED 2025-12-21
COALITION_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# Park + CollaborationFlow + ChatFlow - REMOVED 2025-12-21
PARK_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# Domain + CollaborationFlow + ResearchFlow - REMOVED 2025-12-21
DOMAIN_FLOW_PATHS: dict[str, dict[str, Any]] = {}

# =============================================================================
# Combined Registry
# =============================================================================

# Hero Path paths (active paths only)
HERO_PATH_FLOW_PATHS: dict[str, dict[str, Any]] = {
    **BRAIN_FLOW_PATHS,
}

# All jewel-flow paths
ALL_JEWEL_FLOW_PATHS: dict[str, dict[str, Any]] = {
    **HERO_PATH_FLOW_PATHS,
}


# =============================================================================
# Affordances
# =============================================================================

BRAIN_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "query",
    "history",
    "reset",
)

GARDENER_FLOW_AFFORDANCES: tuple[str, ...] = ()  # Deprecated 2025-12-21

GESTALT_FLOW_AFFORDANCES: tuple[str, ...] = ()  # Removed 2025-12-21


# =============================================================================
# AGENTESE Nodes
# =============================================================================


@dataclass
class JewelFlowNode(BaseLogosNode):
    """
    Base node for jewel-specific flow paths.

    Provides common infrastructure for all jewel+flow integrations.
    """

    _handle: str = "self.jewel"
    _jewel_name: str = ""
    _modality: str = ""

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return affordances based on jewel and modality."""
        if self._jewel_name == "brain":
            return BRAIN_FLOW_AFFORDANCES
        return ()

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View jewel-flow state."""
        return BasicRendering(
            summary=f"{self._jewel_name.title()} Flow",
            content=f"Flow modality: {self._modality or 'none'}",
            metadata={
                "jewel": self._jewel_name,
                "modality": self._modality,
                "active": False,
            },
        )


@dataclass
class BrainFlowNode(JewelFlowNode):
    """
    self.jewel.brain.flow.chat - Brain's conversational memory interface.

    Wraps Brain operations in ChatFlow for turn-based querying.
    """

    _handle: str = "self.jewel.brain.flow.chat"
    _jewel_name: str = "brain"
    _modality: str = "chat"

    # Flow state
    _chat_flow: Any = None
    _query_history: list[dict[str, Any]] = field(default_factory=list)

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View Brain chat flow state."""
        return BasicRendering(
            summary="Brain Chat Flow",
            content=(f"Active: {self._chat_flow is not None}\nQueries: {len(self._query_history)}"),
            metadata={
                "jewel": "brain",
                "modality": "chat",
                "active": self._chat_flow is not None,
                "query_count": len(self._query_history),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Brain-specific chat aspects."""
        match aspect:
            case "query":
                return await self._query(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "reset":
                return await self._reset(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _query(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Query Brain via conversational chat."""
        query = kwargs.get("query") or kwargs.get("message")
        if not query:
            return {"error": "query is required"}

        # For now, delegate to Brain's semantic search
        try:
            from agents.brain import BrainCrystal

            brain = BrainCrystal.get_instance()
            results = brain.search(query, limit=kwargs.get("limit", 5))

            # Track query
            self._query_history.append(
                {
                    "query": query,
                    "result_count": len(results),
                }
            )

            return {
                "status": "success",
                "query": query,
                "results": [r.to_dict() for r in results] if results else [],
                "turn": len(self._query_history),
            }
        except ImportError:
            return {"error": "Brain not available"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get query history."""
        limit = kwargs.get("limit", 10)
        return {
            "queries": self._query_history[-limit:],
            "total": len(self._query_history),
        }

    async def _reset(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset chat context."""
        self._chat_flow = None
        self._query_history = []
        return {"status": "reset", "jewel": "brain", "modality": "chat"}


# =============================================================================
# Factory Functions
# =============================================================================


def create_brain_flow_node() -> BrainFlowNode:
    """Create a BrainFlowNode for self.jewel.brain.flow.chat.* paths."""
    return BrainFlowNode()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Path registries
    "BRAIN_FLOW_PATHS",
    "GARDENER_FLOW_PATHS",
    "GESTALT_FLOW_PATHS",
    "HERO_PATH_FLOW_PATHS",
    "ALL_JEWEL_FLOW_PATHS",
    # Deferred/removed paths (kept for backward compat, now empty)
    "ATELIER_FLOW_PATHS",
    "COALITION_FLOW_PATHS",
    "PARK_FLOW_PATHS",
    "DOMAIN_FLOW_PATHS",
    # Affordances
    "BRAIN_FLOW_AFFORDANCES",
    "GARDENER_FLOW_AFFORDANCES",
    "GESTALT_FLOW_AFFORDANCES",
    # Nodes
    "JewelFlowNode",
    "BrainFlowNode",
    # Factories
    "create_brain_flow_node",
]
