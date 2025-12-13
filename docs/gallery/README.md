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

## Core Insight

The Gallery is not a website. It is an **I-gent service** that:
- Manifests as TUI, web UI, or CLI depending on context
- Projects agent capabilities as explorable demos
- Derives content from operad operations (AD-003: Generative Over Enumerative)

---

## AGENTESE Integration

### Paths

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
| K-gent | Soul Vibe | "🎭 Playful, 🔬 Abstract, ✂️ Minimal" |
| K-gent | Soul Shadow | Jungian analysis of eigenvectors |
| H-gent | Dialectic | Synthesize thesis + antithesis |
| H-gent | Shadow Scanner | "You claim X, shadow Y" |
| P-gent | Parse | Universal parser with confidence |
| J-gent | Reality | Classify DET/PROB/CHAOTIC |
| A-gent | Oblique | Brian Eno strategies |
| U-gent | Circuit Breaker | Tool health dashboard |

---

## Demo Specification

Each demo is specified as:

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

### Example Demo Spec

```python
DemoSpec(
    id="soul-vibe",
    name="Soul Vibe",
    one_liner="One-liner soul state from eigenvectors",
    genus="K",
    complexity=2,
    operad_operation="SOUL_OPERAD.introspect",

    description="""
    K-gent condenses the 7 eigenvector dimensions into a
    human-readable vibe summary. Different eigenvalue weights
    produce different emoji + descriptor combinations.
    """,

    code_example="""
    kgent = KgentAgent.from_context(ctx)
    vibe = await kgent.get_vibe()
    print(vibe)  # → "🎭 Playful, 🔬 Abstract, ✂️ Minimal"
    """,

    expected_output="🎭 Playful, 🔬 Abstract, ✂️ Minimal",

    interactive=True,   # User can adjust eigenvector weights
    streaming=False,
    prerequisites=["hello-world"]
)
```

---

## Generation from Operad

Demos derive from operad operations (AD-003):

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
            operad_operation=f"{operad.name}.{op_name}",
            description=generate_description(operation),
            code_example=generate_code_example(operad, op_name),
            expected_output=generate_expected_output(operation),
            interactive=True,
            streaming=False,
            prerequisites=[]
        )
        demos.append(demo)
    return demos

# Usage
soul_demos = generate_demos_from_operad(SOUL_OPERAD)
parse_demos = generate_demos_from_operad(PARSE_OPERAD)
```

---

## Manifestation Modes

### TUI Mode (Primary)

```
┌─────────────────────────────────────────────────────────────────┐
│ kgents gallery                                     [q] quit      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SOUL (K-gent)                    THINKING (H-gent)              │
│  ┌──────────────────┐            ┌──────────────────┐           │
│  │ 🎭 Soul Vibe     │            │ 👤 Shadow        │           │
│  │ One-liner state  │            │ Jungian analysis │           │
│  └──────────────────┘            └──────────────────┘           │
│                                                                  │
│  ┌──────────────────┐            ┌──────────────────┐           │
│  │ 📈 Soul Drift    │            │ ⚖️ Dialectic     │           │
│  │ Track evolution  │            │ Hegelian synth   │           │
│  └──────────────────┘            └──────────────────┘           │
│                                                                  │
│  [h/j/k/l] navigate  [Enter] run demo  [?] help                 │
└─────────────────────────────────────────────────────────────────┘
```

### CLI Mode

```bash
$ kg gallery
Available demos (6):
  1. hello-world      [Lvl 1] Your first agent
  2. composition      [Lvl 2] Pipe agents together
  3. lift-maybe       [Lvl 3] Handle optional values
  4. soul-vibe        [Lvl 2] One-liner soul state
  5. dialectic        [Lvl 3] Synthesize two concepts
  6. polynomial       [Lvl 4] State machine agent

$ kg gallery run soul-vibe
Running: Soul Vibe
---
🎭 Playful, 🔬 Abstract, ✂️ Minimal
---
[Enter] to try again with different inputs, [q] to quit
```

### Web Mode (Future)

Static site generated from demo specs, with embedded WASM runtime for interactive demos.

---

## Tour System

Guided tours take users through progressive complexity:

```python
@dataclass
class Tour:
    """A guided sequence of demos."""
    id: str
    name: str
    description: str
    steps: list[TourStep]

@dataclass
class TourStep:
    """A single step in a tour."""
    demo_id: str
    instruction: str       # What to do
    explanation: str       # Why it matters
    challenge: str | None  # Optional exercise
```

### Example Tour

```python
FIRST_HOUR_TOUR = Tour(
    id="first-hour",
    name="Your First Hour with kgents",
    description="From zero to polynomial agents in 60 minutes",
    steps=[
        TourStep(
            demo_id="hello-world",
            instruction="Run your first agent",
            explanation="Every agent is a morphism: A → B",
            challenge=None
        ),
        TourStep(
            demo_id="composition",
            instruction="Compose two agents",
            explanation="Agents compose: (A → B) >> (B → C) = (A → C)",
            challenge="Try composing Ground >> Judge >> Sublate"
        ),
        TourStep(
            demo_id="soul-vibe",
            instruction="Ask K-gent about itself",
            explanation="K-gent is the persona functor",
            challenge="What happens if you change the aesthetic eigenvector?"
        ),
        # ... more steps
    ]
)
```

---

## Implementation Roadmap

### Phase 1: Demo Registry (Week 1)

- [ ] `DemoSpec` dataclass
- [ ] Demo registry with 10 initial demos
- [ ] CLI `kg gallery` command

### Phase 2: TUI Mode (Week 2)

- [ ] Textual-based gallery browser
- [ ] h/j/k/l navigation
- [ ] Demo execution with output display

### Phase 3: Operad Generation (Week 3)

- [ ] `generate_demos_from_operad()` function
- [ ] Auto-generate demos from SOUL_OPERAD, PARSE_OPERAD
- [ ] Sync demo registry with operad changes

### Phase 4: Tour System (Week 4)

- [ ] Tour dataclasses
- [ ] `kg gallery tour first-hour` command
- [ ] Progress tracking

### Phase 5: Web Export (Future)

- [ ] Static site generator
- [ ] WASM runtime for interactive demos
- [ ] GitHub Pages deployment

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Time to first demo | < 30 seconds |
| Demos available | 20+ (10 generated) |
| Tour completion rate | > 50% |
| User satisfaction | "Wow" on first run |

---

## Integration Points

| System | Integration |
|--------|-------------|
| AGENTESE | `self.gallery.*` paths |
| I-gent | TUI widgets, semantic fields |
| Operad | Demo generation from operations |
| CLI | `kg gallery` command family |
| Ghost | Gallery usage metrics |

---

## Anti-patterns

- Static documentation pretending to be interactive
- Demos that require reading docs first
- Examples that don't actually run
- Gallery that's separate from the agent system

---

## References

- `strategic-recommendations-2025-12-13.md` — Original 10x UX analysis
- `crown-jewels.md` — Demo content source
- `plans/skills/cli-command.md` — CLI patterns
- `spec/i-gents/` — Visualization specs

---

*"The best system teaches through use, not through documentation."*
