"""
K-gent Sessions API Endpoints.

Exposes KgentFlux via REST/SSE API:
- POST /v1/kgent/sessions - Create a new session
- GET /v1/kgent/sessions - List sessions
- GET /v1/kgent/sessions/{id} - Get session details
- POST /v1/kgent/sessions/{id}/messages - Send message (returns SSE stream)
- GET /v1/kgent/sessions/{id}/messages - Get message history
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional
from uuid import UUID

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException, Request
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    BaseModel = object  # type: ignore
    StreamingResponse = None  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Request/Response Models ---


class CreateSessionRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to create a new K-gent session."""

    title: Optional[str] = Field(
        default=None,
        description="Session title",
        examples=["Deep reflection session"],
    )
    agent_type: str = Field(
        default="kgent",
        description="Agent type (kgent, agentese)",
        examples=["kgent"],
    )
    mode: Optional[str] = Field(
        default="reflect",
        description="Initial dialogue mode (reflect, advise, challenge, explore)",
        examples=["reflect"],
    )


class SessionResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with session details."""

    id: str = Field(..., description="Session ID")
    tenant_id: str = Field(..., description="Tenant ID")
    title: Optional[str] = Field(default=None, description="Session title")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(default="active", description="Session status")
    message_count: int = Field(default=0, description="Number of messages")
    tokens_used: int = Field(default=0, description="Tokens used in session")
    created_at: str = Field(..., description="Creation timestamp")


class MessageRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to send a message in a session."""

    message: str = Field(
        ...,
        description="Message content",
        examples=["What patterns am I avoiding?"],
    )
    mode: Optional[str] = Field(
        default=None,
        description="Override dialogue mode for this message",
        examples=["challenge"],
    )
    stream: bool = Field(
        default=True,
        description="Whether to stream the response via SSE",
    )


class MessageResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response for a non-streamed message."""

    id: str = Field(..., description="Message ID")
    session_id: str = Field(..., description="Session ID")
    role: str = Field(..., description="Message role (user, assistant)")
    content: str = Field(..., description="Message content")
    tokens_used: int = Field(default=0, description="Tokens used")
    created_at: str = Field(..., description="Creation timestamp")


class SessionListResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with list of sessions."""

    sessions: list[SessionResponse] = Field(
        default_factory=list,
        description="List of sessions",
    )
    total: int = Field(default=0, description="Total number of sessions")


# --- In-Memory Message Store ---

# For MVP, messages are stored in-memory
# Production would use database
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
    from datetime import UTC, datetime

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

# Track active KgentFlux instances per session
_flux_instances: dict[str, Any] = {}


# --- Router Factory ---


def create_sessions_router() -> "APIRouter":
    """
    Create K-gent Sessions API router.

    Returns:
        FastAPI router with session endpoints

    Raises:
        ImportError: If FastAPI is not installed
    """
    if not HAS_FASTAPI:
        # Return a stub for when FastAPI is not available
        return None  # type: ignore[return-value]

    from datetime import datetime

    from agents.k.events import dialogue_turn_event
    from agents.k.flux import KgentFlux, KgentFluxConfig, create_kgent_flux
    from agents.k.persona import DialogueMode
    from agents.k.soul import KgentSoul
    from protocols.tenancy.context import get_current_tenant
    from protocols.tenancy.models import UsageEventType
    from protocols.tenancy.service import TenantService

    from .auth import get_api_key, has_scope

    router = APIRouter(prefix="/v1/kgent", tags=["kgent"])

    # Shared services
    _tenant_service = TenantService()

    @router.post("/sessions", response_model=SessionResponse)
    async def create_session(
        request: CreateSessionRequest,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> SessionResponse:
        """
        Create a new K-gent session.

        Sessions maintain conversation state across multiple messages.

        Example:
            POST /v1/kgent/sessions
            {
                "title": "Deep reflection",
                "mode": "reflect"
            }

        Returns:
            Created session
        """
        if not has_scope(api_key, "write"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'write' scope to create sessions",
            )

        # Get tenant
        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(
                status_code=401,
                detail="Tenant context required",
            )

        # Create session
        session = await _tenant_service.create_session(
            tenant_id=tenant.id,
            agent_type=request.agent_type,
            title=request.title,
        )

        # Create KgentFlux instance for this session
        config = KgentFluxConfig(
            pulse_enabled=False,  # No pulse for API sessions
            agent_id=str(session.id),
        )
        flux = create_kgent_flux(config=config)

        # Set initial mode if specified
        if request.mode:
            try:
                mode = DialogueMode(request.mode.lower())
                flux.soul.enter_mode(mode)
            except ValueError:
                pass

        _flux_instances[str(session.id)] = flux

        # Record usage
        await _tenant_service.record_usage(
            tenant_id=tenant.id,
            event_type=UsageEventType.SESSION_CREATE,
            source="api",
            session_id=session.id,
        )

        return SessionResponse(
            id=str(session.id),
            tenant_id=str(session.tenant_id),
            title=session.title,
            agent_type=session.agent_type,
            status=session.status.value if session.status else "unknown",
            message_count=session.message_count,
            tokens_used=session.tokens_used,
            created_at=session.created_at.isoformat() if session.created_at else "",
        )

    @router.get("/sessions", response_model=SessionListResponse)
    async def list_sessions(
        api_key: "ApiKeyData" = Depends(get_api_key),
        limit: int = 20,
        offset: int = 0,
    ) -> SessionListResponse:
        """
        List sessions for the current tenant.

        Example:
            GET /v1/kgent/sessions?limit=10

        Returns:
            List of sessions
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'read' scope",
            )

        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(status_code=401, detail="Tenant context required")

        sessions = await _tenant_service.list_sessions(tenant.id)
        total = len(sessions)

        # Apply pagination
        paginated = sessions[offset : offset + limit]

        return SessionListResponse(
            sessions=[
                SessionResponse(
                    id=str(s.id),
                    tenant_id=str(s.tenant_id),
                    title=s.title,
                    agent_type=s.agent_type,
                    status=s.status.value if s.status else "unknown",
                    message_count=s.message_count,
                    tokens_used=s.tokens_used,
                    created_at=s.created_at.isoformat() if s.created_at else "",
                )
                for s in paginated
            ],
            total=total,
        )

    @router.get("/sessions/{session_id}", response_model=SessionResponse)
    async def get_session(
        session_id: str,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> SessionResponse:
        """
        Get session details.

        Example:
            GET /v1/kgent/sessions/{session_id}

        Returns:
            Session details
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(status_code=401, detail="Tenant context required")

        try:
            uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        session = await _tenant_service.get_session(uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verify tenant ownership
        if session.tenant_id != tenant.id:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=str(session.id),
            tenant_id=str(session.tenant_id),
            title=session.title,
            agent_type=session.agent_type,
            status=session.status.value if session.status else "unknown",
            message_count=session.message_count,
            tokens_used=session.tokens_used,
            created_at=session.created_at.isoformat() if session.created_at else "",
        )

    @router.post("/sessions/{session_id}/messages")
    async def send_message(
        session_id: str,
        request: MessageRequest,
        api_key: "ApiKeyData" = Depends(get_api_key),
        http_request: Request = None,  # type: ignore
    ) -> Any:
        """
        Send a message to a K-gent session.

        By default, returns a Server-Sent Events (SSE) stream with chunks.
        Set stream=false for a single JSON response.

        SSE Events:
        - event: chunk - Partial response text
        - event: complete - Final message with metadata
        - event: error - Error occurred

        Example:
            POST /v1/kgent/sessions/{session_id}/messages
            {
                "message": "What patterns am I avoiding?",
                "stream": true
            }

        Returns:
            SSE stream or MessageResponse
        """
        if not has_scope(api_key, "write"):
            raise HTTPException(
                status_code=403,
                detail="API key requires 'write' scope",
            )

        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(status_code=401, detail="Tenant context required")

        try:
            uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        session = await _tenant_service.get_session(uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.tenant_id != tenant.id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get or create flux instance
        flux = _flux_instances.get(session_id)
        if not flux:
            config = KgentFluxConfig(
                pulse_enabled=False,
                agent_id=session_id,
            )
            flux = create_kgent_flux(config=config)
            _flux_instances[session_id] = flux

        # Store user message (return value unused but side effect is the goal)
        _add_message(session_id, "user", request.message)

        # Parse mode
        mode = None
        if request.mode:
            try:
                mode = DialogueMode(request.mode.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid mode '{request.mode}'",
                )

        if request.stream:
            # Return SSE stream
            return StreamingResponse(
                _stream_response(
                    flux,
                    session_id,
                    request.message,
                    mode,
                    tenant.id,
                    _tenant_service,
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # Non-streaming response
            event = dialogue_turn_event(
                message=request.message,
                mode=mode.value if mode else None,
                is_request=True,
            )
            result = await flux.invoke(event)

            # Store assistant message
            response_text = result.payload.get("response", "")
            tokens_used = result.payload.get("tokens_used", 0)
            assistant_msg = _add_message(
                session_id, "assistant", response_text, tokens_used
            )

            # Record usage
            await _tenant_service.record_usage(
                tenant_id=tenant.id,
                event_type=UsageEventType.LLM_CALL,
                source="kgent",
                tokens_out=tokens_used,
                session_id=uuid,
            )

            # Update session stats
            messages = _get_messages(session_id)
            await _tenant_service.update_session(
                uuid,
                message_count=len(messages),
                tokens_used=sum(m.get("tokens_used", 0) for m in messages),
            )

            return MessageResponse(
                id=assistant_msg["id"],
                session_id=session_id,
                role="assistant",
                content=response_text,
                tokens_used=tokens_used,
                created_at=assistant_msg["created_at"],
            )

    @router.get("/sessions/{session_id}/messages")
    async def get_messages(
        session_id: str,
        api_key: "ApiKeyData" = Depends(get_api_key),
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Get message history for a session.

        Example:
            GET /v1/kgent/sessions/{session_id}/messages

        Returns:
            List of messages
        """
        if not has_scope(api_key, "read"):
            raise HTTPException(status_code=403, detail="API key requires 'read' scope")

        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(status_code=401, detail="Tenant context required")

        try:
            uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        session = await _tenant_service.get_session(uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.tenant_id != tenant.id:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = _get_messages(session_id)
        total = len(messages)
        paginated = messages[offset : offset + limit]

        return {
            "messages": paginated,
            "total": total,
            "session_id": session_id,
        }

    return router


async def _stream_response(
    flux: Any,
    session_id: str,
    message: str,
    mode: Any,
    tenant_id: UUID,
    tenant_service: Any,
) -> AsyncIterator[str]:
    """
    Generate real-time SSE stream for K-gent response.

    Uses KgentFlux.soul.dialogue() with on_chunk callback for
    real streaming instead of simulated chunking.
    """
    from agents.k.soul import BudgetTier

    chunks: list[str] = []
    chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

    def on_chunk(chunk_text: str) -> None:
        """Callback for each streaming chunk from LLM."""
        chunk_queue.put_nowait(chunk_text)

    # Track dialogue result
    dialogue_result: Any = None
    dialogue_error: Exception | None = None

    async def run_dialogue() -> None:
        """Run dialogue in background, pushing chunks to queue."""
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
            # Signal completion
            chunk_queue.put_nowait(None)

    # Start dialogue task
    dialogue_task = asyncio.create_task(run_dialogue())

    try:
        # Stream chunks as they arrive
        chunk_index = 0
        while True:
            chunk = await chunk_queue.get()

            if chunk is None:
                # Dialogue complete
                break

            chunks.append(chunk)
            yield f"event: chunk\ndata: {json.dumps({'text': chunk, 'index': chunk_index})}\n\n"
            chunk_index += 1

        # Wait for dialogue task to complete
        await dialogue_task

        # Check for errors
        if dialogue_error is not None:
            raise dialogue_error

        # Get final results
        response_text = dialogue_result.response if dialogue_result else "".join(chunks)
        tokens_used = dialogue_result.tokens_used if dialogue_result else 0

        # Store assistant message
        _add_message(session_id, "assistant", response_text, tokens_used)

        # Record usage
        await tenant_service.record_usage(
            tenant_id=tenant_id,
            event_type=UsageEventType.LLM_CALL,
            source="kgent",
            tokens_out=tokens_used,
            session_id=UUID(session_id),
        )

        # Update session stats
        messages = _get_messages(session_id)
        await tenant_service.update_session(
            UUID(session_id),
            message_count=len(messages),
            tokens_used=sum(m.get("tokens_used", 0) for m in messages),
        )

        # Send complete event
        complete_data = {
            "text": response_text,
            "tokens_used": tokens_used,
            "chunks": len(chunks),
        }
        yield f"event: complete\ndata: {json.dumps(complete_data)}\n\n"

    except Exception as e:
        # Cancel dialogue task if still running
        if not dialogue_task.done():
            dialogue_task.cancel()
            try:
                await dialogue_task
            except asyncio.CancelledError:
                pass

        # Send error event
        error_data = {"error": str(e), "type": type(e).__name__}
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


# Import for type checking
if TYPE_CHECKING:
    from protocols.tenancy.models import UsageEventType
