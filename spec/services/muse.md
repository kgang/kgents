# The Muse

> *"I see the arc of your work. I know when you're rising, when you're stuck, when you're about to break through. I whisper—never shout."*

**Status:** Proposal
**Implementation:** `impl/claude/services/muse/` (2 tests)

---

## Purpose

The Muse is the **pattern-aware guide**—it detects narrative structure in work sessions and whispers contextual suggestions at the right moment. Unlike tools that demand attention, The Muse respects flow, understands story, and offers genuine encouragement only when earned.

## Core Insight

**Work Has Narrative Structure**: Every work session follows a dramatic arc—exposition, rising action, climax, falling action, resolution. The Muse detects where you are in this arc and calibrates its suggestions accordingly. It also adds **aesthetic sensitivity**—understanding that work isn't just effective or ineffective, it's beautiful or grinding, joyful or tedious.

---

## Metaphysical Position

```
                    ┌─────────────────────────────────────────┐
                    │               THE MUSE                   │
                    │                                          │
                    │   [Story Arc]    [Whisper Engine]        │
                    │        │                 │               │
                    │        └─────────────────┘               │
                    │                 │                        │
  Witness Crystals ►│      ┌──────────┴──────────┐            │
                    │      ▼                     ▼            │
                    │   StoryArc            Whispered         │
                    │   Detection           Guidance          │
                    │      │                     │            │
                    └──────┼─────────────────────┼────────────┘
                           │                     │
                           ▼                     ▼
                      Dashboard              Floating
                      Projection             Toast UI
```

The Muse occupies `self.*` context—it is fundamentally introspective. It consumes Witness crystals and produces guidance.

---

## Categorical Foundation

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

**Key Insight**: SILENT ≠ DORMANT. Silent means actively observing but choosing not to speak. Dormant means cooldown after dismissal. The distinction preserves agency without nagging.

### The Operad

```python
MUSE_OPERAD = Operad(
    name="MUSE",
    extends=["PAIRING_OPERAD", "NARRATIVE_OPERAD"],
    operations={
        # Pattern detection (story arc)
        "detect_arc": Operation(
            arity=1,
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

        # Suggestion (pairing)
        "pair": Operation(
            arity=2,
            output="Suggestion",
            effects=["reads:context"],
            description="Match context to potential tool"
        ),
        "whisper": Operation(
            arity=1,
            output="Whisper",
            effects=["presents:ui"],
            description="Surface a suggestion gently"
        ),

        # The Muse's unique operations
        "sense_aesthetic": Operation(
            arity=1,
            output="AestheticReading",
            effects=["reads:witness"],
            description="Read aesthetic quality of current work"
        ),
        "encourage": Operation(
            arity=0,
            output="Encouragement",
            effects=["presents:ui", "invokes:llm"],
            description="Offer genuine encouragement (not empty praise)"
        ),
        "reframe": Operation(
            arity=1,
            output="Reframe",
            effects=["invokes:llm"],
            description="Offer new perspective on a blockage"
        ),
    },
)
```

### The Sheaf

```python
class MuseSheaf(Sheaf[Session, PatternView, MuseInsight]):
    """
    Coherent insight from pattern observations.

    Local sections:
    - Story arc (phase, tension, dramatic question)
    - User mood (derived from event patterns)
    - Context relevance (what tools might help)
    - Historical patterns (past similar situations)

    Gluing condition: All patterns agree on current session phase.
    Global section: Unified MuseInsight with suggestion + timing
    """

    def overlap(self, a: str, b: str) -> bool:
        """All pattern sources share session context."""
        return True

    def compatible(self, view_a: PatternView, view_b: PatternView) -> bool:
        """Compatible if arc phase doesn't contradict."""
        return view_a.phase == view_b.phase or view_a.confidence < 0.5

    def glue(self, sections: dict[str, PatternView]) -> MuseInsight:
        """Synthesize patterns into actionable insight."""
        # Implementation in impl/
```

---

## Core Concepts

### Story Arc

Based on Freytag's pyramid, adapted for development work:

```python
class ArcPhase(Enum):
    EXPOSITION = "exposition"       # Setting context, reading code
    RISING_ACTION = "rising"        # Building complexity, experiments
    CLIMAX = "climax"               # The breakthrough (or the wall)
    FALLING_ACTION = "falling"      # Cleanup, refinement, polish
    DENOUEMENT = "denouement"       # Reflection, documentation

    @property
    def typical_duration_minutes(self) -> tuple[int, int]:
        return {
            ArcPhase.EXPOSITION: (5, 20),
            ArcPhase.RISING_ACTION: (20, 90),
            ArcPhase.CLIMAX: (5, 15),
            ArcPhase.FALLING_ACTION: (10, 30),
            ArcPhase.DENOUEMENT: (5, 15),
        }[self]

@dataclass(frozen=True)
class StoryArc:
    phase: ArcPhase
    tension: float              # 0.0-1.0
    dramatic_question: str      # What is at stake?
    predicted_climax: datetime | None
    confidence: float
```

### Whisper

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
    opening: str              # The gentle hook
    suggestions: list[Suggestion]
    mood: MoodVector          # Matches user's apparent mood
    urgency: float            # 0.0-1.0 (affects persistence)
    expires_at: datetime

@dataclass(frozen=True)
class Suggestion:
    """A concrete action The Muse suggests."""
    label: str
    agentese_path: str        # What to invoke if accepted
    explanation: str          # Why this might help
```

### Mood Vector

```python
@dataclass(frozen=True)
class MoodVector:
    """Affective signature derived from work patterns."""
    energy: float        # -1 (depleted) to 1 (energized)
    focus: float         # -1 (scattered) to 1 (laser)
    frustration: float   # 0 (none) to 1 (high)
    momentum: float      # -1 (stuck) to 1 (flowing)

    def suggests_intervention(self) -> bool:
        """Should Muse consider whispering?"""
        return (
            self.frustration > 0.6 or
            self.momentum < -0.3 or
            (self.energy < -0.5 and self.focus < 0)
        )
```

---

## AGENTESE Interface

### Node Registration

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
```

### Aspects

| Aspect | Request | Response | Description |
|--------|---------|----------|-------------|
| `manifest` | — | MuseManifestResponse | Current state, arc phase, whisper stats |
| `arc` | — | StoryArc | Current story arc analysis |
| `tension` | — | TensionResponse | Tension level with reasons |
| `whisper` | — | Whisper \| None | Current whisper if any |
| `encourage` | — | Encouragement | Request genuine encouragement |
| `reframe` | ReframeRequest | ReframeResponse | Request new perspective |
| `summon` | — | MuseSummonResponse | Force immediate suggestions |

---

## Pattern Detection

### Signal Aggregation (Pattern 4)

The Muse uses Signal Aggregation for arc detection:

```python
class StoryArcDetector:
    """Detects narrative structure using signal aggregation."""

    def analyze(self, crystals: list[ExperienceCrystal]) -> StoryArc:
        signals = [
            self._count_failures_then_success(crystals),
            self._measure_focus_intensity(crystals),
            self._detect_breakthrough_language(crystals),
            self._analyze_file_touch_patterns(crystals),
            self._measure_commit_frequency(crystals),
        ]
        phase, confidence = self._aggregate_to_phase(signals)
        # ...
```

### Arc Phase Indicators

| Phase | Indicators | Weight |
|-------|------------|--------|
| EXPOSITION | File reads > writes, grep/search commands | 0.4 |
| RISING_ACTION | Edits increasing, test failures, experiments | 0.5 |
| CLIMAX | Tests pass after failures, commit, breakthrough language | 0.3 |
| FALLING_ACTION | Cleanup commits, refactoring, formatting | 0.3 |
| DENOUEMENT | README edits, docs, reflection commands | 0.4 |

---

## Whisper System

### Dismissal Memory (Pattern 5)

```python
class WhisperEngine:
    """Decides when and what to whisper."""

    def __init__(self, dismissal_memory: DismissalMemory):
        self.dismissals = dismissal_memory
        self.current_whisper: Whisper | None = None
        self.queue: list[Whisper] = []
        self.cooldown_hours = 4

    def should_suggest(self, topic: str) -> bool:
        """Check if topic was recently dismissed."""
        return not self.dismissals.is_dismissed(topic)
```

### Whisper Constraints

| Constraint | Rule | Rationale |
|------------|------|-----------|
| Single active | Max 1 whisper at a time | Respect attention |
| Dismissal cooldown | 4h per topic | "Not now" means not now |
| Focus respect | Suppress if tension > 0.8 | Don't break flow |
| Relevance threshold | Only surface if relevance > 0.7 | Avoid noise |
| Timeout | Whispers expire after 5 min | Auto-cleanup |

### Tone Adaptation

Whisper tone matches context:

```python
OPENINGS = {
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
```

---

## kgentsd Integration

### Flux Lifting

```python
class MuseFlux(FluxAgent[MuseState, WitnessEvent, MuseOutput]):
    """
    The Muse listens to The Witness.

    Data flow:
        SystemEvents → Witness → Crystals → Muse → Whispers
    """

    async def start(
        self,
        crystals: AsyncIterable[ExperienceCrystal],
    ) -> AsyncGenerator[MuseOutput, None]:
        self.state = MuseState.SILENT
        arc_buffer: list[ExperienceCrystal] = []

        async for crystal in crystals:
            arc_buffer.append(crystal)

            # Update story arc (rolling window)
            arc = await self._analyze_arc(arc_buffer[-5:])

            # Consider whispering
            if self.state == MuseState.SILENT:
                whisper = await self._consider_whisper(arc, crystal)
                if whisper:
                    self.state = MuseState.WHISPERING
                    yield MuseOutput(type="whisper", whisper=whisper)

            yield MuseOutput(type="arc_update", arc=arc)
```

### Dependency Chain

```
SystemEvents → Witness → Crystals → Muse → Whispers
                  ↓
              D-gent (Memory)
```

The Muse ONLY processes crystals, not raw events. This creates clean separation.

---

## Cross-Jewel Integration

### Consumers of Muse Output

| Consumer | What Muse Provides | Integration |
|----------|-------------------|-------------|
| **Brain** | Story arc for context | Brain can ask "what phase am I in?" |

### Events Emitted

```python
# Via SynergyBus
MuseWhisperCreated(whisper_id: str, topic: str, urgency: float)
MuseWhisperDismissed(whisper_id: str, topic: str, cooldown_hours: int)
MuseArcChanged(from_phase: ArcPhase, to_phase: ArcPhase, tension: float)
MuseBreakthroughDetected(session_id: str, description: str)
```

---

## Visual Projections

### The Whisper Toast

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

### The Story Arc View

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎭 THE MUSE: Story Arc                                   ● SILENT          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                                         ╱╲                                   ║
║                                        ╱  ╲  CLIMAX (predicted: ~11:30)     ║
║                              ╱╲      ╱    ╲                                 ║
║                             ╱  ╲    ╱      ╲                                ║
║                            ╱    ╲  ╱        ← YOU ARE HERE                  ║
║             ╱╲            ╱      ╲╱                                         ║
║            ╱  ╲          ╱                                                  ║
║  ─────────╱    ╲────────╱                   ╲─────────────                  ║
║                                                                               ║
║   EXPOSITION   RISING ACTION              FALLING      DENOUEMENT           ║
║                                                                               ║
║  Dramatic Question: "Can path-first routing replace legacy dispatch?"       ║
║  Tension: ████████░░ 75%    Mood: Focused, determined                       ║
║   [A]rc view  [T]ension history  [S]ummon muse  [W]hisper settings         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Web Components

```typescript
// services/muse/web/
├── MuseDashboard.tsx     // Main container
├── StoryArc.tsx          // Arc visualization
├── WhisperToast.tsx      // Floating suggestion
├── TensionMeter.tsx      // Current tension
├── EncouragementCard.tsx // Earned encouragement
└── hooks/
    ├── useMuse.ts        // State subscription
    ├── useWhisper.ts     // Whisper management
    └── useArc.ts         // Arc queries
```

---

## Laws

| # | Law | Status | Description |
|---|-----|--------|-------------|
| 1 | whisper_not_shout | VERIFIED | Max 1 active whisper at a time; queue others |
| 2 | dismissal_respected | VERIFIED | Dismissed whispers have cooldown on that topic |
| 3 | encouragement_earned | STRUCTURAL | Only offered after genuine progress detected |
| 4 | aesthetic_sensitivity | STRUCTURAL | Tone adapts to user's apparent mood |
| 5 | witness_dependency | VERIFIED | Muse only processes crystals, never raw events |
| 6 | focus_protection | VERIFIED | High tension (>0.8) blocks whisper generation |

---

## Anti-Patterns

- **Shouting**: Demanding attention with modals or notifications
- **Empty Praise**: "Great job!" without detected progress is hollow
- **Ignoring Dismissal**: Re-suggesting dismissed topics breaks trust
- **Bypassing Witness**: Processing raw events creates coupling and races
- **Constant Whispers**: Over-suggestion creates noise; less is more
- **Phase Forcing**: Don't tell users they "should" be in a different phase

---

## Relationship to Witness

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
└──────────────────────────────────────────────────────────────────────────────┘
```

The Witness **captures**. The Muse **interprets**. Together they transform grinding into story.

---

## Implementation Reference

```
impl/claude/services/muse/
├── __init__.py           # Exports
├── core.py               # MuseService
├── polynomial.py         # MUSE_POLYNOMIAL
├── operad.py             # MUSE_OPERAD
├── sheaf.py              # MuseSheaf
├── flux.py               # MuseFlux
├── arc.py                # StoryArc, ArcPhase, StoryArcDetector
├── whisper.py            # Whisper, WhisperEngine
├── mood.py               # MoodVector derivation
├── encouragement.py      # Genuine encouragement generation
├── dismissal.py          # DismissalMemory (Pattern 5)
├── node.py               # @node registration
└── web/                  # React components
```

---

*"The Muse whispers. The Muse waits. The Muse knows when you're ready."*

*Synthesized: 2025-12-19 | Category: self.* | Whispers, Never Shouts*
