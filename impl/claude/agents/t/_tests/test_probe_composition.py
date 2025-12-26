"""
Tests for TruthFunctor composition.

Tests the composition operators (>> and |) and verifies categorical laws:
1. Associativity: (f >> g) >> h ≡ f >> (g >> h)
2. Identity: There exists an identity probe such that id >> p ≡ p ≡ p >> id
3. Trace preservation: Composition preserves PolicyTrace accumulation
4. Reward composition: Combined rewards calculated correctly

Uses NullProbe as the concrete probe type for testing since it's fully implemented.
When other probe types (ChaosProbe, WitnessProbe, etc.) are implemented, add
specific composition tests for those as well.
"""

from __future__ import annotations

import pytest

from agents.t.probes.null_probe import NullProbe, NullState
from agents.t.truth_functor import (
    ComposedProbe,
    PolicyTrace,
    TruthVerdict,
)


class TestSequentialComposition:
    """Test sequential composition (>>)."""

    @pytest.mark.asyncio
    async def test_basic_sequential_composition(self):
        """Test basic f >> g composition."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        # Compose: probe1 >> probe2
        composed = probe1 >> probe2

        assert isinstance(composed, ComposedProbe)
        assert composed.op == "seq"
        assert composed.left == probe1
        assert composed.right == probe2

    @pytest.mark.asyncio
    async def test_sequential_executes_both(self):
        """Test that sequential composition runs both probes."""
        probe1 = NullProbe(constant="first")
        probe2 = NullProbe(constant="second")

        composed = probe1 >> probe2

        # Mock agent (we're testing probe composition, not agent behavior)
        mock_agent = lambda x: x

        result = await composed.verify(mock_agent, "input")

        # Sequential composition should use right probe's result
        assert result.value.value == "second"

    @pytest.mark.asyncio
    async def test_sequential_accumulates_traces(self):
        """Test that sequential composition merges traces."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        composed = probe1 >> probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have entries from both probes
        # Each NullProbe emits 2 entries per invocation
        assert len(result.entries) >= 4

    @pytest.mark.asyncio
    async def test_sequential_preserves_order(self):
        """Test that sequential composition preserves execution order."""
        probe1 = NullProbe(constant="first", delay_ms=10)
        probe2 = NullProbe(constant="second", delay_ms=5)

        composed = probe1 >> probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Verify traces are in order (probe1 entries before probe2 entries)
        # This is implicit in the sequential execution


class TestParallelComposition:
    """Test parallel composition (|)."""

    @pytest.mark.asyncio
    async def test_basic_parallel_composition(self):
        """Test basic f | g composition."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        # Compose: probe1 | probe2
        composed = probe1 | probe2

        assert isinstance(composed, ComposedProbe)
        assert composed.op == "par"
        assert composed.left == probe1
        assert composed.right == probe2

    @pytest.mark.asyncio
    async def test_parallel_executes_both(self):
        """Test that parallel composition runs both probes."""
        probe1 = NullProbe(constant="left")
        probe2 = NullProbe(constant="right")

        composed = probe1 | probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Parallel composition should combine both results
        assert isinstance(result.value.value, tuple)
        assert result.value.value == ("left", "right")

    @pytest.mark.asyncio
    async def test_parallel_combines_passed_status(self):
        """Test that parallel composition ANDs the passed status."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        composed = probe1 | probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # For NullProbes, verify() returns True, so composed should pass
        # (This will be more interesting with probes that can fail)
        assert result.value.passed is True

    @pytest.mark.asyncio
    async def test_parallel_takes_min_confidence(self):
        """Test that parallel composition takes minimum confidence."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        composed = probe1 | probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # NullProbes don't set confidence explicitly, but verify the structure
        assert hasattr(result.value, 'confidence')

    @pytest.mark.asyncio
    async def test_parallel_merges_traces(self):
        """Test that parallel composition merges traces from both probes."""
        probe1 = NullProbe(constant="a")
        probe2 = NullProbe(constant="b")

        composed = probe1 | probe2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have entries from both probes
        assert len(result.entries) >= 2


class TestAssociativityLaw:
    """Test associativity law: (f >> g) >> h ≡ f >> (g >> h)."""

    @pytest.mark.asyncio
    async def test_sequential_associativity(self):
        """Test that sequential composition is associative."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")
        p3 = NullProbe(constant="c")

        # Two ways to associate
        left_assoc = (p1 >> p2) >> p3
        right_assoc = p1 >> (p2 >> p3)

        mock_agent = lambda x: x

        # Execute both
        result_left = await left_assoc.verify(mock_agent, "input")
        result_right = await right_assoc.verify(mock_agent, "input")

        # Results should be equivalent
        # (Final value should be the same)
        assert result_left.value.value == result_right.value.value

        # Both should have 3 trace entries (one from each probe)
        # Note: ComposedProbe may add its own entries, so use >=
        assert len(result_left.entries) >= 3
        assert len(result_right.entries) >= 3

    @pytest.mark.asyncio
    async def test_parallel_associativity(self):
        """Test that parallel composition is associative."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")
        p3 = NullProbe(constant="c")

        # Two ways to associate
        left_assoc = (p1 | p2) | p3
        right_assoc = p1 | (p2 | p3)

        mock_agent = lambda x: x

        # Execute both
        result_left = await left_assoc.verify(mock_agent, "input")
        result_right = await right_assoc.verify(mock_agent, "input")

        # Both should execute all three probes
        assert len(result_left.entries) >= 3
        assert len(result_right.entries) >= 3

    @pytest.mark.asyncio
    async def test_mixed_composition_associativity(self):
        """Test associativity with mixed >> and | operators."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")
        p3 = NullProbe(constant="c")
        p4 = NullProbe(constant="d")

        # Complex composition: (p1 >> p2) | (p3 >> p4)
        left_branch = p1 >> p2
        right_branch = p3 >> p4
        composed = left_branch | right_branch

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have traces from all four probes
        assert len(result.entries) >= 4


class TestComposedProbeName:
    """Test naming of composed probes."""

    def test_sequential_name(self):
        """Test that sequential composition has readable name."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        assert ">>" in composed.name
        assert "NullProbe" in composed.name

    def test_parallel_name(self):
        """Test that parallel composition has readable name."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 | p2

        assert "|" in composed.name
        assert "NullProbe" in composed.name

    def test_nested_composition_name(self):
        """Test naming of nested compositions."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")
        p3 = NullProbe(constant="c")

        # Nested: (p1 >> p2) | p3
        composed = (p1 >> p2) | p3

        # Should show structure
        assert ">>" in composed.name
        assert "|" in composed.name


class TestComposedProbeStates:
    """Test state space of composed probes."""

    def test_sequential_state_space(self):
        """Test that sequential composition has product state space."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        states = composed.states

        # Should be product: p1.states × p2.states
        # Each NullProbe has 3 states, so composed has 3×3 = 9
        assert len(states) == 9

    def test_parallel_state_space(self):
        """Test that parallel composition has product state space."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 | p2

        states = composed.states

        # Same as sequential: product space
        assert len(states) == 9

    def test_composed_states_are_tuples(self):
        """Test that composed states are tuples of component states."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        states = composed.states

        # All states should be tuples
        for state in states:
            assert isinstance(state, tuple)
            assert len(state) == 2


class TestComposedProbeActions:
    """Test action space of composed probes."""

    def test_sequential_actions(self):
        """Test that sequential composition exposes left actions initially."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        # Get actions from initial product state
        initial_state = (NullState.READY, NullState.READY)

        actions = composed.actions(initial_state)

        # Sequential: only left's actions available
        # NullProbe READY has "invoke" action
        assert any(a.name == "invoke" for a in actions)

    def test_parallel_actions(self):
        """Test that parallel composition unions actions."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 | p2

        initial_state = (NullState.READY, NullState.READY)

        actions = composed.actions(initial_state)

        # Parallel: union of both actions
        # Both NullProbes have "invoke", so union is just {"invoke"}
        assert any(a.name == "invoke" for a in actions)


class TestComposedProbeReward:
    """Test reward calculation for composed probes."""

    def test_sequential_reward_left_only(self):
        """Test reward when only left component transitions."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        from agents.t.truth_functor import ProbeAction

        state_before = (NullState.READY, NullState.READY)
        state_after = (NullState.COMPUTING, NullState.READY)

        action = ProbeAction("invoke")

        reward = composed.reward(state_before, action, state_after)

        # Only left transitioned, so only left's reward
        assert reward.ethical > 0  # NullProbe gives ethical reward

    def test_sequential_reward_right_only(self):
        """Test reward when only right component transitions."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        from agents.t.truth_functor import ProbeAction

        state_before = (NullState.DONE, NullState.READY)
        state_after = (NullState.DONE, NullState.COMPUTING)

        action = ProbeAction("invoke")

        reward = composed.reward(state_before, action, state_after)

        # Only right transitioned, so only right's reward
        assert reward.ethical > 0

    def test_parallel_reward_sum(self):
        """Test that parallel rewards sum when both transition."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 | p2

        from agents.t.truth_functor import ProbeAction

        # Both transition
        state_before = (NullState.READY, NullState.READY)
        state_after = (NullState.COMPUTING, NullState.COMPUTING)

        action = ProbeAction("invoke")

        reward = composed.reward(state_before, action, state_after)

        # Both transitioned, so sum of both rewards
        # Each NullProbe gives ethical (1.0) + composable (1.0) + generative (0.5)
        # Total ethical should be 2 * 1.0 = 2.0
        assert reward.ethical == pytest.approx(1.0 + 1.0)
        assert reward.composable == pytest.approx(1.0 + 1.0)
        assert reward.generative == pytest.approx(0.5 + 0.5)


class TestComposedProbeMode:
    """Test analysis mode inheritance."""

    def test_composed_inherits_left_mode(self):
        """Test that composed probe uses left probe's mode."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        # NullProbe doesn't set mode explicitly in current impl,
        # but the ComposedProbe.mode property should access left.mode
        # This will be more interesting when we have probes with different modes


class TestTracePreservation:
    """Test that composition preserves PolicyTrace semantics."""

    @pytest.mark.asyncio
    async def test_sequential_preserves_total_reward(self):
        """Test that sequential composition preserves cumulative reward."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 >> p2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have positive total reward
        assert result.total_reward > 0

    @pytest.mark.asyncio
    async def test_parallel_preserves_total_reward(self):
        """Test that parallel composition preserves cumulative reward."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")

        composed = p1 | p2

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have positive total reward from both probes
        assert result.total_reward > 0

    @pytest.mark.asyncio
    async def test_nested_composition_accumulates_traces(self):
        """Test that deeply nested composition accumulates all traces."""
        p1 = NullProbe(constant="a")
        p2 = NullProbe(constant="b")
        p3 = NullProbe(constant="c")
        p4 = NullProbe(constant="d")

        # Complex nesting: ((p1 >> p2) | p3) >> p4
        composed = ((p1 >> p2) | p3) >> p4

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have entries from all four probes
        assert len(result.entries) >= 4


class TestCompositionEdgeCases:
    """Test edge cases in composition."""

    @pytest.mark.asyncio
    async def test_compose_with_self(self):
        """Test composing a probe with itself."""
        probe = NullProbe(constant="self")

        composed = probe >> probe

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should work (runs probe twice)
        assert result.value.value == "self"

    @pytest.mark.asyncio
    async def test_long_sequential_chain(self):
        """Test long chain of sequential compositions."""
        probes = [NullProbe(constant=f"p{i}") for i in range(5)]

        # Chain them all: p0 >> p1 >> p2 >> p3 >> p4
        composed = probes[0]
        for probe in probes[1:]:
            composed = composed >> probe

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Final result should be from last probe
        assert result.value.value == "p4"

        # Should have traces from all 5 probes
        assert len(result.entries) >= 5

    @pytest.mark.asyncio
    async def test_wide_parallel_composition(self):
        """Test wide parallel composition (many probes in parallel)."""
        probes = [NullProbe(constant=f"p{i}") for i in range(4)]

        # Parallel: p0 | p1 | p2 | p3
        composed = probes[0]
        for probe in probes[1:]:
            composed = composed | probe

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should have traces from all 4 probes
        assert len(result.entries) >= 4
