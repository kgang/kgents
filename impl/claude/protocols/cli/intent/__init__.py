"""
Intent Layer - The 10 Core Verbs for Human-Agent Interaction.

The Intent Layer provides a verb-first interface that maps human intentions
to agent operations. Users learn ~10 verbs, not 18 genera.

Commands:
  new       Create something (agent, flow, tongue)
  run       Execute an intent
  check     Verify target against principles/laws
  think     Generate hypotheses about a topic
  watch     Observe without judgment
  find      Search the catalog
  fix       Repair malformed input
  speak     Create a domain language (Tongue)
  judge     Evaluate against the 7 principles
  do        Natural language intent router

Philosophy:
  "Users think in verbs, not taxonomies."
  The Intent Layer is the membrane between human intention and agent action.

See: docs/cli-integration-plan.md Part 2
"""

from __future__ import annotations

# Lazy loading - only import when accessed
__all__ = [
    "cmd_new",
    "cmd_run",
    "cmd_check",
    "cmd_think",
    "cmd_watch",
    "cmd_find",
    "cmd_fix",
    "cmd_speak",
    "cmd_judge",
    "cmd_do",
]


def __getattr__(name: str):
    """Lazy load command handlers."""
    if name in (
        "cmd_new",
        "cmd_run",
        "cmd_check",
        "cmd_think",
        "cmd_watch",
        "cmd_find",
        "cmd_fix",
        "cmd_speak",
        "cmd_judge",
    ):
        from . import commands

        return getattr(commands, name)
    elif name == "cmd_do":
        from . import router

        return router.cmd_do
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
