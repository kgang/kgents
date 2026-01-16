#!/usr/bin/env python3
"""
Test script for TruthFunctor probes.

Verifies all five probe types can be instantiated and have the required interface.
"""

import pytest

# Import directly from module files
from agents.t.probes.chaos_probe import ChaosConfig, ChaosProbe, ChaosType
from agents.t.probes.judge_probe import JudgeConfig, JudgeProbe, JudgmentCriteria
from agents.t.probes.null_probe import NullProbe
from agents.t.probes.trust_probe import Proposal, TrustConfig, TrustDecision, TrustProbe
from agents.t.probes.witness_probe import WitnessConfig, WitnessProbe


# Mock agent for testing probes that need an agent
class MockAgent:
    """Simple mock agent for probe testing."""

    async def invoke(self, input):
        """Return input unchanged (identity agent)."""
        return input


@pytest.mark.asyncio
async def test_null_probe():
    """Test NullProbe instantiation and interface."""
    print("\n=== NullProbe (EPISTEMIC) ===")
    # NullProbe is a dataclass with `constant` and `delay_ms` fields directly
    probe = NullProbe(constant="constant", delay_ms=10)
    print(f"Name: {probe.name}")
    # states is a property returning frozenset, not a method
    print(f"States: {probe.states}")
    print(f"Actions (READY): {probe.actions(list(probe.states)[0])}")

    # Test verify (NullProbe uses verify, not invoke directly)
    agent = MockAgent()
    trace = await probe.verify(agent, "ignored input")
    print(f"Verify result: {trace.value.value}")
    assert trace.value.value == "constant", "NullProbe should return constant output"
    assert trace.value.passed, "NullProbe should always pass"

    print("NullProbe passed all tests")


@pytest.mark.asyncio
async def test_chaos_probe():
    """Test ChaosProbe instantiation and interface."""
    print("\n=== ChaosProbe (DIALECTICAL) ===")
    # ChaosConfig uses `intensity` not `probability`
    probe = ChaosProbe(
        ChaosConfig(
            chaos_type=ChaosType.NOISE,
            intensity=0.3,
            seed=42,
        )
    )
    print(f"Name: {probe.name}")
    # states is a property returning frozenset, not a method
    print(f"States: {probe.states}")
    print(f"Actions (READY): {probe.actions(list(probe.states)[0])}")

    # Test verify (ChaosProbe uses verify, not invoke directly)
    agent = MockAgent()
    trace = await probe.verify(agent, "test")
    print(f"Verify result: passed={trace.value.passed}")
    print(f"Verdict reasoning: {trace.value.reasoning}")

    print("ChaosProbe passed all tests")


@pytest.mark.asyncio
async def test_witness_probe():
    """Test WitnessProbe instantiation and interface."""
    print("\n=== WitnessProbe (CATEGORICAL) ===")
    probe = WitnessProbe(WitnessConfig(label="TestWitness", max_history=10))
    print(f"Name: {probe.name}")
    # states is a property returning frozenset, not a method
    print(f"States: {probe.states}")
    print(f"Actions (OBSERVING): {probe.actions(list(probe.states)[0])}")

    # Test invoke (WitnessProbe has invoke for transparent observation)
    result = await probe.invoke("data")
    print(f"Invoke result: {result}")
    assert result == "data", "WitnessProbe should be identity morphism"

    # Test history
    assert "data" in probe.history, "WitnessProbe should capture input"
    probe.assert_captured("data")
    probe.assert_count(1)

    # Test verify
    agent = MockAgent()
    trace = await probe.verify(agent, "test_input")
    print(f"Verify result: passed={trace.value.passed}")
    assert trace.value.passed, "WitnessProbe should satisfy categorical laws"
    print("WitnessProbe passed all tests")


@pytest.mark.asyncio
async def test_judge_probe():
    """Test JudgeProbe instantiation and interface."""
    print("\n=== JudgeProbe (EPISTEMIC) ===")
    criteria = JudgmentCriteria(correctness=1.0, safety=1.0, style=0.3)
    probe = JudgeProbe(JudgeConfig(criteria=criteria, threshold=0.8))
    print(f"Name: {probe.name}")
    # states is a property returning frozenset, not a method
    print(f"States: {probe.states}")
    print(f"Actions (READY): {probe.actions(list(probe.states)[0])}")

    # Test verify (JudgeProbe uses verify with (intent, output) tuple)
    agent = MockAgent()
    trace = await probe.verify(agent, ("Fix bug", "Bug fixed successfully"))
    result = trace.value.value  # JudgmentResult is in verdict.value
    print(f"Verify result: {result.weighted_score:.3f}")
    print(f"  Correctness: {result.correctness:.3f}")
    print(f"  Safety: {result.safety:.3f}")
    print(f"  Style: {result.style:.3f}")
    print(f"  Reasoning: {result.reasoning}")
    print(f"  Passed: {trace.value.passed}")

    print("JudgeProbe passed all tests")


@pytest.mark.asyncio
async def test_trust_probe():
    """Test TrustProbe instantiation and interface."""
    print("\n=== TrustProbe (GENERATIVE) ===")
    # TrustConfig uses:
    # - capital_stake (not initial_capital)
    # - threshold (not regenerability_threshold)
    # - risk_threshold (not galois_threshold)
    probe = TrustProbe(
        TrustConfig(
            capital_stake=1.0,
            threshold=0.8,
            risk_threshold=0.2,
        )
    )
    print(f"Name: {probe.name}")
    # states is a property returning frozenset, not a method
    print(f"States: {probe.states}")
    print(f"Actions (READY): {probe.actions(list(probe.states)[0])}")

    # Test verify with good proposal
    # Proposal uses `risk` field (not galois_loss)
    proposal = Proposal(
        agent="test-agent",
        action="refactor",
        diff="Clean up module structure",
        risk=0.15,
    )
    agent = MockAgent()
    trace = await probe.verify(agent, proposal)
    result = trace.value.value  # TrustDecision is in verdict.value
    print(f"Verify result: approved={result.approved}, bypassed={result.bypassed}")
    # TrustDecision has `regenerable` (boolean) not `regenerability_score`
    print(f"  Regenerable: {result.regenerable}")
    if result.galois_loss is not None:
        print(f"  Galois loss: {result.galois_loss:.3f}")
    else:
        print("  Galois loss: N/A")
    print(f"  Reason: {result.reason}")
    print(f"  Capital: {probe.current_capital:.3f}")
    print(f"  Passed: {trace.value.passed}")

    print("TrustProbe passed all tests")


@pytest.mark.asyncio
async def test_all_probes():
    """Run all probe tests."""
    print("=" * 60)
    print("Testing TruthFunctor Probes")
    print("=" * 60)

    await test_null_probe()
    await test_chaos_probe()
    await test_witness_probe()
    await test_judge_probe()
    await test_trust_probe()

    print("\n" + "=" * 60)
    print("All probe tests passed!")
    print("=" * 60)
    print("\nTruthFunctor Interface Summary:")
    print("  - states: Returns DP state space (property)")
    print("  - actions(s): Returns available actions from state s")
    print("  - transition(s, a): Returns next state after action")
    print("  - reward(s, a): Returns constitutional reward")
    print("  - verify(): Verifies categorical laws, returns PolicyTrace")
    print("\nFive Probe Types:")
    print("  1. NullProbe (EPISTEMIC) - Constant morphism for ground truth")
    print("  2. ChaosProbe (DIALECTICAL) - Perturbation for resilience testing")
    print("  3. WitnessProbe (CATEGORICAL) - Observer for law verification")
    print("  4. JudgeProbe (EPISTEMIC) - LLM-as-Judge for semantic truth")
    print("  5. TrustProbe (GENERATIVE) - Capital-backed regenerability gate")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_all_probes())
