"""
Bootstrap CLI Commands

Phase 2 of the Conscious Shell: Commands for displaying and verifying
the foundational laws and principles that govern the kgents system.

Commands:
    kgents laws                  - Display the 7 category laws
    kgents laws verify           - Verify laws hold for agents
    kgents laws witness <op>     - Witness a composition

    kgents principles            - Display the 7 design principles
    kgents principles check      - Evaluate against principles
"""

from .laws import cmd_laws
from .principles import cmd_principles

__all__ = [
    "cmd_laws",
    "cmd_principles",
]
