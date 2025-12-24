# Phase 3: Architecture

> *"Make the impossible structural."*

**Timeline**: 5 weeks
**Prerequisite**: Phase 2 CPRM working (AUC > 0.75, search efficiency gain)
**Core Deliverable**: Sharp Binding Module

---

## The Problem We Solve

Variable binding is the hardest unsolved problem in neural reasoning.

When a model reasons "Let x = 5. Then x + 3 = 8", the binding of x to 5 is **soft**. It's an attention pattern that decays over distance, interferes with other bindings, and fails unpredictably.

Phase 3 solves this with **Sharp Binding Modules**: discrete, addressable memory slots that hold variable bindings exactly.

---

## Deliverable 1: Sharp Binding Module (15 days)

The core innovation. Everything else is secondary.

```python
class SharpBindingModule(nn.Module):
    """
    16 slots. Each holds (variable, value) pair.
    Write is discrete. Read is winner-take-all.
    Bindings don't decay. Period.

    TESTS BINDING RETENTION UNDER MIDDLE-PERTURBATIONS.
    """

    def __init__(self, num_slots: int = 16, dim: int = 768):
        super().__init__()
        self.num_slots = num_slots
        self.dim = dim

        # Slot storage
        self.keys = nn.Parameter(torch.zeros(num_slots, dim))      # Variable embeddings
        self.values = nn.Parameter(torch.zeros(num_slots, dim))    # Bound values
        self.occupied = nn.Parameter(torch.zeros(num_slots))       # Occupancy flags

        # Projections
        self.key_proj = nn.Linear(dim, dim)
        self.val_proj = nn.Linear(dim, dim)
        self.query_proj = nn.Linear(dim, dim)

    def bind(self, variable: Tensor, value: Tensor, temp: float = 0.1) -> int:
        """
        Discrete write. Uses Gumbel-Softmax for differentiability.
        """
        key = self.key_proj(variable)

        # Score slots: prefer empty, then least similar to existing keys
        empty_bonus = (1 - self.occupied) * 10.0
        similarity_penalty = torch.einsum('d,nd->n', key, self.keys)
        scores = empty_bonus - similarity_penalty

        # Discrete selection
        if self.training:
            selection = F.gumbel_softmax(scores, tau=temp, hard=True)
            slot_idx = selection.argmax().item()
        else:
            slot_idx = scores.argmax().item()

        # Write
        self.keys.data[slot_idx] = key.detach()
        self.values.data[slot_idx] = self.val_proj(value).detach()
        self.occupied.data[slot_idx] = 1.0

        return slot_idx

    def lookup(self, variable: Tensor) -> Tensor:
        """
        Winner-take-all read. Returns exactly one value.
        INVARIANT TO VARIATORS.
        """
        query = self.query_proj(variable)

        # Similarity to all keys
        scores = torch.einsum('d,nd->n', query, self.keys)
        scores = scores - (1 - self.occupied) * 1e9  # Mask empty slots

        # Winner-take-all
        best = scores.argmax()
        return self.values[best]

    def clear(self, slot_idx: int):
        """Explicit deallocation."""
        self.occupied.data[slot_idx] = 0.0

    def dump(self) -> dict:
        """Inspect current state. For debugging and explanation."""
        return {
            i: {'key': self.keys[i], 'value': self.values[i]}
            for i in range(self.num_slots)
            if self.occupied[i] > 0.5
        }
```

**Integration with Language Model**:

```python
class BindingAwareLM(nn.Module):
    """
    Wrap any language model with a Sharp Binding Module.
    Detect binding/substitution operations and route to SBM.
    """

    def __init__(self, base_lm: nn.Module, sbm: SharpBindingModule):
        super().__init__()
        self.lm = base_lm
        self.sbm = sbm

        hidden = base_lm.config.hidden_size
        self.bind_head = nn.Linear(hidden, 1)  # "Is this a binding?"
        self.sub_head = nn.Linear(hidden, 1)   # "Is this a substitution?"

    def forward(self, input_ids, **kwargs):
        # Run base LM
        outputs = self.lm(input_ids, output_hidden_states=True, **kwargs)
        hidden = outputs.hidden_states[-1]

        # Detect operations (per token)
        bind_scores = self.bind_head(hidden).sigmoid().squeeze(-1)
        sub_scores = self.sub_head(hidden).sigmoid().squeeze(-1)

        # Process bindings
        for i in range(hidden.size(1) - 1):
            if bind_scores[0, i] > 0.5:
                # Token i is variable, i+1 is value
                self.sbm.bind(hidden[0, i], hidden[0, i+1])

        # Process substitutions
        for i in range(hidden.size(1)):
            if sub_scores[0, i] > 0.5:
                # Look up and inject
                bound_val = self.sbm.lookup(hidden[0, i])
                hidden[0, i] = hidden[0, i] + bound_val  # Residual add

        # Re-run final layer with modified hidden
        outputs.logits = self.lm.lm_head(hidden)
        return outputs
```

---

## Deliverable 2: Binding Retention Benchmark (5 days)

We need to prove SBM works. Create a benchmark specifically for binding retention.

**HYPOTHESIS**: SBM retains bindings under middle-perturbations (shuffle, paraphrase, grouping).

```python
class BindingBenchmark:
    """
    Test: Can the model remember x=5 after N tokens?
    INCLUDES MIDDLE-PERTURBATION VARIANTS.

    Phase A: Toy example (x=5, filler, x+1)
    Phase B: Single trail with full instrumentation
    Phase C: n=3 binding distances (10, 50, 100 tokens)
    Phase D: Full benchmark across all gaps
    """

    def generate_problem(self, gap: int, perturbation: str = None) -> tuple[str, str]:
        """
        Create problem with controlled binding distance.
        Apply middle-perturbations to filler.

        Perturbations:
        - None: standard filler
        - "shuffle": shuffle filler sentences
        - "paraphrase": rephrase filler
        - "group": merge filler into one block
        """
        var = random.choice(['x', 'y', 'z', 'n', 'm'])
        val = random.randint(1, 100)

        # Filler tokens between binding and use
        filler_sentences = ["The sky is blue."] * (gap // 5)

        if perturbation == "shuffle":
            random.shuffle(filler_sentences)
        elif perturbation == "paraphrase":
            filler_sentences = [paraphrase(s) for s in filler_sentences]
        elif perturbation == "group":
            filler_sentences = [" ".join(filler_sentences)]

        filler = " ".join(filler_sentences)

        prompt = f"Let {var} = {val}. {filler} What is {var} + 1?"
        answer = str(val + 1)
        return prompt, answer

    async def evaluate(
        self,
        model,
        gaps: list[int] = [10, 25, 50, 100, 200],
        perturbations: list[str] = [None, "shuffle", "paraphrase", "group"]
    ):
        """
        Measure accuracy vs binding distance across perturbations.

        Phase A: Single toy example (gap=10, no perturbation)
        Phase B: Single trail (gap=50, all perturbations, full logging)
        Phase C: n=3 gaps (10, 50, 100), all perturbations
        Phase D: All gaps, all perturbations, 100 samples each
        """
        results = {}

        for gap in gaps:
            results[gap] = {}
            for pert in perturbations:
                # Phase A check: if this is first gap/pert, validate toy
                if gap == gaps[0] and pert == perturbations[0]:
                    toy_result = await self._validate_toy(model, gap, pert)
                    assert toy_result['correct'], "Toy example must work"

                # Phase B check: if gap=50 and no pert, log full trail
                if gap == 50 and pert is None:
                    trail_result = await self._validate_trail(model, gap, pert)
                    print(f"Trail logged: {trail_result['trace']}")

                # Phase C/D: run samples
                correct = 0
                n_samples = 3 if (gap in [10, 50, 100]) and len(results) < 3 else 100

                for _ in range(n_samples):
                    prompt, expected = self.generate_problem(gap, pert)
                    response = await model.generate(prompt)
                    if expected in response:
                        correct += 1

                results[gap][pert or "baseline"] = correct / n_samples

        return results

    async def _validate_toy(self, model, gap: int, pert: str) -> dict:
        """Phase A: Validate toy example works."""
        prompt, expected = self.generate_problem(gap, pert)
        response = await model.generate(prompt)
        return {'correct': expected in response, 'prompt': prompt, 'response': response}

    async def _validate_trail(self, model, gap: int, pert: str) -> dict:
        """Phase B: Full trail logging."""
        prompt, expected = self.generate_problem(gap, pert)
        response = await model.generate(prompt, return_trace=True)
        return {
            'trace': response.trace,
            'bindings': model.sbm.dump(),
            'correct': expected in response.text
        }
```

**Target Results**:

| Gap (tokens) | Baseline | Shuffle | Paraphrase | Group | With SBM |
|--------------|----------|---------|------------|-------|----------|
| 10 | 95% | 90% | 92% | 93% | 99% |
| 25 | 85% | 75% | 80% | 82% | 99% |
| 50 | 70% | 55% | 60% | 65% | 98% |
| 100 | 55% | 35% | 40% | 45% | 97% |
| 200 | 40% | 20% | 25% | 30% | 95% |

**Key Hypothesis**: SBM bindings don't decay AND don't care about middle-perturbations. That's the whole point.

---

## Deliverable 3: Training Pipeline (5 days)

Train binding/substitution detectors on synthetic data with middle-perturbations.

**Research Protocol Applied**:

```python
def create_binding_dataset(n: int = 10000) -> Dataset:
    """
    Generate training data with binding annotations.

    Phase A: 1 toy example with all perturbations
    Phase B: 1 trail with full logging
    Phase C: 3 problems × all perturbations
    Phase D: Scale to n=10000
    """
    examples = []

    # Phase A: Toy
    toy_var = 'x'
    toy_val = 5
    toy_gap = 10
    for pert in [None, "shuffle", "paraphrase", "group"]:
        text, tokens, bind_labels, sub_labels = _generate_example(
            toy_var, toy_val, toy_gap, pert
        )
        examples.append({
            'text': text,
            'tokens': tokens,
            'bind_labels': bind_labels,
            'sub_labels': sub_labels,
            'perturbation': pert or "baseline",
            'phase': 'toy'
        })

    # Phase B: Trail (gap=50, all perturbations, logged)
    trail_var = 'y'
    trail_val = 13
    trail_gap = 50
    for pert in [None, "shuffle", "paraphrase", "group"]:
        text, tokens, bind_labels, sub_labels = _generate_example(
            trail_var, trail_val, trail_gap, pert
        )
        examples.append({
            'text': text,
            'tokens': tokens,
            'bind_labels': bind_labels,
            'sub_labels': sub_labels,
            'perturbation': pert or "baseline",
            'phase': 'trail',
            'log_full': True
        })

    # Phase C: Proof (n=3 problems)
    proof_configs = [
        ('z', 7, 25),
        ('n', 42, 75),
        ('m', 100, 150)
    ]
    for var, val, gap in proof_configs:
        for pert in [None, "shuffle", "paraphrase", "group"]:
            text, tokens, bind_labels, sub_labels = _generate_example(var, val, gap, pert)
            examples.append({
                'text': text,
                'tokens': tokens,
                'bind_labels': bind_labels,
                'sub_labels': sub_labels,
                'perturbation': pert or "baseline",
                'phase': 'proof'
            })

    # Phase D: Scale to n
    remaining = n - len(examples)
    for _ in range(remaining):
        var = random.choice(['x', 'y', 'z', 'n', 'm'])
        val = random.randint(1, 100)
        gap = random.randint(5, 200)
        pert = random.choice([None, "shuffle", "paraphrase", "group"])

        text, tokens, bind_labels, sub_labels = _generate_example(var, val, gap, pert)
        examples.append({
            'text': text,
            'tokens': tokens,
            'bind_labels': bind_labels,
            'sub_labels': sub_labels,
            'perturbation': pert or "baseline",
            'phase': 'scale'
        })

    return Dataset.from_dict(examples)


def _generate_example(var: str, val: int, gap: int, perturbation: str = None):
    """Generate one training example with optional middle-perturbation."""
    filler_sentences = ["word"] * gap

    if perturbation == "shuffle":
        random.shuffle(filler_sentences)
    elif perturbation == "paraphrase":
        filler_sentences = [f"token_{i}" for i in range(gap)]
    elif perturbation == "group":
        filler_sentences = [" ".join(filler_sentences)]

    filler = " ".join(filler_sentences)
    text = f"Let {var} = {val}. {filler} What is {var}?"

    tokens = tokenize(text)
    bind_labels = [0] * len(tokens)
    sub_labels = [0] * len(tokens)

    # Mark binding position (the variable in "Let x = ...")
    bind_pos = find_token_position(tokens, var, first=True)
    if bind_pos:
        bind_labels[bind_pos] = 1

    # Mark substitution position (the variable in "What is x?")
    sub_pos = find_token_position(tokens, var, last=True)
    if sub_pos:
        sub_labels[sub_pos] = 1

    return text, tokens, bind_labels, sub_labels


def train_binding_heads(model: BindingAwareLM, dataset: Dataset):
    """
    Train only the bind_head and sub_head. Freeze everything else.
    USES PHASED PROTOCOL FOR VALIDATION.
    """
    for param in model.lm.parameters():
        param.requires_grad = False

    optimizer = AdamW([
        {'params': model.bind_head.parameters()},
        {'params': model.sub_head.parameters()},
        {'params': model.sbm.parameters()}
    ], lr=1e-4)

    # Phase A: Validate toy examples work
    toy_batch = dataset.filter(lambda x: x['phase'] == 'toy')
    toy_loss = validate_toy_batch(model, toy_batch)
    assert toy_loss < 0.5, "Toy should train"

    # Phase B: Log full trail
    trail_batch = dataset.filter(lambda x: x['phase'] == 'trail')
    trail_results = validate_trail_batch(model, trail_batch)
    print(f"Trail bindings: {trail_results['bindings']}")

    # Phase C: Proof run
    proof_batch = dataset.filter(lambda x: x['phase'] == 'proof')
    proof_loss = validate_proof_batch(model, proof_batch)
    assert proof_loss < 0.3, "Proof should train well"

    # Phase D: Full training
    for epoch in range(5):
        for batch in DataLoader(dataset, batch_size=16):
            outputs = model(batch['input_ids'])

            bind_loss = F.binary_cross_entropy(
                model.bind_head(outputs.hidden_states[-1]).squeeze(-1),
                batch['bind_labels'].float()
            )
            sub_loss = F.binary_cross_entropy(
                model.sub_head(outputs.hidden_states[-1]).squeeze(-1),
                batch['sub_labels'].float()
            )

            (bind_loss + sub_loss).backward()
            optimizer.step()
            optimizer.zero_grad()
```

---

## Success Propositions

| Proposition | Test | Consequence if False |
|-------------|------|---------------------|
| SBM retains bindings at 100 tokens with >95% accuracy | Binding Benchmark | Architecture fails |
| SBM handles 5+ simultaneous bindings correctly | Multi-variable test | Slot design needs work |
| SBM bindings invariant to middle-perturbations | Perturbation test suite | Training needs perturbation augmentation |
| Binding/substitution detection achieves F1 > 0.9 | Held-out synthetic data | Detection needs more data |
| End-to-end reasoning improves on binding-heavy problems | GSM8K subset | Integration needs debugging |

### ValidationEngine Integration

Sharp Binding Module validation with benchmark caching:

```yaml
# initiatives/categorical-phase3.yaml
id: categorical_phase3
name: "Phase 3: Architecture"
description: "Sharp Binding Module for variable tracking"
witness_tags: ["categorical", "phase3", "architecture", "sbm"]

phases:
  - id: sbm_core
    name: "SBM Core Implementation"
    description: "Basic binding retention with middle-perturbation robustness"
    propositions:
      - id: retention_100_tokens
        description: "Retains bindings at 100 tokens with >95% accuracy"
        metric: accuracy
        threshold: 0.95
        direction: ">"
        required: true
      - id: multi_binding
        description: "Handles 5+ simultaneous bindings"
        metric: accuracy
        threshold: 0.95
        direction: ">"
        required: true
      - id: perturbation_invariance
        description: "Bindings survive middle-perturbations (shuffle/paraphrase/group)"
        metric: accuracy
        threshold: 0.90
        direction: ">"
        required: true
    gate:
      condition: all_required

  - id: detection_training
    name: "Detection Training"
    description: "Train binding/substitution detectors"
    depends_on: [sbm_core]
    propositions:
      - id: detector_f1
        description: "Binding/substitution F1 > 0.9"
        metric: f1
        threshold: 0.9
        direction: ">"
        required: true
    gate:
      condition: all_required

  - id: e2e_integration
    name: "End-to-End Integration"
    description: "SBM improves real reasoning"
    depends_on: [detection_training]
    propositions:
      - id: gsm8k_improvement
        description: "Improves on binding-heavy GSM8K problems"
        metric: percent
        threshold: 5  # 5% improvement
        direction: ">"
        required: true
    gate:
      condition: all_required
```

```python
# Phased benchmark validation
engine = get_validation_engine()

async def run_sbm_validation():
    """Run binding benchmark with phased protocol."""

    # Phase A: Toy example
    toy_result = await benchmark._validate_toy(model, gap=10, pert=None)
    assert toy_result['correct'], "Toy must work"

    # Phase B: Full trail
    trail_result = await benchmark._validate_trail(model, gap=50, pert=None)
    print(f"Trail trace: {len(trail_result['trace'])} steps")

    # Phase C: Proof run (n=3 gaps)
    proof_results = await benchmark.evaluate(
        model,
        gaps=[10, 50, 100],
        perturbations=[None, "shuffle", "paraphrase", "group"]
    )
    assert all(proof_results[g]['baseline'] > 0.9 for g in [10, 50, 100])

    # Phase D: Full benchmark
    handle = await engine.validate_cached(
        "categorical_phase3",
        {
            "retention_100_tokens": benchmark_results[100]['baseline'],
            "multi_binding": multi_var_accuracy,
            "perturbation_invariance": min(
                benchmark_results[100]['shuffle'],
                benchmark_results[100]['paraphrase'],
                benchmark_results[100]['group']
            ),
        },
        phase_id="sbm_core",
        ttl=timedelta(hours=2),  # Benchmark results don't change often
    )

    return handle


# The Binding Benchmark itself uses proxy caching internally
class BindingBenchmark:
    """Enhanced with ProxyHandle caching."""

    async def evaluate_cached(
        self, model, gaps: list[int], force: bool = False
    ) -> "ProxyHandle[dict[int, float]]":
        """Cache benchmark results via ProxyHandleStore."""
        from services.proxy import SourceType, get_proxy_handle_store

        store = get_proxy_handle_store()
        return await store.compute(
            source_type=SourceType.CUSTOM,
            compute_fn=lambda: self.evaluate(model, gaps),
            human_label=f"SBM Binding Benchmark: {model.__class__.__name__}",
            source_hash=self._model_hash(model),
            force=force,
            ttl=timedelta(hours=1),
        )
```

---

## Research Protocol Summary

**Every deliverable follows the four-phase protocol**:

1. **Phase A**: Toy example (x=5, gap=10, baseline) — debug and validate
2. **Phase B**: Single trail (y=13, gap=50, all perturbations, full logging)
3. **Phase C**: Proof run (n=3 gaps: 10/50/100, all perturbations)
4. **Phase D**: Scale to full benchmark (all gaps, all perturbations, 100 samples)

**NO MORE "test on 1000 problems"** — that's Phase D after A/B/C validate.

---

## What We Cut

- ~~Coherence Checker Layers~~ — Nice but not the core innovation. Defer.
- ~~Categorical loss functions~~ — CPRM from Phase 2 serves this purpose.
- ~~Multiple architectures~~ — One architecture, one implementation, make it work.
- ~~Elaborate benchmarking~~ — Binding Benchmark + GSM8K subset. That's it.

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-2 | Phase A: Toy validation |
| 3-4 | Phase B: Trail validation |
| 5-6 | Phase C: Proof run (n=3) |
| 7-10 | Phase D: Full SBM implementation |
| 11-15 | BindingAwareLM integration |
| 16-20 | Binding dataset generation with perturbations |
| 21-25 | Training pipeline with phased validation |
| 26-30 | Binding Benchmark evaluation |
| 31-35 | Documentation and cleanup |

---

## Integration

```python
# AGENTESE paths
"self.binding.create" → BindingCreateNode    # Explicit bind
"self.binding.lookup" → BindingLookupNode    # Explicit lookup
"self.binding.state" → BindingStateNode      # Inspect current bindings

# CategoricalAgent uses SBM by default
class CategoricalAgent(PolyAgent):
    def __init__(self, state, sbm: SharpBindingModule):
        super().__init__(state)
        self.sbm = sbm

    async def bind(self, var: str, val: Any):
        """Explicit binding API."""
        var_emb = self.embed(var)
        val_emb = self.embed(str(val))
        return self.sbm.bind(var_emb, val_emb)
```

---

## Why This Matters

Variable binding is where symbolic and neural diverge. Symbolic systems bind exactly. Neural systems approximate.

Sharp Binding Modules bridge this gap. For the first time, a neural system can:
1. Remember that x=5 across arbitrary distances
2. Handle multiple variables without interference
3. **Retain bindings under middle-perturbations** (shuffle, paraphrase, group)
4. Show you exactly what it's tracking (interpretability)

This is the architectural foundation for reliable reasoning.

---

*Phase 3 is 5 weeks. At the end, variable binding is solved. The hardest problem in neural reasoning has a concrete, working solution. Middle-perturbations don't matter. Monad variators don't matter. Bindings are sharp.*
