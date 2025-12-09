# Kairos: The Art of Timing

**When H-gents surface tensions and execute interventions.**

---

## Philosophy

> "The right word at the wrong time is the wrong word."
> — Ancient Greek rhetorical wisdom

*Kairos* (καιρός) is the Greek concept of the opportune moment—the qualitative time when conditions align for effective action. It contrasts with *chronos* (χρόνος), quantitative clock time.

The Mirror Protocol's power lies not just in detecting tensions, but in **surfacing them at the right moment**. A truth delivered at the wrong time creates defensiveness; the same truth at the right moment creates transformation.

---

## The Kairos Model

```python
@dataclass(frozen=True)
class Kairos:
    """An opportune moment for intervention."""

    moment_type: KairosType
    tension: Tension
    recommended_intervention: InterventionType
    cost_at_this_moment: float
    window_duration: timedelta | None  # How long this moment lasts
    evidence: list[str]  # Why this moment is opportune

class KairosType(Enum):
    """Types of opportune moments."""

    RETROSPECTIVE = "retrospective"     # Scheduled reflection time
    DECISION_POINT = "decision_point"   # Active decision being made
    PATTERN_PEAK = "pattern_peak"       # Behavior just repeated notably
    EXPLICIT_ASK = "explicit_ask"       # User requested feedback
    NEW_MEMBER = "new_member"           # Onboarding moment
    CRISIS_AFTERMATH = "crisis_after"   # Post-incident review
    MILESTONE = "milestone"             # Project completion/launch
    PLANNING = "planning"               # Strategic planning session
    ONE_ON_ONE = "one_on_one"           # Private conversation
    TEAM_SYNC = "team_sync"             # Regular team meeting
```

---

## Intervention Types

Different moments suit different interventions.

```python
class InterventionType(Enum):
    """Types of intervention by intrusiveness."""

    # Passive (always available, user-initiated)
    REFLECT = "reflect"       # Surface a pattern when asked
    REMEMBER = "remember"     # Recall relevant past decisions

    # Active (opt-in, system-initiated)
    REMIND = "remind"         # Gentle commitment tracking
    SUGGEST = "suggest"       # Propose principle-aligned actions
    DRAFT = "draft"           # Generate documentation

    # Structural (requires explicit approval)
    RITUAL = "ritual"         # Create recurring processes
    AUDIT = "audit"           # Systematic principle review
    ESCALATE = "escalate"     # Raise to leadership attention
```

### Intervention-Moment Matrix

| Moment Type | Best Interventions | Worst Interventions |
|-------------|-------------------|---------------------|
| Retrospective | REFLECT, AUDIT | REMIND, ESCALATE |
| Decision Point | REMEMBER, SUGGEST | AUDIT, RITUAL |
| Pattern Peak | REFLECT | ESCALATE |
| Explicit Ask | Any passive | None |
| New Member | REMEMBER | AUDIT, ESCALATE |
| Crisis Aftermath | REFLECT, RITUAL | All active |
| Milestone | REFLECT, DRAFT | REMIND |
| Planning | SUGGEST, RITUAL | REMIND |
| One-on-One | REFLECT, REMIND | ESCALATE |
| Team Sync | REFLECT | ESCALATE |

---

## The Intervention Cost Function

Before any intervention, calculate social cost at this moment.

```python
def calculate_intervention_cost(
    tension: Tension,
    context: OrganizationalContext,
    timing: datetime,
) -> float:
    """
    Estimate social friction of intervening NOW.

    High cost = wait for better moment
    Low cost = safe to proceed

    Returns: 0.0 (trivial) to 1.0+ (dangerous)
    """

    # Base cost from tension severity
    base_cost = tension.divergence

    # Visibility multiplier
    # Public interventions cost more than private
    visibility_multiplier = {
        "dm": 0.5,
        "small_group": 0.8,
        "team_channel": 1.2,
        "all_hands": 1.8,
        "external": 2.5,
    }[context.visibility]

    # Stress multiplier
    # Interventions during crunch cost more
    stress_multiplier = 1.0 + context.current_stress_level

    # Timing multiplier
    # Some moments naturally suit intervention
    timing_multiplier = moment_multiplier(timing, context)

    # Relationship multiplier
    # Trust reduces cost
    relationship_multiplier = 1.5 - (context.agent_trust_level * 0.8)

    # Recency multiplier
    # Recently addressed tensions are cheaper
    recency_multiplier = 1.0 + (days_since_last_mention(tension) * 0.01)

    return (
        base_cost
        * visibility_multiplier
        * stress_multiplier
        * timing_multiplier
        * relationship_multiplier
        * recency_multiplier
    )
```

### Moment Multiplier

```python
def moment_multiplier(timing: datetime, context: OrganizationalContext) -> float:
    """
    Calculate timing-based cost multiplier.

    Lower multiplier = better moment for intervention.
    """

    # Retrospective: Best time for reflection
    if is_retrospective_moment(timing, context):
        return 0.3

    # Decision point: Good for REMEMBER, bad for AUDIT
    if is_decision_moment(timing, context):
        return 0.6

    # Crisis: Worst time for non-essential intervention
    if context.in_crisis:
        return 2.0

    # End of sprint/quarter: Good for reflection
    if is_milestone_moment(timing, context):
        return 0.5

    # Monday morning: People are fresh
    if timing.weekday() == 0 and timing.hour < 12:
        return 0.8

    # Friday afternoon: People want to close loops
    if timing.weekday() == 4 and timing.hour > 14:
        return 1.3

    # Default
    return 1.0
```

---

## The Kairos Engine

```python
class KairosEngine:
    """
    Holds tensions until the right moment to surface them.

    This is the timing brain of the Mirror Protocol.
    """

    def __init__(
        self,
        intervention_threshold: float = 0.5,  # Max cost to proceed
        check_interval: timedelta = timedelta(hours=1),
    ):
        self.held_tensions: list[HeldTension] = []
        self.intervention_threshold = intervention_threshold
        self.check_interval = check_interval

    async def hold(self, tension: Tension) -> None:
        """Add a tension to be held until kairos arrives."""
        self.held_tensions.append(HeldTension(
            tension=tension,
            held_since=datetime.now(),
            best_cost_seen=float('inf'),
            best_moment_seen=None,
        ))

    async def check_for_kairos(
        self,
        context: OrganizationalContext,
    ) -> list[Kairos]:
        """
        Check all held tensions for opportune moments.

        Returns list of tensions ready for intervention.
        """
        ready = []

        for held in self.held_tensions:
            moment = await detect_moment_type(context)
            cost = calculate_intervention_cost(
                held.tension,
                context,
                datetime.now(),
            )

            # Track best moment seen
            if cost < held.best_cost_seen:
                held.best_cost_seen = cost
                held.best_moment_seen = moment

            # Check if we should proceed
            if cost < self.intervention_threshold:
                kairos = Kairos(
                    moment_type=moment,
                    tension=held.tension,
                    recommended_intervention=select_intervention(
                        held.tension,
                        moment,
                    ),
                    cost_at_this_moment=cost,
                    window_duration=estimate_window(moment),
                    evidence=collect_moment_evidence(context),
                )
                ready.append(kairos)

        return ready

    async def wait_for_kairos(self, tension: Tension) -> Kairos:
        """
        Hold a tension until the right moment arrives.

        This may wait hours, days, or weeks.
        """
        await self.hold(tension)

        while True:
            context = await get_current_context()
            ready = await self.check_for_kairos(context)

            for kairos in ready:
                if kairos.tension == tension:
                    self.held_tensions.remove(
                        next(h for h in self.held_tensions if h.tension == tension)
                    )
                    return kairos

            await asyncio.sleep(self.check_interval.total_seconds())
```

---

## Moment Detection

### Retrospective Detection

```python
async def detect_retrospective(context: OrganizationalContext) -> bool:
    """Detect if we're in a retrospective moment."""

    # Scheduled retrospective
    if context.current_meeting and "retro" in context.current_meeting.title.lower():
        return True

    # End of sprint
    if context.sprint_day == context.sprint_length:
        return True

    # Explicit reflection invitation
    if context.recent_messages and any(
        is_reflection_invitation(m) for m in context.recent_messages
    ):
        return True

    return False
```

### Decision Point Detection

```python
async def detect_decision_point(context: OrganizationalContext) -> bool:
    """Detect if an active decision is being made."""

    decision_indicators = [
        "should we",
        "what if we",
        "let's decide",
        "vote on",
        "proposal:",
        "option a or b",
        "recommend",
    ]

    if context.recent_messages:
        for msg in context.recent_messages[-10:]:
            if any(ind in msg.content.lower() for ind in decision_indicators):
                return True

    return False
```

### Crisis Detection

```python
async def detect_crisis(context: OrganizationalContext) -> bool:
    """Detect if organization is in crisis mode."""

    crisis_indicators = [
        context.incident_channel_active,
        context.after_hours_activity > 2.0,  # 2x normal
        context.message_velocity > 3.0,  # 3x normal
        any("urgent" in m.content.lower() for m in context.recent_messages),
        any("outage" in m.content.lower() for m in context.recent_messages),
    ]

    return sum(crisis_indicators) >= 2
```

---

## Intervention Selection

```python
def select_intervention(
    tension: Tension,
    moment: KairosType,
) -> InterventionType:
    """Select appropriate intervention for this tension at this moment."""

    # Explicit ask: Give what they asked for
    if moment == KairosType.EXPLICIT_ASK:
        return InterventionType.REFLECT

    # Retrospective: Reflection is natural
    if moment == KairosType.RETROSPECTIVE:
        if tension.divergence > 0.7:
            return InterventionType.AUDIT
        return InterventionType.REFLECT

    # Decision point: Surface relevant history
    if moment == KairosType.DECISION_POINT:
        return InterventionType.REMEMBER

    # New member: Light touch
    if moment == KairosType.NEW_MEMBER:
        return InterventionType.REMEMBER

    # Crisis aftermath: Start process improvement
    if moment == KairosType.CRISIS_AFTERMATH:
        return InterventionType.RITUAL

    # Planning: Suggest changes
    if moment == KairosType.PLANNING:
        return InterventionType.SUGGEST

    # Default: Passive reflection
    return InterventionType.REFLECT
```

---

## Anti-Kairos: When NOT to Intervene

### Absolute Blockers

These conditions block all intervention:

```python
def is_blocked(context: OrganizationalContext) -> tuple[bool, str]:
    """Check for absolute intervention blockers."""

    # Active crisis
    if context.in_crisis and context.crisis_severity > 0.8:
        return True, "Active crisis—all non-essential intervention blocked"

    # Sanctuary time
    if context.current_time in context.sanctuary_periods:
        return True, "Sanctuary period—no system-initiated contact"

    # Trust breach recovery
    if context.recent_trust_breach:
        return True, "Rebuilding trust—passive mode only"

    # Explicit opt-out
    if context.user_opted_out:
        return True, "User opted out of proactive intervention"

    return False, ""
```

### Cost Spikes

These conditions dramatically increase cost:

| Condition | Cost Multiplier | Reason |
|-----------|-----------------|--------|
| Crisis mode | 3.0x | People are overwhelmed |
| Recent layoffs | 2.5x | Organizational trauma |
| Quarterly close | 2.0x | Maximum stress |
| Friday 4pm | 1.5x | End-of-week fatigue |
| Major launch | 2.0x | Focus needed elsewhere |
| Conflict in channel | 2.0x | Emotions running high |

---

## The Patience Principle

The Kairos Engine embodies **patience as a virtue**.

```python
@dataclass
class PatienceMetrics:
    """Track the engine's patience."""

    tensions_held: int
    avg_hold_time: timedelta
    longest_hold: timedelta
    interventions_executed: int
    interventions_declined: int

    @property
    def patience_ratio(self) -> float:
        """Higher = more patient."""
        if self.interventions_executed == 0:
            return float('inf')
        return self.interventions_declined / self.interventions_executed
```

**Good patience ratios**:
- New system: 5:1 (mostly wait, rarely intervene)
- Established trust: 2:1 (selective intervention)
- High trust: 1:1 (balanced intervention)

---

## Escalation Tiers

When cost is too high but tension is urgent.

```python
class EscalationTier(Enum):
    """Levels of escalation for high-cost tensions."""

    NONE = "none"           # Wait for natural kairos
    SOFT = "soft"           # Private DM to relevant person
    MEDIUM = "medium"       # Raise in 1:1 or small group
    STRONG = "strong"       # Raise in team setting
    EMERGENCY = "emergency" # Immediate broadcast

def select_escalation(
    tension: Tension,
    days_held: int,
    urgency: float,
) -> EscalationTier:
    """Select escalation tier for persistent tensions."""

    # Very urgent: escalate quickly
    if urgency > 0.9:
        return EscalationTier.EMERGENCY

    # Urgent and held long: escalate
    if urgency > 0.7 and days_held > 7:
        return EscalationTier.STRONG

    # Moderate urgency, long hold: soft escalate
    if urgency > 0.5 and days_held > 14:
        return EscalationTier.MEDIUM

    # Low urgency, very long hold: consider soft
    if days_held > 30:
        return EscalationTier.SOFT

    return EscalationTier.NONE
```

---

## Implementation Notes

### State Management

```python
@dataclass
class HeldTension:
    """A tension being held by the Kairos Engine."""

    tension: Tension
    held_since: datetime
    best_cost_seen: float
    best_moment_seen: KairosType | None
    check_count: int = 0
    escalation_tier: EscalationTier = EscalationTier.NONE

    @property
    def days_held(self) -> int:
        return (datetime.now() - self.held_since).days

    @property
    def urgency(self) -> float:
        """Urgency increases with hold time and divergence."""
        base_urgency = self.tension.divergence
        time_multiplier = 1.0 + (self.days_held * 0.02)  # +2% per day
        return min(base_urgency * time_multiplier, 1.0)
```

### Persistence

Held tensions must survive restarts:

```python
async def persist_held_tensions(
    engine: KairosEngine,
    storage: Storage,
) -> None:
    """Save held tensions to persistent storage."""
    await storage.write(
        "kairos/held_tensions",
        [t.to_dict() for t in engine.held_tensions],
    )

async def restore_held_tensions(
    engine: KairosEngine,
    storage: Storage,
) -> None:
    """Restore held tensions from storage."""
    data = await storage.read("kairos/held_tensions")
    engine.held_tensions = [HeldTension.from_dict(d) for d in data]
```

---

## See Also

- [contradiction.md](contradiction.md) — How tensions are detected
- [sublation.md](sublation.md) — How tensions resolve
- [README.md](README.md) — H-gent overview
- [../../docs/mirror-protocol-implementation.md](../../docs/mirror-protocol-implementation.md) — Mirror Protocol plan

---

*"The right intervention at the wrong time is the wrong intervention. Patience is not passivity—it is wisdom about when to act."*
