# Integration & Ecosystem

**Status**: Phase 5 - Polish & Integration
**Related**: [jit.md](./jit.md), [lazy.md](./lazy.md), [stability.md](./stability.md)

---

## Overview

J-gents don't operate in isolation—they integrate deeply with the kgents ecosystem. This document specifies:

1. **Global Memoization** - Cache compiled agents by hash
2. **Cross-genus Composition** - How J-gents work with H/E/T/C-gents
3. **Bootstrap Integration** - J-gents as derived constructs
4. **Performance Optimization** - Lazy evaluation, caching, resource management

---

## 1. Global Memoization

### 1.1 The Caching Problem

JIT compilation is expensive. When a J-gent compiles an agent for intent `I` with context `C`, future J-gents encountering the same `(I, C)` should reuse the compiled agent.

### 1.2 Promise Hash

```python
from hashlib import sha256
from typing import Any
import json

def promise_hash(intent: str, context: dict[str, Any]) -> str:
    """
    Compute stable hash of (intent, context) tuple.

    Invariants:
    - Same (intent, context) → same hash
    - Different (intent, context) → different hash (high probability)
    - Order-independent for dict context
    """
    canonical = json.dumps(
        {"intent": intent, "context": context},
        sort_keys=True,
        ensure_ascii=True
    )
    return sha256(canonical.encode('utf-8')).hexdigest()
```

### 1.3 Agent Cache

```python
from typing import Optional, Type
from bootstrap.types import Agent

class AgentCache:
    """
    Global cache for JIT-compiled agents.

    Lifecycle:
    - Ephemeral agents cached by promise_hash
    - Cache persists for session duration
    - LRU eviction when size exceeds limit
    """

    def __init__(self, max_size: int = 100):
        self._cache: dict[str, Type[Agent]] = {}
        self._access_order: list[str] = []  # LRU tracking
        self.max_size = max_size

    def get(self, hash_key: str) -> Optional[Type[Agent]]:
        """Retrieve cached agent, update LRU."""
        if hash_key in self._cache:
            self._access_order.remove(hash_key)
            self._access_order.append(hash_key)
            return self._cache[hash_key]
        return None

    def put(self, hash_key: str, agent_class: Type[Agent]) -> None:
        """Store compiled agent, evict LRU if needed."""
        if hash_key in self._cache:
            # Update existing
            self._access_order.remove(hash_key)
        elif len(self._cache) >= self.max_size:
            # Evict least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

        self._cache[hash_key] = agent_class
        self._access_order.append(hash_key)

    def clear(self) -> None:
        """Clear all cached agents."""
        self._cache.clear()
        self._access_order.clear()

# Global singleton
_agent_cache = AgentCache()

def get_cached_agent(intent: str, context: dict) -> Optional[Type[Agent]]:
    """Retrieve cached agent for (intent, context)."""
    hash_key = promise_hash(intent, context)
    return _agent_cache.get(hash_key)

def cache_agent(intent: str, context: dict, agent_class: Type[Agent]) -> None:
    """Cache compiled agent for (intent, context)."""
    hash_key = promise_hash(intent, context)
    _agent_cache.put(hash_key, agent_class)
```

### 1.4 Integration with JGent

```python
# In jgent.py
async def _decompose_and_resolve(self, intent: str) -> T:
    # Check cache BEFORE JIT compilation
    cached = get_cached_agent(intent, self.context)
    if cached:
        return await cached().invoke(intent)

    # JIT compile new agent
    source = await MetaArchitect().invoke(intent)

    # ... chaosmonger checks ...

    # Compile
    agent_class = self._compile_agent(source)

    # Cache for future use
    cache_agent(intent, self.context, agent_class)

    return await agent_class().invoke(intent)
```

### 1.5 Cache Invalidation

Cache entries are invalidated when:
- Session ends (ephemeral agents don't persist across sessions)
- LRU eviction (cache size limit exceeded)
- Explicit `_agent_cache.clear()` call

**Principle**: Caching is transparent optimization—agents behave identically whether cached or freshly compiled.

---

## 2. Cross-Genus Composition

### 2.1 J-gents + H-gents (Hypothesis Testing)

H-gents generate hypotheses; J-gents can JIT-compile experiments to test them.

```python
# H-gent proposes hypothesis
hypothesis = await HypothesisAgent().invoke(observation)

# J-gent JIT-compiles experiment to test it
jgent = JGent[bool](ground=False)
result = await jgent.invoke(f"Test hypothesis: {hypothesis.statement}")

# Contradict/Sublate based on result
if result:
    synthesis = await Sublate().invoke((hypothesis, evidence))
else:
    contradiction = await Contradict().invoke((hypothesis, evidence))
```

**Flow**:
```
Observation → H-gent → Hypothesis → J-gent → Experiment → Judge → Synthesis
```

### 2.2 J-gents + T-gents (Testing)

T-gents attack code; J-gents generate defenders.

```python
# T-gent (saboteur) generates adversarial input
attack = await LatencyAgent().invoke(code)

# J-gent compiles defense
jgent = JGent[Agent](ground=IdentityAgent())
defender = await jgent.invoke(
    f"Create agent that handles: {attack.description}"
)

# Composition: defended_agent = defender >> original_agent
defended = defender >> original_agent
```

**Flow**:
```
Code → T-gent → Attack → J-gent → Defender → Composed Agent
```

### 2.4 J-gents + C-gents (Composition)

C-gents define composition laws; J-gents respect them when compiling.

```python
# JIT-compiled agents must be valid functors
class MetaArchitect:
    async def invoke(self, intent: str) -> str:
        # Generate agent source code
        source = await self._generate(intent)

        # Ensure compiled agent satisfies functor laws
        assert self._satisfies_identity_law(source)
        assert self._satisfies_composition_law(source)

        return source
```

**Invariant**: All JIT-compiled agents are morphisms and obey composition laws.

---

## 3. Bootstrap Integration

### 3.1 J-gents as Derived Constructs

J-gents are NOT new irreducibles—they're coordination patterns over existing bootstrap agents:

| J-gent Component | Bootstrap Derivation |
|------------------|---------------------|
| **RealityClassifier** | `Ground + Judge` (classify before act) |
| **Promise[T]** | `Fix + Ground` (deferred iteration with fallback) |
| **MetaArchitect** | `Autopoiesis` (active self-production) |
| **Chaosmonger** | `Judge` (algorithmic subset of evaluation) |
| **Test-Driven Reality** | `Contradict` (result vs. validation) |
| **JGent Coordinator** | `Fix + Compose` (iterate composition until stable) |

### 3.2 Example: Promise Derivation

```python
# Promise[T] = Fix + Ground
class Promise(Generic[T]):
    ground: T              # Ground: fallback value
    resolved: Optional[T]  # Fix: iterate until stable

    async def resolve(self) -> T:
        # Fix: Apply until converged
        result = await self.computation()

        # Contradict: Test vs. result
        if not await self.test(result):
            return self.ground  # Ground: collapse on failure

        self.resolved = result
        return result
```

**Principle**: J-gents introduce no new abstractions—they orchestrate existing ones.

---

## 4. Performance Optimization

### 4.1 Lazy Promise Expansion

Promises defer computation until explicitly resolved:

```python
# Create promise (no computation yet)
promise = Promise(
    intent="Parse 1GB log file",
    ground=ParsedLog.empty(),
    computation=lambda: parse_logs("huge.log")
)

# No work done until resolve() called
result = await promise.resolve()  # Computation happens HERE
```

**Benefit**: Only compute what's actually needed.

### 4.2 Parallel Promise Resolution

Independent promises can resolve concurrently:

```python
async def resolve_all(promises: list[Promise[T]]) -> list[T]:
    """Resolve promises in parallel where possible."""
    # Analyze dependency DAG
    independent = find_independent_promises(promises)
    dependent = find_dependent_promises(promises)

    # Resolve independent in parallel
    results = await asyncio.gather(*[p.resolve() for p in independent])

    # Resolve dependent sequentially
    for p in dependent:
        results.append(await p.resolve())

    return results
```

**Benefit**: Exploit parallelism in promise tree.

### 4.3 Entropy Budget as Resource Governor

Entropy budget prevents runaway recursion:

```python
# depth=0: budget=1.0 → full LLM calls, complex compilation
# depth=1: budget=0.5 → cached agents, simpler prompts
# depth=2: budget=0.33 → heuristic agents only
# depth=3: budget=0.25 → collapse to ground immediately
```

**Benefit**: Graceful degradation under resource pressure.

### 4.4 Chaosmonger as Early Filter

Chaosmonger rejects unstable code BEFORE expensive Judge evaluation:

```
Fast path: MetaArchitect → Chaosmonger → [unstable] → Ground (fast)
Slow path: MetaArchitect → Chaosmonger → [stable] → Judge → [accept] → Execute (slow)
```

**Benefit**: Catch obvious failures cheaply.

---

## 5. Future Enhancements

### 5.1 Persistent Agent Cache

Currently, cache is session-scoped. Future: persist to disk.

```python
class PersistentAgentCache(AgentCache):
    def __init__(self, cache_dir: Path):
        super().__init__()
        self.cache_dir = cache_dir

    def get(self, hash_key: str) -> Optional[Type[Agent]]:
        # Check memory cache first
        if cached := super().get(hash_key):
            return cached

        # Check disk cache
        cache_file = self.cache_dir / f"{hash_key}.py"
        if cache_file.exists():
            return self._load_from_disk(cache_file)

        return None
```

**Benefit**: Amortize compilation cost across sessions.

### 5.2 Compute Markets (Speculative)

Hypothetical: J-gents could bid on compilation tasks.

```python
class ComputeMarket:
    def bid(self, intent: str, budget: float) -> Promise[Agent]:
        """Bid computation resources for agent compilation."""
        ...
```

**Status**: NOT IMPLEMENTED. Interesting theoretical direction.

### 5.3 Distributed Promise Resolution

Hypothetical: Resolve promises across multiple machines.

```python
class DistributedJGent(JGent):
    async def invoke(self, intent: str) -> T:
        # Serialize promise tree
        serialized = self._serialize_promises(intent)

        # Distribute to worker nodes
        results = await self.cluster.map(resolve_promise, serialized)

        # Aggregate results
        return self._aggregate(results)
```

**Status**: NOT IMPLEMENTED. Would require distributed runtime.

---

## 6. Integration Checklist

### 6.1 Specification Complete

- [x] README.md - Core philosophy
- [x] reality.md - Reality classification
- [x] lazy.md - Promise abstraction
- [x] stability.md - Entropy budgets & Chaosmonger
- [x] jit.md - JIT compilation
- [x] integration.md - This document

### 6.2 Bootstrap Updates Required

- [ ] `spec/bootstrap.md` - Add "Reality is Trichotomous" idiom
- [ ] `spec/agents/functors.md` - Add Promise Functor
- [ ] `spec/anatomy.md` - Add Ephemeral Agents section

### 6.3 Implementation Complete

- [x] `agents/j/meta_architect.py` - JIT compiler
- [x] `agents/j/sandbox.py` - Safe execution
- [x] `agents/j/jgent.py` - Main coordinator
- [x] `test_j_gents_phase3.py` - Compilation tests (22 passing)
- [x] `test_j_gents_phase4.py` - Coordination tests (28 passing)

### 6.4 Integration Tests Needed

- [ ] J-gent + H-gent composition test
- [ ] J-gent + T-gent adversarial test
- [ ] Agent cache hit/miss behavior test
- [ ] Entropy budget enforcement test
- [ ] Promise DAG parallelism test

---

## 7. Success Criteria (Phase 5)

### Specification Quality
- [x] All J-gents specs complete (6 docs)
- [ ] Bootstrap modifications documented
- [ ] Cross-genus interactions specified
- [x] No new irreducibles introduced

### Implementation Quality
- [x] Core J-gent implementation passes mypy --strict
- [x] 50 tests passing (Phase 3 + Phase 4)
- [ ] Integration tests with H/E/T-gents
- [ ] Agent cache performance validated

### Documentation Quality
- [x] Philosophy clearly articulated
- [x] Relationship to bootstrap agents explicit
- [ ] Bootstrap.md updated with Idiom 7
- [ ] anatomy.md updated with ephemeral agents

---

## 8. Philosophical Notes

### On Memoization vs. Persistence

**Memoization** (yes): Cache compiled agents for session performance.
**Persistence** (no): Don't commit ephemeral agents to spec/impl.

Ephemeral agents are **tools**, not **specifications**. They emerge from need, serve their purpose, and dissolve. Caching is pragmatic optimization; persistence would be conceptual clutter.

### On Compute Markets

The compute market idea (from JAIgent research) is intriguing but premature. Current kgents are **single-machine, single-user tools**. Distributed computation introduces new concerns:

- Network partitions
- Byzantine agents
- Resource accounting
- Privacy/security

These belong in a **future distributed kgents spec** (hypothetical "R-gents" for Replicated?), not in core J-gents.

### On Laziness as Default

J-gents make laziness **explicit** through `Promise[T]`, but don't make it **mandatory**. Agents can still be eager if appropriate. The promise abstraction is opt-in.

**Guideline**: Use promises when:
- Computation is expensive
- Result may not be needed
- Parallelism opportunities exist

Use eager evaluation when:
- Computation is cheap
- Result always needed
- Sequential dependency exists

---

---

## 9. Alethic Projection Integration

### 9.1 The Missing Link

The original J-gent spec had MetaArchitect producing **source code**:

```python
MetaArchitect: (Intent, Context, Constraints) → SourceCode
```

**Enhanced design** — MetaArchitect produces **decorated agent class**:

```python
MetaArchitect: (Intent, Context, Constraints) → (Nucleus, Halo)

# Then Alethic Projection takes over
ProjectorRegistry.compile(nucleus, halo, target="local")
```

This means J-gent can:
1. Generate an ephemeral agent definition
2. Project it to **any target** based on context

### 9.2 Reality Classification → Projector Selection

Extend J-gent's reality classification to include **projection target selection**:

```python
class RealityClassifier:
    async def classify(self, intent: str, context: dict) -> Classification:
        reality = await self._classify_reality(intent)
        target = await self._select_target(reality, context)

        return Classification(
            reality=reality,      # DETERMINISTIC | PROBABILISTIC | CHAOTIC
            target=target,        # LOCAL | CLI | WASM | K8S | MARIMO
            entropy_budget=self._compute_budget(reality),
        )

    def _select_target(self, reality: Reality, context: dict) -> Target:
        match reality:
            case Reality.DETERMINISTIC:
                return Target.LOCAL  # Fast, in-process
            case Reality.PROBABILISTIC:
                if context.get("interactive"):
                    return Target.MARIMO  # Exploration
                elif context.get("production"):
                    return Target.K8S  # Scale
                else:
                    return Target.CLI  # Quick test
            case Reality.CHAOTIC:
                return Target.WASM  # Sandboxed, untrusted
```

### 9.3 The Agent Foundry Crown Jewel

The full synthesis lives in a new **Crown Jewel** that orchestrates J-gent + Alethic Projection:

```python
class AgentFoundry:
    """
    Crown Jewel: On-demand agent construction.

    Combines J-gent JIT intelligence with Alethic Projection
    to create and deploy ephemeral agents.
    """

    async def forge(
        self,
        intent: str,
        context: dict | None = None,
    ) -> CompiledAgent:
        # 1. Classify reality + select target
        classification = await self.classifier.classify(intent, context)

        # 2. Generate (Nucleus, Halo) via MetaArchitect
        agent_def = await self.architect.generate(intent, classification)

        # 3. Validate via Chaosmonger
        if not await self.chaosmonger.is_stable(agent_def):
            return self._fallback_agent(intent)

        # 4. Project to target
        projector = self.projectors.get(classification.target)
        return projector.compile(agent_def.cls)
```

**Full Specification**: See `spec/services/foundry.md`

### 9.4 Capability Inference

MetaArchitect can infer capabilities from intent:

```python
class CapabilityInferrer:
    """Infer Halo capabilities from intent analysis."""

    async def infer(self, intent: str) -> set[Capability]:
        capabilities = set()

        if "state" in intent or "remember" in intent:
            capabilities.add(Capability.Stateful(schema=dict))

        if "stream" in intent or "continuous" in intent:
            capabilities.add(Capability.Streamable(budget=5.0))

        if "observe" in intent or "metrics" in intent:
            capabilities.add(Capability.Observable(metrics=True))

        return capabilities
```

### 9.5 Sandbox Graduation

Chaotic reality agents start in WASM sandbox, graduate based on proven behavior:

```
Reality: CHAOTIC
    │
    ▼
WASMProjector (sandbox)
    │
    ├── Success × N → Confidence increases
    │
    ▼
LocalProjector (trusted)
    │
    ├── Success × M → Production ready
    │
    ▼
K8sProjector (deployed)
```

### 9.6 Integration Checklist (Alethic)

- [ ] MetaArchitect enhanced to produce `(Nucleus, Halo)` not `SourceCode`
- [ ] RealityClassifier extended with `_select_target()` method
- [ ] AgentFoundry Crown Jewel implemented (`services/foundry/`)
- [ ] AGENTESE nodes registered (`self.foundry.*`)
- [ ] WASMProjector implemented for chaotic reality sandbox

---

## Summary

**Phase 5 delivers**:

1. ✅ `integration.md` specification (this document)
2. ⏳ Bootstrap spec updates (bootstrap.md, functors.md, anatomy.md)
3. ⏳ Integration tests across agent genera
4. ⏳ Performance validation (caching, lazy evaluation)
5. **NEW**: ✅ Alethic Projection integration specified

J-gents are now **fully specified** and **functionally implemented**. The Alethic Projection synthesis completes the vision: **Classify reality, compile the mind, project anywhere, graduate to permanence.**

See also:
- `spec/services/foundry.md` — Agent Foundry Crown Jewel
- `spec/protocols/alethic-projection.md` — Projector targets and composition
