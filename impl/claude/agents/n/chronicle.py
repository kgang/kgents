"""
N-gent Chronicle: Multi-Agent Narrative Weaving.

The Chronicle weaves crystals from multiple agents into a unified timeline.
This is the substrate for multi-agent sagas.

Philosophy:
    When multiple agents collaborate, their crystals form a tapestry.
    The Chronicle preserves the weave. The Bard tells the story.

Components:
    - Interaction: A point where agent timelines intersect
    - Chronicle: Collection of crystals from multiple agents
    - ChronicleBuilder: Fluent API for building chronicles
    - TimelineView: View of a single agent's timeline within the chronicle
    - CorrelationDetector: Detect interactions between agents
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterator

from .bard import Bard, Narrative, NarrativeGenre, NarrativeRequest, Verbosity
from .types import SemanticTrace


@dataclass
class Interaction:
    """
    A point where agent timelines intersect.

    Interactions are detected via:
    - Correlation IDs (explicit)
    - Temporal proximity (within 100ms)
    - Shared resources (same inputs/outputs)
    """

    timestamp: datetime
    from_agent: str
    to_agent: str
    interaction_type: str  # "call", "response", "shared_data", "temporal"
    from_trace_id: str
    to_trace_id: str
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def agents(self) -> tuple[str, str]:
        """Get the agent pair."""
        return (self.from_agent, self.to_agent)


@dataclass
class TimelineView:
    """
    View of a single agent's timeline within the chronicle.

    Provides focused access to one agent's crystals and interactions.
    """

    agent_id: str
    traces: list[SemanticTrace]
    outgoing_interactions: list[Interaction]
    incoming_interactions: list[Interaction]

    @property
    def trace_count(self) -> int:
        """Number of traces in this timeline."""
        return len(self.traces)

    @property
    def duration(self) -> timedelta | None:
        """Duration of this agent's activity."""
        if not self.traces:
            return None
        return self.traces[-1].timestamp - self.traces[0].timestamp

    @property
    def total_gas(self) -> int:
        """Total gas consumed by this agent."""
        return sum(t.gas_consumed for t in self.traces)

    @property
    def collaborators(self) -> set[str]:
        """Agents this timeline interacted with."""
        agents = set()
        for i in self.outgoing_interactions:
            agents.add(i.to_agent)
        for i in self.incoming_interactions:
            agents.add(i.from_agent)
        return agents

    def errors(self) -> list[SemanticTrace]:
        """Get all error traces."""
        return [t for t in self.traces if t.action == "ERROR"]


class Chronicle:
    """
    A collection of crystals from multiple agents.

    NOT a story yet—that's the Bard's job.
    This is the structured substrate for multi-agent narratives.

    Usage:
        chronicle = Chronicle()

        # Add crystals from multiple agents
        for trace in agent_a_traces:
            chronicle.add_crystal(trace)
        for trace in agent_b_traces:
            chronicle.add_crystal(trace)

        # Weave into unified timeline
        timeline = chronicle.weave()

        # Generate a narrative
        narrative = await chronicle.to_narrative(bard)

        # View individual agent timelines
        view_a = chronicle.get_agent_timeline("AgentA")
    """

    def __init__(
        self,
        correlation_window_ms: int = 100,
        detect_interactions: bool = True,
    ):
        """
        Initialize the Chronicle.

        Args:
            correlation_window_ms: Max time between traces to consider temporal correlation
            detect_interactions: Whether to auto-detect interactions
        """
        self._crystals: dict[str, list[SemanticTrace]] = {}  # agent_id → traces
        self._interactions: list[Interaction] = []
        self._correlation_window = timedelta(milliseconds=correlation_window_ms)
        self._detect_interactions = detect_interactions
        self._trace_index: dict[str, SemanticTrace] = {}  # trace_id → trace

    @property
    def agent_ids(self) -> list[str]:
        """Get all agent IDs in the chronicle."""
        return list(self._crystals.keys())

    @property
    def interactions(self) -> list[Interaction]:
        """Get all detected interactions."""
        return self._interactions.copy()

    @property
    def total_traces(self) -> int:
        """Total number of traces across all agents."""
        return sum(len(traces) for traces in self._crystals.values())

    @property
    def agent_count(self) -> int:
        """Number of unique agents."""
        return len(self._crystals)

    @property
    def time_span(self) -> timedelta | None:
        """Total time span of the chronicle."""
        all_traces = self.weave()
        if not all_traces:
            return None
        return all_traces[-1].timestamp - all_traces[0].timestamp

    def add_crystal(self, trace: SemanticTrace) -> None:
        """
        Add a crystal to the chronicle.

        Automatically detects interactions if enabled.
        """
        # Add to agent's timeline
        if trace.agent_id not in self._crystals:
            self._crystals[trace.agent_id] = []
        self._crystals[trace.agent_id].append(trace)

        # Index for quick lookup
        self._trace_index[trace.trace_id] = trace

        # Sort the agent's timeline
        self._crystals[trace.agent_id].sort(key=lambda t: t.timestamp)

        # Detect interactions
        if self._detect_interactions:
            self._detect_interaction(trace)

    def add_crystals(self, traces: list[SemanticTrace]) -> None:
        """Add multiple crystals at once."""
        for trace in traces:
            self.add_crystal(trace)

    def add_interaction(self, interaction: Interaction) -> None:
        """Manually add an interaction."""
        self._interactions.append(interaction)

    def get_crystal(self, trace_id: str) -> SemanticTrace | None:
        """Get a crystal by ID."""
        return self._trace_index.get(trace_id)

    def get_agent_crystals(self, agent_id: str) -> list[SemanticTrace]:
        """Get all crystals for an agent."""
        return self._crystals.get(agent_id, []).copy()

    def get_agent_timeline(self, agent_id: str) -> TimelineView | None:
        """Get a view of an agent's timeline."""
        if agent_id not in self._crystals:
            return None

        traces = self._crystals[agent_id]
        outgoing = [i for i in self._interactions if i.from_agent == agent_id]
        incoming = [i for i in self._interactions if i.to_agent == agent_id]

        return TimelineView(
            agent_id=agent_id,
            traces=traces,
            outgoing_interactions=outgoing,
            incoming_interactions=incoming,
        )

    def weave(self) -> list[SemanticTrace]:
        """
        Interleave all crystals by timestamp.

        Returns a unified timeline, ready for the Bard.
        """
        all_traces: list[SemanticTrace] = []
        for traces in self._crystals.values():
            all_traces.extend(traces)

        return sorted(all_traces, key=lambda t: t.timestamp)

    def weave_around(
        self,
        trace_id: str,
        window: timedelta | None = None,
    ) -> list[SemanticTrace]:
        """
        Get traces around a specific trace.

        Useful for debugging - see what was happening when a trace occurred.
        """
        center_trace = self.get_crystal(trace_id)
        if not center_trace:
            return []

        window = window or timedelta(seconds=5)
        start_time = center_trace.timestamp - window
        end_time = center_trace.timestamp + window

        woven = self.weave()
        return [t for t in woven if start_time <= t.timestamp <= end_time]

    def filter_by_agents(self, agent_ids: list[str]) -> list[SemanticTrace]:
        """Get woven timeline for specific agents only."""
        traces: list[SemanticTrace] = []
        for agent_id in agent_ids:
            traces.extend(self._crystals.get(agent_id, []))
        return sorted(traces, key=lambda t: t.timestamp)

    def filter_by_time(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[SemanticTrace]:
        """Get woven timeline within a time range."""
        woven = self.weave()
        result = woven

        if start_time:
            result = [t for t in result if t.timestamp >= start_time]
        if end_time:
            result = [t for t in result if t.timestamp <= end_time]

        return result

    async def to_narrative(
        self,
        bard: Bard | None = None,
        genre: NarrativeGenre = NarrativeGenre.LITERARY,
        verbosity: Verbosity = Verbosity.NORMAL,
        title: str | None = None,
    ) -> Narrative:
        """
        Ask the Bard to tell the chronicle as a saga.

        Args:
            bard: The Bard to use (creates default if None)
            genre: Narrative genre
            verbosity: Level of detail
            title: Optional title

        Returns:
            A Narrative telling the multi-agent story
        """
        bard = bard or Bard()
        woven = self.weave()

        return await bard.invoke(
            NarrativeRequest(
                traces=woven,
                genre=genre,
                verbosity=verbosity,
                title=title or self._generate_chronicle_title(),
            )
        )

    def get_collaboration_graph(self) -> dict[str, list[str]]:
        """
        Get the collaboration graph between agents.

        Returns dict of agent_id -> list of collaborator IDs.
        """
        graph: dict[str, list[str]] = {agent_id: [] for agent_id in self._crystals}

        for interaction in self._interactions:
            if interaction.from_agent in graph:
                if interaction.to_agent not in graph[interaction.from_agent]:
                    graph[interaction.from_agent].append(interaction.to_agent)

        return graph

    def iter_interactions(
        self,
        agent_id: str | None = None,
    ) -> Iterator[Interaction]:
        """
        Iterate over interactions.

        Args:
            agent_id: Filter to interactions involving this agent
        """
        for interaction in self._interactions:
            if agent_id is None:
                yield interaction
            elif interaction.from_agent == agent_id or interaction.to_agent == agent_id:
                yield interaction

    def to_dict(self) -> dict[str, Any]:
        """Convert chronicle to dictionary for serialization."""
        return {
            "agents": list(self._crystals.keys()),
            "total_traces": self.total_traces,
            "interactions": len(self._interactions),
            "crystals": {
                agent_id: [t.to_dict() for t in traces]
                for agent_id, traces in self._crystals.items()
            },
            "interaction_list": [
                {
                    "timestamp": i.timestamp.isoformat(),
                    "from_agent": i.from_agent,
                    "to_agent": i.to_agent,
                    "type": i.interaction_type,
                    "from_trace_id": i.from_trace_id,
                    "to_trace_id": i.to_trace_id,
                }
                for i in self._interactions
            ],
        }

    def _detect_interaction(self, new_trace: SemanticTrace) -> None:
        """Detect interactions when a new trace is added."""
        # Check against all other agents' recent traces
        for agent_id, traces in self._crystals.items():
            if agent_id == new_trace.agent_id:
                continue

            for trace in traces:
                interaction = self._check_interaction(new_trace, trace)
                if interaction:
                    self._interactions.append(interaction)

    def _check_interaction(
        self,
        trace_a: SemanticTrace,
        trace_b: SemanticTrace,
    ) -> Interaction | None:
        """Check if two traces represent an interaction."""
        # Temporal proximity
        time_diff = abs((trace_a.timestamp - trace_b.timestamp).total_seconds())
        if time_diff * 1000 <= self._correlation_window.total_seconds() * 1000:
            # Determine direction based on timestamp
            if trace_a.timestamp < trace_b.timestamp:
                from_trace, to_trace = trace_a, trace_b
            else:
                from_trace, to_trace = trace_b, trace_a

            return Interaction(
                timestamp=from_trace.timestamp,
                from_agent=from_trace.agent_id,
                to_agent=to_trace.agent_id,
                interaction_type="temporal",
                from_trace_id=from_trace.trace_id,
                to_trace_id=to_trace.trace_id,
            )

        # Parent-child relationship
        if trace_a.parent_id == trace_b.trace_id:
            return Interaction(
                timestamp=trace_b.timestamp,
                from_agent=trace_b.agent_id,
                to_agent=trace_a.agent_id,
                interaction_type="call",
                from_trace_id=trace_b.trace_id,
                to_trace_id=trace_a.trace_id,
            )

        if trace_b.parent_id == trace_a.trace_id:
            return Interaction(
                timestamp=trace_a.timestamp,
                from_agent=trace_a.agent_id,
                to_agent=trace_b.agent_id,
                interaction_type="call",
                from_trace_id=trace_a.trace_id,
                to_trace_id=trace_b.trace_id,
            )

        return None

    def _generate_chronicle_title(self) -> str:
        """Generate a title for the chronicle."""
        agents = list(self._crystals.keys())
        if len(agents) == 0:
            return "Empty Chronicle"
        elif len(agents) == 1:
            return f"The {agents[0]} Chronicle"
        elif len(agents) == 2:
            return f"The {agents[0]} and {agents[1]} Collaboration"
        else:
            return f"The {len(agents)}-Agent Chronicle"


class ChronicleBuilder:
    """
    Fluent API for building chronicles.

    Usage:
        chronicle = (
            ChronicleBuilder()
            .with_correlation_window(200)  # 200ms
            .add_traces(agent_a_traces)
            .add_traces(agent_b_traces)
            .add_interaction(Interaction(...))
            .build()
        )
    """

    def __init__(self):
        self._correlation_window_ms = 100
        self._detect_interactions = True
        self._traces: list[SemanticTrace] = []
        self._manual_interactions: list[Interaction] = []

    def with_correlation_window(self, ms: int) -> ChronicleBuilder:
        """Set the correlation window in milliseconds."""
        self._correlation_window_ms = ms
        return self

    def without_interaction_detection(self) -> ChronicleBuilder:
        """Disable automatic interaction detection."""
        self._detect_interactions = False
        return self

    def add_trace(self, trace: SemanticTrace) -> ChronicleBuilder:
        """Add a single trace."""
        self._traces.append(trace)
        return self

    def add_traces(self, traces: list[SemanticTrace]) -> ChronicleBuilder:
        """Add multiple traces."""
        self._traces.extend(traces)
        return self

    def add_interaction(self, interaction: Interaction) -> ChronicleBuilder:
        """Add a manual interaction."""
        self._manual_interactions.append(interaction)
        return self

    def build(self) -> Chronicle:
        """Build the chronicle."""
        chronicle = Chronicle(
            correlation_window_ms=self._correlation_window_ms,
            detect_interactions=self._detect_interactions,
        )

        for trace in self._traces:
            chronicle.add_crystal(trace)

        for interaction in self._manual_interactions:
            chronicle.add_interaction(interaction)

        return chronicle


class CorrelationDetector:
    """
    Advanced correlation detection between agent traces.

    Detects:
    - Temporal correlations (proximity in time)
    - Causal correlations (parent-child relationships)
    - Data correlations (shared inputs/outputs)
    - Semantic correlations (via L-gent embeddings)
    """

    def __init__(
        self,
        temporal_window_ms: int = 100,
        semantic_threshold: float = 0.8,
    ):
        """
        Initialize the detector.

        Args:
            temporal_window_ms: Max time between traces for temporal correlation
            semantic_threshold: Min similarity for semantic correlation
        """
        self.temporal_window = timedelta(milliseconds=temporal_window_ms)
        self.semantic_threshold = semantic_threshold

    def detect_all(
        self,
        traces: list[SemanticTrace],
    ) -> list[Interaction]:
        """Detect all correlations between traces."""
        interactions: list[Interaction] = []

        # Sort by timestamp for efficient processing
        sorted_traces = sorted(traces, key=lambda t: t.timestamp)

        # Check each pair
        for i, trace_a in enumerate(sorted_traces):
            for trace_b in sorted_traces[i + 1 :]:
                # Skip same agent
                if trace_a.agent_id == trace_b.agent_id:
                    continue

                # Check temporal
                time_diff = (trace_b.timestamp - trace_a.timestamp).total_seconds()
                if time_diff > self.temporal_window.total_seconds():
                    break  # No more temporal correlations possible

                interaction = self._detect_correlation(trace_a, trace_b)
                if interaction:
                    interactions.append(interaction)

        return interactions

    def _detect_correlation(
        self,
        trace_a: SemanticTrace,
        trace_b: SemanticTrace,
    ) -> Interaction | None:
        """Detect correlation between two traces."""
        # Causal (parent-child)
        if trace_b.parent_id == trace_a.trace_id:
            return Interaction(
                timestamp=trace_a.timestamp,
                from_agent=trace_a.agent_id,
                to_agent=trace_b.agent_id,
                interaction_type="call",
                from_trace_id=trace_a.trace_id,
                to_trace_id=trace_b.trace_id,
            )

        # Data correlation (shared outputs -> inputs)
        if self._has_data_correlation(trace_a, trace_b):
            return Interaction(
                timestamp=trace_a.timestamp,
                from_agent=trace_a.agent_id,
                to_agent=trace_b.agent_id,
                interaction_type="data_flow",
                from_trace_id=trace_a.trace_id,
                to_trace_id=trace_b.trace_id,
            )

        # Semantic correlation (if vectors available)
        if trace_a.vector and trace_b.vector:
            similarity = self._cosine_similarity(
                list(trace_a.vector),
                list(trace_b.vector),
            )
            if similarity >= self.semantic_threshold:
                return Interaction(
                    timestamp=trace_a.timestamp,
                    from_agent=trace_a.agent_id,
                    to_agent=trace_b.agent_id,
                    interaction_type="semantic",
                    from_trace_id=trace_a.trace_id,
                    to_trace_id=trace_b.trace_id,
                    metadata={"similarity": similarity},
                )

        # Temporal (default fallback if close in time)
        return Interaction(
            timestamp=trace_a.timestamp,
            from_agent=trace_a.agent_id,
            to_agent=trace_b.agent_id,
            interaction_type="temporal",
            from_trace_id=trace_a.trace_id,
            to_trace_id=trace_b.trace_id,
        )

    def _has_data_correlation(
        self,
        trace_a: SemanticTrace,
        trace_b: SemanticTrace,
    ) -> bool:
        """Check if trace_a's outputs appear in trace_b's inputs."""
        if not trace_a.outputs or not trace_b.inputs:
            return False

        # Simple check: any shared keys with same values
        for key, value in trace_a.outputs.items():
            if key in trace_b.inputs and trace_b.inputs[key] == value:
                return True

        # Check output hash appears in inputs
        if trace_a.output_hash:
            for value in trace_b.inputs.values():
                if isinstance(value, str) and trace_a.output_hash in value:
                    return True

        return False

    def _cosine_similarity(
        self,
        vec_a: list[float],
        vec_b: list[float],
    ) -> float:
        """Calculate cosine similarity between vectors."""
        if len(vec_a) != len(vec_b):
            return 0.0

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
