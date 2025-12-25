# TruthFunctor Protocol

**Status**: Core implementation complete
**Location**: `/impl/claude/agents/t/truth_functor.py`
**Created**: 2025-12-24

## Overview

TruthFunctor is the DP-native verification protocol that replaces the old T-gent abstraction. Every TruthFunctor is a morphism that verifies agent behavior while emitting a PolicyTrace as proof.

**Key Insight**: Verification IS a decision process. The probe navigates a state space of observations, taking actions (tests), accumulating constitutional reward, and producing a trace that IS the proof.

## Architecture

```
F: Agent[A, B] → PolicyTrace[TruthVerdict[B]]

TruthFunctor[S, A, B] where:
  S: Probe state space (phases of verification)
  A: Agent input type
  B: Agent output type

DP Formulation:
  - states: Valid probe states (frozenset)
  - actions(s): Valid actions from state s
  - transition(s, a): State evolution s → s'
  - reward(s, a, s'): Constitutional scoring
  - gamma: Discount factor (default 0.99)
  - verify(): Main entry point, produces PolicyTrace
```

## Core Types

### 1. AnalysisMode

Four modes from the Analysis Operad:

```python
class AnalysisMode(Enum):
    CATEGORICAL = auto()   # Verify composition laws
    EPISTEMIC = auto()     # Verify axiom grounding
    DIALECTICAL = auto()   # Inject contradictions
    GENERATIVE = auto()    # Test regenerability
```

### 2. ConstitutionalScore

Reward function based on 7 constitutional principles:

```python
@dataclass(frozen=True)
class ConstitutionalScore:
    tasteful: float = 0.0       # Clear purpose, justified design
    curated: float = 0.0        # Intentional, not exhaustive
    ethical: float = 0.0        # Augments humans (2.0x weight)
    joy_inducing: float = 0.0   # Delightful interaction (1.2x)
    composable: float = 0.0     # Morphism in category (1.5x)
    heterarchical: float = 0.0  # Flux, not hierarchy
    generative: float = 0.0     # Spec is compression

    @property
    def weighted_total(self) -> float:
        """Weighted sum, ethical has 2.0x weight"""
```

Operations:
- `score1 + score2`: Component-wise addition
- `score * scalar`: Scalar multiplication

### 3. TruthVerdict[B]

Final result of verification:

```python
@dataclass(frozen=True)
class TruthVerdict(Generic[B]):
    value: B                      # Actual output from agent
    passed: bool                  # Whether verification succeeded
    confidence: float             # Confidence in [0, 1]
    reasoning: str                # Human-readable explanation
    galois_loss: float | None     # Optional Galois connection loss
    timestamp: datetime
```

### 4. ProbeState

State during verification:

```python
@dataclass(frozen=True)
class ProbeState:
    phase: str                              # Current phase (e.g., "testing")
    observations: tuple[Any, ...]           # Immutable observations
    laws_verified: FrozenSet[str]           # Laws verified so far
    compression_ratio: float                # Generative compression

    # Convenience methods
    def with_observation(self, obs) -> ProbeState
    def with_law(self, law_name) -> ProbeState
    def transition_to(self, new_phase) -> ProbeState
```

### 5. ProbeAction

Action the probe can take:

```python
@dataclass(frozen=True)
class ProbeAction:
    name: str                    # Action name
    parameters: tuple[Any, ...]  # Action parameters

# Examples:
ProbeAction("test_associativity", (f, g, h))
ProbeAction("inject_contradiction", ("axiom_1", "axiom_2"))
ProbeAction("measure_compression", ())
```

### 6. TraceEntry

Single step in the trace:

```python
@dataclass(frozen=True)
class TraceEntry:
    state_before: ProbeState       # s
    action: ProbeAction            # a
    state_after: ProbeState        # s'
    reward: ConstitutionalScore    # r
    reasoning: str                 # Why this action?
    timestamp: datetime
```

This is the (s, a, s', r) tuple from DP formulation, plus reasoning.

### 7. PolicyTrace[B]

Writer monad for accumulated trace:

```python
@dataclass
class PolicyTrace(Generic[B]):
    value: B                       # Final verdict
    entries: list[TraceEntry]      # Trace of transitions

    def append(self, entry: TraceEntry) -> PolicyTrace[B]

    @property
    def total_reward(self) -> float   # Sum of rewards
    @property
    def max_reward(self) -> float     # Max single-step reward
    @property
    def avg_reward(self) -> float     # Average reward
```

The trace IS the proof. Each entry shows what was tested, why, and what reward was earned.

### 8. TruthFunctor[S, A, B]

Abstract base class:

```python
class TruthFunctor(ABC, Generic[S, A, B]):
    name: str
    mode: AnalysisMode
    gamma: float = 0.99

    # DP formulation (must implement)
    @property
    @abstractmethod
    def states(self) -> FrozenSet[S]:
        """Valid probe states"""

    @abstractmethod
    def actions(self, state: S) -> FrozenSet[ProbeAction]:
        """Valid actions for state"""

    @abstractmethod
    def transition(self, state: S, action: ProbeAction) -> S:
        """State transition"""

    @abstractmethod
    def reward(self, state: S, action: ProbeAction, next_state: S) -> ConstitutionalScore:
        """Constitutional reward"""

    # Main entry point (must implement)
    @abstractmethod
    async def verify(self, agent: Any, input: A) -> PolicyTrace[TruthVerdict[B]]:
        """Verify agent, produce traced verdict"""

    # Composition operators
    def __rshift__(self, other) -> ComposedProbe:
        """self >> other: Sequential composition"""

    def __or__(self, other) -> ComposedProbe:
        """self | other: Parallel composition"""
```

### 9. ComposedProbe

Product of two probes:

```python
@dataclass
class ComposedProbe(TruthFunctor):
    left: TruthFunctor
    right: TruthFunctor
    op: str  # "seq" | "par"

    # Sequential (>>): Run left, then right
    # Parallel (|): Run both, merge traces
```

State space: `left.states × right.states` (product)

## Five Probe Types

These replace the old T-gent types:

| Probe | Old T-gents | Mode | Purpose |
|-------|-------------|------|---------|
| **NullProbe** | MockAgent, FixtureAgent | EPISTEMIC | Constants & fixtures |
| **ChaosProbe** | FailingAgent, NoiseAgent, etc. | DIALECTICAL | Chaos & perturbation |
| **WitnessProbe** | SpyAgent, CounterAgent, etc. | CATEGORICAL | Observation & counting |
| **JudgeProbe** | JudgeAgent, OracleAgent | EPISTEMIC | Semantic evaluation |
| **TrustProbe** | TrustGate | GENERATIVE | Capital-backed gating |

## Usage Examples

### Basic Verification

```python
from agents.t import TruthFunctor, PolicyTrace, TruthVerdict
from agents.t.probes import ChaosProbe, ChaosConfig, ChaosType

# Create probe
probe = ChaosProbe(ChaosConfig(
    chaos_type=ChaosType.FAILURE,
    intensity=0.5
))

# Verify agent
trace: PolicyTrace[TruthVerdict] = await probe.verify(my_agent, input_data)

# Inspect results
print(f"Passed: {trace.value.passed}")
print(f"Confidence: {trace.value.confidence}")
print(f"Total reward: {trace.total_reward}")
print(f"Steps: {len(trace.entries)}")

# Examine trace
for entry in trace.entries:
    print(f"Action: {entry.action.name}")
    print(f"Reward: {entry.reward.weighted_total}")
    print(f"Reasoning: {entry.reasoning}")
```

### Sequential Composition

```python
from agents.t.probes import WitnessProbe, JudgeProbe

witness = WitnessProbe(WitnessConfig(...))
judge = JudgeProbe(JudgeConfig(...))

# Sequential: run witness, then judge
composed = witness >> judge

trace = await composed.verify(agent, input)
# trace.entries contains entries from both probes
```

### Parallel Composition

```python
from agents.t.probes import NullProbe, ChaosProbe

null_probe = NullProbe(NullConfig(...))
chaos_probe = ChaosProbe(ChaosConfig(...))

# Parallel: run both, merge results
composed = null_probe | chaos_probe

trace = await composed.verify(agent, input)
# trace.value is tuple: (null_verdict, chaos_verdict)
```

### Custom Probe

```python
from agents.t import TruthFunctor, AnalysisMode, ProbeState, ProbeAction
from agents.t import ConstitutionalScore, PolicyTrace, TruthVerdict

class MyProbe(TruthFunctor[str, int, str]):
    name = "my_probe"
    mode = AnalysisMode.CATEGORICAL

    @property
    def states(self) -> FrozenSet[str]:
        return frozenset(["init", "testing", "complete"])

    def actions(self, state: str) -> FrozenSet[ProbeAction]:
        if state == "init":
            return frozenset([ProbeAction("start_test")])
        elif state == "testing":
            return frozenset([ProbeAction("run_test", (i,)) for i in range(3)])
        else:
            return frozenset([ProbeAction("finish")])

    def transition(self, state: str, action: ProbeAction) -> str:
        if state == "init":
            return "testing"
        elif state == "testing" and action.name == "run_test":
            return "testing"  # Stay in testing
        else:
            return "complete"

    def reward(self, state: str, action: ProbeAction, next_state: str) -> ConstitutionalScore:
        # Higher reward for compositional testing
        return ConstitutionalScore(
            composable=1.0 if action.name == "run_test" else 0.5,
            ethical=1.0,  # Always respect agent autonomy
        )

    async def verify(self, agent, input: int) -> PolicyTrace[TruthVerdict[str]]:
        trace = PolicyTrace(TruthVerdict(
            value="pending",
            passed=False,
            confidence=0.0,
            reasoning="Not yet verified"
        ))

        state = ProbeState(phase="init", observations=())

        # Run through states
        for action in [
            ProbeAction("start_test"),
            ProbeAction("run_test", (1,)),
            ProbeAction("finish"),
        ]:
            next_state_phase = self.transition(state.phase, action)
            next_state = state.transition_to(next_state_phase)

            reward = self.reward(state.phase, action, next_state_phase)

            trace.append(TraceEntry(
                state_before=state,
                action=action,
                state_after=next_state,
                reward=reward,
                reasoning=f"Executed {action.name}"
            ))

            state = next_state

        # Update verdict
        trace.value = TruthVerdict(
            value=str(input),
            passed=True,
            confidence=0.95,
            reasoning="All tests passed"
        )

        return trace
```

## Integration Points

### W-gent (Witness)

PolicyTrace entries can be witnessed:

```python
from agents.w import Observer

# Verify with witness
trace = await probe.verify(agent, input)

# Each trace entry can be marked
for entry in trace.entries:
    await observer.emit_mark(
        action=entry.action.name,
        reasoning=entry.reasoning,
        reward=entry.reward.weighted_total
    )
```

### Director (Merit Function)

ConstitutionalScore integrates with Director's merit:

```python
from services.director import Director

# Director uses constitutional scores to evaluate probes
trace = await probe.verify(agent, input)
merit = director.evaluate_trace(trace)  # Uses total_reward
```

### Analysis Service

TruthFunctors map to AnalysisMode:

```python
from services.analysis import AnalysisService

# Each mode gets specific probes
categorical_probes = [p for p in probes if p.mode == AnalysisMode.CATEGORICAL]
epistemic_probes = [p for p in probes if p.mode == AnalysisMode.EPISTEMIC]
```

## Design Rationale

### Why DP Formulation?

1. **Formal Semantics**: Every probe is a well-defined MDP
2. **Composability**: Product states, sum rewards
3. **Optimality**: Can apply RL algorithms to learn better verification strategies
4. **Traceability**: PolicyTrace = proof of verification

### Why Constitutional Scoring?

1. **Alignment**: Rewards reflect kgents principles
2. **Weighted Ethics**: Ethical considerations have 2x weight
3. **Multi-objective**: Balance 7 principles, not just pass/fail
4. **Transparency**: Each principle scored separately

### Why Writer Monad?

1. **Accumulation**: Natural way to build up trace
2. **Composition**: Traces compose naturally with >>
3. **Purity**: Verification doesn't modify agent
4. **Proof**: Trace IS the proof, not just side effect

## Migration Path

Old T-gents → TruthFunctor:

```python
# OLD: MockAgent
from agents.t import MockAgent, MockConfig
mock = MockAgent(MockConfig(output="result"))
result = await mock(input)

# NEW: NullProbe
from agents.t.probes import NullProbe, NullConfig
probe = NullProbe(NullConfig(output="result"))
trace = await probe.verify(mock, input)
verdict = trace.value

# Benefits:
# - trace.entries shows verification steps
# - trace.total_reward shows constitutional alignment
# - verdict.confidence shows certainty
```

## Files

```
impl/claude/agents/t/
├── truth_functor.py          # Core protocol (this file)
├── probes/
│   ├── __init__.py          # Exports all types
│   ├── null_probe.py        # NullProbe (EPISTEMIC)
│   ├── chaos_probe.py       # ChaosProbe (DIALECTICAL)
│   ├── witness_probe.py     # WitnessProbe (CATEGORICAL)
│   ├── judge_probe.py       # JudgeProbe (EPISTEMIC)
│   └── trust_probe.py       # TrustProbe (GENERATIVE)
└── TRUTHFUNCTOR_PROTOCOL.md # This documentation
```

## Next Steps

1. **Implement Five Probes**: Create concrete implementations
2. **Test Suite**: Property-based tests for DP laws
3. **Integration Tests**: Verify with real agents
4. **Director Integration**: Wire constitutional scores to merit
5. **UI Integration**: Display PolicyTrace in web UI
6. **Documentation**: Add examples to docs/skills/

## References

- T-gent Types I-V: `docs/skills/test-patterns.md`
- Analysis Operad: `spec/a-gents/analysis.md`
- Constitutional Principles: `CLAUDE.md`
- DP Formulation: Bellman equations, MDP theory
- Writer Monad: Category theory, monadic composition

---

**Philosophy**: The trace IS the proof. The verdict IS the mark. Constitutional reward IS the merit function.
