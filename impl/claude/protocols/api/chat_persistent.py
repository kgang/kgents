"""
Chat REST API (Persistent): Chat session management with D-gent persistence.

This is the persistent version of chat.py, backed by ChatPersistence.
Use this router when you need sessions to survive server restarts.

Provides:
- POST /api/chat/session - Create new session
- GET /api/chat/session/:id - Get session by ID
- GET /api/chat/sessions - List sessions with filters
- POST /api/chat/:id/send - Send message (streaming SSE response)
- POST /api/chat/:id/fork - Fork session at specific turn
- POST /api/chat/:id/rewind - Rewind session by removing turns
- GET /api/chat/:id/evidence - Get Bayesian evidence state
- DELETE /api/chat/:id - Delete session
- POST /api/chat/:id/crystal - Crystallize session summary
- GET /api/chat/:id/crystal - Get crystallized summary

Architecture:
- ChatPersistence backed by StorageProvider (SQLite/PostgreSQL)
- Sessions, turns, checkpoints, and crystals persisted to relational store
- SSE streaming for real-time message delivery
- Atomic save operations (session + turns together)
- Survives server restarts

See: spec/protocols/chat-web.md
See: services/chat/persistence.py
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Literal

try:
    from fastapi import APIRouter, HTTPException, Path, Query
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

from services.chat import ChatSession as ChatSessionDomain
from services.chat.persistence import ChatPersistence

logger = logging.getLogger(__name__)

# Global persistence instance (initialized on startup)
_persistence: ChatPersistence | None = None


async def initialize_persistence() -> None:
    """Initialize persistence layer. Call during app startup."""
    global _persistence
    if _persistence is None:
        _persistence = await ChatPersistence.create()
        logger.info("ChatPersistence initialized")


def get_persistence() -> ChatPersistence:
    """Get persistence instance. Raises if not initialized."""
    if _persistence is None:
        raise RuntimeError(
            "ChatPersistence not initialized. Call initialize_persistence() on startup."
        )
    return _persistence


# =============================================================================
# Pydantic Models (API DTOs)
# =============================================================================


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""

    project_id: str | None = Field(None, description="Optional project ID to link session")
    branch_name: str = Field("main", description="Branch name for session")


class SendMessageRequest(BaseModel):
    """Request to send a message."""

    message: str = Field(..., description="User message content")


class ForkSessionRequest(BaseModel):
    """Request to fork a session."""

    branch_name: str = Field(..., description="Name for the forked branch")
    fork_point: int | None = Field(
        None, description="Turn number to fork from (defaults to last turn)"
    )


class RewindSessionRequest(BaseModel):
    """Request to rewind a session."""

    turns: int = Field(..., description="Number of turns to rewind", ge=1)


class CrystallizeRequest(BaseModel):
    """Request to crystallize a session."""

    title: str = Field(..., description="Crystal title")
    summary: str = Field(..., description="Summary text")
    key_decisions: list[str] = Field(default_factory=list, description="Key decisions made")
    artifacts: list[str] = Field(default_factory=list, description="Artifacts produced")


class SessionResponse(BaseModel):
    """Session response DTO."""

    id: str
    project_id: str | None
    branch_name: str
    parent_id: str | None
    fork_point: int | None
    turn_count: int
    context_size: int
    state: str
    evidence: dict[str, Any]
    created_at: str
    last_active: str


class SessionListResponse(BaseModel):
    """List of sessions response."""

    sessions: list[SessionResponse]
    total: int
    limit: int
    offset: int


class CrystalResponse(BaseModel):
    """Crystallized session response."""

    session_id: str
    title: str
    summary: str
    key_decisions: list[str]
    artifacts: list[str]
    final_evidence: dict[str, Any]
    final_turn_count: int
    created_at: str


# =============================================================================
# Converter Functions
# =============================================================================


def domain_to_response(session: ChatSessionDomain) -> SessionResponse:
    """Convert domain ChatSession to API response DTO."""
    return SessionResponse(
        id=session.id,
        project_id=session.project_id,
        branch_name=session.node.branch_name,
        parent_id=session.node.parent_id,
        fork_point=session.node.fork_point,
        turn_count=session.turn_count,
        context_size=session.context_size,
        state=session.state.value,
        evidence=session.evidence.to_dict(),
        created_at=session.node.created_at.isoformat(),
        last_active=session.node.last_active.isoformat(),
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_chat_router() -> "APIRouter | None":
    """Create the persistent chat API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/chat", tags=["chat"])

    @router.post("/session", response_model=SessionResponse, status_code=201)
    async def create_session(request: CreateSessionRequest) -> SessionResponse:
        """
        Create a new chat session.

        Args:
            request: Session creation request

        Returns:
            Created session
        """
        persistence = get_persistence()

        # Create domain session
        session = ChatSessionDomain.create(
            project_id=request.project_id, branch_name=request.branch_name
        )

        # Persist
        await persistence.save_session(session)

        logger.info(f"Created chat session: {session.id}")

        return domain_to_response(session)

    @router.get("/session/{session_id}", response_model=SessionResponse)
    async def get_session(
        session_id: str = Path(..., description="Session ID"),
    ) -> SessionResponse:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        session = await persistence.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return domain_to_response(session)

    @router.get("/sessions", response_model=SessionListResponse)
    async def list_sessions(
        project_id: str | None = Query(None, description="Filter by project ID"),
        branch_name: str | None = Query(None, description="Filter by branch name"),
        limit: int = Query(50, ge=1, le=100, description="Max sessions to return"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
    ) -> SessionListResponse:
        """
        List sessions with optional filters.

        Args:
            project_id: Optional project filter
            branch_name: Optional branch filter
            limit: Max sessions to return
            offset: Pagination offset

        Returns:
            List of sessions
        """
        persistence = get_persistence()

        sessions = await persistence.list_sessions(
            project_id=project_id, branch_name=branch_name, limit=limit, offset=offset
        )

        total = await persistence.count_sessions(project_id=project_id)

        return SessionListResponse(
            sessions=[domain_to_response(s) for s in sessions],
            total=total,
            limit=limit,
            offset=offset,
        )

    @router.post("/{session_id}/send")
    async def send_message(
        request: SendMessageRequest,
        session_id: str = Path(..., description="Session ID"),
    ) -> StreamingResponse:
        """
        Send a message and stream the response.

        Uses SSE (Server-Sent Events) for streaming.

        Args:
            session_id: Session identifier
            request: Message request

        Returns:
            Streaming response with SSE format

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        session = await persistence.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events for streaming response."""
            try:
                started_at = datetime.now()

                # Simulate streaming response (replace with actual LLM call)
                # In production, this would invoke K-gent or another LLM
                response_text = f"Echo: {request.message}\n\nThis is a simulated response. Session is now persistent and survives restarts!"

                # Stream response character by character (simulated)
                accumulated = ""
                for char in response_text:
                    accumulated += char
                    # Send SSE event with current content
                    yield f"data: {json.dumps({'type': 'content', 'content': accumulated})}\n\n"
                    await asyncio.sleep(0.01)  # Simulate typing delay

                completed_at = datetime.now()

                # Add turn to session
                session.add_turn(
                    user_message=request.message, assistant_response=accumulated
                )

                # Persist updated session
                await persistence.save_session(session)

                # Send completion event
                yield f"data: {json.dumps({'type': 'done', 'turn_count': session.turn_count})}\n\n"

            except Exception as e:
                logger.exception("Error in message streaming")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.post("/{session_id}/fork", response_model=SessionResponse, status_code=201)
    async def fork_session(
        request: ForkSessionRequest,
        session_id: str = Path(..., description="Session ID to fork"),
    ) -> SessionResponse:
        """
        Fork a session at a specific turn.

        Creates a new session that branches from the parent.

        Args:
            session_id: Parent session ID
            request: Fork request

        Returns:
            New forked session

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        parent_session = await persistence.load_session(session_id)

        if not parent_session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Use domain fork operation
        _, forked_session = parent_session.fork(branch_name=request.branch_name)

        # If fork_point specified, rewind to that point
        if request.fork_point is not None:
            turns_to_remove = forked_session.turn_count - request.fork_point
            if turns_to_remove > 0:
                forked_session = forked_session.rewind(turns_to_remove)

        # Persist forked session
        await persistence.save_session(forked_session)

        logger.info(
            f"Forked session {session_id} -> {forked_session.id} ({request.branch_name})"
        )

        return domain_to_response(forked_session)

    @router.post("/{session_id}/rewind", response_model=SessionResponse)
    async def rewind_session(
        request: RewindSessionRequest,
        session_id: str = Path(..., description="Session ID"),
    ) -> SessionResponse:
        """
        Rewind a session by removing recent turns.

        Args:
            session_id: Session identifier
            request: Rewind request

        Returns:
            Updated session

        Raises:
            HTTPException: If session not found or rewind count invalid
        """
        persistence = get_persistence()

        session = await persistence.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        if request.turns > session.turn_count:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot rewind {request.turns} turns, session only has {session.turn_count} turns",
            )

        # Use domain rewind operation
        rewound_session = session.rewind(request.turns)

        # Persist rewound session
        await persistence.save_session(rewound_session)

        logger.info(f"Rewound session {session_id} by {request.turns} turns")

        return domain_to_response(rewound_session)

    @router.get("/{session_id}/evidence")
    async def get_evidence(
        session_id: str = Path(..., description="Session ID"),
    ) -> dict[str, Any]:
        """
        Get the current evidence state for a session.

        Args:
            session_id: Session identifier

        Returns:
            Evidence state

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        session = await persistence.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return session.evidence.to_dict()

    @router.delete("/{session_id}", status_code=204)
    async def delete_session(
        session_id: str = Path(..., description="Session ID"),
    ) -> None:
        """
        Delete a session and all related data.

        Args:
            session_id: Session identifier

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        deleted = await persistence.delete_session(session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        logger.info(f"Deleted session {session_id}")

    @router.post("/{session_id}/crystal", response_model=CrystalResponse, status_code=201)
    async def crystallize_session(
        request: CrystallizeRequest,
        session_id: str = Path(..., description="Session ID"),
    ) -> CrystalResponse:
        """
        Crystallize a session into a summary.

        Args:
            session_id: Session identifier
            request: Crystallize request

        Returns:
            Crystal data

        Raises:
            HTTPException: If session not found
        """
        persistence = get_persistence()

        session = await persistence.load_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Save crystal
        await persistence.save_crystal(
            session_id=session_id,
            title=request.title,
            summary=request.summary,
            key_decisions=request.key_decisions,
            artifacts=request.artifacts,
        )

        # Load and return crystal
        crystal = await persistence.load_crystal(session_id)

        if not crystal:
            raise HTTPException(status_code=500, detail="Failed to save crystal")

        return CrystalResponse(**crystal)

    @router.get("/{session_id}/crystal", response_model=CrystalResponse)
    async def get_crystal(
        session_id: str = Path(..., description="Session ID"),
    ) -> CrystalResponse:
        """
        Get crystallized session summary.

        Args:
            session_id: Session identifier

        Returns:
            Crystal data

        Raises:
            HTTPException: If session or crystal not found
        """
        persistence = get_persistence()

        crystal = await persistence.load_crystal(session_id)

        if not crystal:
            raise HTTPException(
                status_code=404, detail=f"No crystal found for session {session_id}"
            )

        return CrystalResponse(**crystal)

    return router


__all__ = ["create_chat_router", "initialize_persistence", "get_persistence"]
