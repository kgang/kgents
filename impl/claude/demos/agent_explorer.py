# mypy: ignore-errors
"""
kgents Agent Explorer — Interactive marimo notebook

The Alethic Architecture in action: same agent, six projections.
This is the marimo projection.

Run:
    marimo edit demos/agent_explorer.py
"""

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import time
    from abc import ABC, abstractmethod
    from typing import TypeVar, Generic
    return ABC, Generic, TypeVar, abstractmethod, mo, time


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
    """)
    return


@app.cell
def _(ABC, Generic, TypeVar, abstractmethod):
    # The Agent protocol — minimal, composable, universal
    A = TypeVar("A")
    B = TypeVar("B")

    class Agent(ABC, Generic[A, B]):
        """The atomic unit of kgents: A → B with identity."""
        @property
        @abstractmethod
        def name(self) -> str: ...

        @abstractmethod
        async def invoke(self, input: A) -> B: ...

    # === PLAIN AGENTS (no Halo) ===

    class TextTransformer(Agent[str, str]):
        """Uppercase transformation. Deterministic, bounded, safe."""
        halo = None  # No capabilities declared
        @property
        def name(self) -> str:
            return "text-transformer"
        async def invoke(self, text: str) -> str:
            return text.upper()

    class ReverseAgent(Agent[str, str]):
        """String reversal. The simplest non-trivial transformation."""
        halo = None
        @property
        def name(self) -> str:
            return "reverse-agent"
        async def invoke(self, text: str) -> str:
            return text[::-1]

    # === AGENTS WITH HALOS (capability declarations) ===

    class ObservableWordCounter(Agent[str, str]):
        """
        Word analysis with @Observable metrics.

        The Halo declares: "I want to be observed."
        - LocalProjector → attaches metrics collectors
        - K8sProjector → generates ServiceMonitor
        - MarimoProjector → shows latency callout (what you see below!)
        """
        halo = ["@Observable(metrics=True)"]
        @property
        def name(self) -> str:
            return "observable-word-counter"
        async def invoke(self, text: str) -> str:
            words = text.split()
            unique = set(w.lower() for w in words)
            return f"Words: {len(words)} | Unique: {len(unique)}\n→ {', '.join(words)}"

    class StatefulEcho(Agent[str, str]):
        """
        Echo that remembers invocation count.

        The Halo declares: "I need persistent state."
        - LocalProjector → wraps with StatefulAdapter
        - K8sProjector → generates StatefulSet + PVC
        - DockerProjector → adds VOLUME mount
        - MarimoProjector → uses mo.state() for persistence
        """
        halo = ["@Stateful(schema=dict)"]
        _count = 0  # Simulated state for demo
        @property
        def name(self) -> str:
            return "stateful-echo"
        async def invoke(self, text: str) -> str:
            StatefulEcho._count += 1
            return f"[invocation #{StatefulEcho._count}] ✨ {text} ✨"

    class SoulfulGreeter(Agent[str, str]):
        """
        A greeter with personality.

        The Halo declares: "I have a soul."
        - LocalProjector → wraps with SoulfulAdapter (K-gent integration)
        - K8sProjector → adds K-gent sidecar container
        - MarimoProjector → shows persona badge
        """
        halo = ["@Soulful(persona='wise-owl', mode='friendly')"]
        @property
        def name(self) -> str:
            return "soulful-greeter"
        async def invoke(self, text: str) -> str:
            return f"🦉 Hoo! You said '{text}'... The wise owl nods thoughtfully."

    AGENTS = {
        "🔠 TextTransformer (plain)": TextTransformer,
        "🔄 ReverseAgent (plain)": ReverseAgent,
        "📊 ObservableWordCounter (@Observable)": ObservableWordCounter,
        "💾 StatefulEcho (@Stateful)": StatefulEcho,
        "🦉 SoulfulGreeter (@Soulful)": SoulfulGreeter,
    }
    return (AGENTS,)


@app.cell
def _(AGENTS, mo):
    agent_selector = mo.ui.dropdown(
        options=AGENTS,
        value="🔠 TextTransformer (plain)",
        label="Agent",
    )

    user_input = mo.ui.text_area(
        placeholder="Type something to invoke the agent...",
        label="Input",
        full_width=True,
    )
    return agent_selector, user_input


@app.cell
def _(agent_selector, mo, user_input):
    # Show selected agent's Halo info
    agent_cls = agent_selector.value
    halo_info = None
    if agent_cls and hasattr(agent_cls, 'halo') and agent_cls.halo:
        halo_str = ", ".join(agent_cls.halo)
        halo_info = mo.callout(
            mo.md(f"**Halo**: `{halo_str}`"),
            kind="info"
        )
    elif agent_cls:
        halo_info = mo.callout(
            mo.md("**Halo**: None (plain agent)"),
            kind="neutral"
        )

    mo.vstack([
        mo.md("## Try It"),
        mo.hstack([agent_selector], justify="start"),
        halo_info,
        user_input,
    ])
    return


@app.cell
def _(mo, user_input):
    # Dynamic run button - disabled when no input
    has_input = bool(user_input.value and user_input.value.strip())

    run_button = mo.ui.run_button(
        label="▶ Invoke" if has_input else "⏸ Enter text first",
        disabled=not has_input,
    )

    mo.hstack([run_button], justify="start")
    return has_input, run_button


@app.cell
async def _(agent_selector, has_input, mo, run_button, time, user_input):
    # Only execute when button is clicked AND we have input
    if not run_button.value or not has_input:
        mo.md("") if has_input else None
    else:
        agent_cls = agent_selector.value
        t0 = time.time()
        try:
            agent = agent_cls()
            result = await agent.invoke(user_input.value)
            elapsed_ms = (time.time() - t0) * 1000

            # Build output based on Halo
            output_parts = [
                mo.md(f"### Result from `{agent.name}`"),
                mo.md(f"```\n{result}\n```"),
            ]

            # Metrics row
            metrics = [mo.callout(mo.md(f"⏱ {elapsed_ms:.2f}ms"), kind="success")]

            # Add Halo-specific UI
            if hasattr(agent_cls, 'halo') and agent_cls.halo:
                for cap in agent_cls.halo:
                    if "@Observable" in cap:
                        metrics.append(mo.callout(mo.md("📊 Observable"), kind="info"))
                    if "@Stateful" in cap:
                        metrics.append(mo.callout(mo.md("💾 Stateful"), kind="warn"))
                    if "@Soulful" in cap:
                        metrics.append(mo.callout(mo.md("🦉 Soulful"), kind="info"))

            output_parts.append(mo.hstack(metrics, justify="start", gap=1))
            mo.vstack(output_parts)

        except Exception as e:
            mo.callout(mo.md(f"Error: `{e}`"), kind="danger")
    return


@app.cell
def _(mo):
    mo.md("""
    ---

    ## What's Actually Happening

    When you click **Invoke**, you're witnessing the same pattern that powers all of kgents:

    ```
    Input → Agent.invoke() → Output
    ```

    That's it. That's the whole thing.

    But the *power* comes from what wraps this core:

    1. **Capabilities** (`@Stateful`, `@Observable`, `@Soulful`, `@Streamable`)
       declare what an agent needs—without specifying *how* to provide it.

    2. **Projectors** read those declarations and compile to targets.
       The MarimoProjector gives you `mo.ui.text_area()` and latency callouts.
       The K8sProjector gives you StatefulSets and HPAs.

    3. **The Halo** is the bridge—a declarative specification that different
       projectors interpret differently, but with guaranteed semantic equivalence.

    Try the **StatefulEcho** agent multiple times—notice how it remembers invocation count.
    That's `@Stateful` in action. In K8s, this would be a PersistentVolumeClaim.
    Here, it's just a class variable. Same semantics, different substrate.

    ---

    ## The Mirror Test

    > *"Does this feel like me on my best day?"*

    A good agent should feel *inevitable*. Not clever—obvious in hindsight.
    The `TextTransformer` is almost too simple. But that's the point.

    **Depth over breadth.** Start with the atomic case. Get it right.
    Then compose.

    ```python
    pipeline = TextTransformer() >> ReverseAgent() >> ObservableWordCounter()
    ```

    Composition is the game. The agent is just the atom.

    ---

    *Built with the Alethic Architecture — tasteful, curated, joy-inducing.*
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
