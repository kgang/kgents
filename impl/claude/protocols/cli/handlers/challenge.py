"""
Challenge Handler: Devil's Advocate mode via K-gent soul.

This is an ergonomic alias for `kgents soul challenge`.

Usage:
    kgents challenge "We need microservices"
    kgents challenge "Tests should always pass"
    kgents challenge --deep "Our architecture is sound"

AGENTESE Path: self.soul.challenge
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_challenge(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Devil's Advocate: Challenge a claim using K-gent soul.

    This is an alias for `kgents soul challenge <claim>`.
    Routes directly to the soul handler with 'challenge' mode.

    AGENTESE Path: self.soul.challenge

    Returns:
        0 on success, 1 on error
    """
    # Help flag
    if "--help" in args or "-h" in args:
        print(__doc__)
        print()
        print("OPTIONS:")
        print("  --deep              Use LLM for deeper analysis")
        print("  --json              Output as JSON")
        print("  --help, -h          Show this help")
        print()
        print("EXAMPLES:")
        print('  kgents challenge "We need to rewrite everything"')
        print('  kgents challenge "The tests are comprehensive"')
        print('  kgents challenge --deep "Our security is solid"')
        print()
        print("PIPELINE USAGE:")
        print("  In REPL: self.soul.challenge >> void.shadow.project")
        print("  (Challenge a claim, then analyze what shadow it reveals)")
        return 0

    # Delegate to soul handler with 'challenge' prepended
    from protocols.cli.handlers.soul import cmd_soul

    return cmd_soul(["challenge"] + args, ctx)
