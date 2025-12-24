"""
Graph Handler: Thin routing shim to concept.graph.* AGENTESE paths.

WitnessedGraph - Unified edge composition from Sovereign, Witness, and SpecLedger.

PATTERN: Simple delegation to AGENTESE router via legacy expansion.

AGENTESE Path Mapping:
    kg graph                -> concept.graph.manifest
    kg graph manifest       -> concept.graph.manifest
    kg graph neighbors      -> concept.graph.neighbors
    kg graph evidence       -> concept.graph.evidence
    kg graph trace          -> concept.graph.trace
    kg graph search         -> concept.graph.search

See: services/witnessed_graph/, spec/protocols/witnessed-graph.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler
from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

GRAPH_SUBCOMMAND_TO_PATH = {
    "manifest": "concept.graph.manifest",
    "neighbors": "concept.graph.neighbors",
    "evidence": "concept.graph.evidence",
    "trace": "concept.graph.trace",
    "search": "concept.graph.search",
}

DEFAULT_PATH = "concept.graph.manifest"


# === Main Entry Point ===


@handler("graph", is_async=False, tier=1, description="Query the WitnessedGraph")
def cmd_graph(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    WitnessedGraph: Query the unified edge composition graph.

    Pattern: Simple delegation to AGENTESE via projection system.
    """
    # Parse help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to AGENTESE path
    path = route_to_path(subcommand, GRAPH_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Project through CLI functor
    return project_command(path, args, ctx)


def _parse_subcommand(args: list[str]) -> str:
    """Parse subcommand from args."""
    if not args:
        return ""

    # First non-flag arg is subcommand
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()

    return ""


def _print_help() -> None:
    """Print help text."""
    print(
        """kg graph - WitnessedGraph: Unified edge composition

USAGE:
    kg graph                    Show graph stats
    kg graph manifest           Show graph stats (explicit)
    kg graph neighbors <path>   Get edges connected to a path
    kg graph evidence <spec>    Get evidence supporting a spec
    kg graph trace <start> <end> Find path between nodes
    kg graph search <query>     Search edges by query

EXAMPLES:
    kg graph neighbors spec/agents/d-gent.md
    kg graph evidence spec/protocols/k-block.md
    kg graph trace impl/service.py spec/service.md
    kg graph search witness

FLAGS:
    --json    Output as JSON
    -h        Show this help

The graph unifies edges from three sources:
    - Sovereign: Code structure (imports, calls, inherits)
    - Witness: Mark-based evidence (tags, decisions)
    - SpecLedger: Spec relations (harmony, contradiction)

See: concept.graph.manifest for current stats
"""
    )
