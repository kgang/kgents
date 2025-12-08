# Performance Patterns for Composable Agents

## The Composition Overhead Problem

Every `f >> g` creates a `ComposedAgent(f, g)` wrapper. Deep pipelines accumulate wrappers:

```python
a >> b >> c >> d
# Creates: ComposedAgent(ComposedAgent(ComposedAgent(a, b), c), d)
```

**Impact:**
- Each wrapper adds memory overhead
- Deep pipelines → many intermediate objects
- Type information harder to track statically

**When it matters:**
- Hot loops composing agents dynamically
- Very deep pipelines (10+ stages)
- Memory-constrained environments

**When it doesn't matter:**
- Static pipelines defined once
- Shallow compositions (2-5 stages)
- Normal production workloads

---

## Solutions

### 1. Flattening (Implemented)

Extract atomic agents from composed pipeline for analysis:

```python
from bootstrap import flatten

pipeline = a >> b >> c >> d
parts = flatten(pipeline)  # [a, b, c, d]

# Use case: Debugging which stage failed
for i, agent in enumerate(parts):
    try:
        result = await agent.invoke(data)
    except Exception as e:
        print(f"Stage {i} ({agent.name}) failed: {e}")
        break
```

**Cost:** O(n) traversal of composition tree
**Benefit:** Visibility into composition structure

### 2. Id Optimization (Future)

The identity law states `Id >> f ≡ f`, but current implementation creates wrapper:

```python
# Current (impl/claude/bootstrap/id.py:53-69)
Id >> f  # Returns ComposedAgent(Id, f)

# Ideal (future optimization)
Id >> f  # Returns f directly (zero wrapper cost)
```

**Challenge:** Type system expects `ComposedAgent` return type
**Solution:** Return `f` directly; behavioral equivalence preserves law
**Benefit:** Eliminates wrappers in Id-heavy compositions

### 3. Batch Composition

Use `pipeline()` for multi-agent composition instead of chaining `>>`:

```python
from bootstrap import pipeline

# Chained: Creates nested ComposedAgent tree
p1 = a >> b >> c >> d  # Depth 3

# Batch: Single balanced tree
p2 = pipeline(a, b, c, d)  # Still depth 3, but cleaner

# Type safety note: pipeline() loses intermediate type info
# Prefer >> for type-checked composition, pipeline() for dynamic
```

**Trade-off:**
- `>>` operator: Type-safe, more wrappers
- `pipeline()`: Type-unsafe, same structure

**Recommendation:** Use `>>` for static pipelines, reserve `pipeline()` for dynamic agent lists.

---

## Parallel Composition

When agents are independent, compose them in parallel using concurrency primitives:

```python
import asyncio
from bootstrap import Agent

# Sequential (slow)
result_a = await agent_a.invoke(input_a)
result_b = await agent_b.invoke(input_b)
result_c = await agent_c.invoke(input_c)

# Parallel (fast)
results = await asyncio.gather(
    agent_a.invoke(input_a),
    agent_b.invoke(input_b),
    agent_c.invoke(input_c),
)
result_a, result_b, result_c = results
```

**When to use:**
- Agents operate on different data
- No dependencies between agents
- I/O-bound or CPU-bound operations

**When NOT to use:**
- Sequential dependencies (output of A → input of B)
- Shared mutable state (race conditions)
- Order matters for side effects

**Future:** Dedicated `Parallel` C-gent for explicit fan-out/fan-in (see `spec/c-gents/parallel.md`).

---

## Lazy Composition

Don't invoke until needed - separate composition from execution:

```python
# BAD: Eager - invokes immediately even if not needed
if should_process:
    result = await (parse >> validate >> transform).invoke(data)
else:
    result = None

# GOOD: Lazy - composes, then invokes only when ready
pipeline = parse >> validate >> transform
if should_process:
    result = await pipeline.invoke(data)
else:
    result = None

# BETTER: Conditional composition (future C-gent)
from bootstrap.conditional import when
result = await when(should_process)(pipeline).invoke(data)
```

**Benefit:** Avoid constructing expensive pipelines that won't be used
**Pattern:** Compose at module/class level, invoke at runtime

---

## Memoization Pattern

For pure agents (same input → same output), cache results:

```python
from functools import lru_cache
from bootstrap import Agent

class ExpensiveAgent(Agent[str, int]):
    @property
    def name(self) -> str:
        return "ExpensiveComputation"

    @lru_cache(maxsize=128)
    def _compute(self, input: str) -> int:
        # Expensive pure computation
        return sum(ord(c) for c in input)

    async def invoke(self, input: str) -> int:
        return self._compute(input)
```

**Trade-offs:**
- ✅ Speed: O(1) for cached inputs
- ❌ Memory: Stores up to `maxsize` results
- ❌ Purity requirement: Only works for deterministic agents

**Future:** Dedicated `Memo` D-gent for declarative memoization (see `spec/d-gents/cache.md`).

---

## Composition Depth Analysis

Use `depth()` to analyze composition complexity:

```python
from bootstrap import depth

simple = a >> b
complex = (a >> b) >> (c >> d)

print(depth(simple))   # 1
print(depth(complex))  # 2

# Rule of thumb: depth > 5 suggests refactoring opportunity
# Consider extracting sub-pipelines into named agents
```

**When depth matters:**
- Deep compositions harder to debug (which stage failed?)
- Type checker performance degrades with depth
- Stack traces become unwieldy

**Solution:** Extract sub-compositions into named agents:

```python
# Before: depth 6
mega_pipeline = a >> b >> c >> d >> e >> f >> g

# After: depth 2
preprocessing = a >> b >> c
processing = d >> e
postprocessing = f >> g
mega_pipeline = preprocessing >> processing >> postprocessing
```

---

## Benchmarking Composition

Measure composition overhead vs invoke overhead:

```python
import time
from bootstrap import Id, Agent

class NoOp(Agent[int, int]):
    @property
    def name(self) -> str:
        return "NoOp"

    async def invoke(self, input: int) -> int:
        return input

# Benchmark composition
start = time.perf_counter()
pipeline = NoOp()
for _ in range(1000):
    pipeline = pipeline >> NoOp()
composition_time = time.perf_counter() - start

# Benchmark invocation
start = time.perf_counter()
for _ in range(1000):
    await pipeline.invoke(42)
invocation_time = time.perf_counter() - start

print(f"Composition: {composition_time:.4f}s")
print(f"Invocation: {invocation_time:.4f}s")
# Typical: composition ~1ms, invocation ~10ms
# Ratio: Invoke is 10× more expensive than compose
```

**Insight:** Composition is cheap relative to invocation. Optimize `invoke()`, not `>>`.

---

## Best Practices

1. **Compose statically, invoke dynamically**
   - Define pipelines at module level
   - Invoke them in functions/methods

2. **Parallelize independent operations**
   - Use `asyncio.gather()` for fan-out
   - Judge and Contradict already do this internally

3. **Cache pure computations**
   - Use `lru_cache` for deterministic agents
   - Consider Ground caching pattern

4. **Flatten for debugging**
   - Extract atomic agents when troubleshooting
   - Inspect intermediate results

5. **Monitor depth**
   - Keep composition depth < 5 for readability
   - Extract sub-pipelines into named agents

6. **Profile before optimizing**
   - Measure actual bottlenecks
   - Composition overhead rarely matters in practice

---

## See Also

- [bootstrap.md](../bootstrap.md) - Performance section
- [composition.md](composition.md) - Category theory foundations
- [parallel.md](parallel.md) - Parallel composition agent (future)
- [conditional.md](conditional.md) - Conditional composition (future)
