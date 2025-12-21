---
path: plans/morning-coffee-implementation
status: active
progress: 50
last_touched: 2025-12-21
touched_by: claude-opus-4
blocking: []
enables: [liminal-protocols, anti-sausage-voice-loop]
session_notes: |
  Synthesized from brainstorming/2025-12-21-morning-coffee-ritual.md
  Spec written to spec/services/morning-coffee.md
  First Liminal Transition Protocol — pattern for kg pause, kg evening, kg return
  Phase 2 complete: 224 tests, all generators implemented
phase_ledger:
  PLAN: complete
  ACT: in_progress
  REFLECT: not_started
---

# Morning Coffee Implementation Plan

> *"The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale."*

**Spec:** `spec/services/morning-coffee.md`
**Implementation:** `impl/claude/services/liminal/`
**Estimated Effort:** 2-3 sessions

---

## Phase 1: Core Data Structures (Session 1) ✅ COMPLETE

### 1.1 Define Types

```
impl/claude/services/liminal/coffee/types.py
```

**Deliverables:**
- [x] `CoffeeState` enum (DORMANT, GARDEN, WEATHER, MENU, CAPTURE, TRANSITION)
- [x] `ChallengeLevel` enum with properties (emoji, description, cognitive_load)
- [x] `Movement` dataclass (name, prompt, duration_hint, requires_input)
- [x] `GardenItem` dataclass (files_changed, description, category)
- [x] `GardenView` dataclass (harvest, growing, sprouting, seeds)
- [x] `WeatherPattern` dataclass (type, label, description)
- [x] `ConceptualWeather` dataclass (refactoring, emerging, scaffolding, tension)
- [x] `MenuItem` dataclass (label, description, level, agentese_path, source)
- [x] `ChallengeMenu` dataclass (gentle, focused, intense, serendipitous)
- [x] `MorningVoice` dataclass (date, non_code_thought, eye_catch, success_criteria)

**Test:** 38 tests for type instantiation and frozen immutability ✅

### 1.2 Define Polynomial

```
impl/claude/services/liminal/coffee/polynomial.py
```

**Deliverables:**
- [x] `COFFEE_POLYNOMIAL` with 6 positions
- [x] Transition function respecting skippable movements
- [x] Law: any movement can transition to DORMANT (exit)
- [x] Law: manifest stays in same state
- [x] Multiple input formats (string, dict, RitualEvent)

**Test:** 47 tests for state transitions, laws, and full ritual flow ✅

**Total Phase 1 Tests:** 85 passing

---

## Phase 2: Movement Implementations (Session 1-2) ✅ COMPLETE

### 2.1 Garden View Generator ✅

```
impl/claude/services/liminal/coffee/garden.py
```

**Inputs:**
- `git diff --stat` (yesterday's file changes)
- `NOW.md` parsing (percentage progress)
- Recent brainstorming files

**Deliverables:**
- [x] `parse_git_stat(since: datetime) -> list[GardenItem]`
- [x] `parse_now_md() -> dict[str, float]` (jewel → percentage)
- [x] `generate_garden_view() -> GardenView`

**Patterns Applied:**
- Signal Aggregation (Pattern 4) for categorizing changes
- Dual-Channel Output (Pattern 7) for CLI + semantic

**Test:** 34 tests ✅

### 2.2 Conceptual Weather Analyzer ✅

```
impl/claude/services/liminal/coffee/weather.py
```

**Inputs:**
- `plans/*.md` headers and status
- Git commit messages for semantic patterns

**Deliverables:**
- [x] `detect_refactoring() -> list[WeatherPattern]`
- [x] `detect_emerging() -> list[WeatherPattern]`
- [x] `detect_scaffolding() -> list[WeatherPattern]`
- [x] `detect_tension() -> list[WeatherPattern]`
- [x] `generate_weather() -> ConceptualWeather`

**Patterns Applied:**
- Signal Aggregation (Pattern 4) for pattern detection
- Bounded History (Pattern 8) for recent crystals

**Test:** 36 tests ✅

### 2.3 Menu Generator ✅

```
impl/claude/services/liminal/coffee/menu.py
```

**Inputs:**
- TODO items from plans and NOW.md
- Garden/Weather context for enrichment

**Deliverables:**
- [x] `classify_challenge(item: str) -> ChallengeLevel`
- [x] `generate_menu() -> ChallengeMenu`
- [x] Serendipity option always present

**Patterns Applied:**
- Multiplied Context (Pattern 3): context × item difficulty = placement
- Enum Property (Pattern 2): ChallengeLevel with metadata

**Test:** 38 tests ✅

### 2.4 Voice Capture ✅

```
impl/claude/services/liminal/coffee/capture.py
```

**Outputs:**
- Voice anchor to Brain (if substantive)
- XDG-compliant persistence

**Deliverables:**
- [x] `CaptureSession` for multi-question flow
- [x] `MorningVoice.as_voice_anchor() -> dict | None`
- [x] Persistence to voice anchor store (`save_voice`, `load_voice`)
- [x] History analysis (`extract_voice_patterns`)

**Patterns Applied:**
- Container Owns Workflow (Pattern 1): CoffeeService owns CaptureSession

**Test:** 31 tests ✅

**Total Phase 2 Tests:** 139 passing (34 + 36 + 38 + 31)

---

## Phase 3: Service & AGENTESE Integration (Session 2)

### 3.1 Coffee Service

```
impl/claude/services/liminal/coffee/core.py
```

**Deliverables:**
- [ ] `CoffeeService` class with DI-injected dependencies
- [ ] Methods: `garden()`, `weather()`, `menu()`, `capture()`, `begin()`
- [ ] State machine via COFFEE_POLYNOMIAL
- [ ] Event emission via SynergyBus

**Patterns Applied:**
- No Hollow Services (Pattern 15): require providers in constructor
- Async-Safe Emission (Pattern 6): emit events from sync methods

### 3.2 AGENTESE Node Registration

```
impl/claude/services/liminal/coffee/node.py
```

**Deliverables:**
- [ ] `@node("time.coffee", ...)` registration
- [ ] All aspects implemented
- [ ] Affordances defined
- [ ] Provider registered in `services/providers.py`

**Patterns Applied:**
- Contract-First Types (Pattern 13): response types defined
- DI registration verified

**Test:** Node discovery, aspect invocation

### 3.3 CLI Handler

```
impl/claude/protocols/cli/handlers/coffee.py
```

**Deliverables:**
- [ ] `kg coffee` — full ritual
- [ ] `kg coffee --quick` — garden + menu
- [ ] `kg coffee garden|weather|menu|capture` — individual movements
- [ ] Rich CLI output with boxes and emoji

**Patterns Applied:**
- Dual-Channel Output (Pattern 7)

---

## Phase 4: Polish & Integration (Session 3)

### 4.1 Cross-Jewel Wiring

**Deliverables:**
- [ ] Muse integration: consume story arc for menu suggestions
- [ ] Brain integration: store voice captures as crystals
- [ ] Gardener integration: season context for challenge gradients
- [ ] Anti-sausage: voice anchors become reference

### 4.2 History & Tracking

**Deliverables:**
- [ ] `kg coffee history` — past captures
- [ ] Voice evolution visualization (how morning Kent changes over time)
- [ ] Success criteria tracking (did day meet morning expectations?)

### 4.3 Documentation

**Deliverables:**
- [ ] Update HYDRATE.md with Coffee status
- [ ] Add to systems-reference.md
- [ ] CLI help text

---

## Implementation Order

```
Phase 1: Types → Polynomial
     ↓
Phase 2: Garden → Weather → Menu → Capture  (can parallelize)
     ↓
Phase 3: Service → Node → CLI
     ↓
Phase 4: Integration → History → Docs
```

---

## Test Strategy

| Layer | Test Type | Count Target |
|-------|-----------|--------------|
| Types | Unit (frozen, immutable) | 10 |
| Generators | Property-based (various inputs) | 15 |
| Service | Integration (state machine) | 10 |
| CLI | Snapshot (output format) | 5 |
| **Total** | | **40** |

---

## Success Criteria

1. **Functional**: `kg coffee` runs full ritual in ~10 minutes
2. **Skippable**: Any movement exits cleanly with `Ctrl+C` or explicit skip
3. **Voice Preserved**: Morning captures become voice anchors
4. **Non-Demanding**: Garden/Weather are pure observation, no input required
5. **Joyful**: Ritual feels like warming up, not booting up

---

## Voice Anchors for Implementation

*"Flit in and out of flow like a musician or artist"*
*"Fresh interactions at his relatively most relaxed and authentic"*
*"The valence and magnitude of challenge suited to my taste that instant"*

---

## Next Session

Start with **Phase 1.1**: Define types in `types.py`. The categorical foundation makes everything else straightforward.

---

*"The morning mind knows things the afternoon mind has forgotten."*
