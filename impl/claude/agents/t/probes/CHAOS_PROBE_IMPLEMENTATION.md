# ChaosProbe Implementation Summary

## Overview

ChaosProbe is the DIALECTICAL mode probe in the TruthFunctor reformulation of T-gent. It consolidates four legacy chaos agents (FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent) into a single DP-native probe with the TruthFunctor interface.

## Philosophy

> "Dialectical tension reveals truth. An agent that survives contradiction is more truthful than one that only works in ideal conditions."

ChaosProbe injects controlled chaos to verify agents can handle perturbation and adversarial conditions.

## Implementation

### Files Created/Modified

1. **`agents/t/probes/chaos_probe.py`** (468 lines)
   - Main implementation with TruthFunctor interface
   - Four chaos types: FAILURE, NOISE, LATENCY, FLAKINESS
   - DP formulation with 4 states, 3 actions
   - Constitutional reward calculation

2. **`agents/t/probes/_tests/test_chaos_probe.py`** (495 lines)
   - 21 comprehensive tests covering all aspects
   - Tests for each chaos type
   - Determinism, composition, rewards tests
   - All tests passing ✅

3. **`agents/t/probes/_tests/__init__.py`**
   - Created test directory structure

## Architecture

### DP Formulation

```
States: {READY, INJECTING, OBSERVING, SYNTHESIZING}

Actions:
  - inject_chaos: Start chaos injection
  - observe_survival: Run agent and observe behavior
  - synthesize_verdict: Produce final TruthVerdict

Transitions:
  READY --inject_chaos--> INJECTING
  INJECTING --observe_survival--> OBSERVING
  OBSERVING --synthesize_verdict--> SYNTHESIZING
```

### Constitutional Rewards

```python
Base Score:
  ethical=0.5
  joy_inducing=0.3 * intensity
  heterarchical=0.8
  composable=0.7

Survival Bonus:
  ethical=1.0  # Full credit
  joy_inducing=0.5 * intensity
  heterarchical=0.9
  composable=0.8
```

### Chaos Types

#### FAILURE
- Controlled exceptions (RuntimeError, ValueError, Exception)
- Simulates FailingAgent behavior
- Supports fail_count for recovery testing
- Intensity controls exception type

#### NOISE
- Semantic perturbation of string inputs
- Case changes (low intensity)
- Character swaps (medium intensity)
- Noise injection (high intensity)
- Simulates NoiseAgent behavior

#### LATENCY
- Temporal delays
- Base delay = intensity (in seconds)
- Optional variance parameter
- Simulates LatencyAgent behavior

#### FLAKINESS
- Probabilistic failures
- Fail probability = intensity
- Simulates FlakyAgent behavior

## Usage

### Basic Usage

```python
from agents.t.probes.chaos_probe import chaos_probe, ChaosType

# Test with failure chaos
probe = chaos_probe(
    chaos_type=ChaosType.FAILURE,
    intensity=0.3,
    seed=42,
)

# Verify agent under test
trace = await probe.verify(my_agent, test_input)

# Check if agent survived
if trace.value.passed:
    print("Agent survived chaos!")
else:
    print(f"Agent failed: {trace.value.reasoning}")
```

### Advanced Configuration

```python
# Failure with recovery
probe = chaos_probe(
    chaos_type=ChaosType.FAILURE,
    intensity=0.5,
    fail_count=3,  # Fail 3 times, then recover
    seed=42,
)

# Latency with variance
probe = chaos_probe(
    chaos_type=ChaosType.LATENCY,
    intensity=0.2,  # 0.2s base delay
    variance=0.05,  # ±0.05s variance
    seed=42,
)
```

### Composition

```python
from agents.t.probes.null_probe import null_probe

chaos = chaos_probe(chaos_type=ChaosType.NOISE, seed=42)
null = null_probe(constant="baseline")

# Sequential: test chaos then baseline
composed_seq = chaos >> null

# Parallel: test both simultaneously
composed_par = chaos | null
```

## Key Features

### 1. Determinism via Seed
All chaos is reproducible with a seed parameter for reliable testing.

### 2. PolicyTrace Emission
Every verification emits a PolicyTrace with:
- TruthVerdict (passed/failed + confidence)
- List of TraceEntry (state transitions with rewards)
- Total/max/avg reward calculations

### 3. Constitutional Scoring
Rewards reflect alignment with 7 principles:
- Ethical (safety first)
- Joy-inducing (delightful chaos)
- Heterarchical (adaptation under stress)
- Composable (can chain with other probes)
- Tasteful, Curated, Generative (base scores)

### 4. TruthFunctor Interface
Full DP formulation:
- `states()`: Returns state space
- `actions(s)`: Returns valid actions from state s
- `transition(s, a)`: State evolution
- `reward(s, a, s')`: Constitutional scoring
- `verify(agent, input)`: Main entry point

### 5. Composition Support
Probes compose via:
- `>>` (sequential): Run first, then second
- `|` (parallel): Run both, merge results

## Test Coverage

### Test Categories

1. **Basic Interface** (3 tests)
   - Initialization
   - State space
   - Action space

2. **Chaos Types** (4 tests)
   - FAILURE injection
   - NOISE perturbation
   - LATENCY delays
   - FLAKINESS probability

3. **Configuration** (3 tests)
   - Intensity effects
   - Determinism via seed
   - Convenience function

4. **Rewards** (2 tests)
   - Constitutional calculation
   - Survival bonuses

5. **Integration** (5 tests)
   - PolicyTrace emission
   - Trace accumulation
   - Composition (>> and |)
   - TruthVerdict structure
   - Reset behavior

6. **Edge Cases** (4 tests)
   - Zero intensity
   - Max intensity
   - Empty input
   - Agent failures

**Total: 21 tests, all passing ✅**

## Legacy Consolidation

ChaosProbe replaces and consolidates:

| Legacy Agent | Lines | ChaosProbe Equivalent |
|--------------|-------|-----------------------|
| FailingAgent | 158 | ChaosType.FAILURE |
| NoiseAgent | 211 | ChaosType.NOISE |
| LatencyAgent | 105 | ChaosType.LATENCY |
| FlakyAgent | 92 | ChaosType.FLAKINESS |
| **Total** | **566** | **468 (unified)** |

Benefits:
- Single interface instead of four
- Unified configuration
- Shared infrastructure (seed, reset, composition)
- DP-native semantics
- Constitutional rewards

## Type Safety

All code is fully type-checked with mypy:
- Generic type parameters `A`, `B` for input/output
- Frozen dataclass for ChaosConfig
- Type-safe PolicyTrace construction
- Proper `type: ignore` comments for unavoidable Any

## Future Extensions

Potential enhancements:
1. **More chaos types**: Memory pressure, CPU throttling, network partition
2. **Multi-stage chaos**: Sequence different chaos types
3. **Adaptive intensity**: Learn optimal chaos levels
4. **Chaos schedules**: Time-based chaos injection patterns
5. **Witness integration**: Send PolicyTrace to W-gent for marking

## Related Files

- `agents/t/truth_functor.py`: Base TruthFunctor class
- `agents/t/probes/null_probe.py`: EPISTEMIC mode probe (for comparison)
- `services/categorical/dp_bridge.py`: DP ↔ Agent isomorphism
- `docs/skills/test-patterns.md`: Testing philosophy

## Success Criteria

✅ All chaos types work correctly
✅ Intensity controls severity
✅ Deterministic via seed
✅ Constitutional rewards calculated
✅ Composition with other probes (>> and |)
✅ PolicyTrace emission on every invocation
✅ 21/21 tests passing
✅ Full type safety

## Summary

ChaosProbe successfully implements the DIALECTICAL mode of the TruthFunctor reformulation. It consolidates four legacy chaos agents into a single, well-tested, DP-native probe with constitutional rewards and full composition support. The implementation is clean, type-safe, and ready for integration into the T-gent verification pipeline.

**Implementation Date**: 2025-12-24
**Lines of Code**: 468 (chaos_probe.py) + 495 (tests) = 963 total
**Tests**: 21 passing
**Type Safety**: Full mypy compliance
