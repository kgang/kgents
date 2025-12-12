# Reference Implementation Guide

A practical guide for working with the kgents reference implementation in `impl/claude/agents/`.

---

## Quick Reference: Agent Genera

| Letter | Purpose | Key Files | Tests |
|--------|---------|-----------|-------|
| **a** | Skeleton architecture | `skeleton.py`, `creativity.py` | `test_skeleton.py` |
| **b** | Token economics, metering | `metered_functor.py`, `hypothesis.py` | `test_banker.py` |
| **c** | Category theory, composition | `functor.py`, `monad.py`, `parallel.py` | `test_c_integration.py` |
| **d** | State/Memory (Bicameral) | `bicameral.py`, `context_comonad.py`, `context_window.py`, `linearity.py`, `projector.py` | `test_bicameral.py`, `test_comonad.py` |
| **e** | Thermodynamic evolution | `cycle.py` | — |
| **f** | Factory pipeline | `factory.py`, `parser.py` | `test_factory_integration.py` |
| **g** | Grammar/Generation | `grammar.py` | — |
| **h** | Dialectics (Hegel/Jung) | — | — |
| **i** | Interface (SemanticField) | `semantic_field.py`, `terrarium_tui.py` | — |
| **j** | JIT compilation | `compiler.py`, `templates.py`, `t_integration.py` | — |
| **k** | Kent simulacra | `persona.py` | — |
| **l** | Semantic registry | `semantic_registry.py`, `server.py`, `Dockerfile` | — |
| **m** | Cartography (HoloMap) | `cartographer.py`, `attractors.py` | — |
| **n** | Narrative traces | `chronicle.py` | — |
| **o** | Observer functor | `observer.py`, `cortex_observer.py` | — |
| **p** | Parser/Persistence | — | — |
| **psi** | Metaphor engine | `engine.py`, `corpus.py`, `learning.py` | `test_engine.py` |
| **q** | Quartermaster (K8s exec) | `quartermaster.py` | — |
| **r** | Refinery (optimization) | `refinery.py`, `advanced.py`, `integrations.py` | `test_refinery.py` |
| **t** | Testing (Types I-V) | `trustgate.py`, mock, spy, judge, property | `test_trustgate.py` |
| **u** | Utility (tools, MCP) | `core.py`, `mcp.py`, `executor.py`, `orchestration.py`, `permissions.py` | `test_core.py`, `test_mcp.py` |
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

### Context Comonad (D-gent)

Store comonad for context window management:

```python
from agents.d.context_comonad import ContextComonad

comonad = ContextComonad(initial_state)

# Extract current value
current = comonad.extract()

# Extend with a function
extended = comonad.extend(lambda ctx: transform(ctx.extract()))

# Duplicate for nested context
duplicated = comonad.duplicate()
```

**Files**: `agents/d/context_comonad.py`, `agents/d/context_window.py`, `agents/d/linearity.py`, `agents/d/projector.py`

### TrustGate (T-gent)

Capability-based trust verification:

```python
from agents.t.trustgate import TrustGate, BypassToken

gate = TrustGate(ledger=capital_ledger)

# Check if agent has sufficient trust
if await gate.verify(agent_id, required_trust=100):
    # Proceed with operation
    pass

# Bypass for privileged operations (unforgeable capability)
token = BypassToken.create(reason="admin override")
await gate.bypass(token, operation)
```

**Files**: `agents/t/trustgate.py`

### U-gent Tools & MCP

Tool execution and MCP integration (migrated from T-gent):

```python
from agents.u.core import Tool, ToolRegistry
from agents.u.mcp import MCPClient
from agents.u.executor import ToolExecutor

# Register tools
registry = ToolRegistry()
registry.register(my_tool)

# Execute via MCP
client = MCPClient(server_url)
result = await client.call_tool("tool_name", args)

# Or via executor
executor = ToolExecutor(registry)
result = await executor.execute("tool_name", args)
```

**Files**: `agents/u/core.py`, `agents/u/mcp.py`, `agents/u/executor.py`, `agents/u/orchestration.py`

### Capital Accounting (shared)

Event-sourced trust ledger:

```python
from shared.capital import CapitalLedger, Transaction
from shared.costs import OperationCost
from shared.budget import Budget

ledger = CapitalLedger()

# Record transaction
ledger.record(Transaction(
    agent_id="agent-1",
    amount=100,
    operation="tool_call",
))

# Check balance (derived from events)
balance = ledger.balance("agent-1")

# Budget allocation
budget = Budget(total=1000)
budget.allocate("agent-1", 500)
```

**Files**: `shared/capital.py`, `shared/costs.py`, `shared/budget.py`

### Pataphysics (shared)

Exception semantics and imaginary solutions:

```python
from shared.pataphysics import PataphysicsSolver, ImaginarySolution

solver = PataphysicsSolver()

# Find solution in exception space
solution = solver.solve(
    problem="impossible constraint",
    constraints=["must be X", "must not be X"],
)
# Returns ImaginarySolution with clinamen (swerve) and syzygy (alignment)
```

**Files**: `shared/pataphysics.py`, `shared/melting.py`

### Wundt Curator (middleware)

Aesthetic filtering based on Wundt curve:

```python
from protocols.agentese.middleware.curator import WundtCurator

curator = WundtCurator(
    complexity_threshold=0.7,
    novelty_weight=0.5,
)

# Filter outputs by aesthetic value
filtered = await curator.curate(outputs)
```

**Files**: `protocols/agentese/middleware/curator.py`

### Concept Blending (contexts)

Fauconnier-Turner conceptual integration:

```python
from protocols.agentese.contexts.concept_blend import ConceptBlender

blender = ConceptBlender()

# Blend two input spaces
blend = await blender.blend(
    space1={"frame": "journey", "elements": [...]},
    space2={"frame": "argument", "elements": [...]},
)
# Returns emergent structure with novel inferences
```

**Files**: `protocols/agentese.contexts/concept_blend.py`

### Self Judgment (contexts)

Critic's loop for dialectical refinement:

```python
from protocols.agentese.contexts.self_judgment import CriticLoop

critic = CriticLoop()

# Refine through dialectical challenge
refined = await critic.refine(
    thesis=initial_output,
    criteria=["clarity", "correctness", "elegance"],
    max_iterations=3,
)
```

**Files**: `protocols/agentese/contexts/self_judgment.py`

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
| Mypy errors | Now strict mode (0 errors); run `uv run mypy .` |
| T-gent vs U-gent | T = Testing (Types I-V, TrustGate); U = Utility (tools, MCP, executor) |
| Dockerfiles | Use `__deps__.py` manifests; validate with `build_agent_image.py` |

---

## What's NOT Implemented (Spec Only)

These exist in `spec/` but not `impl/`:

| Agent | Spec Location | Status |
|-------|---------------|--------|
| **Ω-gent** (Somatic) | `spec/omega-gents/` | Spec complete, no impl |
| **Y-gent** (Topology) | `spec/y-gents/` | Partial |
| **I-gent v2.5** (Semantic Flux) | `plans/self/interface.md` | Spec complete, awaiting impl |
| Z-gent (Zettelkasten) | — | Specced in principles |

The Ω-gent morpheme system and `self.body.*` proprioception are fully specified but awaiting implementation.

The I-gent v2.5 "Semantic Flux" interface (density fields, flow arrows, glitch mechanic) is fully specified in `plans/self/interface.md` but not yet implemented.

---

## Architecture Philosophy

1. **Spec → Impl**: Read the spec first (`spec/<letter>-gents/`)
2. **Category Laws**: Composition must satisfy identity and associativity
3. **Orthogonality**: Optional features (metadata, protocols) don't break composition
4. **Minimal Output**: LLM agents return single outputs; composition happens at pipeline level
5. **Graceful Degradation**: Systems work (degraded) when deps are missing
