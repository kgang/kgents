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
        """
        step_text = self.extract_step(trace, step_idx)
        scores = self.forward(*self.tokenize(step_text))

        # Weighted combination: sheaf matters most
        return 0.3 * scores.monad + 0.5 * scores.sheaf + 0.2 * scores.correctness
```

**Training Data**: Phase 1 generated 10,000 traces with labels. Use them.

```python
def create_training_data():
    """
    Convert Phase 1 correlation study into training examples.
    """
    examples = []
    for row in phase1_results:
        steps = parse_steps(row['trace'])
        for i, step in enumerate(steps):
            examples.append({
                'text': step,
                'monad_label': row['monad_identity'],  # From Phase 1
                'sheaf_label': row['sheaf_coherence'],  # From Phase 1
                'correct_label': float(row['correct'])
            })
    return Dataset.from_dict(examples)

def train_cprm(dataset: Dataset) -> CPRM:
    model = CPRM()
    optimizer = AdamW(model.parameters(), lr=2e-5)

    for epoch in range(3):
        for batch in DataLoader(dataset, batch_size=32, shuffle=True):
            scores = model(batch['input_ids'], batch['attention_mask'])

            loss = (
                F.binary_cross_entropy(scores.monad, batch['monad_label']) +
                F.binary_cross_entropy(scores.sheaf, batch['sheaf_label']) +
                F.binary_cross_entropy(scores.correctness, batch['correct_label'])
            )

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

    return model
```

**Output**: A trained CPRM that scores any reasoning step for law compliance.

---

## Deliverable 2: CPRM-Guided Search (5 days)

Replace standard beam search with CPRM-guided search. Prune branches that violate laws.

```python
class CPRMSearch:
    """
    Best-first search guided by CPRM scores.
    """

    def __init__(self, llm: LLM, cprm: CPRM, beam_width: int = 5):
        self.llm = llm
        self.cprm = cprm
        self.beam_width = beam_width

    async def search(self, problem: str, max_steps: int = 10) -> SearchResult:
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
    description: "Train Categorical Process Reward Model"
    propositions:
      - id: cprm_auc
        description: "CPRM heads achieve AUC > 0.75"
        metric: auc
        threshold: 0.75
        direction: ">"
        required: true
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

# Phase 2 has dependencies: cprm_training → search_integration
# Validate each phase as you complete it

# After training CPRM
handle = await engine.validate_cached(
    "categorical_phase2",
    {"cprm_auc": validation_auc},
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

## What We Cut

- ~~Descent consensus~~ — Complex multi-agent machinery deferred to Phase 3
- ~~Elaborate PRM architecture~~ — DeBERTa + 3 heads is sufficient
- ~~Multiple training runs~~ — One run, evaluate, iterate if needed
- ~~Operad checking~~ — Still not ready; monad + sheaf carry the weight

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-5 | CPRM training data preparation |
| 6-10 | CPRM training and validation |
| 11-15 | CPRM-guided search implementation |
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

## The Key Metric

**Search efficiency**: Nodes explored per correct answer.

If CPRM-guided search achieves the same accuracy with 30% fewer nodes, the categorical approach pays for itself. Every LLM call costs money and time. Pruning bad paths early is pure value.

---

*Phase 2 is 4 weeks. At the end, categorical laws are a training signal, not just a measurement. Reasoning gets cheaper and more reliable.*
