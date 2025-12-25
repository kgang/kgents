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

import pytest
import asyncio
import time

from agents.t.probes.null_probe import NullProbe, NullConfig, NullState


class TestNullProbeBasics:
    """Basic NullProbe functionality tests."""

    def test_initialization(self):
        """Test creating a NullProbe."""
        config = NullConfig(output="constant_value", delay_ms=0)
        probe = NullProbe(config)

        assert probe.config.output == "constant_value"
        assert probe.config.delay_ms == 0
        assert probe.name == "NullProbe(output=constant_value)"
        assert probe.__is_test__ is True

    def test_default_config(self):
        """Test NullProbe with default config."""
        config = NullConfig()
        probe = NullProbe(config)

        assert probe.config.output is None
        assert probe.config.delay_ms == 0

    @pytest.mark.asyncio
    async def test_constant_morphism_property(self):
        """Test that NullProbe always returns the same output."""
        config = NullConfig(output=42)
        probe = NullProbe(config)

        # Different inputs should all produce the same output
        result1 = await probe.invoke("input_1")
        result2 = await probe.invoke("different_input")
        result3 = await probe.invoke({"complex": "input"})

        assert result1 == 42
        assert result2 == 42
        assert result3 == 42

    @pytest.mark.asyncio
    async def test_returns_configured_output(self):
        """Test that NullProbe returns pre-configured output."""
        # Test with string
        probe_str = NullProbe(NullConfig(output="test_string"))
        assert await probe_str.invoke("ignored") == "test_string"

        # Test with dict
        expected_dict = {"status": "ok", "value": 123}
        probe_dict = NullProbe(NullConfig(output=expected_dict))
        assert await probe_dict.invoke("ignored") == expected_dict

        # Test with None
        probe_none = NullProbe(NullConfig(output=None))
        assert await probe_none.invoke("ignored") is None


class TestNullProbeStateTransitions:
    """Test DP state transitions."""

    def test_states(self):
        """Test that NullProbe defines correct state space."""
        probe = NullProbe(NullConfig())

        states = probe.states()

        assert NullState.READY in states
        assert NullState.COMPUTING in states
        assert NullState.DONE in states
        assert len(states) == 3

    def test_actions_from_ready(self):
        """Test available actions from READY state."""
        probe = NullProbe(NullConfig())

        actions = probe.actions(NullState.READY)

        assert "invoke" in actions
        assert len(actions) == 1

    def test_actions_from_other_states(self):
        """Test no actions available from non-READY states."""
        probe = NullProbe(NullConfig())

        assert len(probe.actions(NullState.COMPUTING)) == 0
        assert len(probe.actions(NullState.DONE)) == 0

    def test_transition_ready_to_computing(self):
        """Test state transition: READY → COMPUTING."""
        probe = NullProbe(NullConfig())

        next_state = probe.transition(NullState.READY, "invoke")

        assert next_state == NullState.COMPUTING

    def test_transition_computing_to_done(self):
        """Test state transition: COMPUTING → DONE."""
        probe = NullProbe(NullConfig())

        next_state = probe.transition(NullState.COMPUTING, "anything")

        assert next_state == NullState.DONE

    def test_transition_done_stays_done(self):
        """Test that DONE state is terminal."""
        probe = NullProbe(NullConfig())

        next_state = probe.transition(NullState.DONE, "anything")

        assert next_state == NullState.DONE


class TestNullProbeReward:
    """Test constitutional reward calculation."""

    def test_reward_for_invoke_from_ready(self):
        """Test reward for invoke action from READY state."""
        probe = NullProbe(NullConfig())

        reward = probe.reward(NullState.READY, "invoke")

        # NullProbe should get positive reward for:
        # - ETHICAL: deterministic, predictable (Principle.ETHICAL.weight = 2.0)
        # - COMPOSABLE: satisfies identity law (Principle.COMPOSABLE.weight = 1.5)
        assert reward > 0.0
        # Exact value is sum of weights: 2.0 + 1.5 = 3.5
        assert reward == pytest.approx(3.5)

    def test_zero_reward_for_other_transitions(self):
        """Test that non-invoke transitions get no reward."""
        probe = NullProbe(NullConfig())

        # Wrong state
        assert probe.reward(NullState.COMPUTING, "invoke") == 0.0
        assert probe.reward(NullState.DONE, "invoke") == 0.0

        # Wrong action from READY
        assert probe.reward(NullState.READY, "other_action") == 0.0


class TestNullProbeTrace:
    """Test PolicyTrace emission."""

    @pytest.mark.asyncio
    async def test_emits_trace(self):
        """Test that NullProbe emits PolicyTrace with entries."""
        probe = NullProbe(NullConfig(output="result"))

        # Invoke probe
        await probe.invoke("input")

        # Get trace
        trace = await probe.get_trace()

        assert trace.value == "result"
        assert len(trace.log) == 1

    @pytest.mark.asyncio
    async def test_trace_entry_content(self):
        """Test trace entry contains correct information."""
        probe = NullProbe(NullConfig(output=42))

        await probe.invoke("test_input")

        trace = await probe.get_trace()
        entry = trace.log[0]

        # Check entry fields
        assert entry.state_before == NullState.READY
        assert entry.action == "invoke"
        assert entry.state_after == NullState.DONE
        assert entry.value == pytest.approx(3.5)  # ethical + composable weights
        assert "Constant morphism" in entry.rationale
        assert "42" in entry.rationale

    @pytest.mark.asyncio
    async def test_multiple_invocations_accumulate_trace(self):
        """Test that multiple invocations accumulate in trace log."""
        probe = NullProbe(NullConfig(output="result"))

        await probe.invoke("input1")
        await probe.invoke("input2")
        await probe.invoke("input3")

        trace = await probe.get_trace()

        assert len(trace.log) == 3
        # All should have same value (constant morphism)
        for entry in trace.log:
            assert entry.value == pytest.approx(3.5)

    @pytest.mark.asyncio
    async def test_call_count(self):
        """Test call_count tracks invocations."""
        probe = NullProbe(NullConfig())

        assert probe.call_count == 0

        await probe.invoke("input1")
        assert probe.call_count == 1

        await probe.invoke("input2")
        assert probe.call_count == 2

        await probe.invoke("input3")
        assert probe.call_count == 3


class TestNullProbeTiming:
    """Test timing and delay functionality."""

    @pytest.mark.asyncio
    async def test_zero_delay(self):
        """Test that zero delay executes immediately."""
        probe = NullProbe(NullConfig(output="fast", delay_ms=0))

        start = time.time()
        await probe.invoke("input")
        elapsed = time.time() - start

        # Should be nearly instant (< 10ms)
        assert elapsed < 0.01

    @pytest.mark.asyncio
    async def test_with_delay(self):
        """Test that delay_ms adds appropriate latency."""
        probe = NullProbe(NullConfig(output="slow", delay_ms=50))

        start = time.time()
        await probe.invoke("input")
        elapsed = time.time() - start

        # Should take at least 50ms
        assert elapsed >= 0.05
        # But not too much longer (< 100ms total)
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_delay_does_not_affect_result(self):
        """Test that delay doesn't change the constant output."""
        probe = NullProbe(NullConfig(output="constant", delay_ms=20))

        result = await probe.invoke("input")

        assert result == "constant"


class TestNullProbeReset:
    """Test reset functionality for test isolation."""

    @pytest.mark.asyncio
    async def test_reset_clears_trace(self):
        """Test that reset() clears the trace log."""
        probe = NullProbe(NullConfig(output="test"))

        # Accumulate some trace
        await probe.invoke("input1")
        await probe.invoke("input2")

        assert probe.call_count == 2

        # Reset
        probe.reset()

        # Trace should be empty
        assert probe.call_count == 0
        trace = await probe.get_trace()
        assert len(trace.log) == 0

    @pytest.mark.asyncio
    async def test_reset_restores_ready_state(self):
        """Test that reset() returns probe to READY state."""
        probe = NullProbe(NullConfig(output="test"))

        await probe.invoke("input")

        # Reset
        probe.reset()

        # Should be back to READY
        # We can't access _state directly, but we can invoke again
        result = await probe.invoke("input")
        assert result == "test"

    @pytest.mark.asyncio
    async def test_reset_between_tests(self):
        """Test reset enables test isolation."""
        probe = NullProbe(NullConfig(output="test"))

        # Test 1
        await probe.invoke("input1")
        assert probe.call_count == 1

        # Reset for Test 2
        probe.reset()

        # Test 2
        await probe.invoke("input2")
        assert probe.call_count == 1  # Count reset, not 2


class TestNullProbeIdentityLaw:
    """Test identity law verification."""

    def test_verify_identity_law(self):
        """Test that NullProbe satisfies identity law."""
        probe = NullProbe(NullConfig(output="constant"))

        # Identity law: Id >> NullProbe(x) ≡ NullProbe(x)
        # For NullProbe, this is trivially true (constant morphism)
        assert probe.verify() is True

    def test_identity_law_with_different_outputs(self):
        """Test identity law holds for different output values."""
        probe_str = NullProbe(NullConfig(output="string"))
        probe_int = NullProbe(NullConfig(output=42))
        probe_none = NullProbe(NullConfig(output=None))

        assert probe_str.verify() is True
        assert probe_int.verify() is True
        assert probe_none.verify() is True


class TestNullProbeConvenienceFunction:
    """Test the null_probe() convenience function."""

    @pytest.mark.asyncio
    async def test_null_probe_function(self):
        """Test creating NullProbe via convenience function."""
        from agents.t.probes.null_probe import null_probe

        probe = null_probe(output=42, delay_ms=0)

        assert await probe.invoke("input") == 42
        assert probe.config.delay_ms == 0

    @pytest.mark.asyncio
    async def test_null_probe_default_args(self):
        """Test null_probe() with default arguments."""
        from agents.t.probes.null_probe import null_probe

        probe = null_probe()

        assert await probe.invoke("input") is None
        assert probe.config.delay_ms == 0


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

        probe = NullProbe(NullConfig(output=complex_output))

        result = await probe.invoke("input")

        assert result == complex_output
        assert result is complex_output  # Same object reference

    @pytest.mark.asyncio
    async def test_concurrent_invocations(self):
        """Test that multiple concurrent invocations work correctly."""
        probe = NullProbe(NullConfig(output="result", delay_ms=10))

        # Run 5 concurrent invocations
        results = await asyncio.gather(
            probe.invoke("input1"),
            probe.invoke("input2"),
            probe.invoke("input3"),
            probe.invoke("input4"),
            probe.invoke("input5"),
        )

        # All should return the same constant
        assert all(r == "result" for r in results)
        # Should have 5 trace entries
        assert probe.call_count == 5

    @pytest.mark.asyncio
    async def test_with_large_delay(self):
        """Test probe with larger delay (performance baseline)."""
        probe = NullProbe(NullConfig(output="slow", delay_ms=100))

        start = time.time()
        result = await probe.invoke("input")
        elapsed = time.time() - start

        assert result == "slow"
        assert elapsed >= 0.1  # At least 100ms
