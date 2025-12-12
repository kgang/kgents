"""
Tests for C-gent UniversalFunctor compliance (Alethic Algebra Phase 2).

Verifies that all C-gent functors satisfy the functor laws:
1. Identity: F(id) = id in F's category
2. Composition: F(g . f) = F(g) . F(f)
"""

import pytest
from agents.a.functor import (
    FunctorRegistry,
    verify_composition_law,
    verify_functor,
    verify_identity_law,
)
from agents.c.functor import (
    AsyncFunctor,
    EitherFunctor,
    FixFunctor,
    Just,
    Left,
    ListFunctor,
    LoggedFunctor,
    MaybeFunctor,
    Right,
)
from bootstrap.types import Agent

# =============================================================================
# Test Fixtures
# =============================================================================


class IdentityAgent(Agent[int, int]):
    """Identity agent for law testing."""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input: int) -> int:
        return input


class DoubleAgent(Agent[int, int]):
    """Doubles its input."""

    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class AddOneAgent(Agent[int, int]):
    """Adds one to input."""

    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input: int) -> int:
        return input + 1


# =============================================================================
# MaybeFunctor Law Tests
# =============================================================================


class TestMaybeFunctorLaws:
    """Verify MaybeFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law_just(self) -> None:
        """F(id)(Just(x)) = Just(x)."""
        result = await verify_identity_law(MaybeFunctor, IdentityAgent(), Just(42))

        assert result.passed is True
        assert result.left_result == Just(42)
        assert result.right_result == Just(42)

    @pytest.mark.asyncio
    async def test_identity_law_nothing(self) -> None:
        """F(id)(Nothing) = Nothing."""
        from agents.c.functor import Nothing

        lifted = MaybeFunctor.lift(IdentityAgent())
        result = await lifted.invoke(Nothing)

        assert result.is_nothing()

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            MaybeFunctor,
            DoubleAgent(),
            AddOneAgent(),
            Just(5),
        )

        assert result.passed is True
        # (5 * 2) + 1 = 11
        assert result.left_result == Just(11)
        assert result.right_result == Just(11)

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            MaybeFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            Just(5),
        )

        assert report.passed is True
        assert report.functor_name == "MaybeFunctor"

    def test_pure(self) -> None:
        """pure(x) = Just(x)."""
        result = MaybeFunctor.pure(42)
        assert result == Just(42)


# =============================================================================
# EitherFunctor Law Tests
# =============================================================================


class TestEitherFunctorLaws:
    """Verify EitherFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law_right(self) -> None:
        """F(id)(Right(x)) = Right(x)."""
        result = await verify_identity_law(EitherFunctor, IdentityAgent(), Right(42))

        assert result.passed is True
        assert result.left_result == Right(42)

    @pytest.mark.asyncio
    async def test_identity_law_left(self) -> None:
        """F(id)(Left(e)) = Left(e)."""
        lifted = EitherFunctor.lift(IdentityAgent())
        result = await lifted.invoke(Left("error"))

        assert result.is_left()
        # Cast to Left to access error attribute (mypy can't narrow Either type)
        left_result = result
        assert isinstance(left_result, Left)
        assert left_result.error == "error"

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            EitherFunctor,
            DoubleAgent(),
            AddOneAgent(),
            Right(5),
        )

        assert result.passed is True
        assert result.left_result == Right(11)
        assert result.right_result == Right(11)

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            EitherFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            Right(5),
        )

        assert report.passed is True

    def test_pure(self) -> None:
        """pure(x) = Right(x)."""
        result = EitherFunctor.pure(42)
        assert result == Right(42)


# =============================================================================
# ListFunctor Law Tests
# =============================================================================


class TestListFunctorLaws:
    """Verify ListFunctor satisfies functor laws."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(xs) = xs."""
        result = await verify_identity_law(ListFunctor, IdentityAgent(), [1, 2, 3])

        assert result.passed is True
        assert result.left_result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_identity_law_empty(self) -> None:
        """F(id)([]) = []."""
        lifted = ListFunctor.lift(IdentityAgent())
        result = await lifted.invoke([])

        assert result == []

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            ListFunctor,
            DoubleAgent(),
            AddOneAgent(),
            [1, 2, 3],
        )

        assert result.passed is True
        # [1*2+1, 2*2+1, 3*2+1] = [3, 5, 7]
        assert result.left_result == [3, 5, 7]
        assert result.right_result == [3, 5, 7]

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            ListFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            [1, 2],
        )

        assert report.passed is True

    def test_pure(self) -> None:
        """pure(x) = [x]."""
        result = ListFunctor.pure(42)
        assert result == [42]


# =============================================================================
# LoggedFunctor Law Tests
# =============================================================================


class TestLoggedFunctorLaws:
    """Verify LoggedFunctor satisfies functor laws (as endofunctor)."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(x) = x (logged)."""
        result = await verify_identity_law(LoggedFunctor, IdentityAgent(), 42)

        assert result.passed is True
        assert result.left_result == 42

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            LoggedFunctor,
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert result.passed is True
        assert result.left_result == 11

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            LoggedFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert report.passed is True

    def test_pure(self) -> None:
        """pure(x) = x (identity for endofunctor)."""
        result = LoggedFunctor.pure(42)
        assert result == 42


# =============================================================================
# FixFunctor Law Tests
# =============================================================================


class TestFixFunctorLaws:
    """Verify FixFunctor satisfies functor laws (as endofunctor)."""

    @pytest.mark.asyncio
    async def test_identity_law(self) -> None:
        """F(id)(x) = x (with retry)."""
        result = await verify_identity_law(FixFunctor, IdentityAgent(), 42)

        assert result.passed is True
        assert result.left_result == 42

    @pytest.mark.asyncio
    async def test_composition_law(self) -> None:
        """F(g . f) = F(g) . F(f)."""
        result = await verify_composition_law(
            FixFunctor,
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert result.passed is True
        assert result.left_result == 11

    @pytest.mark.asyncio
    async def test_full_verification(self) -> None:
        """Complete functor verification."""
        report = await verify_functor(
            FixFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert report.passed is True

    def test_pure(self) -> None:
        """pure(x) = x (identity for endofunctor)."""
        result = FixFunctor.pure(42)
        assert result == 42


# =============================================================================
# AsyncFunctor Tests (Special handling for Futures)
# =============================================================================


class TestAsyncFunctorLaws:
    """Verify AsyncFunctor behavior (special case: returns Future)."""

    @pytest.mark.asyncio
    async def test_lift_returns_future(self) -> None:
        """AsyncFunctor.lift() returns an agent that produces futures."""
        lifted = AsyncFunctor.lift(DoubleAgent())
        future = await lifted.invoke(5)

        # Should be a Future
        import asyncio

        assert isinstance(future, asyncio.Future)

        # Await the future to get the result
        result = await future
        assert result == 10

    @pytest.mark.asyncio
    async def test_pure_returns_resolved_future(self) -> None:
        """pure(x) returns an immediately-resolved Future."""
        import asyncio

        future = AsyncFunctor.pure(42)
        assert isinstance(future, asyncio.Future)

        # Should already be done
        result = await future
        assert result == 42


# =============================================================================
# Registry Tests
# =============================================================================


class TestFunctorRegistration:
    """Verify C-gent functors are properly registered."""

    def test_maybe_functor_registered(self) -> None:
        """MaybeFunctor is in the registry."""
        functor = FunctorRegistry.get("Maybe")
        assert functor is not None
        assert functor.__name__ == "MaybeFunctor"

    def test_either_functor_registered(self) -> None:
        """EitherFunctor is in the registry."""
        functor = FunctorRegistry.get("Either")
        assert functor is not None
        assert functor.__name__ == "EitherFunctor"

    def test_list_functor_registered(self) -> None:
        """ListFunctor is in the registry."""
        functor = FunctorRegistry.get("List")
        assert functor is not None
        assert functor.__name__ == "ListFunctor"

    def test_async_functor_registered(self) -> None:
        """AsyncFunctor is in the registry."""
        functor = FunctorRegistry.get("Async")
        assert functor is not None
        assert functor.__name__ == "AsyncFunctor"

    def test_logged_functor_registered(self) -> None:
        """LoggedFunctor is in the registry."""
        functor = FunctorRegistry.get("Logged")
        assert functor is not None
        assert functor.__name__ == "LoggedFunctor"

    def test_fix_functor_registered(self) -> None:
        """FixFunctor is in the registry."""
        functor = FunctorRegistry.get("Fix")
        assert functor is not None
        assert functor.__name__ == "FixFunctor"

    def test_all_cgent_functors_in_registry(self) -> None:
        """All C-gent functors are registered."""
        all_functors = FunctorRegistry.all_functors()

        expected = {"Maybe", "Either", "List", "Async", "Logged", "Fix"}
        registered = set(all_functors.keys())

        # All expected functors should be present
        assert expected.issubset(registered)


# =============================================================================
# Backward Compatibility Tests
# =============================================================================


class TestBackwardCompatibility:
    """Verify existing convenience functions still work."""

    @pytest.mark.asyncio
    async def test_maybe_function(self) -> None:
        """maybe() convenience function works."""
        from agents.c.functor import maybe

        lifted = maybe(DoubleAgent())
        result = await lifted.invoke(Just(5))
        assert result == Just(10)

    @pytest.mark.asyncio
    async def test_either_function(self) -> None:
        """either() convenience function works."""
        from agents.c.functor import either

        lifted = either(DoubleAgent())
        result = await lifted.invoke(Right(5))
        assert result == Right(10)

    @pytest.mark.asyncio
    async def test_list_agent_function(self) -> None:
        """list_agent() convenience function works."""
        from agents.c.functor import list_agent

        lifted = list_agent(DoubleAgent())
        result = await lifted.invoke([1, 2, 3])
        assert result == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_fix_function(self) -> None:
        """fix() convenience function works."""
        from agents.c.functor import fix

        lifted = fix(DoubleAgent())
        result = await lifted.invoke(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_logged_function(self) -> None:
        """logged() convenience function works."""
        from agents.c.functor import logged

        lifted = logged(DoubleAgent())
        result = await lifted.invoke(5)
        assert result == 10
        assert len(lifted.history) == 1
