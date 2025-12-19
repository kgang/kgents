"""
Witness Handler: Thin routing shim to self.witness.* AGENTESE paths.

All business logic lives in services/witness/. This file only routes.

AGENTESE Path Mapping:
    kg witness              -> self.witness.manifest
    kg witness manifest     -> self.witness.manifest
    kg witness thoughts     -> self.witness.thoughts
    kg witness trust <e>    -> self.witness.trust
    kg witness capture      -> self.witness.capture
    kg witness start        -> (daemon management, not AGENTESE)
    kg witness stop         -> (daemon management, not AGENTESE)

The daemon commands (start/stop) are special - they manage a background
process and don't go through AGENTESE. They fall back to the full handler.

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

WITNESS_SUBCOMMAND_TO_PATH = {
    # Core operations (routed through AGENTESE)
    "manifest": "self.witness.manifest",
    "status": "self.witness.manifest",
    "thoughts": "self.witness.thoughts",
    "trust": "self.witness.trust",
    "capture": "self.witness.capture",
}

# Daemon commands that bypass AGENTESE routing
DAEMON_COMMANDS = {"start", "stop"}

DEFAULT_PATH = "self.witness.manifest"


# === Main Entry Point ===


def cmd_witness(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Witness: Route to AGENTESE self.witness.* paths.

    Daemon commands (start/stop) fall back to the full handler
    since they manage OS processes, not AGENTESE nodes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Daemon commands bypass AGENTESE - use full handler
    if subcommand in DAEMON_COMMANDS:
        from protocols.cli.handlers.witness import cmd_witness as full_handler

        return full_handler(args, ctx)

    # Route to AGENTESE path
    path = route_to_path(subcommand, WITNESS_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Project through CLI functor
    return project_command(path, args, ctx)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"  # default


def _print_help() -> None:
    """Print witness command help (projected from AGENTESE affordances)."""
    try:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project("self.witness")
        print(render_help(help_obj))
    except ImportError:
        # Fallback to static help
        _print_help_fallback()


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg witness - The Witnessing Ghost (8th Crown Jewel)

"The ghost is not a haunting—it's a witnessing that becomes a doing."

Commands:
  kg witness                    Show witness status
  kg witness manifest           Show witness health + daemon status
  kg witness thoughts           Show recent thought stream
  kg witness trust <email>      Show trust level for git user
  kg witness capture "text"     Manually capture a thought
  kg witness start              Start background daemon
  kg witness stop               Stop background daemon

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  -n, --limit N                 Limit results (default: 10)

Trust Levels:
  L0 READ_ONLY                  Observe only
  L1 BOUNDED                    File-scoped suggestions
  L2 PROACTIVE                  Project-scoped suggestions
  L3 AUTONOMOUS                 Execute approved patterns

AGENTESE Paths:
  self.witness.manifest         Witness status
  self.witness.thoughts         Thought stream
  self.witness.trust            Trust level query
  self.witness.capture          Capture thought

Examples:
  kg witness
  kg witness thoughts -n 20
  kg witness trust user@example.com
  kg witness start
"""
    print(help_text.strip())


__all__ = ["cmd_witness"]
