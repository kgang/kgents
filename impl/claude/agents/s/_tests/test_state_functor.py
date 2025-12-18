"""
Tests for StateFunctor and StatefulAgent.

Tests cover:
- Basic state threading
- Logic function lifting
- State persistence across invocations
- Adapter compatibility
- Agent composition
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agents.poly.types import Agent
from agents.s import (
    MemoryStateBackend,
    StateConfig,
    StatefulAgent,
    StateFunctor,
)

# =============================================================================
# Test Helpers
# =============================================================================


@dataclass
class IdentityAgent(Agent[str, str]):
    """Identity agent for testing."""

    @property
    def name(self) -> str:
        return "Identity"

    async def invoke(self, input_data: str) -> str:
        return input_data


@dataclass
class DoubleAgent(Agent[int, int]):
    """Doubles input."""

    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input_data: int) -> int:
        return input_data * 2


@dataclass
class AddOneAgent(Agent[int, int]):
    """Adds one to input."""

    @property
    def name(self) -> str:
        return "AddOne"

    async def invoke(self, input_data: int) -> int:
        return input_data + 1


# =============================================================================
# StateBackend Tests
# =============================================================================


class TestMemoryStateBackend:
    """Tests for MemoryStateBackend."""

    @pytest.mark.asyncio
    async def test_load_returns_initial(self) -> None:
        """Load returns initial state."""
        backend = MemoryStateBackend(initial={"count": 0})
        state = await backend.load()
        assert state == {"count": 0}

    @pytest.mark.asyncio
    async def test_save_persists_state(self) -> None:
        """Save persists state for subsequent loads."""
        backend = MemoryStateBackend(initial={"count": 0})
        await backend.save({"count": 42})
        state = await backend.load()
        assert state == {"count": 42}

    @pytest.mark.asyncio
    async def test_load_returns_copy(self) -> None:
        """Load returns a deep copy (mutations don't affect stored state)."""
        backend = MemoryStateBackend(initial={"count": 0})
        state = await backend.load()
        state["count"] = 999  # Mutate loaded state

        # Stored state should be unchanged
        state2 = await backend.load()
        assert state2 == {"count": 0}

    @pytest.mark.asyncio
    async def test_save_stores_copy(self) -> None:
        """Save stores a deep copy (external mutations don't affect stored state)."""
        backend = MemoryStateBackend(initial={"count": 0})
        state = {"count": 42}
        await backend.save(state)

        state["count"] = 999  # Mutate after save

        # Stored state should be unchanged
        loaded = await backend.load()
        assert loaded == {"count": 42}

    def test_snapshot_returns_current(self) -> None:
        """Snapshot returns current state synchronously."""
        backend = MemoryStateBackend(initial={"count": 0})
        assert backend.snapshot() == {"count": 0}

    def test_reset_restores_initial(self) -> None:
        """Reset restores initial state."""
        backend = MemoryStateBackend(initial={"count": 0})
        backend._state = {"count": 999}
        backend.reset()
        assert backend.snapshot() == {"count": 0}


# =============================================================================
# StatefulAgent Tests
# =============================================================================


class TestStatefulAgent:
    """Tests for StatefulAgent."""

    @pytest.mark.asyncio
    async def test_basic_state_threading(self) -> None:
        """StatefulAgent threads state through invocations."""

        def counter_logic(input_data: str, state: int) -> tuple[str, int]:
            return f"count={state}", state + 1

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        agent = functor.lift_logic(counter_logic)

        r1 = await agent.invoke("tick")
        r2 = await agent.invoke("tick")
        r3 = await agent.invoke("tick")

        assert r1 == "count=0"
        assert r2 == "count=1"
        assert r3 == "count=2"

    @pytest.mark.asyncio
    async def test_state_persists_in_backend(self) -> None:
        """State changes are persisted to backend."""

        def increment(_, state: int) -> tuple[int, int]:
            return state, state + 1

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        agent = functor.lift_logic(increment)

        await agent.invoke("a")
        await agent.invoke("b")
        await agent.invoke("c")

        # Check backend directly
        assert backend.snapshot() == 3

    @pytest.mark.asyncio
    async def test_async_logic_supported(self) -> None:
        """Async logic functions are supported."""

        async def async_counter(input_data: str, state: int) -> tuple[str, int]:
            return f"async:{state}", state + 1

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        agent = functor.lift_logic(async_counter)

        result = await agent.invoke("tick")
        assert result == "async:0"

    @pytest.mark.asyncio
    async def test_dict_state(self) -> None:
        """Dict state works correctly."""

        def accumulate(item: str, state: dict) -> tuple[list, dict]:
            items = state.get("items", [])
            new_items = items + [item]
            return new_items, {"items": new_items, "count": len(new_items)}

        backend = MemoryStateBackend(initial={"items": [], "count": 0})
        functor = StateFunctor.create(backend=backend)
        agent = functor.lift_logic(accumulate)

        r1 = await agent.invoke("a")
        r2 = await agent.invoke("b")

        assert r1 == ["a"]
        assert r2 == ["a", "b"]
        assert backend.snapshot() == {"items": ["a", "b"], "count": 2}

    @pytest.mark.asyncio
    async def test_name_property(self) -> None:
        """StatefulAgent has descriptive name."""

        def logic(x: int, s: int) -> tuple[int, int]:
            return x, s

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        agent = functor.lift_logic(logic)

        assert "Stateful" in agent.name
        assert "Logic" in agent.name


# =============================================================================
# StateFunctor Tests
# =============================================================================


class TestStateFunctor:
    """Tests for StateFunctor."""

    def test_registered_in_functor_registry(self) -> None:
        """StateFunctor is registered in FunctorRegistry."""
        from agents.a.functor import FunctorRegistry

        functor = FunctorRegistry.get("State")
        assert functor is not None
        assert functor.__name__ == "StateFunctor"

    @pytest.mark.asyncio
    async def test_lift_requires_backend(self) -> None:
        """lift() raises if no backend provided."""
        with pytest.raises(ValueError, match="requires a backend"):
            StateFunctor.lift(IdentityAgent())

    @pytest.mark.asyncio
    async def test_lift_with_backend(self) -> None:
        """lift() works with backend."""
        backend = MemoryStateBackend(initial=0)
        stateful = StateFunctor.lift(IdentityAgent(), backend=backend)

        assert isinstance(stateful, StatefulAgent)
        result = await stateful.invoke("hello")
        # IdentityAgent just returns input unchanged, so StatefulAgent
        # detects non-tuple output and returns it directly
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_lift_logic_requires_instance_backend(self) -> None:
        """lift_logic() requires backend on instance."""
        functor = StateFunctor()
        with pytest.raises(ValueError, match="requires backend"):
            functor.lift_logic(lambda x, s: (x, s))

    @pytest.mark.asyncio
    async def test_create_factory(self) -> None:
        """create() returns configured instance."""
        backend = MemoryStateBackend(initial=42)
        functor = StateFunctor.create(backend=backend)

        def echo(x: str, s: int) -> tuple[str, int]:
            return f"{x}:{s}", s

        agent = functor.lift_logic(echo)
        result = await agent.invoke("test")
        assert result == "test:42"

    def test_unlift_extracts_inner(self) -> None:
        """unlift() extracts the inner agent."""
        backend = MemoryStateBackend(initial=0)

        def logic(x: int, s: int) -> tuple[int, int]:
            return x, s

        functor = StateFunctor.create(backend=backend)
        stateful = functor.lift_logic(logic)

        inner = StateFunctor.unlift(stateful)
        assert inner is stateful.inner

    def test_pure_returns_tuple(self) -> None:
        """pure() embeds value as (value, None)."""
        result = StateFunctor.pure(42)
        assert result == (42, None)


# =============================================================================
# Composition Tests
# =============================================================================


class TestStatefulAgentComposition:
    """Tests for StatefulAgent composition."""

    @pytest.mark.asyncio
    async def test_stateful_agents_compose(self) -> None:
        """StatefulAgents can be created and used sequentially."""

        def counter(x: int, s: int) -> tuple[int, int]:
            return s, s + 1

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        stateful = functor.lift_logic(counter)

        # Sequential invocations (state threads through)
        r1 = await stateful.invoke(0)  # returns 0, state becomes 1
        r2 = await stateful.invoke(0)  # returns 1, state becomes 2
        r3 = await stateful.invoke(0)  # returns 2, state becomes 3

        assert r1 == 0
        assert r2 == 1
        assert r3 == 2

    @pytest.mark.asyncio
    async def test_stateful_with_transform(self) -> None:
        """StatefulAgent output can be transformed."""

        def counter(x: int, s: int) -> tuple[int, int]:
            return s, s + 1

        backend = MemoryStateBackend(initial=0)
        functor = StateFunctor.create(backend=backend)
        stateful = functor.lift_logic(counter)

        # Get result and transform externally
        r1 = await stateful.invoke(0)
        assert r1 * 2 == 0  # 0 * 2 = 0

        r2 = await stateful.invoke(0)
        assert r2 * 2 == 2  # 1 * 2 = 2


# =============================================================================
# Config Tests
# =============================================================================


class TestStateConfig:
    """Tests for StateConfig."""

    def test_default_config(self) -> None:
        """Default config has expected values."""
        config = StateConfig()
        assert config.auto_save is True
        assert config.auto_load is True
        assert config.namespace == "default"

    def test_with_namespace(self) -> None:
        """with_namespace creates copy with new namespace."""
        config = StateConfig(auto_save=False)
        new_config = config.with_namespace("custom")

        assert new_config.namespace == "custom"
        assert new_config.auto_save is False  # Preserved
        assert config.namespace == "default"  # Original unchanged

    @pytest.mark.asyncio
    async def test_auto_save_false_skips_save(self) -> None:
        """auto_save=False skips automatic save."""

        def increment(_, state: int) -> tuple[int, int]:
            return state, state + 1

        backend = MemoryStateBackend(initial=0)
        config = StateConfig(auto_save=False)
        functor = StateFunctor.create(backend=backend, config=config)
        agent = functor.lift_logic(increment)

        # Multiple invokes
        await agent.invoke("a")
        await agent.invoke("b")
        await agent.invoke("c")

        # State not persisted (each invoke sees initial state)
        # Actually, auto_save=False means save() is not called,
        # but internal state of StatefulAgent may still track
        # Let's check the backend directly
        assert backend.snapshot() == 0  # Never saved
