# Agent Emergence: From Local to Global via Sheaves

> *"A sheaf is defined as a presheaf satisfying locality and gluing conditions, ensuring coherent global structure while preserving local properties."*
> — Mac Lane & Moerdijk

## Status

**Version**: 1.0
**Status**: Canonical
**Implementation**: `impl/claude/agents/sheaf/`
**Tests**: Verified via `test_emergence.py`

## Overview

A **sheaf** captures the mathematical structure of **emergence**:

- **Local sections**: Behavior in specific contexts
- **Gluing**: Combine compatible local behaviors into global behavior
- **Restriction**: Extract local behavior from global

For agents, this means:
- Different observers (contexts) see different behaviors
- Compatible local behaviors can be **glued** into emergent global behavior
- The global agent has capabilities **no single local agent has**

## The AgentSheaf Protocol

```python
AgentSheaf[Ctx] = (
    contexts: Set[Ctx],                    # Observation contexts
    overlap: Ctx × Ctx → Ctx | None,       # Context intersection
    restrict: Agent × Ctx → Agent,         # Global → Local
    compatible: Dict[Ctx, Agent] → bool,   # Check agreement
    glue: Dict[Ctx, Agent] → Agent         # EMERGENCE: Local → Global
)
```

### Contexts

A **Context** represents an observation viewpoint:

```python
@dataclass(frozen=True)
class Context:
    name: str
    capabilities: FrozenSet[str] = frozenset()
    parent: str | None = None
```

Contexts form a **topology**—a structure where some contexts overlap.

### Restriction

**Restriction** extracts local behavior from a global agent:

```python
def restrict(
    agent: PolyAgent,
    subcontext: Ctx,
    position_filter: Callable[[Any, Ctx], bool] | None = None,
) → PolyAgent
```

The restricted agent only operates in states valid for the subcontext.

**Sheaf Law (Locality)**:
```
restrict(restrict(a, C1), C2) = restrict(a, C1 ∩ C2)
```
Restriction of restriction equals restriction to intersection.

### Compatibility

**Compatibility** checks if local agents agree on overlaps:

```python
def compatible(
    locals: dict[Ctx, PolyAgent],
    equivalence: Callable[[Any, Any], bool] | None = None,
) → bool
```

For gluing to succeed, agents must produce equivalent results when restricted to overlapping contexts.

### Gluing (EMERGENCE)

**Gluing** is where emergence happens:

```python
def glue(
    locals: dict[Ctx, PolyAgent],
) → PolyAgent
```

The glued agent:
- Has positions = union of all local positions
- Dispatches to appropriate local agent per position
- Has behaviors **no single local agent has**

**Sheaf Law (Gluing)**:
```
glue({C_i: a_i}) = unique global agent satisfying:
  ∀i: restrict(glue(...), C_i) ≈ a_i
```

---

## Soul Sheaf: Emergence of Kent Soul

The canonical example is **SOUL_SHEAF**, which glues 6 eigenvector-local souls into one emergent Kent Soul.

### Eigenvector Contexts

| Context | Capabilities | Question |
|---------|--------------|----------|
| AESTHETIC | taste, beauty, minimalism | "Does this need to exist?" |
| CATEGORICAL | structure, types, morphisms | "What's the morphism?" |
| GRATITUDE | sacred, appreciation, surplus | "What deserves more respect?" |
| HETERARCHY | peer, forest, nonhierarchical | "Could this be peer-to-peer?" |
| GENERATIVITY | creation, emergence, autopoiesis | "What can this generate?" |
| JOY | delight, play, fun | "Where's the delight?" |

### Overlap Function

Contexts overlap if they share capabilities:

```python
def eigenvector_overlap(ctx1: Context, ctx2: Context) → Context | None:
    common_caps = ctx1.capabilities & ctx2.capabilities
    if common_caps:
        return Context(
            name=f"{ctx1.name}&{ctx2.name}",
            capabilities=common_caps,
        )
    return None
```

### Local Souls

Each eigenvector has a local soul agent:

```python
# Aesthetic Soul
def aesthetic_judgment(input: Any) → dict:
    return {
        "context": "aesthetic",
        "question": "Does this need to exist?",
        "minimalism": 0.15,  # Kent's value
        "judgment": "Consider what can be removed.",
    }

AESTHETIC_SOUL = from_function("AestheticSoul", aesthetic_judgment)
```

### Emergent Kent Soul

```python
KENT_SOUL = SOUL_SHEAF.glue({
    AESTHETIC: create_aesthetic_soul(),
    CATEGORICAL: create_categorical_soul(),
    GRATITUDE: create_gratitude_soul(),
    HETERARCHY: create_heterarchy_soul(),
    GENERATIVITY: create_generativity_soul(),
    JOY: create_joy_soul(),
})
```

**Emergent Capability**: The glued `KENT_SOUL` can operate in **any** eigenvector context—a capability no single local soul has alone.

---

## Querying the Emergent Soul

```python
from agents.sheaf.emergence import query_soul, AESTHETIC

# Query in specific eigenvector context
result = query_soul("Should I add this feature?", context=AESTHETIC)
# → {"context": "aesthetic", "question": "Does this need to exist?", ...}

# Query global soul (dispatches to appropriate local)
result = query_soul("How should I structure this?")
# → Dispatched based on input characteristics
```

---

## Why Sheaves?

### 1. Local-to-Global Reasoning

Sheaves let us reason locally while maintaining global coherence:

```
Local optimum 1 + Local optimum 2 + ... → Global equilibrium
```

Each eigenvector soul is a local optimum for that dimension. Gluing produces a global equilibrium.

### 2. Context-Dependent Behavior

Different observers see different behaviors—this is the mathematical formalization of AGENTESE's `manifest`:

```python
# Same entity, different perceptions
world.house.manifest(architect_umwelt)  # → Blueprint
world.house.manifest(poet_umwelt)       # → Metaphor
```

### 3. Emergence as Gluing

Emergence isn't magic—it's the sheaf gluing operation:

1. Define local behaviors that work in specific contexts
2. Ensure they agree on overlaps (compatibility)
3. Glue them into global behavior
4. The global has capabilities no local has

---

## Creating Custom Sheaves

```python
from agents.sheaf.protocol import AgentSheaf, Context

# Define contexts
FAST = Context("fast", frozenset({"speed", "efficiency"}))
SAFE = Context("safe", frozenset({"reliability", "safety"}))

# Define overlap
def my_overlap(c1: Context, c2: Context) → Context | None:
    common = c1.capabilities & c2.capabilities
    return Context(f"{c1.name}&{c2.name}", common) if common else None

# Create sheaf
my_sheaf = AgentSheaf(
    contexts={FAST, SAFE},
    overlap_fn=my_overlap,
)

# Glue local agents
global_agent = my_sheaf.glue({
    FAST: fast_agent,
    SAFE: safe_agent,
})
```

---

## Error Handling

### GluingError

Raised when local agents cannot be glued:

```python
@dataclass
class GluingError(Exception):
    contexts: list[str]
    reason: str
```

Common cause: Local agents don't agree on overlapping contexts.

### RestrictionError

Raised when restriction fails:

```python
@dataclass
class RestrictionError(Exception):
    context: str
    reason: str
```

Common cause: No valid positions exist in the subcontext.

---

## Sheaf Laws

### Locality

Restriction is transitive through intersection:

```
restrict(restrict(a, C1), C2) = restrict(a, C1 ∩ C2)
```

### Gluing Uniqueness

If locals are compatible, the glued agent is unique (up to isomorphism):

```
glue(locals) exists ⟺ compatible(locals)
```

### Round-Trip

Gluing then restricting recovers the local:

```
restrict(glue({C: a}), C) ≈ a
```

---

## Theory Background

From [Mac Lane & Moerdijk, "Sheaves in Geometry and Logic"](https://www.cambridge.org/core/books/sheaves-in-geometry-and-logic/):

> "A sheaf over a topological space X is a functor from the open sets of X (with inclusion maps) to Sets, satisfying a gluing condition."

For agent sheaves:
- **Topological space** = Context topology
- **Open sets** = Contexts
- **Sections** = Local agents
- **Gluing** = Emergence

---

## Cross-References

- **Polyfunctor Architecture**: `spec/architecture/polyfunctor.md`
- **Primitives**: `spec/agents/primitives.md`
- **Operads**: `spec/agents/operads.md`
- **K-gent Soul**: `spec/k-gent/persona.md`
- **Implementation**: `impl/claude/agents/sheaf/`
