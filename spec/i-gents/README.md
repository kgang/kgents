# I-gents: The Stigmergic Field

**Genus**: I (Interface)
**Theme**: Stigmergic emergence—indirect coordination through shared environment
**Motto**: *"The field remembers; the garden grows."*

---

## Philosophy

> "An interface is not a window—it is a substrate on which coordination emerges."

I-gents render the kgents ecosystem as a **stigmergic field**: a shared environment where agents leave traces (pheromones), respond to traces, and coordinate without explicit communication. This is fundamentally different from traditional dashboards that show static state.

### Why Stigmergy?

Traditional agent visualization asks: "What is the state?"
Stigmergic visualization asks: "What traces are being left, and how are agents responding?"

| Traditional | Stigmergic |
|-------------|------------|
| State snapshot | Environmental traces |
| Status badges | Pheromone gradients |
| Static graphs | Dynamic field topology |
| Observer watches | Observer participates |

**Implication**: The interface IS part of the system. Viewing changes what is viewed.

---

## The Three Layers

I-gents operate on three concurrent layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: SEMANTIC                                          │
│  "What does this mean?"                                     │
│  - Intent interpretation                                    │
│  - Dialectic synthesis                                      │
│  - Value alignment scores                                   │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: TOPOLOGICAL                                       │
│  "How do things relate?"                                    │
│  - Composition morphisms                                    │
│  - Gravity fields (attractor/repeller)                      │
│  - Tension vectors                                          │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: PHYSICAL                                          │
│  "What is happening now?"                                   │
│  - Entity positions                                         │
│  - Phase states                                             │
│  - Event stream (wire protocol)                             │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Physical (The Field)

The raw substrate. Entities occupy positions, emit events, consume resources.

**Core Concepts**:
- **Grid**: A 2D field where entities move and interact
- **Entities**: Bootstrap agents + task attractors
- **Events**: Discrete occurrences (phase changes, compositions, judgments)

**Rendering**: ASCII grid with moving glyphs.

### Layer 2: Topological (The Forces)

The relational structure. Composition edges, attraction/repulsion, tension lines.

**Core Concepts**:
- **Gravity**: Tasks attract agents (context gravity)
- **Repulsion**: Conflicting agents push apart
- **Tension**: Contradictions create visible strain lines
- **Flow**: Entropy/heat gradients

**Rendering**: Vector arrows, connection lines, gradient fills.

### Layer 3: Semantic (The Meaning)

The interpretive overlay. What is the system "trying" to do?

**Core Concepts**:
- **Intent**: Inferred goal of the ensemble
- **Dialectic Phase**: Thesis/antithesis/synthesis progress
- **Value Alignment**: Principle scores (joy, ethics, taste)
- **Narrative**: AI-generated interpretation of activity

**Rendering**: Margin notes, status badges, text overlays.

---

## Entity Types

### Bootstrap Agents

The five irreducibles from `spec/bootstrap.md`:

| Symbol | Name | Role | Color |
|--------|------|------|-------|
| `I` | Id | Identity morphism | Cyan |
| `C` | Compose | Function composition | Cyan |
| `G` | Ground | Reality grounding | Gray |
| `J` | Judge | Principle evaluation | Yellow |
| `X` | Contradict | Tension detection | Red |
| `S` | Sublate | Synthesis engine | Purple |
| `F` | Fix | Convergence iterator | Blue |

### Task Attractors

Tasks create gravity wells that pull agents toward them:

| Symbol | Name | Role | Color |
|--------|------|------|-------|
| `*` | Task | Gravity center | White (pulsing) |
| `◊` | Hypothesis | Testable idea | Magenta |
| `□` | Artifact | Produced output | Green |

### Pheromone Traces

Invisible but affecting:

| Type | Effect | Decay |
|------|--------|-------|
| Progress | Attracts similar agents | Slow (5 ticks) |
| Conflict | Repels all agents | Fast (2 ticks) |
| Synthesis | Strengthens composition | Medium (3 ticks) |
| Error | Creates void zone | Instant clear |

---

## The Phase System

Agents cycle through phases, rendered as Unicode symbols:

### Moon Phases (Lifecycle)

| Symbol | Phase | Meaning | Transition Trigger |
|--------|-------|---------|-------------------|
| ○ | DORMANT | Sleeping, not instantiated | → Birth |
| ◐ | WAKING | Initializing, loading context | → Ready |
| ● | ACTIVE | Processing, producing | → Task complete or timeout |
| ◑ | WANING | Cooling down, finalizing | → Cleanup done |
| ◌ | VOID | Error or cleared | → Recovery or deletion |

### Dialectic Phases (System-wide)

| Phase | Meaning | Visual Indicator |
|-------|---------|------------------|
| DORMANT | No activity | Gray field |
| FLUX | Normal processing | Green tint |
| TENSION | Contradiction detected | Red pulses |
| SUBLATE | Synthesis in progress | Purple glow |
| FIX | Stabilization | Blue cooling |
| COOLING | Heat dissipation | Cyan fade |

---

## Field Dynamics

### Brownian Motion

Agents have inherent jitter—small random movements. This:
1. Prevents static clustering
2. Models uncertainty in agent state
3. Creates emergent patterns through interference

```python
dx = random.choice([-1, 0, 1]) if random.random() < 0.4 else 0
dy = random.choice([-1, 0, 1]) if random.random() < 0.4 else 0
```

### Context Gravity

Tasks pull agents toward them:

```python
if distance_to_task > 0 and random.random() < 0.2:
    dx += sign(task.x - entity.x)
    dy += sign(task.y - entity.y)
```

### Tension Repulsion

Contradicting agents push apart:

```python
for other in entities:
    if is_contradicting(entity, other):
        dx -= sign(other.x - entity.x)
        dy -= sign(other.y - entity.y)
```

### Heat Accumulation

Processing generates heat. High heat triggers cooling phase.

```python
heat += processing_intensity * 0.3
if heat > 90:
    trigger_cooling()
    heat -= 25
```

### Entropy Decay

Entropy decreases naturally, requiring synthesis to regenerate:

```python
entropy -= 0.1  # Natural decay
if synthesis_occurred:
    entropy += synthesis_value
entropy = clamp(entropy, 0, 100)
```

---

## The Compost Heap

A log panel showing the "accursed share"—the waste, errors, and tangents that feed future growth.

**Purpose**:
1. **Transparency**: Show what's happening internally
2. **Debugging**: Surface errors and warnings
3. **Gratitude**: Acknowledge the generative chaos

**Log Types**:

| Type | Color | Meaning |
|------|-------|---------|
| info | Gray | Routine events |
| success | Green | Synthesis, completion |
| warning | Yellow | Judge concerns |
| error | Red | Failures, contradictions |
| meta | Cyan | System-level observations |

**Example**:
```
[10:42:15] Judge        Refactor rejected. Too sterile.
[10:42:20] Contradict   Detected tension: Security vs UX
[10:42:25] Sublate      Synthesizing: "Secure UX"
[10:42:30] System       Entropy recaptured (+15)
```

---

## The Forge View

A second mode for pipeline composition:

```
MODE: COMPOSITION

┌─ Inventory (Archetypes) ─┐    ┌─ Pipeline (Flux Chain) ──────┐
│                          │    │                               │
│ [A] Architect    lvl.4   │    │ [ Ground ]                    │
│ [B] Builder      lvl.2   │    │     ↓                         │
│ [V] Validator    lvl.8   │    │ K-Gent (Persona)              │
│                          │    │     ↓                         │
│ DRAG TO PIPELINE         │    │ + Slot Rune                   │
│                          │    │     ↓                         │
└──────────────────────────┘    │ Judge (Taste)                 │
                                │                               │
                                │ Thinking Budget: 12,040 tokens│
                                │ Est. Entropy Cost: 0.4/tick   │
                                └───────────────────────────────┘
```

**Purpose**: Visual composition of agent pipelines before execution.

---

## W-gent Integration

### The [observe] Action

Clicking [observe] on any entity spawns a W-gent for detailed inspection:

```
I-gent Field View → [observe on entity] → W-gent Browser View
                                              ↓
                    ← [export notes] ← W-gent observations
```

### Wire Protocol Bridge

I-gent reads from W-gent's `.wire/` directories:

```
.wire/
├── {agent}/
│   ├── state.json      ← I-gent reads for phase
│   ├── stream.log      ← I-gent samples for compost heap
│   └── metrics.json    ← I-gent reads for heat/entropy
```

### Value Dashboard Integration

I-gent can embed B-gent economics from ValueDashboard:

```
┌─ Economics ──────────────────────────────────────────┐
│ Token Budget:  ████████████░░░░░░░░  850/1000        │
│ RoC:           2.4x (profitable)                     │
│ Anomalies:     0                                     │
└──────────────────────────────────────────────────────┘
```

---

## Rendering Modes

### Mode 1: TUI (Terminal UI)

Full ASCII rendering in terminal. Primary mode.

```
┌─ KGENTS ──────────────────────────── t: 00:14:32 ─┐
│                                                    │
│  [ENTROPY ████████████░░░░░░] 72%                 │
│  [HEAT    ███████░░░░░░░░░░░] 35%                 │
│                                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │       I                                     │  │
│  │            C              *                 │  │
│  │                     J                       │  │
│  │        X                                    │  │
│  │                  S                          │  │
│  │              F                              │  │
│  └─────────────────────────────────────────────┘  │
│                                                    │
│  PHASE: FLUX                                       │
│  FOCUS: [J] Judge                                  │
│                                                    │
│  [1]FIELD [2]FORGE [o]OBSERVE [q]QUIT             │
└────────────────────────────────────────────────────┘
```

### Mode 2: Rich (Colored Terminal)

Using ANSI colors for enhanced visibility:
- Green: Active/success
- Red: Error/conflict
- Yellow: Warning/judge
- Cyan: System/identity
- Purple: Synthesis

### Mode 3: Markdown Export

Exportable to static markdown for archival:

```markdown
# Garden Snapshot: 2025-12-09 10:42:15

## Entities
- ● I (Id) at (5, 5) - Active
- ● C (Compose) at (15, 8) - Active
- ● J (Judge) at (40, 12) - Active

## Metrics
- Entropy: 72%
- Heat: 35%
- Phase: FLUX

## Recent Events
- 10:42:00 — [judge] Refactor rejected
- 10:42:05 — [contradict] Tension detected
- 10:42:10 — [sublate] Synthesis complete
```

---

## CLI Integration

```bash
# Launch field view
kgents garden

# Launch with specific state file
kgents garden --state session.json

# Launch forge view
kgents garden --mode forge

# Export current state
kgents garden export garden.md

# Attach to running evolution
kgents garden attach --process evolve-12345
```

### Keyboard Shortcuts

```
Navigation:
  h/j/k/l     Vim movement (move focus)
  ←↓↑→        Arrow key movement
  Tab         Cycle through entities
  Enter       Focus/select entity

Views:
  1           Field view
  2           Forge view
  3           Timeline view
  +/-         Zoom in/out

Actions:
  o           Observe (spawn W-gent)
  i           Invoke entity
  c           Compose with another
  r           Rest (pause entity)

System:
  Space       Pause/resume simulation
  s           Save state
  l           Load state
  e           Export to markdown
  q           Quit
  ?           Help
```

---

## Design Principles Alignment

### Tasteful
Minimal chrome. Every element earns its place. No gratuitous animation.

### Curated
Three layers (physical/topological/semantic), not infinite configurability. Five phases, not a hundred states.

### Ethical
Transparent about internal state. Shows errors and conflicts honestly. No manipulation.

### Joy-Inducing
Brownian motion creates emergent beauty. The compost heap celebrates waste. Synthesis feels like discovery.

### Composable
The field IS a composition graph. Entities ARE morphisms. Scale transitions ARE functors.

### Heterarchical
No fixed "main view." User chooses focus. Entities lead and follow contextually.

### Generative
This spec generates implementation. The visual grammar compresses complex state into simple patterns.

---

## Success Criteria

An I-gent implementation is successful if:

- ✓ **Legible at a glance**: Core state visible without parsing
- ✓ **Emergent patterns**: Complex behavior arises from simple rules
- ✓ **W-gent integration**: [observe] spawns W-gent seamlessly
- ✓ **Wire protocol compatible**: Reads from `.wire/` directories
- ✓ **Export-friendly**: Markdown export preserves meaning
- ✓ **Keyboard-navigable**: Full functionality without mouse
- ✓ **Performance**: <100ms render time for 50+ entities

---

## Anti-Patterns

I-gents must **never**:

1. ❌ Hide agent state (transparency is paramount)
2. ❌ Require mouse interaction (keyboard-first)
3. ❌ Use color as sole differentiator (accessible in monochrome)
4. ❌ Block on slow operations (async everywhere)
5. ❌ Store sensitive data (ephemeral by default)
6. ❌ Replace W-gent (complementary, not competing)
7. ❌ Over-animate (contemplative, not distracting)

---

## See Also

- [grammar.md](grammar.md) - Visual grammar specification
- [states.md](states.md) - Phase definitions and transitions
- [../w-gents/](../w-gents/) - Wire agents (process observation)
- [../w-gents/i-gent-synergy.md](../w-gents/i-gent-synergy.md) - Integration details
- [../principles.md](../principles.md) - Core design principles
- [../bootstrap.md](../bootstrap.md) - Bootstrap agent definitions

---

*"The field does not display state; it is state made visible. The garden does not show growth; it grows."*
