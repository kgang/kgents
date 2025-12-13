"""
FluxAgent + VisualHint Integration Example

Demonstrates how a FluxAgent emits VisualHints to shape its TUI representation.
This is documentation code showing the heterarchical UI principle in action.

NOT EXECUTABLE - This is example code showing the pattern.
Once FluxAgent has access to VisualHint, agents can emit hints in their output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from impl.claude.agents.flux.agent import FluxAgent

    from .hints import VisualHint

# ─────────────────────────────────────────────────────────────
# Example 1: B-gent (Banker) emits table hints
# ─────────────────────────────────────────────────────────────


async def bgent_example(flux_agent: "FluxAgent[Any, Any]") -> None:
    """
    B-gent (Banker) emits financial table hints.

    The B-gent processes financial events and emits its balance sheet
    as a table hint, allowing the I-gent to render it appropriately.
    """
    from .hints import VisualHint

    # Imagine B-gent has processed some transactions
    # and now wants to display its state
    balance_sheet = {
        "Assets": 1000,
        "Liabilities": 300,
        "Net Worth": 700,
    }

    # Emit as VisualHint
    _ = VisualHint(
        type="table",
        data=balance_sheet,
        position="sidebar",
        priority=10,
        agent_id=flux_agent.id,
    )

    # In a real FluxAgent, you would yield this
    # The I-gent's HintContainer would render it as a DataTable
    # yield hint


# ─────────────────────────────────────────────────────────────
# Example 2: Y-gent (Topology) emits graph hints
# ─────────────────────────────────────────────────────────────


async def ygent_example(flux_agent: "FluxAgent[Any, Any]") -> None:
    """
    Y-gent (Topology) emits agent graph hints.

    The Y-gent tracks agent connections and emits a graph visualization
    of the current topology.
    """
    from .hints import VisualHint

    # Y-gent has analyzed the agent topology
    topology = {
        "nodes": ["K-gent", "B-gent", "L-gent", "D-gent"],
        "edges": [
            ("K-gent", "B-gent"),
            ("K-gent", "L-gent"),
            ("B-gent", "D-gent"),
        ],
    }

    _ = VisualHint(
        type="graph",
        data=topology,
        position="main",
        priority=20,
        agent_id=flux_agent.id,
    )

    # yield hint


# ─────────────────────────────────────────────────────────────
# Example 3: K-gent emits density + sparkline hints
# ─────────────────────────────────────────────────────────────


async def kgent_example(flux_agent: "FluxAgent[Any, Any]") -> None:
    """
    K-gent emits density field and activity sparkline.

    The K-gent expresses its current cognitive state as a density field
    and its recent activity history as a sparkline.
    """
    from .hints import VisualHint

    # Current cognitive state
    _ = VisualHint(
        type="density",
        data={
            "activity": 0.75,
            "phase": "ACTIVE",
            "name": "K",
        },
        position="main",
        priority=15,
        agent_id=flux_agent.id,
    )

    # Recent activity history
    activity_history = [0.3, 0.4, 0.6, 0.7, 0.75, 0.8, 0.75]
    _ = VisualHint(
        type="sparkline",
        data={
            "values": activity_history,
            "width": 20,
        },
        position="footer",
        priority=5,
        agent_id=flux_agent.id,
    )

    # yield density_hint
    # yield sparkline_hint


# ─────────────────────────────────────────────────────────────
# Example 4: FluxAgent wrapper with hint emission
# ─────────────────────────────────────────────────────────────


class HintEmittingFluxAgent:
    """
    Example wrapper showing how a FluxAgent could emit hints.

    This is conceptual code showing the pattern.
    In practice, FluxAgent.start() would be modified to yield
    both regular results and VisualHints.
    """

    def __init__(self, flux_agent: "FluxAgent[Any, Any]"):
        self.flux_agent = flux_agent

    async def start_with_hints(
        self, source: AsyncIterator[Any]
    ) -> AsyncIterator[Any | "VisualHint"]:
        """
        Start flux and yield both results and hints.

        This demonstrates how FluxAgent output could be augmented
        with VisualHints.

        Example:
            >>> async for item in agent.start_with_hints(events):
            ...     if isinstance(item, VisualHint):
            ...         container.add_hint(item)
            ...     else:
            ...         process_result(item)
        """
        # Process normal flux
        async for result in self.flux_agent.start(source):
            # Yield the result
            yield result

            # Optionally emit a hint based on result
            # This is where agent-specific logic would go
            # For example, B-gent might emit table after balance update
            # yield self._generate_hint(result)

    def _generate_hint(self, result: Any) -> "VisualHint":
        """
        Generate a hint based on result.

        Agent-specific logic determines what kind of hint to emit.
        """
        from .hints import VisualHint

        # Example: emit simple text hint
        return VisualHint(
            type="text",
            data={"text": f"Processed: {result}"},
            position="footer",
            agent_id=self.flux_agent.id,
        )


# ─────────────────────────────────────────────────────────────
# Example 5: Multi-agent hint orchestration
# ─────────────────────────────────────────────────────────────


async def multi_agent_hints_example() -> None:
    """
    Multiple agents emitting different hints simultaneously.

    The I-gent's HintContainer receives hints from multiple agents
    and renders them in their respective positions with proper priorities.
    """
    from .hints import VisualHint

    # K-gent emits density (main, high priority)
    kgent_hint = VisualHint(
        type="density",
        data={"activity": 0.8, "phase": "ACTIVE"},
        position="main",
        priority=20,
        agent_id="k-gent-1",
    )

    # B-gent emits table (sidebar, medium priority)
    bgent_hint = VisualHint(
        type="table",
        data={"Assets": 100, "Liabilities": 50},
        position="sidebar",
        priority=10,
        agent_id="b-gent-1",
    )

    # Monitor agent emits sparkline (footer, low priority)
    monitor_hint = VisualHint(
        type="sparkline",
        data={"values": [1, 2, 3, 4, 5]},
        position="footer",
        priority=5,
        agent_id="monitor-1",
    )

    # Y-gent emits topology graph (main, high priority)
    ygent_hint = VisualHint(
        type="graph",
        data={"nodes": ["K", "B"], "edges": [("K", "B")]},
        position="main",
        priority=15,
        agent_id="y-gent-1",
    )

    # The HintContainer would receive all these and render:
    # - Main: K-gent density (priority 20), then Y-gent graph (priority 15)
    # - Sidebar: B-gent table (priority 10)
    # - Footer: Monitor sparkline (priority 5)

    _ = [kgent_hint, bgent_hint, monitor_hint, ygent_hint]

    # In actual code:
    # container = HintContainer()
    # container.hints = hints
    # Container automatically re-renders with all hints in place


# ─────────────────────────────────────────────────────────────
# Design Notes
# ─────────────────────────────────────────────────────────────

"""
Design Philosophy:

1. HETERARCHICAL: Agents define their own representation
   - B-gent knows it should be a table
   - Y-gent knows it should be a graph
   - K-gent knows it should be a density field

2. EXTENSIBLE: New agents can register new hint types
   - Custom agents can define custom widgets
   - HintRegistry is open for extension

3. COMPOSABLE: Hints compose freely
   - Multiple agents can emit to same position
   - Priorities control render order
   - Positions control layout

4. DECOUPLED: Agents don't know about widgets
   - Agents emit abstract hints
   - HintRegistry maps to concrete widgets
   - UI changes don't affect agents

Future Extensions:

1. FluxAgent could have .emit_hint() method
2. Hints could include refresh_rate for dynamic updates
3. Hints could include interactions (click handlers)
4. Hints could be nested (hints within hints)

The key insight: The I-gent is a BROWSER that renders
agent-emitted layout hints. The framework doesn't impose
a fixed UI—agents speak, and the framework listens.
"""
