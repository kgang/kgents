"""
Tend Command Handler: Apply tending gestures to the garden.

The tending calculus provides six primitive gestures for gardener-world interaction:
- OBSERVE: Perceive without changing
- PRUNE: Remove what no longer serves
- GRAFT: Add something new
- WATER: Nurture via TextGRAD
- ROTATE: Change perspective
- WAIT: Allow time to pass

Usage:
    kg tend observe <target>           Observe without changing
    kg tend prune <target> --reason    Mark for removal
    kg tend graft <target> --reason    Add new element
    kg tend water <target> --feedback  Nurture via TextGRAD
    kg tend rotate <target>            Change perspective
    kg tend wait                       Intentional pause

Example:
    kg tend observe concept.gardener
    kg tend water concept.prompt.task.review --feedback "Add more specificity"
    kg tend prune concept.prompt.old --reason "No longer used"
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for tend command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS (the six tending verbs):")
    print("  observe <target>   Perceive without changing (nearly free)")
    print("  prune <target>     Mark for removal (moderate cost)")
    print("  graft <target>     Add new element (creative, expensive)")
    print("  water <target>     Nurture via TextGRAD (moderate cost)")
    print("  rotate <target>    Change perspective (cheap)")
    print("  wait               Intentional pause (free)")
    print()
    print("OPTIONS:")
    print("  --reason <text>    Reasoning for prune/graft gestures")
    print("  --feedback <text>  Feedback for water gesture (TextGRAD)")
    print("  --tone <0.0-1.0>   How definitive (default: 0.5)")
    print("  --observer <name>  Observer archetype")
    print("  --json             Output as JSON")
    print("  --help, -h         Show this help")


# =============================================================================
# AGENTESE Thin Routing (Wave 2.5)
# =============================================================================

# Verb -> AGENTESE path mapping
TEND_VERB_MAP: dict[str, str] = {
    "observe": "self.garden.tend.observe",
    "prune": "self.garden.tend.prune",
    "graft": "self.garden.tend.graft",
    "water": "self.garden.tend.water",
    "rotate": "self.garden.tend.rotate",
    "wait": "self.garden.tend.wait",
}


def cmd_tend(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the tend command.

    Wave 2.5: Routes to self.garden.tend.* AGENTESE paths via thin routing.

    Args:
        args: Command-line arguments (after the command name)
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("tend", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Parse named arguments
    reason = _extract_arg(args, "--reason")
    feedback = _extract_arg(args, "--feedback")
    tone_str = _extract_arg(args, "--tone")
    observer = _extract_arg(args, "--observer") or "default"

    tone = 0.5
    if tone_str:
        try:
            tone = float(tone_str)
            tone = max(0.0, min(1.0, tone))  # Clamp to 0-1
        except ValueError:
            pass

    # Get subcommand (verb)
    verb = None
    target = None

    for arg in args:
        if arg.startswith("-"):
            continue
        if verb is None:
            verb = arg.lower()
        elif target is None:
            target = arg

    # No verb given
    if verb is None:
        _print_help()
        return 0

    # Try thin routing to AGENTESE path (Wave 2.5)
    if verb in TEND_VERB_MAP and json_mode:
        from protocols.cli.projection import project_command

        path = TEND_VERB_MAP[verb]
        kwargs: dict[str, Any] = {"json_output": True}

        if target:
            kwargs["target"] = target
        if reason:
            kwargs["reason"] = reason
        if feedback:
            kwargs["feedback"] = feedback
        kwargs["tone"] = tone

        try:
            return project_command(path=path, args=list(args), ctx=ctx, kwargs=kwargs)
        except Exception:
            pass  # Fall through to legacy handlers

    # Run async handler (legacy Rich output)
    return asyncio.run(
        _async_tend(
            verb=verb,
            target=target,
            reason=reason or feedback or "",
            tone=tone,
            observer=observer,
            json_mode=json_mode,
            ctx=ctx,
        )
    )


async def _async_tend(
    verb: str,
    target: str | None,
    reason: str,
    tone: float,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of tend command."""
    try:
        # Validate verb
        valid_verbs = {"observe", "prune", "graft", "water", "rotate", "wait"}
        if verb not in valid_verbs:
            _emit_output(
                f"[TEND] Unknown verb: {verb}. Valid: {', '.join(valid_verbs)}",
                {"error": f"Unknown verb: {verb}", "valid": list(valid_verbs)},
                ctx,
            )
            return 1

        # Wait doesn't need a target
        if verb != "wait" and not target:
            _emit_output(
                f"[TEND] {verb} requires a target. Usage: kg tend {verb} <target>",
                {"error": f"{verb} requires a target"},
                ctx,
            )
            return 1

        # Default target for wait
        if verb == "wait":
            target = ""

        # At this point, target is guaranteed to be str (validated above or defaulted)
        assert target is not None

        match verb:
            case "observe":
                return await _handle_observe(target, observer, json_mode, ctx)
            case "prune":
                return await _handle_prune(target, reason, tone, observer, json_mode, ctx)
            case "graft":
                return await _handle_graft(target, reason, tone, observer, json_mode, ctx)
            case "water":
                return await _handle_water(target, reason, tone, observer, json_mode, ctx)
            case "rotate":
                return await _handle_rotate(target, reason, observer, json_mode, ctx)
            case "wait":
                return await _handle_wait(reason, json_mode, ctx)
            case _:
                # Should never reach here due to validation above
                return 1

    except ImportError as e:
        _emit_output(
            f"[TEND] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TEND] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _handle_observe(
    target: str,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle OBSERVE gesture - perceive without changing."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, observe

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = observe(target, f"Observing {target}")
    gesture = gesture.__class__(
        verb=gesture.verb,
        target=gesture.target,
        tone=gesture.tone,
        reasoning=gesture.reasoning,
        entropy_cost=gesture.entropy_cost,
        observer=observer,
    )

    result = await apply_gesture(garden, gesture)

    output = {
        "verb": "observe",
        "target": target,
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "observations": list(result.reasoning_trace),
        "entropy_cost": gesture.entropy_cost,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        lines = [
            "",
            f"  {emoji} OBSERVE: {target}",
            "",
        ]
        for obs in result.reasoning_trace:
            lines.append(f"    {obs}")
        lines.append("")
        lines.append(f"  Entropy cost: {gesture.entropy_cost:.3f}")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0 if result.success else 1


async def _handle_prune(
    target: str,
    reason: str,
    tone: float,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle PRUNE gesture - mark for removal."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, prune

    if not reason:
        _emit_output(
            "[TEND] prune requires --reason. Usage: kg tend prune <target> --reason 'why'",
            {"error": "prune requires --reason"},
            ctx,
        )
        return 1

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = prune(target, reason, tone)
    gesture = gesture.__class__(
        verb=gesture.verb,
        target=gesture.target,
        tone=gesture.tone,
        reasoning=gesture.reasoning,
        entropy_cost=gesture.entropy_cost,
        observer=observer,
    )

    result = await apply_gesture(garden, gesture)

    output = {
        "verb": "prune",
        "target": target,
        "reason": reason,
        "tone": tone,
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "changes": result.changes,
        "reasoning": list(result.reasoning_trace),
        "entropy_cost": gesture.entropy_cost,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        status = "Accepted" if result.accepted else "Rejected"
        lines = [
            "",
            f"  {emoji} PRUNE: {target}",
            "",
            f"  Reason: {reason}",
            f"  Tone:   {tone:.0%} (definitiveness)",
            f"  Status: {status}",
            "",
        ]
        for trace in result.reasoning_trace:
            lines.append(f"    {trace}")
        if result.changes:
            lines.append("")
            lines.append("  Changes:")
            for change in result.changes:
                lines.append(f"    - {change}")
        lines.append("")
        lines.append(f"  Entropy cost: {gesture.entropy_cost:.3f}")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0 if result.success else 1


async def _handle_graft(
    target: str,
    reason: str,
    tone: float,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle GRAFT gesture - add something new."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, graft

    if not reason:
        _emit_output(
            "[TEND] graft requires --reason. Usage: kg tend graft <target> --reason 'what to add'",
            {"error": "graft requires --reason"},
            ctx,
        )
        return 1

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = graft(target, reason, tone)
    gesture = gesture.__class__(
        verb=gesture.verb,
        target=gesture.target,
        tone=gesture.tone,
        reasoning=gesture.reasoning,
        entropy_cost=gesture.entropy_cost,
        observer=observer,
    )

    result = await apply_gesture(garden, gesture)

    output = {
        "verb": "graft",
        "target": target,
        "reason": reason,
        "tone": tone,
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "changes": result.changes,
        "reasoning": list(result.reasoning_trace),
        "entropy_cost": gesture.entropy_cost,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        status = "Accepted" if result.accepted else "Rejected"
        lines = [
            "",
            f"  {emoji} GRAFT: {target}",
            "",
            f"  Addition: {reason}",
            f"  Tone:     {tone:.0%} (definitiveness)",
            f"  Status:   {status}",
            "",
        ]
        for trace in result.reasoning_trace:
            lines.append(f"    {trace}")
        if result.changes:
            lines.append("")
            lines.append("  Changes:")
            for change in result.changes:
                lines.append(f"    - {change}")
        lines.append("")
        lines.append(f"  Entropy cost: {gesture.entropy_cost:.3f}")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0 if result.success else 1


async def _handle_water(
    target: str,
    feedback: str,
    tone: float,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle WATER gesture - nurture via TextGRAD."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, water

    if not feedback:
        _emit_output(
            "[TEND] water requires --feedback. Usage: kg tend water <target> --feedback 'improvement'",
            {"error": "water requires --feedback"},
            ctx,
        )
        return 1

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = water(target, feedback, tone)
    gesture = gesture.__class__(
        verb=gesture.verb,
        target=gesture.target,
        tone=gesture.tone,
        reasoning=gesture.reasoning,
        entropy_cost=gesture.entropy_cost,
        observer=observer,
    )

    result = await apply_gesture(garden, gesture)

    # Calculate effective learning rate
    learning_rate = tone * garden.season.plasticity

    output = {
        "verb": "water",
        "target": target,
        "feedback": feedback,
        "tone": tone,
        "learning_rate": learning_rate,
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "changes": result.changes,
        "synergies_triggered": result.synergies_triggered,
        "reasoning": list(result.reasoning_trace),
        "entropy_cost": gesture.entropy_cost,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        status = "Applied" if result.accepted else "Rejected"
        lines = [
            "",
            f"  {emoji} WATER: {target}",
            "",
            f"  Feedback:      {feedback}",
            f"  Tone:          {tone:.0%}",
            f"  Learning Rate: {learning_rate:.2f} (tone x plasticity)",
            f"  Status:        {status}",
            "",
        ]
        for trace in result.reasoning_trace:
            lines.append(f"    {trace}")
        if result.synergies_triggered:
            lines.append("")
            lines.append("  Synergies triggered:")
            for syn in result.synergies_triggered:
                lines.append(f"    - {syn}")
        lines.append("")
        lines.append(f"  Entropy cost: {gesture.entropy_cost:.3f}")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0 if result.success else 1


async def _handle_rotate(
    target: str,
    reason: str,
    observer: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle ROTATE gesture - change perspective."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, rotate

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = rotate(target, reason or f"Rotating perspective on {target}")
    gesture = gesture.__class__(
        verb=gesture.verb,
        target=gesture.target,
        tone=gesture.tone,
        reasoning=gesture.reasoning,
        entropy_cost=gesture.entropy_cost,
        observer=observer,
    )

    result = await apply_gesture(garden, gesture)

    output = {
        "verb": "rotate",
        "target": target,
        "observer": observer,
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "reasoning": list(result.reasoning_trace),
        "entropy_cost": gesture.entropy_cost,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        lines = [
            "",
            f"  {emoji} ROTATE: {target}",
            "",
            f"  Observer: {observer}",
            "",
        ]
        for trace in result.reasoning_trace:
            lines.append(f"    {trace}")
        lines.append("")
        lines.append(f"  Entropy cost: {gesture.entropy_cost:.3f}")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0 if result.success else 1


async def _handle_wait(
    reason: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle WAIT gesture - intentional pause."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.tending import apply_gesture, wait

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    gesture = wait(reason or "Allowing time to pass")
    result = await apply_gesture(garden, gesture)

    output = {
        "verb": "wait",
        "reason": reason or "Allowing time to pass",
        "accepted": result.accepted,
        "state_changed": result.state_changed,
        "reasoning": list(result.reasoning_trace),
        "entropy_cost": 0.0,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(output, indent=2), output, ctx)
    else:
        emoji = gesture.verb.emoji
        lines = [
            "",
            f"  {emoji} WAIT",
            "",
        ]
        for trace in result.reasoning_trace:
            lines.append(f"    {trace}")
        lines.append("")
        lines.append("  Entropy cost: 0.000 (waiting is free)")
        lines.append("")

        _emit_output("\n".join(lines), output, ctx)

    return 0


def _extract_arg(args: list[str], flag: str) -> str | None:
    """Extract value after a flag from args."""
    for i, arg in enumerate(args):
        if arg == flag and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith(f"{flag}="):
            return arg[len(flag) + 1 :]
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


# =============================================================================
# Alias Commands (Top-level shortcuts)
# =============================================================================


def cmd_observe(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg observe -> kg tend observe."""
    return cmd_tend(["observe"] + args, ctx)


def cmd_prune(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg prune -> kg tend prune."""
    return cmd_tend(["prune"] + args, ctx)


def cmd_graft(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg graft -> kg tend graft."""
    return cmd_tend(["graft"] + args, ctx)


def cmd_water(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg water -> kg tend water."""
    return cmd_tend(["water"] + args, ctx)


def cmd_rotate(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg rotate -> kg tend rotate."""
    return cmd_tend(["rotate"] + args, ctx)


def cmd_wait(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Alias: kg wait -> kg tend wait."""
    return cmd_tend(["wait"] + args, ctx)


__all__ = [
    "cmd_tend",
    # Aliases
    "cmd_observe",
    "cmd_prune",
    "cmd_graft",
    "cmd_water",
    "cmd_rotate",
    "cmd_wait",
]
