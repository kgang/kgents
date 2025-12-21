# A-gents: Alethic Architecture

> *"A" for Architecture. A for Aletheia. A for the foundation upon which all agents stand.*

---

## Why "Alethic"?

From Greek *aletheia* (ἀλήθεια)—truth, disclosure, unconcealment. In kgents:

1. **Truth-Preserving**: Category laws (identity, associativity) are verified, not assumed
2. **Self-Disclosing**: Agents describe themselves through Halos
3. **Ground Reality**: Primitives like `GROUND`, `JUDGE`, `SUBLATE` operate on claims

A-gent is not a single agent—it's the **architectural foundation** that makes agents truthful.

---

## The Three Pillars

### 1. Skeleton (core/skeleton.md)

The minimal contract every agent MUST satisfy:

```yaml
identity:
  name: string
  genus: string
  version: string
  purpose: string

interface:
  input: type
  output: type
  errors: [error-spec]

behavior:
  guarantees: [what-it-promises]
  constraints: [what-it-won't-do]
```

Every kgents agent inherits this structure, explicitly or implicitly.

### 2. Halo Capabilities

Declarative metadata that describes what an agent *could become*:

```python
@Capability.Stateful(schema=MyMemory)
@Capability.Soulful(persona="Kent")
class MyAgent(Agent[str, str]):
    async def invoke(self, input: str) -> str:
        return f"Hello, {input}"
```

The Halo is the potentiality; the Projector actualizes it.

### 3. Archetypes

Pre-packaged Halos for common patterns:

| Archetype | Halo | Use Case |
|-----------|------|----------|
| **Kappa** | Stateless, Replicated, Horizontal | Microservices |
| **Lambda** | Stateless, Event-triggered | Functions |
| **Delta** | Stateful, Persistent, Durable | Actors |

```python
class MyService(Kappa[Request, Response]):
    async def invoke(self, req: Request) -> Response:
        return process(req)
```

---

## The Alethic Agent

A polynomial state machine for truth-seeking:

```
GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING
```

This isn't just a fancy state machine—it composes the primitive polynomial agents (`GROUND`, `JUDGE`, `SUBLATE`) to perform structured reasoning.

```python
from agents.a import AlethicAgent, Query

agent = AlethicAgent()
response = await agent.reason(Query(claim="The sky is blue"))
print(response.verdict.accepted)  # True/False
print(response.reasoning_trace)   # How we got there
```

---

## The Functor Protocol

Universal lifting with law verification:

```python
@UniversalFunctor
class MyFunctor:
    @classmethod
    def lift(cls, f: Callable[[A], B]) -> Callable[[F[A]], F[B]]:
        ...
```

Functors are verified against categorical laws at runtime:
- **Identity**: `fmap(id) == id`
- **Composition**: `fmap(f . g) == fmap(f) . fmap(g)`

---

## The Nucleus-Halo-Projector Triad

This is the core insight of A-gent:

```
┌─────────────────────────────────────────────────────────────────────┐
│  NUCLEUS         Pure Agent[A, B] logic (what it does)              │
├─────────────────────────────────────────────────────────────────────┤
│  HALO            @Capability.* decorators (what it could become)    │
├─────────────────────────────────────────────────────────────────────┤
│  PROJECTOR       Target-specific compilation (how it manifests)     │
└─────────────────────────────────────────────────────────────────────┘
```

The same agent can be projected to:
- **K8sProjector** → Kubernetes manifests
- **LocalProjector** → In-process execution
- **CLIProjector** → Command-line interface

---

## CLI Interface

```bash
kg a                       # Show help
kg a inspect MyAgent       # Show Halo + Nucleus details
kg a manifest MyAgent      # K8sProjector → YAML output
kg a run MyAgent           # LocalProjector → run agent
kg a list                  # List registered agents
kg a new MyAgent           # Scaffold new agent
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `skeleton.py` | Minimal agent contract, `BootstrapWitness` |
| `halo.py` | `@Capability.*` decorators |
| `archetypes.py` | `Kappa`, `Lambda`, `Delta` |
| `alethic.py` | `AlethicAgent` polynomial |
| `functor.py` | `UniversalFunctor` protocol |
| `quick.py` | `@agent` decorator for rapid creation |

---

## See Also

- [core/skeleton.md](core/skeleton.md) — The minimal agent structure
- [alethic.md](alethic.md) — Alethic architecture deep dive
- [spec/architecture/polyfunctor.md](../architecture/polyfunctor.md) — Polynomial functor theory

---

*The Alethic Architecture: Where truth-seeking becomes structure.*
