"""
Mirror Handler: Full introspection combining all three H-gents.

Uses JungAgent, HegelAgent, and LacanAgent together for comprehensive
self-analysis of the system.

The mirror shows:
- Shadow (Jung): What the system represses
- Dialectic (Hegel): Current tensions in the system
- Gaps (Lacan): What cannot be represented

Usage:
    kgents mirror                    # Full introspection of kgents
    kgents mirror "helpful AI"       # Introspect custom self-image
    kgents mirror --json            # Output as JSON

The shadow, the tension, and the gap meet:
Your system's shadow is [X], held in tension with [Y],
pointing toward the gap of [Z].
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Default self-image for kgents system
DEFAULT_SELF_IMAGE = """
kgents: A specification for tasteful, curated, ethical, joy-inducing agents.
Helpful but not servile. Accurate but acknowledging limits.
Safe but not neutered. Composable but not fragmented.
"""


def _print_help() -> None:
    """Print help for mirror command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --save              Save analysis to SoulSession for drift tracking")
    print("  --drift             Compare to previous saved analysis")
    print("  --history           Show introspection timeline")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents mirror")
    print('  kgents mirror "I am a helpful AI"')
    print("  kgents mirror --json")
    print("  kgents mirror --save           # Persist for later comparison")
    print("  kgents mirror --drift          # Show what changed since last save")
    print("  kgents mirror --history        # Show introspection timeline")
    print()
    print("ABOUT THE MIRROR:")
    print("  The mirror doesn't just reflect - it reveals.")
    print("  Three windows into what the system cannot say about itself.")
    print("  Shadow, tension, and gap together form a complete picture.")


def cmd_mirror(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Full introspection using all three H-gents.

    Usage:
        kgents mirror [self-image] [--json] [--save] [--drift] [--history]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("mirror", args)
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
    history_mode = "--history" in args

    # Extract self-image (everything that's not a flag)
    self_image_parts: list[str] = []
    for arg in args:
        if arg.startswith("-"):
            continue
        self_image_parts.append(arg)

    # Default if not provided
    if not self_image_parts:
        self_image = DEFAULT_SELF_IMAGE.strip()
    else:
        self_image = " ".join(self_image_parts)

    # Run async handler
    return asyncio.run(
        _async_mirror(self_image, json_mode, save_mode, drift_mode, history_mode, ctx)
    )


async def _async_mirror(
    self_image: str,
    json_mode: bool,
    save_mode: bool,
    drift_mode: bool,
    history_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of mirror command using all H-gents."""
    try:
        from agents.h.hegel import DialecticInput, HegelAgent
        from agents.h.jung import JungAgent, JungInput
        from agents.h.lacan import LacanAgent, LacanError, LacanInput, LacanOutput
        from agents.k.session import SoulSession

        # Handle history mode - just show timeline, no analysis
        if history_mode:
            session = await SoulSession.load()
            history = await session.get_introspection_history("mirror", limit=10)

            if json_mode:
                history_semantic: dict[str, Any] = {
                    "command": "mirror",
                    "mode": "history",
                    "records": [r.to_dict() for r in history],
                }
                _emit_output(
                    json.dumps(history_semantic, indent=2), history_semantic, ctx
                )
            else:
                lines = [
                    "[MIRROR] Introspection Timeline",
                    "",
                ]
                if not history:
                    lines.append("No introspection history found.")
                    lines.append("Use 'kgents mirror --save' to start tracking.")
                else:
                    for record in history:
                        timestamp = record.created_at.strftime("%Y-%m-%d %H:%M")
                        balance = record.data.get("shadow", {}).get("balance", "?")
                        shadow_count = len(
                            record.data.get("shadow", {}).get("inventory", [])
                        )
                        lines.append(
                            f"  [{timestamp}] balance={balance:.2f}, shadows={shadow_count}"
                        )
                        if record.tags:
                            lines.append(f"    tags: {', '.join(record.tags)}")
                    lines.extend(
                        [
                            "",
                            f"Total records: {len(history)}",
                        ]
                    )
                _emit_output(
                    "\n".join(lines), {"records": [r.to_dict() for r in history]}, ctx
                )
            return 0

        # Run all three agents concurrently
        jung_input = JungInput(system_self_image=self_image)
        lacan_input = LacanInput(output=self_image)

        # For Hegel, we'll create a dialectic from the first shadow content found
        # Or use a default tension if no shadow found
        jung_output, lacan_result = await asyncio.gather(
            JungAgent().invoke(jung_input),
            LacanAgent().invoke(lacan_input),
        )

        # Now run Hegel with discovered tension
        if jung_output.shadow_inventory:
            # Use first shadow as thesis, persona as antithesis
            thesis = jung_output.shadow_inventory[0].content
            antithesis = "presented identity: " + self_image[:50]
        else:
            # Default tension
            thesis = "self-knowledge"
            antithesis = "self-presentation"

        hegel_input = DialecticInput(thesis=thesis, antithesis=antithesis)
        hegel_output = await HegelAgent().invoke(hegel_input)

        # Handle Lacan result
        lacan_output: LacanOutput | None = None
        lacan_error: LacanError | None = None
        if isinstance(lacan_result, LacanError):
            lacan_error = lacan_result
        else:
            lacan_output = lacan_result

        # Build semantic output
        semantic: dict[str, Any] = {
            "command": "mirror",
            "self_image": self_image,
            "shadow": {
                "inventory": [
                    {"content": s.content, "reason": s.exclusion_reason}
                    for s in jung_output.shadow_inventory
                ],
                "projections": [
                    {"onto": p.projected_onto, "content": p.shadow_content}
                    for p in jung_output.projections
                ],
                "balance": jung_output.persona_shadow_balance,
            },
            "dialectic": {
                "thesis": thesis,
                "antithesis": antithesis,
                "synthesis": hegel_output.synthesis,
                "productive_tension": hegel_output.productive_tension,
                "notes": hegel_output.sublation_notes,
            },
            "gaps": None,
        }

        if lacan_output:
            semantic["gaps"] = {
                "gaps": lacan_output.gaps,
                "knot_status": lacan_output.knot_status.value,
                "objet_petit_a": lacan_output.objet_petit_a,
            }
        elif lacan_error:
            semantic["gaps"] = {"error": lacan_error.message}

        # Handle drift mode - compare to previous
        drift_report = None
        if drift_mode:
            session = await SoulSession.load()
            drift_report = await session.compute_drift("mirror", semantic)

        # Handle save mode - persist to SoulSession
        if save_mode:
            session = await SoulSession.load()
            await session.record_introspection("mirror", semantic, self_image)
            semantic["saved"] = True

        if json_mode:
            if drift_report:
                semantic["drift"] = drift_report.to_dict()
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[MIRROR] Full Introspection",
                "",
                "=" * 40,
                " Shadow (Jung)",
                "=" * 40,
                "",
            ]

            # Shadow section
            if jung_output.shadow_inventory:
                for shadow in jung_output.shadow_inventory[:3]:
                    lines.append(f"  * {shadow.content}")
                    lines.append(f"    ({shadow.exclusion_reason})")
            else:
                lines.append("  No shadow content detected.")
            lines.extend(
                [
                    "",
                    f"  Balance: {jung_output.persona_shadow_balance:.2f}",
                    "",
                    "=" * 40,
                    " Dialectic (Hegel)",
                    "=" * 40,
                    "",
                ]
            )

            # Dialectic section
            lines.append(f"  Thesis: {thesis}")
            lines.append(f"  Antithesis: {antithesis}")
            if hegel_output.productive_tension:
                lines.append("  [Tension held - no synthesis forced]")
            else:
                lines.append(f"  Synthesis: {hegel_output.synthesis}")
            lines.append(f"  {hegel_output.sublation_notes}")
            lines.extend(
                [
                    "",
                    "=" * 40,
                    " Gaps (Lacan)",
                    "=" * 40,
                    "",
                ]
            )

            # Gaps section
            if lacan_output:
                if lacan_output.gaps:
                    for gap in lacan_output.gaps[:3]:
                        lines.append(f"  * {gap}")
                lines.extend(
                    [
                        "",
                        f"  Knot Status: {lacan_output.knot_status.value}",
                    ]
                )
                if lacan_output.objet_petit_a:
                    lines.append(f'  Objet petit a: "{lacan_output.objet_petit_a}"')
            elif lacan_error:
                lines.append(f"  [Error: {lacan_error.message}]")
            else:
                lines.append("  [No gaps analysis available]")

            # Integration summary
            lines.extend(
                [
                    "",
                    "=" * 40,
                    " Integration",
                    "=" * 40,
                    "",
                    "The shadow, the tension, and the gap meet:",
                ]
            )

            # Generate integration insight
            shadow_summary = (
                jung_output.shadow_inventory[0].content[:40] + "..."
                if jung_output.shadow_inventory
                else "no detected shadow"
            )
            tension_summary = (
                "productive tension"
                if hegel_output.productive_tension
                else str(hegel_output.synthesis)[:40]
                if hegel_output.synthesis
                else "resolved"
            )
            gap_summary = (
                lacan_output.objet_petit_a or lacan_output.gaps[0][:40]
                if lacan_output and (lacan_output.objet_petit_a or lacan_output.gaps)
                else "unknown lack"
            )

            lines.extend(
                [
                    f"  Your system's shadow is [{shadow_summary}],",
                    f"  held in tension with [{tension_summary}],",
                    f"  pointing toward the gap of [{gap_summary}].",
                ]
            )

            # Drift report
            if drift_report:
                lines.extend(
                    [
                        "",
                        "=" * 40,
                        " Drift Report",
                        "=" * 40,
                        "",
                        f"Since: {drift_report.previous_timestamp.strftime('%Y-%m-%d %H:%M')}",
                        "",
                    ]
                )
                if drift_report.added:
                    lines.append("New shadows emerged:")
                    for item in drift_report.added[:3]:
                        lines.append(f"  + {item[:60]}...")
                if drift_report.removed:
                    lines.append("Shadows integrated/resolved:")
                    for item in drift_report.removed[:3]:
                        lines.append(f"  - {item[:60]}...")
                if drift_report.integration_delta != 0:
                    direction = (
                        "improved"
                        if drift_report.integration_delta > 0
                        else "decreased"
                    )
                    lines.append(
                        f"Integration {direction} by {abs(drift_report.integration_delta):.2f}"
                    )
                lines.append(f"Stability: {drift_report.stability_score:.2f}")
            elif drift_mode:
                lines.extend(
                    [
                        "",
                        "=" * 40,
                        " Drift Report",
                        "=" * 40,
                        "",
                        "No previous mirror analysis found. Use --save to create baseline.",
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
            f"[MIRROR] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[MIRROR] X Error: {e}",
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
