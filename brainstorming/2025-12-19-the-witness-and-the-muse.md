# The Witness and The Muse: Two Oblique Crown Jewels

> *"The persona is a garden, not a museum."*
> *"Daring, bold, creative, opinionated but not gaudy."*

**Date**: 2025-12-19
**Synthesis from**: 2025-12-19-oblique-crown-jewels.md
**Method**: Combining the strongest ideas while deepening kgents ecosystem integration

---

## The Synthesis

From the original 7 Oblique Crown Jewels, two natural clusters emerged:

| Original Ideas | Combined Into | Why This Fusion |
|----------------|---------------|-----------------|
| Scribe + Chronicler + Cartographer | **The Witness** | All capture/record; Witness is the unified passive observer |
| Dramaturg + Sommelier | **The Muse** | Both analyze patterns to surface insight; Muse whispers story and guidance |

The **Librarian** and **Synthesizer** become aspects of these two, not separate jewels—respecting the Curated principle (fewer jewels, more depth).

---

## Crown Jewel 1: The Witness

> *"I am the membrane between event and meaning. Through me, experience becomes memory."*

### The Vision

The Witness is the **unified passive observer** that captures, maps, and records everything—without being asked. It combines:

- **Scribe's transcription** (what happened)
- **Chronicler's narrative** (what it means)
- **Cartographer's topology** (where it happened in the codebase)

But more than combining, The Witness introduces a new concept: **Experience Crystallization**—the transformation of ephemeral events into durable, navigable memory.

### The Metaphysical Position

The Witness occupies a unique position in the kgents ecosystem:

```
                    ┌─────────────────────────────────────────┐
                    │              THE WITNESS                │
                    │                                         │
  Events ────────►  │   [Scribe]     [Chronicler]   [Carto]  │
  (ephemeral)       │       │              │            │     │
                    │       └──────────────┼────────────┘     │
                    │                      ▼                  │
                    │          ┌───────────────────┐          │
                    │          │ Experience Crystal │         │
                    │          └───────────────────┘          │
                    │                      │                  │
                    └──────────────────────│──────────────────┘
                                           ▼
                                   D-gent (Memory)
                                           │
                                   ┌───────┼───────┐
                                   ▼       ▼       ▼
                                Brain  Gardener  The Muse
```

### The Polynomial

```python
WITNESS_POLYNOMIAL = PolyAgent[WitnessState, SystemEvent, ExperienceCrystal](
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

**Key Insight**: WITNESSING is the default state. Unlike other jewels that must be invoked, The Witness runs passively once attuned. It's the only Crown Jewel with a persistent background state.

### The Operad

```python
WITNESS_OPERAD = Operad(
    name="WITNESS",
    extends=["TEMPORAL_OPERAD", "MEMORY_OPERAD"],  # Inherits from time.* and self.*
    operations={
        # Capture operations (from Scribe)
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

        # Synthesis operations (from Chronicler)
        "narrate": Operation(
            arity="*",  # Variable arity
            output="Narrative",
            effects=["reads:observations", "invokes:llm"],
            description="Transform observations into story"
        ),
        "chapter": Operation(
            arity=2,  # (start_marker, end_marker)
            output="Chapter",
            effects=["writes:chapters"],
            description="Bound a narrative segment"
        ),

        # Topology operations (from Cartographer)
        "map": Operation(
            arity=0,
            output="TopologySnapshot",
            effects=["reads:filesystem"],
            description="Current codebase topology with heat"
        ),
        "territory": Operation(
            arity=1,  # Focus path
            output="TerritoryDetail",
            effects=["reads:filesystem"],
            description="Deep map of specific area"
        ),

        # Crystallization (the unique operation)
        "crystallize": Operation(
            arity="*",
            output="ExperienceCrystal",
            effects=["reads:all", "writes:crystals", "invokes:llm"],
            description="Fuse observations + narrative + topology into crystal"
        ),
    },
    laws=[
        Law(
            name="observation_immutability",
            description="Observations are append-only; never modified after capture",
            status="VERIFIED",
        ),
        Law(
            name="crystal_completeness",
            description="Every crystal contains observations + narrative + topology",
            status="VERIFIED",
        ),
        Law(
            name="passive_default",
            description="WITNESSING state continues until explicitly changed",
            status="STRUCTURAL",
        ),
    ],
)
```

### The Sheaf (Experience Coherence)

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
    Global section: Unified ExperienceCrystal with:
      - Timeline (ordered events)
      - Narrative (meaning derived from events)
      - Topology (where in codebase)
      - Heat map (activity intensity)
    """

    def glue(self, sections: dict[str, list[LocalView]]) -> ExperienceCrystal:
        # Timeline from all sources
        events = self._merge_timeline(
            sections["terminal"],
            sections["filesystem"],
            sections["git"],
        )

        # Narrative synthesis via K-gent
        narrative = await self._synthesize_narrative(events)

        # Topology from filesystem observations
        topology = self._extract_topology(sections["filesystem"])

        # Heat from activity frequency
        heat = self._compute_heat(events, topology)

        return ExperienceCrystal(
            session_id=self.session.id,
            timeline=events,
            narrative=narrative,
            topology=topology,
            heat=heat,
            markers=sections.get("markers", []),
            crystallized_at=datetime.now(),
        )
```

### The Experience Crystal

```python
@dataclass(frozen=True)
class ExperienceCrystal:
    """
    The atomic unit of The Witness's memory.

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

    def as_memory(self) -> DgentEntry:
        """Project into D-gent for long-term storage."""
        return DgentEntry(
            key=f"witness:crystal:{self.session_id}",
            value=self.to_json(),
            metadata={
                "type": "experience_crystal",
                "topics": list(self.topics),
                "mood": self.mood.to_dict(),
                "complexity": self.complexity,
            },
        )
```

### kgentsd Integration (Passive by Default)

```python
class WitnessFlux(FluxAgent[WitnessState, SystemEvent, ExperienceCrystal]):
    """
    The Witness lives in the event stream.

    Unlike other jewels that wait to be invoked, The Witness
    is always WITNESSING when kgentsd is running. This is the
    'set it and forget it' promise made concrete.
    """

    async def start(self, events: AsyncIterable[SystemEvent]) -> AsyncGenerator[ExperienceCrystal, None]:
        """
        Entry point when kgentsd starts.

        The Witness immediately enters WITNESSING state and
        begins passive capture. Crystals are yielded when:
        - User marks → crystallize
        - Natural break detected (15+ min pause)
        - Session ends
        """
        self.state = WitnessState.WITNESSING

        buffer: list[WitnessEvent] = []
        async for event in events:
            # Always capture
            observation = await self._observe(event)
            buffer.append(observation)

            # Check for crystallization triggers
            if self._should_crystallize(buffer, event):
                crystal = await self._crystallize(buffer)
                yield crystal
                buffer = []

    async def _observe(self, event: SystemEvent) -> WitnessEvent:
        """
        Transform raw event into WitnessEvent with context.

        Adds:
        - Timestamp with microsecond precision
        - Session context
        - Codebase position (current file, function if applicable)
        - Heat increment for activity tracking
        """
        match event:
            case AgenteseInvocation(path=path, observer=obs):
                return WitnessEvent(
                    type=EventType.INVOCATION,
                    content=f"$ kg {path}",
                    path=path,
                    observer=obs.archetype,
                    timestamp=event.timestamp,
                    codebase_position=await self._get_position(),
                )
            case FileModified(path=path):
                return WitnessEvent(
                    type=EventType.EDIT,
                    content=f"Edited: {path}",
                    path=path,
                    diff_summary=await self._get_diff_summary(path),
                    timestamp=event.timestamp,
                    codebase_position=path,
                )
            case GitCommit(sha=sha, message=msg):
                return WitnessEvent(
                    type=EventType.COMMIT,
                    content=f"Committed: {msg[:50]}",
                    sha=sha,
                    files_changed=event.files,
                    timestamp=event.timestamp,
                    codebase_position="git:HEAD",
                )
            case UserMark(label=label):
                return WitnessEvent(
                    type=EventType.MARKER,
                    content=label,
                    timestamp=event.timestamp,
                    codebase_position=await self._get_position(),
                    marker_id=uuid4(),
                )

    def _should_crystallize(self, buffer: list[WitnessEvent], event: SystemEvent) -> bool:
        """
        Determine if current buffer should crystallize.

        Triggers:
        - User marker with 'crystal' or 'end' label
        - 15+ minute gap in events (natural break)
        - Buffer size exceeds threshold (100 events)
        - Git push (session milestone)
        """
        if isinstance(event, UserMark) and "crystal" in event.label.lower():
            return True

        if buffer and self._gap_minutes(buffer[-1], event) > 15:
            return True

        if len(buffer) > 100:
            return True

        if isinstance(event, GitPush):
            return True

        return False
```

### AGENTESE Node Registration

```python
@node(
    path="time.witness",
    description="The unified passive observer—captures, maps, and crystallizes experience",
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
class WitnessNode:
    """
    AGENTESE interface to The Witness.

    The Witness runs passively via kgentsd, but users can also
    interact directly via these aspects.
    """

    @aspect("manifest")
    async def manifest(self, observer: Observer) -> WitnessManifestResponse:
        """Current Witness state and recent activity summary."""
        state = await self.witness.get_state()
        recent = await self.witness.get_recent_observations(limit=10)
        crystals = await self.witness.get_crystals(limit=5)

        return WitnessManifestResponse(
            state=state,
            session_duration=state.session_duration(),
            observations_count=len(recent),
            crystals_count=len(crystals),
            recent_activity=recent[:3],  # Just a taste
            current_territory=state.current_territory,
        )

    @aspect("mark")
    async def mark(self, observer: Observer, label: str) -> MarkResponse:
        """Mark a significant moment in the session."""
        marker = await self.witness.mark(label, observer)
        return MarkResponse(
            marker_id=marker.id,
            timestamp=marker.timestamp,
            label=marker.label,
            message="Moment marked. The Witness remembers.",
        )

    @aspect("crystallize")
    async def crystallize(self, observer: Observer) -> ExperienceCrystal:
        """Force crystallization of current observations."""
        crystal = await self.witness.crystallize()
        return crystal

    @aspect("timeline")
    async def timeline(self, observer: Observer, limit: int = 50) -> TimelineResponse:
        """View the session timeline."""
        events = await self.witness.get_timeline(limit=limit)
        return TimelineResponse(events=events)

    @aspect("crystal")
    async def crystal(self, observer: Observer, query: CrystalQuery) -> ExperienceCrystal:
        """Retrieve a specific crystal by ID or query."""
        if query.crystal_id:
            return await self.witness.get_crystal(query.crystal_id)
        else:
            return await self.witness.search_crystals(query.search)

    @aspect("territory")
    async def territory(self, observer: Observer, path: str | None = None) -> TerritoryResponse:
        """View the codebase topology around a path."""
        topo = await self.witness.get_territory(path or ".")
        return TerritoryResponse(
            path=path or ".",
            structure=topo.structure,
            heat=topo.heat,
            dependencies=topo.dependencies,
        )
```

### Visual Projection: The Witness Chamber

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  👁️  THE WITNESS                                    ● WITNESSING  02:34:17 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─ TIMELINE ─────────────────────────────────────────────────────────────┐  ║
║  │                                                                         │  ║
║  │  09:15  ┌───────────────────────────────────────────────┐               │  ║
║  │         │ $ kg self.forest.manifest                     │               │  ║
║  │         └───────────────────────────────────────────────┘               │  ║
║  │         → Forest health checked: 12 active, 789 tests                   │  ║
║  │                                                                         │  ║
║  │  09:23  ◆ MARKER: "Starting routing refactor"                          │  ║
║  │                                                                         │  ║
║  │  09:25  🔧 hollow.py (+45/-12)                                          │  ║
║  │  09:28  🔧 hollow.py (+8/-3)                                            │  ║
║  │  09:31  🔧 hollow.py (+15/-0)  ← Focus detected: hollow.py              │  ║
║  │                                                                         │  ║
║  │  09:45  ⚡ Committed: "feat(cli): Path-first routing"                   │  ║
║  │                                                                         │  ║
║  │  09:47  ◆ MARKER: "Routing complete, on to tests"                       │  ║
║  │                                                                         │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
║  ┌─ TERRITORY ───────────────────────┐  ┌─ CRYSTALS (3 this session) ──────┐  ║
║  │                                   │  │                                   │  ║
║  │     protocols/cli/               │  │  💎 "The Routing Discovery"        │  ║
║  │     ├── hollow.py  🔥🔥🔥        │  │     09:15-09:47 (32 min)           │  ║
║  │     ├── repl.py    ●             │  │     23 events, 2 markers           │  ║
║  │     └── main.py    ○             │  │                                   │  ║
║  │                                   │  │  💎 "Testing the Path"            │  ║
║  │     Legend: 🔥 blazing ● warm ○ cool  │  │     09:47-10:15 (28 min)           │  ║
║  │                                   │  │     18 events, 1 marker           │  ║
║  └───────────────────────────────────┘  └───────────────────────────────────┘  ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║  The Witness observes. The Witness remembers. The Witness never interrupts.  ║
║   [M]ark moment  [C]rystallize now  [T]erritory view  [Q]uiet (minimize)     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Cross-Jewel Integration

The Witness feeds every other Crown Jewel:

| Consumer Jewel | What Witness Provides | Integration Pattern |
|----------------|----------------------|---------------------|
| **Brain** | ExperienceCrystals become Engrams | `brain.capture_from_witness()` |
| **Gardener** | Session activity informs season transitions | Season.plasticity_from_witness() |
| **Gestalt** | Heat map for architecture visualization | `gestalt.overlay_heat()` |
| **Atelier** | Territory for context-aware design | `atelier.context_from_witness()` |
| **The Muse** | Pattern detection input | Direct subscription |

---

## Crown Jewel 2: The Muse

> *"I see the arc of your work. I know when you're rising, when you're stuck, when you're about to break through. I whisper—never shout."*

### The Vision

The Muse combines:
- **Dramaturg's story arc detection** (work has narrative structure)
- **Sommelier's contextual suggestions** (right tool, right moment)

But The Muse adds something neither had: **Aesthetic Sensitivity**—an understanding that work isn't just effective or ineffective, it's beautiful or ugly, joyful or grinding.

### The Metaphysical Position

```
                    ┌─────────────────────────────────────────┐
                    │               THE MUSE                   │
                    │                                          │
                    │   [Pattern Engine]  [Suggestion Engine]  │
                    │          │                  │            │
                    │          └──────────────────┘            │
                    │                    │                     │
  The Witness ─────►│        ┌───────────┴───────────┐         │
  (crystals)        │        ▼                       ▼         │
                    │   Story Arc              Whispered       │
                    │   Detection              Guidance        │
                    │        │                       │         │
                    └────────┼───────────────────────┼─────────┘
                             │                       │
                             ▼                       ▼
                        Terminal               Floating
                        Projection             Toast UI
```

### The Polynomial

```python
MUSE_POLYNOMIAL = PolyAgent[MuseState, PatternEvent, MuseOutput](
    positions=frozenset({
        MuseState.SILENT,           # Observing but not speaking
        MuseState.CONTEMPLATING,    # Pattern detected, deciding whether to speak
        MuseState.WHISPERING,       # Actively showing a suggestion
        MuseState.RESONATING,       # User engaged with suggestion (expanded)
        MuseState.REFLECTING,       # Post-engagement synthesis
        MuseState.DORMANT,          # Dismissed, in cooldown
    }),
    directions=lambda state: {
        MuseState.SILENT: {"pattern_detected", "user_summons"},
        MuseState.CONTEMPLATING: {"whisper", "suppress", "defer"},
        MuseState.WHISPERING: {"expand", "dismiss", "accept", "timeout"},
        MuseState.RESONATING: {"close", "act", "explore"},
        MuseState.REFLECTING: {"complete", "persist"},
        MuseState.DORMANT: {"cooldown_complete", "force_wake"},
    }[state],
    transition=muse_transition,
)
```

**Key Insight**: The Muse has a **SILENT** state that is not the same as DORMANT. Silent means actively observing but choosing not to speak. Dormant means cooldown after dismissal. The distinction preserves agency without nagging.

### The Operad

```python
MUSE_OPERAD = Operad(
    name="MUSE",
    extends=["PAIRING_OPERAD", "NARRATIVE_OPERAD"],
    operations={
        # Pattern detection (from Dramaturg)
        "detect_arc": Operation(
            arity=1,  # Takes event stream
            output="StoryArc",
            effects=["reads:witness"],
            description="Identify narrative structure in work"
        ),
        "identify_tension": Operation(
            arity=1,
            output="TensionLevel",
            effects=["reads:witness"],
            description="Measure current dramatic tension"
        ),
        "predict_climax": Operation(
            arity=1,
            output="ClimaxPrediction",
            effects=["reads:witness", "invokes:llm"],
            description="Forecast when breakthrough might occur"
        ),

        # Suggestion (from Sommelier)
        "pair": Operation(
            arity=2,  # (Context, ToolSpace)
            output="Suggestion",
            effects=["reads:context"],
            description="Match context to potential tool"
        ),
        "whisper": Operation(
            arity=1,  # Suggestion to surface
            output="Whisper",
            effects=["presents:ui"],
            description="Surface a suggestion gently"
        ),

        # The Muse's unique operations
        "sense_aesthetic": Operation(
            arity=1,
            output="AestheticReading",
            effects=["reads:witness"],
            description="Read the aesthetic quality of current work"
        ),
        "encourage": Operation(
            arity=0,
            output="Encouragement",
            effects=["presents:ui", "invokes:llm"],
            description="Offer genuine encouragement (not empty praise)"
        ),
        "reframe": Operation(
            arity=1,  # Takes stuck-point
            output="Reframe",
            effects=["invokes:llm"],
            description="Offer a new perspective on a blockage"
        ),
    },
    laws=[
        Law(
            name="whisper_not_shout",
            description="Max 1 active whisper at a time; queue others",
            status="VERIFIED",
        ),
        Law(
            name="dismissal_respected",
            description="Dismissed whispers have 4h cooldown on that topic",
            status="VERIFIED",
        ),
        Law(
            name="encouragement_earned",
            description="Encouragement only offered after genuine progress detected",
            status="STRUCTURAL",
        ),
        Law(
            name="aesthetic_sensitivity",
            description="Muse adjusts tone to match user's apparent mood",
            status="STRUCTURAL",
        ),
    ],
)
```

### The Story Arc Engine

```python
@dataclass
class StoryArc:
    """
    The dramatic structure of a work session.

    Based on Freytag's pyramid but adapted for development work:
    - EXPOSITION: Setting context, reading code, understanding
    - RISING_ACTION: Building complexity, experiments, attempts
    - CLIMAX: The breakthrough (or the wall)
    - FALLING_ACTION: Cleanup, refinement, polish
    - DENOUEMENT: Reflection, documentation, next steps
    """
    phase: ArcPhase
    tension: float  # 0.0-1.0
    dramatic_question: str  # What is at stake?
    predicted_climax: datetime | None
    confidence: float


class StoryArcDetector:
    """
    Detects narrative structure in work sessions.

    Uses signal aggregation (Pattern 4 from crown-jewel-patterns.md)
    to identify phase transitions.
    """

    async def analyze(self, crystals: list[ExperienceCrystal]) -> StoryArc:
        # Aggregate signals from crystals
        signals = [
            self._count_failures_then_success(crystals),
            self._measure_focus_intensity(crystals),
            self._detect_breakthrough_language(crystals),
            self._analyze_file_touch_patterns(crystals),
            self._measure_commit_frequency(crystals),
        ]

        phase, confidence = self._aggregate_to_phase(signals)
        tension = self._compute_tension(signals, phase)
        question = await self._infer_dramatic_question(crystals, phase)

        return StoryArc(
            phase=phase,
            tension=tension,
            dramatic_question=question,
            predicted_climax=self._predict_climax(tension, phase) if phase in (ArcPhase.RISING_ACTION,) else None,
            confidence=confidence,
        )

    def _aggregate_to_phase(self, signals: list[Signal]) -> tuple[ArcPhase, float]:
        """
        Pattern 4: Signal Aggregation.

        Multiple weak signals → strong phase detection with confidence.
        """
        # Each signal votes for phases
        votes: dict[ArcPhase, float] = defaultdict(float)
        for signal in signals:
            for phase, weight in signal.phase_weights.items():
                votes[phase] += weight * signal.confidence

        # Highest vote wins
        best_phase = max(votes, key=votes.get)
        confidence = votes[best_phase] / sum(votes.values())

        return best_phase, confidence
```

### The Whisper System

```python
@dataclass(frozen=True)
class Whisper:
    """
    A gentle suggestion from The Muse.

    Whispers are:
    - Non-intrusive (floating toast, not modal)
    - Dismissable (one click, 4h cooldown)
    - Contextual (based on current work)
    - Actionable (each has 1-3 concrete suggestions)
    """
    id: str
    topic: str
    opening: str          # The gentle hook
    suggestions: list[Suggestion]
    mood: MoodVector      # Matches user's apparent mood
    urgency: float        # 0.0-1.0 (affects persistence)
    expires_at: datetime


@dataclass(frozen=True)
class Suggestion:
    """A concrete action The Muse suggests."""
    label: str
    agentese_path: str    # What to invoke if accepted
    explanation: str      # Why this might help


class WhisperEngine:
    """
    Decides when and what to whisper.

    Respects:
    - Dismissal memory (Pattern 5 from crown-jewel-patterns.md)
    - One whisper at a time (Law: whisper_not_shout)
    - Context relevance threshold (0.7+)
    """

    def __init__(self, dismissal_memory: DismissalMemory):
        self.dismissals = dismissal_memory
        self.current_whisper: Whisper | None = None
        self.queue: list[Whisper] = []

    async def consider(
        self,
        arc: StoryArc,
        context: WorkContext,
        tool_space: ToolSpace,
    ) -> Whisper | None:
        """
        Consider whether to whisper.

        Returns None if:
        - Already whispering
        - No relevant suggestions
        - Topic recently dismissed
        - User in deep focus (high tension, no breaks)
        """
        # Respect focus
        if arc.tension > 0.8 and context.time_since_break < timedelta(minutes=30):
            return None

        # Find best pairing
        candidates = await self._find_pairings(context, tool_space)
        if not candidates:
            return None

        # Filter by dismissal memory
        candidates = [c for c in candidates if not self.dismissals.is_dismissed(c.topic)]
        if not candidates:
            return None

        # Best candidate becomes whisper
        best = max(candidates, key=lambda c: c.relevance)
        if best.relevance < 0.7:
            return None

        return self._create_whisper(best, arc)

    def _create_whisper(self, pairing: Pairing, arc: StoryArc) -> Whisper:
        """
        Create a whisper from a pairing.

        Whisper tone matches:
        - Story arc phase
        - User's apparent mood
        - Time of day (gentler in morning, more direct in afternoon)
        """
        mood = self._read_mood(arc)
        opening = self._compose_opening(pairing, mood, arc.phase)

        return Whisper(
            id=str(uuid4()),
            topic=pairing.topic,
            opening=opening,
            suggestions=pairing.suggestions,
            mood=mood,
            urgency=self._compute_urgency(pairing, arc),
            expires_at=datetime.now() + timedelta(minutes=5),
        )

    def _compose_opening(
        self,
        pairing: Pairing,
        mood: MoodVector,
        phase: ArcPhase,
    ) -> str:
        """
        Compose the opening line of a whisper.

        Varies by context:
        - RISING_ACTION: "You're building something..."
        - STUCK: "I notice you've been wrestling with..."
        - BREAKTHROUGH: "That was a breakthrough. While it's fresh..."
        """
        templates = {
            (ArcPhase.RISING_ACTION, "high_energy"): [
                "You're building momentum on {topic}. A thought...",
                "The pattern emerging around {topic} reminds me...",
            ],
            (ArcPhase.RISING_ACTION, "low_energy"): [
                "You've been working on {topic} for a while. Maybe...",
                "A gentle suggestion about {topic}...",
            ],
            (ArcPhase.CLIMAX, "any"): [
                "That was a breakthrough. While it's fresh, consider...",
                "The {topic} work just clicked. Capture it with...",
            ],
            (ArcPhase.FALLING_ACTION, "any"): [
                "Now that {topic} is settling, you might...",
                "Polish time. For {topic}, consider...",
            ],
        }

        key = (phase, self._energy_level(mood))
        candidates = templates.get(key, templates[(phase, "any")])
        return random.choice(candidates).format(topic=pairing.topic)
```

### AGENTESE Node Registration

```python
@node(
    path="self.muse",
    description="Pattern detection and contextual guidance—whispers story and suggestion",
    contracts={
        "manifest": Response(MuseManifestResponse),
        "arc": Response(StoryArc),
        "tension": Response(TensionResponse),
        "whisper": Response(Whisper | None),
        "encourage": Response(Encouragement),
        "reframe": Contract(ReframeRequest, ReframeResponse),
        "summon": Response(MuseSummonResponse),
    },
    effects=["reads:witness", "presents:ui", "invokes:llm"],
    affordances={
        "guest": ["manifest", "arc"],
        "observer": ["manifest", "arc", "tension"],
        "participant": ["manifest", "arc", "tension", "whisper", "encourage"],
        "architect": ["*"],
    },
)
class MuseNode:
    """
    AGENTESE interface to The Muse.

    The Muse runs passively (like The Witness) but can also
    be summoned directly for guidance.
    """

    @aspect("manifest")
    async def manifest(self, observer: Observer) -> MuseManifestResponse:
        """Current Muse state and activity."""
        state = await self.muse.get_state()
        arc = await self.muse.current_arc()
        return MuseManifestResponse(
            state=state,
            current_arc_phase=arc.phase,
            tension=arc.tension,
            dramatic_question=arc.dramatic_question,
            whispers_today=await self.muse.count_whispers_today(),
            dismissals_active=await self.muse.count_active_dismissals(),
        )

    @aspect("arc")
    async def arc(self, observer: Observer) -> StoryArc:
        """Get the current story arc analysis."""
        return await self.muse.current_arc()

    @aspect("whisper")
    async def whisper(self, observer: Observer) -> Whisper | None:
        """Get the current whisper (if any)."""
        return self.muse.current_whisper

    @aspect("encourage")
    async def encourage(self, observer: Observer) -> Encouragement:
        """
        Request encouragement.

        Unlike automatic whispers, this is user-initiated.
        The Muse will offer genuine encouragement based on
        detected progress (not empty praise).
        """
        crystals = await self.witness.get_recent_crystals(limit=3)
        progress = await self.muse.detect_progress(crystals)

        if not progress.significant:
            return Encouragement(
                message="You're in the work. Sometimes progress is invisible.",
                evidence=[],
                suggestion=None,
            )

        return Encouragement(
            message=await self._compose_encouragement(progress),
            evidence=progress.evidence[:3],
            suggestion=progress.next_step,
        )

    @aspect("reframe")
    async def reframe(self, observer: Observer, stuck_point: str) -> ReframeResponse:
        """
        Request a reframe on a stuck point.

        The Muse will analyze the stuck point and offer
        alternative perspectives.
        """
        arc = await self.muse.current_arc()
        context = await self.witness.get_recent_context()

        reframe = await self.muse.generate_reframe(
            stuck_point=stuck_point,
            arc=arc,
            context=context,
        )

        return ReframeResponse(
            stuck_point=stuck_point,
            reframe=reframe.perspective,
            questions=reframe.clarifying_questions,
            suggestions=reframe.concrete_steps,
        )

    @aspect("summon")
    async def summon(self, observer: Observer) -> MuseSummonResponse:
        """
        Summon The Muse explicitly.

        Bypasses the normal whisper timing to get immediate
        suggestions based on current context.
        """
        context = await self.witness.get_recent_context()
        arc = await self.muse.current_arc()

        # Force consideration without timing constraints
        suggestions = await self.muse.force_suggestions(context, arc)

        return MuseSummonResponse(
            arc=arc,
            suggestions=suggestions,
            message="The Muse attends.",
        )
```

### Visual Projection: The Whisper

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  💫 The Muse whispers:                                          [×] Dismiss │
│                                                                             │
│  "You've been building routing logic for 47 minutes. The pattern emerging  │
│   reminds me of AGENTESE path composition. Consider:                        │
│                                                                             │
│    → kg time.witness.crystallize     Capture this before you forget        │
│    → kg concept.operad.manifest      See the composition grammar           │
│    → kg self.brain.capture           Note the insight for later            │
│                                                                             │
│  [1] Crystallize  [2] Operad  [3] Brain  [Esc] Not now (4h cooldown)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual Projection: The Story Arc

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎭 THE MUSE: Story Arc                                   ● SILENT          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                                         ╱╲                                   ║
║                                        ╱  ╲  CLIMAX (predicted: ~11:30)     ║
║                                       ╱    ╲ "The routing works"             ║
║                              ╱╲      ╱      ╲                                ║
║                             ╱  ╲    ╱        ╲                               ║
║                            ╱    ╲  ╱          ╲                              ║
║             ╱╲            ╱      ╲╱            ╲                             ║
║            ╱  ╲          ╱         ← YOU ARE HERE                           ║
║           ╱    ╲        ╱                        ╲                           ║
║          ╱      ╲      ╱                          ╲                          ║
║  ───────╱        ╲────╱                            ╲───────────────          ║
║                                                                               ║
║   EXPOSITION       RISING ACTION           FALLING      DENOUEMENT           ║
║   "Understanding   "Building it"           "Polish"     "Document"           ║
║    the problem"                                                              ║
║                                                                               ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║  Dramatic Question: "Can path-first routing replace the legacy dispatch?"   ║
║  Tension: ████████░░ 75%                                                    ║
║  Mood: Focused, determined                                                   ║
║                                                                               ║
║  ══════════════════════════════════════════════════════════════════════════  ║
║   [A]rc view  [T]ension history  [S]ummon muse  [W]hisper settings  [Q]uit  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### kgentsd Integration

```python
class MuseFlux(FluxAgent[MuseState, WitnessEvent, MuseOutput]):
    """
    The Muse listens to The Witness.

    Unlike The Witness which captures raw events, The Muse
    only processes ExperienceCrystals and high-level patterns.
    This creates a clear dependency chain:

        SystemEvents → Witness → Crystals → Muse → Whispers
    """

    async def start(
        self,
        crystals: AsyncIterable[ExperienceCrystal],
    ) -> AsyncGenerator[MuseOutput, None]:
        """
        Entry point when kgentsd starts.

        The Muse subscribes to crystal emissions from The Witness.
        """
        self.state = MuseState.SILENT
        arc_buffer: list[ExperienceCrystal] = []

        async for crystal in crystals:
            arc_buffer.append(crystal)

            # Update story arc
            arc = await self._analyze_arc(arc_buffer[-5:])  # Rolling window

            # Consider whispering
            if self.state == MuseState.SILENT:
                whisper = await self._consider_whisper(arc, crystal)
                if whisper:
                    self.state = MuseState.WHISPERING
                    yield MuseOutput(type="whisper", whisper=whisper)

            # Yield arc updates periodically
            yield MuseOutput(type="arc_update", arc=arc)
```

---

## The Symbiosis: Witness + Muse

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         THE WITNESS-MUSE SYMBIOSIS                           │
│                                                                              │
│                              kgentsd                                         │
│                                │                                             │
│                    ┌───────────┴───────────┐                                 │
│                    ▼                       ▼                                 │
│              ┌──────────┐           ┌──────────┐                            │
│              │ WITNESS  │           │   MUSE   │                            │
│              │ captures │──────────►│ interprets│                            │
│              └────┬─────┘  crystals └────┬─────┘                            │
│                   │                      │                                   │
│                   ▼                      ▼                                   │
│          ┌───────────────┐     ┌───────────────┐                            │
│          │ D-gent Memory │     │  UI Overlay   │                            │
│          │ (persistent)  │     │  (ephemeral)  │                            │
│          └───────────────┘     └───────────────┘                            │
│                   │                      │                                   │
│                   └──────────────────────┘                                   │
│                              │                                               │
│                              ▼                                               │
│                     Other Crown Jewels                                       │
│                   (Brain, Gardener, etc.)                                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### The Data Flow

1. **kgentsd** emits raw SystemEvents (file changes, git ops, AGENTESE invocations)
2. **Witness** observes events, transforms into WitnessEvents with context
3. **Witness** crystallizes sessions into ExperienceCrystals
4. **Crystals** go to D-gent (memory) AND to **Muse** (analysis)
5. **Muse** detects patterns, story arcs, aesthetic quality
6. **Muse** whispers suggestions when appropriate
7. **Other jewels** consume crystals and whispers as needed

### The Joy Test

| Jewel | Transformation | Joy Factor |
|-------|----------------|------------|
| **The Witness** | Ephemeral work → Permanent crystals | "I never lose my discoveries" |
| **The Muse** | Grinding → Story; Confusion → Guidance | "My work has meaning and direction" |

### The Mirror Test

*Does this feel like Kent on his best day?*

- **Daring**: Passive background agents that just work
- **Bold**: Work becomes story; confusion becomes guidance
- **Creative**: Experience crystallization; whispered suggestions
- **Opinionated**: Whispers not shouts; dismissal respected; earned encouragement
- **Not gaudy**: Clean polynomials; coherent operads; sheaf gluing

---

## Implementation Priority

| Phase | Focus | Deliverables |
|-------|-------|--------------|
| **P0** | Core Witness | WitnessPolynomial, basic event capture, D-gent integration |
| **P1** | Crystallization | ExperienceCrystal, narrative synthesis, topology |
| **P2** | Muse Arc | StoryArcDetector, ArcPhase, tension measurement |
| **P3** | Muse Whispers | WhisperEngine, dismissal memory, UI overlay |
| **P4** | Cross-Jewel | Integration with Brain, Gardener, kgentsd |

---

## AGENTESE Paths

| Path | Purpose | Effects |
|------|---------|---------|
| `time.witness.manifest` | Current witness state | reads:state |
| `time.witness.mark` | Mark significant moment | writes:markers |
| `time.witness.crystallize` | Force crystallization | writes:crystals, invokes:llm |
| `time.witness.timeline` | View session timeline | reads:events |
| `time.witness.territory` | View codebase topology | reads:filesystem |
| `self.muse.manifest` | Current muse state | reads:state |
| `self.muse.arc` | Get story arc | reads:witness |
| `self.muse.whisper` | Get current whisper | reads:whisper |
| `self.muse.encourage` | Request encouragement | invokes:llm |
| `self.muse.reframe` | Request perspective shift | invokes:llm |
| `self.muse.summon` | Force suggestions | reads:witness, invokes:llm |

---

*"The Witness sees. The Muse speaks. Together, they make work meaningful."*

*Synthesized: 2025-12-19 | Two from Seven | Depth over Breadth*
