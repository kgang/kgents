"""Tests for Perturbation handling."""

import asyncio
import time

import pytest
from agents.flux.perturbation import (
    Perturbation,
    await_perturbation,
    create_perturbation,
    is_perturbation,
    unwrap_perturbation,
)


class TestPerturbationCreation:
    """Test Perturbation dataclass creation."""

    @pytest.mark.asyncio
    async def test_create_perturbation_basic(self):
        future = asyncio.get_event_loop().create_future()
        p = Perturbation(data="test", result_future=future)

        assert p.data == "test"
        assert p.result_future is future
        assert p.priority == 0  # Default

    @pytest.mark.asyncio
    async def test_create_perturbation_with_priority(self):
        future = asyncio.get_event_loop().create_future()
        p = Perturbation(data="test", result_future=future, priority=100)

        assert p.priority == 100

    @pytest.mark.asyncio
    async def test_perturbation_timestamp(self):
        before = time.time()
        future = asyncio.get_event_loop().create_future()
        p = Perturbation(data="test", result_future=future)
        after = time.time()

        assert before <= p.timestamp <= after


class TestPerturbationOrdering:
    """Test Perturbation priority ordering."""

    @pytest.mark.asyncio
    async def test_higher_priority_comes_first(self):
        loop = asyncio.get_event_loop()
        p1 = Perturbation(data="low", result_future=loop.create_future(), priority=10)
        p2 = Perturbation(data="high", result_future=loop.create_future(), priority=100)

        # Higher priority should be "less than" for min-heap
        assert p2 < p1

    @pytest.mark.asyncio
    async def test_same_priority_ordered_by_timestamp(self):
        loop = asyncio.get_event_loop()
        p1 = Perturbation(data="first", result_future=loop.create_future(), priority=10)
        await asyncio.sleep(0.01)  # Ensure different timestamps
        p2 = Perturbation(
            data="second", result_future=loop.create_future(), priority=10
        )

        # Earlier timestamp should be "less than"
        assert p1 < p2

    @pytest.mark.asyncio
    async def test_priority_queue_ordering(self):
        queue: asyncio.PriorityQueue[Perturbation] = asyncio.PriorityQueue()
        loop = asyncio.get_event_loop()

        # Add in random order
        p_low = Perturbation(
            data="low", result_future=loop.create_future(), priority=10
        )
        p_high = Perturbation(
            data="high", result_future=loop.create_future(), priority=100
        )
        p_med = Perturbation(
            data="med", result_future=loop.create_future(), priority=50
        )

        await queue.put(p_low)
        await queue.put(p_high)
        await queue.put(p_med)

        # Should come out in priority order (high, med, low)
        assert (await queue.get()).data == "high"
        assert (await queue.get()).data == "med"
        assert (await queue.get()).data == "low"


class TestPerturbationResult:
    """Test Perturbation result handling."""

    @pytest.mark.asyncio
    async def test_set_result(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        p.set_result("done")

        assert p.is_done
        assert p.result_future.result() == "done"

    @pytest.mark.asyncio
    async def test_set_result_idempotent(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        p.set_result("first")
        p.set_result("second")  # Should not raise

        assert p.result_future.result() == "first"

    @pytest.mark.asyncio
    async def test_set_exception(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        error = ValueError("test error")
        p.set_exception(error)

        assert p.is_done
        with pytest.raises(ValueError, match="test error"):
            p.result_future.result()

    @pytest.mark.asyncio
    async def test_cancel(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        p.cancel("Cancelled")

        assert p.is_done
        assert p.result_future.cancelled()

    @pytest.mark.asyncio
    async def test_is_done_false(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        assert p.is_done is False


class TestIsPerturbation:
    """Test is_perturbation() function."""

    @pytest.mark.asyncio
    async def test_perturbation_returns_true(self):
        loop = asyncio.get_event_loop()
        p = Perturbation(data="test", result_future=loop.create_future())

        assert is_perturbation(p) is True

    def test_regular_data_returns_false(self):
        assert is_perturbation("string") is False
        assert is_perturbation(123) is False
        assert is_perturbation({"key": "value"}) is False
        assert is_perturbation(None) is False


class TestUnwrapPerturbation:
    """Test unwrap_perturbation() function."""

    @pytest.mark.asyncio
    async def test_unwrap_perturbation(self):
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        p = Perturbation(data="test", result_future=future)

        data, result_future = unwrap_perturbation(p)

        assert data == "test"
        assert result_future is future

    def test_unwrap_regular_data(self):
        data, result_future = unwrap_perturbation("test")

        assert data == "test"
        assert result_future is None

    def test_unwrap_dict(self):
        data, result_future = unwrap_perturbation({"key": "value"})

        assert data == {"key": "value"}
        assert result_future is None


class TestCreatePerturbation:
    """Test create_perturbation() helper function."""

    @pytest.mark.asyncio
    async def test_create_with_data(self):
        p = create_perturbation(data="test")

        assert p.data == "test"
        assert p.result_future is not None
        assert p.priority == 100  # Default priority

    @pytest.mark.asyncio
    async def test_create_with_priority(self):
        p = create_perturbation(data="test", priority=50)

        assert p.priority == 50

    @pytest.mark.asyncio
    async def test_created_future_is_usable(self):
        p = create_perturbation(data="test")

        p.set_result("done")

        assert await p.result_future == "done"


class TestAwaitPerturbation:
    """Test await_perturbation() helper function."""

    @pytest.mark.asyncio
    async def test_await_result(self):
        p = create_perturbation(data="test")

        # Set result in background
        async def set_later():
            await asyncio.sleep(0.01)
            p.set_result("done")

        asyncio.create_task(set_later())

        result = await await_perturbation(p)
        assert result == "done"

    @pytest.mark.asyncio
    async def test_await_with_timeout_success(self):
        p = create_perturbation(data="test")

        async def set_later():
            await asyncio.sleep(0.01)
            p.set_result("done")

        asyncio.create_task(set_later())

        result = await await_perturbation(p, timeout=1.0)
        assert result == "done"

    @pytest.mark.asyncio
    async def test_await_timeout_exceeded(self):
        p = create_perturbation(data="test")

        # Don't set result

        with pytest.raises(asyncio.TimeoutError):
            await await_perturbation(p, timeout=0.01)

    @pytest.mark.asyncio
    async def test_await_exception(self):
        p = create_perturbation(data="test")
        p.set_exception(ValueError("error"))

        with pytest.raises(ValueError, match="error"):
            await await_perturbation(p)
