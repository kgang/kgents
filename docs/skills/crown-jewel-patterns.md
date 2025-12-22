---
path: docs/skills/crown-jewel-patterns
status: active
progress: 100
last_touched: 2025-12-21
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Extracted from post-implementation reflection of the first completed Crown Jewel.
  These patterns are reusable across all Crown Jewels.
  Pattern 15 added from Morpheus/Chat debugging (hollow service anti-pattern).
  Updated to remove references to deleted Crown Jewels (only Brain remains).
phase_ledger:
  PLAN: complete
  REFLECT: complete
---

# Skill: Crown Jewel Implementation Patterns

> *"The first jewel teaches how to craft all the others."*

**Difficulty**: Intermediate
**Prerequisites**: `polynomial-agent.md`, `agentese-path.md`
**Source**: Post-implementation reflection from the first completed Crown Jewel

---

## Overview

These patterns emerged from implementing the first Crown Jewel to reach production maturity. They apply broadly to all Crown Jewels and represent tested, production-ready approaches.

---

## Pattern 1: Container Owns Workflow

**Problem**: Workflows (sessions, tasks, exhibitions) need lifecycle management within persistent state.

**Wrong**: Workflow creates Container
```python
# Workflow creates its own home → orphaned when workflow ends
session = GardenerSession(name="work")
garden = session.create_garden()  # Garden dies with session
```

**Right**: Container owns Workflow
```python
class Container:
    _workflow: Workflow | None = None
    workflow_id: str | None = None  # For history

    def get_or_create_workflow(self, name: str) -> Workflow:
        if self._workflow is None:
            self._workflow = create_workflow(name)
            self.workflow_id = self._workflow.id
            self._on_workflow_started()  # State transition
        return self._workflow

    async def on_workflow_complete(self):
        await self._on_workflow_ended()
        self._workflow = None
        # workflow_id preserved for history
```

**Benefits**:
- Container persists across workflows
- Clean lifecycle management
- History preserved via ID

**Apply to**:
| Jewel | Container | Workflow |
|-------|-----------|----------|
| Brain | Membrane | Crystal Session |
| (Future) | Gallery | Exhibition |
| (Future) | Team | Task |
| (Future) | Scenario | Simulation |

---

## Pattern 2: Enum Property Pattern

**Problem**: Enum values need associated metadata (colors, costs, valid transitions).

**Wrong**: External lookup dictionaries
```python
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()

# Scattered across codebase
STATUS_COLORS = {Status.PENDING: "yellow", Status.ACTIVE: "blue"}
STATUS_COSTS = {Status.PENDING: 0.1, Status.ACTIVE: 0.5}
```

**Right**: Properties on enum
```python
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETE = auto()

    @property
    def color(self) -> str:
        return {
            Status.PENDING: "yellow",
            Status.ACTIVE: "blue",
            Status.COMPLETE: "green",
        }[self]

    @property
    def cost(self) -> float:
        return {
            Status.PENDING: 0.1,
            Status.ACTIVE: 0.5,
            Status.COMPLETE: 0.0,
        }[self]

    @property
    def can_transition_to(self) -> set["Status"]:
        return {
            Status.PENDING: {Status.ACTIVE},
            Status.ACTIVE: {Status.COMPLETE, Status.PENDING},
            Status.COMPLETE: set(),
        }[self]
```

**Benefits**:
- Metadata co-located with enum
- IDE autocomplete works
- Type-safe access

**Apply to**:
| Jewel | Enum | Properties |
|-------|------|------------|
| Brain | CrystalType | weight, entropy_cost, search_boost |
| (Future) | BidState | can_outbid, min_increment |
| (Future) | AgentRole | capabilities, cost_multiplier |
| (Future) | MaskType | interactivity, visibility |

---

## Pattern 3: Multiplied Context Effect

**Problem**: Context should modulate user intent, not override it.

**Wrong**: Binary context
```python
# Context overrides intent entirely
if season == DORMANT:
    learning_rate = 0.0  # No learning possible
else:
    learning_rate = user_tone  # Full learning
```

**Right**: Multiplied effect
```python
# Context modulates intent smoothly
effective_rate = user_intent * context_factor

# Example:
learning_rate = input_intensity * mode_plasticity
# HIGH_PLASTICITY (0.9) × definitive (1.0) → 0.9 (aggressive)
# LOW_PLASTICITY (0.1) × tentative (0.3) → 0.03 (minimal)
```

**Benefits**:
- Smooth gradients, no cliff edges
- User intent always factors in
- No explosion of special cases

**Apply to**:
| Jewel | Intent | Context | Effect |
|-------|--------|---------|--------|
| Brain | capture_intensity | memory_mode | retention_strength |
| (Future) | bid_amount | market_heat | effective_bid |
| (Future) | urgency | agent_load | priority_score |
| (Future) | immersion | scenario_intensity | experience |

---

## Pattern 4: Signal Aggregation for Decisions

**Problem**: Complex decisions require weighing multiple factors.

**Wrong**: Boolean explosion
```python
if gesture_freq > 2 and entropy < 0.5 and session_active:
    transition = True
elif gesture_freq > 1 and entropy < 0.7:
    transition = True  # Different threshold, duplicated logic
```

**Right**: Confidence aggregation
```python
def evaluate_transition(signals: Signals) -> tuple[float, str]:
    confidence = 0.0
    reasons = []

    # Each signal contributes independently
    if signals.gesture_frequency > 2.0:
        confidence += 0.5
        reasons.append(f"High activity ({signals.gesture_frequency:.1f}/h)")
    elif signals.gesture_frequency > 1.0:
        confidence += 0.3
        reasons.append(f"Moderate activity ({signals.gesture_frequency:.1f}/h)")

    if signals.entropy_available > 0.5:
        confidence += 0.3
        reasons.append("Entropy available")

    if signals.session_active:
        confidence += 0.2
        reasons.append("Session active")

    return min(1.0, confidence), "; ".join(reasons)

# Usage
confidence, reason = evaluate_transition(signals)
if confidence >= THRESHOLD:
    suggest_transition(reason)
```

**Benefits**:
- Transparent (see why decision was made)
- Composable (add/remove signals easily)
- Tunable (adjust weights)
- Explains itself (reasons string)

**Apply to**:
| Jewel | Decision | Signals |
|-------|----------|---------|
| Brain | Crystal promotion | access_freq, semantic_density, age |
| (Future) | Agent recommendation | skill_match, availability, past_success |
| (Future) | Bid suggestion | market_value, creator_reputation, demand |

---

## Pattern 5: Dismissal Memory

**Problem**: Suggestions that are dismissed should not immediately reappear.

**Implementation**:
```python
from datetime import datetime, timedelta

_dismissed: dict[str, datetime] = {}
COOLDOWN_HOURS = 4

def dismiss(key: str) -> None:
    """Record that a suggestion was dismissed."""
    _dismissed[key] = datetime.now()

def should_suggest(key: str) -> bool:
    """Check if suggestion can be made (not recently dismissed)."""
    dismissed_at = _dismissed.get(key)
    if dismissed_at is None:
        return True
    return datetime.now() - dismissed_at >= timedelta(hours=COOLDOWN_HOURS)

def clear_dismissals(prefix: str) -> None:
    """Clear all dismissals matching prefix."""
    keys_to_remove = [k for k in _dismissed if k.startswith(prefix)]
    for key in keys_to_remove:
        del _dismissed[key]
```

**Benefits**:
- Respects user's "not now"
- Time-bounded (resurfaces when context may have changed)
- Memory-efficient (only stores timestamps)

**Apply to**:
| Jewel | Suggestion Type | Key Format |
|-------|-----------------|------------|
| Brain | Crystal cleanup | `{membrane_id}:cleanup:{date}` |
| (Future) | Drift alert | `{module}:{dependency}` |
| (Future) | Style recommendation | `{creator}:{style}` |
| (Future) | Team suggestion | `{task}:{agent_combo}` |

---

## Pattern 6: Async-Safe Event Emission

**Problem**: Sync methods need to emit events to async systems.

**Implementation**:
```python
import asyncio

def sync_method_with_event(self, data, emit_event=True):
    # ... sync state changes ...

    if emit_event:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._emit_event(data))
        except RuntimeError:
            # No running event loop - skip emission
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"No event loop for emission: {data}")

async def _emit_event(self, data):
    from protocols.synergy import get_synergy_bus
    event = create_event(data)
    await get_synergy_bus().emit(event)
```

**Benefits**:
- Core methods stay sync (simpler, easier to test)
- Events still emitted when async context exists
- Graceful degradation when no event loop

**Apply to**: All jewels that emit synergy events from state transitions.

---

## Pattern 7: Dual-Channel Output

**Problem**: CLI commands should serve both humans and agents.

**Implementation**:
```python
def _emit_output(
    human: str,
    semantic: dict,
    ctx: "InvocationContext | None",
) -> None:
    """Emit both human-readable and machine-readable output."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        # Fallback for direct invocation
        print(human)

# Usage
_emit_output(
    human=f"\n  {garden.season.emoji} Garden: {garden.name}\n",
    semantic={
        "garden_id": garden.garden_id,
        "season": garden.season.name,
        "health": garden.metrics.health_score,
    },
    ctx=ctx,
)
```

**Benefits**:
- Same command serves humans (terminal) and agents (JSON)
- No duplicate command implementations
- Consistent semantics across interfaces

**Apply to**: All CLI handlers via `protocols/cli/handlers/`.

---

## Pattern 8: Bounded History Trace

**Problem**: History should enable analysis without unbounded growth.

**Implementation**:
```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass(frozen=True)  # Immutable!
class HistoryEntry:
    action: str
    target: str
    timestamp: datetime = field(default_factory=datetime.now)

    def is_recent(self, hours: int = 24) -> bool:
        return datetime.now() - self.timestamp < timedelta(hours=hours)

class Container:
    history: list[HistoryEntry] = field(default_factory=list)
    MAX_HISTORY = 50

    def add_history(self, entry: HistoryEntry) -> None:
        self.history.append(entry)
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY:]

    @property
    def recent_diversity(self) -> int:
        """Count unique actions in recent history."""
        recent = [e for e in self.history if e.is_recent()]
        return len({e.action for e in recent})
```

**Benefits**:
- Bounded memory (never grows past MAX)
- Enables trajectory analysis (diversity, frequency)
- Immutable entries (facts, not mutable state)

**Apply to**:
| Jewel | History Type | Analysis |
|-------|--------------|----------|
| Brain | Captures | trajectory, frequency, diversity |
| (Future) | Bids | market trends, creator patterns |
| (Future) | Task assignments | agent utilization, success rates |
| (Future) | Player actions | engagement, decision patterns |

---

## Pattern 9: Directed State Cycle

**Problem**: State machines can have too many valid transitions, creating chaos.

**Wrong**: Fully-connected
```
Any state → Any other state (exponential complexity)
```

**Right**: Directed cycle
```
     ┌─────────────────────────────────────┐
     │                                     │
     ▼                                     │
  STATE_1 ──────► STATE_2 ──────► STATE_3
     ▲                                     │
     │                                     ▼
  STATE_5 ◄────── STATE_4 ◄─────────────┘
```

**Implementation**:
```python
TRANSITION_RULES: dict[State, list[State]] = {
    State.DORMANT: [State.SPROUTING],      # One forward
    State.SPROUTING: [State.BLOOMING],     # One forward
    State.BLOOMING: [State.HARVEST],       # One forward
    State.HARVEST: [State.COMPOSTING],     # One forward
    State.COMPOSTING: [State.DORMANT],     # Back to start
}

def can_transition(from_state: State, to_state: State) -> bool:
    return to_state in TRANSITION_RULES.get(from_state, [])
```

**Benefits**:
- One rule per state (simple)
- Natural rhythm (clear progression)
- Prevents chaotic jumping

**Apply to**:
| Jewel | Cycle |
|-------|-------|
| Brain | CAPTURING→PROCESSING→INDEXED→RECALLED→ARCHIVED→CAPTURING |
| (Future) | DRAFT→BIDDING→EVALUATION→AWARD→COMPLETE |
| (Future) | FORMING→ASSIGNED→EXECUTING→REVIEWING→DISBANDED |
| (Future) | SETUP→RUNNING→PAUSED→COMPLETE |

---

## Pattern 10: Operad Inheritance

**Problem**: New domains need composition grammar that builds on existing operads.

**Wrong**: Copy-paste operations
```python
# Duplicated operations across operads
JEWEL_OPERAD = Operad(
    operations={
        "split": Operation(...),  # Copied from DESIGN_OPERAD
        "stack": Operation(...),  # Copied again
        # ... all duplicated
    }
)
```

**Right**: Spread inheritance
```python
def create_soul_operad() -> Operad:
    from agents.operad import AGENT_OPERAD

    return Operad(
        name="SOUL_OPERAD",
        operations={
            # Soul-specific operations
            "introspect": Operation(arity=0, ...),
            "shadow": Operation(arity=1, ...),
            "dialectic": Operation(arity=2, ...),
            # Inherit all AGENT_OPERAD operations
            **AGENT_OPERAD.operations,
        },
        laws=[
            Law(name="introspection_idempotence", ...),
            # Inherit all AGENT_OPERAD laws
            *AGENT_OPERAD.laws,
        ],
    )
```

**Benefits**:
- Single source of truth for base operations
- Domain-specific operations compose with inherited ones
- Law inheritance ensures consistency

**Apply to**:
| Child Operad | Parent | Domain-Specific Ops |
|--------------|--------|---------------------|
| SOUL_OPERAD | AGENT_OPERAD | introspect, shadow, dialectic |
| TOWN_OPERAD | AGENT_OPERAD | greet, gossip, trade, solo |
| BRAIN_OPERAD | AGENT_OPERAD | capture, recall, associate |

---

## Pattern 11: Circadian Modulation

**Problem**: UI should feel different at different times of day without being disruptive.

**Implementation (Backend)**:
```python
class CircadianPhase(Enum):
    DAWN = "dawn"      # 6-10
    NOON = "noon"      # 10-16
    DUSK = "dusk"      # 16-20
    MIDNIGHT = "midnight"  # 20-6

    @classmethod
    def from_hour(cls, hour: int) -> "CircadianPhase":
        if 6 <= hour < 10: return cls.DAWN
        if 10 <= hour < 16: return cls.NOON
        if 16 <= hour < 20: return cls.DUSK
        return cls.MIDNIGHT

@dataclass(frozen=True)
class QualiaModifier:
    warmth: float    # -1 to 1 (additive)
    brightness: float  # 0 to 1 (multiplicative)
    tempo: float     # -1 to 1 (additive to animation speed)

CIRCADIAN_MODIFIERS = {
    CircadianPhase.DAWN: QualiaModifier(warmth=-0.2, brightness=0.8, tempo=0.2),
    CircadianPhase.NOON: QualiaModifier(warmth=0.0, brightness=1.0, tempo=0.0),
    CircadianPhase.DUSK: QualiaModifier(warmth=0.3, brightness=0.6, tempo=-0.2),
    CircadianPhase.MIDNIGHT: QualiaModifier(warmth=-0.1, brightness=0.3, tempo=-0.4),
}
```

**Implementation (Frontend)**:
```typescript
function useCircadian() {
  const [phase, setPhase] = useState<CircadianPhase>(() =>
    getCircadianPhase(new Date().getHours())
  );
  const [override, setOverride] = useState<CircadianPhase | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhase(getCircadianPhase(new Date().getHours()));
    }, 60000);  // Update every minute
    return () => clearInterval(interval);
  }, []);

  return {
    phase: override ?? phase,
    modifier: CIRCADIAN_MODIFIERS[override ?? phase],
    setOverride,
    clearOverride: () => setOverride(null),
    isOverridden: override !== null,
  };
}
```

**Benefits**:
- Subtle mood shifts (dusk = warmer, slower)
- Manual override for demos
- Backend + frontend alignment

**Apply to**:
| Jewel | What Changes | Effect |
|-------|-------------|--------|
| Brain | Crystal luminosity, recall speed | Warmer at dusk, slower at midnight |
| Town | Citizen activity patterns | More active at noon, reflective at midnight |
| (Future) | Dashboard accent color | Cooler in morning, warmer evening |

---

## Pattern 12: Law Honesty (STRUCTURAL Status)

**Problem**: Some operad laws express design constraints, not runtime-verifiable invariants.

**Wrong**: Pretend laws always pass
```python
def _verify_commutativity(*args) -> LawVerification:
    # This doesn't actually verify anything!
    return LawVerification(status=LawStatus.PASSED, ...)
```

**Right**: Honest STRUCTURAL status
```python
def _verify_pattern_commutativity(*args) -> LawVerification:
    """
    HONESTY: This law is STRUCTURAL, not runtime-verified.

    Pattern selection and parameter tuning DON'T fully commute because
    select_family resets config while tune_param modifies existing.
    Order matters for final values, but operations don't interfere.

    We mark as STRUCTURAL to indicate this is a design choice.
    """
    return LawVerification(
        law_name="pattern_commutativity",
        status=LawStatus.STRUCTURAL,
        message="Design choice: select_family resets, tune_param modifies",
    )
```

**When to use each status**:
| Status | When | Example |
|--------|------|---------|
| PASSED | Runtime verification succeeds | `qualia.blend(a,b,0.5) = qualia.blend(b,a,0.5)` |
| FAILED | Runtime verification fails | Composition produces wrong result |
| STRUCTURAL | Design constraint, not runtime | Commutativity is intentionally broken |
| SKIPPED | Cannot verify (missing deps) | External service unavailable |

**Benefits**:
- Honest documentation of law behavior
- Tests can expect STRUCTURAL (not fake PASSED)
- Design intent is clear

---

## Pattern 13: Contract-First Types (Phase 7)

**Problem**: BE (Python) and FE (TypeScript) type definitions drift because they're defined separately.

**Wrong**: Duplicate type definitions
```python
# Python backend
@dataclass
class TownManifest:
    name: str
    citizen_count: int  # Might rename to "count"
```

```typescript
// TypeScript frontend (may drift!)
interface TownManifest {
  name: string;
  citizenCount: number;  // Already drifted!
}
```

**Right**: `@node(contracts={})` is the authority
```python
from dataclasses import dataclass
from protocols.agentese.contract import Contract, Response
from protocols.agentese.registry import node

@dataclass
class TownManifestResponse:
    """Response for manifest aspect."""
    name: str
    citizen_count: int

@dataclass
class CitizenCreateRequest:
    name: str
    archetype: str

@dataclass
class CitizenCreateResponse:
    citizen_id: str
    success: bool

@node(
    "world.town",
    description="Agent Town Crown Jewel",
    contracts={
        # Perception aspects (no request needed)
        "manifest": Response(TownManifestResponse),
        # Mutation aspects (request + response)
        "citizen.create": Contract(CitizenCreateRequest, CitizenCreateResponse),
    }
)
@dataclass
class TownNode(BaseLogosNode):
    ...
```

**Frontend discovers at build time**:
```bash
# Generate TypeScript from BE contracts
npm run sync-types

# Verify types are in sync (CI)
npm run sync-types:check
```

**Benefits**:
- Single source of truth (Python dataclass)
- Type drift caught in CI before merge
- JSON Schema bridges Python → TypeScript
- Contract coverage tracked as metric

**Type Separation**:
| Category | Location | Source |
|----------|----------|--------|
| Contract Types | `_generated/` | BE discovery |
| Local Types | `_local.ts` | FE-only (colors, icons) |

**Apply to**: All Crown Jewel `@node` registrations.

**See**: `agentese-contract-protocol.md` for complete documentation.

---

## Pattern 14: Teaching Mode Toggle

**Problem**: Users need to toggle between "power user" and "learner" modes across the application.

**Wrong**: Component-level teaching flags scattered everywhere
```typescript
// Scattered boolean props that don't sync
<TracePanel showExplanation={showExplanation} />
<StateIndicator showTooltip={showTooltip} />
<OperadBadge showArity={showArity} />
// No centralized control, inconsistent behavior
```

**Right**: Global teaching mode via React context + localStorage
```typescript
// hooks/useTeachingMode.tsx
export function TeachingModeProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabled] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('kgents_teaching_mode');
    if (stored !== null) setEnabled(stored === 'true');
    setIsLoaded(true);
  }, []);

  const toggle = useCallback(() => {
    const next = !enabled;
    setEnabled(next);
    localStorage.setItem('kgents_teaching_mode', String(next));
  }, [enabled]);

  return (
    <TeachingModeContext.Provider value={{ enabled, toggle, isLoaded }}>
      {children}
    </TeachingModeContext.Provider>
  );
}

// Usage in components
function TracePanel({ events, maxEvents }: TracePanelProps) {
  const { enabled: teachingEnabled } = useTeachingModeSafe();

  return (
    <div>
      {/* Content always shown */}
      <Timeline events={events} maxEvents={maxEvents} />

      {/* Teaching callouts only when enabled */}
      {teachingEnabled && (
        <TeachingCallout category="conceptual">
          Every state change is recorded via the N-gent witness pattern.
        </TeachingCallout>
      )}
    </div>
  );
}
```

**Accessibility additions**:
```typescript
// StateIndicator with keyboard and screen reader support
<div
  role={isClickable ? 'button' : 'status'}
  tabIndex={isClickable ? 0 : undefined}
  aria-label={`${label} state, ${category}`}
  aria-live={animate ? 'polite' : undefined}
  onKeyDown={(e) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick();
    }
  }}
  className={cn(
    'transition-all duration-200',
    'motion-reduce:transition-none',
    animate && 'animate-pulse motion-reduce:animate-none',
    isClickable && 'focus-visible:outline focus-visible:outline-2'
  )}
>
```

**Benefits**:
- Centralized control via context
- Persists across sessions (localStorage)
- Graceful degradation (`useTeachingModeSafe`)
- Respects `prefers-reduced-motion`
- Full keyboard navigation
- Screen reader support via ARIA

**Components**:
| Component | Purpose |
|-----------|---------|
| `TeachingModeProvider` | Context provider wrapping app |
| `useTeachingMode()` | Hook for components inside provider |
| `useTeachingModeSafe()` | Hook with fallback for any component |
| `TeachingToggle` | Pre-built toggle button (compact or full) |
| `WhenTeaching` | Conditional render wrapper |
| `TeachingCallout` | Gradient callout with category styling |

**Apply to**: Town (citizen polynomial, trace), Brain (crystal metadata, associations).

---

## Pattern 15: No Hollow Services

**Problem**: Services with default constructors can be instantiated without required configuration, creating objects that pass type checks but fail at runtime.

**Wrong**: Default constructor bypasses DI
```python
# Direct instantiation creates hollow object
async def get_chat_factory():
    # ❌ Creates MorpheusPersistence with empty gateway - no providers!
    morpheus = MorpheusPersistence()
    return ChatServiceFactory(morpheus=morpheus)

# Later at runtime:
# "No provider found for model: claude-sonnet-4-20250514"
# Cryptic error because gateway has no adapters registered
```

**Right**: Always go through DI/bootstrap
```python
async def get_chat_factory():
    # ✅ Gets properly configured service with ClaudeCLIAdapter registered
    morpheus = await get_service("morpheus_persistence")
    return ChatServiceFactory(morpheus=morpheus)
```

**Why This Matters for Agent Systems**:

Agent services have deep dependency graphs. An LLM gateway isn't just a class—it's a *composition* of:
- Adapters (ClaudeCLI, OpenAI, Anthropic)
- Rate limiters per archetype
- Telemetry/observability hooks
- Provider routing by model prefix

When you instantiate directly, you get a **structurally valid but behaviorally hollow** object:
- ✅ Has all the right methods
- ✅ Passes type checks
- ✅ Can be assigned to the correct type
- ❌ Missing runtime configuration
- ❌ Fails with cryptic "no provider" errors

**Prevention Strategies**:

```python
# Option 1: Make wrong thing impossible (no default for critical deps)
class MorpheusPersistence:
    def __init__(self, gateway: MorpheusGateway):  # Required!
        if not gateway.list_providers():
            raise ValueError("Gateway must have at least one provider")
        self._gateway = gateway

# Option 2: Factory function only (hide constructor)
def create_morpheus_persistence() -> MorpheusPersistence:
    """Only way to create a properly configured instance."""
    gateway = MorpheusGateway()
    gateway.register_provider("claude-cli", ClaudeCLIAdapter(), "claude-")
    return MorpheusPersistence(gateway=gateway)

# Option 3: Builder with validation
MorpheusPersistence.builder() \
    .with_provider(ClaudeCLIAdapter()) \
    .build()  # Raises if no providers
```

**Detection**:

```python
# In bootstrap or app startup, verify services are wired
async def verify_services():
    morpheus = await get_service("morpheus_persistence")
    providers = morpheus.gateway.list_providers()
    if not providers:
        raise RuntimeError("Morpheus has no providers - check bootstrap wiring")
    logger.info(f"Morpheus OK: {len(providers)} providers registered")
```

**The Rule**:

> **Crown Jewels should NEVER be instantiated directly outside bootstrap.**
> Always go through `get_service()` or the DI container.
> If a service needs runtime wiring (adapters, buses, stores),
> the "convenient" direct instantiation is the wrong way.

**Benefits**:
- Catches misconfiguration at startup, not runtime
- Single source of truth for service creation
- Makes the "wrong way" awkward (or impossible)
- Cryptic runtime errors become clear startup errors

**Apply to**:
| Service | Required Wiring |
|---------|-----------------|
| MorpheusPersistence | Gateway with registered providers |
| ChatServiceFactory | MorpheusPersistence for LLM composition |
| BrainPersistence | TableAdapter + D-gent router |
| TownPersistence | Citizen + Conversation adapters |

---

## Quick Reference

| Pattern | Use When | Key Insight |
|---------|----------|-------------|
| Container Owns Workflow | Persistent state + transient workflows | Container persists; workflows come and go |
| Enum Property | Enum values need metadata | Co-locate metadata with enum |
| Multiplied Context | Context modulates intent | `effective = intent × context` |
| Signal Aggregation | Multi-factor decisions | Confidence + reasons string |
| Dismissal Memory | Suggestion systems | Time-bounded "not now" |
| Async-Safe Emission | Sync→async bridge | `create_task` with fallback |
| Dual-Channel Output | CLI for humans + agents | `emit(human, semantic)` |
| Bounded History | Trajectory analysis | Immutable + trim to MAX |
| Directed Cycle | State machine design | One forward per state |
| Operad Inheritance | Building on base operads | `**PARENT.operations` spread |
| Circadian Modulation | Time-of-day UI shifts | Phase → modifier → apply |
| Law Honesty | Laws that aren't runtime | STRUCTURAL status for design constraints |
| Contract-First Types | BE/FE type sync | `@node(contracts={})` is authority |
| Teaching Mode Toggle | Learner vs. power user UX | Context + localStorage + accessibility |
| **No Hollow Services** | Services needing runtime config | Always use DI; never direct instantiation |

---

## Related

- [polynomial-agent](polynomial-agent.md) — State machine fundamentals
- [test-patterns](test-patterns.md) — Testing these patterns
- [data-bus-integration](data-bus-integration.md) — Event-driven patterns

---

## Changelog

- 2025-12-21: Scrubbed references to deleted Crown Jewels (only Brain remains)
- 2025-12-19: Added Pattern 15 (No Hollow Services) from Morpheus/Chat provider debugging
- 2025-12-18: Added Pattern 14 (Teaching Mode Toggle) from design overhaul
- 2025-12-18: Added Pattern 13 (Contract-First Types) from Phase 7 Autopoietic Architecture
- 2025-12-18: Added patterns 10-12 (Operad Inheritance, Circadian Modulation, Law Honesty)
- 2025-12-16: Initial version from post-implementation reflection
