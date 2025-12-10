"""Tests for N-gent types: SemanticTrace and related structures."""

from datetime import datetime

import pytest

from ..types import Action, Determinism, SemanticTrace, TraceContext


class TestDeterminism:
    """Tests for Determinism enum."""

    def test_determinism_values(self):
        """Verify enum values."""
        assert Determinism.DETERMINISTIC.value == "deterministic"
        assert Determinism.PROBABILISTIC.value == "probabilistic"
        assert Determinism.CHAOTIC.value == "chaotic"

    def test_determinism_from_string(self):
        """Can create from string value."""
        assert Determinism("deterministic") == Determinism.DETERMINISTIC
        assert Determinism("probabilistic") == Determinism.PROBABILISTIC
        assert Determinism("chaotic") == Determinism.CHAOTIC


class TestAction:
    """Tests for Action constants and classification."""

    def test_action_constants(self):
        """Verify action constants exist."""
        assert Action.INVOKE == "INVOKE"
        assert Action.GENERATE == "GENERATE"
        assert Action.ERROR == "ERROR"
        assert Action.LOOKUP == "LOOKUP"

    def test_classify_deterministic(self):
        """Deterministic actions classified correctly."""
        assert Action.classify_determinism(Action.LOOKUP) == Determinism.DETERMINISTIC
        assert (
            Action.classify_determinism(Action.TRANSFORM) == Determinism.DETERMINISTIC
        )
        assert Action.classify_determinism(Action.PARSE) == Determinism.DETERMINISTIC
        assert Action.classify_determinism(Action.VALIDATE) == Determinism.DETERMINISTIC

    def test_classify_chaotic(self):
        """Chaotic actions classified correctly."""
        assert Action.classify_determinism(Action.CALL_API) == Determinism.CHAOTIC
        assert Action.classify_determinism(Action.CALL_TOOL) == Determinism.CHAOTIC
        assert Action.classify_determinism(Action.ERROR) == Determinism.CHAOTIC

    def test_classify_probabilistic(self):
        """Default actions are probabilistic."""
        assert Action.classify_determinism(Action.INVOKE) == Determinism.PROBABILISTIC
        assert Action.classify_determinism(Action.GENERATE) == Determinism.PROBABILISTIC
        assert Action.classify_determinism(Action.DECIDE) == Determinism.PROBABILISTIC
        assert Action.classify_determinism("unknown") == Determinism.PROBABILISTIC


class TestSemanticTrace:
    """Tests for SemanticTrace (the Crystal)."""

    @pytest.fixture
    def sample_trace(self) -> SemanticTrace:
        """Create a sample trace for testing."""
        return SemanticTrace(
            trace_id="test-123",
            parent_id=None,
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            agent_id="test-agent",
            agent_genus="B",
            action="INVOKE",
            inputs={"question": "What is the answer?"},
            outputs={"answer": 42},
            input_hash="abc123",
            input_snapshot=b'{"question": "What is the answer?"}',
            output_hash="def456",
            gas_consumed=100,
            duration_ms=50,
            vector=None,
            determinism=Determinism.PROBABILISTIC,
            metadata={"test": True},
        )

    def test_trace_is_frozen(self, sample_trace):
        """SemanticTrace is immutable."""
        with pytest.raises(AttributeError):
            sample_trace.agent_id = "new-agent"

    def test_trace_has_required_fields(self, sample_trace):
        """Verify all required fields are present."""
        assert sample_trace.trace_id == "test-123"
        assert sample_trace.agent_id == "test-agent"
        assert sample_trace.agent_genus == "B"
        assert sample_trace.action == "INVOKE"
        assert sample_trace.inputs == {"question": "What is the answer?"}
        assert sample_trace.outputs == {"answer": 42}

    def test_trace_parent_id_optional(self, sample_trace):
        """Parent ID can be None for root traces."""
        assert sample_trace.parent_id is None

        nested = SemanticTrace(
            trace_id="child-456",
            parent_id="test-123",
            timestamp=datetime.utcnow(),
            agent_id="child-agent",
            agent_genus="G",
            action="GENERATE",
            inputs={},
            outputs={},
            input_hash="",
            input_snapshot=b"",
            output_hash=None,
            gas_consumed=0,
            duration_ms=0,
        )
        assert nested.parent_id == "test-123"

    def test_trace_vector_optional(self, sample_trace):
        """Vector is optional (computed later by L-gent)."""
        assert sample_trace.vector is None

    def test_trace_with_vector(self, sample_trace):
        """Can create new trace with vector."""
        vector = [0.1, 0.2, 0.3, 0.4]
        with_vector = sample_trace.with_vector(vector)

        assert with_vector.vector == (0.1, 0.2, 0.3, 0.4)
        assert with_vector.trace_id == sample_trace.trace_id
        assert sample_trace.vector is None  # Original unchanged

    def test_trace_to_dict(self, sample_trace):
        """Conversion to dict for serialization."""
        data = sample_trace.to_dict()

        assert data["trace_id"] == "test-123"
        assert data["agent_id"] == "test-agent"
        assert data["agent_genus"] == "B"
        assert data["action"] == "INVOKE"
        assert data["inputs"] == {"question": "What is the answer?"}
        assert data["outputs"] == {"answer": 42}
        assert data["determinism"] == "probabilistic"
        assert "timestamp" in data

    def test_trace_from_dict(self, sample_trace):
        """Reconstruction from dict."""
        data = sample_trace.to_dict()
        restored = SemanticTrace.from_dict(
            data, input_snapshot=sample_trace.input_snapshot
        )

        assert restored.trace_id == sample_trace.trace_id
        assert restored.agent_id == sample_trace.agent_id
        assert restored.action == sample_trace.action
        assert restored.determinism == sample_trace.determinism

    def test_trace_roundtrip(self, sample_trace):
        """Dict conversion roundtrip preserves data."""
        data = sample_trace.to_dict()
        restored = SemanticTrace.from_dict(
            data, input_snapshot=sample_trace.input_snapshot
        )
        data2 = restored.to_dict()

        # Compare dicts (excluding input_snapshot which isn't in dict)
        assert data == data2


class TestTraceContext:
    """Tests for TraceContext."""

    def test_context_creation(self):
        """Can create trace context."""
        ctx = TraceContext(
            trace_id="ctx-123",
            parent_id=None,
            agent_id="test-agent",
            agent_genus="B",
            input_snapshot=b"test data",
            input_hash="abc123",
            start_time=datetime.utcnow(),
        )

        assert ctx.trace_id == "ctx-123"
        assert ctx.agent_id == "test-agent"
        assert ctx.parent_id is None

    def test_context_with_parent(self):
        """Context can have parent for nested calls."""
        ctx = TraceContext(
            trace_id="child-456",
            parent_id="parent-123",
            agent_id="child-agent",
            agent_genus="G",
            input_snapshot=b"nested data",
            input_hash="def456",
            start_time=datetime.utcnow(),
        )

        assert ctx.parent_id == "parent-123"
