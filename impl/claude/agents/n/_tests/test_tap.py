"""Tests for HistorianTap wire protocol integration."""

from datetime import datetime, timezone

import pytest

from ..historian import Historian
from ..store import MemoryCrystalStore
from ..tap import FrameType, HistorianTap, WireFrame, WireIntegration
from ..types import Action, Determinism


def make_frame(
    frame_type: FrameType,
    correlation_id: str = "corr-123",
    agent_id: str = "test-agent",
    agent_genus: str = "B",
    payload: any = None,
    metadata: dict | None = None,
) -> WireFrame:
    """Helper to create test frames."""
    return WireFrame(
        frame_type=frame_type,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc),
        agent_id=agent_id,
        agent_genus=agent_genus,
        payload=payload or {},
        metadata=metadata or {},
    )


class TestWireFrame:
    """Tests for WireFrame data class."""

    def test_frame_creation(self):
        """Can create a wire frame."""
        frame = make_frame(FrameType.INVOKE_START)
        assert frame.frame_type == FrameType.INVOKE_START
        assert frame.correlation_id == "corr-123"
        assert frame.agent_id == "test-agent"

    def test_frame_action_from_metadata(self):
        """Action extracted from metadata."""
        frame = make_frame(
            FrameType.INVOKE_END,
            metadata={"action": "GENERATE"},
        )
        assert frame.action == "GENERATE"

    def test_frame_action_default(self):
        """Action defaults to INVOKE."""
        frame = make_frame(FrameType.INVOKE_END)
        assert frame.action == Action.INVOKE

    def test_frame_determinism_hint_llm(self):
        """Determinism hint for LLM calls."""
        frame = make_frame(
            FrameType.INVOKE_END,
            metadata={"llm_call": True},
        )
        assert frame.determinism_hint == Determinism.PROBABILISTIC

    def test_frame_determinism_hint_api(self):
        """Determinism hint for external APIs."""
        frame = make_frame(
            FrameType.INVOKE_END,
            metadata={"external_api": True},
        )
        assert frame.determinism_hint == Determinism.CHAOTIC

    def test_frame_determinism_hint_explicit(self):
        """Explicit determinism in metadata."""
        frame = make_frame(
            FrameType.INVOKE_END,
            metadata={"determinism": "deterministic"},
        )
        assert frame.determinism_hint == Determinism.DETERMINISTIC


class TestHistorianTap:
    """Tests for HistorianTap."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        return MemoryCrystalStore()

    @pytest.fixture
    def historian(self, store) -> Historian:
        h = Historian(store)
        h.reset_context()
        return h

    @pytest.fixture
    def tap(self, historian) -> HistorianTap:
        return HistorianTap(historian)

    def test_tap_creation(self, historian):
        """Can create a tap."""
        tap = HistorianTap(historian)
        assert tap.historian is historian
        assert tap.active_traces == 0

    @pytest.mark.asyncio
    async def test_tap_passes_through(self, tap):
        """Tap returns frame unchanged."""
        frame = make_frame(FrameType.LOG_EVENT)
        result = await tap.on_frame(frame)
        assert result is frame

    @pytest.mark.asyncio
    async def test_invoke_start_begins_trace(self, tap, store):
        """INVOKE_START begins a trace."""
        frame = make_frame(
            FrameType.INVOKE_START,
            payload={"input": "test"},
        )
        await tap.on_frame(frame)

        assert tap.active_traces == 1
        assert "corr-123" in tap.get_pending_trace_ids()

    @pytest.mark.asyncio
    async def test_invoke_end_completes_trace(self, tap, store):
        """INVOKE_END completes the trace."""
        start = make_frame(
            FrameType.INVOKE_START,
            payload={"input": "test"},
        )
        await tap.on_frame(start)
        assert tap.active_traces == 1

        end = make_frame(
            FrameType.INVOKE_END,
            payload={"output": "result"},
        )
        await tap.on_frame(end)

        assert tap.active_traces == 0
        assert store.count() == 1

        crystal = list(store.iter_all())[0]
        assert crystal.agent_id == "test-agent"
        assert crystal.outputs == {"output": "result"}

    @pytest.mark.asyncio
    async def test_error_aborts_trace(self, tap, store):
        """ERROR aborts the trace."""
        start = make_frame(FrameType.INVOKE_START)
        await tap.on_frame(start)

        error = make_frame(
            FrameType.ERROR,
            payload=ValueError("test error"),
        )
        await tap.on_frame(error)

        assert tap.active_traces == 0
        assert store.count() == 1

        crystal = list(store.iter_all())[0]
        assert crystal.action == Action.ERROR

    @pytest.mark.asyncio
    async def test_error_with_dict_payload(self, tap, store):
        """ERROR can have dict payload with error key."""
        start = make_frame(FrameType.INVOKE_START)
        await tap.on_frame(start)

        error = make_frame(
            FrameType.ERROR,
            payload={"error": "Something failed"},
        )
        await tap.on_frame(error)

        crystal = list(store.iter_all())[0]
        assert "Something failed" in str(crystal.outputs)

    @pytest.mark.asyncio
    async def test_multiple_concurrent_traces(self, tap, store):
        """Can handle multiple concurrent traces."""
        # Start two traces
        start1 = make_frame(FrameType.INVOKE_START, correlation_id="c1")
        start2 = make_frame(FrameType.INVOKE_START, correlation_id="c2")
        await tap.on_frame(start1)
        await tap.on_frame(start2)

        assert tap.active_traces == 2

        # End them in reverse order
        end2 = make_frame(FrameType.INVOKE_END, correlation_id="c2")
        end1 = make_frame(FrameType.INVOKE_END, correlation_id="c1")
        await tap.on_frame(end2)
        await tap.on_frame(end1)

        assert tap.active_traces == 0
        assert store.count() == 2

    @pytest.mark.asyncio
    async def test_orphan_end_ignored(self, tap, store):
        """INVOKE_END without matching START is ignored."""
        end = make_frame(
            FrameType.INVOKE_END,
            correlation_id="nonexistent",
        )
        await tap.on_frame(end)

        assert tap.active_traces == 0
        assert store.count() == 0

    @pytest.mark.asyncio
    async def test_action_from_metadata(self, tap, store):
        """Action is extracted from frame metadata."""
        start = make_frame(FrameType.INVOKE_START)
        await tap.on_frame(start)

        end = make_frame(
            FrameType.INVOKE_END,
            metadata={"action": "GENERATE"},
        )
        await tap.on_frame(end)

        crystal = list(store.iter_all())[0]
        assert crystal.action == "GENERATE"

    @pytest.mark.asyncio
    async def test_determinism_from_metadata(self, tap, store):
        """Determinism hint from frame metadata."""
        start = make_frame(FrameType.INVOKE_START)
        await tap.on_frame(start)

        end = make_frame(
            FrameType.INVOKE_END,
            metadata={"llm_call": True},
        )
        await tap.on_frame(end)

        crystal = list(store.iter_all())[0]
        assert crystal.determinism == Determinism.PROBABILISTIC

    def test_sync_version(self, tap, store):
        """Sync version works for non-async contexts."""
        start = make_frame(FrameType.INVOKE_START)
        tap.on_frame_sync(start)
        assert tap.active_traces == 1

        end = make_frame(FrameType.INVOKE_END)
        tap.on_frame_sync(end)
        assert tap.active_traces == 0
        assert store.count() == 1


class TestWireIntegration:
    """Tests for WireIntegration convenience methods."""

    @pytest.fixture
    def store(self) -> MemoryCrystalStore:
        return MemoryCrystalStore()

    @pytest.fixture
    def historian(self, store) -> Historian:
        h = Historian(store)
        h.reset_context()
        return h

    @pytest.fixture
    def wire(self, historian) -> WireIntegration:
        return WireIntegration(historian)

    def test_create_start_frame(self, wire):
        """Can create start frame."""
        frame = wire.create_start_frame(
            correlation_id="c1",
            agent_id="agent",
            agent_genus="B",
            payload={"test": True},
        )

        assert frame.frame_type == FrameType.INVOKE_START
        assert frame.correlation_id == "c1"
        assert frame.payload == {"test": True}

    def test_create_end_frame(self, wire):
        """Can create end frame."""
        frame = wire.create_end_frame(
            correlation_id="c1",
            agent_id="agent",
            agent_genus="B",
            payload={"result": 42},
            determinism=Determinism.DETERMINISTIC,
        )

        assert frame.frame_type == FrameType.INVOKE_END
        assert frame.payload == {"result": 42}
        assert frame.determinism_hint == Determinism.DETERMINISTIC

    def test_create_error_frame(self, wire):
        """Can create error frame."""
        error = ValueError("test")
        frame = wire.create_error_frame(
            correlation_id="c1",
            agent_id="agent",
            agent_genus="B",
            error=error,
        )

        assert frame.frame_type == FrameType.ERROR
        assert frame.payload is error

    @pytest.mark.asyncio
    async def test_trace_callable_success(self, wire, store):
        """Decorator traces successful calls."""

        @wire.trace_callable("my-agent", "B", "GENERATE")
        async def my_func(x):
            return {"result": x * 2}

        result = await my_func(21)
        assert result == {"result": 42}

        assert store.count() == 1
        crystal = list(store.iter_all())[0]
        assert crystal.agent_id == "my-agent"
        assert crystal.action == "GENERATE"

    @pytest.mark.asyncio
    async def test_trace_callable_error(self, wire, store):
        """Decorator traces failed calls."""

        @wire.trace_callable("my-agent", "B")
        async def failing_func():
            raise ValueError("oops")

        with pytest.raises(ValueError):
            await failing_func()

        assert store.count() == 1
        crystal = list(store.iter_all())[0]
        assert crystal.action == Action.ERROR
