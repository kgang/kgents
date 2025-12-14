"""
Dialectic Handler: Hegelian synthesis of opposing concepts.

Uses H-gent HegelAgent for dialectical synthesis:
thesis + antithesis → synthesis (aufheben)

Aufheben means:
1. To preserve (what's essential from both)
2. To negate (what's contradictory)
3. To elevate (to a higher level of understanding)

Usage:
    kgents dialectic "move fast" "be thorough"
    kgents dialectic "freedom"           # Surfaces antithesis automatically
    kgents dialectic "speed" "quality" --json

The dialectic returns:
- synthesis: The unified insight (or None if tension held)
- productive_tension: Whether synthesis is premature
- sublation_notes: What was preserved, negated, elevated
- lineage: Full chain of dialectic steps
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for dialectic command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --save              Save analysis to SoulSession for drift tracking")
    print("  --drift             Compare to previous saved analysis")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents dialectic "move fast" "be thorough"')
    print('  kgents dialectic "freedom"')
    print('  kgents dialectic "abstract" "concrete" --json')
    print('  kgents dialectic "speed" "quality" --save   # Persist for later')
    print('  kgents dialectic "speed" "quality" --drift  # Show what changed')
    print()
    print("ABOUT DIALECTICS:")
    print("  Dialectic doesn't compromise - it synthesizes.")
    print("  If only thesis provided, antithesis is surfaced automatically.")
    print("  Some tensions are productive - they shouldn't be resolved.")


def cmd_dialectic(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Dialectic synthesis using H-gent HegelAgent.

    Usage:
        kgents dialectic "thesis" ["antithesis"] [--json] [--save] [--drift]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("dialectic", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    save_mode = "--save" in args
    drift_mode = "--drift" in args

    # Extract concepts (everything that's not a flag)
    concepts: list[str] = []
    for arg in args:
        if arg.startswith("-"):
            continue
        concepts.append(arg)

    if len(concepts) < 1:
        _emit_output(
            "[DIALECTIC] X Error: Need at least one concept for dialectic\n"
            'Usage: kgents dialectic "thesis" ["antithesis"]',
            {"error": "Need at least one concept"},
            ctx,
        )
        return 1

    thesis = concepts[0]
    antithesis = concepts[1] if len(concepts) > 1 else None

    # Run async handler
    return asyncio.run(
        _async_dialectic(thesis, antithesis, json_mode, save_mode, drift_mode, ctx)
    )


async def _async_dialectic(
    thesis: str,
    antithesis: str | None,
    json_mode: bool,
    save_mode: bool,
    drift_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of dialectic command using HegelAgent."""
    try:
        from agents.h.hegel import DialecticInput, HegelAgent
        from agents.k.session import SoulSession

        # Build input for HegelAgent
        input_data = DialecticInput(thesis=thesis, antithesis=antithesis)

        # Invoke the agent
        output = await HegelAgent().invoke(input_data)

        # Build semantic output
        semantic: dict[str, Any] = {
            "command": "dialectic",
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": output.synthesis,
            "sublation_notes": output.sublation_notes,
            "productive_tension": output.productive_tension,
            "lineage": [
                {
                    "stage": step.stage,
                    "thesis": str(step.thesis),
                    "antithesis": str(step.antithesis) if step.antithesis else None,
                    "result": str(step.result) if step.result else None,
                    "notes": step.notes,
                }
                for step in output.lineage
            ],
        }

        # Add tension info if present
        if output.tension:
            semantic["tension"] = {
                "mode": output.tension.mode.value,
                "severity": output.tension.severity,
                "description": output.tension.description,
            }
            # Also store the surfaced antithesis for drift tracking
            if output.tension.antithesis:
                semantic["antithesis"] = output.tension.antithesis

        # Handle drift mode - compare to previous
        drift_report = None
        if drift_mode:
            session = await SoulSession.load()
            drift_report = await session.compute_drift("dialectic", semantic)

        # Handle save mode - persist to SoulSession
        if save_mode:
            session = await SoulSession.load()
            self_image = f"{thesis} vs {antithesis}" if antithesis else thesis
            await session.record_introspection("dialectic", semantic, self_image)
            semantic["saved"] = True

        if json_mode:
            if drift_report:
                semantic["drift"] = drift_report.to_dict()
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = []

            if output.productive_tension:
                # Tension held - no synthesis
                lines.extend(
                    [
                        "[DIALECTIC] Tension Held",
                        "",
                        f"Thesis: {thesis}",
                    ]
                )
                if output.tension:
                    lines.append(f"Antithesis: {output.tension.antithesis}")
                elif antithesis:
                    lines.append(f"Antithesis: {antithesis}")
                lines.extend(
                    [
                        "",
                        "Holding Productive Tension:",
                        f"  {output.sublation_notes}",
                        "",
                        "  These values cannot be fully synthesized without loss.",
                        "  The tension itself is generative.",
                        "",
                        "  Live with both. Navigate case by case.",
                    ]
                )
            else:
                # Synthesis achieved
                lines.extend(
                    [
                        "[DIALECTIC] Synthesis",
                        "",
                        f"Thesis: {thesis}",
                    ]
                )
                if output.tension:
                    lines.append(f"Antithesis: {output.tension.antithesis}")
                elif antithesis:
                    lines.append(f"Antithesis: {antithesis}")
                lines.extend(
                    [
                        "",
                        f"Synthesis: {output.synthesis}",
                        f"  {output.sublation_notes}",
                        "",
                    ]
                )

                # Show lineage if interesting
                if output.lineage:
                    lines.append("Lineage:")
                    for step in output.lineage[:3]:  # Show max 3 steps
                        lines.append(f"  [{step.stage}] {step.notes[:60]}...")

                if output.next_thesis:
                    lines.extend(
                        [
                            "",
                            "(This synthesis becomes the new thesis for further dialectic)",
                        ]
                    )

            # Drift report
            if drift_report:
                lines.extend(
                    [
                        "",
                        "--- Drift Report ---",
                        f"Since: {drift_report.previous_timestamp.strftime('%Y-%m-%d %H:%M')}",
                        "",
                    ]
                )
                if drift_report.added:
                    lines.append("New developments:")
                    for item in drift_report.added[:3]:
                        lines.append(f"  + {item[:60]}...")
                if drift_report.removed:
                    lines.append("Resolved/abandoned:")
                    for item in drift_report.removed[:3]:
                        lines.append(f"  - {item[:60]}...")
                if drift_report.changed:
                    lines.append("Dialectic shifts:")
                    for item, old_val, new_val in drift_report.changed[:3]:
                        old_display = old_val[:20] if len(old_val) > 20 else old_val
                        new_display = new_val[:20] if len(new_val) > 20 else new_val
                        lines.append(f"  ~ {item}: {old_display} -> {new_display}")
                lines.append(f"Stability: {drift_report.stability_score:.2f}")
            elif drift_mode:
                lines.extend(
                    [
                        "",
                        "--- Drift Report ---",
                        "No previous dialectic analysis found. Use --save to create baseline.",
                    ]
                )

            # Save confirmation
            if save_mode:
                lines.extend(
                    [
                        "",
                        "[Saved to SoulSession for drift tracking]",
                    ]
                )

            _emit_output("\n".join(lines), semantic, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[DIALECTIC] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[DIALECTIC] X Error: {e}",
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
