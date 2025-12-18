"""
Forest Handler: Thin routing to self.forest.* AGENTESE paths.

This handler routes CLI commands to ForestNode aspects via the projection functor.

Usage:
    kg forest                 # Show manifest (canopy view)
    kg forest manifest        # Generate _forest.md from plan headers
    kg forest status          # Generate _status.md content
    kg forest witness         # Show drift report
    kg forest tithe           # Archive stale plans (dry run)
    kg forest tithe --execute # Actually archive stale plans
    kg forest reconcile       # Full reconciliation
    kg forest reconcile --commit  # Reconcile and git commit
    kg forest sip             # Select dormant plan (accursed share)
    kg forest define <path>   # Create new plan scaffold

AGENTESE Paths:
    self.forest.manifest   - Canopy view from plan YAML headers
    self.forest.status     - Implementation status matrix
    self.forest.witness    - Drift report (what's stale)
    self.forest.tithe      - Archive stale plans
    self.forest.reconcile  - Full meta file reconciliation
    self.forest.sip        - Select from accursed share
    self.forest.define     - Create new plan

> "The garden tends itself, but only because we planted it together."
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Subcommand -> AGENTESE path mapping
# ForestNode is registered via SelfContextResolver at "self.forest"
FOREST_SUBCOMMAND_MAP: dict[str, str] = {
    "manifest": "self.forest.manifest",
    "status": "self.forest.status",
    "witness": "self.forest.witness",
    "tithe": "self.forest.tithe",
    "reconcile": "self.forest.reconcile",
    "sip": "self.forest.sip",  # Could also be void.forest.sip
    "refine": "self.forest.refine",
    "define": "self.forest.define",
}


def cmd_forest(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    AGENTESE-native forest health operations.

    Routes CLI invocations to self.forest.* paths via the projection functor.
    """
    # Help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # Parse subcommand (default: manifest)
    subcommand = "manifest"
    for arg in args:
        if arg in FOREST_SUBCOMMAND_MAP:
            subcommand = arg
            break

    # Route to AGENTESE path
    path = FOREST_SUBCOMMAND_MAP.get(subcommand, "self.forest.manifest")

    # Parse kwargs from remaining args
    kwargs: dict[str, str | bool] = {}
    if "--execute" in args:
        kwargs["execute"] = True
    if "--commit" in args:
        kwargs["commit"] = True
    if "--json" in args:
        kwargs["json_output"] = True

    # Handle positional args (e.g., plan path for define)
    positional = [a for a in args if not a.startswith("-") and a not in FOREST_SUBCOMMAND_MAP]
    if positional and subcommand == "define":
        kwargs["path"] = positional[0]
    if positional and subcommand == "refine":
        kwargs["plan_path"] = positional[0]

    # Project through CLI functor
    from protocols.cli.projection import project_command

    return project_command(
        path=path,
        args=args,
        ctx=ctx,
        kwargs=kwargs,
    )
