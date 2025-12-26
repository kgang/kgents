"""
Tests for NullProbe.

The NullProbe is the constant morphism c_b: A → b.
It serves as ground truth for differential testing and identity law verification.

Tests cover:
1. Constant morphism property (always returns same output)
2. PolicyTrace emission with DP semantics
3. Constitutional reward calculation
4. Identity law verification
5. Timing delays
6. State transitions
"""

from __future__ import annotations

import asyncio
import time

import pytest

from agents.t.probes.null_probe import NullProbe, NullState, null_probe


class TestNullProbeBasics:
    """Basic NullProbe functionality tests."""

    def test_initialization(self):
        """Test creating a NullProbe."""
        probe = NullProbe(constant="constant_value", delay_ms=0)

        assert probe.constant == "constant_value"
        assert probe.delay_ms == 0
        assert probe.name == "NullProbe(output=constant_value)"

    def test_default_config(self):
        """Test NullProbe with default parameters."""
        probe = NullProbe(constant=None)

        assert probe.constant is None
        assert probe.delay_ms == 0

    @pytest.mark.asyncio
    async def test_constant_morphism_property(self):
        """Test that NullProbe always returns the same output."""
        probe = NullProbe(constant=42)

        # Different inputs should all produce the same output
        mock_agent = lambda x: x
        trace1 = await probe.verify(mock_agent, "input_1")
        trace2 = await probe.verify(mock_agent, "different_input")
        trace3 = await probe.verify(mock_agent, {"complex": "input"})

        assert trace1.value.value == 42
        assert trace2.value.value == 42
        assert trace3.value.value == 42

    @pytest.mark.asyncio
    async def test_returns_configured_output(self):
        """Test that NullProbe returns pre-configured output."""
        mock_agent = lambda x: x

        # Test with string
        probe_str = NullProbe(constant="test_string")
        trace = await probe_str.verify(mock_agent, "ignored")
        assert trace.value.value == "test_string"

        # Test with dict
        expected_dict = {"status": "ok", "value": 123}
        probe_dict = NullProbe(constant=expected_dict)
        trace = await probe_dict.verify(mock_agent, "ignored")
        assert trace.value.value == expected_dict

        # Test with None
        probe_none = NullProbe(constant=None)
        trace = await probe_none.verify(mock_agent, "ignored")
        assert trace.value.value is None


class TestNullProbeStateTransitions:
    """Test DP state transitions."""

    def test_states(self):
        """Test that NullProbe defines correct state space."""
        probe = NullProbe(constant=None)

        states = probe.states

        assert NullState.READY in states
        assert NullState.COMPUTING in states
        assert NullState.DONE in states
        assert len(states) == 3

    def test_actions_from_ready(self):
        """Test available actions from READY state."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        actions = probe.actions(NullState.READY)

        assert ProbeAction("invoke") in actions
        assert len(actions) == 1

    def test_actions_from_other_states(self):
        """Test no actions available from non-READY states."""
        probe = NullProbe(constant=None)

        assert len(probe.actions(NullState.COMPUTING)) == 0
        assert len(probe.actions(NullState.DONE)) == 0

    def test_transition_ready_to_computing(self):
        """Test state transition: READY → COMPUTING."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        next_state = probe.transition(NullState.READY, ProbeAction("invoke"))

        assert next_state == NullState.COMPUTING

    def test_transition_computing_to_done(self):
        """Test state transition: COMPUTING → DONE."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        next_state = probe.transition(NullState.COMPUTING, ProbeAction("anything"))

        assert next_state == NullState.DONE

    def test_transition_done_stays_done(self):
        """Test that DONE state is terminal."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        next_state = probe.transition(NullState.DONE, ProbeAction("anything"))

        assert next_state == NullState.DONE


class TestNullProbeReward:
    """Test constitutional reward calculation."""

    def test_reward_for_invoke_from_ready(self):
        """Test reward for invoke action from READY state."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        reward = probe.reward(
            NullState.READY, ProbeAction("invoke"), NullState.COMPUTING
        )

        # NullProbe should get positive reward for:
        # - ETHICAL: deterministic, predictable (1.0)
        # - COMPOSABLE: satisfies identity law (1.0)
        # - GENERATIVE: minimal but present (0.5)
        assert reward.ethical == 1.0
        assert reward.composable == 1.0
        assert reward.generative == 0.5
        assert reward.weighted_total > 0.0

    def test_zero_reward_for_other_transitions(self):
        """Test that non-invoke transitions get no reward."""
        from agents.t.truth_functor import ProbeAction

        probe = NullProbe(constant=None)

        # Wrong state
        reward1 = probe.reward(
            NullState.COMPUTING, ProbeAction("invoke"), NullState.DONE
        )
        assert reward1.weighted_total == 0.0

        reward2 = probe.reward(
            NullState.DONE, ProbeAction("invoke"), NullState.DONE
        )
        assert reward2.weighted_total == 0.0

        # Wrong action from READY
        reward3 = probe.reward(
            NullState.READY, ProbeAction("other_action"), NullState.READY
        )
        assert reward3.weighted_total == 0.0


class TestNullProbeTrace:
    """Test PolicyTrace emission."""

    @pytest.mark.asyncio
    async def test_emits_trace(self):
        """Test that NullProbe emits PolicyTrace with entries."""
        probe = NullProbe(constant="result")

        # Verify probe
        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "input")

        assert trace.value.value == "result"
        assert len(trace.entries) >= 1

    @pytest.mark.asyncio
    async def test_trace_entry_content(self):
        """Test trace entry contains correct information."""
        probe = NullProbe(constant=42)

        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "test_input")

        # Check verdict
        assert trace.value.value == 42
        assert trace.value.passed is True
        assert trace.value.confidence == 1.0
        assert "constant morphism" in trace.value.reasoning.lower()

        # Check trace entries
        assert len(trace.entries) >= 1
        entry = trace.entries[0]
        assert "constant morphism" in entry.reasoning.lower()

    @pytest.mark.asyncio
    async def test_multiple_invocations_produce_traces(self):
        """Test that multiple invocations each produce traces."""
        probe = NullProbe(constant="result")

        mock_agent = lambda x: x
        trace1 = await probe.verify(mock_agent, "input1")
        trace2 = await probe.verify(mock_agent, "input2")
        trace3 = await probe.verify(mock_agent, "input3")

        # Each trace should have the same constant value
        assert trace1.value.value == "result"
        assert trace2.value.value == "result"
        assert trace3.value.value == "result"

        # Each should have entries
        assert len(trace1.entries) >= 1
        assert len(trace2.entries) >= 1
        assert len(trace3.entries) >= 1


class TestNullProbeTiming:
    """Test timing and delay functionality."""

    @pytest.mark.asyncio
    async def test_zero_delay(self):
        """Test that zero delay executes immediately."""
        probe = NullProbe(constant="fast", delay_ms=0)

        mock_agent = lambda x: x
        start = time.time()
        await probe.verify(mock_agent, "input")
        elapsed = time.time() - start

        # Should be nearly instant (< 10ms)
        assert elapsed < 0.01

    @pytest.mark.asyncio
    async def test_with_delay(self):
        """Test that delay_ms adds appropriate latency."""
        probe = NullProbe(constant="slow", delay_ms=50)

        mock_agent = lambda x: x
        start = time.time()
        await probe.verify(mock_agent, "input")
        elapsed = time.time() - start

        # Should take at least 50ms
        assert elapsed >= 0.05
        # But not too much longer (< 100ms total)
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_delay_does_not_affect_result(self):
        """Test that delay doesn't change the constant output."""
        probe = NullProbe(constant="constant", delay_ms=20)

        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "input")

        assert trace.value.value == "constant"


class TestNullProbeImmutability:
    """Test that NullProbe is immutable."""

    def test_frozen_dataclass(self):
        """Test that NullProbe is a frozen dataclass."""
        probe = NullProbe(constant="test")

        # Should not be able to modify fields
        with pytest.raises(Exception):  # FrozenInstanceError
            probe.constant = "modified"  # type: ignore

    @pytest.mark.asyncio
    async def test_verify_is_pure(self):
        """Test that verify() is pure (no side effects)."""
        probe = NullProbe(constant="result")

        mock_agent = lambda x: x

        # Call verify multiple times
        trace1 = await probe.verify(mock_agent, "input")
        trace2 = await probe.verify(mock_agent, "input")

        # Both should produce the same result
        assert trace1.value.value == trace2.value.value
        assert trace1.value.passed == trace2.value.passed
        assert trace1.value.confidence == trace2.value.confidence


class TestNullProbeIdentityLaw:
    """Test identity law verification."""

    @pytest.mark.asyncio
    async def test_constant_morphism_property(self):
        """Test that NullProbe satisfies constant morphism property."""
        probe = NullProbe(constant="constant")

        mock_agent = lambda x: x

        # Identity law: Id >> NullProbe(x) ≡ NullProbe(x)
        # For NullProbe, this is trivially true (constant morphism)
        # The output is always the constant, regardless of input
        trace = await probe.verify(mock_agent, "any_input")
        assert trace.value.value == "constant"
        assert trace.value.passed is True

    @pytest.mark.asyncio
    async def test_identity_law_with_different_outputs(self):
        """Test identity law holds for different output values."""
        mock_agent = lambda x: x

        probe_str = NullProbe(constant="string")
        trace_str = await probe_str.verify(mock_agent, "input")
        assert trace_str.value.value == "string"
        assert trace_str.value.passed is True

        probe_int = NullProbe(constant=42)
        trace_int = await probe_int.verify(mock_agent, "input")
        assert trace_int.value.value == 42
        assert trace_int.value.passed is True

        probe_none = NullProbe(constant=None)
        trace_none = await probe_none.verify(mock_agent, "input")
        assert trace_none.value.value is None
        assert trace_none.value.passed is True


class TestNullProbeConvenienceFunction:
    """Test the null_probe() convenience function."""

    @pytest.mark.asyncio
    async def test_null_probe_function(self):
        """Test creating NullProbe via convenience function."""
        probe = null_probe(constant=42, delay_ms=0)

        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "input")
        assert trace.value.value == 42
        assert probe.delay_ms == 0

    @pytest.mark.asyncio
    async def test_null_probe_default_args(self):
        """Test null_probe() with default arguments."""
        probe = null_probe()

        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "input")
        assert trace.value.value is None
        assert probe.delay_ms == 0


class TestNullProbeEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_with_complex_output_type(self):
        """Test NullProbe with complex output types."""
        complex_output = {
            "nested": {
                "data": [1, 2, 3],
                "metadata": {"type": "test"}
            }
        }

        probe = NullProbe(constant=complex_output)

        mock_agent = lambda x: x
        trace = await probe.verify(mock_agent, "input")

        assert trace.value.value == complex_output
        assert trace.value.value is complex_output  # Same object reference

    @pytest.mark.asyncio
    async def test_concurrent_invocations(self):
        """Test that multiple concurrent invocations work correctly."""
        probe = NullProbe(constant="result", delay_ms=10)

        mock_agent = lambda x: x

        # Run 5 concurrent invocations
        traces = await asyncio.gather(
            probe.verify(mock_agent, "input1"),
            probe.verify(mock_agent, "input2"),
            probe.verify(mock_agent, "input3"),
            probe.verify(mock_agent, "input4"),
            probe.verify(mock_agent, "input5"),
        )

        # All should return the same constant
        assert all(t.value.value == "result" for t in traces)
        # Each should have passed
        assert all(t.value.passed for t in traces)

    @pytest.mark.asyncio
    async def test_with_large_delay(self):
        """Test probe with larger delay (performance baseline)."""
        probe = NullProbe(constant="slow", delay_ms=100)

        mock_agent = lambda x: x
        start = time.time()
        trace = await probe.verify(mock_agent, "input")
        elapsed = time.time() - start

        assert trace.value.value == "slow"
        assert elapsed >= 0.1  # At least 100ms
