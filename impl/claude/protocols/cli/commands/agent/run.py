"""
Run command for A-gent.

Compiles and runs an agent locally via LocalProjector.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import _emit_output
from .inspect import resolve_agent_class

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


async def execute_run(
    agent_name: str,
    input_data: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'a run <agent>' command."""
    try:
        from system.projector import LocalProjector

        agent_cls = resolve_agent_class(agent_name)
        if agent_cls is None:
            _emit_output(
                f"[A] Agent not found: {agent_name}",
                {"error": f"Agent not found: {agent_name}"},
                ctx,
            )
            return 1

        # Check if it's an abstract archetype
        from agents.a.archetypes import Delta, Kappa, Lambda

        if agent_cls in (Kappa, Lambda, Delta):
            _emit_output(
                f"[A] Cannot run '{agent_name}' directly - it's an abstract archetype.\n"
                f"    Archetypes must be subclassed with concrete implementations.\n\n"
                f"    Example:\n"
                f"      class MyService({agent_name}[str, str]):\n"
                f"          @property\n"
                f"          def name(self): return 'my-service'\n"
                f"          async def invoke(self, x): return x.upper()\n\n"
                f"    Then run: kgents a run my_module.MyService",
                {
                    "error": f"Abstract archetype: {agent_name}",
                    "hint": "subclass required",
                },
                ctx,
            )
            return 1

        # Compile with LocalProjector
        projector = LocalProjector()
        compiled = projector.compile(agent_cls)

        _emit_output(f"[A] Compiled: {compiled.name}", {"compiled": compiled.name}, ctx)

        # If input provided, invoke
        if input_data is not None:
            result = await compiled.invoke(input_data)

            if json_mode:
                import json

                output = {
                    "agent": compiled.name,
                    "input": input_data,
                    "output": str(result),
                }
                _emit_output(json.dumps(output, indent=2), output, ctx)
            else:
                _emit_output(f"[A] Output: {result}", {"output": str(result)}, ctx)
        else:
            _emit_output(
                "[A] Agent compiled. Use --input to invoke.",
                {"status": "compiled"},
                ctx,
            )

        return 0

    except Exception as e:
        _emit_output(f"[A] Error running agent: {e}", {"error": str(e)}, ctx)
        return 1
