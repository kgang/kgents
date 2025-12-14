"""
Continuous Handler: Recursive Hegelian dialectic until stability.

Uses H-gent ContinuousDialectic to apply dialectic synthesis recursively
to a list of theses. Each synthesis becomes the new thesis for the next round.

The process stops when:
- Productive tension is reached (synthesis would be premature)
- No more theses remain
- Maximum iterations reached

Usage:
    kgents continuous "speed" "quality" "simplicity"
    kgents continuous "freedom" "security"
    kgents continuous "thesis1" "thesis2" "thesis3" --max 10 --json

The continuous dialectic returns:
- List of synthesis steps (thesis + antithesis -> synthesis)
- Whether productive tension was reached
- Final synthesis (or held tension)
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for continuous command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --max <n>           Maximum iterations (default: 5)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents continuous "speed" "quality" "simplicity"')
    print('  kgents continuous "freedom" "security"')
    print('  kgents continuous "A" "B" "C" --max 10')
    print("  kgents continuous speed quality simplicity --json")
    print()
    print("ABOUT CONTINUOUS DIALECTIC:")
    print("  Each synthesis becomes the thesis for the next step.")
    print("  The chain continues until a productive tension is reached,")
    print("  or all theses are exhausted, or max iterations hit.")
    print()
    print("  This reveals the ultimate synthesis (or irreducible tension)")
    print("  when multiple concepts need to be unified.")


def cmd_continuous(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Continuous dialectic using H-gent ContinuousDialectic.

    Usage:
        kgents continuous "thesis1" "thesis2" [...] [--max n] [--json]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("continuous", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    max_iterations = 5

    # Parse --max flag
    theses: list[str] = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == "--max" and i + 1 < len(args):
            try:
                max_iterations = int(args[i + 1])
                skip_next = True
                continue
            except ValueError:
                pass
        if arg.startswith("--max="):
            try:
                max_iterations = int(arg.split("=", 1)[1])
                continue
            except ValueError:
                pass
        if arg.startswith("-"):
            continue
        theses.append(arg)

    if len(theses) < 2:
        _emit_output(
            "[CONTINUOUS] X Error: Need at least two theses for continuous dialectic\n"
            'Usage: kgents continuous "thesis1" "thesis2" [...]',
            {"error": "Need at least two theses"},
            ctx,
        )
        return 1

    # Run async handler
    return asyncio.run(_async_continuous(theses, max_iterations, json_mode, ctx))


async def _async_continuous(
    theses: list[str],
    max_iterations: int,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of continuous command using ContinuousDialectic."""
    try:
        from agents.h.hegel import ContinuousDialectic

        # Create and invoke the agent
        agent = ContinuousDialectic(max_iterations=max_iterations)
        outputs = await agent.invoke(theses)

        # Build semantic output
        steps = []
        for output in outputs:
            step: dict[str, Any] = {
                "thesis": output.tension.thesis if output.tension else None,
                "antithesis": output.tension.antithesis if output.tension else None,
                "synthesis": output.synthesis,
                "productive_tension": output.productive_tension,
                "notes": output.sublation_notes,
            }
            steps.append(step)

        # Determine final state
        final_output = outputs[-1] if outputs else None
        final_synthesis = None
        ended_in_tension = False

        if final_output:
            if final_output.productive_tension:
                ended_in_tension = True
            else:
                final_synthesis = final_output.synthesis

        semantic: dict[str, Any] = {
            "command": "continuous",
            "theses": theses,
            "max_iterations": max_iterations,
            "steps": steps,
            "iterations": len(outputs),
            "final_synthesis": final_synthesis,
            "ended_in_tension": ended_in_tension,
        }

        if json_mode:
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[CONTINUOUS] Recursive Dialectic",
                "",
                f"Theses: {' -> '.join(theses)}",
                f"Max iterations: {max_iterations}",
                "",
            ]

            # Show each step
            for i, output in enumerate(outputs, 1):
                lines.append(f"Step {i}:")
                if output.tension:
                    lines.append(f"  Thesis: {output.tension.thesis}")
                    lines.append(f"  Antithesis: {output.tension.antithesis}")

                if output.productive_tension:
                    lines.append("  [Tension Held - no synthesis forced]")
                    lines.append(f"  {output.sublation_notes}")
                else:
                    lines.append(f"  Synthesis: {output.synthesis}")
                    if output.sublation_notes:
                        lines.append(f"  ({output.sublation_notes})")
                lines.append("")

            # Final summary
            lines.append("=" * 40)
            if ended_in_tension:
                lines.append("Result: PRODUCTIVE TENSION")
                lines.append("  The final concepts cannot be fully synthesized.")
                lines.append("  This tension is generative - hold both.")
            elif final_synthesis:
                lines.append("Result: SYNTHESIS")
                lines.append(f"  Final: {final_synthesis}")
            else:
                lines.append("Result: No synthesis achieved")

            lines.append(f"\nIterations: {len(outputs)} of {max_iterations} max")

            _emit_output("\n".join(lines), semantic, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[CONTINUOUS] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[CONTINUOUS] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


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
