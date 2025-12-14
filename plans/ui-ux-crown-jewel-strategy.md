---
path: plans/ui-ux-crown-jewel-strategy
status: active
progress: 0
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [dashboard-textual-refactor, i-gent-radical-redesign]
session_notes: |
  Crown Jewel Grand Strategy based on Radical Redesign Proposal PDF.
  Grounded in spec/principles.md. Full 11-phase N-cycle ceremony.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.03
  returned: 0.0
---

# UI/UX Crown Jewel Grand Strategy

> *"The interface IS part of the system. Viewing changes what is viewed."*

**Source Document**: `docs/Radical Redesign Proposal for the Kgents UI_UX Ecosystem.pdf`
**Grounding**: `spec/principles.md` (Seven Principles + Three Meta-Principles)
**Method**: Full 11-Phase N-Cycle Ceremony (AD-005)

---

## The Resonance Map

The Radical Redesign Proposal is not merely *aligned* with kgents principles—it is their **apotheosis** in visual-experiential space. Every proposed feature maps to a principle:

| Proposal Section | Principle Alignment | Resonance Strength |
|------------------|--------------------|--------------------|
| Perceptual Overlays | Accursed Share (entropy visible) | **Deep** |
| Dialectic Dashboards | AGENTESE (refine aspect) | **Deep** |
| Temporal Scaffolds | Heterarchical (time composition) | **Deep** |
| Visual Composition Flows | Composable (>> as UI gesture) | **Deep** |
| Stigmergic Gardens | Generative (traces from rules) | **Deep** |
| Verb-First UI Language | AGENTESE (No View From Nowhere) | **Exact** |
| View-As Mode | Polymorphic Observation | **Exact** |
| Handle Navigation | Logos invocation | **Exact** |

**The Core Insight**: The redesign proposes making the UI an **embodied AGENTESE interpreter**. Every UI gesture maps to `logos.invoke(path)`. This is not UI design—it is **ontology implementation**.

---

## Strategic Framing

### What This Is

A **Crown Jewel Implementation** that:
1. Transforms I-gent from dashboard to **living substrate**
2. Makes AGENTESE tangible through interaction
3. Demonstrates the seven principles visibly in operation
4. Creates the benchmark for agent-centric UI/UX

### What This Is Not

- Feature sprawl (anti-tasteful)
- Incremental improvement (anti-generative)
- Technical debt migration (that's `dashboard-textual-refactor.md`)
- Web-first (TUI-first, web follows naturally via Textual-web)

### Exit Criteria

1. `kg garden` shows living stigmergic field with visible pheromone traces
2. AGENTESE handles work as navigation: `world.robin.manifest` opens Robin's page
3. Dialectic dashboard renders thesis/antithesis/synthesis in real-time
4. Timeline panel supports time-travel debugging (select point → see state)
5. Visual composition: keyboard-driven agent wiring with law verification
6. Kent says "this is amazing" (HARD REQUIREMENT per `_focus.md`)

---

## The Four Waves

Borrowing from `dashboard-textual-refactor.md` wave structure, but elevated to Crown Jewel ceremony:

### Wave 1: The Foundation (Architectural Prerequisites)

**Dependency**: `dashboard-textual-refactor.md` Phases 1-4
**Purpose**: Clean architecture enables radical features

| Component | From Refactor Plan | Crown Jewel Extension |
|-----------|--------------------|-----------------------|
| EventBus | Phase 1 | Add `PheromoneTraceEvent`, `DialecticPhaseEvent` |
| KgentsScreen | Phase 2 | Add `AGENTESE_HANDLE` class var for navigation |
| Mixins | Phase 3 | Add `DialecticMixin`, `TemporalMixin` |
| Services | Phase 4 | Add `LogosNavigator`, `StigmergyEngine` |

**Estimated Effort**: 3-4 agents parallel, ~2-3 sessions

### Wave 2: The Ontology Layer (AGENTESE Integration)

**Purpose**: Make AGENTESE tangible as navigation and action

| Feature | Implementation | Principle |
|---------|----------------|-----------|
| Handle Navigation | Command palette accepts `world.*` paths → Logos resolves → UI navigates | AGENTESE |
| Affordance Actions | `affordances()` → dynamic action buttons on pages | Ethical |
| View-As Mode | `view-as <agent>` command sets observer context for manifest | Polymorphism |
| Observer Feedback | "[perturbation]" notices when observation affects state | Transparency |

**New Files**:
- `impl/claude/agents/i/services/logos_navigator.py`
- `impl/claude/agents/i/screens/agentese_palette.py`
- `impl/claude/agents/i/widgets/affordance_menu.py`

**Estimated Effort**: 2-3 agents parallel, ~2 sessions

### Wave 3: The Perceptual Layer (New Metaphors)

**Purpose**: Implement the four major new views from the proposal

#### 3A: Stigmergic Garden
- Brownian motion for agent glyphs
- Pheromone trace rendering (fading backgrounds/gradients)
- Context gravity (agents drift toward `*` tasks)
- Conflict repulsion (contradicting agents push apart)

**New Files**:
- `impl/claude/agents/i/widgets/stigmergic_field.py`
- `impl/claude/agents/i/data/pheromone_grid.py`

#### 3B: Dialectic Dashboard
- Thesis/antithesis/synthesis panels
- Real-time debate visualization for `.refine` aspect
- Value alignment meters during reasoning
- Human intervention hooks

**New Files**:
- `impl/claude/agents/i/screens/dialectic.py`
- `impl/claude/agents/i/widgets/thesis_panel.py`

#### 3C: Temporal Scaffolds
- Interactive timeline with scrollable events
- State snapshot at selected time point
- Play/pause/rewind controls
- Future scheduling visualization

**New Files**:
- `impl/claude/agents/i/screens/temporal.py`
- `impl/claude/agents/i/widgets/timeline_scrubber.py` (enhance existing)

#### 3D: Visual Composition Flows
- Keyboard-driven agent linking
- Type-safe composition (law verification before connecting)
- Generative composition via `void.compose.sip`
- Ghost layout for suggestions

**New Files**:
- `impl/claude/agents/i/screens/composer.py`
- `impl/claude/agents/i/widgets/composition_canvas.py`

**Estimated Effort**: 4 agents parallel (one per sub-wave), ~3-4 sessions

### Wave 4: The Integration Layer (Polish and Coherence)

**Purpose**: Wire everything together, achieve crown jewel status

| Task | Description |
|------|-------------|
| Overlay System | Toggle key (`o`) cycles overlays: none → pheromones → semantic |
| Command Palette | `/` search with handle autocomplete |
| Help Integration | `?` overlay pulls from spec files dynamically |
| Theme Coherence | Earth theme with temperature shifts |
| Demo Mode | `kg garden --demo` with pre-computed hotdata |

**New Files**:
- `impl/claude/agents/i/services/overlay_manager.py`
- `impl/claude/agents/i/data/demo_fixtures.py`

**Estimated Effort**: 2-3 agents, ~2 sessions

---

## N-Phase Ledger: Crown Jewel Ceremony

### PLAN (This Document)
- **Scope**: Complete UI/UX transformation per Radical Redesign Proposal
- **Non-Goals**: Web-specific features (Textual-web handles this), mobile, electron
- **Exit Criteria**: Strategy document approved, waves defined
- **Entropy Sip**: 0.10 (high novelty requires exploration budget)
- **Status**: TOUCHED

### RESEARCH (Next Phase)
- **Files to Map**:
  - `impl/claude/agents/i/screens/*.py` - Current screen inventory
  - `spec/i-gents/*.md` - I-gent specifications
  - `impl/claude/protocols/agentese/logos.py` - Handle resolution
  - `impl/claude/agents/i/widgets/*.py` - Widget inventory
- **Unknowns**:
  - How does Textual handle dynamic background gradients for pheromones?
  - Can timeline scrubber replay from O-gent event logs?
  - What's the latency of Logos resolution for navigation?
- **Blockers**: None identified (dashboard-textual-refactor is parallel track)

### DEVELOP (Contracts)
- **StigmergyEngine Protocol**:
  ```python
  class StigmergyEngine(Protocol):
      def tick(self) -> None: ...
      def deposit_pheromone(self, pos: Position, type: PheromoneType, intensity: float) -> None: ...
      def get_gradient(self, pos: Position) -> PheromoneGradient: ...
  ```
- **LogosNavigator Protocol**:
  ```python
  class LogosNavigator(Protocol):
      def navigate(self, handle: str) -> None: ...
      def autocomplete(self, partial: str) -> list[str]: ...
  ```

### STRATEGIZE (This Document)
- **Wave Order**: 1 → 2 → 3 (parallel within) → 4
- **Parallel Tracks**: Wave 3 sub-waves can run simultaneously
- **Checkpoints**: After each wave, verify tests pass and demo works
- **Status**: TOUCHED

### CROSS-SYNERGIZE (Pending)
- **Compositions to Explore**:
  - StigmergyEngine + FluxReflector (pheromones visible in CLI logs?)
  - LogosNavigator + existing CommandPalette
  - DialecticDashboard + K-gent persona (K-gent as dialectic participant?)
  - TemporalScaffold + M-gent memory (timeline shows memory crystallization?)

### IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
- **Deferred**: Execution begins after strategy approval

---

## Branch Candidates

| Branch | Type | Classification |
|--------|------|----------------|
| Web-specific features | Parallel | Deferred to Wave 5 |
| VSCode extension | Parallel | Deferred to future |
| Accessibility audit | Parallel | Can run after Wave 2 |
| Performance profiling | Sequential | Runs after Wave 3 |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tests | All pass, mypy clean | `uv run pytest && uv run mypy` |
| Response Time | <100ms for navigation | Profiling |
| Kent Delight | "this is amazing" | Human feedback |
| Demo Quality | Compelling 60-second tour | Video recording |
| Autopoiesis Score | >50% from spec | LOC comparison |

---

## The Crown Jewel Test

The implementation succeeds if:

1. **Tasteful**: Every element earns its place
2. **Curated**: Three layers (physical/topological/semantic), not infinite configurability
3. **Ethical**: Transparent about agent state; shows errors honestly
4. **Joy-Inducing**: Brownian motion creates emergent beauty
5. **Composable**: The field IS a composition graph; entities ARE morphisms
6. **Heterarchical**: No fixed "main view"; user chooses focus
7. **Generative**: This spec generates implementation

And the meta-principles:
8. **Accursed Share**: Pheromone traces are the waste made visible
9. **AGENTESE**: Every UI gesture is a `logos.invoke()` call
10. **Personality Space**: The interface has K-gent's warmth

---

*"The garden will not only grow; it will flourish, and invite the user to cultivate it with unprecedented agility and insight."*
