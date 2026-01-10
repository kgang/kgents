"""
N-Phase Session REST API.

Exposes N-Phase session management via REST endpoints:
- POST /v1/nphase/sessions - Create a new session
- GET /v1/nphase/sessions - List sessions
- GET /v1/nphase/sessions/{id} - Get session details
- POST /v1/nphase/sessions/{id}/advance - Advance phase
- POST /v1/nphase/sessions/{id}/checkpoint - Create checkpoint
- POST /v1/nphase/sessions/{id}/handles - Add handle
- POST /v1/nphase/sessions/{id}/detect - Detect phase from output

See: plans/nphase-native-integration.md (Wave 3)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    Depends = None  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment, misc]

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
    """Request to create a new N-Phase session."""

    title: str = Field(
        default="",
        description="Session title",
        examples=["Feature Implementation"],
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata",
    )


class SessionResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with session summary."""

    id: str = Field(..., description="Session ID")
    title: str = Field(default="", description="Session title")
    current_phase: str = Field(..., description="Current phase (UNDERSTAND, ACT, REFLECT)")
    cycle_count: int = Field(default=0, description="Completed cycle count")
    checkpoint_count: int = Field(default=0, description="Number of checkpoints")
    handle_count: int = Field(default=0, description="Number of handles")
    ledger_count: int = Field(default=0, description="Number of ledger entries")
    entropy_spent: dict[str, float] = Field(
        default_factory=dict, description="Entropy spent by category"
    )
    created_at: str = Field(..., description="Creation timestamp")
    last_touched: str = Field(..., description="Last activity timestamp")


class SessionListResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response with list of sessions."""

    sessions: list[SessionResponse] = Field(
        default_factory=list,
        description="List of sessions",
    )
    total: int = Field(default=0, description="Total number of sessions")


class AdvancePhaseRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to advance session phase."""

    target_phase: str | None = Field(
        default=None,
        description="Target phase (UNDERSTAND, ACT, REFLECT). If None, advances to next.",
        examples=["ACT"],
    )
    payload: Any = Field(
        default=None,
        description="Reason or context for the transition",
    )
    auto_checkpoint: bool = Field(
        default=True,
        description="Create checkpoint before advancing",
    )


class PhaseTransitionResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response for phase transition."""

    from_phase: str = Field(..., description="Previous phase")
    to_phase: str = Field(..., description="New phase")
    cycle_count: int = Field(..., description="Current cycle count")
    checkpoint_id: str | None = Field(default=None, description="Created checkpoint ID")


class CheckpointRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to create a checkpoint."""

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Checkpoint metadata",
    )


class CheckpointResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response for checkpoint creation."""

    id: str = Field(..., description="Checkpoint ID")
    session_id: str = Field(..., description="Session ID")
    phase: str = Field(..., description="Phase at checkpoint")
    cycle_count: int = Field(..., description="Cycle count at checkpoint")
    handle_count: int = Field(..., description="Handles at checkpoint")
    created_at: str = Field(..., description="Creation timestamp")


class AddHandleRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to add a handle."""

    path: str = Field(..., description="AGENTESE path", examples=["world.file.manifest"])
    content: Any = Field(..., description="Handle content")


class HandleResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response for handle creation."""

    path: str = Field(..., description="Handle path")
    phase: str = Field(..., description="Phase when acquired")
    created_at: str = Field(..., description="Creation timestamp")


class DetectPhaseRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to detect phase from output."""

    output: str = Field(
        ...,
        description="LLM output to analyze",
        examples=["Research complete. ⟿[ACT]"],
    )
    auto_advance: bool = Field(
        default=False,
        description="Auto-advance if high confidence signal detected",
    )


class DetectPhaseResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response for phase detection."""

    action: str = Field(
        ..., description="Detected action (CONTINUE, HALT, ELASTIC, HEURISTIC, NONE)"
    )
    target_phase: str | None = Field(default=None, description="Suggested phase")
    confidence: float = Field(..., description="Detection confidence")
    reason: str | None = Field(default=None, description="Halt reason if HALT")
    auto_advanced: bool = Field(default=False, description="Whether session was auto-advanced")
    current_phase: str = Field(..., description="Current session phase after detection")


class RestoreCheckpointRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to restore from checkpoint."""

    checkpoint_id: str = Field(..., description="Checkpoint ID to restore")


# --- Router Factory ---


def create_nphase_router() -> "APIRouter":
    """
    Create N-Phase Session API router.

    Returns:
        FastAPI router with session endpoints

    Raises:
        ImportError: If FastAPI is not installed
    """
    if not HAS_FASTAPI:
        return None  # type: ignore[return-value]

    from protocols.nphase.detector import PhaseDetector, SignalAction
    from protocols.nphase.operad import NPhase
    from protocols.nphase.session import (
        create_session,
        delete_session,
        get_session,
        list_sessions,
    )

    router = APIRouter(prefix="/v1/nphase", tags=["nphase"])

    # Shared detector instance
    detector = PhaseDetector()

    @router.post("/sessions", response_model=SessionResponse)
    async def create_nphase_session(
        request: CreateSessionRequest,
    ) -> SessionResponse:
        """
        Create a new N-Phase session.

        Sessions track phase state, checkpoints, and handles across requests.

        Example:
            POST /v1/nphase/sessions
            {
                "title": "Feature Implementation"
            }
        """
        session = create_session(title=request.title, metadata=request.metadata)
        summary = session.summary()

        return SessionResponse(
            id=summary["id"],
            title=summary["title"],
            current_phase=summary["current_phase"],
            cycle_count=summary["cycle_count"],
            checkpoint_count=summary["checkpoint_count"],
            handle_count=summary["handle_count"],
            ledger_count=summary["ledger_count"],
            entropy_spent=summary["entropy_spent"],
            created_at=summary["created_at"],
            last_touched=summary["last_touched"],
        )

    @router.get("/sessions", response_model=SessionListResponse)
    async def list_nphase_sessions(
        limit: int = 20,
        offset: int = 0,
    ) -> SessionListResponse:
        """
        List all N-Phase sessions.

        Example:
            GET /v1/nphase/sessions?limit=10
        """
        sessions = list_sessions()
        total = len(sessions)

        # Apply pagination
        paginated = sessions[offset : offset + limit]

        return SessionListResponse(
            sessions=[
                SessionResponse(
                    id=s.id,
                    title=s.title,
                    current_phase=s.current_phase.name,
                    cycle_count=s.cycle_count,
                    checkpoint_count=len(s.checkpoints),
                    handle_count=len(s.handles),
                    ledger_count=len(s.ledger),
                    entropy_spent=s.entropy_spent,
                    created_at=s.created_at.isoformat(),
                    last_touched=s.last_touched.isoformat(),
                )
                for s in paginated
            ],
            total=total,
        )

    @router.get("/sessions/{session_id}", response_model=SessionResponse)
    async def get_nphase_session(session_id: str) -> SessionResponse:
        """
        Get session details.

        Example:
            GET /v1/nphase/sessions/{session_id}
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        summary = session.summary()
        return SessionResponse(
            id=summary["id"],
            title=summary["title"],
            current_phase=summary["current_phase"],
            cycle_count=summary["cycle_count"],
            checkpoint_count=summary["checkpoint_count"],
            handle_count=summary["handle_count"],
            ledger_count=summary["ledger_count"],
            entropy_spent=summary["entropy_spent"],
            created_at=summary["created_at"],
            last_touched=summary["last_touched"],
        )

    @router.delete("/sessions/{session_id}")
    async def delete_nphase_session(session_id: str) -> dict[str, Any]:
        """
        Delete a session.

        Example:
            DELETE /v1/nphase/sessions/{session_id}
        """
        if not delete_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        return {"deleted": True, "session_id": session_id}

    @router.post("/sessions/{session_id}/advance", response_model=PhaseTransitionResponse)
    async def advance_phase(
        session_id: str,
        request: AdvancePhaseRequest,
    ) -> PhaseTransitionResponse:
        """
        Advance session to next phase.

        If target_phase is not specified, advances to the next phase
        in the cycle (UNDERSTAND → ACT → REFLECT → UNDERSTAND).

        Example:
            POST /v1/nphase/sessions/{session_id}/advance
            {
                "target_phase": "ACT",
                "payload": "Research complete"
            }
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Parse target phase
        target: NPhase | None = None
        if request.target_phase:
            try:
                target = NPhase[request.target_phase.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid phase: {request.target_phase}. Valid: UNDERSTAND, ACT, REFLECT",
                )

        from_phase = session.current_phase

        # Check if auto-checkpoint will create one
        checkpoint_id: str | None = None
        if request.auto_checkpoint:
            cp = session.checkpoint({"trigger": "advance", "reason": "phase_boundary"})
            checkpoint_id = cp.id

        try:
            entry = session.advance_phase(
                target=target,
                payload=request.payload,
                auto_checkpoint=False,  # We already did it above
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return PhaseTransitionResponse(
            from_phase=from_phase.name,
            to_phase=entry.to_phase.name,
            cycle_count=entry.cycle_count,
            checkpoint_id=checkpoint_id,
        )

    @router.post("/sessions/{session_id}/checkpoint", response_model=CheckpointResponse)
    async def create_checkpoint(
        session_id: str,
        request: CheckpointRequest,
    ) -> CheckpointResponse:
        """
        Create a checkpoint at current state.

        Checkpoints enable rollback and session handoff.

        Example:
            POST /v1/nphase/sessions/{session_id}/checkpoint
            {
                "metadata": {"reason": "before risky operation"}
            }
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        cp = session.checkpoint(request.metadata)

        return CheckpointResponse(
            id=cp.id,
            session_id=session_id,
            phase=cp.phase.name,
            cycle_count=cp.cycle_count,
            handle_count=len(cp.handles),
            created_at=cp.created_at.isoformat(),
        )

    @router.post("/sessions/{session_id}/restore")
    async def restore_checkpoint(
        session_id: str,
        request: RestoreCheckpointRequest,
    ) -> SessionResponse:
        """
        Restore session from checkpoint.

        Example:
            POST /v1/nphase/sessions/{session_id}/restore
            {
                "checkpoint_id": "abc123"
            }
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        try:
            session.restore(request.checkpoint_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        summary = session.summary()
        return SessionResponse(
            id=summary["id"],
            title=summary["title"],
            current_phase=summary["current_phase"],
            cycle_count=summary["cycle_count"],
            checkpoint_count=summary["checkpoint_count"],
            handle_count=summary["handle_count"],
            ledger_count=summary["ledger_count"],
            entropy_spent=summary["entropy_spent"],
            created_at=summary["created_at"],
            last_touched=summary["last_touched"],
        )

    @router.post("/sessions/{session_id}/handles", response_model=HandleResponse)
    async def add_handle(
        session_id: str,
        request: AddHandleRequest,
    ) -> HandleResponse:
        """
        Add a handle to the session.

        Handles are AGENTESE paths resolved during session execution.
        They are associated with the current phase.

        Example:
            POST /v1/nphase/sessions/{session_id}/handles
            {
                "path": "world.file.manifest",
                "content": {"file": "session.py", "lines": 100}
            }
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        handle = session.add_handle(request.path, request.content)

        return HandleResponse(
            path=handle.path,
            phase=handle.phase.name,
            created_at=handle.created_at.isoformat(),
        )

    @router.get("/sessions/{session_id}/handles")
    async def list_handles(
        session_id: str,
        phase: str | None = None,
    ) -> dict[str, Any]:
        """
        List handles for a session.

        Optionally filter by phase.

        Example:
            GET /v1/nphase/sessions/{session_id}/handles?phase=UNDERSTAND
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if phase:
            try:
                target_phase = NPhase[phase.upper()]
                handles = session.get_handles_for_phase(target_phase)
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid phase: {phase}")
        else:
            handles = session.handles

        return {
            "handles": [
                {
                    "path": h.path,
                    "phase": h.phase.name,
                    "content": h.content,
                    "created_at": h.created_at.isoformat(),
                }
                for h in handles
            ],
            "total": len(handles),
        }

    @router.get("/sessions/{session_id}/checkpoints")
    async def list_checkpoints(session_id: str) -> dict[str, Any]:
        """
        List checkpoints for a session.

        Example:
            GET /v1/nphase/sessions/{session_id}/checkpoints
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "checkpoints": [cp.to_dict() for cp in session.checkpoints],
            "total": len(session.checkpoints),
        }

    @router.get("/sessions/{session_id}/ledger")
    async def get_ledger(session_id: str) -> dict[str, Any]:
        """
        Get phase transition ledger.

        Returns audit trail of all phase transitions.

        Example:
            GET /v1/nphase/sessions/{session_id}/ledger
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "ledger": [entry.to_dict() for entry in session.ledger],
            "total": len(session.ledger),
        }

    @router.post("/sessions/{session_id}/detect", response_model=DetectPhaseResponse)
    async def detect_phase(
        session_id: str,
        request: DetectPhaseRequest,
    ) -> DetectPhaseResponse:
        """
        Detect phase signal from LLM output.

        Analyzes output for:
        - Explicit signifiers (⟿[PHASE], ⟂[REASON], ⤳[OP:args])
        - Heuristic patterns

        If auto_advance=True and a high-confidence signal is detected,
        automatically advances the session phase.

        Example:
            POST /v1/nphase/sessions/{session_id}/detect
            {
                "output": "Research complete. ⟿[ACT]",
                "auto_advance": true
            }
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        signal = detector.detect(request.output, session.current_phase)
        auto_advanced = False

        # Auto-advance if requested and signal is high confidence transition
        if request.auto_advance and signal.should_auto_advance and signal.target_phase:
            try:
                session.advance_phase(signal.target_phase, payload="auto-detected")
                auto_advanced = True
            except ValueError:
                pass  # Invalid transition, don't auto-advance

        return DetectPhaseResponse(
            action=signal.action.name,
            target_phase=signal.target_phase.name if signal.target_phase else None,
            confidence=signal.confidence,
            reason=signal.reason,
            auto_advanced=auto_advanced,
            current_phase=session.current_phase.name,
        )

    @router.post("/sessions/{session_id}/entropy")
    async def spend_entropy(
        session_id: str,
        category: str,
        amount: float,
    ) -> dict[str, Any]:
        """
        Record entropy expenditure.

        Example:
            POST /v1/nphase/sessions/{session_id}/entropy?category=llm&amount=100
        """
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.spend_entropy(category, amount)

        return {
            "category": category,
            "amount": amount,
            "total": session.entropy_spent,
        }

    return router


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "create_nphase_router",
    # Request/Response models
    "CreateSessionRequest",
    "SessionResponse",
    "SessionListResponse",
    "AdvancePhaseRequest",
    "PhaseTransitionResponse",
    "CheckpointRequest",
    "CheckpointResponse",
    "AddHandleRequest",
    "HandleResponse",
    "DetectPhaseRequest",
    "DetectPhaseResponse",
    "RestoreCheckpointRequest",
]
