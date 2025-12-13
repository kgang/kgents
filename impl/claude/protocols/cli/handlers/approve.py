"""
Approve Handler: CLI commands for YIELD turn governance.

Part of the Turn-gents Realization: making governance tangible for developers.

Usage:
    kgents pending              # List pending YIELD turns
    kgents approve <turn_id>    # Approve a pending YIELD turn
    kgents reject <turn_id>     # Reject a pending YIELD turn

YIELD turns are the governance intercept points in Turn-gents.
They operationalize the "ethical" principle: preserve human agency.

When an agent emits a YIELD turn:
1. Execution blocks until approval/rejection/timeout
2. Developer can review the proposed action
3. Approve to continue, Reject to prevent

This is Phase 5 of Turn-gents: Yield Governance.

References:
- Turn-gents Plan: Phase 5 (Yield Governance)
- weave/yield_handler.py: YieldHandler, ApprovalStrategy
- weave/turn.py: YieldTurn
"""

from __future__ import annotations

import asyncio
import json as json_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_pending_help() -> None:
    """Print help for pending command."""
    print("kgents pending - List pending YIELD turns awaiting approval")
    print()
    print("USAGE:")
    print("  kgents pending [options]")
    print()
    print("OPTIONS:")
    print("  --json            Output as JSON")
    print("  --source AGENT    Filter by source agent")
    print("  --help, -h        Show this help")


def _print_approve_help() -> None:
    """Print help for approve command."""
    print("kgents approve - Approve a pending YIELD turn")
    print()
    print("USAGE:")
    print("  kgents approve <turn_id>")
    print()
    print("ARGUMENTS:")
    print("  turn_id           ID of the YIELD turn to approve (can be partial)")
    print()
    print("OPTIONS:")
    print("  --help, -h        Show this help")


def _print_reject_help() -> None:
    """Print help for reject command."""
    print("kgents reject - Reject a pending YIELD turn")
    print()
    print("USAGE:")
    print("  kgents reject <turn_id> [--reason <reason>]")
    print()
    print("ARGUMENTS:")
    print("  turn_id           ID of the YIELD turn to reject (can be partial)")
    print()
    print("OPTIONS:")
    print("  --reason TEXT     Reason for rejection")
    print("  --help, -h        Show this help")


# =============================================================================
# Global YieldHandler Instance
# =============================================================================

# In a real implementation, this would be managed by the lifecycle system
_global_yield_handler: Any = None


def _get_yield_handler() -> Any:
    """Get or create the global YieldHandler."""
    global _global_yield_handler

    if _global_yield_handler is None:
        from weave import YieldHandler

        _global_yield_handler = YieldHandler()

    return _global_yield_handler


def get_yield_handler() -> Any:
    """Public API to get the global YieldHandler."""
    return _get_yield_handler()


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_pending(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    List pending YIELD turns awaiting approval.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("pending", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_pending_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Parse --source
    source_filter: str | None = None
    for i, arg in enumerate(args):
        if arg == "--source" and i + 1 < len(args):
            source_filter = args[i + 1]

    try:
        return _execute_pending(source_filter, json_mode, ctx)
    except Exception as e:
        _emit_output(
            f"[PENDING] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _execute_pending(
    source_filter: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the pending command."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    handler = _get_yield_handler()
    pending = handler.list_pending()

    # Apply source filter
    if source_filter:
        pending = [t for t in pending if t.source == source_filter]

    if not pending:
        _emit_output(
            "[PENDING] No pending YIELD turns.",
            {"status": "empty", "pending": []},
            ctx,
        )
        return 0

    if json_mode:
        pending_data = [
            {
                "id": t.id,
                "source": t.source,
                "yield_reason": t.yield_reason,
                "content": str(t.content)[:200],
                "required_approvers": list(t.required_approvers),
                "approved_by": list(t.approved_by),
                "pending_approvers": list(t.pending_approvers()),
                "confidence": t.confidence,
            }
            for t in pending
        ]
        _emit_output(
            json_module.dumps(pending_data, indent=2),
            {"pending": pending_data},
            ctx,
        )
    else:
        console = Console()

        console.print(f"\n[bold yellow]Pending YIELD Turns ({len(pending)})[/]\n")

        for turn in pending:
            # Build panel content
            content_preview = str(turn.content)
            if len(content_preview) > 200:
                content_preview = content_preview[:197] + "..."

            pending_approvers = turn.pending_approvers()
            approved_by = turn.approved_by

            details = Text()
            details.append("Source: ", style="dim")
            details.append(f"{turn.source}\n", style="yellow")
            details.append("Reason: ", style="dim")
            details.append(f"{turn.yield_reason}\n", style="white")
            details.append("Content: ", style="dim")
            details.append(f"{content_preview}\n", style="white")
            details.append("Confidence: ", style="dim")
            conf_color = (
                "green"
                if turn.confidence > 0.7
                else "yellow"
                if turn.confidence > 0.3
                else "red"
            )
            details.append(f"{turn.confidence:.0%}\n", style=conf_color)
            details.append("Approved by: ", style="dim")
            details.append(f"{', '.join(approved_by) or 'none'}\n", style="green")
            details.append("Awaiting: ", style="dim")
            details.append(f"{', '.join(pending_approvers)}", style="yellow")

            panel = Panel(
                details,
                title=f"[cyan]{turn.id[:16]}...[/]",
                subtitle="[dim]kg approve {id} | kg reject {id}[/]",
                border_style="yellow",
            )
            console.print(panel)
            console.print()

        console.print("[dim]Use 'kg approve <id>' or 'kg reject <id>' to respond.[/]")

    return 0


def cmd_approve(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Approve a pending YIELD turn.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("approve", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_approve_help()
        return 0

    # Get turn_id (first non-flag argument)
    turn_id: str | None = None
    for arg in args:
        if arg.startswith("-"):
            continue
        turn_id = arg
        break

    if not turn_id:
        _emit_output(
            "[APPROVE] No turn ID specified.\nUsage: kgents approve <turn_id>",
            {"error": "No turn ID specified"},
            ctx,
        )
        return 1

    try:
        return asyncio.run(_execute_approve(turn_id, ctx))
    except Exception as e:
        _emit_output(
            f"[APPROVE] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _execute_approve(
    turn_id: str,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the approve command."""
    from rich.console import Console

    handler = _get_yield_handler()

    # Find the turn (support partial IDs)
    full_id = _resolve_turn_id(handler, turn_id)
    if full_id is None:
        _emit_output(
            f"[APPROVE] Turn not found: {turn_id}",
            {"error": f"Turn not found: {turn_id}"},
            ctx,
        )
        return 1

    # Approve as "human" (CLI user)
    approver = "human"
    try:
        success = await handler.approve(full_id, approver)
    except ValueError as e:
        _emit_output(
            f"[APPROVE] Cannot approve: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1

    if success:
        # Check if fully approved now
        turn = handler.get_pending(full_id)
        if turn is None:
            # Turn was fully approved and removed from pending
            console = Console()
            console.print(f"[green]Approved:[/] {full_id[:16]}...")
            console.print("[dim]Turn is fully approved and can proceed.[/]")
        else:
            # Still needs more approvers
            pending = turn.pending_approvers()
            console = Console()
            console.print(f"[green]Approved by {approver}:[/] {full_id[:16]}...")
            console.print(f"[yellow]Still awaiting:[/] {', '.join(pending)}")
    else:
        _emit_output(
            f"[APPROVE] Turn not found or already processed: {turn_id}",
            {"error": "Turn not found or already processed"},
            ctx,
        )
        return 1

    return 0


def cmd_reject(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Reject a pending YIELD turn.

    Args:
        args: Command-line arguments
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("reject", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_reject_help()
        return 0

    # Parse --reason
    reason: str = ""
    for i, arg in enumerate(args):
        if arg == "--reason" and i + 1 < len(args):
            reason = args[i + 1]

    # Get turn_id (first non-flag argument)
    turn_id: str | None = None
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--reason":
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        turn_id = arg
        break

    if not turn_id:
        _emit_output(
            "[REJECT] No turn ID specified.\n"
            "Usage: kgents reject <turn_id> [--reason <reason>]",
            {"error": "No turn ID specified"},
            ctx,
        )
        return 1

    try:
        return asyncio.run(_execute_reject(turn_id, reason, ctx))
    except Exception as e:
        _emit_output(
            f"[REJECT] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _execute_reject(
    turn_id: str,
    reason: str,
    ctx: "InvocationContext | None",
) -> int:
    """Execute the reject command."""
    from rich.console import Console

    handler = _get_yield_handler()

    # Find the turn (support partial IDs)
    full_id = _resolve_turn_id(handler, turn_id)
    if full_id is None:
        _emit_output(
            f"[REJECT] Turn not found: {turn_id}",
            {"error": f"Turn not found: {turn_id}"},
            ctx,
        )
        return 1

    # Get turn info before rejection
    turn = handler.get_pending(full_id)

    # Reject as "human" (CLI user)
    rejector = "human"
    success = await handler.reject(full_id, rejector, reason)

    if success:
        console = Console()
        console.print(f"[red]Rejected:[/] {full_id[:16]}...")
        if turn:
            console.print(f"[dim]Source:[/] {turn.source}")
            console.print(f"[dim]Reason:[/] {turn.yield_reason}")
        if reason:
            console.print(f"[dim]Rejection reason:[/] {reason}")
        console.print("[dim]The agent will be notified of the rejection.[/]")
    else:
        _emit_output(
            f"[REJECT] Turn not found or already processed: {turn_id}",
            {"error": "Turn not found or already processed"},
            ctx,
        )
        return 1

    return 0


# =============================================================================
# Helper Functions
# =============================================================================


def _resolve_turn_id(handler: Any, partial_id: str) -> str | None:
    """
    Resolve a partial turn ID to a full ID.

    Supports:
    - Full UUID
    - Partial prefix (e.g., first 8 characters)
    """
    # Check for exact match
    if handler.is_pending(partial_id):
        return str(partial_id)

    # Check for prefix match
    for turn in handler.list_pending():
        if turn.id.startswith(partial_id):
            return str(turn.id)

    return None


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


__all__ = [
    "cmd_pending",
    "cmd_approve",
    "cmd_reject",
    "get_yield_handler",
]
