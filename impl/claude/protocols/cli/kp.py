"""
kp: Quick Probe CLI.

"The laws hold, or they don't. No middle ground."

This is the maximum-ergonomics interface for quick probes.
Two keystrokes vs eight: friction matters for frequent checks.

Usage:
    kp health                        # Quick health check
    kp health --all                  # All Crown Jewels
    kp health --jewel brain          # Specific jewel
    kp health --json                 # JSON output

Equivalent to:
    kg probe health

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md §Phase 4
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Quick probe entry point."""
    if argv is None:
        argv = sys.argv[1:]

    # Import handler lazily
    from protocols.cli.handlers.probe_thin import cmd_probe

    # Default to health probe if no probe type specified
    if not argv or (argv and argv[0].startswith("-")):
        # No probe type, default to health
        argv = ["health"] + argv

    # Pass all args to probe command
    if "--help" in argv or "-h" in argv:
        print('kp - Quick Probe: kp [health|identity|associativity|coherence|budget] [options]')
        print()
        print("Examples:")
        print('  kp health                    # Check all Crown Jewels')
        print('  kp health --jewel brain      # Check specific jewel')
        print('  kp health --json             # JSON output')
        print()
        print("For full help: kg probe --help")
        return 0

    return cmd_probe(list(argv))


if __name__ == "__main__":
    sys.exit(main())
