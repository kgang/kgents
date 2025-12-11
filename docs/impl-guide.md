# Reference Implementation Guide

A practical guide for working with the kgents reference implementation in `impl/claude/agents/`.

---

## Quick Reference: Agent Genera

| Letter | Purpose | Key Files | Tests |
|--------|---------|-----------|-------|
| **a** | Skeleton architecture | `skeleton.py`, `creativity.py` | `test_skeleton.py` |
| **b** | Token economics, metering | `metered_functor.py`, `hypothesis.py` | `test_banker.py` |
| **c** | Category theory, composition | `functor.py`, `monad.py`, `parallel.py` | `test_c_integration.py` |
| **d** | State/Memory (Bicameral) | `bicameral.py`, `lens.py`, `symbiont.py` | `test_bicameral.py` |
| **e** | Thermodynamic evolution | `cycle.py` | — |
| **f** | Factory pipeline | `factory.py`, `parser.py` | `test_factory_integration.py` |
| **g** | Grammar/Generation | `grammar.py` | — |
| **h** | Dialectics (Hegel/Jung) | — | — |
| **i** | Interface (SemanticField) | `semantic_field.py` | — |
| **j** | JIT compilation | `compiler.py`, `templates.py` | — |
| **k** | Kent simulacra | `persona.py` | — |
| **l** | Semantic registry | `semantic_registry.py` | — |
| **m** | Cartography (HoloMap) | `cartographer.py`, `attractors.py` | — |
| **n** | Narrative traces | `chronicle.py` | — |
| **o** | Observer functor | `observer.py`, `cortex_observer.py` | — |
| **p** | Parser/Persistence | — | — |
| **psi** | Metaphor engine | `engine.py`, `corpus.py`, `learning.py` | `test_engine.py` |
| **q** | Quartermaster (K8s exec) | `quartermaster.py` | — |
| **r** | Refinery (optimization) | `refinery.py`, `advanced.py` | `test_refinery.py` |
| **t** | Tool use, MCP | `tool.py`, `mcp_client.py`, `permissions.py` | `test_mcp.py` |
| **w** | Wire protocol, bus | `bus.py`, `interceptors.py` | — |

---

## Core Patterns

### 1. Agent Creation

Every agent follows the `Agent[A, B]` protocol from `bootstrap/types.py`:

```python
from bootstrap.types import Agent

class MyAgent(Agent[InputType, OutputType]):
    async def invoke(self, input: InputType) -> OutputType:
        # Agent logic
        return result

    @property
    def name(self) -> str:
        return "my-agent"
```

### 2. Composition via >>

Agents compose linearly (C-gent pattern):

```python
from agents.c.functor import compose

pipeline = agent_a >> agent_b >> agent_c
result = await pipeline.invoke(input)
```

### 3. The Symbiont Pattern (D-gent)

Separate pure logic from stateful memory:

```python
from agents.d.symbiont import Symbiont

# Pure agent + D-gent state = Symbiont
symbiont = Symbiont(
    logic=pure_agent,
    memory=d_gent_instance,
)
```

### 4. Observation (O-gent)

Wrap agents with observation without affecting behavior:

```python
from agents.o.observer import ObserverFunctor

observed = ObserverFunctor(my_agent, callbacks=[on_before, on_after])
# observed.invoke() behaves identically but emits observations
```

### 5. Metering (B-gent)

Apply token economics:

```python
from agents.b.metered_functor import MeteredFunctor

metered = MeteredFunctor(my_agent, budget=1000)
# Raises BudgetExhausted if cost exceeds budget
```

---

## Key Subsystems

### Bicameral Memory (D-gent)

The memory system uses a split-brain architecture:

```python
from agents.d.bicameral import create_bicameral_memory

bicameral = create_bicameral_memory(
    relational=sqlite_store,    # Left brain: structured
    vector=vector_store,        # Right brain: semantic
    embedder=embed_fn,
    auto_heal_ghosts=True,      # Reconcile orphan refs
)

results = await bicameral.recall("query")
```

**Files**: `agents/d/bicameral.py`, `agents/d/lens.py`

### Synapse (Active Inference)

Routes memories based on surprise:

```python
from instance_db.synapse import Synapse, SynapseConfig

synapse = Synapse(
    store=memory_store,
    config=SynapseConfig(
        surprise_threshold=0.5,   # Fast path
        flashbulb_threshold=0.9,  # Immediate storage
    ),
)

await synapse.fire(signal)  # Auto-routes to appropriate path
```

**Files**: `instance_db/synapse.py`

### Semantic Field (Stigmergy)

Agents communicate via pheromone-like signals:

```python
from agents.i.semantic_field import create_semantic_field, PheromoneType

field = create_semantic_field()

# Emit signal
field.emit(PheromoneType.METAPHOR, data={"source": "A", "target": "B"})

# Sense signals
signals = field.sense(PheromoneType.METAPHOR, threshold=0.5)
```

**Files**: `agents/i/semantic_field.py`

### M-gent Cartography

Memory-as-orientation with HoloMap:

```python
from agents.m.cartographer import create_cartographer, Resolution

cartographer = create_cartographer(vector_search, trace_store)
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)
# Returns: landmarks, desire_lines, voids, horizon
```

**Files**: `agents/m/cartographer.py`, `agents/m/attractors.py`

### Ψ-gent Metaphor Engine

Six-stage reasoning pipeline:

```python
from agents.psi.engine import MetaphorEngine
from agents.psi.types import Problem

engine = MetaphorEngine()
solution = engine.solve_problem(
    Problem(
        id="prob-1",
        description="The API is slow",
        domain="performance",
        constraints=["must not break existing clients"],
    )
)
# Returns: Solution with metaphor_solution, translated_answer, distortion
```

**Stages**: RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY

**Files**: `agents/psi/engine.py`, `agents/psi/corpus.py`, `agents/psi/learning.py`

### R-gent Refinery

Prompt optimization via teleprompters:

```python
from agents.r.refinery import RefineryAgent
from agents.r.types import Signature, OptimizationBudget

refinery = RefineryAgent(teleprompter=my_teleprompter)
optimized = await refinery.refine(
    agent=target_agent,
    signature=Signature(...),
    examples=training_examples,
    budget=OptimizationBudget(max_iterations=10),
)
```

**Files**: `agents/r/refinery.py`, `agents/r/advanced.py`, `agents/r/dspy_backend.py`

### W-gent Interceptors

Pipeline: Safety(50) → Metering(100) → Telemetry(200) → Persona(300)

```python
from agents.w.interceptors import InterceptorPipeline, SafetyInterceptor

pipeline = InterceptorPipeline([
    SafetyInterceptor(priority=50),
    MeteringInterceptor(priority=100),
])

# Apply to agent invocations
result = await pipeline.intercept(agent, input)
```

**Files**: `agents/w/interceptors.py`, `agents/w/bus.py`

---

## Integration Patterns

### Cross-Agent Integration Files

When agents need to collaborate, use `*_integration.py` files:

- `agents/b/egent_integration.py` - B-gent + E-gent
- `agents/b/robin_integration.py` - B-gent redistribution
- `agents/c/j_integration.py` - C-gent + J-gent
- `agents/psi/integrations.py` - Ψ-gent bridges

### Foundational Agents

These can be imported anywhere without circular deps:

- `shared` - Common utilities
- `a` - Skeleton types
- `d` - State primitives
- `l` - Registry
- `c` - Composition

### SemanticField for Decoupling

When direct imports would create cycles, use pheromones:

```python
# In Agent A (emitter)
field.emit(PheromoneType.OPPORTUNITY, {"budget": 1000})

# In Agent B (sensor) - no import of A needed
opportunities = field.sense(PheromoneType.OPPORTUNITY)
```

---

## CLI Entry Points

**K-Terrarium** (Kubernetes):
```bash
kgents infra init        # Create cluster
kgents infra status      # Show state
kgents infra apply <agent>  # Deploy agent
kgents dev <agent>       # Live reload
```

**DevEx**:
```bash
kgents status            # Cortex health
kgents dream             # LucidDreamer briefing
kgents map               # HoloMap visualization
kgents signal            # SemanticField state
kgents ghost             # Project to .kgents/ghost/
```

---

## Testing Conventions

- Tests live in `_tests/` subdirectories
- Slow tests marked with `@pytest.mark.slow`
- External deps (Redis, SQL) gracefully skipped

```bash
pytest -m "not slow" -q              # Fast tests
pytest impl/claude/agents/d/ -v      # Specific agent
```

---

## Common Gotchas

| Issue | Fix |
|-------|-----|
| Python 3.12 syntax | Use `Generic[A]` + `TypeVar`, not `class Foo[A]:` |
| Cross-agent imports | Use `*_integration.py` files or SemanticField |
| Forward refs | `from __future__ import annotations` + `TYPE_CHECKING` |
| Mypy errors | Check `mypy-baseline.txt`, run filter |

---

## What's NOT Implemented (Spec Only)

These exist in `spec/` but not `impl/`:

| Agent | Spec Location | Status |
|-------|---------------|--------|
| **Ω-gent** (Somatic) | `spec/omega-gents/` | Spec complete, no impl |
| **Y-gent** (Topology) | `spec/y-gents/` | Partial |
| Z-gent (Zettelkasten) | — | Specced in principles |

The Ω-gent morpheme system and `self.body.*` proprioception are fully specified but awaiting implementation.

---

## Architecture Philosophy

1. **Spec → Impl**: Read the spec first (`spec/<letter>-gents/`)
2. **Category Laws**: Composition must satisfy identity and associativity
3. **Orthogonality**: Optional features (metadata, protocols) don't break composition
4. **Minimal Output**: LLM agents return single outputs; composition happens at pipeline level
5. **Graceful Degradation**: Systems work (degraded) when deps are missing
