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
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for a command."""
    print(__doc__)
    print()
    print("COMMANDS:")
    print("  inspect <agent>     Show Halo (capabilities) and Nucleus details")
    print("  manifest <agent>    Generate K8s manifests (YAML)")
    print("  run <agent>         Compile and run agent locally")
    print("  list                List available agents")
    print("  new <name>          Scaffold a new agent (interactive)")
    print()
    print("OPTIONS:")
    print("  --namespace <ns>    K8s namespace for manifests (default: kgents-agents)")
    print("  --input <data>      Input data for 'run' command")
    print("  --validate          Validate generated manifests (for 'manifest' command)")
    print("  --json              Output as JSON")
    print(
        "  --archetype <type>  Archetype for 'new' command (kappa|lambda|delta|minimal)"
    )
    print("  --output <path>     Output path for 'new' command")
    print("  --help, -h          Show this help")


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
        _print_help()
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
    match subcommand:
        case "inspect":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'inspect' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return _handle_inspect(agent_name, json_mode, ctx)

        case "manifest":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'manifest' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return _handle_manifest(
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
            return asyncio.run(_handle_run(agent_name, input_data, json_mode, ctx))

        case "list":
            return _handle_list(json_mode, ctx)

        case "new":
            if not agent_name:
                _emit_output(
                    "[A] Error: 'new' requires an agent name",
                    {"error": "Missing agent name"},
                    ctx,
                )
                return 1
            return _handle_new(agent_name, archetype, output_path, ctx)

        case _:
            _emit_output(
                f"[A] Unknown command: {subcommand}",
                {"error": f"Unknown command: {subcommand}"},
                ctx,
            )
            _print_help()
            return 1


def _resolve_agent_class(agent_name: str) -> type[Any] | None:
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


def _handle_inspect(
    agent_name: str, json_mode: bool, ctx: "InvocationContext | None"
) -> int:
    """Handle 'a inspect <agent>' command."""
    try:
        from agents.a.archetypes import get_archetype
        from agents.a.halo import get_halo

        agent_cls = _resolve_agent_class(agent_name)
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


def _handle_manifest(
    agent_name: str,
    namespace: str,
    json_mode: bool,
    validate_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'a manifest <agent>' command."""
    try:
        from system.projector import K8sProjector, manifests_to_yaml

        agent_cls = _resolve_agent_class(agent_name)
        if agent_cls is None:
            _emit_output(
                f"[A] Agent not found: {agent_name}",
                {"error": f"Agent not found: {agent_name}"},
                ctx,
            )
            return 1

        # Compile to K8s manifests
        projector = K8sProjector(namespace=namespace)
        resources = projector.compile(agent_cls)

        # Validate if requested
        if validate_mode:
            validation_result = _validate_manifests(resources)
            if not validation_result["valid"]:
                _emit_output(
                    f"[A] Validation failed: {validation_result['errors']}",
                    {"valid": False, "errors": validation_result["errors"]},
                    ctx,
                )
                return 1

        if json_mode:
            import json

            manifests = [r.to_dict() for r in resources]
            result: dict[str, Any] = {"manifests": manifests, "count": len(resources)}
            if validate_mode:
                result["valid"] = True
                result["message"] = f"Generated {len(resources)} valid K8s resources"
            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            yaml_output = manifests_to_yaml(resources)
            if validate_mode:
                _emit_output(
                    f"[A] Generated {len(resources)} valid K8s resources\n---\n{yaml_output}",
                    {"manifest_count": len(resources), "valid": True},
                    ctx,
                )
            else:
                _emit_output(yaml_output, {"manifest_count": len(resources)}, ctx)

        return 0

    except Exception as e:
        _emit_output(f"[A] Error generating manifests: {e}", {"error": str(e)}, ctx)
        return 1


def _validate_manifests(resources: list[Any]) -> dict[str, Any]:
    """
    Validate K8s manifests for correctness.

    Checks:
    - Required fields present (apiVersion, kind, metadata.name)
    - Names are RFC 1123 compliant
    - Namespace is set on all resources
    - No duplicate resource names within same kind

    Returns:
        dict with 'valid' bool and 'errors' list
    """
    import re

    rfc1123 = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
    errors: list[str] = []
    seen: dict[str, set[str]] = {}  # kind -> set of names

    for r in resources:
        d = r.to_dict()

        # Check required fields
        if "apiVersion" not in d:
            errors.append(f"Missing apiVersion in {r.kind}")
        if "kind" not in d:
            errors.append("Missing kind")
        if "metadata" not in d or "name" not in d.get("metadata", {}):
            errors.append(f"Missing metadata.name in {r.kind}")
            continue

        name = d["metadata"]["name"]
        kind = d["kind"]

        # RFC 1123 validation
        if not rfc1123.match(name):
            errors.append(f"Invalid name '{name}' in {kind}: not RFC 1123 compliant")

        # Length check
        if len(name) > 63:
            errors.append(f"Name '{name}' in {kind} exceeds 63 chars")

        # Namespace check
        if "namespace" not in d.get("metadata", {}):
            errors.append(f"Missing namespace in {kind}/{name}")

        # Duplicate check
        if kind not in seen:
            seen[kind] = set()
        if name in seen[kind]:
            errors.append(f"Duplicate {kind} name: {name}")
        seen[kind].add(name)

    return {"valid": len(errors) == 0, "errors": errors}


async def _handle_run(
    agent_name: str,
    input_data: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle 'a run <agent>' command."""
    try:
        from system.projector import LocalProjector

        agent_cls = _resolve_agent_class(agent_name)
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


def _handle_list(json_mode: bool, ctx: "InvocationContext | None") -> int:
    """Handle 'a list' command."""
    try:
        from agents.a.archetypes import Delta, Kappa, Lambda

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


def _emit_output(
    human: str, semantic: dict[str, Any], ctx: "InvocationContext | None"
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


# --- Scaffolding Templates ---

_TEMPLATES = {
    "minimal": '''"""
{name}: A minimal agent.

Run:
    python -m {module_path}
"""

import asyncio

from bootstrap.types import Agent


class {class_name}(Agent[str, str]):
    """
    {description}

    Type: Agent[str, str]
    Input: A string
    Output: A processed string
    """

    @property
    def name(self) -> str:
        return "{snake_name}"

    async def invoke(self, input: str) -> str:
        return f"Processed: {{input}}"


async def main() -> None:
    agent = {class_name}()
    result = await agent.invoke("hello")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
''',
    "kappa": '''"""
{name}: A full-stack Kappa agent.

Kappa = Stateful + Soulful + Observable + Streamable

Run:
    python -m {module_path}
"""

import asyncio
from dataclasses import dataclass, field

from agents.a import Kappa, get_halo


@dataclass
class {class_name}State:
    """State schema for {class_name}."""

    call_count: int = 0
    history: list[str] = field(default_factory=list)


class {class_name}(Kappa[str, str]):
    """
    {description}

    Type: Kappa[str, str] (full-stack agent)
    Input: A string
    Output: A processed string

    Capabilities:
    - Stateful: Persists state across invocations
    - Soulful: Persona-aware via K-gent
    - Observable: Emits telemetry
    - Streamable: Can be lifted to Flux domain
    """

    def __init__(self) -> None:
        self._state = {class_name}State()

    @property
    def name(self) -> str:
        return "{snake_name}"

    async def invoke(self, input: str) -> str:
        self._state.call_count += 1
        self._state.history.append(input)
        return f"[Call #{{self._state.call_count}}] {{input}}"


async def main() -> None:
    agent = {class_name}()

    # Multiple invocations to show state
    for msg in ["hello", "world", "kgents"]:
        result = await agent.invoke(msg)
        print(result)

    # Inspect capabilities
    halo = get_halo({class_name})
    print(f"\\nCapabilities: {{[type(c).__name__ for c in halo]}}")


if __name__ == "__main__":
    asyncio.run(main())
''',
    "lambda": '''"""
{name}: A minimal Lambda agent.

Lambda = Observable only (the lightest archetype)

Run:
    python -m {module_path}
"""

import asyncio

from agents.a import Lambda, get_halo


class {class_name}(Lambda[str, str]):
    """
    {description}

    Type: Lambda[str, str] (minimal agent)
    Input: A string
    Output: A processed string

    Capabilities:
    - Observable: Emits telemetry (can be monitored)
    """

    @property
    def name(self) -> str:
        return "{snake_name}"

    async def invoke(self, input: str) -> str:
        return f"Lambda processed: {{input}}"


async def main() -> None:
    agent = {class_name}()
    result = await agent.invoke("hello")
    print(result)

    # Inspect capabilities
    halo = get_halo({class_name})
    print(f"Capabilities: {{[type(c).__name__ for c in halo]}}")


if __name__ == "__main__":
    asyncio.run(main())
''',
    "delta": '''"""
{name}: A data-focused Delta agent.

Delta = Stateful + Observable (data-focused archetype)

Run:
    python -m {module_path}
"""

import asyncio
from dataclasses import dataclass, field

from agents.a import Delta, get_halo


@dataclass
class {class_name}State:
    """State schema for {class_name}."""

    records: list[dict] = field(default_factory=list)


class {class_name}(Delta[str, str]):
    """
    {description}

    Type: Delta[str, str] (data-focused agent)
    Input: A string
    Output: A processed string

    Capabilities:
    - Stateful: Persists data across invocations
    - Observable: Emits telemetry
    """

    def __init__(self) -> None:
        self._state = {class_name}State()

    @property
    def name(self) -> str:
        return "{snake_name}"

    async def invoke(self, input: str) -> str:
        record = {{"input": input, "index": len(self._state.records)}}
        self._state.records.append(record)
        return f"Stored record #{{record['index']}}: {{input}}"


async def main() -> None:
    agent = {class_name}()

    for data in ["alpha", "beta", "gamma"]:
        result = await agent.invoke(data)
        print(result)

    print(f"\\nTotal records: {{len(agent._state.records)}}")

    # Inspect capabilities
    halo = get_halo({class_name})
    print(f"Capabilities: {{[type(c).__name__ for c in halo]}}")


if __name__ == "__main__":
    asyncio.run(main())
''',
}


def _to_pascal_case(name: str) -> str:
    """Convert snake_case or kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


def _to_snake_case(name: str) -> str:
    """Convert PascalCase or kebab-case to snake_case."""
    import re

    # Handle kebab-case
    name = name.replace("-", "_")
    # Handle PascalCase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _handle_new(
    agent_name: str,
    archetype: str,
    output_path: str | None,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'a new <name>' command.

    Scaffolds a new agent with the given name and archetype.
    """
    import os
    from pathlib import Path

    # Validate archetype
    archetype = archetype.lower()
    if archetype not in _TEMPLATES:
        _emit_output(
            f"[A] Unknown archetype: {archetype}. Options: {', '.join(_TEMPLATES.keys())}",
            {"error": f"Unknown archetype: {archetype}"},
            ctx,
        )
        return 1

    # Generate names
    class_name = _to_pascal_case(agent_name)
    snake_name = _to_snake_case(agent_name)

    # Determine output path
    if output_path is None:
        output_path = f"{snake_name}.py"

    path = Path(output_path)

    # Check if file exists
    if path.exists():
        _emit_output(
            f"[A] File already exists: {output_path}",
            {"error": f"File exists: {output_path}"},
            ctx,
        )
        return 1

    # Generate module path (for docstring)
    if path.suffix == ".py":
        module_path = str(path.with_suffix("")).replace(os.sep, ".")
    else:
        module_path = snake_name

    # Generate content
    template = _TEMPLATES[archetype]
    content = template.format(
        name=agent_name,
        class_name=class_name,
        snake_name=snake_name,
        module_path=module_path,
        description=f"A {archetype} agent scaffolded by kgents.",
    )

    # Write file
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

        _emit_output(
            f"[A] Created {archetype} agent: {output_path}\n"
            f"    Class: {class_name}\n"
            f"    Run: python {output_path}",
            {
                "created": str(output_path),
                "class_name": class_name,
                "archetype": archetype,
            },
            ctx,
        )
        return 0

    except Exception as e:
        _emit_output(
            f"[A] Error creating agent: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1
