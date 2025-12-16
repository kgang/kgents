"""
Playground: Interactive tutorials for kgents.

This module provides the tutorial engine and content for `kgents play`.
Zero-to-delight in under 5 minutes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

from .menu import show_menu
from .repl import start_repl, start_repl_sync
from .tutorial import Tutorial, TutorialStep

# Tutorial registry
TUTORIALS: dict[str, "Tutorial"] = {}


def _load_tutorials() -> None:
    """Load all tutorials on first access."""
    if TUTORIALS:
        return  # Already loaded

    from .content.composition import COMPOSITION_TUTORIAL
    from .content.functor import FUNCTOR_TUTORIAL
    from .content.hello_world import HELLO_WORLD_TUTORIAL
    from .content.soul import SOUL_TUTORIAL

    TUTORIALS["hello"] = HELLO_WORLD_TUTORIAL
    TUTORIALS["compose"] = COMPOSITION_TUTORIAL
    TUTORIALS["functor"] = FUNCTOR_TUTORIAL
    TUTORIALS["soul"] = SOUL_TUTORIAL


async def run_tutorial(
    name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Run a specific tutorial by name."""
    _load_tutorials()

    if name not in TUTORIALS:
        return 1

    tutorial = TUTORIALS[name]
    return await tutorial.run(json_mode, ctx)


__all__ = [
    "Tutorial",
    "TutorialStep",
    "TUTORIALS",
    "show_menu",
    "run_tutorial",
    "start_repl",
    "start_repl_sync",
]
