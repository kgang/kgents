# Psi-gent Walkthrough: The Morphic Engine

A guided tour through the Ψ-gent implementation for Kent and collaborators.

---

## Overview

**Location**: `impl/claude/agents/psi/`
**Tests**: 104 passing
**Core Insight**: Metaphor selection is a contextual bandit problem.

The Morphic Engine transforms hard problems into easier ones by finding the right metaphor. It implements reasoning-by-analogy as a six-stage geometric transformation pipeline.

---

## Architecture

```
RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY
    ↑          ↑                              ↓
    └──────────┴──────────── LEARN ←─────────┘
```

### File Map (~1,500 lines)

| File | Lines | Purpose |
|------|-------|---------|
| `types.py` | ~385 | Core types + validation + serialization |
| `corpus.py` | ~455 | 6 standard metaphors + corpus management |
| `engine.py` | ~745 | Six-stage pipeline + backtracking |
| `learning.py` | ~330 | Thompson sampling + abstraction learning |
| `integrations.py` | ~560 | L/B/D/N/G-gent adapters |
| `__init__.py` | ~100 | Public API exports |

---

## Session 1: Types & Design Philosophy

**File**: `types.py`
**Duration**: ~30 min
**Tests**: `test_types.py` (30 tests)

### Key Concepts

1. **Problem** (lines 25-52)
   - Frozen dataclass (immutable)
   - `complexity` property: heuristic [0.0, 1.0]
   - `with_embedding()`: functional update pattern

2. **Metaphor** (lines 75-103)
   - Contains `Operation` tuples with preconditions/effects
   - `tractability` property: power for reasoning
   - Standard pattern: `with_embedding()` for immutable updates

3. **Projection** (lines 120-138)
   - Problem mapped into metaphor terms
   - `abstraction`: 0.0 (concrete) to 1.0 (abstract)
   - `coverage` property: mappings / (mappings + gaps)

4. **Distortion** (lines 180-206)
   - Three-axis quality metric:
     - `structural_loss`: unmapped concepts
     - `round_trip_error`: Phi^-1(Phi(P)) vs P
     - `prediction_failures`: implications that didn't hold
   - `acceptable` property: threshold check (< 0.5)

### Discussion Points

- Why frozen dataclasses everywhere?
- The `with_*` pattern for immutable updates
- Validation functions as invariant checkers
- Why three distortion axes?

### Try It

```python
from agents.psi import Problem, Distortion

p = Problem(id="test", description="API is slow", domain="software")
print(f"Complexity: {p.complexity}")

d = Distortion(0.2, 0.3, 1)
print(f"Total: {d.total}, Acceptable: {d.acceptable}")
```

---

## Session 2: The Standard Corpus

**File**: `corpus.py`
**Duration**: ~30 min
**Tests**: `test_corpus.py` (20 tests)

### The Six Metaphors

| Metaphor | Domain | Core Operations |
|----------|--------|-----------------|
| Plumbing | engineering | locate_constriction, widen_pipe, add_reservoir, add_bypass, seal_leak |
| Ecosystem | biology | identify_niche, strengthen_symbiosis, remove_invasive, increase_biodiversity |
| Traffic | transportation | identify_bottleneck, add_lane, install_signal, reroute_traffic |
| Medicine | healthcare | diagnose, treat, monitor, vaccinate |
| Architecture | construction | assess_foundation, identify_load_bearing, renovate, add_support |
| Gardening | horticulture | plant, prune, weed, fertilize |

### Design Principles

1. **Each operation has**:
   - Name (verb phrase)
   - Description (what it does)
   - Signature (input → output)
   - Preconditions (when applicable)
   - Effects (what changes)

2. **Each metaphor has**:
   - Concrete examples showing real application
   - At least 4 operations (tractability)
   - Cross-domain applicability

### MetaphorCorpus Class

- `static`: Built-in metaphors (immutable)
- `dynamic`: Runtime-added metaphors
- `add()`: Validates before adding
- `remove()`: Only for dynamic metaphors

### Discussion Points

- Why these six domains?
- What makes a "good" metaphor?
- When would you add a dynamic metaphor?
- How do examples help reasoning?

### Try It

```python
from agents.psi import STANDARD_CORPUS, create_standard_corpus

corpus = create_standard_corpus()
plumbing = corpus.get("plumbing")
print(f"Operations: {[op.name for op in plumbing.operations]}")
```

---

## Session 3: The Morphic Engine

**File**: `engine.py`
**Duration**: ~45 min
**Tests**: `test_engine.py` (33 tests)

### The Six Stages

#### Stage 1: RETRIEVE (lines 88-115)
- Find candidate metaphors for the problem
- Uses learning model if trained, else cold-start
- Returns `list[tuple[Metaphor, float]]` (scored)

#### Stage 2: PROJECT (lines 120-330)
- Map problem concepts → metaphor concepts
- `abstraction` parameter controls mapping leniency
- Produces `Projection` with mappings + gaps + confidence

#### Stage 3: CHALLENGE (lines 335-421)
- Stress-test the projection
- Four checks: coverage, confidence, applicable operations, critical gaps
- Must pass 3/4 to survive

#### Stage 4: SOLVE (lines 425-509)
- Reason within metaphor space
- Apply up to 3 operations
- Build reasoning chain
- Synthesize conclusion

#### Stage 5: TRANSLATE (lines 515-552)
- Map solution back to problem terms
- Reverse the concept mappings
- Extract actionable recommendations

#### Stage 6: VERIFY (lines 558-595)
- Measure solution quality via distortion
- Check constraints are addressed
- Return `(Distortion, bool)`

### The Search Loop (lines 601-743)

```python
while state.iteration < max_iterations:
    candidates = retrieve(exclude=tried)
    projection = project(candidates[0])
    if not challenge(projection).survives:
        backtrack → continue
    solution = solve(projection)
    translated = translate(solution)
    distortion = verify(solution)
    if verified:
        record_feedback → return solution
    else:
        decide_recovery → continue
```

### Discussion Points

- Why backtrack on challenge failure?
- The abstraction dial: concrete vs abstract
- How does `_decide_recovery` choose what to do?
- Stage callbacks for observability

### Try It

```python
from agents.psi import MetaphorEngine, Problem

engine = MetaphorEngine()
problem = Problem(
    id="perf-001",
    description="The API is slow. Users are complaining.",
    domain="software",
    constraints=("Must improve within sprint",)
)

solution = engine.solve_problem(problem)
print(f"Success: {solution.success}")
print(f"Answer: {solution.translated_answer}")
for action in solution.specific_actions:
    print(f"  - {action}")
```

---

## Session 4: The Learning System

**File**: `learning.py`
**Duration**: ~30 min
**Tests**: `test_learning.py` (21 tests)

### Core Insight

> "Metaphor selection is a contextual bandit problem"

Given features of a problem, which metaphor will yield the best solution?

### Thompson Sampling Model (lines 160-227)

- Beta distribution per (domain, metaphor_id) pair
- `alpha`: successes + prior
- `beta`: failures + prior
- `sample()`: random draw from posterior
- `decay()`: forget old data gradually

### Key Functions

1. **outcome_to_reward** (lines 22-40)
   - SUCCESS → 1.0 + distortion bonus
   - PARTIAL → 0.3
   - CHALLENGE_FAILED → -0.3
   - PROJECTION_FAILED → -0.5

2. **extract_features** (lines 48-67)
   - Domain clustering
   - Complexity bucket
   - Embedding cluster (if available)

3. **retrieve_with_learning** (lines 282-306)
   - Thompson: sample from posterior (exploration)
   - UCB: mean + 2*std (confidence bound)
   - Greedy: expected reward (exploitation)

### Abstraction Model (lines 235-274)

- Learns optimal abstraction level per problem type
- Records successful abstractions
- Suggests median of successful history

### Discussion Points

- Why Thompson sampling over UCB?
- The explore/exploit tradeoff
- Cold start problem: what happens with no data?
- How decay enables adaptation to changing patterns

### Try It

```python
from agents.psi.learning import ThompsonSamplingModel
from agents.psi.types import ProblemFeatures, Feedback, Outcome

model = ThompsonSamplingModel()
features = ProblemFeatures(
    domain="software",
    domain_cluster=50,
    complexity=0.5,
    constraint_count=2,
    description_length=100,
    has_embedding=False,
)

# Before training
print(f"Before: {model.predict(features, 'plumbing')}")

# Train on successes
for _ in range(10):
    model.update(Feedback(
        problem_id="1",
        problem_features=features,
        metaphor_id="plumbing",
        abstraction=0.5,
        outcome=Outcome.SUCCESS,
    ))

print(f"After: {model.predict(features, 'plumbing')}")
```

---

## Session 5: Integrations

**File**: `integrations.py`
**Duration**: ~30 min

### L-gent (Embeddings)

- `LEmbedder` protocol: `embed()`, `embed_batch()`
- `embed_problem()`, `embed_metaphor()`, `embed_corpus()`
- `cosine_similarity()` for retrieval
- `retrieve_by_embedding()`: semantic search

### B-gent (Token Economics)

- `BudgetManager` protocol: `authorize()`, `record_cost()`
- `PsiBudget`: per-stage token budgets
- `solve_with_budget()`: budget-controlled solving
- `TokenReceipt`: tracks actual usage

### D-gent (Persistence)

- `DataAgent` protocol: `get()`, `set()`
- `serialize_model()`, `deserialize_model()`
- `PersistentEngine`: auto-saves learning state

### N-gent (Tracing)

- `Historian` protocol: `begin_trace()`, `end_trace()`, `abort_trace()`
- `PsiTrace`: complete solve attempt history
- `solve_with_tracing()`: full observability

### G-gent (Prompts)

- `GrammarEngine` protocol: `render()`, `parse()`
- `PSI_TEMPLATES`: prompt templates for each stage
- `project_with_grammar()`: structured prompt generation

### Graceful Degradation

```python
class ResilientEngine:
    """Falls back gracefully when integrations unavailable."""

    def solve_problem(self, problem):
        # Try L-gent embedding
        if self.deps.l_gent:
            try:
                problem = embed_problem(problem, self.deps.l_gent)
            except:
                pass  # Continue without

        # Try N-gent tracing
        if self.deps.n_gent:
            try:
                return solve_with_tracing(problem, self.engine, self.deps.n_gent)
            except:
                pass  # Fall back

        # Basic solve
        return self.engine.solve_problem(problem)
```

### Discussion Points

- Protocol-based dependency injection
- Why graceful degradation matters
- Which integrations would you prioritize?
- The `GentDependencies` container pattern

---

## Session 6: Testing & Laws

**Files**: `_tests/*.py`
**Duration**: ~20 min

### Test Structure

| File | Tests | Coverage |
|------|-------|----------|
| `test_types.py` | 30 | Type invariants, validation |
| `test_corpus.py` | 20 | Metaphor structure, corpus CRUD |
| `test_engine.py` | 33 | All 6 stages + backtracking |
| `test_learning.py` | 21 | Models, retrieval, laws |

### Law Tests (marked with `@pytest.mark.law`)

1. **Distortion invariants**: components bounded [0,1]
2. **Projection invariants**: abstraction/confidence bounded
3. **solve_always_returns_solution**: never returns None
4. **backtrack_excludes_tried**: no repeated metaphors
5. **thompson_sampling_explores**: samples vary
6. **success_increases_probability**: learning works

### Running Tests

```bash
# All Psi-gent tests
python -m pytest impl/claude/agents/psi/_tests/ -v

# Just law tests
python -m pytest impl/claude/agents/psi/_tests/ -m law -v

# With coverage
python -m pytest impl/claude/agents/psi/_tests/ --cov=impl/claude/agents/psi
```

---

## Next Steps

### Potential Enhancements

1. **E-gent Integration** (Ψ×E)
   - Metaphors as evolvable entities
   - Mutation for metaphor refinement
   - Natural selection of effective metaphors

2. **Real LLM Integration**
   - Replace `_default_llm_call` with actual LLM
   - Structured outputs for PROJECT stage
   - Chain-of-thought for SOLVE stage

3. **Embedding-First Retrieval**
   - Pre-embed entire corpus
   - Semantic similarity for cold start
   - Hybrid: embedding + learning

4. **Multi-Metaphor Composition**
   - Apply multiple metaphors to same problem
   - Synthesize insights across frameworks
   - Track which combinations work

### Questions for Kent

1. Which integration is highest priority?
2. Should metaphors be user-extensible at runtime?
3. How should we handle LLM failures in production?
4. What's the desired persistence strategy?

---

## Quick Reference

### Creating a Problem

```python
Problem(
    id="unique-id",
    description="What's wrong",
    domain="software|organization|...",
    constraints=("must X", "cannot Y"),
    context={"key": "value"},
    embedding=None,  # L-gent adds this
)
```

### Using the Engine

```python
engine = MetaphorEngine(config=EngineConfig(
    max_candidates=5,
    max_iterations=10,
    distortion_threshold=0.5,
    enable_learning=True,
))

solution = engine.solve_problem(problem)
```

### Checking Solution Quality

```python
if solution.success:  # distortion.acceptable
    print(solution.translated_answer)
    for action in solution.specific_actions:
        print(f"  - {action}")
else:
    print(f"Distortion too high: {solution.distortion.total}")
```
