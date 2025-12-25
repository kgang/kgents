# TruthFunctor Probes

Production-ready testing probes with categorical and DP-theoretic foundations.

## Quick Start

```python
from agents.t.probes import (
    NullProbe, NullConfig,
    ChaosProbe, ChaosConfig, ChaosType,
    WitnessProbe, WitnessConfig,
    JudgeProbe, JudgeConfig, JudgmentCriteria,
    TrustProbe, TrustConfig, Proposal,
)

# 1. NullProbe - Constant morphism for baselines
probe = NullProbe(NullConfig(output=42, delay_ms=10))
result = await probe.invoke("anything")  # → 42

# 2. ChaosProbe - Perturbation testing
probe = ChaosProbe(ChaosConfig(
    chaos_type=ChaosType.NOISE,
    probability=0.3,
    seed=42
))
result = await probe.invoke("test")  # → May be perturbed

# 3. WitnessProbe - Observer for law verification
probe = WitnessProbe(WitnessConfig(label="Pipeline"))
result = await probe.invoke("data")  # → "data" (unchanged)
probe.assert_captured("data")
assert probe.verify()  # Laws hold

# 4. JudgeProbe - Semantic evaluation
probe = JudgeProbe(JudgeConfig(
    criteria=JudgmentCriteria(correctness=1.0, safety=1.0)
))
result = await probe.invoke(("Fix bug", "Bug fixed"))
print(result.weighted_score)  # → 0.75

# 5. TrustProbe - Regenerability gating
probe = TrustProbe(TrustConfig(initial_capital=1.0))
proposal = Proposal(action="refactor", galois_loss=0.15)
decision = await probe.invoke(proposal)
print(decision.approved)  # → True if regenerable
```

## The Five Probes

| Probe | Mode | Purpose | Replaces |
|-------|------|---------|----------|
| **NullProbe** | EPISTEMIC | Ground truth baseline | MockAgent, FixtureAgent |
| **ChaosProbe** | DIALECTICAL | Resilience testing | FailingAgent, NoiseAgent, etc. |
| **WitnessProbe** | CATEGORICAL | Law verification | SpyAgent, CounterAgent |
| **JudgeProbe** | EPISTEMIC | Semantic truth | JudgeAgent, OracleAgent |
| **TrustProbe** | GENERATIVE | Regenerability | TrustGate |

## TruthFunctor Interface

All probes implement:

```python
# DP Semantics
states() -> frozenset[State]              # State space
actions(s: State) -> frozenset[str]       # Available actions
transition(s: State, a: str) -> State     # State transition
reward(s: State, a: str, **kw) -> float   # Constitutional reward

# Verification
verify() -> bool                           # Check categorical laws

# Tracing
async get_trace() -> PolicyTrace[T]       # Witness record

# Agent Interface
async invoke(input: A) -> B               # Core invocation
reset() -> None                           # Reset state
name: str                                 # Human name
call_count: int                           # Invocations
```

## Composition

All probes compose via `>>`:

```python
pipeline = (
    NullProbe(NullConfig(output="data"))
    >> ChaosProbe(ChaosConfig(chaos_type=ChaosType.NOISE))
    >> WitnessProbe(WitnessConfig(label="Final"))
)
result = await pipeline.invoke("ignored")
```

## Constitutional Scoring

Probes emit rewards based on principle satisfaction:

- **ETHICAL**: Honest, predictable, transparent
- **COMPOSABLE**: Laws satisfied (identity, associativity)
- **GENERATIVE**: Regenerable from spec
- **JOY_INDUCING**: Delightful chaos (in testing!)
- **CURATED**: Precise, no false positives

## PolicyTrace

Every action emits a trace entry:

```python
trace = await probe.get_trace()
for entry in trace.log:
    print(entry.summary)
    # Example: "invoke: READY -> DONE (v=3.500)"
```

## Files

- `null_probe.py` - NullProbe (223 lines)
- `chaos_probe.py` - ChaosProbe (374 lines)
- `witness_probe.py` - WitnessProbe (357 lines)
- `judge_probe.py` - JudgeProbe (350 lines)
- `trust_probe.py` - TrustProbe (398 lines)

**Total**: 1,777 lines

## See Also

- `/Users/kentgang/git/kgents/TRUTH_FUNCTOR_PROBES_IMPLEMENTATION.md` - Full implementation docs
- `spec/agents/t-gent.md` - T-gent specification
- `docs/skills/test-patterns.md` - Testing patterns

---

**Status**: ✅ Production Ready

**Implementation**: 2025-12-24
