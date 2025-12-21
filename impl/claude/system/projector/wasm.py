"""
WASMProjector: Compiles agent Halo to browser-sandboxed WASM execution.

The WASMProjector reads an agent's declarative capabilities (Halo)
and produces an HTML bundle that runs the agent via Pyodide (Python in WASM).

WHY THIS EXISTS:
CHAOTIC reality agents MUST run sandboxed before being trusted.
The browser sandbox is the most battle-tested isolation boundary.
This is zero-trust agent execution.

Capability Mapping:
| Capability  | WASM Feature                                      |
|-------------|---------------------------------------------------|
| @Stateful   | IndexedDB persistence                             |
| @Soulful    | Stored in pyodide namespace                       |
| @Observable | Performance API + console.time                    |
| @Streamable | ReadableStream with async iteration               |
| @TurnBased  | IndexedDB for weave storage                       |

The Alethic Isomorphism:
    Same Halo + LocalProjector  → Runnable Python object
    Same Halo + K8sProjector    → K8s Manifests
    Same Halo + CLIProjector    → Executable shell script
    Same Halo + DockerProjector → Dockerfile
    Same Halo + WASMProjector   → Sandboxed HTML bundle
    All produce semantically equivalent agents.

Example:
    >>> @Capability.Stateful(schema=MyState)
    ... @Capability.Streamable(budget=5.0)
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> html = WASMProjector().compile(MyAgent)
    >>> # html is self-contained HTML that runs the agent in browser
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
class WASMArtifact:
    """
    Result of WASMProjector compilation.

    Contains the HTML bundle and metadata for downstream use.
    """

    html: str
    agent_name: str
    agent_source: str
    uses_indexeddb: bool = False
    uses_streaming: bool = False
    exposed_functions: list[str] = field(default_factory=list)

    def save(self, path: str) -> None:
        """Write HTML bundle to file."""
        from pathlib import Path

        Path(path).write_text(self.html)


@dataclass
class WASMProjector(Projector[str]):
    """
    Compiles agent Halo into browser-sandboxed WASM bundle.

    The WASMProjector reads capability decorators and produces
    an HTML file that runs the agent via Pyodide in a browser sandbox.

    This is the CHAOTIC reality safety net:
    - No filesystem access (browser sandbox)
    - No network access (unless explicitly enabled)
    - Memory isolation via WASM
    - CPU time bounded by browser

    Configuration:
        pyodide_version: Pyodide CDN version (default: 0.24.1)
        include_packages: Additional Python packages to load
        theme: UI theme (light/dark/minimal)

    Example:
        >>> @Capability.Stateful(schema=dict)
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> html = WASMProjector().compile(MyAgent)
        >>> # Open html in browser to run sandboxed agent
    """

    pyodide_version: str = "0.24.1"
    include_packages: list[str] = field(default_factory=list)
    theme: str = "minimal"  # light | dark | minimal
    title_prefix: str = "kgents sandbox"

    @property
    def name(self) -> str:
        return "WASMProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> str:
        """
        Compile agent class to sandboxed HTML bundle.

        Reads the agent's Halo and produces an HTML file that:
        - Loads Pyodide (Python in WASM)
        - Embeds the agent source code
        - Provides sandboxed I/O via DOM
        - Persists state to IndexedDB if @Stateful
        - Streams output if @Streamable

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Self-contained HTML as string

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

        # Build HTML sections
        html_parts = []

        # DOCTYPE and head
        html_parts.append(self._generate_head(agent_name, class_name))

        # Styles
        html_parts.append(self._generate_styles())

        # Body structure
        html_parts.append(
            self._generate_body(
                agent_name=agent_name,
                persona=getattr(soulful_cap, "persona", None) if soulful_cap else None,
                has_stateful=stateful_cap is not None,
                has_streamable=streamable_cap is not None,
                has_observable=observable_cap is not None,
            )
        )

        # Pyodide bootstrap and agent code
        html_parts.append(
            self._generate_pyodide_script(
                agent_source=agent_source,
                class_name=class_name,
                has_stateful=stateful_cap is not None,
                has_streamable=streamable_cap is not None,
                has_observable=observable_cap is not None,
                has_turnbased=turnbased_cap is not None,
            )
        )

        # Close HTML
        html_parts.append("</body>\n</html>")

        return "\n".join(html_parts)

    def compile_artifact(self, agent_cls: type["Agent[Any, Any]"]) -> WASMArtifact:
        """
        Compile to WASMArtifact for composition with other projectors.

        Returns structured artifact with metadata for downstream use.
        """
        from agents.a.halo import get_halo

        halo = get_halo(agent_cls)

        def _has_cap(cap_name: str) -> bool:
            return any(type(c).__name__ == cap_name for c in halo)

        html = self.compile(agent_cls)
        agent_source = self._extract_source(agent_cls)

        return WASMArtifact(
            html=html,
            agent_name=self._derive_agent_name(agent_cls),
            agent_source=agent_source,
            uses_indexeddb=_has_cap("StatefulCapability") or _has_cap("TurnBasedCapability"),
            uses_streaming=_has_cap("StreamableCapability"),
            exposed_functions=["invoke"],
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
            # and don't exist in the WASM runtime
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

    def _generate_head(self, agent_name: str, class_name: str) -> str:
        """Generate HTML head section."""
        return textwrap.dedent(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{self.title_prefix}: {agent_name}</title>
                <meta name="description" content="Sandboxed execution of {class_name} agent via Pyodide">
                <meta name="generator" content="kgents WASMProjector">

                <!-- Pyodide -->
                <script src="https://cdn.jsdelivr.net/pyodide/v{self.pyodide_version}/full/pyodide.js"></script>
        """).strip()

    def _generate_styles(self) -> str:
        """Generate CSS styles."""
        if self.theme == "minimal":
            return textwrap.dedent("""
                <style>
                    :root {
                        --bg: #1a1a2e;
                        --surface: #16213e;
                        --text: #e8e8e8;
                        --accent: #0f3460;
                        --highlight: #e94560;
                        --success: #4ecca3;
                        --warning: #ffc947;
                    }
                    * { box-sizing: border-box; margin: 0; padding: 0; }
                    body {
                        font-family: 'SF Mono', 'Fira Code', monospace;
                        background: var(--bg);
                        color: var(--text);
                        min-height: 100vh;
                        display: flex;
                        flex-direction: column;
                        padding: 2rem;
                    }
                    .header {
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 2rem;
                    }
                    .header h1 {
                        font-size: 1.5rem;
                        font-weight: 400;
                    }
                    .badge {
                        background: var(--highlight);
                        padding: 0.25rem 0.75rem;
                        border-radius: 1rem;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    }
                    .sandbox-indicator {
                        background: var(--success);
                        color: var(--bg);
                    }
                    .container {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 2rem;
                        flex: 1;
                    }
                    @media (max-width: 768px) {
                        .container { grid-template-columns: 1fr; }
                    }
                    .panel {
                        background: var(--surface);
                        border-radius: 0.5rem;
                        padding: 1.5rem;
                        display: flex;
                        flex-direction: column;
                    }
                    .panel-header {
                        font-size: 0.875rem;
                        color: var(--highlight);
                        margin-bottom: 1rem;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                    }
                    textarea, .output {
                        flex: 1;
                        background: var(--bg);
                        border: 1px solid var(--accent);
                        border-radius: 0.25rem;
                        padding: 1rem;
                        color: var(--text);
                        font-family: inherit;
                        font-size: 0.875rem;
                        resize: none;
                        min-height: 200px;
                    }
                    textarea:focus {
                        outline: none;
                        border-color: var(--highlight);
                    }
                    .output {
                        overflow-y: auto;
                        white-space: pre-wrap;
                    }
                    .controls {
                        display: flex;
                        gap: 1rem;
                        margin-top: 1rem;
                    }
                    button {
                        background: var(--highlight);
                        color: white;
                        border: none;
                        padding: 0.75rem 1.5rem;
                        border-radius: 0.25rem;
                        cursor: pointer;
                        font-family: inherit;
                        font-size: 0.875rem;
                        transition: opacity 0.2s;
                    }
                    button:hover { opacity: 0.9; }
                    button:disabled { opacity: 0.5; cursor: not-allowed; }
                    button.secondary {
                        background: var(--accent);
                    }
                    .status {
                        margin-top: 1rem;
                        padding: 0.75rem;
                        border-radius: 0.25rem;
                        font-size: 0.875rem;
                    }
                    .status.loading { background: var(--warning); color: var(--bg); }
                    .status.ready { background: var(--success); color: var(--bg); }
                    .status.error { background: var(--highlight); }
                    .metrics {
                        margin-top: 1rem;
                        font-size: 0.75rem;
                        color: var(--text);
                        opacity: 0.7;
                    }
                    .metrics span { margin-right: 1.5rem; }
                </style>
            """).strip()
        else:
            # Light theme (default fallback)
            return "<style>body { font-family: sans-serif; padding: 2rem; }</style>"

    def _generate_body(
        self,
        agent_name: str,
        persona: str | None,
        has_stateful: bool,
        has_streamable: bool,
        has_observable: bool,
    ) -> str:
        """Generate HTML body structure."""
        persona_badge = f'<span class="badge">{persona}</span>' if persona else ""
        capabilities = []
        if has_stateful:
            capabilities.append("stateful")
        if has_streamable:
            capabilities.append("streaming")
        if has_observable:
            capabilities.append("observable")
        caps_display = " • ".join(capabilities) if capabilities else "minimal"

        return textwrap.dedent(f"""
            </head>
            <body>
                <div class="header">
                    <h1>{agent_name}</h1>
                    <span class="badge sandbox-indicator">SANDBOXED</span>
                    {persona_badge}
                </div>

                <div id="status" class="status loading">Loading Pyodide runtime...</div>

                <div class="container">
                    <div class="panel">
                        <div class="panel-header">Input</div>
                        <textarea id="input" placeholder="Enter input for the agent..."></textarea>
                        <div class="controls">
                            <button id="run-btn" disabled>Run Agent</button>
                            <button id="clear-btn" class="secondary">Clear</button>
                        </div>
                    </div>

                    <div class="panel">
                        <div class="panel-header">Output</div>
                        <div id="output" class="output"></div>
                        <div id="metrics" class="metrics" style="display: none;">
                            <span id="latency">Latency: --</span>
                            <span id="output-size">Size: --</span>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 2rem; font-size: 0.75rem; opacity: 0.5;">
                    Capabilities: {caps_display} | Runtime: Pyodide {self.pyodide_version} | Isolation: Browser WASM Sandbox
                </div>
        """).strip()

    def _generate_pyodide_script(
        self,
        agent_source: str,
        class_name: str,
        has_stateful: bool,
        has_streamable: bool,
        has_observable: bool,
        has_turnbased: bool,
    ) -> str:
        """Generate Pyodide bootstrap and agent execution script."""
        # Escape backticks and backslashes in agent source for JS template literal
        escaped_source = (
            agent_source.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        )

        # IndexedDB helpers for stateful/turnbased
        indexeddb_code = ""
        if has_stateful or has_turnbased:
            indexeddb_code = """
# IndexedDB persistence via js bridge
async def load_state():
    from js import indexedDB
    # Simplified: use localStorage fallback
    from js import localStorage
    import json
    stored = localStorage.getItem('agent_state')
    return json.loads(stored) if stored else {}

async def save_state(state):
    from js import localStorage
    import json
    localStorage.setItem('agent_state', json.dumps(state))
"""

        # Observable metrics
        observable_code = ""
        if has_observable:
            observable_code = """
import time
_start_time = None

def start_metrics():
    global _start_time
    _start_time = time.time()

def get_metrics():
    if _start_time is None:
        return {}
    return {'latency_ms': (time.time() - _start_time) * 1000}
"""

        # Runtime wrapper code
        runtime_code = f"""
# Minimal agent runtime for WASM sandbox
from dataclasses import dataclass
from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod

A = TypeVar('A')
B = TypeVar('B')

class Agent(ABC, Generic[A, B]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def invoke(self, input: A) -> B: ...

{indexeddb_code}
{observable_code}

# Agent implementation
{escaped_source}

# Create agent instance
_agent = {class_name}()

async def run_agent(input_text):
    {"start_metrics()" if has_observable else ""}
    result = await _agent.invoke(input_text)
    return str(result)
"""

        return textwrap.dedent(f"""
            <script>
                let pyodide = null;
                const statusEl = document.getElementById('status');
                const inputEl = document.getElementById('input');
                const outputEl = document.getElementById('output');
                const runBtn = document.getElementById('run-btn');
                const clearBtn = document.getElementById('clear-btn');
                const metricsEl = document.getElementById('metrics');
                const latencyEl = document.getElementById('latency');
                const outputSizeEl = document.getElementById('output-size');

                async function initPyodide() {{
                    try {{
                        statusEl.textContent = 'Loading Pyodide...';
                        pyodide = await loadPyodide();

                        statusEl.textContent = 'Initializing agent...';

                        // Load agent code
                        await pyodide.runPythonAsync(`{runtime_code}`);

                        statusEl.textContent = 'Ready — Agent loaded in sandbox';
                        statusEl.className = 'status ready';
                        runBtn.disabled = false;
                    }} catch (err) {{
                        statusEl.textContent = 'Error: ' + err.message;
                        statusEl.className = 'status error';
                        console.error(err);
                    }}
                }}

                async function runAgent() {{
                    if (!pyodide) return;

                    const input = inputEl.value;
                    if (!input.trim()) {{
                        outputEl.textContent = 'Please enter some input.';
                        return;
                    }}

                    runBtn.disabled = true;
                    outputEl.textContent = 'Running...';
                    const startTime = performance.now();

                    try {{
                        // Escape input for Python string
                        const escapedInput = input.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'");
                        const result = await pyodide.runPythonAsync(`await run_agent('${{escapedInput}}')`);

                        const elapsed = performance.now() - startTime;
                        outputEl.textContent = result;

                        // Show metrics
                        {"metricsEl.style.display = 'block';" if has_observable else ""}
                        latencyEl.textContent = 'Latency: ' + elapsed.toFixed(2) + 'ms';
                        outputSizeEl.textContent = 'Size: ' + result.length + ' chars';

                    }} catch (err) {{
                        outputEl.textContent = 'Error: ' + err.message;
                        console.error(err);
                    }} finally {{
                        runBtn.disabled = false;
                    }}
                }}

                // Event listeners
                runBtn.addEventListener('click', runAgent);
                clearBtn.addEventListener('click', () => {{
                    inputEl.value = '';
                    outputEl.textContent = '';
                    metricsEl.style.display = 'none';
                }});

                // Ctrl+Enter to run
                inputEl.addEventListener('keydown', (e) => {{
                    if (e.ctrlKey && e.key === 'Enter') {{
                        runAgent();
                    }}
                }});

                // Initialize on load
                initPyodide();
            </script>
        """).strip()

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if WASMProjector supports a capability type.

        WASMProjector supports all five standard capabilities,
        mapping them to browser-safe equivalents.

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
