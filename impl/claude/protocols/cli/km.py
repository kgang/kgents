"""
km: Quick Mark CLI.

"Every action leaves a mark."

This is the maximum-ergonomics interface for everyday marking.
Two keystrokes vs seven: friction matters for frequent actions.

Usage:
    km "Did a thing"                     # Minimal
    km "Chose X" -w "Because Y"          # With reasoning
    km "Pattern" -p composable           # With principles

Equivalent to:
    kg witness mark "..."

See: plans/witness-fusion-ux-design.md
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Quick mark entry point."""
    if argv is None:
        argv = sys.argv[1:]

    # Import handler lazily
    from protocols.cli.handlers.witness_thin import cmd_mark

    # Pass all args to mark command
    if not argv:
        print('km - Quick Mark: km "action" [-w why] [-p principles]')
        print()
        print("Examples:")
        print('  km "Refactored DI container"')
        print('  km "Chose PostgreSQL" -w "Scaling needs"')
        print('  km "Used Crown Jewel" -p composable,generative')
        return 0

    return cmd_mark(list(argv))


if __name__ == "__main__":
    sys.exit(main())
