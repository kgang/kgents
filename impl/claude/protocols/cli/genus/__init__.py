"""
Genus Layer CLI Commands - Power-user access to agent genera.

This module provides full taxonomy access to the agent genera for users who need
precision operations beyond the Intent Layer's 10 verbs.

Commands are namespaced by genus letter/name:
  kgents grammar reify "<domain>"    # G-gent
  kgents jit compile "<intent>"      # J-gent
  kgents parse extract <input>       # P-gent
  kgents library catalog             # L-gent
  kgents witness watch <target>      # W-gent

Phase 5 of the Conscious Shell implementation.
See: docs/cli-integration-plan.md Part 6: Genus Layer
"""

from __future__ import annotations

__all__ = [
    # C-gent commands
    "cmd_capital",
    # G-gent commands
    "cmd_grammar",
    # I-gent commands
    "cmd_garden",
    # J-gent commands
    "cmd_jit",
    # P-gent commands
    "cmd_parse",
    # L-gent commands
    "cmd_library",
    # W-gent commands
    "cmd_witness",
]


def cmd_capital(args: list[str]) -> int:
    """Capital/Economy commands (C-gent)."""
    from .c_gent import cmd_capital as handler

    return handler(args)


def cmd_garden(args: list[str]) -> int:
    """Garden/Interface commands (I-gent)."""
    from .i_gent import cmd_garden as handler

    return handler(args)


def cmd_grammar(args: list[str]) -> int:
    """Grammar/DSL commands (G-gent)."""
    from .g_gent import cmd_grammar as handler

    return handler(args)


def cmd_jit(args: list[str]) -> int:
    """JIT compilation commands (J-gent)."""
    from .j_gent import cmd_jit as handler

    return handler(args)


def cmd_parse(args: list[str]) -> int:
    """Parser commands (P-gent)."""
    from .p_gent import cmd_parse as handler

    return handler(args)


def cmd_library(args: list[str]) -> int:
    """Library/catalog commands (L-gent)."""
    from .l_gent import cmd_library as handler

    return handler(args)


def cmd_witness(args: list[str]) -> int:
    """Witness commands (W-gent)."""
    from .w_gent import cmd_witness as handler

    return handler(args)
