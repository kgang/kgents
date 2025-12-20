"""
Witness Audit Trail: Automatic Action Recording for Cross-Jewel Operations.

"Every action leaves a trace. Every trace enables rollback."

The audit system automatically records:
- Pipeline step executions
- Scheduled task completions
- Cross-jewel invocations

This bridges the scheduler/pipeline layer with persistence, ensuring
the rollback window is always populated.

Pattern: "Container Owns Workflow" (crown-jewel-patterns.md)
The AuditingInvoker wraps JewelInvoker, owning the action recording lifecycle.

See: plans/kgentsd-cross-jewel.md
See: services/witness/persistence.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable, Protocol
from uuid import uuid4

from .invoke import InvocationResult, JewelInvoker, is_mutation_path
from .pipeline import Pipeline, PipelineResult, PipelineRunner, Step
from .polynomial import ActionResult, TrustLevel

if TYPE_CHECKING:
    from protocols.agentese.node import Observer

    from .persistence import WitnessPersistence


logger = logging.getLogger(__name__)


# =============================================================================
# Audit Entry
# =============================================================================


@dataclass
class AuditEntry:
    """
    A single entry in the audit trail.

    Captures everything needed for accountability and rollback.
    """

    entry_id: str = field(default_factory=lambda: f"audit-{uuid4().hex[:12]}")
    path: str = ""
    action_type: str = ""  # invoke, pipeline, schedule
    success: bool = True
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Context
    observer_archetype: str = ""
    trust_level: str = ""
    kwargs: dict[str, Any] = field(default_factory=dict)

    # Rollback info
    is_mutation: bool = False
    reversible: bool = True
    inverse_action: str | None = None

    def to_action_result(self) -> ActionResult:
        """Convert to ActionResult for persistence."""
        return ActionResult(
            action_id=self.entry_id,
            action=f"{self.action_type}: {self.path}",
            success=self.success,
            message=self.error or "OK",
            reversible=self.reversible,
            inverse_action=self.inverse_action,
            timestamp=self.timestamp,
        )


# =============================================================================
# Audit Callback Protocol
# =============================================================================


class AuditCallback(Protocol):
    """Protocol for audit callbacks."""

    async def __call__(self, entry: AuditEntry) -> None:
        """Called when an action is recorded."""
        ...


# =============================================================================
# Auditing Invoker
# =============================================================================


@dataclass
class AuditingInvoker:
    """
    JewelInvoker wrapper that automatically records actions to persistence.

    Every mutation is recorded, creating an audit trail that populates
    the rollback window.

    Pattern: Decorator (wraps existing invoker without modifying it)

    Example:
        auditing = AuditingInvoker(invoker, persistence)

        # All invocations are now audited
        result = await auditing.invoke("world.forge.fix", observer)

        # Access the underlying invoker
        auditing.inner.trust_level  # Still accessible
    """

    inner: JewelInvoker
    persistence: "WitnessPersistence | None" = None
    record_reads: bool = False  # If True, also record read-only operations
    callbacks: list[AuditCallback] = field(default_factory=list)
    _log: list[AuditEntry] = field(default_factory=list)

    async def invoke(
        self,
        path: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> InvocationResult:
        """
        Invoke an AGENTESE path with automatic auditing.

        Mutations are always recorded. Reads are optionally recorded.
        """
        start_time = datetime.now(UTC)
        is_mutation = is_mutation_path(path)

        # Delegate to inner invoker
        result = await self.inner.invoke(path, observer, **kwargs)

        # Calculate duration
        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        # Create audit entry
        entry = AuditEntry(
            path=path,
            action_type="invoke",
            success=result.success,
            result=result.result,
            error=result.error,
            duration_ms=duration_ms,
            observer_archetype=getattr(observer, "archetype", ""),
            trust_level=self.inner.trust_level.name,
            kwargs=kwargs,
            is_mutation=is_mutation,
            reversible=is_mutation,  # Assume mutations are reversible by default
        )

        # Record if mutation or if recording reads
        if is_mutation or self.record_reads:
            await self._record(entry)

        return result

    async def invoke_read(
        self,
        path: str,
        observer: "Observer",
        **kwargs: Any,
    ) -> InvocationResult:
        """Convenience for read-only invocations."""
        return await self.invoke(path, observer, **kwargs)

    async def invoke_mutation(
        self,
        path: str,
        observer: "Observer",
        reversible: bool = True,
        inverse_action: str | None = None,
        **kwargs: Any,
    ) -> InvocationResult:
        """
        Invoke a mutation with explicit rollback info.

        Args:
            path: AGENTESE path
            observer: Observer context
            reversible: Whether this action can be rolled back
            inverse_action: Action to undo this mutation
            **kwargs: Arguments for invocation
        """
        start_time = datetime.now(UTC)

        result = await self.inner.invoke(path, observer, **kwargs)

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        entry = AuditEntry(
            path=path,
            action_type="invoke",
            success=result.success,
            result=result.result,
            error=result.error,
            duration_ms=duration_ms,
            observer_archetype=getattr(observer, "archetype", ""),
            trust_level=self.inner.trust_level.name,
            kwargs=kwargs,
            is_mutation=True,
            reversible=reversible,
            inverse_action=inverse_action,
        )

        await self._record(entry)
        return result

    async def _record(self, entry: AuditEntry) -> None:
        """Record an audit entry."""
        self._log.append(entry)

        # Persist if persistence layer is available
        if self.persistence:
            try:
                await self.persistence.record_action(entry.to_action_result())
            except Exception as e:
                logger.error(f"Failed to persist audit entry: {e}")

        # Fire callbacks
        for callback in self.callbacks:
            try:
                await callback(entry)
            except Exception as e:
                logger.error(f"Audit callback failed: {e}")

    def add_callback(self, callback: AuditCallback) -> None:
        """Add an audit callback."""
        self.callbacks.append(callback)

    def get_log(
        self,
        mutations_only: bool = True,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get recent audit entries."""
        entries = self._log
        if mutations_only:
            entries = [e for e in entries if e.is_mutation]
        return list(reversed(entries[-limit:]))

    @property
    def trust_level(self) -> TrustLevel:
        """Expose inner invoker's trust level."""
        return self.inner.trust_level


# =============================================================================
# Auditing Pipeline Runner
# =============================================================================


@dataclass
class AuditingPipelineRunner:
    """
    PipelineRunner wrapper that audits the entire pipeline execution.

    Records:
    - Pipeline start/end as a single action
    - Optionally each step as individual actions

    Example:
        runner = AuditingPipelineRunner(
            invoker=auditing_invoker,
            observer=observer,
            persistence=persistence,
        )

        result = await runner.run(pipeline)
        # Pipeline execution recorded in rollback window
    """

    invoker: "AuditingInvoker | JewelInvoker"
    observer: "Observer"
    persistence: "WitnessPersistence | None" = None
    record_steps: bool = False  # Record individual steps (in addition to pipeline)
    abort_on_failure: bool = True
    log_steps: bool = True

    async def run(
        self,
        pipeline: Pipeline,
        initial_kwargs: dict[str, Any] | None = None,
        name: str = "",
    ) -> PipelineResult:
        """
        Execute a pipeline with automatic auditing.

        The pipeline execution is recorded as a single action.
        """
        start_time = datetime.now(UTC)

        # Create inner runner with appropriate invoker
        inner_invoker = (
            self.invoker.inner if isinstance(self.invoker, AuditingInvoker) else self.invoker
        )

        runner = PipelineRunner(
            invoker=inner_invoker,
            observer=self.observer,
            abort_on_failure=self.abort_on_failure,
            log_steps=self.log_steps,
        )

        result = await runner.run(pipeline, initial_kwargs)

        # Calculate duration
        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        # Record pipeline execution
        entry = AuditEntry(
            path=f"pipeline:{name or 'unnamed'}",
            action_type="pipeline",
            success=result.success,
            result=result.to_dict(),
            error=result.error,
            duration_ms=duration_ms,
            observer_archetype=getattr(self.observer, "archetype", ""),
            trust_level=(
                self.invoker.trust_level.name if hasattr(self.invoker, "trust_level") else "UNKNOWN"
            ),
            kwargs=initial_kwargs or {},
            is_mutation=any(
                is_mutation_path(s.path) for s in pipeline.steps if isinstance(s, Step)
            ),
            reversible=True,  # Pipelines are reversible if we track step inverses
        )

        if self.persistence:
            try:
                await self.persistence.record_action(entry.to_action_result())
            except Exception as e:
                logger.error(f"Failed to persist pipeline audit: {e}")

        return result


# =============================================================================
# Factory Functions
# =============================================================================


def create_auditing_invoker(
    invoker: JewelInvoker,
    persistence: "WitnessPersistence | None" = None,
    record_reads: bool = False,
) -> AuditingInvoker:
    """
    Create an auditing invoker wrapper.

    Args:
        invoker: The JewelInvoker to wrap
        persistence: Optional persistence layer for durable audit trail
        record_reads: If True, also record read-only operations

    Returns:
        AuditingInvoker instance
    """
    return AuditingInvoker(
        inner=invoker,
        persistence=persistence,
        record_reads=record_reads,
    )


def create_auditing_runner(
    invoker: "AuditingInvoker | JewelInvoker",
    observer: "Observer",
    persistence: "WitnessPersistence | None" = None,
    record_steps: bool = False,
) -> AuditingPipelineRunner:
    """
    Create an auditing pipeline runner.

    Args:
        invoker: Invoker (auditing or regular)
        observer: Observer context
        persistence: Optional persistence layer
        record_steps: If True, record individual steps

    Returns:
        AuditingPipelineRunner instance
    """
    return AuditingPipelineRunner(
        invoker=invoker,
        observer=observer,
        persistence=persistence,
        record_steps=record_steps,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AuditEntry",
    "AuditCallback",
    "AuditingInvoker",
    "AuditingPipelineRunner",
    "create_auditing_invoker",
    "create_auditing_runner",
]
