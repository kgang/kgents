# I-gent Time: Explicit Temporal Semantics

Time is a first-class citizen in I-gents. Every visualization includes temporal context, and time operations (rewind, play, step) are primary navigation verbs.

---

## Philosophy

> "The garden grows in time; the book accumulates pages. To observe without time is to see a corpse, not a life."

Most interfaces treat time as metadata—a timestamp column, a "last modified" field. I-gents treat time as **structure**. The timeline is not decoration; it is the skeleton upon which observation hangs.

---

## Time Representation

### Format

Time is displayed as elapsed duration since the relevant epoch:

```
t: HH:MM:SS
```

For longer durations:

```
t: DD:HH:MM:SS
```

For sub-second precision (when needed):

```
t: HH:MM:SS.mmm
```

### Examples

```
t: 00:14:32      # 14 minutes, 32 seconds
t: 01:23:45      # 1 hour, 23 minutes, 45 seconds
t: 03:12:00:00   # 3 days, 12 hours
t: 00:00:05.123  # 5 seconds, 123 milliseconds
```

---

## Epochs

Each visualization scale has its own epoch (time zero):

| Scale | Epoch | Meaning |
|-------|-------|---------|
| Glyph | Agent birth | When this agent was first instantiated |
| Card | Agent birth | Same as glyph |
| Page | Agent birth | Time since first activation |
| Garden | Session start | When the current session began |
| Library | System start | When the kgents system initialized |

### Epoch Selection Rationale

- **Glyph/Card/Page**: Agent-centric time answers "how long has this agent existed?"
- **Garden**: Session-centric time answers "how long have I been working?"
- **Library**: System-centric time answers "how long has the ecosystem been running?"

### Cross-Epoch Reference

When viewing an agent within a garden, both times may be relevant:

```
╔══ A-gent ════════════════════════════════════════════════╗
║  state: ● active                                         ║
║  agent time: 00:14:32    session time: 02:30:15          ║
╚══════════════════════════════════════════════════════════╝
```

---

## The Timeline View

Every scale supports a **timeline view** toggle, showing temporal evolution.

### Agent Timeline

```
┌─ A-gent timeline ────────────────────────────────────────────┐
│                                                              │
│  t=0        t=5        t=10       t=15       t=20    now     │
│  ├──────────┼──────────┼──────────┼──────────┼───────┤       │
│  ○          ◐          ●          ●          ●       ●       │
│  birth      wake       active     compose    ·       ·       │
│                                   with C                     │
│                                                              │
│  events:                                                     │
│  ────────────────────────────────────────────────────────    │
│  t=0   — created from spec/a-gents/README.md                 │
│  t=5   — activated by user request                           │
│  t=10  — first invocation received                           │
│  t=15  — composed with C-gent                                │
│                                                              │
│  [◀ rewind]  [▶ play]  [⏸ pause]  [▶▶ step]                  │
└──────────────────────────────────────────────────────────────┘
```

### Garden Timeline

```
┌─ garden timeline ────────────────────────────────────────────┐
│                                                              │
│  t=0        t=30m      t=1h       t=1.5h     t=2h     now    │
│  ├──────────┼──────────┼──────────┼──────────┼───────┤       │
│                                                              │
│  A: ○───────◐──────────●───────────────────────────────●     │
│  B: ────────○──────────────────────◐────────●──────────●     │
│  C: ──────────────────────────────────────────────◐────●     │
│  K: ●───────────────────────────────────────────────────●    │
│                                                              │
│  [◀ rewind]  [▶ play]  [⏸ pause]  [▶▶ step]                  │
└──────────────────────────────────────────────────────────────┘
```

### Library Timeline

```
┌─ library timeline ───────────────────────────────────────────┐
│                                                              │
│  t=0        t=1d       t=2d       t=3d       t=4d     now    │
│  ├──────────┼──────────┼──────────┼──────────┼───────┤       │
│                                                              │
│  main:      ████░░░░░░░░░░░░████████████████████████████     │
│  exp:       ░░░░░░░░████████████████████████░░░░░░░░░░░░     │
│  prod:      ░░░░░░░░░░░░░░░░░░░░░░░░████████████████████     │
│                                                              │
│  [◀ rewind]  [▶ play]  [⏸ pause]  [▶▶ step]                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Time Navigation

### Rewind

Move backward in time to observe past states.

**Semantics**:
- The view updates to show state at selected time
- All metrics, phases, and compositions reflect that moment
- Margin notes filter to show only notes up to that time
- Read-only: Cannot modify past states

**Implementation**: Uses D-gent state history (snapshots or event sourcing).

### Play

Animate forward from current position.

**Semantics**:
- Time advances automatically (configurable speed)
- Changes animate: phase transitions, composition edges appearing
- Margin notes accumulate as time passes
- Can play past-to-present or continue into live mode

**Speeds**:
- 1x: Real-time (1 second view = 1 second elapsed)
- 10x: Accelerated
- 0.1x: Slow motion

### Pause

Freeze at current time.

**Semantics**:
- View fixed at specific moment
- No updates even if agents change in real-time
- Useful for inspection and annotation
- Margin note addition still works (adds at current view time)

### Step

Advance one event at a time.

**Semantics**:
- Jump to next significant event (phase change, invocation, composition)
- Skip empty intervals
- Useful for debugging and analysis

---

## Time and Events

### Event Types

Events are timestamped occurrences recorded by agents:

| Event Type | Symbol | Description |
|------------|--------|-------------|
| Phase change | `◐→●` | Transition between phases |
| Invocation | `▶` | Agent received input |
| Completion | `✓` | Agent produced output |
| Error | `✗` | Agent encountered failure |
| Composition | `⊕` | Agent composed with another |
| Note | `✎` | Margin note added |

### Event Log

The timeline includes an event log:

```
┌─ events ─────────────────────────────────────────────────────┐
│  t=00:00:00   ◐→● A-gent activated                          │
│  t=00:05:00   ▶   A-gent invoked with "analyze patterns"     │
│  t=00:05:12   ✓   A-gent completed (3 patterns found)        │
│  t=00:10:00   ⊕   A-gent composed with C-gent                │
│  t=00:10:05   ▶   Pipeline invoked                           │
│  t=00:10:15   ✗   C-gent error: type mismatch                │
│  t=00:10:20   ✎   [kent] investigating type issue            │
└──────────────────────────────────────────────────────────────┘
```

---

## Time Density

Not all time is equally interesting. I-gents support **time density** visualization.

### Density Indicators

```
t=0        t=5        t=10       t=15       t=20
├──────────┼──────────┼──░░░░░░░░┼──────────┼───────┤
                        sparse      dense
```

**Legend**:
- `──` Dense activity (many events per unit time)
- `░░` Sparse activity (few events)
- Helps focus attention on interesting periods

### Auto-Zoom

When rewinding, timeline can auto-zoom to areas of high density:
- Compress boring periods (dormant stretches)
- Expand interesting periods (active work)

---

## Time and Memory

### D-gent Integration

Time travel requires state history, provided by D-gents:

| D-gent Type | Time Capability |
|-------------|-----------------|
| VolatileAgent | Current session only |
| PersistentAgent | Across sessions (disk) |
| StreamAgent | Full event sourcing |

**Event sourcing** is the richest time model:
- Every change is an event
- State at any time is computable by replaying events
- Perfect rewind fidelity

**Snapshot-based** is more efficient:
- Periodic state snapshots
- Approximate times between snapshots
- Lower storage overhead

### Time Horizon

The **time horizon** is how far back history is preserved:

| Horizon | Typical Use |
|---------|-------------|
| Session (volatile) | Debugging, exploration |
| Week (persistent) | Development cycle |
| Indefinite (stream) | Audit, compliance, research |

Configuration example:
```yaml
time_horizon:
  volatile: session
  persistent: 7d
  stream: indefinite
```

---

## Time Synchronization

### Multi-Agent Time

When viewing multiple agents, their times must be synchronized:

**Problem**: Agent A was born at t=0, Agent B at t=100.
**Solution**: Garden time uses session epoch; agent-specific time is secondary.

```
Garden time: 01:00:00 (session epoch)

  Agent A: t=01:00:00 (born at session start)
  Agent B: t=00:58:20 (born 1:40 into session)
```

### Distributed Systems

For library views spanning multiple systems:
- Use wall-clock time (UTC) for cross-system correlation
- Display local epoch for human readability
- Handle clock skew gracefully (bounded tolerance)

---

## Time Display Formats

### Compact (Glyphs, Cards)

```
t: 14:32
```

### Standard (Pages)

```
t: 00:14:32
```

### Extended (Timelines)

```
t=0min        t=15min       t=30min
```

### Absolute (Cross-Session)

```
2025-12-08 14:32:05 UTC
```

### Relative (Human-Friendly)

```
5 minutes ago
yesterday at 14:32
3 days, 2 hours ago
```

---

## Time and Contemplation

Time in I-gents is not just data—it supports **contemplative observation**:

### The Breath Cycle

The breath indicator pulses with time:
```
breath: ░░░░████░░░░  (exhale)
```
4-second cycle reminds the observer that time passes, the system is alive.

### Age Visualization

Long-running agents show their age:
```
┌─ K-gent ─────────────────┐
│ ● active                 │
│ age: 127 days            │  ← Been alive a long time
│ sessions: 89             │
└──────────────────────────┘
```

### Patience Indicators

When agents are waking or waning, show expected duration:
```
◐ waking... (est. 3s remaining)
```

This invites patience rather than anxiety.

---

## Time Anti-Patterns

I-gents must **never**:

1. ❌ Hide timestamps (time is always visible)
2. ❌ Use vague time ("recently" without specifics)
3. ❌ Conflate epochs (agent time ≠ session time)
4. ❌ Allow rewound views to modify state (time travel is read-only)
5. ❌ Lose event history silently (explicit horizon configuration)
6. ❌ Display future predictions as facts (only observed past)

---

## Time and Ethics

**Transparency**: Time information must be accurate and available.

**Honesty**: Rewound views clearly indicate they are historical.

**Control**: Users can configure time horizons (privacy-respecting).

**No Deception**: Animations and playback don't fabricate events.

---

## See Also

- [README.md](README.md) - I-gent philosophy
- [grammar.md](grammar.md) - Visual grammar (timeline elements)
- [states.md](states.md) - Phase transitions (time-ordered)
- [../d-gents/README.md](../d-gents/README.md) - State persistence (time travel backend)
- [../d-gents/protocols.md](../d-gents/protocols.md) - StreamAgent for event sourcing
