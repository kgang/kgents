"""
Tests for N-gent Phase 4: Chronicle (multi-agent weaving).

Tests:
- Interaction: Points where agent timelines intersect
- Chronicle: Multi-agent crystal collection
- ChronicleBuilder: Fluent API
- TimelineView: Single agent timeline
- CorrelationDetector: Advanced correlation detection
"""

import pytest
from datetime import datetime, timedelta
from typing import Any

from ..types import Determinism, SemanticTrace
from ..bard import NarrativeGenre
from ..chronicle import (
    Chronicle,
    ChronicleBuilder,
    CorrelationDetector,
    Interaction,
    TimelineView,
)


# =============================================================================
# Fixtures
# =============================================================================


def make_trace(
    trace_id: str = "trace-1",
    agent_id: str = "AgentA",
    agent_genus: str = "T",
    action: str = "INVOKE",
    parent_id: str | None = None,
    timestamp: datetime | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    duration_ms: int = 50,
) -> SemanticTrace:
    """Create a test trace."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=timestamp or datetime.utcnow(),
        agent_id=agent_id,
        agent_genus=agent_genus,
        action=action,
        inputs=inputs or {"prompt": "test"},
        outputs=outputs or {"result": "success"},
        input_hash="abc123",
        input_snapshot=b'{"prompt": "test"}',
        output_hash="def456",
        gas_consumed=100,
        duration_ms=duration_ms,
        determinism=Determinism.PROBABILISTIC,
    )


def make_multi_agent_traces() -> list[SemanticTrace]:
    """Create traces from multiple agents with interactions."""
    base_time = datetime.utcnow()

    traces = [
        # Agent A starts
        make_trace("a-1", "AgentA", timestamp=base_time),
        # Agent A calls Agent B
        make_trace(
            "b-1",
            "AgentB",
            parent_id="a-1",
            timestamp=base_time + timedelta(milliseconds=10),
        ),
        # Agent B completes
        make_trace(
            "b-2",
            "AgentB",
            parent_id="b-1",
            timestamp=base_time + timedelta(milliseconds=50),
        ),
        # Agent A processes result
        make_trace(
            "a-2",
            "AgentA",
            parent_id="a-1",
            timestamp=base_time + timedelta(milliseconds=60),
        ),
        # Agent C joins (temporal correlation)
        make_trace("c-1", "AgentC", timestamp=base_time + timedelta(milliseconds=70)),
    ]
    return traces


# =============================================================================
# Interaction Tests
# =============================================================================


class TestInteraction:
    """Tests for Interaction dataclass."""

    def test_interaction_creation(self):
        """Test creating an interaction."""
        interaction = Interaction(
            timestamp=datetime.utcnow(),
            from_agent="AgentA",
            to_agent="AgentB",
            interaction_type="call",
            from_trace_id="a-1",
            to_trace_id="b-1",
        )

        assert interaction.from_agent == "AgentA"
        assert interaction.to_agent == "AgentB"
        assert interaction.interaction_type == "call"

    def test_interaction_agents_property(self):
        """Test agents property."""
        interaction = Interaction(
            timestamp=datetime.utcnow(),
            from_agent="AgentA",
            to_agent="AgentB",
            interaction_type="call",
            from_trace_id="a-1",
            to_trace_id="b-1",
        )

        assert interaction.agents == ("AgentA", "AgentB")

    def test_interaction_with_correlation_id(self):
        """Test interaction with correlation ID."""
        interaction = Interaction(
            timestamp=datetime.utcnow(),
            from_agent="AgentA",
            to_agent="AgentB",
            interaction_type="call",
            from_trace_id="a-1",
            to_trace_id="b-1",
            correlation_id="corr-123",
        )

        assert interaction.correlation_id == "corr-123"


# =============================================================================
# TimelineView Tests
# =============================================================================


class TestTimelineView:
    """Tests for TimelineView."""

    def test_timeline_view_creation(self):
        """Test creating a timeline view."""
        traces = [make_trace("t-1"), make_trace("t-2")]
        view = TimelineView(
            agent_id="AgentA",
            traces=traces,
            outgoing_interactions=[],
            incoming_interactions=[],
        )

        assert view.agent_id == "AgentA"
        assert view.trace_count == 2

    def test_timeline_view_duration(self):
        """Test duration property."""
        base_time = datetime.utcnow()
        traces = [
            make_trace("t-1", timestamp=base_time),
            make_trace("t-2", timestamp=base_time + timedelta(seconds=5)),
        ]
        view = TimelineView(
            agent_id="AgentA",
            traces=traces,
            outgoing_interactions=[],
            incoming_interactions=[],
        )

        assert view.duration is not None
        assert view.duration.total_seconds() == 5

    def test_timeline_view_total_gas(self):
        """Test total_gas property."""
        traces = [
            make_trace("t-1"),  # 100 gas each
            make_trace("t-2"),
        ]
        view = TimelineView(
            agent_id="AgentA",
            traces=traces,
            outgoing_interactions=[],
            incoming_interactions=[],
        )

        assert view.total_gas == 200

    def test_timeline_view_collaborators(self):
        """Test collaborators property."""
        traces = [make_trace("t-1")]
        outgoing = [
            Interaction(
                timestamp=datetime.utcnow(),
                from_agent="AgentA",
                to_agent="AgentB",
                interaction_type="call",
                from_trace_id="t-1",
                to_trace_id="b-1",
            )
        ]
        incoming = [
            Interaction(
                timestamp=datetime.utcnow(),
                from_agent="AgentC",
                to_agent="AgentA",
                interaction_type="call",
                from_trace_id="c-1",
                to_trace_id="t-1",
            )
        ]

        view = TimelineView(
            agent_id="AgentA",
            traces=traces,
            outgoing_interactions=outgoing,
            incoming_interactions=incoming,
        )

        assert view.collaborators == {"AgentB", "AgentC"}

    def test_timeline_view_errors(self):
        """Test errors method."""
        traces = [
            make_trace("t-1", action="INVOKE"),
            make_trace("t-2", action="ERROR"),
            make_trace("t-3", action="INVOKE"),
        ]
        view = TimelineView(
            agent_id="AgentA",
            traces=traces,
            outgoing_interactions=[],
            incoming_interactions=[],
        )

        errors = view.errors()
        assert len(errors) == 1
        assert errors[0].action == "ERROR"


# =============================================================================
# Chronicle Tests
# =============================================================================


class TestChronicle:
    """Tests for Chronicle multi-agent weaving."""

    def test_chronicle_creation(self):
        """Test creating a chronicle."""
        chronicle = Chronicle()

        assert chronicle.agent_ids == []
        assert chronicle.total_traces == 0
        assert chronicle.agent_count == 0

    def test_add_crystal(self):
        """Test adding a crystal."""
        chronicle = Chronicle()
        trace = make_trace("t-1", "AgentA")

        chronicle.add_crystal(trace)

        assert chronicle.total_traces == 1
        assert "AgentA" in chronicle.agent_ids

    def test_add_crystals(self):
        """Test adding multiple crystals."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()

        chronicle.add_crystals(traces)

        assert chronicle.total_traces == 5
        assert chronicle.agent_count == 3

    def test_get_crystal(self):
        """Test getting a crystal by ID."""
        chronicle = Chronicle()
        trace = make_trace("t-1", "AgentA")
        chronicle.add_crystal(trace)

        result = chronicle.get_crystal("t-1")
        assert result is not None
        assert result.trace_id == "t-1"

    def test_get_crystal_not_found(self):
        """Test getting a non-existent crystal."""
        chronicle = Chronicle()

        result = chronicle.get_crystal("nonexistent")
        assert result is None

    def test_get_agent_crystals(self):
        """Test getting crystals for an agent."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        agent_a_crystals = chronicle.get_agent_crystals("AgentA")
        assert len(agent_a_crystals) == 2

    def test_weave(self):
        """Test weaving crystals into timeline."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        woven = chronicle.weave()

        assert len(woven) == 5
        # Should be sorted by timestamp
        for i in range(len(woven) - 1):
            assert woven[i].timestamp <= woven[i + 1].timestamp

    def test_weave_around(self):
        """Test weaving around a specific trace."""
        chronicle = Chronicle()
        base_time = datetime.utcnow()
        traces = [
            make_trace("t-1", timestamp=base_time),
            make_trace("t-2", timestamp=base_time + timedelta(seconds=2)),
            make_trace("t-3", timestamp=base_time + timedelta(seconds=10)),
        ]
        chronicle.add_crystals(traces)

        # Get traces within 5 seconds of t-2
        nearby = chronicle.weave_around("t-2", window=timedelta(seconds=5))

        assert len(nearby) == 2  # t-1 and t-2

    def test_filter_by_agents(self):
        """Test filtering by agents."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        filtered = chronicle.filter_by_agents(["AgentA", "AgentB"])

        assert all(t.agent_id in ["AgentA", "AgentB"] for t in filtered)
        assert len(filtered) == 4

    def test_filter_by_time(self):
        """Test filtering by time range."""
        chronicle = Chronicle()
        base_time = datetime.utcnow()
        traces = [
            make_trace("t-1", timestamp=base_time),
            make_trace("t-2", timestamp=base_time + timedelta(seconds=5)),
            make_trace("t-3", timestamp=base_time + timedelta(seconds=10)),
        ]
        chronicle.add_crystals(traces)

        filtered = chronicle.filter_by_time(
            start_time=base_time + timedelta(seconds=2),
            end_time=base_time + timedelta(seconds=8),
        )

        assert len(filtered) == 1
        assert filtered[0].trace_id == "t-2"

    def test_get_agent_timeline(self):
        """Test getting agent timeline view."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        view = chronicle.get_agent_timeline("AgentA")

        assert view is not None
        assert view.agent_id == "AgentA"
        assert view.trace_count == 2

    def test_get_agent_timeline_not_found(self):
        """Test getting timeline for non-existent agent."""
        chronicle = Chronicle()

        view = chronicle.get_agent_timeline("NonexistentAgent")
        assert view is None

    def test_time_span(self):
        """Test time_span property."""
        chronicle = Chronicle()
        base_time = datetime.utcnow()
        traces = [
            make_trace("t-1", timestamp=base_time),
            make_trace("t-2", timestamp=base_time + timedelta(seconds=10)),
        ]
        chronicle.add_crystals(traces)

        span = chronicle.time_span
        assert span is not None
        assert span.total_seconds() == 10

    def test_interaction_detection(self):
        """Test automatic interaction detection."""
        chronicle = Chronicle(correlation_window_ms=100)
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        interactions = chronicle.interactions

        # Should detect parent-child interactions
        assert len(interactions) > 0

    def test_interaction_detection_disabled(self):
        """Test with interaction detection disabled."""
        chronicle = Chronicle(detect_interactions=False)
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        interactions = chronicle.interactions
        assert len(interactions) == 0

    def test_get_collaboration_graph(self):
        """Test getting collaboration graph."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        graph = chronicle.get_collaboration_graph()

        assert "AgentA" in graph
        assert "AgentB" in graph
        assert "AgentC" in graph

    @pytest.mark.asyncio
    async def test_to_narrative(self):
        """Test generating narrative from chronicle."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        narrative = await chronicle.to_narrative(genre=NarrativeGenre.TECHNICAL)

        assert narrative is not None
        assert len(narrative.traces_used) == 5

    def test_to_dict(self):
        """Test chronicle serialization."""
        chronicle = Chronicle()
        traces = [make_trace("t-1", "AgentA")]
        chronicle.add_crystals(traces)

        data = chronicle.to_dict()

        assert "agents" in data
        assert "total_traces" in data
        assert data["total_traces"] == 1

    def test_iter_interactions(self):
        """Test iterating over interactions."""
        chronicle = Chronicle()
        traces = make_multi_agent_traces()
        chronicle.add_crystals(traces)

        # Add manual interaction
        chronicle.add_interaction(
            Interaction(
                timestamp=datetime.utcnow(),
                from_agent="AgentA",
                to_agent="AgentB",
                interaction_type="manual",
                from_trace_id="a-1",
                to_trace_id="b-1",
            )
        )

        all_interactions = list(chronicle.iter_interactions())
        agent_a_interactions = list(chronicle.iter_interactions("AgentA"))

        assert len(agent_a_interactions) <= len(all_interactions)


# =============================================================================
# ChronicleBuilder Tests
# =============================================================================


class TestChronicleBuilder:
    """Tests for ChronicleBuilder fluent API."""

    def test_builder_basic(self):
        """Test basic builder usage."""
        traces = make_multi_agent_traces()

        chronicle = ChronicleBuilder().add_traces(traces).build()

        assert chronicle.total_traces == 5

    def test_builder_with_correlation_window(self):
        """Test setting correlation window."""
        traces = make_multi_agent_traces()

        chronicle = (
            ChronicleBuilder().with_correlation_window(200).add_traces(traces).build()
        )

        assert chronicle.total_traces == 5

    def test_builder_without_interaction_detection(self):
        """Test disabling interaction detection."""
        traces = make_multi_agent_traces()

        chronicle = (
            ChronicleBuilder()
            .without_interaction_detection()
            .add_traces(traces)
            .build()
        )

        assert len(chronicle.interactions) == 0

    def test_builder_add_single_trace(self):
        """Test adding single trace."""
        trace = make_trace("t-1")

        chronicle = ChronicleBuilder().add_trace(trace).build()

        assert chronicle.total_traces == 1

    def test_builder_add_manual_interaction(self):
        """Test adding manual interaction."""
        trace = make_trace("t-1")
        interaction = Interaction(
            timestamp=datetime.utcnow(),
            from_agent="AgentA",
            to_agent="AgentB",
            interaction_type="manual",
            from_trace_id="t-1",
            to_trace_id="b-1",
        )

        chronicle = (
            ChronicleBuilder().add_trace(trace).add_interaction(interaction).build()
        )

        assert len(chronicle.interactions) >= 1


# =============================================================================
# CorrelationDetector Tests
# =============================================================================


class TestCorrelationDetector:
    """Tests for CorrelationDetector."""

    def test_detector_creation(self):
        """Test creating a detector."""
        detector = CorrelationDetector(
            temporal_window_ms=200,
            semantic_threshold=0.9,
        )

        assert detector.temporal_window.total_seconds() == 0.2
        assert detector.semantic_threshold == 0.9

    def test_detect_all(self):
        """Test detecting all correlations."""
        detector = CorrelationDetector(temporal_window_ms=100)
        traces = make_multi_agent_traces()

        interactions = detector.detect_all(traces)

        # Should detect parent-child and temporal correlations
        assert len(interactions) > 0

    def test_detect_parent_child(self):
        """Test detecting parent-child correlations."""
        detector = CorrelationDetector(
            temporal_window_ms=50
        )  # Small window to test parent-child specifically
        base_time = datetime.utcnow()

        traces = [
            make_trace("parent", "AgentA", timestamp=base_time),
            make_trace(
                "child",
                "AgentB",
                parent_id="parent",
                timestamp=base_time + timedelta(milliseconds=30),
            ),
        ]

        interactions = detector.detect_all(traces)

        # Should find the parent-child relationship (within temporal window)
        assert len(interactions) >= 1
        # At least one should be detected (could be temporal or call type)
        assert any(
            i.from_trace_id == "parent" or i.to_trace_id == "child"
            for i in interactions
        )

    def test_detect_temporal_correlation(self):
        """Test detecting temporal correlations."""
        detector = CorrelationDetector(temporal_window_ms=100)
        base_time = datetime.utcnow()

        traces = [
            make_trace("t-1", "AgentA", timestamp=base_time),
            make_trace(
                "t-2", "AgentB", timestamp=base_time + timedelta(milliseconds=50)
            ),
        ]

        interactions = detector.detect_all(traces)

        # Should find temporal correlation
        assert len(interactions) >= 1

    def test_no_correlation_outside_window(self):
        """Test no correlation for traces outside window."""
        detector = CorrelationDetector(temporal_window_ms=100)
        base_time = datetime.utcnow()

        traces = [
            make_trace("t-1", "AgentA", timestamp=base_time),
            make_trace("t-2", "AgentB", timestamp=base_time + timedelta(seconds=10)),
        ]

        interactions = detector.detect_all(traces)

        # No temporal correlations (outside window)
        temporal = [i for i in interactions if i.interaction_type == "temporal"]
        assert len(temporal) == 0

    def test_same_agent_no_correlation(self):
        """Test no correlation between same agent's traces."""
        detector = CorrelationDetector()
        base_time = datetime.utcnow()

        traces = [
            make_trace("t-1", "AgentA", timestamp=base_time),
            make_trace(
                "t-2", "AgentA", timestamp=base_time + timedelta(milliseconds=10)
            ),
        ]

        interactions = detector.detect_all(traces)

        # Same agent traces should not create interactions
        assert len(interactions) == 0
