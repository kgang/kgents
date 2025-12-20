"""
O-gent Dimension X: Telemetric Observability (The Body)

Standard metrics collection for infrastructure health.
Answers: "Is it running?"

Observes:
- Latency, errors, throughput (OpenTelemetry-compatible)
- Agent composition topology (who composes with whom)
- Process lifecycle events

This is the "physical" layer of observation—the body of the system.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .observer import (
    Agent,
    BaseObserver,
    EntropyEvent,
    ObservationContext,
    ObservationResult,
)

# =============================================================================
# Metrics Types
# =============================================================================


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"  # Monotonically increasing
    GAUGE = "gauge"  # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution
    SUMMARY = "summary"  # Pre-aggregated quantiles


@dataclass
class MetricValue:
    """A single metric value."""

    name: str
    value: float
    type: MetricType
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def with_labels(self, **labels: str) -> "MetricValue":
        """Create a copy with additional labels."""
        new_labels = {**self.labels, **labels}
        return MetricValue(
            name=self.name,
            value=self.value,
            type=self.type,
            labels=new_labels,
            timestamp=self.timestamp,
        )


@dataclass
class HistogramBucket:
    """A histogram bucket."""

    le: float  # Upper bound (less than or equal)
    count: int = 0


@dataclass
class HistogramValue:
    """A histogram metric value."""

    name: str
    buckets: list[HistogramBucket]
    sum: float = 0.0
    count: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def observe(self, value: float) -> None:
        """Add an observation to the histogram."""
        self.sum += value
        self.count += 1
        for bucket in self.buckets:
            if value <= bucket.le:
                bucket.count += 1


# =============================================================================
# Metrics Collector
# =============================================================================


class MetricsCollector:
    """
    Collects and stores metrics.

    OpenTelemetry-compatible interface for metrics collection.
    """

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, HistogramValue] = {}
        self._history: list[MetricValue] = []

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        self._counters[key] += value
        self._history.append(
            MetricValue(
                name=name,
                value=self._counters[key],
                type=MetricType.COUNTER,
                labels=labels or {},
            )
        )

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
        self._history.append(
            MetricValue(
                name=name,
                value=value,
                type=MetricType.GAUGE,
                labels=labels or {},
            )
        )

    def histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        buckets: list[float] | None = None,
    ) -> None:
        """Add an observation to a histogram."""
        key = self._make_key(name, labels)

        if key not in self._histograms:
            bucket_values = buckets or [
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ]
            self._histograms[key] = HistogramValue(
                name=name,
                buckets=[HistogramBucket(le=b) for b in bucket_values],
                labels=labels or {},
            )

        self._histograms[key].observe(value)
        self._history.append(
            MetricValue(
                name=name,
                value=value,
                type=MetricType.HISTOGRAM,
                labels=labels or {},
            )
        )

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        """Get current gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key)

    def get_histogram(
        self, name: str, labels: dict[str, str] | None = None
    ) -> HistogramValue | None:
        """Get histogram."""
        key = self._make_key(name, labels)
        return self._histograms.get(key)

    def get_history(self, limit: int = 100) -> list[MetricValue]:
        """Get metric history."""
        return self._history[-limit:]

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create a unique key for metric storage."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def clear(self) -> None:
        """Clear all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._history.clear()


# =============================================================================
# Telemetry Observer
# =============================================================================


class TelemetryObserver(BaseObserver):
    """
    Standard metrics collection observer.

    Collects:
    - agent.latency_ms: Invocation latency histogram
    - agent.invocations: Invocation counter (success/failure)
    - agent.errors: Error counter
    - agent.active: Currently executing agents gauge
    """

    def __init__(
        self,
        observer_id: str = "telemetry",
        metrics: MetricsCollector | None = None,
    ) -> None:
        super().__init__(observer_id=observer_id)
        self.metrics = metrics if metrics is not None else MetricsCollector()
        self._active_agents: set[str] = set()

    def pre_invoke(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
    ) -> ObservationContext:
        """Start tracking an invocation."""
        ctx = super().pre_invoke(agent, input_data)

        # Track active agents
        self._active_agents.add(ctx.agent_id)
        self.metrics.gauge(
            "agent.active",
            len(self._active_agents),
        )

        return ctx

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Record successful invocation metrics."""
        agent_labels = {"agent": context.agent_name}

        # Record latency
        self.metrics.histogram(
            "agent.latency_ms",
            duration_ms,
            labels=agent_labels,
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000],
        )

        # Increment success counter
        self.metrics.increment(
            "agent.invocations",
            labels={**agent_labels, "success": "true"},
        )

        # Update active agents
        self._active_agents.discard(context.agent_id)
        self.metrics.gauge(
            "agent.active",
            len(self._active_agents),
        )

        return await super().post_invoke(context, result, duration_ms)

    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> EntropyEvent:
        """Record error metrics."""
        agent_labels = {"agent": context.agent_name}

        # Increment error counter
        self.metrics.increment(
            "agent.errors",
            labels={**agent_labels, "error_type": type(error).__name__},
        )

        # Increment failure counter
        self.metrics.increment(
            "agent.invocations",
            labels={**agent_labels, "success": "false"},
        )

        # Update active agents
        self._active_agents.discard(context.agent_id)
        self.metrics.gauge(
            "agent.active",
            len(self._active_agents),
        )

        return super().record_entropy(context, error)

    def get_agent_stats(self, agent_name: str) -> dict[str, Any]:
        """Get statistics for a specific agent."""
        labels = {"agent": agent_name}

        success_count = self.metrics.get_counter(
            "agent.invocations",
            labels={**labels, "success": "true"},
        )
        failure_count = self.metrics.get_counter(
            "agent.invocations",
            labels={**labels, "success": "false"},
        )
        total = success_count + failure_count

        histogram = self.metrics.get_histogram("agent.latency_ms", labels)

        return {
            "agent": agent_name,
            "invocations": total,
            "successes": success_count,
            "failures": failure_count,
            "success_rate": success_count / total if total > 0 else 0.0,
            "latency_avg_ms": histogram.sum / histogram.count
            if histogram and histogram.count > 0
            else 0.0,
            "latency_sum_ms": histogram.sum if histogram else 0.0,
        }


# =============================================================================
# Topology Mapper
# =============================================================================


@dataclass
class CompositionEdge:
    """An edge in the composition graph."""

    source: str  # Source agent name
    target: str  # Target agent name
    count: int = 1  # How many times this composition occurred
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class TopologyNode:
    """A node in the composition graph."""

    name: str
    invocation_count: int = 0
    composition_count: int = 0  # How many times composed with others
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionGraph:
    """The composition topology of agents."""

    nodes: list[str]
    edges: list[tuple[str, str, int]]  # (source, target, count)
    hot_paths: list[list[str]]  # Most frequently used paths
    bottlenecks: list[str]  # Agents with high fan-in

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "nodes": self.nodes,
            "edges": [{"source": s, "target": t, "count": c} for s, t, c in self.edges],
            "hot_paths": self.hot_paths,
            "bottlenecks": self.bottlenecks,
        }


class TopologyMapper:
    """
    Maps the composition graph of agents.

    Useful for understanding:
    - Which agents compose together?
    - What are the hottest composition paths?
    - Where are the bottlenecks?
    """

    def __init__(self) -> None:
        self._nodes: dict[str, TopologyNode] = {}
        self._edges: dict[tuple[str, str], CompositionEdge] = {}

    def observe_invocation(self, agent_name: str) -> None:
        """Record an agent invocation."""
        if agent_name not in self._nodes:
            self._nodes[agent_name] = TopologyNode(name=agent_name)
        self._nodes[agent_name].invocation_count += 1

    def observe_composition(
        self,
        source_agent: str,
        target_agent: str,
    ) -> None:
        """
        Record a composition event.

        When agent A >> agent B is composed.
        """
        # Ensure nodes exist
        for name in [source_agent, target_agent]:
            if name not in self._nodes:
                self._nodes[name] = TopologyNode(name=name)

        # Update composition counts
        self._nodes[source_agent].composition_count += 1
        self._nodes[target_agent].composition_count += 1

        # Update or create edge
        edge_key = (source_agent, target_agent)
        if edge_key in self._edges:
            self._edges[edge_key].count += 1
            self._edges[edge_key].last_seen = datetime.now()
        else:
            self._edges[edge_key] = CompositionEdge(
                source=source_agent,
                target=target_agent,
            )

    def get_topology(self) -> CompositionGraph:
        """Return the current composition topology."""
        nodes = list(self._nodes.keys())
        edges = [(edge.source, edge.target, edge.count) for edge in self._edges.values()]

        return CompositionGraph(
            nodes=nodes,
            edges=edges,
            hot_paths=self._find_hot_paths(),
            bottlenecks=self._find_bottlenecks(),
        )

    def _find_hot_paths(self, top_n: int = 5) -> list[list[str]]:
        """Find the most frequently used composition paths."""
        # Simple implementation: return top edges as 2-node paths
        sorted_edges = sorted(
            self._edges.values(),
            key=lambda e: e.count,
            reverse=True,
        )
        return [[e.source, e.target] for e in sorted_edges[:top_n]]

    def _find_bottlenecks(self, threshold: int = 3) -> list[str]:
        """
        Find agents that are bottlenecks (high fan-in).

        A bottleneck is an agent that many others compose into.
        """
        # Count incoming edges for each node
        fan_in: dict[str, int] = defaultdict(int)
        for (source, target), edge in self._edges.items():
            fan_in[target] += edge.count

        # Find nodes above threshold
        return [node for node, count in fan_in.items() if count >= threshold]

    def get_node(self, agent_name: str) -> TopologyNode | None:
        """Get node info for an agent."""
        return self._nodes.get(agent_name)

    def get_edge(self, source: str, target: str) -> CompositionEdge | None:
        """Get edge info for a composition."""
        return self._edges.get((source, target))

    def get_neighbors(self, agent_name: str) -> dict[str, list[str]]:
        """Get agents that compose with the given agent."""
        outgoing = [t for (s, t) in self._edges if s == agent_name]
        incoming = [s for (s, t) in self._edges if t == agent_name]
        return {"outgoing": outgoing, "incoming": incoming}

    def visualize(self, max_nodes: int = 20) -> str:
        """
        Render topology as ASCII graph.

        Returns a simple text representation.
        """
        lines = ["=== COMPOSITION TOPOLOGY ===", ""]

        # Show nodes
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.invocation_count,
            reverse=True,
        )[:max_nodes]

        lines.append("Nodes (by invocation count):")
        for node in sorted_nodes:
            lines.append(f"  [{node.name}] invocations={node.invocation_count}")

        lines.append("")
        lines.append("Edges (by composition count):")

        sorted_edges = sorted(
            self._edges.values(),
            key=lambda e: e.count,
            reverse=True,
        )[:max_nodes]

        for edge in sorted_edges:
            lines.append(f"  {edge.source} --({edge.count})--> {edge.target}")

        # Show hot paths
        hot_paths = self._find_hot_paths(3)
        if hot_paths:
            lines.append("")
            lines.append("Hot Paths:")
            for path in hot_paths:
                lines.append(f"  {' >> '.join(path)}")

        # Show bottlenecks
        bottlenecks = self._find_bottlenecks()
        if bottlenecks:
            lines.append("")
            lines.append(f"Bottlenecks: {', '.join(bottlenecks)}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear topology data."""
        self._nodes.clear()
        self._edges.clear()


# =============================================================================
# Topology Observer
# =============================================================================


class TopologyObserver(BaseObserver):
    """
    Observer that tracks composition topology.

    Integrates with TopologyMapper to record agent interactions.
    """

    def __init__(
        self,
        observer_id: str = "topology",
        mapper: TopologyMapper | None = None,
    ) -> None:
        super().__init__(observer_id=observer_id)
        self.mapper = mapper if mapper is not None else TopologyMapper()
        self._last_agent: str | None = None

    def pre_invoke(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
    ) -> ObservationContext:
        """Record invocation and potential composition."""
        ctx = super().pre_invoke(agent, input_data)

        # Record invocation
        self.mapper.observe_invocation(ctx.agent_name)

        # If there was a previous agent, this might be a composition
        if self._last_agent and self._last_agent != ctx.agent_name:
            self.mapper.observe_composition(self._last_agent, ctx.agent_name)

        self._last_agent = ctx.agent_name
        return ctx

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Record successful completion."""
        return await super().post_invoke(context, result, duration_ms)

    def record_entropy(
        self,
        context: ObservationContext,
        error: Exception,
    ) -> EntropyEvent:
        """Record error and clear composition chain."""
        # Reset composition tracking on error
        self._last_agent = None
        return super().record_entropy(context, error)

    def get_topology(self) -> CompositionGraph:
        """Get current topology."""
        return self.mapper.get_topology()


# =============================================================================
# Convenience Functions
# =============================================================================


def create_metrics_collector() -> MetricsCollector:
    """Create a new metrics collector."""
    collector: MetricsCollector = MetricsCollector()
    return collector


def create_telemetry_observer(
    metrics: MetricsCollector | None = None,
    observer_id: str = "telemetry",
) -> TelemetryObserver:
    """Create a telemetry observer."""
    return TelemetryObserver(observer_id=observer_id, metrics=metrics)


def create_topology_mapper() -> TopologyMapper:
    """Create a new topology mapper."""
    mapper: TopologyMapper = TopologyMapper()
    return mapper


def create_topology_observer(
    mapper: TopologyMapper | None = None,
    observer_id: str = "topology",
) -> TopologyObserver:
    """Create a topology observer."""
    return TopologyObserver(observer_id=observer_id, mapper=mapper)
