# Bootstrap Regeneration Plan

**Date**: Dec 8, 2025
**Status**: Ready to implement

---

## Executive Summary

Regenerate the 7 irreducible bootstrap agents from specification. The bootstrap directory is cleared; only `REGENERATION_VALIDATION_GUIDE.md` remains.

**Agents to implement** (in dependency order):
1. `types.py` - Agent[A,B] base class + core types
2. `id.py` - Identity agent
3. `ground.py` - Empirical seed
4. `compose.py` - Composition operator
5. `contradict.py` - Tension detection
6. `judge.py` - Seven mini-judges
7. `sublate.py` - Synthesis/hold
8. `fix.py` - Fixed-point iteration

---

## Implementation Order (Dependency Graph)

```
Level 0: types.py
    │
    ├───────────────────────┐
    │                       │
Level 1: id.py          ground.py
    │                       │
    ├───────────────────────┤
    │                       │
Level 2: compose.py     contradict.py
    │                       │
    ├───────────────────────┤
    │                       │
Level 3: judge.py       sublate.py
    │
    │
Level 4: fix.py
```

---

## Level 0: types.py

**Purpose**: Foundation types for all agents.

**Core Types**:
```python
Agent[A, B]           # Abstract base class
ComposedAgent[A, B, C] # Sequential composition
Result[T, E]          # Ok[T] | Err[E] for error handling
Tension               # Detected contradiction
Synthesis             # Resolution result
HoldTension           # Conscious holding of unresolved tension
Verdict               # ACCEPT | REVISE | REJECT
VerdictType           # Enum for verdict types
Principles            # The 7 evaluation criteria
```

**Key Implementation Details**:
- `Agent[A, B]` is abstract with `invoke(input: A) -> B` and `name` property
- `__rshift__` operator implements composition (`f >> g`)
- `ComposedAgent` preserves type safety: `Agent[A,B] >> Agent[B,C] → Agent[A,C]`
- Generic type parameters via `TypeVar`

**Spec Reference**: `spec/bootstrap.md` lines 1-40, `spec/anatomy.md`

---

## Level 1a: id.py

**Purpose**: Identity agent - composition unit.

**Type**: `Id: A → A`

**Laws**:
- `Id(x) = x`
- Left identity: `Id >> f = f`
- Right identity: `f >> Id = f`

**Key Implementation**:
```python
class Id(Agent[A, A]):
    async def invoke(self, input: A) -> A:
        return input

    def __rshift__(self, other: Agent[A, B]) -> Agent[A, B]:
        return other  # Right identity optimization

    def __rlshift__(self, other: Agent[B, A]) -> Agent[B, A]:
        return other  # Left identity via reverse operator
```

**Spec Reference**: `spec/bootstrap.md` lines 41-55

---

## Level 1b: ground.py

**Purpose**: Empirical seed - loads persona and world state.

**Type**: `Ground: Void → Facts`

**Output Structure**:
```python
@dataclass
class PersonaSeed:
    name: str
    roles: list[str]
    values: list[str]
    communication_style: str
    heuristics: list[str]
    dislikes: list[str]

@dataclass
class WorldSeed:
    date: str
    context: dict[str, Any]

@dataclass
class Facts:
    persona: PersonaSeed
    world: WorldSeed
    history: Optional[dict[str, Any]] = None
```

**Key Implementation**:
- Reads `spec/k-gent/persona.md` for persona data
- Parses markdown sections into structured PersonaSeed
- Optional: Use GroundParser agent for LLM-based extraction (autopoiesis)

**Spec Reference**: `spec/bootstrap.md` lines 98-142, `spec/k-gent/persona.md`

---

## Level 2a: compose.py

**Purpose**: The agent-that-makes-agents via sequential composition.

**Type**: `Compose: (Agent, Agent) → Agent`

**Key Implementation**:
```python
class ComposedAgent(Agent[A, C]):
    """f >> g: run f, then g on f's output."""
    def __init__(self, f: Agent[A, B], g: Agent[B, C]):
        self.f = f
        self.g = g

    async def invoke(self, input: A) -> C:
        intermediate = await self.f.invoke(input)
        return await self.g.invoke(intermediate)

def compose(f: Agent[A, B], g: Agent[B, C]) -> Agent[A, C]:
    """Convenience function for composition."""
    return ComposedAgent(f, g)
```

**Laws to Verify**:
- Associativity: `(f >> g) >> h ≡ f >> (g >> h)`
- Identity: `Id >> f ≡ f ≡ f >> Id`
- Closure: Composition produces an Agent

**Spec Reference**: `spec/bootstrap.md` lines 57-70, `spec/c-gents/composition.md`

---

## Level 2b: contradict.py

**Purpose**: Tension detection between two outputs.

**Type**: `Contradict: (A, B) → Tension | None`

**Tension Types**:
```python
class TensionMode(Enum):
    LOGICAL = "logical"        # A and ¬A
    PRAGMATIC = "pragmatic"    # A recommends X, B recommends ¬X
    AXIOLOGICAL = "axiological" # Serves value V vs ¬V
    TEMPORAL = "temporal"      # Past-self vs present-self
    AESTHETIC = "aesthetic"    # Style/taste conflicts

@dataclass
class Tension:
    thesis: Any
    antithesis: Any
    mode: TensionMode
    severity: float  # 0.0-1.0
    description: str
```

**Architecture**:
```python
class TensionDetector(Protocol):
    """Extensible detection via Protocol pattern."""
    def detect(self, a: Any, b: Any) -> Optional[Tension]: ...

class Contradict(Agent[ContradictInput, ContradictResult]):
    def __init__(self, detectors: list[TensionDetector] = None):
        self._detectors = detectors or default_detectors()
```

**Key Pattern**: Per-detector timeout and circuit breaker for robustness.

**Spec Reference**: `spec/bootstrap.md` lines 145-163

---

## Level 3a: judge.py

**Purpose**: The value function - evaluates against 7 principles.

**Type**: `Judge: (Agent, Principles) → Verdict`

**Architecture: Seven Mini-Judges**:
```python
# Seven individual judges, one per principle
judge_tasteful: Agent[JudgeInput, PartialVerdict]
judge_curated: Agent[JudgeInput, PartialVerdict]
judge_ethical: Agent[JudgeInput, PartialVerdict]
judge_joyful: Agent[JudgeInput, PartialVerdict]
judge_composable: Agent[JudgeInput, PartialVerdict]
judge_heterarchical: Agent[JudgeInput, PartialVerdict]
judge_generative: Agent[JudgeInput, PartialVerdict]

# Composed via >>
judge = (judge_tasteful >> judge_curated >> judge_ethical >>
         judge_joyful >> judge_composable >> judge_heterarchical >>
         judge_generative >> aggregate_verdicts)
```

**Types**:
```python
@dataclass
class JudgeInput:
    agent: Agent[Any, Any]
    principles: Principles
    context: Optional[dict] = None

@dataclass
class PartialVerdict:
    principle: str
    passed: bool
    reasons: list[str]
    confidence: float = 1.0

@dataclass
class Verdict:
    type: VerdictType  # ACCEPT, REVISE, REJECT
    partial_verdicts: list[PartialVerdict]
    revisions: Optional[list[str]] = None
    reasoning: str = ""
```

**The 7 Principles** (from spec/principles.md):
1. **Tasteful**: Clear, justified purpose; no bloat
2. **Curated**: Unique value; quality over quantity
3. **Ethical**: Transparent, respects agency
4. **Joy-inducing**: Personality, warmth, collaboration feel
5. **Composable**: Works with others; single outputs; category laws
6. **Heterarchical**: Can lead or follow; no fixed hierarchy
7. **Generative**: Regenerable from spec; compressed design

**Spec Reference**: `spec/bootstrap.md` lines 72-93, `spec/principles.md`

---

## Level 3b: sublate.py

**Purpose**: Hegelian synthesis - resolve or consciously hold tension.

**Type**: `Sublate: Tension → Synthesis | HoldTension`

**Key Types**:
```python
@dataclass
class Synthesis:
    resolution_type: str  # "preserve", "negate", "elevate"
    result: Any
    explanation: str
    preserved_from_thesis: list[str]
    preserved_from_antithesis: list[str]

@dataclass
class HoldTension:
    tension: Tension
    why_held: str
    revisit_conditions: list[str]
```

**Key Implementation**:
```python
class Sublate(Agent[list[Tension], SublateResult]):
    async def invoke(self, tensions: list[Tension]) -> SublateResult:
        for tension in tensions:
            resolution = await self._attempt_synthesis(tension)
            if can_synthesize(resolution):
                return Synthesis(...)
            else:
                return HoldTension(
                    tension=tension,
                    why_held="Synthesis not yet possible",
                    revisit_conditions=[...]
                )
```

**Pattern**: Sublate, don't overwrite - merge defaults, preserve both sides.

**Spec Reference**: `spec/bootstrap.md` lines 166-178, `spec/h-gents/hegel.md`

---

## Level 4: fix.py

**Purpose**: Fixed-point iteration - find stability.

**Type**: `Fix: (A → A) → A`

**Key Pattern: Fix Needs Memory**:
```python
@dataclass
class FixConfig:
    max_iterations: int = 100
    equality_check: Callable[[A, A], bool] = lambda a, b: a == b
    should_continue: Callable[[A, int], bool] = lambda a, i: True  # With iteration context

@dataclass
class FixResult(Generic[A]):
    value: A
    converged: bool
    iterations: int
    history: list[A] = field(default_factory=list)
    proximity: float = 0.0  # Adaptive convergence metric

class Fix(Agent[tuple[Callable[[A], Awaitable[A]], A], FixResult[A]]):
    async def invoke(self, input: tuple[Callable, A]) -> FixResult[A]:
        transform, initial = input
        current = initial

        for i in range(self._config.max_iterations):
            previous = current
            current = await transform(current)

            if self._config.equality_check(previous, current):
                return FixResult(
                    value=current,
                    converged=True,
                    iterations=i + 1
                )

        return FixResult(value=current, converged=False, iterations=self._config.max_iterations)
```

**Critical Pattern**: State accumulates between iterations (not stateless).

**Spec Reference**: `spec/bootstrap.md` lines 181-193, Idiom 1 (lines 318-347)

---

## Verification Checklist

After each level, verify:

- [ ] `mypy --strict bootstrap/` passes
- [ ] Composition laws hold (associativity, identity)
- [ ] Type signatures match spec
- [ ] Agent passes Judge (where applicable)

### Specific Tests

**Id**:
- [ ] `Id(x) == x` for all x
- [ ] `Id >> f == f` for any f
- [ ] `f >> Id == f` for any f

**Compose**:
- [ ] `(f >> g) >> h ≅ f >> (g >> h)`
- [ ] Types propagate: `Agent[A,B] >> Agent[B,C] → Agent[A,C]`

**Ground**:
- [ ] Returns Facts with persona and world
- [ ] Loads from spec/k-gent/persona.md

**Contradict**:
- [ ] Returns None for identical inputs
- [ ] Detects obvious conflicts

**Judge**:
- [ ] Returns Verdict with valid type
- [ ] Seven mini-judges compose correctly
- [ ] Id agent passes Judge

**Sublate**:
- [ ] Can synthesize simple tensions
- [ ] Can hold complex tensions

**Fix**:
- [ ] Converges for convergent functions
- [ ] Respects max_iterations
- [ ] State accumulates

---

## Implementation Notes

### From Previous Evolution (Improvements to Preserve)

1. **Id**: `__rlshift__` for left-identity, relaxed `is` check to equality
2. **Compose**: `FixComposedAgent` total via Either type, decoupled analyzer/transformer
3. **Types**: `FixConfig.should_continue` has iteration context
4. **Fix**: Proximity metric for adaptive convergence
5. **Judge**: Mini-judges as pure functions, immutable VerdictAccumulator
6. **Contradict**: Per-detector timeout/circuit breaker, TensionEvidence tracking

### Autopoiesis Consideration

The documents suggest using agents to help implement:
- K-gent for naming decisions
- CreativityCoach for design exploration
- HypothesisEngine for architecture validation
- Judge to review each agent

However, since bootstrap agents are being regenerated first, we'll do mechanical translation from spec, then validate with Judge once it's implemented.

---

## Estimated Implementation Order

1. **types.py** (~150 lines) - All base types and Agent class
2. **id.py** (~50 lines) - Simplest, validates composition works
3. **ground.py** (~100 lines) - Loads persona, returns Facts
4. **compose.py** (~75 lines) - ComposedAgent, compose function
5. **contradict.py** (~150 lines) - TensionDetector protocol, basic detectors
6. **judge.py** (~300 lines) - Seven mini-judges, aggregation
7. **sublate.py** (~150 lines) - Synthesis and HoldTension logic
8. **fix.py** (~100 lines) - Fixed-point with memory pattern

**Total**: ~1100 lines of implementation

---

## Success Criteria

From REGENERATION_VALIDATION_GUIDE.md:

**Required (Must Pass)**:
- ✓ All identity laws hold
- ✓ Composition is associative
- ✓ Ground returns Facts
- ✓ Judge returns Verdict
- ✓ Fix converges for convergent functions
- ✓ No runtime errors for valid inputs
- ✓ `mypy --strict` passes

**Acceptable Differences**:
- Variable names
- Code formatting
- Comment style
- Internal implementation details

**Unacceptable**:
- Different type signatures
- Different behavior for standard inputs
- Broken composition laws
- Wrong return types

---

## Ready to Begin

Start with Level 0: `types.py`
