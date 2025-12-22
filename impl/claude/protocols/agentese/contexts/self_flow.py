"""
AGENTESE Self Flow Context

Flow-related nodes for self.flow.* paths:
- FlowNode: The agent's flow (chat/research/collaboration) subsystem
- ChatFlowNode: Chat modality state and operations
- ResearchFlowNode: Research/hypothesis tree state
- CollaborationFlowNode: Multi-agent blackboard state

F-gent Flow provides three conversational modalities:
1. Chat: Streaming conversation with context management
2. Research: Tree of thought exploration with hypothesis tracking
3. Collaboration: Multi-agent blackboard patterns

Note: This is distinct from agents.flux (streaming functor infrastructure).
Flow is about conversational *modalities*, Flux is about *stream processing*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Flow Affordances ===

FLOW_AFFORDANCES: tuple[str, ...] = (
    # State inspection
    "state",  # Get current FlowState
    "modality",  # Get current modality (chat/research/collaboration)
    "entropy",  # Get remaining entropy budget
    # Operations
    "start",  # Start a flow
    "stop",  # Stop a flow
    "reset",  # Reset flow state
    # Chat-specific
    "context",  # Get current context window
    "history",  # Get chat history
    "turn",  # Current turn number
    # Research-specific
    "tree",  # Get hypothesis tree
    "branch",  # Create new branch
    "synthesize",  # Synthesize insights
    # Collaboration-specific
    "board",  # Get blackboard state
    "post",  # Post contribution
    "vote",  # Vote on proposal
    "decide",  # Make decision
)

CHAT_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "context",
    "history",
    "turn",
    "metrics",
    "send",
    "reset",
)

RESEARCH_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "tree",
    "branch",
    "refute",
    "support",
    "synthesize",
    "insights",
)

COLLABORATION_FLOW_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "board",
    "post",
    "vote",
    "propose",
    "decide",
    "contributions",
)


# === Flow Node ===


@dataclass
class FlowNode(BaseLogosNode):
    """
    self.flow - The agent's conversational flow subsystem.

    Provides access to F-gent Flow modalities:
    - Chat: Streaming conversation with context management
    - Research: Tree of thought exploration
    - Collaboration: Multi-agent blackboard patterns

    AGENTESE: self.flow.*

    Note: This is distinct from agents.flux (streaming infrastructure).
    Flow = conversational modalities, Flux = stream processing.
    """

    _handle: str = "self.flow"

    # Active flows by modality
    _chat_flow: Any = None  # ChatFlow from agents.f
    _research_flow: Any = None  # ResearchFlow from agents.f
    _collaboration_flow: Any = None  # CollaborationFlow from agents.f

    # Current active modality
    _active_modality: str | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Flow affordances available to all archetypes."""
        return FLOW_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current flow state."""
        active_flows = []
        if self._chat_flow is not None:
            active_flows.append("chat")
        if self._research_flow is not None:
            active_flows.append("research")
        if self._collaboration_flow is not None:
            active_flows.append("collaboration")

        return BasicRendering(
            summary="Flow State",
            content=(
                f"Active modality: {self._active_modality or 'none'}\n"
                f"Available flows: {active_flows or 'none configured'}"
            ),
            metadata={
                "active_modality": self._active_modality,
                "available_flows": active_flows,
                "has_chat": self._chat_flow is not None,
                "has_research": self._research_flow is not None,
                "has_collaboration": self._collaboration_flow is not None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle flow-specific aspects."""
        match aspect:
            case "state":
                return await self._get_state(observer, **kwargs)
            case "modality":
                return self._active_modality or "none"
            case "entropy":
                return await self._get_entropy(observer, **kwargs)
            case "start":
                return await self._start_flow(observer, **kwargs)
            case "stop":
                return await self._stop_flow(observer, **kwargs)
            case "reset":
                return await self._reset_flow(observer, **kwargs)
            # Chat shortcuts
            case "context":
                return await self._get_context(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "turn":
                return await self._get_turn(observer, **kwargs)
            # Research shortcuts
            case "tree":
                return await self._get_tree(observer, **kwargs)
            case "branch":
                return await self._create_branch(observer, **kwargs)
            case "synthesize":
                return await self._synthesize(observer, **kwargs)
            # Collaboration shortcuts
            case "board":
                return await self._get_board(observer, **kwargs)
            case "post":
                return await self._post_contribution(observer, **kwargs)
            case "vote":
                return await self._vote(observer, **kwargs)
            case "decide":
                return await self._decide(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # === State Operations ===

    async def _get_state(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current flow state."""
        try:
            from agents.f import FlowState

            if self._chat_flow is not None:
                return {
                    "modality": "chat",
                    "state": self._chat_flow.state.value
                    if hasattr(self._chat_flow, "state")
                    else "unknown",
                }
            if self._research_flow is not None:
                return {
                    "modality": "research",
                    "state": self._research_flow.state.value
                    if hasattr(self._research_flow, "state")
                    else "unknown",
                }
            if self._collaboration_flow is not None:
                return {
                    "modality": "collaboration",
                    "state": self._collaboration_flow.state.value
                    if hasattr(self._collaboration_flow, "state")
                    else "unknown",
                }
            return {"state": FlowState.DORMANT.value, "modality": None}
        except ImportError:
            return {
                "state": "dormant",
                "modality": None,
                "note": "F-gent not installed",
            }

    async def _get_entropy(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get remaining entropy budget."""
        # Entropy is tracked per-flow
        for flow in [self._chat_flow, self._research_flow, self._collaboration_flow]:
            if flow is not None and hasattr(flow, "_entropy"):
                return {"entropy": flow._entropy}
        return {"entropy": 1.0, "note": "no active flow"}

    async def _start_flow(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Start a flow with the specified modality.

        AGENTESE: self.flow.start[modality="chat", config={...}]

        Note: Most flows require an agent. Call with agent= kwarg or
        use the dedicated modality sub-nodes which configure agents.
        """
        modality = kwargs.get("modality", "chat")
        config = kwargs.get("config", {})

        # Check if we have a pre-configured flow
        if modality == "chat" and self._chat_flow is not None:
            self._active_modality = "chat"
            return {"status": "already_started", "modality": "chat"}
        if modality == "research" and self._research_flow is not None:
            self._active_modality = "research"
            return {"status": "already_started", "modality": "research"}
        if modality == "collaboration" and self._collaboration_flow is not None:
            self._active_modality = "collaboration"
            return {"status": "already_started", "modality": "collaboration"}

        # Starting a flow requires an agent in most cases
        # For now, return a "prepared" status that indicates ready for messages
        try:
            from agents.f import ChatConfig, FlowConfig, ResearchConfig

            if modality == "chat":
                # Mark as ready - actual ChatFlow requires agent at message time
                self._active_modality = "chat"
                return {
                    "status": "prepared",
                    "modality": "chat",
                    "config": config,
                    "note": "Flow prepared. Use self.flow.chat.send[message=...] with an agent.",
                }

            elif modality == "research":
                self._active_modality = "research"
                return {
                    "status": "prepared",
                    "modality": "research",
                    "config": config,
                    "note": "Flow prepared. Use self.flow.research.branch[...] to start exploring.",
                }

            elif modality == "collaboration":
                self._active_modality = "collaboration"
                return {
                    "status": "prepared",
                    "modality": "collaboration",
                    "config": config,
                    "note": "Flow prepared. Use self.flow.collaboration.post[...] to contribute.",
                }

            else:
                return {
                    "error": f"Unknown modality: {modality}",
                    "valid": ["chat", "research", "collaboration"],
                }

        except ImportError as e:
            return {"error": f"F-gent not available: {e}"}

    async def _stop_flow(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Stop the current flow."""
        modality = kwargs.get("modality", self._active_modality)

        if modality == "chat" and self._chat_flow is not None:
            self._chat_flow = None
        elif modality == "research" and self._research_flow is not None:
            self._research_flow = None
        elif modality == "collaboration" and self._collaboration_flow is not None:
            self._collaboration_flow = None

        if modality == self._active_modality:
            self._active_modality = None

        return {"status": "stopped", "modality": modality}

    async def _reset_flow(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset flow state."""
        modality = kwargs.get("modality", self._active_modality)

        if modality == "chat" and self._chat_flow is not None:
            self._chat_flow.reset()
            return {"status": "reset", "modality": "chat"}
        elif modality == "research" and self._research_flow is not None:
            self._research_flow.reset()
            return {"status": "reset", "modality": "research"}
        elif modality == "collaboration" and self._collaboration_flow is not None:
            self._collaboration_flow.reset()
            return {"status": "reset", "modality": "collaboration"}

        return {"status": "no_flow_to_reset", "modality": modality}

    # === Chat Operations ===

    async def _get_context(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get current chat context window."""
        if self._chat_flow is None:
            return {
                "error": "No chat flow active",
                "usage": "self.flow.start[modality='chat']",
            }

        try:
            context = self._chat_flow.get_context()
            return {
                "messages": len(context),
                "tokens": self._chat_flow.current_tokens
                if hasattr(self._chat_flow, "current_tokens")
                else "unknown",
                "strategy": self._chat_flow.context_strategy
                if hasattr(self._chat_flow, "context_strategy")
                else "unknown",
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get chat history."""
        if self._chat_flow is None:
            return {"error": "No chat flow active"}

        limit = kwargs.get("limit", 10)
        try:
            history = self._chat_flow.get_history()
            return {
                "turns": len(history),
                "recent": history[-limit:] if len(history) > limit else history,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_turn(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> int:
        """Get current turn number."""
        if self._chat_flow is None:
            return 0
        return getattr(self._chat_flow, "_turn_count", 0)

    # === Research Operations ===

    async def _get_tree(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get hypothesis tree state."""
        if self._research_flow is None:
            return {
                "error": "No research flow active",
                "usage": "self.flow.start[modality='research']",
            }

        try:
            tree = self._research_flow.tree
            return {
                "root": tree.root.content if tree.root else None,
                "branches": len(tree.branches) if hasattr(tree, "branches") else 0,
                "depth": tree.max_depth if hasattr(tree, "max_depth") else "unknown",
            }
        except Exception as e:
            return {"error": str(e)}

    async def _create_branch(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new hypothesis branch."""
        if self._research_flow is None:
            return {"error": "No research flow active"}

        hypothesis = kwargs.get("hypothesis")
        if not hypothesis:
            return {"error": "hypothesis is required"}

        parent_id = kwargs.get("parent_id")

        try:
            branch = self._research_flow.branch(hypothesis, parent_id=parent_id)
            return {
                "status": "created",
                "branch_id": branch.id if hasattr(branch, "id") else "unknown",
                "hypothesis": hypothesis,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _synthesize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Synthesize insights from hypothesis tree."""
        if self._research_flow is None:
            return {"error": "No research flow active"}

        try:
            synthesis = self._research_flow.synthesize()
            return {
                "status": "synthesized",
                "insights": synthesis.insights if hasattr(synthesis, "insights") else [],
                "confidence": synthesis.confidence
                if hasattr(synthesis, "confidence")
                else "unknown",
            }
        except Exception as e:
            return {"error": str(e)}

    # === Collaboration Operations ===

    async def _get_board(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get blackboard state."""
        if self._collaboration_flow is None:
            return {
                "error": "No collaboration flow active",
                "usage": "self.flow.start[modality='collaboration']",
            }

        try:
            board = self._collaboration_flow.blackboard
            return {
                "contributions": len(board.contributions) if hasattr(board, "contributions") else 0,
                "proposals": len(board.proposals) if hasattr(board, "proposals") else 0,
                "decisions": len(board.decisions) if hasattr(board, "decisions") else 0,
                "current_round": board.current_round
                if hasattr(board, "current_round")
                else "unknown",
            }
        except Exception as e:
            return {"error": str(e)}

    async def _post_contribution(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Post a contribution to the blackboard."""
        if self._collaboration_flow is None:
            return {"error": "No collaboration flow active"}

        content = kwargs.get("content")
        contribution_type = kwargs.get("type", "idea")

        if not content:
            return {"error": "content is required"}

        try:
            posted_result = self._collaboration_flow.post(
                content=content,
                agent_id=self._umwelt_to_meta(observer).name,
                contribution_type=contribution_type,
            )
            return {
                "status": "posted",
                "contribution_id": posted_result.id if hasattr(posted_result, "id") else "unknown",
                "type": contribution_type,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _vote(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Vote on a proposal."""
        if self._collaboration_flow is None:
            return {"error": "No collaboration flow active"}

        proposal_id = kwargs.get("proposal_id")
        vote_value = kwargs.get("vote", "approve")  # approve, reject, abstain

        if not proposal_id:
            return {"error": "proposal_id is required"}

        try:
            self._collaboration_flow.vote(
                proposal_id=proposal_id,
                agent_id=self._umwelt_to_meta(observer).name,
                vote=vote_value,
            )
            return {
                "status": "voted",
                "proposal_id": proposal_id,
                "vote": vote_value,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _decide(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a decision on a proposal."""
        if self._collaboration_flow is None:
            return {"error": "No collaboration flow active"}

        proposal_id = kwargs.get("proposal_id")

        if not proposal_id:
            return {"error": "proposal_id is required"}

        try:
            decision = self._collaboration_flow.decide(proposal_id=proposal_id)
            return {
                "status": "decided",
                "proposal_id": proposal_id,
                "outcome": decision.outcome if hasattr(decision, "outcome") else "unknown",
                "votes": decision.vote_summary if hasattr(decision, "vote_summary") else {},
            }
        except Exception as e:
            return {"error": str(e)}


# === Modality-Specific Sub-Nodes ===


@dataclass
class ChatFlowNode(BaseLogosNode):
    """
    self.flow.chat - Chat modality operations.

    AGENTESE: self.flow.chat.*
    """

    _handle: str = "self.flow.chat"
    _parent_flow: FlowNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return CHAT_FLOW_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View chat flow state."""
        if self._parent_flow is None or self._parent_flow._chat_flow is None:
            return BasicRendering(
                summary="Chat Flow",
                content="No chat flow active",
                metadata={"active": False},
            )

        chat = self._parent_flow._chat_flow
        return BasicRendering(
            summary="Chat Flow State",
            content=(
                f"Turn: {getattr(chat, '_turn_count', 0)}\n"
                f"Messages: {len(getattr(chat, '_messages', []))}"
            ),
            metadata={
                "active": True,
                "turn_count": getattr(chat, "_turn_count", 0),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Delegate to parent flow's chat operations."""
        if self._parent_flow is None:
            return {"error": "No parent flow configured"}

        match aspect:
            case "context":
                return await self._parent_flow._get_context(observer, **kwargs)
            case "history":
                return await self._parent_flow._get_history(observer, **kwargs)
            case "turn":
                return await self._parent_flow._get_turn(observer, **kwargs)
            case "metrics":
                return await self._get_metrics(observer, **kwargs)
            case "send":
                return await self._send_message(observer, **kwargs)
            case "reset":
                return await self._parent_flow._reset_flow(observer, modality="chat", **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_metrics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get chat metrics."""
        if self._parent_flow is None or self._parent_flow._chat_flow is None:
            return {"error": "No chat flow active"}

        chat = self._parent_flow._chat_flow
        try:
            metrics: dict[str, Any] = chat.get_metrics()
            return metrics
        except Exception:
            return {
                "turn_count": getattr(chat, "_turn_count", 0),
                "message_count": len(getattr(chat, "_messages", [])),
            }

    async def _send_message(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a message in the chat flow."""
        if self._parent_flow is None or self._parent_flow._chat_flow is None:
            return {"error": "No chat flow active"}

        message = kwargs.get("message")
        if not message:
            return {"error": "message is required"}

        chat = self._parent_flow._chat_flow
        try:
            response = await chat.send_message(message)
            return {
                "status": "sent",
                "response": response,
            }
        except Exception as e:
            return {"error": str(e)}


@dataclass
class ResearchFlowNode(BaseLogosNode):
    """
    self.flow.research - Research modality operations.

    AGENTESE: self.flow.research.*
    """

    _handle: str = "self.flow.research"
    _parent_flow: FlowNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return RESEARCH_FLOW_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View research flow state."""
        if self._parent_flow is None or self._parent_flow._research_flow is None:
            return BasicRendering(
                summary="Research Flow",
                content="No research flow active",
                metadata={"active": False},
            )

        research = self._parent_flow._research_flow
        return BasicRendering(
            summary="Research Flow State",
            content="Research flow active with hypothesis tree",
            metadata={
                "active": True,
                "has_tree": hasattr(research, "tree"),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Delegate to parent flow's research operations."""
        if self._parent_flow is None:
            return {"error": "No parent flow configured"}

        match aspect:
            case "tree":
                return await self._parent_flow._get_tree(observer, **kwargs)
            case "branch":
                return await self._parent_flow._create_branch(observer, **kwargs)
            case "refute":
                return await self._refute_hypothesis(observer, **kwargs)
            case "support":
                return await self._support_hypothesis(observer, **kwargs)
            case "synthesize":
                return await self._parent_flow._synthesize(observer, **kwargs)
            case "insights":
                return await self._get_insights(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _refute_hypothesis(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add refuting evidence to a hypothesis."""
        if self._parent_flow is None or self._parent_flow._research_flow is None:
            return {"error": "No research flow active"}

        hypothesis_id = kwargs.get("hypothesis_id")
        evidence = kwargs.get("evidence")

        if not hypothesis_id or not evidence:
            return {"error": "hypothesis_id and evidence are required"}

        try:
            research = self._parent_flow._research_flow
            research.refute(hypothesis_id, evidence)
            return {"status": "refuted", "hypothesis_id": hypothesis_id}
        except Exception as e:
            return {"error": str(e)}

    async def _support_hypothesis(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add supporting evidence to a hypothesis."""
        if self._parent_flow is None or self._parent_flow._research_flow is None:
            return {"error": "No research flow active"}

        hypothesis_id = kwargs.get("hypothesis_id")
        evidence = kwargs.get("evidence")

        if not hypothesis_id or not evidence:
            return {"error": "hypothesis_id and evidence are required"}

        try:
            research = self._parent_flow._research_flow
            research.support(hypothesis_id, evidence)
            return {"status": "supported", "hypothesis_id": hypothesis_id}
        except Exception as e:
            return {"error": str(e)}

    async def _get_insights(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get accumulated insights."""
        if self._parent_flow is None or self._parent_flow._research_flow is None:
            return {"error": "No research flow active"}

        try:
            research = self._parent_flow._research_flow
            insights = getattr(research, "insights", [])
            return {"insights": insights, "count": len(insights)}
        except Exception as e:
            return {"error": str(e)}


@dataclass
class CollaborationFlowNode(BaseLogosNode):
    """
    self.flow.collaboration - Collaboration modality operations.

    AGENTESE: self.flow.collaboration.*
    """

    _handle: str = "self.flow.collaboration"
    _parent_flow: FlowNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return COLLABORATION_FLOW_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View collaboration flow state."""
        if self._parent_flow is None or self._parent_flow._collaboration_flow is None:
            return BasicRendering(
                summary="Collaboration Flow",
                content="No collaboration flow active",
                metadata={"active": False},
            )

        collab = self._parent_flow._collaboration_flow
        return BasicRendering(
            summary="Collaboration Flow State",
            content="Collaboration flow active with blackboard",
            metadata={
                "active": True,
                "has_blackboard": hasattr(collab, "blackboard"),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Delegate to parent flow's collaboration operations."""
        if self._parent_flow is None:
            return {"error": "No parent flow configured"}

        match aspect:
            case "board":
                return await self._parent_flow._get_board(observer, **kwargs)
            case "post":
                return await self._parent_flow._post_contribution(observer, **kwargs)
            case "vote":
                return await self._parent_flow._vote(observer, **kwargs)
            case "propose":
                return await self._propose(observer, **kwargs)
            case "decide":
                return await self._parent_flow._decide(observer, **kwargs)
            case "contributions":
                return await self._get_contributions(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _propose(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new proposal."""
        if self._parent_flow is None or self._parent_flow._collaboration_flow is None:
            return {"error": "No collaboration flow active"}

        content = kwargs.get("content")
        if not content:
            return {"error": "content is required"}

        try:
            collab = self._parent_flow._collaboration_flow
            proposal = collab.propose(
                content=content,
                agent_id=self._umwelt_to_meta(observer).name,
            )
            return {
                "status": "proposed",
                "proposal_id": proposal.id if hasattr(proposal, "id") else "unknown",
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_contributions(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get contributions from blackboard."""
        if self._parent_flow is None or self._parent_flow._collaboration_flow is None:
            return {"error": "No collaboration flow active"}

        agent_id = kwargs.get("agent_id")
        contribution_type = kwargs.get("type")
        limit = kwargs.get("limit", 20)

        try:
            collab = self._parent_flow._collaboration_flow
            board = collab.blackboard
            contributions = board.read(
                agent_id=agent_id,
                contribution_type=contribution_type,
            )
            return {
                "contributions": contributions[:limit],
                "count": len(contributions),
            }
        except Exception as e:
            return {"error": str(e)}


# === Factory Function ===


def create_flow_resolver() -> FlowNode:
    """Create a FlowNode for self.flow.* paths."""
    return FlowNode()


# === Export ===

__all__ = [
    # Nodes
    "FlowNode",
    "ChatFlowNode",
    "ResearchFlowNode",
    "CollaborationFlowNode",
    # Affordances
    "FLOW_AFFORDANCES",
    "CHAT_FLOW_AFFORDANCES",
    "RESEARCH_FLOW_AFFORDANCES",
    "COLLABORATION_FLOW_AFFORDANCES",
    # Factory
    "create_flow_resolver",
]
