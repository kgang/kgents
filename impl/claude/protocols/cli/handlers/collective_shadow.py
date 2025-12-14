"""
Collective Shadow Handler: System-level shadow from agent composition.

Uses H-gent CollectiveShadowAgent to analyze what emerges from the
combination of multiple agents - shadow that no individual agent owns.

This goes beyond individual shadow analysis:
- What the entire system excludes (not just one agent)
- Shadow that emerges from agent composition
- System-level projections onto external entities

Usage:
    kgents collective-shadow                          # Analyze kgents ecosystem
    kgents collective-shadow --agents "A,B,C"         # Specify agent personas
    kgents collective-shadow --behaviors "X,Y"        # Specify emergent behaviors
    kgents collective-shadow --json                   # Output as JSON

The collective shadow analysis returns:
- collective_persona: System self-description
- shadow_inventory: System-level shadow content
- system_level_projections: Where the system projects shadow
- emergent_shadow_content: Shadow emerging from composition
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Default kgents ecosystem description
DEFAULT_SYSTEM_DESCRIPTION = """
kgents: A specification for tasteful, curated, ethical, joy-inducing agents.
Safe, composable, and designed to augment human judgment.
"""

DEFAULT_AGENT_PERSONAS = [
    "A-gent: Universal alethic agent with dynamic persona",
    "K-gent: Kent simulacra for self-dialogue",
    "H-gent: Introspection agents (Jung, Hegel, Lacan)",
    "I-gent: Visualization and reactive primitives",
    "D-gent: Data and memory management",
    "E-gent: Evolutionary and teleological agents",
]

DEFAULT_EMERGENT_BEHAVIORS = [
    "Cross-agent composition creating emergent properties",
    "Reflexive introspection (agents analyzing agents)",
    "Autonomous decision-making with human oversight",
]


def _print_help() -> None:
    """Print help for collective-shadow command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --agents <list>     Comma-separated agent personas")
    print("  --behaviors <list>  Comma-separated emergent behaviors")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents collective-shadow")
    print('  kgents collective-shadow --agents "Agent A,Agent B"')
    print('  kgents collective-shadow --behaviors "Composition,Self-reference"')
    print("  kgents collective-shadow --json")
    print()
    print("ABOUT COLLECTIVE SHADOW:")
    print("  Individual agents have individual shadow.")
    print("  But agent systems have emergent shadow that no component owns.")
    print("  This shadow arises from the spaces between agents,")
    print("  from what the composition itself excludes or denies.")


def cmd_collective_shadow(
    args: list[str], ctx: "InvocationContext | None" = None
) -> int:
    """
    Collective shadow analysis using H-gent CollectiveShadowAgent.

    Usage:
        kgents collective-shadow [--agents <list>] [--behaviors <list>] [--json]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("collective-shadow", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    agent_personas = DEFAULT_AGENT_PERSONAS.copy()
    emergent_behaviors = DEFAULT_EMERGENT_BEHAVIORS.copy()

    # Parse --agents and --behaviors flags
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == "--agents" and i + 1 < len(args):
            agent_personas = [p.strip() for p in args[i + 1].split(",")]
            skip_next = True
        elif arg.startswith("--agents="):
            agent_personas = [p.strip() for p in arg.split("=", 1)[1].split(",")]
        elif arg == "--behaviors" and i + 1 < len(args):
            emergent_behaviors = [b.strip() for b in args[i + 1].split(",")]
            skip_next = True
        elif arg.startswith("--behaviors="):
            emergent_behaviors = [b.strip() for b in arg.split("=", 1)[1].split(",")]

    # Run async handler
    return asyncio.run(
        _async_collective_shadow(
            DEFAULT_SYSTEM_DESCRIPTION.strip(),
            agent_personas,
            emergent_behaviors,
            json_mode,
            ctx,
        )
    )


async def _async_collective_shadow(
    system_description: str,
    agent_personas: list[str],
    emergent_behaviors: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of collective-shadow command using CollectiveShadowAgent."""
    try:
        from agents.h.jung import CollectiveShadowAgent, CollectiveShadowInput

        # Build input for CollectiveShadowAgent
        input_data = CollectiveShadowInput(
            system_description=system_description,
            agent_personas=agent_personas,
            emergent_behaviors=emergent_behaviors,
        )

        # Invoke the agent
        output = await CollectiveShadowAgent().invoke(input_data)

        # Build semantic output
        semantic: dict[str, Any] = {
            "command": "collective-shadow",
            "system_description": system_description,
            "agent_personas": agent_personas,
            "emergent_behaviors": emergent_behaviors,
            "collective_persona": output.collective_persona,
            "shadow_inventory": [
                {
                    "content": s.content,
                    "exclusion_reason": s.exclusion_reason,
                    "difficulty": s.integration_difficulty.value,
                }
                for s in output.shadow_inventory
            ],
            "system_level_projections": [
                {
                    "shadow_content": p.shadow_content,
                    "projected_onto": p.projected_onto,
                    "evidence": p.evidence,
                }
                for p in output.system_level_projections
            ],
            "emergent_shadow_content": output.emergent_shadow_content,
        }

        if json_mode:
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[COLLECTIVE-SHADOW] System-Level Shadow Analysis",
                "",
            ]

            # Agent personas analyzed
            lines.append(f"Agents Analyzed: {len(agent_personas)}")
            for persona in agent_personas[:5]:  # Show max 5
                lines.append(f"  * {persona}")
            if len(agent_personas) > 5:
                lines.append(f"  ... and {len(agent_personas) - 5} more")
            lines.append("")

            # Shadow inventory
            if output.shadow_inventory:
                lines.append("System Shadow Inventory:")
                for shadow in output.shadow_inventory:
                    lines.append(f"  * {shadow.content}")
                    lines.append(f"    ({shadow.exclusion_reason})")
                    lines.append(
                        f"    Difficulty: {shadow.integration_difficulty.value}"
                    )
                lines.append("")

            # System-level projections
            if output.system_level_projections:
                lines.append("System-Level Projections:")
                for proj in output.system_level_projections:
                    lines.append(f'  * Projects "{proj.shadow_content[:40]}..."')
                    lines.append(f"    onto: {proj.projected_onto}")
                    lines.append(f"    Evidence: {proj.evidence}")
                lines.append("")

            # Emergent shadow content
            if output.emergent_shadow_content:
                lines.append("Emergent Shadow (from composition):")
                for emergent in output.emergent_shadow_content:
                    lines.append(f"  * {emergent}")
                lines.append("")

            # Summary
            lines.append("=" * 40)
            lines.append("Summary:")
            lines.append(f"  System shadows: {len(output.shadow_inventory)}")
            lines.append(f"  Projections: {len(output.system_level_projections)}")
            lines.append(f"  Emergent shadow: {len(output.emergent_shadow_content)}")
            lines.append("")
            lines.append("The collective shadow is what emerges between agents,")
            lines.append("not owned by any single component but by the whole.")

            _emit_output("\n".join(lines), semantic, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[COLLECTIVE-SHADOW] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[COLLECTIVE-SHADOW] X Error: {e}",
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
