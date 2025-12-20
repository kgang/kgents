"""
ConfirmationManager: Level 2 Suggestion Confirmation Flow.

At Level 2 (SUGGESTION), the Witness can propose actions but requires
human confirmation before execution.

Flow:
    1. Witness proposes action → PendingSuggestion created
    2. User notified (CLI, Web, notification)
    3. User reviews and confirms/rejects
    4. Suggestion marked accepted/rejected
    5. Metrics updated for trust escalation

Suggestions expire after 1 hour if not acted upon.

See: plans/kgentsd-trust-system.md
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Suggestion Status
# =============================================================================


class SuggestionStatus(Enum):
    """Status of a pending suggestion."""

    PENDING = auto()  # Awaiting confirmation
    CONFIRMED = auto()  # User approved
    REJECTED = auto()  # User rejected
    EXPIRED = auto()  # Timed out
    EXECUTED = auto()  # Successfully executed after confirmation


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ActionPreview:
    """Preview of what an action will do."""

    description: str
    affected_files: list[str] = field(default_factory=list)
    reversible: bool = True
    estimated_duration_seconds: float = 0.0
    risk_level: str = "low"  # low, medium, high


@dataclass
class PendingSuggestion:
    """A suggestion awaiting human confirmation."""

    id: str
    action: str
    target: str | None
    rationale: str
    preview: ActionPreview
    confidence: float  # 0.0 to 1.0

    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    status: SuggestionStatus = SuggestionStatus.PENDING

    # User response
    confirmed_at: datetime | None = None
    confirmed_by: str | None = None
    rejection_reason: str | None = None

    # Phase 4C: Pipeline execution support
    # The pipeline to execute on confirmation (optional - set by daemon)
    pipeline: Any = None  # Pipeline from services.witness.pipeline
    initial_kwargs: dict[str, Any] = field(default_factory=dict)  # Initial args for pipeline

    @property
    def is_expired(self) -> bool:
        """Check if suggestion has expired."""
        return datetime.now() > self.expires_at and self.status == SuggestionStatus.PENDING

    @property
    def time_remaining(self) -> timedelta:
        """Time remaining before expiration."""
        return max(self.expires_at - datetime.now(), timedelta(0))

    def to_display(self) -> dict[str, Any]:
        """Format for human review."""
        return {
            "id": self.id,
            "action": self.action,
            "target": self.target,
            "rationale": self.rationale,
            "confidence": f"{self.confidence:.0%}",
            "preview": {
                "description": self.preview.description,
                "affected_files": self.preview.affected_files,
                "reversible": self.preview.reversible,
                "risk_level": self.preview.risk_level,
            },
            "expires_in": str(self.time_remaining).split(".")[0],
            "status": self.status.name,
        }


@dataclass
class ConfirmationResult:
    """Result of a confirmation action."""

    suggestion_id: str
    accepted: bool
    executed: bool = False
    execution_result: str | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    # Phase 4C: Pipeline execution details
    pipeline_result: Any = None  # PipelineResult from services.witness.pipeline
    duration_ms: float = 0.0


# =============================================================================
# ConfirmationManager
# =============================================================================


class ConfirmationManager:
    """
    Manages pending suggestions awaiting confirmation.

    Handles the L2 confirmation flow:
    - Submit suggestions
    - Notify users
    - Handle confirmations/rejections
    - Execute approved actions
    - Track metrics for escalation

    Example:
        manager = ConfirmationManager()

        # Submit a suggestion
        suggestion = await manager.submit(
            action="git commit -m 'fix: typo'",
            rationale="Detected uncommitted typo fix",
            confidence=0.85,
        )

        # User confirms
        result = await manager.confirm(suggestion.id)
        assert result.accepted
        assert result.executed
    """

    def __init__(
        self,
        notification_handler: Callable[[PendingSuggestion], Coroutine[Any, Any, None]]
        | None = None,
        execution_handler: Callable[[str], Coroutine[Any, Any, tuple[bool, str]]] | None = None,
        pipeline_runner: Any | None = None,  # PipelineRunner for workflow execution
        expiration_hours: float = 1.0,
    ) -> None:
        """
        Initialize confirmation manager.

        Args:
            notification_handler: Async function to notify user of new suggestion
            execution_handler: Async function to execute confirmed action (fallback)
            pipeline_runner: PipelineRunner for executing workflow pipelines (Phase 4C)
            expiration_hours: Hours before suggestions expire (default 1)
        """
        self._pending: dict[str, PendingSuggestion] = {}
        self._notification_handler = notification_handler
        self._execution_handler = execution_handler
        self._pipeline_runner = pipeline_runner
        self._expiration_hours = expiration_hours

        # Metrics
        self.total_submitted = 0
        self.total_confirmed = 0
        self.total_rejected = 0
        self.total_expired = 0
        self.total_executed = 0

    def set_pipeline_runner(self, runner: Any) -> None:
        """Set the pipeline runner for workflow execution."""
        self._pipeline_runner = runner

    async def submit(
        self,
        action: str,
        rationale: str,
        confidence: float = 0.5,
        target: str | None = None,
        preview: ActionPreview | None = None,
        pipeline: Any | None = None,
        initial_kwargs: dict[str, Any] | None = None,
    ) -> PendingSuggestion:
        """
        Submit a suggestion for confirmation.

        Args:
            action: The action to perform (workflow name or command)
            rationale: Why this action is suggested
            confidence: Confidence level (0-1)
            target: Optional target for the action
            preview: Optional preview of action effects
            pipeline: Optional Pipeline to execute on confirmation (Phase 4C)
            initial_kwargs: Optional initial arguments for pipeline execution

        Returns:
            PendingSuggestion awaiting confirmation
        """
        suggestion_id = f"sug-{uuid.uuid4().hex[:8]}"

        suggestion = PendingSuggestion(
            id=suggestion_id,
            action=action,
            target=target,
            rationale=rationale,
            preview=preview or ActionPreview(description=f"Execute: {action}"),
            confidence=confidence,
            expires_at=datetime.now() + timedelta(hours=self._expiration_hours),
            pipeline=pipeline,
            initial_kwargs=initial_kwargs or {},
        )

        self._pending[suggestion_id] = suggestion
        self.total_submitted += 1

        # Notify user (fire and forget)
        if self._notification_handler:
            try:
                await self._notification_handler(suggestion)
            except Exception as e:
                logger.error(f"Failed to notify user of suggestion {suggestion_id}: {e}")

        logger.info(f"Suggestion submitted: {suggestion_id} - {action[:50]}")
        return suggestion

    async def confirm(
        self,
        suggestion_id: str,
        confirmed_by: str = "user",
    ) -> ConfirmationResult:
        """
        Confirm a pending suggestion.

        Args:
            suggestion_id: ID of the suggestion to confirm
            confirmed_by: Who confirmed (for audit)

        Returns:
            ConfirmationResult with execution details
        """
        suggestion = self._pending.get(suggestion_id)
        if suggestion is None:
            return ConfirmationResult(
                suggestion_id=suggestion_id,
                accepted=False,
                error="Suggestion not found",
            )

        if suggestion.is_expired:
            suggestion.status = SuggestionStatus.EXPIRED
            self.total_expired += 1
            return ConfirmationResult(
                suggestion_id=suggestion_id,
                accepted=False,
                error="Suggestion has expired",
            )

        # Mark as confirmed
        suggestion.status = SuggestionStatus.CONFIRMED
        suggestion.confirmed_at = datetime.now()
        suggestion.confirmed_by = confirmed_by
        self.total_confirmed += 1

        # Execute pipeline or fallback to execution_handler
        executed = False
        execution_result = None
        error = None
        pipeline_result = None
        duration_ms = 0.0
        start_time = datetime.now()

        # Phase 4C: Execute pipeline if available
        if suggestion.pipeline is not None and self._pipeline_runner is not None:
            try:
                pipeline_result = await self._pipeline_runner.run(
                    suggestion.pipeline,
                    initial_kwargs=suggestion.initial_kwargs,
                )
                executed = pipeline_result.success
                execution_result = (
                    f"Pipeline completed: {len(pipeline_result.step_results)} steps"
                    if pipeline_result.success
                    else f"Pipeline failed at step {pipeline_result.aborted_at_step}"
                )
                duration_ms = pipeline_result.total_duration_ms
                if executed:
                    suggestion.status = SuggestionStatus.EXECUTED
                    self.total_executed += 1
                else:
                    error = pipeline_result.error
                logger.info(
                    f"Pipeline executed for {suggestion_id}: "
                    f"success={executed}, steps={len(pipeline_result.step_results)}"
                )
            except Exception as e:
                error = str(e)
                logger.error(f"Failed to execute pipeline for {suggestion_id}: {e}")

        # Fallback to execution_handler if no pipeline
        elif self._execution_handler:
            try:
                success, result_msg = await self._execution_handler(suggestion.action)
                executed = success
                execution_result = result_msg
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                if success:
                    suggestion.status = SuggestionStatus.EXECUTED
                    self.total_executed += 1
                else:
                    error = result_msg
            except Exception as e:
                error = str(e)
                logger.error(f"Failed to execute suggestion {suggestion_id}: {e}")

        # Remove from pending
        del self._pending[suggestion_id]

        logger.info(f"Suggestion confirmed: {suggestion_id} (executed={executed})")
        return ConfirmationResult(
            suggestion_id=suggestion_id,
            accepted=True,
            executed=executed,
            execution_result=execution_result,
            error=error,
            pipeline_result=pipeline_result,
            duration_ms=duration_ms,
        )

    async def reject(
        self,
        suggestion_id: str,
        reason: str = "",
    ) -> ConfirmationResult:
        """
        Reject a pending suggestion.

        Args:
            suggestion_id: ID of the suggestion to reject
            reason: Why it was rejected (for learning)

        Returns:
            ConfirmationResult
        """
        suggestion = self._pending.get(suggestion_id)
        if suggestion is None:
            return ConfirmationResult(
                suggestion_id=suggestion_id,
                accepted=False,
                error="Suggestion not found",
            )

        suggestion.status = SuggestionStatus.REJECTED
        suggestion.rejection_reason = reason
        self.total_rejected += 1

        # Remove from pending
        del self._pending[suggestion_id]

        logger.info(f"Suggestion rejected: {suggestion_id} - {reason}")
        return ConfirmationResult(
            suggestion_id=suggestion_id,
            accepted=False,
        )

    async def expire_stale(self) -> int:
        """
        Expire suggestions that have timed out.

        Returns:
            Number of expired suggestions
        """
        expired_ids = [sid for sid, s in self._pending.items() if s.is_expired]

        for sid in expired_ids:
            suggestion = self._pending.pop(sid)
            suggestion.status = SuggestionStatus.EXPIRED
            self.total_expired += 1
            logger.info(f"Suggestion expired: {sid}")

        return len(expired_ids)

    def get_pending(self) -> list[PendingSuggestion]:
        """Get all pending suggestions."""
        return [s for s in self._pending.values() if s.status == SuggestionStatus.PENDING]

    def get_suggestion(self, suggestion_id: str) -> PendingSuggestion | None:
        """Get a specific suggestion."""
        return self._pending.get(suggestion_id)

    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate for escalation metrics."""
        total_decided = self.total_confirmed + self.total_rejected
        if total_decided == 0:
            return 0.0
        return self.total_confirmed / total_decided

    @property
    def stats(self) -> dict[str, int | float]:
        """Get manager statistics."""
        return {
            "total_submitted": self.total_submitted,
            "total_confirmed": self.total_confirmed,
            "total_rejected": self.total_rejected,
            "total_expired": self.total_expired,
            "total_executed": self.total_executed,
            "pending_count": len(self._pending),
            "acceptance_rate": self.acceptance_rate,
        }

    def clear(self) -> None:
        """Clear all pending suggestions (for testing)."""
        self._pending.clear()


__all__ = [
    "ConfirmationManager",
    "PendingSuggestion",
    "ConfirmationResult",
    "ActionPreview",
    "SuggestionStatus",
]
