# Failure as Evidence: The Self-Improving Compiler

> *"Every failed generation is a lesson. Every lesson is a prior. Every prior shapes the next generation."*

**Date**: 2025-12-21
**Status**: Brainstorming
**Related**: `spec/protocols/agentic-self-hosting-compiler.md`, `plans/ashc-master.md`

---

## The Core Insight

**Failed generations are not waste. They are evidence.**

Current ASHC flow:
```
Spec → Generate N variations → Verify each → Select best → Output
                                    ↓
                              Failures discarded
```

Proposed flow:
```
Spec → Generate N variations → Verify each → Select best → Output
                                    ↓
                              Failures → Evidence Corpus
                                    ↓
                              Causal Learning
                                    ↓
                              Refined Prior for NEXT generation
```

The difference: **closed-loop learning**. The compiler gets smarter over time.

---

## Why This Matters

### 1. Failures Contain Signal

A failed generation tells us something:
- Which spec phrasings lead to bugs
- Which code patterns fail mypy
- Which architectural choices cause test failures
- Which nudges make things worse

This is **negative evidence**—just as valuable as positive evidence.

```python
# Current: Discard failure
if not run.passed:
    continue  # Waste!

# Proposed: Learn from failure
if not run.passed:
    learner.observe_failure(run)
    causal_graph.add_edge(
        nudge=run.nudges,
        outcome_delta=-run.verification_score,  # Negative!
        context=run.error_messages,
    )
```

### 2. The Causal Graph Becomes a Prior

After 1000 generations across many specs, the causal graph knows:

| Nudge Pattern | Effect | Confidence |
|---------------|--------|------------|
| "Add type hints" | +25% pass rate | 0.92 |
| "Use global state" | -35% pass rate | 0.87 |
| "Add error handling" | +15% pass rate | 0.78 |
| "Remove docstrings" | -8% pass rate | 0.65 |

This becomes a **learned prior** for new generations:
- Before generating, consult the causal graph
- Weight prompts toward patterns that historically work
- Avoid patterns that historically fail

```python
async def generate_with_prior(spec: str) -> str:
    # Consult accumulated evidence
    beneficial_nudges = causal_graph.beneficial_edges[:5]
    harmful_nudges = causal_graph.harmful_edges[:5]

    prompt = f"""
    Generate implementation for: {spec}

    HISTORICALLY HELPFUL (apply these):
    {[n.nudge.reason for n in beneficial_nudges]}

    HISTORICALLY HARMFUL (avoid these):
    {[n.nudge.reason for n in harmful_nudges]}
    """
    return await llm.generate(prompt)
```

### 3. Health Data for Project and Developer

The evidence corpus is a diagnostic tool:

**For the Project:**
- Which specs are fragile (high failure rate)?
- Which code areas have unstable tests?
- Where is the technical debt (many retries needed)?

**For the Developer (Kent):**
- Which of my intuitions are confirmed by data?
- Which spec patterns lead to clean implementations?
- Am I getting better over time? (meta-meta-learning)

```python
@dataclass
class ProjectHealth:
    """Diagnostic derived from evidence corpus."""

    total_generations: int
    success_rate_trend: list[float]  # Over time
    fragile_specs: list[str]         # Low pass rate
    robust_specs: list[str]          # High pass rate
    learned_insights: list[CausalEdge]  # Top lessons

    def diagnose(self) -> str:
        if self.success_rate_trend[-1] > self.success_rate_trend[0]:
            return "IMPROVING: Compiler learning from failures"
        else:
            return "DEGRADING: Check recent spec changes"
```

---

## The Recursive Loop

This creates a beautiful recursive structure:

```
Generation 1:  Spec → Impl₁ (FAIL) → Evidence₁
Generation 2:  Spec + Evidence₁ → Impl₂ (FAIL) → Evidence₂
Generation 3:  Spec + Evidence₁₂ → Impl₃ (PASS) → Evidence₃
...
Generation N:  Spec + Evidence₁..ₙ₋₁ → Implₙ (PASS, faster)
```

Each generation benefits from ALL previous generations.

**This is why capturing data early is critical.** The sooner we start accumulating evidence, the richer the prior becomes.

---

## Implementation Sketch

### Phase 1: Evidence Persistence

Currently evidence lives in memory. Persist it:

```python
class EvidenceStore:
    """Persistent evidence corpus across sessions."""

    async def save_run(self, run: Run) -> None:
        """Save run to persistent store (SQLite/Postgres)."""

    async def load_for_spec(self, spec_hash: str) -> Evidence:
        """Load all runs for a spec."""

    async def load_causal_graph(self) -> CausalGraph:
        """Load accumulated causal knowledge."""

    async def get_health(self) -> ProjectHealth:
        """Compute project health from all evidence."""
```

### Phase 2: Prior Injection

Use accumulated evidence in generation:

```python
class PriorAwareCompiler(EvidenceCompiler):
    """Compiler that uses accumulated evidence as prior."""

    def __init__(self, evidence_store: EvidenceStore):
        self.store = evidence_store

    async def compile(self, spec: str) -> ASHCOutput:
        # Load prior from persistent evidence
        graph = await self.store.load_causal_graph()

        # Extract lessons
        do_this = graph.beneficial_edges[:5]
        avoid_this = graph.harmful_edges[:5]

        # Inject into generation
        enriched_spec = self._enrich_spec(spec, do_this, avoid_this)

        # Generate with prior
        output = await super().compile(enriched_spec)

        # Save ALL runs (pass and fail) for future
        for run in output.evidence.runs:
            await self.store.save_run(run)

        return output
```

### Phase 3: Active Learning

Don't just passively accumulate—actively explore:

```python
class ActiveLearningCompiler(PriorAwareCompiler):
    """Compiler that strategically explores to learn faster."""

    async def compile(self, spec: str) -> ASHCOutput:
        # Identify uncertain regions in causal graph
        uncertain_nudges = self.graph.uncertain_edges()

        # Generate some variations that TEST these uncertainties
        exploration_specs = [
            self._apply_nudge(spec, nudge)
            for nudge in uncertain_nudges[:3]
        ]

        # Run explorations to reduce uncertainty
        for exp_spec in exploration_specs:
            result = await self._quick_verify(exp_spec)
            self.graph = self.graph.with_observation(result)

        # Now generate with refined prior
        return await super().compile(spec)
```

---

## The Deeper Pattern: Stigmergy

This is **stigmergic learning**—agents leaving traces that guide future agents.

```
Ant 1: Fails path A → Leaves "avoid" pheromone
Ant 2: Sees pheromone → Takes path B → Succeeds → Leaves "prefer" pheromone
Ant 3: Sees both pheromones → Takes B confidently
```

ASHC equivalent:
```
Gen 1: Fails with global state → Leaves CausalEdge(global_state, -0.35)
Gen 2: Sees edge → Avoids global state → Succeeds → Leaves CausalEdge(DI, +0.20)
Gen 3: Sees both → Uses DI confidently → Succeeds faster
```

The evidence corpus is a **shared memory** that transcends individual generations.

---

## What to Capture (Expanded)

Current capture:
- Test pass/fail counts
- Type errors
- Lint violations

Proposed expanded capture:

| Category | Data | Why |
|----------|------|-----|
| **Structural** | AST diff between spec and impl | Learn spec→impl patterns |
| **Temporal** | Time to generate, time to verify | Identify slow paths |
| **Semantic** | Error messages, stack traces | Learn failure modes |
| **Contextual** | Surrounding code, imports used | Learn context patterns |
| **Human** | Kent's nudges and their effects | Learn Kent's intuition |
| **Environmental** | Model used, temperature, tokens | Optimize generation params |

```python
@dataclass
class RichRun(Run):
    """Extended run with full diagnostic capture."""

    # Existing
    test_results: TestReport
    type_results: TypeReport
    lint_results: LintReport

    # New: Structural
    ast_diff: ASTDiff | None = None
    import_graph: dict[str, list[str]] = field(default_factory=dict)

    # New: Temporal
    generation_time_ms: float = 0.0
    verification_time_ms: float = 0.0

    # New: Semantic
    error_messages: tuple[str, ...] = ()
    stack_traces: tuple[str, ...] = ()

    # New: Contextual
    context_hash: str = ""  # Hash of surrounding code

    # New: Environmental
    model_used: str = ""
    temperature: float = 0.0
    tokens_used: int = 0
```

---

## The Vision: Self-Improving Codebase

Imagine:

1. **Day 1**: ASHC generates code with 60% pass rate
2. **Week 1**: After 100 generations, pass rate is 75%
3. **Month 1**: After 1000 generations, pass rate is 90%
4. **Year 1**: ASHC rarely fails; it has learned your codebase

The codebase becomes **self-documenting through evidence**:
- No need to write "best practices" docs
- The causal graph IS the best practices
- New developers can query: "What works in this codebase?"

```bash
# Future CLI
ashc insights --spec "authentication"
# → "Historical success: use JWT (87%), avoid session cookies (62%)"
# → "Top nudges: add rate limiting (+23%), add logging (+15%)"
# → "Avoid: global auth state (-31%), sync I/O (-22%)"
```

---

## Next Steps

1. **Persist Evidence**: Add `EvidenceStore` with SQLite backend
2. **Capture Failures**: Ensure failed runs are saved, not discarded
3. **Build Prior Injection**: Use accumulated graph in generation prompts
4. **Add Health Dashboard**: Visualize project health from evidence
5. **Experiment**: Run same spec 100 times, measure improvement

---

## The Meta-Insight

> *"The compiler is not a tool. It is a learning system."*

Traditional compilers are static: same input → same output.

ASHC is dynamic: same input → better output over time.

This is not just a compiler. It is a **co-evolving partner** that learns your codebase, your patterns, your intuitions—and gets better at being you.

*"Daring, bold, creative, opinionated but not gaudy."*

---

## Related Ideas

- **M-gent Crystals**: Evidence corpus could be stored as crystals in the memory system
- **Stigmergy Protocol**: Formalize the pheromone-like trace-leaving pattern
- **Bootstrap Regeneration**: Use failure evidence to improve bootstrap specs
- **Economic Accountability**: Failed generations cost credibility; successful ones earn it

---

*"Every failure is a teacher. Every teacher is a prior. Every prior shapes the future."*
