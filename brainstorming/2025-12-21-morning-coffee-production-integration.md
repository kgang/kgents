# Morning Coffee Production Integration: Three Creative Lines

> *"The morning mind knows things the afternoon mind has forgotten."*

**Date**: 2025-12-21
**Status**: Brainstorming → Synthesis → Recommendation
**Related**: `spec/services/morning-coffee.md`, `services/liminal/coffee/`

---

## The Challenge

Morning Coffee is **architecturally complete** (264 tests, 4 movements, polynomial state machine). Now it needs production integration:

1. **VoicePersistence** — Move from JSON files to D-gent backed storage
2. **Brain Integration** — Proper DI wiring, semantic search
3. **SynergyBus Events** — Cross-jewel coordination
4. **Session Context Loading** — `kg coffee begin` loads relevant files
5. **AGENTESE Enhancement** — Add archaeology and patterns aspects

Rather than approach this as a mechanical wiring task, we explored **three creative lines** that each bring a distinct metaphor and capability set.

---

## Line 1: Stigmergy — Voice Traces That Guide Future Sessions

### Core Metaphor

**Each morning voice is a pheromone deposit.** Like ants leaving traces that guide future ants, Kent's morning captures accumulate into a distributed memory field. Future mornings don't just *recall* past captures; they *sense gradients* that have been reinforced by repeated patterns.

### Key Insight

> *"The termite knows nothing of the cathedral; the cathedral knows nothing of the termite. Together they build."*

Voice captures are not records to be queried. They are **pheromones in a field**. The field decays naturally (Ebbinghaus forgetting), but traces that recur get reinforced. Over time, the field learns Kent's patterns without explicit programming.

### The Stigmergic Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE STIGMERGIC MORNING LOOP                          │
│                                                                              │
│   1. SENSE        ───────────────►  2. CAPTURE                              │
│   Query pheromone field            Record today's voice as traces           │
│   "What patterns are strong?"      Deposit pheromones at concepts           │
│                                                                              │
│            ▲                              │                                  │
│            │                              ▼                                  │
│                                                                              │
│   4. REINFORCE    ◄───────────────  3. TRACE                                │
│   End-of-day feedback              Voice enters the field                   │
│   "Did I ship?" → +/- intensity    Associates with past traces              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Mechanisms

1. **Dual-Track Storage**:
   - D-gent stores exact captures (queryable, causal chain)
   - PheromoneField stores semantic traces (decay-enabled, association-forming)

2. **Pattern Detection Without ML**:
   - Concepts that recur get stronger traces
   - Associations form when concepts co-occur
   - No explicit "learn" button — emergence from accumulation

3. **End-of-Day Reinforcement**:
   - "Did you accomplish your morning intention?"
   - Successful intentions get reinforced (intensity × 1.5)
   - Failures decay naturally (no explicit punishment)

4. **Stigmergic Menu Suggestions**:
   ```
   📍 FROM YOUR PATTERNS
      "Ship something" appears in 7 of last 10 mornings
      "Depth over breadth" — recurring voice anchor
   ```

### Why This is Daring

- Treats voices as **living traces** rather than dead records
- Commits to stigmergy as a metaphor, not just a buzzword
- No ML required — patterns emerge from accumulation and decay

---

## Line 2: Liminal Archaeology — Excavating the Morning Mind

### Core Metaphor

**Voices are sedimentary layers.** Each `MorningVoice` capture is a fossilized moment. Over months, these form strata — a record of what the vision-holder cares about when uncontaminated by debugging fatigue.

### Key Insight

> *"What you repeatedly say at 8am reveals your true north. The afternoon mind lies; the morning mind confesses."*

Traditional voice search treats each capture as equal. Archaeology treats them as **strata** — later layers compress and transform earlier ones, creating meaning through temporal pressure.

### Voice Stratigraphy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VOICE STRATIGRAPHY                                    │
│                                                                              │
│   2025-12 │ "Ship the verification layer" "Make ASHC feel magical"         │
│   ────────┼───────────────────────────────────────────────────────────────  │
│   2025-11 │ "Finish categorical foundation" "Get Town working"              │
│   ────────┼───────────────────────────────────────────────────────────────  │
│   2025-10 │ "Make the agents compose" "Tasteful > feature-complete"         │
│   ────────┼───────────────────────────────────────────────────────────────  │
│   2025-09 │ "Build K-gent" "The persona should feel alive"                  │
│                                                                              │
│   PRESSURE → COMPRESSION → EMERGENCE                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What Becomes Visible at Scale

| Scale | What You See |
|-------|--------------|
| **Day** | "Ship feature X" — just a task |
| **Week** | Challenge level preferences, energy patterns |
| **Month** | Seasonal priorities, vocabulary evolution, theme crystallization |
| **Quarter** | Abandoned concerns (what stopped appearing?), stable anchors |

### Stratum Types

```python
class VoiceStratum(Enum):
    SURFACE = "surface"       # Last 7 days — fresh, uncompressed
    SHALLOW = "shallow"       # 7-30 days — beginning to settle
    DEEP = "deep"             # 30-90 days — compressed, crystalized
    FOSSIL = "fossil"         # 90+ days — ancient wisdom or obsolete
```

### Archaeological Operations

| Operation | Description | CLI Command |
|-----------|-------------|-------------|
| `dig` | Retrieve voices from specific stratum | `kg coffee archaeology dig --stratum deep` |
| `sift` | Filter by theme, energy, pattern | `kg coffee archaeology sift --theme "composability"` |
| `carbon_date` | Analyze temporal patterns | `kg coffee archaeology date --theme "tasteful"` |
| `fossil_record` | Complete stratigraphic view | `kg coffee archaeology record` |
| `emergence` | Patterns only visible at month scale | `kg coffee archaeology emerge` |

### Theme Crystallization

```python
@dataclass(frozen=True)
class ThemeCrystal:
    theme: str                          # Extracted theme name
    first_appearance: date              # When it first surfaced
    last_appearance: date               # Most recent mention
    occurrence_count: int               # How often it appears
    strata_distribution: dict[str, int] # Which layers contain it
    confidence: float                   # Crystallization strength
```

### The Fossil Record Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│  Voice Fossil Record                                             │
├─────────────────────────────────────────────────────────────────┤
│  SURFACE (Dec 15-21) ────────────────────────────────────────   │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 6 voices                                    │
│  Themes: "ASHC", "verification", "production-ready"             │
│                                                                  │
│  SHALLOW (Nov 21 - Dec 14) ──────────────────────────────────   │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 18 voices                           │
│  ⚡ CRYSTALLIZED: "Tasteful > feature-complete" (4 mentions)    │
│                                                                  │
│  DEEP (Oct - Nov 20) ────────────────────────────────────────   │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 24 voices                                       │
│  💎 FOSSIL: "Joy-inducing" (first appeared here)                │
│                                                                  │
│  FOSSIL LAYER (Sep and earlier) ─────────────────────────────   │
│  ⚰️  ABANDONED: "multi-agent framework" (not mentioned since)   │
│  🏛️  TIMELESS: "The persona is a garden, not a museum"         │
└─────────────────────────────────────────────────────────────────┘
```

### Why This is Daring

- Claims temporal compression creates meaning
- Treats accumulated voices as a distinct kind of knowledge
- The stratigraphy metaphor unlocks new interfaces (dig, sift, carbon-date)
- Distinguishes "abandoned concerns" from "timeless anchors"

---

## Line 3: Circadian Resonance — Learning Your Rhythms

### Core Metaphor

**Morning voices are vibrations in a resonance chamber.** Over time, patterns emerge: Monday mornings resonate differently than Fridays. Post-vacation mornings have a distinct frequency. The system attunes to these rhythms.

### Key Insight

> *"The system does not prescribe — it attunes."*

It notices when today rhymes with a past successful morning and suggests accordingly. It learns that Kent prefers GENTLE on Mondays and INTENSE on Thursdays. It adapts without demanding.

### Temporal Coordinates

Every voice capture gains temporal coordinates:

```python
@dataclass(frozen=True)
class TemporalCoords:
    day_of_week: int           # 0=Monday ... 6=Sunday
    week_of_year: int          # 1-52
    month: int                 # 1-12
    project_phase: str | None  # "foundation", "building", "shipping"
    after_gap: bool            # True if previous capture was >3 days ago
    streak_length: int         # Consecutive days of captures
```

### Resonance Detection

```python
async def find_resonant(
    today_coords: TemporalCoords,
    limit: int = 5,
) -> list[ResonanceMatch]:
    """Find past mornings that echo today's temporal context."""
    # Compute temporal resonance
    # Weight by: same day of week, similar phase, energy match
    # Return sorted by resonance strength
```

### Weekly Pattern Detection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Your Morning Rhythms (last 30 days)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Weekly Pattern:                                                             │
│  Mon   🧘 GENTLE     ▓▓▓▓░░░░░░ (67% of Mondays)                            │
│  Tue   🎯 FOCUSED    ▓▓▓▓▓▓░░░░ (80%)                                       │
│  Wed   🎯 FOCUSED    ▓▓▓▓▓░░░░░ (75%)                                       │
│  Thu   🔥 INTENSE    ▓▓▓▓▓▓░░░░ (60%)                                       │
│  Fri   🎲 VARIED     ░░░░░░░░░░ (no pattern)                                │
│                                                                              │
│  Today's Resonance:                                                          │
│  💫 Similar mornings: Dec 14, Dec 7, Nov 30 (Saturdays after deep work)      │
│  Those days, you chose: 🧘 GENTLE (2), 🎲 SERENDIPITOUS (1)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Resonance Echo

When resonance is detected, surface it gently:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ☕ Good morning                                                              │
│                                                                              │
│  💫 This morning echoes December 7th...                                     │
│                                                                              │
│  Then, you said:                                                             │
│  "I want to feel like I'm exploring, not completing."                        │
│                                                                              │
│  That morning, you chose 🎲 SERENDIPITOUS and                               │
│  ended up discovering the sheaf coherence pattern.                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Adaptive Ritual

The ritual adapts based on circadian context:

| Context | Adaptation |
|---------|------------|
| Monday | Gentler start, longer Garden View |
| After gap (>3 days) | "Welcome back! What did you dream about while away?" |
| High streak (7+ days) | "🔥 7-day streak! Deep work available." |
| Before deadline | Leaner menu, fewer GENTLE options |

### Why This is Daring

- Commits to learning personal rhythms without explicit programming
- Trusts that patterns will emerge from temporal data
- Adapts the ritual to natural human cycles rather than fighting them

---

## Synthesis: The Three Lines Unified

### Complementary, Not Competing

| Line | Focus | Timescale | Infrastructure |
|------|-------|-----------|----------------|
| **Stigmergy** | Emergent patterns from traces | Days→Weeks | PheromoneField + D-gent |
| **Archaeology** | Excavation across strata | Weeks→Months | Brain search + TableAdapter |
| **Circadian** | Temporal rhythms | Weekly/Seasonal | Temporal indexing + Resonance |

These three approaches can **compose**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     UNIFIED VOICE INTELLIGENCE                               │
│                                                                              │
│   LAYER 1: PERSISTENCE (D-gent + TableAdapter)                              │
│   ├── Exact voice captures with causal chain                                │
│   └── Brain crystals for semantic search                                    │
│                                                                              │
│   LAYER 2: STIGMERGY (PheromoneField)                                       │
│   ├── Concept traces that decay and reinforce                               │
│   └── Association emergence without explicit learning                       │
│                                                                              │
│   LAYER 3: ARCHAEOLOGY (Stratum classification)                             │
│   ├── Surface/Shallow/Deep/Fossil layer analysis                            │
│   └── Theme crystallization over time                                       │
│                                                                              │
│   LAYER 4: CIRCADIAN (Temporal indexing)                                    │
│   ├── Weekly/seasonal pattern detection                                     │
│   └── Resonance matching for adaptive suggestions                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Recommended Implementation: Layered Approach

### Phase 1: Foundation (Required)

**VoicePersistence with D-gent + Brain integration**

This is the mandatory foundation. Without it, nothing else works.

```python
class VoicePersistence:
    """D-gent backed voice storage with semantic search."""

    def __init__(
        self,
        session_maker: async_sessionmaker,
        dgent: DgentProtocol,
        brain: BrainPersistence,
    ):
        self._table = TableAdapter(session_maker, VoiceCapture)
        self._dgent = dgent
        self._brain = brain

    async def capture(self, voice: MorningVoice) -> CaptureResult:
        """Store voice with dual-track persistence."""
        # 1. Store in VoiceCapture table (queryable metadata)
        # 2. Store in D-gent (semantic content for archaeology)
        # 3. Create Brain crystal (for cross-jewel search)
```

**Implementation Order**:
1. Create `models/voice.py` with `VoiceCapture` SQLAlchemy model
2. Create `services/liminal/coffee/persistence.py` with `VoicePersistence`
3. Wire through providers.py and bootstrap.py
4. Migrate existing JSON voices

### Phase 2: Archaeology (Recommended)

**Stratum classification + Theme crystallization**

This adds the temporal depth that makes Voice Archaeology valuable.

```python
class VoiceArchaeology:
    """Excavate meaning from accumulated morning voices."""

    async def classify_stratum(self, voice_date: date) -> VoiceStratum: ...
    async def excavate(self, query: str, strata: list[VoiceStratum]) -> list[Find]: ...
    async def crystallize_themes(self) -> list[ThemeCrystal]: ...
```

**New CLI Commands**:
- `kg coffee archaeology dig --stratum deep`
- `kg coffee archaeology record`
- `kg coffee archaeology emerge`

### Phase 3: Stigmergy (Optional Enhancement)

**Pheromone traces + Association formation**

This adds the emergent learning capability.

```python
class VoicePheromoneField(PheromoneField):
    """Pheromone field specialized for voice captures."""

    async def deposit_with_association(self, concept: str, intensity: float): ...
    async def sense_patterns(self) -> list[str]: ...
```

**Enhancement to Menu**:
- "📍 FROM YOUR PATTERNS" section showing emergent suggestions

### Phase 4: Circadian (Optional Enhancement)

**Temporal indexing + Resonance detection**

This adds the rhythm-aware adaptation.

```python
class CircadianResonance:
    """Detect and adapt to morning rhythms."""

    async def detect_weekly_pattern(self) -> WeeklyPattern: ...
    async def find_resonant_mornings(self, today: TemporalCoords) -> list[Match]: ...
    async def adapt_ritual(self, coords: TemporalCoords) -> RitualAdaptation: ...
```

**New CLI Command**:
- `kg coffee rhythms`

---

## Key Files to Create/Modify

| File | Purpose | Phase |
|------|---------|-------|
| `models/voice.py` (NEW) | VoiceCapture SQLAlchemy model | 1 |
| `services/liminal/coffee/persistence.py` (NEW) | VoicePersistence class | 1 |
| `services/liminal/coffee/archaeology.py` (NEW) | VoiceArchaeology class | 2 |
| `services/liminal/coffee/stigmergy.py` (NEW) | VoicePheromoneField | 3 |
| `services/liminal/coffee/circadian.py` (NEW) | CircadianResonance | 4 |
| `services/liminal/coffee/core.py` | Inject new persistence | 1 |
| `services/liminal/coffee/node.py` | Add archaeology aspects | 2 |
| `services/providers.py` | DI wiring | 1 |
| `services/bootstrap.py` | Service creation | 1 |

---

## Success Criteria

**Phase 1 (Foundation)**:
- [ ] Voice captures persisted via D-gent (not JSON files)
- [ ] Brain crystals created for every voice capture
- [ ] Migration path from JSON → D-gent working
- [ ] All 264+ tests still passing

**Phase 2 (Archaeology)**:
- [ ] Stratum classification working
- [ ] `kg coffee archaeology record` shows fossil record
- [ ] Theme crystallization extracts patterns
- [ ] New tests for archaeology layer

**Phase 3 (Stigmergy)** (optional):
- [ ] PheromoneField integrated with voice captures
- [ ] Menu shows "FROM YOUR PATTERNS" section
- [ ] Traces decay and reinforce correctly

**Phase 4 (Circadian)** (optional):
- [ ] Temporal coordinates stored with each voice
- [ ] Weekly patterns detected
- [ ] `kg coffee rhythms` shows rhythm map

---

## Anti-Patterns to Avoid

1. **Don't break existing CLI** — Current commands must keep working
2. **Don't require Brain** — Graceful degradation if unavailable
3. **Don't slow startup** — Lazy loading for persistence
4. **Don't lose voices** — Migration path from JSON to D-gent
5. **Don't over-engineer** — Phase 1 is the foundation; 2-4 are enhancements
6. **Don't smooth the voice** — Preserve raw captures, analyze metadata

---

## Voice Anchors for This Work

*"The morning mind knows things the afternoon mind has forgotten."*

*"Daring, bold, creative, opinionated but not gaudy."*

*"The persona is a garden, not a museum."*

*"Tasteful > feature-complete."*

---

*Brainstormed: 2025-12-21 | Three creative lines explored, synthesized, ready for implementation.*
