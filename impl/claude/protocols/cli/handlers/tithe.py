"""
Tithe Handler: Voluntarily discharge metabolic pressure.

The Accursed Share: surplus must be spent.

Usage:
    kgents tithe          # Discharge default amount (0.1)
    kgents tithe --amount 0.3  # Discharge more
    kgents tithe --status  # Show metabolic status only

Example output:
    [TITHE] Discharged: 0.10 | Remaining: 0.35 | The river flows.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_tithe(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Voluntarily discharge entropy pressure.

    kgents tithe - Pay for order, discharge metabolic pressure.

    The Accursed Share: surplus must be spent. Use this command
    to voluntarily discharge pressure before fever triggers.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("tithe", args)
        except ImportError:
            pass

    # Parse args
    help_mode = "--help" in args or "-h" in args
    status_mode = "--status" in args
    amount = 0.1  # Default

    # Parse --amount flag
    for i, arg in enumerate(args):
        if arg.startswith("--amount="):
            try:
                amount = float(arg.split("=", 1)[1])
            except ValueError:
                _emit_output(
                    "[TITHE] X Invalid amount value",
                    {"error": "Invalid amount value"},
                    ctx,
                )
                return 1
        elif arg == "--amount" and i + 1 < len(args):
            try:
                amount = float(args[i + 1])
            except ValueError:
                _emit_output(
                    "[TITHE] X Invalid amount value",
                    {"error": "Invalid amount value"},
                    ctx,
                )
                return 1

    if help_mode:
        print(__doc__)
        return 0

    # Run async tithe
    return asyncio.run(_async_tithe(amount=amount, status_only=status_mode, ctx=ctx))


async def _async_tithe(
    amount: float = 0.1,
    status_only: bool = False,
    ctx: "InvocationContext | None" = None,
) -> int:
    """
    Async implementation of tithe command.
    """
    try:
        from protocols.agentese.metabolism import get_metabolic_engine

        engine = get_metabolic_engine()

        if status_only:
            # Show status only
            status = engine.status()
            human_output = _format_status(status)
            _emit_output(human_output, status, ctx)
            return 0

        # Perform tithe
        result = engine.tithe(amount)

        # Format output
        human_output = (
            f"[TITHE] Discharged: {result['discharged']:.2f} | "
            f"Remaining: {result['remaining_pressure']:.2f} | "
            f"{result['gratitude']}"
        )

        semantic_output = {
            "action": "tithe",
            "discharged": result["discharged"],
            "remaining_pressure": result["remaining_pressure"],
            "gratitude": result["gratitude"],
        }

        _emit_output(human_output, semantic_output, ctx)
        return 0

    except ImportError as e:
        error_human = f"[TITHE] X Metabolism not available: {e}"
        error_semantic = {"error": f"Metabolism not available: {e}"}
        _emit_output(error_human, error_semantic, ctx)
        return 1

    except Exception as e:
        error_human = f"[TITHE] X Error: {e}"
        error_semantic = {"error": str(e)}
        _emit_output(error_human, error_semantic, ctx)
        return 1


def _format_status(status: dict[str, Any]) -> str:
    """Format metabolic status for human output."""
    pressure = status["pressure"]
    threshold = status["critical_threshold"]
    pressure_pct = int(pressure / threshold * 100) if threshold > 0 else 0
    temp = status["temperature"]
    fever_str = "FEVER" if status["in_fever"] else "normal"

    return (
        f"[METABOLISM] {fever_str} | "
        f"Pressure: {pressure:.2f} ({pressure_pct}% of threshold) | "
        f"Temperature: {temp:.2f}"
    )


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
