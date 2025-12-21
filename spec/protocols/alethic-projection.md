# Alethic Projection Protocol

> *"Projectors compile agents to targets. Not rendering—compilation."*

**Status**: Canonical
**Implementation**: `impl/claude/system/projector/`
**Relates To**: [`projection.md`](projection.md) (UI), [`../a-gents/alethic.md`](../a-gents/alethic.md)

---

## The Two Projection Domains

kgents has **two distinct projection protocols** that serve different purposes:

| Protocol | Functor | Input | Output | Purpose |
|----------|---------|-------|--------|---------|
| **UI Projection** | `State → Renderable[T]` | Agent state | Visual representation | Display agent state to users |
| **Agent Compilation** | `(Nucleus, Halo) → Executable[T]` | Agent class + capabilities | Deployable artifact | Deploy agents to targets |

This document covers **Agent Compilation**. For UI Projection, see [`projection.md`](projection.md).

---

## The Agent Compilation Functor

```
Projector[T] : (Nucleus, Halo) → Executable[T]

Where:
- Nucleus = Agent[A, B] (pure logic—what the agent does)
- Halo = Set[Capability] (declarative metadata—what it could become)
- T = Target (Local, K8s, CLI, marimo, WASM)
- Executable[T] = Target-specific runnable artifact
```

### The Key Insight

Projectors read **compile-time metadata** (Halos) and produce **runtime artifacts**. The Halo is not runtime behavior—it's a declaration of potential that the projector realizes.

```python
# Halo is declaration (compile-time)
@Capability.Stateful(schema=MySchema)
@Capability.Observable(metrics=["latency"])
class MyAgent(Agent[str, str]):
    async def invoke(self, x: str) -> str:
        return x.upper()

# Projection is realization (produces runtime)
compiled = LocalProjector().compile(MyAgent)
# compiled is StatefulAdapter wrapping ObservableMixin wrapping MyAgent
```

---

## Target Registry

| Target | Projector | Output Type | Halo Mappings |
|--------|-----------|-------------|---------------|
| **Local** | `LocalProjector` | `Agent[A, B]` | Stateful→StatefulAdapter, Soulful→SoulfulAdapter, Streamable→FluxAgent |
| **K8s** | `K8sProjector` | `list[K8sResource]` | Stateful→StatefulSet+PVC, Soulful→Sidecar, Observable→ServiceMonitor |
| **CLI** | `CLIProjector` | `str` (script) | Generates shell-executable Python script |
| **Docker** | `DockerProjector` | `str` (Dockerfile) | Generates container build context |
| **marimo** | `MarimoProjector` | `str` (cell) | Generates notebook cell template |
| **WASM** | `WASMProjector` | `WASMModule` | Sandboxed browser-runnable agent (PRIORITY) |

---

## Capability → Target Mapping

### LocalProjector

The LocalProjector applies **functor wrappers** in canonical order:

```
Nucleus → D → K → TurnBased → Mirror → Flux
        (inner)                    (outer)
```

| Capability | Adapter | Effect |
|------------|---------|--------|
| `@Stateful` | `StatefulAdapter` | Provides `state` property, `update_state()` method |
| `@Soulful` | `SoulfulAdapter` | Provides `persona` property with K-gent governance |
| `@TurnBased` | `TurnBasedAdapter` | Records to TheWeave, CausalCone context, entropy tracking |
| `@Observable` | Marker | Pre-attachment flag for FluxAgent mirror |
| `@Streamable` | `FluxAgent` | Entropy budget, feedback loop, streaming iteration |

### K8sProjector

The K8sProjector generates **Kubernetes resources**:

| Capability | Resources | Notes |
|------------|-----------|-------|
| `@Stateful` | StatefulSet + PVC | Persistent storage, stable network identity |
| `@Soulful` | Sidecar container | K-gent persona governance via gRPC |
| `@Observable` | ServiceMonitor + metrics port | Prometheus integration |
| `@Streamable` | HorizontalPodAutoscaler | Auto-scaling based on entropy budget |
| `@TurnBased` | ConfigMap | Turn-gents protocol configuration |

### CLIProjector

The CLIProjector generates **shell-executable scripts**:

```python
class CLIProjector(Projector[str]):
    def compile(self, agent_cls: type[Agent], halo: Halo) -> str:
        return f'''#!/usr/bin/env python
from {agent_cls.__module__} import {agent_cls.__name__}
import asyncio, sys

if __name__ == "__main__":
    agent = {agent_cls.__name__}()
    input_data = sys.stdin.read() if not sys.stdin.isatty() else sys.argv[1]
    result = asyncio.run(agent.invoke(input_data))
    print(result)
'''
```

---

## Projector Laws

Projectors must satisfy three categorical laws:

### 1. Determinism

Same input produces same output:

```python
p = LocalProjector()
result1 = p.compile(MyAgent)
result2 = p.compile(MyAgent)
assert type(result1) == type(result2)  # Structural equality
```

### 2. Capability Preservation

Halo capabilities map to target features:

```python
@Capability.Stateful(schema=dict)
class MyAgent(Agent): ...

compiled = LocalProjector().compile(MyAgent)
assert hasattr(compiled, 'state')        # StatefulAdapter provides this
assert hasattr(compiled, 'update_state')  # And this
```

### 3. Empty Halo Identity

Agent with no capabilities projects to itself:

```python
class PlainAgent(Agent): ...

compiled = LocalProjector().compile(PlainAgent)
assert isinstance(compiled, PlainAgent)  # No wrappers added
```

---

## The Alethic Isomorphism

The key guarantee:

```
Same Halo + LocalProjector  → Runnable Python agent
Same Halo + K8sProjector    → K8s manifests

Both produce SEMANTICALLY EQUIVALENT agents.
```

The agent's behavior is identical regardless of deployment target. Only the infrastructure differs.

### Verification

```python
# Compile same agent to different targets
local = LocalProjector().compile(MyAgent)
k8s = K8sProjector().compile(MyAgent)

# Same capabilities realized differently
assert local.config.entropy_budget == 5.0  # From @Streamable(budget=5.0)

k8s_hpa = next(r for r in k8s if r.kind == "HorizontalPodAutoscaler")
assert k8s_hpa.spec["maxReplicas"] == 10  # budget * 2, capped at 10
```

---

## Implementation

### Projector Protocol

```python
class Projector(ABC, Generic[Target]):
    """Categorical compiler: (Nucleus, Halo) → Executable[Target]."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable projector name."""
        ...

    @abstractmethod
    def compile(self, agent_cls: type[Agent[Any, Any]]) -> Target:
        """Compile agent class to target artifact."""
        ...

    @abstractmethod
    def supports(self, capability: type[CapabilityBase]) -> bool:
        """Check if projector supports a capability."""
        ...
```

### Error Hierarchy

```python
ProjectorError                    # Base
├── UnsupportedCapabilityError    # Projector doesn't support capability
├── CompilationError              # Failed to compile agent
└── InvalidNameError              # RFC 1123 name validation failure
```

---

## CLI Integration

### Current Commands

```bash
kg a manifest MyAgent              # K8s YAML (default)
kg a run MyAgent --input "hello"   # Run locally
```

### Enhanced Commands (Target)

```bash
kg a manifest MyAgent --target k8s      # K8s YAML
kg a manifest MyAgent --target docker   # Dockerfile
kg a manifest MyAgent --target cli      # Shell script
kg a manifest MyAgent --target marimo   # Notebook cell

kg a run MyAgent --input "hello"        # Run locally
kg a run MyAgent --stream               # SSE streaming mode
kg a run MyAgent --trace                # Show state transitions

kg a inspect MyAgent                    # Show Halo + capabilities
kg a inspect MyAgent --polynomial       # Show state machine diagram

kg a validate MyAgent                   # Verify Halo consistency
```

---

## Connection to UI Projection

The two projection domains complement each other:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   [Define]         [Compile]            [Run]           [Display]   │
│                                                                     │
│   Agent[A,B]  ──▶  Projector[T]  ──▶  Executable  ──▶  State  ──▶  │
│   + @Halo                               .invoke()                   │
│                                                                     │
│                    ▲                                   │            │
│                    │                                   ▼            │
│              Agent Compilation                   UI Projection      │
│         (Nucleus,Halo) → Executable[T]        State → Renderable[T] │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Agent Compilation** produces the executable.
**UI Projection** displays the executable's state.

Both are **natural transformations** preserving structure, but operating on different domains.

---

## Extended Projector Targets

The following projectors extend the base registry to support additional deployment targets.

### DockerProjector

**Purpose**: Generate Dockerfile for containerized agent deployment.

```python
class DockerProjector(Projector[str]):
    """Compile agent to Dockerfile."""

    base_image: str = "python:3.12-slim"

    def compile(self, agent_cls: type[Agent]) -> str:
        return f'''
FROM {self.base_image}

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY {agent_cls.__module__.replace('.', '/')} /app/

# Health check endpoint
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", "8080"]
'''
```

| Capability | Docker Feature |
|------------|----------------|
| `@Stateful` | Volume mount for state persistence |
| `@Soulful` | K-gent sidecar container in compose |
| `@Observable` | Prometheus metrics endpoint exposed |
| `@Streamable` | Streaming-optimized entrypoint |

### MarimoProjector

**Purpose**: Generate marimo notebook cells for interactive agent exploration.

**Why This Matters**:
- Exploratory development of new agents
- Teaching/documentation via executable notebooks
- J-gent MetaArchitect output can be immediately explored in marimo

```python
class MarimoProjector(Projector[str]):
    """Compile agent to marimo notebook cell."""

    def compile(self, agent_cls: type[Agent]) -> str:
        return f'''
import marimo as mo
from {agent_cls.__module__} import {agent_cls.__name__}
from system.projector import LocalProjector

# Compile agent with full capabilities
agent = LocalProjector().compile({agent_cls.__name__})

# Interactive input
input_widget = mo.ui.text(placeholder="Enter input...")

# Agent execution cell
@mo.cell
async def run_agent():
    if input_widget.value:
        result = await agent.invoke(input_widget.value)
        return mo.md(f"**Result**: {{result}}")
    return mo.md("Enter input above")
'''
```

| Capability | marimo Feature |
|------------|----------------|
| `@Stateful` | `mo.json()` state inspector widget |
| `@Soulful` | Persona banner + conversation mode |
| `@Observable` | `mo.stat()` metrics dashboard |
| `@Streamable` | Streaming output cell with live updates |
| `@TurnBased` | Turn history visualization |

### WASMProjector (PRIORITY)

**Purpose**: Compile agents to WebAssembly for sandboxed browser execution.

**Why This Matters**:
- Zero-trust execution environment for JIT-compiled agents
- J-gent chaotic reality classification → run in WASM sandbox, not on server
- Servo work provides the foundation — browser engine primitives are available
- Enables client-side agent execution without server round-trips
- Critical for offline-capable agents and edge deployment

```python
class WASMProjector(Projector[WASMModule]):
    """Compile agent to WebAssembly module."""

    def compile(self, agent_cls: type[Agent]) -> WASMModule:
        # 1. Generate Python source
        source = self._generate_minimal_source(agent_cls)

        # 2. Compile via Pyodide or RustPython
        wasm = self._compile_to_wasm(source)

        # 3. Add capability stubs
        if self._has_cap("Stateful"):
            wasm = self._add_indexeddb_state(wasm)

        if self._has_cap("Observable"):
            wasm = self._add_performance_api(wasm)

        return wasm
```

| Capability | WASM Feature |
|------------|--------------|
| `@Stateful` | IndexedDB persistence |
| `@Observable` | Performance API + console.time |
| `@Streamable` | ReadableStream output |
| `@Soulful` | N/A (no K-gent in browser) |

**Use Case**: Chaosmonger runs JIT agent in WASM sandbox before promoting to LocalProjector.

---

## Projector Composition

Projectors compose like agents — this is **required**, not aspirational:

### Sequential Composition (>>)

```python
# Docker → K8s (build image, then deploy)
docker_k8s = DockerProjector() >> K8sProjector()

# Result: Dockerfile + K8s Deployment referencing the image
```

When composed sequentially, the downstream projector receives the upstream's output:

```python
class K8sProjector(Projector[list[K8sResource]]):
    def compile(
        self,
        agent_cls: type[Agent],
        docker_artifact: DockerArtifact | None = None,  # From upstream
    ) -> list[K8sResource]:
        resources = self._base_resources(agent_cls)

        # If composed with DockerProjector, use its image tag
        if docker_artifact:
            for r in resources:
                if r.kind in ("Deployment", "StatefulSet"):
                    r.spec["template"]["spec"]["containers"][0]["image"] = (
                        docker_artifact.image_tag
                    )

        return resources
```

### Parallel Composition (//)

```python
# Multi-target: deploy everywhere simultaneously
multi_target = LocalProjector() // K8sProjector() // CLIProjector()

# Result: (LocalAgent, [K8sResource], str)
results = multi_target.compile(MyAgent)
```

This enables:
- Local development with `LocalProjector`
- CLI testing with `CLIProjector`
- Production deployment with `K8sProjector`
- Documentation with `MarimoProjector`

### Composition Laws

Projector composition must satisfy:

| Law | Requirement |
|-----|-------------|
| **Associativity** | `(A >> B) >> C ≡ A >> (B >> C)` |
| **Identity** | `Id >> P ≡ P ≡ P >> Id` |
| **Parallel Commutativity** | `A // B ≡ B // A` (order of outputs changes) |

---

## Foundry Integration

The Agent Foundry service (see `spec/services/foundry.md`) uses projectors as its compilation backend:

```python
class AgentFoundry:
    async def forge(self, intent: str, context: dict) -> CompiledAgent:
        # 1. Reality classification determines target
        classification = await self.classifier.classify(intent, context)

        # 2. MetaArchitect generates (Nucleus, Halo)
        agent_def = await self.architect.generate(intent)

        # 3. Select projector based on classification
        projector = self.projectors.get(classification.target)

        # 4. Compile
        return projector.compile(agent_def.cls)
```

The Reality → Target mapping:

| Reality | Target | Rationale |
|---------|--------|-----------|
| DETERMINISTIC | LOCAL | Fast, in-process |
| PROBABILISTIC + interactive | MARIMO | Exploration |
| PROBABILISTIC + production | K8S | Scale |
| CHAOTIC | WASM | Sandboxed, untrusted |

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| Runtime Halo checks | Capabilities are compile-time | Read Halo once in `compile()` |
| Implicit wrapping order | Non-deterministic behavior | Explicit canonical order |
| Target-specific nucleus code | Breaks portability | Pure nucleus, let projector adapt |
| Skipping unsupported capabilities | Silent failure | Raise `UnsupportedCapabilityError` |

---

## Test Requirements

### Law Tests

```python
def test_determinism():
    """Same input → same output."""
    p = LocalProjector()
    r1, r2 = p.compile(MyAgent), p.compile(MyAgent)
    assert type(r1) == type(r2)

def test_capability_preservation():
    """Halo capabilities map to features."""
    @Capability.Stateful(schema=dict)
    class A(Agent): ...

    compiled = LocalProjector().compile(A)
    assert hasattr(compiled, 'state')

def test_empty_halo_identity():
    """Empty Halo produces minimal agent."""
    class PlainAgent(Agent): ...

    compiled = LocalProjector().compile(PlainAgent)
    assert isinstance(compiled, PlainAgent)
```

### Property-Based Tests

```python
from hypothesis import given, strategies as st

@given(capabilities=st.lists(st.sampled_from([
    StatefulCapability(schema=dict),
    SoulfulCapability(persona="test"),
    ObservableCapability(metrics=True),
    StreamableCapability(budget=5.0),
])))
def test_any_halo_compiles(capabilities):
    """Any valid Halo can be projected."""
    @apply_capabilities(capabilities)
    class DynamicAgent(Agent): ...

    result = LocalProjector().compile(DynamicAgent)
    assert result is not None
```

---

## Implementation Reference

- Base protocol: `impl/claude/system/projector/base.py`
- Local projector: `impl/claude/system/projector/local.py`
- K8s projector: `impl/claude/system/projector/k8s.py`
- K8s database: `impl/claude/system/projector/k8s_database.py`
- Halo definitions: `impl/claude/agents/a/halo.py`
- Tests: `impl/claude/system/projector/_tests/`

---

*"The Projector is the bridge between potential and reality."*
