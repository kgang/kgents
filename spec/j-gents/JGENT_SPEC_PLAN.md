# J-gents Specification Plan: JIT Agent Intelligence (JAIgent)

**Status**: DRAFT
**Author**: Synthesized from Kent's research + existing kgents architecture
**Date**: December 2025

---

## Executive Summary

J-gents introduce **Just-in-Time Agent Intelligence** to kgents—the ability for agents to classify reality, lazily expand computation, compile ephemeral sub-agents on demand, and collapse safely to ground truth when stability is threatened.

This document reconciles the JAIgent research with existing kgents specifications, identifying:
1. Concepts that already exist (preserve)
2. Concepts that need integration (extend)
3. Novel concepts that need specification (create)
4. Tensions that need resolution (synthesize)

---

## Part 1: Reconciliation Analysis

### 1.1 Existing Concepts That Map to JAIgent

| JAIgent Concept | Existing kgents | Alignment | Action |
|-----------------|-----------------|-----------|--------|
| Ground Truth / Golden Parachute | `Ground (⊥)` in bootstrap.md | **EXCELLENT** | Preserve as-is |
| Dialectic (Thesis/Antithesis/Synthesis) | `Contradict + Sublate` in bootstrap.md | **EXCELLENT** | Preserve as-is |
| Fixed-point iteration until stable | `Fix (μ)` in bootstrap.md | **GOOD** | Extend with entropy budget |
| Composability | `Compose (∘)` in C-gents | **GOOD** | Extend with lazy semantics |
| Self-production | Autopoiesis in impl/claude | **PARTIAL** | Formalize as JIT compilation |
| Deferred computation | Maybe/Async functors | **PARTIAL** | Extend with Promise abstraction |
| Stability/Safety | SandboxTestAgent, SafetyConfig | **PARTIAL** | Add Chaosmonger checks |

### 1.2 Novel JAIgent Concepts Requiring New Specification

| Concept | Description | Why Novel |
|---------|-------------|-----------|
| **Reality Classification** | DETERMINISTIC / PROBABILISTIC / CHAOTIC trichotomy | Formal decision point for decomposition |
| **Lazy Promise Tree** | Unevaluated computation tree with forward/backward flow | Explicit laziness as first-class citizen |
| **Entropy Budget** | Diminishing computation budget per recursion depth | Formal resource bounds per depth |
| **Chaosmonger** | AST-based stability analysis before execution | Algorithmic pre-filter before Judge |
| **JIT Compilation** | Generate agent classes on-the-fly | Active autopoiesis vs. measurement |
| **Test-Driven Reality** | Generate unit tests alongside code | Accountability mechanism |
| **Global Memoization** | Hash-based promise caching | Ecosystem optimization |

### 1.3 Tensions Requiring Synthesis

#### Tension 1: Minimal Output Principle vs. JIT Agent Compilation

**Thesis (kgents)**: "Single output per invocation—don't ask agents to combine multiple outputs"

**Antithesis (JAIgent)**: "JIT compiles entire agent classes on demand"

**Synthesis**: JIT compilation operates at the **META level**. The Meta-Architect produces ONE output: an agent class. That agent class, once compiled, follows the minimal output principle. JIT compilation is about producing **agents**, not asking agents to produce **arrays of outputs**.

```
Meta-Architect: (Intent, Context) → AgentClass  // Single output: one agent
CompiledAgent: Input → Output                   // Single output: one result
```

#### Tension 2: Heterarchy vs. Recursive Depth Limits

**Thesis (kgents)**: "No fixed hierarchy—leadership is contextual"

**Antithesis (JAIgent)**: "Hard depth limits, entropy budgets per level"

**Synthesis**: Depth limits are **SAFETY BOUNDS**, not hierarchy. An agent at depth 3 can still lead or follow contextually—the depth limit prevents infinite regression, not role assignment. Think of it as "recursion budget" not "chain of command."

```python
# NOT hierarchy (who reports to whom)
# YES safety (prevent runaway recursion)
class DepthLimit:
    max_depth: int = 3
    entropy_budget: Callable[[int], float] = lambda d: 1.0 / (d + 1)
```

#### Tension 3: Judge vs. Chaosmonger

**Thesis (kgents)**: "Judge embodies human values—taste cannot be computed"

**Antithesis (JAIgent)**: "Chaosmonger performs algorithmic stability analysis"

**Synthesis**: Chaosmonger is **PRE-JUDGE**. It filters out unstable code BEFORE Judge evaluates it. Judge still has final say on taste/ethics/joy. Chaosmonger handles what CAN be computed (cyclomatic complexity, import analysis); Judge handles what CANNOT (is this tasteful?).

```
Pipeline: GeneratedCode → Chaosmonger → [stable?] → Judge → [accept?] → Execute
                              ↓                         ↓
                        [unstable → Ground]       [reject → Ground]
```

---

## Part 2: J-gents Specification Structure

### 2.1 Proposed Directory Structure

```
spec/j-gents/
├── README.md              # Overview: JIT Agent Intelligence
├── reality.md             # Reality Classification
├── lazy.md                # Lazy Promises & Accountability
├── stability.md           # Entropy Budgets & Chaosmonger
├── jit.md                 # JIT Agent Compilation
└── integration.md         # Ecosystem (memoization, markets)
```

### 2.2 Core Specification: README.md

```markdown
# J-gents: Just-in-Time Agent Intelligence

The letter **J** represents agents that embody **JIT (Just-in-Time) intelligence**—
the ability to classify reality, defer computation, compile ephemeral sub-agents,
and collapse safely when stability is threatened.

## Philosophy

> "Determine the nature of reality; compile the mind to match it; collapse to safety."

J-gents treat reality as a tree of **unobserved promises**. When confronted with
a complex problem, a J-gent:

1. **Classifies** the reality (deterministic, probabilistic, chaotic)
2. **Defers** computation until needed (lazy promise expansion)
3. **Compiles** specialized sub-agents if needed (JIT autopoiesis)
4. **Validates** results before accepting (test-driven accountability)
5. **Collapses** to Ground if stability is threatened (safety-first)

## Relationship to Bootstrap

J-gents are **derivable** from bootstrap agents:

| J-gent Component | Derived From |
|------------------|--------------|
| Reality Classification | Ground + Judge |
| Lazy Promises | Fix + Compose |
| JIT Compilation | Autopoiesis (Fix + Ground + Compose) |
| Stability Analysis | Judge (algorithmic subset) |
| Accountability | Contradict (test vs. result) |
| Safety Collapse | Ground (return to known state) |

J-gents do NOT add new irreducibles—they are a **coordination pattern** over
existing bootstrap primitives.
```

### 2.3 Specification: reality.md

```markdown
# Reality Classification

J-gents classify tasks into three reality types before proceeding.

## The Trichotomy

### 1. DETERMINISTIC Reality
- Task is atomic, well-defined, bounded
- Single-step execution possible
- Examples: "Add 2+2", "Query SQL", "Format JSON"
- **Action**: Execute directly with standard tool

### 2. PROBABILISTIC Reality
- Task is complex, requires decomposition
- Multiple possible approaches
- Examples: "Analyze logs", "Refactor module", "Design API"
- **Action**: Decompose into sub-promises, spawn child J-gents

### 3. CHAOTIC Reality
- Task is unbounded, recursive, or unstable
- Exceeds entropy budget or depth limit
- Examples: "Solve everything", "Infinite improvement loop"
- **Action**: Collapse to Ground immediately

## Classification Agent

```python
RealityClassifier: (Intent, Context, EntropyBudget) → Reality
Reality = DETERMINISTIC | PROBABILISTIC | CHAOTIC
```

### Classification Heuristics

1. **Atomic test**: Can this be done in one tool call?
   - Yes → DETERMINISTIC
   - No → continue

2. **Decomposition test**: Can this be broken into sub-tasks?
   - Yes → PROBABILISTIC
   - No → continue

3. **Boundedness test**: Is there a clear stopping condition?
   - Yes → PROBABILISTIC
   - No → CHAOTIC

4. **Budget test**: Is entropy budget > threshold?
   - Yes → proceed with classification
   - No → CHAOTIC (force collapse)
```

### 2.4 Specification: lazy.md

```markdown
# Lazy Promises & Accountability

J-gents separate **Forward Responsibility** (promises) from
**Backward Accountability** (proofs).

## The Promise Abstraction

```python
@dataclass
class Promise(Generic[T]):
    intent: str                    # What this promises to deliver
    context: dict                  # Available context at promise time
    ground: T                      # Fallback if promise fails
    resolved: Optional[T] = None   # Lazily populated on demand
    proof: Optional[Test] = None   # Validation for resolved value
```

## Forward Responsibility (Root → Leaf)

- **Direction**: Parent promises before child executes
- **Nature**: Optimistic, lazy, deferred
- **Mechanism**: Build dependency DAG without computing

```
Root Promise: "Fix the bug"
    ├── Child Promise: "Diagnose root cause"
    │       ├── Leaf: "Read logs" (DETERMINISTIC)
    │       └── Leaf: "Parse stack trace" (DETERMINISTIC)
    └── Child Promise: "Apply fix"
            └── Leaf: "Modify code" (DETERMINISTIC)
```

## Backward Accountability (Leaf → Root)

- **Direction**: Leaf proves before parent accepts
- **Nature**: Pessimistic, strict, validated
- **Mechanism**: Test-Driven Reality

```python
# Generate proof alongside result
async def resolve(promise: Promise[T]) -> T:
    result = await compute(promise)
    proof = await generate_test(promise.intent, result)

    if not proof(result):
        return promise.ground  # Collapse to safety

    promise.resolved = result
    promise.proof = proof
    return result
```

## Test-Driven Reality

Every non-trivial promise generates a validation test:

```python
TestGenerator: (Intent, Result) → Test
Test: Result → bool
```

The result is NOT accepted unless `test(result) == True`.
Failure collapses to `promise.ground`.
```

### 2.5 Specification: stability.md

```markdown
# Entropy Budgets & Stability Analysis

J-gents maintain stability through entropy budgets and the Chaosmonger.

## Entropy Budget

Computation budget diminishes with recursion depth:

```python
entropy_budget(depth: int) -> float:
    return 1.0 / (depth + 1)

# depth=0: budget=1.0 (full freedom)
# depth=1: budget=0.5 (half freedom)
# depth=2: budget=0.33 (third freedom)
# depth=3: budget=0.25 (quarter freedom)
```

When budget < threshold, force CHAOTIC classification → collapse to Ground.

## The Chaosmonger

Pre-Judge stability filter for JIT-compiled code.

### Stability Metrics

1. **Cyclomatic Complexity**: Control flow paths
   - `complexity(ast) < budget * MAX_COMPLEXITY`

2. **Branching Factor**: Expected tree width
   - `branching(ast) < budget * MAX_BRANCHING`

3. **Import Risk**: Dependency stability
   - `import_risk(ast) < budget * MAX_IMPORT_RISK`

4. **Recursion Check**: Unbounded loops
   - `has_unbounded_recursion(ast) → REJECT`

### Chaosmonger Pipeline

```python
Chaosmonger: (AST, EntropyBudget) → Stable | Unstable(reason)

if chaosmonger(ast, budget) == Unstable:
    return Ground  # Don't even try to execute
else:
    proceed_to_judge(ast)  # Judge evaluates taste/ethics
```

## Relationship to Judge

| Concern | Handler | Computable? |
|---------|---------|-------------|
| Cyclomatic complexity | Chaosmonger | Yes |
| Import safety | Chaosmonger | Yes |
| Unbounded recursion | Chaosmonger | Yes |
| Tasteful? | Judge | No |
| Ethical? | Judge | No |
| Joy-inducing? | Judge | No |

Chaosmonger handles the **computable subset** of safety.
Judge handles the **irreducible human values**.
```

### 2.6 Specification: jit.md

```markdown
# JIT Agent Compilation

The defining feature of J-gents: compile specialized agents on demand.

## The Meta-Architect

When a J-gent classifies reality as PROBABILISTIC and determines that
no existing agent fits the need, it invokes the Meta-Architect.

```python
MetaArchitect: (Intent, Context, Constraints) → AgentClass

# Input
intent = "Parse Java stack traces and identify OOM patterns"
context = {"log_format": "log4j", "expected_patterns": ["OutOfMemory"]}
constraints = {"max_complexity": 10, "allowed_imports": ["re", "dataclasses"]}

# Output
class StackTraceParser(Agent[str, ParsedTrace]):
    async def invoke(self, log_text: str) -> ParsedTrace:
        # Generated implementation
        ...
```

## Compilation Pipeline

```
Intent → MetaArchitect → SourceCode → Chaosmonger → [stable?]
                                                        ↓
                                    [unstable] ← Ground
                                                        ↓
                                    [stable] → Judge → [accept?]
                                                           ↓
                                           [reject] ← Ground
                                                           ↓
                                           [accept] → Compile → Execute
```

## Ephemeral Agents

JIT-compiled agents are **ephemeral**:
- Created for a specific task instance
- Not persisted to spec or impl
- Garbage collected after task completion
- May be cached by hash for reuse (see integration.md)

## Safety Invariants

1. **Sandbox execution**: JIT agents run in restricted environment
2. **Import whitelist**: Only allowed modules
3. **No network**: Cannot make external calls unless explicit
4. **Time-bounded**: Hard timeout enforced
5. **Type-checked**: Must pass mypy before execution

## Relationship to Autopoiesis

Autopoiesis (existing) = **Measurement** of self-production score
JIT Compilation (new) = **Active** self-production on demand

```
Autopoiesis Score = (lines generated by kgents) / (total lines)
JIT Contribution = (ephemeral agents compiled) / (total invocations)
```
```

---

## Part 3: Modifications to Existing Specs

### 3.1 bootstrap.md Additions

Add to "Applied Idioms" section:

```markdown
### Idiom 7: Reality is Trichotomous

> Classification precedes computation.

Before expanding a task, classify its reality:

| Reality | Characteristic | Action |
|---------|---------------|--------|
| DETERMINISTIC | Atomic, bounded | Execute directly |
| PROBABILISTIC | Complex, decomposable | Spawn sub-agents |
| CHAOTIC | Unbounded, unstable | Collapse to Ground |

This is Fix applied to the decision of WHETHER to iterate:
- DETERMINISTIC: No iteration needed
- PROBABILISTIC: Iterate with budget
- CHAOTIC: Iteration forbidden
```

### 3.2 c-gents/functors.md Additions

Add new functor:

```markdown
### Promise Functor

Defers computation until explicitly resolved.

```
Agent: A → B
PromiseAgent: A → Promise<B>

Promise<B> is not computed until resolve() called.
If resolve fails, returns Ground value.
```

Laws:
- Promise preserves identity: `Promise(Id) = PromiseId`
- Promise preserves composition: `Promise(f >> g) = Promise(f) >> Promise(g)`
```

### 3.3 anatomy.md Additions

Add section on ephemeral agents:

```markdown
## Ephemeral Agents

Some agents exist only for a single task instance:

- **JIT-compiled**: Generated by Meta-Architect for specific intent
- **Not persisted**: No entry in spec/ or impl/
- **Sandboxed**: Run with restricted permissions
- **Cached by hash**: May be reused if same intent + context

Ephemeral agents still follow all seven principles—they're evaluated
by Judge before execution. They just don't persist beyond their task.
```

---

## Part 4: Implementation Changes (impl/claude)

### 4.1 New Directory: agents/j/

```
impl/claude/agents/j/
├── __init__.py
├── reality.py         # RealityClassifier agent
├── promise.py         # Promise[T] data structure
├── chaosmonger.py     # AST stability analyzer
├── meta_architect.py  # JIT agent compiler
└── jgent.py           # Main JGent coordinator
```

### 4.2 Core Implementation: jgent.py

```python
"""
J-gent: Just-in-Time Agent Intelligence

The coordination agent that:
1. Classifies reality
2. Manages lazy promise tree
3. Invokes Meta-Architect when needed
4. Enforces entropy budgets
5. Collapses to Ground on instability
"""

from typing import TypeVar, Generic
from dataclasses import dataclass
from bootstrap.types import Agent, Result
from bootstrap.ground import Ground
from bootstrap.fix import Fix
from .reality import RealityClassifier, Reality
from .promise import Promise
from .chaosmonger import Chaosmonger
from .meta_architect import MetaArchitect

T = TypeVar('T')

@dataclass
class JGentConfig:
    max_depth: int = 3
    entropy_threshold: float = 0.1
    chaosmonger_enabled: bool = True

class JGent(Agent[str, T], Generic[T]):
    """Main J-gent coordinator."""

    def __init__(
        self,
        ground: T,
        config: JGentConfig = JGentConfig(),
        depth: int = 0
    ):
        self.ground = ground
        self.config = config
        self.depth = depth
        self.entropy_budget = 1.0 / (depth + 1)

    @property
    def name(self) -> str:
        return f"JGent[depth={self.depth}]"

    async def invoke(self, intent: str) -> T:
        # Check entropy budget
        if self.entropy_budget < self.config.entropy_threshold:
            return self.ground  # Collapse to safety

        # Classify reality
        reality = await RealityClassifier().invoke(
            (intent, self.entropy_budget)
        )

        match reality:
            case Reality.DETERMINISTIC:
                return await self._execute_atomic(intent)
            case Reality.PROBABILISTIC:
                return await self._decompose_and_resolve(intent)
            case Reality.CHAOTIC:
                return self.ground  # Collapse to safety

    async def _execute_atomic(self, intent: str) -> T:
        """Execute deterministic task directly."""
        # Use existing tool/agent
        ...

    async def _decompose_and_resolve(self, intent: str) -> T:
        """Decompose into sub-promises, potentially JIT-compile."""
        # Check if existing agent fits
        existing = await self._find_existing_agent(intent)
        if existing:
            return await existing.invoke(intent)

        # JIT compile new agent
        source = await MetaArchitect().invoke(intent)

        # Stability check
        if self.config.chaosmonger_enabled:
            stability = await Chaosmonger().invoke(
                (source, self.entropy_budget)
            )
            if not stability.is_stable:
                return self.ground  # Unstable → collapse

        # Compile and execute
        agent = self._compile_agent(source)

        # Create child J-gent with reduced budget
        child = JGent(
            ground=self.ground,
            config=self.config,
            depth=self.depth + 1
        )

        return await agent.invoke(intent)
```

### 4.3 Extensions to Existing Code

#### bootstrap/fix.py

Add entropy budget tracking:

```python
@dataclass
class FixConfig:
    max_iterations: int = 100
    entropy_budget: Optional[float] = None  # NEW

@dataclass
class FixResult(Generic[A]):
    value: A
    converged: bool
    iterations: int
    history: tuple[A, ...]
    proximity: float
    entropy_remaining: float  # NEW: Track budget consumption
```

#### agents/e/safety.py

Integrate Chaosmonger checks:

```python
class SafetyConfig:
    # Existing
    read_only: bool = True
    syntax_check: bool = True
    type_check: bool = True
    self_test: bool = True
    convergence_threshold: float = 0.95

    # NEW: Chaosmonger integration
    chaosmonger_enabled: bool = True
    max_cyclomatic_complexity: int = 20
    max_branching_factor: int = 5
    allowed_imports: set[str] = field(default_factory=lambda: {
        "typing", "dataclasses", "asyncio", "re", "json"
    })
```

#### agents/e/experiment.py

Add test generation:

```python
class ExperimentAgent:
    async def invoke(self, input: ExperimentInput) -> ExperimentResult:
        # Existing: generate improvement
        improvement = await self._generate_improvement(input)

        # NEW: Generate accountability test
        test = await self._generate_test(input.hypothesis, improvement)

        return ExperimentResult(
            improvement=improvement,
            test=test,  # NEW
            status=...
        )

    async def _generate_test(
        self,
        hypothesis: str,
        improvement: CodeImprovement
    ) -> str:
        """Generate unit test that validates the improvement."""
        ...
```

---

## Part 5: Implementation Phases

### Phase 1: Core Data Structures (Week 1)
- [ ] Create `spec/j-gents/` directory
- [ ] Write README.md, reality.md
- [ ] Implement `Promise[T]` data type
- [ ] Implement `RealityClassifier` agent

### Phase 2: Stability Layer (Week 2)
- [ ] Write stability.md spec
- [ ] Implement `Chaosmonger` AST analyzer
- [ ] Integrate with existing `SafetyConfig`
- [ ] Add entropy budget to `Fix`

### Phase 3: JIT Compilation (Week 3)
- [ ] Write jit.md spec
- [ ] Implement `MetaArchitect` agent
- [ ] Sandboxed execution environment
- [ ] Integration with Judge

### Phase 4: Coordination (Week 4)
- [ ] Write lazy.md spec
- [ ] Implement main `JGent` coordinator
- [ ] Test-driven reality (test generation)
- [ ] End-to-end integration tests

### Phase 5: Polish & Integration (Week 5)
- [ ] Write integration.md (memoization)
- [ ] Update bootstrap.md, anatomy.md, functors.md
- [ ] Performance optimization
- [ ] Documentation

---

## Part 6: Success Criteria

### Spec Quality
- [ ] J-gents derivable from bootstrap agents (no new irreducibles)
- [ ] All seven principles satisfied
- [ ] Tensions resolved via synthesis (documented)

### Implementation Quality
- [ ] mypy --strict passes
- [ ] Test coverage > 80%
- [ ] Integrates with existing evolve pipeline
- [ ] Can JIT-compile at least one useful agent type

### Integration Quality
- [ ] Works with existing H-gents dialectic
- [ ] Respects K-gent personalization
- [ ] Composes with C-gents patterns

---

## Appendix: Concept Cross-Reference

| JAIgent Term | kgents Equivalent | Notes |
|--------------|-------------------|-------|
| AutoPoieticNode | JGent | Main coordinator |
| Ground Truth | Ground (⊥) | Exact match |
| Wave Function Collapse | Fix (μ) | Similar iteration |
| Thesis/Antithesis/Synthesis | Contradict/Sublate | Exact match |
| DialecticFrame | Tension + Synthesis | Similar structure |
| Meta-Architect | JIT MetaArchitect | Same concept |
| Chaosmonger | stability.py + Chaosmonger | Extended |
| Entropy Budget | depth-based budget | Novel formalization |
| Promise Tree | Lazy Promise structure | Novel |
| Test-Driven Reality | Accountability tests | Novel |
| Merkle DAG | Optional memoization | Future enhancement |
| Compute Markets | Not implemented | Future enhancement |
