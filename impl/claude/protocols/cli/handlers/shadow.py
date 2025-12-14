"""
Shadow Handler: Surface shadow content using Jungian analysis.

Uses H-gent JungAgent to analyze shadow content - what the system represses,
ignores, or exiles to maintain coherence.

Based on Jungian shadow concept:
- The shadow contains what we repress or don't acknowledge
- It's not "bad" - it's what we haven't integrated
- Integration means acknowledging and working with it

Usage:
    kgents shadow                    # Analyze kgents system identity
    kgents shadow "helpful AI"       # Analyze custom self-image
    kgents shadow --json            # Output as JSON

The shadow analysis returns:
- shadow_inventory: list of shadow content with exclusion reasons
- projections: where the system projects shadow onto others
- integration_paths: recommended paths for integration
- persona_shadow_balance: 0 = all persona, 1 = fully integrated
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
    """Print help for shadow command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --save              Save analysis to SoulSession for drift tracking")
    print("  --drift             Compare to previous saved analysis")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents shadow")
    print('  kgents shadow "I am a helpful AI assistant"')
    print("  kgents shadow --json")
    print("  kgents shadow --save          # Persist for later comparison")
    print("  kgents shadow --drift         # Show what changed since last save")
    print()
    print("ABOUT SHADOW WORK:")
    print("  The shadow isn't your enemy - it's the disowned parts of yourself.")
    print("  Acknowledging shadow content leads to integration and wholeness.")
    print("  Integration (not elimination) is the goal.")


def cmd_shadow(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Shadow analysis using H-gent JungAgent.

    Usage:
        kgents shadow [self-image] [--json] [--save] [--drift]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("shadow", args)
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

    # Extract self-image (everything that's not a flag)
    self_image_parts: list[str] = []
    for arg in args:
        if arg.startswith("-"):
            continue
        self_image_parts.append(arg)

    # Default to kgents self-image if not provided
    if not self_image_parts:
        self_image = DEFAULT_SELF_IMAGE.strip()
    else:
        self_image = " ".join(self_image_parts)

    # Run async handler
    return asyncio.run(_async_shadow(self_image, json_mode, save_mode, drift_mode, ctx))


async def _async_shadow(
    self_image: str,
    json_mode: bool,
    save_mode: bool,
    drift_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of shadow command using JungAgent."""
    try:
        from agents.h.jung import JungAgent, JungInput
        from agents.k.session import SoulSession

        # Build input for JungAgent
        input_data = JungInput(system_self_image=self_image)

        # Invoke the agent
        output = await JungAgent().invoke(input_data)

        # Build semantic output
        semantic = {
            "command": "shadow",
            "self_image": self_image,
            "shadow_inventory": [
                {
                    "content": s.content,
                    "exclusion_reason": s.exclusion_reason,
                    "difficulty": s.integration_difficulty.value,
                }
                for s in output.shadow_inventory
            ],
            "projections": [
                {
                    "shadow_content": p.shadow_content,
                    "projected_onto": p.projected_onto,
                    "evidence": p.evidence,
                }
                for p in output.projections
            ],
            "integration_paths": [
                {
                    "shadow_content": ip.shadow_content,
                    "method": ip.integration_method,
                    "risks": ip.risks,
                }
                for ip in output.integration_paths
            ],
            "balance": output.persona_shadow_balance,
        }

        # Handle drift mode - compare to previous
        drift_report = None
        if drift_mode:
            session = await SoulSession.load()
            drift_report = await session.compute_drift("shadow", semantic)

        # Handle save mode - persist to SoulSession
        if save_mode:
            session = await SoulSession.load()
            await session.record_introspection("shadow", semantic, self_image)
            semantic["saved"] = True

        if json_mode:
            if drift_report:
                semantic["drift"] = drift_report.to_dict()
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[SHADOW] Shadow Analysis",
                "",
            ]

            # Shadow inventory
            if output.shadow_inventory:
                lines.append("Shadow Inventory:")
                for shadow in output.shadow_inventory:
                    lines.append(f"  * {shadow.content}")
                    lines.append(f"    ({shadow.exclusion_reason})")
                lines.append("")

            # Projections
            if output.projections:
                lines.append("Projections:")
                for proj in output.projections:
                    lines.append(
                        f'  * Projects "{proj.shadow_content}" onto {proj.projected_onto}'
                    )
                    lines.append(f"    Evidence: {proj.evidence}")
                lines.append("")

            # Integration paths
            if output.integration_paths:
                lines.append("Integration Paths:")
                for path in output.integration_paths:
                    lines.append(f'  * "{path.shadow_content[:50]}..."')
                    lines.append(f"    -> {path.integration_method}")
                    if path.risks:
                        lines.append(f"    Risks: {', '.join(path.risks)}")
                lines.append("")

            # Balance
            balance_bar = _render_balance_bar(output.persona_shadow_balance)
            balance_desc = (
                "more persona than shadow acknowledged"
                if output.persona_shadow_balance < 0.5
                else "well integrated"
                if output.persona_shadow_balance > 0.7
                else "moderate integration"
            )
            lines.append(
                f"Balance: {balance_bar} {output.persona_shadow_balance:.2f} ({balance_desc})"
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
                        "--- Drift Report ---",
                        "No previous shadow analysis found. Use --save to create baseline.",
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
            f"[SHADOW] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[SHADOW] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _render_balance_bar(value: float, width: int = 10) -> str:
    """Render a progress bar for balance value."""
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
