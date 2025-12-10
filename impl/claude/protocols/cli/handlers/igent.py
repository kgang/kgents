"""
I-gent CLI handlers for the Hollow Shell.

Commands:
  kgents garden              Launch interactive field view
  kgents garden demo         Run demo with simulated activity
  kgents garden forge        Launch forge (composition) view
  kgents garden export       Export current state to markdown
  kgents whisper             Get status whisper for prompt
"""

from __future__ import annotations

from typing import Sequence


def cmd_garden(args: Sequence[str]) -> int:
    """Handle garden command - I-gent stigmergic field."""
    from protocols.cli.genus.i_gent import cmd_garden as handler

    return handler(list(args))


def cmd_whisper(args: Sequence[str]) -> int:
    """Handle whisper command - status for prompt integration."""
    from protocols.cli.igent_synergy import get_whisper_for_prompt, StatusWhisper

    # Parse args
    fmt = "prompt"
    for arg in args:
        if arg in ("--raw", "-r"):
            fmt = "raw"
        elif arg in ("--help", "-h"):
            print("kgents whisper - Get status whisper for prompt")
            print()
            print("USAGE:")
            print("  kgents whisper [--raw]")
            print()
            print("OPTIONS:")
            print("  --raw, -r    Show raw whisper (not formatted for prompt)")
            print("  --help, -h   Show this help")
            return 0

    if fmt == "prompt":
        print(get_whisper_for_prompt())
    else:
        whisper = StatusWhisper()
        print(whisper.render())

    return 0
