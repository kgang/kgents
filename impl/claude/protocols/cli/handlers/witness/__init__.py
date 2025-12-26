"""
Witness Handler: CLI for everyday mark-making.

"Every action leaves a mark. The mark IS the witness."

PATTERN: Rich CLI UX layer that provides extensive formatting and interaction.
         Unlike simple handlers, this has complex custom logic that can't be
         delegated to AGENTESE router (interactive flows, tree visualization, etc.)

This is the UX layer for the Witness Crown Jewel. It provides:
- `kg witness mark "action"` - Create a mark (the core habit)
- `kg witness show` - View recent marks
- `kg witness session` - View current session's marks

The km alias is recommended for daily use:
- `km "Did a thing"` - Quick mark (2 keystrokes)
- `km "Chose X" -w "Because Y"` - With reasoning
- `km "Used pattern" -p composable` - With principles

Agent-friendly mode:
- `km "action" --json` - Machine-readable output for programmatic use
- `kg witness show --json` - Marks as JSON array
- `kg witness show --today --json` - Filter + JSON for agent queries

See: spec/protocols/witness-supersession.md
See: docs/skills/witness-for-agents.md
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler

# Import all command handlers
from .context import cmd_context, cmd_context_async
from .crystals import (
    cmd_crystal,
    cmd_crystal_async,
    cmd_crystallize,
    cmd_crystallize_async,
    cmd_crystals,
    cmd_crystals_async,
    cmd_expand,
    cmd_expand_async,
)
from .dashboard import cmd_dashboard, cmd_graph
from .integration import cmd_promote, cmd_propose_now, cmd_stream
from .marks import (
    _cmd_mark_async,
    _cmd_show_async,
    cmd_mark,
    cmd_session,
    cmd_session_async,
    cmd_show,
)
from .tree import cmd_tree, cmd_tree_async

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Main Entry Point
# =============================================================================


@handler("witness", is_async=True, tier=1, description="Everyday mark-making")
async def cmd_witness(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Witness Crown Jewel: Mark-making CLI.

    "Every action leaves a mark. The mark IS the witness."

    This handler is async to properly integrate with the daemon's event loop.
    When running in daemon mode, async operations can use the daemon's
    database sessions directly without creating conflicting connections.
    """
    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = args[0].lower()
    sub_args = args[1:]

    # Check if running in daemon context
    in_daemon = os.environ.get("KGENTS_DAEMON_WORKER") is not None

    # Async subcommand handlers (always use these when cmd_witness is async)
    async_handlers = {
        "mark": _cmd_mark_async,
        "m": _cmd_mark_async,
        "show": _cmd_show_async,
        "recent": _cmd_show_async,
        "list": _cmd_show_async,
        "session": cmd_session_async,
        "tree": cmd_tree_async,
        "crystallize": cmd_crystallize_async,
        "crystals": cmd_crystals_async,
        "crystal": cmd_crystal_async,
        "expand": cmd_expand_async,
        "context": cmd_context_async,
        "ctx": cmd_context_async,
    }

    # Sync subcommand handlers (for commands that don't need async DB access)
    sync_handlers = {
        "stream": cmd_stream,
        "propose-now": cmd_propose_now,
        "propose": cmd_propose_now,
        "promote": cmd_promote,
        "dashboard": cmd_dashboard,
        "dash": cmd_dashboard,
        "graph": cmd_graph,
    }

    # Since cmd_witness itself is async, prefer async handlers
    if subcommand in async_handlers:
        return await async_handlers[subcommand](sub_args)

    # Use sync handler if available (for non-DB commands)
    if subcommand in sync_handlers:
        return sync_handlers[subcommand](sub_args)

    # If first arg doesn't look like a subcommand, treat as mark action
    if not subcommand.startswith("-"):
        return await _cmd_mark_async(args)

    print(f"Unknown subcommand: {subcommand}")
    _print_help()
    return 1


def _print_help() -> None:
    """Print witness command help."""
    help_text = """
kg witness - Everyday Mark-Making & Memory Crystallization

"Every action leaves a mark. The mark IS the witness."
"Marks become crystals. Crystals become wisdom."

MARK COMMANDS:
  kg witness mark "action"     Create a mark
  kg witness show              Show recent marks
  kg witness session           Show this session's marks

LINEAGE COMMANDS:
  kg witness tree <id>         Show causal tree (children)
  kg witness tree <id> --ancestry  Show parent chain

CRYSTAL COMMANDS:
  kg witness crystallize       Crystallize marks into insight
  kg witness crystals          List recent crystals
  kg witness crystal <id>      Show crystal details
  kg witness expand <id>       Show crystal sources

CONTEXT COMMANDS:
  kg witness context           Budget-aware crystal context
  kg witness context --budget N  Set token budget (default: 2000)
  kg witness context --query X   Relevance-weighted by query

MARK OPTIONS:
  -w, --why "reason"          Add reasoning
  -p, --principles a,b        Add principles
  -t, --tag <tag>             Add tag (can repeat: --tag a --tag b)
  --parent <mark_id>          Link as child of parent (lineage)
  --json                      Machine-readable JSON output

SHOW OPTIONS:
  -l, --limit N               Number of marks (default: 20)
  -v, --verbose               Show reasoning
  --json                      Output as JSON array
  --today                     Only marks from today
  --grep "pattern"            Filter by content/reasoning
  --tag "principle"           Filter by principle tag

TREE OPTIONS:
  --depth N                   Max depth to traverse (default: 10)
  --ancestry                  Show ancestors instead of children
  --json                      Output as JSON

CRYSTALLIZE OPTIONS:
  --level session|day|week    Target level (default: session)
  --session <id>              Session identifier
  --tree <mark_id>            Crystallize tree from root mark
  --json                      Output as JSON

CRYSTALS OPTIONS:
  --level 0|1|2|3             Filter by level (0=session, 1=day, etc)
  -l, --limit N               Number to show (default: 10)
  --json                      Output as JSON

CONTEXT OPTIONS:
  --budget N                  Token budget (default: 2000)
  --query "topic"             Relevance filter (keyword matching)
  --recency-weight N          Weight for recency vs relevance (0.0-1.0, default: 0.7)
  --json                      Output as JSON (for agents)

INTEGRATION COMMANDS (Phase 4):
  kg witness stream            Stream crystal events in real-time
  kg witness propose-now       Propose NOW.md updates from crystals
  kg witness promote           Promote crystals to Brain teachings

STREAM OPTIONS:
  --level 0|1|2|3             Filter by level

PROPOSE OPTIONS:
  --apply                     Apply proposals with backup
  --json                      Output as JSON

PROMOTE OPTIONS:
  <crystal_id>                Promote specific crystal
  --auto                      Auto-promote top candidates
  --candidates                List promotion candidates
  --json                      Output as JSON

VISUALIZATION COMMANDS (Phase 5):
  kg witness dashboard         Textual TUI crystal navigator (default)
  kg witness graph             Crystal graph as JSON (for frontend)

DASHBOARD OPTIONS:
  --level 0|1|2|3             Filter by level
  --classic                   Use old Rich-based dashboard
  TUI Keys: j/k=navigate, Enter=copy, 0-3=level, a=all, r=refresh, q=quit

GRAPH OPTIONS:
  --level 0|1|2|3             Filter by level
  --limit N                   Max crystals per level (default: 50)

QUICK ALIAS (recommended):
  km "action"                  = kg witness mark "action"
  km "X" -w "Y"                = kg witness mark "X" -w "Y"
  km "X" --tag eureka          = kg witness mark "X" --tag eureka
  km "X" --parent mark-abc     = Link as child of parent

EXAMPLES:
  kg witness mark "Refactored DI container"
  kg witness mark "Chose PostgreSQL" -w "Scaling needs"
  kg witness mark "Insight" --tag eureka --tag pattern  # Multiple tags
  kg witness mark "Fixed issue" --parent mark-abc123    # Create causal link
  kg witness tree mark-abc123          # See tree of related marks
  kg witness crystallize               # LLM-powered insight extraction
  kg witness crystallize --tree mark-abc  # Crystallize entire tree
  kg witness context --budget 1500     # Get crystals within budget
  kg witness context --query "audit"   # Relevance-weighted context

AGENT-FRIENDLY EXAMPLES:
  km "Completed task" --json             # Returns: {"mark_id": "...", ...}
  km "Follow-up" --parent mark-abc --json  # Returns with parent link
  kg witness tree mark-abc --json        # Tree structure as JSON
  kg witness crystallize --json          # Returns: {"crystal_id": "...", ...}
  kg witness crystals --json             # Returns crystal array
  kg witness show --today --json         # Today's marks for context
  kg witness context --budget 1000 --json  # Budget-aware context for agents

PHILOSOPHY:
  Marks are observations. Crystals are insights.
  An action without a mark is a reflex.
  An action with a mark is agency.
  Crystallization reveals patterns.
  Lineage reveals causation.
  Budget forces compression.

See: spec/protocols/witness-crystallization.md
See: docs/skills/witness-for-agents.md
"""
    print(help_text.strip())


__all__ = [
    "cmd_witness",
    # Export commonly used commands for direct import
    "cmd_mark",
    "cmd_show",
    "cmd_session",
    "cmd_crystallize",
    "cmd_crystals",
    "cmd_crystal",
    "cmd_expand",
    "cmd_context",
    "cmd_tree",
    "cmd_stream",
    "cmd_propose_now",
    "cmd_promote",
    "cmd_dashboard",
    "cmd_graph",
]
