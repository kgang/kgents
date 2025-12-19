"""
Commission Service: The heart of the Metaphysical Forge.

A Commission is Kent's intent to build an agent. The Commission flows through
seven artisans (K-gent, Architect, Smith, Herald, Projector, Sentinel, Witness),
each contributing their specialized expertise.

This is the transformation from "spectator fishbowl" to "developer's forge":
- Atelier (Old):  Spectators → watch → Builders → create → Artifacts
- Forge (New):    Kent → commissions → Artisans → build → Agents

Commission States (PolyAgent):
- PENDING: Initial intent captured, awaiting K-gent review
- DESIGNING: Architect creating categorical design
- IMPLEMENTING: Smith generating service code
- EXPOSING: Herald creating AGENTESE nodes
- PROJECTING: Projector creating UI surfaces
- SECURING: Sentinel reviewing for vulnerabilities
- VERIFYING: Witness generating and running tests
- REVIEWING: K-gent final approval
- COMPLETE: All artisans approved
- REJECTED: K-gent rejected at some stage
- FAILED: Technical failure during processing

"The Forge is where Kent builds with Kent."

See: spec/protocols/metaphysical-forge.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.k.soul import KgentSoul


class CommissionStatus(str, Enum):
    """Commission lifecycle states."""

    PENDING = "pending"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    EXPOSING = "exposing"
    PROJECTING = "projecting"
    SECURING = "securing"
    VERIFYING = "verifying"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    REJECTED = "rejected"
    FAILED = "failed"


class ArtisanType(str, Enum):
    """The seven artisans of the Forge."""

    KGENT = "kgent"  # Soul/Governance
    ARCHITECT = "architect"  # Categorical design
    SMITH = "smith"  # Implementation
    HERALD = "herald"  # Protocol/AGENTESE
    PROJECTOR = "projector"  # Surfaces
    SENTINEL = "sentinel"  # Security
    WITNESS = "witness"  # Testing


@dataclass
class ArtisanOutput:
    """Output from an artisan's work on a commission."""

    artisan: ArtisanType
    status: str  # "pending", "working", "complete", "failed", "skipped"
    output: dict[str, Any] | None = None
    annotation: str | None = None  # K-gent's note on this work
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


@dataclass
class Commission:
    """
    A commission to build an agent.

    Kent describes what he wants (intent), and the Forge's seven artisans
    work together to produce a complete metaphysical fullstack agent.
    """

    id: str
    intent: str  # What Kent wants to build
    name: str | None = None  # Optional name for the target agent
    status: CommissionStatus = CommissionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # K-gent governance
    soul_approved: bool = False
    soul_annotation: str | None = None
    soul_eigenvector_context: dict[str, float] | None = None

    # Artisan outputs (accumulated as work progresses)
    artisan_outputs: dict[str, ArtisanOutput] = field(default_factory=dict)

    # Final artifact (when complete)
    artifact_path: str | None = None  # e.g., "services/preferences/"
    artifact_summary: str | None = None

    # Intervention tracking
    interventions: list[dict[str, Any]] = field(default_factory=list)
    paused: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "intent": self.intent,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "soul_approved": self.soul_approved,
            "soul_annotation": self.soul_annotation,
            "soul_eigenvector_context": self.soul_eigenvector_context,
            "artisan_outputs": {
                k: {
                    "artisan": v.artisan.value,
                    "status": v.status,
                    "output": v.output,
                    "annotation": v.annotation,
                    "started_at": v.started_at.isoformat() if v.started_at else None,
                    "completed_at": v.completed_at.isoformat() if v.completed_at else None,
                    "error": v.error,
                }
                for k, v in self.artisan_outputs.items()
            },
            "artifact_path": self.artifact_path,
            "artifact_summary": self.artifact_summary,
            "interventions": self.interventions,
            "paused": self.paused,
        }


# === Commission Transitions ===

# Valid transitions in the commission state machine
COMMISSION_TRANSITIONS: dict[CommissionStatus, list[CommissionStatus]] = {
    CommissionStatus.PENDING: [
        CommissionStatus.DESIGNING,  # K-gent approved
        CommissionStatus.REJECTED,  # K-gent rejected
    ],
    CommissionStatus.DESIGNING: [
        CommissionStatus.IMPLEMENTING,  # Design complete
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.IMPLEMENTING: [
        CommissionStatus.EXPOSING,  # Service complete
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.EXPOSING: [
        CommissionStatus.PROJECTING,  # Node complete
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.PROJECTING: [
        CommissionStatus.SECURING,  # Surfaces complete
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.SECURING: [
        CommissionStatus.VERIFYING,  # Security passed
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.VERIFYING: [
        CommissionStatus.REVIEWING,  # Tests passed
        CommissionStatus.FAILED,
        CommissionStatus.REJECTED,
    ],
    CommissionStatus.REVIEWING: [
        CommissionStatus.COMPLETE,  # K-gent final approval
        CommissionStatus.REJECTED,  # K-gent final rejection
    ],
    CommissionStatus.COMPLETE: [],  # Terminal
    CommissionStatus.REJECTED: [],  # Terminal
    CommissionStatus.FAILED: [],  # Terminal
}


class CommissionService:
    """
    Commission orchestration service.

    Manages the flow of commissions through the seven artisans:
    1. K-gent (initial review) → PENDING → DESIGNING
    2. Architect (design) → DESIGNING → IMPLEMENTING
    3. Smith (implement) → IMPLEMENTING → EXPOSING
    4. Herald (expose) → EXPOSING → PROJECTING
    5. Projector (project) → PROJECTING → SECURING
    6. Sentinel (secure) → SECURING → VERIFYING
    7. Witness (verify) → VERIFYING → REVIEWING
    8. K-gent (final approval) → REVIEWING → COMPLETE

    DI Requirements:
    - kgent_soul: KgentSoul (optional, for governance)
    """

    def __init__(self, kgent_soul: "KgentSoul | None" = None) -> None:
        """
        Initialize CommissionService.

        Args:
            kgent_soul: Optional KgentSoul for governance. If None, governance is skipped.
        """
        self.soul = kgent_soul
        self._commissions: dict[str, Commission] = {}

        # Initialize artisans (Phase 4)
        from .artisans import (
            ArchitectArtisan,
            HeraldArtisan,
            ProjectorArtisan,
            SmithArtisan,
        )

        self._architect = ArchitectArtisan(soul=kgent_soul)
        self._smith = SmithArtisan(soul=kgent_soul)
        self._herald = HeraldArtisan(soul=kgent_soul)
        self._projector = ProjectorArtisan(soul=kgent_soul)

    async def create(
        self,
        intent: str,
        name: str | None = None,
    ) -> Commission:
        """
        Create a new commission.

        AGENTESE: world.forge.commission.create

        Args:
            intent: What Kent wants to build (natural language description)
            name: Optional name for the target agent

        Returns:
            The created Commission in PENDING status
        """
        commission_id = f"commission-{uuid.uuid4().hex[:12]}"

        commission = Commission(
            id=commission_id,
            intent=intent,
            name=name,
            status=CommissionStatus.PENDING,
        )

        self._commissions[commission_id] = commission
        return commission

    async def get(self, commission_id: str) -> Commission | None:
        """Get a commission by ID."""
        return self._commissions.get(commission_id)

    async def list(
        self,
        status: CommissionStatus | None = None,
        limit: int = 20,
    ) -> list[Commission]:
        """
        List commissions with optional status filter.

        AGENTESE: world.forge.commission.list
        """
        commissions = list(self._commissions.values())

        if status is not None:
            commissions = [c for c in commissions if c.status == status]

        # Sort by created_at descending
        commissions.sort(key=lambda c: c.created_at, reverse=True)

        return commissions[:limit]

    async def start_review(self, commission_id: str) -> Commission | None:
        """
        Start K-gent initial review.

        AGENTESE: world.forge.commission.start

        Transitions: PENDING → DESIGNING (if approved) or REJECTED
        """
        commission = self._commissions.get(commission_id)
        if commission is None:
            return None

        if commission.status != CommissionStatus.PENDING:
            return None  # Can only start from PENDING

        # Mark K-gent artisan as working
        commission.artisan_outputs[ArtisanType.KGENT.value] = ArtisanOutput(
            artisan=ArtisanType.KGENT,
            status="working",
            started_at=datetime.now(timezone.utc),
        )

        # K-gent review
        if self.soul is not None:
            try:
                intercept_result = await self.soul.intercept(
                    f"Commission review: {commission.intent}"
                )

                commission.soul_annotation = intercept_result.annotation
                commission.soul_eigenvector_context = self.soul.eigenvectors.to_dict()

                if intercept_result.recommendation == "escalate":
                    # K-gent rejected
                    commission.status = CommissionStatus.REJECTED
                    commission.soul_approved = False
                    commission.artisan_outputs[ArtisanType.KGENT.value].status = "complete"
                    commission.artisan_outputs[ArtisanType.KGENT.value].completed_at = datetime.now(
                        timezone.utc
                    )
                    commission.artisan_outputs[ArtisanType.KGENT.value].output = {
                        "approved": False,
                        "reason": intercept_result.annotation,
                    }
                else:
                    # K-gent approved - proceed to designing
                    commission.status = CommissionStatus.DESIGNING
                    commission.soul_approved = True
                    commission.artisan_outputs[ArtisanType.KGENT.value].status = "complete"
                    commission.artisan_outputs[ArtisanType.KGENT.value].completed_at = datetime.now(
                        timezone.utc
                    )
                    commission.artisan_outputs[ArtisanType.KGENT.value].output = {
                        "approved": True,
                        "annotation": intercept_result.annotation,
                    }

            except Exception as e:
                # K-gent failure - proceed anyway (graceful degradation)
                commission.status = CommissionStatus.DESIGNING
                commission.soul_approved = True
                commission.soul_annotation = f"K-gent review skipped: {e}"
                commission.artisan_outputs[ArtisanType.KGENT.value].status = "skipped"
                commission.artisan_outputs[ArtisanType.KGENT.value].error = str(e)
        else:
            # No K-gent - auto-approve
            commission.status = CommissionStatus.DESIGNING
            commission.soul_approved = True
            commission.soul_annotation = "K-gent not configured - auto-approved"
            commission.artisan_outputs[ArtisanType.KGENT.value].status = "skipped"

        commission.updated_at = datetime.now(timezone.utc)
        return commission

    async def advance(self, commission_id: str) -> Commission | None:
        """
        Advance commission to the next stage.

        This now uses REAL artisans (Architect, Smith) for actual work.
        Herald, Projector, Sentinel, and Witness are still placeholders (Phase 4-5).

        Returns the updated commission, or None if not found/invalid transition.
        """
        commission = self._commissions.get(commission_id)
        if commission is None:
            return None

        if commission.paused:
            return None  # Can't advance while paused

        current_status = commission.status
        valid_transitions = COMMISSION_TRANSITIONS.get(current_status, [])

        if not valid_transitions:
            return None  # Terminal state

        # Status → (artisan type, next status)
        artisan_map: dict[CommissionStatus, tuple[ArtisanType, CommissionStatus]] = {
            CommissionStatus.DESIGNING: (
                ArtisanType.ARCHITECT,
                CommissionStatus.IMPLEMENTING,
            ),
            CommissionStatus.IMPLEMENTING: (
                ArtisanType.SMITH,
                CommissionStatus.EXPOSING,
            ),
            CommissionStatus.EXPOSING: (
                ArtisanType.HERALD,
                CommissionStatus.PROJECTING,
            ),
            CommissionStatus.PROJECTING: (
                ArtisanType.PROJECTOR,
                CommissionStatus.SECURING,
            ),
            CommissionStatus.SECURING: (
                ArtisanType.SENTINEL,
                CommissionStatus.VERIFYING,
            ),
            CommissionStatus.VERIFYING: (
                ArtisanType.WITNESS,
                CommissionStatus.REVIEWING,
            ),
            CommissionStatus.REVIEWING: (
                ArtisanType.KGENT,
                CommissionStatus.COMPLETE,
            ),
        }

        if current_status not in artisan_map:
            return None

        artisan_type, next_status = artisan_map[current_status]

        # Execute the appropriate artisan
        if current_status == CommissionStatus.DESIGNING:
            # REAL WORK: Architect generates categorical design
            output = await self._architect.design(commission)
            commission.artisan_outputs[artisan_type.value] = output

            if output.status == "failed":
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

        elif current_status == CommissionStatus.IMPLEMENTING:
            # REAL WORK: Smith generates code from architect's design
            architect_output = commission.artisan_outputs.get(ArtisanType.ARCHITECT.value)
            if architect_output is None or architect_output.output is None:
                # Can't implement without design
                commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                    artisan=artisan_type,
                    status="failed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error="No architect design to implement",
                )
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            output = await self._smith.implement(commission, architect_output.output)
            commission.artisan_outputs[artisan_type.value] = output

            if output.status == "failed":
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            # Set artifact path from Smith output
            if output.output and "path" in output.output:
                commission.artifact_path = output.output["path"]

        elif current_status == CommissionStatus.EXPOSING:
            # REAL WORK: Herald generates AGENTESE node
            architect_output = commission.artisan_outputs.get(ArtisanType.ARCHITECT.value)
            smith_output = commission.artisan_outputs.get(ArtisanType.SMITH.value)

            if architect_output is None or architect_output.output is None:
                commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                    artisan=artisan_type,
                    status="failed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error="No architect design to expose",
                )
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            if smith_output is None or smith_output.output is None:
                commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                    artisan=artisan_type,
                    status="failed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error="No smith output to expose",
                )
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            output = await self._herald.expose(
                commission,
                architect_output.output,
                smith_output.output,
            )
            commission.artisan_outputs[artisan_type.value] = output

            if output.status == "failed":
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

        elif current_status == CommissionStatus.PROJECTING:
            # REAL WORK: Projector generates React components
            architect_output = commission.artisan_outputs.get(ArtisanType.ARCHITECT.value)
            smith_output = commission.artisan_outputs.get(ArtisanType.SMITH.value)
            herald_output = commission.artisan_outputs.get(ArtisanType.HERALD.value)

            if architect_output is None or architect_output.output is None:
                commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                    artisan=artisan_type,
                    status="failed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error="No architect design to project",
                )
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            if herald_output is None or herald_output.output is None:
                commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                    artisan=artisan_type,
                    status="failed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    error="No herald output to project",
                )
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

            output = await self._projector.project(
                commission,
                architect_output.output,
                smith_output.output if smith_output else {},
                herald_output.output,
            )
            commission.artisan_outputs[artisan_type.value] = output

            if output.status == "failed":
                commission.status = CommissionStatus.FAILED
                commission.updated_at = datetime.now(timezone.utc)
                return commission

        else:
            # Placeholder for Sentinel, Witness (Phase 5)
            commission.artisan_outputs[artisan_type.value] = ArtisanOutput(
                artisan=artisan_type,
                status="complete",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                output={
                    "placeholder": True,
                    "artisan": artisan_type.value,
                    "stage": current_status.value,
                    "note": f"{artisan_type.value} artisan not yet implemented (Phase 5)",
                },
                annotation=f"{artisan_type.value} auto-approved (placeholder)",
            )

        # Advance to next status
        commission.status = next_status
        commission.updated_at = datetime.now(timezone.utc)

        return commission

    async def pause(self, commission_id: str) -> Commission | None:
        """
        Pause a commission.

        AGENTESE: world.forge.commission.pause
        """
        commission = self._commissions.get(commission_id)
        if commission is None:
            return None

        commission.paused = True
        commission.interventions.append(
            {
                "type": "pause",
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        commission.updated_at = datetime.now(timezone.utc)

        return commission

    async def resume(self, commission_id: str) -> Commission | None:
        """
        Resume a paused commission.

        AGENTESE: world.forge.commission.resume
        """
        commission = self._commissions.get(commission_id)
        if commission is None:
            return None

        commission.paused = False
        commission.interventions.append(
            {
                "type": "resume",
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        commission.updated_at = datetime.now(timezone.utc)

        return commission

    async def cancel(self, commission_id: str, reason: str | None = None) -> bool:
        """
        Cancel a commission.

        AGENTESE: world.forge.commission.cancel
        """
        commission = self._commissions.get(commission_id)
        if commission is None:
            return False

        # Can only cancel non-terminal states
        if commission.status in (
            CommissionStatus.COMPLETE,
            CommissionStatus.REJECTED,
            CommissionStatus.FAILED,
        ):
            return False

        commission.status = CommissionStatus.REJECTED
        commission.interventions.append(
            {
                "type": "cancel",
                "reason": reason,
                "at": datetime.now(timezone.utc).isoformat(),
            }
        )
        commission.updated_at = datetime.now(timezone.utc)

        return True


__all__ = [
    "Commission",
    "CommissionService",
    "CommissionStatus",
    "ArtisanType",
    "ArtisanOutput",
    "COMMISSION_TRANSITIONS",
]
