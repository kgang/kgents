# The Witness

> *"I am the membrane between event and meaning. Through me, experience becomes memory."*

**Status:** Proposal
**Implementation:** `impl/claude/services/witness/` (32 tests)

---

## Purpose

The Witness is the **unified passive observer**—it captures, maps, and crystallizes experience without being asked. Unlike other Crown Jewels that must be invoked, The Witness runs passively once attuned, transforming ephemeral events into durable, navigable memory.

## Core Insight

**Experience Crystallization**: Events alone are noise. The Witness fuses observations + narrative + topology into *crystals*—structured, retrievable, semantically rich snapshots that persist across sessions and feed all other jewels.

---

## Metaphysical Position

```
                    ┌─────────────────────────────────────────┐
                    │              THE WITNESS                │
                    │                                         │
  Events ────────►  │   [Observe]    [Narrate]    [Map]      │
  (ephemeral)       │       │             │          │        │
                    │       └─────────────┼──────────┘        │
                    │                     ▼                   │
                    │         ┌───────────────────┐           │
                    │         │ Experience Crystal │          │
                    │         └───────────────────┘           │
                    │                     │                   │
                    └─────────────────────│───────────────────┘
                                          ▼
                                  D-gent (Memory)
                                          │
                                  ┌───────┼───────┐
                                  ▼       ▼       ▼
                               Brain  Gardener  Muse
```

The Witness occupies `time.*` context—it is fundamentally temporal. Everything flows through it into persistent memory.

---

## Categorical Foundation

### The Polynomial

```python
WITNESS_POLYNOMIAL = PolyAgent[WitnessState, SystemEvent, WitnessOutput](
    positions=frozenset({
        WitnessState.DORMANT,       # Not yet activated
        WitnessState.ATTUNING,      # Calibrating to user patterns
        WitnessState.WITNESSING,    # Passive capture (default running state)
        WitnessState.CRYSTALLIZING, # Synthesizing experience
        WitnessState.DREAMING,      # Background pattern detection
    }),
    directions=lambda state: {
        WitnessState.DORMANT: {"attune", "quickstart"},
        WitnessState.ATTUNING: {"complete_attunement", "abort"},
        WitnessState.WITNESSING: {
            "mark",           # User marks significant moment
            "crystallize",    # Force crystallization now
            "dream",          # Enter background analysis
            "disable",        # Return to dormant
        },
        WitnessState.CRYSTALLIZING: {"complete", "abort"},
        WitnessState.DREAMING: {"wake", "insight"},
    }[state],
    transition=witness_transition,
)
```

**Key Insight**: WITNESSING is the default state. The Witness runs passively once attuned—it's the only Crown Jewel with a persistent background state.

### The Operad

```python
WITNESS_OPERAD = Operad(
    name="WITNESS",
    extends=["TEMPORAL_OPERAD", "MEMORY_OPERAD"],
    operations={
        # Capture operations
        "observe": Operation(
            arity=1,
            output="Observation",
            effects=["reads:events"],
            description="Passive event capture without judgment"
        ),
        "mark": Operation(
            arity=1,
            output="Marker",
            effects=["writes:markers"],
            description="User signals 'this matters'"
        ),

        # Synthesis operations
        "narrate": Operation(
            arity="*",
            output="Narrative",
            effects=["reads:observations", "invokes:llm"],
            description="Transform observations into story"
        ),
        "chapter": Operation(
            arity=2,
            output="Chapter",
            effects=["writes:chapters"],
            description="Bound a narrative segment"
        ),

        # Topology operations
        "map": Operation(
            arity=0,
            output="TopologySnapshot",
            effects=["reads:filesystem"],
            description="Current codebase topology with heat"
        ),
        "territory": Operation(
            arity=1,
            output="TerritoryDetail",
            effects=["reads:filesystem"],
            description="Deep map of specific area"
        ),

        # The unique crystallization operation
        "crystallize": Operation(
            arity="*",
            output="ExperienceCrystal",
            effects=["reads:all", "writes:crystals", "invokes:llm"],
            description="Fuse observations + narrative + topology into crystal"
        ),
    },
)
```

### The Sheaf

```python
class WitnessSheaf(Sheaf[Session, LocalView, ExperienceCrystal]):
    """
    Coherent experience from distributed observations.

    Local sections (from different sources):
    - Terminal events (AGENTESE invocations)
    - File events (filesystem watcher)
    - Git events (commits, branches)
    - Time markers (user-defined significant moments)
    - Topology snapshots (codebase structure)

    Gluing condition: All events within a session agree on timeline.
    Global section: Unified ExperienceCrystal
    """

    def overlap(self, a: str, b: str) -> bool:
        """Two sources overlap if their events share timestamp space."""
        return True  # All sources share session timeline

    def compatible(self, section_a: LocalView, section_b: LocalView) -> bool:
        """Compatible if events don't contradict on shared timestamps."""
        return self._events_consistent(section_a, section_b)

    def glue(self, sections: dict[str, list[LocalView]]) -> ExperienceCrystal:
        """Fuse all local views into global crystal."""
        # Implementation in impl/
```

---

## Core Concepts

### Experience Crystal

```python
@dataclass(frozen=True)
class ExperienceCrystal:
    """
    The atomic unit of Witness memory.

    Unlike D-gent's generic storage, ExperienceCrystals are
    structured for retrieval, reflection, and cross-session learning.
    """
    session_id: str
    timeline: list[WitnessEvent]
    narrative: Narrative
    topology: TopologySnapshot
    heat: HeatMap
    markers: list[Marker]
    crystallized_at: datetime

    # Semantic handles for retrieval
    topics: frozenset[str]           # Auto-extracted themes
    entities: frozenset[str]         # Files, functions, classes mentioned
    mood: MoodVector                 # Affective signature
    complexity: float                # Session complexity score
```

### Event Types

```python
class EventType(Enum):
    INVOCATION = "invocation"  # AGENTESE command
    EDIT = "edit"              # File modification
    COMMIT = "commit"          # Git commit
    MARKER = "marker"          # User-defined moment
    NAVIGATION = "navigation"  # Directory/file navigation

@dataclass(frozen=True)
class WitnessEvent:
    type: EventType
    content: str
    timestamp: datetime
    codebase_position: str
    # Additional fields per type
```

---

## AGENTESE Interface

### Node Registration

```python
@node(
    path="time.witness",
    description="Unified passive observer—captures, maps, and crystallizes experience",
    contracts={
        "manifest": Response(WitnessManifestResponse),
        "attune": Contract(AttuneRequest, AttuneResponse),
        "mark": Contract(MarkRequest, MarkResponse),
        "crystallize": Response(ExperienceCrystal),
        "timeline": Response(TimelineResponse),
        "crystal": Contract(CrystalQuery, ExperienceCrystal),
        "territory": Contract(TerritoryRequest, TerritoryResponse),
    },
    effects=["reads:events", "reads:filesystem", "writes:crystals"],
    affordances={
        "guest": ["manifest", "timeline"],
        "observer": ["manifest", "timeline", "crystal", "territory"],
        "participant": ["manifest", "timeline", "crystal", "territory", "mark"],
        "architect": ["*"],
    },
)
```

### Aspects

| Aspect | Request | Response | Description |
|--------|---------|----------|-------------|
| `manifest` | — | WitnessManifestResponse | Current state, session duration, recent activity |
| `attune` | AttuneRequest | AttuneResponse | Start witnessing with calibration |
| `mark` | MarkRequest | MarkResponse | Mark significant moment |
| `crystallize` | — | ExperienceCrystal | Force crystallization now |
| `timeline` | — | TimelineResponse | View session events |
| `crystal` | CrystalQuery | ExperienceCrystal | Retrieve specific crystal |
| `territory` | TerritoryRequest | TerritoryResponse | Codebase topology with heat |

---

## kgentsd Integration

The Witness lives in the event stream. Unlike other jewels that wait to be invoked, The Witness is always WITNESSING when kgentsd is running.

### Event Sources

| Source | Events | Priority |
|--------|--------|----------|
| AGENTESE | Invocation, result | High |
| Filesystem | File modification, creation, deletion | Medium |
| Git | Commit, push, branch | Medium |
| User | Markers, navigation | High |

### Flux Lifting

```python
class WitnessFlux(FluxAgent[WitnessState, SystemEvent, ExperienceCrystal]):
    """
    The Witness lifted to continuous flow.

    Crystals are yielded when:
    - User marks with 'crystal' label
    - Natural break detected (15+ min pause)
    - Buffer size exceeds threshold (100 events)
    - Git push (session milestone)
    """
```

### Crystallization Triggers

| Trigger | Condition | Priority |
|---------|-----------|----------|
| User marker | Label contains "crystal" or "end" | Immediate |
| Natural break | 15+ minute gap in events | High |
| Buffer overflow | >100 events accumulated | Medium |
| Git push | Session milestone | High |

---

## Cross-Jewel Integration

### Consumers

| Consumer | What Witness Provides | Integration |
|----------|----------------------|-------------|
| **Brain** | ExperienceCrystals → Engrams | `brain.capture_from_witness()` |
| **Gardener** | Session activity → Season transitions | Season.plasticity_from_witness() |
| **Gestalt** | Heat map for architecture | `gestalt.overlay_heat()` |
| **Atelier** | Territory for context | `atelier.context_from_witness()` |
| **Muse** | Pattern detection input | Direct subscription |

### Events Emitted

```python
# Via SynergyBus
WitnessCrystalEmitted(crystal_id: str, session_id: str, topics: list[str])
WitnessMarkerCreated(marker_id: str, label: str, timestamp: datetime)
WitnessStateChanged(from_state: WitnessState, to_state: WitnessState)
```

---

## Visual Projections

### CLI

```
╔════════════════════════════════════════════════════════════════════╗
║  👁️  THE WITNESS                              ● WITNESSING  02:34:17 ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌─ TIMELINE ─────────────────────────────────────────────────────┐  ║
║  │  09:15  $ kg self.forest.manifest                              │  ║
║  │  09:23  ◆ MARKER: "Starting routing refactor"                  │  ║
║  │  09:25  🔧 hollow.py (+45/-12)                                 │  ║
║  │  09:45  ⚡ Committed: "feat(cli): Path-first routing"          │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  ┌─ TERRITORY ────────┐  ┌─ CRYSTALS (3) ─────────────────────────┐  ║
║  │  protocols/cli/    │  │  💎 "The Routing Discovery" (32 min)   │  ║
║  │  ├── hollow.py 🔥🔥│  │  💎 "Testing the Path" (28 min)        │  ║
║  │  ├── repl.py ●     │  └────────────────────────────────────────┘  ║
║  └────────────────────┘                                              ║
║   [M]ark moment  [C]rystallize now  [T]erritory  [Q]uiet            ║
╚════════════════════════════════════════════════════════════════════╝
```

### Web

```typescript
// services/witness/web/
├── WitnessChamber.tsx    // Main container
├── Timeline.tsx          // Event timeline with heat
├── TerritoryMap.tsx      // Codebase topology
├── CrystalViewer.tsx     // Crystal inspection
├── MarkerInput.tsx       // Quick marker creation
└── hooks/
    ├── useWitness.ts     // State subscription
    └── useCrystals.ts    // Crystal queries
```

---

## Laws

| # | Law | Status | Description |
|---|-----|--------|-------------|
| 1 | observation_immutability | VERIFIED | Observations are append-only; never modified after capture |
| 2 | crystal_completeness | VERIFIED | Every crystal contains observations + narrative + topology |
| 3 | passive_default | STRUCTURAL | WITNESSING state continues until explicitly changed |
| 4 | timeline_consistency | VERIFIED | Events within a crystal are strictly ordered by timestamp |
| 5 | marker_permanence | VERIFIED | Markers cannot be deleted, only annotated |

---

## Anti-Patterns

- **Active Witness**: Making the Witness require invocation for each observation defeats the purpose
- **Unbounded Buffer**: Must crystallize periodically; infinite accumulation causes memory issues
- **Narrative Coupling**: Narrative synthesis should be async; don't block event capture
- **Bypassing D-gent**: Crystals MUST go through D-gent for cross-jewel access
- **Heat Without Action**: Heat map is for visualization, not automatic intervention

---

## Implementation Reference

```
impl/claude/services/witness/
├── __init__.py           # Exports
├── core.py               # WitnessService
├── polynomial.py         # WITNESS_POLYNOMIAL
├── operad.py             # WITNESS_OPERAD
├── sheaf.py              # WitnessSheaf
├── flux.py               # WitnessFlux
├── crystal.py            # ExperienceCrystal dataclass
├── events.py             # Event types and handlers
├── topology.py           # Codebase mapping
├── narrative.py          # K-gent integration for synthesis
├── persistence.py        # D-gent adapter
├── node.py               # @node registration
└── web/                  # React components
```

---

*"The Witness sees. The Witness remembers. The Witness never interrupts."*

*Synthesized: 2025-12-19 | Category: time.* | Passive by Default*
