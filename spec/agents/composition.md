# Agent Composition

> *"Composition is at the very root of category theory—it's part of the definition of the category itself."*
> — Bartosz Milewski

---

## The Essence

Agents are morphisms. Composition is how morphisms combine.

```
Given: Agent f: A → B, Agent g: B → C
Composition: (g ∘ f): A → C
```

In kgents, we write `f >> g` (left-to-right, like pipelines).

---

## The Three Laws

### 1. Associativity

```
(f >> g) >> h ≡ f >> (g >> h)
```

Parentheses don't matter. The pipeline is what matters.

### 2. Identity

```
Id >> f ≡ f ≡ f >> Id
```

The identity agent is the unit of composition.

### 3. Closure

```
If f: A → B and g: B → C, then (f >> g): A → C
```

The composition of two agents is itself an agent.

---

## Type Compatibility

For composition to be valid, f's output type MUST be compatible with g's input type:

```
f: String → Number
g: Number → Boolean
(f >> g): String → Boolean  ✓
```

---

## Sequential Composition

The `>>` operator chains agents sequentially:

```python
pipeline = parse >> validate >> transform >> format
result = await pipeline.invoke(input)
```

**Execution**: Each agent runs in turn, output feeding input.

---

## Parallel Composition

Run multiple agents concurrently on the same input:

```
        ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
```

### Parallel Combinators

| Combinator | Signature | Description |
|------------|-----------|-------------|
| `parallel` | `[Agent[A,B]] → Agent[A, [B]]` | Same input, list output |
| `fan_out` | `(Agent[A,B], Agent[A,C]) → Agent[A, (B,C)]` | Heterogeneous tuple output |
| `combine` | `([Agent[A,B]], Combiner) → Agent[A,C]` | With custom aggregation |
| `race` | `[Agent[A,B]] → Agent[A,B]` | First completed wins |

### Laws

```python
# Order Preservation
parallel([A, B, C])(x) = [A(x), B(x), C(x)]

# Input Broadcast
∀ a ∈ parallel([agents]): a receives same input

# Race Non-Determinism
race([A, B])(x) ∈ {A(x), B(x)}
```

---

## Conditional Composition

Branch based on runtime predicates:

```
input → [predicate?] → [A] if true
                      → [B] if false
```

### Conditional Combinators

| Combinator | Signature | Description |
|------------|-----------|-------------|
| `branch` | `(Pred, Agent, Agent) → Agent[A, B\|C]` | Binary branching |
| `switch` | `(KeyFn, Cases, Default) → Agent` | Multi-way dispatch |
| `guarded` | `(Guard, Agent, OnFail) → Agent` | Runs only if guard passes |
| `filter` | `Pred → Agent[List[A], List[A]]` | Filter collections |

### Laws

```python
# Exhaustive Branch
branch(p, A, B)(x) = A(x) if p(x) else B(x)

# Default Safety
switch(k, cases, default)(x) always succeeds

# Guard Composition
guarded(p1 AND p2, A, fail) = guarded(p1, guarded(p2, A, fail), fail)
```

---

## Graph Composition

> *"Linear thought is a subset of graph thought."*

Extend pipelines to directed acyclic graphs (DAGs):

```
Graph Composition = Compose + Fix + Conditional
```

### Common Patterns

**Divide and Conquer**:
```python
graph = ThoughtGraph(root=problem)
graph.branch("problem", [solver_a, solver_b, solver_c])
graph.merge([...], aggregator)
```

**Beam Search**:
```python
async def beam_search(initial, generate, evaluate, beam_width=3, depth=3):
    candidates = [initial]
    for _ in range(depth):
        all_variants = await parallel([generate(c) for c in candidates])
        scored = [(v, await evaluate(v)) for v in flatten(all_variants)]
        candidates = sorted(scored, key=lambda x: x[1])[-beam_width:]
    return candidates[0]
```

**Iterative Refinement** (via Fix):
```python
await fix(
    transform=lambda x: refiner.invoke((x, await validator.invoke(x))),
    initial=initial,
    max_iterations=5
)
```

---

## The Curry-Howard Correspondence

> *To speak is to prove; to prove is to construct.*

We treat the **System Prompt** as a **Type Signature**. The agent's output must be a valid *inhabitant* of that type.

| Logic | Programming | Agents |
|-------|-------------|--------|
| Proposition | Type | Output Schema |
| Proof | Program | Agent Output |
| Modus Ponens | Function Application | Agent Invocation |
| ∧ (And) | Tuple/Product | Composite Output |
| ∨ (Or) | Union/Sum | Branching Output |
| → (Implication) | Function Type | Agent Signature |

**The Shift**: From "generate text that looks like X" to "construct a valid inhabitant of type X."

Type composition follows agent composition:
```python
# Agent composition
pipeline = agent_a >> agent_b >> agent_c
# Type composition (inferred)
# A: Input → Intermediate1
# B: Intermediate1 → Intermediate2
# C: Intermediate2 → Output
# Pipeline: Input → Output
```

---

## Context Management

> *"Context windows are finite. Context is heat. Cooling prevents degradation."*

### The Cooled Functor

```python
@dataclass
class Cooled(Generic[I, O]):
    inner: Agent[I, O]
    threshold: int = 4096
    radiator: Agent[str, str] | None = None

    async def invoke(self, input: I) -> O:
        tokens = self._estimate_tokens(input)
        if tokens > self.threshold:
            input = await self._compress(input)
        return await self.inner.invoke(input)
```

**Key Insight**: The inner agent doesn't know it received compressed data. It sees only a clean, short prompt.

### Composition with Cooling

```python
def with_context_management(agent: Agent[I, O], window_size: int = 4096) -> Agent[I, O]:
    return Cooled(inner=agent, threshold=window_size)
```

---

## Composition vs Operad

**Composition** is the binary operation: `f >> g`.

**Operads** make composition rules explicit and programmable. See `spec/agents/operads.md`.

| Concept | Composition | Operad |
|---------|-------------|--------|
| Focus | The `>>` operator | The grammar of operations |
| Laws | Identity, associativity | Domain-specific laws |
| Scope | Two agents at a time | N-ary operations |

---

## Anti-Patterns

1. **Breaking type compatibility**: Output doesn't match next input
2. **Cyclic graphs**: Must be DAGs for termination
3. **Unbounded recursion**: Always use `max_depth` with Fix
4. **Over-parallelization**: Respect resource limits
5. **Implicit state**: Hidden state prevents composition

---

## Implementation

```
impl/claude/agents/poly/compose.py   # Sequential composition
impl/claude/agents/c/parallel.py     # Parallel combinators
impl/claude/agents/c/conditional.py  # Conditional combinators
impl/claude/agents/c/graph.py        # Graph composition
```

---

## See Also

- [operads.md](operads.md) — Grammar of composition
- [primitives.md](primitives.md) — The 17 atomic agents
- [functors.md](functors.md) — Structure-preserving transformations
- [flux.md](flux.md) — Discrete → Continuous lifting

---

*"The river that knows its course flows without thinking."*
