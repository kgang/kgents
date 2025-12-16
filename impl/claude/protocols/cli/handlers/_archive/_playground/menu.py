"""
Playground Menu: Interactive tutorial selection.

Provides a delightful entry point to the playground
with clear choices and instant feedback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


MENU_BANNER = """
============================================================
           Welcome to the kgents Playground!
============================================================

Learn by doing. Each tutorial takes < 5 minutes.

"""

MENU_OPTIONS = [
    ("1", "hello", "Hello World", "Your first agent"),
    ("2", "compose", "Composition", "Pipe agents together with >>"),
    ("3", "functor", "Lift to Maybe", "Handle optional values elegantly"),
    ("4", "soul", "K-gent Dialogue", "Chat with Kent's simulacrum"),
    ("5", "repl", "Free Exploration", "REPL with pre-imported modules"),
]


async def show_menu(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Display interactive menu and handle selection."""
    from . import run_tutorial

    if json_mode:
        import json

        data = {
            "menu": [
                {"key": key, "id": id_, "title": title, "desc": desc}
                for key, id_, title, desc in MENU_OPTIONS
            ]
        }
        _emit_output(json.dumps(data), data, ctx)
        return 0

    while True:
        # Display menu
        _emit_output(MENU_BANNER, {"status": "menu"}, ctx)

        for key, id_, title, desc in MENU_OPTIONS:
            line = f"  [{key}] {title:<20} - {desc}"
            _emit_output(line, {"option": id_}, ctx)

        _emit_output("\n  [q] Quit\n", {}, ctx)

        # Get selection
        try:
            choice = input("Choose (1-5) or 'q' to quit: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            _emit_output("\n[Goodbye! Come back anytime.]", {"status": "quit"}, ctx)
            return 0

        if choice in ("q", "quit", "exit"):
            _emit_output("\n[Goodbye! Come back anytime.]", {"status": "quit"}, ctx)
            return 0

        # Find matching option
        selected = None
        for key, id_, title, desc in MENU_OPTIONS:
            if choice == key or choice == id_:
                selected = id_
                break

        if selected is None:
            _emit_output(
                f"\nUnknown option: {choice}. Try 1-5.\n", {"error": "invalid"}, ctx
            )
            continue

        # Run selected tutorial or REPL
        if selected == "repl":
            # Return sentinel to signal "run REPL sync outside async"
            return -1
        else:
            result = await run_tutorial(selected, json_mode, ctx)

        # After tutorial, show menu again (unless they quit)
        if result != 0:
            return result

        # Ask if they want to continue
        try:
            again = input("\n[Press Enter for menu, 'q' to quit] ").strip().lower()
            if again in ("q", "quit", "exit"):
                return 0
        except (KeyboardInterrupt, EOFError):
            return 0


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
