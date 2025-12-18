# Gallery Service Specification

> *"Show, don't tell. The gallery is where agents reveal themselves."*

**Status**: Future (agent-native service)
**Agent Genus**: I-gent (visualization)
**AGENTESE Path**: `self.gallery.*`

---

## Purpose

The Gallery is an **agent-native service** that provides interactive, explorable demonstrations of kgents capabilities. Unlike static documentation, the Gallery:

1. **Runs live agents** — Demos execute actual agent code
2. **Adapts to observer** — Different users see different affordances
3. **Generates from operad** — Gallery items derive from `SOUL_OPERAD`, `PARSE_OPERAD`, etc.
4. **Teaches through use** — Progressive disclosure from simple to complex

---

## Philosophy

> "An agent is a morphism A → B. Everything else is added via Halo."

The Gallery demonstrates kgents' core principles:

- **Composability**: Agents are morphisms that compose predictably
- **Functors**: Lift agents to new contexts (Maybe, Flux, etc.)
- **Personality**: Soul governance ensures aligned responses
- **Tasteful design**: Quality over quantity, always

---

## Featured Examples

| Demo | Description |
|------|-------------|
| **Hello World** | Your first agent - learn the fundamental `Agent[A, B]` pattern |
| **Composition** | Chain agents with `>>` - category theory in action |
| **Functors** | Handle optional values with the Maybe functor |
| **Soul Dialogue** | Chat with K-gent, Kent's digital simulacra |
| **Streaming** | Transform discrete agents into continuous processors with Flux |
| **Custom Archetype** | Build production-ready agents with Kappa |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/kentgang/kgents.git
cd kgents

# Install dependencies
pip install -e .

# Interactive tutorials
kgents play hello        # Start with hello world
kgents play compose      # Learn composition
kgents play functor      # Explore functors
kgents play soul         # Meet K-gent
```

---

## Learning Path

1. **Hello World** — Understand the `Agent[A, B]` pattern
2. **Composition** — Learn to chain agents with `>>`
3. **Functors** — Handle edge cases elegantly
4. **Soul Dialogue** — Add personality to your agents
5. **Streaming** — Process continuous flows
6. **Custom Archetype** — Build production systems

---

## AGENTESE Integration

| Path | Purpose | Returns |
|------|---------|---------|
| `self.gallery.manifest` | Get gallery view for observer | `GalleryView` |
| `self.gallery.demo` | Run a specific demo | `DemoResult` |
| `self.gallery.tour` | Start guided tour | `TourSession` |
| `self.gallery.catalog` | List all available demos | `list[DemoSpec]` |

### Observer-Dependent Views

```python
# New user: simple demos, progressive complexity
await logos.invoke("self.gallery.manifest", novice_umwelt)
# → Shows: Hello World, Basic Composition, First Functor

# Expert user: full catalog, advanced patterns
await logos.invoke("self.gallery.manifest", expert_umwelt)
# → Shows: Polynomial Agents, Operad Composition, Sheaf Gluing
```

---

## Demo Categories

### By Complexity

| Level | Description | Examples |
|-------|-------------|----------|
| **1. Hello World** | First agent | `Id`, simple `invoke()` |
| **2. Composition** | Two agents combined | `Ground >> Judge` |
| **3. Functors** | Lifted agents | `Maybe(agent)`, `Fix(agent)` |
| **4. Polynomial** | State machines | `SOUL_POLYNOMIAL` |
| **5. Operad** | Grammar composition | `SOUL_OPERAD.compose(...)` |
| **6. Emergence** | Sheaf gluing | `KENT_SOUL` from local agents |

### By Agent Genus

| Genus | Demo | One-Liner |
|-------|------|-----------|
| K-gent | Soul Vibe | Eigenvector mood |
| K-gent | Soul Shadow | Jungian analysis |
| H-gent | Dialectic | Synthesize thesis + antithesis |
| P-gent | Parse | Universal parser with confidence |
| J-gent | Reality | Classify DET/PROB/CHAOTIC |

---

## Demo Specification

```python
@dataclass
class DemoSpec:
    """Specification for a gallery demo."""
    id: str                      # Unique identifier
    name: str                    # Display name
    one_liner: str               # What it does in one sentence
    genus: str                   # Agent genus (K, H, P, J, etc.)
    complexity: int              # 1-6 scale
    operad_operation: str | None # If derived from operad

    # Content
    description: str             # Full description
    code_example: str            # Runnable Python code
    expected_output: str         # What user should see

    # Affordances
    interactive: bool            # Can user modify inputs?
    streaming: bool              # Shows real-time updates?
    prerequisites: list[str]     # Demo IDs to complete first
```

---

## Generation from Operad

Demos derive from operad operations (AD-003: Generative Over Enumerative):

```python
def generate_demos_from_operad(operad: Operad) -> list[DemoSpec]:
    """Generate gallery demos from operad operations."""
    demos = []
    for op_name, operation in operad.operations.items():
        demo = DemoSpec(
            id=f"{operad.name.lower()}-{op_name}",
            name=f"{operad.name} {op_name.title()}",
            one_liner=operation.signature,
            genus=infer_genus(operad),
            complexity=infer_complexity(operation),
            # ...
        )
        demos.append(demo)
    return demos
```

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Time to first demo | < 30 seconds |
| Demos available | 20+ (10 generated) |
| Tour completion rate | > 50% |
| User satisfaction | "Wow" on first run |

---

## References

- `protocols/projection/gallery/` — Projection Gallery implementation
- `crown-jewels.md` — Demo content source
- `spec/i-gents/` — Visualization specs

---

*"The best system teaches through use, not through documentation."*
