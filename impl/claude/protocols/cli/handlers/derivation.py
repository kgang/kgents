"""
Derivation Handler: CLI for querying agent derivations.

"Every agent can trace its lineage to Id, Compose, or Ground."

AGENTESE Path Mapping:
    kg derivation             -> concept.derivation.manifest
    kg derivation show ...    -> concept.derivation.query
    kg derivation ancestors   -> concept.derivation.navigate (edge=derives_from)
    kg derivation dependents  -> concept.derivation.navigate (edge=dependents)
    kg derivation principles  -> concept.derivation.principles
    kg derivation tree        -> concept.derivation.dag
    kg derivation list        -> concept.derivation.manifest
    kg derivation why         -> concept.derivation.confidence
    kg derivation propagate   -> concept.derivation.propagate

See: spec/protocols/derivation-framework.md §7

Teaching:
    gotcha: Agent names are case-insensitive in CLI but Titlecase in registry.
            The handler normalizes: "brain" -> "Brain"
            (Evidence: test_derivation_handler.py::test_agent_name_normalization)

    gotcha: The handler routes to AGENTESE paths - all logic is in
            protocols/agentese/contexts/concept_derivation.py
            (Evidence: test_derivation_handler.py::test_routes_to_agentese)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

DERIVATION_SUBCOMMAND_TO_PATH = {
    # Show derivation details
    "show": "concept.derivation.query",
    # Navigate hypergraph
    "ancestors": "concept.derivation.navigate",
    "dependents": "concept.derivation.navigate",
    # Visualization
    "tree": "concept.derivation.dag",
    "dag": "concept.derivation.dag",
    # Principle breakdown
    "principles": "concept.derivation.principles",
    # Confidence explanation
    "why": "concept.derivation.confidence",
    "confidence": "concept.derivation.confidence",
    # Listing
    "list": "concept.derivation.manifest",
    "status": "concept.derivation.manifest",
    # Mutation
    "propagate": "concept.derivation.propagate",
    # Timeline
    "timeline": "concept.derivation.timeline",
}

DEFAULT_PATH = "concept.derivation.manifest"


# === Argument Parsing ===


def normalize_agent_name(name: str | None) -> str | None:
    """
    Normalize agent name to Titlecase for registry lookup.

    CLI accepts: brain, Brain, BRAIN
    Registry expects: Brain

    Teaching:
        gotcha: K-gent and M-gent have hyphens that should be preserved.
    """
    if not name:
        return None

    # Handle hyphenated names (K-gent, M-gent)
    if "-" in name:
        parts = name.split("-")
        return "-".join(p.capitalize() for p in parts)

    return name.title()


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"  # default


def _extract_agent_name(args: list[str], subcommand: str) -> str | None:
    """Extract agent name from args after subcommand."""
    found_subcommand = False
    for arg in args:
        if arg.startswith("-"):
            continue
        if not found_subcommand:
            if arg.lower() == subcommand:
                found_subcommand = True
            continue
        # First non-flag arg after subcommand is agent name
        return arg

    return None


def _build_kwargs(args: list[str], subcommand: str) -> dict[str, str | bool]:
    """Build kwargs for AGENTESE invocation."""
    kwargs: dict[str, str | bool] = {}

    # Extract agent name
    agent_name = _extract_agent_name(args, subcommand)
    if agent_name:
        kwargs["agent_name"] = normalize_agent_name(agent_name) or agent_name

    # Handle edge type for navigate subcommands
    if subcommand == "ancestors":
        kwargs["edge"] = "derives_from"
    elif subcommand == "dependents":
        kwargs["edge"] = "dependents"

    # Parse flags
    for i, arg in enumerate(args):
        if arg == "--tier" and i + 1 < len(args):
            kwargs["tier"] = args[i + 1]
        elif arg == "--focus" and i + 1 < len(args):
            kwargs["focus"] = normalize_agent_name(args[i + 1]) or args[i + 1]
        elif arg == "--source" and i + 1 < len(args):
            kwargs["source"] = normalize_agent_name(args[i + 1]) or args[i + 1]

    return kwargs


# === Main Entry Point ===


def cmd_derivation(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Derivation Framework: Route to concept.derivation.* paths.

    All business logic is in protocols/agentese/contexts/concept_derivation.py.
    This handler only routes and normalizes agent names.

    Usage:
        kg derivation                      Show framework status
        kg derivation show Brain           Show Brain's derivation
        kg derivation ancestors Flux       Trace Flux's ancestry
        kg derivation dependents Id        Show what derives from Id
        kg derivation principles Witness   Principle breakdown
        kg derivation tree                 ASCII DAG visualization
        kg derivation why Brain            Confidence explanation
        kg derivation propagate --source=Compose  Force propagation
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to AGENTESE path
    path = route_to_path(subcommand, DERIVATION_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Build kwargs from args
    kwargs = _build_kwargs(args, subcommand)

    # Check for output flags
    json_output = "--json" in args
    trace_mode = "--trace" in args

    # Project through CLI functor
    return project_command(
        path,
        args,
        ctx,
        json_output=json_output,
        trace_mode=trace_mode,
        kwargs=kwargs,
    )


# === Help Text ===


def _print_help() -> None:
    """Print derivation command help (projected from AGENTESE affordances)."""
    try:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project("concept.derivation")
        print(render_help(help_obj))
    except ImportError:
        # Fallback to static help
        _print_help_fallback()


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg derivation - Agent Derivation Framework

"Every agent can trace its lineage to Id, Compose, or Ground."

Commands:
  kg derivation                      Show framework status and statistics
  kg derivation show <agent>         Show derivation details for an agent
  kg derivation ancestors <agent>    Trace lineage to bootstrap axioms
  kg derivation dependents <agent>   Show agents that derive from this one
  kg derivation principles <agent>   Principle draw breakdown (radar view)
  kg derivation tree [--tier=<t>]    ASCII DAG of all derivations
  kg derivation why <agent>          Explain confidence calculation
  kg derivation propagate [--source] Force confidence propagation
  kg derivation timeline <agent>     Confidence history over time

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --trace                       Show AGENTESE path being invoked
  --tier <tier>                 Filter by tier (bootstrap, functor, jewel, app)
  --focus <agent>               Highlight agent in DAG
  --source <agent>              Source for propagation

Tiers (by confidence ceiling):
  bootstrap  (1.00)  Id, Compose, Judge, Ground, Contradict, Sublate, Fix
  functor    (0.98)  Flux, Cooled, Either, Superposed, Logged
  polynomial (0.95)  SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL
  operad     (0.92)  TOWN_OPERAD, SOUL_OPERAD
  jewel      (0.85)  Brain, Witness, Forge, Conductor
  app        (0.75)  MorningCoffee, Gardener

AGENTESE Paths:
  concept.derivation.manifest    Framework status
  concept.derivation.query       Query specific agent
  concept.derivation.dag         DAG for visualization
  concept.derivation.navigate    Hypergraph navigation
  concept.derivation.principles  Principle breakdown
  concept.derivation.confidence  Confidence explanation

Examples:
  kg derivation show Brain
  kg derivation ancestors Flux
  kg derivation tree --tier=jewel
  kg derivation why Witness
"""
    print(help_text.strip())


__all__ = ["cmd_derivation"]
