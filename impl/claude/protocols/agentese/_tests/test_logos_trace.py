"""
Tests for PolicyTrace emission in AGENTESE Logos (TIER 2)

Verifies:
- PolicyTrace is emitted on successful invoke
- Trace captures path resolution
- Trace captures affordance checking
- Trace captures invocation lifecycle
- Trace has correct constitutional scores
- Trace is stored on observer
- Alias expansion is traced
"""

from __future__ import annotations

import pytest

from agents.t.truth_functor import (
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
)
from ..logos import Logos, PlaceholderNode, SimpleRegistry, create_logos
from ..node import Observer


@pytest.fixture
def simple_logos() -> Logos:
    """Create a Logos with a simple test node."""
    registry = SimpleRegistry()
    node = PlaceholderNode(
        handle="world.test",
        archetype_affordances={
            "developer": ("manifest", "witness", "affordances", "debug"),
            "guest": ("manifest", "witness", "affordances"),
        },
    )
    registry.register("world.test", node)
    return create_logos(registry=registry)


class TestPolicyTraceEmission:
    """Test PolicyTrace emission on AGENTESE invocations."""

    @pytest.mark.asyncio
    async def test_trace_emitted_on_successful_invoke(self, simple_logos: Logos) -> None:
        """PolicyTrace is created and stored on observer after invoke."""
        observer = Observer(archetype="developer")
        result = await simple_logos.invoke("world.test.manifest", observer)

        # Observer should have trace stored
        assert hasattr(observer, "last_trace")
        trace = getattr(observer, "last_trace")
        assert isinstance(trace, PolicyTrace)
        assert trace.value == result

    @pytest.mark.asyncio
    async def test_trace_captures_path_resolution(self, simple_logos: Logos) -> None:
        """Trace includes path resolution step."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")
        assert trace is not None

        # Find resolution entry
        resolution_entries = [
            e for e in trace.entries if e.action.name == "resolve"
        ]
        assert len(resolution_entries) == 1

        entry = resolution_entries[0]
        assert entry.state_before.phase == "resolution"
        assert entry.state_after.phase == "resolved"
        # ProbeAction parameters is a tuple: (node_path,)
        assert "world.test" in entry.action.parameters

    @pytest.mark.asyncio
    async def test_trace_captures_affordance_check(self, simple_logos: Logos) -> None:
        """Trace includes affordance verification."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")
        affordance_entries = [
            e for e in trace.entries if e.action.name == "check_affordance"
        ]
        assert len(affordance_entries) == 1

        entry = affordance_entries[0]
        assert entry.state_before.phase == "affordance_check"
        assert entry.state_after.phase == "affordance_verified"
        assert entry.reward.ethical == 1.0  # Affordance passed

    @pytest.mark.asyncio
    async def test_trace_captures_invocation_lifecycle(self, simple_logos: Logos) -> None:
        """Trace captures invoke start and completion."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        # Find invocation entries
        invoke_entries = [e for e in trace.entries if e.action.name == "invoke"]
        complete_entries = [e for e in trace.entries if e.action.name == "complete"]

        assert len(invoke_entries) == 1
        assert len(complete_entries) == 1

        invoke_entry = invoke_entries[0]
        assert invoke_entry.state_before.phase == "invoking"
        assert invoke_entry.state_after.phase == "in_progress"

        complete_entry = complete_entries[0]
        assert complete_entry.state_before.phase == "in_progress"
        assert complete_entry.state_after.phase == "complete"

    @pytest.mark.asyncio
    async def test_trace_constitutional_scores(self, simple_logos: Logos) -> None:
        """Trace entries have appropriate constitutional scores."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        # All entries should have rewards
        assert len(trace.entries) > 0
        for entry in trace.entries:
            assert isinstance(entry.reward, ConstitutionalScore)
            # At least one principle should score > 0
            assert entry.reward.weighted_total >= 0

        # Total reward should be positive for successful invocation
        assert trace.total_reward > 0

    @pytest.mark.asyncio
    async def test_trace_has_reasoning(self, simple_logos: Logos) -> None:
        """Every trace entry has human-readable reasoning."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        for entry in trace.entries:
            assert entry.reasoning
            assert len(entry.reasoning) > 0

    @pytest.mark.asyncio
    async def test_guest_observer_gets_trace(self, simple_logos: Logos) -> None:
        """Guest observer also receives trace."""
        observer = Observer.guest()
        await simple_logos.invoke("world.test.manifest", observer)

        assert hasattr(observer, "last_trace")
        trace = getattr(observer, "last_trace")
        assert isinstance(trace, PolicyTrace)

    @pytest.mark.asyncio
    async def test_none_observer_creates_guest_with_trace(self, simple_logos: Logos) -> None:
        """When observer is None, guest observer is created but trace is not accessible."""
        # This test verifies that None observer defaults to guest but we can't access trace
        result = await simple_logos.invoke("world.test.manifest")
        assert result is not None  # Invocation succeeded


class TestAliasExpansionTracing:
    """Test PolicyTrace for alias expansion."""

    @pytest.mark.asyncio
    async def test_alias_expansion_traced(self, simple_logos: Logos) -> None:
        """Alias expansion is recorded in trace."""
        simple_logos.alias("test", "world.test")
        observer = Observer(archetype="developer")

        await simple_logos.invoke("test.manifest", observer)

        trace = getattr(observer, "last_trace")
        alias_entries = [
            e for e in trace.entries if e.action.name == "expand_alias"
        ]

        assert len(alias_entries) == 1
        entry = alias_entries[0]
        assert entry.state_before.phase == "alias_expansion"
        assert entry.state_after.phase == "alias_expanded"
        # ProbeAction parameters is a tuple: (original_path, expanded_path)
        assert entry.action.parameters[0] == "test.manifest"
        assert entry.action.parameters[1] == "world.test.manifest"

    @pytest.mark.asyncio
    async def test_no_alias_expansion_no_trace_entry(self, simple_logos: Logos) -> None:
        """No alias expansion means no alias trace entry."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")
        alias_entries = [
            e for e in trace.entries if e.action.name == "expand_alias"
        ]

        assert len(alias_entries) == 0


class TestTracePhaseProgression:
    """Test that trace phases progress correctly."""

    @pytest.mark.asyncio
    async def test_phases_progress_in_order(self, simple_logos: Logos) -> None:
        """Phases progress: resolution → affordance_check → invoking → complete."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        # Extract phases in order
        phases = [e.state_before.phase for e in trace.entries]

        # Should see resolution, affordance_check, invoking, in_progress
        assert "resolution" in phases
        assert "affordance_check" in phases
        assert "invoking" in phases

        # Resolution comes before affordance check
        resolution_idx = phases.index("resolution")
        affordance_idx = phases.index("affordance_check")
        assert resolution_idx < affordance_idx

    @pytest.mark.asyncio
    async def test_final_state_is_complete(self, simple_logos: Logos) -> None:
        """Final trace entry ends in 'complete' phase."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")
        final_entry = trace.entries[-1]

        assert final_entry.state_after.phase == "complete"


class TestTraceMetrics:
    """Test PolicyTrace reward metrics."""

    @pytest.mark.asyncio
    async def test_total_reward_accumulates(self, simple_logos: Logos) -> None:
        """Total reward is sum of all entry rewards."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        manual_total = sum(e.reward.weighted_total for e in trace.entries)
        assert trace.total_reward == manual_total
        assert trace.total_reward > 0

    @pytest.mark.asyncio
    async def test_max_reward_computed(self, simple_logos: Logos) -> None:
        """Max reward is the highest single-step reward."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        manual_max = max(e.reward.weighted_total for e in trace.entries)
        assert trace.max_reward == manual_max

    @pytest.mark.asyncio
    async def test_avg_reward_computed(self, simple_logos: Logos) -> None:
        """Average reward is total / count."""
        observer = Observer(archetype="developer")
        await simple_logos.invoke("world.test.manifest", observer)

        trace = getattr(observer, "last_trace")

        expected_avg = trace.total_reward / len(trace.entries)
        assert trace.avg_reward == expected_avg
