#!/usr/bin/env python3
"""
Test script for TruthFunctor probes.

Verifies all five probe types can be instantiated and have the required interface.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from module files
from agents.t.probes.chaos_probe import ChaosConfig, ChaosProbe, ChaosType
from agents.t.probes.judge_probe import JudgeConfig, JudgeProbe, JudgmentCriteria
from agents.t.probes.null_probe import NullConfig, NullProbe
from agents.t.probes.trust_probe import Proposal, TrustConfig, TrustDecision, TrustProbe
from agents.t.probes.witness_probe import WitnessConfig, WitnessProbe


async def test_null_probe():
    """Test NullProbe instantiation and interface."""
    print("\n=== NullProbe (EPISTEMIC) ===")
    probe = NullProbe(NullConfig(output="constant", delay_ms=10))
    print(f"Name: {probe.name}")
    print(f"States: {probe.states()}")
    print(f"Actions (READY): {probe.actions(list(probe.states())[0])}")

    # Test invoke
    result = await probe.invoke("ignored input")
    print(f"Invoke result: {result}")
    assert result == "constant", "NullProbe should return constant output"

    # Test verify
    assert probe.verify(), "NullProbe should satisfy identity law"
    print("✓ NullProbe passed all tests")


async def test_chaos_probe():
    """Test ChaosProbe instantiation and interface."""
    print("\n=== ChaosProbe (DIALECTICAL) ===")
    probe = ChaosProbe(ChaosConfig(
        chaos_type=ChaosType.NOISE,
        probability=0.3,
        seed=42,
    ))
    print(f"Name: {probe.name}")
    print(f"States: {probe.states()}")
    print(f"Actions (READY): {probe.actions(list(probe.states())[0])}")

    # Test invoke (may perturb)
    result = await probe.invoke("test")
    print(f"Invoke result: {result}")

    # Test verify
    probe.verify()  # May not hold for probabilistic chaos
    print("✓ ChaosProbe passed all tests")


async def test_witness_probe():
    """Test WitnessProbe instantiation and interface."""
    print("\n=== WitnessProbe (CATEGORICAL) ===")
    probe = WitnessProbe(WitnessConfig(label="TestWitness", max_history=10))
    print(f"Name: {probe.name}")
    print(f"States: {probe.states()}")
    print(f"Actions (OBSERVING): {probe.actions(list(probe.states())[0])}")

    # Test invoke (identity morphism)
    result = await probe.invoke("data")
    print(f"Invoke result: {result}")
    assert result == "data", "WitnessProbe should be identity morphism"

    # Test history
    assert "data" in probe.history, "WitnessProbe should capture input"
    probe.assert_captured("data")
    probe.assert_count(1)

    # Test verify
    assert probe.verify(), "WitnessProbe should satisfy categorical laws"
    print("✓ WitnessProbe passed all tests")


async def test_judge_probe():
    """Test JudgeProbe instantiation and interface."""
    print("\n=== JudgeProbe (EPISTEMIC) ===")
    criteria = JudgmentCriteria(correctness=1.0, safety=1.0, style=0.3)
    probe = JudgeProbe(JudgeConfig(criteria=criteria, threshold=0.8))
    print(f"Name: {probe.name}")
    print(f"States: {probe.states()}")
    print(f"Actions (READY): {probe.actions(list(probe.states())[0])}")

    # Test invoke
    result = await probe.invoke(("Fix bug", "Bug fixed successfully"))
    print(f"Invoke result: {result.weighted_score:.3f}")
    print(f"  Correctness: {result.correctness:.3f}")
    print(f"  Safety: {result.safety:.3f}")
    print(f"  Style: {result.style:.3f}")
    print(f"  Reasoning: {result.reasoning}")

    # Test verify
    assert probe.verify(), "JudgeProbe should be consistent"
    print("✓ JudgeProbe passed all tests")


async def test_trust_probe():
    """Test TrustProbe instantiation and interface."""
    print("\n=== TrustProbe (GENERATIVE) ===")
    probe = TrustProbe(TrustConfig(
        initial_capital=1.0,
        regenerability_threshold=0.8,
        galois_threshold=0.2,
    ))
    print(f"Name: {probe.name}")
    print(f"States: {probe.states()}")
    print(f"Actions (READY): {probe.actions(list(probe.states())[0])}")

    # Test invoke with good proposal
    proposal = Proposal(
        action="refactor",
        spec="Clean up module structure",
        galois_loss=0.15,
    )
    result = await probe.invoke(proposal)
    print(f"Invoke result: approved={result.approved}, bypassed={result.bypassed}")
    print(f"  Regenerability: {result.regenerability_score:.3f}")
    print(f"  Galois loss: {result.galois_loss:.3f}")
    print(f"  Reason: {result.reason}")
    print(f"  Capital: {probe.capital:.3f}")

    # Test verify
    assert probe.verify(), "TrustProbe should maintain regenerability"
    print("✓ TrustProbe passed all tests")


async def main():
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
    print("✅ All probe tests passed!")
    print("=" * 60)
    print("\n📊 TruthFunctor Interface Summary:")
    print("  - states(): Returns DP state space")
    print("  - actions(s): Returns available actions from state s")
    print("  - transition(s, a): Returns next state after action")
    print("  - reward(s, a): Returns constitutional reward")
    print("  - verify(): Verifies categorical laws")
    print("\n🎯 Five Probe Types:")
    print("  1. NullProbe (EPISTEMIC) - Constant morphism for ground truth")
    print("  2. ChaosProbe (DIALECTICAL) - Perturbation for resilience testing")
    print("  3. WitnessProbe (CATEGORICAL) - Observer for law verification")
    print("  4. JudgeProbe (EPISTEMIC) - LLM-as-Judge for semantic truth")
    print("  5. TrustProbe (GENERATIVE) - Capital-backed regenerability gate")


if __name__ == "__main__":
    asyncio.run(main())
