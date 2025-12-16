---
path: docs/skills/gardener-logos
status: active
progress: 100
last_touched: 2025-12-16
touched_by: claude-opus-4
blocking: []
enables: []
session_notes: |
  Created from gardener-logos-enactment reflection.
  Synthesizes all 8 phases of implementation (COMPLETE).
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: complete
  MEASURE: touched
  REFLECT: complete
entropy:
  planned: 0.10
  spent: 0.10
  returned: 0.00
---

# Skill: Gardener-Logos Patterns

> The garden tends itself, but it still needs a gardener. The gardener tends the garden, but is also tended BY the garden.

**Difficulty**: Intermediate
**Prerequisites**: AGENTESE paths, PolyAgent fundamentals
**Files**: `impl/claude/protocols/gardener_logos/`
**Tests**: 349+ (203 core + 69 CLI + 52 session + 25 auto-inducer)

---

## Overview

Gardener-Logos is the unified substrate for prompt management and development orchestration. It merges:

| Component | Purpose |
|-----------|---------|
| **Tending Calculus** | Gesture-based operations (observe, prune, graft, water, rotate, wait) |
| **Garden Seasons** | State machine for relationship-to-change (DORMANT → SPROUTING → BLOOMING → HARVEST → COMPOSTING) |
| **Plots** | Named regions of focus (linked to plans/jewels) |
| **Session Integration** | Phase → Season synergy (SENSE/ACT/REFLECT maps to seasons) |
| **Auto-Inducer** | Automatic season transition suggestions |

---

## Core Pattern 1: Tending Calculus

### The Six Verbs

```python
from protocols.gardener_logos.tending import (
    observe, prune, graft, water, rotate, wait,
    apply_gesture, TendingGesture, TendingVerb,
)

# OBSERVE - Nearly free (0.01 entropy), never changes state
gesture = observe("concept.prompt.task.review", "Checking health")

# PRUNE - Moderate cost (0.15), best in HARVEST/COMPOSTING
gesture = prune("concept.prompt.deprecated", "No longer used", tone=0.8)

# GRAFT - Expensive (0.20), best in SPROUTING
gesture = graft("concept.prompt.task.new", "Adding capability", tone=0.7)

# WATER - TextGRAD integration (0.10), season adjusts learning rate
gesture = water("concept.prompt.task.review", "More empathy needed", tone=0.6)

# ROTATE - Perspective change (0.05)
gesture = rotate("concept.gardener.season")

# WAIT - Free (0.00), intentional non-action
gesture = wait("Allowing ideas to settle")
```

### Applying Gestures

```python
from protocols.gardener_logos.garden import create_garden
from protocols.gardener_logos.tending import apply_gesture

garden = create_garden("My Garden")

result = await apply_gesture(
    garden,
    gesture,
    store=persistence_store,  # Optional: auto-saves
    emit_event=True,          # Synergy bus integration
    evaluate_transition=True, # Phase 8: Auto-Inducer
)

if result.success:
    print(f"Changes: {result.changes}")
    if result.suggested_transition:
        print(f"Suggestion: {result.suggested_transition.reason}")
```

**Key Insight**: Gestures have *tone* (0.0-1.0). Tone × Season Plasticity = Effective Learning Rate.

---

## Core Pattern 2: Garden Seasons

### Season Properties

```python
from protocols.gardener_logos.garden import GardenSeason

season = GardenSeason.SPROUTING

# Each season affects behavior:
season.emoji          # 🌱
season.plasticity     # 0.9 (how much change is accepted)
season.entropy_multiplier  # 1.5 (cost of operations)
```

| Season | Plasticity | Entropy | Best For |
|--------|------------|---------|----------|
| DORMANT 💤 | 0.1 | 0.5× | Observation, planning |
| SPROUTING 🌱 | 0.9 | 1.5× | New ideas, grafting |
| BLOOMING 🌸 | 0.3 | 1.0× | Crystallization, refinement |
| HARVEST 🌾 | 0.2 | 0.8× | Gathering, pruning |
| COMPOSTING 🍂 | 0.8 | 2.0× | Breaking down patterns |

### Season Transitions

```python
# Manual transition
garden.transition_season(
    GardenSeason.SPROUTING,
    reason="Starting new feature work",
    emit_event=True,  # Fires synergy event
)

# Auto-suggested via Auto-Inducer (Phase 8)
from protocols.gardener_logos.seasons import suggest_season_transition

suggestion = suggest_season_transition(garden)
if suggestion and suggestion.should_suggest:
    print(f"Consider: {suggestion.from_season} → {suggestion.to_season}")
    print(f"Why: {suggestion.reason}")
    print(f"Confidence: {suggestion.confidence:.0%}")
```

---

## Core Pattern 3: Session ↔ Garden Synergy

### Phase → Season Mapping

```python
# Garden owns session - phases sync with seasons
session = garden.get_or_create_session(
    name="Feature Work",
    plan_path="plans/core-apps/my-feature.md",
)

# Phase advancement triggers season evaluation
await garden.on_session_phase_advance(
    SessionPhase.SENSE,
    SessionPhase.ACT,
)
# May transition DORMANT → SPROUTING

await garden.on_session_phase_advance(
    SessionPhase.ACT,
    SessionPhase.REFLECT,
)
# May transition SPROUTING → BLOOMING
```

| Session Phase Change | Potential Garden Transition |
|---------------------|----------------------------|
| SENSE → ACT | DORMANT/COMPOSTING → SPROUTING |
| ACT → REFLECT | SPROUTING → BLOOMING |
| Multiple cycles (3+) | BLOOMING → HARVEST |
| Session complete | → HARVEST |

**Key Insight**: Creating a session when DORMANT auto-transitions to SPROUTING.

---

## Core Pattern 4: Plots as Focus Regions

```python
from protocols.gardener_logos.plots import PlotState, create_crown_jewel_plots

# Create plots for all crown jewels
plots = create_crown_jewel_plots()
for name, plot in plots.items():
    garden.plots[name] = plot

# Focus on a specific plot
garden.active_plot = "brain"
plot = garden.plots["brain"]

# Plots track:
plot.progress      # 0-1
plot.rigidity      # How much it resists change
plot.crown_jewel   # CrownJewel enum if applicable
plot.plan_path     # Link to Forest Protocol plan
```

---

## Core Pattern 5: Auto-Inducer

### Transition Signals

```python
from protocols.gardener_logos.seasons import TransitionSignals

signals = TransitionSignals.gather(garden)

# Signals measured:
signals.gesture_frequency    # Gestures per hour
signals.gesture_diversity    # Unique verbs used
signals.plot_progress_delta  # Progress change
signals.time_in_season_hours # How long in current season
signals.entropy_spent_ratio  # Budget consumption
signals.session_active       # Is session running?
signals.reflect_count        # REFLECT cycles completed
```

### Dismissal Memory

```python
from protocols.gardener_logos.seasons import (
    dismiss_transition,
    is_transition_dismissed,
)

# User dismisses a suggestion
dismiss_transition(
    garden.garden_id,
    GardenSeason.SPROUTING,
    GardenSeason.BLOOMING,
)

# Won't suggest again for 4 hours
assert is_transition_dismissed(garden.garden_id, ...)
```

---

## Core Pattern 6: Synergy Bus Integration

### Events Emitted

```python
# Gesture events (state-changing gestures only)
from protocols.synergy.events import create_gesture_applied_event

# Season change events
from protocols.synergy.events import create_season_changed_event

# Plot progress events
from protocols.synergy.events import create_plot_progress_event
```

### Cross-Jewel Handlers

| Handler | Trigger | Effect |
|---------|---------|--------|
| GardenToBrainHandler | Season changes, gestures | Auto-capture to Brain |
| GestaltToGardenHandler | Gestalt analysis | Update matching plots |

---

## Core Pattern 7: AGENTESE Integration

### Available Paths

```
concept.gardener.manifest       # Garden overview
concept.gardener.tend           # Apply gesture
concept.gardener.season.*       # Season operations
concept.gardener.plot.*         # Plot management
concept.gardener.session.*      # Session operations
concept.gardener.route          # NL → AGENTESE
concept.gardener.propose        # Suggestions
concept.prompt.*               # Delegated to Prompt Logos
```

### CLI Commands

```bash
kg garden                       # Show garden ASCII
kg garden season                # Show current season
kg garden health                # Show health metrics
kg garden transition BLOOMING   # Change season

kg tend observe concept.prompt  # Observe target
kg tend water concept.prompt.X  # TextGRAD nurturing
kg tend prune concept.prompt.Y  # Mark for removal

kg plot                         # List plots
kg plot brain                   # Show plot
kg plot focus brain             # Set active plot
```

---

## Key Learnings (Synthesized)

### Design Patterns

```
Tending ≠ CRUD: Gestures have tone, meaning, and relationship context
Season plasticity modulates change: High plasticity = aggressive TextGRAD
Entropy budget creates scarcity: Forces intentionality in gestures
Session → Season synergy: Phase changes suggest garden transitions
Auto-Inducer suggests, never auto-applies: User confirms transitions
Dismissal memory prevents nagging: 4-hour cooldown on dismissed suggestions
Synergy bus enables cross-jewel: Garden events flow to Brain, Gestalt
```

### Architecture Insights

```
GardenState owns GardenerSession: Unified state model
Gestures are immutable records: Append-only momentum trace
Season affects all operations: Plasticity × Tone = Effective Rate
Plots link to Forest Protocol: Each plot can reference a plan file
Persistence via SQLite: Gardens survive sessions
Event emission async-safe: Uses create_task when loop available
```

### Testing Patterns

```
203 tests across 6 test files
Property-based: Hypothesis for gesture sequences
Synergy mocking: Test events without full bus
Session lifecycle: Test phase → season transitions
Persistence round-trip: Save/load verification
```

---

## Common Pitfalls

### 1. Ignoring Season Context

**Wrong**:
```python
# Applying graft in DORMANT season
gesture = graft("concept.prompt.new", "Adding", tone=0.9)
await apply_gesture(garden, gesture)  # Low plasticity = weak effect
```

**Right**:
```python
# Check season first
if garden.season == GardenSeason.SPROUTING:
    gesture = graft("concept.prompt.new", "Adding", tone=0.9)
    await apply_gesture(garden, gesture)  # High plasticity = strong effect
else:
    garden.transition_season(GardenSeason.SPROUTING, "Ready to add")
```

### 2. Forgetting Entropy Cost

**Wrong**:
```python
# Many expensive gestures exhaust budget
for i in range(100):
    await apply_gesture(garden, graft(f"prompt.{i}", "Adding"))
    # Eventually entropy_spent > budget
```

**Right**:
```python
# Check entropy budget
if garden.metrics.entropy_spent < garden.metrics.entropy_budget * 0.8:
    await apply_gesture(garden, gesture)
else:
    await apply_gesture(garden, wait("Budget running low"))
```

### 3. Not Linking Plots to Plans

**Wrong**:
```python
# Orphan plot without plan reference
plot = PlotState(name="my-feature", path="concept.feature.mine")
garden.plots["mine"] = plot
```

**Right**:
```python
# Plot linked to Forest Protocol
plot = PlotState(
    name="my-feature",
    path="concept.feature.mine",
    plan_path="plans/my-feature.md",  # Forest Protocol link
    crown_jewel=CrownJewel.ATELIER,   # If applicable
)
```

---

## Reusable Patterns for Other Jewels

These patterns from Gardener-Logos apply broadly:

### The Ownership Pattern
**Use when**: A persistent container holds transient workflows.

```python
# Container owns Workflow, not vice versa
class Container:
    _workflow: Workflow | None = None

    def get_or_create_workflow(self, name: str) -> Workflow:
        if self._workflow is None:
            self._workflow = create_workflow(name)
            self._on_workflow_started()
        return self._workflow

    async def on_workflow_complete(self):
        self._workflow = None
        self._on_workflow_ended()
```

**Applicable to**: Atelier exhibitions, Coalition task assignments.

### The Signal Aggregation Pattern
**Use when**: Multiple factors contribute to a decision.

```python
def evaluate_recommendation(signals: Signals) -> tuple[float, str]:
    confidence = 0.0
    reasons = []

    if signals.factor_a > threshold_a:
        confidence += weight_a
        reasons.append("Factor A triggered")

    # ... more factors ...

    return min(1.0, confidence), "; ".join(reasons)
```

**Applicable to**: Coalition agent selection, Atelier bidding, Gestalt drift alerts.

### The Dismissal Memory Pattern
**Use when**: Suggestions should respect user's "not now" intent.

```python
_dismissed: dict[str, datetime] = {}
COOLDOWN_HOURS = 4

def should_suggest(key: str) -> bool:
    dismissed_at = _dismissed.get(key)
    if dismissed_at is None:
        return True
    return datetime.now() - dismissed_at >= timedelta(hours=COOLDOWN_HOURS)
```

**Applicable to**: Gestalt dependency alerts, Atelier style recommendations.

### The Enum Property Pattern
**Use when**: Enum values have associated metadata.

```python
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETE = auto()

    @property
    def can_transition_to(self) -> set["Status"]:
        return {
            Status.PENDING: {Status.ACTIVE},
            Status.ACTIVE: {Status.COMPLETE, Status.PENDING},
            Status.COMPLETE: set(),
        }[self]

    @property
    def color(self) -> str:
        return {Status.PENDING: "yellow", Status.ACTIVE: "blue", Status.COMPLETE: "green"}[self]
```

**Applicable to**: Task states, auction phases, document maturity levels.

### The Multiplied Context Pattern
**Use when**: Context should modulate effect, not replace it.

```python
# Intent × Context = Effective Value
effective_rate = user_intent * context_factor

# Examples:
# intent=0.9, context=0.5 → 0.45 (modulated)
# intent=0.9, context=1.0 → 0.9 (full effect)
```

**Applicable to**: Atelier bid amounts, Coalition urgency, TextGRAD learning rates.

---

## Related Skills

- `agentese-path.md` — Adding AGENTESE paths
- `polynomial-agent.md` — State machines
- `plan-file.md` — Forest Protocol plans
- `test-patterns.md` — Testing conventions

---

## Changelog

- 2025-12-16: Added reusable patterns section from post-implementation reflection
- 2025-12-16: Initial version from gardener-logos-enactment reflection
