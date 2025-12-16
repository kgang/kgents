"""
Forest Handler: AGENTESE-native forest health operations.

Replaces manual Chief of Staff reconciliation with self.forest.* paths.

Usage:
    kg forest                 # Show manifest (canopy view)
    kg forest manifest        # Generate _forest.md from plan headers
    kg forest status          # Generate _status.md content
    kg forest witness         # Show drift report
    kg forest tithe           # Archive stale plans (dry run)
    kg forest tithe --execute # Actually archive stale plans
    kg forest reconcile       # Full reconciliation
    kg forest reconcile --commit  # Reconcile and git commit

AGENTESE Paths:
    self.forest.manifest   - Canopy view from plan YAML headers
    self.forest.status     - Implementation status matrix
    self.forest.witness    - Drift report (what's stale)
    self.forest.tithe      - Archive stale plans
    self.forest.reconcile  - Full meta file reconciliation

> "The garden tends itself, but only because we planted it together."
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_forest(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    AGENTESE-native forest health operations.

    kg forest - Manage forest health via self.forest.* paths.
    """
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("forest", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # Determine subcommand
    subcommand = "manifest"  # default
    execute = "--execute" in args
    commit = "--commit" in args

    # Find subcommand
    for arg in args:
        if arg in ("manifest", "status", "witness", "tithe", "reconcile"):
            subcommand = arg
            break

    return asyncio.run(
        _async_forest(subcommand, execute=execute, commit=commit, ctx=ctx)
    )


class _MockDNA:
    """Mock DNA for CLI invocation."""

    def __init__(self, archetype: str = "ops") -> None:
        self.name = "cli-observer"
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class _MockObserver:
    """Mock observer for CLI invocation - satisfies Umwelt protocol."""

    def __init__(self, archetype: str = "ops") -> None:
        self.dna = _MockDNA(archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}


async def _async_forest(
    subcommand: str,
    execute: bool = False,
    commit: bool = False,
    ctx: "InvocationContext | None" = None,
) -> int:
    """Async implementation of forest command."""
    try:
        from protocols.agentese.contexts.forest import ForestNode, create_forest_node

        node: ForestNode = create_forest_node()

        # Create a simple observer (mock for CLI)
        observer = _MockObserver(archetype="ops")

        match subcommand:
            case "manifest":
                result = await node._invoke_aspect("manifest", observer)
                _emit_output(
                    result.content,
                    {"action": "manifest", "metadata": result.metadata},
                    ctx,
                )
                return 0

            case "status":
                result = await node._invoke_aspect("status", observer)
                _emit_output(
                    result.content,
                    {"action": "status", "metadata": result.metadata},
                    ctx,
                )
                return 0

            case "witness":
                result = await node._invoke_aspect("witness", observer)
                _emit_output(
                    result.content,
                    {"action": "witness", "metadata": result.metadata},
                    ctx,
                )
                return 0

            case "tithe":
                result = await node._invoke_aspect("tithe", observer, execute=execute)
                _emit_output(
                    result.content,
                    {"action": "tithe", "metadata": result.metadata},
                    ctx,
                )
                return 0

            case "reconcile":
                result = await node._invoke_aspect("reconcile", observer, commit=commit)
                _emit_output(
                    result.content,
                    {"action": "reconcile", "metadata": result.metadata},
                    ctx,
                )
                return 0

            case _:
                _emit_output(
                    f"Unknown subcommand: {subcommand}",
                    {"error": f"Unknown subcommand: {subcommand}"},
                    ctx,
                )
                return 1

    except ImportError as e:
        error_human = f"[FOREST] Import error: {e}"
        error_semantic = {"error": f"Import error: {e}"}
        _emit_output(error_human, error_semantic, ctx)
        return 1

    except Exception as e:
        error_human = f"[FOREST] Error: {e}"
        error_semantic = {"error": str(e)}
        _emit_output(error_human, error_semantic, ctx)
        return 1


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
