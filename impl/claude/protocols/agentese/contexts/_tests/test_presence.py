"""
Tests for self.presence - Agent Presence and Cursor Broadcasting.

CLI v7 Phase 5A: Wiring existing infrastructure.

Tests:
- Demo mode starts and stops correctly
- Cursor state transitions work
- Stream yields proper SSE-compatible events
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from protocols.agentese.contexts.self_presence import (
    DEMO_AGENTS,
    PRESENCE_AFFORDANCES,
    PresenceNode,
    _demo_tasks,
)
from services.conductor.presence import (
    CursorState,
    PresenceChannel,
    get_presence_channel,
)

# =============================================================================
# Fixtures
# =============================================================================


@dataclass
class MockObserver:
    """Minimal observer for testing."""

    archetype: str = "developer"
    capabilities: frozenset[str] = frozenset()

    @property
    def dna(self) -> Any:
        return self


@pytest.fixture
def observer() -> MockObserver:
    """Create a mock observer."""
    return MockObserver()


@pytest.fixture
def channel() -> PresenceChannel:
    """Create a fresh presence channel for testing."""
    # Get the global channel and clear it
    ch = get_presence_channel()
    ch._cursors.clear()
    return ch


@pytest.fixture
def presence_node(channel: PresenceChannel) -> PresenceNode:
    """Create a presence node with the test channel."""
    node = PresenceNode()
    node._channel = channel
    return node


# =============================================================================
# Affordances Tests
# =============================================================================


def test_presence_affordances_include_demo() -> None:
    """Demo is in the affordances list."""
    assert "demo" in PRESENCE_AFFORDANCES


def test_presence_affordances_complete() -> None:
    """All expected affordances are present."""
    expected = {
        "manifest",
        "snapshot",
        "cursor",
        "join",
        "leave",
        "update",
        "states",
        "circadian",
        "stream",
        "demo",
    }
    assert set(PRESENCE_AFFORDANCES) == expected


# =============================================================================
# Manifest Tests
# =============================================================================


@pytest.mark.asyncio
async def test_manifest_returns_active_count(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Manifest shows active cursor count."""
    result = await presence_node.manifest(observer)
    assert "Active cursors:" in result.content


# =============================================================================
# Demo Mode Tests
# =============================================================================


@pytest.mark.asyncio
async def test_demo_start_creates_agents(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Demo start creates the requested number of agents."""
    # Start with 2 agents
    result = await presence_node.invoke("demo", observer, action="start", agent_count=2)

    assert result["success"] is True
    assert result["action"] == "start"
    assert len(result["agent_ids"]) == 2
    assert result["agent_ids"][0] == DEMO_AGENTS[0]["id"]
    assert result["agent_ids"][1] == DEMO_AGENTS[1]["id"]

    # Tasks should be running
    assert len(_demo_tasks) == 2

    # Clean up
    await presence_node.invoke("demo", observer, action="stop")


@pytest.mark.asyncio
async def test_demo_stop_removes_agents(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Demo stop removes all demo agents."""
    # Start then stop
    await presence_node.invoke("demo", observer, action="start", agent_count=2)
    result = await presence_node.invoke("demo", observer, action="stop")

    assert result["success"] is True
    assert result["action"] == "stop"
    assert len(result["agent_ids"]) == 2

    # Tasks should be cancelled
    assert len(_demo_tasks) == 0

    # Give async tasks time to fully cancel
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_demo_start_replaces_existing(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Starting demo again replaces existing demo agents."""
    # Start with 2, then start with 1
    await presence_node.invoke("demo", observer, action="start", agent_count=2)
    result = await presence_node.invoke("demo", observer, action="start", agent_count=1)

    assert result["success"] is True
    assert len(result["agent_ids"]) == 1
    assert len(_demo_tasks) == 1

    # Clean up
    await presence_node.invoke("demo", observer, action="stop")


@pytest.mark.asyncio
async def test_demo_max_agents_is_three(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Demo caps at 3 agents maximum."""
    result = await presence_node.invoke("demo", observer, action="start", agent_count=10)

    assert result["success"] is True
    # Should be capped at 3
    assert len(result["agent_ids"]) == 3

    # Clean up
    await presence_node.invoke("demo", observer, action="stop")


@pytest.mark.asyncio
async def test_demo_invalid_action(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Invalid action returns error."""
    result = await presence_node.invoke("demo", observer, action="invalid")

    assert result["success"] is False
    assert "Unknown action" in result["message"]


# =============================================================================
# Stream Tests
# =============================================================================


@pytest.mark.asyncio
async def test_stream_yields_connected_event(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Stream yields a connected event first."""
    stream = await presence_node.invoke("stream", observer)

    # Get first event
    first = await stream.__anext__()

    assert first["type"] == "connected"
    assert "timestamp" in first


@pytest.mark.asyncio
async def test_stream_yields_initial_cursors(
    presence_node: PresenceNode,
    observer: MockObserver,
    channel: PresenceChannel,
) -> None:
    """Stream yields initial cursors after connection."""
    from services.conductor.presence import AgentCursor

    # Add a cursor first
    cursor = AgentCursor(
        agent_id="test-agent",
        display_name="Test",
        state=CursorState.WAITING,
        activity="Testing",
    )
    await channel.join(cursor)

    # Start stream
    stream = await presence_node.invoke("stream", observer, poll_interval=0.1)

    # Get connected event
    await stream.__anext__()

    # Get cursor update
    cursor_event = await stream.__anext__()

    assert cursor_event["type"] == "cursor_update"
    assert cursor_event["cursor"]["agent_id"] == "test-agent"


# =============================================================================
# Cursor State Tests
# =============================================================================


@pytest.mark.asyncio
async def test_cursor_states_returns_all_states(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """States aspect returns all cursor states with properties."""
    result = await presence_node.invoke("states", observer)

    assert "states" in result
    assert len(result["states"]) == len(CursorState)

    # Check structure
    state = result["states"][0]
    assert "name" in state
    assert "emoji" in state
    assert "color" in state
    assert "can_transition_to" in state


@pytest.mark.asyncio
async def test_circadian_returns_phase_info(
    presence_node: PresenceNode,
    observer: MockObserver,
) -> None:
    """Circadian aspect returns phase information."""
    result = await presence_node.invoke("circadian", observer)

    assert "phase" in result
    assert "tempo_modifier" in result
    assert "warmth" in result
    assert "hour" in result


# =============================================================================
# Join/Leave Tests
# =============================================================================


@pytest.mark.asyncio
async def test_join_adds_cursor(
    presence_node: PresenceNode,
    observer: MockObserver,
    channel: PresenceChannel,
) -> None:
    """Join adds a cursor to the channel."""
    result = await presence_node.invoke(
        "join",
        observer,
        agent_id="new-agent",
        display_name="New Agent",
        initial_state="WAITING",
    )

    assert result["success"] is True
    assert result["cursor"]["agent_id"] == "new-agent"
    assert result["active_count"] == 1

    # Verify in channel
    cursor = channel.get_cursor("new-agent")
    assert cursor is not None
    assert cursor.display_name == "New Agent"


@pytest.mark.asyncio
async def test_leave_removes_cursor(
    presence_node: PresenceNode,
    observer: MockObserver,
    channel: PresenceChannel,
) -> None:
    """Leave removes a cursor from the channel."""
    # Join first
    await presence_node.invoke(
        "join",
        observer,
        agent_id="temp-agent",
        display_name="Temp",
    )

    # Leave
    result = await presence_node.invoke("leave", observer, agent_id="temp-agent")

    assert result["success"] is True
    assert result["was_present"] is True
    assert result["active_count"] == 0

    # Verify removed
    cursor = channel.get_cursor("temp-agent")
    assert cursor is None


# =============================================================================
# Update Tests
# =============================================================================


@pytest.mark.asyncio
async def test_update_changes_cursor_state(
    presence_node: PresenceNode,
    observer: MockObserver,
    channel: PresenceChannel,
) -> None:
    """Update changes cursor state and activity."""
    # Join first
    await presence_node.invoke(
        "join",
        observer,
        agent_id="update-agent",
        display_name="Update Test",
        initial_state="WAITING",
    )

    # Update to FOLLOWING (valid from WAITING)
    result = await presence_node.invoke(
        "update",
        observer,
        agent_id="update-agent",
        state="FOLLOWING",
        activity="Following the user",
        focus_path="self.memory",
    )

    assert result["success"] is True
    assert result["cursor"]["state"] == "FOLLOWING"
    assert result["cursor"]["activity"] == "Following the user"
    assert result["cursor"]["focus_path"] == "self.memory"


@pytest.mark.asyncio
async def test_update_rejects_invalid_transition(
    presence_node: PresenceNode,
    observer: MockObserver,
    channel: PresenceChannel,
) -> None:
    """Update rejects invalid state transitions."""
    # Join in WAITING state, then transition to WORKING
    await presence_node.invoke(
        "join",
        observer,
        agent_id="invalid-agent",
        display_name="Invalid Test",
        initial_state="WAITING",
    )

    # First move to WORKING (valid from WAITING)
    await presence_node.invoke(
        "update",
        observer,
        agent_id="invalid-agent",
        state="WORKING",
    )

    # Try to jump to EXPLORING (not allowed from WORKING)
    # WORKING can only go to: SUGGESTING, WAITING, FOLLOWING
    result = await presence_node.invoke(
        "update",
        observer,
        agent_id="invalid-agent",
        state="EXPLORING",
    )

    assert result["success"] is False
    assert "Invalid transition" in result["error"]
