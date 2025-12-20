"""
Tool Executor: Async Execution with Tracing, Timeout, and Trust Gating.

The ToolExecutor wraps tool invocation with:
- Trust gate check (pre-invocation)
- Timeout enforcement
- Differance trace recording (post-invocation)
- SynergyBus event emission

Integration Points:
- Witness: Trust gate, audit trail
- Differance: Trace capture with ghost alternatives
- SynergyBus: Tool lifecycle events

Pattern (from crown-jewel-patterns.md):
- Pattern 6: Async-Safe Event Emission (fire-and-forget traces)
- Pattern 15: No Hollow Services (requires DI wiring)

See: spec/services/tooling.md §6-7
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .base import Tool, ToolError, ToolResult, ToolTimeoutError
from .trust_gate import GateResult, ToolTrustGate, TrustViolation

if TYPE_CHECKING:
    from agents.differance import DifferanceStore
    from protocols.synergy import SynergyEventBus
    from services.witness import WitnessPersistence

logger = logging.getLogger(__name__)

A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Execution Context
# =============================================================================


@dataclass
class ExecutionContext:
    """
    Context for a tool execution.

    Captures all metadata about an execution for tracing and audit.
    """

    execution_id: str = field(default_factory=lambda: f"exec-{uuid.uuid4().hex[:12]}")
    tool_name: str = ""
    observer_id: str | None = None
    git_email: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None
    gate_result: GateResult | None = None
    alternatives_considered: list[str] = field(default_factory=list)

    def complete(self, success: bool, error: str | None = None) -> None:
        """Mark execution as complete."""
        self.ended_at = datetime.now(UTC)
        self.duration_ms = (self.ended_at - self.started_at).total_seconds() * 1000
        self.success = success
        self.error = error


# =============================================================================
# Tool Executor
# =============================================================================


class ToolExecutor:
    """
    Executor for tool invocations with full observability.

    Provides:
    - Trust gate check before execution
    - Timeout enforcement (default 2min, max 10min)
    - Differance trace recording
    - SynergyBus event emission

    Example:
        executor = ToolExecutor(
            witness=witness_persistence,
            differance=differance_store,
        )

        result = await executor.execute(
            tool=ReadTool(),
            request=ReadRequest(path="/path/to/file"),
            observer=observer,
        )

    DI Integration:
        # In providers.py
        async def get_tool_executor():
            witness = await get_service("witness_persistence")
            differance = await get_service("differance_store")
            return ToolExecutor(witness=witness, differance=differance)
    """

    def __init__(
        self,
        witness: "WitnessPersistence | None" = None,
        differance: "DifferanceStore | None" = None,
        synergy_bus: "SynergyEventBus | None" = None,
        default_timeout_ms: int = 120_000,
        max_timeout_ms: int = 600_000,
    ) -> None:
        """
        Initialize executor with integrations.

        Args:
            witness: WitnessPersistence for trust gating
            differance: DifferanceStore for trace recording
            synergy_bus: SynergyBus for event emission
            default_timeout_ms: Default timeout (2 minutes)
            max_timeout_ms: Maximum timeout (10 minutes)
        """
        self._witness = witness
        self._differance = differance
        self._synergy_bus = synergy_bus
        self._default_timeout_ms = default_timeout_ms
        self._max_timeout_ms = max_timeout_ms
        self._trust_gate = ToolTrustGate(witness=witness)

    async def execute(
        self,
        tool: Tool[A, B],
        request: A,
        observer: Any | None = None,
        git_email: str | None = None,
        timeout_ms: int | None = None,
        alternatives: list[str] | None = None,
    ) -> ToolResult[B]:
        """
        Execute a tool with full observability.

        Args:
            tool: Tool to execute
            request: Input request
            observer: Optional Umwelt for trust context
            git_email: Git email for trust lookup
            timeout_ms: Override timeout
            alternatives: Ghost alternatives for trace

        Returns:
            ToolResult with value and metadata

        Raises:
            TrustViolation: If trust check fails
            ToolTimeoutError: If execution exceeds timeout
            ToolError: On execution failure
        """
        # Create execution context
        ctx = ExecutionContext(
            tool_name=tool.name,
            observer_id=str(getattr(observer, "identity", None)) if observer else None,
            git_email=git_email,
            alternatives_considered=alternatives or [],
        )

        try:
            # Pre-invocation: Trust gate check
            gate_result = await self._check_trust(tool, observer, git_email)
            ctx.gate_result = gate_result

            if not gate_result.allowed:
                if gate_result.requires_confirmation:
                    # TODO: Handle confirmation flow
                    raise TrustViolation(
                        f"Tool {tool.name} requires confirmation",
                        gate_result,
                    )
                raise TrustViolation(gate_result.message, gate_result)

            # Emit pre-invocation event
            await self._emit_event("tool.invoked", ctx, request)

            # Determine timeout
            effective_timeout = self._get_timeout(tool, timeout_ms)

            # Execute with timeout
            start_time = time.monotonic()
            try:
                result = await asyncio.wait_for(
                    tool.invoke(request),
                    timeout=effective_timeout / 1000,  # Convert to seconds
                )
            except asyncio.TimeoutError:
                ctx.complete(success=False, error="Timeout")
                raise ToolTimeoutError(
                    f"Tool {tool.name} timed out after {effective_timeout}ms",
                    tool.name,
                    int(effective_timeout),
                )

            duration_ms = (time.monotonic() - start_time) * 1000
            ctx.complete(success=True)

            # Post-invocation: Record trace
            await self._record_trace(ctx, request, result)

            # Emit completion event
            await self._emit_event("tool.completed", ctx, request, result)

            return ToolResult(
                value=result,
                duration_ms=duration_ms,
                tool_name=tool.name,
            )

        except TrustViolation:
            # Re-raise trust violations
            await self._emit_event("tool.trust_denied", ctx, request)
            raise

        except ToolTimeoutError:
            await self._emit_event("tool.timeout", ctx, request)
            await self._record_trace(ctx, request, None)
            raise

        except Exception as e:
            ctx.complete(success=False, error=str(e))
            await self._emit_event("tool.failed", ctx, request, error=str(e))
            await self._record_trace(ctx, request, None)

            if isinstance(e, ToolError):
                raise
            raise ToolError(str(e), tool.name) from e

    async def check_trust(
        self,
        tool: Tool[Any, Any],
        observer: Any | None = None,
        git_email: str | None = None,
    ) -> GateResult:
        """
        Check trust without executing.

        Useful for UI to show which tools are available.
        """
        return await self._check_trust(tool, observer, git_email)

    async def _check_trust(
        self,
        tool: Tool[Any, Any],
        observer: Any,
        git_email: str | None,
    ) -> GateResult:
        """Internal trust check."""
        # Use tool's trust requirement if higher than default
        self._trust_gate.set_requirement(tool.name, tool.trust_required)
        return await self._trust_gate.check(tool.name, observer, git_email)

    def _get_timeout(self, tool: Tool[Any, Any], override_ms: int | None) -> float:
        """Get effective timeout in milliseconds."""
        if override_ms is not None:
            return min(override_ms, self._max_timeout_ms)
        return min(tool.timeout_default_ms, self._max_timeout_ms)

    async def _record_trace(
        self,
        ctx: ExecutionContext,
        request: Any,
        result: Any,
    ) -> None:
        """Record execution trace in Differance (fire-and-forget)."""
        if self._differance is None:
            return

        try:
            # Lazy import to avoid circular
            from agents.differance import WiringTrace

            # Create trace using the correct factory method
            trace = WiringTrace.create(
                operation=f"world.tools.{ctx.tool_name}",
                inputs=(str(request)[:100],),  # Truncate for storage
                output=str(result)[:100] if result else ctx.error or "error",
                context=f"Tool execution: {ctx.tool_name}",
                # Alternatives could be added here if we tracked them
            )

            # Fire-and-forget: record to store
            asyncio.create_task(self._differance.append(trace))

        except Exception as e:
            logger.debug(f"Trace recording failed: {e}")

    async def _emit_event(
        self,
        event_type: str,
        ctx: ExecutionContext,
        request: Any,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        """Emit tool lifecycle event to SynergyBus (fire-and-forget)."""
        if self._synergy_bus is None:
            logger.debug(
                f"Tool event: {event_type} tool={ctx.tool_name} "
                f"success={ctx.success} duration={ctx.duration_ms:.1f}ms"
            )
            return

        from protocols.synergy import (
            Jewel,
            SynergyEvent,
            SynergyEventType,
        )

        # Map event type strings to SynergyEventType
        type_map = {
            "tool.invoked": SynergyEventType.TOOL_INVOKED,
            "tool.completed": SynergyEventType.TOOL_COMPLETED,
            "tool.failed": SynergyEventType.TOOL_FAILED,
            "tool.trust_denied": SynergyEventType.TOOL_TRUST_DENIED,
            "tool.timeout": SynergyEventType.TOOL_FAILED,  # Timeout is a failure
        }

        synergy_type = type_map.get(event_type)
        if synergy_type is None:
            logger.debug(f"Unknown tool event type: {event_type}")
            return

        event = SynergyEvent(
            source_jewel=Jewel.TOOLING,
            target_jewel=Jewel.ALL,
            event_type=synergy_type,
            source_id=ctx.execution_id,
            payload={
                "tool_name": ctx.tool_name,
                "observer_id": ctx.observer_id,
                "success": ctx.success,
                "duration_ms": ctx.duration_ms,
                "error": error,
            },
        )

        # Fire-and-forget (Pattern 6: Async-Safe Event Emission)
        asyncio.create_task(self._synergy_bus.emit(event))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ExecutionContext",
    "ToolExecutor",
]
