"""
Tests for Bindings: AGENTESE path connections.

Wave 5 - Reality Wiring: Binding tests
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest
from agents.i.reactive.wiring.bindings import (
    AGENTESEBinding,
    BindingConfig,
    BindingMode,
    BindingSpec,
    PathBinding,
    _extract_status,
    apply_binding_spec,
    create_binding,
)
from agents.i.reactive.wiring.subscriptions import EventBus, EventType, create_event_bus

# === Mock Types ===


@dataclass
class MockRenderable:
    """Mock renderable result."""

    content: str
    metadata: dict[str, Any]


class MockLogos:
    """Mock Logos for testing."""

    def __init__(self) -> None:
        self._paths: dict[str, Any] = {}
        self._invoke_count: int = 0

    def set_path_result(self, path: str, result: Any) -> None:
        """Set what invoke() returns for a path."""
        self._paths[path] = result

    async def invoke(self, path: str, observer: Any, **kwargs: Any) -> Any:
        """Mock invoke that returns configured results."""
        self._invoke_count += 1
        return self._paths.get(path, {"path": path, "status": "mock"})


class MockUmwelt:
    """Mock Umwelt for testing."""

    id: str = "mock-observer"
    dna: Any = None


# === Tests ===


class TestBindingConfig:
    """Tests for BindingConfig."""

    def test_binding_config_defaults(self) -> None:
        """BindingConfig should have sensible defaults."""
        config = BindingConfig(path_pattern="self.soul")

        assert config.path_pattern == "self.soul"
        assert config.poll_interval_ms == 1000.0
        assert config.mode == BindingMode.HYBRID
        assert config.transform == "auto"
        assert config.enabled is True

    def test_binding_config_custom(self) -> None:
        """BindingConfig should accept custom values."""
        config = BindingConfig(
            path_pattern="world.agents",
            poll_interval_ms=500.0,
            mode=BindingMode.POLL,
            transform="agent",
            enabled=False,
        )

        assert config.poll_interval_ms == 500.0
        assert config.mode == BindingMode.POLL
        assert config.transform == "agent"
        assert config.enabled is False


class TestPathBinding:
    """Tests for PathBinding."""

    @pytest.mark.asyncio
    async def test_path_binding_create(self) -> None:
        """PathBinding.create should initialize properly."""
        logos = MockLogos()
        observer = MockUmwelt()

        binding = PathBinding.create("self.soul.manifest", logos, observer)  # type: ignore[arg-type]

        assert binding.path == "self.soul.manifest"
        assert binding.signal.value is None
        assert binding.is_running is False

    @pytest.mark.asyncio
    async def test_path_binding_poll_once(self) -> None:
        """poll_once() should invoke path and update signal."""
        logos = MockLogos()
        logos.set_path_result("self.soul.manifest", {"mode": "reflect"})
        observer = MockUmwelt()

        binding = PathBinding.create("self.soul.manifest", logos, observer)  # type: ignore[arg-type]

        result = await binding.poll_once()

        assert result == {"mode": "reflect"}
        assert binding.signal.value == {"mode": "reflect"}
        assert binding.poll_count == 1

    @pytest.mark.asyncio
    async def test_path_binding_poll_error_handling(self) -> None:
        """poll_once() should handle errors gracefully."""

        class ErrorLogos:
            async def invoke(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("Network error")

        binding = PathBinding.create("self.soul.manifest", ErrorLogos(), MockUmwelt())  # type: ignore[arg-type]

        result = await binding.poll_once()

        assert result is None
        assert binding.signal.value is None

    @pytest.mark.asyncio
    async def test_path_binding_start_stop(self) -> None:
        """start() and stop() should control polling."""
        logos = MockLogos()
        observer = MockUmwelt()
        config = BindingConfig(path_pattern="test", poll_interval_ms=10.0)

        binding = PathBinding.create("test", logos, observer, config)  # type: ignore[arg-type]

        await binding.start()
        assert binding.is_running is True

        # Let it poll a couple times
        await asyncio.sleep(0.03)

        await binding.stop()
        assert binding.is_running is False

        # Should have polled at least once
        assert binding.poll_count >= 1


class TestAGENTESEBinding:
    """Tests for AGENTESEBinding."""

    def test_agentese_binding_creation(self) -> None:
        """AGENTESEBinding should initialize properly."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(
            logos=logos,  # type: ignore[arg-type]
            observer=observer,  # type: ignore[arg-type]
            event_bus=event_bus,
        )

        assert binding.binding_count == 0
        assert binding.running_count == 0

    def test_bind_creates_path_binding(self) -> None:
        """bind() should create and store PathBinding."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]  # type: ignore[arg-type]
        path_binding = binding.bind("self.test.path")

        assert binding.binding_count == 1
        assert path_binding.path == "self.test.path"

    def test_bind_soul(self) -> None:
        """bind_soul() should create soul binding."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.bind_soul("self.soul", poll_interval_ms=100.0)

        assert binding.binding_count == 1
        assert binding._soul_path == "self.soul.manifest"

    def test_bind_agents(self) -> None:
        """bind_agents() should create agents binding."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.bind_agents("world.agents", poll_interval_ms=200.0)

        assert binding.binding_count == 1
        assert binding._agents_path == "world.agents.manifest"

    def test_push_yield(self) -> None:
        """push_yield() should add yield and emit event."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()
        received_events: list[Any] = []

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        event_bus.subscribe(
            EventType.YIELD_CREATED, lambda e: received_events.append(e)
        )

        binding.push_yield({"content": "test yield"})

        assert len(binding._yields) == 1
        assert len(received_events) == 1
        assert received_events[0].payload == {"content": "test yield"}

    def test_push_yield_max_limit(self) -> None:
        """push_yield() should respect max yields limit."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding._max_yields = 5

        for i in range(10):
            binding.push_yield({"content": f"yield-{i}"})

        assert len(binding._yields) == 5
        # Newest should be first
        assert binding._yields[0]["content"] == "yield-9"

    def test_clear_yields(self) -> None:
        """clear_yields() should remove all yields."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.push_yield({"content": "test"})
        binding.clear_yields()

        assert len(binding._yields) == 0

    @pytest.mark.asyncio
    async def test_poll_all(self) -> None:
        """poll_all() should poll all bindings."""
        logos = MockLogos()
        logos.set_path_result("path1", {"data": 1})
        logos.set_path_result("path2", {"data": 2})
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.bind("path1")
        binding.bind("path2")

        results = await binding.poll_all()

        assert results["path1"] == {"data": 1}
        assert results["path2"] == {"data": 2}

    @pytest.mark.asyncio
    async def test_start_stop_all(self) -> None:
        """start_all() and stop_all() should control all bindings."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        config = BindingConfig(path_pattern="test", poll_interval_ms=10.0)
        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.bind("path1", config)
        binding.bind("path2", config)

        await binding.start_all()
        assert binding.running_count == 2

        await binding.stop_all()
        assert binding.running_count == 0

    def test_set_entropy_and_seed(self) -> None:
        """set_entropy() and set_seed() should update config."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]

        binding.set_entropy(0.75)
        assert binding._entropy == 0.75

        binding.set_seed(999)
        assert binding._seed == 999

    def test_to_dashboard_state(self) -> None:
        """to_dashboard_state() should create DashboardScreenState."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = AGENTESEBinding(logos=logos, observer=observer, event_bus=event_bus)  # type: ignore[arg-type]
        binding.push_yield({"content": "test"})

        state = binding.to_dashboard_state(t=100.0, width=80, height=24)

        assert state.t == 100.0
        assert state.width == 80
        assert state.height == 24
        assert len(state.yields) == 1


class TestExtractStatus:
    """Tests for _extract_status helper."""

    def test_extract_from_status(self) -> None:
        """Should extract from 'status' key."""
        assert _extract_status({"status": "active"}) == "active"

    def test_extract_from_phase(self) -> None:
        """Should extract from 'phase' key."""
        assert _extract_status({"phase": "idle"}) == "idle"

    def test_extract_from_mode_challenge(self) -> None:
        """Should map challenge mode to active."""
        assert _extract_status({"mode": "challenge"}) == "active"

    def test_extract_from_mode_reflect(self) -> None:
        """Should map reflect mode to thinking."""
        assert _extract_status({"mode": "reflect"}) == "thinking"

    def test_extract_default(self) -> None:
        """Should default to idle."""
        assert _extract_status({}) == "idle"


class TestCreateBinding:
    """Tests for create_binding factory function."""

    def test_create_binding_with_event_bus(self) -> None:
        """create_binding() should use provided event_bus."""
        logos = MockLogos()
        observer = MockUmwelt()
        event_bus = create_event_bus()

        binding = create_binding(logos, observer, event_bus)  # type: ignore[arg-type]

        assert binding.event_bus is event_bus

    def test_create_binding_creates_event_bus(self) -> None:
        """create_binding() should create event_bus if not provided."""
        logos = MockLogos()
        observer = MockUmwelt()

        binding = create_binding(logos, observer)  # type: ignore[arg-type]

        assert binding.event_bus is not None


class TestBindingSpec:
    """Tests for BindingSpec."""

    def test_binding_spec_defaults(self) -> None:
        """BindingSpec should have sensible defaults."""
        spec = BindingSpec()

        assert spec.soul_path is None
        assert spec.agents_path is None
        assert spec.yield_patterns == []
        assert spec.poll_interval_ms == 500.0
        assert spec.entropy == 0.0
        assert spec.seed == 42

    def test_binding_spec_custom(self) -> None:
        """BindingSpec should accept custom values."""
        spec = BindingSpec(
            soul_path="self.soul",
            agents_path="world.agents",
            poll_interval_ms=100.0,
            entropy=0.5,
            seed=123,
        )

        assert spec.soul_path == "self.soul"
        assert spec.agents_path == "world.agents"
        assert spec.poll_interval_ms == 100.0
        assert spec.entropy == 0.5
        assert spec.seed == 123


class TestApplyBindingSpec:
    """Tests for apply_binding_spec function."""

    @pytest.mark.asyncio
    async def test_apply_binding_spec(self) -> None:
        """apply_binding_spec() should configure and start bindings."""
        logos = MockLogos()
        observer = MockUmwelt()

        spec = BindingSpec(
            soul_path="self.soul",
            agents_path="world.agents",
            poll_interval_ms=100.0,
            entropy=0.3,
            seed=999,
        )

        binding = await apply_binding_spec(spec, logos, observer)  # type: ignore[arg-type]

        assert binding._entropy == 0.3
        assert binding._seed == 999
        assert binding.binding_count == 2  # soul + agents
        assert binding.running_count == 2  # Both should be started

        await binding.stop_all()

    @pytest.mark.asyncio
    async def test_apply_binding_spec_minimal(self) -> None:
        """apply_binding_spec() should work with minimal spec."""
        logos = MockLogos()
        observer = MockUmwelt()

        spec = BindingSpec()  # All defaults

        binding = await apply_binding_spec(spec, logos, observer)  # type: ignore[arg-type]

        assert binding.binding_count == 0  # No paths specified

        await binding.stop_all()
