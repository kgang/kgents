"""
Soul Handler: K-gent Digital Soul CLI interface.

K-gent Soul is the Middleware of Consciousness:
1. INTERCEPTS Semaphores from Purgatory (auto-resolves or annotates)
2. INHABITS Terrarium as ambient presence (not just CLI command)
3. DREAMS during Hypnagogia (async refinement at night)

Usage:
    kgents soul                    # Interactive (default: REFLECT)
    kgents soul reflect [prompt]   # Introspection
    kgents soul advise [prompt]    # Guidance
    kgents soul challenge [prompt] # Dialectics
    kgents soul explore [prompt]   # Discovery
    kgents soul stream             # Ambient FLOWING mode (Phase 3)
    kgents soul starters           # Show starter prompts
    kgents soul manifest           # Show current soul state
    kgents soul chat               # Interactive chat REPL
    kgents soul chat --message "X" # One-shot chat message

This module is a thin router. Implementation is in commands/soul/.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from protocols.cli.commands.soul import ALL_MODES, DIALOGUE_MODES, print_help
from protocols.cli.shared import InvocationContext

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext as ReflectorContext


# Module-level soul instance (singleton for CLI session)
_soul_instance: Any = None


def _get_soul() -> Any:
    """
    Get or create the K-gent Soul instance.

    Resolution order:
    1. Try to get from lifecycle state (shared across CLI session)
    2. Fall back to module-level singleton (in-memory)
    """
    from agents.k import KgentSoul

    global _soul_instance

    # Try to get from lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state

        lifecycle_state = get_lifecycle_state()
        if lifecycle_state is not None:
            soul = getattr(lifecycle_state, "soul", None)
            if soul is not None:
                return soul
    except ImportError:
        pass

    # Fall back to module-level singleton
    if _soul_instance is None:
        _soul_instance = KgentSoul()
    return _soul_instance


def set_soul(soul: Any) -> None:
    """Set the module-level soul instance."""
    global _soul_instance
    _soul_instance = soul


def cmd_soul(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """
    K-gent Soul: The Middleware of Consciousness.

    kgents soul - Engage in self-dialogue with your digital simulacra.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("soul", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        print_help()
        return 0

    # Create unified context
    invocation_ctx = InvocationContext.from_args(args, reflector_ctx=ctx)

    # Get mode/subcommand and prompt
    mode = None
    prompt_parts: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        # Only treat as mode if it's a valid mode/subcommand
        if mode is None and arg.lower() in ALL_MODES:
            mode = arg
        else:
            prompt_parts.append(arg)

    prompt = " ".join(prompt_parts) if prompt_parts else None

    # Default mode is reflect
    if mode is None:
        mode = "reflect"

    # Run async router
    return asyncio.run(_async_route(mode, prompt, invocation_ctx, args))


async def _async_route(
    mode: str,
    prompt: str | None,
    ctx: InvocationContext,
    args: list[str],
) -> int:
    """Route to the appropriate command handler."""
    from protocols.cli.commands.soul import ambient, being, dialogue, inspect, quick

    try:
        soul = _get_soul()

        # Parse special options
        summary_mode = "--summary" in args
        sync_hypnagogia = "--sync" in args
        dry_run = "--dry-run" in args
        use_llm = "--deep" in args

        limit = 10
        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                try:
                    limit = int(args[i + 1])
                except ValueError:
                    pass

        pulse_interval = 30
        show_pulses = "--no-pulses" not in args
        for i, arg in enumerate(args):
            if arg == "--pulse-interval" and i + 1 < len(args):
                try:
                    pulse_interval = int(args[i + 1])
                except ValueError:
                    pass

        watch_path = None
        for i, arg in enumerate(args):
            if arg == "--path" and i + 1 < len(args):
                watch_path = args[i + 1]
                break

        # Route to handlers
        match mode.lower():
            # Chat command (Phase 3 - Chat Protocol)
            case "chat":
                return await _execute_chat(prompt, args, ctx)

            # Quick commands
            case "vibe":
                return await quick.execute_vibe(ctx, soul)
            case "drift":
                return await quick.execute_drift(ctx, soul)
            case "tense":
                return await quick.execute_tense(ctx, soul)

            # Pro commands
            case "approve":
                from .soul_approve import _async_soul_approve

                return await _async_soul_approve(
                    prompt or "", ctx.json_mode, ctx._reflector_ctx
                )

            case "why":
                # Recursive why - delegates to dedicated handler
                from .why import cmd_why

                # Re-assemble args for why handler
                why_args = [a for a in args if a != "why"]
                if prompt:
                    why_args.insert(0, prompt)
                return cmd_why(why_args, ctx._reflector_ctx)

            case "tension":
                # Tension detection - delegates to dedicated handler
                from .tension import cmd_tension

                # Re-assemble args for tension handler
                tension_args = [a for a in args if a != "tension"]
                return cmd_tension(tension_args, ctx._reflector_ctx)

            # Ambient commands
            case "stream":
                return await ambient.execute_stream(
                    ctx, soul, pulse_interval, show_pulses
                )
            case "watch":
                return await ambient.execute_watch(ctx, soul, watch_path)

            # Inspection commands
            case "starters":
                return await inspect.execute_starters(ctx, soul)
            case "manifest":
                return await inspect.execute_manifest(ctx, soul)
            case "eigenvectors":
                return await inspect.execute_eigenvectors(ctx, soul)
            case "audit":
                return inspect.execute_audit(ctx, soul, summary_mode, limit)
            case "garden":
                return await inspect.execute_garden(ctx, soul, sync_hypnagogia)
            case "validate":
                file_path = _extract_file_path(args, "validate")
                return await inspect.execute_validate(ctx, soul, file_path, use_llm)
            case "dream":
                return await inspect.execute_dream(ctx, soul, dry_run)

            # Being commands
            case "history":
                return await being.execute_history(ctx, limit)
            case "propose":
                desc_parts = [
                    a for a in args if not a.startswith("-") and a != "propose"
                ]
                description = " ".join(desc_parts) if desc_parts else None
                return await being.execute_propose(ctx, description)
            case "commit":
                change_id = _extract_id(args, "commit")
                return await being.execute_commit(ctx, change_id)
            case "crystallize":
                name_parts = [
                    a for a in args if not a.startswith("-") and a != "crystallize"
                ]
                name = " ".join(name_parts) if name_parts else None
                return await being.execute_crystallize(ctx, name)
            case "resume":
                crystal_id = _extract_id(args, "resume")
                return await being.execute_resume(ctx, crystal_id)

        # Default: dialogue commands (reflect, advise, challenge, explore)
        if mode.lower() in DIALOGUE_MODES:
            return await dialogue.execute_dialogue(mode, prompt, ctx, soul)

        # Unknown mode
        from protocols.cli.shared import OutputFormatter

        output = OutputFormatter(ctx)
        output.emit_error(f"Unknown mode: {mode}")
        return 1

    except ImportError as e:
        print(f"[SOUL] X K-gent module not available: {e}")
        return 1
    except Exception as e:
        print(f"[SOUL] X Error: {e}")
        return 1


def _extract_file_path(args: list[str], command: str) -> str | None:
    """Extract file path from args for commands like validate."""
    for arg in args:
        if not arg.startswith("-") and arg != command:
            return arg
    return None


def _extract_id(args: list[str], command: str) -> str | None:
    """Extract an ID from args for commands like commit, resume."""
    for arg in args:
        if not arg.startswith("-") and arg != command:
            return arg
    return None


# --- Top-Level Mode Aliases ---
# These allow `kgents reflect "prompt"` instead of `kgents soul reflect "prompt"`


def cmd_reflect(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """Alias: kgents reflect -> kgents soul reflect."""
    return cmd_soul(["reflect"] + args, ctx)


def cmd_advise(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """Alias: kgents advise -> kgents soul advise."""
    return cmd_soul(["advise"] + args, ctx)


def cmd_challenge(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """Alias: kgents challenge -> kgents soul challenge."""
    return cmd_soul(["challenge"] + args, ctx)


def cmd_explore(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """Alias: kgents explore -> kgents soul explore."""
    return cmd_soul(["explore"] + args, ctx)


# --- Chat Command (Phase 3 - Chat Protocol) ---


async def _execute_chat(
    prompt: str | None,
    args: list[str],
    ctx: Any,
) -> int:
    """
    Execute the chat command - interactive REPL with K-gent.

    Usage:
        kgents soul chat               # Enter interactive chat REPL
        kgents soul chat --message "X" # One-shot: send message, get response
        kgents soul chat --json        # Output as JSON (one-shot only)

    This routes through the CLI projection to the ChatProjection REPL.
    """
    from protocols.cli.projection import project_command

    # Parse --message flag for one-shot mode
    message = None
    json_output = "--json" in args

    for i, arg in enumerate(args):
        if arg == "--message" and i + 1 < len(args):
            message = args[i + 1]
            break
        elif arg.startswith("--message="):
            message = arg.split("=", 1)[1]
            break

    # If prompt provided without --message flag, treat as message
    if prompt and not message:
        message = prompt

    # Build kwargs
    kwargs: dict[str, Any] = {}
    if message:
        kwargs["message"] = message

    # Project to chat path
    return project_command(
        path="self.soul.chat",
        args=args,
        ctx=ctx,
        json_output=json_output,
        kwargs=kwargs,
        entity_name="K-gent",
    )
