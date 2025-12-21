"""
MarimoProjector: Compiles agent Halo to marimo notebook cell.

The MarimoProjector reads an agent's declarative capabilities (Halo)
and produces a marimo notebook cell that enables interactive agent exploration.

WHY THIS EXISTS:
PROBABILISTIC reality agents benefit from interactive exploration.
Marimo's reactive cells enable state inspection, input experimentation,
and real-time observation of agent behavior.

Capability Mapping:
| Capability  | Marimo Feature                                    |
|-------------|---------------------------------------------------|
| @Stateful   | mo.state() for persistence across runs            |
| @Soulful    | Persona badge in cell UI                          |
| @Observable | Metrics sidebar with mo.callout()                 |
| @Streamable | mo.status.progress_bar() for streaming output     |
| @TurnBased  | State inspector for weave files                   |

The Alethic Isomorphism:
    Same Halo + LocalProjector  → Runnable Python object
    Same Halo + K8sProjector    → K8s Manifests
    Same Halo + CLIProjector    → Executable shell script
    Same Halo + DockerProjector → Dockerfile
    Same Halo + WASMProjector   → Sandboxed HTML bundle
    Same Halo + MarimoProjector → Interactive notebook cell
    All produce semantically equivalent agents.

Example:
    >>> @Capability.Stateful(schema=MyState)
    ... @Capability.Observable(metrics=["latency"])
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> cell = MarimoProjector().compile(MyAgent)
    >>> # cell is marimo Python cell source code
"""

from __future__ import annotations

import inspect
import textwrap
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .base import Projector, UnsupportedCapabilityError

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from agents.poly.types import Agent


@dataclass
class MarimoArtifact:
    """
    Result of MarimoProjector compilation.

    Contains the marimo cell source and metadata for downstream use.
    """

    cell_source: str
    agent_name: str
    agent_source: str
    uses_state: bool = False
    uses_streaming: bool = False
    uses_metrics: bool = False
    exposed_inputs: list[str] = field(default_factory=list)

    def save(self, path: str) -> None:
        """Write cell source to Python file."""
        from pathlib import Path

        Path(path).write_text(self.cell_source)


@dataclass
class MarimoProjector(Projector[str]):
    """
    Compiles agent Halo into marimo notebook cell.

    The MarimoProjector reads capability decorators and produces
    Python source code that runs as a marimo cell with reactive
    widgets for agent exploration.

    This is the INTERACTIVE exploration target:
    - Real-time input/output experimentation
    - State persistence across cell runs
    - Observable metrics in sidebar
    - Streaming progress indicators

    Configuration:
        include_imports: Whether to include marimo imports (True for standalone)
        show_source: Whether to include agent source in a collapsible section
        theme: UI theme hint for styling

    Example:
        >>> @Capability.Stateful(schema=dict)
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> cell = MarimoProjector().compile(MyAgent)
        >>> # Run cell in marimo notebook for interactive exploration
    """

    include_imports: bool = True
    show_source: bool = True
    theme: str = "minimal"  # light | dark | minimal

    @property
    def name(self) -> str:
        return "MarimoProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> str:
        """
        Compile agent class to marimo cell source.

        Reads the agent's Halo and produces Python code that:
        - Creates reactive input widgets via mo.ui
        - Instantiates and runs the agent
        - Displays output with appropriate formatting
        - Persists state via mo.state() if @Stateful
        - Shows metrics if @Observable

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Marimo cell Python source code as string

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
        """
        from agents.a.halo import get_halo

        halo = get_halo(agent_cls)

        # Helper to find capabilities by name
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

        # Get agent metadata
        agent_name = self._derive_agent_name(agent_cls)
        class_name = agent_cls.__name__

        # Extract agent source code
        agent_source = self._extract_source(agent_cls)

        # Build cell sections
        parts = []

        # 1. Imports
        if self.include_imports:
            parts.append(
                self._generate_imports(
                    has_stateful=stateful_cap is not None,
                    has_observable=observable_cap is not None,
                    has_streamable=streamable_cap is not None,
                )
            )

        # 2. Agent definition (embedded)
        parts.append(self._generate_agent_definition(agent_source))

        # 3. State management
        if stateful_cap is not None or turnbased_cap is not None:
            parts.append(self._generate_state_management(agent_name))

        # 4. Main cell UI
        parts.append(
            self._generate_main_cell(
                agent_name=agent_name,
                class_name=class_name,
                persona=getattr(soulful_cap, "persona", None) if soulful_cap else None,
                has_stateful=stateful_cap is not None,
                has_observable=observable_cap is not None,
                has_streamable=streamable_cap is not None,
            )
        )

        # 5. Source viewer (optional)
        if self.show_source:
            parts.append(self._generate_source_viewer(agent_source, class_name))

        return "\n\n".join(parts)

    def compile_artifact(self, agent_cls: type["Agent[Any, Any]"]) -> MarimoArtifact:
        """
        Compile to MarimoArtifact for composition with other projectors.

        Returns structured artifact with metadata for downstream use.
        """
        from agents.a.halo import get_halo

        halo = get_halo(agent_cls)

        def _has_cap(cap_name: str) -> bool:
            return any(type(c).__name__ == cap_name for c in halo)

        cell_source = self.compile(agent_cls)
        agent_source = self._extract_source(agent_cls)

        return MarimoArtifact(
            cell_source=cell_source,
            agent_name=self._derive_agent_name(agent_cls),
            agent_source=agent_source,
            uses_state=_has_cap("StatefulCapability") or _has_cap("TurnBasedCapability"),
            uses_streaming=_has_cap("StreamableCapability"),
            uses_metrics=_has_cap("ObservableCapability"),
            exposed_inputs=["text_input"],  # Default input type
        )

    def _derive_agent_name(self, agent_cls: type) -> str:
        """Convert CamelCase class name to kebab-case."""
        name = agent_cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        return "".join(result)

    def _extract_source(self, agent_cls: type) -> str:
        """Extract agent class source code, stripping capability decorators."""
        try:
            source = inspect.getsource(agent_cls)
            # Strip @Capability.* decorators - they're already processed
            lines = source.split("\n")
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip decorator lines that start with @Capability
                if stripped.startswith("@Capability"):
                    continue
                filtered_lines.append(line)
            return "\n".join(filtered_lines)
        except (OSError, TypeError):
            # Fallback for dynamically created classes
            return f"# Source not available for {agent_cls.__name__}"

    def _generate_imports(
        self,
        has_stateful: bool,
        has_observable: bool,
        has_streamable: bool,
    ) -> str:
        """Generate marimo import statements."""
        imports = [
            "import marimo as mo",
            "import asyncio",
            "from dataclasses import dataclass",
            "from typing import TypeVar, Generic, Any",
            "from abc import ABC, abstractmethod",
        ]

        if has_observable:
            imports.append("import time")

        return "\n".join(imports)

    def _generate_agent_definition(self, agent_source: str) -> str:
        """Generate the agent class definition with minimal runtime."""
        runtime = textwrap.dedent("""
            # Minimal agent runtime for marimo
            A = TypeVar('A')
            B = TypeVar('B')

            class Agent(ABC, Generic[A, B]):
                @property
                @abstractmethod
                def name(self) -> str: ...

                @abstractmethod
                async def invoke(self, input: A) -> B: ...
        """).strip()

        return f"{runtime}\n\n# Agent implementation\n{agent_source}"

    def _generate_state_management(self, agent_name: str) -> str:
        """Generate mo.state() for persistent state."""
        return textwrap.dedent(f"""
            # State management for {agent_name}
            agent_state, set_agent_state = mo.state({{}})
            run_history, set_run_history = mo.state([])
        """).strip()

    def _generate_main_cell(
        self,
        agent_name: str,
        class_name: str,
        persona: str | None,
        has_stateful: bool,
        has_observable: bool,
        has_streamable: bool,
    ) -> str:
        """Generate the main interactive cell."""
        # Build capability badges
        badges = []
        if has_stateful:
            badges.append("stateful")
        if has_streamable:
            badges.append("streaming")
        if has_observable:
            badges.append("observable")

        caps_text = " • ".join(badges) if badges else "minimal"
        persona_line = (
            f'\nmo.callout(mo.md("**Persona**: {persona}"), kind="info"),' if persona else ""
        )

        # Observable metrics
        metrics_code = ""
        if has_observable:
            metrics_code = textwrap.dedent("""

                # Observable metrics
                _start_time = None

                def start_metrics():
                    global _start_time
                    _start_time = time.time()

                def get_metrics():
                    if _start_time is None:
                        return {"latency_ms": 0}
                    return {"latency_ms": (time.time() - _start_time) * 1000}
            """)

        # Streaming progress
        progress_code = ""
        if has_streamable:
            progress_code = "\n    progress = mo.status.progress_bar()"

        # State persistence
        state_save = ""
        if has_stateful:
            state_save = textwrap.dedent("""

                    # Update state
                    set_run_history(lambda h: h + [{
                        "input": user_input.value,
                        "output": str(result),
                        "timestamp": time.time() if 'time' in dir() else 0,
                    }])
            """)

        return textwrap.dedent(f"""
            # {agent_name} — Interactive Exploration
            {metrics_code}
            # Create agent instance
            _agent = {class_name}()

            # Input widget
            user_input = mo.ui.text_area(
                placeholder="Enter input for the agent...",
                label="Input",
            )

            # Run button
            run_button = mo.ui.run_button(label="Run Agent")

            async def run_agent():
                if not user_input.value.strip():
                    return mo.callout(mo.md("Please enter some input."), kind="warn")
                {"start_metrics()" if has_observable else ""}{progress_code}
                try:
                    result = await _agent.invoke(user_input.value)
                    {"metrics = get_metrics()" if has_observable else ""}{state_save}
                    newline = chr(10)
                    latency_callout = {"mo.callout(mo.md('Latency: ' + str(round(metrics['latency_ms'], 2)) + 'ms'), kind='info')" if has_observable else "None"}
                    return mo.vstack([
                        mo.md(f"**Output:**"),
                        mo.md(f"```{{newline}}{{result}}{{newline}}```"),
                    ] + ([latency_callout] if latency_callout else []))
                except Exception as e:
                    return mo.callout(mo.md(f"Error: {{e}}"), kind="danger")

            # Main cell output
            mo.vstack([
                mo.hstack([
                    mo.md("## {agent_name}"),
                    mo.md("**Capabilities**: {caps_text}"),{persona_line}
                ]),
                user_input,
                run_button,
                mo.md("---"),
                mo.md("**Output:**") if run_button.value else mo.md("*Click Run to execute*"),
                asyncio.run(run_agent()) if run_button.value else None,
            ])
        """).strip()

    def _generate_source_viewer(self, agent_source: str, class_name: str) -> str:
        """Generate collapsible source code viewer."""
        # Escape the source for embedding in f-string
        escaped_source = agent_source.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

        return textwrap.dedent(f'''
            # Source viewer
            mo.accordion({{
                "View {class_name} Source": mo.md(f"""
            ```python
            {escaped_source}
            ```
            """)
            }})
        ''').strip()

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if MarimoProjector supports a capability type.

        MarimoProjector supports all five standard capabilities,
        mapping them to marimo-native equivalents.

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


# Public API
__all__ = [
    "MarimoProjector",
    "MarimoArtifact",
]
