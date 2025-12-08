# Parallel Composition

Fan-out and fan-in patterns for concurrent agent execution.

---

## Definition

> **Parallel composition** enables concurrent execution of agents with results combined.

```
        ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
```

---

## Agents

### Parallel

Run multiple agents concurrently on the same input.

```
Parallel: List[Agent[A, B]] → Agent[A, List[B]]
```

**Semantics**:
- All agents receive the same input
- All agents run concurrently
- Returns list of all outputs (order preserved)
- Waits for all agents to complete

**Example**:
```python
analyze = parallel(
    sentiment_agent,
    topic_agent,
    entity_agent,
)
# Returns [sentiment, topics, entities]
```

---

### FanOut

Fan out to heterogeneous agents.

```
FanOut: (Agent[A, B], Agent[A, C], ...) → Agent[A, Tuple[B, C, ...]]
```

**Semantics**:
- Like Parallel but returns tuple for heterogeneous types
- Preserves type information for each branch

**Example**:
```python
process = fan_out(
    extract_text,    # → str
    extract_images,  # → List[Image]
    extract_meta,    # → Metadata
)
# Returns (str, List[Image], Metadata)
```

---

### Combine

Parallel execution with custom combination.

```
Combine: (List[Agent[A, B]], Combiner[List[B], C]) → Agent[A, C]
```

**Semantics**:
- Runs agents in parallel
- Applies combiner function to list of results
- Returns combined result

**Example**:
```python
vote = combine(
    agents=[model_a, model_b, model_c],
    combiner=lambda results: max(results, key=lambda r: r.confidence),
)
```

---

### Race

First-completed-wins pattern.

```
Race: List[Agent[A, B]] → Agent[A, B]
```

**Semantics**:
- All agents start concurrently
- Returns result from first agent to complete
- Cancels remaining agents
- Useful for redundancy or timeout patterns

**Example**:
```python
fast_lookup = race(
    cache_agent,
    database_agent,
    fallback_agent,
)
```

---

## Laws

### Order Preservation

Parallel preserves agent order in results:
```
parallel([A, B, C])(x) = [A(x), B(x), C(x)]
```

### Input Broadcast

All agents receive identical input:
```
∀ a ∈ parallel([agents]): a receives same input
```

### Race Non-Determinism

Race result depends on timing:
```
race([A, B])(x) ∈ {A(x), B(x)}
```

---

## Composition with Sequential

Parallel composes with sequential (>>):

```python
pipeline = (
    parse              # Sequential: parse input
    >> parallel(       # Parallel: analyze concurrently
        sentiment,
        entities,
        topics,
    )
    >> combine_results # Sequential: merge results
)
```

---

## Error Handling

### Parallel Errors

If any agent fails in Parallel:
- **Fail-fast**: First error cancels others (default)
- **Collect-all**: Wait for all, return errors with results

### Race Errors

If first-completed agent fails:
- Continue waiting for next completion
- Fail only if all agents fail

---

## See Also

- [composition.md](composition.md) - Base composition laws
- [conditional.md](conditional.md) - Branching patterns
- [monads.md](monads.md) - Error handling patterns
