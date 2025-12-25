# Constitutional Reward System: Quick Reference

**Status**: Implemented
**Date**: 2024-12-24
**Integration**: TruthFunctor Probes + DP-Bridge

---

## The Core Insight

> *"The 7 principles aren't aspirational documentation. They're the actual reward function."*

Every action in kgents is scored against the Constitution. This isn't enforcement from outside—it's intrinsic to the system architecture.

```python
R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')
```

---

## The 7 Principles as Rewards

| Principle | Weight | What It Measures |
|-----------|--------|------------------|
| **ETHICAL** | 2.0 | Safety, predictability, preserving human agency |
| **COMPOSABLE** | 1.5 | Satisfies categorical laws (identity, associativity) |
| **JOY_INDUCING** | 1.2 | Delight in interaction, elegance |
| **TASTEFUL** | 1.0 | Clear purpose, no bloat |
| **CURATED** | 1.0 | Intentional selection, not feature creep |
| **HETERARCHICAL** | 1.0 | Flux over fixed hierarchy |
| **GENERATIVE** | 1.0 | Regenerable from spec |

---

## Basic Usage

### Evaluate Any Action

```python
from services.categorical import Constitution

eval = Constitution.evaluate(
    state_before="initial state",
    action="do_something",
    state_after="final state",
    context={"deterministic": True},  # Optional context
)

print(f"Total score: {eval.weighted_total:.2f}")
print(f"Min score: {eval.min_score:.2f}")
print(f"Satisfies threshold: {eval.satisfies_threshold(0.7)}")

# Per-principle breakdown
for principle, score in eval.by_principle.items():
    print(f"{principle.name}: {score:.2f}")
```

### Probe-Specific Rewards

```python
from services.categorical import ProbeRewards

# NullProbe (identity law testing)
eval = ProbeRewards.null_probe_reward(state, action, state_)
# Returns: ETHICAL=1.0, COMPOSABLE=1.0

# ChaosProbe (robustness testing)
eval = ProbeRewards.chaos_probe_reward(state, action, state_, survived=True)
# Returns: ETHICAL=1.0, HETERARCHICAL=0.8

# MonadProbe (monad law testing)
eval = ProbeRewards.monad_probe_reward(
    state, action, state_,
    identity_satisfied=True,
    associativity_satisfied=True,
)
# Returns: COMPOSABLE=1.0, ETHICAL=1.0

# SheafProbe (coherence testing)
eval = ProbeRewards.sheaf_probe_reward(
    state, action, state_,
    coherence_score=0.95,
    violation_count=1,
)
# Returns: ETHICAL=0.95, GENERATIVE=0.95, COMPOSABLE=0.95
```

### Galois Loss (Regenerability)

```python
from services.categorical import compute_galois_loss

# Test regenerability
loss = await compute_galois_loss(output_text, llm_client)

# loss ∈ [0, 1]
# 0.0 = perfect regeneration
# 1.0 = complete failure
```

---

## Integration Points

### With DP-Bridge ValueFunction

```python
from services.categorical import Constitution, Principle

# Use constitutional evaluation in DP value function
def reward_function(state, action, next_state):
    eval = Constitution.evaluate(state, action, next_state)
    return eval.weighted_total

# Or principle-specific
def ethical_reward(state, action, next_state):
    eval = Constitution.evaluate(state, action, next_state)
    return eval.by_principle[Principle.ETHICAL]
```

### With TruthFunctor Probes

```python
from services.categorical import ProbeRewards, MonadProbe

async def test_monad_laws_with_constitutional_rewards(problem, llm):
    probe = MonadProbe(llm)
    result = await probe.test_all(problem)

    # Get constitutional evaluation
    eval = ProbeRewards.monad_probe_reward(
        state_before=problem,
        action="monad_test",
        state_after=result,
        identity_satisfied=(result.identity_score > 0.9),
        associativity_satisfied=(result.associativity_score > 0.9),
    )

    return eval.weighted_total  # Use as reward signal
```

### With Witness Marks

```python
from services.categorical import Constitution

# Every action can emit a constitutional justification
eval = Constitution.evaluate(state, action, next_state)

mark = Mark.from_thought(
    content=f"Action scored {eval.weighted_total:.2f}",
    reasoning="\n".join([
        f"{ps.principle.name}: {ps.score:.2f} - {ps.reasoning}"
        for ps in eval.scores
    ]),
    tags=("constitutional", "evaluation"),
)
```

---

## Context Parameters

The `context` dict allows fine-grained control:

```python
context = {
    # TASTEFUL
    # (auto-detected from action name)

    # CURATED
    "intentional": True,  # Explicitly mark as curated
    "curation_rationale": "Why this feature",

    # ETHICAL
    "preserves_human_agency": True,  # Default True
    "deterministic": True,  # Default True

    # JOY_INDUCING
    "joyful": True,
    "joy_evidence": "Why delightful",

    # COMPOSABLE
    "satisfies_identity": True,  # Default True
    "satisfies_associativity": True,  # Default True

    # HETERARCHICAL
    "enforces_hierarchy": False,  # Default False
    "enables_fluidity": True,

    # GENERATIVE
    "has_spec": True,
    "regenerability_score": 0.9,  # [0, 1]
}

eval = Constitution.evaluate(state, action, next_state, context=context)
```

---

## Testing

Run the comprehensive test suite:

```bash
cd impl/claude
uv run pytest services/categorical/_tests/test_constitution.py -v
```

Tests cover:
- Principle weight configuration
- Individual principle evaluators
- Aggregation and scoring
- All probe-specific rewards
- Galois loss computation
- Integration with DP-bridge

---

## Design Decisions

### Why These Weights?

- **ETHICAL (2.0)**: Safety first. Violations here should dominate other concerns.
- **COMPOSABLE (1.5)**: Architecture second. Composition is how we scale.
- **JOY_INDUCING (1.2)**: Kent's aesthetic priority. This is what makes kgents kgents.
- **Others (1.0)**: Equal baseline importance.

### Why Heuristic Evaluators?

The evaluators use heuristics (action names, state complexity, context flags) rather than deep analysis. This is intentional:

1. **Performance**: Fast, no LLM calls needed for basic scoring
2. **Transparency**: Clear rules, auditable
3. **Extensibility**: Override with domain-specific evaluators
4. **Testability**: Deterministic behavior

For production use, replace heuristics with domain-specific scoring functions:

```python
class CustomConstitution(Constitution):
    @staticmethod
    def _evaluate_tasteful(s, a, s_, ctx):
        # Your domain-specific tasteful evaluation
        return PrincipleScore(...)
```

### Why Probe-Specific Rewards?

Different probes measure different things. ProbeRewards bridges categorical law testing to constitutional evaluation:

- **NullProbe**: Identity law → COMPOSABLE + ETHICAL
- **ChaosProbe**: Robustness → ETHICAL + HETERARCHICAL
- **MonadProbe**: Monad laws → COMPOSABLE + ETHICAL
- **SheafProbe**: Coherence → ETHICAL + GENERATIVE + COMPOSABLE

This makes the reward signal *meaningful* for what the probe tests.

---

## Next Steps

1. **Wire to existing probes**: Update `MonadProbe`, `SheafDetector` to use `ProbeRewards`
2. **Add to DP solver**: Use `Constitution.evaluate` as the reward function in `DPSolver`
3. **Expose via AGENTESE**: Create `/world.constitutional.evaluate` node
4. **Visualize in UI**: Show principle breakdown in probe results
5. **Meta-optimization**: Use MetaDP to tune principle weights

---

*"The proof IS the decision. The mark IS the witness. The Constitution IS the reward."*
