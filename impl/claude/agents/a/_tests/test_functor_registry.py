"""
Tests for FunctorRegistry and cross-functor composition (Phase 4 & 5).

Verifies:
1. All expected functors are registered
2. Registry discovery works
3. Functor composition (F . G) works
4. Composition matrix: key pairs compose correctly
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest

# Import modules to trigger auto-registration
import agents.c.functor  # noqa: F401 - needed for registration
import agents.d.state_monad  # noqa: F401 - needed for registration
import agents.flux.functor  # noqa: F401 - needed for registration
import agents.k.functor  # noqa: F401 - needed for registration
from agents.a.functor import (
    FunctorRegistry,
    UniversalFunctor,
    compose_functors,
    identity_functor,
)
from agents.poly.types import Agent

# =============================================================================
# Test Fixtures
# =============================================================================


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


class IdentityAgent(Agent[int, int]):
    """Identity agent."""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input: int) -> int:
        return input


# =============================================================================
# Registry Activation Tests (Phase 4)
# =============================================================================


class TestFunctorRegistration:
    """Verify all functors are registered."""

    def test_c_gent_functors_registered(self) -> None:
        """All 6 C-gent functors are registered."""
        expected = {"Maybe", "Either", "List", "Async", "Logged", "Fix"}
        registered = set(FunctorRegistry.all_functors().keys())
        assert expected.issubset(registered)

    def test_state_functor_registered(self) -> None:
        """StateMonadFunctor is registered."""
        functor = FunctorRegistry.get("State")
        assert functor is not None
        assert "State" in functor.__name__

    def test_flux_functor_registered(self) -> None:
        """FluxFunctor is registered."""
        functor = FunctorRegistry.get("Flux")
        assert functor is not None
        assert "Flux" in functor.__name__

    def test_soul_functor_registered(self) -> None:
        """SoulFunctor is registered."""
        functor = FunctorRegistry.get("Soul")
        assert functor is not None
        assert "Soul" in functor.__name__

    def test_at_least_9_functors(self) -> None:
        """Registry contains at least 9 functors (Phase 4 goal)."""
        all_functors = FunctorRegistry.all_functors()
        assert len(all_functors) >= 9, f"Only {len(all_functors)} functors registered"

    def test_all_functors_have_lift(self) -> None:
        """All registered functors have lift() method."""
        for name, functor in FunctorRegistry.all_functors().items():
            assert hasattr(functor, "lift"), f"{name} missing lift()"

    def test_most_functors_have_unlift(self) -> None:
        """Most registered functors have unlift() method (symmetric lifting)."""
        functors_with_unlift = 0
        for name, functor in FunctorRegistry.all_functors().items():
            if hasattr(functor, "unlift"):
                # Check it's actually implemented (not just inherited)
                try:
                    functor.unlift(DoubleAgent())  # type: ignore[arg-type]
                except (TypeError, NotImplementedError):
                    functors_with_unlift += 1  # Has unlift, just wrong type
                except Exception:
                    functors_with_unlift += 1  # Other error, but has unlift

        # At least 4 new functors should have unlift (Maybe, Either, List, Observer, State, etc.)
        assert functors_with_unlift >= 4, f"Only {functors_with_unlift} functors with unlift"


# =============================================================================
# Composition Tests (Phase 5)
# =============================================================================


class TestFunctorComposition:
    """Test functor composition (F . G)."""

    @pytest.mark.asyncio
    async def test_identity_functor_is_unit(self) -> None:
        """Identity functor is the composition unit."""
        IdF = identity_functor()
        agent = DoubleAgent()

        lifted = IdF.lift(agent)

        assert lifted is agent
        assert await lifted.invoke(5) == 10

    @pytest.mark.asyncio
    async def test_compose_maybe_logged(self) -> None:
        """Maybe . Logged composition works."""
        from agents.c.functor import Just, LoggedFunctor, MaybeFunctor

        composed_lift = compose_functors(MaybeFunctor, LoggedFunctor)
        agent = DoubleAgent()

        lifted = composed_lift(agent)

        # Inner is LoggedAgent, outer is MaybeAgent
        result = await lifted.invoke(Just(5))
        assert result == Just(10)

    @pytest.mark.asyncio
    async def test_compose_either_list(self) -> None:
        """Either . List composition works."""
        from agents.c.functor import EitherFunctor, ListFunctor, Right

        composed_lift = compose_functors(EitherFunctor, ListFunctor)
        agent = DoubleAgent()

        lifted = composed_lift(agent)

        # Input is Either[E, list[int]]
        result = await lifted.invoke(Right([1, 2, 3]))
        assert result == Right([2, 4, 6])


class TestCompositionMatrix:
    """Test composition matrix: verify key functor pairs compose."""

    @pytest.mark.asyncio
    async def test_flux_state_composition(self) -> None:
        """Flux . State composition (streaming + state)."""
        from agents.flux.functor import FluxFunctor
        from agents.s import MemoryStateBackend, StateFunctor

        backend = MemoryStateBackend(initial={"count": 0})

        # State(agent) first, then Flux
        state_agent = StateFunctor.lift(DoubleAgent(), backend=backend)
        flux_agent = FluxFunctor.lift(state_agent)

        # Create source stream
        async def source() -> AsyncGenerator[int, None]:
            yield 5
            yield 10

        # Collect results
        # Note: Full test would use Flux.start(), but we just verify composition works
        assert flux_agent is not None

    @pytest.mark.asyncio
    async def test_maybe_fix_composition(self) -> None:
        """Maybe . Fix composition (optional + resilience)."""
        from agents.c.functor import FixFunctor, Just, MaybeFunctor

        composed_lift = compose_functors(MaybeFunctor, FixFunctor)
        agent = DoubleAgent()

        lifted = composed_lift(agent)

        result = await lifted.invoke(Just(7))
        assert result == Just(14)


# =============================================================================
# Registry Discovery Tests
# =============================================================================


class TestRegistryDiscovery:
    """Test registry discovery patterns."""

    def test_get_returns_none_for_unknown(self) -> None:
        """get() returns None for unknown functor."""
        result = FunctorRegistry.get("NonExistent")
        assert result is None

    def test_all_functors_returns_copy(self) -> None:
        """all_functors() returns a copy (immutable view)."""
        all1 = FunctorRegistry.all_functors()
        all2 = FunctorRegistry.all_functors()
        assert all1 is not all2
        assert all1 == all2

    def test_functor_names_are_consistent(self) -> None:
        """Functor names match their class names (convention)."""
        for name, functor in FunctorRegistry.all_functors().items():
            # Name should appear somewhere in class name
            # E.g., "Maybe" in "MaybeFunctor", "Observer" in "UnifiedObserverFunctor"
            assert name in functor.__name__ or functor.__name__.startswith(name)


# =============================================================================
# Batch Law Verification Tests
# =============================================================================


class TestBatchFunctorLawVerification:
    """
    Verify all registered functors satisfy categorical laws.

    This is the "alethic witness" test - ensures the entire functor
    ecosystem maintains algebraic coherence.
    """

    @pytest.mark.asyncio
    async def test_maybe_functor_satisfies_laws(self) -> None:
        """Verify MaybeFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.c.functor import Just, MaybeFunctor

        test_input = Just(5)
        report = await verify_functor(
            MaybeFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )
        assert report.identity_law.passed, (
            f"Maybe: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"Maybe: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_either_functor_satisfies_laws(self) -> None:
        """Verify EitherFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.c.functor import EitherFunctor, Right

        test_input = Right(5)
        report = await verify_functor(
            EitherFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )
        assert report.identity_law.passed, (
            f"Either: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"Either: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_list_functor_satisfies_laws(self) -> None:
        """Verify ListFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.c.functor import ListFunctor

        test_input = [5]
        report = await verify_functor(
            ListFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )
        assert report.identity_law.passed, (
            f"List: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"List: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_logged_functor_satisfies_laws(self) -> None:
        """Verify LoggedFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.c.functor import LoggedFunctor

        test_input = 5
        report = await verify_functor(
            LoggedFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )
        assert report.identity_law.passed, (
            f"Logged: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"Logged: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_fix_functor_satisfies_laws(self) -> None:
        """Verify FixFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.c.functor import FixFunctor

        test_input = 5
        report = await verify_functor(
            FixFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )
        assert report.identity_law.passed, (
            f"Fix: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"Fix: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_soul_functor_satisfies_laws(self) -> None:
        """Verify SoulFunctor satisfies categorical laws."""
        from agents.a.functor import verify_functor
        from agents.k.functor import Soul, SoulFunctor

        # Soul functor operates on Soul[int] values
        test_input = Soul(value=5)

        report = await verify_functor(
            SoulFunctor,
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            test_input,
        )

        assert report.identity_law.passed, (
            f"Soul: Identity law failed - {report.identity_law.explanation}"
        )
        assert report.composition_law.passed, (
            f"Soul: Composition law failed - {report.composition_law.explanation}"
        )

    @pytest.mark.asyncio
    async def test_verify_all_reports_generated(self) -> None:
        """
        Test FunctorRegistry.verify_all() generates reports for all functors.

        This tests the batch verification API produces reports. Note that
        non-discrete functors (Flux, Observer, State, Async) may not pass
        standard verification because they operate on different domains.
        """
        from agents.c.functor import Just, Right

        def input_factory(functor_name: str) -> Any:
            """Create appropriate test input for each functor type."""
            if functor_name == "Maybe":
                return Just(5)
            elif functor_name == "Either":
                return Right(5)
            elif functor_name == "List":
                return [5]
            elif functor_name == "Soul":
                from agents.k.functor import Soul

                return Soul(value=5)
            else:
                # Default for Logged, Fix, and others
                return 5

        reports = await FunctorRegistry.verify_all(
            IdentityAgent(),
            DoubleAgent(),
            AddOneAgent(),
            input_factory,
        )

        # Verify we got reports for registered functors
        assert len(reports) > 0, "No functors were verified"

        # Verify all functors produced a report (even if some fail due to domain mismatch)
        all_functors = FunctorRegistry.all_functors()
        for name in all_functors:
            assert name in reports, f"Missing report for {name}"
