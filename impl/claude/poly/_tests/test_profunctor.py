"""
Tests for LogosProfunctor - the bridge between intent and implementation.

These tests verify:
- Intent resolution
- Interface lifting
- Different Logos modes (Real, Dream, Test)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Type

import pytest

from ..interface import (
    BasePolyInterface,
    HouseState,
    ObserveHouse,
    WorldHouse,
)
from ..profunctor import (
    DictResolver,
    InterfaceMorphism,
    LogosComposition,
    LogosProfunctor,
    SyncGround,
    WrappingLifter,
    create_dream_logos,
    create_real_logos,
    create_test_logos,
)


class TestDictResolver:
    """Tests for DictResolver."""

    def test_resolve_registered_intent(self) -> None:
        """DictResolver resolves registered intents."""
        house = WorldHouse()
        resolver = DictResolver(registry={"world.house": house})

        resolved = resolver.resolve("world.house")

        assert resolved is house

    def test_resolve_unregistered_raises(self) -> None:
        """DictResolver raises for unregistered intents."""
        resolver = DictResolver()

        with pytest.raises(KeyError, match="world.unknown"):
            resolver.resolve("world.unknown")

    def test_resolve_with_fallback(self) -> None:
        """DictResolver uses fallback for unregistered intents."""
        fallback = WorldHouse()
        resolver = DictResolver(fallback=fallback)

        resolved = resolver.resolve("anything")

        assert resolved is fallback

    def test_can_resolve(self) -> None:
        """can_resolve() returns True for registered intents."""
        house = WorldHouse()
        resolver = DictResolver(registry={"world.house": house})

        assert resolver.can_resolve("world.house")
        assert not resolver.can_resolve("world.unknown")

    def test_register(self) -> None:
        """register() adds interfaces."""
        resolver = DictResolver()
        house = WorldHouse()

        resolver.register("world.house", house)

        assert resolver.can_resolve("world.house")
        assert resolver.resolve("world.house") is house


class TestWrappingLifter:
    """Tests for WrappingLifter."""

    def test_lift_creates_morphism(self) -> None:
        """WrappingLifter creates InterfaceMorphism."""
        lifter = WrappingLifter()
        house = WorldHouse()

        morphism = lifter.lift(house)

        assert isinstance(morphism, InterfaceMorphism)

    def test_lifted_morphism_has_interface(self) -> None:
        """Lifted morphism contains the interface."""
        lifter = WrappingLifter()
        house = WorldHouse()

        morphism = lifter.lift(house)

        assert isinstance(morphism, InterfaceMorphism)
        assert morphism.interface is house


class TestInterfaceMorphism:
    """Tests for InterfaceMorphism."""

    def test_apply_uses_wrapped_interface(self) -> None:
        """InterfaceMorphism.apply() uses wrapped interface."""
        house = WorldHouse()
        morphism = InterfaceMorphism(interface=house)

        new_state, output = morphism.apply(
            house,  # This is ignored
            ObserveHouse("test", "view"),
        )

        assert new_state.observation_count == 1

    def test_on_states_returns_interface_state(self) -> None:
        """on_states() returns the wrapped interface's state."""
        house = WorldHouse()
        house.state = HouseState(observation_count=5)
        morphism = InterfaceMorphism(interface=house)

        result = morphism.on_states(HouseState())  # Input ignored

        assert result.observation_count == 5


class TestSyncGround:
    """Tests for SyncGround."""

    @pytest.mark.asyncio
    async def test_execute_calls_morphism(self) -> None:
        """SyncGround executes morphism."""
        ground = SyncGround()
        house = WorldHouse()
        morphism = InterfaceMorphism(interface=house)

        result = await ground.execute(morphism, ObserveHouse("test", "view"))

        assert result.state_delta["observed"] is True

    @pytest.mark.asyncio
    async def test_execute_without_interface_raises(self) -> None:
        """SyncGround raises if morphism lacks interface."""
        from ..morphism import IdentityMorphism

        ground = SyncGround()
        morphism: IdentityMorphism[Any, Any] = IdentityMorphism()  # No interface attr

        with pytest.raises(ValueError, match="InterfaceMorphism"):
            await ground.execute(morphism, ObserveHouse("test", "view"))


class TestLogosComposition:
    """Tests for LogosComposition."""

    def test_bridge_uses_resolver(self) -> None:
        """bridge() uses resolver to get interface."""
        house = WorldHouse()
        logos = LogosComposition(
            resolver=DictResolver(registry={"world.house": house}),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        resolved = logos.bridge("world.house")

        assert resolved is house

    def test_lift_uses_lifter(self) -> None:
        """lift() uses lifter to create morphism."""
        house = WorldHouse()
        logos = LogosComposition(
            resolver=DictResolver(),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        morphism = logos.lift(house)

        assert isinstance(morphism, InterfaceMorphism)

    @pytest.mark.asyncio
    async def test_execute_uses_ground(self) -> None:
        """execute() uses ground."""
        house = WorldHouse()
        logos = LogosComposition(
            resolver=DictResolver(),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        morphism = logos.lift(house)
        result = await logos.execute(morphism, ObserveHouse("test", "view"))

        assert result.state_delta["observed"] is True

    def test_pipeline_single_intent(self) -> None:
        """pipeline() with single intent."""
        house = WorldHouse()
        logos = LogosComposition(
            resolver=DictResolver(registry={"world.house": house}),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        pipeline = logos.pipeline("world.house")

        assert isinstance(pipeline, InterfaceMorphism)

    def test_pipeline_multiple_intents(self) -> None:
        """pipeline() with multiple intents."""
        house1 = WorldHouse()
        house2 = WorldHouse()
        logos = LogosComposition(
            resolver=DictResolver(
                registry={
                    "step1": house1,
                    "step2": house2,
                }
            ),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        pipeline = logos.pipeline("step1", "step2")

        # Pipeline is composed morphism
        from ..morphism import ComposedMorphism

        assert isinstance(pipeline, ComposedMorphism)

    def test_pipeline_empty(self) -> None:
        """pipeline() with no intents returns identity."""
        logos = LogosComposition(
            resolver=DictResolver(),
            lifter=WrappingLifter(),
            ground=SyncGround(),
        )

        pipeline = logos.pipeline()

        from ..morphism import IdentityMorphism

        assert isinstance(pipeline, IdentityMorphism)


class TestCreateRealLogos:
    """Tests for create_real_logos factory."""

    def test_creates_logos_composition(self) -> None:
        """create_real_logos() creates LogosComposition."""
        logos = create_real_logos()

        assert isinstance(logos, LogosComposition)

    def test_with_registry(self) -> None:
        """create_real_logos() accepts initial registry."""
        house = WorldHouse()
        logos = create_real_logos(registry={"world.house": house})

        assert logos.bridge("world.house") is house


class TestCreateTestLogos:
    """Tests for create_test_logos factory."""

    def test_creates_logos_composition(self) -> None:
        """create_test_logos() creates LogosComposition."""
        logos = create_test_logos()

        assert isinstance(logos, LogosComposition)

    def test_with_mocks(self) -> None:
        """create_test_logos() accepts mock interfaces."""

        @dataclass
        class MockState:
            value: str = "mock"

        @dataclass
        class MockInterface(BasePolyInterface[MockState, Any, Any]):
            state: MockState = field(default_factory=MockState)

            def scope(self, s: MockState) -> Type[Any]:
                return object

            def dynamics(self, s: MockState, input: Any) -> tuple[MockState, Any]:
                return MockState("observed"), {"mock": True}

        mock = MockInterface()
        logos = create_test_logos(mocks={"world.house": mock})

        resolved = logos.bridge("world.house")
        assert resolved is mock


class TestCreateDreamLogos:
    """Tests for create_dream_logos factory."""

    def test_creates_logos_composition(self) -> None:
        """create_dream_logos() creates LogosComposition."""

        def hallucinate(intent: str) -> WorldHouse:
            return WorldHouse()

        logos = create_dream_logos(hallucinator=hallucinate)

        assert isinstance(logos, LogosComposition)

    def test_can_resolve_anything(self) -> None:
        """Dream logos can resolve any intent."""

        def hallucinate(intent: str) -> WorldHouse:
            return WorldHouse()

        logos = create_dream_logos(hallucinator=hallucinate)

        # These all work
        logos.bridge("anything")
        logos.bridge("world.house")
        logos.bridge("nonexistent.path")

    def test_hallucinator_called_with_intent(self) -> None:
        """Hallucinator receives the intent string."""
        received_intents: list[str] = []

        def hallucinate(intent: str) -> WorldHouse:
            received_intents.append(intent)
            return WorldHouse()

        logos = create_dream_logos(hallucinator=hallucinate)

        logos.bridge("test.intent")

        assert "test.intent" in received_intents


class TestLogosIntegration:
    """Integration tests for Logos usage patterns."""

    def test_full_workflow(self) -> None:
        """Complete workflow: resolve, lift, compose."""
        house = WorldHouse()
        logos = create_real_logos(registry={"world.house": house})

        # Resolve
        interface = logos.bridge("world.house")

        # Lift
        morphism = logos.lift(interface)

        # Apply
        new_state, output = morphism.apply(interface, ObserveHouse("test", "view"))

        assert new_state.observation_count == 1

    @pytest.mark.asyncio
    async def test_execute_workflow(self) -> None:
        """Execute workflow."""
        house = WorldHouse()
        logos = create_real_logos(registry={"world.house": house})

        interface = logos.bridge("world.house")
        morphism = logos.lift(interface)
        result = await logos.execute(morphism, ObserveHouse("architect", "view"))

        assert "observed" in result.state_delta

    def test_pipeline_workflow(self) -> None:
        """Pipeline workflow."""
        house1 = WorldHouse()
        house2 = WorldHouse()

        logos = create_real_logos(
            registry={
                "world.house.observe": house1,
                "world.house.analyze": house2,
            }
        )

        pipeline = logos.pipeline(
            "world.house.observe",
            "world.house.analyze",
        )

        # Pipeline created successfully
        from ..morphism import ComposedMorphism

        assert isinstance(pipeline, ComposedMorphism)
