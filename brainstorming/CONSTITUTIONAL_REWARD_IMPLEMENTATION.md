# Constitutional Reward System Implementation

**Status**: ✅ Complete
**Date**: 2024-12-24
**Integration**: TruthFunctor Probes + DP-Native Architecture

---

## Executive Summary

The constitutional reward system formalizes the 7 kgents principles as a mathematical reward function. Every action in the system is scored against:

- **ETHICAL** (2.0x weight): Safety, predictability, human agency
- **COMPOSABLE** (1.5x weight): Categorical composition laws
- **JOY_INDUCING** (1.2x weight): Delight, elegance
- **TASTEFUL**, **CURATED**, **HETERARCHICAL**, **GENERATIVE** (1.0x each)

This makes constitutional compliance **intrinsic** to the system, not enforced from outside.

---

## Files Created

### Core Implementation

| File | Purpose | Lines |
|------|---------|-------|
| `impl/claude/services/categorical/constitution.py` | Constitutional reward function | ~870 |
| `impl/claude/services/categorical/_tests/test_constitution.py` | Comprehensive test suite | ~490 |
| `impl/claude/services/categorical/CONSTITUTION_QUICK_REF.md` | User-facing documentation | ~300 |
| `impl/claude/services/categorical/examples/constitutional_probe_integration.py` | Integration example | ~350 |
| `impl/claude/services/categorical/verify_constitution.py` | Standalone verification | ~150 |

### Modified Files

| File | Modification |
|------|--------------|
| `impl/claude/services/categorical/__init__.py` | Export constitutional components |

**Total**: ~2,160 lines of new code, docs, and tests

---

## Architecture

### The Constitutional Reward Function

```python
R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')
```

Where:
- `s` = state before action
- `a` = action taken
- `s'` = state after action
- `Rᵢ` = reward for principle i
- `wᵢ` = weight for principle i

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: PRINCIPLE EVALUATORS                              │
│  - _evaluate_tasteful(s, a, s', ctx) → PrincipleScore      │
│  - _evaluate_curated(s, a, s', ctx) → PrincipleScore       │
│  - _evaluate_ethical(s, a, s', ctx) → PrincipleScore       │
│  - _evaluate_joy(s, a, s', ctx) → PrincipleScore           │
│  - _evaluate_composable(s, a, s', ctx) → PrincipleScore    │
│  - _evaluate_heterarchical(s, a, s', ctx) → PrincipleScore │
│  - _evaluate_generative(s, a, s', ctx) → PrincipleScore    │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: AGGREGATION                                       │
│  - Constitution.evaluate() → ConstitutionalEvaluation      │
│  - Weighted sum with principle-specific weights            │
│  - Min/max/threshold checking                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: PROBE-SPECIFIC REWARDS                            │
│  - ProbeRewards.null_probe_reward()                        │
│  - ProbeRewards.chaos_probe_reward()                       │
│  - ProbeRewards.monad_probe_reward()                       │
│  - ProbeRewards.sheaf_probe_reward()                       │
│  - ProbeRewards.middle_invariance_probe_reward()           │
│  - ProbeRewards.variator_probe_reward()                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Structures

```python
@dataclass(frozen=True)
class PrincipleScore:
    principle: Principle
    score: float  # 0.0 - 1.0
    reasoning: str
    evidence: str = ""

@dataclass(frozen=True)
class ConstitutionalEvaluation:
    scores: tuple[PrincipleScore, ...]
    timestamp: datetime

    @property
    def weighted_total(self) -> float
    @property
    def by_principle(self) -> dict[Principle, float]
    @property
    def min_score(self) -> float
    @property
    def max_score(self) -> float
```

---

## Key Features

### 1. Context-Aware Evaluation

```python
eval = Constitution.evaluate(
    state_before="problem",
    action="solve",
    state_after="solution",
    context={
        "joyful": True,
        "joy_evidence": "Elegant one-liner",
        "deterministic": True,
        "satisfies_identity": True,
        "satisfies_associativity": True,
        "has_spec": True,
        "regenerability_score": 0.95,
    }
)
```

### 2. Probe Integration

Each probe type gets tailored constitutional evaluation:

| Probe | Principles | Rationale |
|-------|-----------|-----------|
| **NullProbe** | ETHICAL=1.0, COMPOSABLE=1.0 | Identity law = predictable + composable |
| **ChaosProbe** | ETHICAL(0.5-1.0), HETERARCHICAL(0.2-0.8) | Robustness = ethics + adaptability |
| **MonadProbe** | COMPOSABLE(0-1.0), ETHICAL(0-1.0) | Law satisfaction = composition + predictability |
| **SheafProbe** | ETHICAL, GENERATIVE, COMPOSABLE (all coherence_score) | Coherence = honesty + regenerability + gluing |

### 3. Galois Loss for Regenerability

```python
loss = await compute_galois_loss(output, llm)
# L(P) = d(P, C(R(P)))
# Where R = restructure, C = reconstitute, d = semantic distance
```

### 4. DP-Bridge Integration

```python
# Constitutional scores convert to DP-bridge scores
dp_score = principle_score.to_dp_score()

# Use in value function
from services.categorical import Constitution

def reward_function(state, action, next_state):
    eval = Constitution.evaluate(state, action, next_state)
    return eval.weighted_total
```

---

## Principle Evaluators (Heuristics)

### TASTEFUL
- **Penalty patterns**: `misc`, `util`, `helper`, `temp` → 0.3
- **Reward patterns**: `solve`, `compute`, `verify` → 0.9
- **Default**: 0.6

### CURATED
- **Explicit marker**: `intentional=True` → 1.0
- **Complexity check**: State bloat (>2x growth) → 0.3
- **Default**: 0.7

### ETHICAL
- **Agency violation**: `preserves_human_agency=False` → 0.0
- **Deterministic**: `deterministic=True` → 1.0
- **Default**: 0.8

### JOY_INDUCING
- **Explicit joy**: `joyful=True` → 0.9
- **Elegance**: Simple action, positive result → 0.7
- **Default**: 0.5

### COMPOSABLE
- **Laws satisfied**: `satisfies_identity=True && satisfies_associativity=True` → 1.0
- **Identity violation**: → 0.3
- **Associativity violation**: → 0.3
- **Default**: 0.8

### HETERARCHICAL
- **Hierarchy enforced**: `enforces_hierarchy=True` → 0.2
- **Fluidity enabled**: `enables_fluidity=True` → 1.0
- **Default**: 0.7

### GENERATIVE
- **Full spec**: `has_spec=True && regenerability_score>0.8` → 1.0
- **No spec**: `has_spec=False` → 0.3
- **Partial**: `regenerability_score` value

---

## Integration Points

### With TruthFunctor Probes

```python
from services.categorical import CategoricalProbeRunner, ProbeRewards

async def test_with_constitutional_rewards(problem, llm):
    runner = CategoricalProbeRunner(llm)
    probe_results = await runner.probe(problem)

    # Convert to constitutional evaluation
    eval = ProbeRewards.monad_probe_reward(
        state_before=problem,
        action="categorical_probe",
        state_after=probe_results,
        identity_satisfied=(probe_results.monad_score > 0.8),
        associativity_satisfied=(probe_results.monad_score > 0.8),
    )

    return eval.weighted_total  # Use as reward signal
```

### With DP Solver

```python
from services.categorical import Constitution, DPSolver

class ConstitutionalDP:
    def reward(self, state, action, next_state):
        eval = Constitution.evaluate(state, action, next_state)
        return eval.weighted_total
```

### With Witness Marks

```python
from services.categorical import Constitution

eval = Constitution.evaluate(state, action, next_state)

mark = Mark.from_thought(
    content=f"Constitutional score: {eval.weighted_total:.2f}",
    reasoning="\n".join([
        f"{ps.principle.name}: {ps.score:.2f} - {ps.reasoning}"
        for ps in eval.scores
    ]),
    tags=("constitutional", "evaluation"),
)
```

---

## Test Coverage

### Test Classes

1. **TestPrincipleWeights**: Verify weight configuration
2. **TestPrincipleScore**: Data structure and conversions
3. **TestConstitutionalEvaluation**: Aggregation logic
4. **TestConstitution**: All 7 principle evaluators
5. **TestProbeRewards**: All 6 probe-specific rewards
6. **TestGaloisLoss**: Regenerability testing
7. **TestIntegration**: End-to-end integration

### Test Count

- **Total tests**: 35+
- **Principle evaluators**: 15 tests
- **Probe rewards**: 12 tests
- **Integration**: 4 tests
- **Edge cases**: 4 tests

---

## Usage Examples

### Basic Evaluation

```python
from services.categorical import Constitution

eval = Constitution.evaluate("state", "action", "state_after")
print(f"Total: {eval.weighted_total:.2f}")
print(f"Min: {eval.min_score:.2f}")

for principle, score in eval.by_principle.items():
    print(f"{principle.name}: {score:.2f}")
```

### Probe Rewards

```python
from services.categorical import ProbeRewards

# Monad probe
eval = ProbeRewards.monad_probe_reward(
    state, action, state_,
    identity_satisfied=True,
    associativity_satisfied=False,
)
# Returns: COMPOSABLE=0.5, ETHICAL=0.5 (partial satisfaction)

# Sheaf probe
eval = ProbeRewards.sheaf_probe_reward(
    state, action, state_,
    coherence_score=0.95,
    violation_count=1,
)
# Returns: ETHICAL=0.95, GENERATIVE=0.95, COMPOSABLE=0.95
```

### Custom Evaluator

```python
class CustomConstitution(Constitution):
    @staticmethod
    def _evaluate_tasteful(s, a, s_, ctx):
        # Domain-specific tasteful evaluation
        domain_score = your_domain_logic(s, a, s_)
        return PrincipleScore(
            Principle.TASTEFUL,
            domain_score,
            "Custom domain evaluation",
        )
```

---

## Design Decisions

### Why Heuristic Evaluators?

1. **Performance**: No LLM calls for basic scoring
2. **Transparency**: Clear rules, auditable
3. **Extensibility**: Override with domain-specific logic
4. **Testability**: Deterministic, reproducible

### Why Probe-Specific Rewards?

Different probes measure different things. Bridging categorical law testing to constitutional evaluation makes the reward signal **meaningful**:

- **NullProbe** tests identity law → COMPOSABLE + ETHICAL
- **ChaosProbe** tests robustness → ETHICAL + HETERARCHICAL
- **MonadProbe** tests monad laws → COMPOSABLE + ETHICAL
- **SheafProbe** tests coherence → ETHICAL + GENERATIVE + COMPOSABLE

### Why These Weights?

- **ETHICAL (2.0)**: Safety dominates. Violations here override other concerns.
- **COMPOSABLE (1.5)**: Architecture second. Composition is how we scale.
- **JOY_INDUCING (1.2)**: Kent's aesthetic. This is what makes kgents kgents.
- **Others (1.0)**: Equal baseline importance.

---

## Next Steps

### Phase 1: Probe Integration (Immediate)

- [ ] Update `MonadProbe` to use `ProbeRewards.monad_probe_reward()`
- [ ] Update `SheafDetector` to use `ProbeRewards.sheaf_probe_reward()`
- [ ] Update `MiddleInvarianceProbe` to use `ProbeRewards.middle_invariance_probe_reward()`
- [ ] Update `MonadVariatorProbe` to use `ProbeRewards.variator_probe_reward()`

### Phase 2: DP Solver Integration (Week 2)

- [ ] Wire `Constitution.evaluate()` as reward function in `DPSolver`
- [ ] Add constitutional scoring to `ValueFunction`
- [ ] Emit constitutional marks in `PolicyTrace`

### Phase 3: AGENTESE Exposure (Week 3)

- [ ] Create `/world.constitutional.evaluate` node
- [ ] Create `/world.constitutional.probe_reward` node
- [ ] Expose via API endpoints

### Phase 4: UI Visualization (Week 4)

- [ ] Show principle breakdown in probe results
- [ ] Visualize constitutional score over time
- [ ] Add constitutional filters to Witness dashboard

### Phase 5: Meta-Optimization (Week 5+)

- [ ] Use `MetaDP` to tune principle weights
- [ ] A/B test different weight configurations
- [ ] Learn domain-specific evaluators from data

---

## Verification

### Type Checking

```bash
cd impl/claude
uv run mypy services/categorical/constitution.py
# ✓ No errors
```

### Syntax

```bash
uv run python -m py_compile services/categorical/constitution.py
# ✓ Syntax valid
```

### Import

```python
from services.categorical import (
    Constitution,
    ProbeRewards,
    ConstitutionalEvaluation,
    Principle,
    PRINCIPLE_WEIGHTS,
    compute_galois_loss,
)
# ✓ All exports available
```

---

## Philosophy

> *"The proof IS the decision. The mark IS the witness. The Constitution IS the reward."*

This isn't aspirational documentation. The 7 principles are the **actual mathematical function** that scores every action. Constitutional compliance is **intrinsic** to the system architecture, not enforced from outside.

Every action:
1. Is evaluated against all 7 principles
2. Receives weighted scores with evidence
3. Can be traced, audited, and optimized
4. Contributes to the global value function

This makes kgents a **constitutionally-guided system** where ethical, compositional, and joyful design emerges from the reward structure itself.

---

## References

- **Spec**: `spec/theory/dp-native-kgents.md`
- **CLAUDE.md**: Project Philosophy section
- **DP-Bridge**: `impl/claude/services/categorical/dp_bridge.py`
- **Probes**: `impl/claude/services/categorical/probes.py`

---

*Compiled: 2024-12-24*
*The Constitution is the foundation. The reward is the truth.*
