# Phase 1: Foundations

> *"Measure first. Build only what measurement validates."*

**Timeline**: 3 weeks
**Core Question**: Do categorical laws predict reasoning correctness?

---

## The Bet

LLM reasoning failures are not random. They follow patterns that category theory predicts:
- **Monad law violations** → CoT breaks down
- **Sheaf incoherence** → Hallucinations

Phase 1 builds the instruments to detect these patterns. If the correlation holds (r > 0.3), we have a new paradigm. If not, we've learned something important in 3 weeks, not 12 months.

---

## Deliverable 1: Monad Law Probe (3 days)

The monad laws say: trivial modifications shouldn't change answers, and grouping shouldn't matter.

```python
class MonadProbe:
    """
    Two tests. That's it.
    """

    async def identity_test(self, llm: LLM, problem: str, n: int = 50) -> float:
        """
        Add "Let me think step by step." prefix.
        Measure: How often does this CHANGE the answer?

        If identity holds: Change rate ≈ 0
        If identity fails: Change rate > 0
        """
        base = [await llm.solve(problem) for _ in range(n)]
        prefixed = [await llm.solve("Let me think step by step. " + problem) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        prefixed_mode = Counter(prefixed).most_common(1)[0][0]

        return 1.0 if base_mode == prefixed_mode else 0.0

    async def associativity_test(self, llm: LLM, problem: str, steps: list[str]) -> float:
        """
        Run the same reasoning with different step groupings.
        Measure: How often do groupings produce different answers?

        If associativity holds: Different groupings → same answer
        If associativity fails: Different groupings → different answers
        """
        # Group as ((step1, step2), step3)
        left = await llm.reason_grouped(problem, [[steps[0], steps[1]], [steps[2]]])
        # Group as (step1, (step2, step3))
        right = await llm.reason_grouped(problem, [[steps[0]], [steps[1], steps[2]]])

        return 1.0 if left == right else 0.0
```

**Output**: A score from 0-1 for each problem. Higher = better law satisfaction.

---

## Deliverable 2: Sheaf Coherence Detector (5 days)

Hallucinations are claims that contradict each other. The sheaf condition says: local claims must agree on overlaps.

```python
class SheafDetector:
    """
    Extract claims. Check pairwise consistency. Done.
    """

    async def detect(self, trace: str) -> CoherenceResult:
        # Step 1: Extract factual claims using structured prompting
        claims = await self.extract_claims(trace)
        # Returns: [("X is 5", context), ("Y > X", context), ...]

        # Step 2: Check each pair for contradiction
        violations = []
        for i, (claim_a, ctx_a) in enumerate(claims):
            for j, (claim_b, ctx_b) in enumerate(claims[i+1:], i+1):
                if await self.contradicts(claim_a, claim_b):
                    violations.append((i, j, claim_a, claim_b))

        return CoherenceResult(
            is_coherent=len(violations) == 0,
            violations=violations,
            score=1.0 - (len(violations) / max(len(claims), 1))
        )

    async def extract_claims(self, trace: str) -> list[tuple[str, str]]:
        """
        Prompt: "List all factual claims made in this reasoning trace.
        Format: CLAIM: [claim] | CONTEXT: [what it refers to]"
        """
        response = await self.llm.generate(EXTRACTION_PROMPT.format(trace=trace))
        return self.parse_claims(response)

    async def contradicts(self, claim_a: str, claim_b: str) -> bool:
        """
        Prompt: "Do these two claims contradict each other? YES or NO."
        """
        response = await self.llm.generate(
            f"Claim A: {claim_a}\nClaim B: {claim_b}\n\nDo these contradict? YES or NO:"
        )
        return "YES" in response.upper()
```

**Output**: Coherence score from 0-1. Lower = more contradictions = more likely hallucination.

---

## Deliverable 3: The Correlation Study (5 days)

This is the gate. Everything depends on this.

```python
async def run_correlation_study():
    """
    1000 problems. 10 traces each. Measure everything. Compute correlations.
    """
    results = []

    for problem in GSM8K[:500] + HOTPOTQA[:500]:
        for _ in range(10):
            trace = await llm.generate_cot(problem.question)
            answer = extract_answer(trace)

            results.append({
                'problem_id': problem.id,
                'trace': trace,
                'correct': problem.check(answer),
                'monad_identity': await monad_probe.identity_test(llm, problem.question),
                'monad_assoc': await monad_probe.associativity_test(llm, problem.question, parse_steps(trace)),
                'sheaf_coherence': (await sheaf_detector.detect(trace)).score
            })

    df = pd.DataFrame(results)

    return {
        'monad_identity_corr': df['monad_identity'].corr(df['correct']),
        'monad_assoc_corr': df['monad_assoc'].corr(df['correct']),
        'sheaf_corr': df['sheaf_coherence'].corr(df['correct']),
        'combined_auc': train_classifier(df).auc
    }
```

---

## Success Propositions

| Proposition | Threshold | Consequence if False |
|-------------|-----------|---------------------|
| Monad identity correlates with accuracy | r > 0.3 | Drop monad from framework |
| Sheaf coherence correlates with correctness | r > 0.4 | Drop sheaf from framework |
| Combined metrics predict accuracy | AUC > 0.7 | Categorical approach fails, pivot |

**If all propositions hold**: Phase 2 proceeds.
**If combined AUC < 0.6**: Stop. The theory doesn't apply to LLMs.

### ValidationEngine Integration

These propositions are tracked via the Validation Framework (`services/validation/`):

```yaml
# initiatives/categorical-phase1.yaml
id: categorical_phase1
name: "Phase 1: Foundations"
description: "Validate categorical laws predict reasoning correctness"
witness_tags: ["categorical", "phase1", "foundations"]

propositions:
  - id: monad_identity_correlation
    description: "Monad identity law correlates with accuracy"
    metric: pearson_r
    threshold: 0.3
    direction: ">"
    required: true

  - id: sheaf_coherence_correlation
    description: "Sheaf coherence correlates with correctness"
    metric: pearson_r
    threshold: 0.4
    direction: ">"
    required: true

  - id: combined_auc
    description: "Combined categorical metrics predict accuracy"
    metric: auc
    threshold: 0.7
    direction: ">"
    required: true

gate:
  id: phase1_gate
  name: "Phase 1 Completion Gate"
  condition: all_required
```

```python
# Running validation with caching (AD-015)
from services.validation import get_validation_engine

engine = get_validation_engine()

# Run correlation study, cache results (5 min TTL)
handle = await engine.validate_cached(
    "categorical_phase1",
    measurements={
        "monad_identity_correlation": study_results['monad_identity_corr'],
        "sheaf_coherence_correlation": study_results['sheaf_corr'],
        "combined_auc": study_results['combined_auc'],
    },
    ttl=timedelta(minutes=30),  # Cache expensive correlation study
)

if handle.data.passed:
    print("✅ Phase 1 passed - proceed to Phase 2")
else:
    blockers = engine.get_blockers()
    print(f"❌ Blocked by: {[b.proposition.id for b in blockers]}")
```

---

## What We Cut

- ~~Operad law checking~~ — Too complex for Phase 1. Monad + Sheaf are sufficient.
- ~~Syntax reasoning AST~~ — Moved to Phase 2. Measurement comes first.
- ~~Elaborate claim extraction~~ — LLM-based extraction is good enough.
- ~~Multiple benchmarks~~ — GSM8K + HotpotQA cover math and multi-hop. Enough.

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-3 | Monad probe implemented and tested |
| 4-8 | Sheaf detector implemented and tested |
| 9-15 | Correlation study running |
| 16-18 | Analysis and decision |

---

## Integration

```python
# New paths in AGENTESE
"concept.laws.monad_identity" → MonadIdentityNode
"concept.laws.sheaf_coherence" → SheafCoherenceNode

# New witness metadata
@dataclass
class Mark:
    # ... existing fields ...
    monad_score: float | None = None
    sheaf_score: float | None = None
```

---

*Phase 1 is 3 weeks. At the end, we know if categorical machine reasoning is real or a beautiful fiction. Either answer is valuable.*
