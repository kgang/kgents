"""
Tests for the Universal Functor Protocol (Alethic Algebra).

These tests verify:
1. Functor law compliance (identity, composition)
2. Protocol structural checks
3. Functor registry operations
4. Functor composition combinators
"""

from typing import Any

import pytest
from agents.a.functor import (
    FunctorLawResult,
    FunctorRegistry,
    FunctorVerificationReport,
    Liftable,
    Pointed,
    UniversalFunctor,
    compose_functors,
    identity_functor,
    verify_composition_law,
    verify_functor,
    verify_identity_law,
)
from agents.poly.types import Agent

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


# A simple functor that wraps values in a tuple
class TupleFunctor(UniversalFunctor[tuple[Any, Any]]):
    """Wraps agent output in a tuple with the original input."""

    @staticmethod
    def lift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
        class TupleAgent(Agent[Any, tuple[Any, Any]]):
            def __init__(self, inner: Agent[Any, Any]) -> None:
                self._inner = inner

            @property
            def name(self) -> str:
                return f"Tuple({self._inner.name})"

            async def invoke(self, input: Any) -> tuple[Any, Any]:
                result = await self._inner.invoke(input)
                return (input, result)

        return TupleAgent(agent)

    @staticmethod
    def pure(value: Any) -> tuple[Any, Any]:
        return (None, value)


# Identity functor (does nothing)
class IdFunctor(UniversalFunctor[Any]):
    """Identity functor - returns agent unchanged."""

    @staticmethod
    def lift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
        return agent

    @staticmethod
    def pure(value: Any) -> Any:
        return value


# =============================================================================
# Protocol Tests
# =============================================================================


class TestLiftableProtocol:
    """Test the Liftable protocol."""

    def test_class_satisfies_liftable(self) -> None:
        """Classes with lift() method satisfy Liftable."""
        # IdFunctor has a lift static method
        assert hasattr(IdFunctor, "lift")
        # Runtime check would require instance, but we verify structure

    def test_universal_functor_is_liftable(self) -> None:
        """UniversalFunctor subclasses satisfy Liftable protocol."""

        class CustomFunctor(UniversalFunctor[Any]):
            @staticmethod
            def lift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
                return agent

        assert hasattr(CustomFunctor, "lift")


class TestPointedProtocol:
    """Test the Pointed protocol."""

    def test_class_with_pure_satisfies_pointed(self) -> None:
        """Classes with pure() method satisfy Pointed."""
        assert hasattr(TupleFunctor, "pure")
        result = TupleFunctor.pure(42)
        assert result == (None, 42)


# =============================================================================
# Law Verification Tests
# =============================================================================


class TestFunctorLaws:
    """Test functor law verification."""

    @pytest.mark.asyncio
    async def test_identity_law_passes_for_id_functor(self) -> None:
        """Identity functor satisfies identity law."""
        result = await verify_identity_law(IdFunctor, IdentityAgent(), 42)

        assert isinstance(result, FunctorLawResult)
        assert result.law_name == "identity"
        assert result.passed is True
        assert result.left_result == 42
        assert result.right_result == 42

    @pytest.mark.asyncio
    async def test_composition_law_passes_for_id_functor(self) -> None:
        """Identity functor satisfies composition law."""
        result = await verify_composition_law(
            IdFunctor,
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert isinstance(result, FunctorLawResult)
        assert result.law_name == "composition"
        assert result.passed is True
        # F(g.f)(5) = (5 * 2) + 1 = 11
        assert result.left_result == 11
        assert result.right_result == 11

    @pytest.mark.asyncio
    async def test_verify_functor_full_report(self) -> None:
        """Full functor verification produces complete report."""
        report = await verify_functor(
            IdFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            5,
        )

        assert isinstance(report, FunctorVerificationReport)
        assert report.functor_name == "IdFunctor"
        assert report.identity_law.passed is True
        assert report.composition_law.passed is True
        assert report.passed is True


class TestTupleFunctor:
    """Test the TupleFunctor example."""

    @pytest.mark.asyncio
    async def test_tuple_functor_lifts_agent(self) -> None:
        """TupleFunctor wraps output in tuple."""
        lifted = TupleFunctor.lift(DoubleAgent())
        result = await lifted.invoke(5)

        assert result == (5, 10)

    @pytest.mark.asyncio
    async def test_tuple_functor_identity_law(self) -> None:
        """TupleFunctor identity law (note: fails by design)."""
        # The tuple functor doesn't satisfy identity law because
        # it adds structure - this tests that our verification catches it
        result = await verify_identity_law(TupleFunctor, IdentityAgent(), 42)

        # (42, 42) != 42, so law fails
        assert result.passed is False

    @pytest.mark.asyncio
    async def test_tuple_functor_pure(self) -> None:
        """TupleFunctor.pure embeds value in tuple."""
        result = TupleFunctor.pure("hello")
        assert result == (None, "hello")


# =============================================================================
# Functor Combinator Tests
# =============================================================================


class TestFunctorCombinators:
    """Test functor composition and combinators."""

    @pytest.mark.asyncio
    async def test_identity_functor_factory(self) -> None:
        """identity_functor() returns identity functor."""
        IdF = identity_functor()
        lifted = IdF.lift(DoubleAgent())
        result = await lifted.invoke(5)

        assert result == 10

    @pytest.mark.asyncio
    async def test_compose_functors_identity(self) -> None:
        """Composing with identity functor is identity."""
        IdF = identity_functor()
        composed_lift = compose_functors(IdF, IdF)

        lifted = composed_lift(DoubleAgent())
        result = await lifted.invoke(5)

        assert result == 10

    @pytest.mark.asyncio
    async def test_compose_functors_order(self) -> None:
        """Functor composition applies in correct order."""
        # compose_functors(F, G) means F(G(agent))
        composed_lift = compose_functors(TupleFunctor, IdFunctor)

        lifted = composed_lift(DoubleAgent())
        result = await lifted.invoke(5)

        # G(agent) = agent (IdFunctor)
        # F(G(agent)) = TupleFunctor(agent)
        assert result == (5, 10)


# =============================================================================
# Registry Tests
# =============================================================================


class TestFunctorRegistry:
    """Test the functor registry."""

    def setup_method(self) -> None:
        """Save and clear registry before each test."""
        self._saved_functors = FunctorRegistry._functors.copy()
        FunctorRegistry._functors.clear()

    def teardown_method(self) -> None:
        """Restore registry after each test."""
        FunctorRegistry._functors.clear()
        FunctorRegistry._functors.update(self._saved_functors)

    def test_register_and_get(self) -> None:
        """Can register and retrieve functors."""
        FunctorRegistry.register("id", IdFunctor)
        retrieved = FunctorRegistry.get("id")

        assert retrieved is IdFunctor

    def test_get_returns_none_for_unknown(self) -> None:
        """get() returns None for unknown functors."""
        result = FunctorRegistry.get("nonexistent")
        assert result is None

    def test_all_functors(self) -> None:
        """all_functors() returns copy of registry."""
        FunctorRegistry.register("id", IdFunctor)
        FunctorRegistry.register("tuple", TupleFunctor)

        all_f = FunctorRegistry.all_functors()

        assert len(all_f) == 2
        assert "id" in all_f
        assert "tuple" in all_f

    @pytest.mark.asyncio
    async def test_verify_all_functors(self) -> None:
        """verify_all() checks all registered functors."""
        FunctorRegistry.register("id", IdFunctor)

        def input_factory(name: str) -> int:
            return 5

        reports = await FunctorRegistry.verify_all(
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            input_factory,
        )

        assert "id" in reports
        assert reports["id"].passed is True


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_verify_handles_exceptions(self) -> None:
        """Verification handles exceptions gracefully."""

        class FailingFunctor(UniversalFunctor[Any]):
            @staticmethod
            def lift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
                raise RuntimeError("Intentional failure")

        result = await verify_identity_law(FailingFunctor, IdentityAgent(), 42)

        assert result.passed is False
        assert "Intentional failure" in result.explanation

    def test_functor_without_pure_raises(self) -> None:
        """Functor without pure() raises NotImplementedError."""

        class NoPureFunctor(UniversalFunctor[Any]):
            @staticmethod
            def lift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
                return agent

        with pytest.raises(NotImplementedError):
            NoPureFunctor.pure(42)
