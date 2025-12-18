# The Garden Protocol: Next-Generation Planning

**Status:** Draft Specification
**Date:** 2025-12-18
**Derived From:** `plans/next-generation-planning.md`
**Principles:** Tasteful, Curated, Joy-Inducing, Composable, Generative

---

## Epigraph

> *"The persona is a garden, not a museum."* — _focus.md
>
> *"One insight per line. If it takes a paragraph, it's not distilled."* — meta.md
>
> *"Plans are conversations with future selves, not checklists."*

---

## Part I: Purpose & Core Insight

### 1.1 Why Does This Need to Exist?

The Forest Protocol is functional but mechanical. It tracks tasks without soul:

| Current | Problem |
|---------|---------|
| `status: active` | Too coarse. "Active" could mean excited or neglected. |
| `progress: 55` | Arbitrary. What does 55% mean? |
| `phase_ledger: SENSE: touched` | Bureaucratic. Checkbox mentality. |
| `session_notes: Next: X` | Terse. No warmth, no insight. |
| `entropy: spent: 0.0` | The accursed share is dormant everywhere. |

The Garden Protocol transforms planning from task-tracking to **cultivation**.

### 1.2 The Core Insight

> **The unit of planning is the session, not the plan file.**

Plans are emergent patterns in session traces—like paths worn through a garden by walking. The plan file is a persistent artifact, but the session is where work happens.

---

## Part II: Formal Definition

### 2.1 The Garden Polynomial

```python
from protocols.agentese.poly import PolyAgent

class Season(Enum):
    SPROUTING = "sprouting"    # New, exploring, high plasticity
    BLOOMING = "blooming"      # Active development, productive
    FRUITING = "fruiting"      # Harvesting results, documentation
    COMPOSTING = "composting"  # Extracting learnings, winding down
    DORMANT = "dormant"        # Resting, may dream

@dataclass
class GardenPolynomial(PolyAgent[Season, GardenInput, GardenOutput]):
    """
    Planning as polynomial functor.

    The same input produces different outputs depending on season:
    - SPROUTING: divergent exploration welcome
    - BLOOMING: focused work expected
    - COMPOSTING: reflection and extraction
    - DORMANT: may dream (void.* connections)
    """
    positions: frozenset[Season] = frozenset(Season)

    def directions(self, season: Season) -> frozenset[GardenInput]:
        """Season-dependent valid inputs."""
        match season:
            case Season.SPROUTING:
                return frozenset([GardenInput.EXPLORE, GardenInput.DEFINE, GardenInput.CONNECT])
            case Season.BLOOMING:
                return frozenset([GardenInput.BUILD, GardenInput.TEST, GardenInput.REFINE])
            case Season.FRUITING:
                return frozenset([GardenInput.DOCUMENT, GardenInput.SHIP, GardenInput.CELEBRATE])
            case Season.COMPOSTING:
                return frozenset([GardenInput.EXTRACT, GardenInput.ARCHIVE, GardenInput.TITHE])
            case Season.DORMANT:
                return frozenset([GardenInput.DREAM, GardenInput.WAKE])
```

### 2.2 The Garden Operad

```python
GARDEN_OPERAD = Operad(
    operations={
        # Unary operations (self-transformation)
        "tend": Operation(arity=1, compose=tend_compose),
        "prune": Operation(arity=1, compose=prune_compose),
        "water": Operation(arity=1, compose=water_compose),

        # Binary operations (plan interaction)
        "cross_pollinate": Operation(arity=2, compose=cross_pollinate_compose),
        "graft": Operation(arity=2, compose=graft_compose),

        # Nullary operations (void.* draws)
        "dream": Operation(arity=0, compose=dream_compose),
        "sip": Operation(arity=0, compose=sip_compose),
    },
    laws=[
        # Tending is idempotent: tend >> tend ≡ tend
        Law("tend_idempotent", lambda a: (a >> "tend" >> "tend") == (a >> "tend")),
        # Cross-pollination is symmetric
        Law("cross_symmetric", lambda a, b: cross_pollinate(a, b) == cross_pollinate(b, a)),
        # Entropy conservation: sips must tithe
        Law("entropy_balance", lambda g: g.entropy.spent <= g.entropy.available),
    ]
)
```

### 2.3 The Garden Sheaf

```python
class GardenSheaf:
    """
    Global coherence from local plan views.

    The sheaf condition ensures all plans glue to a coherent project.
    """

    def overlap(self, plan_a: str, plan_b: str) -> set[str]:
        """What do these plans share?"""
        return shared_concepts(plan_a, plan_b) | shared_files(plan_a, plan_b)

    def compatible(self, view_a: PlanView, view_b: PlanView, overlap: set[str]) -> bool:
        """Do these views agree on shared elements?"""
        for concept in overlap:
            if view_a.get(concept) != view_b.get(concept):
                return False
        return True

    def glue(self, views: list[PlanView]) -> ProjectView:
        """Combine compatible local views into global view."""
        if not all_pairwise_compatible(views):
            raise CoherenceError("Plans don't glue: conflict in shared elements")
        return merge_views(views)
```

---

## Part III: The New Header Format

### 3.1 Before (Forest Protocol)

```yaml
---
path: plans/coalition-forge
status: active
progress: 55
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables: []
session_notes: |
  Wave 2 synergies in progress. 221 tests.
phase_ledger:
  SENSE: complete
  ACT: in_progress
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---
```

### 3.2 After (Garden Protocol)

```yaml
---
path: self.forest.plan.coalition-forge
mood: excited
momentum: 0.7
trajectory: accelerating
season: BLOOMING
last_gardened: 2025-12-18
gardener: claude-opus-4-5

letter: |
  We made real progress today. Coalition events feel elegant—
  natural emergence from citizen interactions. The Atelier
  synergy via exquisite corpse is particularly delightful.

  Still fuzzy: consent debt integration. Look at Park's INHABIT.

  Feeling: energized but ready to rest.

resonates_with:
  - atelier-experience  # exquisite corpse connection
  - punchdrunk-park     # consent/masks isomorphism

entropy:
  available: 0.10
  spent: 0.03
  sips:
    - "2025-12-16: Noticed masks → coalition identity isomorphism"
    - "2025-12-18: void suggested Bataille connection"
---
```

### 3.3 Field Definitions

| Field | Type | Meaning |
|-------|------|---------|
| `path` | AGENTESE path | `self.forest.plan.<name>` |
| `mood` | string | Current emotional state (see vocabulary) |
| `momentum` | float [0,1] | Energy/activity level |
| `trajectory` | enum | `accelerating \| cruising \| decelerating \| parked` |
| `season` | Season | Life cycle stage |
| `last_gardened` | date | Last meaningful interaction |
| `gardener` | string | Who last tended this |
| `letter` | text | **Conversation with future self** (not notes) |
| `resonates_with` | list[path] | Semantic connections (not just dependencies) |
| `entropy` | object | Void budget tracking |

### 3.4 Mood Vocabulary

Choose from natural, unstrained words:

| Mood | When to Use |
|------|-------------|
| `excited` | High energy, eager to work on this |
| `curious` | Exploring, not sure where it leads |
| `focused` | Deep work, don't interrupt |
| `satisfied` | Good progress, happy with state |
| `stuck` | Blocked but not by external dep |
| `waiting` | Blocked by external dep |
| `tired` | Needs rest, don't push |
| `dreaming` | Dormant but generating connections |
| `complete` | Ready for archive |

**Anti-pattern**: Don't use forced vocabulary ("vibing", "stoked", "effervescent"). Keep it natural.

---

## Part IV: The Session as Primary Unit

### 4.1 Session Structure

```yaml
# _sessions/2025-12-18-morning.md
---
date: 2025-12-18
period: morning  # morning | afternoon | evening | night
gardener: claude-opus-4-5
plans_tended:
  - coalition-forge (BLOOMING → BLOOMING, momentum +0.1)
  - punchdrunk-park (DORMANT → SPROUTING, woke for consent work)
gestures:
  - type: code
    plan: coalition-forge
    summary: "Added coalition event emission to citizen actions"
    files: [services/town/coalition.py, services/town/events.py]
  - type: insight
    plan: coalition-forge
    summary: "Masks in Park ≅ identities in Coalition—both enable threshold-crossing"
  - type: void_sip
    plan: punchdrunk-park
    summary: "Dream surfaced: Bataille's festival → Park spectacle"
entropy_spent: 0.02
---

## Letter to Next Session

We're close on Coalition events. The infrastructure is there, but the tests
need work—currently at 221, should be 250+ for confidence.

Park woke up today because of the consent resonance. The masks/identity
isomorphism is real and might simplify both plans if we extract it.

Leave Coalition blooming. Park is sprouting—gentle exploration, don't force.
```

### 4.2 Gestures

Atomic units of work within a session:

```python
class GestureType(Enum):
    CODE = "code"           # Files changed
    INSIGHT = "insight"     # Learning captured
    DECISION = "decision"   # Choice made
    VOID_SIP = "void_sip"   # Entropy draw
    VOID_TITHE = "void_tithe"  # Learning returned
    CONNECT = "connect"     # Cross-plan link discovered
    PRUNE = "prune"         # Removed/archived something
```

### 4.3 Session → Plan Propagation

After each session:
1. Plans mentioned update their `last_gardened`
2. Mood/momentum adjust based on gestures
3. `resonates_with` updates from `connect` gestures
4. `entropy.spent` increases from void draws
5. Season may transition based on accumulated gestures

---

## Part V: AGENTESE Integration

### 5.1 Plan as Node

```python
@logos.node("self.forest.plan")
class PlanNode:
    """Plans are first-class AGENTESE entities."""

    @aspect(AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, plan_path: str) -> PlanView:
        """Return plan state appropriate for this observer."""
        plan = await load_plan(plan_path)
        return project_for_observer(plan, observer)

    @aspect(AspectCategory.PERCEPTION)
    async def letter(self, observer: Observer, plan_path: str) -> str:
        """Return the letter (conversation with future self)."""
        plan = await load_plan(plan_path)
        return plan.letter

    @aspect(AspectCategory.MUTATION, effects=[Effect.WRITES("plan")])
    async def tend(self, observer: Observer, plan_path: str, update: PlanUpdate) -> Plan:
        """Update plan state with a tending gesture."""
        ...

    @aspect(AspectCategory.ENTROPY)
    async def dream(self, observer: Observer, plan_path: str) -> list[Connection]:
        """Generate speculative connections from void.*"""
        plan = await load_plan(plan_path)
        if plan.season != Season.DORMANT:
            return []  # Only dormant plans dream

        # Draw from void
        sip = await logos("void.entropy.sip", observer, amount=0.02)

        # Generate semantic connections
        connections = await find_resonances(plan, sip.entropy)
        return connections
```

### 5.2 Registered Paths

```
self.forest.*                    # Forest-level operations
  self.forest.manifest           # Project overview
  self.forest.health             # Coherence check (sheaf condition)

self.forest.plan.*               # Plan operations
  self.forest.plan.{name}.manifest
  self.forest.plan.{name}.letter
  self.forest.plan.{name}.tend
  self.forest.plan.{name}.dream

self.forest.session.*            # Session operations
  self.forest.session.manifest   # Current session state
  self.forest.session.begin
  self.forest.session.end
  self.forest.session.gesture

self.forest.garden.*             # Garden-wide operations
  self.forest.garden.prune       # Archive dormant plans
  self.forest.garden.pollinate   # Find cross-plan connections
  self.forest.garden.coherence   # Check sheaf condition
```

---

## Part VI: Entropy & The Accursed Share

### 6.1 Budget Mechanics

Each plan has an entropy budget that **actually gets spent**:

```yaml
entropy:
  available: 0.10    # Starting budget (configurable per plan)
  spent: 0.03        # Accumulated draws
  sips:              # Record of what was drawn
    - "2025-12-16: Noticed masks → coalition identity isomorphism"
```

### 6.2 Operations

| Operation | Effect | When |
|-----------|--------|------|
| `sip` | Draw entropy, reduce available | Exploring tangents |
| `tithe` | Return learning to void, restore available | Completing/archiving |
| `dream` | Draw while dormant, no explicit cost | Background connections |

### 6.3 Exhaustion Behavior

When `spent >= available`:
- Plan can still work (no hard block)
- But no more `sip` operations allowed
- Suggests transition to COMPOSTING (extract learnings, tithe)
- Forces intentionality about exploration vs execution

---

## Part VII: Season Transitions

### 7.1 Transition Graph

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
              ┌──────────┐                               │
        ┌────▶│ SPROUTING │────────────────┐              │
        │     └──────────┘                 │              │
        │          │                       │              │
        │          │ momentum > 0.5        │ stuck        │
        │          ▼                       ▼              │
        │     ┌──────────┐           ┌──────────┐        │
        │     │ BLOOMING │◀─────────▶│ DORMANT  │────────┘
        │     └──────────┘           └──────────┘
        │          │                       ▲
        │          │ near completion       │ no activity
        │          ▼                       │
        │     ┌──────────┐                 │
        │     │ FRUITING │                 │
        │     └──────────┘                 │
        │          │                       │
        │          │ shipped               │
        │          ▼                       │
        │     ┌───────────┐                │
        └─────│COMPOSTING │────────────────┘
              └───────────┘
```

### 7.2 Automatic Signals

| Signal | Trigger | Suggested Action |
|--------|---------|------------------|
| `momentum_decay` | No gestures for 3+ days | Consider DORMANT |
| `entropy_exhausted` | spent >= available | Consider COMPOSTING |
| `resonance_cluster` | 3+ plans share concepts | Consider cross-pollination |
| `coherence_conflict` | Sheaf gluing fails | Resolve plan conflicts |

### 7.3 Human Override

Transitions are **suggestions**, not enforced. The Gardener (K-gent) can:
- Ignore signals
- Force transitions manually
- Keep a plan in any season indefinitely

---

## Part VIII: Migration from Forest Protocol

### 8.1 Compatibility

Old format continues to work:
```yaml
# This still parses
status: active  # → mood: focused (inferred)
progress: 55    # → momentum: 0.55, trajectory: cruising
```

### 8.2 Migration Script

```python
def migrate_plan(old_path: Path) -> Path:
    """Convert Forest Protocol to Garden Protocol."""
    header = parse_yaml_header(old_path)

    new_header = {
        "path": f"self.forest.plan.{header['path'].split('/')[-1]}",
        "mood": status_to_mood(header.get("status", "active")),
        "momentum": header.get("progress", 0) / 100,
        "trajectory": infer_trajectory(header),
        "season": infer_season(header),
        "last_gardened": header.get("last_touched"),
        "gardener": header.get("touched_by"),
        "letter": header.get("session_notes", ""),
        "resonates_with": header.get("enables", []) + header.get("blocking", []),
        "entropy": header.get("entropy", {"available": 0.05, "spent": 0.0, "sips": []})
    }

    # Drop: phase_ledger, progress (derived), status (replaced)
    return write_new_format(old_path, new_header)
```

### 8.3 Phased Rollout

| Phase | Week | Action |
|-------|------|--------|
| 1 | 1 | Add Garden Protocol parser alongside Forest Protocol |
| 2 | 2 | Migrate 3 plans manually, validate tooling |
| 3 | 3 | Auto-migrate remaining plans |
| 4 | 4 | Deprecate Forest Protocol parser |

---

## Part IX: Anti-Patterns

### 9.1 What This Is NOT

- **Not a task tracker** — No checkboxes, no burndown charts, no velocity metrics
- **Not comprehensive** — Quality over exhaustive coverage
- **Not prescriptive** — Moods suggest attention, don't enforce behavior
- **Not bureaucratic** — No ledgers, no mandatory fields, no forms
- **Not precious** — Warmth without forced whimsy

### 9.2 Specific Pitfalls

| Pitfall | Why It's Wrong | Alternative |
|---------|----------------|-------------|
| Mood as gamification | Makes planning performative | Mood is for self-awareness, not leaderboards |
| Over-literal seasons | "It's winter so everything is DORMANT" | Seasons are project state, not calendar |
| Entropy as score | "I have 0.15 entropy budget!" | Entropy is constraint, not achievement |
| Letter as log | "2025-12-18: Did X. Did Y." | Letter is reflection, not changelog |
| Forced resonance | "Every plan must resonate with 3 others" | Resonance is discovered, not mandated |

---

## Part X: Success Criteria

### 10.1 Qualitative

| Criterion | Test |
|-----------|------|
| **Feels soulful** | Reading a plan header should feel like reading _focus.md |
| **Letters get written** | >50% of sessions should leave meaningful letters |
| **Entropy moves** | `spent` should actually change, not always be 0.0 |
| **Resonance emerges** | Cross-plan connections discovered via void.dream |
| **Coherence maintained** | Sheaf gluing succeeds for active plans |

### 10.2 Quantitative

| Metric | Target |
|--------|--------|
| Header size | Same or smaller than Forest Protocol |
| Parse time | <10ms per plan |
| Migration coverage | 100% of existing plans parseable |
| AGENTESE integration | All plan operations via `self.forest.*` |

---

## Part XI: Implementation Plan

### 11.1 Phase 1: Types & Parser (1 session)

```python
# impl/claude/protocols/garden/types.py
@dataclass
class GardenPlanHeader:
    path: str
    mood: str
    momentum: float
    trajectory: Trajectory
    season: Season
    last_gardened: date
    gardener: str
    letter: str
    resonates_with: list[str]
    entropy: EntropyBudget
```

### 11.2 Phase 2: Polynomial & Operad (1 session)

Implement `GardenPolynomial` and `GARDEN_OPERAD` with law verification.

### 11.3 Phase 3: AGENTESE Nodes (1 session)

Register `self.forest.plan.*` and `self.forest.session.*` paths.

### 11.4 Phase 4: Migration (1 session)

Write migration script, convert existing plans.

### 11.5 Phase 5: Sheaf Coherence (optional)

Implement `GardenSheaf` for cross-plan consistency checking.

---

## Appendix A: Full Header Schema

```yaml
# JSON Schema for validation
$schema: http://json-schema.org/draft-07/schema#
type: object
required: [path, mood, season]
properties:
  path:
    type: string
    pattern: ^self\.forest\.plan\.[a-z0-9-]+$
  mood:
    type: string
    enum: [excited, curious, focused, satisfied, stuck, waiting, tired, dreaming, complete]
  momentum:
    type: number
    minimum: 0
    maximum: 1
  trajectory:
    type: string
    enum: [accelerating, cruising, decelerating, parked]
  season:
    type: string
    enum: [SPROUTING, BLOOMING, FRUITING, COMPOSTING, DORMANT]
  last_gardened:
    type: string
    format: date
  gardener:
    type: string
  letter:
    type: string
  resonates_with:
    type: array
    items:
      type: string
  entropy:
    type: object
    properties:
      available:
        type: number
        minimum: 0
      spent:
        type: number
        minimum: 0
      sips:
        type: array
        items:
          type: string
```

---

## Appendix B: Connection to Gardener-Logos

The Garden Protocol inherits from Gardener-Logos (see `plans/_archive/complete/the-gardener.md`):

| Gardener-Logos | Garden Protocol |
|----------------|-----------------|
| `GardenState` | `GardenPolynomial` |
| `Season` enum | Same (SPROUTING, BLOOMING, etc.) |
| `Gesture` | Same structure |
| `momentum` | Same semantics |
| `rigidity` | Dropped (not needed for planning) |

The key insight: **Gardener-Logos was already implementing planning** through the tending metaphor. The Garden Protocol makes this explicit and extends it to plan files.

---

*"The garden tends itself, but only because we planted it together."*

*Spec version: 1.0 | Date: 2025-12-18*
