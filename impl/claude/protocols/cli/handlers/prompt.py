"""
CLI Handler for Evergreen Prompt System.

Wave 6 of the Evergreen Prompt System.

Provides the `kg prompt` command for prompt system operations:
- kg prompt                    - Show current compiled prompt
- kg prompt compile            - Compile CLAUDE.md
- kg prompt history            - Show checkpoint history
- kg prompt rollback <id>      - Rollback to checkpoint
- kg prompt diff <id1> <id2>   - Diff two checkpoints
- kg prompt validate           - Run category law checks

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


USAGE = """
kg prompt - Evergreen Prompt System

USAGE:
    kg prompt [OPTIONS]                  Show current compiled prompt
    kg prompt compile [OPTIONS]          Compile CLAUDE.md from sections
    kg prompt history [--limit N]        Show checkpoint history
    kg prompt rollback <checkpoint_id>   Rollback to checkpoint
    kg prompt diff <id1> <id2>           Diff two checkpoints
    kg prompt validate                   Run category law checks
    kg prompt export [--output FILE]     Export current prompt

OPTIONS:
    --show-reasoning    Show reasoning traces for each section
    --show-habits       Show habit influence (PolicyVector)
    --feedback TEXT     Apply TextGRAD feedback to improve
    --auto-improve      Run habit encoder and propose improvements
    --preview           Preview changes without writing
    --checkpoint/--no-checkpoint  Create checkpoint (default: True)
    --emit-metrics      Emit metrics to metrics/evergreen/
    --output, -o PATH   Output path for compiled prompt

EXAMPLES:
    kg prompt                              # Show current prompt
    kg prompt --show-reasoning             # Show with reasoning traces
    kg prompt compile -o CLAUDE.md         # Compile and save
    kg prompt compile --feedback "be more concise"
    kg prompt history --limit 5
    kg prompt rollback abc12345
    kg prompt diff abc12345 def67890
    kg prompt validate
"""


def cmd_prompt(args: list[str]) -> int:
    """
    Entry point for kg prompt command.

    Args:
        args: Command line arguments after 'kg prompt'

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if not args or args[0] in ("--help", "-h"):
        print(USAGE)
        return 0

    # Parse subcommand
    subcommand = args[0] if args else "show"

    # Handle flag-based show mode
    if subcommand.startswith("--"):
        # It's a flag, treat as show with options
        return _handle_show(args)

    # Handle explicit subcommands
    remaining_args = args[1:] if len(args) > 1 else []

    handlers = {
        "compile": _handle_compile,
        "history": _handle_history,
        "rollback": _handle_rollback,
        "diff": _handle_diff,
        "validate": _handle_validate,
        "export": _handle_export,
        "show": _handle_show,
    }

    handler = handlers.get(subcommand)
    if handler is None:
        print(f"Unknown subcommand: {subcommand}")
        print(USAGE)
        return 1

    try:
        return handler(remaining_args)
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_show(args: list[str]) -> int:
    """Show current compiled prompt."""
    from protocols.prompt.cli import compile_prompt

    # Parse flags
    show_reasoning = "--show-reasoning" in args
    show_habits = "--show-habits" in args

    try:
        compile_prompt(
            checkpoint=False,  # Don't checkpoint for show
            show_reasoning=show_reasoning,
            show_habits=show_habits,
        )
        return 0
    except Exception as e:
        print(f"Error showing prompt: {e}")
        return 1


def _handle_compile(args: list[str]) -> int:
    """Compile CLAUDE.md from sections."""
    from protocols.prompt.cli import compile_prompt

    # Parse arguments
    output_path = None
    checkpoint = True
    reason = None
    show_reasoning = False
    show_habits = False
    feedback = None
    auto_improve = False
    preview = False
    emit_metrics = False
    include_dynamic = True

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("--output", "-o") and i + 1 < len(args):
            output_path = Path(args[i + 1])
            i += 2
        elif arg == "--no-checkpoint":
            checkpoint = False
            i += 1
        elif arg == "--checkpoint":
            checkpoint = True
            i += 1
        elif arg in ("--reason", "-r") and i + 1 < len(args):
            reason = args[i + 1]
            i += 2
        elif arg == "--show-reasoning":
            show_reasoning = True
            i += 1
        elif arg == "--show-habits":
            show_habits = True
            i += 1
        elif arg == "--feedback" and i + 1 < len(args):
            feedback = args[i + 1]
            i += 2
        elif arg == "--auto-improve":
            auto_improve = True
            i += 1
        elif arg == "--preview":
            preview = True
            i += 1
        elif arg == "--emit-metrics":
            emit_metrics = True
            i += 1
        elif arg == "--no-dynamic":
            include_dynamic = False
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            return 1

    try:
        compile_prompt(
            output_path=output_path,
            checkpoint=checkpoint,
            reason=reason,
            show_reasoning=show_reasoning,
            show_habits=show_habits,
            feedback=feedback,
            auto_improve=auto_improve,
            preview=preview,
            emit_metrics=emit_metrics,
            include_dynamic=include_dynamic,
        )
        return 0
    except Exception as e:
        print(f"Compilation error: {e}")
        return 1


def _handle_history(args: list[str]) -> int:
    """Show checkpoint history."""
    from protocols.prompt.cli import show_history

    # Parse --limit
    limit = 10
    for i, arg in enumerate(args):
        if arg in ("--limit", "-n") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                print(f"Invalid limit: {args[i + 1]}")
                return 1
            break

    try:
        show_history(limit=limit)
        return 0
    except Exception as e:
        print(f"Error showing history: {e}")
        return 1


def _handle_rollback(args: list[str]) -> int:
    """Rollback to a checkpoint."""
    from protocols.prompt.cli import do_rollback

    if not args:
        print("Error: checkpoint_id required")
        print("Usage: kg prompt rollback <checkpoint_id>")
        return 1

    checkpoint_id = args[0]

    try:
        do_rollback(checkpoint_id)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"Rollback error: {e}")
        return 1


def _handle_diff(args: list[str]) -> int:
    """Diff two checkpoints."""
    from protocols.prompt.cli import show_diff

    if len(args) < 2:
        print("Error: two checkpoint IDs required")
        print("Usage: kg prompt diff <id1> <id2>")
        return 1

    id1, id2 = args[0], args[1]

    try:
        show_diff(id1, id2)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(f"Diff error: {e}")
        return 1


def _handle_validate(args: list[str]) -> int:
    """Run category law checks."""
    import asyncio

    from protocols.agentese.contexts.prompt import PromptNode

    print("Running category law checks...")
    print("-" * 40)

    try:
        node = PromptNode()

        # Create a minimal mock observer
        class MockDNA:
            name = "validator"

        class MockUmwelt:
            dna = MockDNA()
            archetype = "developer"

        observer = MockUmwelt()

        # Run validation
        result = asyncio.run(node._validate(observer))

        # Display results
        print("\nLaw Checks:")
        all_passed = True
        for law_name, passed in result.law_checks:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {law_name}")
            if not passed:
                all_passed = False

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        print("-" * 40)
        if result.valid:
            print("[OK] All laws validated successfully")
            return 0
        else:
            print("[FAIL] Some laws failed validation")
            return 1

    except Exception as e:
        print(f"Validation error: {e}")
        return 1


def _handle_export(args: list[str]) -> int:
    """Export current prompt to file."""
    from protocols.prompt.cli import compile_prompt

    # Parse --output
    output_path = Path("CLAUDE.exported.md")
    for i, arg in enumerate(args):
        if arg in ("--output", "-o") and i + 1 < len(args):
            output_path = Path(args[i + 1])
            break

    try:
        content = compile_prompt(
            output_path=output_path,
            checkpoint=False,  # Don't checkpoint for export
        )
        print(f"Exported prompt to: {output_path}")
        print(f"  Size: {len(content)} chars (~{len(content) // 4} tokens)")
        return 0
    except Exception as e:
        print(f"Export error: {e}")
        return 1


# Register with CLI
COMMANDS = {
    "prompt": cmd_prompt,
}


__all__ = ["cmd_prompt", "COMMANDS"]
