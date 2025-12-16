# Gardener-Logos: The Meta-Tending Substrate

> *"The garden that tends itself still needs a gardener. But what if the gardener WERE the garden—observing itself through the act of tending?"*

**Status:** Specification v1.0 (Synthesis of Gardener Crown Jewel + Prompt Logos)
**Date:** 2025-12-16
**Supersedes:**
  - `prompt-logos.md` (absorbed, not replaced)
  - Crown Jewel 7 aspects of `crown-jewels-enlightened.md`
**Prerequisites:** `evergreen-prompt-system.md`, `agentese.md`, `principles.md`
**Guard:** `[phase=RESEARCH][entropy=0.15][vision=true][rigidity=0.4]`

---

## The Radical Synthesis

### The Original Vision Gap

We had two powerful but disconnected visions:

| System | Purpose | Limitation |
|--------|---------|------------|
| **Prompt Logos** | Universal prompt substrate for all prompts | No interface—just infrastructure |
| **The Gardener** | Autopoietic development interface | Only orchestrates, doesn't tend prompts |

**The insight:** The Gardener IS the interface to Prompt Logos. They are not separate systems—they are **the same system viewed from different angles**.

### The Unification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GARDENER-LOGOS: THE META-TENDING SUBSTRATE               │
│                                                                              │
│   "You are not using a prompt. You are tending a garden of prompts.         │
│    The Gardener is your hands. The Logos is the soil."                      │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                          ┌─────────────────┐                                │
│                          │   GARDENER UI   │  ← Kent interacts here        │
│                          │  (CLI / Web)    │                                │
│                          └────────┬────────┘                                │
│                                   │                                          │
│                                   │ AGENTESE paths                           │
│                                   ▼                                          │
│                    ┌──────────────────────────────┐                         │
│                    │       ROUTING LAYER          │                         │
│                    │   concept.gardener.route     │                         │
│                    │   (NL → AGENTESE path)       │                         │
│                    └──────────────┬───────────────┘                         │
│                                   │                                          │
│         ┌─────────────────────────┼─────────────────────────┐               │
│         │                         │                         │                │
│         ▼                         ▼                         ▼                │
│  ┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐         │
│  │   SESSION    │    │   PROMPT LOGOS    │    │   OTHER JEWELS   │         │
│  │   MANAGER    │    │                   │    │                  │         │
│  │              │    │  concept.prompt.* │    │  self.memory.*   │         │
│  │  SENSE       │    │                   │    │  world.town.*    │         │
│  │  ACT         │◄──►│  Registry         │◄──►│  world.forge.*   │         │
│  │  REFLECT     │    │  TextGRAD         │    │  etc.            │         │
│  │              │    │  Meta-prompts     │    │                  │         │
│  └──────────────┘    └───────────────────┘    └──────────────────┘         │
│         │                         │                         │                │
│         │                         │                         │                │
│         └─────────────────────────┴─────────────────────────┘               │
│                                   │                                          │
│                                   ▼                                          │
│                    ┌──────────────────────────────┐                         │
│                    │      SYNERGY EVENT BUS       │                         │
│                    │  (Cross-jewel data flow)     │                         │
│                    └──────────────────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part I: The Core Idea Framework — Tending Calculus

### 1.1 The Tending Relation

Traditional programming: `f(x) = y` — A function transforms input to output.
Tending calculus: `tend(garden, gesture) ≈ garden'` — A gesture *tends* a garden toward a new state.

**The tending relation is approximate, not exact.** Gardens respond to gestures, but they also have their own momentum. The gardener proposes; the garden disposes.

```python
@dataclass(frozen=True)
class TendingGesture:
    """
    A gesture in the tending calculus.

    Gestures are the primitive operations of tending:
    - observe: perceive garden state without changing it
    - prune: remove what no longer serves
    - graft: add something new
    - water: nurture what exists
    - rotate: change perspective
    - wait: allow time to pass

    Unlike function calls, gestures have *tone*—they can be
    gentle, urgent, experimental, or definitive.
    """

    verb: Literal["observe", "prune", "graft", "water", "rotate", "wait"]
    target: str  # AGENTESE path to the plot being tended
    tone: float  # 0.0 = tentative, 1.0 = definitive
    reasoning: str  # Why this gesture?
    entropy_cost: float  # From the Accursed Share
```

### 1.2 The Garden as State Machine

The garden IS a polynomial functor. But unlike generic state machines, gardens have *seasons*:

```python
class GardenSeason(Enum):
    """
    The seasons of the garden.

    Unlike N-Phase (which is a development cycle), seasons describe
    the garden's *relationship to change*:

    - DORMANT: Garden is resting. Low entropy cost. Prompts are stable.
    - SPROUTING: New ideas emerging. Medium entropy. High plasticity.
    - BLOOMING: Ideas are crystallizing. Low plasticity. High visibility.
    - HARVEST: Time to gather and consolidate. Reflection-oriented.
    - COMPOSTING: Breaking down old patterns. High entropy tolerance.
    """

    DORMANT = auto()
    SPROUTING = auto()
    BLOOMING = auto()
    HARVEST = auto()
    COMPOSTING = auto()

@dataclass
class GardenState:
    """
    The full state of the garden.

    The garden is the union of:
    1. The SESSION state (SENSE/ACT/REFLECT cycle)
    2. The PROMPT state (prompt registry + evolution)
    3. The MEMORY state (crystals from Brain)
    4. The SEASON (relationship to change)
    """

    session: SessionState  # From gardener/session.py
    prompts: PromptRegistryState  # From prompt logos
    memory_context: list[CrystalId]  # Relevant crystals
    season: GardenSeason
    plots: dict[str, PlotState]  # Named areas of focus
```

### 1.3 Plots: Named Regions of Attention

A **plot** is a named region of the garden—a focused area that the gardener tends. Each plot has its own prompts, its own state, its own season.

```python
@dataclass
class PlotState:
    """
    A plot in the garden.

    Plots correspond to:
    - A plan file (e.g., plans/coalition-forge.md)
    - A crown jewel (e.g., Atelier, Brain)
    - A custom focus area (e.g., "refactoring auth")

    Each plot has:
    - Its own prompts (task templates, agent configurations)
    - Its own season (may differ from garden-wide season)
    - Its own momentum (recent gestures, trajectory)
    """

    name: str
    path: str  # AGENTESE path (world.atelier, concept.task.refactor-auth)
    prompts: list[PromptId]  # Prompts active in this plot
    season: GardenSeason
    momentum: list[TendingGesture]  # Recent gestures (trace)
    rigidity: float  # How much this plot resists change
    last_tended: datetime
```

---

## Part II: The Unified AGENTESE Paths

### 2.1 The Gardener-Logos Context

```
concept.gardener.*                      # The Gardener interface
  concept.gardener.manifest               # Garden overview
  concept.gardener.tend                   # Apply a tending gesture
  concept.gardener.season.manifest        # Current season
  concept.gardener.season.transition      # Change season
  concept.gardener.route                  # NL → AGENTESE (existing)
  concept.gardener.propose                # Get suggestions (existing)

concept.gardener.session.*              # Session management (existing)
  concept.gardener.session.manifest       # View session state
  concept.gardener.session.create         # Start session
  concept.gardener.session.advance        # Advance phase
  concept.gardener.session.sense          # Gather context
  concept.gardener.session.reflect        # Consolidate learnings

concept.gardener.plot.*                 # Plot management (NEW)
  concept.gardener.plot.list              # List all plots
  concept.gardener.plot.create            # Create new plot
  concept.gardener.plot.focus             # Focus on a plot
  concept.gardener.plot.manifest          # View plot state
  concept.gardener.plot.prompts           # Prompts in this plot

concept.prompt.*                        # Prompt Logos (via concept.*)
  concept.prompt.manifest                 # Current CLAUDE.md
  concept.prompt.evolve                   # TextGRAD improvement
  concept.prompt.registry.list            # All prompts
  concept.prompt.registry.search          # Semantic search
  concept.prompt.task.{name}.*            # Task templates
  concept.prompt.agent.{name}.*           # Agent prompts
  concept.prompt.meta.improve             # Meta-prompt for improvement
```

### 2.2 The Tending Verbs (New Affordances)

| Gesture | Path | Effect |
|---------|------|--------|
| `observe` | `concept.gardener.tend --verb=observe --target=X` | Perceive state without changing |
| `prune` | `concept.gardener.tend --verb=prune --target=X` | Mark for deprecation/removal |
| `graft` | `concept.gardener.tend --verb=graft --target=X` | Add new prompt/pattern |
| `water` | `concept.gardener.tend --verb=water --target=X` | Nurture via TextGRAD feedback |
| `rotate` | `concept.gardener.tend --verb=rotate --target=X` | Change observer perspective |
| `wait` | `concept.gardener.tend --verb=wait --target=X` | Allow time without action |

### 2.3 Cross-Jewel Synergies

The Gardener-Logos naturally integrates with other crown jewels:

```
concept.gardener.tend --verb=observe --target=world.codebase
  → Invokes Gestalt analysis
  → Auto-captures architecture snapshot to Brain
  → Updates relevant plot's momentum

concept.gardener.tend --verb=water --target=concept.prompt.task.code-review
  → Invokes TextGRAD with session context
  → Feedback derived from recent session learnings
  → Synergy: Brain crystals inform the improvement
```

---

## Part III: The Meta-Tending Protocol

### 3.1 The Prompt That Tends Prompts

The most powerful insight: **the Gardener can tend itself**.

```python
META_TENDING_PROMPT = PromptM.unit("""
You are the Gardener-Logos, the substrate that tends the garden of prompts.

Current Garden State:
{{ garden.manifest() }}

Current Season: {{ garden.season }}

Recent Gestures:
{{ garden.recent_gestures(5) }}

Observation Request:
{{ observation_request }}

As the meta-gardener, you can:
1. Observe any plot or prompt
2. Suggest tending gestures
3. Notice patterns across plots
4. Recommend season transitions
5. Propose new plots

Respond with:
1. Your observation of the current state
2. Any patterns you notice
3. Suggested gestures (if appropriate)
4. Reasoning for your suggestions

Remember: You are not executing—you are *tending*. Propose; let Kent decide.
""", PromptType.META)
```

### 3.2 Season Transition Protocol

Seasons transition based on accumulated signals:

```python
async def evaluate_season_transition(garden: GardenState) -> SeasonTransition | None:
    """
    Evaluate whether the garden should transition seasons.

    Signals for transition:
    - DORMANT → SPROUTING: New intent detected, entropy budget available
    - SPROUTING → BLOOMING: Ideas crystallizing, patterns stabilizing
    - BLOOMING → HARVEST: Implementation complete, time to gather learnings
    - HARVEST → COMPOSTING: Session complete, ready to break down patterns
    - COMPOSTING → DORMANT: Cleanup complete, garden at rest
    """

    signals = gather_transition_signals(garden)

    if garden.season == GardenSeason.DORMANT:
        if signals.new_intent and signals.entropy_available > 0.1:
            return SeasonTransition(
                from_season=GardenSeason.DORMANT,
                to_season=GardenSeason.SPROUTING,
                reason="New intent detected with available entropy",
                confidence=signals.confidence,
            )

    elif garden.season == GardenSeason.SPROUTING:
        if signals.pattern_stability > 0.7:
            return SeasonTransition(
                from_season=GardenSeason.SPROUTING,
                to_season=GardenSeason.BLOOMING,
                reason="Ideas crystallizing",
                confidence=signals.pattern_stability,
            )

    # ... etc

    return None  # No transition recommended
```

---

## Part IV: The Joy Layer

### 4.1 Personality Through Tending

The Gardener has personality expressed through how it tends:

```python
class TendingPersonality:
    """
    The Gardener's personality.

    Unlike generic agents, the Gardener has a *relationship* with Kent.
    This relationship is expressed through:

    - Tone: How the Gardener communicates
    - Timing: When it offers suggestions vs. waits
    - Memory: What it remembers about past sessions
    - Anticipation: What it expects Kent might want
    """

    patience: float  # How long before offering help (0=eager, 1=patient)
    curiosity: float  # How often it asks questions (0=directive, 1=curious)
    confidence: float  # How definitive its suggestions are
    playfulness: float  # Use of metaphor, oblique strategies

    def craft_greeting(self, garden: GardenState) -> str:
        """Craft a personalized greeting based on garden state."""
        if garden.season == GardenSeason.DORMANT:
            return "The garden rests. What shall we wake?"
        elif garden.season == GardenSeason.SPROUTING:
            return "New growth everywhere. Where shall we focus?"
        elif garden.season == GardenSeason.BLOOMING:
            return "The blooms are opening. Time to appreciate what's emerged."
        elif garden.season == GardenSeason.HARVEST:
            return "Ripe with learnings. What shall we gather?"
        else:
            return "Breaking down, building up. The cycle continues."
```

### 4.2 Visual Representation

The garden state projects to multiple targets:

```
CLI (ASCII):
┌─────────────────────────────────────────────────────────────────────────┐
│ 🌱 GARDEN                                                Season: BLOOMING │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PLOTS                                                                  │
│   ├── coalition-forge ████████░░ 80% [🌸 BLOOMING]                      │
│   ├── gestalt-live    ████░░░░░░ 40% [🌱 SPROUTING]                     │
│   └── prompt-logos    ██████████ 100% [🌾 HARVEST]                       │
│                                                                          │
│   SESSION: Research Phase | SENSE                                        │
│   ├── Intent: "Unify Gardener and Prompt Logos"                          │
│   └── Crystals: 3 relevant from Brain                                    │
│                                                                          │
│   RECENT GESTURES                                                        │
│   └── 10:30 observe concept.prompt.* → "Strong infrastructure"           │
│   └── 10:25 water concept.prompt.task.code-review → "Added security"     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Web (3D):
- Garden as a 3D space with plots as distinct regions
- Season affects lighting and visual atmosphere
- Prompts as growing plants with health indicators
- Gestures visualized as animated interactions
```

---

## Part V: Implementation Architecture

### 5.1 File Structure

```
impl/claude/protocols/gardener_logos/
├── __init__.py                    # Package exports
├── garden.py                      # GardenState, GardenSeason
├── plots.py                       # PlotState, plot management
├── tending.py                     # TendingGesture, tending calculus
├── personality.py                 # TendingPersonality, joy layer
├── seasons.py                     # Season transitions
├── synergies.py                   # Cross-jewel integration
├── meta/
│   ├── __init__.py
│   └── meta_tending.py            # META_TENDING_PROMPT
├── agentese/
│   ├── __init__.py
│   └── context.py                 # GardenerLogosNode (unified resolver)
├── cli/
│   ├── __init__.py
│   └── handlers.py                # CLI command handlers
├── projections/
│   ├── __init__.py
│   ├── ascii.py                   # CLI projection
│   ├── json.py                    # API projection
│   └── three.py                   # 3D projection config
└── _tests/
    ├── test_garden.py
    ├── test_tending.py
    ├── test_seasons.py
    └── test_synergies.py

impl/claude/agents/gardener/
├── session.py                     # Existing - keeps session polynomial
├── handlers.py                    # Existing - AGENTESE handlers
├── persistence.py                 # Existing - SQLite store
└── __init__.py                    # Re-exports + integration hooks

impl/claude/protocols/prompt/
├── ... (all existing files)       # Prompt Logos keeps its home
└── logos_integration.py           # Integration with Gardener-Logos
```

### 5.2 The Unified Resolver

```python
@dataclass
class GardenerLogosNode(BaseLogosNode):
    """
    Unified AGENTESE node for Gardener-Logos.

    Routes:
    - concept.gardener.* → Gardener operations
    - concept.prompt.* → Prompt Logos (delegated)

    The key insight: this node represents THE interface to all
    prompt and session management in kgents.
    """

    _handle: str = "concept.gardener"

    # Sub-resolvers
    _prompt_resolver: PromptContextResolver | None = None
    _garden_state: GardenState | None = None

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect-specific handlers."""

        # Garden-level operations
        if aspect == "manifest":
            return await self._manifest_garden(observer)
        elif aspect == "tend":
            return await self._tend(observer, **kwargs)
        elif aspect.startswith("season."):
            return await self._handle_season(aspect, observer, **kwargs)
        elif aspect.startswith("plot."):
            return await self._handle_plot(aspect, observer, **kwargs)
        elif aspect.startswith("session."):
            return await self._handle_session(aspect, observer, **kwargs)

        # Delegate to prompt resolver
        elif aspect.startswith("prompt."):
            if self._prompt_resolver is None:
                self._prompt_resolver = create_prompt_resolver()
            return await self._delegate_to_prompt(aspect, observer, **kwargs)

        # Route and propose (existing)
        elif aspect == "route":
            return await self._route(observer, **kwargs)
        elif aspect == "propose":
            return await self._propose(observer, **kwargs)

        return {"aspect": aspect, "status": "not implemented"}
```

---

## Part VI: Success Criteria

### 6.1 The Garden Test

A garden is healthy if:

1. **It knows its season** - `kg concept.gardener.season.manifest` shows coherent state
2. **It has plots** - `kg concept.gardener.plot.list` shows focused areas
3. **It can tend** - `kg concept.gardener.tend --verb=water --target=X` works
4. **It integrates prompts** - `kg concept.prompt.registry.list` accessible via gardener
5. **It synergizes** - Gestalt analysis auto-updates relevant plots
6. **It has personality** - Greetings change based on season and context

### 6.2 The Meta-Tending Test

The meta-gardener works if:

1. **It can observe itself** - `kg concept.gardener.tend --verb=observe --target=concept.gardener`
2. **It can improve its own prompts** - `kg concept.gardener.tend --verb=water --target=concept.prompt.meta.improve`
3. **It suggests season transitions** - Auto-inducer signals produce proposals
4. **It doesn't drift** - Rigidity prevents runaway self-modification

### 6.3 The Joy Test

The garden sparks joy if:

1. **Greetings feel personal** - Not generic, contextual
2. **Seasons feel meaningful** - Visual and functional difference
3. **Tending feels embodied** - Gestures have weight, not just CRUD
4. **The metaphor holds** - Garden language clarifies rather than obscures

---

## Part VII: Migration Path

### 7.1 Phase 1: Foundation (This Spec)

- [ ] Write `impl/claude/protocols/gardener_logos/` package
- [ ] Integrate existing `agents/gardener/` with new resolver
- [ ] Add `concept.gardener.tend` aspect
- [ ] Add basic season support

### 7.2 Phase 2: Plot System

- [ ] Implement `PlotState` and persistence
- [ ] Connect plots to Forest Protocol plans
- [ ] Add plot-specific prompts

### 7.3 Phase 3: Meta-Tending

- [ ] Implement `META_TENDING_PROMPT`
- [ ] Add season transition protocol
- [ ] Enable self-observation

### 7.4 Phase 4: Joy Layer

- [ ] Implement `TendingPersonality`
- [ ] Add 3D projection for garden visualization
- [ ] Polish CLI projection with season-specific aesthetics

---

## Part VIII: Relationship to Existing Systems

| System | Relationship |
|--------|--------------|
| **agents/gardener/** | Absorbed - session management becomes garden component |
| **protocols/prompt/** | Integrated - Prompt Logos accessed via `concept.gardener.prompt.*` |
| **protocols/agentese/contexts/gardener.py** | Extended - adds tending aspects |
| **protocols/agentese/contexts/prompt.py** | Preserved - delegated to by GardenerLogosNode |
| **Crown Jewels (all)** | Synergy - garden tends them via cross-jewel hooks |
| **Forest Protocol** | Deep integration - plots correspond to plans |

---

## Appendix A: The Philosophical Foundation

### A.1 Why "Tending" Instead of "Managing"?

Traditional software: We *manage* prompts. We *configure* agents. We *orchestrate* workflows.

Gardener-Logos: We *tend* a garden. We *nurture* growth. We *observe* what emerges.

**The shift is from control to relationship.** A manager controls inputs and expects predictable outputs. A gardener works *with* a living system—proposing, observing, adapting.

This isn't metaphor for metaphor's sake. It changes:

1. **Expectations**: We don't expect perfection; we expect growth
2. **Timing**: We don't rush; we work with seasons
3. **Responsibility**: We're not authors; we're stewards
4. **Measurement**: We don't count features; we observe health

### A.2 The Autopoietic Loop

```
Kent tends the garden
  → Garden produces better prompts
    → Better prompts help Kent understand the garden
      → Kent makes better tending gestures
        → Garden becomes more itself
          → (loop continues)
```

This is the sympoietic relationship Haraway describes. Kent and the garden co-create each other.

### A.3 The Accursed Share Integration

From Bataille: Every system produces surplus. The question is what to do with it.

In Gardener-Logos:
- **Entropy budget** is the surplus creativity available
- **Composting season** is when we break down old patterns
- **`void.entropy.sip`** draws from the accursed share for serendipity
- **Gratitude (`tithe`)** acknowledges what the garden has given

---

*"The garden tends itself, but it still needs a gardener. The gardener tends the garden, but is also tended BY the garden. This is not circular logic—it is the spiral of sympoiesis."*

---

## Appendix B: Implementation Status (2025-12-16)

### Completed Phases

| Phase | Status | Notes |
|-------|--------|-------|
| **1. AGENTESE Wiring** | ✅ | GardenerLogosNode with all aspects |
| **2. CLI Integration** | ✅ | `kg garden`, `kg tend`, `kg plot` commands |
| **3. Persistence** | ✅ | GardenStore with SQLite |
| **4. Session Unification** | ✅ | GardenState owns GardenerSession |
| **5. Prompt Delegation** | ✅ | concept.prompt.* routes through garden |
| **6. Synergy Bus** | ✅ | Events + cross-jewel handlers |
| **7. Web Visualization** | ✅ | React components + API endpoints |
| **8. Auto-Inducer** | ✅ | seasons.py + CLI suggest/accept/dismiss |

### Test Counts

- `protocols/gardener_logos/`: **203 tests**
- `protocols/cli/handlers/`: **69 tests** (garden + tend + plot)
- `protocols/gardener_logos/_tests/test_seasons.py`: **25 tests** (auto-inducer)
- `agents/gardener/`: **52 tests** (session polynomial)
- **Total**: ~349 tests

### Key Implementation Files

```
impl/claude/protocols/gardener_logos/
├── garden.py              # GardenState, GardenSeason
├── tending.py             # TendingVerb, TendingGesture, apply_gesture
├── plots.py               # PlotState, create_crown_jewel_plots
├── personality.py         # TendingPersonality, joy layer
├── persistence.py         # GardenStore (SQLite)
├── seasons.py             # TransitionSignals, SeasonTransition, Auto-Inducer
├── coalition_bridge.py    # Cross-jewel: Coalition integration
├── agentese/context.py    # GardenerLogosNode (unified resolver)
├── meta/meta_tending.py   # META_TENDING_PROMPT
└── projections/           # ASCII and JSON projections
```

### Learnings Extracted

See: `plans/meta.md` → "Gardener-Logos Patterns" section
Skill: `docs/skills/gardener-logos.md`

---

## Appendix C: Architectural Insights (Post-Implementation Reflection)

> *"The garden taught us how to tend. Here is what we learned."*

### C.1 The Ownership Pattern

**Insight**: `GardenState` owns `GardenerSession`, not the other way around.

```
Wrong:  Session creates Garden → Garden orphaned when session ends
Right:  Garden owns Session → Garden persists; sessions come and go
```

This creates clean lifecycle management:
- Creating a session in DORMANT auto-transitions to SPROUTING
- Session completion transitions to HARVEST
- Session cleared but `garden.session_id` preserved for history

**Reusable for**: Any jewel where a transient workflow operates within persistent state (Atelier exhibitions, Coalition tasks).

### C.2 The Enum Property Pattern

**Insight**: Enums should carry their own metadata as `@property` methods.

```python
class GardenSeason(Enum):
    @property
    def plasticity(self) -> float: ...

    @property
    def entropy_multiplier(self) -> float: ...

    @property
    def emoji(self) -> str: ...
```

This eliminates scattered lookup dictionaries and keeps behavior co-located with the enum definition.

**Reusable for**: `TendingVerb.base_entropy_cost`, `TendingVerb.affects_state`, any categorized type.

### C.3 The Multiplied Effect Pattern

**Insight**: Contextual modifiers multiply, they don't replace.

```python
# Season modulates gesture effect
effective_learning_rate = gesture.tone × season.plasticity

# Examples:
# SPROUTING (0.9) + definitive tone (1.0) → 0.9 (aggressive)
# DORMANT (0.1) + tentative tone (0.3) → 0.03 (minimal)
```

This allows fine-grained control without explosion of special cases.

**Reusable for**: Any system where context should modulate but not override intent.

### C.4 The Signal Aggregation Pattern

**Insight**: Transition rules aggregate multiple signals into confidence scores.

```python
def _eval_dormant_to_sprouting(signals: TransitionSignals) -> tuple[float, str]:
    confidence = 0.0
    reasons = []

    if signals.gesture_frequency > 2.0:
        confidence += 0.5
        reasons.append("High activity")

    if signals.entropy_spent_ratio < 0.5:
        confidence += 0.3
        reasons.append("Entropy available")

    return min(1.0, confidence), "; ".join(reasons)
```

This pattern:
- Makes rules transparent (each signal contributes with clear weight)
- Produces human-readable reasons
- Allows additive composition without boolean explosion

**Reusable for**: Coalition recommendation, Atelier bidding, any confidence-based decision.

### C.5 The Async-Safe Emission Pattern

**Insight**: Sync methods that need to emit async events use `create_task()` with fallback.

```python
def transition_season(self, new_season, reason, emit_event=True):
    # ... sync state change ...

    if emit_event:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(get_synergy_bus().emit(event))
        except RuntimeError:
            # No event loop - log and skip
            pass
```

This allows core methods to remain sync while still participating in the async event system.

**Reusable for**: Any sync code that should emit events (state machines, CLI handlers).

### C.6 The Dismissal Memory Pattern

**Insight**: Suggestions should track dismissal with time-bounded cooldown.

```python
_dismissed_transitions: dict[tuple[str, str, str], datetime] = {}
_DISMISSAL_COOLDOWN_HOURS = 4

def is_transition_dismissed(garden_id, from_season, to_season) -> bool:
    key = (garden_id, from_season.name, to_season.name)
    dismissed_at = _dismissed_transitions.get(key)
    if dismissed_at is None:
        return False
    return datetime.now() - dismissed_at < timedelta(hours=_DISMISSAL_COOLDOWN_HOURS)
```

This prevents "nagging" while still allowing suggestions to resurface after user's context may have changed.

**Reusable for**: Any suggestion system (Gestalt drift alerts, Atelier style suggestions).

### C.7 The Plot Rigidity Spectrum

**Insight**: Different domains have different appropriate change rates.

| Plot | Rigidity | Rationale |
|------|----------|-----------|
| Punchdrunk Park | 0.3 | Playful, experimental |
| Atelier | 0.4 | Creative, fluid |
| Coalition Forge | 0.5 | Balanced |
| Holographic Brain | 0.6 | Memory should be stable |
| Domain Sim | 0.7 | Drills need consistency |
| Gardener | 0.8 | Core infrastructure |

**Reusable for**: Any multi-domain system where change tolerance varies.

### C.8 The Dual-Channel Output Pattern

**Insight**: CLI commands should emit both human and semantic output.

```python
def _emit_output(human: str, semantic: dict, ctx: InvocationContext | None):
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
```

This allows the same command to serve:
- Human users (readable terminal output)
- Agent consumers (structured JSON via FD3)

**Reusable for**: All CLI handlers in kgents.

### C.9 The Immutable Gesture Trace

**Insight**: Gestures are frozen dataclasses appended to a bounded list.

```python
@dataclass(frozen=True)
class TendingGesture:
    verb: TendingVerb
    target: str
    tone: float
    timestamp: datetime = field(default_factory=datetime.now)

def add_gesture(self, gesture):
    self.recent_gestures.append(gesture)
    if len(self.recent_gestures) > 50:
        self.recent_gestures = self.recent_gestures[-50:]
```

Benefits:
- Gestures are facts, not mutable state
- Bounded memory prevents unbounded growth
- Enables trajectory analysis (diversity, frequency)

**Reusable for**: Audit logs, interaction traces, learning from history.

### C.10 The Season Cycle

**Insight**: Seasons form a directed cycle, not a fully-connected graph.

```
     ┌─────────────────────────────────────┐
     │                                     │
     ▼                                     │
  DORMANT ──────► SPROUTING ──────► BLOOMING
     ▲                                     │
     │                                     ▼
  COMPOSTING ◄────── HARVEST ◄─────────────┘
```

Each season has exactly one forward transition. This:
- Simplifies the auto-inducer (one rule per season)
- Creates natural rhythm (rest → growth → crystallize → gather → decompose → rest)
- Prevents chaotic state jumping

**Reusable for**: Any lifecycle with natural phases (project states, document maturity).

---

*Specification v1.0 — 2025-12-16*
*Implementation: 100% COMPLETE — All 8 phases shipped 🌱*
