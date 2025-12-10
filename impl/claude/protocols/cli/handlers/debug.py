"""
Debug CLI handlers.

Commands:
  debug ctx    Dump current CLI context
"""

from __future__ import annotations

from typing import Sequence


def cmd_debug(args: Sequence[str]) -> int:
    """Handle debug commands."""
    if not args or args[0] in ("--help", "-h"):
        print("kgents debug - Debug utilities")
        print()
        print("USAGE:")
        print("  kgents debug <command>")
        print()
        print("COMMANDS:")
        print("  ctx    Dump current CLI context")
        return 0

    command = args[0]
    cmd_args = list(args[1:])

    if command == "ctx":
        return _cmd_ctx(cmd_args)
    else:
        print(f"Unknown debug command: {command}")
        print("Available: ctx")
        return 1


def _cmd_ctx(args: list[str]) -> int:
    """Dump current CLI context."""
    from protocols.cli.hollow import find_kgents_root, load_context

    print("=== CLI Context ===")
    print()

    # Check for .kgents root
    root = find_kgents_root()
    if root:
        print(f"Workspace root: {root}")
        print(f"Config: {root}/.kgents/config.yaml")
    else:
        print("Workspace root: (not in kgents workspace)")

    print()

    # Load context
    ctx = load_context()
    if ctx:
        print("Loaded context:")
        for key, value in ctx.items():
            print(f"  {key}: {value}")
    else:
        print("No context loaded (no config.yaml or empty)")

    return 0
