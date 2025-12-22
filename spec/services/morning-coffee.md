# Morning Coffee ☕

> *"The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale, feels the instrument respond."*

**Status:** Draft
**Implementation:** `impl/claude/services/liminal/` (0 tests)
**Voice Anchor:** *"Flit in and out of flow like a musician or artist"*

---

## Purpose

Morning Coffee is a **Liminal Transition Protocol** — a ritual that honors state changes between rest and work. Unlike traditional dev rituals (standups, status checks) that are **extractive** (pulling information FROM the developer), Morning Coffee is **generative** (helping the developer BECOME ready for creative work).

## Core Insight

**The liminal state is precious.** Kent arrives having rested, dreamed, and frolicked among non-CS concepts. This state should be honored, bridged, captured, and amplified — not immediately demanded into focus. Morning Coffee is the musical warmup before the concerto.

---

## Metaphysical Position

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MORNING COFFEE                                    │
│                                                                              │
│  Movement 1: Garden View 🌱        "What grew while I slept?"               │
│       │                                                                      │
│       ▼                                                                      │
│  Movement 2: Conceptual Weather 🌤️  "What's shifting in the atmosphere?"    │
│       │                                                                      │
│       ▼                                                                      │
│  Movement 3: Menu 🍳               "What suits my taste this morning?"       │
│       │                                                                      │
│       ▼                                                                      │
│  Movement 4: Fresh Capture 📝       "What's Kent saying before code?"       │
│       │                                                                      │
│       ▼                                                                      │
│  [Transition] ─────────────────────► Ready for work                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

Morning Coffee occupies `time.*` context — it is fundamentally about transitions between temporal states. It consumes signals from Witness, Brain, and git to produce a ritualized onboarding experience.

---

## Categorical Foundation

### The Polynomial

```python
COFFEE_POLYNOMIAL = PolyAgent[CoffeeState, RitualEvent, CoffeeOutput](
    positions=frozenset({
        CoffeeState.DORMANT,        # Not in ritual
        CoffeeState.GARDEN,         # Movement 1: Observing
        CoffeeState.WEATHER,        # Movement 2: Understanding
        CoffeeState.MENU,           # Movement 3: Choosing
        CoffeeState.CAPTURE,        # Movement 4: Recording
        CoffeeState.TRANSITION,     # Bridging to work
    }),
    directions=lambda state: {
        CoffeeState.DORMANT: {"wake", "force_start"},
        CoffeeState.GARDEN: {"continue", "skip_to_menu", "exit"},
        CoffeeState.WEATHER: {"continue", "skip_to_menu", "exit"},
        CoffeeState.MENU: {"select", "serendipity", "exit"},
        CoffeeState.CAPTURE: {"record", "skip", "exit"},
        CoffeeState.TRANSITION: {"begin_work", "linger"},
    }[state],
    transition=coffee_transition,
)
```

**Key Insight**: Every movement is skippable. If inspiration strikes during Garden View, honor it. The ritual serves the human, not vice versa.

### The Operad (Inherits NARRATIVE_OPERAD)

```python
COFFEE_OPERAD = Operad(
    name="COFFEE",
    extends=["NARRATIVE_OPERAD", "TEMPORAL_OPERAD"],
    operations={
        # Movement 1: Garden
        "view_garden": Operation(
            arity=0, output="GardenView",
            effects=["reads:git", "reads:now_md"],
            description="Non-demanding overview of recent changes"
        ),

        # Movement 2: Weather
        "read_weather": Operation(
            arity=0, output="ConceptualWeather",
            effects=["reads:plans", "reads:witness"],
            description="Conceptual movements, not code changes"
        ),

        # Movement 3: Menu
        "generate_menu": Operation(
            arity=1, output="ChallengeMenu",
            effects=["reads:todos", "reads:context"],
            description="Present challenge gradients by valence/magnitude"
        ),

        # Movement 4: Capture
        "capture_voice": Operation(
            arity=1, output="MorningVoice",
            effects=["writes:voice_anchors", "invokes:llm"],
            description="Record fresh voice before code takes over"
        ),

        # Transition
        "begin_transition": Operation(
            arity=1, output="TransitionPhrase",
            effects=["writes:session"],
            description="Bridge phrase into work state"
        ),
    },
)
```

---

## Core Concepts

### The Four Movements

Each movement has a distinct character and can be exited at any time:

```python
@dataclass(frozen=True)
class Movement:
    """A phase of the Morning Coffee ritual."""
    name: str
    prompt: str               # What is asked
    duration_hint: str        # "~2 min", "~5 min"
    skippable: bool = True
    requires_input: bool      # False = observation, True = interaction

MOVEMENTS = {
    "garden": Movement(
        name="Garden View",
        prompt="What grew while I slept?",
        duration_hint="~2 min",
        requires_input=False,
    ),
    "weather": Movement(
        name="Conceptual Weather",
        prompt="What's shifting in the atmosphere?",
        duration_hint="~2 min",
        requires_input=False,
    ),
    "menu": Movement(
        name="Menu",
        prompt="What suits my taste this morning?",
        duration_hint="~3 min",
        requires_input=True,
    ),
    "capture": Movement(
        name="Fresh Capture",
        prompt="What's on your mind before code takes over?",
        duration_hint="~3 min",
        requires_input=True,
    ),
}
```

### Challenge Gradients

The Menu presents work by **valence** (gentleness) and **magnitude** (depth):

```python
class ChallengeLevel(Enum):
    GENTLE = "gentle"       # Warmup, low stakes
    FOCUSED = "focused"     # Clear objective, moderate depth
    INTENSE = "intense"     # Deep work, high cognitive load
    SERENDIPITOUS = "serendipitous"  # Follow curiosity

    @property
    def emoji(self) -> str:
        return {"gentle": "🧘", "focused": "🎯", "intense": "🔥", "serendipitous": "🎲"}[self.value]

    @property
    def description(self) -> str:
        return {
            "gentle": "Warmup, low stakes",
            "focused": "Clear objective, moderate depth",
            "intense": "Deep work, high cognitive load",
            "serendipitous": "Follow curiosity",
        }[self.value]

@dataclass(frozen=True)
class MenuItem:
    """A potential work item on the menu."""
    label: str
    description: str
    level: ChallengeLevel
    agentese_path: str | None    # Path to invoke if selected
    source: str                   # Where this came from ("todo", "plan", "witness")
```

### Morning Voice

The anti-sausage goldmine — Kent's authentic voice before code takes over:

```python
@dataclass(frozen=True)
class MorningVoice:
    """Fresh capture of Kent's authentic morning state."""
    date: date
    non_code_thought: str | None      # "What's on your mind (not code)?"
    eye_catch: str | None             # "What catches your eye in the garden?"
    success_criteria: str | None      # "What would make today feel good?"
    raw_feeling: str | None           # Optional: general feeling

    def as_voice_anchor(self) -> VoiceAnchor | None:
        """Convert to voice anchor if substantive."""
        if self.success_criteria:
            return VoiceAnchor(
                text=self.success_criteria,
                source="morning_coffee",
                captured_at=datetime.now(),
            )
        return None
```

---

## AGENTESE Interface

### Node Registration

```python
@node(
    path="time.coffee",
    description="Morning Coffee ritual — liminal transition from rest to work",
    contracts={
        "manifest": Response(CoffeeManifestResponse),
        "garden": Response(GardenView),
        "weather": Response(ConceptualWeather),
        "menu": Response(ChallengeMenu),
        "capture": Contract(CaptureRequest, MorningVoice),
        "begin": Response(TransitionResponse),
        "history": Response(CoffeeHistoryResponse),
    },
    effects=["reads:git", "reads:witness", "reads:plans", "writes:voice"],
    affordances={
        "guest": ["manifest"],
        "observer": ["manifest", "garden", "weather"],
        "participant": ["manifest", "garden", "weather", "menu", "capture", "begin"],
        "architect": ["*"],
    },
)
```

### Aspects

| Aspect | Request | Response | Description |
|--------|---------|----------|-------------|
| `manifest` | — | CoffeeManifestResponse | Current ritual state, last ritual date |
| `garden` | — | GardenView | Yesterday's changes, growth indicators |
| `weather` | — | ConceptualWeather | Refactoring, emerging, scaffolding patterns |
| `menu` | — | ChallengeMenu | Challenge items by gradient |
| `capture` | CaptureRequest | MorningVoice | Record fresh morning voice |
| `begin` | — | TransitionResponse | Complete ritual, begin work |
| `history` | — | CoffeeHistoryResponse | Past captures for voice tracking |

### CLI Interface

```bash
kg coffee              # Full ritual
kg coffee --quick      # Garden + Menu only
kg coffee garden       # Just movement 1
kg coffee menu         # Just movement 3
kg coffee capture      # Just movement 4 (voice capture)
```

---

## Integration Points

### Consumers and Producers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MORNING COFFEE DATA FLOW                          │
│                                                                              │
│   INPUTS                      COFFEE                    OUTPUTS             │
│                                                                              │
│   git diff ──────────────────► Garden View                                  │
│   NOW.md ────────────────────► Garden View                                  │
│   plans/*.md ────────────────► Conceptual Weather                           │
│   Witness crystals ──────────► Conceptual Weather                           │
│   TODOs ─────────────────────► Menu Generation        ──► Session context   │
│   Recent captures ───────────► Menu Generation        ──► K-gent voice      │
│                                                        ──► Anti-sausage     │
│   User responses ────────────► Fresh Capture          ──► Voice anchors     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cross-Jewel Integration

| Jewel | Integration | Direction |
|-------|-------------|-----------|
| **Witness** | Crystals inform Conceptual Weather | Coffee consumes |
| **Muse** | Story arc context for Menu suggestions | Coffee consumes |
| **K-gent** | Morning voice feeds personality | Coffee produces |
| **Brain** | Captures stored as crystals | Coffee produces |
| **Anti-Sausage** | Morning voice becomes reference | Coffee produces |

### Events Emitted

```python
# Via SynergyBus
CoffeeRitualStarted(session_id: str, timestamp: datetime)
CoffeeMovementCompleted(movement: str, duration_seconds: int)
CoffeeVoiceCaptured(capture_id: str, has_success_criteria: bool)
CoffeeRitualCompleted(session_id: str, chosen_challenge: ChallengeLevel)
CoffeeRitualExited(session_id: str, at_movement: str)  # Early exit
```

---

## Visual Projections

### CLI: Garden View

```
┌─────────────────────────────────────────────────────────────────┐
│  Yesterday's Harvest                                             │
├─────────────────────────────────────────────────────────────────┤
│  ◉ 3 files changed → Brain persistence hardening                │
│  ◉ New test: test_semantic_consistency.py                       │
│  ◉ UI: Town visualization improvements                          │
│                                                                  │
│  🌿 Growing:   Brain 100% → stable                              │
│  🌱 Sprouting: Town 85% → visualization complete                │
│  🌱 Sprouting: Atelier 75% → commission flow active             │
│  🌰 Seeds:     ASHC compiler → L0 kernel designed               │
└─────────────────────────────────────────────────────────────────┘
```

### CLI: Conceptual Weather

```
┌─────────────────────────────────────────────────────────────────┐
│  Conceptual Weather Report                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔄 REFACTORING: S-gents → D-gents consolidation                │
│     The "stateful agent" abstraction is migrating...            │
│                                                                  │
│  🌊 EMERGING: Failure-as-Evidence principle                     │
│     "What you tried and rejected is information"                │
│                                                                  │
│  🏗️ SCAFFOLDING: ASHC compiler architecture                     │
│     L0 kernel → Pass operad → Bootstrap regeneration            │
│                                                                  │
│  ⚡ TENSION: Depth vs. breadth in crown jewel work              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CLI: Menu

```
┌─────────────────────────────────────────────────────────────────┐
│  Today's Menu                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🧘 GENTLE (warmup, low stakes)                                 │
│     • Write a test for existing behavior                        │
│     • Document a pattern you discovered yesterday               │
│     • Refine a UI detail that's been bugging you                │
│                                                                  │
│  🎯 FOCUSED (clear objective, moderate depth)                   │
│     • Wire ASHC L0 kernel to existing AST                       │
│     • Complete Town citizen interaction patterns                │
│     • Complete Brain crystalline facet interaction              │
│     • Implement one ASHC pass                                   │
│                                                                  │
│  🔥 INTENSE (deep work, high cognitive load)                    │
│     • Bootstrap regeneration: make spec regenerate impl         │
│     • Solve the sheaf coherence visualization problem           │
│     • Design the voice capture feedback loop                    │
│                                                                  │
│  🎲 SERENDIPITOUS                                               │
│     "What caught your eye in the garden view?"                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CLI: Fresh Capture

```
Morning Voice (2025-12-21):

Q: "What's on your mind that has nothing to do with code?"
> [Kent types freely]

Q: "Looking at the garden view, what catches your eye?"
> [Fresh reaction, unfiltered]

Q: "What would make today feel like a good day?"
> [Authentic success criteria]
```

---

## Laws

| # | Law | Status | Description |
|---|-----|--------|-------------|
| 1 | skippable_movements | VERIFIED | Any movement can be skipped; ritual serves human |
| 2 | observation_before_demand | STRUCTURAL | Garden/Weather are non-interactive; don't demand focus early |
| 3 | voice_freshness | STRUCTURAL | Capture happens before code interaction; preserves morning state |
| 4 | choice_not_assignment | VERIFIED | Menu presents invitations, not tasks; Kent chooses |
| 5 | exit_honored | VERIFIED | Early exit respected; no guilt, no nagging |
| 6 | serendipity_option | VERIFIED | "Follow curiosity" always available in Menu |

---

## Generalization: Liminal Transition Protocols

Morning Coffee is the first instance of a broader pattern:

```python
class LiminalProtocol(Protocol):
    """A ritual that honors state transitions."""

    from_state: str      # "rest", "deep_work", "away"
    to_state: str        # "work", "break", "back"
    movements: list[Movement]

    def capture_leaving_state(self) -> StateCapture:
        """What to preserve from the state being left."""
        ...

    def bridge(self) -> BridgePhrase:
        """Gentle transition between states."""
        ...

    def prepare_entering_state(self) -> Preparation:
        """What to set up for the state being entered."""
        ...
```

### Future Protocols

| Protocol | Transition | Key Capture |
|----------|------------|-------------|
| `kg coffee` | Rest → Work | Morning voice, challenge selection |
| `kg pause` | Deep Work → Break | Current thought, return context |
| `kg evening` | Work → Rest | Day summary, tomorrow hints |
| `kg return` | Away → Back | What was interrupted, reentry |

---

## Anti-Patterns

- **Demanding Focus Early**: Garden/Weather should let the eye wander, not demand attention
- **Task Assignment**: Menu presents choices, not assignments; "pick" not "do"
- **Guilt on Exit**: Early exit is fine; ritual serves human, not vice versa
- **Skipping Capture**: Voice capture is the gold; make it easy, not skippable by default
- **Overly Long Ritual**: Total should be ~10 min; respect morning time
- **Feature Creep**: Four movements are enough; resist adding more

---

## Implementation Reference

```
impl/claude/services/liminal/
├── __init__.py           # Exports
├── coffee/
│   ├── core.py           # CoffeeService
│   ├── polynomial.py     # COFFEE_POLYNOMIAL
│   ├── operad.py         # COFFEE_OPERAD
│   ├── garden.py         # GardenView generation
│   ├── weather.py        # ConceptualWeather analysis
│   ├── menu.py           # ChallengeMenu generation
│   ├── capture.py        # MorningVoice recording
│   ├── node.py           # @node registration
│   └── _tests/
├── protocol.py           # Base LiminalProtocol
└── web/                  # React components (future)
```

---

*"The morning mind knows things the afternoon mind has forgotten."*

*Specified: 2025-12-21 | Category: time.* | Liminal Transition Protocol*
