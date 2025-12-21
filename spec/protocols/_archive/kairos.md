# Kairos Protocol: Opportune Moment Detection

**Status:** Specification v1.0
**Depends On:** Mirror Protocol, EventStream, J-gents (entropy budgets)
**Part Of:** Mirror Protocol Phase 3
**Last Updated:** 2025-12-09

---

## Philosophy

> "There is a time for every purpose under heaven."

Phase 1 detects tensions. Phase 2 observes temporal patterns. Phase 3 answers: **When should we surface a tension?**

Not all truths should be spoken at all times. The **Kairos Controller** determines the opportune moment—when:
- The user has **attention** available (not overwhelmed)
- The tension is **salient** (momentum has built)
- The **cost** of intervention is justified by potential **value**

From Greek καιρός (kairos): the right, critical, or opportune moment.

---

## The Problem

Without timing intelligence:
- ❌ Tensions surface during flow states (disruptive)
- ❌ Minor tensions interrupt major work (priority inversion)
- ❌ Repeated reminders create notification fatigue
- ❌ Critical tensions lost in noise

With Kairos:
- ✅ Surface tensions when user pauses naturally
- ✅ Prioritize by severity × momentum × attention budget
- ✅ Defer low-urgency tensions to appropriate moments
- ✅ Emergency bypass for critical divergences

---

## Core Concepts

### 1. Attention Budget

User's available cognitive capacity at moment *t*:

```
A(t) = base_budget × context_multiplier × temporal_factor

Where:
- base_budget: User's default attention capacity (configured)
- context_multiplier: Activity state (0.1 = deep work, 1.0 = idle)
- temporal_factor: Time of day curve (peak hours vs fatigue)
```

**States**:
- `DEEP_WORK`: 0.1 (minimal interruptions, emergencies only)
- `ACTIVE`: 0.5 (working but interruptible)
- `TRANSITIONING`: 0.8 (between tasks, good moment)
- `IDLE`: 1.0 (no active work, optimal moment)

**Detection Signals** (filesystem/git/editor heuristics):
- Last git commit age
- Last file modification time
- Keyboard/editor activity patterns
- CLI command patterns (rapid vs sparse)

### 2. Tension Salience

How urgent is a tension at moment *t*?

```
S(t) = base_severity × momentum_factor × recency_weight

Where:
- base_severity: Intrinsic importance (0.0-1.0)
- momentum_factor: Semantic drift velocity (1.0 = stable, >1.5 = accelerating)
- recency_weight: Exponential decay (fresh tensions prioritized)
```

**Severity Tiers**:
- `CRITICAL`: 0.9+ (foundational contradiction detected)
- `HIGH`: 0.7-0.9 (significant divergence)
- `MEDIUM`: 0.4-0.7 (notable tension)
- `LOW`: 0.0-0.4 (minor inconsistency)

### 3. Thermodynamic Cost Function

Cost of surfacing a tension:

```
C(t) = (η·S(t) + γ·L(t)) / A(t)

Where:
- η: Severity weight (how bad is the tension?)
- S(t): Salience at time t
- γ: Load penalty (cost of interrupting current state)
- L(t): Cognitive load at time t (inferred from activity)
- A(t): Attention budget at time t

Lower cost = better moment to surface
```

**Intervention Rule**:
```
IF C(t) < threshold AND A(t) > min_attention:
    Surface tension
ELSE IF severity == CRITICAL:
    Emergency surface (override)
ELSE:
    Defer to next observation window
```

### 4. Entropy Budget

Maximum intervention rate over time window:

```python
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class EntropyBudget:
    """Limit intervention frequency to prevent fatigue."""

    window: timedelta              # Observation window (e.g., 1 hour, 1 day)
    max_interventions: int         # Max surfacings per window
    current_count: int = 0         # Current usage
    recharge_rate: float = 0.1     # Budget recovery per minute

    def can_intervene(self) -> bool:
        """Check if budget available."""
        return self.current_count < self.max_interventions

    def consume(self) -> bool:
        """Attempt to consume budget."""
        if self.can_intervene():
            self.current_count += 1
            return True
        return False

    def recharge(self, elapsed_minutes: float):
        """Recover budget over time."""
        recovered = int(elapsed_minutes * self.recharge_rate)
        self.current_count = max(0, self.current_count - recovered)
```

**Budget Levels** (user-configurable):
- `LOW`: 1 intervention per 4 hours (minimalist)
- `MEDIUM`: 3 interventions per 2 hours (balanced) **[DEFAULT]**
- `HIGH`: 6 interventions per hour (attentive)
- `UNLIMITED`: No limit (development/debugging)

---

## Kairos Controller Architecture

### State Machine

```
                    ┌───────────────┐
                    │   OBSERVING   │
                    │  (watch mode)  │
                    └───────┬───────┘
                            │
                   Tension detected
                            │
                            ▼
                    ┌───────────────┐
                    │  EVALUATING   │
                    │ (compute C(t)) │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │               │
            C(t) < threshold    C(t) >= threshold
                    │               │
                    ▼               ▼
            ┌───────────┐   ┌──────────────┐
            │ SURFACING │   │   DEFERRING  │
            │ (present) │   │ (queue/wait) │
            └─────┬─────┘   └──────┬───────┘
                  │                 │
                  │                 │
                  └────────┬────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ COOLDOWN     │
                    │ (recharge)   │
                    └──────────────┘
```

### Core Types

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class AttentionState(Enum):
    DEEP_WORK = 0.1
    ACTIVE = 0.5
    TRANSITIONING = 0.8
    IDLE = 1.0

class TensionSeverity(Enum):
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 0.75
    CRITICAL = 0.95

@dataclass
class KairosContext:
    """Current state for timing decision."""

    timestamp: datetime
    attention_state: AttentionState
    attention_budget: float         # A(t)
    cognitive_load: float           # L(t), 0.0-1.0
    recent_interventions: int       # Last N surfacings
    last_activity_age: float        # Minutes since last action

@dataclass
class TensionEvaluation:
    """Evaluation of when to surface a tension."""

    tension_id: str
    base_severity: TensionSeverity
    salience: float                  # S(t)
    momentum_factor: float           # From SemanticMomentumTracker
    cost: float                      # C(t)
    threshold: float                 # Decision boundary
    should_surface: bool
    defer_reason: str | None        # Why deferred (if applicable)

@dataclass
class InterventionRecord:
    """Log of past surfacings for pattern analysis."""

    timestamp: datetime
    tension_id: str
    severity: TensionSeverity
    attention_state: AttentionState
    user_response: str | None       # "dismissed", "engaged", "resolved"
```

### Controller Interface

```python
from typing import Protocol

class KairosController(Protocol):
    """Determines opportune moments for tension surfacing."""

    def evaluate_timing(
        self,
        tension: Tension,
        context: KairosContext,
        momentum: float
    ) -> TensionEvaluation:
        """Compute whether NOW is the right moment."""
        ...

    def defer_tension(
        self,
        tension_id: str,
        min_delay: timedelta,
        reason: str
    ):
        """Queue tension for later evaluation."""
        ...

    def surface_tension(
        self,
        tension: Tension,
        format: OutputFormat = OutputFormat.RICH
    ) -> InterventionRecord:
        """Present tension to user, record interaction."""
        ...

    def update_budget(self, elapsed: timedelta):
        """Recharge entropy budget based on elapsed time."""
        ...

    def get_intervention_history(
        self,
        window: timedelta
    ) -> list[InterventionRecord]:
        """Retrieve recent surfacing patterns."""
        ...
```

---

## Implementation Strategy

### Phase 3a: Static Timing (MVP)

**Goal**: Simple attention heuristics, no ML.

**Components**:
1. `SimpleAttentionDetector`: Filesystem/git activity → AttentionState
2. `StaticCostFunction`: Implement C(t) with fixed weights
3. `EntropyBudget`: Rate limiting
4. `KairosController`: Evaluation + surfacing logic

**CLI**:
```bash
# Autonomous watch mode (surfaces tensions when opportune)
kgents mirror watch ~/Vault --budget=medium

# Check current timing context (debug)
kgents mirror timing --show-state
```

**Tests**:
- Attention state detection from filesystem fixtures
- Cost function with various severity × budget combinations
- Entropy budget consumption + recharge
- Deferred tension queue management

### Phase 3b: Learning Timing (Advanced)

**Goal**: Learn user's optimal timing from interaction patterns.

**Additions**:
1. `InterventionAnalyzer`: ML model on user responses
2. `PersonalizedCostFunction`: User-specific weights (η, γ)
3. `PredictiveAttention`: Time-series forecasting of availability

**Data Collection**:
- User dismissal vs engagement rate by time-of-day
- Attention state at successful interventions
- Dwell time on surfaced tensions

---

## Ethical Considerations

### Attention Respect

- **Default: Medium Budget**: Conservative intervention rate
- **User Control**: Budget level configurable via `--budget` flag
- **Transparency**: Show why a tension was surfaced (`--explain`)
- **Opt-Out**: `--no-kairos` disables timing, surfaces all immediately

### Notification Fatigue Prevention

- **Cooldown Periods**: Minimum 30 minutes between surfacings (configurable)
- **Severity Escalation**: Only increase frequency if tensions worsen
- **Silence Mode**: Respect `DEEP_WORK` state (emergencies only)

### Emergency Override

```python
def should_override_budget(tension: Tension) -> bool:
    """Critical tensions bypass Kairos."""
    return (
        tension.severity == TensionSeverity.CRITICAL
        and tension.momentum_factor > 2.0  # Rapidly accelerating
    )
```

---

## Cost Function Calibration

### Default Weights

```python
DEFAULT_WEIGHTS = {
    "eta": 1.5,      # Severity weight (η)
    "gamma": 0.8,    # Load penalty (γ)
    "threshold": 0.6 # Decision boundary
}
```

### Example Calculations

**Scenario 1: High severity, low attention**
```
S(t) = 0.9 (CRITICAL severity)
L(t) = 0.7 (moderate cognitive load)
A(t) = 0.1 (DEEP_WORK state)

C(t) = (1.5×0.9 + 0.8×0.7) / 0.1
     = (1.35 + 0.56) / 0.1
     = 19.1  >> threshold (0.6)

Decision: DEFER (even though critical, user is deep in flow)
```

**Scenario 2: Medium severity, high attention**
```
S(t) = 0.5 (MEDIUM severity)
L(t) = 0.2 (light load)
A(t) = 1.0 (IDLE state)

C(t) = (1.5×0.5 + 0.8×0.2) / 1.0
     = (0.75 + 0.16) / 1.0
     = 0.91  > threshold (0.6)

Decision: DEFER (not urgent enough)
```

**Scenario 3: High severity, transitioning**
```
S(t) = 0.75 (HIGH severity)
L(t) = 0.3 (transitioning between tasks)
A(t) = 0.8 (TRANSITIONING state)

C(t) = (1.5×0.75 + 0.8×0.3) / 0.8
     = (1.125 + 0.24) / 0.8
     = 1.71  > threshold (0.6)

Decision: DEFER (wait for full idle)
```

Wait, these calculations are backwards—I defined it as "Lower cost = better moment" but the threshold logic is inverted. Let me fix:

### Corrected: Benefit Function

Actually, let's reframe as a **benefit** function (higher = better moment):

```
B(t) = A(t) × S(t) / (1 + L(t))

Where:
- B(t): Benefit of surfacing now
- A(t): Attention budget (0.1-1.0)
- S(t): Tension salience (0.0-1.0)
- L(t): Cognitive load (0.0-1.0, normalized)

Surface if: B(t) > threshold AND budget_available
```

**Revised Scenario 3**:
```
S(t) = 0.75
L(t) = 0.3
A(t) = 0.8

B(t) = 0.8 × 0.75 / (1 + 0.3)
     = 0.6 / 1.3
     = 0.46

Threshold: 0.4
Decision: SURFACE ✓ (good transitional moment)
```

---

## Integration with Mirror Protocol

### Watch Mode Flow

```python
async def watch_loop(
    vault_path: Path,
    budget: BudgetLevel,
    interval: timedelta = timedelta(minutes=10)
):
    """Autonomous observation + opportune surfacing."""

    kairos = KairosController(budget=budget)
    stream = GitStream(vault_path)
    witness = TemporalWitness(stream)

    while True:
        # 1. Observe new events
        drift_report = await witness.detect_drift()

        # 2. Detect tensions from drift
        tensions = await detect_tensions_from_drift(drift_report)

        # 3. Evaluate timing for each tension
        context = kairos.get_current_context()

        for tension in tensions:
            momentum = get_semantic_momentum(tension)
            eval = kairos.evaluate_timing(tension, context, momentum)

            if eval.should_surface:
                if kairos.budget.consume():
                    record = kairos.surface_tension(tension)
                    await handle_user_response(record)
                else:
                    kairos.defer_tension(tension.id, reason="budget_exhausted")
            else:
                kairos.defer_tension(tension.id, reason=eval.defer_reason)

        # 4. Recharge + sleep
        kairos.update_budget(interval)
        await asyncio.sleep(interval.total_seconds())
```

### CLI Extensions

```bash
# Start autonomous watch with medium intervention rate
kgents mirror watch ~/Vault --budget=medium

# Show current attention state + queued tensions
kgents mirror timing

# Force-surface next deferred tension (override Kairos)
kgents mirror surface --next

# View intervention history
kgents mirror history --window=7d

# Explain why a tension was deferred
kgents mirror explain <tension_id>
```

---

## Design Principles Applied

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Timing decisions respect user's flow state |
| **Curated** | Only surface tensions at opportune moments |
| **Ethical** | Attention budget prevents manipulation, user control paramount |
| **Joy-Inducing** | Interventions feel helpful, not nagging |
| **Composable** | Kairos composes with EventStream, SemanticMomentum, Mirror |
| **Generative** | Timing patterns emerge from interaction history |
| **Heterarchical** | Functional (evaluate) + autonomous (watch) modes |

---

## Future: Kairos Learning (Phase 3b+)

### Personalized Timing Models

- **Circadian Patterns**: Learn user's peak attention hours
- **Context Switching**: Detect "good break points" in workflow
- **Response Prediction**: ML model for dismiss vs engage likelihood

### Multi-User Organizations

- **Shared Attention**: Team-level budget (avoid bombarding whole team)
- **Role-Based Timing**: Engineers vs managers have different flow patterns
- **Collective Kairos**: Surface tensions at team retrospectives

---

## See Also

- [mirror.md](mirror.md) — Mirror Protocol overview
- [event_stream.md](event_stream.md) — EventStream + SemanticMomentumTracker
- [../j-gents/stability.md](../j-gents/stability.md) — Entropy budgets, Chaosmonger
- [../principles.md](../principles.md) — Ethical principle (attention respect)

---

*"The right word at the right moment—this is the art of rhetoric, and the science of Kairos."*
