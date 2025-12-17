"""
New/scaffold command for A-gent.

Scaffolds a new agent with the given name and archetype.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from . import _emit_output

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# --- Scaffolding Templates ---

_TEMPLATES = {
    "minimal": '''"""
{name}: A minimal agent.

Run:
    python -m {module_path}
"""

import asyncio

from agents.poly.types import Agent


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
    # Handle kebab-case
    name = name.replace("-", "_")
    # Handle PascalCase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def execute_new(
    agent_name: str,
    archetype: str,
    output_path: str | None,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'a new <name>' command.

    Scaffolds a new agent with the given name and archetype.
    """
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
