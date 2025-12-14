"""
AGENTESE Context Routers.

This module provides the CLI-to-AGENTESE bridge, mapping the 5 contexts
(self, world, concept, void, time) to CLI commands.

The Hegelian Synthesis:
  Thesis:    AGENTESE purity (world.house.manifest)
  Antithesis: Professional CLI conventions (git add, npm install)
  Synthesis:  AGENTESE contexts as nouns, familiar verbs as subcommands

Usage:
    kgents self status         # -> self.capabilities.manifest
    kgents world agents list   # -> world.agents.manifest
    kgents concept laws verify # -> concept.laws.verify
    kgents void entropy sip    # -> void.entropy.sip
    kgents time trace witness  # -> time.trace.witness
"""

from .base import ContextRouter, context_help
from .concept import cmd_concept
from .self_ import cmd_self
from .time_ import cmd_time
from .void import cmd_void
from .world import cmd_world

__all__ = [
    "ContextRouter",
    "context_help",
    # Context entry points
    "cmd_self",
    "cmd_world",
    "cmd_concept",
    "cmd_void",
    "cmd_time",
]
