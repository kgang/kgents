"""
Archetype Handler: Identify active and shadow archetypes using Jungian analysis.

Uses H-gent JungAgent's archetype identification to analyze which Jungian
archetypes are active in a system and which are in shadow.

Jungian archetypes:
- Persona: The mask we present to the world
- Shadow: What we repress or deny
- Anima/Animus: Our relationship to the other
- Self: Integrated wholeness
- Trickster: Rule-breaking creativity
- Wise Old Man: Authority and wisdom

Usage:
    kgents archetype                      # Analyze kgents system identity
    kgents archetype "I am an AI"         # Analyze custom self-image
    kgents archetype --json               # Output as JSON

The archetype analysis returns:
- Active archetypes: Currently manifesting in the system
- Shadow archetypes: Mentioned in limitations, avoided or repressed
- For each: manifestation pattern and shadow aspect
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
    """Print help for archetype command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --save              Save analysis to SoulSession for drift tracking")
    print("  --drift             Compare to previous saved analysis")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents archetype")
    print('  kgents archetype "I am a helpful AI assistant"')
    print("  kgents archetype --json")
    print("  kgents archetype --save       # Persist for later comparison")
    print("  kgents archetype --drift      # Show archetype activation changes")
    print()
    print("ABOUT ARCHETYPES:")
    print("  Archetypes are universal patterns of behavior and meaning.")
    print("  Active archetypes shape how your system presents itself.")
    print("  Shadow archetypes are avoided or repressed but still influence behavior.")


def cmd_archetype(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Archetype analysis using H-gent JungAgent.

    Usage:
        kgents archetype [self-image] [--json] [--save] [--drift]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("archetype", args)
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
    return asyncio.run(
        _async_archetype(self_image, json_mode, save_mode, drift_mode, ctx)
    )


async def _async_archetype(
    self_image: str,
    json_mode: bool,
    save_mode: bool,
    drift_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of archetype command using identify_archetypes."""
    try:
        from agents.h.jung import JungInput, identify_archetypes
        from agents.k.session import SoulSession

        # Build input for identify_archetypes
        input_data = JungInput(system_self_image=self_image)

        # Call the pure function
        archetypes = identify_archetypes(input_data)

        # Separate active and shadow archetypes
        active = [a for a in archetypes if a.is_active and not a.is_shadow]
        shadow = [a for a in archetypes if a.is_shadow]
        both = [a for a in archetypes if a.is_active and a.is_shadow]

        # Build semantic output
        semantic: dict[str, Any] = {
            "command": "archetype",
            "self_image": self_image,
            "active_archetypes": [
                {
                    "archetype": a.archetype.value,
                    "manifestation": a.manifestation,
                    "shadow_aspect": a.shadow_aspect,
                }
                for a in active
            ],
            "shadow_archetypes": [
                {
                    "archetype": a.archetype.value,
                    "manifestation": a.manifestation,
                    "shadow_aspect": a.shadow_aspect,
                }
                for a in shadow
            ],
            "active_and_shadow": [
                {
                    "archetype": a.archetype.value,
                    "manifestation": a.manifestation,
                    "shadow_aspect": a.shadow_aspect,
                }
                for a in both
            ],
            "total_detected": len(archetypes),
        }

        # Handle drift mode - compare to previous
        drift_report = None
        if drift_mode:
            session = await SoulSession.load()
            drift_report = await session.compute_drift("archetype", semantic)

        # Handle save mode - persist to SoulSession
        if save_mode:
            session = await SoulSession.load()
            await session.record_introspection("archetype", semantic, self_image)
            semantic["saved"] = True

        if json_mode:
            if drift_report:
                semantic["drift"] = drift_report.to_dict()
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[ARCHETYPE] Jungian Archetype Analysis",
                "",
            ]

            # Active archetypes
            if active:
                lines.append("Active Archetypes:")
                for arch in active:
                    lines.append(f"  * {arch.archetype.value.upper()}")
                    lines.append(f"    Manifests as: {arch.manifestation}")
                    lines.append(f"    Shadow risk: {arch.shadow_aspect}")
                lines.append("")

            # Archetypes in both active and shadow (tension)
            if both:
                lines.append("Archetypes in Tension (both active and shadow):")
                for arch in both:
                    lines.append(f"  * {arch.archetype.value.upper()}")
                    lines.append(f"    Active in: {arch.manifestation}")
                    lines.append(f"    Yet avoided: {arch.shadow_aspect}")
                lines.append("")

            # Shadow archetypes
            if shadow:
                lines.append("Shadow Archetypes (avoided/repressed):")
                for arch in shadow:
                    lines.append(f"  * {arch.archetype.value.upper()}")
                    lines.append(f"    Would manifest as: {arch.manifestation}")
                    lines.append(f"    Currently: {arch.shadow_aspect}")
                lines.append("")

            # Summary
            if not archetypes:
                lines.append("No archetypes detected in the self-image.")
                lines.append("Try adding descriptive terms about identity/behavior.")
            else:
                lines.append(
                    f"Total: {len(active)} active, {len(shadow)} shadow, {len(both)} in tension"
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
                    lines.append("Newly activated archetypes:")
                    for item in drift_report.added:
                        lines.append(f"  + {item}")
                if drift_report.removed:
                    lines.append("Deactivated archetypes:")
                    for item in drift_report.removed:
                        lines.append(f"  - {item}")
                if drift_report.changed:
                    lines.append("Archetypes shifted:")
                    for item, old, new in drift_report.changed:
                        lines.append(f"  ~ {item}: {old} -> {new}")
                lines.append(f"Stability: {drift_report.stability_score:.2f}")
            elif drift_mode:
                lines.extend(
                    [
                        "",
                        "--- Drift Report ---",
                        "No previous archetype analysis found. Use --save to create baseline.",
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
            f"[ARCHETYPE] X H-gent module not available: {e}",
            {"error": f"H-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[ARCHETYPE] X Error: {e}",
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
