"""
Tests for the D-gent Polynomial Agent.

Tests verify:
1. MemoryPhase state machine
2. Direction validation at each phase
3. Load/store operations
4. Query and forget operations
5. History tracking
"""

import pytest
from agents.d.polynomial import (
    MEMORY_POLYNOMIAL,
    ForgetCommand,
    LoadCommand,
    MemoryPhase,
    MemoryPolynomialAgent,
    MemoryResponse,
    QueryCommand,
    StoreCommand,
    memory_directions,
    memory_transition,
    reset_memory,
)

# =============================================================================
# Setup/Teardown
# =============================================================================


@pytest.fixture(autouse=True)
def clean_memory():
    """Reset memory before each test."""
    reset_memory()
    yield
    reset_memory()


# =============================================================================
# State Tests
# =============================================================================


class TestMemoryPhase:
    """Test the MemoryPhase enum."""

    def test_all_phases_defined(self) -> None:
        """All six memory phases are defined."""
        assert MemoryPhase.IDLE
        assert MemoryPhase.LOADING
        assert MemoryPhase.STORING
        assert MemoryPhase.QUERYING
        assert MemoryPhase.STREAMING
        assert MemoryPhase.FORGETTING

    def test_phases_are_unique(self) -> None:
        """Each phase has a unique value."""
        phases = list(MemoryPhase)
        values = [p.value for p in phases]
        assert len(values) == len(set(values))


# =============================================================================
# Direction Tests
# =============================================================================


class TestMemoryDirections:
    """Test phase-dependent direction validation."""

    def test_idle_accepts_all_commands(self) -> None:
        """IDLE phase accepts all command types."""
        dirs = memory_directions(MemoryPhase.IDLE)
        assert LoadCommand in dirs
        assert StoreCommand in dirs
        assert QueryCommand in dirs
        assert ForgetCommand in dirs

    def test_loading_accepts_load_command(self) -> None:
        """LOADING phase accepts LoadCommand."""
        dirs = memory_directions(MemoryPhase.LOADING)
        assert LoadCommand in dirs or type(LoadCommand) in dirs

    def test_storing_accepts_store_command(self) -> None:
        """STORING phase accepts StoreCommand."""
        dirs = memory_directions(MemoryPhase.STORING)
        assert StoreCommand in dirs or type(StoreCommand) in dirs


# =============================================================================
# Transition Tests
# =============================================================================


class TestMemoryTransition:
    """Test the memory state transition function."""

    def test_idle_routes_to_loading(self) -> None:
        """IDLE → LOADING on LoadCommand."""
        cmd = LoadCommand(key="test")
        new_phase, output = memory_transition(MemoryPhase.IDLE, cmd)

        assert new_phase == MemoryPhase.LOADING
        assert isinstance(output, LoadCommand)

    def test_idle_routes_to_storing(self) -> None:
        """IDLE → STORING on StoreCommand."""
        cmd = StoreCommand(state={"key": "value"})
        new_phase, output = memory_transition(MemoryPhase.IDLE, cmd)

        assert new_phase == MemoryPhase.STORING
        assert isinstance(output, StoreCommand)

    def test_storing_returns_to_idle(self) -> None:
        """STORING → IDLE after store."""
        cmd = StoreCommand(state="test_data")
        new_phase, output = memory_transition(MemoryPhase.STORING, cmd)

        assert new_phase == MemoryPhase.IDLE
        assert isinstance(output, MemoryResponse)
        assert output.success is True

    def test_loading_returns_to_idle(self) -> None:
        """LOADING → IDLE after load."""
        # First store something
        memory_transition(MemoryPhase.STORING, StoreCommand(state="stored"))

        # Then load
        new_phase, output = memory_transition(MemoryPhase.LOADING, LoadCommand())

        assert new_phase == MemoryPhase.IDLE
        assert isinstance(output, MemoryResponse)
        assert output.success is True

    def test_forgetting_clears_state(self) -> None:
        """FORGETTING clears specified state."""
        # Store something
        memory_transition(MemoryPhase.STORING, StoreCommand(state="to_forget", key="k"))

        # Forget it
        new_phase, output = memory_transition(
            MemoryPhase.FORGETTING, ForgetCommand(key="k")
        )

        assert new_phase == MemoryPhase.IDLE
        assert output.success is True

    def test_streaming_stays_in_streaming(self) -> None:
        """STREAMING stays in STREAMING after processing event."""
        event = {"type": "event", "data": "test"}
        new_phase, output = memory_transition(MemoryPhase.STREAMING, event)

        assert new_phase == MemoryPhase.STREAMING
        assert output.success is True


# =============================================================================
# Polynomial Agent Tests
# =============================================================================


class TestMemoryPolynomial:
    """Test the MEMORY_POLYNOMIAL agent."""

    def test_has_all_positions(self) -> None:
        """Agent has all six phases as positions."""
        assert len(MEMORY_POLYNOMIAL.positions) == 6
        for phase in MemoryPhase:
            assert phase in MEMORY_POLYNOMIAL.positions

    def test_invoke_store(self) -> None:
        """invoke() works for store operation."""
        # Route through IDLE
        _, cmd = MEMORY_POLYNOMIAL.invoke(MemoryPhase.IDLE, StoreCommand(state="test"))
        _, response = MEMORY_POLYNOMIAL.invoke(MemoryPhase.STORING, cmd)

        assert isinstance(response, MemoryResponse)
        assert response.success is True


# =============================================================================
# Wrapper Tests
# =============================================================================


class TestMemoryPolynomialAgentWrapper:
    """Test the backwards-compatible MemoryPolynomialAgent wrapper."""

    def test_initial_phase_is_idle(self) -> None:
        """Agent starts in IDLE phase."""
        agent = MemoryPolynomialAgent()
        assert agent.phase == MemoryPhase.IDLE

    @pytest.mark.asyncio
    async def test_store_and_load(self) -> None:
        """Store then load returns stored state."""
        agent = MemoryPolynomialAgent()

        store_response = await agent.store({"count": 42})
        assert store_response.success is True

        load_response = await agent.load()
        assert load_response.success is True
        assert load_response.state == {"count": 42}

    @pytest.mark.asyncio
    async def test_store_with_key(self) -> None:
        """Store with key creates named state."""
        agent = MemoryPolynomialAgent()

        await agent.store("value1", key="key1")
        await agent.store("value2", key="key2")

        r1 = await agent.load(key="key1")
        r2 = await agent.load(key="key2")

        assert r1.state == "value1"
        assert r2.state == "value2"

    @pytest.mark.asyncio
    async def test_query_returns_all_state(self) -> None:
        """Query returns all stored state."""
        agent = MemoryPolynomialAgent()

        await agent.store("a", key="k1")
        await agent.store("b", key="k2")

        response = await agent.query()
        assert response.success is True
        assert isinstance(response.state, dict)
        assert "k1" in response.state
        assert "k2" in response.state

    @pytest.mark.asyncio
    async def test_forget_key(self) -> None:
        """Forget removes specific key."""
        agent = MemoryPolynomialAgent()

        await agent.store("value", key="to_forget")
        await agent.forget(key="to_forget")

        response = await agent.load(key="to_forget")
        assert response.state is None

    @pytest.mark.asyncio
    async def test_forget_all(self) -> None:
        """Forget all clears all state."""
        agent = MemoryPolynomialAgent()

        await agent.store("a", key="k1")
        await agent.store("b", key="k2")
        await agent.forget(all=True)

        response = await agent.query()
        assert response.state == {}

    @pytest.mark.asyncio
    async def test_history_tracking(self) -> None:
        """History tracks previous states."""
        agent = MemoryPolynomialAgent()

        await agent.store(1)
        await agent.store(2)
        await agent.store(3)

        history = await agent.history()
        assert len(history) >= 2
        assert 1 in history
        assert 2 in history

    @pytest.mark.asyncio
    async def test_stream_events(self) -> None:
        """Stream processes events and tracks them."""
        agent = MemoryPolynomialAgent()

        r1 = await agent.stream({"event": 1})
        r2 = await agent.stream({"event": 2})

        assert r1.success is True
        assert r2.success is True
        assert agent.phase == MemoryPhase.STREAMING


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_load_with_default(self) -> None:
        """Load returns default if key not found."""
        agent = MemoryPolynomialAgent()

        response = await agent.load(key="nonexistent", default="default_value")
        assert response.state == "default_value"

    @pytest.mark.asyncio
    async def test_store_overwrites(self) -> None:
        """Storing same key overwrites and tracks history."""
        agent = MemoryPolynomialAgent()

        await agent.store("first")
        await agent.store("second")

        response = await agent.load()
        assert response.state == "second"
        assert "first" in response.history

    @pytest.mark.asyncio
    async def test_initial_state_preserved(self) -> None:
        """Initial state is preserved if provided."""
        agent = MemoryPolynomialAgent(initial_state={"initial": True})

        response = await agent.load()
        assert response.state == {"initial": True}


# =============================================================================
# Instance Isolation Tests
# =============================================================================


class TestInstanceIsolation:
    """Test that agent instances have isolated memory state."""

    @pytest.mark.asyncio
    async def test_agents_have_isolated_state(self) -> None:
        """Two agents should not share state."""
        agent1 = MemoryPolynomialAgent()
        agent2 = MemoryPolynomialAgent()

        # Store in agent1
        await agent1.store("agent1_data", key="shared_key")

        # agent2 should not see agent1's data
        response = await agent2.load(key="shared_key")
        assert response.state is None

    @pytest.mark.asyncio
    async def test_agents_have_isolated_history(self) -> None:
        """Two agents should not share history."""
        agent1 = MemoryPolynomialAgent()
        agent2 = MemoryPolynomialAgent()

        # Build history in agent1
        await agent1.store(1)
        await agent1.store(2)
        await agent1.store(3)

        # agent2 should have empty history
        history = await agent2.history()
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_initial_state_is_isolated(self) -> None:
        """Initial states should be isolated between instances."""
        agent1 = MemoryPolynomialAgent(initial_state="agent1_initial")
        agent2 = MemoryPolynomialAgent(initial_state="agent2_initial")

        r1 = await agent1.load()
        r2 = await agent2.load()

        assert r1.state == "agent1_initial"
        assert r2.state == "agent2_initial"

    @pytest.mark.asyncio
    async def test_forget_is_isolated(self) -> None:
        """Forgetting in one agent doesn't affect another."""
        agent1 = MemoryPolynomialAgent()
        agent2 = MemoryPolynomialAgent()

        await agent1.store("data1")
        await agent2.store("data2")

        # Forget all in agent1
        await agent1.forget(all=True)

        # agent2 should still have its data
        response = await agent2.load()
        assert response.state == "data2"

    @pytest.mark.asyncio
    async def test_streaming_is_isolated(self) -> None:
        """Streaming history should be isolated."""
        agent1 = MemoryPolynomialAgent()
        agent2 = MemoryPolynomialAgent()

        await agent1.stream({"event": "agent1"})
        await agent1.stream({"event": "agent1_2"})

        # Start streaming in agent2
        r2 = await agent2.stream({"event": "agent2"})

        # agent2's history should only contain its own event
        assert len(r2.history) == 1
        assert r2.history[0] == {"event": "agent2"}
