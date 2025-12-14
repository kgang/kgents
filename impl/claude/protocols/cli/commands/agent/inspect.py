"""
Inspect command for A-gent.

Shows Halo (capabilities) and Nucleus details for an agent.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from . import _emit_output

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def resolve_agent_class(agent_name: str) -> type[Any] | None:
    """
    Resolve agent name to agent class.

    Lookup order:
    1. Check agents.a.archetypes (Kappa, Lambda, Delta)
    2. Check FunctorRegistry for registered agents
    3. Try to import from agents.* modules
    """
    # 1. Check archetypes
    try:
        from agents.a.archetypes import Delta, Kappa, Lambda

        archetype_map = {
            "kappa": Kappa,
            "lambda": Lambda,
            "delta": Delta,
        }
        if agent_name.lower() in archetype_map:
            return archetype_map[agent_name.lower()]
    except ImportError:
        pass

    # 2. Try to import as module.ClassName
    if "." in agent_name:
        try:
            module_path, class_name = agent_name.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls if isinstance(cls, type) else None
        except (ImportError, AttributeError):
            pass

    # 3. Try common agent locations
    agent_modules = [
        "agents.a.archetypes",
        "agents.k",
        "agents.flux",
    ]

    for module_path in agent_modules:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, agent_name):
                cls = getattr(module, agent_name)
                return cls if isinstance(cls, type) else None
        except ImportError:
            pass

    return None


def execute_inspect(
    agent_name: str, json_mode: bool, ctx: "InvocationContext | None"
) -> int:
    """Handle 'a inspect <agent>' command."""
    try:
        from agents.a.archetypes import get_archetype
        from agents.a.halo import get_halo

        agent_cls = resolve_agent_class(agent_name)
        if agent_cls is None:
            _emit_output(
                f"[A] Agent not found: {agent_name}",
                {"error": f"Agent not found: {agent_name}"},
                ctx,
            )
            return 1

        # Get Halo (capabilities)
        halo = get_halo(agent_cls)
        capabilities: list[dict[str, Any]] = []
        for cap in halo:
            config = {}
            for k, v in vars(cap).items():
                if k.startswith("_"):
                    continue
                # Convert type objects to string names for JSON serialization
                if isinstance(v, type):
                    config[k] = v.__name__
                else:
                    config[k] = v
            capabilities.append(
                {
                    "name": type(cap).__name__,
                    "config": config,
                }
            )

        # Get archetype
        archetype = get_archetype(agent_cls)
        archetype_name = archetype.__name__ if archetype else None

        # Build output
        result = {
            "agent": agent_cls.__name__,
            "archetype": archetype_name,
            "capabilities": capabilities,
            "nucleus": {
                "module": agent_cls.__module__,
                "doc": agent_cls.__doc__[:200] if agent_cls.__doc__ else None,
            },
        }

        if json_mode:
            import json

            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            lines = [
                f"[A] Agent: {agent_cls.__name__}",
                "",
            ]

            if archetype_name:
                lines.append(f"  Archetype: {archetype_name}")

            lines.append("")
            lines.append("  Capabilities:")

            if not capabilities:
                lines.append("    (none)")
            else:
                for cap_info in capabilities:
                    config_str = ", ".join(
                        f"{k}={v}" for k, v in cap_info["config"].items()
                    )
                    lines.append(f"    @{cap_info['name']}({config_str})")

            lines.append("")
            lines.append(f"  Module: {agent_cls.__module__}")

            if agent_cls.__doc__:
                lines.append("")
                lines.append(f"  Doc: {agent_cls.__doc__[:100]}...")

            _emit_output("\n".join(lines), result, ctx)

        return 0

    except Exception as e:
        _emit_output(f"[A] Error inspecting {agent_name}: {e}", {"error": str(e)}, ctx)
        return 1
