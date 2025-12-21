# mypy: ignore-errors
"""
kgents Agent Explorer — Interactive marimo notebook

The Alethic Architecture in action: same agent, six projections.
This is the marimo projection — the INTERACTIVE exploration target.

This demo showcases the core kgents concepts:
1. **Agents** — The atomic unit: A → B with identity
2. **PolyAgents** — Dynamical systems with state machines
3. **Halos** — Declarative capability decorators
4. **Composition** — Agents compose via >> operator
5. **Projections** — Same agent, multiple manifestations

Run:
    cd impl/claude && marimo edit demos/agent_explorer.py
"""

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import time
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    from typing import Any, Callable, FrozenSet, Generic, Tuple, TypeVar

    import marimo as mo

    return (
        ABC,
        Callable,
        FrozenSet,
        Generic,
        Tuple,
        TypeVar,
        abstractmethod,
        dataclass,
        mo,
        time,
    )


@app.cell
def _(mo):
    mo.md("""
    # 🎭 The Alethic Architecture

    > *"The noun is a lie. There is only the rate of change."*

    This notebook is a **living proof** of a core kgents insight: **agents are not their deployment**.

    The same agent definition—what we call the **Halo** (its declared capabilities)—can be
    projected onto radically different substrates:

    | Projector | What You Get | When You'd Use It |
    |-----------|--------------|-------------------|
    | `LocalProjector` | Python object | Development, testing |
    | `CLIProjector` | Shell script | Quick automation |
    | `DockerProjector` | Dockerfile | Containerized deployment |
    | `K8sProjector` | Kubernetes manifests | Production at scale |
    | `WASMProjector` | Browser sandbox | Zero-trust execution |
    | **`MarimoProjector`** | **This notebook** | **Interactive exploration** |

    The projector doesn't change the agent's *semantics*—only its *manifestation*.

    ---

    ## What You'll Explore

    1. **Simple Agents** — The `Agent[A, B]` protocol
    2. **Polynomial Agents** — State machines with mode-dependent behavior
    3. **Halo Capabilities** — `@Stateful`, `@Observable`, `@Soulful` decorators
    4. **Composition** — The `>>` operator that makes agents morphisms

    ---
    """)
    return


@app.cell
def _(
    ABC,
    Callable,
    FrozenSet,
    Generic,
    Tuple,
    TypeVar,
    abstractmethod,
    dataclass,
):
    """Define the core Agent and PolyAgent protocols."""

    # Type variables for agent signatures
    A = TypeVar("A")  # Input type
    B = TypeVar("B")  # Output type
    C = TypeVar("C")  # Third type (for composition)
    S = TypeVar("S")  # State type (for PolyAgent)

    # =========================================================================
    # AGENT PROTOCOL: The Atomic Unit
    # =========================================================================

    class Agent(ABC, Generic[A, B]):
        """
        The atomic unit of kgents: A → B with identity.

        An agent is a morphism in a category where:
        - Objects are types
        - Morphisms are agents (async functions with identity)
        - Composition is >>
        """

        @property
        @abstractmethod
        def name(self) -> str:
            """Agent name for identification."""
            ...

        @abstractmethod
        async def invoke(self, input: A) -> B:
            """Execute the agent's core logic."""
            ...

        def __rshift__(self, other: "Agent[B, C]") -> "ComposedAgent[A, B, C]":
            """Sequential composition: self >> other."""
            return ComposedAgent(self, other)

    # =========================================================================
    # COMPOSED AGENT: Sequential Composition
    # =========================================================================

    class ComposedAgent(Agent[A, C], Generic[A, B, C]):
        """Two agents composed: output of first feeds input of second."""

        def __init__(self, left: Agent[A, B], right: Agent[B, C]):
            self._left = left
            self._right = right

        @property
        def name(self) -> str:
            return f"{self._left.name}>>{self._right.name}"

        async def invoke(self, input: A) -> C:
            intermediate = await self._left.invoke(input)
            return await self._right.invoke(intermediate)

    # =========================================================================
    # POLYAGENT: Dynamical Systems with State
    # =========================================================================

    @dataclass(frozen=True)
    class PolyAgent(Generic[S, A, B]):
        """
        Polynomial Agent: Agents as dynamical systems.

        Based on Spivak's polynomial functors:
            P(y) = Σ_{s ∈ Position} y^{Direction(s)}

        This captures:
        - Positions: States the system can be in
        - Directions: Inputs the system can receive at each position
        - Transitions: How state × input → (state, output)

        The key insight: Agents aren't just functions A → B, they're
        dynamical systems with internal state and mode-dependent behavior.
        """

        name: str
        positions: FrozenSet[S]
        _directions: Callable[[S], FrozenSet[A]]
        _transition: Callable[[S, A], Tuple[S, B]]

        def directions(self, state: S) -> FrozenSet[A]:
            """Get valid inputs for state."""
            return self._directions(state)

        def transition(self, state: S, input: A) -> Tuple[S, B]:
            """Execute state transition."""
            return self._transition(state, input)

        def invoke(self, state: S, input: A) -> Tuple[S, B]:
            """Execute one step of the dynamical system."""
            if state not in self.positions:
                raise ValueError(f"Invalid state: {state}")
            return self.transition(state, input)

        def run(self, initial: S, inputs: list) -> Tuple[S, list]:
            """Run the system through a sequence of inputs."""
            state = initial
            outputs = []
            for inp in inputs:
                state, out = self.invoke(state, inp)
                outputs.append(out)
            return state, outputs

    # =========================================================================
    # HALO: Declarative Capability Protocol
    # =========================================================================

    @dataclass(frozen=True)
    class StatefulCapability:
        """Declare that this agent requires persistent state."""

        schema: type
        backend: str = "auto"

    @dataclass(frozen=True)
    class ObservableCapability:
        """Declare that this agent should emit observability data."""

        mirror: bool = True
        metrics: bool = True

    @dataclass(frozen=True)
    class SoulfulCapability:
        """Declare that this agent should embody K-gent personality."""

        persona: str
        mode: str = "advisory"

    @dataclass(frozen=True)
    class StreamableCapability:
        """Declare that this agent can be lifted to Flux domain."""

        budget: float = 10.0
        feedback: float = 0.0

    class Capability:
        """Factory for creating capability decorators."""

        @staticmethod
        def Stateful(*, schema: type, backend: str = "auto"):
            return StatefulCapability(schema=schema, backend=backend)

        @staticmethod
        def Observable(*, mirror: bool = True, metrics: bool = True):
            return ObservableCapability(mirror=mirror, metrics=metrics)

        @staticmethod
        def Soulful(*, persona: str, mode: str = "advisory"):
            return SoulfulCapability(persona=persona, mode=mode)

        @staticmethod
        def Streamable(*, budget: float = 10.0, feedback: float = 0.0):
            return StreamableCapability(budget=budget, feedback=feedback)

    # Helper to add halo to agent
    def with_halo(caps: list):
        """Decorator to add capabilities to an agent class."""

        def decorator(cls):
            cls.__halo__ = caps
            return cls

        return decorator

    def get_halo(agent_cls: type) -> list:
        """Get the Halo (capability list) of an agent class."""
        return getattr(agent_cls, "__halo__", [])

    return (
        Agent,
        Capability,
        ObservableCapability,
        PolyAgent,
        SoulfulCapability,
        StatefulCapability,
        get_halo,
        with_halo,
    )


@app.cell
def _(Agent, Capability, PolyAgent, with_halo):
    """Define example agents showcasing different patterns."""

    # =========================================================================
    # SIMPLE AGENTS (no Halo)
    # =========================================================================

    class TextTransformer(Agent[str, str]):
        """Uppercase transformation. Deterministic, bounded, safe."""

        @property
        def name(self) -> str:
            return "text-transformer"

        async def invoke(self, text: str) -> str:
            return text.upper()

    class ReverseAgent(Agent[str, str]):
        """String reversal. The simplest non-trivial transformation."""

        @property
        def name(self) -> str:
            return "reverse-agent"

        async def invoke(self, text: str) -> str:
            return text[::-1]

    class WordCounter(Agent[str, str]):
        """Count words and unique terms."""

        @property
        def name(self) -> str:
            return "word-counter"

        async def invoke(self, text: str) -> str:
            words = text.split()
            unique = set(w.lower() for w in words)
            return f"Words: {len(words)} | Unique: {len(unique)}"

    # =========================================================================
    # AGENTS WITH HALOS (capability declarations)
    # =========================================================================

    @with_halo(
        [
            Capability.Observable(metrics=True),
        ]
    )
    class ObservableWordCounter(Agent[str, str]):
        """
        Word analysis with @Observable metrics.

        The Halo declares: "I want to be observed."
        - LocalProjector → attaches metrics collectors
        - K8sProjector → generates ServiceMonitor
        - MarimoProjector → shows latency callout
        """

        @property
        def name(self) -> str:
            return "observable-word-counter"

        async def invoke(self, text: str) -> str:
            words = text.split()
            unique = set(w.lower() for w in words)
            return f"Words: {len(words)} | Unique: {len(unique)}\n→ {', '.join(words[:5])}..."

    @with_halo(
        [
            Capability.Stateful(schema=dict),
        ]
    )
    class StatefulEcho(Agent[str, str]):
        """
        Echo that remembers invocation count.

        The Halo declares: "I need persistent state."
        - LocalProjector → wraps with StatefulAdapter
        - K8sProjector → generates StatefulSet + PVC
        - MarimoProjector → uses mo.state() for persistence
        """

        _count = 0  # Simulated state for demo

        @property
        def name(self) -> str:
            return "stateful-echo"

        async def invoke(self, text: str) -> str:
            StatefulEcho._count += 1
            return f"[invocation #{StatefulEcho._count}] ✨ {text} ✨"

    @with_halo(
        [
            Capability.Soulful(persona="wise-owl", mode="friendly"),
        ]
    )
    class SoulfulGreeter(Agent[str, str]):
        """
        A greeter with personality.

        The Halo declares: "I have a soul."
        - LocalProjector → wraps with SoulfulAdapter (K-gent integration)
        - K8sProjector → adds K-gent sidecar container
        - MarimoProjector → shows persona badge
        """

        @property
        def name(self) -> str:
            return "soulful-greeter"

        async def invoke(self, text: str) -> str:
            return f"🦉 Hoo! You said '{text}'... The wise owl nods thoughtfully."

    # =========================================================================
    # POLYAGENT: State Machine Example
    # =========================================================================

    # Traffic Light: A classic state machine
    traffic_light = PolyAgent(
        name="traffic-light",
        positions=frozenset(["red", "yellow", "green"]),
        _directions=lambda s: frozenset(["tick"]),  # Always accepts "tick"
        _transition=lambda s, _: {
            "red": ("green", "🟢 GO"),
            "green": ("yellow", "🟡 SLOW"),
            "yellow": ("red", "🔴 STOP"),
        }[s],
    )

    # Counter: A state machine with numeric state
    def counter_directions(n: int):
        return frozenset(["inc", "dec", "reset"])

    def counter_transition(n: int, cmd: str):
        if cmd == "inc":
            return (n + 1, f"Count: {n + 1}")
        elif cmd == "dec":
            return (n - 1, f"Count: {n - 1}")
        elif cmd == "reset":
            return (0, "Count: 0 (reset)")
        return (n, f"Unknown: {cmd}")

    counter_agent = PolyAgent(
        name="counter",
        positions=frozenset(range(-100, 101)),  # Support -100 to 100
        _directions=counter_directions,
        _transition=counter_transition,
    )

    # =========================================================================
    # AGENT REGISTRY
    # =========================================================================

    SIMPLE_AGENTS = {
        "🔠 TextTransformer": TextTransformer,
        "🔄 ReverseAgent": ReverseAgent,
        "📊 WordCounter": WordCounter,
    }

    HALO_AGENTS = {
        "📊 Observable WordCounter": ObservableWordCounter,
        "💾 Stateful Echo": StatefulEcho,
        "🦉 Soulful Greeter": SoulfulGreeter,
    }

    POLY_AGENTS = {
        "🚦 Traffic Light": traffic_light,
        "🔢 Counter": counter_agent,
    }
    return (
        HALO_AGENTS,
        POLY_AGENTS,
        ReverseAgent,
        SIMPLE_AGENTS,
        TextTransformer,
        WordCounter,
    )


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 1. Simple Agents: The `Agent[A, B]` Protocol

    The simplest agent is just a typed async function with a name.
    These have no capabilities—they're pure morphisms.

    ```python
    class TextTransformer(Agent[str, str]):
        async def invoke(self, text: str) -> str:
            return text.upper()
    ```
    """)
    return


@app.cell
def _(SIMPLE_AGENTS, mo):
    # UI for simple agents
    simple_agent_selector = mo.ui.dropdown(
        options=list(SIMPLE_AGENTS.keys()),
        value="🔠 TextTransformer",
        label="Select Agent",
    )

    simple_input = mo.ui.text(
        placeholder="Type something...",
        label="Input",
        value="hello world",
    )

    mo.hstack([simple_agent_selector, simple_input], gap=2)
    return simple_agent_selector, simple_input


@app.cell
async def _(SIMPLE_AGENTS, mo, simple_agent_selector, simple_input, time):
    if simple_input.value:
        _agent_cls = SIMPLE_AGENTS[simple_agent_selector.value]
        _agent = _agent_cls()

        _t0 = time.time()
        _result = await _agent.invoke(simple_input.value)
        _elapsed = (time.time() - _t0) * 1000

        _output = mo.vstack(
            [
                mo.md(f"**Agent**: `{_agent.name}`"),
                mo.hstack(
                    [
                        mo.callout(mo.md(f"**Output**: {_result}"), kind="success"),
                        mo.callout(mo.md(f"⏱ {_elapsed:.2f}ms"), kind="neutral"),
                    ],
                    gap=1,
                ),
            ]
        )
    else:
        _output = mo.md("*Enter some text to see the agent in action*")
    _output
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 2. Composition: The `>>` Operator

    Agents are morphisms in a category. This means they compose:

    ```python
    pipeline = TextTransformer() >> ReverseAgent() >> WordCounter()
    ```

    The output of each agent flows into the next. **This is the game.**
    """)
    return


@app.cell
def _(ReverseAgent, TextTransformer, WordCounter, mo):
    # Build the composed pipeline
    pipeline = TextTransformer() >> ReverseAgent() >> WordCounter()

    compose_input = mo.ui.text(
        placeholder="Enter text to transform...",
        label="Input",
        value="Hello World",
    )

    compose_input
    return compose_input, pipeline


@app.cell
async def _(
    ReverseAgent,
    TextTransformer,
    WordCounter,
    compose_input,
    mo,
    pipeline,
    time,
):
    if compose_input.value:
        # Run the full pipeline
        _t0 = time.time()
        _final_result = await pipeline.invoke(compose_input.value)
        _elapsed = (time.time() - _t0) * 1000

        # Also run each step for visualization
        _step1 = await TextTransformer().invoke(compose_input.value)
        _step2 = await ReverseAgent().invoke(_step1)
        _step3 = await WordCounter().invoke(_step2)

        _output = mo.vstack(
            [
                mo.md(f"**Pipeline**: `{pipeline.name}`"),
                mo.md("**Execution Trace:**"),
                mo.hstack(
                    [
                        mo.callout(mo.md(f"1️⃣ `{compose_input.value}`"), kind="neutral"),
                        mo.md("→"),
                        mo.callout(mo.md(f"2️⃣ `{_step1}`"), kind="neutral"),
                        mo.md("→"),
                        mo.callout(mo.md(f"3️⃣ `{_step2}`"), kind="neutral"),
                        mo.md("→"),
                        mo.callout(mo.md(f"4️⃣ `{_step3}`"), kind="success"),
                    ],
                    gap=0,
                ),
                mo.callout(mo.md(f"⏱ Pipeline completed in {_elapsed:.2f}ms"), kind="info"),
            ]
        )
    else:
        _output = mo.md("*Enter text to see composition in action*")
    _output
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 3. Halo: Declarative Capabilities

    The **Halo** is the set of capabilities that wrap an agent's pure logic.
    Capabilities are metadata decorators that declare what an agent *could become*
    without coupling to implementation.

    | Capability | What It Declares | LocalProjector | K8sProjector |
    |------------|------------------|----------------|--------------|
    | `@Stateful` | Needs persistence | SQLite Symbiont | StatefulSet + PVC |
    | `@Observable` | Emits telemetry | WebSocket to Terrarium | Prometheus |
    | `@Soulful` | Has personality | K-gent wrapper | K-gent sidecar |
    | `@Streamable` | Lifts to Flux | FluxAgent wrapper | HPA + autoscaling |

    The same agent, different projections, **guaranteed semantic equivalence**.
    """)
    return


@app.cell
def _(HALO_AGENTS, mo):
    # UI for Halo agents - create widgets only
    halo_agent_selector = mo.ui.dropdown(
        options=list(HALO_AGENTS.keys()),
        value="📊 Observable WordCounter",
        label="Select Agent",
    )

    halo_input = mo.ui.text(
        placeholder="Type something...",
        label="Input",
        value="the quick brown fox jumps over the lazy dog",
    )

    mo.hstack([halo_agent_selector, halo_input], gap=2)
    return halo_agent_selector, halo_input


@app.cell
def _(HALO_AGENTS, get_halo, halo_agent_selector, mo):
    # Show capabilities for selected agent (separate cell to access .value)
    _selected_cls = HALO_AGENTS[halo_agent_selector.value]
    _halo_caps = get_halo(_selected_cls)

    # Format capabilities as badges
    _cap_badges = []
    for _cap in _halo_caps:
        _cap_type = type(_cap).__name__.replace("Capability", "")
        _cap_badges.append(mo.callout(mo.md(f"**@{_cap_type}**"), kind="info"))

    _output = mo.hstack(_cap_badges if _cap_badges else [mo.md("*No capabilities*")], gap=1)
    return


@app.cell
async def _(
    HALO_AGENTS,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    get_halo,
    halo_agent_selector,
    halo_input,
    mo,
    time,
):
    if halo_input.value:
        _agent_cls = HALO_AGENTS[halo_agent_selector.value]
        _agent = _agent_cls()
        _halo = get_halo(_agent_cls)

        _t0 = time.time()
        _result = await _agent.invoke(halo_input.value)
        _elapsed = (time.time() - _t0) * 1000

        # Build output based on capabilities
        _output_parts = [
            mo.md(f"**Agent**: `{_agent.name}`"),
            mo.callout(mo.md(f"```\n{_result}\n```"), kind="success"),
        ]

        # Add capability-specific UI
        _metrics_row = [mo.callout(mo.md(f"⏱ {_elapsed:.2f}ms"), kind="neutral")]

        for _cap in _halo:
            if isinstance(_cap, ObservableCapability):
                _metrics_row.append(mo.callout(mo.md("📊 Observable"), kind="info"))
            if isinstance(_cap, StatefulCapability):
                _metrics_row.append(mo.callout(mo.md("💾 Stateful"), kind="warn"))
            if isinstance(_cap, SoulfulCapability):
                _metrics_row.append(
                    mo.callout(mo.md(f"🦉 {_cap.persona} ({_cap.mode})"), kind="info")
                )

        _output_parts.append(mo.hstack(_metrics_row, gap=1))
        _output = mo.vstack(_output_parts)
    else:
        _output = mo.md("*Enter text to see Halo-enhanced agent in action*")
    _output
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## 4. PolyAgents: Dynamical Systems

    The **real power** of kgents is `PolyAgent` — polynomial agents with state.

    ```
    P(y) = Σ_{s ∈ Position} y^{Direction(s)}
    ```

    This captures:
    - **Positions**: States the system can be in
    - **Directions**: Valid inputs at each position
    - **Transitions**: How (state, input) → (new_state, output)

    Think of it as a **state machine** where the available actions depend on your current state.
    """)
    return


@app.cell
def _(POLY_AGENTS, mo):
    # UI for PolyAgents
    poly_agent_selector = mo.ui.dropdown(
        options=list(POLY_AGENTS.keys()),
        value="🚦 Traffic Light",
        label="Select State Machine",
    )

    poly_agent_selector
    return (poly_agent_selector,)


@app.cell
def _(POLY_AGENTS, mo, poly_agent_selector):
    # State for the selected PolyAgent
    selected_poly = POLY_AGENTS[poly_agent_selector.value]

    # Create mo.state for current position
    poly_state, set_poly_state = mo.state(next(iter(selected_poly.positions)))
    run_history, set_run_history = mo.state([])
    return poly_state, selected_poly, set_poly_state, set_run_history


@app.cell
def _(mo, poly_state, selected_poly):
    # Access state values in a separate cell
    # poly_state is a getter function - call it to get the value
    _current = poly_state()
    _valid_inputs = list(selected_poly.directions(_current))

    # Display current state
    _output = mo.vstack(
        [
            mo.md(f"**Agent**: `{selected_poly.name}`"),
            mo.md(f"**Current State**: `{_current}`"),
            mo.md(f"**Valid Inputs**: `{_valid_inputs}`"),
        ]
    )
    _output
    return


@app.cell
def _(mo, poly_state, selected_poly, set_poly_state, set_run_history):
    # Input buttons for each valid action
    # CRITICAL: poly_state is a GETTER FUNCTION from mo.state().
    # You must CALL it to get the value: poly_state()
    # marimo's reactive system may auto-unwrap in some contexts, but closures
    # capture the function reference. Always call explicitly for closure safety.

    # Call the getter to get the actual current state value
    _current = poly_state()  # <-- MUST call as function!
    _valid_inputs = list(selected_poly.directions(_current))

    # Create buttons with the concrete value captured via function parameters
    def _create_buttons(concrete_state):
        """Create buttons capturing a concrete state value."""
        buttons = []
        for cmd in _valid_inputs:

            def make_handler(state_value, command):
                def handler(_):
                    new_state, output = selected_poly.invoke(state_value, command)
                    set_poly_state(new_state)
                    set_run_history(
                        lambda h: h + [(str(state_value), command, output, str(new_state))]
                    )

                return handler

            buttons.append(
                mo.ui.button(
                    label=cmd.upper(),
                    on_change=make_handler(concrete_state, cmd),
                    kind="neutral",
                )
            )
        return buttons

    _buttons = _create_buttons(_current)

    _output = mo.vstack(
        [
            mo.hstack(_buttons, gap=1),
            mo.md("---"),
            mo.md("**History**:"),
        ]
    )
    _output
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## The Mirror Test

    > *"Does this feel like me on my best day?"*

    A good agent should feel *inevitable*. Not clever—obvious in hindsight.

    **Depth over breadth.** Start with the atomic case. Get it right.
    Then compose.

    ```python
    # The composition is the game
    pipeline = TextTransformer() >> ReverseAgent() >> ObservableWordCounter()

    # The Halo is the bridge
    @Capability.Stateful(schema=Memory)
    @Capability.Soulful(persona="Kent")
    class MyAgent(Agent[str, str]): ...

    # The PolyAgent is the dynamical system
    fsm = PolyAgent(
        positions=frozenset(["idle", "active", "done"]),
        _transition=lambda s, x: ...
    )
    ```

    ---

    ## Key Insights

    1. **Agents are morphisms**: They compose via `>>`
    2. **PolyAgents are dynamical systems**: State × Input → (State, Output)
    3. **Halos are declarative**: Capabilities don't couple to implementation
    4. **Projectors interpret**: Same Halo → different manifestations
    5. **The noun is a lie**: There is only the rate of change

    ---

    *Built with the Alethic Architecture — tasteful, curated, joy-inducing.*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
