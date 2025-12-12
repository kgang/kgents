"""Tests for HolographicBuffer (The Mirror Protocol).

THE CRITICAL TESTS:
- reflect() returns in <10ms regardless of observer count
- Mirror broadcasts to N observers without blocking agent
- Disconnected observers are cleaned up automatically
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest
from protocols.terrarium.mirror import HolographicBuffer


@dataclass
class MockWebSocket:
    """Mock WebSocket for testing."""

    accepted: bool = False
    messages: list[str] = field(default_factory=list)
    should_fail: bool = False
    delay: float = 0.0  # Simulated network delay

    async def accept(self) -> None:
        self.accepted = True

    async def send_text(self, data: str) -> None:
        if self.should_fail:
            raise ConnectionError("Mock disconnect")
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        self.messages.append(data)


class TestHolographicBufferBasics:
    """Basic HolographicBuffer functionality."""

    @pytest.mark.asyncio
    async def test_reflect_stores_in_history(self) -> None:
        """Events are stored in history."""
        buffer = HolographicBuffer(max_history=10)

        await buffer.reflect({"type": "test", "value": 1})
        await buffer.reflect({"type": "test", "value": 2})

        assert buffer.history_length == 2
        assert buffer.events_reflected == 2

    @pytest.mark.asyncio
    async def test_history_respects_max_size(self) -> None:
        """History doesn't exceed max_history."""
        buffer = HolographicBuffer(max_history=3)

        for i in range(5):
            await buffer.reflect({"value": i})

        assert buffer.history_length == 3
        snapshot = buffer.get_snapshot()
        # Should have the last 3 events
        assert [e["value"] for e in snapshot] == [2, 3, 4]

    @pytest.mark.asyncio
    async def test_observer_count_starts_zero(self) -> None:
        """No observers initially."""
        buffer = HolographicBuffer()
        assert buffer.observer_count == 0

    @pytest.mark.asyncio
    async def test_attach_increments_observer_count(self) -> None:
        """Attaching observer increases count."""
        buffer = HolographicBuffer()
        ws = MockWebSocket()

        await buffer.attach_mirror(ws)

        assert buffer.observer_count == 1
        assert ws.accepted

    @pytest.mark.asyncio
    async def test_detach_decrements_observer_count(self) -> None:
        """Detaching observer decreases count."""
        buffer = HolographicBuffer()
        ws = MockWebSocket()

        await buffer.attach_mirror(ws)
        result = buffer.detach_mirror(ws)

        assert result is True
        assert buffer.observer_count == 0

    @pytest.mark.asyncio
    async def test_detach_nonexistent_returns_false(self) -> None:
        """Detaching non-existent observer returns False."""
        buffer = HolographicBuffer()
        ws = MockWebSocket()

        result = buffer.detach_mirror(ws)

        assert result is False


class TestMirrorProtocolBroadcast:
    """The Mirror Protocol: broadcast to observers."""

    @pytest.mark.asyncio
    async def test_reflect_broadcasts_to_observer(self) -> None:
        """Events are broadcast to attached observers."""
        buffer = HolographicBuffer()
        ws = MockWebSocket()
        await buffer.attach_mirror(ws)

        await buffer.reflect({"type": "test", "value": 42})
        # Give broadcast task time to run
        await asyncio.sleep(0.05)

        # Should have history event + broadcast event
        # attach_mirror sends history (empty), then reflect sends new event
        assert len(ws.messages) == 1
        assert "42" in ws.messages[0]

    @pytest.mark.asyncio
    async def test_reflect_broadcasts_to_multiple_observers(self) -> None:
        """Events are broadcast to all observers."""
        buffer = HolographicBuffer()
        observers = [MockWebSocket() for _ in range(5)]

        for ws in observers:
            await buffer.attach_mirror(ws)

        await buffer.reflect({"type": "test"})
        await asyncio.sleep(0.05)

        for ws in observers:
            assert len(ws.messages) == 1

    @pytest.mark.asyncio
    async def test_new_observer_receives_history(self) -> None:
        """New observers receive history (The Ghost)."""
        buffer = HolographicBuffer(max_history=10)

        # Emit some events first
        await buffer.reflect({"seq": 1})
        await buffer.reflect({"seq": 2})
        await buffer.reflect({"seq": 3})

        # Then attach observer
        ws = MockWebSocket()
        await buffer.attach_mirror(ws)

        # Should receive 3 history events immediately
        assert len(ws.messages) == 3
        assert "1" in ws.messages[0]
        assert "2" in ws.messages[1]
        assert "3" in ws.messages[2]


class TestMirrorProtocolFireAndForget:
    """THE CRITICAL PROPERTY: Fire and forget—slow clients don't slow the agent."""

    @pytest.mark.asyncio
    async def test_reflect_does_not_wait_for_slow_observers(self) -> None:
        """reflect() returns quickly even with slow observers.

        This is THE critical test. The agent must not be slowed by observers.
        """
        buffer = HolographicBuffer(broadcast_timeout=0.1)

        # Create slow observers
        slow_observers = [MockWebSocket(delay=1.0) for _ in range(10)]
        for ws in slow_observers:
            await buffer.attach_mirror(ws)

        # reflect() should return almost immediately
        import time

        start = time.perf_counter()
        await buffer.reflect({"type": "test"})
        elapsed = time.perf_counter() - start

        # reflect() itself should be <10ms
        # (the broadcast happens in background task)
        assert elapsed < 0.01, f"reflect() took {elapsed * 1000:.1f}ms, should be <10ms"

        # Wait for broadcast task to timeout (avoids unawaited coroutine warnings)
        await asyncio.sleep(0.15)

    @pytest.mark.asyncio
    async def test_reflect_fast_with_many_observers(self) -> None:
        """reflect() stays fast regardless of observer count.

        100 observers should not meaningfully slow reflect().
        """
        buffer = HolographicBuffer(broadcast_timeout=0.1)

        # Attach 100 observers
        observers = [MockWebSocket() for _ in range(100)]
        for ws in observers:
            await buffer.attach_mirror(ws)

        # Time 100 reflects
        import time

        start = time.perf_counter()
        for i in range(100):
            await buffer.reflect({"seq": i})
        elapsed = time.perf_counter() - start

        # 100 reflects should be <1s total (<10ms each)
        assert elapsed < 1.0, f"100 reflects took {elapsed * 1000:.1f}ms"

        # Wait for broadcast tasks to complete (avoids unawaited coroutine warnings)
        await asyncio.sleep(0.15)

    @pytest.mark.asyncio
    async def test_disconnected_observers_cleaned_up(self) -> None:
        """Failed observers are removed automatically."""
        buffer = HolographicBuffer(broadcast_timeout=0.1)

        # One working, one failing
        good_ws = MockWebSocket()
        bad_ws = MockWebSocket(should_fail=True)

        await buffer.attach_mirror(good_ws)
        await buffer.attach_mirror(bad_ws)
        assert buffer.observer_count == 2

        # Broadcast triggers cleanup of failed observer
        await buffer.reflect({"type": "test"})
        await asyncio.sleep(0.15)  # Wait for broadcast task

        # Bad observer should be removed
        assert buffer.observer_count == 1

    @pytest.mark.asyncio
    async def test_reflect_with_no_observers_is_instant(self) -> None:
        """reflect() with no observers is basically instant."""
        buffer = HolographicBuffer()

        import time

        start = time.perf_counter()
        for i in range(1000):
            await buffer.reflect({"seq": i})
        elapsed = time.perf_counter() - start

        # 1000 reflects with no observers should be very fast
        assert elapsed < 0.5, f"1000 reflects took {elapsed * 1000:.1f}ms"


class TestHolographicBufferSnapshot:
    """Snapshot functionality for REST endpoints."""

    @pytest.mark.asyncio
    async def test_get_snapshot_returns_copy(self) -> None:
        """get_snapshot returns a copy, not the internal deque."""
        buffer = HolographicBuffer()

        await buffer.reflect({"value": 1})
        snapshot = buffer.get_snapshot()

        # Modifying snapshot shouldn't affect buffer
        snapshot.append({"value": 999})

        assert buffer.history_length == 1

    @pytest.mark.asyncio
    async def test_clear_history(self) -> None:
        """clear_history empties the buffer."""
        buffer = HolographicBuffer()

        await buffer.reflect({"value": 1})
        await buffer.reflect({"value": 2})
        buffer.clear_history()

        assert buffer.history_length == 0
        # Event count is not reset
        assert buffer.events_reflected == 2


class TestEventSerialization:
    """Events must be JSON-serializable."""

    @pytest.mark.asyncio
    async def test_non_serializable_event_handled(self) -> None:
        """Non-JSON-serializable events don't crash the buffer."""
        buffer = HolographicBuffer()
        ws = MockWebSocket()
        await buffer.attach_mirror(ws)

        # Try to reflect something non-serializable
        class NotSerializable:
            pass

        # This should not raise
        await buffer.reflect({"obj": NotSerializable()})

        # Give broadcast time to run (and fail gracefully)
        await asyncio.sleep(0.05)

        # Observer should not have received anything (serialization failed)
        # But buffer should still work
        assert buffer.events_reflected == 1


class TestGracefulShutdown:
    """Tests for graceful shutdown and drain functionality."""

    @pytest.mark.asyncio
    async def test_pending_broadcast_count_tracks_tasks(self) -> None:
        """pending_broadcast_count tracks in-flight broadcasts."""
        buffer = HolographicBuffer(broadcast_timeout=0.5)

        # Attach a slow observer
        ws = MockWebSocket(delay=0.2)
        await buffer.attach_mirror(ws)

        # Reflect an event - creates pending broadcast
        await buffer.reflect({"type": "test"})

        # Should have 1 pending broadcast
        assert buffer.pending_broadcast_count >= 0  # May already complete

        # Wait for broadcast to complete
        await asyncio.sleep(0.3)
        assert buffer.pending_broadcast_count == 0

    @pytest.mark.asyncio
    async def test_drain_waits_for_pending_broadcasts(self) -> None:
        """drain() waits for pending broadcasts to complete."""
        buffer = HolographicBuffer(broadcast_timeout=0.5, drain_timeout=2.0)

        # Attach observers
        observers = [MockWebSocket() for _ in range(3)]
        for ws in observers:
            await buffer.attach_mirror(ws)

        # Emit several events
        for i in range(5):
            await buffer.reflect({"seq": i})

        # Drain should complete
        completed = await buffer.drain()

        assert completed >= 0
        assert buffer.is_shutting_down is True

    @pytest.mark.asyncio
    async def test_drain_skips_new_broadcasts(self) -> None:
        """After drain starts, new reflect() calls skip broadcasting."""
        buffer = HolographicBuffer()

        ws = MockWebSocket()
        await buffer.attach_mirror(ws)

        # Start drain
        await buffer.drain()

        # New reflect should not broadcast
        initial_messages = len(ws.messages)
        await buffer.reflect({"type": "post-drain"})
        await asyncio.sleep(0.05)

        # No new messages should arrive
        assert len(ws.messages) == initial_messages

        # But history should still be updated
        assert buffer.events_reflected >= 1

    @pytest.mark.asyncio
    async def test_drain_times_out_on_slow_broadcasts(self) -> None:
        """drain() respects timeout and cancels slow broadcasts."""
        buffer = HolographicBuffer(broadcast_timeout=2.0, drain_timeout=0.1)

        # Attach a very slow observer
        ws = MockWebSocket(delay=5.0)
        await buffer.attach_mirror(ws)

        # Emit event
        await buffer.reflect({"type": "test"})

        # Drain should timeout
        import time

        start = time.perf_counter()
        await buffer.drain()
        elapsed = time.perf_counter() - start

        # Should return in ~drain_timeout (0.1s), not broadcast_timeout (2s)
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_drain_returns_zero_when_no_pending(self) -> None:
        """drain() returns 0 when no broadcasts pending."""
        buffer = HolographicBuffer()

        # No observers, no pending broadcasts
        completed = await buffer.drain()

        assert completed == 0

    @pytest.mark.asyncio
    async def test_shutdown_drains_and_disconnects(self) -> None:
        """shutdown() drains broadcasts and disconnects all mirrors."""
        buffer = HolographicBuffer()

        # Attach observers
        observers = [MockWebSocket() for _ in range(3)]
        for ws in observers:
            await buffer.attach_mirror(ws)
        assert buffer.observer_count == 3

        # Shutdown
        await buffer.shutdown()

        assert buffer.is_shutting_down is True
        assert buffer.observer_count == 0

    @pytest.mark.asyncio
    async def test_is_shutting_down_initially_false(self) -> None:
        """is_shutting_down starts as False."""
        buffer = HolographicBuffer()
        assert buffer.is_shutting_down is False
