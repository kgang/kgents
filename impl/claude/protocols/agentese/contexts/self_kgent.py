"""
AGENTESE Self K-gent Context: Session Management

The self.kgent context provides access to K-gent session management:
- self.kgent.session.create - Create a new session
- self.kgent.session.list - List sessions for current tenant
- self.kgent.session.{id}.manifest - Get session details
- self.kgent.session.{id}.message - Send message (SSE stream)
- self.kgent.session.{id}.history - Get message history

Sessions maintain conversation state across multiple messages,
with real-time streaming via SSE for LLM responses.

AGENTESE: self.kgent.*

Principle Alignment:
- Composable: Sessions compose dialogue turns
- Joy-Inducing: Real-time streaming provides responsive UX
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator
from uuid import UUID

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# K-gent session affordances
KGENT_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "create",
    "list",
    "message",
    "history",
)

# --- In-Memory Message Store ---
# For MVP, messages are stored in-memory (matches sessions.py)
_message_store: dict[str, list[dict[str, Any]]] = {}


def _get_messages(session_id: str) -> list[dict[str, Any]]:
    """Get messages for a session."""
    if session_id not in _message_store:
        _message_store[session_id] = []
    return _message_store[session_id]


def _add_message(
    session_id: str,
    role: str,
    content: str,
    tokens: int = 0,
) -> dict[str, Any]:
    """Add a message to a session."""
    import uuid

    msg = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "role": role,
        "content": content,
        "tokens_used": tokens,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _get_messages(session_id).append(msg)
    return msg


# --- Flux Instance Store ---
_flux_instances: dict[str, Any] = {}


@node(
    "self.kgent",
    description="K-gent session management - create, list, message",
    singleton=True,
)
@dataclass
class KgentSessionNode(BaseLogosNode):
    """
    self.kgent - K-gent session interface.

    Provides session-based conversation management:
    - Create sessions with optional mode
    - Send messages with SSE streaming
    - Retrieve message history
    """

    _handle: str = "self.kgent"

    # Tenant service (lazy-loaded)
    _tenant_service: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_tenant_service(self) -> Any:
        """Lazy-load tenant service."""
        if self._tenant_service is None:
            try:
                from protocols.tenancy.service import TenantService

                self._tenant_service = TenantService()
            except ImportError:
                logger.warning("TenantService not available")
        return self._tenant_service

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Session affordances available to all archetypes."""
        return KGENT_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View K-gent session status."""
        return BasicRendering(
            summary="K-gent Sessions",
            content="Session management for K-gent conversations.\n\nUse create to start a new session, message to send messages.",
            metadata={
                "affordances": list(KGENT_AFFORDANCES),
                "active_sessions": len(_flux_instances),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle kgent-specific aspects."""
        match aspect:
            case "create":
                return await self._create_session(observer, **kwargs)
            case "list":
                return await self._list_sessions(observer, **kwargs)
            case "message":
                return await self._send_message(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Create a new K-gent session",
        examples=["self.kgent.create[title='Reflection', mode='reflect']"],
    )
    async def _create_session(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new K-gent session.

        Args:
            title: Optional session title
            agent_type: Agent type (default: "kgent")
            mode: Initial dialogue mode (reflect, advise, challenge, explore)

        Returns:
            Session details with id, status, etc.
        """
        title = kwargs.get("title")
        agent_type = kwargs.get("agent_type", "kgent")
        mode = kwargs.get("mode", "reflect")

        tenant_service = self._get_tenant_service()
        if tenant_service is None:
            return {"error": "Tenant service not available"}

        try:
            from protocols.tenancy.context import get_current_tenant
            from protocols.tenancy.models import UsageEventType

            tenant = get_current_tenant()
            if not tenant:
                return {"error": "Tenant context required"}

            # Create session
            session = await tenant_service.create_session(
                tenant_id=tenant.id,
                agent_type=agent_type,
                title=title,
            )

            # Create KgentFlux instance
            from agents.k.flux import KgentFluxConfig, create_kgent_flux
            from agents.k.persona import DialogueMode

            config = KgentFluxConfig(
                pulse_enabled=False,
                agent_id=str(session.id),
            )
            flux = create_kgent_flux(config=config)

            # Set initial mode
            if mode:
                try:
                    dialogue_mode = DialogueMode(mode.lower())
                    flux.soul.enter_mode(dialogue_mode)
                except ValueError:
                    pass

            _flux_instances[str(session.id)] = flux

            # Record usage
            await tenant_service.record_usage(
                tenant_id=tenant.id,
                event_type=UsageEventType.SESSION_CREATE,
                source="agentese",
                session_id=session.id,
            )

            return {
                "id": str(session.id),
                "tenant_id": str(session.tenant_id),
                "title": session.title,
                "agent_type": session.agent_type,
                "status": session.status.value if session.status else "unknown",
                "message_count": session.message_count,
                "tokens_used": session.tokens_used,
                "created_at": session.created_at.isoformat() if session.created_at else "",
            }
        except ImportError as e:
            return {"error": f"Missing dependency: {e}"}
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="List K-gent sessions for current tenant",
        examples=["self.kgent.list", "self.kgent.list[limit=10]"],
    )
    async def _list_sessions(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List sessions for the current tenant.

        Args:
            limit: Max sessions to return (default: 20)
            offset: Pagination offset (default: 0)

        Returns:
            List of sessions with total count
        """
        limit = kwargs.get("limit", 20)
        offset = kwargs.get("offset", 0)

        tenant_service = self._get_tenant_service()
        if tenant_service is None:
            return {"error": "Tenant service not available", "sessions": [], "total": 0}

        try:
            from protocols.tenancy.context import get_current_tenant

            tenant = get_current_tenant()
            if not tenant:
                return {"error": "Tenant context required", "sessions": [], "total": 0}

            sessions = await tenant_service.list_sessions(tenant.id)
            total = len(sessions)
            paginated = sessions[offset : offset + limit]

            return {
                "sessions": [
                    {
                        "id": str(s.id),
                        "tenant_id": str(s.tenant_id),
                        "title": s.title,
                        "agent_type": s.agent_type,
                        "status": s.status.value if s.status else "unknown",
                        "message_count": s.message_count,
                        "tokens_used": s.tokens_used,
                        "created_at": s.created_at.isoformat() if s.created_at else "",
                    }
                    for s in paginated
                ],
                "total": total,
            }
        except ImportError as e:
            return {"error": f"Missing dependency: {e}", "sessions": [], "total": 0}
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return {"error": str(e), "sessions": [], "total": 0}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Send message to K-gent session (returns SSE stream)",
        examples=["self.kgent.message[session_id='...', message='Hello']"],
    )
    async def _send_message(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any] | AsyncGenerator[dict[str, Any], None]:
        """
        Send a message to a K-gent session.

        Args:
            session_id: Target session ID
            message: Message content
            mode: Optional mode override
            stream: Whether to stream response (default: True)

        Returns:
            SSE stream of chunks or final response dict
        """
        session_id = kwargs.get("session_id")
        message = kwargs.get("message")
        mode_str = kwargs.get("mode")
        stream = kwargs.get("stream", True)

        if not session_id:
            return {"error": "session_id required"}
        if not message:
            return {"error": "message required"}

        tenant_service = self._get_tenant_service()
        if tenant_service is None:
            return {"error": "Tenant service not available"}

        try:
            from protocols.tenancy.context import get_current_tenant
            from protocols.tenancy.models import UsageEventType

            tenant = get_current_tenant()
            if not tenant:
                return {"error": "Tenant context required"}

            # Validate session
            try:
                uuid = UUID(session_id)
            except ValueError:
                return {"error": "Invalid session ID format"}

            session = await tenant_service.get_session(uuid)
            if not session:
                return {"error": "Session not found"}

            if session.tenant_id != tenant.id:
                return {"error": "Session not found"}  # Security: don't reveal existence

            # Get or create flux instance
            flux = _flux_instances.get(session_id)
            if not flux:
                from agents.k.flux import KgentFluxConfig, create_kgent_flux

                config = KgentFluxConfig(
                    pulse_enabled=False,
                    agent_id=session_id,
                )
                flux = create_kgent_flux(config=config)
                _flux_instances[session_id] = flux

            # Store user message
            _add_message(session_id, "user", message)

            # Parse mode
            mode = None
            if mode_str:
                from agents.k.persona import DialogueMode

                try:
                    mode = DialogueMode(mode_str.lower())
                except ValueError:
                    return {"error": f"Invalid mode '{mode_str}'"}

            if stream:
                # Return async generator for SSE streaming
                return self._stream_response(
                    flux, session_id, message, mode, tenant.id, tenant_service
                )
            else:
                # Non-streaming response
                from agents.k.events import dialogue_turn_event

                event = dialogue_turn_event(
                    message=message,
                    mode=mode.value if mode else None,
                    is_request=True,
                )
                result = await flux.invoke(event)

                response_text = result.payload.get("response", "")
                tokens_used = result.payload.get("tokens_used", 0)
                assistant_msg = _add_message(session_id, "assistant", response_text, tokens_used)

                # Record usage
                await tenant_service.record_usage(
                    tenant_id=tenant.id,
                    event_type=UsageEventType.LLM_CALL,
                    source="kgent",
                    tokens_out=tokens_used,
                    session_id=uuid,
                )

                # Update session stats
                messages = _get_messages(session_id)
                await tenant_service.update_session(
                    uuid,
                    message_count=len(messages),
                    tokens_used=sum(m.get("tokens_used", 0) for m in messages),
                )

                return {
                    "id": assistant_msg["id"],
                    "session_id": session_id,
                    "role": "assistant",
                    "content": response_text,
                    "tokens_used": tokens_used,
                    "created_at": assistant_msg["created_at"],
                }

        except ImportError as e:
            return {"error": f"Missing dependency: {e}"}
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {"error": str(e)}

    async def _stream_response(
        self,
        flux: Any,
        session_id: str,
        message: str,
        mode: Any,
        tenant_id: UUID,
        tenant_service: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Generate SSE stream for K-gent response."""
        from agents.k.soul import BudgetTier
        from protocols.tenancy.models import UsageEventType

        chunks: list[str] = []
        chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

        def on_chunk(chunk_text: str) -> None:
            chunk_queue.put_nowait(chunk_text)

        dialogue_result: Any = None
        dialogue_error: Exception | None = None

        async def run_dialogue() -> None:
            nonlocal dialogue_result, dialogue_error
            try:
                dialogue_result = await flux.soul.dialogue(
                    message=message,
                    mode=mode,
                    budget=BudgetTier.DIALOGUE,
                    on_chunk=on_chunk,
                )
            except Exception as e:
                dialogue_error = e
            finally:
                chunk_queue.put_nowait(None)

        dialogue_task = asyncio.create_task(run_dialogue())

        try:
            chunk_index = 0
            while True:
                chunk = await chunk_queue.get()
                if chunk is None:
                    break
                chunks.append(chunk)
                yield {"type": "chunk", "text": chunk, "index": chunk_index}
                chunk_index += 1

            await dialogue_task

            if dialogue_error is not None:
                raise dialogue_error

            response_text = dialogue_result.response if dialogue_result else "".join(chunks)
            tokens_used = dialogue_result.tokens_used if dialogue_result else 0

            _add_message(session_id, "assistant", response_text, tokens_used)

            await tenant_service.record_usage(
                tenant_id=tenant_id,
                event_type=UsageEventType.LLM_CALL,
                source="kgent",
                tokens_out=tokens_used,
                session_id=UUID(session_id),
            )

            messages = _get_messages(session_id)
            await tenant_service.update_session(
                UUID(session_id),
                message_count=len(messages),
                tokens_used=sum(m.get("tokens_used", 0) for m in messages),
            )

            yield {
                "type": "complete",
                "text": response_text,
                "tokens_used": tokens_used,
                "chunks": len(chunks),
            }

        except Exception as e:
            if not dialogue_task.done():
                dialogue_task.cancel()
                try:
                    await dialogue_task
                except asyncio.CancelledError:
                    pass
            yield {"type": "error", "error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="Get message history for a session",
        examples=["self.kgent.history[session_id='...']"],
    )
    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get message history for a session.

        Args:
            session_id: Target session ID
            limit: Max messages to return (default: 50)
            offset: Pagination offset (default: 0)

        Returns:
            List of messages with total count
        """
        session_id = kwargs.get("session_id")
        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        if not session_id:
            return {"error": "session_id required", "messages": [], "total": 0}

        tenant_service = self._get_tenant_service()
        if tenant_service is None:
            return {"error": "Tenant service not available", "messages": [], "total": 0}

        try:
            from protocols.tenancy.context import get_current_tenant

            tenant = get_current_tenant()
            if not tenant:
                return {"error": "Tenant context required", "messages": [], "total": 0}

            # Validate session
            try:
                uuid = UUID(session_id)
            except ValueError:
                return {"error": "Invalid session ID format", "messages": [], "total": 0}

            session = await tenant_service.get_session(uuid)
            if not session:
                return {"error": "Session not found", "messages": [], "total": 0}

            if session.tenant_id != tenant.id:
                return {"error": "Session not found", "messages": [], "total": 0}

            messages = _get_messages(session_id)
            total = len(messages)
            paginated = messages[offset : offset + limit]

            return {
                "messages": paginated,
                "total": total,
                "session_id": session_id,
            }

        except ImportError as e:
            return {"error": f"Missing dependency: {e}", "messages": [], "total": 0}
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return {"error": str(e), "messages": [], "total": 0}


# Factory function
def create_kgent_session_node() -> KgentSessionNode:
    """Create a KgentSessionNode instance."""
    return KgentSessionNode()


__all__ = [
    "KgentSessionNode",
    "KGENT_AFFORDANCES",
    "create_kgent_session_node",
]
