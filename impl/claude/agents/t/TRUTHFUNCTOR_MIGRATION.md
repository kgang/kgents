# TruthFunctor Migration Summary

## Overview

The T-gent module has been updated to support both the new TruthFunctor protocol and legacy T-gent types for backwards compatibility.

## New Architecture

### TruthFunctor Protocol

All T-gents are being migrated to the TruthFunctor protocol, which provides:

- **DP-native semantics**: (states, actions, transition, reward, gamma)
- **Automatic PolicyTrace emission**: Every verification produces a witnessed trace
- **Constitutional reward scoring**: 7 principles (ethical, composable, joy, etc.)
- **AnalysisMode mapping**: CATEGORICAL, EPISTEMIC, DIALECTICAL, GENERATIVE

### Five Probe Types

The new probe types replace the old T-gent type hierarchy:

| New Probe | Replaces | Mode | Purpose |
|-----------|----------|------|---------|
| **NullProbe** | MockAgent, FixtureAgent | EPISTEMIC | Constant morphism baseline |
| **ChaosProbe** | FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent | DIALECTICAL | Perturbation testing |
| **WitnessProbe** | SpyAgent, CounterAgent, MetricsAgent | CATEGORICAL | Observer morphism |
| **JudgeProbe** | JudgeAgent, OracleAgent | EPISTEMIC | Semantic evaluation |
| **TrustProbe** | TrustGate | GENERATIVE | Capital-backed gating |

## File Structure

```
agents/t/
├── __init__.py              # Main module with exports
├── truth_functor.py         # Core TruthFunctor protocol types
├── compat.py                # Backwards compatibility wrappers
└── probes/                  # Probe implementations
    ├── __init__.py
    ├── null_probe.py        # ✓ Implemented
    ├── chaos_probe.py       # ⏳ TODO: Fix dataclass errors
    ├── witness_probe.py     # ⏳ TODO: Fix dataclass errors
    ├── judge_probe.py       # ⏳ TODO: Fix dataclass errors
    └── trust_probe.py       # ⏳ TODO: Fix dataclass errors
```

## Exports

### New TruthFunctor Types

```python
from agents.t import (
    # Core protocol
    TruthFunctor,
    PolicyTrace,
    TruthVerdict,
    ConstitutionalScore,
    AnalysisMode,
    ProbeState,
    ProbeAction,
    TraceEntry,

    # Probes (currently only NullProbe)
    NullProbe,
    NullConfig,

    # Operad
    PROBE_OPERAD,
)
```

### Legacy Types (Still Supported)

```python
from agents.t import (
    # Type I - Nullifiers
    MockAgent, MockConfig,
    FixtureAgent, FixtureConfig,

    # Type II - Saboteurs
    FailingAgent, FailingConfig,
    NoiseAgent, NoiseConfig,
    LatencyAgent,
    FlakyAgent,

    # Type III - Observers
    SpyAgent,
    PredicateAgent,
    CounterAgent,
    MetricsAgent,

    # Type IV - Critics
    JudgeAgent,
    OracleAgent,
    PropertyAgent,

    # Type V - Trust Gate
    TrustGate,
)
```

## Migration Guide

### Example: MockAgent → NullProbe

**Old (still works, but deprecated)**:
```python
from agents.t import MockAgent, MockConfig

mock = MockAgent(MockConfig(output="result"))
result = await mock.invoke(input)
```

**New (preferred)**:
```python
from agents.t import NullProbe, NullConfig

probe = NullProbe(NullConfig(output="result"))
trace = await probe.verify(agent, input)

# Access result
result = trace.value.value

# Access trace for witnessing
for entry in trace.entries:
    print(f"State: {entry.state_after.phase}")
    print(f"Reward: {entry.reward.weighted_total}")
```

### Example: Composition

**Old**:
```python
mock1 = MockAgent(MockConfig(output="step1"))
mock2 = MockAgent(MockConfig(output="step2"))
pipeline = mock1 >> mock2
```

**New**:
```python
probe1 = NullProbe(NullConfig(output="step1"))
probe2 = NullProbe(NullConfig(output="step2"))
composed = probe1 >> probe2  # Uses ComposedProbe

# OR via PROBE_OPERAD
from agents.t import PROBE_OPERAD
composed = PROBE_OPERAD.operations["seq"].compose(probe1, probe2)
```

## Backwards Compatibility

The `compat.py` module provides backwards compatibility wrappers:

- **MockAgent**: Wraps NullProbe, emits deprecation warning
- **FixtureAgent**: Wraps NullProbe, emits deprecation warning
- **Other types**: TODO - will be added as probes are completed

All existing code using legacy T-gent types will continue to work, but will emit deprecation warnings on first use.

## Current Status

### ✓ Completed

1. ✅ TruthFunctor protocol defined (`truth_functor.py`)
2. ✅ NullProbe implemented (`probes/null_probe.py`)
3. ✅ Backwards compatibility for MockAgent/FixtureAgent (`compat.py`)
4. ✅ Updated exports in `__init__.py`
5. ✅ PROBE_OPERAD integration

### ⏳ TODO

1. Fix dataclass errors in remaining probes:
   - `chaos_probe.py`
   - `witness_probe.py`
   - `judge_probe.py`
   - `trust_probe.py`

2. Complete backwards compatibility wrappers:
   - FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent → ChaosProbe
   - SpyAgent, PredicateAgent, CounterAgent, MetricsAgent → WitnessProbe
   - JudgeAgent, OracleAgent → JudgeProbe
   - TrustGate → TrustProbe

3. Update tests to use new TruthFunctor API

4. Add examples and documentation

## Testing

```bash
# Test new imports
cd impl/claude
uv run python -c "from agents.t import NullProbe, NullConfig; print('✓ Import successful')"

# Test backwards compatibility
uv run python -c "from agents.t import MockAgent; m = MockAgent('test'); print('✓ Compat works')"

# Test legacy types still work
uv run python -c "from agents.t import SpyAgent, FailingAgent; print('✓ Legacy types work')"
```

## Design Decisions

### 1. Why TruthFunctor?

The TruthFunctor protocol unifies all verification probes under a DP-native formulation:

- **States**: Verification phases (READY, COMPUTING, DONE, etc.)
- **Actions**: Test operations (invoke, verify, observe, etc.)
- **Transitions**: Deterministic state evolution
- **Rewards**: Constitutional scoring (7 principles)
- **Traces**: PolicyTrace for witnessing

This makes verification **first-class** in the DP framework, not an afterthought.

### 2. Why Keep Legacy Types?

- **Backwards compatibility**: Existing code doesn't break
- **Gradual migration**: Teams can migrate on their schedule
- **Deprecation warnings**: Users are informed of better alternatives
- **Zero breaking changes**: All existing tests pass

### 3. Why Separate `compat.py`?

- **Clear separation**: New vs legacy code
- **Easy to remove**: When migration is complete, delete one file
- **Minimal pollution**: Legacy types don't clutter main module
- **Explicit warnings**: Deprecation logic centralized

## Next Steps

1. **Fix probe implementations**: Resolve dataclass errors in remaining probes
2. **Complete compat wrappers**: Add remaining legacy type wrappers
3. **Update tests**: Migrate tests to use new TruthFunctor API
4. **Documentation**: Add usage examples and migration guide
5. **Announce**: Notify users of new architecture and migration path

---

**Generated**: 2025-12-24
**Status**: In Progress
**Owner**: Kent Gang
