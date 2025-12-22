"""
Time Context Router: Traces, turns, telemetry.

AGENTESE Context: time.*

This context handles all temporal operations:
- time.trace      -> Static + runtime tracing (was: kgents trace)
- time.turns      -> Turn history (was: kgents turns)
- time.dag        -> DAG visualization (was: kgents dag)
- time.fork       -> Fork from a turn (was: kgents fork)
- time.telemetry  -> OpenTelemetry (was: kgents telemetry)
- time.pending    -> Pending YIELD turns (was: kgents pending)
- time.approve    -> Approve YIELD turn (was: kgents approve)
- time.reject     -> Reject YIELD turn (was: kgents reject)

Usage:
    kgents time                    # Show time overview
    kgents time trace              # Call graph tracing
    kgents time turns              # Turn history
    kgents time dag                # DAG visualization
    kgents time telemetry          # OpenTelemetry status
    kgents time pending            # List pending YIELD turns
    kgents time approve <id>       # Approve a pending turn
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class TimeRouter(ContextRouter):
    """Router for time.* context (traces, turns, telemetry)."""

    context = "time"
    description = "Traces, turns, telemetry"

    def _register_holons(self) -> None:
        """Register time.* holons."""
        self.register(
            "trace",
            "Static + runtime call graph tracing",
            _handle_trace,
            aspects=["show", "witness", "diff"],
        )
        self.register(
            "turns",
            "Show turn history for an agent",
            _handle_turns,
            aspects=["list", "show", "inspect"],
        )
        self.register(
            "dag",
            "Visualize turn DAG (causal structure)",
            _handle_dag,
            aspects=["show", "export"],
        )
        self.register(
            "fork",
            "Fork from a turn for debugging",
            _handle_fork,
            aspects=["create", "list"],
        )
        self.register(
            "telemetry",
            "OpenTelemetry observability",
            _handle_telemetry,
            aspects=["status", "traces", "metrics"],
        )
        self.register(
            "pending",
            "List pending YIELD turns",
            _handle_pending,
            aspects=["list"],
        )
        self.register(
            "approve",
            "Approve a pending YIELD turn",
            _handle_approve,
            aspects=["commit"],
        )
        self.register(
            "reject",
            "Reject a pending YIELD turn",
            _handle_reject,
            aspects=["cancel"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_trace(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time trace -> delegating to existing trace handler."""
    from protocols.cli.handlers.trace import cmd_trace

    return cmd_trace(args, ctx)


def _handle_turns(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time turns -> delegating to existing turns handler."""
    from protocols.cli.handlers.turns import cmd_turns

    return cmd_turns(args, ctx)


def _handle_dag(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time dag -> delegating to existing dag handler."""
    from protocols.cli.handlers.turns import cmd_dag

    return cmd_dag(args, ctx)


def _handle_fork(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time fork -> delegating to existing fork handler."""
    from protocols.cli.handlers.turns import cmd_fork

    return cmd_fork(args, ctx)


def _handle_telemetry(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time telemetry -> delegating to existing telemetry handler."""
    from protocols.cli.handlers.telemetry import cmd_telemetry

    return cmd_telemetry(args, ctx)


def _handle_pending(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time pending -> delegating to existing pending handler."""
    from protocols.cli.handlers.approve import cmd_pending

    return cmd_pending(args, ctx)


def _handle_approve(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time approve -> delegating to existing approve handler."""
    from protocols.cli.handlers.approve import cmd_approve

    return cmd_approve(args, ctx)


def _handle_reject(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle time reject -> delegating to existing reject handler."""
    from protocols.cli.handlers.approve import cmd_reject

    return cmd_reject(args, ctx)


# =============================================================================
# Entry Point
# =============================================================================

_router: TimeRouter | None = None


def get_router() -> TimeRouter:
    """Get or create the time context router."""
    global _router
    if _router is None:
        _router = TimeRouter()
    return _router


def cmd_time(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Time context: Traces, turns, telemetry.

    AGENTESE: time.*

    Usage:
        kgents time                # Show overview
        kgents time trace          # Call graph tracing
        kgents time turns          # Turn history
        kgents time forest         # Plan forest health
        kgents time telemetry      # OpenTelemetry status
    """
    router = get_router()
    return router.route(args, ctx)
