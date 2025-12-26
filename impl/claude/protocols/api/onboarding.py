"""
Onboarding API — First Time User Experience Backend

Handles the Genesis FTUE flow with axiom tracking:

FTUE Axioms (from spec/protocols/ftue-axioms.md):
- F1: Identity Seed (first K-Block) - POST /api/onboarding/first-declaration
- F2: Connection Pattern (first edge) - tracked in first-declaration
- F3: Judgment Experience (first judgment) - POST /api/onboarding/judgment
- FG: Growth Witness (witnessed emergence) - POST /api/onboarding/witness-emergence

Each axiom completion:
1. Updates the OnboardingSession with axiom ID and timestamp
2. Creates a witness mark with action and axiom metadata

Philosophy:
"The act of declaring, capturing, and auditing your decisions is itself
a radical act of self-transformation."

See: spec/protocols/ftue-axioms.md
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    HTTPException = None  # type: ignore[misc, assignment]
    BaseModel = object  # type: ignore[misc, assignment]
    Field = lambda **kwargs: None  # type: ignore[misc, assignment]

logger = logging.getLogger(__name__)

# =============================================================================
# Request/Response Models
# =============================================================================


class OnboardingStartRequest(BaseModel):
    """Request to start onboarding session."""

    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")


class OnboardingStartResponse(BaseModel):
    """Response from starting onboarding."""

    session_id: str = Field(..., description="Unique session ID for this onboarding")
    started_at: datetime = Field(..., description="When onboarding started")


class FirstDeclarationRequest(BaseModel):
    """User's first personal axiom."""

    declaration: str = Field(
        ..., description="What matters most to the user right now", min_length=1
    )
    session_id: Optional[str] = Field(None, description="Optional onboarding session ID")


class EdgeInfo(BaseModel):
    """Information about a created edge."""

    edge_id: str = Field(..., description="Unique edge identifier")
    source_id: str = Field(..., description="Source K-Block ID (user's axiom)")
    target_id: str = Field(..., description="Target K-Block ID (Zero Seed axiom)")
    target_title: str = Field(..., description="Title of the target axiom")
    edge_type: str = Field(..., description="Type of edge (derives_from)")
    context: str = Field(..., description="Context for this edge")


class FirstDeclarationResponse(BaseModel):
    """Response from creating first K-Block."""

    kblock_id: str = Field(..., description="ID of created K-Block")
    layer: int = Field(..., description="Assigned layer (likely L3 Goal)")
    loss: float = Field(..., description="Galois loss score (0.0 to 1.0)")
    justification: str = Field(..., description="Why this matters (auto-generated)")
    celebration: dict[str, Any] = Field(
        default_factory=dict, description="Celebratory data for frontend (confetti, etc.)"
    )
    edges: list[EdgeInfo] = Field(
        default_factory=list,
        description="Edges linking user's axiom to Zero Seed foundation",
    )


class OnboardingStatusResponse(BaseModel):
    """Current onboarding status."""

    completed: bool = Field(..., description="Whether FTUE is complete")
    session_id: Optional[str] = Field(None, description="Current session ID")
    first_kblock_id: Optional[str] = Field(None, description="ID of first K-Block if created")
    started_at: Optional[datetime] = Field(None, description="When onboarding started")
    completed_at: Optional[datetime] = Field(None, description="When onboarding completed")


# =============================================================================
# FTUE Axiom Models (F1, F2, F3, FG)
# =============================================================================


class FTUEAxiomStatus(BaseModel):
    """Status of a single FTUE axiom."""

    complete: bool = Field(default=False, description="Whether this axiom is complete")
    artifact_id: Optional[str] = Field(default=None, description="ID of the artifact (K-Block, edge, judgment, mark)")
    completed_at: Optional[datetime] = Field(default=None, description="When this axiom was completed")


class FTUEStatusResponse(BaseModel):
    """Complete FTUE axiom status for all four axioms."""

    session_id: Optional[str] = Field(None, description="Current session ID")
    all_complete: bool = Field(..., description="Whether all axioms are complete")

    # Individual axiom statuses
    f1_identity_seed: FTUEAxiomStatus = Field(..., description="F1: Identity Seed (first K-Block)")
    f2_connection_pattern: FTUEAxiomStatus = Field(..., description="F2: Connection Pattern (first edge)")
    f3_judgment_experience: FTUEAxiomStatus = Field(..., description="F3: Judgment Experience (first judgment)")
    fg_growth_witness: FTUEAxiomStatus = Field(..., description="FG: Growth Witness (witnessed emergence)")


class JudgmentRequest(BaseModel):
    """Request to record the user's first judgment (F3 axiom)."""

    proposal_id: str = Field(..., description="ID of the proposal being judged")
    proposal_type: str = Field(..., description="Type of proposal (insight, edge, refinement)")
    proposal_title: str = Field(..., description="Title of the proposal")
    proposal_description: str = Field(..., description="Description of the proposal")
    kblock_id: str = Field(..., description="ID of user's first K-Block")
    verdict: str = Field(
        ...,
        description="Judgment verdict: 'accept', 'revise', or 'reject'",
    )
    revision: Optional[str] = Field(
        None,
        description="If verdict is 'revise', the user's revision",
    )
    declaration: str = Field(..., description="User's original declaration")
    session_id: Optional[str] = Field(None, description="Onboarding session ID")


class JudgmentEmerged(BaseModel):
    """What emerged from the user's judgment."""

    kblock_id: Optional[str] = Field(None, description="ID of created K-Block (if any)")
    edge_id: Optional[str] = Field(None, description="ID of created edge (if any)")
    insight: Optional[str] = Field(None, description="Insight text (if any)")


class JudgmentResponse(BaseModel):
    """Response from recording the user's first judgment."""

    success: bool = Field(..., description="Whether the judgment was recorded successfully")
    verdict: str = Field(..., description="The verdict: accept, revise, or reject")
    emerged: JudgmentEmerged = Field(..., description="What emerged from the judgment")
    witness_mark_id: str = Field(..., description="ID of the witness mark for this judgment")
    message: str = Field(..., description="Human-readable description of what happened")
    # Keep for backwards compatibility
    judgment_id: Optional[str] = Field(None, description="ID of the created judgment")
    f3_complete: Optional[bool] = Field(None, description="Whether F3 axiom is now complete")


class WitnessEmergenceRequest(BaseModel):
    """Request to record the user witnessing emergence (FG axiom)."""

    session_id: Optional[str] = Field(None, description="Onboarding session ID")
    emerged_from: list[str] = Field(
        default_factory=list,
        description="IDs of artifacts that contributed to emergence (F1, F2, F3 artifacts)",
    )
    emergence_type: str = Field(
        ...,
        description="Type of emergence witnessed: 'derived_edge', 'generated_insight', 'pattern_discovered'",
    )
    description: Optional[str] = Field(
        None,
        description="User's description of what they witnessed",
    )


class WitnessEmergenceResponse(BaseModel):
    """Response from recording emergence witness (FG axiom)."""

    witness_id: str = Field(..., description="ID of the emergence witness mark")
    fg_complete: bool = Field(..., description="Whether FG axiom is now complete")
    ftue_complete: bool = Field(..., description="Whether entire FTUE is now complete")
    mark_id: str = Field(..., description="ID of the witness mark")


# =============================================================================
# FTUE Witness Mark Helper
# =============================================================================


async def create_ftue_witness_mark(
    action: str,
    axiom: str,
    artifact_id: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Create a witness mark for FTUE axiom completion.

    Args:
        action: The action type (identity_seed_planted, connection_seed_planted, etc.)
        axiom: The axiom identifier (F1, F2, F3, FG)
        artifact_id: ID of the artifact (K-Block, edge, judgment, mark)
        metadata: Additional metadata to include in the mark

    Returns:
        The mark ID

    See: spec/protocols/ftue-axioms.md (Relationship to Witness)
    """
    try:
        from services.witness import (
            Mark,
            Response,
            Stimulus,
            UmweltSnapshot,
            get_mark_store,
        )

        # Build metadata
        mark_metadata = {
            "axiom": axiom,
            "artifact_id": artifact_id,
            "ftue": True,
            **(metadata or {}),
        }

        # Create the mark
        mark = Mark(
            origin="ftue",
            domain="system",
            stimulus=Stimulus(
                kind="ftue_axiom",
                content=f"FTUE axiom {axiom} completed",
                source="onboarding",
                metadata={"axiom": axiom},
            ),
            response=Response(
                kind="axiom_planted",
                content=action,
                success=True,
                metadata=mark_metadata,
            ),
            umwelt=UmweltSnapshot.system(),
            tags=(axiom.lower(), "ftue", action),
            metadata=mark_metadata,
        )

        # Store the mark
        store = get_mark_store()
        store.append(mark)

        logger.info(f"Created FTUE witness mark: {mark.id} for axiom {axiom}")
        return str(mark.id)

    except Exception as e:
        logger.warning(f"Failed to create FTUE witness mark: {e}")
        # Return a placeholder ID if mark creation fails (non-critical)
        import uuid
        return f"mark-{uuid.uuid4().hex[:12]}"


# =============================================================================
# Layer Assignment Logic
# =============================================================================


def assign_layer_from_declaration(declaration: str) -> int:
    """
    Assign Galois layer based on declaration content.

    FTUE Special Rule: First declaration always goes to L1 (Axiom) because:
    - L1 Axioms are foundational and require NO lineage
    - User's first statement IS their foundational assumption
    - This makes the first K-Block a valid root in the derivation DAG

    Philosophical justification:
    "Your first declaration is axiomatic—it needs no proof, only witnessing."

    Args:
        declaration: User's first declaration

    Returns:
        Layer 1 (Axiom) - the foundational root for FTUE
    """
    # For FTUE, always assign to L1 (Axiom) as it's the only layer that
    # doesn't require lineage validation (foundational assumption)
    return 1


def compute_loss_from_declaration(declaration: str, layer: int) -> float:
    """
    Compute Galois loss for first declaration.

    For FTUE L1 Axioms, loss reflects clarity of the foundational assumption:
    - Very specific (>80 chars, concrete) → low loss (0.10-0.25)
    - Medium specificity (30-80 chars) → medium loss (0.30-0.45)
    - Vague or exploratory (<30 chars) → higher loss (0.50-0.65)

    Args:
        declaration: User's first declaration
        layer: Assigned layer (always 1 for FTUE)

    Returns:
        Loss score (0.0 to 1.0)
    """
    # Base loss for L1 Axioms - foundational assumptions can be clear or vague
    base = 0.35

    # Adjust based on specificity
    length = len(declaration)
    if length > 80:
        # Longer = more specific → lower loss
        return max(0.10, base - 0.18)
    elif length < 30:
        # Shorter = more vague → higher loss
        return min(0.65, base + 0.20)

    # Medium length = base loss
    return base


def generate_justification(declaration: str, layer: int) -> str:
    """
    Generate auto-justification for first K-Block.

    Args:
        declaration: User's first declaration
        layer: Assigned layer (always 1 for FTUE)

    Returns:
        Justification string
    """
    # For FTUE L1 Axioms, the justification is simple
    return "My first axiom — a foundational assumption that needs no proof, only witnessing"


def _get_loss_interpretation(loss: float) -> str:
    """
    Get friendly interpretation of Galois loss score.

    Args:
        loss: Loss score (0.0 to 1.0)

    Returns:
        Human-readable interpretation
    """
    if loss < 0.1:
        return "Very coherent — you know what you want!"
    elif loss < 0.3:
        return "Pretty clear, with room to grow."
    elif loss < 0.5:
        return "A bit hand-wavy, and that's okay!"
    else:
        return "Very exploratory — the system will help you refine this."


def _get_celebration_color(loss: float) -> str:
    """
    Get celebration color based on loss score.

    Args:
        loss: Loss score (0.0 to 1.0)

    Returns:
        Color name or hex code
    """
    if loss < 0.1:
        return "#c4a77d"  # Amber - perfect coherence
    elif loss < 0.3:
        return "#7a9d7a"  # Moss - good clarity
    elif loss < 0.5:
        return "#8a8a94"  # Steel - exploratory
    else:
        return "#7a85a0"  # Slate - very exploratory


def _get_celebration_intensity(loss: float) -> str:
    """
    Get celebration intensity based on loss score.

    Lower loss = more intense celebration (more coherent = better!)

    Args:
        loss: Loss score (0.0 to 1.0)

    Returns:
        Intensity level: "high", "medium", "low"
    """
    if loss < 0.2:
        return "high"
    elif loss < 0.5:
        return "medium"
    else:
        return "low"


# =============================================================================
# Router Creation
# =============================================================================


def create_onboarding_router() -> Optional["APIRouter"]:
    """
    Create onboarding API router.

    Endpoints:
    - POST /api/onboarding/start - Begin FTUE
    - POST /api/onboarding/first-declaration - Create first K-Block
    - GET /api/onboarding/status - Check completion status

    Returns:
        FastAPI router or None if FastAPI not available
    """
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, skipping onboarding router")
        return None

    router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

    @router.post("/start", response_model=OnboardingStartResponse)
    async def start_onboarding(
        request: OnboardingStartRequest,
    ) -> OnboardingStartResponse:
        """
        Start a new onboarding session.

        Creates a session ID to track the user through FTUE.
        Optional for now (can create first K-Block without session).
        """
        import uuid

        from models import OnboardingSession
        from models.base import get_async_session

        session_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        # Create persistent session
        session = OnboardingSession(
            id=session_id,
            user_id=request.user_id,
            current_step="started",
            completed=False,
        )

        async with get_async_session() as db:
            db.add(session)
            await db.commit()

        logger.info(f"Onboarding session started: {session_id}")

        return OnboardingStartResponse(
            session_id=session_id,
            started_at=started_at,
        )

    @router.post("/first-declaration", response_model=FirstDeclarationResponse)
    async def create_first_declaration(
        request: FirstDeclarationRequest,
    ) -> FirstDeclarationResponse:
        """
        Create the user's first K-Block from their declaration.

        This is the key moment in FTUE — transforming intent into structure.

        Flow:
        1. Assign layer based on declaration content
        2. Compute Galois loss
        3. Generate justification
        4. Create K-Block and persist to storage
        5. Update session status

        Args:
            request: User's first declaration

        Returns:
            K-Block details (ID, layer, loss, justification)

        Raises:
            HTTPException: If K-Block creation fails
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            # Assign layer
            layer = assign_layer_from_declaration(request.declaration)

            # Compute loss
            loss = compute_loss_from_declaration(request.declaration, layer)

            # Generate justification
            justification = generate_justification(request.declaration, layer)

            # Create title from declaration (first sentence or truncate)
            title = request.declaration.split(".")[0][:80]
            if len(request.declaration.split(".")[0]) > 80:
                title = title + "..."

            # Build K-Block content with loss and justification
            content = f"""# {title}

{request.declaration}

## Justification

{justification}

## Galois Loss

Loss: {loss:.2f}

**Interpretation**: {_get_loss_interpretation(loss)}
"""

            # Get storage and create K-Block
            storage = await get_postgres_zero_seed_storage()
            kblock, node_id = await storage.create_node(
                layer=layer,
                title=title,
                content=content,
                lineage=[],  # First declaration has no parents
                confidence=1.0 - loss,  # Confidence = 1 - loss
                tags=["ftue", "first-declaration", "user-generated"],
                created_by="user",
            )

            # =================================================================
            # F1: Identity Seed - Create witness mark for first K-Block
            # =================================================================
            f1_mark_id = await create_ftue_witness_mark(
                action="identity_seed_planted",
                axiom="F1",
                artifact_id=node_id,
                metadata={
                    "kblock_id": node_id,
                    "layer": layer,
                    "loss": loss,
                    "declaration_preview": request.declaration[:100],
                },
            )

            # Update session if provided (F1 complete)
            if request.session_id:
                from models import OnboardingSession
                from models.base import get_async_session

                async with get_async_session() as db:
                    session = await db.get(OnboardingSession, request.session_id)
                    if session:
                        session.first_kblock_id = node_id
                        session.first_declaration = request.declaration
                        session.f1_completed_at = datetime.utcnow()
                        session.current_step = "f1_complete"
                        # Don't mark as completed yet - need all 4 axioms
                        await db.commit()

            logger.info(
                f"F1 complete: First K-Block created: {node_id} (L{layer}, loss={loss:.2f})"
            )

            # =================================================================
            # F2: Connection Pattern - Create edges linking user's axiom to Zero Seed
            # =================================================================
            edges_created: list[EdgeInfo] = []
            first_edge_id: str | None = None

            try:
                from services.providers import get_sovereign_store

                store = await get_sovereign_store()

                # Get Zero Seed L1 axioms (A1, A2, G)
                zero_seed_axioms = await storage.get_layer_nodes(layer=1)

                for axiom in zero_seed_axioms:
                    axiom_id = str(axiom.id)
                    # Don't link to self
                    if axiom_id == node_id:
                        continue

                    # Create edge: user's axiom derives_from Zero Seed axiom
                    context = "User's first axiom builds on Zero Seed foundation"
                    edge_id = await store.add_edge(
                        from_path=node_id,
                        to_path=axiom_id,
                        edge_type="derives_from",
                        mark_id=None,  # Will update with F2 mark
                        context=context,
                    )

                    # Track first edge for F2 axiom
                    if first_edge_id is None:
                        first_edge_id = edge_id

                    # Extract title from axiom
                    axiom_title = getattr(axiom, "_title", None)
                    if not axiom_title:
                        # Try to extract from content (first line after #)
                        content_lines = axiom.content.split("\n")
                        for line in content_lines:
                            if line.startswith("# "):
                                axiom_title = line[2:].strip()
                                break
                        if not axiom_title:
                            axiom_title = f"L1 Axiom {axiom_id[:8]}"

                    edges_created.append(
                        EdgeInfo(
                            edge_id=edge_id,
                            source_id=node_id,
                            target_id=axiom_id,
                            target_title=axiom_title,
                            edge_type="derives_from",
                            context=context,
                        )
                    )

                    logger.info(
                        f"Created edge {edge_id}: {node_id[:8]}... -> {axiom_id[:8]}... ({axiom_title})"
                    )

                # If edges were created, complete F2 axiom
                if first_edge_id:
                    # Create F2 witness mark
                    f2_mark_id = await create_ftue_witness_mark(
                        action="connection_seed_planted",
                        axiom="F2",
                        artifact_id=first_edge_id,
                        metadata={
                            "edge_id": first_edge_id,
                            "source_kblock_id": node_id,
                            "total_edges": len(edges_created),
                        },
                    )

                    # Update session with F2 completion
                    if request.session_id:
                        from models import OnboardingSession
                        from models.base import get_async_session

                        async with get_async_session() as db:
                            session = await db.get(OnboardingSession, request.session_id)
                            if session:
                                session.f2_edge_id = first_edge_id
                                session.f2_completed_at = datetime.utcnow()
                                session.current_step = "f2_complete"
                                await db.commit()

                    logger.info(
                        f"F2 complete: Created {len(edges_created)} edges, first edge: {first_edge_id}"
                    )

            except ImportError:
                # Sovereign store not available (testing environment)
                logger.warning("Sovereign store not available, skipping edge creation (F2 not completed)")
            except Exception as e:
                # Non-critical - log but don't fail the declaration
                logger.warning(f"Failed to create Zero Seed edges (F2 not completed): {e}")

            # Generate celebration data
            celebration = {
                "confetti": True,
                "emoji": "✨",
                "message": "You've made your first declaration!",
                "color": _get_celebration_color(loss),
                "intensity": _get_celebration_intensity(loss),
            }

            return FirstDeclarationResponse(
                kblock_id=node_id,
                layer=layer,
                loss=loss,
                justification=justification,
                celebration=celebration,
                edges=edges_created,
            )

        except Exception as e:
            logger.error(f"Failed to create first declaration: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create K-Block: {str(e)}",
            )

    @router.get("/status", response_model=OnboardingStatusResponse)
    async def get_onboarding_status(
        session_id: Optional[str] = None,
    ) -> OnboardingStatusResponse:
        """
        Check onboarding completion status.

        Returns whether user has completed FTUE.
        If session_id provided, returns that session's status.
        Otherwise, returns global completion status (for single-user mode).

        Args:
            session_id: Optional session ID to check

        Returns:
            Onboarding status
        """
        from models import OnboardingSession
        from models.base import get_async_session
        from sqlalchemy import select

        async with get_async_session() as db:
            if session_id:
                # Get specific session
                session = await db.get(OnboardingSession, session_id)
                if session:
                    return OnboardingStatusResponse(
                        completed=session.completed,
                        session_id=session_id,
                        first_kblock_id=session.first_kblock_id,
                        started_at=session.created_at,
                        completed_at=session.completed_at,
                    )

            # Global status: completed if any session is completed
            result = await db.execute(
                select(OnboardingSession).where(OnboardingSession.completed == True)
            )
            any_session = result.scalar_one_or_none()

            return OnboardingStatusResponse(
                completed=any_session is not None,
                session_id=None,
                first_kblock_id=None,
                started_at=None,
                completed_at=None,
            )

    @router.post("/cleanup")
    async def cleanup_old_sessions(
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        Clean up abandoned sessions older than specified hours.

        This is called periodically to prevent database bloat.
        Default: Remove sessions older than 24 hours that aren't completed.

        Args:
            hours: Age threshold in hours (default: 24)

        Returns:
            Cleanup stats (count of deleted sessions)
        """
        from datetime import timedelta

        from models import OnboardingSession
        from models.base import get_async_session
        from sqlalchemy import delete

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        async with get_async_session() as db:
            # Delete old, incomplete sessions
            result = await db.execute(
                delete(OnboardingSession).where(
                    OnboardingSession.completed == False,
                    OnboardingSession.created_at < cutoff_time,
                )
            )
            await db.commit()

            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} abandoned onboarding sessions")

            return {
                "success": True,
                "deleted_count": deleted_count,
                "cutoff_hours": hours,
                "cutoff_time": cutoff_time.isoformat(),
            }

    @router.post("/complete")
    async def mark_onboarding_complete(
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Mark onboarding as complete.

        This is called when user finishes the FTUE journey and
        enters the main kgents studio.

        Args:
            session_id: Optional session ID to complete

        Returns:
            Completion confirmation with timestamp
        """
        import uuid

        from models import OnboardingSession
        from models.base import get_async_session

        completed_at = datetime.utcnow()

        async with get_async_session() as db:
            if session_id:
                # Update existing session
                session = await db.get(OnboardingSession, session_id)
                if session:
                    session.completed = True
                    session.completed_at = completed_at
                    session.current_step = "completed"
                    await db.commit()
                    logger.info(f"Onboarding session {session_id} marked complete")
            else:
                # Create a default session for completion tracking
                new_session_id = str(uuid.uuid4())
                session = OnboardingSession(
                    id=new_session_id,
                    user_id=None,
                    current_step="completed",
                    completed=True,
                    completed_at=completed_at,
                )
                db.add(session)
                await db.commit()
                logger.info(f"Onboarding marked complete (new session: {new_session_id})")

        return {
            "success": True,
            "completed_at": completed_at.isoformat(),
            "message": "Welcome to kgents! Your journey begins.",
        }

    # =========================================================================
    # F3: Judgment Experience Endpoint
    # =========================================================================

    @router.post("/judgment", response_model=JudgmentResponse)
    async def record_first_judgment(
        request: JudgmentRequest,
    ) -> JudgmentResponse:
        """
        Record the user's first judgment (F3 axiom).

        This completes F3: Judgment Experience - establishing that
        "I can shape this system" through accept/revise/reject.

        From spec/protocols/ftue-axioms.md:
        "A meaningful accept/revise/reject decision on a generated proposal.
         The system proposes; the user disposes."

        Args:
            request: Judgment request with verdict and optional revision

        Returns:
            JudgmentResponse with judgment ID and completion status

        Raises:
            HTTPException: If judgment creation fails
        """
        import uuid

        try:
            # Validate verdict
            valid_verdicts = {"accept", "revise", "reject"}
            if request.verdict.lower() not in valid_verdicts:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid verdict: {request.verdict}. Must be one of: {valid_verdicts}",
                )

            # Generate judgment ID
            judgment_id = f"judgment-{uuid.uuid4().hex[:12]}"

            # Create F3 witness mark
            mark_id = await create_ftue_witness_mark(
                action="judgment_seed_planted",
                axiom="F3",
                artifact_id=judgment_id,
                metadata={
                    "judgment_id": judgment_id,
                    "proposal_id": request.proposal_id,
                    "proposal_type": request.proposal_type,
                    "proposal_title": request.proposal_title,
                    "kblock_id": request.kblock_id,
                    "verdict": request.verdict.lower(),
                    "has_revision": request.revision is not None,
                },
            )

            f3_complete = True

            # Build emergence info based on verdict
            emerged = JudgmentEmerged(
                kblock_id=request.kblock_id if request.verdict.lower() != "reject" else None,
                edge_id=None,  # Could be set if edge was created
                insight=request.revision if request.verdict.lower() == "revise" else None,
            )

            # Build human-readable message
            verdict_lower = request.verdict.lower()
            if verdict_lower == "accept":
                message = f"You accepted the proposal '{request.proposal_title}'. Your judgment shapes the system."
            elif verdict_lower == "revise":
                message = f"You revised the proposal '{request.proposal_title}'. Your voice is heard."
            else:
                message = f"You rejected the proposal '{request.proposal_title}'. That's a valid judgment too."

            # Update session if provided
            if request.session_id:
                from models import OnboardingSession
                from models.base import get_async_session

                async with get_async_session() as db:
                    session = await db.get(OnboardingSession, request.session_id)
                    if session:
                        session.f3_judgment_id = judgment_id
                        session.f3_completed_at = datetime.utcnow()
                        session.current_step = "f3_complete"
                        await db.commit()

            logger.info(
                f"F3 complete: Judgment {judgment_id} recorded with verdict '{request.verdict}'"
            )

            return JudgmentResponse(
                success=True,
                verdict=verdict_lower,
                emerged=emerged,
                witness_mark_id=mark_id,
                message=message,
                judgment_id=judgment_id,
                f3_complete=f3_complete,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to record judgment: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to record judgment: {str(e)}",
            )

    # =========================================================================
    # FG: Growth Witness Endpoint
    # =========================================================================

    @router.post("/witness-emergence", response_model=WitnessEmergenceResponse)
    async def record_emergence_witness(
        request: WitnessEmergenceRequest,
    ) -> WitnessEmergenceResponse:
        """
        Record the user witnessing emergence (FG axiom).

        This completes FG: Growth Witness - establishing that the user
        has witnessed something grow from their seeds.

        From spec/protocols/ftue-axioms.md:
        "After F1-F3, show something that emerged. Could be a derived edge,
         a generated insight, or a pattern the system noticed."

        Args:
            request: Emergence witness request

        Returns:
            WitnessEmergenceResponse with witness ID and completion status

        Raises:
            HTTPException: If witness recording fails
        """
        import uuid

        try:
            # Validate emergence type
            valid_types = {"derived_edge", "generated_insight", "pattern_discovered"}
            if request.emergence_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid emergence_type: {request.emergence_type}. Must be one of: {valid_types}",
                )

            # Generate witness ID
            witness_id = f"witness-{uuid.uuid4().hex[:12]}"

            # Create FG witness mark
            mark_id = await create_ftue_witness_mark(
                action="growth_witnessed",
                axiom="FG",
                artifact_id=witness_id,
                metadata={
                    "witness_id": witness_id,
                    "emerged_from": request.emerged_from,
                    "emergence_type": request.emergence_type,
                    "description": request.description,
                },
            )

            fg_complete = True
            ftue_complete = False

            # Update session if provided
            if request.session_id:
                from models import OnboardingSession
                from models.base import get_async_session

                async with get_async_session() as db:
                    session = await db.get(OnboardingSession, request.session_id)
                    if session:
                        session.fg_witness_id = witness_id
                        session.fg_completed_at = datetime.utcnow()

                        # Check if all axioms are complete
                        if session.all_axioms_complete:
                            session.current_step = "completed"
                            session.completed = True
                            session.completed_at = datetime.utcnow()
                            ftue_complete = True
                        else:
                            session.current_step = "fg_complete"

                        await db.commit()

            logger.info(
                f"FG complete: Emergence witnessed ({request.emergence_type}), "
                f"witness_id={witness_id}, ftue_complete={ftue_complete}"
            )

            return WitnessEmergenceResponse(
                witness_id=witness_id,
                fg_complete=fg_complete,
                ftue_complete=ftue_complete,
                mark_id=mark_id,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to record emergence witness: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to record emergence witness: {str(e)}",
            )

    # =========================================================================
    # FTUE Status Endpoint
    # =========================================================================

    @router.get("/ftue-status", response_model=FTUEStatusResponse)
    async def get_ftue_status(
        session_id: Optional[str] = None,
    ) -> FTUEStatusResponse:
        """
        Get detailed FTUE axiom status.

        Returns the completion status of all four FTUE axioms:
        - F1: Identity Seed (first K-Block)
        - F2: Connection Pattern (first edge)
        - F3: Judgment Experience (first judgment)
        - FG: Growth Witness (witnessed emergence)

        Args:
            session_id: Optional session ID to check

        Returns:
            FTUEStatusResponse with status of all axioms
        """
        from models import OnboardingSession
        from models.base import get_async_session
        from sqlalchemy import select

        async with get_async_session() as db:
            session: OnboardingSession | None = None

            if session_id:
                session = await db.get(OnboardingSession, session_id)
            else:
                # Get most recent session
                result = await db.execute(
                    select(OnboardingSession).order_by(
                        OnboardingSession.created_at.desc()
                    ).limit(1)
                )
                session = result.scalar_one_or_none()

            if session:
                return FTUEStatusResponse(
                    session_id=session.id,
                    all_complete=session.all_axioms_complete,
                    f1_identity_seed=FTUEAxiomStatus(
                        complete=session.f1_complete,
                        artifact_id=session.first_kblock_id,
                        completed_at=session.f1_completed_at,
                    ),
                    f2_connection_pattern=FTUEAxiomStatus(
                        complete=session.f2_complete,
                        artifact_id=session.f2_edge_id,
                        completed_at=session.f2_completed_at,
                    ),
                    f3_judgment_experience=FTUEAxiomStatus(
                        complete=session.f3_complete,
                        artifact_id=session.f3_judgment_id,
                        completed_at=session.f3_completed_at,
                    ),
                    fg_growth_witness=FTUEAxiomStatus(
                        complete=session.fg_complete,
                        artifact_id=session.fg_witness_id,
                        completed_at=session.fg_completed_at,
                    ),
                )

            # No session found - return empty status
            return FTUEStatusResponse(
                session_id=None,
                all_complete=False,
                f1_identity_seed=FTUEAxiomStatus(complete=False),
                f2_connection_pattern=FTUEAxiomStatus(complete=False),
                f3_judgment_experience=FTUEAxiomStatus(complete=False),
                fg_growth_witness=FTUEAxiomStatus(complete=False),
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Router factory
    "create_onboarding_router",
    # Start endpoint
    "OnboardingStartRequest",
    "OnboardingStartResponse",
    # First declaration endpoint (F1 + F2)
    "FirstDeclarationRequest",
    "FirstDeclarationResponse",
    "EdgeInfo",
    # Status endpoint
    "OnboardingStatusResponse",
    # FTUE axiom models
    "FTUEAxiomStatus",
    "FTUEStatusResponse",
    # F3: Judgment endpoint
    "JudgmentRequest",
    "JudgmentResponse",
    "JudgmentEmerged",
    # FG: Emergence witness endpoint
    "WitnessEmergenceRequest",
    "WitnessEmergenceResponse",
    # Helper function
    "create_ftue_witness_mark",
]
