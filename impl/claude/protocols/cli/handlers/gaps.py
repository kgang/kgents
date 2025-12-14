"""
Gaps Handler: Surface representational gaps using Lacanian analysis.

Uses H-gent LacanAgent to analyze what cannot be represented - the gap
between reality, symbolization, and imagination.

Lacan's three registers:
- Real: That which resists symbolization; the impossible kernel
- Symbolic: Language, structure, law, the system of differences
- Imaginary: Images, ideals, the ego, coherent narratives

Usage:
    kgents gaps                                    # Analyze default system text
    kgents gaps "We are a helpful AI assistant"   # Analyze custom text
    kgents gaps --json                            # Output as JSON

The gaps analysis returns:
- gaps: What cannot be represented
- register_location: Position in Symbolic/Imaginary/Real
- slippages: Register miscategorizations
- knot_status: Whether the registers are properly knotted
- objet_petit_a: What the system is organized around lacking
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Default text for analysis
DEFAULT_TEXT = (
    "We are a helpful AI assistant that provides accurate and safe responses."
)


def _print_help() -> None:
    """Print help for gaps command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents gaps")
    print('  kgents gaps "We are a helpful AI assistant"')
    print("  kgents gaps --json")
    print()
    print("ABOUT LACANIAN ANALYSIS:")
    print("  The Real is what cannot be symbolized - the impossible kernel.")
    print("  Gaps reveal what your system cannot represent about itself.")
    print("  Problems arise when the registers come unknotted.")


def cmd_gaps(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Gaps analysis using H-gent LacanAgent.

    Usage:
        kgents gaps [text] [--json]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("gaps", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Extract text (everything that's not a flag)
    text_parts: list[str] = []
    for arg in args:
        if arg.startswith("-"):
            continue
        text_parts.append(arg)

    # Default if not provided
    if not text_parts:
        text = DEFAULT_TEXT
    else:
        text = " ".join(text_parts)

    # Run async handler
    return asyncio.run(_async_gaps(text, json_mode, ctx))


async def _async_gaps(
    text: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of gaps command using LacanAgent."""
    try:
        from agents.h.lacan import LacanAgent, LacanError, LacanInput, LacanOutput

        # Build input for LacanAgent
        input_data = LacanInput(output=text)

        # Invoke the agent
        result = await LacanAgent().invoke(input_data)

        # Check for error
        if isinstance(result, LacanError):
            _emit_output(
                f"[GAPS] X Analysis error: {result.message}",
                {"error": result.message, "type": result.error_type},
                ctx,
            )
            return 1

        output: LacanOutput = result

        # Build semantic output
        semantic: dict[str, Any] = {
            "command": "gaps",
            "text": text,
            "gaps": output.gaps,
            "register_location": {
                "symbolic": output.register_location.symbolic,
                "imaginary": output.register_location.imaginary,
                "real_proximity": output.register_location.real_proximity,
            },
            "slippages": [
                {
                    "claimed": s.claimed.value,
                    "actual": s.actual.value,
                    "evidence": s.evidence,
                }
                for s in output.slippages
            ],
            "knot_status": output.knot_status.value,
            "objet_petit_a": output.objet_petit_a,
        }

        if json_mode:
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[GAPS] Representational Analysis",
                "",
            ]

            # Gaps
            if output.gaps:
                lines.append("Gaps (what cannot be represented):")
                for gap in output.gaps:
                    lines.append(f"  * {gap}")
                lines.append("")

            # Register location
            lines.append("Register Location:")
            lines.append(
                f"  Symbolic:   {_render_bar(output.register_location.symbolic)} "
                f"{output.register_location.symbolic:.2f}"
            )
            lines.append(
                f"  Imaginary:  {_render_bar(output.register_location.imaginary)} "
                f"{output.register_location.imaginary:.2f}"
            )
            lines.append(
                f"  Real:       {_render_bar(output.register_location.real_proximity)} "
                f"{output.register_location.real_proximity:.2f}"
            )
            lines.append("")

            # Knot status
            knot_desc = {
                "stable": "Registers are properly knotted.",
                "loosening": "High imaginary content drifting from symbolic structure.",
                "unknotted": "Registers have come apart - crisis state.",
            }
            lines.append(f"Knot Status: {output.knot_status.value.upper()}")
            lines.append(f"  {knot_desc.get(output.knot_status.value, '')}")
            lines.append("")

            # Slippages
            if output.slippages:
                lines.append("Slippages (register miscategorizations):")
                for slip in output.slippages:
                    lines.append(
                        f"  * Claims {slip.claimed.value}, actually {slip.actual.value}"
                    )
                    lines.append(f"    {slip.evidence}")
                lines.append("")

            # Objet petit a
            if output.objet_petit_a:
                lines.append("Objet petit a:")
                lines.append(f'  "{output.objet_petit_a}"')
                lines.append("  This is what the system is organized around lacking.")

            _emit_output("\n".join(lines), semantic, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[GAPS] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[GAPS] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _render_bar(value: float, width: int = 10) -> str:
    """Render a progress bar for register value."""
    filled = int(value * width)
    empty = width - filled
    return "[" + "#" * filled + "." * empty + "]"


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
