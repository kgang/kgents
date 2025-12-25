# TruthFunctor Quick Reference

**One-liner**: DP-native verification probes that emit PolicyTrace with constitutional scoring.

## Type Signature

```python
F: Agent[A, B] → PolicyTrace[TruthVerdict[B]]

TruthFunctor[S, A, B]  # S=probe state, A=input, B=output
```

## Core Types (9)

```python
# 1. Analysis modes
AnalysisMode.CATEGORICAL   # Verify composition laws
AnalysisMode.EPISTEMIC     # Verify axiom grounding
AnalysisMode.DIALECTICAL   # Inject contradictions
AnalysisMode.GENERATIVE    # Test regenerability

# 2. Constitutional reward (7 principles)
ConstitutionalScore(
    ethical=1.0,      # 2.0x weight (highest)
    composable=1.0,   # 1.5x weight
    joy_inducing=1.0, # 1.2x weight
    tasteful=1.0,
    curated=1.0,
    heterarchical=1.0,
    generative=1.0,
)
score.weighted_total  # → normalized [0, 1]

# 3. Final verdict
TruthVerdict(
    value=result,           # Actual output
    passed=True,           # Pass/fail
    confidence=0.95,       # [0, 1]
    reasoning="...",       # Why?
    galois_loss=None,      # Optional
)

# 4. Probe state
ProbeState(
    phase="testing",                    # Current phase
    observations=(obs1, obs2),          # Immutable
    laws_verified=frozenset(["law1"]), # Laws checked
    compression_ratio=0.8,              # Generative
)

# 5. Probe action
ProbeAction("test_associativity", (f, g, h))

# 6. Trace entry (s, a, s', r)
TraceEntry(
    state_before=s,
    action=a,
    state_after=s_prime,
    reward=r,
    reasoning="...",
)

# 7. Policy trace (Writer monad)
PolicyTrace(
    value=verdict,
    entries=[entry1, entry2, ...],
)
trace.total_reward  # Sum
trace.max_reward    # Max
trace.avg_reward    # Average

# 8. Base class
class MyProbe(TruthFunctor[S, A, B]):
    name = "my_probe"
    mode = AnalysisMode.CATEGORICAL

    @property
    def states(self) -> FrozenSet[S]: ...
    def actions(self, state: S) -> FrozenSet[ProbeAction]: ...
    def transition(self, state: S, action: ProbeAction) -> S: ...
    def reward(self, state: S, action: ProbeAction, next_state: S) -> ConstitutionalScore: ...
    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]: ...

# 9. Composed probe
probe1 >> probe2  # Sequential
probe1 | probe2   # Parallel
```

## Five Probe Types

```python
from agents.t.probes import (
    NullProbe,      # EPISTEMIC    (was MockAgent, FixtureAgent)
    ChaosProbe,     # DIALECTICAL  (was FailingAgent, NoiseAgent)
    WitnessProbe,   # CATEGORICAL  (was SpyAgent, CounterAgent)
    JudgeProbe,     # EPISTEMIC    (was JudgeAgent, OracleAgent)
    TrustProbe,     # GENERATIVE   (was TrustGate)
)
```

## Basic Usage

```python
from agents.t.probes import ChaosProbe, ChaosConfig, ChaosType

# Create probe
probe = ChaosProbe(ChaosConfig(
    chaos_type=ChaosType.FAILURE,
    intensity=0.5,
))

# Verify
trace = await probe.verify(my_agent, input_data)

# Results
print(f"Passed: {trace.value.passed}")
print(f"Confidence: {trace.value.confidence}")
print(f"Reward: {trace.total_reward}")
print(f"Steps: {len(trace.entries)}")
```

## Composition

```python
# Sequential: left then right
composed = probe1 >> probe2
trace = await composed.verify(agent, input)

# Parallel: both, merge traces
composed = probe1 | probe2
trace = await composed.verify(agent, input)
# trace.value is tuple: (verdict1, verdict2)
```

## Custom Probe Template

```python
from agents.t import TruthFunctor, AnalysisMode
from agents.t import ProbeState, ProbeAction, TraceEntry
from agents.t import ConstitutionalScore, PolicyTrace, TruthVerdict

class MyProbe(TruthFunctor[str, int, str]):
    """
    S = str (probe states: "init" | "testing" | "complete")
    A = int (agent input type)
    B = str (agent output type)
    """
    name = "my_probe"
    mode = AnalysisMode.CATEGORICAL

    @property
    def states(self) -> FrozenSet[str]:
        return frozenset(["init", "testing", "complete"])

    def actions(self, state: str) -> FrozenSet[ProbeAction]:
        if state == "init":
            return frozenset([ProbeAction("start")])
        elif state == "testing":
            return frozenset([ProbeAction("test", (i,)) for i in range(3)])
        else:
            return frozenset([ProbeAction("finish")])

    def transition(self, state: str, action: ProbeAction) -> str:
        match (state, action.name):
            case ("init", "start"):
                return "testing"
            case ("testing", "test"):
                return "testing"
            case (_, "finish"):
                return "complete"
            case _:
                return state

    def reward(
        self,
        state: str,
        action: ProbeAction,
        next_state: str,
    ) -> ConstitutionalScore:
        return ConstitutionalScore(
            ethical=1.0,      # Always respect autonomy
            composable=1.0,   # Tests composition
            joy_inducing=0.8, # Helpful feedback
        )

    async def verify(
        self,
        agent: Any,
        input: int,
    ) -> PolicyTrace[TruthVerdict[str]]:
        # Initialize trace
        trace = PolicyTrace(TruthVerdict(
            value="",
            passed=False,
            confidence=0.0,
            reasoning="In progress",
        ))

        # Initialize state
        state = ProbeState(phase="init", observations=())

        # State machine loop
        for action in self._get_action_sequence():
            next_phase = self.transition(state.phase, action)
            next_state = state.transition_to(next_phase)

            reward = self.reward(state.phase, action, next_phase)

            trace.append(TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Executed {action.name}",
            ))

            state = next_state

        # Update final verdict
        trace.value = TruthVerdict(
            value=str(input),
            passed=True,
            confidence=0.95,
            reasoning="Verification complete",
        )

        return trace

    def _get_action_sequence(self) -> list[ProbeAction]:
        """Generate action sequence for verification."""
        return [
            ProbeAction("start"),
            ProbeAction("test", (1,)),
            ProbeAction("test", (2,)),
            ProbeAction("finish"),
        ]
```

## DP Formulation Checklist

When implementing a TruthFunctor, ensure:

- ✓ `states`: Finite, well-defined state space
- ✓ `actions(s)`: State-dependent action space
- ✓ `transition(s, a)`: Deterministic state evolution
- ✓ `reward(s, a, s')`: Constitutional scoring
- ✓ `verify()`: Produces PolicyTrace with verdict
- ✓ `name`: Descriptive probe name
- ✓ `mode`: Maps to AnalysisMode
- ✓ `gamma`: Discount factor (default 0.99)

## Integration Hooks

```python
# W-gent: Witness trace entries
for entry in trace.entries:
    await observer.emit_mark(
        action=entry.action.name,
        reasoning=entry.reasoning,
        reward=entry.reward.weighted_total,
    )

# Director: Merit evaluation
merit = director.evaluate_trace(trace)

# Analysis: Filter by mode
categorical_probes = [
    p for p in probes
    if p.mode == AnalysisMode.CATEGORICAL
]
```

## Migration from T-gents

```python
# OLD (T-gent)
from agents.t import MockAgent, MockConfig
mock = MockAgent(MockConfig(output="result"))
result = await mock(input)

# NEW (TruthFunctor)
from agents.t.probes import NullProbe, NullConfig
probe = NullProbe(NullConfig(output="result"))
trace = await probe.verify(mock, input)
verdict = trace.value

# Benefits:
# - trace.entries: verification steps
# - trace.total_reward: constitutional alignment
# - verdict.confidence: certainty measure
# - verdict.reasoning: explanation
```

## File Locations

```
impl/claude/agents/t/
├── truth_functor.py                    # Core protocol
├── probes/
│   ├── __init__.py                     # Exports
│   ├── null_probe.py                   # NullProbe
│   ├── chaos_probe.py                  # ChaosProbe
│   ├── witness_probe.py                # WitnessProbe
│   ├── judge_probe.py                  # JudgeProbe
│   └── trust_probe.py                  # TrustProbe
├── TRUTHFUNCTOR_PROTOCOL.md            # Full docs
└── TRUTHFUNCTOR_QUICK_REF.md           # This file
```

## Import Patterns

```python
# Core types
from agents.t import (
    TruthFunctor,
    PolicyTrace,
    TruthVerdict,
    ConstitutionalScore,
    AnalysisMode,
)

# Concrete probes
from agents.t.probes import (
    NullProbe,
    ChaosProbe,
    WitnessProbe,
    JudgeProbe,
    TrustProbe,
)

# Everything
from agents.t.probes import *
```

## Key Insights

1. **Verification = DP**: Every probe is an MDP
2. **Trace = Proof**: PolicyTrace is the proof
3. **Constitutional Reward**: 7 principles, ethical weighted 2x
4. **Composition**: `>>` sequential, `|` parallel
5. **Writer Monad**: Natural accumulation pattern

---

**The trace IS the proof. The verdict IS the mark.**
