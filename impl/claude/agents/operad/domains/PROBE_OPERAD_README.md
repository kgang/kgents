# ProbeOperad: Grammar of Verification Probe Composition

> *"The proof IS the decision. The mark IS the witness. The value IS the composition."*

**Version**: 1.0
**Status**: Production
**Date**: 2025-12-25
**Principles**: Composable, Generative, Heterarchical, Tasteful

---

## Purpose

The ProbeOperad defines how verification probes compose. It integrates:

- **DP-native semantics** from `spec/theory/dp-native-kgents.md`
- **Witness PolicyTrace** for execution traces (Writer monad)
- **ProbeResult types** from `services/probe/types.py`
- **Operad composition grammar** from `agents/operad/core.py`

This enables composing verification probes with **Bellman equation semantics**, where the value of a composed probe is derived from component values via optimal substructure.

---

## Core Insight

**Verification probes are not just functions—they are value functions in the DP sense.**

```
V(composed_probe) = max_strategy [R(component_1) + γ·V(component_2)]
```

Every composition has:
- **State space**: Probe results
- **Actions**: seq, par, branch, fix, witness
- **Transitions**: How results flow through composition
- **Reward**: Probe success/failure
- **Trace**: PolicyTrace (Writer monad)

---

## The Five Operations

### 1. Sequential Composition (`seq`)

**Signature**: `Probe × Probe → Probe`
**Semantics**: Run left, then right (right receives left's result in context)
**Value**: `V(p >> q) = V(p) + γ·V(q)` (Bellman additive)

```python
from agents.operad.domains.probe import SequentialProbe

# Run identity check, then associativity check
composed = SequentialProbe(identity_probe, associativity_probe)
result = await composed.verify(target, context)
```

**Properties**:
- If either fails, composition fails
- Traces accumulate (Writer monad)
- Duration sums: `duration(p>>q) = duration(p) + duration(q)`

---

### 2. Parallel Composition (`par`)

**Signature**: `Probe × Probe → Probe`
**Semantics**: Run both concurrently, take best result
**Value**: `V(p || q) = max(V(p), V(q))` (DP max)

```python
from agents.operad.domains.probe import ParallelProbe

# Try two different verification strategies, take best
composed = ParallelProbe(fast_probe, thorough_probe)
result = await composed.verify(target, context)
```

**Properties**:
- Both probes run (concurrent)
- Result has better status (PASSED > SKIPPED > FAILED > ERROR)
- Duration is max: `duration(p||q) = max(duration(p), duration(q))`
- Both traces merged

---

### 3. Branch Composition (`branch`)

**Signature**: `Pred × Probe × Probe → Probe`
**Semantics**: If predicate then left else right
**Value**: `V(branch) = P(pred)·V(left) + (1-P(pred))·V(right)` (expectation)

```python
from agents.operad.domains.probe import BranchProbe

# Check complexity, use different verification strategies
composed = BranchProbe(
    predicate=complexity_probe,
    if_true=expensive_verification,
    if_false=fast_verification,
)
result = await composed.verify(target, context)
```

**Properties**:
- Predicate evaluated first
- Only chosen branch runs
- Trace includes predicate + branch

---

### 4. Fixed-Point Composition (`fix`)

**Signature**: `Probe → Probe`
**Semantics**: Iterate until convergence (or max iterations)
**Value**: `V(fix) = V(body) / (1 - γ)` (infinite horizon)

```python
from agents.operad.domains.probe import FixedPointProbe

# Iteratively refine verification until stable
composed = FixedPointProbe(refinement_probe, max_iterations=10)
result = await composed.verify(target, context)
```

**Properties**:
- Stops when result stabilizes
- Max iterations prevents infinite loops
- Context updated each iteration

---

### 5. Witness Composition (`witness`)

**Signature**: `Probe → PolicyTrace[Probe]`
**Semantics**: Wrap probe to emit explicit trace entries
**Value**: `V(witness(p)) = V(p)` (value unchanged)

```python
from agents.operad.domains.probe import WitnessedProbe

# Ensure verification is traced
composed = WitnessedProbe(important_probe)
result = await composed.verify(target, context)
assert len(result.log) > 0  # Guaranteed trace
```

**Properties**:
- Every verification step gets TraceEntry
- Trace prepended (witness first)
- Value unchanged

---

## The Three Laws

### 1. Associativity

**Equation**: `(p >> q) >> r ≡ p >> (q >> r)`

Sequential composition is associative—grouping doesn't matter.

```python
ASSOCIATIVITY_LAW.verify(p, q, r)  # -> PASSED
```

---

### 2. Identity

**Equation**: `null >> p ≡ p ≡ p >> null`

The null probe is the identity element—doesn't affect result.

```python
IDENTITY_LAW.verify(p)  # -> PASSED
```

---

### 3. Trace Preservation

**Equation**: `witness(p >> q) ≡ witness(p) >> witness(q)`

Witnessing distributes over composition.

```python
TRACE_PRESERVATION_LAW.verify(p, q)  # -> PASSED
```

---

## Integration with Services

### ProbeProtocol

All probes implement the `ProbeProtocol`:

```python
class MyProbe:
    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        # 1. Perform verification
        passed = self.check(target)

        # 2. Create result
        result = ProbeResult(
            name="my_probe",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED if passed else ProbeStatus.FAILED,
            details="Details here",
            duration_ms=elapsed,
        )

        # 3. Return with trace
        return PolicyTrace.pure(result)
```

---

### Using with Operad

```python
from agents.operad import PROBE_OPERAD

p = IdentityProbe()
q = AssociativityProbe()

# Compose via operad
composed = PROBE_OPERAD.compose("seq", p, q)
result = await composed.verify(agent, {})
```

---

### DP-Native Integration

ProbeOperad is DP-native by design:

| DP Component | Probe Mapping |
|--------------|---------------|
| State space | ProbeResult values |
| Actions | seq, par, branch, fix, witness |
| Transitions | Probe execution |
| Reward | ProbeStatus (PASSED=1.0, FAILED=0.0) |
| Value function | Composition value via Bellman |
| Policy trace | PolicyTrace (Writer monad) |
| Optimal policy | Best composition strategy |

---

## Usage Examples

### Example 1: Sequential Health Check

```python
from agents.operad.domains.probe import SequentialProbe
from services.probe.health import check_brain, check_witness

# Check brain, then witness
health_check = SequentialProbe(check_brain(), check_witness())
result = await health_check.verify(system, {})

if result.value.passed:
    print("System healthy!")
```

---

### Example 2: Parallel Verification Strategies

```python
from agents.operad.domains.probe import ParallelProbe
from services.probe.laws import check_fast, check_thorough

# Try both, take best
verification = ParallelProbe(check_fast(), check_thorough())
result = await verification.verify(agent, {})

print(f"Best strategy: {result.value.name}")
```

---

### Example 3: Adaptive Verification

```python
from agents.operad.domains.probe import BranchProbe

# If complex, use thorough check; else fast check
adaptive = BranchProbe(
    predicate=complexity_probe(),
    if_true=thorough_check(),
    if_false=fast_check(),
)
result = await adaptive.verify(target, {})
```

---

### Example 4: Iterative Refinement

```python
from agents.operad.domains.probe import FixedPointProbe

# Refine until convergence
refiner = FixedPointProbe(refinement_probe(), max_iterations=5)
result = await refiner.verify(spec, {})

if "Converged" in result.value.details:
    print("Spec verified!")
```

---

## Teaching Gotchas

### Gotcha 1: ProbeProtocol vs PolyAgent

**Issue**: ProbeOperad operations compose `ProbeProtocol` objects, NOT `PolyAgent` objects.

**Why**: Unlike `AGENT_OPERAD` which composes agents, `ProbeOperad` works at the verification layer where we compose verification judgments.

**Evidence**: `ProbeResult` is the value in `PolicyTrace[ProbeResult]`

**Fix**: Implement `ProbeProtocol` for your verification logic.

---

### Gotcha 2: Bellman Semantics in Practice

**Issue**: Understanding how values propagate through composition.

**Why**: Each operation has different Bellman semantics:
- `seq`: Additive (`V(p>>q) = V(p) + γ·V(q)`)
- `par`: Max (`V(p||q) = max(V(p), V(q))`)
- `branch`: Expectation (`V = P·V(true) + (1-P)·V(false)`)

**Evidence**: `spec/theory/dp-native-kgents.md §2.1`

**Fix**: Choose operations based on desired value combination.

---

### Gotcha 3: Trace Accumulation (Writer Monad)

**Issue**: Traces grow through composition.

**Why**: `PolicyTrace` is a Writer monad—`bind()` appends to log, doesn't replace.

**Evidence**: `PolicyTrace.bind()` does `self.log + result.log`

**Fix**: Don't worry about trace size for verification—it's the proof!

---

### Gotcha 4: Async Law Verification

**Issue**: Operad laws are sync, but probes are async.

**Why**: Law verification happens at operad construction (sync), but probe execution is async.

**Evidence**: Sync wrappers `_verify_*_sync()` call `asyncio.run()`

**Fix**: Laws verify structurally at construction; behavioral verification happens at runtime.

---

## Testing

Run the test suite:

```bash
cd impl/claude
uv run pytest agents/operad/domains/_tests/test_probe_operad.py -v
```

Tests verify:
- ✓ Operad structure (5 operations, 3 laws)
- ✓ Sequential composition
- ✓ Parallel composition (best result)
- ✓ Branch composition (predicate-based)
- ✓ Fixed-point convergence
- ✓ Witness trace emission
- ✓ Null probe identity
- ✓ Associativity law
- ✓ Identity law
- ✓ Trace preservation law
- ✓ Bellman value semantics
- ✓ Trace accumulation (Writer monad)

---

## Architecture

```
ProbeOperad
├── Operations (5)
│   ├── seq: Sequential (Bellman additive)
│   ├── par: Parallel (Bellman max)
│   ├── branch: Conditional (Bellman expectation)
│   ├── fix: Fixed-point (infinite horizon)
│   └── witness: Trace wrapper
├── Laws (3)
│   ├── Associativity: (p>>q)>>r ≡ p>>(q>>r)
│   ├── Identity: null>>p ≡ p ≡ p>>null
│   └── Trace preservation: witness(p>>q) ≡ witness(p)>>witness(q)
└── Types
    ├── ProbeProtocol: Verification interface
    ├── SequentialProbe: p >> q composition
    ├── ParallelProbe: p || q composition
    ├── BranchProbe: pred ? p : q composition
    ├── FixedPointProbe: iterate until convergence
    ├── WitnessedProbe: trace wrapper
    └── NullProbe: identity element
```

---

## See Also

- `spec/theory/dp-native-kgents.md` - DP-Agent isomorphism
- `spec/theory/analysis-operad.md` - Four modes of analysis
- `services/probe/types.py` - ProbeResult, ProbeStatus, ProbeType
- `services/categorical/dp_bridge.py` - PolicyTrace, TraceEntry
- `agents/operad/core.py` - Operad infrastructure
- `agents/operad/domains/_tests/test_probe_operad.py` - Test suite

---

**Status**: Production-ready. All tests pass. Integrated with OperadRegistry.
