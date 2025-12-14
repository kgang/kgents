"""
List command for A-gent.

Lists available archetypes and registered agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import _emit_output

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def execute_list(json_mode: bool, ctx: "InvocationContext | None") -> int:
    """Handle 'a list' command."""
    try:
        from agents.a.archetypes import Delta, Kappa, Lambda  # noqa: F401

        # List known archetypes
        archetypes = [
            {
                "name": "Kappa",
                "description": "Full-stack: Stateful + Soulful + Observable + Streamable",
            },
            {"name": "Lambda", "description": "Minimal: Observable only"},
            {"name": "Delta", "description": "Data-focused: Stateful + Observable"},
        ]

        if json_mode:
            import json

            _emit_output(
                json.dumps({"archetypes": archetypes}, indent=2),
                {"archetypes": archetypes},
                ctx,
            )
        else:
            lines = [
                "[A] Available Archetypes:",
                "",
            ]
            for a in archetypes:
                lines.append(f"  {a['name']}")
                lines.append(f"    {a['description']}")
                lines.append("")

            lines.append("Use 'kgents a inspect <name>' for details.")
            _emit_output("\n".join(lines), {"archetypes": archetypes}, ctx)

        return 0

    except Exception as e:
        _emit_output(f"[A] Error listing agents: {e}", {"error": str(e)}, ctx)
        return 1
