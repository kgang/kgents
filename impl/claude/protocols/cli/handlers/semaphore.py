"""
Semaphore Handler: Manage agent semaphores from the CLI.

Agent Semaphores are pause points where agents yield control to humans
for approval, context, or decisions. This handler provides CLI access
to the Purgatory store.

Usage:
    kgents semaphore list         # List pending semaphores
    kgents semaphore resolve ID   # Resolve a semaphore
    kgents semaphore cancel ID    # Cancel a semaphore
    kgents semaphore inspect ID   # Show details of a semaphore
    kgents semaphore void         # Void all expired semaphores

Example output:
    [SEMAPHORE] 3 pending
      sem-abc123: [approval_needed] "Approve this action?"
      sem-def456: [context_required] "Need more info"
      sem-ghi789: [sensitive_action] "Delete database?"
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for semaphore command."""
    print(__doc__)
    print()
    print("COMMANDS:")
    print("  list              List all pending semaphores")
    print("  resolve <ID>      Resolve a semaphore (prompts for input)")
    print("  cancel <ID>       Cancel a pending semaphore")
    print("  inspect <ID>      Show full details of a semaphore")
    print("  void              Void all expired semaphores")
    print()
    print("OPTIONS:")
    print("  --input <text>    Response for resolve (non-interactive)")
    print("  --json            Output as JSON")
    print("  --help, -h        Show this help")


def cmd_semaphore(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Manage agent semaphores from the CLI.

    kgents semaphore - Human-in-the-loop control for agent operations.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("semaphore", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Get subcommand
    subcommand = None
    subcommand_args: list[str] = []
    json_mode = "--json" in args

    for arg in args:
        if arg.startswith("-"):
            continue
        if subcommand is None:
            subcommand = arg
        else:
            subcommand_args.append(arg)

    if subcommand is None:
        subcommand = "list"  # Default to list

    # Parse --input flag
    input_value = None
    for i, arg in enumerate(args):
        if arg.startswith("--input="):
            input_value = arg.split("=", 1)[1]
        elif arg == "--input" and i + 1 < len(args):
            input_value = args[i + 1]

    # Run async handler
    return asyncio.run(
        _async_semaphore(
            subcommand=subcommand,
            subcommand_args=subcommand_args,
            input_value=input_value,
            json_mode=json_mode,
            ctx=ctx,
        )
    )


async def _async_semaphore(
    subcommand: str,
    subcommand_args: list[str],
    input_value: str | None = None,
    json_mode: bool = False,
    ctx: "InvocationContext | None" = None,
) -> int:
    """
    Async implementation of semaphore command.
    """
    try:
        from agents.flux.semaphore import Purgatory

        # Get or create purgatory instance
        purgatory = _get_purgatory()

        match subcommand:
            case "list":
                return await _handle_list(purgatory, json_mode, ctx)
            case "resolve":
                if not subcommand_args:
                    _emit_output(
                        "[SEMAPHORE] X Missing token ID",
                        {"error": "Missing token ID"},
                        ctx,
                    )
                    return 1
                return await _handle_resolve(
                    purgatory, subcommand_args[0], input_value, json_mode, ctx
                )
            case "cancel":
                if not subcommand_args:
                    _emit_output(
                        "[SEMAPHORE] X Missing token ID",
                        {"error": "Missing token ID"},
                        ctx,
                    )
                    return 1
                return await _handle_cancel(
                    purgatory, subcommand_args[0], json_mode, ctx
                )
            case "inspect":
                if not subcommand_args:
                    _emit_output(
                        "[SEMAPHORE] X Missing token ID",
                        {"error": "Missing token ID"},
                        ctx,
                    )
                    return 1
                return await _handle_inspect(
                    purgatory, subcommand_args[0], json_mode, ctx
                )
            case "void":
                return await _handle_void(purgatory, json_mode, ctx)
            case _:
                _emit_output(
                    f"[SEMAPHORE] X Unknown subcommand: {subcommand}",
                    {"error": f"Unknown subcommand: {subcommand}"},
                    ctx,
                )
                return 1

    except ImportError as e:
        _emit_output(
            f"[SEMAPHORE] X Semaphore module not available: {e}",
            {"error": f"Semaphore module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[SEMAPHORE] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


# Module-level purgatory instance (singleton for CLI session)
_purgatory_instance: Any = None


def _get_purgatory() -> Any:
    """
    Get or create the Purgatory instance.

    Resolution order:
    1. Try to get from lifecycle state (shared across CLI session)
    2. Fall back to module-level singleton (in-memory)

    The lifecycle state's purgatory is preferred because:
    - It can be backed by D-gent for persistence
    - It's shared across all CLI commands in the session
    - It survives command re-invocations
    """
    from agents.flux.semaphore import Purgatory

    global _purgatory_instance

    # Try to get from lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state

        lifecycle_state = get_lifecycle_state()
        if lifecycle_state is not None:
            # Check if lifecycle has a purgatory
            purgatory = getattr(lifecycle_state, "purgatory", None)
            if purgatory is not None:
                return purgatory
    except ImportError:
        pass

    # Fall back to module-level singleton
    if _purgatory_instance is None:
        _purgatory_instance = Purgatory()
    return _purgatory_instance


def set_purgatory(purgatory: Any) -> None:
    """
    Set the module-level purgatory instance.

    Used for testing and explicit configuration.
    """
    global _purgatory_instance
    _purgatory_instance = purgatory


async def _handle_list(
    purgatory: Any,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'semaphore list' command."""
    pending = purgatory.list_pending()

    if json_mode:
        import json

        tokens = [
            {
                "id": t.id,
                "reason": t.reason.value
                if hasattr(t.reason, "value")
                else str(t.reason),
                "prompt": t.prompt,
                "severity": t.severity,
                "deadline": t.deadline.isoformat() if t.deadline else None,
            }
            for t in pending
        ]
        _emit_output(
            json.dumps({"pending": tokens}, indent=2),
            {"pending": tokens},
            ctx,
        )
    else:
        if not pending:
            _emit_output(
                "[SEMAPHORE] No pending semaphores",
                {"pending_count": 0, "pending": []},
                ctx,
            )
        else:
            lines = [f"[SEMAPHORE] {len(pending)} pending"]
            for t in pending:
                reason = t.reason.value if hasattr(t.reason, "value") else str(t.reason)
                lines.append(f'  {t.id}: [{reason}] "{t.prompt}"')

            human_output = "\n".join(lines)
            semantic_output = {
                "pending_count": len(pending),
                "pending": [
                    {
                        "id": t.id,
                        "reason": t.reason.value
                        if hasattr(t.reason, "value")
                        else str(t.reason),
                        "prompt": t.prompt,
                    }
                    for t in pending
                ],
            }
            _emit_output(human_output, semantic_output, ctx)

    return 0


async def _handle_resolve(
    purgatory: Any,
    token_id: str,
    input_value: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'semaphore resolve' command."""
    # Get token first to show prompt
    token = purgatory.get(token_id)
    if token is None:
        _emit_output(
            f"[SEMAPHORE] X Token not found: {token_id}",
            {"error": "Token not found", "token_id": token_id},
            ctx,
        )
        return 1

    if not token.is_pending:
        status = (
            "resolved"
            if token.is_resolved
            else "cancelled"
            if token.is_cancelled
            else "voided"
            if token.is_voided
            else "unknown"
        )
        _emit_output(
            f"[SEMAPHORE] X Token already {status}: {token_id}",
            {"error": f"Token already {status}", "token_id": token_id},
            ctx,
        )
        return 1

    # Get input if not provided
    if input_value is None:
        print(f"\n[SEMAPHORE] Resolving: {token_id}")
        print(f"Prompt: {token.prompt}")
        if token.options:
            print(f"Options: {', '.join(token.options)}")
        print()
        try:
            input_value = input("Your response: ")
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 1

    # Resolve
    reentry = await purgatory.resolve(token_id, input_value)
    if reentry is None:
        _emit_output(
            f"[SEMAPHORE] X Failed to resolve: {token_id}",
            {"error": "Failed to resolve", "token_id": token_id},
            ctx,
        )
        return 1

    _emit_output(
        f"[SEMAPHORE] Resolved: {token_id}",
        {"status": "resolved", "token_id": token_id},
        ctx,
    )
    return 0


async def _handle_cancel(
    purgatory: Any,
    token_id: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'semaphore cancel' command."""
    success = await purgatory.cancel(token_id)
    if success:
        _emit_output(
            f"[SEMAPHORE] Cancelled: {token_id}",
            {"status": "cancelled", "token_id": token_id},
            ctx,
        )
        return 0
    else:
        _emit_output(
            f"[SEMAPHORE] X Token not found or not pending: {token_id}",
            {"error": "Token not found or not pending", "token_id": token_id},
            ctx,
        )
        return 1


async def _handle_inspect(
    purgatory: Any,
    token_id: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'semaphore inspect' command."""
    token = purgatory.get(token_id)
    if token is None:
        _emit_output(
            f"[SEMAPHORE] X Token not found: {token_id}",
            {"error": "Token not found", "token_id": token_id},
            ctx,
        )
        return 1

    status = (
        "resolved"
        if token.is_resolved
        else "cancelled"
        if token.is_cancelled
        else "voided"
        if token.is_voided
        else "pending"
    )

    semantic = {
        "token_id": token.id,
        "status": status,
        "reason": token.reason.value
        if hasattr(token.reason, "value")
        else str(token.reason),
        "prompt": token.prompt,
        "options": token.options,
        "severity": token.severity,
        "deadline": token.deadline.isoformat() if token.deadline else None,
        "escalation": token.escalation,
        "created_at": token.created_at.isoformat() if token.created_at else None,
        "resolved_at": token.resolved_at.isoformat() if token.resolved_at else None,
        "cancelled_at": token.cancelled_at.isoformat() if token.cancelled_at else None,
        "voided_at": token.voided_at.isoformat() if token.voided_at else None,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
    else:
        reason = (
            token.reason.value if hasattr(token.reason, "value") else str(token.reason)
        )
        lines = [
            f"[SEMAPHORE] {token_id}",
            f"  Status: {status}",
            f"  Reason: {reason}",
            f"  Prompt: {token.prompt}",
        ]
        if token.options:
            lines.append(f"  Options: {', '.join(token.options)}")
        lines.append(f"  Severity: {token.severity}")
        if token.deadline:
            lines.append(f"  Deadline: {token.deadline.isoformat()}")
        if token.escalation:
            lines.append(f"  Escalation: {token.escalation}")
        if token.created_at:
            lines.append(f"  Created: {token.created_at.isoformat()}")
        if token.resolved_at:
            lines.append(f"  Resolved: {token.resolved_at.isoformat()}")
        if token.cancelled_at:
            lines.append(f"  Cancelled: {token.cancelled_at.isoformat()}")
        if token.voided_at:
            lines.append(f"  Voided: {token.voided_at.isoformat()}")

        _emit_output("\n".join(lines), semantic, ctx)

    return 0


async def _handle_void(
    purgatory: Any,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'semaphore void' command."""
    voided = await purgatory.void_expired()

    if json_mode:
        import json

        result = {
            "voided_count": len(voided),
            "voided_ids": [t.id for t in voided],
        }
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        if not voided:
            _emit_output(
                "[SEMAPHORE] No expired semaphores to void",
                {"voided_count": 0, "voided_ids": []},
                ctx,
            )
        else:
            lines = [f"[SEMAPHORE] Voided {len(voided)} expired semaphore(s):"]
            for t in voided:
                lines.append(f"  {t.id}")

            _emit_output(
                "\n".join(lines),
                {"voided_count": len(voided), "voided_ids": [t.id for t in voided]},
                ctx,
            )

    return 0


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
