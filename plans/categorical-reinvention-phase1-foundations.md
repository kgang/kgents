# Phase 1: Foundations

> *"Measure first. Build only what measurement validates."*

**Timeline**: 3 weeks
**Core Question**: Do categorical laws predict reasoning correctness?

---

## The Bet

LLM reasoning failures are not random. They follow patterns that category theory predicts:
- **Middle-invariance violations** → Prompt brittleness
- **Monad law violations** → CoT breaks down
- **Sheaf incoherence** → Hallucinations

Phase 1 builds the instruments to detect these patterns. If the correlation holds (r > 0.3), we have a new paradigm. If not, we've learned something important in 3 weeks, not 12 months.

---

## NEW HYPOTHESIS: Middle-Invariance

**Conjecture**: A prompt with perturbations to the *middle* is approximately equal to its behavior without them.

**Reasoning**: Consider the limit where a prompt shrinks—the beginning and end tokens remain the most salient. Beginning frames the task; end triggers the completion. The middle carries detail, but is more tolerant to noise.

**This replaces the naive "monoid identity" hypothesis** (arbitrary text at beginning/end is differential). Middle-invariance is categorically more defensible.

**Testable Predictions**:
1. Inserting random tokens in the middle → similar output distribution
2. Removing middle tokens (within semantic bounds) → similar output
3. Reordering middle clauses (where order-independent) → similar output

---

## Deliverable 1: Middle-Invariance Probe (3 days)

```python
class MiddleInvarianceProbe:
    """
    Test: Does the middle matter less than the edges?
    """

    async def middle_perturbation_test(self, llm: LLM, prompt: str, n: int = 50) -> float:
        """
        Insert noise tokens in the middle 20-80% of the prompt.
        Measure: How often does this CHANGE the answer?

        If middle-invariance holds: Change rate ≈ 0
        If middle is critical: Change rate > 0
        """
        base = [await llm.solve(prompt) for _ in range(n)]

        # Inject whitespace/filler in the middle
        mid_start = len(prompt) // 5
        mid_end = 4 * len(prompt) // 5
        perturbed_prompt = (
            prompt[:mid_start]
            + " [Note: intermediate detail follows.] "
            + prompt[mid_start:mid_end]
            + " [End intermediate detail.] "
            + prompt[mid_end:]
        )

        perturbed = [await llm.solve(perturbed_prompt) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        perturbed_mode = Counter(perturbed).most_common(1)[0][0]

        return 1.0 if base_mode == perturbed_mode else 0.0

    async def middle_deletion_test(self, llm: LLM, prompt: str, n: int = 50) -> float:
        """
        Remove a semantically-redundant middle clause.
        Measure: Does the answer stay the same?
        """
        # Identify a middle clause (heuristic: second sentence if multi-sentence)
        sentences = prompt.split(". ")
        if len(sentences) < 3:
            return 1.0  # Not applicable

        # Remove middle sentence
        reduced_prompt = ". ".join(sentences[:1] + sentences[2:])

        base = [await llm.solve(prompt) for _ in range(n)]
        reduced = [await llm.solve(reduced_prompt) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        reduced_mode = Counter(reduced).most_common(1)[0][0]

        return 1.0 if base_mode == reduced_mode else 0.0

    async def edge_perturbation_test(self, llm: LLM, prompt: str, n: int = 50) -> float:
        """
        CONTROL: Insert noise at the BEGINNING.
        Measure: This SHOULD break things (lower score = hypothesis confirmed).
        """
        base = [await llm.solve(prompt) for _ in range(n)]
        prefix_perturbed = [await llm.solve("Ignore this. " + prompt) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        perturbed_mode = Counter(prefix_perturbed).most_common(1)[0][0]

        # INVERTED: We WANT this to differ
        return 0.0 if base_mode == perturbed_mode else 1.0
```

**Output**: A score from 0-1 for each problem. Higher = middle-invariance holds.

---

## Deliverable 2: Monad Variators (4 days)

**Concept**: Transformations that preserve prompt/agent identity.

These make prompts act "more monadically"—transformations that preserve essence:

1. **Language translation** (English → Spanish for same semantic content)
2. **Whitespace normalization** (extra spaces, line breaks)
3. **Character swaps within tolerance** (typos that preserve meaning)
4. **Reordering non-ordered information** (e.g., "red, blue, green" → "green, blue, red")

```python
class MonadVariatorProbe:
    """
    Test: Do semantically-equivalent transformations preserve behavior?
    """

    async def language_invariance_test(self, llm: LLM, prompt: str, n: int = 30) -> float:
        """
        Translate prompt to Spanish, then back to English.
        Measure: Does the answer stay the same?
        """
        # Translate using LLM itself
        spanish = await llm.generate(f"Translate to Spanish: {prompt}")
        back_to_english = await llm.generate(f"Translate to English: {spanish}")

        base = [await llm.solve(prompt) for _ in range(n)]
        translated = [await llm.solve(back_to_english) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        translated_mode = Counter(translated).most_common(1)[0][0]

        return 1.0 if base_mode == translated_mode else 0.0

    async def whitespace_invariance_test(self, llm: LLM, prompt: str, n: int = 30) -> float:
        """
        Add extra whitespace throughout.
        Measure: Should not change answer.
        """
        import re
        # Double all spaces
        spaced_prompt = re.sub(r' ', '  ', prompt)

        base = [await llm.solve(prompt) for _ in range(n)]
        spaced = [await llm.solve(spaced_prompt) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        spaced_mode = Counter(spaced).most_common(1)[0][0]

        return 1.0 if base_mode == spaced_mode else 0.0

    async def reordering_invariance_test(self, llm: LLM, prompt: str, items: list[str], n: int = 30) -> float:
        """
        Given a prompt with an unordered list of items, shuffle the list.
        Measure: Should not change answer.

        Example: "Given colors: red, blue, green" → "Given colors: green, blue, red"
        """
        import random
        shuffled_items = items.copy()
        random.shuffle(shuffled_items)

        original_list = ", ".join(items)
        shuffled_list = ", ".join(shuffled_items)

        perturbed_prompt = prompt.replace(original_list, shuffled_list)

        base = [await llm.solve(prompt) for _ in range(n)]
        shuffled = [await llm.solve(perturbed_prompt) for _ in range(n)]

        base_mode = Counter(base).most_common(1)[0][0]
        shuffled_mode = Counter(shuffled).most_common(1)[0][0]

        return 1.0 if base_mode == shuffled_mode else 0.0
```

**Output**: Variator score from 0-1. Higher = more monadic behavior.

---

## Deliverable 3: Sheaf Coherence Detector (5 days)

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

## Deliverable 4: The Phased Research Protocol (5 days)

**NEW APPROACH**: Start small, validate machinery, scale gradually.

```python
async def run_phased_research_protocol():
    """
    Phase A: Toy example (validate basic machinery)
    Phase B: Small run with full trace (1 trail/problem/agent, complete instrumentation)
    Phase C: "Proof" run with n=2-5 (statistical validity without cost)
    Phase D: Gradual scale OR attack full experiment
    """

    # PHASE A: Single toy example
    toy_problem = "What is 2 + 2?"
    toy_trace = await llm.generate_cot(toy_problem)

    toy_results = {
        'middle_invariance': await middle_probe.middle_perturbation_test(llm, toy_problem, n=10),
        'monad_variator': await variator_probe.whitespace_invariance_test(llm, toy_problem, n=10),
        'sheaf_coherence': (await sheaf_detector.detect(toy_trace)).score
    }

    print(f"Phase A (Toy): {toy_results}")
    if all(score > 0.5 for score in toy_results.values()):
        print("✅ Phase A passed - machinery works")
    else:
        print("❌ Phase A failed - fix machinery before proceeding")
        return

    # PHASE B: Small run with full instrumentation (n=1 per problem)
    phase_b_problems = GSM8K[:10]
    phase_b_results = []

    for problem in phase_b_problems:
        trace = await llm.generate_cot(problem.question)
        answer = extract_answer(trace)

        phase_b_results.append({
            'problem_id': problem.id,
            'trace': trace,
            'correct': problem.check(answer),
            'middle_invariance': await middle_probe.middle_perturbation_test(llm, problem.question, n=5),
            'edge_perturbation': await middle_probe.edge_perturbation_test(llm, problem.question, n=5),
            'monad_variator': await variator_probe.whitespace_invariance_test(llm, problem.question, n=5),
            'sheaf_coherence': (await sheaf_detector.detect(trace)).score
        })

    df_b = pd.DataFrame(phase_b_results)
    print(f"Phase B (n=10, full trace):")
    print(df_b[['correct', 'middle_invariance', 'monad_variator', 'sheaf_coherence']].describe())

    # PHASE C: "Proof" run (n=2-5 per problem, 50 problems)
    phase_c_problems = GSM8K[:50]
    phase_c_results = []

    for problem in phase_c_problems:
        for trial in range(3):  # n=3 for statistical validity
            trace = await llm.generate_cot(problem.question)
            answer = extract_answer(trace)

            phase_c_results.append({
                'problem_id': problem.id,
                'trial': trial,
                'trace': trace,
                'correct': problem.check(answer),
                'middle_invariance': await middle_probe.middle_perturbation_test(llm, problem.question, n=10),
                'edge_perturbation': await middle_probe.edge_perturbation_test(llm, problem.question, n=10),
                'monad_variator_whitespace': await variator_probe.whitespace_invariance_test(llm, problem.question, n=10),
                'monad_variator_language': await variator_probe.language_invariance_test(llm, problem.question, n=10),
                'sheaf_coherence': (await sheaf_detector.detect(trace)).score
            })

    df_c = pd.DataFrame(phase_c_results)

    correlations = {
        'middle_invariance_corr': df_c['middle_invariance'].corr(df_c['correct']),
        'edge_perturbation_corr': df_c['edge_perturbation'].corr(df_c['correct']),
        'monad_variator_ws_corr': df_c['monad_variator_whitespace'].corr(df_c['correct']),
        'monad_variator_lang_corr': df_c['monad_variator_language'].corr(df_c['correct']),
        'sheaf_corr': df_c['sheaf_coherence'].corr(df_c['correct']),
    }

    print(f"Phase C (n=50×3): {correlations}")

    # DECISION GATE: Do correlations warrant Phase D?
    if correlations['middle_invariance_corr'] > 0.25 or correlations['sheaf_corr'] > 0.3:
        print("✅ Phase C shows signal - proceed to Phase D (full scale)")
        # PHASE D: Full experiment (500 problems × 10 trials)
        return await run_phase_d_full_scale()
    else:
        print("❌ Phase C shows no signal - stop or pivot")
        return correlations
```

---

## Success Propositions

| Proposition | Threshold | Consequence if False |
|-------------|-----------|---------------------|
| Middle-invariance correlates with accuracy | r > 0.25 | Drop middle-invariance hypothesis |
| Edge-perturbation anti-correlates with accuracy | r < -0.2 | Edges not more important than middle |
| Monad variators preserve correctness | variator_score > 0.6 | Variators don't capture monadic behavior |
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
  - id: middle_invariance_correlation
    description: "Middle-invariance correlates with accuracy"
    metric: pearson_r
    threshold: 0.25
    direction: ">"
    required: true

  - id: edge_perturbation_correlation
    description: "Edge perturbation anti-correlates with accuracy"
    metric: pearson_r
    threshold: -0.2
    direction: "<"
    required: true

  - id: monad_variator_score
    description: "Monad variators preserve correctness"
    metric: mean_score
    threshold: 0.6
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

# Run correlation study, cache results (30 min TTL)
handle = await engine.validate_cached(
    "categorical_phase1",
    measurements={
        "middle_invariance_correlation": study_results['middle_invariance_corr'],
        "edge_perturbation_correlation": study_results['edge_perturbation_corr'],
        "monad_variator_score": study_results['monad_variator_avg'],
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

- ~~Simple monad identity (prefix/suffix)~~ — Replaced by middle-invariance hypothesis
- ~~1000 problem runs upfront~~ — Replaced by phased research protocol (A→B→C→D)
- ~~Operad law checking~~ — Too complex for Phase 1. Monad + Sheaf are sufficient.
- ~~Syntax reasoning AST~~ — Moved to Phase 2. Measurement comes first.
- ~~Elaborate claim extraction~~ — LLM-based extraction is good enough.
- ~~Multiple benchmarks~~ — GSM8K + HotpotQA cover math and multi-hop. Enough.

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-3 | Middle-invariance probe implemented and tested (Phase A toy validation) |
| 4-7 | Monad variator probe implemented and tested |
| 8-12 | Sheaf detector implemented and tested |
| 13-15 | Phase B + Phase C runs (small-scale correlation study) |
| 16-18 | Analysis, decision gate, Phase D launch (if warranted) |

---

## Integration

```python
# New paths in AGENTESE
"concept.laws.middle_invariance" → MiddleInvarianceNode
"concept.laws.monad_variators" → MonadVariatorNode
"concept.laws.sheaf_coherence" → SheafCoherenceNode

# New witness metadata
@dataclass
class Mark:
    # ... existing fields ...
    middle_invariance_score: float | None = None
    monad_variator_score: float | None = None
    sheaf_score: float | None = None
```

---

*Phase 1 is 3 weeks. At the end, we know if categorical machine reasoning is real or a beautiful fiction. Either answer is valuable.*
