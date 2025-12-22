# Witness Assurance Surface

> *"The persona is a garden, not a museum."*

**Status:** Standard
**Implementation:** `impl/claude/services/witness/` (64+ tests), `impl/claude/web/src/components/witness/`
**Heritage:** Witness Primitives, Evidence Ladder, PROV-O, Living Earth palette

---

## Purpose

Make trust visible. The Witness Assurance Surface projects the WitnessGarden polynomial into navigable visualizations across CLI, TUI, and Web. It answers: *"Is this codebase honest?"*

This is not a dashboard. It's a living assurance case where specs grow, evidence accumulates, and problems surface naturally—like weeds in a garden.

---

## Core Insight

**Trust is not a badge—it's a living organism.**

The UI doesn't *display* trust; it *grows* trust. Every spec is a plant:
- Evidence is soil depth (more evidence → taller plant)
- Confidence is health (high → blooming, decayed → wilting)
- Orphans are weeds (visible at edges, inviting tending)

---

## Formal Definition

### The Trust Surface Functor

```
TrustSurface : WitnessGarden × AccountabilityLens × Density → Scene

where:
  WitnessGarden = PolyAgent[SpecHealth, Evidence, PlantVisual]
  AccountabilityLens = Audit | Author | Trust
  Density = compact | comfortable | spacious
  Scene = renderable structure (per AD-008)
```

### The WitnessGarden Polynomial

The garden is a polynomial agent (AD-002). Specs have states; evidence causes transitions.

```
Positions: {unwitnessed, in_progress, witnessed, contested, superseded}

Directions(s): Evidence inputs valid per state
  unwitnessed  → {mark, trace, test, prompt}
  in_progress  → {mark, trace, test, proof, refutation}
  witnessed    → {refutation, supersession}
  contested    → {resolution, supersession}
  superseded   → {} (terminal)

Transition: (SpecHealth, Evidence) → (SpecHealth, PlantVisual)
```

### Accountability Lens (Simplifying Isomorphism per AD-008)

Instead of scattered "who is viewing?" conditionals, we name the dimension:

| Lens | What It Shows | Who It's For | Key Binding |
|------|---------------|--------------|-------------|
| **Audit** | Full evidence chain, all levels, rebuttals prominent | External reviewers | `A` |
| **Author** | My marks, my contributions, attention items | Contributors | `U` |
| **Trust** | Confidence only, green/yellow/red at a glance | Executives | `T` |

This is opinionated. We know there are three observer types and we design for each.

---

## Type Signatures

### Garden Types

```python
@dataclass(frozen=True)
class SpecPlant:
    """A spec rendered as a plant in the garden."""
    path: str
    status: SpecStatus  # From evidence.py
    confidence: float   # 0.0-1.0
    evidence_levels: EvidenceLevels
    # Derived visual properties
    height: int         # Taller = more evidence
    health: PlantHealth # blooming | healthy | wilting | dead

class PlantHealth(Enum):
    BLOOMING = "blooming"  # witnessed, high confidence
    HEALTHY = "healthy"    # in_progress, stable
    WILTING = "wilting"    # contested or decaying
    DEAD = "dead"          # superseded

@dataclass(frozen=True)
class OrphanWeed:
    """An artifact without prompt lineage."""
    path: str
    created_at: datetime
    suggested_prompt: str | None  # If we can guess origin

@dataclass(frozen=True)
class GardenScene:
    """The complete garden visualization."""
    specs: tuple[SpecPlant, ...]
    orphans: tuple[OrphanWeed, ...]
    overall_health: float  # Average confidence
    lens: AccountabilityLens
```

### Pulse Types

```python
@dataclass(frozen=True)
class ConfidencePulse:
    """Heartbeat of trust for a spec."""
    confidence: float
    previous_confidence: float | None
    pulse_rate: PulseRate  # flatline | awakening | alive | thriving
    delta_direction: Literal["increasing", "decreasing", "stable"]

class PulseRate(Enum):
    FLATLINE = 0      # confidence < 0.3: no animation
    AWAKENING = 0.5   # confidence 0.3-0.6: slow pulse
    ALIVE = 1.0       # confidence 0.6-0.9: steady pulse
    THRIVING = 1.5    # confidence > 0.9: strong pulse
```

### Ladder Types

```python
@dataclass(frozen=True)
class EvidenceLadder:
    """The complete evidence stack from L-∞ to L3."""
    orphan: int    # L-∞: Artifacts without lineage
    prompt: int    # L-2: PromptAncestor count
    trace: int     # L-1: TraceWitness count
    mark: int      # L0: Human marks
    test: int      # L1: Test artifacts
    proof: int     # L2: Formal proofs
    bet: int       # L3: Economic bets
```

### Provenance Types

```python
@dataclass(frozen=True)
class ProvenanceNode:
    """A node in the artifact genealogy."""
    id: str
    type: Literal["orphan", "prompt", "artifact", "mark", "crystal", "test", "proof"]
    label: str
    timestamp: datetime
    confidence: float | None
    author: Literal["kent", "claude", "system"]
    children: tuple["ProvenanceNode", ...] = ()
```

---

## Laws/Invariants

### Observer Law
Same garden + different lens = different scene. The lens is a morphism, not a filter.

### Monotonicity Law
Plant height only increases. Evidence accumulates; it is never removed.

### Health Dynamics Law
```
health = f(evidence_freshness, contradiction_count, prompt_fitness)
```
Health decays over time unless refreshed by new evidence.

### Orphan Visibility Law
Orphans are ALWAYS visible. There is no "hide orphans" option. Weeds exist; we tend them.

### Heartbeat Fidelity Law
Pulse rate reflects actual confidence. A flatline at 0.28 confidence is honest; a thriving pulse at 0.28 is a lie.

---

## Integration

### AGENTESE Paths (Typed per AD-013)

| Path | Type Signature | Component |
|------|----------------|-----------|
| `self.witness.garden` | `Observer → Witness[GardenScene]` | `SpecGarden` |
| `self.witness.ladder` | `(SpecPath, Observer) → Witness[EvidenceLadder]` | `EvidenceLadder` |
| `self.witness.provenance` | `SpecPath → Witness[ProvenanceTree]` | `ProvenanceTree` |
| `self.witness.pulse` | `SpecPath → Witness[ConfidencePulse]` | `EvidencePulse` |
| `self.witness.orphans` | `Observer → Witness[list[OrphanWeed]]` | (part of garden) |

### Composition with Witness Primitives

The Surface projects existing primitives; it does not replace them.

```
Mark → contributes to → EvidenceLadder.mark
Crystal → derived from → ProvenanceNode
Walk → session context → GardenScene filtering
Evidence → determines → SpecPlant.status
```

### SSE Streaming

```python
@node("self.witness.garden")
class WitnessGardenNode(BaseLogosNode):
    aspects = ["manifest", "stream"]

    async def stream(self, observer: AgentMeta) -> AsyncIterator[GardenEvent]:
        """SSE stream of garden updates."""
        # Yields on: new mark, test result, proof completion, orphan change
```

---

## Component Morphisms

Each component is a morphism from data to visual. Implementation details in `impl/`.

### EvidencePulse : Confidence → HeartbeatVisual

Transforms confidence into a breathing animation. Not decorative—diagnostic.

| Confidence Range | Visual Behavior |
|------------------|-----------------|
| 0.0–0.3 | Flatline (stillness) |
| 0.3–0.6 | Slow pulse (awakening) |
| 0.6–0.9 | Steady pulse (alive) |
| 0.9–1.0 | Strong pulse (thriving) |
| On increase | Accelerates briefly |
| On decrease | Becomes irregular |

### EvidenceLadder : Evidence[] → StackVisual

Seven rungs from L-∞ (orphan) to L3 (economic bet). Colors from Living Earth palette.

| Level | Color | Meaning |
|-------|-------|---------|
| L-∞ Orphan | `#991B1B` (red) | Needs attention |
| L-2 Prompt | `sage` | Generative origin |
| L-1 Trace | `#06B6D4` (cyan) | Runtime observation |
| L0 Mark | `copper` | Human attention |
| L1 Test | `#22C55E` (green) | Automation |
| L2 Proof | `#A855F7` (purple) | Formal |
| L3 Bet | `#F59E0B` (amber) | Economic |

### ProvenanceTree : PromptAncestor[] → TreeVisual

Genealogy rendered horizontally (time flows left → right). AI nodes shimmer subtly; human nodes are solid.

### SpecGarden : SpecPlant[] → GardenScene

The primary visualization. Plants grow from ground layers (evidence strata). Weeds cluster at edges.

### WitnessAssurance : (Garden, Lens, Density) → Page

The complete dashboard. Composes all components with lens and density awareness.

---

## Celebration Moments

Joy, not confetti. Milestones earn toasts, not explosions.

| Milestone | Toast |
|-----------|-------|
| Spec reaches WITNESSED | "Witnessed: {name} has earned full witness status" |
| Confidence crosses 0.5 | "Awakening: {name} is coming alive" |
| Orphan linked to prompt | "Tended: {name} now has lineage" |

---

## Anti-Patterns

1. **Spreadsheet aesthetics** — We're a garden, not a ledger. If it looks like Excel, start over.

2. **Hiding orphans** — Orphans are weeds to tend, not shame to conceal. Visibility is non-negotiable.

3. **Static badges** — Trust has a heartbeat. A green checkmark is dead; a pulsing indicator is alive.

4. **Confetti celebrations** — *"Daring, bold, creative, opinionated but not gaudy."* Joy is warmth, not particles.

5. **Mode-specific components** — Use density dimension, not `isMobile` conditionals (AD-008).

6. **Ignoring the heartbeat on low confidence** — Flatline IS the animation at low confidence. Stillness communicates.

---

## The Mirror Test

> *"Does this make the assurance case understandable at a glance?"*

**Honest if:**
- A new contributor sees project health in 5 seconds (garden overview)
- Any artifact's genealogy is traceable in 3 clicks
- Low-fitness prompts surface as wilting plants
- Orphans are visible weeds, inviting tending
- Trust accumulation is visible as growth

**Impressive but dishonest if:**
- Garden animation distracts from real status
- Weeds are hidden by default
- Only blooming plants are shown
- The heartbeat is always strong regardless of actual confidence

---

## Constitutional Alignment

| Article | How This Surface Embodies It |
|---------|------------------------------|
| **I. Symmetric Agency** | Same plant representation for Kent's and Claude's marks |
| **IV. The Disgust Veto** | Wilting plants are visually distinct—problems aren't hidden |
| **V. Trust Accumulation** | Garden growth shows earned trust over time |
| **VI. Fusion as Goal** | Provenance shows human+AI contributions interleaved |
| **VII. Amendment** | The garden evolves—dead plants compost, new ones grow |

---

## Implementation Reference

- **Backend:** `impl/claude/services/witness/`
- **Frontend:** `impl/claude/web/src/components/witness/`
- **Parent Spec:** `spec/protocols/witness-primitives.md`
- **Evidence Model:** `spec/protocols/witness-assurance-protocol.md` (Evidence Ladder)
- **Elastic Patterns:** `docs/skills/elastic-ui-patterns.md`

---

*"The UI IS the trust surface. Every pixel grows or wilts."*
