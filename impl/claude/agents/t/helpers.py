"""
Test Helpers: Convenience functions for testing agents.

Quick utilities for common testing patterns:
- assert_agent_output: Verify agent produces expected output
- assert_functor_laws: Verify functor satisfies identity/composition
- mock_agent: Create a mock that returns a fixed value
- spy_pipeline: Wrap a pipeline with observation

These complement the Type I-V T-gents with simpler, pytest-style helpers.
"""

from __future__ import annotations

from typing import Any, TypeVar

from agents.poly.types import Agent

A = TypeVar("A")
B = TypeVar("B")


async def assert_agent_output(
    agent: Agent[A, B],
    input: A,
    expected: B,
    msg: str | None = None,
) -> None:
    """
    Assert an agent produces expected output.

    Simple assertion helper for agent testing.

    Args:
        agent: The agent to test
        input: Input to invoke with
        expected: Expected output
        msg: Optional message on failure

    Raises:
        AssertionError: If output doesn't match expected

    Example:
        await assert_agent_output(double, 5, 10)
        await assert_agent_output(greet, "World", "Hello, World!")
    """
    result = await agent.invoke(input)
    if result != expected:
        default_msg = (
            f"Agent {agent.name}.invoke({input!r}) = {result!r}, expected {expected!r}"
        )
        raise AssertionError(msg or default_msg)


async def assert_agent_raises(
    agent: Agent[A, B],
    input: A,
    exception_type: type[Exception],
    msg: str | None = None,
) -> Exception:
    """
    Assert an agent raises a specific exception.

    Args:
        agent: The agent to test
        input: Input to invoke with
        exception_type: Expected exception type
        msg: Optional message on failure

    Returns:
        The caught exception (for further inspection)

    Raises:
        AssertionError: If agent doesn't raise or raises wrong type

    Example:
        exc = await assert_agent_raises(parser, "invalid", ValueError)
        assert "parse" in str(exc)
    """
    try:
        result = await agent.invoke(input)
        default_msg = (
            f"Agent {agent.name}.invoke({input!r}) should have raised "
            f"{exception_type.__name__}, got {result!r}"
        )
        raise AssertionError(msg or default_msg)
    except exception_type as e:
        return e
    except Exception as e:
        default_msg = (
            f"Agent {agent.name}.invoke({input!r}) raised {type(e).__name__}, "
            f"expected {exception_type.__name__}"
        )
        raise AssertionError(msg or default_msg) from e


async def assert_composition_associative(
    f: Agent[A, B],
    g: Agent[B, Any],
    h: Agent[Any, Any],
    test_input: A,
) -> None:
    """
    Assert that agent composition is associative.

    Verifies: (f >> g) >> h = f >> (g >> h)

    Args:
        f, g, h: Agents to compose
        test_input: Input to test with

    Raises:
        AssertionError: If associativity is violated
    """
    left = (f >> g) >> h
    right = f >> (g >> h)

    left_result = await left.invoke(test_input)
    right_result = await right.invoke(test_input)

    if left_result != right_result:
        raise AssertionError(
            f"Associativity violated:\n"
            f"  (f >> g) >> h = {left_result!r}\n"
            f"  f >> (g >> h) = {right_result!r}"
        )


async def assert_functor_identity(
    functor: Any,
    test_value: Any,
) -> None:
    """
    Assert a functor satisfies the identity law.

    Identity law: F(id) = id
    Lifting the identity function should produce identity behavior.

    Args:
        functor: The functor class (must have .lift() and .pure())
        test_value: Value to test with

    Raises:
        AssertionError: If identity law is violated
    """
    from agents.a.quick import agent

    @agent
    async def identity(x: Any) -> Any:
        return x

    # Lift identity
    lifted = functor.lift(identity)

    # Apply to a pure value
    wrapped = functor.pure(test_value)
    result = await lifted.invoke(wrapped)

    # Extract if possible, otherwise compare directly
    if hasattr(result, "value"):
        actual = result.value
    else:
        actual = result

    if actual != test_value:
        raise AssertionError(
            f"Functor identity law violated:\n"
            f"  F(id)({test_value!r}) = {actual!r}\n"
            f"  Expected: {test_value!r}"
        )


async def assert_functor_composition(
    functor: Any,
    f: Agent[A, B],
    g: Agent[B, Any],
    test_value: A,
) -> None:
    """
    Assert a functor satisfies the composition law.

    Composition law: F(g >> f) = F(g) >> F(f)
    Lifting a composition equals composing lifted functions.

    Args:
        functor: The functor class
        f: First agent (inner)
        g: Second agent (outer)
        test_value: Value to test with

    Raises:
        AssertionError: If composition law is violated
    """
    # Lift the composition
    composed = f >> g
    lifted_composed = functor.lift(composed)

    # Compose the lifted functions
    lifted_f = functor.lift(f)
    lifted_g = functor.lift(g)
    composed_lifted = lifted_f >> lifted_g

    # Apply to wrapped value
    wrapped = functor.pure(test_value)

    result1 = await lifted_composed.invoke(wrapped)
    result2 = await composed_lifted.invoke(wrapped)

    # Extract values for comparison
    v1 = result1.value if hasattr(result1, "value") else result1
    v2 = result2.value if hasattr(result2, "value") else result2

    if v1 != v2:
        raise AssertionError(
            f"Functor composition law violated:\n"
            f"  F(g >> f)({test_value!r}) = {v1!r}\n"
            f"  (F(g) >> F(f))({test_value!r}) = {v2!r}"
        )


def quick_mock(return_value: B) -> Agent[Any, B]:
    """
    Create a mock agent that always returns the given value.

    For more sophisticated mocking, use MockAgent from agents.t.

    Args:
        return_value: Value to return on every invoke

    Returns:
        An agent that returns the value

    Example:
        mock = quick_mock(42)
        assert await mock.invoke("anything") == 42
    """
    from agents.a.quick import FunctionAgent

    async def _mock(_: Any) -> B:
        return return_value

    return FunctionAgent(_mock, agent_name="mock")


def counting_agent(
    inner: Agent[A, B],
) -> tuple[Agent[A, B], list[A]]:
    """
    Wrap an agent to record all inputs.

    For more sophisticated observation, use SpyAgent from agents.t.

    Args:
        inner: Agent to wrap

    Returns:
        Tuple of (wrapped agent, list that will contain all inputs)

    Example:
        wrapped, calls = counting_agent(my_agent)
        await wrapped.invoke("hello")
        await wrapped.invoke("world")
        assert calls == ["hello", "world"]
    """
    calls: list[A] = []

    class CountingWrapper(Agent[A, B]):
        @property
        def name(self) -> str:
            return f"counting({inner.name})"

        async def invoke(self, input: A) -> B:
            calls.append(input)
            return await inner.invoke(input)

    return CountingWrapper(), calls


__all__ = [
    "assert_agent_output",
    "assert_agent_raises",
    "assert_composition_associative",
    "assert_functor_identity",
    "assert_functor_composition",
    "quick_mock",
    "counting_agent",
]
