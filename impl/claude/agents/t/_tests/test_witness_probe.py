"""
Tests for WitnessProbe: CATEGORICAL mode observer.

Tests verify:
1. Identity morphism behavior (pass-through)
2. History tracking (SpyAgent consolidation)
3. Invocation counting (CounterAgent consolidation)
4. Performance metrics (MetricsAgent consolidation)
5. Law verification (identity, associativity)
6. Constitutional rewards
7. Composition with other probes
8. PolicyTrace accumulation
"""

from __future__ import annotations

import pytest

from agents.poly.types import Agent
from agents.t.probes.null_probe import NullProbe
from agents.t.probes.witness_probe import (
    ASSOCIATIVITY_LAW,
    IDENTITY_LAW,
    Law,
    WitnessConfig,
    WitnessPhase,
    WitnessProbe,
    witness_probe,
)
from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    ProbeAction,
    ProbeState,
)


class TestWitnessProbeBasics:
    """Test basic WitnessProbe functionality."""

    def test_witness_probe_creation(self):
        """Test creating a WitnessProbe."""
        probe = witness_probe(label="Test")

        assert probe.name == "WitnessProbe(Test)"
        assert probe.mode == AnalysisMode.CATEGORICAL
        assert probe.call_count == 0

    def test_witness_probe_with_custom_laws(self):
        """Test creating probe with custom laws."""
        probe = witness_probe(label="Test", laws=["identity"])

        # Should only check identity law
        assert len(probe.config.laws_to_check) == 1
        assert IDENTITY_LAW in probe.config.laws_to_check

    def test_witness_probe_states(self):
        """Test probe state space."""
        probe = witness_probe()

        states = probe.states

        # Should have 3 canonical states
        assert len(states) == 3

        # All states should be ProbeState
        for state in states:
            assert isinstance(state, ProbeState)

    def test_witness_probe_mode(self):
        """Test that WitnessProbe is CATEGORICAL mode."""
        probe = witness_probe()

        assert probe.mode == AnalysisMode.CATEGORICAL


class TestIdentityMorphism:
    """Test that WitnessProbe is identity morphism (passes data through)."""

    @pytest.mark.asyncio
    async def test_invoke_returns_input_unchanged(self):
        """Test that invoke returns input unchanged."""
        probe = witness_probe()

        input_data = "test data"
        result = await probe.invoke(input_data)

        # Identity: output = input
        assert result == input_data

    @pytest.mark.asyncio
    async def test_invoke_multiple_times(self):
        """Test invoking multiple times."""
        probe = witness_probe()

        inputs = ["a", "b", "c"]
        results = []

        for inp in inputs:
            result = await probe.invoke(inp)
            results.append(result)

        # All should pass through unchanged
        assert results == inputs

    @pytest.mark.asyncio
    async def test_invoke_different_types(self):
        """Test invoke with different data types."""
        probe = witness_probe()

        # String
        assert await probe.invoke("string") == "string"

        # Number
        assert await probe.invoke(42) == 42

        # List
        assert await probe.invoke([1, 2, 3]) == [1, 2, 3]

        # Dict
        assert await probe.invoke({"key": "value"}) == {"key": "value"}


class TestHistoryTracking:
    """Test history tracking (SpyAgent consolidation)."""

    @pytest.mark.asyncio
    async def test_history_captures_inputs(self):
        """Test that history captures all inputs."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")
        await probe.invoke("c")

        assert probe.history == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_history_max_size(self):
        """Test that history respects max_history."""
        probe = witness_probe(max_history=3)

        # Add 5 items
        for i in range(5):
            await probe.invoke(f"item_{i}")

        # Should only keep last 3
        assert len(probe.history) == 3
        assert probe.history == ["item_2", "item_3", "item_4"]

    @pytest.mark.asyncio
    async def test_last_captured_value(self):
        """Test last() returns most recent value."""
        probe = witness_probe()

        await probe.invoke("first")
        await probe.invoke("second")
        await probe.invoke("third")

        assert probe.last() == "third"

    def test_last_raises_on_empty(self):
        """Test that last() raises on empty history."""
        probe = witness_probe()

        with pytest.raises(IndexError):
            probe.last()


class TestInvocationCounting:
    """Test invocation counting (CounterAgent consolidation)."""

    @pytest.mark.asyncio
    async def test_call_count_increments(self):
        """Test that call_count increments."""
        probe = witness_probe()

        assert probe.call_count == 0

        await probe.invoke("a")
        assert probe.call_count == 1

        await probe.invoke("b")
        assert probe.call_count == 2

    @pytest.mark.asyncio
    async def test_assert_count(self):
        """Test assert_count assertion."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")

        # Should pass
        probe.assert_count(2)

        # Should fail
        with pytest.raises(AssertionError):
            probe.assert_count(3)

    @pytest.mark.asyncio
    async def test_assert_captured(self):
        """Test assert_captured assertion."""
        probe = witness_probe()

        await probe.invoke("target")
        await probe.invoke("other")

        # Should pass
        probe.assert_captured("target")

        # Should fail
        with pytest.raises(AssertionError):
            probe.assert_captured("missing")

    @pytest.mark.asyncio
    async def test_assert_not_empty(self):
        """Test assert_not_empty assertion."""
        probe = witness_probe()

        # Should fail when empty
        with pytest.raises(AssertionError):
            probe.assert_not_empty()

        # Should pass after invocation
        await probe.invoke("data")
        probe.assert_not_empty()


class TestPerformanceMetrics:
    """Test performance metrics (MetricsAgent consolidation)."""

    @pytest.mark.asyncio
    async def test_avg_time_calculated(self):
        """Test that average time is calculated."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")

        # Should have non-zero average time
        assert probe.avg_time_ms >= 0

    @pytest.mark.asyncio
    async def test_min_max_time(self):
        """Test min/max time tracking."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")
        await probe.invoke("c")

        # Should have valid min/max
        assert probe.min_time_ms >= 0
        assert probe.max_time_ms >= probe.min_time_ms

    def test_metrics_on_empty(self):
        """Test metrics return 0 when empty."""
        probe = witness_probe()

        assert probe.avg_time_ms == 0.0
        assert probe.min_time_ms == 0.0
        assert probe.max_time_ms == 0.0


class TestDPSemantics:
    """Test DP semantics (states, actions, transitions, rewards)."""

    def test_actions_in_observing_state(self):
        """Test actions available in OBSERVING state."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        actions = probe.actions(state)

        # Should have observe and verify actions
        action_names = {a.name for a in actions}
        assert "observe" in action_names
        assert "verify_identity" in action_names
        assert "verify_associativity" in action_names

    def test_actions_in_verifying_state(self):
        """Test actions available in VERIFYING state."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.VERIFYING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        actions = probe.actions(state)

        action_names = {a.name for a in actions}
        assert "verify_identity" in action_names
        assert "verify_associativity" in action_names
        assert "synthesize" in action_names

    def test_actions_in_complete_state(self):
        """Test that COMPLETE state has no actions."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.COMPLETE.name,
            observations=(),
            laws_verified=frozenset(),
        )

        actions = probe.actions(state)

        # No actions in COMPLETE
        assert len(actions) == 0

    def test_transition_observe_stays_in_observing(self):
        """Test that observe action stays in OBSERVING."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        action = ProbeAction("observe")
        next_state = probe.transition(state, action)

        # Should stay in OBSERVING
        assert WitnessPhase[next_state.phase] == WitnessPhase.OBSERVING

    def test_transition_verify_to_verifying(self):
        """Test that verify actions transition to VERIFYING."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        action = ProbeAction("verify_identity")
        next_state = probe.transition(state, action)

        # Should transition to VERIFYING
        assert WitnessPhase[next_state.phase] == WitnessPhase.VERIFYING

    def test_transition_synthesize_to_complete(self):
        """Test that synthesize transitions to COMPLETE."""
        probe = witness_probe()

        state = ProbeState(
            phase=WitnessPhase.VERIFYING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        action = ProbeAction("synthesize")
        next_state = probe.transition(state, action)

        # Should transition to COMPLETE
        assert WitnessPhase[next_state.phase] == WitnessPhase.COMPLETE

    def test_reward_for_observe(self):
        """Test reward for observe action."""
        probe = witness_probe()

        state_before = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        action = ProbeAction("observe")
        state_after = state_before

        reward = probe.reward(state_before, action, state_after)

        # Should reward generative (enables compression)
        assert isinstance(reward, ConstitutionalScore)
        assert reward.generative > 0

    def test_reward_for_verify_satisfied(self):
        """Test reward for verify action when law satisfied."""
        probe = witness_probe()

        state_before = ProbeState(
            phase=WitnessPhase.OBSERVING.name,
            observations=(),
            laws_verified=frozenset(),
        )

        state_after = ProbeState(
            phase=WitnessPhase.VERIFYING.name,
            observations=(),
            laws_verified=frozenset(["verify_identity"]),
        )

        action = ProbeAction("verify_identity")

        reward = probe.reward(state_before, action, state_after)

        # Should reward composable (law holds)
        assert reward.composable > 0


class TestLawVerification:
    """Test categorical law verification."""

    @pytest.mark.asyncio
    async def test_verify_identity_law(self):
        """Test verifying identity law."""
        probe = witness_probe(laws=["identity"])

        # Simple identity agent
        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Should pass
        assert trace.value.passed
        assert "identity" in trace.value.reasoning

    @pytest.mark.asyncio
    async def test_verify_associativity_law(self):
        """Test verifying associativity law."""
        probe = witness_probe(laws=["associativity"])

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Should pass (trivially for list append)
        assert trace.value.passed
        assert "associativity" in trace.value.reasoning

    @pytest.mark.asyncio
    async def test_verify_all_laws(self):
        """Test verifying all configured laws."""
        probe = witness_probe(laws=["identity", "associativity"])

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Both should pass
        assert trace.value.passed
        assert "identity" in trace.value.reasoning
        assert "associativity" in trace.value.reasoning

    @pytest.mark.asyncio
    async def test_verify_produces_trace(self):
        """Test that verify produces PolicyTrace."""
        probe = witness_probe()

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Should have trace entries
        assert len(trace.entries) > 0

        # Should have positive reward
        assert trace.total_reward > 0

    @pytest.mark.asyncio
    async def test_verify_confidence(self):
        """Test that verify produces confidence score."""
        probe = witness_probe(laws=["identity", "associativity"])

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Confidence should be 1.0 (all laws passed)
        assert trace.value.confidence == 1.0


class TestCompositionWithOtherProbes:
    """Test composition with other probes."""

    @pytest.mark.asyncio
    async def test_compose_with_null_probe_sequential(self):
        """Test sequential composition: WitnessProbe >> NullProbe."""
        witness = witness_probe(label="Witness")
        null = NullProbe(constant="constant")

        composed = witness >> null

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should execute both probes
        assert len(result.entries) >= 2

    @pytest.mark.asyncio
    async def test_compose_with_null_probe_parallel(self):
        """Test parallel composition: WitnessProbe | NullProbe."""
        witness = witness_probe(label="Witness")
        null = NullProbe(constant="constant")

        composed = witness | null

        mock_agent = lambda x: x
        result = await composed.verify(mock_agent, "input")

        # Should execute both probes
        assert len(result.entries) >= 2

    @pytest.mark.asyncio
    async def test_witness_in_pipeline(self):
        """Test WitnessProbe in agent pipeline."""
        probe = witness_probe(label="Pipeline")

        # Create simple agents
        class DoubleAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Double"

            async def invoke(self, x: int) -> int:
                return x * 2

        agent = DoubleAgent()

        # Compose: agent >> probe
        pipeline = agent >> probe

        result = await pipeline.invoke(5)

        # Should pass through
        assert result == 10

        # Should have captured
        probe.assert_captured(10)


class TestResetFunctionality:
    """Test reset for test isolation."""

    @pytest.mark.asyncio
    async def test_reset_clears_history(self):
        """Test that reset clears history."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")

        assert len(probe.history) == 2

        probe.reset()

        assert len(probe.history) == 0

    @pytest.mark.asyncio
    async def test_reset_clears_count(self):
        """Test that reset clears call count."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")

        assert probe.call_count == 2

        probe.reset()

        assert probe.call_count == 0

    @pytest.mark.asyncio
    async def test_reset_clears_trace(self):
        """Test that reset clears trace entries."""
        probe = witness_probe()

        await probe.invoke("a")

        # Should have trace entries
        assert len(probe._trace_entries) > 0

        probe.reset()

        # Should be cleared
        assert len(probe._trace_entries) == 0


class TestConstitutionalRewards:
    """Test constitutional reward calculation."""

    @pytest.mark.asyncio
    async def test_rewards_accumulate(self):
        """Test that rewards accumulate over invocations."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")
        await probe.invoke("c")

        # Should have accumulated rewards
        total_reward = sum(entry.reward.weighted_total for entry in probe._trace_entries)
        assert total_reward > 0

    @pytest.mark.asyncio
    async def test_verify_produces_synthesis_reward(self):
        """Test that verify produces synthesis reward."""
        probe = witness_probe(laws=["identity", "associativity"])

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # Should have synthesis entry with reward
        synthesis_entries = [e for e in trace.entries if e.action.name == "synthesize"]

        assert len(synthesis_entries) > 0
        assert synthesis_entries[0].reward.composable > 0


class TestEdgeCases:
    """Test edge cases."""

    @pytest.mark.asyncio
    async def test_verify_non_callable_agent(self):
        """Test verify with non-callable agent."""
        probe = witness_probe()

        # Non-callable (just a value)
        agent = "not callable"

        trace = await probe.verify(agent, "test")

        # Should default to identity
        assert trace.value.value == "test"

    @pytest.mark.asyncio
    async def test_empty_laws_list(self):
        """Test probe with no laws to check."""
        probe = witness_probe(laws=[])

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # No laws to verify, but should still work
        # Confidence should be 0 (no laws checked)
        # Actually, with empty laws, 0/0 = nan, but we handle with max(1, ...)
        # So confidence will be 0/1 = 0
        assert trace.value.confidence == 0.0

    @pytest.mark.asyncio
    async def test_compression_ratio_all_unique(self):
        """Test compression ratio when all observations unique."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("b")
        await probe.invoke("c")

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "test")

        # All unique: compression = 4/4 = 1.0
        # (3 invoke + 1 verify)
        state = trace.entries[-1].state_after
        assert state.compression_ratio <= 1.0

    @pytest.mark.asyncio
    async def test_compression_ratio_all_same(self):
        """Test compression ratio when all observations same."""
        probe = witness_probe()

        await probe.invoke("a")
        await probe.invoke("a")
        await probe.invoke("a")

        async def identity_agent(x):
            return x

        trace = await probe.verify(identity_agent, "a")

        # All same: compression = 1/4 = 0.25
        state = trace.entries[-1].state_after
        assert state.compression_ratio < 1.0
