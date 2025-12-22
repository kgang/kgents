# I-gent States: The Moon Phase Lifecycle

Agents have lifecycles. I-gents render these as **moon phases**—a visual metaphor that bridges computational states with contemplative observation.

---

## Philosophy

> "The moon does not hurry, yet it completes its cycle. Agents do not rush, yet they serve their purpose."

Moon phases communicate state through a single character while inviting patience. Unlike binary on/off indicators, phases acknowledge **gradients and transitions**. An agent is rarely simply "working" or "broken"—it is waking, active, waning, or empty.

---

## The Five Phases

### ○ Dormant (New Moon)

**Unicode**: U+25CB (White Circle)

**Meaning**: The agent exists but is not instantiated. It is defined in specification, available to invoke, but consumes no resources.

**Characteristics**:
- No active process
- Configuration loaded but not applied
- State persisted but not in memory
- Ready to activate on demand

**Transitions**:
- → ◐ Waking: Agent is being instantiated
- → ◌ Empty: Agent is deleted or errors before activation

**Analogy**: A book on a shelf—present, available, but not being read.

---

### ◐ Waking (First Quarter)

**Unicode**: U+25D0 (Circle with Left Half Black)

**Meaning**: The agent is transitioning from dormant to active. Initialization is in progress.

**Characteristics**:
- Process starting
- Resources being allocated
- Dependencies being resolved
- Configuration being applied
- D-gent state being loaded

**Transitions**:
- → ● Active: Initialization complete
- → ◌ Empty: Initialization failed
- → ○ Dormant: Activation cancelled

**Duration**: Typically brief (milliseconds to seconds). Extended waking suggests problems.

**Analogy**: Opening a book, finding your place, adjusting the light.

---

### ● Active (Full Moon)

**Unicode**: U+25CF (Black Circle)

**Meaning**: The agent is fully operational. It can receive invocations, participate in composition, and perform its function.

**Characteristics**:
- Process running
- Resources allocated
- Ready for input
- Composition-capable
- State in memory

**Sub-states** (optional detail):
- **Idle**: Active but awaiting input
- **Processing**: Currently handling an invocation
- **Blocked**: Waiting on external dependency

**Transitions**:
- → ◑ Waning: Graceful shutdown initiated
- → ◌ Empty: Unexpected failure/crash
- (Self-loop): Continues processing

**Analogy**: Reading the book, engaged with content.

---

### ◑ Waning (Last Quarter)

**Unicode**: U+25D1 (Circle with Right Half Black)

**Meaning**: The agent is transitioning from active to dormant. Graceful shutdown in progress.

**Characteristics**:
- Completing current work
- Flushing buffers/caches
- Persisting state to D-gent
- Releasing resources
- Closing connections

**Transitions**:
- → ○ Dormant: Shutdown complete
- → ◌ Empty: Shutdown failed (corrupted state)
- → ● Active: Shutdown cancelled (rare)

**Duration**: Should be bounded. Timeouts force transition to Empty if exceeded.

**Analogy**: Placing a bookmark, closing the book, returning it to the shelf.

---

### ◌ Empty (Void)

**Unicode**: U+25CC (Dotted Circle)

**Meaning**: The agent is in an error state, has been cleared, or failed to complete a lifecycle transition.

**Characteristics**:
- Process terminated abnormally
- State may be corrupted or lost
- Requires intervention to recover
- Not available for composition
- May have partial resources leaked

**Sub-states** (diagnosis aid):
- **Crashed**: Unexpected termination during Active
- **Corrupted**: State inconsistency detected
- **Timeout**: Transition exceeded time limit
- **Deleted**: Intentionally removed

**Transitions**:
- → ○ Dormant: After recovery/reset
- → ◐ Waking: Retry activation

**Analogy**: A book that fell behind the shelf—present somewhere, but inaccessible and needing retrieval.

---

## Phase Transition Diagram

```
                    ┌──────────────┐
                    │   ○ Dormant  │
                    └──────┬───────┘
                           │ activate
                           ▼
                    ┌──────────────┐
        ┌───────────│  ◐ Waking   │───────────┐
        │           └──────┬───────┘           │
        │ cancel           │ ready             │ fail
        ▼                  ▼                   ▼
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
 │   ○ Dormant  │   │   ● Active   │◄──│   ◌ Empty    │
 └──────────────┘   └──────┬───────┘   └──────────────┘
                           │                   ▲
                           │ shutdown          │ crash
                           ▼                   │
                    ┌──────────────┐           │
                    │  ◑ Waning    │───────────┘
                    └──────┬───────┘   fail
                           │ complete
                           ▼
                    ┌──────────────┐
                    │   ○ Dormant  │
                    └──────────────┘
```

---

## State Semantics by Agent Type

Different agent genera emphasize different phases:

### A-gents (Abstract/Art)
- Spend most time in **Active** (creative work)
- Waking loads context/style parameters
- Waning saves learned patterns

### B-gents (Bio/Scientific)
- Extended **Waking** for hypothesis loading
- **Active** during experiments
- **Waning** preserves findings to memory

### C-gents (Category Theory)
- **Dormant** is primary state (pure functions ready to compose)
- Brief transitions through Waking/Waning
- Stateless preference minimizes state complexity

### D-gents (Data)
- **Waking** loads persistent state
- **Active** manages in-memory state
- **Waning** is critical for data integrity

### H-gents (Dialectic)
- **Waking** loads thesis/antithesis
- **Active** during synthesis attempt
- **Empty** when tension cannot be resolved

### I-gents (Interface)
- **Active** while user is viewing
- **Dormant** when view is closed
- Minimal Waking/Waning (fast transitions)

### J-gents (JIT)
- Ephemeral: rapid phase cycling
- Many brief Active periods
- **Empty** on Ground collapse

### K-gent (Kent Simulacra)
- Long **Active** periods (session-length)
- **Waking** loads preferences/context
- **Waning** saves interaction learnings

### L-gents (Library)
- **Dormant** until queried
- **Active** during search
- Minimal Waning (read-heavy)

### T-gents (Testing)
- Controlled phase transitions for testing
- Intentionally enter **Empty** to test recovery
- Phase logging is primary output

---

## Phase Indicators in Context

### Glyph Level
Just the symbol:
```
● A
```

### Card Level
Symbol + label:
```
│ ● active     │
```

### Page Level
Symbol + label + duration:
```
║  state: ● active                     t: 00:14:32         ║
```

### Garden Level
Symbol only (density):
```
●A  ○B  ◐C  ●K
```

### Library Level
Aggregate (count by phase):
```
●3  ○2  ◐1  ◌1  # 3 active, 2 dormant, 1 waking, 1 empty
```

---

## Phase-Based Styling

When color is available:

| Phase | Symbol | Color | Intensity |
|-------|--------|-------|-----------|
| ○ Dormant | ○ | Gray | Dim |
| ◐ Waking | ◐ | Yellow | Pulsing |
| ● Active | ● | Green | Bright |
| ◑ Waning | ◑ | Orange | Fading |
| ◌ Empty | ◌ | Red | Static |

In monochrome, use font weight and animation:

| Phase | Monochrome |
|-------|------------|
| ○ Dormant | Normal weight |
| ◐ Waking | Blinking |
| ● Active | Bold |
| ◑ Waning | Dim |
| ◌ Empty | Inverted |

---

## Contemplative Observation

The moon phase metaphor invites **patience**:

- **○ Dormant**: "It rests. Let it rest."
- **◐ Waking**: "It is becoming. Patience."
- **● Active**: "It is present. Attend to it."
- **◑ Waning**: "It is completing. Allow it."
- **◌ Empty**: "Something is wrong. Investigate."

This framing resists the urge to constantly intervene. A dormant agent is not "broken"—it is sleeping. A waking agent does not need acceleration—it is becoming ready.

---

## Phase and Ethics

The Ethical principle manifests in phase transitions:

- **Waking must not be forced**: Allow proper initialization
- **Active must not be overloaded**: Respect capacity limits
- **Waning must not be rushed**: Allow graceful completion
- **Empty must be acknowledged**: Don't hide failures

An interface that hides phase information or lies about state violates transparency.

---

## State Persistence

Phases are not persisted directly—they are **computed from actual state**:

```python
def compute_phase(agent: Agent) -> Phase:
    if agent.process is None:
        if agent.error_state:
            return Phase.EMPTY
        return Phase.DORMANT
    if agent.process.is_starting:
        return Phase.WAKING
    if agent.process.is_stopping:
        return Phase.WANING
    if agent.process.is_running:
        return Phase.ACTIVE
    return Phase.EMPTY
```

This ensures the phase indicator is always **truthful**—it reflects reality, not cached status.

---

## Phase Transitions and D-gents

D-gents (Data agents) interact with phases at boundaries:

| Transition | D-gent Operation |
|------------|------------------|
| Dormant → Waking | `load()` state from persistence |
| Waking → Active | State now in memory |
| Active → Waning | Begin `save()` operations |
| Waning → Dormant | `save()` complete; state persisted |
| Any → Empty | State may be lost/corrupted |

---

## Phase and Composition

Phases affect composition capability:

| Phase | Can Compose? | Notes |
|-------|--------------|-------|
| ○ Dormant | Yes (lazy) | Will wake when invoked |
| ◐ Waking | Wait | Composition queued until Active |
| ● Active | Yes | Full composition capability |
| ◑ Waning | No | Reject new compositions; complete existing |
| ◌ Empty | No | Must recover first |

---

## Margin Note Integration

Phase transitions generate automatic margin notes:

```
┌─ margin notes ──────────────────────────────────────────┐
│ 00:00:00 — [system] phase: (init) → dormant             │
│ 00:05:00 — [system] phase: dormant → waking             │
│ 00:05:02 — [system] phase: waking → active              │
│ 00:15:00 — [system] phase: active → waning              │
│ 00:15:05 — [system] phase: waning → dormant             │
└─────────────────────────────────────────────────────────┘
```

These form the **heartbeat log** of agent lifecycle.

---

## See Also

- [README.md](README.md) - I-gent philosophy
- [grammar.md](grammar.md) - Visual grammar specification
- [time.md](time.md) - Temporal semantics (phase durations)
- [../anatomy.md](../anatomy.md) - Agent lifecycle (formal definition)
- [../d-gents/README.md](../d-gents/README.md) - State persistence
