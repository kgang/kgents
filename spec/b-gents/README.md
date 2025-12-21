# B-gent: The Banker

> *Intelligence is infinite; Compute is finite.*

---

## The Core Insight

**B-gent = Banker = Resource Management**

The Metered Functor transforms any agent into an economic agent:

```
Metered: Agent[A, B] → Agent[A, Receipt[B]]
```

Every invocation becomes a transaction. Every token is tracked. Every result has a price tag.

---

## The Banker Archetype

B-gent deals with **resource-constrained systems**—the thermodynamics of thought:

| Aspect | Description |
|--------|-------------|
| **Resource** | Tokens, compute, time, memory |
| **Conservation** | Value flows, never appears from nothing |
| **Selection** | Efficiency filters what survives |
| **Metabolism** | Consumption, transformation, waste |

### Three Currencies

1. **Gas**: What you spend (tokens, time, cost)
2. **Impact**: What you create (value units, tiered by outcome)
3. **RoC**: Return on Compute = Impact / Gas

When RoC drops below 0.5, the Banker warns of bankruptcy.

---

## Key Concepts

### The Metered Functor

Every agent can be wrapped in metering:

```python
metered_agent = Metered(agent)
receipt = await metered_agent.invoke(input)
# receipt.value = result
# receipt.gas = what was spent
# receipt.impact = what was created
# receipt.roc = efficiency
```

### Linear Logic

Tokens are **linear types**—consumed, not copied:

```
Classical: A → (A → B → C)    // A can be used twice
Linear:    A ⊸ (A ⊸ B) ⊸ C   // Each A used exactly once
```

### Hydraulic Economics

- **Token Bucket**: Refills over time (rate limiting)
- **Sinking Fund**: 1% tax for emergency reserves
- **Token Futures**: Reserve capacity for multi-step jobs

---

## Specification

| Document | Description |
|----------|-------------|
| [banker.md](banker.md) | Full Banker specification |

---

## Design Principles

### 1. Conservation Awareness

B-gents MUST respect conservation laws:
- Tokens circulate but total is conserved
- Cannot spend more than allocated

### 2. Selection Pressure

B-gents MUST implement selection:
- Allocations must be efficient
- Low RoC triggers warnings/termination

### 3. Metabolic Honesty

B-gents MUST track consumption:
- What tokens were consumed?
- What value was created?

---

## Anti-Patterns

- **Unbounded execution**: Always meter, even for "small" tasks
- **Trust without verify**: Agents estimate, bank audits actual usage
- **Single currency**: Consider multiple resource types
- **No reserve**: Sinking Fund prevents cascading failures

---

## Historical Note

Earlier versions of B-gent included "Bio" (scientific reasoning) alongside "Banker" (economics). The "Bio" concepts (hypothesis generation, scientific companions) were aspirational but not implemented, and they didn't fit the core purpose of resource management.

**Design Decision** (2025-12): B-gent now focuses solely on the Banker archetype. Scientific reasoning is not a resource management problem—it's a composition problem (derivable from Compose + Judge per bootstrap.md). The SciAgents paper (cited in heritage.md) inspired the original Bio concepts, but the right place for scientific reasoning is domain-specific agents built on the categorical foundation, not a separate B-gent facet.

---

## See Also

- [banker.md](banker.md) - Full Banker specification
- [../bootstrap.md](../bootstrap.md) - Entropy Budget (related constraint)
- [../o-gents/README.md](../o-gents/README.md) - Observability economics
- [../principles.md](../principles.md) - Conservation as design principle
- [../heritage.md](../heritage.md) - SciAgents and Voyager citations
