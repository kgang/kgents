"""
AGENTESE Self Conductor Context: Conversation Window Management + Live Flux

CLI v7 Phase 2: Deep Conversation
CLI v7 Phase 7: Live Flux

The self.conductor context provides access to ConversationWindow state:
- self.conductor.manifest - View current window status
- self.conductor.snapshot - Get immutable snapshot of window state
- self.conductor.history - Get bounded conversation history
- self.conductor.summary - Get/set conversation summary
- self.conductor.reset - Reset conversation window
- self.conductor.sessions - List active conversation sessions

Phase 7 additions:
- self.conductor.flux - View flux event integration status
- self.conductor.flux_start - Start event integration
- self.conductor.flux_stop - Stop event integration

The Conductor manages bounded conversation history with:
- Sliding window: Evict oldest turns at capacity
- Summarize: Compress evicted turns via LLM
- Hybrid: Combine sliding + summarization
- Forget: Hard truncate (no memory)

AGENTESE: self.conductor.*

Principle Alignment:
- Composable: Windows compose with ChatSession; Events compose through buses
- Ethical: Bounded history prevents resource exhaustion
- Joy-Inducing: "What did we discuss?" should work after 10+ turns
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node
from .conductor_contracts import (
    ConductorManifestResponse,
    ConfigRequest,
    ConfigResponse,
    FluxStartRequest,
    FluxStartResponse,
    FluxStatusRequest,
    FluxStatusResponse,
    FluxStopRequest,
    FluxStopResponse,
    HistoryRequest,
    HistoryResponse,
    ResetRequest,
    ResetResponse,
    SessionsListRequest,
    SessionsListResponse,
    SnapshotRequest,
    SnapshotResponse,
    SummaryGetRequest,
    SummaryGetResponse,
    SummarySetRequest,
    SummarySetResponse,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# Conductor affordances
CONDUCTOR_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "snapshot",
    "history",
    "summary",
    "reset",
    "sessions",
    "config",
    # Phase 7: Live Flux
    "flux",
    "flux_start",
    "flux_stop",
)


@node(
    "self.conductor",
    description="Conversation window management - bounded history with summarization + live flux",
    singleton=True,
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(ConductorManifestResponse),
        # Query aspects (Contract - request + response)
        "snapshot": Contract(SnapshotRequest, SnapshotResponse),
        "history": Contract(HistoryRequest, HistoryResponse),
        "summary": Contract(SummaryGetRequest, SummaryGetResponse),  # GET
        "config": Contract(ConfigRequest, ConfigResponse),
        "sessions": Contract(SessionsListRequest, SessionsListResponse),
        # Mutation aspects
        "reset": Contract(ResetRequest, ResetResponse),
        # Phase 7: Live Flux contracts
        "flux": Contract(FluxStatusRequest, FluxStatusResponse),
        "flux_start": Contract(FluxStartRequest, FluxStartResponse),
        "flux_stop": Contract(FluxStopRequest, FluxStopResponse),
        # Note: summary aspect handles both GET and SET via kwargs detection
        # When content is provided, it uses SummarySetRequest/Response
    },
)
@dataclass
class ConductorNode(BaseLogosNode):
    """
    self.conductor - Conversation window interface.

    Provides window management for deep conversations:
    - View window status and utilization
    - Get bounded conversation history
    - Access conversation summaries
    - Reset or reconfigure windows
    """

    _handle: str = "self.conductor"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Conductor affordances available to all archetypes."""
        return CONDUCTOR_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View Conductor status and window overview."""
        try:
            from services.chat import get_chat_factory

            factory = get_chat_factory()
            sessions = factory.list_sessions()

            # Collect window stats
            window_stats = []
            for session in sessions:
                if hasattr(session, "_composer") and session._composer is not None:
                    composer = session._composer
                    if session.session_id in composer._windows:
                        window = composer._windows[session.session_id]
                        window_stats.append(
                            {
                                "session_id": session.session_id[:8],
                                "node_path": session.node_path,
                                "turn_count": window.turn_count,
                                "utilization": f"{window.utilization:.1%}",
                                "strategy": window.strategy,
                                "has_summary": window.has_summary,
                            }
                        )

            content_lines = [
                "Conductor: Conversation Window Manager",
                f"Active windows: {len(window_stats)}",
                "",
                "Strategies available:",
                "  - sliding: Evict oldest turns at capacity",
                "  - summarize: LLM-compress evicted context",
                "  - hybrid: Sliding + periodic summarization",
                "  - forget: Hard truncate (no memory)",
                "",
            ]

            if window_stats:
                content_lines.append("Active Windows:")
                for stat in window_stats:
                    content_lines.append(
                        f"  [{stat['session_id']}] {stat['node_path']}: "
                        f"{stat['turn_count']} turns, {stat['utilization']} used"
                    )

            return BasicRendering(
                summary="Conductor: Conversation Window Manager",
                content="\n".join(content_lines),
                metadata={
                    "affordances": list(CONDUCTOR_AFFORDANCES),
                    "active_windows": len(window_stats),
                    "windows": window_stats,
                },
            )
        except Exception as e:
            logger.warning(f"Conductor manifest failed: {e}")
            return BasicRendering(
                summary="Conductor",
                content="Conductor service not available.",
                metadata={"error": str(e)},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle conductor-specific aspects."""
        match aspect:
            case "snapshot":
                return await self._get_snapshot(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "summary":
                # Handle both get and set
                if "content" in kwargs:
                    return await self._set_summary(observer, **kwargs)
                return await self._get_summary(observer, **kwargs)
            case "reset":
                return await self._reset_window(observer, **kwargs)
            case "sessions":
                return await self._list_sessions(observer, **kwargs)
            case "config":
                return await self._get_config(observer, **kwargs)
            # Phase 7: Live Flux
            case "flux":
                return await self._get_flux_status(observer, **kwargs)
            case "flux_start":
                return await self._start_flux(observer, **kwargs)
            case "flux_stop":
                return await self._stop_flux(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("window")],
        help="Get immutable snapshot of window state",
        examples=["self.conductor.snapshot[session_id='abc123']"],
    )
    async def _get_snapshot(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get immutable snapshot of a conversation window.

        Args:
            session_id: Target session ID (optional - uses current if not provided)

        Returns:
            WindowSnapshot with turn_count, utilization, has_summary, etc.
        """
        session_id = kwargs.get("session_id")
        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found", "session_id": session_id}

        snapshot = window.snapshot()
        return {
            "turn_count": snapshot.turn_count,
            "total_turn_count": snapshot.total_turn_count,
            "total_tokens": snapshot.total_tokens,
            "utilization": snapshot.utilization,
            "strategy": snapshot.strategy,
            "has_summary": snapshot.has_summary,
            "max_turns": snapshot.max_turns,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("window")],
        help="Get bounded conversation history",
        examples=["self.conductor.history[session_id='abc123', limit=5]"],
    )
    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get bounded conversation history from window.

        Args:
            session_id: Target session ID
            limit: Max messages to return (optional)
            include_system: Include system prompt (default: False)

        Returns:
            List of messages with role and content
        """
        session_id = kwargs.get("session_id")
        limit = kwargs.get("limit")
        include_system = kwargs.get("include_system", False)

        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found", "messages": [], "total": 0}

        messages = window.get_context_messages()

        # Filter system if requested
        if not include_system:
            messages = [m for m in messages if m.role != "system"]

        # Apply limit
        if limit is not None:
            messages = messages[-limit:]

        return {
            "messages": [
                {
                    "role": m.role,
                    "content": m.content[:500] + "..." if len(m.content) > 500 else m.content,
                    "tokens": m.tokens,
                }
                for m in messages
            ],
            "total": len(messages),
            "window_turn_count": window.turn_count,
            "window_total_turn_count": window.total_turn_count,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("window")],
        help="Get conversation summary",
        examples=["self.conductor.summary[session_id='abc123']"],
    )
    async def _get_summary(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get conversation summary from window.

        Args:
            session_id: Target session ID

        Returns:
            Summary content and metadata
        """
        session_id = kwargs.get("session_id")
        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found", "has_summary": False}

        return {
            "has_summary": window.has_summary,
            "summary": window._summary if window.has_summary else None,
            "summarized_turn_count": window._summarized_turn_count,
            "strategy": window.strategy,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("window")],
        help="Set conversation summary manually",
        examples=["self.conductor.summary[session_id='abc123', content='We discussed...']"],
    )
    async def _set_summary(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Manually set conversation summary.

        Args:
            session_id: Target session ID
            content: Summary content to set

        Returns:
            Confirmation with updated state
        """
        session_id = kwargs.get("session_id")
        content = kwargs.get("content")

        if not content:
            return {"error": "content required"}

        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found"}

        window._summary = content
        window._has_summary = True

        return {
            "success": True,
            "summary_length": len(content),
            "has_summary": window.has_summary,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("window")],
        help="Reset conversation window",
        examples=["self.conductor.reset[session_id='abc123']"],
    )
    async def _reset_window(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Reset a conversation window.

        Args:
            session_id: Target session ID
            preserve_system: Keep system prompt (default: True)

        Returns:
            Confirmation of reset
        """
        session_id = kwargs.get("session_id")
        preserve_system = kwargs.get("preserve_system", True)

        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found"}

        # Save system prompt if preserving
        system_prompt = None
        if preserve_system:
            for msg in window.get_context_messages():
                if msg.role == "system":
                    system_prompt = msg.content
                    break

        window.reset()

        # Restore system prompt
        if system_prompt and preserve_system:
            window.set_system_prompt(system_prompt)

        return {
            "success": True,
            "session_id": session_id,
            "preserved_system": preserve_system and system_prompt is not None,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="List active conversation sessions",
        examples=["self.conductor.sessions", "self.conductor.sessions[node_path='self.soul']"],
    )
    async def _list_sessions(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List active conversation sessions with windows.

        Args:
            node_path: Filter by node path (optional)
            limit: Max sessions to return (default: 20)

        Returns:
            List of sessions with window metadata
        """
        node_path = kwargs.get("node_path")
        limit = kwargs.get("limit", 20)

        try:
            from services.chat import get_chat_factory

            factory = get_chat_factory()
            sessions = factory.list_sessions(node_path=node_path)[:limit]

            session_data = []
            for session in sessions:
                data = {
                    "session_id": session.session_id,
                    "node_path": session.node_path,
                    "is_active": session.is_active,
                    "turn_count": len(list(session.get_history())),
                }

                # Add window info if available
                if hasattr(session, "_composer") and session._composer is not None:
                    composer = session._composer
                    if session.session_id in composer._windows:
                        window = composer._windows[session.session_id]
                        data["window"] = {
                            "turn_count": window.turn_count,
                            "total_turn_count": window.total_turn_count,
                            "utilization": window.utilization,
                            "strategy": window.strategy,
                            "has_summary": window.has_summary,
                        }

                session_data.append(data)

            return {
                "sessions": session_data,
                "total": len(session_data),
            }
        except Exception as e:
            logger.warning(f"Failed to list sessions: {e}")
            return {"error": str(e), "sessions": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("config")],
        help="Get window configuration",
        examples=["self.conductor.config[session_id='abc123']"],
    )
    async def _get_config(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get window configuration for a session.

        Args:
            session_id: Target session ID

        Returns:
            Window configuration parameters
        """
        session_id = kwargs.get("session_id")
        window = await self._get_window(session_id)

        if window is None:
            return {"error": "Window not found"}

        return {
            "max_turns": window.max_turns,
            "strategy": window.strategy,
            "context_window_tokens": window.context_window_tokens,
            "summarization_threshold": window.summarization_threshold,
            "has_summarizer": window._summarizer is not None,
        }

    # === Phase 7: Live Flux Methods ===

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("flux")],
        help="Get ConductorFlux event integration status",
        examples=["self.conductor.flux"],
    )
    async def _get_flux_status(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get status of ConductorFlux event integration.

        Returns flux running state, subscriber count, monitored event types.
        """
        try:
            from services.conductor.flux import get_conductor_flux
            from services.conductor.bus_bridge import is_bridge_active
            from protocols.synergy import SynergyEventType

            flux = get_conductor_flux()

            # Event types monitored by flux
            event_types = [
                SynergyEventType.FILE_READ.value,
                SynergyEventType.FILE_EDITED.value,
                SynergyEventType.FILE_CREATED.value,
                SynergyEventType.CONVERSATION_TURN.value,
                SynergyEventType.CURSOR_UPDATED.value,
                SynergyEventType.CURSOR_JOINED.value,
                SynergyEventType.CURSOR_LEFT.value,
                SynergyEventType.SWARM_SPAWNED.value,
                SynergyEventType.SWARM_DESPAWNED.value,
                SynergyEventType.SWARM_A2A_MESSAGE.value,
                SynergyEventType.SWARM_HANDOFF.value,
            ]

            return {
                "running": flux.running,
                "subscriber_count": len(flux._subscribers),
                "event_types_monitored": event_types,
                "bridge_active": is_bridge_active(),
            }
        except Exception as e:
            logger.warning(f"Failed to get flux status: {e}")
            return {"error": str(e), "running": False}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("flux")],
        help="Start ConductorFlux event integration",
        examples=["self.conductor.flux_start"],
    )
    async def _start_flux(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Start ConductorFlux event integration.

        Enables real-time event routing across all CLI v7 phases.
        """
        try:
            from services.conductor.flux import get_conductor_flux
            from services.conductor.bus_bridge import wire_a2a_to_global_synergy

            flux = get_conductor_flux()
            was_running = flux.running

            if not was_running:
                flux.start()
                wire_a2a_to_global_synergy()

            return {
                "success": True,
                "was_already_running": was_running,
            }
        except Exception as e:
            logger.warning(f"Failed to start flux: {e}")
            return {"success": False, "error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("flux")],
        help="Stop ConductorFlux event integration",
        examples=["self.conductor.flux_stop"],
    )
    async def _stop_flux(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Stop ConductorFlux event integration.

        Disables real-time event routing.
        """
        try:
            from services.conductor.flux import get_conductor_flux
            from services.conductor.bus_bridge import unwire_a2a_bridge

            flux = get_conductor_flux()
            was_running = flux.running

            if was_running:
                flux.stop()
                unwire_a2a_bridge()

            return {
                "success": True,
                "was_running": was_running,
            }
        except Exception as e:
            logger.warning(f"Failed to stop flux: {e}")
            return {"success": False, "error": str(e)}

    # === Helper Methods ===

    async def _get_window(self, session_id: str | None) -> Any:
        """
        Get ConversationWindow by session ID.

        Returns None if not found.
        """
        try:
            from services.chat import get_chat_factory

            factory = get_chat_factory()

            if session_id:
                session = factory.get_session_by_id(session_id)
                if session and hasattr(session, "_composer") and session._composer is not None:
                    composer = session._composer
                    return composer._windows.get(session.session_id)
            else:
                # Return first active window if no session_id
                sessions = factory.list_sessions()
                for session in sessions:
                    if (
                        session.is_active
                        and hasattr(session, "_composer")
                        and session._composer is not None
                    ):
                        composer = session._composer
                        if session.session_id in composer._windows:
                            return composer._windows[session.session_id]

            return None
        except Exception as e:
            logger.warning(f"Failed to get window: {e}")
            return None


# Factory function
def create_conductor_node() -> ConductorNode:
    """Create a ConductorNode instance."""
    return ConductorNode()


__all__ = [
    "ConductorNode",
    "CONDUCTOR_AFFORDANCES",
    "create_conductor_node",
]
