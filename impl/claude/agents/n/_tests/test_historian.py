"""Tests for the Historian: invisible crystal collector."""

import pytest

from ..historian import Historian, TracingContext
from ..store import MemoryCrystalStore
from ..types import Action, Determinism


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str = "mock-agent", genus: str = "T"):
        self._name = name
        self._genus = genus

    @property
    def name(self) -> str:
        return self._name

    @property
    def genus(self) -> str:
        return self._genus

    async def invoke(self, input_data):
        return {"result": f"processed {input_data}"}


class TestHistorian:
    """Tests for Historian class."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        """Create a fresh store for each test."""
        return MemoryCrystalStore()

    @pytest.fixture
    def historian(self, store) -> Historian:
        """Create a historian with a fresh store."""
        h = Historian(store)
        h.reset_context()  # Ensure clean state for each test
        return h

    @pytest.fixture
    def agent(self) -> MockAgent:
        """Create a mock agent."""
        return MockAgent()

    def test_historian_creation(self, store):
        """Can create historian with store."""
        historian = Historian(store)
        assert historian.store is store

    def test_begin_trace(self, historian, agent):
        """Begin trace creates context."""
        ctx = historian.begin_trace(agent, {"question": "test"})

        assert ctx.trace_id is not None
        assert ctx.agent_id == "mock-agent"
        assert ctx.agent_genus == "T"
        assert ctx.input_hash is not None
        assert len(ctx.input_snapshot) > 0

    def test_begin_trace_sets_current(self, historian, agent):
        """Begin trace sets current trace ID."""
        ctx = historian.begin_trace(agent, {})
        assert historian.get_current_trace_id() == ctx.trace_id

    def test_end_trace_creates_crystal(self, historian, agent, store):
        """End trace creates and stores crystal."""
        ctx = historian.begin_trace(agent, {"input": "data"})
        crystal = historian.end_trace(ctx, Action.INVOKE, {"output": "result"})

        assert crystal.trace_id == ctx.trace_id
        assert crystal.agent_id == "mock-agent"
        assert crystal.action == Action.INVOKE
        assert crystal.outputs == {"output": "result"}

        # Crystal is stored
        stored = store.get(crystal.trace_id)
        assert stored is not None
        assert stored.trace_id == crystal.trace_id

    def test_end_trace_restores_parent(self, historian, agent):
        """End trace restores parent trace context."""
        # No parent initially
        assert historian.get_current_trace_id() is None

        ctx = historian.begin_trace(agent, {})
        assert historian.get_current_trace_id() == ctx.trace_id

        historian.end_trace(ctx, Action.INVOKE, {})
        assert historian.get_current_trace_id() is None

    def test_nested_traces(self, historian, agent):
        """Nested traces track parent-child relationship."""
        outer = historian.begin_trace(agent, {"level": "outer"})
        inner = historian.begin_trace(agent, {"level": "inner"})

        assert inner.parent_id == outer.trace_id
        assert historian.get_current_trace_id() == inner.trace_id

        historian.end_trace(inner, Action.INVOKE, {})
        assert historian.get_current_trace_id() == outer.trace_id

        historian.end_trace(outer, Action.INVOKE, {})
        assert historian.get_current_trace_id() is None

    def test_abort_trace_records_error(self, historian, agent, store):
        """Abort trace records error crystal."""
        ctx = historian.begin_trace(agent, {"input": "will fail"})

        error = ValueError("Something went wrong")
        crystal = historian.abort_trace(ctx, error)

        assert crystal.action == Action.ERROR
        assert crystal.outputs["error"] == "Something went wrong"
        assert crystal.outputs["type"] == "ValueError"
        assert crystal.determinism == Determinism.CHAOTIC

        stored = store.get(crystal.trace_id)
        assert stored is not None

    def test_abort_with_string_error(self, historian, agent):
        """Can abort with string error message."""
        ctx = historian.begin_trace(agent, {})
        crystal = historian.abort_trace(ctx, "Manual error message")

        assert crystal.outputs["error"] == "Manual error message"
        assert crystal.outputs["type"] == "Error"

    def test_duration_recorded(self, historian, agent):
        """Duration is recorded in milliseconds."""
        import time

        ctx = historian.begin_trace(agent, {})
        time.sleep(0.01)  # 10ms delay
        crystal = historian.end_trace(ctx, Action.INVOKE, {})

        assert crystal.duration_ms >= 10

    def test_gas_estimation(self, historian, agent):
        """Gas is estimated from input/output size."""
        ctx = historian.begin_trace(agent, {"large": "x" * 1000})
        crystal = historian.end_trace(ctx, Action.INVOKE, {"result": "y" * 500})

        # Rough estimate: 4 bytes per token
        assert crystal.gas_consumed > 0

    def test_determinism_auto_detected(self, historian, agent):
        """Determinism is auto-detected from action."""
        ctx = historian.begin_trace(agent, {})

        lookup = historian.end_trace(ctx, Action.LOOKUP, {})
        assert lookup.determinism == Determinism.DETERMINISTIC

        ctx = historian.begin_trace(agent, {})
        generate = historian.end_trace(ctx, Action.GENERATE, {})
        assert generate.determinism == Determinism.PROBABILISTIC

        ctx = historian.begin_trace(agent, {})
        api = historian.end_trace(ctx, Action.CALL_API, {})
        assert api.determinism == Determinism.CHAOTIC

    def test_determinism_override(self, historian, agent):
        """Can override auto-detected determinism."""
        ctx = historian.begin_trace(agent, {})
        crystal = historian.end_trace(
            ctx, Action.INVOKE, {}, determinism=Determinism.DETERMINISTIC
        )

        assert crystal.determinism == Determinism.DETERMINISTIC

    def test_input_hash_consistent(self, historian, agent):
        """Same input produces same hash."""
        input_data = {"key": "value", "number": 42}

        ctx1 = historian.begin_trace(agent, input_data)
        ctx2 = historian.begin_trace(agent, input_data)

        assert ctx1.input_hash == ctx2.input_hash

    def test_different_input_different_hash(self, historian, agent):
        """Different input produces different hash."""
        ctx1 = historian.begin_trace(agent, {"a": 1})
        ctx2 = historian.begin_trace(agent, {"b": 2})

        assert ctx1.input_hash != ctx2.input_hash

    def test_non_traceable_agent(self, historian):
        """Works with non-Traceable agents via fallback."""

        class PlainAgent:
            pass

        agent = PlainAgent()
        ctx = historian.begin_trace(agent, {})

        assert ctx.agent_id == "PlainAgent"
        assert ctx.agent_genus == "unknown"


class TestTracingContext:
    """Tests for TracingContext context manager."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        return MemoryCrystalStore()

    @pytest.fixture
    def historian(self, store) -> Historian:
        h = Historian(store)
        h.reset_context()
        return h

    @pytest.fixture
    def agent(self) -> MockAgent:
        return MockAgent()

    def test_context_manager_success(self, historian, agent, store):
        """Context manager records successful trace."""
        with TracingContext(historian, agent, {"test": "input"}) as ctx:
            ctx.set_result({"output": "success"})

        assert store.count() == 1
        crystal = list(store.iter_all())[0]
        assert crystal.action == Action.INVOKE
        assert crystal.outputs == {"output": "success"}

    def test_context_manager_exception(self, historian, agent, store):
        """Context manager records failed trace on exception."""
        with pytest.raises(ValueError):
            with TracingContext(historian, agent, {}):
                raise ValueError("test error")

        assert store.count() == 1
        crystal = list(store.iter_all())[0]
        assert crystal.action == Action.ERROR
        assert "test error" in crystal.outputs["error"]

    def test_context_manager_trace_id(self, historian, agent):
        """Can access trace ID during execution."""
        with TracingContext(historian, agent, {}) as ctx:
            assert ctx.trace_id is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self, historian, agent, store):
        """Async context manager works correctly."""
        async with TracingContext(historian, agent, {}) as ctx:
            ctx.set_result({"async": True})

        assert store.count() == 1
