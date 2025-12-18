---
path: plans/park-town-design-overhaul
status: active
progress: 95
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables:
  - punchdrunk-park
  - agent-town
  - coalition-forge
session_notes: |
  Design overhaul for Park & Town using Gallery primitives.
  Goal: World-class, delightful, strongly visionary experiences.
  Method: SpecGraph workflow (spec -> impl), first principles.
  2025-12-18: SpecGraph audit complete - 100% alignment. Ready for Phase 1.
  2025-12-18: Phase 1 Foundation STARTED. Created categorical/ with 5 components + 7 presets.
  2025-12-18: Phase 2 Town Enhancement COMPLETE:
    - CitizenPanel: Embedded polynomial state machine with valid transitions
    - TownTracePanel: N-gent witness for town events
    - ObserverSelector: Switch between architect/poet/economist umwelts
    - Mobile: BottomDrawer for trace panel, observer in header
    - FirstVisitOverlay: Welcome modal for first-time visitors
    - EventFeed: Toggle between Events and Trace views
  2025-12-18: Phase 3 Park Enhancement COMPLETE:
    - PhaseVisualization: Crisis phase with embedded polynomial state machine
    - TimerMachine: Timer countdown with polynomial state visualization
    - ConsentDebtMachine: Debt levels as HEALTHY->ELEVATED->HIGH->CRITICAL phases
    - MaskCardEnhanced: Masks with affordances preview and debt cost indicator
    - ParkTracePanel: N-gent witness for park events (phase, timer, force, mask)
    - RunningScenario: Integrated all Phase 3 components into desktop & mobile layouts
    - Mobile: BottomDrawer for masks and trace, fixed action bar at bottom
  2025-12-18: Phase 4 Teaching Layer COMPLETE:
    - useTeachingMode hook with localStorage persistence (hooks/useTeachingMode.tsx)
    - TeachingToggle component (compact lightbulb button) in both Town and Park headers
    - Wired teachingEnabled to TownVisualization: TownTracePanel showTeaching prop
    - Wired teachingEnabled to ParkVisualization: ConsentDebtMachine, PhaseVisualization,
      ParkTracePanel, MaskGridEnhanced all respect teaching toggle
    - Mobile teaching toggle in Town header and Park masks panel
    - Global toggle persists across sessions via localStorage
  2025-12-18: Phase 5 Polish & Integration COMPLETE:
    - Added PHASE_GLOW design tokens (constants/colors.ts)
    - Added TEACHING_GRADIENT design tokens (constants/colors.ts)
    - Added EDGE_ANIMATION config for consistent transitions
    - Updated StateIndicator to use centralized PHASE_GLOW tokens
    - Updated TeachingCallout to use centralized TEACHING_GRADIENT tokens
    - Added keyboard navigation (Enter/Space) to StateIndicator
    - Added aria-labels and screen reader support (role="status/button")
    - Added focus-visible outline styling for accessibility
    - Added motion-reduce: support for prefers-reduced-motion
    - Updated crown-jewel-patterns.md with Pattern 14 (Teaching Mode Toggle)
    - TypeScript validation passes
    - Lazy loading: LazyPolynomialPlayground, LazyOperadWiring, LazyTownLive exports
    - GalleryPage and PilotCard updated with Suspense + lazy components
    - Mesa mobile optimizations: smaller cells, fewer event lines, skip grid lines,
      disable antialias, lower resolution, skip region labels, scaled citizens
    - TownVisualization passes mobile prop to Mesa for mobile layout
    - SSE connection management reviewed - follows best practices (refs, cleanup, batching)
  Remaining: QA visual testing, final review
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: complete
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.04
  returned: 0.0
---

# Park & Town Design Overhaul

> *"The aesthetic is not decoration—it is the categorical structure made perceivable."*

## Executive Vision

Transform Punchdrunk Park and Agent Town from functional applications into **world-class immersive experiences** by deeply integrating the Gallery pilots' interactive primitives with the underlying categorical structure.

**The Governing Insight**: Every UI element is a projection of PolyAgent × Operad × Sheaf. The Gallery pilots made this visible—now we apply it systematically.

---

## Part I: First Principles Analysis

### The Categorical Foundation (What We're Projecting)

Both Park and Town instantiate the same three-layer pattern:

| Layer | Town | Park |
|-------|------|------|
| **Polynomial** | `CITIZEN_POLYNOMIAL` (5 phases) | `DIRECTOR_POLYNOMIAL` (5 phases) |
| **Operad** | `TOWN_OPERAD` (8 operations, 3 laws) | `DIRECTOR_OPERAD` (8 operations, 6 laws) |
| **Sheaf** | Citizen coherence across views | Session coherence across masks |

**The Insight**: The Gallery pilots made these structures *tangible*. PolynomialPlayground visualizes state machines; OperadWiring shows composition. Town and Park should embed these same primitives to teach their domain structure.

### The Current State: What's Working

| Aspect | Town | Park |
|--------|------|------|
| **Streaming** | ✅ SSE via useTownStreamWidget | ❌ Polling (auto-tick interval) |
| **Density Adaptation** | ✅ ElasticSplit, responsive | 🟡 Fixed layout |
| **Phase Visualization** | 🟡 Text badge in header | ✅ PhaseIndicator component |
| **Event Feed** | ✅ Collapsible EventFeed | 🟡 Timer outcomes only |
| **Teaching** | ❌ No pedagogical elements | ❌ No pedagogical elements |
| **Polynomial Exposure** | ❌ Hidden in backend | ❌ Hidden in backend |
| **Operad Exposure** | ❌ Hidden in backend | ❌ Hidden in backend |

### The Current State: What's Not Working

1. **No Teaching Layer**: Users interact without understanding the underlying model
2. **Opaque State Machines**: Citizen/Director phases exist but aren't visualized as state machines
3. **No Composition Visibility**: Available operations aren't shown based on current phase
4. **Scattered Components**: PhaseIndicator, TimerDisplay, ConsentMeter not unified into design system
5. **No Trace History**: N-gent witness pattern not surfaced
6. **Mobile Experience**: Park lacks mobile adaptation entirely

---

## Part II: 15 User Journey Interactions

> *"Design the soil and the season, not the flower."*

### Journey 1: The Newcomer's First Town Visit

**Scenario**: User lands on `/town/demo` with no context.

**Current**: Immediately sees Mesa with moving dots. No explanation.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEACHING OVERLAY (first visit only)                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  "Agent Town is a living simulation of polynomial agents.                │ │
│  │   Each citizen follows a state machine with 5 phases.                    │ │
│  │   Watch: Socrates is currently REFLECTING..."                            │ │
│  │                                                                           │ │
│  │   [Got it] [Show me how it works]                                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Mesa with highlighted citizen                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**: `<FirstVisitOverlay jewel="town" />` with dismiss persistence in localStorage.

---

### Journey 2: Understanding a Citizen's State Machine

**Scenario**: User clicks on Socrates (REFLECTING phase).

**Current**: CitizenPanel shows name, archetype, and eigenvector values.

**Redesigned**:
```
┌───────────────────────────────────────────┐
│  SOCRATES                                  │
│  Scholar Archetype                         │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ [PolynomialPlayground embedded]       │ │
│  │                                        │ │
│  │   IDLE ──▶ SOCIALIZING ──▶ WORKING   │ │
│  │    │                           │       │ │
│  │    └────▶ REFLECTING ◀─────────┘       │ │
│  │              │ (current, glowing)      │ │
│  │              ▼                         │ │
│  │          RESTING                       │ │
│  │                                        │ │
│  │   Valid next: [rest] [socialize]       │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  💡 Teaching: "Only 'wake' is valid from   │
│     RESTING—the Right to Rest enforced    │
│     by directions"                        │
└───────────────────────────────────────────┘
```

**Components**:
- Embed `<PolynomialPlayground preset="citizen" currentState={citizen.phase} compact />` in CitizenPanel
- Derive `validNextInputs` from `citizen_directions(phase)`

---

### Journey 3: Watching Town Operations Compose

**Scenario**: User wants to understand how citizen interactions form.

**Current**: Events appear in feed as text ("Socrates greeted Marcus").

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EVENT FEED (with operad visualization)                                      │
│                                                                               │
│  [42] greet(Socrates, Marcus)                                               │
│       ┌─────────────┐     ┌─────────────┐                                   │
│       │  Socrates   │ ──▶ │   Marcus    │                                   │
│       │  SOCIALIZING│     │   IDLE      │                                   │
│       └─────────────┘     └─────────────┘                                   │
│       Result: Relationship formed                                            │
│                                                                               │
│  [41] solo(Hypatia)                                                          │
│       ┌─────────────┐                                                        │
│       │  Hypatia    │ reflects alone                                         │
│       │  WORKING    │                                                        │
│       └─────────────┘                                                        │
│                                                                               │
│  💡 Teaching: "Operad operations have arity—greet takes 2 citizens,          │
│     solo takes 1. TOWN_OPERAD defines which compositions are valid."         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Components**:
- `<OperationVisualization event={event} />` showing mini-wiring diagram
- Link to full `<OperadWiring operad="TOWN_OPERAD" />` in dedicated panel

---

### Journey 4: Park Crisis Phase Understanding

**Scenario**: User starts a data-breach crisis scenario.

**Current**: Phase badge shows "INCIDENT" with manual transition buttons.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CRISIS PHASE MACHINE                                                        │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  [PolynomialPlayground preset="crisis_phase"]                            │ │
│  │                                                                           │ │
│  │    NORMAL ──breach──▶ INCIDENT ──respond──▶ RESPONSE ──resolve──▶ RECOVERY│
│  │      │                   ▲ (current)           │                         │ │
│  │      │                   │                     │                         │ │
│  │      └─────escalate──────┘                     └─────fail────▶ NORMAL    │ │
│  │                                                                           │ │
│  │   Valid inputs at INCIDENT:                                              │ │
│  │   [Transition to RESPONSE] [Force (2 remaining)] [Add Timer]             │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  💡 Teaching: "The crisis polynomial defines when transitions are valid.     │
│     Force spending affects consent debt, which constrains future options."  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**:
- New preset in PolynomialPlayground: `crisis_phase`
- Positions: NORMAL, INCIDENT, RESPONSE, RECOVERY
- Edges derived from `ParkCrisisPhase` valid transitions

---

### Journey 5: Timer State Machine Visualization

**Scenario**: Multiple compliance timers running (GDPR, SLA).

**Current**: TimerGrid shows countdown with color-coded urgency.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIMER: GDPR 72h                                                             │
│                                                                               │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │  [Mini state machine]                                 │                   │
│  │                                                        │                   │
│  │  PENDING ─▶ ACTIVE ─▶ WARNING ─▶ CRITICAL ─▶ EXPIRED  │                   │
│  │               │                     ▲ (current)       │                   │
│  │               │                     │ 04:23:17        │                   │
│  │               └─────────────────────┘                 │                   │
│  │                                                        │                   │
│  │  ████████████████░░░░ 71% elapsed                     │                   │
│  └──────────────────────────────────────────────────────┘                   │
│                                                                               │
│  💡 Teaching: "Timers are polynomial agents—their phase determines           │
│     valid operations. At CRITICAL, force becomes more expensive."           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**New Preset**: `timer_state` with positions PENDING, ACTIVE, WARNING, CRITICAL, EXPIRED

---

### Journey 6: Consent Debt as Polynomial State

**Scenario**: User has used 2 of 3 forces, debt at 65%.

**Current**: ConsentMeter shows bar + force count.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONSENT DEBT MACHINE                                                        │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │   HEALTHY ──▶ ELEVATED ──▶ HIGH ──▶ CRITICAL                     │       │
│  │                              ▲ (65% debt)                         │       │
│  │                              │                                    │       │
│  │   At HIGH:                                                        │       │
│  │   • Force costs 3x tokens                                         │       │
│  │   • Injection requires mask consent                               │       │
│  │   • Citizens may refuse interactions                              │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                               │
│  Forces: ●●○ (1 remaining)                                                   │
│                                                                               │
│  [Use Force] (Warning: Debt will reach CRITICAL)                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Connection**: Consent debt is a state variable that affects valid operations via `consent_constraint` law.

---

### Journey 7: Director Operad Visualization

**Scenario**: User explores what the "invisible director" can do.

**Current**: No visibility into director mechanics.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  THE INVISIBLE DIRECTOR                                                      │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ [OperadWiring operad="DIRECTOR_OPERAD"]                                  │ │
│  │                                                                           │ │
│  │   Available Operations:                                                   │ │
│  │   ┌─────────┐  ┌──────────────┐  ┌────────┐                              │ │
│  │   │ observe │  │ build_tension│  │ inject │                              │ │
│  │   │  arity=1│  │   arity=1    │  │ arity=2│                              │ │
│  │   └─────────┘  └──────────────┘  └────────┘                              │ │
│  │                                                                           │ │
│  │   Laws (all verified ✓):                                                  │ │
│  │   • consent_constraint: inject requires debt <= threshold                 │ │
│  │   • cooldown_constraint: min time between injections                      │ │
│  │   • tension_flow: building leads to inject or observe                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  💡 Teaching: "The director is invisible—guests never feel directed.         │
│     Serendipity appears as lucky coincidence, not orchestration."           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**: Link "Learn More" from Park to dedicated DIRECTOR_OPERAD explorer.

---

### Journey 8: Mask Selection with Affordance Preview

**Scenario**: User browses available dialogue masks.

**Current**: MaskSelector shows list with name + description.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DIALOGUE MASKS                                                              │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │ │
│  │  │  🎭 Medea       │  │  🎭 Prospero    │  │  🎭 Hecuba      │          │ │
│  │  │  Deceptive      │  │  Commanding     │  │  Grieving       │          │ │
│  │  │                 │  │                 │  │                 │          │ │
│  │  │  Affordances:   │  │  Affordances:   │  │  Affordances:   │          │ │
│  │  │  • Misdirect    │  │  • Command      │  │  • Appeal       │          │ │
│  │  │  • Feign        │  │  • Summon       │  │  • Lament       │          │ │
│  │  │  • Betray       │  │  • Exile        │  │  • Invoke       │          │ │
│  │  │                 │  │                 │  │                 │          │ │
│  │  │  Debt Cost: +5% │  │  Debt Cost: +8% │  │  Debt Cost: +3% │          │ │
│  │  │                 │  │                 │  │                 │          │ │
│  │  │  [Don Mask]     │  │  [Don Mask]     │  │  [Don Mask]     │          │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  💡 Teaching: "Each mask changes your available affordances.                 │
│     This is observer-dependent—AGENTESE in action."                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**New Component**: `<MaskCard mask={mask} affordances={mask.affordances} />` showing preview.

---

### Journey 9: Trace History Panel (N-gent Witness)

**Scenario**: User wants to see what happened in the last 5 minutes.

**Current**: Events list with auto-scroll.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRACE HISTORY (N-gent Witness)                                              │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Timeline                                                                 │ │
│  │  ───●─────●─────●─────●─────●─────●─────●───▶                             │ │
│  │    42    43    44    45    46    47    48                                 │ │
│  │                                                                           │ │
│  │  [48] Phase: INCIDENT → RESPONSE                                          │ │
│  │       consent_debt: 0.45 → 0.52                                           │ │
│  │       Trigger: Manual transition                                          │ │
│  │                                                                           │ │
│  │  [47] Timer: SLA entered WARNING                                          │ │
│  │       Remaining: 00:45:00                                                 │ │
│  │                                                                           │ │
│  │  [46] Force used (2/3)                                                    │ │
│  │       consent_debt: 0.35 → 0.45                                           │ │
│  │       Reason: Timer pressure                                              │ │
│  │                                                                           │ │
│  │  [45] Mask donned: Prospero                                               │ │
│  │       New affordances: [Command, Summon, Exile]                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  💡 Teaching: "Every state change is recorded. time.*.witness reveals        │
│     the narrative arc of your session."                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**New Component**: `<TracePanel events={traceEvents} />` with timeline scrubber.

---

### Journey 10: Coalition Formation in Town

**Scenario**: Multiple citizens form a coalition for a task.

**Current**: Not implemented (coalition-forge plan).

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COALITION: Research Team                                                    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  [OperadWiring showing coalition composition]                             │ │
│  │                                                                           │ │
│  │   ┌──────────┐         ┌──────────────────────────┐                      │ │
│  │   │ Socrates │ ──┐     │      COALITION           │                      │ │
│  │   │ (Scholar) │   │     │                          │                      │ │
│  │   └──────────┘   ├────▶│   Mission: Research      │──▶ Deliverable      │ │
│  │   ┌──────────┐   │     │   Phase: FORMING         │                      │ │
│  │   │ Hypatia  │ ──┤     │   Quorum: 2/3            │                      │ │
│  │   │ (Builder) │   │     │                          │                      │ │
│  │   └──────────┘   │     └──────────────────────────┘                      │ │
│  │   ┌──────────┐   │                                                        │ │
│  │   │   ???    │ ──┘  (pending vote)                                        │ │
│  │   └──────────┘                                                            │ │
│  │                                                                           │ │
│  │   propose >> vote >> merge → Active Coalition                             │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  💡 Teaching: "Coalition formation is operad composition.                    │
│     The quorum law ensures vote_count >= threshold implies active."         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Future**: When coalition-forge ships, integrate OperadWiring for COALITION_OPERAD.

---

### Journey 11: Mobile Town Experience

**Scenario**: User on phone wants to check on their town.

**Current**: ElasticSplit collapses, but Mesa is cramped.

**Redesigned**:
```
┌─────────────────────────┐
│  Town: demo             │
│  Day 5 | AFTERNOON      │
├─────────────────────────┤
│                         │
│     [Mesa full-width]   │
│                         │
│  ●K  ●H                 │
│         ●M              │
│    ●A       ●L          │
│                         │
├─────────────────────────┤
│  Recent: Socrates greeted│
│                         │
│  ▲ Event Feed (tap)     │
└─────────────────────────┘
│  [Play] [Citizen] [?]   │
└─────────────────────────┘
```

**Components**:
- FloatingActions for Play/Citizen/Info
- BottomDrawer for EventFeed and CitizenPanel
- Mesa takes full viewport height minus header/footer

---

### Journey 12: Mobile Park Experience

**Scenario**: User on phone during a crisis drill.

**Current**: Fixed layout doesn't adapt.

**Redesigned**:
```
┌─────────────────────────┐
│  Data Breach | INCIDENT │
│  GDPR: 04:23:17 ⚠️      │
├─────────────────────────┤
│                         │
│  ┌───────────────────┐  │
│  │ Consent: ████░ 65%│  │
│  │ Forces: ●●○       │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │ Phase Machine     │  │
│  │ [compact poly]    │  │
│  │ NORMAL→INCIDENT→? │  │
│  └───────────────────┘  │
│                         │
│  [Actions ▼]            │
├─────────────────────────┤
│  [Force] [Mask] [Phase] │
└─────────────────────────┘
```

**Components**:
- Compact PolynomialPlayground for crisis phase
- BottomDrawer for Masks, Timers, Actions
- FloatingActions for primary controls

---

### Journey 13: Scenario Summary with Learnings

**Scenario**: User completes a crisis scenario.

**Current**: SummaryScreen shows stats + timer outcomes.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏆 SCENARIO COMPLETE: Data Breach                                           │
│                                                                               │
│  ┌────────────────────────────────────────┬─────────────────────────────────┐│
│  │  METRICS                               │  STATE MACHINE TRACE            ││
│  │                                        │                                 ││
│  │  Duration: 45 min                      │  NORMAL ─▶ INCIDENT (0:00)      ││
│  │  Final Debt: 52%                       │           ↓                     ││
│  │  Forces Used: 2/3                      │  RESPONSE (15:23)               ││
│  │  Timers Survived: 3/4                  │           ↓                     ││
│  │                                        │  RECOVERY (38:45)               ││
│  │  ┌──────────────────────────────────┐ │           ↓                     ││
│  │  │ GDPR 72h     ✓ Survived (04:23)  │ │  ✓ RESOLVED (45:00)             ││
│  │  │ SLA 4h       ✓ Survived (00:45)  │ │                                 ││
│  │  │ SEC 24h      ✓ Survived (12:00)  │ │  [View Full Trace]              ││
│  │  │ HIPAA 60d    ✗ EXPIRED           │ │                                 ││
│  │  └──────────────────────────────────┘ │                                 ││
│  └────────────────────────────────────────┴─────────────────────────────────┘│
│                                                                               │
│  💡 LEARNINGS                                                                 │
│  • The HIPAA timer expired because you focused on GDPR first                 │
│  • Your consent debt peaked at 72% after the second force                    │
│  • Consider: Earlier transition to RESPONSE reduces cascade risk             │
│                                                                               │
│  [Start New Scenario] [View in Gallery] [Export Report]                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Components**:
- State machine trace visualization
- AI-generated learnings (LLM call with scenario data)
- Export to PDF/JSON for compliance documentation

---

### Journey 14: Observer-Dependent Mesa Rendering

**Scenario**: Different users see Town differently based on their role.

**Current**: All users see same view.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OBSERVER: architect_umwelt                                                  │
│                                                                               │
│  Mesa View:                                                                   │
│  • Citizens shown with relationship graph overlay                            │
│  • Coalition boundaries visible as dotted regions                            │
│  • Phase colors indicate systemic health                                     │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │        ┌─────────────────────────┐                                       │ │
│  │        │  Research Coalition     │ (dotted boundary)                     │ │
│  │   K────┼──────H                  │                                       │ │
│  │        │       \                 │                                       │ │
│  │        │        A                │                                       │ │
│  │        └─────────────────────────┘                                       │ │
│  │                                                                           │ │
│  │   M──────────L (isolated pair)                                           │ │
│  │                                                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  [Switch to: poet | economist | observer]                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Connection**: AGENTESE observer-dependence. `world.town.manifest(architect_umwelt)` returns different projection.

---

### Journey 15: Teaching Mode Toggle

**Scenario**: Power user wants to hide teaching callouts.

**Current**: No teaching callouts exist.

**Redesigned**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SETTINGS                                                                    │
│                                                                               │
│  Teaching Mode: [●] On  [ ] Off                                              │
│                                                                               │
│  When ON:                                                                     │
│  • Polynomial state machines visible in panels                               │
│  • Operad operations shown with arity badges                                 │
│  • Teaching callouts appear with 💡 icon                                     │
│  • Trace panel shows categorical interpretation                              │
│                                                                               │
│  When OFF:                                                                    │
│  • Clean, minimal interface                                                  │
│  • Operations without categorical explanation                                │
│  • Suitable for experienced users                                            │
│                                                                               │
│  💡 Teaching: "The same underlying model powers both views.                  │
│     Teaching mode is a projection functor that adds pedagogical layers."    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**: `useTeachingMode()` hook with localStorage persistence.

---

## Part III: Extracted Primitives

### From Gallery (Already Built)

| Primitive | Purpose | Status |
|-----------|---------|--------|
| `PolynomialPlayground` | Interactive state machine visualization | ✅ Built |
| `OperadWiring` | Composition diagram with drag-and-drop | ✅ Built |
| `TownLive` | Streaming citizen visualization | ✅ Built |
| `PilotCard` | Category-filtered component card | ✅ Built |

### New Primitives to Extract

| Primitive | Purpose | Source |
|-----------|---------|--------|
| `PhaseIndicatorUnified` | Reusable phase badge with glow/animation | Park `PhaseIndicator` |
| `TracePanel` | Timeline with event history and scrubber | New |
| `TeachingCallout` | Gradient background, icon, educational text | Gallery pattern |
| `PresetSelector` | Dropdown with descriptions, keyboard nav | Gallery pattern |
| `StateTransitionVisualization` | Mini state machine for inline use | `PolynomialPlayground` compact |
| `OperationBadge` | Arity + name + signature preview | `OperadWiring` palette items |
| `ConsentDebtMachine` | Debt levels as polynomial phases | Park `ConsentMeter` enhanced |
| `TimerMachine` | Timer as polynomial with phase colors | Park `TimerDisplay` enhanced |
| `MaskCard` | Mask preview with affordances list | Park `MaskSelector` enhanced |
| `FirstVisitOverlay` | Welcome modal with dismiss persistence | New |

### Design System Additions

```typescript
// New design tokens
const PHASE_GLOW = {
  idle: '0 0 12px rgba(100, 116, 139, 0.5)',      // gray
  active: '0 0 12px rgba(34, 197, 94, 0.5)',      // green
  warning: '0 0 12px rgba(245, 158, 11, 0.5)',    // amber
  critical: '0 0 12px rgba(239, 68, 68, 0.5)',    // red
  success: '0 0 12px rgba(34, 197, 94, 0.5)',     // green
};

const TEACHING_GRADIENT = {
  categorical: 'from-blue-500/20 to-purple-500/20',
  operational: 'from-amber-500/20 to-pink-500/20',
  conceptual: 'from-green-500/20 to-blue-500/20',
};

const EDGE_ANIMATION = {
  duration: '300ms',
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
};
```

---

## Part IV: Implementation Phases

### Phase 1: Foundation (Days 1-2)

**Goal**: Extract and unify primitives from Gallery into design system.

1. **Extract Primitives**
   - Create `components/categorical/` directory
   - Move `PolynomialPlayground` and `OperadWiring` to categorical/
   - Create `StateIndicator` (unified phase badge)
   - Create `TeachingCallout` component
   - Create `TracePanel` component

2. **Add Polynomial Presets**
   - `citizen`: Town citizen 5-phase lifecycle
   - `crisis_phase`: Park NORMAL → INCIDENT → RESPONSE → RECOVERY
   - `timer_state`: PENDING → ACTIVE → WARNING → CRITICAL → EXPIRED
   - `consent_debt`: HEALTHY → ELEVATED → HIGH → CRITICAL
   - `director`: OBSERVING → BUILDING → INJECTING → COOLING → INTERVENING

3. **Add Operad Configurations**
   - `TOWN_OPERAD` with all 8 operations
   - `DIRECTOR_OPERAD` with all 8 operations
   - Visual distinction: arity badges, signature tooltips

### Phase 2: Town Enhancement (Days 3-4)

**Goal**: Integrate categorical primitives into Town experience.

1. **CitizenPanel Enhancement**
   - Embed compact `PolynomialPlayground` showing citizen state machine
   - Show valid next inputs based on `citizen_directions(phase)`
   - Add teaching callout explaining Right to Rest

2. **EventFeed Enhancement**
   - Add mini operation visualization for each event
   - Link to full OperadWiring panel
   - Add arity badge to operation names

3. **New Components**
   - `CoalitionPreview` (placeholder for coalition-forge)
   - `TownTracePanel` for N-gent witness
   - Observer selector (architect/poet/economist umwelt)

4. **Mobile Optimization**
   - Full-height Mesa with FloatingActions
   - BottomDrawer for CitizenPanel
   - Compact state indicators in header

### Phase 3: Park Enhancement (Days 5-6)

**Goal**: Integrate categorical primitives into Park experience.

1. **Phase Visualization**
   - Replace PhaseTransition with embedded PolynomialPlayground
   - Show valid transitions based on current phase
   - Add teaching callout for crisis flow

2. **Timer Enhancement**
   - TimerMachine component with phase colors
   - State machine visualization per timer
   - Aggregate timeline view

3. **Consent Debt Enhancement**
   - ConsentDebtMachine showing debt levels as phases
   - Preview of constraint effects at each level
   - Connection to DIRECTOR_OPERAD consent_constraint law

4. **Mask System Enhancement**
   - MaskCard with affordances preview
   - Visual affordance grid
   - Debt cost indicator

5. **Mobile Optimization**
   - Compact layout with FloatingActions
   - BottomDrawer for Masks, Timers, Actions
   - Swipeable cards for timer management

### Phase 4: Teaching Layer (Days 7-8)

**Goal**: Add pedagogical layer across both experiences.

1. **FirstVisitOverlay**
   - Per-jewel welcome message
   - "Show me how it works" → highlight tour
   - Dismiss persistence in localStorage

2. **TeachingMode Hook**
   - Global toggle for teaching callouts
   - Affects: Polynomial visibility, Operad explanations, Trace annotations
   - Persisted in localStorage

3. **Teaching Callouts**
   - Positioned contextually throughout UI
   - Categorized: categorical, operational, conceptual
   - Dismissible individually or globally

4. **Scenario Learnings**
   - AI-generated insights from scenario data
   - State machine trace analysis
   - Recommendations for next scenario

### Phase 5: Polish & Integration (Days 9-10)

**Goal**: Ensure cohesive experience across all touchpoints.

1. **Visual Consistency**
   - Apply JEWEL_COLORS consistently
   - Ensure PHASE_GLOW applied to all phase indicators
   - Verify teaching gradients match category

2. **Performance**
   - Lazy load PolynomialPlayground and OperadWiring
   - Optimize Mesa rendering for mobile
   - SSE connection management

3. **Accessibility**
   - Keyboard navigation for state machines
   - Screen reader labels for phases and operations
   - Reduced motion support for animations

4. **Documentation**
   - Update skills with new component patterns
   - Add storybook stories for all primitives
   - Screenshot gallery of all journeys

---

## Part V: SpecGraph Integration

### Spec Updates Required

```yaml
# spec/town/index.md (update)
---
domain: world
holon: town
polynomial:
  positions: [IDLE, SOCIALIZING, WORKING, REFLECTING, RESTING]
  transition: citizen_transition
  directions: citizen_directions
operad:
  operations:
    greet: {arity: 2, signature: "Citizen x Citizen -> Relationship"}
    gossip: {arity: 2, signature: "Citizen x Citizen -> Information"}
    # ... (8 total)
  laws:
    - identity
    - associativity
    - locality
agentese:
  path: world.town
  aspects:
    - manifest
    - citizen.list
    - citizen.detail
service:
  crown_jewel: true
  frontend: true
  persistence: d-gent
---
```

```yaml
# spec/park/index.md (update)
---
domain: world
holon: park
polynomial:
  positions: [OBSERVING, BUILDING, INJECTING, COOLING, INTERVENING]
  transition: director_transition
  directions: director_directions
operad:
  operations:
    observe: {arity: 1}
    build_tension: {arity: 1}
    inject: {arity: 2}
    cooldown: {arity: 1}
    intervene: {arity: 1}
    director_reset: {arity: 0}
    evaluate: {arity: 2}
    abort: {arity: 0}
  laws:
    - consent_constraint
    - cooldown_constraint
    - tension_flow
    - intervention_isolation
    - observe_identity
    - reset_to_observe
agentese:
  path: world.park
  aspects:
    - manifest
    - scenario.start
    - scenario.tick
    - scenario.complete
    - mask.don
    - mask.doff
service:
  crown_jewel: true
  frontend: true
  persistence: d-gent
---
```

---

## Part VI: Success Criteria

### Quantitative

| Metric | Current | Target |
|--------|---------|--------|
| Teaching callouts per page | 0 | 3-5 |
| Polynomial presets | 3 (Gallery only) | 8 (incl. domain-specific) |
| Mobile-optimized pages | 1 (Town) | 2 (Town + Park) |
| Components in categorical/ | 0 | 10 |
| User journey coverage | 0% | 100% (15/15) |

### Qualitative

- [ ] User understands citizen state machine after 2 minutes
- [ ] User can predict valid operations from current phase
- [ ] Park mobile experience is usable on iPhone SE
- [ ] Teaching mode toggle affects both Town and Park
- [ ] Scenario summary shows meaningful learnings
- [ ] Observer-dependent rendering works for at least 2 umwelts

### The Joy Test

> *"Does using this make me smile?"*

- [ ] First visit overlay delights, doesn't annoy
- [ ] State machine animations feel alive, not mechanical
- [ ] Teaching callouts teach, don't condescend
- [ ] Mobile experience feels native, not cramped
- [ ] Summary screen celebrates success, empathizes with failure

---

## Part VII: Related Plans

- `plans/punchdrunk-park.md` — Park core implementation
- `plans/coalition-forge.md` — Coalition system (Journey 10)
- `plans/design-language-consolidation.md` — DESIGN_OPERAD integration
- `plans/autopoietic-architecture.md` — AD-009 vertical slice pattern
- `plans/gallery-pilots-top3.md` — Source of Gallery primitives

---

## Appendix: Component Architecture

```
components/
├── categorical/                    # NEW: Categorical visualization primitives
│   ├── PolynomialPlayground.tsx   # Moved from projection/gallery/
│   ├── OperadWiring.tsx           # Moved from projection/gallery/
│   ├── StateIndicator.tsx         # Unified phase badge
│   ├── OperationBadge.tsx         # Arity + signature preview
│   ├── TeachingCallout.tsx        # Gradient callout with icon
│   ├── TracePanel.tsx             # Timeline with scrubber
│   ├── FirstVisitOverlay.tsx      # Welcome modal
│   └── presets/
│       ├── citizen.ts             # Town citizen polynomial
│       ├── crisis.ts              # Park crisis polynomial
│       ├── timer.ts               # Timer state polynomial
│       ├── consent.ts             # Consent debt polynomial
│       └── director.ts            # Director polynomial
│
├── town/
│   ├── TownVisualization.tsx      # Updated: imports from categorical/
│   ├── CitizenPanel.tsx           # Enhanced: embedded PolynomialPlayground
│   ├── Mesa.tsx                   # Unchanged
│   └── CoalitionPreview.tsx       # NEW: placeholder for coalition-forge
│
├── park/
│   ├── ParkVisualization.tsx      # Updated: imports from categorical/
│   ├── PhaseVisualization.tsx     # NEW: replaces PhaseTransition
│   ├── TimerMachine.tsx           # Enhanced: state machine visualization
│   ├── ConsentDebtMachine.tsx     # Enhanced: debt levels as phases
│   ├── MaskCard.tsx               # NEW: affordances preview
│   └── ScenarioSummary.tsx        # Enhanced: trace + learnings
│
└── elastic/
    ├── ElasticSplit.tsx           # Unchanged
    ├── BottomDrawer.tsx           # Enhanced: mobile-first
    └── FloatingActions.tsx        # Unchanged
```

---

*"The aesthetic is the structure perceiving itself. Beauty is not added—it is revealed."*

*Compiled: 2025-12-18 | Phases: 5 | Journeys: 15 | Components: 20+*
