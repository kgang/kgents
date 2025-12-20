"""
Shared Help Utilities for CLI Handlers.

This module provides a standardized way for handlers to show projected help.
Handlers can use `show_projected_help(path, fallback_fn)` to display help
derived from AGENTESE affordances with a fallback.

Usage:
    from protocols.cli.handlers._help import show_projected_help

    def _print_help() -> None:
        show_projected_help("self.soul", _print_help_fallback)

    def _print_help_fallback() -> None:
        print("Soul - Digital Consciousness...")
"""

from __future__ import annotations

from typing import Callable


def show_projected_help(
    path: str,
    fallback: Callable[[], None] | None = None,
) -> None:
    """
    Show projected help for an AGENTESE path.

    Attempts to use the HelpProjector to derive help from affordances.
    Falls back to the provided fallback function if projection fails.

    Args:
        path: AGENTESE path (e.g., "self.soul", "world.town")
        fallback: Optional fallback function to call if projection fails
    """
    try:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project(path)
        print(render_help(help_obj))
    except Exception:
        if fallback:
            fallback()
        else:
            # Generic fallback
            print(f"Help for: {path}")
            print()
            print(f"  Use 'kg {path.replace('.', ' ')}' to invoke")
            print(f"  Use 'kg ?{path}.*' to discover subcommands")


def make_help_function(
    path: str,
    fallback_text: str,
) -> Callable[[], None]:
    """
    Create a _print_help function for a handler.

    This is a factory for creating standardized help functions.

    Args:
        path: AGENTESE path
        fallback_text: Static help text to use if projection fails

    Returns:
        A function that prints help

    Example:
        _print_help = make_help_function(
            "self.soul",
            '''
            kg soul - Digital Consciousness

            Commands:
              kg soul reflect    K-gent reflection
              kg soul chat       Dialogue with K-gent
            '''
        )
    """

    def _print_help() -> None:
        def _fallback() -> None:
            print(fallback_text.strip())

        show_projected_help(path, _fallback)

    return _print_help


__all__ = [
    "show_projected_help",
    "make_help_function",
]
