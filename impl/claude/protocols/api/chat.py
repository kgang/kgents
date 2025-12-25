"""
Chat REST API: Chat session management with K-gent governance.

Provides:
- POST /api/chat/session - Create new session
- POST /api/chat/sessions - Create new session (plural alias)
- GET /api/chat/session/:id - Get session by ID
- GET /api/chat/sessions - List all sessions with filtering and pagination
- GET /api/chat/sessions/:id - Get session by ID (plural alias)
- DELETE /api/chat/:id - Delete session and all related data
- POST /api/chat/:id/send - Send message (streaming SSE response via K-gent)
- POST /api/chat/:id/fork - Fork session at specific turn
- POST /api/chat/:id/merge - Merge two sessions with strategy (sequential/interleave/manual)
- POST /api/chat/:id/rewind - Rewind session by removing turns
- POST /api/chat/:id/checkpoint - Create checkpoint of current session state
- GET /api/chat/:id/evidence - Get Bayesian evidence state
- GET /api/chat/sessions/:id/branches - Get branch tree for session
- POST /api/chat/mention/resolve - Resolve @mention to content
- POST /api/chat/mention/search/files - Search files for autocomplete
- POST /api/chat/mention/search/symbols - Search symbols for autocomplete
- POST /api/chat/mention/witness - Get witness marks

Architecture:
- In-memory storage (dict) for now - will migrate to D-gent persistence
- SSE streaming for real-time message delivery via K-gent Soul
- Bayesian evidence accumulation (beta distribution)
- Git-like branching with fork_point tracking
- Context size tracking for token budget awareness
- K-gent governance: All LLM calls routed through K-gent for gating & witness marks

Evidence Model:
- prior_alpha, prior_beta: Beta distribution parameters
- Uniform prior (alpha=1, beta=1) for new sessions
- Updates: alpha += successes, beta += failures
- Confidence threshold for should_stop signal (>0.95)

Turn Schema:
- API layer uses Turn with Message objects (rich model for frontend)
- Service layer uses Turn with string fields (simple model for internal ops)
- Conversion at boundary: service Turn.to_api_turn() / Turn.from_api_turn()

See: spec/protocols/chat-web.md
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Literal, Optional

try:
    from fastapi import APIRouter, HTTPException, Path, Query
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

from agents.k import DialogueMode
from services.chat import ChatContext, KgentBridge, create_kgent_bridge


# Persistence (NOTE: Requires model converters - API models != domain models)
# from services.chat.persistence import ChatPersistence

logger = logging.getLogger(__name__)

# Global K-gent bridge instance (singleton)
_kgent_bridge = None




# Global persistence instance (currently disabled - see NOTE)
# NOTE: ChatPersistence uses domain models (services.chat.ChatSession with SessionNode, WorkingContext)
# while this API uses Pydantic ChatSession. Full integration requires bidirectional model converters.
# For production persistence, use chat_persistent.py which uses domain models throughout.
_persistence = None


async def _get_persistence() -> None:
    """
    Get ChatPersistence instance (stub - requires model converters).

    To enable:
    1. Uncomment ChatPersistence import above
    2. Implement API model <-> Domain model converters
    3. Uncomment instantiation below
    4. Add save/load calls in endpoints with conversion
    """
    global _persistence
    if _persistence is None:
        # TODO: Uncomment when converters implemented
        # from services.chat.persistence import ChatPersistence
        # _persistence = ChatPersistence()
        logger.debug("ChatPersistence disabled (use chat_persistent.py for persistence)")
    return _persistence


def get_kgent_bridge() -> KgentBridge:
    """Get or create the global K-gent bridge."""
    global _kgent_bridge
    if _kgent_bridge is None:
        _kgent_bridge = create_kgent_bridge()
    return _kgent_bridge


# =============================================================================
# Pydantic Models
# =============================================================================


class Mention(BaseModel):
    """A mention in a message."""

    type: Literal["file", "symbol", "spec", "witness", "web", "terminal", "project"]
    query: str
    resolved_path: str | None = None


class Message(BaseModel):
    """A message in a turn."""

    role: Literal["user", "assistant", "system"]
    content: str
    mentions: list[Mention] = []
    linearity_tag: Literal["required", "preserved", "droppable"] = "preserved"


class ToolUse(BaseModel):
    """A tool invocation in a turn."""

    name: str
    input: dict[str, Any]
    output: Any
    success: bool
    duration_ms: float


class EvidenceDelta(BaseModel):
    """Evidence delta for a single turn."""

    tools_executed: int = 0
    tools_succeeded: int = 0
    confidence_change: float = 0.0


class ChatEvidence(BaseModel):
    """Evidence accumulator for a session."""

    prior_alpha: float = 1.0
    prior_beta: float = 1.0
    confidence: float = 0.5
    should_stop: bool = False
    tools_succeeded: int = 0
    tools_failed: int = 0
    ashc_equivalence: float | None = None
    ashc_data: dict[str, Any] | None = None  # Full ASHC output for UI display


class PortalEmissionAPI(BaseModel):
    """Portal emission in a turn."""

    portal_id: str
    destination: str
    edge_type: str
    access: Literal["read", "readwrite"]
    content_preview: str | None = None
    content_full: str | None = None
    line_count: int = 0
    exists: bool = True
    auto_expand: bool = True
    emitted_at: str


class Turn(BaseModel):
    """
    A single conversation turn (API model).

    This is the rich API model with Message objects for frontend communication.
    The service layer uses a simpler Turn dataclass with string fields.

    Conversion:
        - To service: services.chat.context.Turn.from_api_turn(api_turn)
        - From service: service_turn.to_api_turn()

    See: services.chat.context.Turn
    """

    turn_number: int
    user_message: Message
    assistant_response: Message
    tools_used: list[ToolUse] = []
    portal_emissions: list[PortalEmissionAPI] = []
    evidence_delta: EvidenceDelta
    confidence: float
    started_at: str
    completed_at: str


class ChatSession(BaseModel):
    """A chat session with branching and evidence tracking."""

    id: str
    project_id: str | None = None
    branch_name: str = "main"
    parent_id: str | None = None
    fork_point: int | None = None
    turns: list[Turn] = []
    context_size: int = 0
    evidence: ChatEvidence
    created_at: str
    last_active: str
    is_merged: bool = False
    merged_into: str | None = None


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


class MergeSessionRequest(BaseModel):
    """Request to merge two sessions."""

    other_id: str = Field(..., description="Session ID to merge with")
    strategy: Literal["sequential", "interleave", "manual"] = Field(
        "sequential", description="Merge strategy to use"
    )


class RewindSessionRequest(BaseModel):
    """Request to rewind a session."""

    turns: int = Field(..., description="Number of turns to rewind", ge=1)


class BranchInfo(BaseModel):
    """Branch information for session tree.

    Uses snake_case for consistency with Python conventions and frontend expectations.
    """

    id: str
    parent_id: str | None = None
    fork_point: int
    branch_name: str
    turn_count: int
    created_at: str
    last_active: str
    is_merged: bool = False
    merged_into: str | None = None
    is_active: bool


class BranchesResponse(BaseModel):
    """Response containing list of branches."""

    branches: list[BranchInfo]


class PortalEmitRequest(BaseModel):
    """Request to emit a portal."""

    destination: str
    edge_type: str = "context"
    access: Literal["read", "readwrite"] = "read"
    auto_expand: bool = True


class PortalWriteRequest(BaseModel):
    """Request to write through a portal."""

    portal_id: str
    content: str


# =============================================================================
# In-Memory Storage
# =============================================================================

# In-memory storage for sessions (will be replaced with persistence)
_sessions: dict[str, ChatSession] = {}


def _calculate_context_size(turns: list[Turn]) -> int:
    """Calculate approximate context size from turns."""
    size = 0
    for turn in turns:
        size += len(turn.user_message.content)
        size += len(turn.assistant_response.content)
    return size


def _update_evidence(
    evidence: ChatEvidence, delta: EvidenceDelta, confidence: float
) -> ChatEvidence:
    """
    Update evidence accumulator with new delta.

    Computes confidence from Beta posterior based on tool success/failure.
    """
    tools_succeeded = evidence.tools_succeeded + delta.tools_succeeded
    tools_failed = evidence.tools_failed + (delta.tools_executed - delta.tools_succeeded)

    # Update beta distribution parameters
    # alpha = successes + 1, beta = failures + 1 (uniform prior)
    prior_alpha = tools_succeeded + 1.0
    prior_beta = tools_failed + 1.0

    # Compute confidence from Beta posterior (mean)
    posterior_mean = prior_alpha / (prior_alpha + prior_beta)

    return ChatEvidence(
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
        confidence=posterior_mean,  # Computed from posterior, not passed through
        should_stop=posterior_mean > 0.95,  # High confidence threshold
        tools_succeeded=tools_succeeded,
        tools_failed=tools_failed,
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_chat_router() -> "APIRouter | None":
    """Create the chat API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/chat", tags=["chat"])

    @router.post("/session", response_model=ChatSession, status_code=201)
    async def create_session(request: CreateSessionRequest) -> ChatSession:
        """
        Create a new chat session.

        Args:
            request: Session creation request

        Returns:
            Created session
        """
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        session = ChatSession(
            id=session_id,
            project_id=request.project_id,
            branch_name=request.branch_name,
            turns=[],
            context_size=0,
            evidence=ChatEvidence(),
            created_at=now,
            last_active=now,
        )

        _sessions[session_id] = session
        # TODO: await persistence.save_session(converted_session) - requires API->Domain converter
        logger.info(f"Created chat session: {session_id}")

        return session

    @router.get("/session/{session_id}", response_model=ChatSession)
    async def get_session(
        session_id: str = Path(..., description="Session ID"),
    ) -> ChatSession:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data

        Raises:
            HTTPException: If session not found
        """
        # TODO: Try persistence.load_session() first, convert to API model, cache in _sessions
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return _sessions[session_id]

    @router.get("/sessions", response_model=list[ChatSession])
    async def list_sessions(
        project_id: str | None = Query(None, description="Filter by project ID"),
        limit: int = Query(50, le=100, description="Maximum number of sessions to return"),
        offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    ) -> list[ChatSession]:
        """
        List all chat sessions with optional filters.

        Args:
            project_id: Optional project ID filter
            limit: Maximum sessions to return (default 50, max 100)
            offset: Number of sessions to skip (default 0)

        Returns:
            List of sessions sorted by last_active (most recent first)
        """
        # Filter sessions by project_id if provided
        sessions = list(_sessions.values())
        if project_id is not None:
            sessions = [s for s in sessions if s.project_id == project_id]

        # Sort by last_active (most recent first)
        sessions.sort(key=lambda s: s.last_active, reverse=True)

        # Apply pagination
        return sessions[offset : offset + limit]

    @router.get("/sessions/{session_id}", response_model=ChatSession)
    async def get_session_plural(
        session_id: str = Path(..., description="Session ID"),
    ) -> ChatSession:
        """
        Get a session by ID (plural path alias).

        This is an alias for GET /session/{session_id} to support
        both /session/:id and /sessions/:id routes.

        Args:
            session_id: Session identifier

        Returns:
            Session data

        Raises:
            HTTPException: If session not found
        """
        return await get_session(session_id)

    @router.post("/sessions", response_model=ChatSession, status_code=201)
    async def create_session_plural(request: CreateSessionRequest) -> ChatSession:
        """
        Create a new chat session (plural path alias).

        This is an alias for POST /session to support
        both /session and /sessions routes.

        Args:
            request: Session creation request

        Returns:
            Created session
        """
        return await create_session(request)

    @router.delete("/{session_id}", status_code=204)
    async def delete_session(
        session_id: str = Path(..., description="Session ID to delete"),
    ) -> None:
        """
        Delete a session and all related data.

        This is a permanent deletion that removes the session from storage.
        All turns, evidence, and branch relationships are deleted.

        Args:
            session_id: Session identifier

        Raises:
            HTTPException: If session not found
        """
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Delete session from storage
        del _sessions[session_id]
        logger.info(f"Deleted session: {session_id}")

        # Note: 204 No Content returns None

    @router.post("/{session_id}/checkpoint", status_code=201)
    async def checkpoint_session(
        session_id: str = Path(..., description="Session ID"),
    ) -> dict[str, Any]:
        """
        Create a checkpoint of current session state.

        Checkpoints capture the full session state including all turns,
        evidence, and metadata for potential restoration or analysis.

        Args:
            session_id: Session identifier

        Returns:
            Dict with checkpoint ID and metadata

        Raises:
            HTTPException: If session not found
        """
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session = _sessions[session_id]

        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Create checkpoint data (in production, this would be persisted)
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "session_id": session_id,
            "created_at": now,
            "turn_count": len(session.turns),
            "context_size": session.context_size,
            "branch_name": session.branch_name,
            "evidence_snapshot": {
                "confidence": session.evidence.confidence,
                "tools_succeeded": session.evidence.tools_succeeded,
                "tools_failed": session.evidence.tools_failed,
            },
        }

        logger.info(
            f"Created checkpoint {checkpoint_id} for session {session_id} at turn {len(session.turns)}"
        )

        return checkpoint

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
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session = _sessions[session_id]

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events for streaming response via K-gent."""
            try:
                started_at = datetime.now().isoformat()
                turn_number = len(session.turns) + 1

                # Create user message
                user_message = Message(
                    role="user",
                    content=request.message,
                    mentions=[],
                    linearity_tag="required",
                )

                # Create chat context for K-gent
                chat_context = ChatContext(
                    session_id=session_id,
                    turn_number=turn_number,
                    user_message=request.message,
                    mode=DialogueMode.ADVISE,  # Default to ADVISE for chat
                )

                # Stream response from K-gent bridge
                bridge = get_kgent_bridge()
                accumulated = ""
                completed_at = None
                mark_id = None
                tools_used: list[dict[str, Any]] = []

                async for sse_chunk in bridge.stream_response(chat_context):
                    # Parse the chunk to track state and filter events
                    # SSE format: "data: {json}\n\n"
                    if sse_chunk.startswith("data: "):
                        try:
                            json_str = sse_chunk[6:].strip()
                            if json_str:
                                data = json.loads(json_str)
                                if data.get("type") == "content":
                                    accumulated = data.get("content", "")
                                    # Pass through content events
                                    yield sse_chunk
                                elif data.get("type") == "done":
                                    # DON'T pass through raw 'done' event from KgentBridge
                                    # We'll send our own with properly formatted Turn object
                                    turn_data = data.get("turn", {})
                                    completed_at = turn_data.get("completed_at")
                                    mark_id = turn_data.get("mark_id")
                                    tools_used = turn_data.get("tools_used", [])
                                elif data.get("type") == "error":
                                    # Pass through error events
                                    yield sse_chunk
                        except json.JSONDecodeError:
                            pass  # Ignore malformed JSON
                    else:
                        # Pass through other events (shouldn't happen, but safe)
                        yield sse_chunk

                # Build turn object for session storage
                if not completed_at:
                    completed_at = datetime.now().isoformat()

                assistant_message = Message(
                    role="assistant",
                    content=accumulated,
                    mentions=[],
                    linearity_tag="preserved",
                )

                # Extract tool results from K-gent response
                tools_executed = len(tools_used)
                tools_succeeded = sum(1 for t in tools_used if t.get("success", False))

                # Compute confidence change based on tool results
                # If no tools used, assume neutral (small positive change)
                if tools_executed == 0:
                    confidence_change = 0.05  # Neutral turn
                else:
                    # Confidence change is the delta from expected 50% success rate
                    actual_success_rate = tools_succeeded / tools_executed
                    confidence_change = actual_success_rate - 0.5

                evidence_delta = EvidenceDelta(
                    tools_executed=tools_executed,
                    tools_succeeded=tools_succeeded,
                    confidence_change=confidence_change,
                )

                # Compute turn confidence from current evidence state
                # This will be the posterior mean after this turn's evidence
                # TODO: Integrate ASHC evidence accumulation for spec edits
                # See: services.chat.ashc_bridge.ASHCBridge for spec compilation evidence
                temp_evidence = _update_evidence(
                    session.evidence, evidence_delta, 0.0  # confidence param ignored now
                )
                turn_confidence = temp_evidence.confidence

                turn = Turn(
                    turn_number=turn_number,
                    user_message=user_message,
                    assistant_response=assistant_message,
                    tools_used=[
                        ToolUse(
                            name=t.get("name", "unknown"),
                            input=t.get("input", {}),
                            output=t.get("output"),
                            success=t.get("success", False),
                            duration_ms=t.get("duration_ms", 0.0),
                        )
                        for t in tools_used
                    ],
                    evidence_delta=evidence_delta,
                    confidence=turn_confidence,
                    started_at=started_at,
                    completed_at=completed_at,
                )

                # Update session
                session.turns.append(turn)
                session.context_size = _calculate_context_size(session.turns)
                session.evidence = temp_evidence  # Use pre-computed evidence
                session.last_active = completed_at
                # TODO: await persistence.save_session(converted_session) after updating

                # Send properly formatted 'done' event to frontend
                # The turn object must match the frontend's Turn interface
                done_event = {
                    "type": "done",
                    "turn": turn.model_dump(),  # Serialize Pydantic model to dict
                }
                yield f"data: {json.dumps(done_event)}\n\n"

            except Exception as e:
                logger.exception("Error in K-gent message streaming")
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

    @router.post("/{session_id}/fork", response_model=ChatSession, status_code=201)
    async def fork_session(
        request: ForkSessionRequest,
        session_id: str = Path(..., description="Session ID to fork"),
    ) -> ChatSession:
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
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        parent_session = _sessions[session_id]
        fork_point = request.fork_point or len(parent_session.turns)

        # Validate fork point
        if fork_point > len(parent_session.turns):
            raise HTTPException(
                status_code=400,
                detail=f"Fork point {fork_point} exceeds number of turns {len(parent_session.turns)}",
            )

        # Create new session
        new_session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Copy turns up to fork point
        forked_turns = parent_session.turns[:fork_point]

        new_session = ChatSession(
            id=new_session_id,
            project_id=parent_session.project_id,
            branch_name=request.branch_name,
            parent_id=parent_session.id,
            fork_point=fork_point,
            turns=forked_turns,
            context_size=_calculate_context_size(forked_turns),
            evidence=ChatEvidence(),  # Reset evidence for fork
            created_at=now,
            last_active=now,
        )

        _sessions[new_session_id] = new_session
        # TODO: await persistence.save_session(converted_new_session) - requires API->Domain converter
        logger.info(
            f"Forked session {session_id} at turn {fork_point} -> {new_session_id} ({request.branch_name})"
        )

        return new_session

    @router.post("/{session_id}/merge", response_model=ChatSession, status_code=201)
    async def merge_session(
        request: MergeSessionRequest,
        session_id: str = Path(..., description="Session ID to merge into"),
    ) -> ChatSession:
        """
        Merge another session into this one.

        Creates a new merged session combining turns from both sessions.
        Marks both source sessions as merged.

        Args:
            session_id: Target session ID
            request: Merge request

        Returns:
            New merged session

        Raises:
            HTTPException: If either session not found
        """
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        if request.other_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {request.other_id} not found")

        base_session = _sessions[session_id]
        other_session = _sessions[request.other_id]

        # Merge turns based on strategy
        if request.strategy == "sequential":
            # Append other's turns after base session's turns
            merged_turns = base_session.turns + other_session.turns
        elif request.strategy == "interleave":
            # Merge by timestamp (started_at)
            merged_turns = sorted(
                base_session.turns + other_session.turns,
                key=lambda t: t.started_at,
            )
        else:  # manual
            # For now, treat manual same as sequential
            # In the future, this could support user-selected turns
            merged_turns = base_session.turns + other_session.turns

        # Combine evidence - use session with more observations
        base_observations = (
            base_session.evidence.prior_alpha + base_session.evidence.prior_beta
        )
        other_observations = (
            other_session.evidence.prior_alpha + other_session.evidence.prior_beta
        )

        if base_observations >= other_observations:
            merged_evidence = ChatEvidence(
                prior_alpha=base_session.evidence.prior_alpha,
                prior_beta=base_session.evidence.prior_beta,
                confidence=base_session.evidence.confidence,
                should_stop=base_session.evidence.should_stop,
                tools_succeeded=base_session.evidence.tools_succeeded,
                tools_failed=base_session.evidence.tools_failed,
            )
        else:
            merged_evidence = ChatEvidence(
                prior_alpha=other_session.evidence.prior_alpha,
                prior_beta=other_session.evidence.prior_beta,
                confidence=other_session.evidence.confidence,
                should_stop=other_session.evidence.should_stop,
                tools_succeeded=other_session.evidence.tools_succeeded,
                tools_failed=other_session.evidence.tools_failed,
            )

        # Create new merged session
        merged_session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        merged_session = ChatSession(
            id=merged_session_id,
            project_id=base_session.project_id or other_session.project_id,
            branch_name=f"{base_session.branch_name}+{other_session.branch_name}",
            parent_id=base_session.id,
            fork_point=None,  # Merged sessions don't have a fork point
            turns=merged_turns,
            context_size=_calculate_context_size(merged_turns),
            evidence=merged_evidence,
            created_at=now,
            last_active=now,
        )

        # Store merged session
        _sessions[merged_session_id] = merged_session

        # Mark source sessions as merged
        base_session.is_merged = True
        base_session.merged_into = merged_session_id
        other_session.is_merged = True
        other_session.merged_into = merged_session_id

        # TODO: await persistence.save_session(converted_merged_session)
        logger.info(
            f"Merged sessions {session_id} + {request.other_id} -> {merged_session_id} "
            f"({request.strategy} strategy, {len(merged_turns)} turns)"
        )

        return merged_session

    @router.post("/{session_id}/rewind", response_model=ChatSession)
    async def rewind_session(
        request: RewindSessionRequest,
        session_id: str = Path(..., description="Session ID"),
    ) -> ChatSession:
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
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session = _sessions[session_id]

        if request.turns > len(session.turns):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot rewind {request.turns} turns, session only has {len(session.turns)} turns",
            )

        # Remove last N turns
        session.turns = session.turns[: -request.turns]
        session.context_size = _calculate_context_size(session.turns)
        session.last_active = datetime.now().isoformat()

        # Recalculate evidence
        session.evidence = ChatEvidence()
        for turn in session.turns:
            session.evidence = _update_evidence(
                session.evidence, turn.evidence_delta, turn.confidence
            )

        # TODO: await persistence.save_session(converted_session) after rewind
        logger.info(f"Rewound session {session_id} by {request.turns} turns")

        return session

    @router.get("/{session_id}/evidence", response_model=ChatEvidence)
    async def get_evidence(
        session_id: str = Path(..., description="Session ID"),
    ) -> ChatEvidence:
        """
        Get the current evidence state for a session.

        Args:
            session_id: Session identifier

        Returns:
            Evidence state

        Raises:
            HTTPException: If session not found
        """
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return _sessions[session_id].evidence

    @router.get("/sessions/{session_id}/branches", response_model=BranchesResponse)
    async def get_branches(
        session_id: str = Path(..., description="Session ID"),
    ) -> BranchesResponse:
        """
        Get branch tree for a session.

        Returns all branches (main + forks) with parent relationships
        for building the branch tree visualization.

        Args:
            session_id: Session identifier (can be any branch in the tree)

        Returns:
            List of branches with parent relationships

        Raises:
            HTTPException: If session not found
        """
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Build branch tree by traversing parent relationships
        current_session = _sessions[session_id]

        # Find root session (main branch)
        root_id = session_id
        visited = {session_id}
        while current_session.parent_id is not None:
            if current_session.parent_id in visited:
                # Circular reference - break
                break
            root_id = current_session.parent_id
            visited.add(root_id)
            if root_id not in _sessions:
                break
            current_session = _sessions[root_id]

        # Collect all branches (root + all descendants)
        branches: list[BranchInfo] = []
        to_process = [root_id]
        processed = set()

        while to_process:
            session_id_to_process = to_process.pop(0)
            if session_id_to_process in processed:
                continue
            processed.add(session_id_to_process)

            if session_id_to_process not in _sessions:
                continue

            session = _sessions[session_id_to_process]

            # Convert session to BranchInfo
            branch = BranchInfo(
                id=session.id,
                parent_id=session.parent_id,
                fork_point=session.fork_point or 0,
                branch_name=session.branch_name,
                turn_count=len(session.turns),
                created_at=session.created_at,
                last_active=session.last_active,
                is_merged=session.is_merged,
                merged_into=session.merged_into,
                is_active=(session.id == session_id),  # Mark original requested session as active
            )
            branches.append(branch)

            # Find children (sessions that have this session as parent)
            children = [
                sid for sid, s in _sessions.items() if s.parent_id == session_id_to_process
            ]
            to_process.extend(children)

        return BranchesResponse(branches=branches)

    # =========================================================================
    # Trust Escalation Endpoints
    # =========================================================================

    @router.get("/trust/suggest-escalation")
    async def suggest_escalation(
        tool_name: str = Query(..., description="Tool name to check"),
        user_id: str = Query("default", description="User ID"),
    ) -> dict[str, Any]:
        """
        Check if trust escalation should be suggested for a tool.

        Args:
            tool_name: Tool name (e.g., "Edit", "Write", "Bash")
            user_id: User identifier

        Returns:
            Dict with should_suggest (bool) and approval_count (int)
        """
        from services.chat.trust_manager import get_trust_manager

        trust_manager = get_trust_manager()
        should_suggest = trust_manager.suggest_escalation(user_id, tool_name)

        if should_suggest:
            stats = trust_manager.get_tool_stats(user_id, tool_name)
            # Mark as suggested to avoid re-suggesting
            trust_manager.mark_escalation_suggested(user_id, tool_name)
            return {
                "should_suggest": True,
                "approval_count": stats["approval_count"],
            }

        return {"should_suggest": False}

    @router.post("/trust/choice")
    async def handle_trust_choice(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Handle user's trust choice for a tool.

        Args:
            request: Dict with tool_name and choice ('trust' | 'keep_asking' | 'never')

        Returns:
            Success response
        """
        from services.chat.trust_manager import get_trust_manager

        tool_name = request.get("tool_name")
        choice = request.get("choice")
        user_id = request.get("user_id", "default")

        if not tool_name or not choice:
            raise HTTPException(status_code=400, detail="Missing tool_name or choice")

        trust_manager = get_trust_manager()

        if choice == "trust":
            trust_manager.escalate_trust(user_id, tool_name)
        elif choice == "never":
            trust_manager.set_never_trust(user_id, tool_name)
        # keep_asking: do nothing (already in ASK state)

        return {"success": True}

    @router.get("/trust/stats")
    async def get_tool_trust_stats(
        tool_name: str = Query(..., description="Tool name"),
        user_id: str = Query("default", description="User ID"),
    ) -> dict[str, Any]:
        """
        Get trust statistics for a tool.

        Args:
            tool_name: Tool name
            user_id: User identifier

        Returns:
            Tool trust statistics
        """
        from services.chat.trust_manager import get_trust_manager

        trust_manager = get_trust_manager()
        return trust_manager.get_tool_stats(user_id, tool_name)

    @router.get("/trust/profile")
    async def get_trust_profile(
        user_id: str = Query("default", description="User ID"),
    ) -> dict[str, Any]:
        """
        Get user's trust profile summary.

        Args:
            user_id: User identifier

        Returns:
            Trust profile summary
        """
        from services.chat.trust_manager import get_trust_manager

        trust_manager = get_trust_manager()
        return trust_manager.get_trust_summary(user_id)

    @router.post("/trust/revoke")
    async def revoke_trust(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Revoke trust for a tool.

        Args:
            request: Dict with tool_name and optional user_id

        Returns:
            Success response
        """
        from services.chat.trust_manager import get_trust_manager

        tool_name = request.get("tool_name")
        user_id = request.get("user_id", "default")

        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing tool_name")

        trust_manager = get_trust_manager()
        trust_manager.revoke_trust(user_id, tool_name)

        return {"success": True}

    # =========================================================================
    # =========================================================================
    # Mention Resolution Endpoints (Part VI: Context Injection)
    # =========================================================================

    @router.post("/mention/resolve")
    async def resolve_mention(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve @mention to content for context injection.

        Args:
            request: Dict with:
                - type: MentionType ('file' | 'symbol' | 'spec' | 'witness' | 'web' | 'terminal' | 'project')
                - target: string (file path, symbol name, URL, etc.)

        Returns:
            Dict with:
                - content: string (resolved content)
                - metadata: dict (type-specific metadata)

        Raises:
            HTTPException: If type invalid or resolution fails
        """
        from pathlib import Path

        mention_type = request.get("type")
        target = request.get("target")

        if not mention_type or not target:
            raise HTTPException(status_code=400, detail="Missing type or target")

        # Get project root (assume we're in impl/claude/protocols/api)
        project_root = Path(__file__).parent.parent.parent.parent

        try:
            if mention_type == "file":
                # Read file content
                file_path = project_root / target.lstrip("/")
                if not file_path.exists():
                    raise HTTPException(status_code=404, detail=f"File not found: {target}")
                if not file_path.is_file():
                    raise HTTPException(status_code=400, detail=f"Not a file: {target}")

                content = file_path.read_text(encoding="utf-8")
                return {
                    "content": content,
                    "metadata": {
                        "path": str(file_path.relative_to(project_root)),
                        "size": len(content),
                        "lines": content.count("\n") + 1,
                    },
                }

            elif mention_type == "spec":
                # Read from spec/ directory
                spec_path = project_root / "spec" / target.lstrip("/")
                if not spec_path.exists():
                    raise HTTPException(status_code=404, detail=f"Spec not found: {target}")
                if not spec_path.is_file():
                    raise HTTPException(status_code=400, detail=f"Not a file: {target}")

                content = spec_path.read_text(encoding="utf-8")
                return {
                    "content": content,
                    "metadata": {
                        "path": f"spec/{target.lstrip('/')}",
                        "size": len(content),
                        "lines": content.count("\n") + 1,
                    },
                }

            elif mention_type == "project":
                # List project files (top-level overview)
                import fnmatch

                files = []
                for item in project_root.rglob("*"):
                    if item.is_file():
                        # Skip common ignore patterns
                        rel_path = item.relative_to(project_root)
                        str_path = str(rel_path)
                        if any(
                            fnmatch.fnmatch(str_path, pattern)
                            for pattern in [
                                ".*",
                                "*.pyc",
                                "__pycache__/*",
                                ".venv/*",
                                "node_modules/*",
                                "dist/*",
                                "build/*",
                            ]
                        ):
                            continue
                        files.append(str_path)

                # Limit to reasonable size
                files = sorted(files)[:200]

                content = "# Project Files\n\n" + "\n".join(f"- {f}" for f in files)
                return {
                    "content": content,
                    "metadata": {
                        "total_files": len(files),
                        "truncated": len(files) >= 200,
                    },
                }

            elif mention_type == "witness":
                # Placeholder for witness integration
                # TODO: Integrate with witness service
                return {
                    "content": f"# Witness Marks\n\n[Witness integration coming soon]\n\nQuery: {target}",
                    "metadata": {
                        "query": target,
                        "placeholder": True,
                    },
                }

            elif mention_type == "web":
                # Placeholder for web fetch
                # TODO: Integrate with web fetch service
                return {
                    "content": f"# Web Content\n\n[Web fetch coming soon]\n\nURL: {target}",
                    "metadata": {
                        "url": target,
                        "placeholder": True,
                    },
                }

            elif mention_type == "terminal":
                # Placeholder for terminal integration
                # TODO: Integrate with terminal/shell
                return {
                    "content": f"# Terminal Output\n\n[Terminal integration coming soon]\n\nCommand: {target}",
                    "metadata": {
                        "command": target,
                        "placeholder": True,
                    },
                }

            elif mention_type == "symbol":
                # Placeholder for symbol resolution
                # TODO: Integrate with AST parsing
                return {
                    "content": f"# Symbol: {target}\n\n[Symbol resolution coming soon]",
                    "metadata": {
                        "symbol": target,
                        "placeholder": True,
                    },
                }

            else:
                raise HTTPException(status_code=400, detail=f"Unknown mention type: {mention_type}")

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error resolving mention {mention_type}:{target}")
            raise HTTPException(status_code=500, detail=f"Resolution failed: {str(e)}")

    @router.post("/mention/search/files")
    async def search_files(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search files for @file mention autocomplete.

        Args:
            request: Dict with:
                - query: string (search query)

        Returns:
            Dict with:
                - files: list[string] (matching file paths, max 20)

        Raises:
            HTTPException: If search fails
        """
        from pathlib import Path
        import fnmatch

        query = request.get("query", "")

        if not query:
            return {"files": []}

        # Get project root
        project_root = Path(__file__).parent.parent.parent.parent

        try:
            matches = []
            query_lower = query.lower()

            # Walk project directory
            for item in project_root.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(project_root)
                    str_path = str(rel_path)

                    # Skip common ignore patterns
                    if any(
                        fnmatch.fnmatch(str_path, pattern)
                        for pattern in [
                            ".*",
                            "*.pyc",
                            "__pycache__/*",
                            ".venv/*",
                            "node_modules/*",
                            "dist/*",
                            "build/*",
                        ]
                    ):
                        continue

                    # Match query
                    if query_lower in str_path.lower():
                        matches.append(str_path)

                    # Stop at 20 matches
                    if len(matches) >= 20:
                        break

            return {"files": sorted(matches)}

        except Exception as e:
            logger.exception(f"Error searching files for query: {query}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    @router.post("/mention/search/symbols")
    async def search_symbols(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Search symbols for @symbol mention autocomplete.

        Args:
            request: Dict with:
                - query: string (search query)

        Returns:
            Dict with:
                - symbols: list[dict] (matching symbols with name, path, docstring)

        Raises:
            HTTPException: If search fails
        """
        query = request.get("query", "")

        # Placeholder for AST parsing integration
        # TODO: Implement AST-based symbol search
        # This would scan Python files for classes, functions, constants
        # and return matches with their locations and docstrings

        return {
            "symbols": [
                # Example structure for when implemented:
                # {
                #     "name": "ChatSession",
                #     "path": "impl/claude/protocols/api/chat.py",
                #     "docstring": "A chat session with branching and evidence tracking."
                # }
            ]
        }

    @router.post("/mention/witness")
    async def get_witness_marks(
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Get witness marks for @witness mention.

        Args:
            request: Dict with:
                - query: string (optional search query)
                - limit: int (optional max marks to return, default 10)

        Returns:
            Dict with:
                - marks: list[dict] (witness marks with id, content, timestamp)

        Raises:
            HTTPException: If query fails
        """
        query = request.get("query")
        limit = request.get("limit", 10)

        # Placeholder for witness service integration
        # TODO: Integrate with services.witness to fetch actual marks
        # This would query the witness store for recent marks,
        # optionally filtered by query string

        return {
            "marks": [
                # Example structure for when implemented:
                # {
                #     "id": "mark_abc123",
                #     "content": "Implemented mention resolution endpoints",
                #     "timestamp": "2025-12-25T10:30:00Z"
                # }
            ]
        }

    # =========================================================================
    # Portal Tool Endpoints
    # =========================================================================

    @router.post("/portal/emit", response_model=PortalEmissionAPI)
    async def emit_portal(request: PortalEmitRequest) -> PortalEmissionAPI:
        """
        Emit a portal for inline file access in chat.

        Opens a portal to a file/resource that provides inline read/write access
        in the chat interface.

        Args:
            request: Portal emission request

        Returns:
            Portal emission with content preview

        Raises:
            HTTPException: If portal tool fails
        """
        try:
            from services.tooling.tools.portal import PortalTool
            from services.tooling.contracts import PortalRequest

            tool = PortalTool()
            result = await tool.invoke(
                PortalRequest(
                    destination=request.destination,
                    edge_type=request.edge_type,
                    access=request.access,
                    auto_expand=request.auto_expand,
                )
            )

            # Cast access to Literal type (tool uses str, API uses Literal)
            access_typed: Literal["read", "readwrite"] = (
                "readwrite" if result.access == "readwrite" else "read"
            )

            return PortalEmissionAPI(
                portal_id=result.portal_id,
                destination=result.destination,
                edge_type=result.edge_type,
                access=access_typed,
                content_preview=result.content_preview,
                content_full=result.content_full,
                line_count=result.line_count,
                exists=result.exists,
                auto_expand=result.auto_expand,
                emitted_at=result.emitted_at,
            )

        except Exception as e:
            logger.exception(f"Error emitting portal to {request.destination}")
            raise HTTPException(status_code=500, detail=f"Portal emission failed: {str(e)}")

    @router.post("/portal/write")
    async def write_portal(request: PortalWriteRequest) -> dict[str, Any]:
        """
        Write content through an open portal.

        Allows writing back to a file through a portal that was opened
        with readwrite access.

        Args:
            request: Portal write request

        Returns:
            Write result with success status

        Raises:
            HTTPException: If portal not found or write fails
        """
        try:
            from services.tooling.tools.portal import PortalWriteTool
            from services.tooling.contracts import PortalWriteRequest as ToolRequest

            tool = PortalWriteTool()
            result = await tool.invoke(
                ToolRequest(
                    portal_id=request.portal_id,
                    content=request.content,
                )
            )

            return {
                "success": result.success,
                "portal_id": result.portal_id,
                "bytes_written": result.bytes_written,
                "new_content_hash": result.new_content_hash,
                "error_message": result.error_message,
            }

        except Exception as e:
            logger.exception(f"Error writing through portal {request.portal_id}")
            raise HTTPException(status_code=500, detail=f"Portal write failed: {str(e)}")

    # =========================================================================
    # Pre-Execution Gating Endpoints
    # =========================================================================

    @router.post("/{session_id}/approve-tool")
    async def approve_tool(
        request: dict[str, Any],
        session_id: str = Path(..., description="Session ID"),
    ) -> dict[str, Any]:
        """
        Approve or deny a pending tool execution.

        Used for pre-execution gating of destructive operations.

        Args:
            session_id: Session identifier
            request: Approval decision with:
                - request_id: Approval request ID
                - approved: True to approve, False to deny
                - always_allow: True if user chose "Always Allow This Tool"
                - reason: Optional reason for denial

        Returns:
            Success response
        """
        from services.chat.gating import get_pre_execution_gate

        request_id = request.get("request_id")
        approved = request.get("approved", False)
        always_allow = request.get("always_allow", False)
        reason = request.get("reason")

        if not request_id:
            raise HTTPException(status_code=400, detail="Missing request_id")

        gate = get_pre_execution_gate()
        gate.respond_to_approval(
            request_id=request_id,
            approved=approved,
            always_allow=always_allow,
            reason=reason,
        )

        return {"success": True, "approved": approved}

    return router


__all__ = ["create_chat_router"]
