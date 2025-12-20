"""
Chat AGENTESE Node: @node("self.chat")

Wraps ChatPersistence and ChatSessionFactory as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.chat.manifest     - Chat service status
- self.chat.sessions     - List active and persisted sessions
- self.chat.session      - Get specific session by ID or name
- self.chat.create       - Create new session for a node path
- self.chat.send         - Send message to session
- self.chat.stream       - Stream response from session
- self.chat.history      - Get session history
- self.chat.save         - Persist session
- self.chat.search       - Search sessions
- self.chat.resume       - Resume a saved session
- self.chat.metrics      - Get session metrics

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/chat.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    ChatManifestResponse,
    ContextBreakdownRequest,
    ContextBreakdownResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionRequest,
    DeleteSessionResponse,
    GetModelsRequest,
    GetModelsResponse,
    GetSessionRequest,
    HistoryRequest,
    HistoryResponse,
    MetricsRequest,
    MetricsResponse,
    ModelOption,
    ResetSessionRequest,
    ResetSessionResponse,
    ResumeSessionRequest,
    ResumeSessionResponse,
    SaveSessionRequest,
    SaveSessionResponse,
    SearchSessionsRequest,
    SendMessageRequest,
    SendMessageResponse,
    SessionDetailResponse,
    SessionsResponse,
    SetModelRequest,
    SetModelResponse,
    StreamChunk,
    StreamMessageRequest,
)
from .factory import ChatSessionFactory, get_chat_factory
from .model_selector import MODEL_OPTIONS, can_switch_model
from .persistence import (
    ChatPersistence,
    PersistedSession,
    get_persistence,
)
from .session import ChatSession

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === ChatNode Rendering ===


@dataclass(frozen=True)
class ChatManifestRendering:
    """Rendering for chat service status."""

    active_sessions: int
    persisted_sessions: int
    sessions_by_node: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "chat_manifest",
            "active_sessions": self.active_sessions,
            "persisted_sessions": self.persisted_sessions,
            "sessions_by_node": self.sessions_by_node,
        }

    def to_text(self) -> str:
        lines = [
            "Chat Service Status",
            "==================",
            f"Active Sessions: {self.active_sessions}",
            f"Persisted Sessions: {self.persisted_sessions}",
        ]
        if self.sessions_by_node:
            lines.append("Sessions by Node:")
            for node_path, count in self.sessions_by_node.items():
                lines.append(f"  {node_path}: {count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SessionListRendering:
    """Rendering for session list."""

    sessions: list[dict[str, Any]]
    query: str = "all"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "session_list",
            "query": self.query,
            "count": len(self.sessions),
            "sessions": self.sessions,
        }

    def to_text(self) -> str:
        if not self.sessions:
            return f"No sessions found for: {self.query}"
        lines = [f"Sessions ({len(self.sessions)} results)", ""]
        for i, s in enumerate(self.sessions[:20], 1):
            name = s.get("name") or s.get("session_id", "unknown")[:12]
            turns = s.get("turn_count", 0)
            node_path = s.get("node_path", "unknown")
            lines.append(f"{i}. {name} ({turns} turns) - {node_path}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SessionDetailRendering:
    """Rendering for single session details."""

    session_id: str
    node_path: str
    name: str | None
    turn_count: int
    state: str
    entropy: float
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "session_detail",
            "session_id": self.session_id,
            "node_path": self.node_path,
            "name": self.name,
            "turn_count": self.turn_count,
            "state": self.state,
            "entropy": self.entropy,
            "metrics": self.metrics,
        }

    def to_text(self) -> str:
        name_str = self.name or self.session_id[:12]
        lines = [
            f"Session: {name_str}",
            "=" * 40,
            f"ID: {self.session_id}",
            f"Node: {self.node_path}",
            f"State: {self.state}",
            f"Turns: {self.turn_count}",
            f"Entropy: {self.entropy:.2f}",
        ]
        if self.metrics:
            lines.append("")
            lines.append("Metrics:")
            for k, v in self.metrics.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ChatResponseRendering:
    """Rendering for chat response."""

    response: str
    session_id: str
    turn_number: int
    tokens_in: int = 0
    tokens_out: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "chat_response",
            "response": self.response,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
        }

    def to_text(self) -> str:
        return self.response


# === ChatNode ===


@node(
    "self.chat",
    description="Chat Service - conversational affordances for any AGENTESE node",
    dependencies=("chat_persistence", "chat_factory"),
    contracts={
        # Perception aspects (Response only - no request needed)
        "manifest": Response(ChatManifestResponse),
        "sessions": Response(SessionsResponse),
        # Mutation aspects (Contract with request + response)
        "session": Contract(GetSessionRequest, SessionDetailResponse),
        "create": Contract(CreateSessionRequest, CreateSessionResponse),
        "send": Contract(SendMessageRequest, SendMessageResponse),
        "stream": Contract(StreamMessageRequest, StreamChunk),  # Yields StreamChunk via SSE
        "history": Contract(HistoryRequest, HistoryResponse),
        "save": Contract(SaveSessionRequest, SaveSessionResponse),
        "resume": Contract(ResumeSessionRequest, ResumeSessionResponse),
        "search": Contract(SearchSessionsRequest, SessionsResponse),
        "metrics": Contract(MetricsRequest, MetricsResponse),
        "delete": Contract(DeleteSessionRequest, DeleteSessionResponse),
        "reset": Contract(ResetSessionRequest, ResetSessionResponse),
        # Model selection
        "models": Contract(GetModelsRequest, GetModelsResponse),
        "set_model": Contract(SetModelRequest, SetModelResponse),
        # Context breakdown (Teaching Mode)
        "context": Contract(ContextBreakdownRequest, ContextBreakdownResponse),
    },
)
class ChatNode(BaseLogosNode):
    """
    AGENTESE node for Chat Crown Jewel.

    Exposes ChatSessionFactory and ChatPersistence through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/chat/create
        {"node_path": "self.soul"}

        # Via Logos directly
        await logos.invoke("self.chat.send", observer, session_id="...", message="Hello")

        # Via CLI
        kgents chat send "..." --session abc123
    """

    def __init__(
        self,
        chat_persistence: ChatPersistence | None = None,
        chat_factory: ChatSessionFactory | None = None,
    ) -> None:
        """
        Initialize ChatNode.

        Args:
            chat_persistence: The persistence layer (injected or uses singleton)
            chat_factory: The session factory (injected or uses singleton)
        """
        self._persistence = chat_persistence or get_persistence()
        self._factory = chat_factory or get_chat_factory()

    @property
    def handle(self) -> str:
        return "self.chat"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Core operations (create, send, history) available to all archetypes.
        Admin operations (delete) restricted to privileged archetypes.
        """
        # Core operations available to all archetypes
        base = (
            "create",
            "send",
            "stream",
            "history",
            "save",
            "sessions",
            "session",
            "resume",
            "metrics",
            "search",
            "models",
            "set_model",
            "context",  # Teaching mode - available to all
        )

        if archetype in ("developer", "admin", "system"):
            # Full access including mutations
            return base + ("delete", "reset")
        else:
            # Standard access
            return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest chat service status to observer.

        AGENTESE: self.chat.manifest
        """
        # Count active sessions from factory
        active_sessions = self._factory.list_sessions()

        # Count persisted sessions
        persisted_count = await self._persistence.count_sessions()

        # Sessions by node
        sessions_by_node: dict[str, int] = {}
        for session in active_sessions:
            node_path = session.node_path
            sessions_by_node[node_path] = sessions_by_node.get(node_path, 0) + 1

        return ChatManifestRendering(
            active_sessions=len(active_sessions),
            persisted_sessions=persisted_count,
            sessions_by_node=sessions_by_node,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        # Route to appropriate method
        if aspect == "create":
            return await self._create_session(observer, **kwargs)
        elif aspect == "send":
            return await self._send_message(observer, **kwargs)
        elif aspect == "stream":
            # Stream returns AsyncIterator directly (no await!)
            # Gateway will detect hasattr(result, "__aiter__") and stream via SSE
            return self._stream_message(observer, **kwargs)
        elif aspect == "history":
            return await self._get_history(observer, **kwargs)
        elif aspect == "save":
            return await self._save_session(observer, **kwargs)
        elif aspect == "sessions":
            return await self._list_sessions(observer, **kwargs)
        elif aspect == "session":
            return await self._get_session(observer, **kwargs)
        elif aspect == "resume":
            return await self._resume_session(observer, **kwargs)
        elif aspect == "metrics":
            return await self._get_metrics(observer, **kwargs)
        elif aspect == "search":
            return await self._search_sessions(observer, **kwargs)
        elif aspect == "delete":
            return await self._delete_session(observer, **kwargs)
        elif aspect == "reset":
            return await self._reset_session(observer, **kwargs)
        elif aspect == "models":
            return await self._get_models(observer, **kwargs)
        elif aspect == "set_model":
            return await self._set_model(observer, **kwargs)
        elif aspect == "context":
            return await self._get_context_breakdown(observer, **kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    # === Aspect Implementations ===

    async def _create_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a new chat session for a node path."""
        node_path = kwargs.get("node_path", "self.soul")
        force_new = kwargs.get("force_new", False)

        session = await self._factory.create_session(
            node_path=node_path,
            observer=observer,
            force_new=force_new,
        )

        return {
            "session_id": session.session_id,
            "node_path": session.node_path,
            "state": session.state.value,
            "created": True,
        }

    async def _send_message(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a message to a chat session."""
        session_id = kwargs.get("session_id")
        message = kwargs.get("message", "")
        node_path = kwargs.get("node_path")

        if not message:
            return {"error": "message required"}

        # Get session by ID or node_path
        session: ChatSession | None = None
        if session_id:
            session = self._factory.get_session_by_id(session_id)
        elif node_path:
            session = self._factory.get_session(node_path, observer)

        if session is None:
            # Create new session
            node_path = node_path or "self.soul"
            session = await self._factory.create_session(node_path, observer)

        try:
            response = await session.send(message)
            last_turn = session._turns[-1] if session._turns else None

            return ChatResponseRendering(
                response=response,
                session_id=session.session_id,
                turn_number=session.turn_count,
                tokens_in=last_turn.tokens_in if last_turn else 0,
                tokens_out=last_turn.tokens_out if last_turn else 0,
            ).to_dict()
        except RuntimeError as e:
            return {"error": str(e), "session_id": session.session_id}

    async def _stream_message(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Stream a message response token by token.

        Returns an async iterator that the gateway will wrap in SSE format.
        Each yielded dict represents a StreamChunk.

        AGENTESE: self.chat.stream
        Gateway: GET /agentese/self/chat/stream/stream (SSE endpoint)
        """
        session_id = kwargs.get("session_id")
        message = kwargs.get("message", "")
        node_path = kwargs.get("node_path")

        if not message:
            yield {"error": "message required", "is_complete": True}
            return

        # Get session by ID or node_path
        session: ChatSession | None = None
        if session_id:
            session = self._factory.get_session_by_id(session_id)
        elif node_path:
            session = self._factory.get_session(node_path, observer)

        if session is None:
            # Create new session
            node_path = node_path or "self.soul"
            session = await self._factory.create_session(node_path, observer)

        # Track turn number before streaming starts
        turn_number = session.turn_count + 1
        tokens_so_far = 0
        full_response = ""

        try:
            # Stream tokens from the session
            async for token in session.stream(message):
                tokens_so_far += 1
                full_response += token
                yield {
                    "content": token,
                    "session_id": session.session_id,
                    "turn_number": turn_number,
                    "is_complete": False,
                    "tokens_so_far": tokens_so_far,
                }

            # Yield completion chunk with final metrics
            last_turn = session._turns[-1] if session._turns else None
            yield {
                "content": "",
                "session_id": session.session_id,
                "turn_number": turn_number,
                "is_complete": True,
                "tokens_so_far": tokens_so_far,
                "full_response": full_response,
                "tokens_in": last_turn.tokens_in if last_turn else 0,
                "tokens_out": last_turn.tokens_out if last_turn else tokens_so_far,
            }

        except RuntimeError as e:
            yield {
                "error": str(e),
                "session_id": session.session_id,
                "turn_number": turn_number,
                "is_complete": True,
            }

    async def _get_history(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get conversation history for a session."""
        session_id = kwargs.get("session_id")
        limit = kwargs.get("limit", 10)

        session = self._factory.get_session_by_id(session_id) if session_id else None

        if session is None:
            return {"error": "session not found", "session_id": session_id}

        turns = session.get_history(limit=limit)

        return {
            "session_id": session.session_id,
            "turn_count": len(turns),
            "turns": [t.to_dict() for t in turns],
        }

    async def _save_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Save a session to persistence."""
        session_id = kwargs.get("session_id")
        name = kwargs.get("name")

        session = self._factory.get_session_by_id(session_id) if session_id else None

        if session is None:
            return {"error": "session not found", "session_id": session_id}

        if name:
            session.set_name(name)

        datum_id = await self._persistence.save_session(session, name=name)

        return {
            "saved": True,
            "session_id": session.session_id,
            "name": name,
            "datum_id": datum_id,
        }

    async def _list_sessions(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List active and persisted sessions."""
        node_path = kwargs.get("node_path")
        limit = kwargs.get("limit", 20)
        include_persisted = kwargs.get("include_persisted", True)

        sessions_list: list[dict[str, Any]] = []

        # Active sessions
        active = self._factory.list_sessions(node_path=node_path)
        for session in active:
            sessions_list.append(
                {
                    "session_id": session.session_id,
                    "node_path": session.node_path,
                    "name": session._name,
                    "turn_count": session.turn_count,
                    "state": session.state.value,
                    "active": True,
                }
            )

        # Persisted sessions
        if include_persisted:
            persisted = await self._persistence.list_sessions(
                node_path=node_path,
                limit=limit,
            )
            # Add persisted sessions that aren't already in active list
            active_ids = {s["session_id"] for s in sessions_list}
            for p in persisted:
                if p.session_id not in active_ids:
                    sessions_list.append(
                        {
                            "session_id": p.session_id,
                            "node_path": p.node_path,
                            "name": p.name,
                            "turn_count": p.turn_count,
                            "state": p.state,
                            "active": False,
                        }
                    )

        return SessionListRendering(
            sessions=sessions_list[:limit],
            query=node_path or "all",
        ).to_dict()

    async def _get_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get details of a specific session."""
        session_id = kwargs.get("session_id")
        name = kwargs.get("name")

        # Try active sessions first
        session = self._factory.get_session_by_id(session_id) if session_id else None

        if session:
            return SessionDetailRendering(
                session_id=session.session_id,
                node_path=session.node_path,
                name=session._name,
                turn_count=session.turn_count,
                state=session.state.value,
                entropy=session.entropy,
                metrics=session.get_metrics(),
            ).to_dict()

        # Try persisted sessions
        persisted: PersistedSession | None = None
        if session_id:
            persisted = await self._persistence.load_session(session_id)
        elif name:
            persisted = await self._persistence.load_by_name(name)

        if persisted:
            return SessionDetailRendering(
                session_id=persisted.session_id,
                node_path=persisted.node_path,
                name=persisted.name,
                turn_count=persisted.turn_count,
                state=persisted.state,
                entropy=persisted.entropy,
                metrics={
                    "total_tokens": persisted.total_tokens,
                    "updated_at": persisted.updated_at.isoformat(),
                },
            ).to_dict()

        return {"error": "session not found"}

    async def _resume_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Resume a saved session."""
        session_id = kwargs.get("session_id")
        name = kwargs.get("name")

        # Load persisted session
        persisted: PersistedSession | None = None
        if session_id:
            persisted = await self._persistence.load_session(session_id)
        elif name:
            persisted = await self._persistence.load_by_name(name)

        if persisted is None:
            return {"error": "session not found"}

        # Create new active session with persisted data
        session = await self._factory.create_session(
            node_path=persisted.node_path,
            observer=observer,
            force_new=True,
        )

        # Note: Full session restoration with history would need ChatSession
        # to accept persisted turns. For now, we just create fresh session
        # but preserve the name.
        if persisted.name:
            session.set_name(persisted.name)

        return {
            "resumed": True,
            "session_id": session.session_id,
            "node_path": session.node_path,
            "name": persisted.name,
            "previous_turns": persisted.turn_count,
        }

    async def _get_metrics(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get session metrics."""
        session_id = kwargs.get("session_id")

        session = self._factory.get_session_by_id(session_id) if session_id else None

        if session is None:
            # Return aggregate metrics
            from .observability import get_chat_metrics_summary

            return get_chat_metrics_summary()

        return session.get_metrics()

    async def _search_sessions(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Search sessions by content."""
        query = kwargs.get("query", "")
        limit = kwargs.get("limit", 20)

        if not query:
            return {"error": "query required"}

        results = await self._persistence.search_sessions(query, limit=limit)

        sessions_list = [
            {
                "session_id": s.session_id,
                "node_path": s.node_path,
                "name": s.name,
                "turn_count": s.turn_count,
            }
            for s in results
        ]

        return SessionListRendering(
            sessions=sessions_list,
            query=query,
        ).to_dict()

    async def _delete_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Delete a session."""
        session_id = kwargs.get("session_id")

        if not session_id:
            return {"error": "session_id required"}

        # Remove from active sessions
        session = self._factory.get_session_by_id(session_id)
        if session:
            self._factory.close_session(session)

        # Remove from persistence
        deleted = await self._persistence.delete_session(session_id)

        return {"deleted": deleted, "session_id": session_id}

    async def _reset_session(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reset a session to initial state."""
        session_id = kwargs.get("session_id")

        session = self._factory.get_session_by_id(session_id) if session_id else None

        if session is None:
            return {"error": "session not found", "session_id": session_id}

        session.reset()

        return {
            "reset": True,
            "session_id": session.session_id,
            "state": session.state.value,
        }

    async def _get_models(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get available models for a session.

        Returns the list of models that can be selected and whether
        the current user is allowed to switch models.
        """
        session_id = kwargs.get("session_id")

        # Get session if provided
        session = self._factory.get_session_by_id(session_id) if session_id else None

        # Check if model switching is allowed
        can_switch = False
        current_model = None

        if session is not None:
            can_switch = can_switch_model(session, observer)
            current_model = session.get_effective_model()

        # Convert MODEL_OPTIONS to contract format
        models = [
            {
                "id": opt.id,
                "name": opt.name,
                "description": opt.description,
                "tier": opt.tier,
            }
            for opt in MODEL_OPTIONS
        ]

        return {
            "models": models,
            "current_model": current_model,
            "can_switch": can_switch,
        }

    async def _set_model(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Set the model for a session.

        Validates that the observer is allowed to switch models
        and that the requested model is valid.
        """
        session_id = kwargs.get("session_id")
        model = kwargs.get("model")

        if not session_id:
            return {
                "success": False,
                "session_id": "",
                "model": model or "",
                "message": "session_id is required",
            }

        if not model:
            return {
                "success": False,
                "session_id": session_id,
                "model": "",
                "message": "model is required",
            }

        # Get session
        session = self._factory.get_session_by_id(session_id)

        if session is None:
            return {
                "success": False,
                "session_id": session_id,
                "model": model,
                "message": "Session not found",
            }

        # Check if switching is allowed
        if not can_switch_model(session, observer):
            return {
                "success": False,
                "session_id": session_id,
                "model": model,
                "message": "Model switching not allowed for this session or user",
            }

        # Get previous model for response
        previous_model = session.get_effective_model()

        # Attempt to set the model
        success, error = session.set_model(model)

        if not success:
            return {
                "success": False,
                "session_id": session_id,
                "model": model,
                "previous_model": previous_model,
                "message": error,
            }

        return {
            "success": True,
            "session_id": session_id,
            "model": model,
            "previous_model": previous_model,
            "message": None,
        }

    async def _get_context_breakdown(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get context breakdown for teaching mode.

        Shows how the context window is being used:
        - System prompt tokens
        - Summary tokens (compressed history)
        - Working memory tokens (recent turns)
        - Available headroom

        AGENTESE: self.chat.context
        """
        session_id = kwargs.get("session_id")

        if not session_id:
            return {"error": "session_id required"}

        # Get session
        session = self._factory.get_session_by_id(session_id)

        if session is None:
            return {"error": "session not found", "session_id": session_id}

        # Get context breakdown from composer's window
        if session.has_composer and session._composer is not None:
            try:
                window = session._composer.get_or_create_window(session)
                breakdown = window.get_context_breakdown()

                return {
                    "segments": [
                        {
                            "name": seg.name,
                            "tokens": seg.tokens,
                            "color": seg.color,
                            "description": seg.description,
                        }
                        for seg in breakdown.segments
                    ],
                    "total_tokens": breakdown.total_tokens,
                    "context_window": breakdown.context_window,
                    "utilization": round(breakdown.utilization, 4),
                    "strategy": breakdown.strategy,
                    "has_summary": breakdown.has_summary,
                }
            except Exception:
                # Fallback to estimate from session
                return self._estimate_context_breakdown(session)
        else:
            # No composer - use session estimate
            return self._estimate_context_breakdown(session)

    def _estimate_context_breakdown(self, session: ChatSession) -> dict[str, Any]:
        """
        Estimate context breakdown from session data when no composer is available.

        Fallback for sessions without an active composer/window.
        """
        # Estimate from session turns
        working_tokens = sum(t.tokens_in + t.tokens_out for t in session._turns)

        # System prompt estimate (if config has one)
        system_tokens = 0
        if session.config.system_prompt:
            system_tokens = len(session.config.system_prompt) // 4

        # Total used
        total_used = system_tokens + working_tokens
        context_window = session.config.context_window
        available = max(0, context_window - total_used)

        segments = []
        if system_tokens > 0:
            segments.append(
                {
                    "name": "System",
                    "tokens": system_tokens,
                    "color": "bg-violet-500",
                    "description": "System prompt and personality",
                }
            )
        if working_tokens > 0:
            segments.append(
                {
                    "name": "Working",
                    "tokens": working_tokens,
                    "color": "bg-cyan-500",
                    "description": f"Recent {len(session._turns)} turns",
                }
            )
        segments.append(
            {
                "name": "Available",
                "tokens": available,
                "color": "bg-gray-700",
                "description": "Remaining context space",
            }
        )

        return {
            "segments": segments,
            "total_tokens": total_used,
            "context_window": context_window,
            "utilization": round(total_used / context_window, 4) if context_window > 0 else 0,
            "strategy": session.config.context_strategy.value,
            "has_summary": False,
        }


# === Exports ===

__all__ = [
    "ChatNode",
    "ChatManifestRendering",
    "SessionListRendering",
    "SessionDetailRendering",
    "ChatResponseRendering",
]
