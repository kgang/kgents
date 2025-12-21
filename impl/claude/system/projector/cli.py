"""
CLIProjector: Compiles agent Halo to shell-executable Python scripts.

The CLIProjector reads an agent's declarative capabilities (Halo)
and produces a standalone Python script that can be executed from
the command line.

Capability Mapping:
| Capability  | CLI Script Feature                                  |
|-------------|-----------------------------------------------------|
| @Stateful   | State persistence to JSON file                      |
| @Soulful    | Persona name in output banner                       |
| @Observable | Metrics printed to stderr                           |
| @Streamable | Streaming output with SSE-like format               |
| @TurnBased  | Turn recording to local weave file                  |

The Alethic Isomorphism:
    Same Halo + LocalProjector  → Runnable Python object
    Same Halo + K8sProjector    → K8s Manifests
    Same Halo + CLIProjector    → Executable shell script
    All produce semantically equivalent agents.

Example:
    >>> @Capability.Stateful(schema=dict)
    ... @Capability.Streamable(budget=5.0)
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> script = CLIProjector().compile(MyAgent)
    >>> # script is executable Python code
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .base import Projector, UnsupportedCapabilityError

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from agents.poly.types import Agent


@dataclass
class CLIProjector(Projector[str]):
    """
    Compiles agent Halo into executable CLI script.

    The CLIProjector reads capability decorators and produces
    a standalone Python script with appropriate CLI behavior.

    Configuration:
        shebang: Shebang line (default: #!/usr/bin/env python)
        include_banner: Whether to print agent info on startup
        state_dir: Directory for state persistence (default: ~/.kgents/cli-state)

    Example:
        >>> @Capability.Stateful(schema=dict)
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> script = CLIProjector().compile(MyAgent)
        >>> print(script)  # Executable Python script
    """

    shebang: str = "#!/usr/bin/env python"
    include_banner: bool = True
    state_dir: str = "~/.kgents/cli-state"

    @property
    def name(self) -> str:
        return "CLIProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> str:
        """
        Compile agent class to executable CLI script.

        Reads the agent's Halo and produces a Python script that:
        - Reads input from stdin or argv
        - Invokes the agent
        - Prints output to stdout
        - Handles state/streaming/metrics based on capabilities

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Executable Python script as string

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
        """
        from agents.a.halo import get_halo

        # Helper functions for capability lookup by name
        halo = get_halo(agent_cls)

        def _has_cap(cap_name: str) -> bool:
            return any(type(c).__name__ == cap_name for c in halo)

        def _get_cap(cap_name: str) -> Any:
            for c in halo:
                if type(c).__name__ == cap_name:
                    return c
            return None

        # Validate capabilities
        supported_type_names = {
            "StatefulCapability",
            "SoulfulCapability",
            "ObservableCapability",
            "StreamableCapability",
            "TurnBasedCapability",
        }

        for cap in halo:
            if type(cap).__name__ not in supported_type_names:
                raise UnsupportedCapabilityError(type(cap), self.name)

        # Extract capability details
        stateful_cap = _get_cap("StatefulCapability")
        soulful_cap = _get_cap("SoulfulCapability")
        observable_cap = _get_cap("ObservableCapability")
        streamable_cap = _get_cap("StreamableCapability")
        turnbased_cap = _get_cap("TurnBasedCapability")

        # Build script components
        module_name = agent_cls.__module__
        class_name = agent_cls.__name__
        agent_name = self._derive_script_name(agent_cls)

        # Generate script sections
        imports = self._generate_imports(
            has_stateful=stateful_cap is not None,
            has_observable=observable_cap is not None,
            has_streamable=streamable_cap is not None,
            has_turnbased=turnbased_cap is not None,
        )

        banner = (
            self._generate_banner(
                agent_name=agent_name,
                persona=soulful_cap.persona if soulful_cap else None,
            )
            if self.include_banner
            else ""
        )

        state_handling = (
            self._generate_state_handling(
                agent_name=agent_name,
                stateful_cap=stateful_cap,
            )
            if stateful_cap
            else ""
        )

        metrics_handling = (
            self._generate_metrics_handling(
                observable_cap=observable_cap,
            )
            if observable_cap and observable_cap.metrics
            else ""
        )

        main_logic = self._generate_main_logic(
            module_name=module_name,
            class_name=class_name,
            has_stateful=stateful_cap is not None,
            has_streamable=streamable_cap is not None,
            streamable_cap=streamable_cap,
        )

        # Assemble script
        script_parts = [
            self.shebang,
            '"""',
            f"CLI script for {class_name} agent.",
            "",
            "Generated by CLIProjector from kgents.",
            "",
            "Usage:",
            f"    ./{agent_name}.py <input>",
            f"    echo 'input' | ./{agent_name}.py",
            '"""',
            "",
            imports,
            "",
        ]

        if banner:
            script_parts.extend([banner, ""])

        if state_handling:
            script_parts.extend([state_handling, ""])

        if metrics_handling:
            script_parts.extend([metrics_handling, ""])

        script_parts.extend(
            [
                main_logic,
                "",
                'if __name__ == "__main__":',
                "    main()",
            ]
        )

        return "\n".join(script_parts)

    def _derive_script_name(self, agent_cls: type) -> str:
        """Convert CamelCase class name to kebab-case script name."""
        name = agent_cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        return "".join(result)

    def _generate_imports(
        self,
        has_stateful: bool,
        has_observable: bool,
        has_streamable: bool,
        has_turnbased: bool,
    ) -> str:
        """Generate import statements."""
        imports = [
            "import asyncio",
            "import sys",
        ]

        if has_stateful:
            imports.extend(
                [
                    "import json",
                    "from pathlib import Path",
                ]
            )

        if has_observable:
            imports.append("import time")

        if has_streamable:
            imports.append("from typing import AsyncIterator")

        return "\n".join(imports)

    def _generate_banner(
        self,
        agent_name: str,
        persona: str | None,
    ) -> str:
        """Generate startup banner."""
        persona_line = f'    print(f"  Persona: {persona}", file=sys.stderr)' if persona else ""

        return textwrap.dedent(f'''
            def print_banner():
                """Print agent info banner."""
                print(f"\\n=== {agent_name} ===", file=sys.stderr)
                {persona_line}
                print("", file=sys.stderr)
        ''').strip()

    def _generate_state_handling(
        self,
        agent_name: str,
        stateful_cap: Any,
    ) -> str:
        """Generate state persistence code."""
        state_dir = self.state_dir

        return textwrap.dedent(f'''
            STATE_FILE = Path("{state_dir}").expanduser() / "{agent_name}-state.json"


            def load_state() -> dict:
                """Load persisted state."""
                STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                if STATE_FILE.exists():
                    return json.loads(STATE_FILE.read_text())
                return {{}}


            def save_state(state: dict) -> None:
                """Persist state to disk."""
                STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                STATE_FILE.write_text(json.dumps(state, indent=2))
        ''').strip()

    def _generate_metrics_handling(
        self,
        observable_cap: Any,
    ) -> str:
        """Generate metrics output code."""
        return textwrap.dedent('''
            def print_metrics(start_time: float, result: str) -> None:
                """Print metrics to stderr."""
                elapsed = time.time() - start_time
                print(f"\\n--- Metrics ---", file=sys.stderr)
                print(f"  Latency: {elapsed:.3f}s", file=sys.stderr)
                print(f"  Output length: {len(result)} chars", file=sys.stderr)
        ''').strip()

    def _generate_main_logic(
        self,
        module_name: str,
        class_name: str,
        has_stateful: bool,
        has_streamable: bool,
        streamable_cap: Any,
    ) -> str:
        """Generate main function logic."""
        # Import line
        import_line = f"from {module_name} import {class_name}"

        # Input handling
        input_handling = textwrap.dedent("""
            # Get input from argv or stdin
            if len(sys.argv) > 1:
                input_data = " ".join(sys.argv[1:])
            elif not sys.stdin.isatty():
                input_data = sys.stdin.read().strip()
            else:
                print("Usage: script.py <input> OR echo 'input' | script.py", file=sys.stderr)
                sys.exit(1)
        """).strip()

        # Agent instantiation
        if has_stateful:
            agent_setup = textwrap.dedent(f"""
                # Create agent with loaded state
                {import_line}
                from system.projector import LocalProjector

                agent = LocalProjector().compile({class_name})

                # Load persisted state
                loaded_state = load_state()
                if loaded_state:
                    await agent.update_state(loaded_state)
            """).strip()
        else:
            agent_setup = textwrap.dedent(f"""
                # Create agent
                {import_line}
                from system.projector import LocalProjector

                agent = LocalProjector().compile({class_name})
            """).strip()

        # Invocation and output
        if has_streamable:
            invoke_logic = textwrap.dedent("""
                # Stream processing
                async def source():
                    yield input_data

                async for chunk in agent.start(source()):
                    print(chunk, flush=True)
            """).strip()
        else:
            invoke_logic = textwrap.dedent("""
                # Single invocation
                result = await agent.invoke(input_data)
                print(result)
            """).strip()

        # State saving
        state_save = ""
        if has_stateful:
            state_save = textwrap.dedent("""
                # Persist updated state
                save_state(agent.state)
            """).strip()

        # Assemble main function
        main_body = "\n    ".join(
            [
                input_handling.replace("\n", "\n    "),
                "",
                agent_setup.replace("\n", "\n    "),
                "",
                invoke_logic.replace("\n", "\n    "),
            ]
        )

        if state_save:
            main_body += "\n    \n    " + state_save.replace("\n", "\n    ")

        return textwrap.dedent(f'''
            async def _main():
                {main_body}


            def main():
                """Entry point."""
                asyncio.run(_main())
        ''').strip()

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if CLIProjector supports a capability type.

        CLIProjector supports all five standard capabilities.

        Args:
            capability: The capability type to check

        Returns:
            True if capability is supported
        """
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
            TurnBasedCapability,
        )

        return capability in {
            StatefulCapability,
            SoulfulCapability,
            ObservableCapability,
            StreamableCapability,
            TurnBasedCapability,
        }
