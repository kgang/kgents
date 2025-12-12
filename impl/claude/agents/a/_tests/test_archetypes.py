"""
Tests for Genus Archetypes.

Archetypes are pre-packaged Halos that provide "batteries included"
ergonomics for common agent patterns.

Test Categories:
1. Archetype capabilities - each archetype has correct capabilities
2. Halo inheritance - subclasses inherit archetype Halo
3. Capability override - subclasses can add/override capabilities
4. Projector integration - archetypes work with LocalProjector
5. Edge cases - multiple inheritance, empty subclasses, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from bootstrap.types import Agent

from ..archetypes import (
    Archetype,
    Delta,
    Kappa,
    Lambda,
    get_archetype,
    is_archetype_instance,
)
from ..halo import (
    Capability,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    get_capability,
    get_halo,
    has_capability,
)

# ═══════════════════════════════════════════════════════════════════════
# Test Fixtures: Concrete Archetype Subclasses
# ═══════════════════════════════════════════════════════════════════════


class EchoKappa(Kappa[str, str]):
    """A Kappa agent that echoes input."""

    @property
    def name(self) -> str:
        return "echo-kappa"

    async def invoke(self, input: str) -> str:
        return f"kappa:{input}"


class EchoLambda(Lambda[str, str]):
    """A Lambda agent that echoes input."""

    @property
    def name(self) -> str:
        return "echo-lambda"

    async def invoke(self, input: str) -> str:
        return f"lambda:{input}"


class EchoDelta(Delta[str, str]):
    """A Delta agent that echoes input."""

    @property
    def name(self) -> str:
        return "echo-delta"

    async def invoke(self, input: str) -> str:
        return f"delta:{input}"


@dataclass
class CustomState:
    """Custom state schema for testing."""

    count: int = 0
    data: str = ""


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Kappa Archetype
# ═══════════════════════════════════════════════════════════════════════


class TestKappaArchetype:
    """Tests for Kappa (full-stack) archetype."""

    def test_kappa_has_stateful_capability(self) -> None:
        """Kappa includes @Stateful capability."""
        assert has_capability(EchoKappa, StatefulCapability)

    def test_kappa_has_soulful_capability(self) -> None:
        """Kappa includes @Soulful capability."""
        assert has_capability(EchoKappa, SoulfulCapability)

    def test_kappa_has_observable_capability(self) -> None:
        """Kappa includes @Observable capability."""
        assert has_capability(EchoKappa, ObservableCapability)

    def test_kappa_has_streamable_capability(self) -> None:
        """Kappa includes @Streamable capability."""
        assert has_capability(EchoKappa, StreamableCapability)

    def test_kappa_has_all_four_capabilities(self) -> None:
        """Kappa archetype includes all four standard capabilities."""
        halo = get_halo(EchoKappa)
        assert len(halo) == 4

    def test_kappa_stateful_config(self) -> None:
        """Kappa's @Stateful has correct default config."""
        cap = get_capability(EchoKappa, StatefulCapability)
        assert cap is not None
        assert cap.schema is dict
        assert cap.backend == "auto"

    def test_kappa_soulful_config(self) -> None:
        """Kappa's @Soulful has correct default config."""
        cap = get_capability(EchoKappa, SoulfulCapability)
        assert cap is not None
        assert cap.persona == "default"
        assert cap.mode == "advisory"

    def test_kappa_observable_config(self) -> None:
        """Kappa's @Observable has mirror and metrics enabled."""
        cap = get_capability(EchoKappa, ObservableCapability)
        assert cap is not None
        assert cap.mirror is True
        assert cap.metrics is True

    def test_kappa_streamable_config(self) -> None:
        """Kappa's @Streamable has correct default config."""
        cap = get_capability(EchoKappa, StreamableCapability)
        assert cap is not None
        assert cap.budget == 10.0
        assert cap.feedback == 0.0

    @pytest.mark.anyio
    async def test_kappa_is_invocable(self) -> None:
        """Kappa subclass can be invoked."""
        agent = EchoKappa()
        result = await agent.invoke("test")
        assert result == "kappa:test"


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Lambda Archetype
# ═══════════════════════════════════════════════════════════════════════


class TestLambdaArchetype:
    """Tests for Lambda (stateless function) archetype."""

    def test_lambda_has_observable_capability(self) -> None:
        """Lambda includes @Observable capability."""
        assert has_capability(EchoLambda, ObservableCapability)

    def test_lambda_no_stateful_capability(self) -> None:
        """Lambda does NOT include @Stateful."""
        assert not has_capability(EchoLambda, StatefulCapability)

    def test_lambda_no_soulful_capability(self) -> None:
        """Lambda does NOT include @Soulful."""
        assert not has_capability(EchoLambda, SoulfulCapability)

    def test_lambda_no_streamable_capability(self) -> None:
        """Lambda does NOT include @Streamable."""
        assert not has_capability(EchoLambda, StreamableCapability)

    def test_lambda_is_minimal(self) -> None:
        """Lambda archetype has only metrics (one capability)."""
        halo = get_halo(EchoLambda)
        assert len(halo) == 1

    def test_lambda_observable_config(self) -> None:
        """Lambda's @Observable has mirror=False, metrics=True."""
        cap = get_capability(EchoLambda, ObservableCapability)
        assert cap is not None
        assert cap.mirror is False  # Minimal overhead
        assert cap.metrics is True

    @pytest.mark.anyio
    async def test_lambda_is_invocable(self) -> None:
        """Lambda subclass can be invoked."""
        agent = EchoLambda()
        result = await agent.invoke("test")
        assert result == "lambda:test"


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Delta Archetype
# ═══════════════════════════════════════════════════════════════════════


class TestDeltaArchetype:
    """Tests for Delta (data-focused) archetype."""

    def test_delta_has_stateful_capability(self) -> None:
        """Delta includes @Stateful capability."""
        assert has_capability(EchoDelta, StatefulCapability)

    def test_delta_has_observable_capability(self) -> None:
        """Delta includes @Observable capability."""
        assert has_capability(EchoDelta, ObservableCapability)

    def test_delta_no_soulful_capability(self) -> None:
        """Delta does NOT include @Soulful."""
        assert not has_capability(EchoDelta, SoulfulCapability)

    def test_delta_no_streamable_capability(self) -> None:
        """Delta does NOT include @Streamable."""
        assert not has_capability(EchoDelta, StreamableCapability)

    def test_delta_has_two_capabilities(self) -> None:
        """Delta archetype has exactly two capabilities."""
        halo = get_halo(EchoDelta)
        assert len(halo) == 2

    def test_delta_stateful_config(self) -> None:
        """Delta's @Stateful has correct default config."""
        cap = get_capability(EchoDelta, StatefulCapability)
        assert cap is not None
        assert cap.schema is dict
        assert cap.backend == "auto"

    def test_delta_observable_config(self) -> None:
        """Delta's @Observable has full observability."""
        cap = get_capability(EchoDelta, ObservableCapability)
        assert cap is not None
        assert cap.mirror is True
        assert cap.metrics is True

    @pytest.mark.anyio
    async def test_delta_is_invocable(self) -> None:
        """Delta subclass can be invoked."""
        agent = EchoDelta()
        result = await agent.invoke("test")
        assert result == "delta:test"


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Halo Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestHaloInheritance:
    """Tests for archetype Halo inheritance."""

    def test_subclass_inherits_archetype_halo(self) -> None:
        """Subclass automatically gets archetype's Halo."""

        class MyService(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "my-service"

            async def invoke(self, x: str) -> str:
                return x

        # Should have all four capabilities from Kappa
        assert has_capability(MyService, StatefulCapability)
        assert has_capability(MyService, SoulfulCapability)
        assert has_capability(MyService, ObservableCapability)
        assert has_capability(MyService, StreamableCapability)

    def test_nested_subclass_inherits_halo(self) -> None:
        """Nested subclass (subclass of subclass) inherits Halo."""

        class BaseService(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "base"

            async def invoke(self, x: str) -> str:
                return x

        class DerivedService(BaseService):
            @property
            def name(self) -> str:
                return "derived"

        # Derived should have same capabilities
        assert len(get_halo(DerivedService)) == 4
        assert has_capability(DerivedService, StreamableCapability)

    def test_empty_subclass_gets_halo(self) -> None:
        """Subclass with no decorators still gets archetype Halo."""

        class EmptyKappa(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "empty"

            async def invoke(self, x: str) -> str:
                return x

        halo = get_halo(EmptyKappa)
        assert len(halo) == 4

    def test_halo_is_separate_per_subclass(self) -> None:
        """Each subclass gets its own Halo copy."""

        class Service1(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "s1"

            async def invoke(self, x: str) -> str:
                return x

        class Service2(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "s2"

            async def invoke(self, x: str) -> str:
                return x

        halo1 = get_halo(Service1)
        halo2 = get_halo(Service2)

        # Should be equal but not same object
        assert halo1 == halo2
        assert halo1 is not halo2


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Capability Override
# ═══════════════════════════════════════════════════════════════════════


class TestCapabilityOverride:
    """Tests for subclass capability override."""

    def test_subclass_can_add_capabilities(self) -> None:
        """Subclass can add more capabilities to archetype."""

        @Capability.Streamable(budget=20.0)
        class StreamingData(Delta[str, str]):
            @property
            def name(self) -> str:
                return "streaming"

            async def invoke(self, x: str) -> str:
                return x

        # Should have Delta's caps + Streamable
        assert has_capability(StreamingData, StatefulCapability)
        assert has_capability(StreamingData, ObservableCapability)
        assert has_capability(StreamingData, StreamableCapability)

        # Streamable config should be from the decorator
        cap = get_capability(StreamingData, StreamableCapability)
        assert cap is not None
        assert cap.budget == 20.0

    def test_subclass_can_override_capability_config(self) -> None:
        """Subclass can override archetype capability configuration."""

        @Capability.Stateful(schema=CustomState, backend="redis")
        class CustomDelta(Delta[str, str]):
            @property
            def name(self) -> str:
                return "custom"

            async def invoke(self, x: str) -> str:
                return x

        cap = get_capability(CustomDelta, StatefulCapability)
        assert cap is not None
        assert cap.schema is CustomState  # Overridden
        assert cap.backend == "redis"  # Overridden

    def test_override_does_not_duplicate(self) -> None:
        """Overriding capability doesn't create duplicates."""

        @Capability.Stateful(schema=list, backend="postgres")
        class OverriddenDelta(Delta[str, str]):
            @property
            def name(self) -> str:
                return "overridden"

            async def invoke(self, x: str) -> str:
                return x

        # Should still have exactly 2 capabilities (Stateful overridden, Observable)
        halo = get_halo(OverriddenDelta)
        stateful_caps = [c for c in halo if isinstance(c, StatefulCapability)]
        assert len(stateful_caps) == 1
        assert len(halo) == 2

    def test_adding_to_lambda_makes_richer(self) -> None:
        """Can enrich Lambda by adding capabilities."""

        @Capability.Stateful(schema=dict)
        @Capability.Streamable(budget=5.0)
        class EnrichedLambda(Lambda[str, str]):
            @property
            def name(self) -> str:
                return "enriched"

            async def invoke(self, x: str) -> str:
                return x

        # Now has three capabilities
        assert has_capability(EnrichedLambda, ObservableCapability)  # From Lambda
        assert has_capability(EnrichedLambda, StatefulCapability)  # Added
        assert has_capability(EnrichedLambda, StreamableCapability)  # Added

    def test_multiple_overrides(self) -> None:
        """Can override multiple capabilities at once."""

        @Capability.Stateful(schema=list, backend="memory")
        @Capability.Soulful(persona="Custom", mode="strict")
        @Capability.Streamable(budget=50.0, feedback=0.3)
        class FullyCustomKappa(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "fully-custom"

            async def invoke(self, x: str) -> str:
                return x

        # Still 4 capabilities
        halo = get_halo(FullyCustomKappa)
        assert len(halo) == 4

        # Check each was overridden
        stateful = get_capability(FullyCustomKappa, StatefulCapability)
        assert stateful is not None
        assert stateful.schema is list
        assert stateful.backend == "memory"

        soulful = get_capability(FullyCustomKappa, SoulfulCapability)
        assert soulful is not None
        assert soulful.persona == "Custom"
        assert soulful.mode == "strict"

        streamable = get_capability(FullyCustomKappa, StreamableCapability)
        assert streamable is not None
        assert streamable.budget == 50.0
        assert streamable.feedback == 0.3


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Projector Integration
# ═══════════════════════════════════════════════════════════════════════


class TestProjectorIntegration:
    """Tests for archetype integration with LocalProjector."""

    def test_kappa_compiles_correctly(self) -> None:
        """Kappa archetype compiles to FluxAgent (outermost)."""
        from agents.flux import FluxAgent
        from system.projector import LocalProjector

        compiled = LocalProjector().compile(EchoKappa)

        # Outermost should be FluxAgent (from Streamable)
        assert isinstance(compiled, FluxAgent)

    def test_lambda_compiles_correctly(self) -> None:
        """Lambda archetype compiles to plain agent (Observable only)."""
        from system.projector import LocalProjector

        compiled = LocalProjector().compile(EchoLambda)

        # Observable without Streamable returns agent as-is
        assert isinstance(compiled, EchoLambda)

    def test_delta_compiles_correctly(self) -> None:
        """Delta archetype compiles to StatefulAdapter."""
        from system.projector import LocalProjector
        from system.projector.local import StatefulAdapter

        compiled = LocalProjector().compile(EchoDelta)

        # Stateful wraps, Observable marks
        assert isinstance(compiled, StatefulAdapter)

    @pytest.mark.anyio
    async def test_compiled_kappa_is_invocable(self) -> None:
        """Compiled Kappa agent can be invoked."""
        from system.projector import LocalProjector

        compiled = LocalProjector().compile(EchoKappa)
        result = await compiled.invoke("test")
        assert result == "kappa:test"

    @pytest.mark.anyio
    async def test_compiled_lambda_is_invocable(self) -> None:
        """Compiled Lambda agent can be invoked."""
        from system.projector import LocalProjector

        compiled = LocalProjector().compile(EchoLambda)
        result = await compiled.invoke("test")
        assert result == "lambda:test"

    @pytest.mark.anyio
    async def test_compiled_delta_is_invocable(self) -> None:
        """Compiled Delta agent can be invoked."""
        from system.projector import LocalProjector

        compiled = LocalProjector().compile(EchoDelta)
        result = await compiled.invoke("test")
        assert result == "delta:test"

    def test_overridden_capability_affects_compilation(self) -> None:
        """Overridden capability config is used in compilation."""
        from agents.flux import FluxAgent
        from system.projector import LocalProjector

        @Capability.Streamable(budget=99.0)
        class CustomBudgetKappa(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "custom-budget"

            async def invoke(self, x: str) -> str:
                return x

        compiled = LocalProjector().compile(CustomBudgetKappa)
        assert isinstance(compiled, FluxAgent)
        assert compiled.config.entropy_budget == 99.0


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Utility Functions
# ═══════════════════════════════════════════════════════════════════════


class TestUtilityFunctions:
    """Tests for archetype utility functions."""

    def test_get_archetype_kappa(self) -> None:
        """get_archetype returns Kappa for Kappa subclass."""
        arch = get_archetype(EchoKappa)
        assert arch is Kappa

    def test_get_archetype_lambda(self) -> None:
        """get_archetype returns Lambda for Lambda subclass."""
        arch = get_archetype(EchoLambda)
        assert arch is Lambda

    def test_get_archetype_delta(self) -> None:
        """get_archetype returns Delta for Delta subclass."""
        arch = get_archetype(EchoDelta)
        assert arch is Delta

    def test_get_archetype_plain_agent_returns_none(self) -> None:
        """get_archetype returns None for non-archetype agent."""

        class PlainAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "plain"

            async def invoke(self, x: str) -> str:
                return x

        arch = get_archetype(PlainAgent)
        assert arch is None

    def test_is_archetype_instance_true(self) -> None:
        """is_archetype_instance returns True for archetype instances."""
        agent = EchoKappa()
        assert is_archetype_instance(agent) is True

    def test_is_archetype_instance_false(self) -> None:
        """is_archetype_instance returns False for plain agents."""

        class PlainAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "plain"

            async def invoke(self, x: str) -> str:
                return x

        agent = PlainAgent()
        assert is_archetype_instance(agent) is False


# ═══════════════════════════════════════════════════════════════════════
# Test Class: Edge Cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge case tests for archetypes."""

    def test_archetype_class_itself_has_halo(self) -> None:
        """The archetype class itself has its Halo."""
        # Kappa class (not subclass) should have all four
        assert has_capability(Kappa, StatefulCapability)
        assert has_capability(Kappa, SoulfulCapability)
        assert has_capability(Kappa, ObservableCapability)
        assert has_capability(Kappa, StreamableCapability)

    def test_base_archetype_has_empty_halo(self) -> None:
        """Base Archetype class has no capabilities."""
        halo = get_halo(Archetype)
        assert len(halo) == 0

    def test_type_parameters_preserved(self) -> None:
        """Generic type parameters work correctly."""

        @dataclass
        class Request:
            body: str

        @dataclass
        class Response:
            data: str

        class TypedService(Kappa[Request, Response]):
            @property
            def name(self) -> str:
                return "typed"

            async def invoke(self, req: Request) -> Response:
                return Response(data=req.body.upper())

        # Should still have capabilities
        assert has_capability(TypedService, StatefulCapability)

    @pytest.mark.anyio
    async def test_typed_archetype_invocation(self) -> None:
        """Typed archetype can be invoked with correct types."""

        @dataclass
        class Input:
            value: int

        @dataclass
        class Output:
            result: int

        class Doubler(Lambda[Input, Output]):
            @property
            def name(self) -> str:
                return "doubler"

            async def invoke(self, inp: Input) -> Output:
                return Output(result=inp.value * 2)

        agent = Doubler()
        result = await agent.invoke(Input(value=21))
        assert result.result == 42

    def test_decorated_before_class_definition(self) -> None:
        """Decorators applied in class definition work correctly."""

        # This is the normal way to add capabilities - should work
        @Capability.Soulful(persona="Test")
        class DecoratedLambda(Lambda[str, str]):
            @property
            def name(self) -> str:
                return "decorated"

            async def invoke(self, x: str) -> str:
                return x

        # Should have Lambda's Observable + added Soulful
        assert has_capability(DecoratedLambda, ObservableCapability)
        assert has_capability(DecoratedLambda, SoulfulCapability)

    def test_archetype_subclass_of_archetype_subclass(self) -> None:
        """Can create archetype subclass chain."""

        class FirstLevel(Kappa[str, str]):
            @property
            def name(self) -> str:
                return "first"

            async def invoke(self, x: str) -> str:
                return x

        class SecondLevel(FirstLevel):
            @property
            def name(self) -> str:
                return "second"

        class ThirdLevel(SecondLevel):
            @property
            def name(self) -> str:
                return "third"

        # All should have Kappa's capabilities
        assert len(get_halo(ThirdLevel)) == 4
        assert has_capability(ThirdLevel, StreamableCapability)

    def test_no_cross_contamination_between_archetypes(self) -> None:
        """Modifying one archetype subclass doesn't affect others."""

        @Capability.Soulful(persona="Special")
        class SpecialDelta(Delta[str, str]):
            @property
            def name(self) -> str:
                return "special"

            async def invoke(self, x: str) -> str:
                return x

        class NormalDelta(Delta[str, str]):
            @property
            def name(self) -> str:
                return "normal"

            async def invoke(self, x: str) -> str:
                return x

        # SpecialDelta has Soulful, NormalDelta doesn't
        assert has_capability(SpecialDelta, SoulfulCapability)
        assert not has_capability(NormalDelta, SoulfulCapability)

        # Both still have Delta's base capabilities
        assert has_capability(SpecialDelta, StatefulCapability)
        assert has_capability(NormalDelta, StatefulCapability)
