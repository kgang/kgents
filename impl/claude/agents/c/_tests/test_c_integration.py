"""
C-gent Integration Tests: Category Theory Laws

Tests C-gent (Category Theory Agents) composition and laws:
- Functor Laws: Identity, Composition
- Monad Laws: Left Identity, Right Identity, Associativity
- Category Laws: Associativity, Identity composition
- Composition patterns: Parallel, Conditional, Sequential

Philosophy: Agents are morphisms. Composition is primary.
"""

import asyncio
from typing import Any

import pytest

from agents.c import (
    Either,
    Just,
    Left,
    # Functor types
    Maybe,
    MaybeEither,
    Nothing,
    Right,
    # Async functor
    async_agent,
    # Conditional composition
    branch,
    check_composition_law,
    # Law validation
    check_identity_law,
    either,
    fan_out,
    # Fix (retry)
    fix,
    guarded,
    # List functor
    list_agent,
    # Logged functor
    logged,
    maybe,
    # Parallel composition
    parallel,
    pure_either,
    # Monad
    pure_maybe,
    race,
    switch,
)
from agents.poly.types import Agent

# --- Helper Agents for Testing ---


class IdentityAgent(Agent[Any, Any]):
    """Identity agent: id(x) = x"""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input: Any) -> Any:
        return input


class DoubleAgent(Agent[int, int]):
    """Doubles an integer."""

    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class AddTenAgent(Agent[int, int]):
    """Adds ten to an integer."""

    @property
    def name(self) -> str:
        return "AddTen"

    async def invoke(self, input: int) -> int:
        return input + 10


class StrToIntAgent(Agent[str, int]):
    """Converts string to int."""

    @property
    def name(self) -> str:
        return "StrToInt"

    async def invoke(self, input: str) -> int:
        return len(input)


class IntToStrAgent(Agent[int, str]):
    """Converts int to string."""

    @property
    def name(self) -> str:
        return "IntToStr"

    async def invoke(self, input: int) -> str:
        return str(input)


class FlakeyAgent(Agent[int, int]):
    """Agent that fails sometimes for testing retry."""

    def __init__(self) -> None:
        self.attempts: int = 0
        self.fail_until: int = 2  # Fail first 2 attempts

    @property
    def name(self) -> str:
        return "Flakey"

    async def invoke(self, input: int) -> int:
        self.attempts += 1
        if self.attempts < self.fail_until:
            raise ValueError(f"Transient failure {self.attempts}")
        return input * 2


class AlwaysFailsAgent(Agent[int, int]):
    """Agent that always fails."""

    @property
    def name(self) -> str:
        return "AlwaysFails"

    async def invoke(self, input: int) -> int:
        raise ValueError("Permanent failure")


class TestFunctorIdentityLaw:
    """Test Functor Identity Law: F(id_A) = id_F(A)"""

    @pytest.mark.asyncio
    async def test_maybe_identity_law_just(self) -> None:
        """Maybe functor preserves identity on Just."""
        identity = IdentityAgent()
        lifted = maybe(identity)

        input_val = Just(42)
        result = await lifted.invoke(input_val)

        assert isinstance(result, Just)
        assert result.value == 42

    @pytest.mark.asyncio
    async def test_maybe_identity_law_nothing(self) -> None:
        """Maybe functor preserves identity on Nothing."""
        identity = IdentityAgent()
        lifted = maybe(identity)

        result = await lifted.invoke(Nothing)

        assert result.is_nothing()

    @pytest.mark.asyncio
    async def test_either_identity_law_right(self) -> None:
        """Either functor preserves identity on Right."""
        identity = IdentityAgent()
        lifted = either(identity)

        input_val = Right(42)
        result = await lifted.invoke(input_val)

        assert isinstance(result, Right)
        assert result.value == 42

    @pytest.mark.asyncio
    async def test_either_identity_law_left(self) -> None:
        """Either functor preserves identity on Left."""
        identity = IdentityAgent()
        lifted = either(identity)

        input_val = Left("error")
        result = await lifted.invoke(input_val)

        assert isinstance(result, Left)
        assert result.error == "error"

    @pytest.mark.asyncio
    async def test_list_identity_law(self) -> None:
        """List functor preserves identity."""
        identity = IdentityAgent()
        lifted = list_agent(identity)

        input_val = [1, 2, 3]
        result = await lifted.invoke(input_val)

        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_identity_law_via_helper(self) -> None:
        """Test identity law using check_identity_law helper."""
        identity = IdentityAgent()
        result = await check_identity_law(maybe, identity, Just(42))
        assert result is True


class TestFunctorCompositionLaw:
    """Test Functor Composition Law: F(g . f) = F(g) . F(f)"""

    @pytest.mark.asyncio
    async def test_maybe_composition_law(self) -> None:
        """Maybe functor preserves composition."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        # Left side: F(g . f)
        composed = double >> add_ten
        lifted_composed = maybe(composed)
        result_left = await lifted_composed.invoke(Just(5))

        # Right side: F(g) . F(f)
        lifted_double = maybe(double)
        lifted_add_ten = maybe(add_ten)
        lifted_composition = lifted_double >> lifted_add_ten
        result_right = await lifted_composition.invoke(Just(5))

        # Both should equal Just(20) = (5 * 2) + 10
        assert isinstance(result_left, Just)
        assert isinstance(result_right, Just)
        assert result_left.value == result_right.value == 20

    @pytest.mark.asyncio
    async def test_either_composition_law(self) -> None:
        """Either functor preserves composition."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        # Left side
        composed = double >> add_ten
        lifted_composed = either(composed)
        result_left = await lifted_composed.invoke(Right(5))

        # Right side
        lifted_composition = either(double) >> either(add_ten)
        result_right = await lifted_composition.invoke(Right(5))

        assert isinstance(result_left, Right)
        assert isinstance(result_right, Right)
        assert result_left.value == result_right.value == 20

    @pytest.mark.asyncio
    async def test_list_composition_law(self) -> None:
        """List functor preserves composition."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        # Left side
        composed = double >> add_ten
        lifted_composed = list_agent(composed)
        result_left = await lifted_composed.invoke([1, 2, 3])

        # Right side
        lifted_composition = list_agent(double) >> list_agent(add_ten)
        result_right = await lifted_composition.invoke([1, 2, 3])

        # [1, 2, 3] -> [2, 4, 6] -> [12, 14, 16]
        assert result_left == result_right == [12, 14, 16]

    @pytest.mark.asyncio
    async def test_composition_law_via_helper(self) -> None:
        """Test composition law using check_composition_law helper."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        result = await check_composition_law(maybe, double, add_ten, Just(5))
        assert result is True


class TestMonadLaws:
    """Test Monad Laws."""

    def test_left_identity_maybe(self) -> None:
        """Left identity: unit(a).bind(f) = f(a)"""

        # f: int -> Maybe[int]
        def f(x: int) -> Maybe[int]:
            return Just(x * 2)

        a = 21

        # Left side: unit(a).bind(f)
        left = pure_maybe(a).flat_map(f)

        # Right side: f(a)
        right = f(a)

        assert isinstance(left, Just)
        assert isinstance(right, Just)
        assert left.value == right.value == 42

    def test_right_identity_maybe(self) -> None:
        """Right identity: m.bind(unit) = m"""
        m = Just(42)

        # m.bind(unit)
        result = m.flat_map(pure_maybe)

        assert isinstance(result, Just)
        assert result.value == 42

    def test_associativity_maybe(self) -> None:
        """Associativity: m.bind(f).bind(g) = m.bind(λa. f(a).bind(g))"""

        def f(x: int) -> Maybe[int]:
            return Just(x * 2)

        def g(x: int) -> Maybe[int]:
            return Just(x + 10)

        m = Just(5)

        # Left side: m.bind(f).bind(g)
        left = m.flat_map(f).flat_map(g)

        # Right side: m.bind(λa. f(a).bind(g))
        right = m.flat_map(lambda a: f(a).flat_map(g))

        # 5 -> 10 -> 20
        assert isinstance(left, Just)
        assert isinstance(right, Just)
        assert left.value == right.value == 20

    def test_left_identity_either(self) -> None:
        """Left identity for Either monad."""

        def f(x: int) -> Either[None, int]:
            return Right(x * 2)

        a = 21

        left = pure_either(a).flat_map(f)
        right = f(a)

        assert isinstance(left, Right)
        assert isinstance(right, Right)
        assert left.value == right.value == 42

    def test_maybe_either_monad_transformer(self) -> None:
        """Test MaybeEither monad transformer."""

        def double(x: int) -> MaybeEither[int]:
            return MaybeEither.pure(x * 2)

        m = MaybeEither.pure(21)
        result = m.bind(double)

        inner = result.run()
        assert isinstance(inner, Just)
        assert isinstance(inner.value, Right)
        assert inner.value.value == 42

    def test_maybe_either_short_circuit_nothing(self) -> None:
        """MaybeEither short-circuits on Nothing."""
        m = MaybeEither.fail_nothing()

        def f(x: int) -> MaybeEither[int]:
            return MaybeEither.pure(x * 2)

        result = m.bind(f)
        assert result.run().is_nothing()

    def test_maybe_either_short_circuit_left(self) -> None:
        """MaybeEither short-circuits on Left."""
        m = MaybeEither.fail_left("error")

        def f(x: int) -> MaybeEither[int]:
            return MaybeEither.pure(x * 2)

        result = m.bind(f)
        inner = result.run()
        assert isinstance(inner, Just)
        assert isinstance(inner.value, Left)


class TestCategoryLaws:
    """Test Category Laws for Agent composition."""

    @pytest.mark.asyncio
    async def test_associativity(self) -> None:
        """Test (f >> g) >> h = f >> (g >> h)"""
        f = StrToIntAgent()
        g = DoubleAgent()
        h = IntToStrAgent()

        # Left side: (f >> g) >> h
        fg = f >> g
        left = fg >> h

        # Right side: f >> (g >> h)
        gh = g >> h
        right = f >> gh

        input_val = "hello"

        result_left = await left.invoke(input_val)
        result_right = await right.invoke(input_val)

        # "hello" -> 5 -> 10 -> "10"
        assert result_left == result_right == "10"

    @pytest.mark.asyncio
    async def test_identity_left(self) -> None:
        """Test id >> f = f"""
        identity = IdentityAgent()
        double = DoubleAgent()

        composed = identity >> double

        result_composed = await composed.invoke(5)
        result_direct = await double.invoke(5)

        assert result_composed == result_direct == 10

    @pytest.mark.asyncio
    async def test_identity_right(self) -> None:
        """Test f >> id = f"""
        double = DoubleAgent()
        identity = IdentityAgent()

        composed = double >> identity

        result_composed = await composed.invoke(5)
        result_direct = await double.invoke(5)

        assert result_composed == result_direct == 10


class TestFixPattern:
    """Test Fix pattern (retry with exponential backoff)."""

    @pytest.mark.asyncio
    async def test_fix_recovers_from_transient_failure(self) -> None:
        """Fix pattern recovers from transient failures."""
        flakey = FlakeyAgent()
        resilient = fix(flakey, max_attempts=5, base_delay=0.01)

        result = await resilient.invoke(21)

        assert result == 42
        assert flakey.attempts == 2  # Failed once, succeeded on second

    @pytest.mark.asyncio
    async def test_fix_propagates_permanent_failure(self) -> None:
        """Fix pattern propagates non-transient failures."""
        always_fails = AlwaysFailsAgent()
        resilient = fix(always_fails, max_attempts=3, base_delay=0.01)

        with pytest.raises(ValueError, match="Permanent failure"):
            await resilient.invoke(5)

    @pytest.mark.asyncio
    async def test_fix_with_custom_is_transient(self) -> None:
        """Fix pattern uses custom is_transient predicate."""

        def is_value_error(e: Exception) -> bool:
            return isinstance(e, ValueError)

        flakey = FlakeyAgent()
        resilient = fix(
            flakey,
            max_attempts=5,
            base_delay=0.01,
            is_transient=is_value_error,
        )

        result = await resilient.invoke(21)
        assert result == 42


class TestListFunctor:
    """Test List functor for parallel processing."""

    @pytest.mark.asyncio
    async def test_list_parallel_processing(self) -> None:
        """List functor processes elements in parallel."""
        double = DoubleAgent()
        lifted = list_agent(double, parallel=True)

        result = await lifted.invoke([1, 2, 3, 4, 5])

        assert result == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_list_sequential_processing(self) -> None:
        """List functor can process elements sequentially."""
        double = DoubleAgent()
        lifted = list_agent(double, parallel=False)

        result = await lifted.invoke([1, 2, 3])

        assert result == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_list_empty_input(self) -> None:
        """List functor handles empty input."""
        double = DoubleAgent()
        lifted = list_agent(double)

        result = await lifted.invoke([])

        assert result == []


class TestAsyncFunctor:
    """Test Async functor for non-blocking execution."""

    @pytest.mark.asyncio
    async def test_async_returns_future(self) -> None:
        """Async functor returns a future immediately."""
        double = DoubleAgent()
        async_double = async_agent(double)

        future = await async_double.invoke(21)

        # Future should be awaitable
        result = await future
        assert result == 42


class TestLoggedFunctor:
    """Test Logged functor for observability."""

    @pytest.mark.asyncio
    async def test_logged_records_invocations(self) -> None:
        """Logged functor records all invocations."""
        double = DoubleAgent()
        logged_double = logged(double)

        await logged_double.invoke(5)
        await logged_double.invoke(10)

        assert len(logged_double.history) == 2
        assert logged_double.history[0].input_repr == "5"
        assert logged_double.history[1].input_repr == "10"

    @pytest.mark.asyncio
    async def test_logged_records_errors(self) -> None:
        """Logged functor records errors."""
        always_fails = AlwaysFailsAgent()
        logged_fails = logged(always_fails)

        with pytest.raises(ValueError):
            await logged_fails.invoke(5)

        assert len(logged_fails.history) == 1
        assert logged_fails.history[0].error is not None
        assert "Permanent failure" in logged_fails.history[0].error


class TestParallelComposition:
    """Test parallel composition patterns."""

    @pytest.mark.asyncio
    async def test_parallel_agents(self) -> None:
        """Parallel composition runs agents concurrently."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        parallel_agent = parallel(double, add_ten)
        result = await parallel_agent.invoke(5)

        # Both agents get same input, results combined as list
        assert result == [10, 15]

    @pytest.mark.asyncio
    async def test_fan_out(self) -> None:
        """Fan-out broadcasts to multiple agents."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        fan = fan_out(double, add_ten)
        results = await fan.invoke(5)

        # Fan-out returns tuple
        assert results == (10, 15)

    @pytest.mark.asyncio
    async def test_race(self) -> None:
        """Race returns first completed result."""

        class SlowAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Slow"

            async def invoke(self, input: int) -> int:
                await asyncio.sleep(0.5)
                return input * 10

        fast = DoubleAgent()
        slow = SlowAgent()

        racer = race(fast, slow)
        result = await racer.invoke(5)

        # Fast agent should win
        assert result == 10  # fast doubles, not slow * 10


class TestConditionalComposition:
    """Test conditional composition patterns."""

    @pytest.mark.asyncio
    async def test_branch(self) -> None:
        """Branch selects agent based on condition."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        # branch takes (predicate, if_true, if_false)
        branching = branch(
            lambda x: x > 10,  # predicate
            add_ten,  # if_true
            double,  # if_false
        )

        # x > 10: add ten
        result_high = await branching.invoke(15)
        assert result_high == 25

        # x <= 10: double
        result_low = await branching.invoke(5)
        assert result_low == 10

    @pytest.mark.asyncio
    async def test_switch(self) -> None:
        """Switch dispatches based on key function."""
        double = DoubleAgent()
        add_ten = AddTenAgent()
        identity = IdentityAgent()

        # switch takes (key_fn, cases, default)
        switching = switch(
            lambda x: "double" if x < 10 else "add",  # key function
            {"double": double, "add": add_ten},  # cases
            identity,  # default
        )

        # x < 10: uses double
        result_low = await switching.invoke(5)
        assert result_low == 10

        # x >= 10: uses add
        result_high = await switching.invoke(15)
        assert result_high == 25

    @pytest.mark.asyncio
    async def test_guarded(self) -> None:
        """Guarded agent only runs if guard passes."""
        double = DoubleAgent()

        # guarded takes (guard, agent, on_fail)
        safe_double = guarded(
            lambda x: x > 0,  # guard
            double,  # agent
            -1,  # on_fail value
        )

        # Guard passes
        result = await safe_double.invoke(5)
        assert result == 10

        # Guard fails
        result_fail = await safe_double.invoke(-5)
        assert result_fail == -1


class TestFunctorLiftedComposition:
    """Test that lifted agents compose correctly."""

    @pytest.mark.asyncio
    async def test_lifted_composition_short_circuits(self) -> None:
        """Lifted agents short-circuit on failure."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        lifted_double = maybe(double)
        lifted_add = maybe(add_ten)

        composed = lifted_double >> lifted_add

        # Nothing short-circuits
        result = await composed.invoke(Nothing)
        assert result.is_nothing()

        # Just passes through
        result_just = await composed.invoke(Just(5))
        assert isinstance(result_just, Just)
        assert result_just.value == 20

    @pytest.mark.asyncio
    async def test_either_composition_propagates_left(self) -> None:
        """Either composition propagates Left."""
        double = DoubleAgent()
        add_ten = AddTenAgent()

        lifted_double = either(double)
        lifted_add = either(add_ten)

        composed = lifted_double >> lifted_add

        # Left propagates
        result = await composed.invoke(Left("error"))
        assert isinstance(result, Left)
        assert result.error == "error"

        # Right passes through
        result_right = await composed.invoke(Right(5))
        assert isinstance(result_right, Right)
        assert result_right.value == 20
