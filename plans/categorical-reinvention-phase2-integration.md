# Phase 2: Integration

> *"The probe becomes the training signal."*

**Timeline**: 4 weeks
**Prerequisite**: Phase 1 correlations validated (AUC > 0.7)
**Core Deliverable**: Categorical Process Reward Model (CPRM)

---

## The Insight

Phase 1 proved: categorical laws predict reasoning quality. Phase 2 converts this insight into a training signal.

Standard Process Reward Models score steps by "does this lead to correct answer?" CPRM scores steps by "does this satisfy categorical laws?" — and because laws predict correctness, this is a better proxy that generalizes beyond the training distribution.

---

## Deliverable 1: Categorical Process Reward Model (10 days)

One model. Three heads. Each head predicts law satisfaction.

```python
class CPRM(nn.Module):
    """
    Backbone + 3 scoring heads.
    Trained on Phase 1 data with automated labels.
    TRAINED ON MIDDLE-PERTURBATION DATA.
    """

    def __init__(self, backbone: str = "microsoft/deberta-v3-base"):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(backbone)
        hidden = self.encoder.config.hidden_size

        self.monad_head = nn.Linear(hidden, 1)
        self.sheaf_head = nn.Linear(hidden, 1)
        self.correctness_head = nn.Linear(hidden, 1)

    def forward(self, input_ids, attention_mask) -> CPRMScores:
        hidden = self.encoder(input_ids, attention_mask).last_hidden_state
        pooled = hidden.mean(dim=1)

        return CPRMScores(
            monad=self.monad_head(pooled).sigmoid(),
            sheaf=self.sheaf_head(pooled).sigmoid(),
            correctness=self.correctness_head(pooled).sigmoid()
        )

    def score_step(self, trace: str, step_idx: int) -> float:
        """
        Score a single step. Used during search.
        INVARIANT TO MONAD VARIATORS (language, whitespace, reordering).
        """
        step_text = self.extract_step(trace, step_idx)
        scores = self.forward(*self.tokenize(step_text))

        # Weighted combination: sheaf matters most
        return 0.3 * scores.monad + 0.5 * scores.sheaf + 0.2 * scores.correctness
```

### Middle-Invariance Training Protocol

**Hypothesis**: CPRM trained on middle-perturbed data is more robust to variation.

```python
def create_middle_perturbation_dataset():
    """
    Generate training data with middle-perturbations applied.

    Phase A: Simple toy example (1 problem, 1 trace)
    Phase B: Small run with full trace (1 trail, n=1)
    Phase C: "Proof" run (n=2-5 problems)
    Phase D: Scale incrementally to full training set
    """

    # Phase A: Toy example (debugging)
    toy_problem = "What is 5 + 3?"
    toy_trace = generate_single_trace(toy_problem)
    toy_perturbed = apply_middle_perturbations(toy_trace, all_types=True)
    validate_toy_example(toy_perturbed)

    # Phase B: Single trail (full instrumentation)
    trail = generate_full_trail(toy_problem, model="claude-opus-4")
    validate_perturbations_preserve_laws(trail)

    # Phase C: Proof run (n=3)
    proof_problems = ["5+3", "x=7, x+2", "sqrt(16)"]
    for prob in proof_problems:
        trail = generate_trail(prob)
        validate_middle_invariance(trail)

    # Phase D: Scale incrementally
    # Start: 10 problems, verify all correct
    # Then: 50 problems, check for drift
    # Then: 500 problems, check for scaling issues
    # Finally: Full Phase 1 dataset (~10K traces)

    examples = []
    for problem in phase1_problems:
        base_traces = phase1_results[problem]['traces']

        for trace in base_traces:
            # Apply middle-perturbations: group, shuffle middle, paraphrase middle
            perturbed_variants = [
                trace,  # Original
                perturb_step_grouping(trace),  # Group 2+3 into one
                perturb_middle_shuffle(trace),  # Reorder middle steps
                perturb_middle_paraphrase(trace),  # Rephrase middle
            ]

            for variant in perturbed_variants:
                steps = parse_steps(variant)
                for i, step in enumerate(steps):
                    examples.append({
                        'text': step,
                        'monad_label': check_monad_identity(step),
                        'sheaf_label': check_sheaf_coherence(variant, i),
                        'correct_label': float(variant_correct(variant)),
                        'perturbation_type': detect_perturbation_type(variant, trace)
                    })

    return Dataset.from_dict(examples)


def apply_middle_perturbations(trace: str, all_types: bool = False) -> list[str]:
    """
    Generate middle-perturbed variants of a trace.

    Types of middle-perturbations:
    - Step grouping: Combine adjacent steps
    - Step reordering: Shuffle commutative middle steps
    - Paraphrasing: Rephrase middle steps in different language
    - Whitespace: Vary indentation and spacing
    """
    variants = [trace]
    steps = parse_steps(trace)

    # Group adjacent middle steps (not first/last)
    if len(steps) >= 3:
        grouped = [
            steps[0],
            " ".join(steps[1:-1]),  # Merge middle
            steps[-1]
        ]
        variants.append("\n".join(grouped))

    # Shuffle middle steps (if they're commutative)
    if len(steps) >= 4:
        middle_shuffled = steps[:1] + random.sample(steps[1:-1], len(steps[1:-1])) + steps[-1:]
        variants.append("\n".join(middle_shuffled))

    # Paraphrase middle (preserve semantics)
    if len(steps) >= 3:
        paraphrased = [steps[0]] + [paraphrase(s) for s in steps[1:-1]] + [steps[-1]]
        variants.append("\n".join(paraphrased))

    return variants


def train_cprm_with_middle_invariance(dataset: Dataset) -> CPRM:
    """
    Train CPRM to be invariant to middle perturbations.
    """
    model = CPRM()
    optimizer = AdamW(model.parameters(), lr=2e-5)

    # Phase A: Validate on toy example
    toy_batch = dataset.filter(lambda x: x['problem_id'] == 'toy')
    toy_loss = validate_toy_training(model, toy_batch)
    assert toy_loss < 0.5, "Toy example should train to low loss"

    # Phase B: Single trail with full trace
    trail_batch = dataset.filter(lambda x: x['trail_id'] == 'proof_trail_1')
    validate_full_trail(model, trail_batch)

    # Phase C: Proof run (n=3)
    proof_batches = [dataset.filter(lambda x: x['problem_id'] == f'proof_{i}') for i in range(3)]
    for proof_batch in proof_batches:
        validate_middle_invariance_property(model, proof_batch)

    # Phase D: Full training
    for epoch in range(3):
        for batch in DataLoader(dataset, batch_size=32, shuffle=True):
            scores = model(batch['input_ids'], batch['attention_mask'])

            # Standard loss
            loss = (
                F.binary_cross_entropy(scores.monad, batch['monad_label']) +
                F.binary_cross_entropy(scores.sheaf, batch['sheaf_label']) +
                F.binary_cross_entropy(scores.correctness, batch['correct_label'])
            )

            # Middle-invariance regularization:
            # Penalize different scores for middle-perturbations of same trace
            if 'perturbation_group' in batch:
                group_scores = scores.monad.view(-1, num_variants_per_trace)
                invariance_loss = group_scores.var(dim=1).mean()
                loss = loss + 0.1 * invariance_loss

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

    return model
```

### Monad Variator Invariance

**Hypothesis**: CPRM should score traces the same under monad variators (language, whitespace, reordering).

```python
def test_variator_invariance(cprm: CPRM):
    """
    Test that CPRM scores are invariant to monad variators.

    Variators:
    - Language: "Let x = 5" vs "Set x to 5" vs "x is assigned 5"
    - Whitespace: different indentation, newlines
    - Reordering: commutative steps in different order
    """

    base_trace = """
    Let x = 5
    Let y = 3
    Compute x + y
    Result: 8
    """

    # Language variator
    language_variant = """
    Set x to 5
    Set y to 3
    Add x and y
    Answer: 8
    """

    # Whitespace variator
    whitespace_variant = "Let x = 5\nLet y = 3\nCompute x + y\nResult: 8"

    # Reordering variator (y and x assignments are commutative)
    reordering_variant = """
    Let y = 3
    Let x = 5
    Compute x + y
    Result: 8
    """

    base_score = cprm.score_step(base_trace, 0)
    lang_score = cprm.score_step(language_variant, 0)
    ws_score = cprm.score_step(whitespace_variant, 0)
    reorder_score = cprm.score_step(reordering_variant, 0)

    # All scores should be within 5% of each other
    assert abs(base_score - lang_score) < 0.05, "Language variator should not affect score"
    assert abs(base_score - ws_score) < 0.05, "Whitespace variator should not affect score"
    assert abs(base_score - reorder_score) < 0.05, "Reordering variator should not affect score"

    print("✅ CPRM is invariant to monad variators")
```

---

## Deliverable 2: CPRM-Guided Search (5 days)

Replace standard beam search with CPRM-guided search. Prune branches that violate laws.

**Research Protocol Applied**:

```python
class CPRMSearch:
    """
    Best-first search guided by CPRM scores.
    DEVELOPED WITH PHASED PROTOCOL.
    """

    def __init__(self, llm: LLM, cprm: CPRM, beam_width: int = 5):
        self.llm = llm
        self.cprm = cprm
        self.beam_width = beam_width

    async def search(self, problem: str, max_steps: int = 10) -> SearchResult:
        """
        Phase A: Toy problem (3 + 5)
        Phase B: Single trail with full logging
        Phase C: n=3 problems, verify correctness
        Phase D: Full benchmark
        """
        # Priority queue: (negative_score, trace, depth)
        frontier = [(0.0, "", 0)]
        best_complete = None

        while frontier:
            neg_score, trace, depth = heapq.heappop(frontier)

            if depth >= max_steps:
                if best_complete is None or neg_score < best_complete[0]:
                    best_complete = (neg_score, trace)
                continue

            # Generate continuations
            continuations = await self.llm.generate_n(
                trace + "\nNext step:",
                n=self.beam_width * 2  # Over-generate, then filter
            )

            # Score each continuation
            scored = []
            for cont in continuations:
                new_trace = trace + "\n" + cont
                score = self.cprm.score_step(new_trace, depth)

                # Hard filter: reject low-coherence steps
                if score < 0.3:
                    continue

                scored.append((score, new_trace))

            # Keep top beam_width
            scored.sort(reverse=True)
            for score, new_trace in scored[:self.beam_width]:
                heapq.heappush(frontier, (-score, new_trace, depth + 1))

        return SearchResult(
            trace=best_complete[1] if best_complete else trace,
            score=-best_complete[0] if best_complete else 0
        )


async def validate_cprm_search_phased():
    """Phased validation of CPRM search."""

    # Phase A: Toy example
    toy_result = await CPRMSearch(...).search("What is 3 + 5?")
    assert "8" in toy_result.trace, "Toy problem should work"

    # Phase B: Single trail with logging
    trail_result = await CPRMSearch(...).search("Let x=7. What is x+2?")
    print(f"Trail trace:\n{trail_result.trace}")
    validate_step_scores(trail_result)

    # Phase C: Proof run (n=3)
    proof_problems = [
        "What is 10 - 3?",
        "If y = 4, what is 2*y?",
        "Compute sqrt(25)"
    ]
    for prob in proof_problems:
        result = await CPRMSearch(...).search(prob)
        assert result.score > 0.7, f"Proof problem '{prob}' should score high"

    # Phase D: Scale to GSM8K
    # Start with 10 problems, then 50, then 500, then full benchmark
    gsm8k_sample = sample_gsm8k(n=10)
    for problem in gsm8k_sample:
        result = await CPRMSearch(...).search(problem)
        # Track accuracy, node exploration, etc.
```

---

## Deliverable 3: Live Coherence Witness (5 days)

Every mark gets checked. Violations trigger alerts.

```python
class CoherenceWitness:
    """
    Witness with sheaf checking on every mark.
    """

    def __init__(self, base: Witness, detector: SheafDetector):
        self.base = base
        self.detector = detector
        self.claims: list[str] = []

    async def mark(self, action: str, reasoning: str, **kwargs) -> Mark:
        # Extract claims from this mark
        new_claims = await self.detector.extract_claims(f"{action}: {reasoning}")

        # Check against history
        violations = []
        for new in new_claims:
            for old in self.claims:
                if await self.detector.contradicts(new[0], old[0]):
                    violations.append((new[0], old[0]))

        # Create mark with coherence info
        mark = await self.base.mark(action, reasoning, **kwargs)
        mark.coherence = CoherenceInfo(
            violations=violations,
            is_coherent=len(violations) == 0
        )

        # Update history
        self.claims.extend(new_claims)

        # Alert on violation
        if violations:
            self._alert(mark, violations)

        return mark

    def _alert(self, mark: Mark, violations: list):
        """
        Violations are important. Log them prominently.
        """
        for new, old in violations:
            logger.error(
                f"COHERENCE VIOLATION in mark {mark.id}:\n"
                f"  New claim: {new}\n"
                f"  Contradicts: {old}"
            )
```

---

## Success Propositions

| Proposition | Test | Consequence if False |
|-------------|------|---------------------|
| CPRM heads achieve AUC > 0.75 on held-out data | Validation split | Training failed, debug |
| CPRM is invariant to monad variators (language, whitespace, reordering) | Variator test suite | Training needs variator augmentation |
| CPRM trained on middle-perturbations is more robust | Compare standard vs middle-perturbed training | Middle-invariance hypothesis rejected |
| CPRM-guided search matches standard search accuracy | GSM8K benchmark | CPRM not useful for search |
| CPRM-guided search explores 30% fewer nodes | Node count comparison | CPRM not efficient |
| Coherence Witness catches >80% of introduced contradictions | Synthetic test | Detector needs tuning |

### ValidationEngine Integration

Track Phase 2 propositions with validated gates:

```yaml
# initiatives/categorical-phase2.yaml
id: categorical_phase2
name: "Phase 2: Integration"
description: "Convert categorical insights into training signal"
witness_tags: ["categorical", "phase2", "integration"]

phases:
  - id: cprm_training
    name: "CPRM Training"
    description: "Train Categorical Process Reward Model with middle-invariance"
    propositions:
      - id: cprm_auc
        description: "CPRM heads achieve AUC > 0.75"
        metric: auc
        threshold: 0.75
        direction: ">"
        required: true
      - id: variator_invariance
        description: "CPRM invariant to monad variators"
        metric: accuracy
        threshold: 0.95
        direction: ">"
        required: true
      - id: middle_perturbation_robustness
        description: "Middle-perturbed training improves robustness"
        metric: percent
        threshold: 10  # 10% improvement in robustness
        direction: ">"
        required: false  # Nice-to-have
    gate:
      condition: all_required

  - id: search_integration
    name: "Search Integration"
    description: "CPRM-guided search effectiveness"
    depends_on: [cprm_training]
    propositions:
      - id: search_accuracy_parity
        description: "CPRM search matches baseline accuracy"
        metric: percent
        threshold: 95  # 95% of baseline accuracy
        direction: ">="
        required: true
      - id: search_efficiency
        description: "30% fewer nodes explored"
        metric: percent
        threshold: 30
        direction: ">="
        required: true
    gate:
      condition: all_required

  - id: coherence_witness
    name: "Coherence Witness"
    description: "Live coherence checking"
    depends_on: [cprm_training]
    propositions:
      - id: contradiction_detection
        description: "Catches >80% of introduced contradictions"
        metric: recall
        threshold: 0.8
        direction: ">"
        required: true
    gate:
      condition: all_required
```

```python
# Phased validation with caching
engine = get_validation_engine()

# Phase A: Toy example validation
toy_results = run_toy_validation()
assert toy_results['loss'] < 0.5

# Phase B: Single trail validation
trail_results = run_trail_validation()
print(f"Trail trace logged: {len(trail_results['steps'])} steps")

# Phase C: Proof run (n=3)
proof_results = run_proof_validation(n=3)
assert all(r['passed'] for r in proof_results)

# Phase D: Full training and validation
handle = await engine.validate_cached(
    "categorical_phase2",
    {
        "cprm_auc": validation_auc,
        "variator_invariance": variator_test_accuracy,
        "middle_perturbation_robustness": robustness_improvement_percent,
    },
    phase_id="cprm_training",
    ttl=timedelta(hours=1),  # Training results stable
)

# After benchmarking search
handle = await engine.validate_cached(
    "categorical_phase2",
    {
        "search_accuracy_parity": (cprm_accuracy / baseline_accuracy) * 100,
        "search_efficiency": node_reduction_percent,
    },
    phase_id="search_integration",
)

# Check overall progress
status = engine.get_status("categorical_phase2")
print(f"Phase 2: {status.progress_percent}% complete")
print(f"Phases done: {status.phases_complete}")
```

---

## Research Protocol Summary

**Every experiment follows the four-phase protocol**:

1. **Phase A**: Simple toy example (1 problem, 1 trace) — debug and validate
2. **Phase B**: Small run with full trace (1 trail, n=1) — instrument and log everything
3. **Phase C**: "Proof" run (n=2-5 problems) — verify hypothesis holds
4. **Phase D**: Scale incrementally — 10 → 50 → 500 → full dataset

**NO MORE "1000 problems, 10 traces each"** — that's Phase D after A/B/C validate.

---

## What We Cut

- ~~Descent consensus~~ — Complex multi-agent machinery deferred to Phase 3
- ~~Elaborate PRM architecture~~ — DeBERTa + 3 heads is sufficient
- ~~Multiple training runs~~ — One run, evaluate, iterate if needed
- ~~Operad checking~~ — Still not ready; monad + sheaf carry the weight

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-2 | Phase A: Toy example validation |
| 3-4 | Phase B: Single trail with full instrumentation |
| 5-6 | Phase C: Proof run (n=3) |
| 7-10 | Phase D: Scale to full dataset |
| 11-15 | CPRM-guided search (phased protocol) |
| 16-20 | CoherenceWitness integration |
| 21-25 | Benchmarking and tuning |
| 26-28 | Documentation |

---

## Integration

```python
# AGENTESE paths
"concept.prm.score" → CPRMScoreNode      # Score a trace
"concept.search.guided" → CPRMSearchNode  # Run guided search

# Witness becomes coherence-aware by default
witness = CoherenceWitness(Witness(storage), SheafDetector())
```

---

## The Key Metrics

1. **Search efficiency**: Nodes explored per correct answer
2. **Variator invariance**: Score consistency across language/whitespace/reordering
3. **Middle-perturbation robustness**: Performance on middle-shuffled traces

If CPRM-guided search achieves the same accuracy with 30% fewer nodes, the categorical approach pays for itself. Every LLM call costs money and time. Pruning bad paths early is pure value.

---

*Phase 2 is 4 weeks. At the end, categorical laws are a training signal, not just a measurement. Reasoning gets cheaper and more reliable. Middle-invariance makes it robust. Monad variators don't matter.*
