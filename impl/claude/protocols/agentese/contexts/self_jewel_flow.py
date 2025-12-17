"""
Jewel-Flow AGENTESE Context

Integrates F-gent Flow modalities with Crown Jewels via AGENTESE paths.
Each jewel gets flow-specific paths for its natural modality:

- Brain + ChatFlow: `self.jewel.brain.flow.chat.*`
- Gardener + ChatFlow: `self.jewel.gardener.flow.chat.*`
- Gestalt + ResearchFlow: `self.jewel.gestalt.flow.research.*`

Future (deferred):
- Atelier + ChatFlow + CollaborationFlow
- Coalition + CollaborationFlow
- Park + CollaborationFlow + ChatFlow
- Domain + CollaborationFlow + ResearchFlow

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

# Gardener + ChatFlow paths (Hero Path Phase 3)
GARDENER_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.gardener.flow.chat.manifest": {
        "aspect": "manifest",
        "description": "View Gardener chat flow state",
        "effects": [],
    },
    "self.jewel.gardener.flow.chat.tend": {
        "aspect": "define",
        "description": "Tend the garden via conversational chat",
        "effects": ["TURN_COMPLETED", "GESTURE_APPLIED"],
    },
    "self.jewel.gardener.flow.chat.suggest": {
        "aspect": "manifest",
        "description": "Get tending suggestions via chat",
        "effects": [],
    },
    "self.jewel.gardener.flow.chat.history": {
        "aspect": "manifest",
        "description": "View tending chat history",
        "effects": [],
    },
    "self.jewel.gardener.flow.chat.reset": {
        "aspect": "define",
        "description": "Reset chat context",
        "effects": ["FLOW_COMPLETED"],
    },
}

# Gestalt + ResearchFlow paths (Hero Path Phase 4)
GESTALT_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.gestalt.flow.research.manifest": {
        "aspect": "manifest",
        "description": "View Gestalt research flow state",
        "effects": [],
    },
    "self.jewel.gestalt.flow.research.explore": {
        "aspect": "define",
        "description": "Explore architecture via hypothesis tree",
        "effects": ["FLOW_STARTED", "HYPOTHESIS_CREATED"],
    },
    "self.jewel.gestalt.flow.research.tree": {
        "aspect": "manifest",
        "description": "View current hypothesis tree",
        "effects": [],
    },
    "self.jewel.gestalt.flow.research.branch": {
        "aspect": "define",
        "description": "Create new hypothesis branch",
        "effects": ["HYPOTHESIS_CREATED"],
    },
    "self.jewel.gestalt.flow.research.synthesize": {
        "aspect": "define",
        "description": "Synthesize insights from exploration",
        "effects": ["HYPOTHESIS_SYNTHESIZED", "ANALYSIS_COMPLETE"],
    },
    "self.jewel.gestalt.flow.research.reset": {
        "aspect": "define",
        "description": "Reset research flow",
        "effects": ["FLOW_COMPLETED"],
    },
}

# =============================================================================
# Deferred Paths (Future Phases)
# =============================================================================

# Atelier + ChatFlow + CollaborationFlow (deferred)
ATELIER_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.atelier.flow.chat.stream": {
        "aspect": "witness",
        "description": "Stream artisan creation",
        "effects": ["FLOW_STARTED"],
    },
    "self.jewel.atelier.flow.chat.bid": {
        "aspect": "define",
        "description": "Inject spectator bid into stream",
        "effects": ["BID_ACCEPTED"],
    },
    "self.jewel.atelier.flow.collaboration.canvas": {
        "aspect": "manifest",
        "description": "View multi-artisan canvas state",
        "effects": [],
    },
    "self.jewel.atelier.flow.collaboration.decide": {
        "aspect": "define",
        "description": "Reach consensus on style decision",
        "effects": ["CONSENSUS_REACHED"],
    },
}

# Coalition + CollaborationFlow (deferred)
COALITION_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.coalition.flow.collaboration.execute": {
        "aspect": "define",
        "description": "Execute task via collaboration flow",
        "effects": ["FLOW_STARTED", "TASK_ASSIGNED"],
    },
    "self.jewel.coalition.flow.collaboration.board": {
        "aspect": "manifest",
        "description": "View task blackboard state",
        "effects": [],
    },
    "self.jewel.coalition.flow.collaboration.handoff": {
        "aspect": "define",
        "description": "Trigger handoff between agents",
        "effects": ["CONTRIBUTION_POSTED"],
    },
    "self.jewel.coalition.flow.collaboration.decide": {
        "aspect": "define",
        "description": "Reach consensus on output",
        "effects": ["CONSENSUS_REACHED"],
    },
}

# Park + CollaborationFlow + ChatFlow (deferred)
PARK_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.park.flow.chat.director": {
        "aspect": "define",
        "description": "Director-player interaction",
        "effects": ["TURN_COMPLETED"],
    },
    "self.jewel.park.flow.chat.force": {
        "aspect": "define",
        "description": "Use force mechanic (consent debt)",
        "effects": ["FORCE_USED"],
    },
    "self.jewel.park.flow.collaboration.scene": {
        "aspect": "manifest",
        "description": "View citizen scene state",
        "effects": [],
    },
    "self.jewel.park.flow.collaboration.reveal": {
        "aspect": "define",
        "description": "Reveal information in scene",
        "effects": ["CONTRIBUTION_POSTED"],
    },
}

# Domain + CollaborationFlow + ResearchFlow (deferred)
DOMAIN_FLOW_PATHS: dict[str, dict[str, Any]] = {
    "self.jewel.domain.flow.collaboration.drill": {
        "aspect": "define",
        "description": "Execute drill via collaboration",
        "effects": ["DRILL_STARTED", "FLOW_STARTED"],
    },
    "self.jewel.domain.flow.collaboration.decide": {
        "aspect": "define",
        "description": "Team decision under timer pressure",
        "effects": ["CONSENSUS_REACHED"],
    },
    "self.jewel.domain.flow.research.investigate": {
        "aspect": "define",
        "description": "Investigate incident via hypotheses",
        "effects": ["HYPOTHESIS_CREATED"],
    },
    "self.jewel.domain.flow.research.synthesize": {
        "aspect": "define",
        "description": "Synthesize root cause analysis",
        "effects": ["HYPOTHESIS_SYNTHESIZED"],
    },
}

# =============================================================================
# Combined Registry
# =============================================================================

# Hero Path paths (Phase 1 scope)
HERO_PATH_FLOW_PATHS: dict[str, dict[str, Any]] = {
    **BRAIN_FLOW_PATHS,
    **GARDENER_FLOW_PATHS,
    **GESTALT_FLOW_PATHS,
}

# All jewel-flow paths (including deferred)
ALL_JEWEL_FLOW_PATHS: dict[str, dict[str, Any]] = {
    **HERO_PATH_FLOW_PATHS,
    # Deferred - uncomment when implemented
    # **ATELIER_FLOW_PATHS,
    # **COALITION_FLOW_PATHS,
    # **PARK_FLOW_PATHS,
    # **DOMAIN_FLOW_PATHS,
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

GARDENER_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "tend",
    "suggest",
    "history",
    "reset",
)

GESTALT_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "explore",
    "tree",
    "branch",
    "synthesize",
    "reset",
)


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
        elif self._jewel_name == "gardener":
            return GARDENER_FLOW_AFFORDANCES
        elif self._jewel_name == "gestalt":
            return GESTALT_FLOW_AFFORDANCES
        return ()

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
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

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View Brain chat flow state."""
        return BasicRendering(
            summary="Brain Chat Flow",
            content=(
                f"Active: {self._chat_flow is not None}\n"
                f"Queries: {len(self._query_history)}"
            ),
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
        # Full ChatFlow integration in Phase 2
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


@dataclass
class GardenerFlowNode(JewelFlowNode):
    """
    self.jewel.gardener.flow.chat - Gardener's conversational tending interface.

    Wraps Gardener operations in ChatFlow for turn-based tending.
    """

    _handle: str = "self.jewel.gardener.flow.chat"
    _jewel_name: str = "gardener"
    _modality: str = "chat"

    # Flow state
    _chat_flow: Any = None
    _tending_history: list[dict[str, Any]] = field(default_factory=list)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View Gardener chat flow state."""
        return BasicRendering(
            summary="Gardener Chat Flow",
            content=(
                f"Active: {self._chat_flow is not None}\n"
                f"Gestures: {len(self._tending_history)}"
            ),
            metadata={
                "jewel": "gardener",
                "modality": "chat",
                "active": self._chat_flow is not None,
                "gesture_count": len(self._tending_history),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Gardener-specific chat aspects."""
        match aspect:
            case "tend":
                return await self._tend(observer, **kwargs)
            case "suggest":
                return await self._suggest(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "reset":
                return await self._reset(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _tend(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Tend the garden via conversational chat."""
        intent = kwargs.get("intent") or kwargs.get("message")
        if not intent:
            return {"error": "intent is required"}

        # Track tending
        self._tending_history.append(
            {
                "intent": intent,
                "timestamp": "now",
            }
        )

        # Placeholder - full implementation in Phase 3
        return {
            "status": "received",
            "intent": intent,
            "note": "Full ChatFlow integration coming in Phase 3",
            "turn": len(self._tending_history),
        }

    async def _suggest(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get tending suggestions."""
        # Placeholder - full implementation in Phase 3
        return {
            "suggestions": [
                {
                    "verb": "OBSERVE",
                    "target": "self.forest",
                    "reason": "Check forest health",
                },
                {
                    "verb": "WATER",
                    "target": "world.atelier",
                    "reason": "Low progress plot",
                },
            ],
            "note": "Full suggestion system in Phase 3",
        }

    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get tending history."""
        limit = kwargs.get("limit", 10)
        return {
            "gestures": self._tending_history[-limit:],
            "total": len(self._tending_history),
        }

    async def _reset(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset chat context."""
        self._chat_flow = None
        self._tending_history = []
        return {"status": "reset", "jewel": "gardener", "modality": "chat"}


@dataclass
class GestaltFlowNode(JewelFlowNode):
    """
    self.jewel.gestalt.flow.research - Gestalt's architecture exploration interface.

    Wraps Gestalt operations in ResearchFlow for hypothesis-driven analysis.
    """

    _handle: str = "self.jewel.gestalt.flow.research"
    _jewel_name: str = "gestalt"
    _modality: str = "research"

    # Flow state
    _research_flow: Any = None
    _hypotheses: list[dict[str, Any]] = field(default_factory=list)
    _current_question: str | None = None

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View Gestalt research flow state."""
        return BasicRendering(
            summary="Gestalt Research Flow",
            content=(
                f"Active: {self._research_flow is not None}\n"
                f"Question: {self._current_question or 'none'}\n"
                f"Hypotheses: {len(self._hypotheses)}"
            ),
            metadata={
                "jewel": "gestalt",
                "modality": "research",
                "active": self._research_flow is not None,
                "question": self._current_question,
                "hypothesis_count": len(self._hypotheses),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Gestalt-specific research aspects."""
        match aspect:
            case "explore":
                return await self._explore(observer, **kwargs)
            case "tree":
                return await self._get_tree(observer, **kwargs)
            case "branch":
                return await self._branch(observer, **kwargs)
            case "synthesize":
                return await self._synthesize(observer, **kwargs)
            case "reset":
                return await self._reset(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _explore(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Start architecture exploration with a question."""
        question = kwargs.get("question")
        if not question:
            return {"error": "question is required"}

        self._current_question = question
        self._hypotheses = []

        # Create initial hypothesis
        root_hypothesis = {
            "id": "h0",
            "content": f"Root: {question}",
            "parent_id": None,
            "depth": 0,
            "status": "exploring",
            "confidence": 0.5,
        }
        self._hypotheses.append(root_hypothesis)

        return {
            "status": "exploring",
            "question": question,
            "root_hypothesis": root_hypothesis,
            "note": "Full ResearchFlow integration in Phase 4",
        }

    async def _get_tree(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current hypothesis tree."""
        return {
            "question": self._current_question,
            "hypotheses": self._hypotheses,
            "depth": max((h.get("depth", 0) for h in self._hypotheses), default=0),
        }

    async def _branch(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new hypothesis branch."""
        hypothesis = kwargs.get("hypothesis")
        parent_id = kwargs.get("parent_id", "h0")

        if not hypothesis:
            return {"error": "hypothesis is required"}

        # Find parent depth
        parent_depth = 0
        for h in self._hypotheses:
            if h.get("id") == parent_id:
                parent_depth = h.get("depth", 0)
                break

        new_h = {
            "id": f"h{len(self._hypotheses)}",
            "content": hypothesis,
            "parent_id": parent_id,
            "depth": parent_depth + 1,
            "status": "exploring",
            "confidence": 0.5,
        }
        self._hypotheses.append(new_h)

        return {
            "status": "branched",
            "hypothesis": new_h,
        }

    async def _synthesize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Synthesize insights from exploration."""
        if not self._hypotheses:
            return {"error": "No hypotheses to synthesize"}

        # Placeholder synthesis
        return {
            "status": "synthesized",
            "question": self._current_question,
            "answer": f"Based on {len(self._hypotheses)} hypotheses...",
            "confidence": 0.7,
            "insights": [
                {"content": "Placeholder insight 1", "confidence": 0.8},
                {"content": "Placeholder insight 2", "confidence": 0.6},
            ],
            "note": "Full synthesis in Phase 4",
        }

    async def _reset(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset research flow."""
        self._research_flow = None
        self._hypotheses = []
        self._current_question = None
        return {"status": "reset", "jewel": "gestalt", "modality": "research"}


# =============================================================================
# Factory Functions
# =============================================================================


def create_brain_flow_node() -> BrainFlowNode:
    """Create a BrainFlowNode for self.jewel.brain.flow.chat.* paths."""
    return BrainFlowNode()


def create_gardener_flow_node() -> GardenerFlowNode:
    """Create a GardenerFlowNode for self.jewel.gardener.flow.chat.* paths."""
    return GardenerFlowNode()


def create_gestalt_flow_node() -> GestaltFlowNode:
    """Create a GestaltFlowNode for self.jewel.gestalt.flow.research.* paths."""
    return GestaltFlowNode()


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
    # Deferred paths
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
    "GardenerFlowNode",
    "GestaltFlowNode",
    # Factories
    "create_brain_flow_node",
    "create_gardener_flow_node",
    "create_gestalt_flow_node",
]
