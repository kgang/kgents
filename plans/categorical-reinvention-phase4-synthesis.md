# Phase 4: Synthesis

> *"Ship it."*

**Timeline**: 3 weeks
**Prerequisite**: Phase 3 SBM working (>95% retention at 100 tokens)
**Core Deliverable**: kgents 2.0

---

## The Goal

Integrate everything into a coherent system. Phases 1-3 built components. Phase 4 makes them a product.

- Phase 1: Probes that measure law satisfaction
- Phase 2: CPRM that scores reasoning steps (middle-invariant, variator-invariant)
- Phase 3: SBM that retains bindings (perturbation-invariant)
- **Phase 4: kgents that uses all three**

---

## Deliverable 1: CategoricalAgent (5 days)

The new base agent. Replaces PolyAgent for reasoning-critical paths.

**USES MIDDLE-INVARIANCE FOR ROBUSTNESS**.

```python
class CategoricalAgent(PolyAgent[S, A, B]):
    """
    Agent with categorical guarantees.

    Features:
    - Sharp Binding Module for variable tracking (perturbation-invariant)
    - CPRM scoring for step verification (variator-invariant)
    - Sheaf coherence checking for consistency

    Usage: Drop-in replacement for PolyAgent in reasoning tasks.
    """

    def __init__(
        self,
        initial_state: S,
        sbm: SharpBindingModule,
        cprm: CPRM,
        coherence: SheafDetector
    ):
        super().__init__(initial_state)
        self.sbm = sbm
        self.cprm = cprm
        self.coherence = coherence
        self.claims: list[str] = []

    async def step(self, input: A) -> B:
        """
        One reasoning step with full categorical verification.
        ROBUST TO MIDDLE-PERTURBATIONS AND MONAD VARIATORS.
        """
        # 1. Run the step
        output = await self._execute(input)

        # 2. Score it (CPRM is variator-invariant)
        score = self.cprm.score_step(str(input) + " → " + str(output), 0)
        if score < 0.3:
            raise LowConfidenceStep(f"CPRM score {score:.2f} below threshold")

        # 3. Check coherence
        new_claims = await self.coherence.extract_claims(str(output))
        violations = []
        for new in new_claims:
            for old in self.claims:
                if await self.coherence.contradicts(new[0], old[0]):
                    violations.append((new[0], old[0]))

        if violations:
            raise CoherenceViolation(violations)

        # 4. Update state
        self.claims.extend(new_claims)
        return output

    def bind(self, var: str, val: Any) -> int:
        """
        Explicit binding. Trackable. Inspectable.
        PERTURBATION-INVARIANT: bindings survive middle-perturbations.
        """
        return self.sbm.bind(self._embed(var), self._embed(str(val)))

    def lookup(self, var: str) -> Any:
        """
        Retrieve a bound value.
        VARIATOR-INVARIANT: lookup doesn't care about language/whitespace.
        """
        return self._decode(self.sbm.lookup(self._embed(var)))

    def dump_bindings(self) -> dict:
        """Show current binding state. For debugging and explanation."""
        return self.sbm.dump()

    def dump_claims(self) -> list[str]:
        """Show accumulated claims. For debugging and explanation."""
        return self.claims
```

---

## Deliverable 2: Categorical Reasoning Pipeline (5 days)

End-to-end pipeline: problem → CPRM-guided search with SBM → verified answer.

**Research Protocol Applied**:

```python
class CategoricalPipeline:
    """
    The complete reasoning system.

    1. Take problem
    2. Run CPRM-guided search with SBM
    3. Verify coherence
    4. Return answer with confidence

    DEVELOPED WITH PHASED PROTOCOL.

    Phase A: Toy problem (3 + 5)
    Phase B: Single trail with full logging
    Phase C: n=3 problems across difficulty
    Phase D: Full benchmark (GSM8K)
    """

    def __init__(
        self,
        llm: LLM,
        cprm: CPRM,
        sbm: SharpBindingModule,
        coherence: SheafDetector
    ):
        self.llm = llm
        self.cprm = cprm
        self.sbm = sbm
        self.coherence = coherence

    async def solve(self, problem: str) -> SolveResult:
        """
        Solve a problem with categorical guarantees.
        ROBUST TO VARIATORS AND PERTURBATIONS.
        """
        # Reset SBM for new problem
        self.sbm.occupied.data.zero_()

        # CPRM-guided search
        trace = ""
        for step in range(10):
            # Generate candidates
            candidates = await self.llm.generate_n(
                f"{problem}\n{trace}\nNext step:",
                n=5
            )

            # Score each (CPRM is variator-invariant)
            scored = [
                (self.cprm.score_step(trace + c, step), c)
                for c in candidates
            ]
            scored.sort(reverse=True)

            # Take best above threshold
            best_score, best_step = scored[0]
            if best_score < 0.3:
                break  # All candidates bad, stop

            trace += "\n" + best_step

            # Check for answer
            if "answer" in best_step.lower() or "therefore" in best_step.lower():
                break

        # Coherence check on final trace
        coherence_result = await self.coherence.detect(trace)

        # Extract answer
        answer = self._extract_answer(trace)

        return SolveResult(
            answer=answer,
            trace=trace,
            confidence=best_score,
            is_coherent=coherence_result.is_coherent,
            bindings=self.sbm.dump(),
            violations=coherence_result.violations
        )


async def validate_pipeline_phased():
    """Phased validation of CategoricalPipeline."""

    pipeline = CategoricalPipeline(...)

    # Phase A: Toy problem
    toy_result = await pipeline.solve("What is 3 + 5?")
    assert "8" in toy_result.answer, "Toy must work"
    assert toy_result.is_coherent, "Toy should be coherent"

    # Phase B: Single trail with full logging
    trail_result = await pipeline.solve("Let x = 7. What is x + 2?")
    print(f"Trail trace:\n{trail_result.trace}")
    print(f"Bindings: {trail_result.bindings}")
    assert "9" in trail_result.answer

    # Phase C: Proof run (n=3 diverse problems)
    proof_problems = [
        ("Simple arithmetic", "What is 10 - 3?", "7"),
        ("Variable binding", "If y = 4, what is 2*y?", "8"),
        ("Multi-step", "x = 5, y = x + 3, what is y?", "8")
    ]
    for name, problem, expected in proof_problems:
        result = await pipeline.solve(problem)
        assert expected in result.answer, f"{name} should work"
        assert result.is_coherent, f"{name} should be coherent"

    # Phase D: Scale to GSM8K
    # Start: 10 problems, verify all work
    # Then: 50 problems, check accuracy
    # Then: 500 problems, check for drift
    # Finally: Full GSM8K benchmark
    gsm8k_sample = sample_gsm8k(n=10)
    for problem in gsm8k_sample:
        result = await pipeline.solve(problem['question'])
        # Track accuracy, coherence, binding stats
```

---

## Deliverable 3: Integration with kgents (5 days)

Wire everything into the existing infrastructure.

```python
# agents/__init__.py
from .poly_agent import PolyAgent
from .categorical_agent import CategoricalAgent  # NEW

# services/categorical/__init__.py
from .pipeline import CategoricalPipeline
from .cprm import CPRM
from .sbm import SharpBindingModule
from .coherence import SheafDetector

# protocols/agentese/nodes/categorical.py
@node("concept.reasoning.solve")
class CategoricalSolveNode(Node):
    """
    Solve a problem using the categorical pipeline.

    Usage: await logos.invoke("concept.reasoning.solve", umwelt, problem=...)
    """

    def __init__(self, pipeline: CategoricalPipeline):
        self.pipeline = pipeline

    async def execute(self, observer: Umwelt, **kwargs) -> SolveResult:
        problem = kwargs.get("problem")
        return await self.pipeline.solve(problem)

@node("self.binding.state")
class BindingStateNode(Node):
    """
    Inspect current bindings.

    Usage: await logos.invoke("self.binding.state", umwelt)
    """

    def __init__(self, agent: CategoricalAgent):
        self.agent = agent

    async def execute(self, observer: Umwelt, **kwargs) -> dict:
        return self.agent.dump_bindings()
```

**Provider Registration**:

```python
# services/providers.py

def get_categorical_pipeline() -> CategoricalPipeline:
    return CategoricalPipeline(
        llm=get_llm(),
        cprm=CPRM.from_pretrained("kgents/cprm-v1"),
        sbm=SharpBindingModule(num_slots=16, dim=768),
        coherence=SheafDetector()
    )

# Container registration
container.register("categorical_pipeline", get_categorical_pipeline, singleton=True)
container.register("categorical_agent", get_categorical_agent, singleton=False)
```

---

## Deliverable 4: The Demo (3 days)

One demo that shows the value. A problem that baseline fails, categorical solves.

**DEMONSTRATES VARIATOR-INVARIANCE AND PERTURBATION-INVARIANCE**.

```python
# examples/categorical_demo.py

"""
Demo: Multi-variable reasoning over long context with perturbations.

Baseline struggles. Categorical nails it.
"""

PROBLEM = """
Let x = 7.
Let y = 13.
Let z = x + y.

The weather is nice today. The sun is shining. Birds are singing.
Many people are outside enjoying the day. Some are walking their dogs.
Others are sitting in cafes reading newspapers. The economy is improving.
Technology advances continue at a rapid pace. Climate change remains a concern.
Politicians debate various issues. Scientists make new discoveries daily.

What is z * 2?
"""

# Perturbation variants: shuffle middle, paraphrase middle, group middle
PROBLEM_SHUFFLED = """
Let x = 7.
Let y = 13.
Let z = x + y.

Scientists make new discoveries daily. The weather is nice today.
Technology advances continue at a rapid pace. Birds are singing.
Politicians debate various issues. Some are walking their dogs.
Climate change remains a concern. Many people are outside enjoying the day.
The economy is improving. The sun is shining.
Others are sitting in cafes reading newspapers.

What is z * 2?
"""

PROBLEM_PARAPHRASED = """
Let x = 7.
Let y = 13.
Let z = x + y.

Today's weather is pleasant. Sunshine fills the sky. Avian creatures vocalize.
Numerous individuals enjoy outdoor activities. Canine companions accompany some.
Coffee shop patrons peruse publications. Economic indicators show growth.
Technological progress accelerates. Environmental concerns persist.
Political discourse continues. Research yields novel findings.

What is z * 2?
"""

# Language variator: different phrasing for bindings
PROBLEM_LANGUAGE_VARIANT = """
Set x to 7.
Set y to 13.
Set z to x plus y.

The weather is nice today. The sun is shining. Birds are singing.
Many people are outside enjoying the day. Some are walking their dogs.
Others are sitting in cafes reading newspapers. The economy is improving.
Technology advances continue at a rapid pace. Climate change remains a concern.
Politicians debate various issues. Scientists make new discoveries daily.

What is z times 2?
"""

async def demo():
    print("=" * 60)
    print("CATEGORICAL REASONING DEMO")
    print("Hypothesis: CategoricalAgent is invariant to:")
    print("  1. Middle-perturbations (shuffle, paraphrase)")
    print("  2. Monad variators (language, whitespace)")
    print("=" * 60)

    # Baseline
    print("\n[BASELINE]")
    baseline = await standard_llm.solve(PROBLEM)
    print(f"Answer: {baseline}")  # Often wrong: 40, 26, or hallucinated

    # Categorical: original
    print("\n[CATEGORICAL - Original]")
    pipeline = CategoricalPipeline(...)
    result1 = await pipeline.solve(PROBLEM)
    print(f"Answer: {result1.answer}")  # 40 (correct)
    print(f"Bindings: {result1.bindings}")  # {'x': 7, 'y': 13, 'z': 20}
    print(f"Coherent: {result1.is_coherent}")  # True

    # Categorical: shuffled middle
    print("\n[CATEGORICAL - Shuffled Middle]")
    result2 = await pipeline.solve(PROBLEM_SHUFFLED)
    print(f"Answer: {result2.answer}")  # Still 40
    print(f"Bindings: {result2.bindings}")  # Still {'x': 7, 'y': 13, 'z': 20}
    assert result2.answer == result1.answer, "Middle-shuffle should not affect answer"

    # Categorical: paraphrased middle
    print("\n[CATEGORICAL - Paraphrased Middle]")
    result3 = await pipeline.solve(PROBLEM_PARAPHRASED)
    print(f"Answer: {result3.answer}")  # Still 40
    assert result3.answer == result1.answer, "Middle-paraphrase should not affect answer"

    # Categorical: language variator
    print("\n[CATEGORICAL - Language Variator]")
    result4 = await pipeline.solve(PROBLEM_LANGUAGE_VARIANT)
    print(f"Answer: {result4.answer}")  # Still 40
    assert result4.answer == result1.answer, "Language variator should not affect answer"

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("CategoricalAgent is:")
    print("  - Middle-invariant (shuffle/paraphrase don't matter)")
    print("  - Variator-invariant (language/whitespace don't matter)")
    print("  - Binding-stable (tracks x, y, z across 200+ tokens)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demo())
```

---

## Success Propositions

| Proposition | Test | Consequence if False |
|-------------|------|---------------------|
| CategoricalAgent is drop-in compatible with PolyAgent | Existing tests pass | API needs work |
| CategoricalPipeline improves accuracy on GSM8K by >5% | Benchmark comparison | Integration broken |
| Demo problem solved correctly across all variants | Manual test | Back to debugging |
| All AGENTESE paths working | Integration tests | Node registration issue |
| Middle-perturbations don't degrade performance | Perturbation test suite | Middle-invariance hypothesis rejected |
| Monad variators don't degrade performance | Variator test suite | Variator-invariance hypothesis rejected |

### ValidationEngine Integration

Phase 4 validates the complete system and tracks release readiness:

```yaml
# initiatives/categorical-phase4.yaml
id: categorical_phase4
name: "Phase 4: Synthesis"
description: "Ship kgents 2.0 with categorical guarantees"
witness_tags: ["categorical", "phase4", "synthesis", "release"]

phases:
  - id: agent_compatibility
    name: "Agent Compatibility"
    description: "CategoricalAgent drop-in replacement"
    propositions:
      - id: polyagent_tests_pass
        description: "All PolyAgent tests pass with CategoricalAgent"
        metric: binary
        threshold: 1
        direction: "="
        required: true
      - id: agentese_paths_working
        description: "All AGENTESE paths registered and functional"
        metric: binary
        threshold: 1
        direction: "="
        required: true
    gate:
      condition: all_required

  - id: invariance_validation
    name: "Invariance Validation"
    description: "Verify middle-invariance and variator-invariance"
    depends_on: [agent_compatibility]
    propositions:
      - id: middle_perturbation_robustness
        description: "Performance stable under middle-perturbations"
        metric: percent
        threshold: 95  # <5% degradation
        direction: ">"
        required: true
      - id: variator_robustness
        description: "Performance stable under monad variators"
        metric: percent
        threshold: 95  # <5% degradation
        direction: ">"
        required: true
    gate:
      condition: all_required

  - id: benchmark_improvement
    name: "Benchmark Improvement"
    description: "Categorical pipeline outperforms baseline"
    depends_on: [invariance_validation]
    propositions:
      - id: gsm8k_accuracy_gain
        description: "GSM8K accuracy improves >5%"
        metric: percent
        threshold: 5
        direction: ">"
        required: true
    gate:
      condition: all_required

  - id: release_gate
    name: "Release Gate"
    description: "Final ship/no-ship decision"
    depends_on: [benchmark_improvement]
    propositions:
      - id: demo_passes
        description: "Demo problem solved correctly across all variants"
        metric: binary
        threshold: 1
        direction: "="
        required: true
      - id: no_critical_blockers
        description: "No critical bugs or regressions"
        metric: binary
        threshold: 1
        direction: "="
        required: true
    gate:
      condition: all_required
```

```python
# Complete validation pipeline for kgents 2.0 release
from services.validation import get_validation_engine
from datetime import timedelta

engine = get_validation_engine()

async def validate_release_readiness():
    """
    Full release validation with caching.
    USES PHASED PROTOCOL.
    """

    # Phase A: Toy validation
    toy_results = run_toy_validation()
    assert all(toy_results.values()), "All toy tests must pass"

    # Phase B: Trail validation (full logging)
    trail_results = run_trail_validation()
    print(f"Trail logged: {len(trail_results['steps'])} steps")

    # Phase C: Proof run (n=3 diverse problems)
    proof_results = run_proof_validation(n=3)
    assert all(r['passed'] for r in proof_results)

    # Phase D: Full validation
    # Phase 1: Agent compatibility (fast, run always)
    compat_handle = await engine.validate_cached(
        "categorical_phase4",
        {
            "polyagent_tests_pass": 1.0 if all_tests_pass else 0.0,
            "agentese_paths_working": 1.0 if paths_registered else 0.0,
        },
        phase_id="agent_compatibility",
    )

    if not compat_handle.data.passed:
        return "❌ Compatibility gate failed"

    # Phase 2: Invariance validation
    invariance_handle = await engine.validate_cached(
        "categorical_phase4",
        {
            "middle_perturbation_robustness": perturbation_performance_percent,
            "variator_robustness": variator_performance_percent,
        },
        phase_id="invariance_validation",
        ttl=timedelta(hours=2),
    )

    if not invariance_handle.data.passed:
        return "❌ Invariance gate failed"

    # Phase 3: Benchmark (expensive, cache aggressively)
    benchmark_handle = await engine.validate_cached(
        "categorical_phase4",
        {"gsm8k_accuracy_gain": accuracy_improvement_percent},
        phase_id="benchmark_improvement",
        ttl=timedelta(hours=4),  # Benchmarks expensive
    )

    if not benchmark_handle.data.passed:
        return "❌ Benchmark gate failed"

    # Phase 4: Release gate
    release_handle = await engine.validate_cached(
        "categorical_phase4",
        {
            "demo_passes": 1.0 if demo_correct else 0.0,
            "no_critical_blockers": 1.0 if not critical_bugs else 0.0,
        },
        phase_id="release_gate",
    )

    if release_handle.data.passed:
        return "✅ kgents 2.0 READY TO SHIP"
    else:
        blockers = engine.get_blockers()
        return f"❌ Release blocked: {blockers}"


# Track full initiative progress
status = engine.get_status("categorical_phase4")
print(f"""
kgents 2.0 Release Status
========================
Progress: {status.progress_percent:.0f}%
Current Phase: {status.current_phase_id}
Completed: {', '.join(str(p) for p in status.phases_complete) or 'None'}
Blockers: {len(status.blockers)}
""")
```

---

## Research Protocol Summary

**Every deliverable follows the four-phase protocol**:

1. **Phase A**: Toy example (3+5, single variant) — debug and validate
2. **Phase B**: Single trail (full logging, all variants)
3. **Phase C**: Proof run (n=3 diverse problems, all variants)
4. **Phase D**: Scale to full benchmark (GSM8K)

**NO MORE "run on 1000 problems immediately"** — that's Phase D after A/B/C validate.

---

## What We Cut

- ~~Elaborate benchmark suite~~ — Demo + GSM8K comparison. Ship.
- ~~Novel reasoning strategies~~ — Future work. Get the basics out.
- ~~Multiple model sizes~~ — One size (base) works. Scaling is later.
- ~~Perfect documentation~~ — Good enough docs. Iterate.

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-2 | Phase A: Toy validation |
| 3-4 | Phase B: Trail validation |
| 5 | Phase C: Proof run (n=3) |
| 6-10 | Phase D: Full CategoricalAgent + Pipeline |
| 11-15 | AGENTESE integration |
| 16-18 | Demo with all variants |
| 19-21 | Documentation and release |

---

## The Transformation

**kgents 1.0**:
- PolyAgent for state machines
- Operad for composition grammar
- Sheaf concepts in documentation
- Standard LLM backend

**kgents 2.0**:
- CategoricalAgent with SBM and coherence checking
- CPRM for step verification (middle-invariant, variator-invariant)
- SBM for binding retention (perturbation-invariant)
- Sheaf checking live in the pipeline
- Neural-symbolic binding that actually works

**Key Innovation**: Robustness to irrelevant variation (middle-perturbations, monad variators).

---

## What Ships

1. **`CategoricalAgent`** — New agent class with categorical guarantees
2. **`CategoricalPipeline`** — End-to-end reasoning with verification
3. **`SharpBindingModule`** — Discrete binding for variable tracking (perturbation-invariant)
4. **`CPRM`** — Trained model for step scoring (variator-invariant)
5. **AGENTESE paths** — `concept.reasoning.solve`, `self.binding.state`
6. **Demo** — Proof that it works across all variants

---

## Post-Launch

After Phase 4 ships:

1. **Iterate on CPRM** — More training data, better heads
2. **Scale SBM** — More slots, hierarchical organization
3. **Add CCL** — Coherence Checker Layers from Phase 3 cut list
4. **Novel strategies** — Syntax reasoning, typed composition

But first: ship.

---

*Phase 4 is 3 weeks. At the end, kgents 2.0 is real. Category theory is no longer just the lens—it's the architecture. Middle-perturbations don't matter. Monad variators don't matter. Reasoning is robust.*

---

## The Full Arc

| Phase | Duration | Core Outcome | Key Invariances | ValidationEngine Initiative |
|-------|----------|--------------|-----------------|----------------------------|
| 1 | 3 weeks | Validated: Laws predict correctness | N/A | `categorical_phase1` (flat) |
| 2 | 4 weeks | Operational: CPRM guides search | Variator-invariant | `categorical_phase2` (3 phases) |
| 3 | 5 weeks | Architectural: SBM solves binding | Perturbation-invariant | `categorical_phase3` (3 phases) |
| 4 | 3 weeks | Shipped: kgents 2.0 | Middle-invariant | `categorical_phase4` (4 phases) |

**Total: 15 weeks**

From theory to product in under 4 months. Each phase has a clear deliverable and clear success criteria. Fail fast or ship fast.

### Validation Infrastructure

Every phase uses the same validation primitives:

```python
# All phases share this workflow
from services.validation import get_validation_engine
from datetime import timedelta

engine = get_validation_engine()

# 1. Register initiatives (once, at startup)
engine.load_initiatives_from_dir(Path("initiatives/categorical/"))

# 2. Run validation with caching (expensive benchmarks)
handle = await engine.validate_cached(
    "categorical_phase1",
    measurements=study_results,
    ttl=timedelta(minutes=30),
)

# 3. Check gate status
if handle.data.passed:
    proceed_to_next_phase()
else:
    blockers = engine.get_blockers()
    fix_blockers(blockers)

# 4. Track overall progress (AGENTESE path)
await logos.invoke("concept.validation.status", umwelt, initiative="categorical_phase2")
```

**Key Integration Points**:
- `SourceType.VALIDATION_RUN` — Cached validation results
- `ProxyHandle[ValidationRun]` — Explicit computation, no auto-refresh
- Witness marks — Every proposition check emits marks
- `source_hash` — Changed measurements invalidate cache

---

## The Invariances (Summary)

**What kgents 2.0 doesn't care about**:

1. **Middle-perturbations** — Shuffle, paraphrase, or group middle steps? CPRM scores the same.
2. **Monad variators** — "Let x = 5" vs "Set x to 5"? CPRM scores the same.
3. **Binding distance** — 10 tokens or 200 tokens? SBM retains bindings equally.
4. **Whitespace/formatting** — Different indentation? No effect on scores or bindings.
5. **Step reordering** — Commutative steps in different order? Still coherent.

**What kgents 2.0 cares about**:

1. **Categorical law satisfaction** — Monad identity, sheaf coherence
2. **Correctness** — Does the trace lead to the right answer?
3. **Claim coherence** — Are claims consistent across the reasoning trace?

---

*"Daring, bold, creative, opinionated but not gaudy."*

This is kgents 2.0. Robust reasoning through categorical invariance.
