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

```python
class BindingBenchmark:
    """
    Test: Can the model remember x=5 after N tokens?
    """

    def generate_problem(self, gap: int) -> tuple[str, str]:
        """
        Create problem with controlled binding distance.
        """
        var = random.choice(['x', 'y', 'z', 'n', 'm'])
        val = random.randint(1, 100)

        # Filler tokens between binding and use
        filler = " ".join(["The sky is blue."] * (gap // 5))

        prompt = f"Let {var} = {val}. {filler} What is {var} + 1?"
        answer = str(val + 1)
        return prompt, answer

    async def evaluate(self, model, gaps: list[int] = [10, 25, 50, 100, 200]):
        """
        Measure accuracy vs binding distance.
        """
        results = {}
        for gap in gaps:
            correct = 0
            for _ in range(100):
                prompt, expected = self.generate_problem(gap)
                response = await model.generate(prompt)
                if expected in response:
                    correct += 1
            results[gap] = correct / 100
        return results
```

**Target Results**:

| Gap (tokens) | Baseline | With SBM |
|--------------|----------|----------|
| 10 | 95% | 99% |
| 25 | 85% | 99% |
| 50 | 70% | 98% |
| 100 | 55% | 97% |
| 200 | 40% | 95% |

SBM bindings don't decay. That's the whole point.

---

## Deliverable 3: Training Pipeline (5 days)

Train binding/substitution detectors on synthetic data.

```python
def create_binding_dataset(n: int = 10000) -> Dataset:
    """
    Generate training data with binding annotations.
    """
    examples = []

    for _ in range(n):
        var = random.choice(['x', 'y', 'z'])
        val = random.randint(1, 100)
        gap = random.randint(5, 50)

        filler = " ".join(["word"] * gap)
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

        examples.append({
            'text': text,
            'tokens': tokens,
            'bind_labels': bind_labels,
            'sub_labels': sub_labels
        })

    return Dataset.from_dict(examples)


def train_binding_heads(model: BindingAwareLM, dataset: Dataset):
    """
    Train only the bind_head and sub_head. Freeze everything else.
    """
    for param in model.lm.parameters():
        param.requires_grad = False

    optimizer = AdamW([
        {'params': model.bind_head.parameters()},
        {'params': model.sub_head.parameters()},
        {'params': model.sbm.parameters()}
    ], lr=1e-4)

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
    description: "Basic binding retention"
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
# Benchmark caching for iterative development
engine = get_validation_engine()

# Run binding benchmark (expensive) - cache for iteration
async def run_sbm_validation():
    # Run benchmark once, cache result
    handle = await engine.validate_cached(
        "categorical_phase3",
        {
            "retention_100_tokens": benchmark_results[100],
            "multi_binding": multi_var_accuracy,
        },
        phase_id="sbm_core",
        ttl=timedelta(hours=2),  # Benchmark results don't change often
    )

    # Force recompute after architecture changes
    if architecture_modified:
        handle = await engine.validate_cached(..., force=True)

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

## What We Cut

- ~~Coherence Checker Layers~~ — Nice but not the core innovation. Defer.
- ~~Categorical loss functions~~ — CPRM from Phase 2 serves this purpose.
- ~~Multiple architectures~~ — One architecture, one implementation, make it work.
- ~~Elaborate benchmarking~~ — Binding Benchmark + GSM8K subset. That's it.

---

## Timeline

| Day | Focus |
|-----|-------|
| 1-5 | SBM implementation and unit tests |
| 6-10 | BindingAwareLM integration |
| 11-15 | Binding dataset generation |
| 16-20 | Training pipeline and training |
| 21-25 | Binding Benchmark evaluation |
| 26-30 | GSM8K integration testing |
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
3. Show you exactly what it's tracking (interpretability)

This is the architectural foundation for reliable reasoning.

---

*Phase 3 is 5 weeks. At the end, variable binding is solved. The hardest problem in neural reasoning has a concrete, working solution.*
