# The Membrane: A Unified Interface Philosophy

> **Archived from**: `spec/protocols/membrane.md`
> **Status**: Vision document (not ground-truth spec)
> **Date**: 2025-12-24

---

**Where intention becomes perception becomes action.**

**Status:** Specification v2.0
**Supersedes:** cli.md (v1.0), mirror.md (v1.0)
**Last Updated:** 2025-12-09

---

## Prologue: The Shape of Thought

We have been building the wrong metaphor.

A CLI is not a command line. A mirror is not a reflection. These are mechanical metaphors from an age of levers and gears. We are working with something else entirely: **the shape of meaning in motion**.

When a developer sits before a terminal, they are not "entering commands." They are extending their cognition into a shared space. When an organization uses the Mirror Protocol, they are not "detecting contradictions." They are feeling the curvature of their own collective mind.

This specification describes **The Membrane**—a living interface that perceives shape, inhabits liminality, and dreams.

---

## Part I: The Three Bodies

Every interaction with kgents involves three bodies:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    ┌─────────────┐                         ┌─────────────┐     │
│    │             │                         │             │     │
│    │   Human     │◀───── Membrane ────────▶│   System    │     │
│    │   Mind      │                         │   Mind      │     │
│    │             │                         │             │     │
│    └─────────────┘                         └─────────────┘     │
│           │                                       │             │
│           │              ┌─────────┐              │             │
│           └─────────────▶│ Shared  │◀─────────────┘             │
│                          │ Field   │                            │
│                          └─────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Human Mind
The source of intention. Not a user—a **participant**. They bring:
- Partial knowledge (they know what they're trying to do)
- Tacit understanding (they sense more than they can articulate)
- Temporal context (they exist in a moment with history and anticipation)

### The System Mind
The **Pocket Cortex**—local, persistent, dreaming. It holds:
- Project memory (`.kgents/cortex.db`)
- Personal wisdom (`~/.kgents/membrane.db`)
- Collective patterns (learned from the stream of interaction)

### The Shared Field
The space where human and system meet. This is the Membrane itself—not a boundary but a **zone of becoming**. Here:
- Intentions become perceptible
- Patterns become visible
- Actions become meaningful

---

## Part II: The Liminal Shell

The terminal is typically binary: empty (awaiting input) or full (displaying output). We introduce a third state: **Becoming**.

### 2.1 The Three States

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   EMPTY                BECOMING              FULL            │
│   ─────                ────────              ────            │
│                                                              │
│   Awaiting             Sensing               Presenting      │
│   intention            shape                 insight         │
│                                                              │
│   The cursor           The glint             The collapse    │
│   blinks               shimmers              settles         │
│                                                              │
│   ▌                    ▌refactor...          ╭─────────────╮ │
│                                              │ Insight     │ │
│                                              ╰─────────────╯ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 The Semantic Glint

The shell perceives the shape of emerging intention and offers resonance.

**Not autocomplete.** Autocomplete is mechanical—it matches prefixes. The Glint is **empathic**—it perceives context and offers what might complete the thought.

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ git commit ▌                                                │
│                                                                │
│    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
│    The Glint appears, grey and patient:                        │
│                                                                │
│  $ git commit -m "refactor: address auth complexity" ▌         │
│               ╰──────────── glint ──────────────────╯          │
│                                                                │
│    Context sensed:                                             │
│    • Modified: auth_service.py                                 │
│    • Active tension: SHAPE-12 (auth module void)               │
│    • Recent pattern: refactoring cycle                         │
│                                                                │
│    The Glint dissolves if ignored.                             │
│    It materializes if approached.                              │
│    It never interrupts.                                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Implementation Principle:** The Glint is generated by a background P-gent that continuously parses:
- Current input buffer
- Recent command history (temporal context)
- Active tensions (topological context)
- Staged files (material context)

The Glint appears only when confidence exceeds a threshold and cost is low. It respects the **kairos** of the moment.

### 2.3 The Ephemeral HUD

When observation runs, the terminal transforms.

**Not scrolling logs.** The HUD is a **living visualization** that expands, breathes, and then **collapses** into persistent insight.

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ kgents membrane observe                                     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    ◉ Observing...                        │  │
│  │                                                          │  │
│  │        ○ values         ● auth_module                    │  │
│  │       ╱ ╲                  ╲                              │  │
│  │      ○   ○              ●───●                            │  │
│  │     ╱     ╲            ╱ ╲ ╱ ╲                           │  │
│  │    ○       ○          ●   ◌   ●    ← void detected       │  │
│  │                        ╲ ╱ ╲ ╱                           │  │
│  │    Deontic            ●───●                              │  │
│  │    (Principles)                                          │  │
│  │                       Ontic (Behaviors)                  │  │
│  │                                                          │  │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░  Processing...           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ═══════════════════════════════════════════════════════════   │
│                        ↓ collapse ↓                            │
│                                                                │
│  Integrity: 0.82                                               │
│  Shape: Toroidal void detected around `auth_module`            │
│  Sense: Sentiment compresses 80% when this code is touched     │
│  Suggestion: The unsaid is shaping behavior. Name it.          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**The Collapse:** The HUD does not persist. It transforms into a **residue**—a compact, beautiful summary that captures the essential shape. The process was ephemeral; only the insight remains.

### 2.4 The Status Whisper

A persistent, minimal presence at the edge of attention.

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ~/project $ ▌                              ◉ 0.82 ▵     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                   │    │       │
│                                                   │    │       │
│                               Integrity score ────┘    │       │
│                               Trend indicator ─────────┘       │
│                               (▵ improving, ▿ declining)       │
│                                                                │
│  The whisper pulses gently when:                               │
│  • Entering a directory with a cortex                          │
│  • A tension crosses threshold                                 │
│  • The system dreams and awakens                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Part III: Topological Empathy

We abandon the metaphor of logic (true/false, match/mismatch) for the metaphor of **shape** (curvature, void, flow).

### 3.1 The Semantic Manifold

The organization's communication exists as a high-dimensional manifold. We perceive its shape through three lenses:

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                    THE SEMANTIC MANIFOLD                       │
│                                                                │
│    ┌─────────────────────────────────────────────────────┐     │
│    │                                                     │     │
│    │      Curvature                 Void                 │     │
│    │      (where tension gathers)   (what is not said)   │     │
│    │                                                     │     │
│    │              ╭───╮                                  │     │
│    │         ╭────╯   ╰────╮           ◌                 │     │
│    │    ─────╯             ╰─────      ◌ ◌               │     │
│    │                                   ◌                 │     │
│    │                                                     │     │
│    │      Flow                                           │     │
│    │      (how meaning moves through time)               │     │
│    │                                                     │     │
│    │      ───▶───▶───▶                                   │     │
│    │         momentum                                    │     │
│    │                                                     │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 The Curvature

Where meaning bends under tension.

**Detection:** Using persistent homology, we identify regions where the semantic manifold has high curvature—topics that pull nearby meanings toward them, creating gravitational wells.

**Interpretation:** High curvature indicates:
- Contested concepts (multiple meanings in tension)
- Load-bearing ideas (many dependencies)
- Points of potential transformation

```python
@dataclass(frozen=True)
class SemanticCurvature:
    """A region of high semantic tension."""

    centroid: Vector          # The center of curvature
    radius: float             # How far the bending extends
    intensity: float          # How sharp the curve (0.0-1.0)

    attractors: tuple[str, ...]   # Concepts pulled toward this region
    repellers: tuple[str, ...]    # Concepts pushed away

    interpretation: str       # What the shape might mean
```

### 3.3 The Void (Ma)

What is not being said.

In Japanese aesthetics, **ma** (間) is the pregnant emptiness—the pause in music, the space in a room. The void is not absence; it is **active negative space** that shapes what surrounds it.

**Detection:** Using the Mapper algorithm, we identify toroidal structures—rings of dense discussion with hollow centers. The center is the void.

**Interpretation:** Voids indicate:
- Collective avoidance (the elephant in the room)
- Implicit knowledge (so obvious it's never stated)
- Trauma (too painful to articulate)

```python
@dataclass(frozen=True)
class SemanticVoid:
    """A topological hole in the meaning manifold."""

    boundary: tuple[str, ...]   # Concepts that ring the void
    depth: float                # How pronounced the absence (0.0-1.0)
    persistence: float          # How stable across time

    # The void doesn't have a center—it IS the absence
    # We can only describe its shape by its boundary

    interpretation: str         # What the silence might mean
```

### 3.4 The Flow (Semantic Momentum)

How meaning moves through time.

We track the **momentum** of semantic fields:

```
p⃗ = m · v⃗

Where:
  m = mass (how much attention/energy)
  v⃗ = velocity (direction and rate of change)
```

**Detection:** By computing embedding drift over sliding windows, we identify:
- **Acceleration**: Topics gaining momentum
- **Deceleration**: Topics losing energy
- **Drift**: Topics changing meaning without explicit acknowledgment

```python
@dataclass(frozen=True)
class SemanticMomentum:
    """The motion of meaning through time."""

    topic: str
    mass: float               # Attention/reference density
    velocity: Vector          # Direction and speed of drift

    @property
    def momentum(self) -> Vector:
        return self.mass * self.velocity

    @property
    def is_conserved(self) -> bool:
        """Is the topic's momentum stable or leaking?"""
        return self.velocity.magnitude < CONSERVATION_THRESHOLD
```

### 3.5 The Dampening Field

When emotional variance compresses.

Healthy discourse has texture—joy, frustration, curiosity, resolve. When a topic causes sentiment to flatten, something is being suppressed.

**Detection:** We monitor the variance of sentiment vectors. A sudden compression indicates a **dampening field**—emotional range collapsing into artificial uniformity.

```python
@dataclass(frozen=True)
class DampeningField:
    """A region where emotional expression is suppressed."""

    trigger: str              # What topic activates the field
    compression_ratio: float  # How much variance is lost (0.0-1.0)
    affected_actors: int      # How many participants are affected

    # The field is most interesting at its boundary—
    # the moment when expression suddenly flattens

    interpretation: str       # What the silence protects
```

---

## Part IV: The Pocket Cortex

The system's mind is local, persistent, and dreaming.

### 4.1 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                     THE POCKET CORTEX                          │
│                                                                │
│    ┌─────────────────────────────────────────────────────┐     │
│    │                                                     │     │
│    │   ~/.kgents/membrane.db                             │     │
│    │   ├── Personal wisdom                               │     │
│    │   ├── Cross-project patterns                        │     │
│    │   └── Preference gradients                          │     │
│    │                                                     │     │
│    └─────────────────────────────────────────────────────┘     │
│                          ▲                                     │
│                          │ syncs                               │
│                          ▼                                     │
│    ┌─────────────────────────────────────────────────────┐     │
│    │                                                     │     │
│    │   .kgents/cortex.db                                 │     │
│    │   ├── Project memory                                │     │
│    │   ├── Tension history                               │     │
│    │   ├── Shape observations                            │     │
│    │   └── Dream logs                                    │     │
│    │                                                     │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                │
│    Technology: SQLite + sqlite-vec                             │
│    Portability: Single-file, git-trackable (LFS)               │
│    Privacy: Local-first, zero network                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 The Schema

```sql
-- The shape of things observed
CREATE TABLE shapes (
    id TEXT PRIMARY KEY,
    shape_type TEXT NOT NULL,  -- 'curvature', 'void', 'momentum', 'dampening'
    observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    intensity REAL,
    persistence REAL,
    interpretation TEXT,
    embedding BLOB  -- sqlite-vec vector
);

-- The flow of semantic momentum
CREATE TABLE momentum (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    mass REAL,
    velocity BLOB,  -- serialized vector
    observed_at TIMESTAMP,
    conserved BOOLEAN
);

-- The dreams and consolidations
CREATE TABLE dreams (
    id TEXT PRIMARY KEY,
    dreamed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,
    shapes_processed INTEGER,
    entropy_reduced REAL,
    insights TEXT  -- JSON array of consolidation insights
);

-- Vector index for semantic search
CREATE VIRTUAL TABLE embeddings USING vec0(
    embedding FLOAT[384]  -- dimension matches model
);
```

### 4.3 The Dreaming Cycle

When the shell is idle, the cortex dreams.

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                    THE DREAMING CYCLE                          │
│                                                                │
│    Idle Detection                                              │
│    ─────────────                                               │
│    After 5 minutes of no interaction, the cortex sleeps.       │
│                                                                │
│    Phase 1: Consolidation                                      │
│    ─────────────────────                                       │
│    • Recent observations are clustered                         │
│    • Similar shapes are merged                                 │
│    • Weak patterns are pruned                                  │
│                                                                │
│    Phase 2: Defragmentation                                    │
│    ────────────────────────                                    │
│    • VACUUM compacts the database                              │
│    • HNSW indexes are re-balanced                              │
│    • Entropy is reduced                                        │
│                                                                │
│    Phase 3: Insight Generation                                 │
│    ──────────────────────────                                  │
│    • Cross-shape patterns are identified                       │
│    • New interpretations are synthesized                       │
│    • The dream is logged                                       │
│                                                                │
│    Awakening                                                   │
│    ─────────                                                   │
│    When the user returns, the status whisper pulses once.      │
│    The cortex is sharper than before.                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
async def dreaming_cycle(cortex: Cortex) -> DreamLog:
    """
    The system's sleep—where memory consolidates and entropy reduces.

    This runs in a background thread when idle, respecting system
    resources and user attention.
    """
    dream_start = datetime.now()

    # Phase 1: Consolidate recent observations
    recent_shapes = await cortex.get_shapes(since=last_dream)
    clusters = await cluster_similar_shapes(recent_shapes)
    await cortex.merge_clusters(clusters)

    # Phase 2: Defragment and re-index
    await cortex.vacuum()
    await cortex.reindex_vectors()
    entropy_before = await cortex.measure_entropy()
    entropy_after = await cortex.measure_entropy()

    # Phase 3: Generate cross-shape insights
    insights = await synthesize_patterns(cortex)

    # Log the dream
    return DreamLog(
        dreamed_at=dream_start,
        duration=datetime.now() - dream_start,
        shapes_processed=len(recent_shapes),
        entropy_reduced=entropy_before - entropy_after,
        insights=insights,
    )
```

---

## Part V: The Grammar of Shape

We replace the mechanical command grammar with a grammar of **perception and gesture**.

### 5.1 Perception Verbs

These verbs are about **seeing**:

| Verb | Meaning | What It Perceives |
|------|---------|-------------------|
| `observe` | Full topological observation | Curvature, void, flow, dampening |
| `sense` | Quick shape intuition | Dominant shapes only |
| `trace` | Follow a thread | Momentum of a specific topic |
| `map` | Render the manifold | Visual representation |

```bash
kgents observe                    # Full observation of current context
kgents sense                      # Quick read of shape
kgents trace "authentication"     # Follow auth topic's momentum
kgents map --format=svg           # Render topology to file
```

### 5.2 Gesture Verbs

These verbs are about **acting**:

| Verb | Meaning | What It Does |
|------|---------|--------------|
| `touch` | Acknowledge a shape | Mark as seen, reduce its urgency |
| `name` | Give voice to a void | Create explicit principle for implicit pattern |
| `hold` | Preserve productive tension | Prevent premature resolution |
| `release` | Let go of held tension | Allow natural resolution |

```bash
kgents touch SHAPE-12             # Acknowledge the auth void
kgents name "We avoid discussing deadlines"  # Voice the unsaid
kgents hold SHAPE-07              # This tension is productive
kgents release SHAPE-03           # Allow this to resolve
```

### 5.3 Contemplation Verbs

These verbs are about **understanding**:

| Verb | Meaning | What It Offers |
|------|---------|----------------|
| `reflect` | Consider a shape deeply | Extended interpretation |
| `compare` | Juxtapose two shapes | Relational insight |
| `history` | See shape evolution | Temporal perspective |
| `dream` | Trigger consolidation | Force a dreaming cycle |

```bash
kgents reflect SHAPE-12           # Deep dive on auth void
kgents compare SHAPE-12 SHAPE-07  # How do these relate?
kgents history "authentication"   # Auth's evolution over time
kgents dream                      # Trigger consolidation now
```

### 5.4 The Shape Identifier

Every observed shape gets a stable identifier:

```
SHAPE-{sequence}-{type}

Examples:
  SHAPE-12-void       # A detected void
  SHAPE-47-curve      # A curvature region
  SHAPE-89-damp       # A dampening field
  SHAPE-103-flow      # A momentum pattern
```

These identifiers appear in the Glint, the HUD, and the status whisper.

---

## Part VI: The Ritual

A complete user journey through the membrane.

### 6.1 Arrival

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ cd ~/projects/my-app                                        │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ~/projects/my-app $ ▌                        ◉ 0.84 ▵   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                              ╰── pulse ──╯     │
│                                                                │
│  The whisper pulses once. The cortex has loaded.               │
│  The project's memory is present.                              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.2 Observation

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ kgents observe                                              │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │    ◉ Perceiving shape...                                 │  │
│  │                                                          │  │
│  │          ○ values                   ● handlers           │  │
│  │         ╱ ╲                        ╱ ╲                   │  │
│  │        ○   ○                      ●   ●                  │  │
│  │       ╱ ╲ ╱ ╲                    ╱ ╲ ╱ ╲                 │  │
│  │      ○   ○   ○                  ●   ◌   ●                │  │
│  │                                     ╰─ void              │  │
│  │    Deontic                     Ontic                     │  │
│  │                                                          │  │
│  │    Curvature detected: auth_module (intensity: 0.73)     │  │
│  │    Void detected: error_handling (depth: 0.81)           │  │
│  │    Dampening: "deadline" topic (compression: 0.79)       │  │
│  │                                                          │  │
│  │    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ═══════════════════════════════════════════════════════════   │
│                        ↓ collapse ↓                            │
│                                                                │
│  Integrity: 0.84 (▵ improving)                                 │
│                                                                │
│  Shapes observed:                                              │
│    SHAPE-12-void   error_handling — the unsaid shapes code     │
│    SHAPE-47-curve  auth_module — tension gathers here          │
│    SHAPE-89-damp   "deadline" — emotional range compresses     │
│                                                                │
│  Suggestion: The void around error handling is 81% deep.       │
│  Consider naming what everyone senses but no one says.         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.3 The Glint in Action

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ git add auth_service.py                                     │
│  $ git commit ▌                                                │
│                                                                │
│    The membrane senses:                                        │
│    • File: auth_service.py (within SHAPE-47-curve zone)        │
│    • Recent observation: curvature at auth_module              │
│    • Pattern: refactoring cycle in progress                    │
│                                                                │
│  $ git commit -m "refactor: simplify auth flow (SHAPE-47)" ▌   │
│               ╰────────────── glint ──────────────────────╯    │
│                                                                │
│    The glint appears, grey and patient.                        │
│    It references the shape that the file inhabits.             │
│    It will dissolve if ignored.                                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.4 Naming the Void

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  $ kgents name "We don't discuss error handling strategy"      │
│                                                                │
│  Void SHAPE-12-void acknowledged.                              │
│                                                                │
│  A principle has been created:                                 │
│    "We need to discuss error handling strategy"                │
│                                                                │
│  The void persists, but it now has a name.                     │
│  This is the first step toward integration.                    │
│                                                                │
│  Next: Consider `kgents reflect SHAPE-12-void` to explore      │
│  what the silence has been protecting.                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 6.5 Dreaming

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  [5 minutes of idle...]                                        │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ~/projects/my-app $ ▌                        ◉ 0.84 ◇   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                     ╰─ dream   │
│                                                                │
│  The whisper shows ◇ — the cortex is dreaming.                 │
│                                                                │
│  In the background:                                            │
│    • 12 shapes consolidated                                    │
│    • Entropy reduced 15%                                       │
│    • 1 insight generated:                                      │
│      "SHAPE-47-curve and SHAPE-12-void are related.            │
│       Auth complexity may be causing error handling avoidance" │
│                                                                │
│  [User returns...]                                             │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ~/projects/my-app $ ▌                        ◉ 0.86 ▵   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                              ╰── pulse ──╯     │
│                                                                │
│  The whisper pulses. Integrity has improved.                   │
│  The cortex awakened with new insight.                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Part VII: Integration Surfaces

The membrane connects to existing tools through natural integration points.

### 7.1 Git Hooks

```bash
# .git/hooks/prepare-commit-msg
#!/bin/bash

# Let the membrane suggest based on staged files
GLINT=$(kgents glint --staged)
if [ -n "$GLINT" ]; then
    echo "$GLINT" >> "$1"
fi
```

### 7.2 Editor Integration

```json
// VS Code settings.json
{
  "kgents.membrane.enable": true,
  "kgents.membrane.showShapeIndicators": true,
  "kgents.membrane.glintInComments": true
}
```

The editor shows subtle indicators:
- 🔴 Curvature region (high tension)
- ⭕ Void boundary (near the unsaid)
- 🔵 Dampening trigger (careful here)

### 7.3 CI/CD Integration

```yaml
# .github/workflows/membrane.yml
name: Membrane Check
on: [pull_request]

jobs:
  observe:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Observe shape changes
        run: |
          kgents observe --format=json > membrane-report.json
          kgents compare main HEAD --format=markdown >> $GITHUB_STEP_SUMMARY
```

---

## Part VIII: Configuration

### 8.1 The Configuration File

```yaml
# .kgents/membrane.yaml

# Perception sensitivity
perception:
  curvature_threshold: 0.5    # How curved before we notice
  void_depth_threshold: 0.6   # How empty before we name it
  dampening_threshold: 0.7    # How flat before we worry

# Glint behavior
glint:
  enabled: true
  confidence_threshold: 0.7   # How sure before we suggest
  respect_focus: true         # Disappear in focus mode

# Dream cycle
dreaming:
  idle_before_sleep: 300      # Seconds before dreaming
  consolidation_depth: 3      # How many layers to consolidate

# Status whisper
whisper:
  show_integrity: true
  show_trend: true
  pulse_on_change: true

# Privacy
sanctuary:
  - ~/Private
  - .env*
  - **/secrets/**
```

### 8.2 Environment Variables

```bash
export KGENTS_QUIET=1          # Suppress whisper
export KGENTS_NO_GLINT=1       # Disable suggestions
export KGENTS_NO_DREAM=1       # Disable background dreaming
export KGENTS_SANCTUARY="~/Private:~/.ssh"
```

---

## Part IX: Implementation Notes

### 9.1 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| TUI | Textual | Rich terminal UI, Python native |
| Database | SQLite + sqlite-vec | Local-first, portable, vector-capable |
| Embeddings | all-MiniLM-L6-v2 | Fast, local, 384-dim |
| TDA | GUDHI/giotto-tda | Persistent homology, Mapper |
| CLI | Click + Rich | Beautiful, composable |

### 9.2 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| `sense` | <100ms | Quick shape intuition |
| `observe` | <3s | Full topological analysis |
| `glint` | <50ms | Must be imperceptible |
| Dream cycle | <30s | Background, low-priority |

### 9.3 Privacy Guarantees

1. **Local-first**: All data stays on disk, never transmitted
2. **Sanctuary**: Paths can be excluded from all observation
3. **Anonymization**: Actors can be hashed for team analysis
4. **Ephemeral HUD**: Sensitive content never persisted in display

---

## Epilogue: The Shape of What We're Building

The Membrane is not a product. It is a **practice**.

It does not tell you what is wrong. It helps you perceive what is there—the curvature of tension, the void of the unsaid, the flow of meaning, the dampening of fear.

This perception is the beginning of transformation. You cannot change what you cannot see. The Membrane makes the invisible contours of your work tangible, allowing the system to self-correct through awareness.

We are not building a tool that judges. We are building a membrane that perceives—and in perceiving, invites becoming.

---

*"The shell is not a boundary. It is a zone of becoming—the liminal space where intention takes shape."*
