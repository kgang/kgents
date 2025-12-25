#!/usr/bin/env python
"""
Standalone verification script for constitutional reward system.

This tests the constitution module without requiring the full kgents environment.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Now import
from services.categorical.constitution import (
    PRINCIPLE_WEIGHTS,
    Constitution,
    ConstitutionalEvaluation,
    Principle,
    ProbeRewards,
)
from services.categorical.dp_bridge import Principle as DPPrinciple

print("=" * 70)
print("Constitutional Reward System Verification")
print("=" * 70)
print()

# Verify Principle is correctly imported
assert Principle == DPPrinciple, "Principle should be imported from dp_bridge"
print("✓ Principle correctly imported from dp_bridge")

# Verify all 7 principles have weights
assert len(PRINCIPLE_WEIGHTS) == 7, "Should have 7 principle weights"
print(f"✓ All 7 principles have weights")
for principle, weight in PRINCIPLE_WEIGHTS.items():
    print(f"  {principle.name}: {weight}")
print()

# Test 1: Basic constitutional evaluation
print("Test 1: Basic Constitutional Evaluation")
print("-" * 70)
eval = Constitution.evaluate("state", "action", "state_after")
assert isinstance(eval, ConstitutionalEvaluation)
assert len(eval.scores) == 7, "Should return scores for all 7 principles"
assert 0.0 <= eval.weighted_total <= 1.0, "Total should be in [0, 1]"
print(f"✓ Evaluation complete")
print(f"  Total score: {eval.weighted_total:.3f}")
print(f"  Min score: {eval.min_score:.3f}")
print(f"  Max score: {eval.max_score:.3f}")
print()

# Test 2: Context-aware evaluation
print("Test 2: Context-Aware Evaluation")
print("-" * 70)
eval_joy = Constitution.evaluate(
    "state",
    "solve",
    "state_after",
    context={"joyful": True, "joy_evidence": "Elegant"},
)
joy_score = eval_joy.by_principle[Principle.JOY_INDUCING]
assert joy_score >= 0.9, "Explicit joy should get high score"
print(f"✓ JOY_INDUCING with explicit marker: {joy_score:.3f}")

eval_ethical = Constitution.evaluate(
    "state",
    "action",
    "state_after",
    context={"deterministic": True, "preserves_human_agency": True},
)
ethical_score = eval_ethical.by_principle[Principle.ETHICAL]
assert ethical_score >= 0.8, "Deterministic + agency should get high ethical score"
print(f"✓ ETHICAL with deterministic + agency: {ethical_score:.3f}")
print()

# Test 3: Probe rewards
print("Test 3: Probe-Specific Rewards")
print("-" * 70)

# Monad probe
monad_eval = ProbeRewards.monad_probe_reward("s", "a", "s_", True, True)
assert monad_eval.by_principle[Principle.COMPOSABLE] == 1.0
assert monad_eval.by_principle[Principle.ETHICAL] == 1.0
print(f"✓ MonadProbe (laws satisfied): COMPOSABLE=1.0, ETHICAL=1.0")

monad_eval_fail = ProbeRewards.monad_probe_reward("s", "a", "s_", False, False)
assert monad_eval_fail.by_principle[Principle.COMPOSABLE] == 0.0
print(f"✓ MonadProbe (laws violated): COMPOSABLE=0.0")

# Sheaf probe
sheaf_eval = ProbeRewards.sheaf_probe_reward("s", "a", "s_", 1.0, 0)
assert sheaf_eval.by_principle[Principle.ETHICAL] == 1.0
assert sheaf_eval.by_principle[Principle.GENERATIVE] == 1.0
assert sheaf_eval.by_principle[Principle.COMPOSABLE] == 1.0
print(f"✓ SheafProbe (coherent): ETHICAL=1.0, GENERATIVE=1.0")

sheaf_eval_fail = ProbeRewards.sheaf_probe_reward("s", "a", "s_", 0.3, 5)
assert sheaf_eval_fail.by_principle[Principle.ETHICAL] == 0.3
print(f"✓ SheafProbe (violations): ETHICAL=0.3")

# Null probe
null_eval = ProbeRewards.null_probe_reward("s", "a", "s_")
assert null_eval.by_principle[Principle.ETHICAL] == 1.0
assert null_eval.by_principle[Principle.COMPOSABLE] == 1.0
print(f"✓ NullProbe: ETHICAL=1.0, COMPOSABLE=1.0")

# Chaos probe
chaos_eval_survived = ProbeRewards.chaos_probe_reward("s", "a", "s_", survived=True)
assert chaos_eval_survived.by_principle[Principle.ETHICAL] == 1.0
print(f"✓ ChaosProbe (survived): ETHICAL=1.0")

chaos_eval_failed = ProbeRewards.chaos_probe_reward("s", "a", "s_", survived=False)
assert chaos_eval_failed.by_principle[Principle.ETHICAL] == 0.5
print(f"✓ ChaosProbe (failed): ETHICAL=0.5")
print()

# Test 4: Serialization
print("Test 4: Serialization")
print("-" * 70)
eval_dict = eval.to_dict()
assert "weighted_total" in eval_dict
assert "scores" in eval_dict
assert len(eval_dict["scores"]) == 7
print(f"✓ Serialization works")
print(f"  Keys: {list(eval_dict.keys())}")
print()

# Test 5: Threshold checking
print("Test 5: Threshold Checking")
print("-" * 70)
high_eval = Constitution.evaluate(
    "s",
    "a",
    "s_",
    context={
        "joyful": True,
        "deterministic": True,
        "satisfies_identity": True,
        "satisfies_associativity": True,
    },
)
assert high_eval.satisfies_threshold(0.5), "Should satisfy 0.5 threshold"
print(f"✓ Threshold checking works")
print(f"  Min score: {high_eval.min_score:.3f}")
print(f"  Satisfies 0.5: {high_eval.satisfies_threshold(0.5)}")
print()

# Summary
print("=" * 70)
print("✅ ALL VERIFICATION TESTS PASS")
print("=" * 70)
print()
print("The constitutional reward system is correctly implemented:")
print("  - All 7 principles evaluated")
print("  - Weighted scoring works")
print("  - Context-aware evaluation")
print("  - Probe-specific rewards functional")
print("  - Serialization operational")
print()
print("Ready for integration with TruthFunctor probes!")
