"""
Tests for Adapters: Transform agent runtime data to widget states.

Wave 5 - Reality Wiring: Adapter tests
"""

from __future__ import annotations

import pytest

from agents.i.reactive.primitives.agent_card import AgentCardState
from agents.i.reactive.primitives.yield_card import YieldCardState
from agents.i.reactive.screens.dashboard import DashboardScreenState
from agents.i.reactive.wiring.adapters import (
    AgentRuntimeAdapter,
    ReactiveDashboardAdapter,
    SoulAdapter,
    YieldAdapter,
    _mode_to_phase,
    _status_to_phase,
    create_dashboard_state,
)


class TestStatusToPhase:
    """Tests for _status_to_phase helper."""

    def test_idle_mapping(self) -> None:
        """idle should map to idle."""
        assert _status_to_phase("idle") == "idle"

    def test_active_mapping(self) -> None:
        """running/active should map to active."""
        assert _status_to_phase("running") == "active"
        assert _status_to_phase("active") == "active"

    def test_waiting_mapping(self) -> None:
        """waiting/paused should map to waiting."""
        assert _status_to_phase("waiting") == "waiting"
        assert _status_to_phase("paused") == "waiting"

    def test_error_mapping(self) -> None:
        """error/failed should map to error."""
        assert _status_to_phase("error") == "error"
        assert _status_to_phase("failed") == "error"

    def test_yielding_mapping(self) -> None:
        """yielding/yielded should map to yielding."""
        assert _status_to_phase("yielding") == "yielding"
        assert _status_to_phase("yielded") == "yielding"

    def test_thinking_mapping(self) -> None:
        """thinking/processing should map to thinking."""
        assert _status_to_phase("thinking") == "thinking"
        assert _status_to_phase("processing") == "thinking"

    def test_complete_mapping(self) -> None:
        """complete/completed/done should map to complete."""
        assert _status_to_phase("complete") == "complete"
        assert _status_to_phase("completed") == "complete"
        assert _status_to_phase("done") == "complete"

    def test_unknown_defaults_to_idle(self) -> None:
        """Unknown status should default to idle."""
        assert _status_to_phase("unknown") == "idle"
        assert _status_to_phase("") == "idle"

    def test_case_insensitive(self) -> None:
        """Status mapping should be case insensitive."""
        assert _status_to_phase("ACTIVE") == "active"
        assert _status_to_phase("Running") == "active"


class TestModeToPhase:
    """Tests for _mode_to_phase helper."""

    def test_challenge_mapping(self) -> None:
        """challenge mode should map to active."""
        assert _mode_to_phase("challenge") == "active"

    def test_reflect_mapping(self) -> None:
        """reflect mode should map to thinking."""
        assert _mode_to_phase("reflect") == "thinking"

    def test_advise_mapping(self) -> None:
        """advise mode should map to active."""
        assert _mode_to_phase("advise") == "active"

    def test_explore_mapping(self) -> None:
        """explore mode should map to thinking."""
        assert _mode_to_phase("explore") == "thinking"

    def test_unknown_defaults_to_idle(self) -> None:
        """Unknown mode should default to idle."""
        assert _mode_to_phase("unknown") == "idle"


class TestSoulAdapter:
    """Tests for SoulAdapter."""

    def test_adapt_from_dict(self) -> None:
        """adapt() should handle dict input."""
        adapter = SoulAdapter()

        state = adapter.adapt(
            {"mode": "challenge", "session_interactions": 5},
            t=1000.0,
            entropy=0.3,
            seed=42,
        )

        assert isinstance(state, AgentCardState)
        assert state.agent_id == "kgent"
        assert state.phase == "active"  # challenge -> active
        assert state.t == 1000.0
        assert state.entropy == 0.3
        assert state.seed == 42

    def test_adapt_tracks_activity(self) -> None:
        """adapt() should track activity history."""
        adapter = SoulAdapter()

        adapter.adapt({"session_interactions": 2})
        adapter.adapt({"session_interactions": 5})
        adapter.adapt({"session_interactions": 8})

        state = adapter.adapt({"session_interactions": 10})

        assert len(state.activity) == 4
        assert all(0.0 <= a <= 1.0 for a in state.activity)

    def test_adapt_brief(self) -> None:
        """adapt_brief() should work like adapt()."""
        adapter = SoulAdapter()

        state = adapter.adapt_brief({"mode": "reflect", "session_interactions": 3})

        assert isinstance(state, AgentCardState)
        assert state.phase == "thinking"

    def test_adapt_default_values(self) -> None:
        """adapt() should use defaults for missing fields."""
        adapter = SoulAdapter()

        state = adapter.adapt({})

        assert state.agent_id == "kgent"
        assert state.name == "Kent"
        assert state.phase == "idle"
        assert state.capability == 1.0


class TestAgentRuntimeAdapter:
    """Tests for AgentRuntimeAdapter."""

    def test_adapt_from_dict(self) -> None:
        """adapt() should handle dict input."""
        adapter = AgentRuntimeAdapter()

        state = adapter.adapt(
            {"id": "agent-1", "name": "Alpha", "status": "running"},
            t=500.0,
            entropy=0.2,
            seed=100,
        )

        assert isinstance(state, AgentCardState)
        assert state.agent_id == "agent-1"
        assert state.name == "Alpha"
        assert state.phase == "active"  # running -> active
        assert state.t == 500.0
        assert state.entropy == 0.2

    def test_adapt_with_agent_id_key(self) -> None:
        """adapt() should handle 'agent_id' key."""
        adapter = AgentRuntimeAdapter()

        state = adapter.adapt({"agent_id": "agent-2", "status": "idle"})

        assert state.agent_id == "agent-2"

    def test_adapt_tracks_per_agent_activity(self) -> None:
        """adapt() should track activity per agent."""
        adapter = AgentRuntimeAdapter()

        adapter.adapt({"id": "a1", "activity": 0.5})
        adapter.adapt({"id": "a1", "activity": 0.7})
        adapter.adapt({"id": "a2", "activity": 0.3})

        state1 = adapter.adapt({"id": "a1", "activity": 0.9})
        state2 = adapter.adapt({"id": "a2", "activity": 0.4})

        # Different agents have different histories
        assert len(state1.activity) == 3  # a1 has 3 updates (0.5, 0.7, 0.9)
        assert len(state2.activity) == 2  # a2 has 2 updates (0.3, 0.4)

    def test_adapt_many(self) -> None:
        """adapt_many() should handle multiple agents."""
        adapter = AgentRuntimeAdapter()

        agents = [
            {"id": "a1", "name": "One", "status": "active"},
            {"id": "a2", "name": "Two", "status": "idle"},
            {"id": "a3", "name": "Three", "status": "error"},
        ]

        states = adapter.adapt_many(agents, t=100.0, entropy=0.1, seed=10)

        assert len(states) == 3
        assert states[0].agent_id == "a1"
        assert states[1].agent_id == "a2"
        assert states[2].agent_id == "a3"
        assert states[0].phase == "active"
        assert states[1].phase == "idle"
        assert states[2].phase == "error"

    def test_adapt_normalizes_values(self) -> None:
        """adapt() should normalize capability and entropy."""
        adapter = AgentRuntimeAdapter()

        state = adapter.adapt(
            {"id": "a1", "capability": 1.5, "status": "active"},
            entropy=2.0,
        )

        assert state.capability == 1.0  # Clamped to max
        assert state.entropy == 1.0  # Clamped to max


class TestYieldAdapter:
    """Tests for YieldAdapter."""

    def test_adapt_from_dict(self) -> None:
        """adapt() should handle dict input."""
        adapter = YieldAdapter()

        state = adapter.adapt(
            {
                "id": "yield-1",
                "content": "Processing complete",
                "type": "artifact",
                "source": "agent-1",
                "importance": 0.8,
            },
            t=200.0,
            entropy=0.1,
        )

        assert isinstance(state, YieldCardState)
        assert state.yield_id == "yield-1"
        assert state.content == "Processing complete"
        assert state.yield_type == "artifact"
        assert state.source_agent == "agent-1"
        assert state.importance == 0.8
        assert state.t == 200.0

    def test_adapt_normalizes_yield_type(self) -> None:
        """adapt() should normalize yield types."""
        adapter = YieldAdapter()

        # Various input types
        states = [
            adapter.adapt({"type": "artifact"}),
            adapter.adapt({"type": "result"}),
            adapter.adapt({"type": "output"}),
            adapter.adapt({"type": "observation"}),
            adapter.adapt({"type": "info"}),
            adapter.adapt({"type": "thought"}),
            adapter.adapt({"type": "debug"}),
        ]

        # Check normalized types
        assert states[0].yield_type == "artifact"
        assert states[1].yield_type == "artifact"  # result -> artifact
        assert states[2].yield_type == "artifact"  # output -> artifact
        assert str(states[3].yield_type) == "observation"  # type: ignore[comparison-overlap]
        assert str(states[4].yield_type) == "observation"  # type: ignore[comparison-overlap]  # info -> observation
        assert states[5].yield_type == "thought"
        assert states[6].yield_type == "thought"  # debug -> thought

    def test_adapt_auto_generates_id(self) -> None:
        """adapt() should auto-generate yield_id if missing."""
        adapter = YieldAdapter()

        state1 = adapter.adapt({"content": "first"})
        state2 = adapter.adapt({"content": "second"})

        assert state1.yield_id.startswith("yield-")
        assert state2.yield_id.startswith("yield-")
        assert state1.yield_id != state2.yield_id

    def test_adapt_many(self) -> None:
        """adapt_many() should handle multiple yields."""
        adapter = YieldAdapter()

        yields = [
            {"content": "one", "type": "artifact"},
            {"content": "two", "type": "observation"},
            {"content": "three", "type": "action"},
        ]

        states = adapter.adapt_many(yields, t=50.0)

        assert len(states) == 3
        assert states[0].content == "one"
        assert states[1].content == "two"
        assert states[2].content == "three"

    def test_adapt_with_yield_id_key(self) -> None:
        """adapt() should handle 'yield_id' key."""
        adapter = YieldAdapter()

        state = adapter.adapt({"yield_id": "y-custom", "content": "test"})

        assert state.yield_id == "y-custom"


class TestCreateDashboardState:
    """Tests for create_dashboard_state factory function."""

    def test_create_dashboard_state_empty(self) -> None:
        """create_dashboard_state() should work with no data."""
        state = create_dashboard_state()

        assert isinstance(state, DashboardScreenState)
        assert len(state.agents) == 0
        assert len(state.yields) == 0

    def test_create_dashboard_state_with_agents(self) -> None:
        """create_dashboard_state() should handle agents."""
        state = create_dashboard_state(
            agents=[
                {"id": "a1", "name": "One", "status": "active"},
                {"id": "a2", "name": "Two", "status": "idle"},
            ]
        )

        assert len(state.agents) == 2
        assert state.agents[0].agent_id == "a1"
        assert state.agents[1].agent_id == "a2"

    def test_create_dashboard_state_with_yields(self) -> None:
        """create_dashboard_state() should handle yields."""
        state = create_dashboard_state(
            yields=[
                {"content": "one", "type": "artifact"},
                {"content": "two", "type": "observation"},
            ]
        )

        assert len(state.yields) == 2
        assert state.yields[0].content == "one"
        assert state.yields[1].content == "two"

    def test_create_dashboard_state_with_config(self) -> None:
        """create_dashboard_state() should handle configuration."""
        state = create_dashboard_state(
            t=1000.0,
            entropy=0.5,
            seed=123,
            width=100,
            height=30,
            show_density_field=False,
        )

        assert state.t == 1000.0
        assert state.entropy == 0.5
        assert state.seed == 123
        assert state.width == 100
        assert state.height == 30
        assert state.show_density_field is False


class TestReactiveDashboardAdapter:
    """Tests for ReactiveDashboardAdapter."""

    def test_initial_state(self) -> None:
        """ReactiveDashboardAdapter should have empty initial state."""
        adapter = ReactiveDashboardAdapter()

        state = adapter.state.value

        assert isinstance(state, DashboardScreenState)
        assert len(state.agents) == 0
        assert len(state.yields) == 0

    def test_add_agent(self) -> None:
        """add_agent() should update state."""
        adapter = ReactiveDashboardAdapter()

        adapter.add_agent({"id": "a1", "name": "Test", "status": "active"})

        state = adapter.state.value
        assert len(state.agents) == 1
        assert state.agents[0].agent_id == "a1"

    def test_add_agent_updates_existing(self) -> None:
        """add_agent() should update existing agent."""
        adapter = ReactiveDashboardAdapter()

        adapter.add_agent({"id": "a1", "name": "Test", "status": "idle"})
        adapter.add_agent({"id": "a1", "name": "Test Updated", "status": "active"})

        state = adapter.state.value
        assert len(state.agents) == 1
        # Latest state should be reflected

    def test_remove_agent(self) -> None:
        """remove_agent() should remove from state."""
        adapter = ReactiveDashboardAdapter()

        adapter.add_agent({"id": "a1", "name": "Test"})
        adapter.remove_agent("a1")

        state = adapter.state.value
        assert len(state.agents) == 0

    def test_push_yield(self) -> None:
        """push_yield() should add to state."""
        adapter = ReactiveDashboardAdapter()

        adapter.push_yield({"content": "one"})
        adapter.push_yield({"content": "two"})

        state = adapter.state.value
        assert len(state.yields) == 2
        assert state.yields[0].content == "two"  # Newest first
        assert state.yields[1].content == "one"

    def test_clear_yields(self) -> None:
        """clear_yields() should remove all yields."""
        adapter = ReactiveDashboardAdapter()

        adapter.push_yield({"content": "test"})
        adapter.clear_yields()

        state = adapter.state.value
        assert len(state.yields) == 0

    def test_set_entropy(self) -> None:
        """set_entropy() should update state entropy."""
        adapter = ReactiveDashboardAdapter()
        adapter.add_agent({"id": "a1"})  # Need agent to trigger rebuild

        adapter.set_entropy(0.7)

        state = adapter.state.value
        assert state.entropy == 0.7

    def test_set_entropy_clamped(self) -> None:
        """set_entropy() should clamp to valid range."""
        adapter = ReactiveDashboardAdapter()
        adapter.add_agent({"id": "a1"})

        adapter.set_entropy(1.5)
        assert adapter.state.value.entropy == 1.0

        adapter.set_entropy(-0.5)
        assert adapter.state.value.entropy == 0.0

    def test_snapshot(self) -> None:
        """snapshot() should return immutable state."""
        adapter = ReactiveDashboardAdapter()

        adapter.add_agent({"id": "a1"})
        snapshot = adapter.snapshot()

        adapter.add_agent({"id": "a2"})

        # Snapshot should not change
        assert len(snapshot.agents) == 1

    def test_subscribe_to_state(self) -> None:
        """state Signal should support subscription."""
        adapter = ReactiveDashboardAdapter()
        updates: list[DashboardScreenState] = []

        adapter.state.subscribe(lambda s: updates.append(s))

        adapter.add_agent({"id": "a1"})
        adapter.push_yield({"content": "test"})

        assert len(updates) == 2
