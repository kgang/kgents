# Ψ-gent Implementation

> **The Morphic Engine**: Reasoning by analogy as geometric transformation.

**Status**: COMPLETE (104 tests passing)
**Location**: `impl/claude/agents/psi/`

---

## Design Philosophy

The current Ψ-gent implementation focuses on **metaphor as computation, not decoration**. It prioritizes measurable outcomes over aspirational frameworks.

### Core Principles

| Principle | Implementation |
|-----------|----------------|
| Morphic transformation | Φ → Σ → Φ⁻¹ (project → solve → translate) |
| Backtracking search | Problems need exploration, not pipelines |
| Integration points | D/N/L/B/G-gent connections |
| Measurable distortion | 3-dimensional quality metric |
| Learning | Thompson sampling for metaphor selection |

### Design Choices

| Choice | Rationale |
|--------|-----------|
| Continuous abstraction (0.0-1.0) | More nuanced than discrete levels |
| CHALLENGE stage | Adversarial testing before committing |
| 3 distortion metrics | Computable: structural_loss, round_trip_error, prediction_failures |
| Data-driven retrieval | Learning replaces static heuristics |

---

## Architecture

### Phase 1: Core Types (`types.py`)

**Goal**: Define the minimal, measurable type system.

**New Types** (from spec/psi-gents/types.md):
```python
Problem            # Input with id, description, domain, constraints, context, embedding
Metaphor           # Framework with operations, examples, embedding
Operation          # Executable action with preconditions/effects
Example            # Concrete instance grounding the metaphor
ConceptMapping     # source → target with confidence
Projection         # Problem mapped into metaphor space
ChallengeResult    # Adversarial test outcome
MetaphorSolution   # Reasoning chain in metaphor space
Solution           # Final output with distortion
Distortion         # Three-dimensional quality metric
SearchState        # Mutable state for backtracking
EngineConfig       # Configuration
Feedback           # Learning signal
Outcome            # Enum for learning
```

**Key Design Decisions**:
- All types are `@dataclass(frozen=True)` for immutability
- Computed properties (complexity, coverage, tractability) instead of stored values
- `tuple` instead of `list` for immutable sequences
- Optional `embedding` fields for L-gent integration

**Lines**: ~200

---

### Phase 2: Six-Stage Engine (`engine.py`)

**Goal**: Implement the core RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY pipeline with backtracking.

**Architecture**:
```
MetaphorEngine
├── retrieve(problem, limit, exclude, context) → [(Metaphor, score)]
├── project(problem, metaphor, abstraction) → Projection
├── challenge(projection) → ChallengeResult
├── solve(projection) → MetaphorSolution
├── translate(metaphor_solution, problem) → (answer, actions, confidence)
├── verify(solution, problem) → (Distortion, bool)
└── solve_problem(problem) → Solution  # Main entry point with search loop
```

**The Search Loop**:
```python
def solve_problem(self, problem: Problem) -> Solution:
    state = SearchState(problem)

    while state.iteration < config.max_iterations:
        # RETRIEVE
        candidates = self.retrieve(problem, exclude=state.tried_ids)
        if not candidates:
            return self._best_or_fail(state)

        metaphor = candidates[0][0]

        # PROJECT
        abstraction = self._suggest_abstraction(problem, state)
        projection = self.project(problem, metaphor, abstraction)

        # CHALLENGE
        challenge_result = self.challenge(projection)
        if not challenge_result.survives:
            state.record_backtrack("challenge", challenge_result.counterexamples)
            continue

        # SOLVE
        metaphor_solution = self.solve(projection)

        # TRANSLATE
        translated, actions, confidence = self.translate(metaphor_solution, problem)

        # Build Solution
        solution = Solution(
            problem=problem,
            metaphor_solution=metaphor_solution,
            translated_answer=translated,
            specific_actions=actions,
            distortion=Distortion(0, 0, 0),  # Placeholder
            trace_id=None
        )

        # VERIFY
        distortion, verified = self.verify(solution, problem)
        solution = solution._replace(distortion=distortion)

        if verified:
            self._record_success(state, solution)
            return solution

        state.record_backtrack("verify", self._decide_recovery(distortion))

    return self._best_or_fail(state)
```

**Lines**: ~500

---

### Phase 3: Metaphor Corpus (`corpus.py`)

**Goal**: Manage static + dynamic metaphor collection.

**Components**:
```python
MetaphorCorpus
├── static: list[Metaphor]      # Built-in metaphors
├── dynamic: list[Metaphor]     # Learned/generated
├── embeddings: dict[str, tuple]
├── add(metaphor, source)
├── get(id) → Metaphor
├── __iter__ → Iterator[Metaphor]
└── validate_metaphor(metaphor) → (bool, list[str])

STANDARD_CORPUS: list[Metaphor]  # Plumbing, Ecosystem, Traffic, etc.
```

**Standard Metaphors** (5-7 to start):
1. **Plumbing**: Flow, constriction, reservoir, pressure
2. **Ecosystem**: Organisms, niches, symbiosis, invasive species
3. **Traffic**: Routes, congestion, signals, capacity
4. **Medicine**: Diagnosis, symptoms, treatment, side effects
5. **Architecture**: Foundations, load-bearing, renovation
6. **Chess**: Positions, openings, sacrifices, endgame
7. **Gardening**: Growth, pruning, soil, seasons

Each metaphor needs 3-5 operations with preconditions/effects.

**Lines**: ~300

---

### Phase 4: Learning System (`learning.py`)

**Goal**: Thompson sampling for metaphor selection.

**Components**:
```python
ProblemFeatures
├── domain, domain_cluster
├── complexity, constraint_count
├── description_length
├── embedding_cluster

Feedback
├── problem_id, problem_features
├── metaphor_id, abstraction
├── outcome, distortion

RetrievalModel (Protocol)
├── predict(features, metaphor_id) → float
├── predict_with_uncertainty() → (mean, std)
├── update(feedback)
├── is_trained → bool

ThompsonSamplingModel  # Primary implementation
FrequencyModel         # Simple fallback
AbstractionModel       # Learns optimal abstraction
```

**Key Insight**: This is a contextual bandit problem. Thompson sampling naturally balances exploration (try new metaphors) and exploitation (use proven ones).

**Lines**: ~250

---

### Phase 5: Integration Adapters (`integrations.py`)

**Goal**: Clean integration with L/B/D/N/G-gents.

**Components**:
```python
GentDependencies
├── l_gent: LEmbedder | None
├── b_gent: BudgetManager | None
├── d_gent: DataAgent | None
├── n_gent: Historian | None
├── g_gent: GrammarEngine | None

IntegrationConfig
├── embedding model/cache settings
├── budget strategy/limits
├── persistence backend
├── trace level/retention

# Adapter functions
embed_problem(problem, l_gent) → Problem
embed_metaphor(metaphor, l_gent) → Metaphor
solve_with_budget(problem, engine, b_gent) → (Solution, Receipt)
solve_with_tracing(problem, engine, n_gent) → (Solution, Trace)
project_with_grammar(problem, metaphor, g_gent) → Projection
```

**Graceful Degradation**: Engine works without any integrations; integrations enhance but don't require.

**Lines**: ~200

---

### Phase 6: MCP Tool (`__init__.py` + MCP updates)

**Goal**: Wire to existing `kgents_psi` MCP tool.

The MCP server at `impl/claude/protocols/cli/mcp/server.py` already has a `kgents_psi` tool. We need to wire it to the new engine.

**Lines**: ~50

---

## File Structure

```
impl/claude/agents/psi/
├── __init__.py          # Exports
├── types.py             # Core types (~250 lines)
├── engine.py            # Six-stage engine (~500 lines)
├── corpus.py            # Metaphor corpus (~300 lines)
├── learning.py          # Thompson sampling (~250 lines)
├── integrations.py      # L/B/D/N/G adapters (~200 lines)
└── _tests/
    ├── test_types.py    # 30 tests
    ├── test_engine.py   # 33 tests
    ├── test_corpus.py   # 20 tests
    └── test_learning.py # 21 tests
```

**Total**: ~1500 lines, 104 tests

---

## Test Strategy

### Unit Tests

1. **types.py**: Property computation, serialization, invariants
2. **engine.py**: Each stage independently, then full pipeline
3. **corpus.py**: Add/get/validate metaphors
4. **learning.py**: Model updates, prediction, exploration

### Integration Tests

1. **L-gent**: Embedding retrieval
2. **B-gent**: Budget metering
3. **D-gent**: State persistence
4. **N-gent**: Tracing

### End-to-End Tests

1. **Simple problem**: "API is slow" with Plumbing
2. **Complex problem**: Multi-constraint organizational issue
3. **Backtrack scenario**: First metaphor fails CHALLENGE
4. **Learning scenario**: Same problem type improves over time

### Law Tests

```python
@pytest.mark.law
def test_distortion_is_bounded():
    """Distortion components must be in [0, 1]."""

@pytest.mark.law
def test_solve_returns_valid_solution():
    """solve_problem always returns a Solution or raises."""

@pytest.mark.law
def test_backtrack_makes_progress():
    """Each backtrack excludes at least one metaphor."""
```

---

## Usage

```python
from agents.psi import MetaphorEngine, Problem

# Define a problem
problem = Problem(
    id="perf-001",
    description="The API is slow. Users are complaining.",
    domain="software",
    constraints=("Must improve within sprint",)
)

# Create engine and solve
engine = MetaphorEngine()
solution = engine.solve_problem(problem)

# Check result
if solution.distortion.acceptable:
    print(f"Solution: {solution.translated_answer}")
    for action in solution.specific_actions:
        print(f"  - {action}")
```

---

*The soul of Ψ-gent is **metaphor as computation**—finding the space where hard problems become easy.*
