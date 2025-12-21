# Integration with Other Gents

> Ψ-gent doesn't work alone.

---

## Overview

The Morphic Engine integrates with several other gent types:

| Gent | Integration | Purpose |
|------|-------------|---------|
| L-gent | Embeddings | Semantic retrieval |
| B-gent | Token budgets | Cost control |
| D-gent | State persistence | Learning memory |
| N-gent | Tracing | Forensics |
| G-gent | Prompt structure | LLM calls |

---

## L-gent: Semantic Embeddings

L-gent provides the embedding infrastructure for semantic retrieval.

### Embedding Problems

```python
def embed_problem(problem: Problem, l_gent: LEmbedder) -> Problem:
    """Add embedding to problem using L-gent."""
    if problem.embedding:
        return problem

    embedding = l_gent.embed(problem.description)
    return Problem(
        id=problem.id,
        description=problem.description,
        domain=problem.domain,
        constraints=problem.constraints,
        context=problem.context,
        embedding=tuple(embedding)
    )
```

### Embedding Metaphors

```python
def embed_metaphor(metaphor: Metaphor, l_gent: LEmbedder) -> Metaphor:
    """Add embedding to metaphor using L-gent."""
    if metaphor.embedding:
        return metaphor

    # Embed the description plus operation names
    text = f"{metaphor.description} Operations: {[op.name for op in metaphor.operations]}"
    embedding = l_gent.embed(text)

    return Metaphor(
        id=metaphor.id,
        name=metaphor.name,
        domain=metaphor.domain,
        description=metaphor.description,
        operations=metaphor.operations,
        examples=metaphor.examples,
        embedding=tuple(embedding)
    )
```

### Batch Embedding

```python
def embed_corpus(corpus: list[Metaphor], l_gent: LEmbedder) -> list[Metaphor]:
    """Batch embed entire corpus."""
    texts = [
        f"{m.description} Operations: {[op.name for op in m.operations]}"
        for m in corpus
    ]
    embeddings = l_gent.embed_batch(texts)

    return [
        Metaphor(
            id=m.id, name=m.name, domain=m.domain,
            description=m.description, operations=m.operations,
            examples=m.examples, embedding=tuple(e)
        )
        for m, e in zip(corpus, embeddings)
    ]
```

---

## B-gent: Token Economics

B-gent controls token budgets and cost tracking.

### Budget Allocation

```python
@dataclass
class PsiBudget:
    """Token budget for a solve attempt."""

    retrieve_budget: int = 500    # Tokens for retrieval
    project_budget: int = 1000    # Tokens for projection
    challenge_budget: int = 800   # Tokens for challenge
    solve_budget: int = 2000      # Tokens for solving (most expensive)
    translate_budget: int = 800   # Tokens for translation
    verify_budget: int = 600      # Tokens for verification

    total_budget: int = 6000

    @property
    def remaining(self) -> int:
        return self.total_budget - (
            self.retrieve_budget + self.project_budget +
            self.challenge_budget + self.solve_budget +
            self.translate_budget + self.verify_budget
        )
```

### Metered Execution

```python
def solve_with_budget(
    problem: Problem,
    engine: MetaphorEngine,
    b_gent: BudgetManager
) -> tuple[Solution | None, TokenReceipt]:
    """Execute solve with B-gent budget control."""

    receipt = TokenReceipt()

    # Authorize budget
    authorization = b_gent.authorize(
        operation="psi_solve",
        estimated_tokens=6000
    )

    if not authorization.approved:
        return None, receipt

    try:
        # Run with metering
        with b_gent.meter(authorization) as meter:
            solution = engine.solve(problem)
            receipt = meter.get_receipt()

        return solution, receipt

    except BudgetExhausted:
        # Partial result handling
        return engine.get_partial_result(), receipt
```

### Cost Tracking

```python
def track_stage_costs(engine: MetaphorEngine, b_gent: BudgetManager) -> None:
    """Track token costs per stage for optimization."""

    stage_costs = engine.get_stage_costs()

    for stage, cost in stage_costs.items():
        b_gent.record_cost(
            category=f"psi_{stage}",
            tokens=cost,
            metadata={"problem_id": engine.current_problem_id}
        )
```

---

## D-gent: State Persistence

D-gent provides durable storage for learning and metaphor corpus.

### Learning State Persistence

```python
class PersistentEngine:
    """MetaphorEngine with D-gent persistence."""

    def __init__(self, d_gent: DataAgent):
        self.d_gent = d_gent
        self.engine = MetaphorEngine()
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted state."""
        # Learning model
        learning_state = self.d_gent.get("psi/learning_model")
        if learning_state:
            self.engine.retrieval_model = deserialize(learning_state)

        # Abstraction model
        abstraction_state = self.d_gent.get("psi/abstraction_model")
        if abstraction_state:
            self.engine.abstraction_model = deserialize(abstraction_state)

        # Dynamic corpus additions
        dynamic_metaphors = self.d_gent.get("psi/dynamic_corpus")
        if dynamic_metaphors:
            for m in dynamic_metaphors:
                self.engine.corpus.add(deserialize_metaphor(m))

    def _save_state(self) -> None:
        """Save state to D-gent."""
        self.d_gent.set("psi/learning_model", serialize(self.engine.retrieval_model))
        self.d_gent.set("psi/abstraction_model", serialize(self.engine.abstraction_model))

    def solve(self, problem: Problem) -> Solution:
        """Solve with automatic state persistence."""
        solution = self.engine.solve(problem)
        self._save_state()
        return solution
```

### Transactional Updates

```python
async def update_with_transaction(
    d_gent: TransactionalDataAgent,
    feedback: Feedback
) -> None:
    """Update learning state transactionally."""

    async with d_gent.transaction() as txn:
        # Load current state
        state = await txn.get("psi/learning_model")
        model = deserialize(state)

        # Update
        model.update(feedback)

        # Save
        await txn.set("psi/learning_model", serialize(model))

        # Commit (or rollback on error)
```

---

## N-gent: Tracing and Forensics

N-gent provides the tracing infrastructure for debugging and analysis.

### Trace Structure

```python
@dataclass
class PsiTrace:
    """Complete trace of a solve attempt."""

    trace_id: str
    problem_id: str
    timestamp: datetime

    # Stage traces
    retrieve_trace: RetrieveTrace | None = None
    project_trace: ProjectTrace | None = None
    challenge_trace: ChallengeTrace | None = None
    solve_trace: SolveTrace | None = None
    translate_trace: TranslateTrace | None = None
    verify_trace: VerifyTrace | None = None

    # Outcome
    outcome: Outcome | None = None
    distortion: Distortion | None = None

    # Backtracks
    backtracks: list[BacktrackEvent] = field(default_factory=list)
```

### Recording Traces

```python
def solve_with_tracing(
    problem: Problem,
    engine: MetaphorEngine,
    n_gent: Historian
) -> tuple[Solution, PsiTrace]:
    """Solve with full N-gent tracing."""

    trace = PsiTrace(
        trace_id=str(uuid4()),
        problem_id=problem.id,
        timestamp=datetime.now()
    )

    ctx = n_gent.begin_trace(
        action="psi_solve",
        input_obj={"problem_id": problem.id}
    )

    try:
        # Each stage records its own trace
        solution = engine.solve(
            problem,
            trace_callback=lambda stage, data: record_stage(trace, stage, data)
        )

        trace.outcome = Outcome.SUCCESS if solution.distortion.acceptable else Outcome.VERIFY_FAILED
        trace.distortion = solution.distortion

        n_gent.end_trace(ctx, outputs={"trace_id": trace.trace_id})
        return solution, trace

    except Exception as e:
        n_gent.abort_trace(ctx, error=str(e))
        raise
```

### Forensic Analysis

```python
def analyze_failure(trace: PsiTrace, n_gent: Historian) -> str:
    """Analyze why a solve attempt failed."""

    bard = n_gent.forensic_bard

    # Build narrative
    narrative = f"Solve attempt for problem {trace.problem_id}\n\n"

    if trace.challenge_trace and not trace.challenge_trace.survives:
        narrative += f"CHALLENGE FAILED: {trace.challenge_trace.counterexamples}\n"
        narrative += bard.explain_failure("challenge", trace.challenge_trace)

    if trace.verify_trace and trace.distortion:
        narrative += f"DISTORTION: {trace.distortion.total:.2f}\n"
        if trace.distortion.prediction_failures > 0:
            narrative += bard.explain_failure("prediction", trace.verify_trace)

    return narrative
```

---

## G-gent: Structured Prompts

G-gent provides validated prompt templates and response parsing.

### Prompt Templates

```python
# G-gent template definitions for Ψ-gent stages

PSI_TEMPLATES = {
    "project": """
    <problem>{problem_description}</problem>
    <metaphor name="{metaphor_name}">{metaphor_description}</metaphor>
    <abstraction level="{abstraction}" />

    Map the problem concepts to metaphor concepts.
    <output>
      <mappings>
        <mapping source="..." target="..." confidence="0.X" />
      </mappings>
      <gaps>...</gaps>
    </output>
    """,

    "challenge_inversion": """
    <projection>{mapped_description}</projection>
    <question type="inversion">
      What if the opposite were true? Would the metaphor still apply?
    </question>
    <output>
      <survives>yes|no</survives>
      <reason>...</reason>
    </output>
    """,

    "solve": """
    <state>{current_state}</state>
    <metaphor>{metaphor_name}</metaphor>
    <operations>{available_operations}</operations>

    Apply the most relevant operation. Show reasoning.
    <output>
      <operation>{operation_name}</operation>
      <reasoning>...</reasoning>
      <new_state>...</new_state>
    </output>
    """,
}
```

### Using G-gent

```python
def project_with_grammar(
    problem: Problem,
    metaphor: Metaphor,
    abstraction: float,
    g_gent: GrammarEngine
) -> Projection:
    """Project using G-gent structured prompts."""

    # Render template
    prompt = g_gent.render(
        "psi_project",
        problem_description=problem.description,
        metaphor_name=metaphor.name,
        metaphor_description=metaphor.description,
        abstraction=abstraction
    )

    # Call LLM
    response = llm_call(prompt)

    # Parse with G-gent validation
    parsed = g_gent.parse("psi_project_output", response)

    return Projection(
        problem=problem,
        metaphor=metaphor,
        mappings=tuple(ConceptMapping(**m) for m in parsed["mappings"]),
        abstraction=abstraction,
        gaps=tuple(parsed["gaps"]),
        confidence=parsed.get("overall_confidence", 0.5)
    )
```

---

## Integration Configuration

```python
@dataclass
class IntegrationConfig:
    """Configuration for gent integrations."""

    # L-gent
    l_gent_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_size: int = 10000

    # B-gent
    default_budget: int = 6000
    budget_strategy: str = "metered"  # or "fixed" or "unlimited"

    # D-gent
    persistence_backend: str = "sqlite"  # or "redis" or "postgres"
    state_path: str = "./psi_state"

    # N-gent
    trace_level: str = "full"  # or "summary" or "none"
    trace_retention_days: int = 30

    # G-gent
    grammar_validation: bool = True
    strict_parsing: bool = False

```

---

## Dependency Injection

```python
@dataclass
class GentDependencies:
    """Injected gent dependencies for MetaphorEngine."""

    l_gent: LEmbedder | None = None
    b_gent: BudgetManager | None = None
    d_gent: DataAgent | None = None
    n_gent: Historian | None = None
    g_gent: GrammarEngine | None = None
    e_gent: EvolutionEngine | None = None

def create_engine(deps: GentDependencies, config: IntegrationConfig) -> MetaphorEngine:
    """Create MetaphorEngine with dependencies."""

    engine = MetaphorEngine(config=config)

    if deps.l_gent:
        engine.embedder = deps.l_gent

    if deps.b_gent:
        engine.budget_manager = deps.b_gent

    if deps.d_gent:
        engine.persistence = deps.d_gent

    if deps.n_gent:
        engine.historian = deps.n_gent

    if deps.g_gent:
        engine.grammar = deps.g_gent

    if deps.e_gent:
        engine.evolution = deps.e_gent

    return engine
```

---

## Graceful Degradation

The engine should work even when integrations are unavailable:

```python
class ResilientEngine:
    """MetaphorEngine that degrades gracefully."""

    def retrieve(self, problem: Problem) -> list[tuple[Metaphor, float]]:
        # Try L-gent embeddings first
        if self.l_gent:
            try:
                return self._retrieve_by_embedding(problem)
            except LGentUnavailable:
                pass

        # Fall back to keyword matching
        return self._retrieve_by_keywords(problem)

    def solve(self, problem: Problem) -> Solution:
        # Try full pipeline with tracing
        if self.n_gent:
            try:
                return self._solve_with_tracing(problem)
            except NGentUnavailable:
                pass

        # Solve without tracing
        return self._solve_basic(problem)
```

---

*Integration makes the engine powerful. Independence makes it reliable.*
