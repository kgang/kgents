"""
A-gent Handler: Alethic Architecture CLI interface.

The Alethic Architecture provides "batteries included" agent deployment:
1. Nucleus: Pure Agent[A, B] logic
2. Halo: Declarative @Capability.* metadata
3. Projector: Target-specific compilation

Usage:
    kgents a                       # Show help
    kgents a inspect <agent>       # Show Halo + Nucleus details
    kgents a manifest <agent>      # K8sProjector -> YAML output
    kgents a run <agent>           # LocalProjector -> run agent
    kgents a list                  # List registered agents

Examples:
    kgents a inspect MyKappaService
    -> Shows: capabilities, archetype, functor chain

    kgents a manifest MyKappaService > deployment.yaml
    -> Produces K8s manifests for kubectl apply

    kgents a run MyKappaService --input "hello"
    -> Compiles with LocalProjector and invokes

This module is a thin router. Implementation is in commands/agent/.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

# Import from commands/agent/ for implementation
from protocols.cli.commands.agent import DIALOGUE_AGENTS, print_help

# Re-export for backward compatibility (tests import from here)
from protocols.cli.commands.agent.dialogue import (
    execute_dialogue,
    resolve_dialogue_agent,
)
from protocols.cli.commands.agent.inspect import execute_inspect, resolve_agent_class
from protocols.cli.commands.agent.list import execute_list
from protocols.cli.commands.agent.manifest import execute_manifest
from protocols.cli.commands.agent.new import execute_new
from protocols.cli.commands.agent.run import execute_run

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Backward compatibility aliases for tests
_handle_dialogue = execute_dialogue
_handle_inspect = execute_inspect
_handle_manifest = execute_manifest
_handle_run = execute_run
_handle_list = execute_list
_handle_new = execute_new
_resolve_agent_class = resolve_agent_class
_resolve_dialogue_agent = resolve_dialogue_agent

# Re-export DIALOGUE_AGENTS at module level
__all__ = [
    "DIALOGUE_AGENTS",
    "cmd_a",
    # Backward compatibility
    "_handle_dialogue",
    "_handle_inspect",
    "_handle_manifest",
    "_handle_run",
    "_handle_list",
    "_handle_new",
    "_resolve_agent_class",
    "_resolve_dialogue_agent",
]


def cmd_a(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    A-gent: Alethic Architecture CLI.

    kgents a - Inspect, compile, and deploy agents via the Alethic Architecture.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("a", args)
        except ImportError:
            pass

    if "--help" in args or "-h" in args or not args:
        print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    validate_mode = "--validate" in args
    namespace = "kgents-agents"
    archetype = "minimal"
    output_path = None

    # Parse --namespace, --archetype, --output
    for i, arg in enumerate(args):
        if arg == "--namespace" and i + 1 < len(args):
            namespace = args[i + 1]
        elif arg == "--archetype" and i + 1 < len(args):
            archetype = args[i + 1]
        elif arg == "--output" and i + 1 < len(args):
            output_path = args[i + 1]

    # Get subcommand
    subcommand = None
    agent_name = None
    input_data = None

    positional: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("-"):
            if arg in (
                "--namespace",
                "--input",
                "--archetype",
                "--output",
            ) and i + 1 < len(args):
                if arg == "--input":
                    input_data = args[i + 1]
                i += 2
                continue
            i += 1
            continue
        positional.append(arg)
        i += 1

    if positional:
        subcommand = positional[0]
    if len(positional) > 1:
        agent_name = positional[1]

    # Dispatch
    return _dispatch(
        subcommand=subcommand,
        agent_name=agent_name,
        json_mode=json_mode,
        validate_mode=validate_mode,
        namespace=namespace,
        archetype=archetype,
        output_path=output_path,
        input_data=input_data,
        ctx=ctx,
    )


def _dispatch(
    subcommand: str | None,
    agent_name: str | None,
    json_mode: bool,
    validate_mode: bool,
    namespace: str,
    archetype: str,
    output_path: str | None,
    input_data: str | None,
    ctx: "InvocationContext | None",
) -> int:
    """Route to the appropriate command handler."""
    from protocols.cli.commands.agent import _emit_output

    match subcommand:
        case "inspect":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'inspect' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return execute_inspect(agent_name, json_mode, ctx)

        case "manifest":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'manifest' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return execute_manifest(
                agent_name, namespace, json_mode, validate_mode, ctx
            )

        case "run":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'run' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return asyncio.run(execute_run(agent_name, input_data, json_mode, ctx))

        case "list":
            return execute_list(json_mode, ctx)

        case "new":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'new' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return execute_new(agent_name, archetype, output_path, ctx)

        case _:
            # Check if subcommand is a dialogue agent
            if subcommand and subcommand in DIALOGUE_AGENTS:
                # agent_name becomes the prompt (positional[1] if exists)
                prompt = agent_name  # agent_name = positional[1], which is the prompt
                return asyncio.run(execute_dialogue(subcommand, prompt, json_mode, ctx))

            _emit_output(
                f"[A] Unknown command: {subcommand}",
                {"error": f"Unknown command: {subcommand}"},
                ctx,
            )
            print_help()
            return 1
