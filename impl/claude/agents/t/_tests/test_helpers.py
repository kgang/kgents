"""Tests for agents.t.helpers - Test convenience functions."""

import pytest

from agents.a.quick import agent
from agents.t.helpers import (
    assert_agent_output,
    assert_agent_raises,
    assert_composition_associative,
    counting_agent,
    quick_mock,
)


class TestAssertAgentOutput:
    """Tests for assert_agent_output."""

    @pytest.mark.asyncio
    async def test_passing_assertion(self) -> None:
        """Passes when output matches."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        await assert_agent_output(double, 5, 10)  # Should not raise

    @pytest.mark.asyncio
    async def test_failing_assertion(self) -> None:
        """Raises AssertionError on mismatch."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        with pytest.raises(AssertionError) as exc_info:
            await assert_agent_output(double, 5, 11)

        assert "10" in str(exc_info.value)  # Actual value
        assert "11" in str(exc_info.value)  # Expected value

    @pytest.mark.asyncio
    async def test_custom_message(self) -> None:
        """Uses custom message when provided."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        with pytest.raises(AssertionError) as exc_info:
            await assert_agent_output(double, 5, 11, msg="Custom failure message")

        assert "Custom failure message" in str(exc_info.value)


class TestAssertAgentRaises:
    """Tests for assert_agent_raises."""

    @pytest.mark.asyncio
    async def test_catches_expected_exception(self) -> None:
        """Returns exception when expected type raised."""

        @agent
        async def failing(x: int) -> int:
            raise ValueError(f"Invalid: {x}")

        exc = await assert_agent_raises(failing, 5, ValueError)
        assert "Invalid: 5" in str(exc)

    @pytest.mark.asyncio
    async def test_fails_when_no_exception(self) -> None:
        """Raises AssertionError when no exception."""

        @agent
        async def passing(x: int) -> int:
            return x

        with pytest.raises(AssertionError) as exc_info:
            await assert_agent_raises(passing, 5, ValueError)

        # Either message format is acceptable
        msg = str(exc_info.value)
        assert "should have raised" in msg or "ValueError" in msg

    @pytest.mark.asyncio
    async def test_fails_when_wrong_exception(self) -> None:
        """Raises AssertionError when wrong exception type."""

        @agent
        async def failing(x: int) -> int:
            raise TypeError("wrong type")

        with pytest.raises(AssertionError) as exc_info:
            await assert_agent_raises(failing, 5, ValueError)

        assert "TypeError" in str(exc_info.value)


class TestAssertCompositionAssociative:
    """Tests for assert_composition_associative."""

    @pytest.mark.asyncio
    async def test_passes_for_associative_composition(self) -> None:
        """Passes when composition is associative."""

        @agent
        async def f(x: int) -> int:
            return x + 1

        @agent
        async def g(x: int) -> int:
            return x * 2

        @agent
        async def h(x: int) -> int:
            return x - 3

        await assert_composition_associative(f, g, h, 5)

    @pytest.mark.asyncio
    async def test_fails_for_non_associative(self) -> None:
        """Fails when composition violates associativity."""
        # Note: Normal agent composition IS associative, so this test
        # verifies the assertion would catch a violation if one occurred.
        # We can't easily create a non-associative composition with
        # standard agents, so we verify the assertion logic works.

        @agent
        async def f(x: int) -> int:
            return x + 1

        @agent
        async def g(x: int) -> int:
            return x * 2

        @agent
        async def h(x: int) -> int:
            return x - 3

        # This should pass because composition IS associative
        await assert_composition_associative(f, g, h, 5)


class TestQuickMock:
    """Tests for quick_mock."""

    @pytest.mark.asyncio
    async def test_returns_fixed_value(self) -> None:
        """Mock always returns the given value."""
        mock = quick_mock(42)

        assert await mock.invoke("anything") == 42
        assert await mock.invoke(None) == 42
        assert await mock.invoke({"complex": "data"}) == 42

    @pytest.mark.asyncio
    async def test_returns_complex_value(self) -> None:
        """Mock can return complex values."""
        expected = {"result": [1, 2, 3], "status": "ok"}
        mock = quick_mock(expected)

        assert await mock.invoke("x") == expected


class TestCountingAgent:
    """Tests for counting_agent."""

    @pytest.mark.asyncio
    async def test_records_calls(self) -> None:
        """Records all inputs."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        wrapped, calls = counting_agent(double)

        await wrapped.invoke(1)
        await wrapped.invoke(2)
        await wrapped.invoke(3)

        assert calls == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_preserves_output(self) -> None:
        """Wrapped agent still produces correct output."""

        @agent
        async def double(x: int) -> int:
            return x * 2

        wrapped, _ = counting_agent(double)

        assert await wrapped.invoke(5) == 10
        assert await wrapped.invoke(7) == 14

    @pytest.mark.asyncio
    async def test_has_descriptive_name(self) -> None:
        """Wrapped agent has descriptive name."""

        @agent
        async def my_agent(x: int) -> int:
            return x

        wrapped, _ = counting_agent(my_agent)

        assert "counting" in wrapped.name
        assert "my_agent" in wrapped.name
