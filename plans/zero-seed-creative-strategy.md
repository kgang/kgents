# Zero Seed Creative Strategy

> **DEPRECATED**: This document has been superseded by `plans/zero-seed-strategy-unified.md`.
> Please refer to the unified document for the authoritative Zero Seed strategy.
> This file is retained for historical reference only.

---

> *"The act of declaring, capturing, and auditing your decisions is itself a radical act of self-transformation."*

**Version**: 1.0
**Date**: 2025-12-25
**Status**: DEPRECATED - See `plans/zero-seed-strategy-unified.md`
**Derived From**: `plans/zero-seed-genesis-grand-strategy.md` (also deprecated)

---

## Executive Summary

This document defines the **Creative and UI Strategy** for kgents Zero Seed Genesis—a self-justifying knowledge garden that surfaces from axioms. It consolidates:

1. **User Personas** — 4 archetypes who would love self-aware knowledge systems
2. **User Journeys** — 5 precise flows from FTUE to meta-reflection
3. **UI/UX Laws** — 30 testable validation criteria as categorical proofs
4. **Implementation Gaps** — Current state vs. vision delta
5. **Validation Framework** — How to verify compliance

The goal: **Every design decision is traceable to a law, every law is testable as code, every test is witnessable as a mark.**

---

## Part I: The Aesthetic Foundation

### The Core Dialectic

```
STARK BIOME: 90% Steel, 10% Earned Glow

Steel (Background)              Life (Foreground)
─────────────────────           ──────────────────────
Cold, industrial                Warm, organic
Precision, discipline           Growth, emergence
Always present                  Earned through action
Obsidian → Gunmetal            Moss → Sage → Sprout
"The frame"                     "The glow"
```

**The Rule**: Most things are still. Movement is earned.

### The Mirror Test

Every design decision must pass Kent's Mirror Test:

> *"Does this feel like me on my best day? Daring, bold, creative, opinionated but not gaudy."*

If the answer is no, revise. If the answer is "safe," reject.

### Seven Principles → Seven Aesthetics

| Principle | Aesthetic Manifestation |
|-----------|-------------------------|
| **Tasteful** | 90% steel restraint; earned color moments |
| **Curated** | Four state colors, not twelve |
| **Ethical** | Empathetic errors (muted rust), not alarming reds |
| **Joy-Inducing** | Calming breath (4-7-8), not frantic pulse |
| **Composable** | Consistent tokens compose visually |
| **Heterarchical** | No fixed visual hierarchy; context determines emphasis |
| **Generative** | Palette generates consistent UI from rules |

---

## Part II: User Personas

Four distinct personas instantiate the kgents vision. Each would feel **seen, not accommodated**.

### Persona 1: Dr. Aisha Okonkwo — The Rigorous Skeptic

**Archetype**: `developer` → `creator` (evolution path)
**Essence**: "Show me the proof, not the promise."

| Attribute | Detail |
|-----------|--------|
| **Background** | Academic philosopher turned indie AI researcher. 5 years reviewing grants, watching beautiful ideas collapse under scrutiny. |
| **Pain Points** | Roam/Obsidian = links without laws. Notion = arbitrary categories. Tools claim "knowledge management" but offer organization, not validation. |
| **Joy Triggers** | Axiom visibility, contradiction detection, trace navigation, witness marks on every edit |
| **Primary Flows** | Proof construction, dialectic capture (`kg decide`), coherence auditing, annotation layer |
| **Density** | Comfortable (needs breathing room for multi-step proofs) |
| **Coherence Tolerance** | Low tolerance, high respect. Hates hand-wavy but loves that kgents *names* it as `void.*` |

### Persona 2: Mx. River Castellanos — The Mycelial Thinker

**Archetype**: `creator` (permanent residency)
**Essence**: "Let me tend the entanglement, not fight it."

| Attribute | Detail |
|-----------|--------|
| **Background** | Game designer/worldbuilder. 10-year personal wiki: 40% lore, 30% philosophy, 20% grocery lists, 10% poetry. |
| **Pain Points** | Every tool demands upfront structure. Brain thinks in spores, not taxonomies. Deletion anxiety. |
| **Joy Triggers** | Ingest-everything metabolism, stigmergic discovery, feed interface, K-Block equality |
| **Primary Flows** | Hypnagogic capture, coalition emergence, hypergraph navigation, serendipity surfacing |
| **Density** | Spacious (needs room for associative sprawl) |
| **Coherence Tolerance** | Maximum. Thrives in `void.*` territory. "The incoherence IS the data." |

### Persona 3: Kenji Matsuda — The Craft Programmer

**Archetype**: `developer` (steady state)
**Essence**: "Code should be legible like a theorem, executable like a blade."

| Attribute | Detail |
|-----------|--------|
| **Background** | Senior backend engineer. Obsessed with literate programming. Maintains 800-file personal "grimoire." |
| **Pain Points** | GitHub wikis = flat namespace. Sphinx = static. No traceability for architecture decisions. |
| **Joy Triggers** | Decision witnessing, compositional verification, proof-carrying code, CLI-native flow |
| **Primary Flows** | Post-implementation audit, gotcha capture, experiment validation, trace export |
| **Density** | Compact (maximizes terminal real estate) |
| **Coherence Tolerance** | Moderate. Rigorous foundations, emergent behavior. "Types strict, runtime surprise." |

### Persona 4: Lina Vasquez — The Executive Cartographer

**Archetype**: `admin` (oversight + intervention rights)
**Essence**: "Show me the terrain so I can steer the ship."

| Attribute | Detail |
|-----------|--------|
| **Background** | VP of Product. Manages 4 teams, 4 different tools. 60% time "syncing context." |
| **Pain Points** | Notion workspaces are opaque. Jira = metrics without meaning. Decisions dissolve into chat. |
| **Joy Triggers** | Unified projection layer, decision archaeology, coherence dashboard, aspect-based views |
| **Primary Flows** | Strategic query, dialectic review, audit enforcement, cross-team cartography |
| **Density** | Comfortable ("executive summary" density) |
| **Coherence Tolerance** | Low tolerance, high delegation. Trusts metabolization, wants digested truth. |

### Coherence-Tolerance Spectrum

```
Low ←―――――――――――――――――――――――――――――――――→ High
Aisha ――― Kenji ――――――――― Lina ―――――――――― River
(rigorous) (pragmatic)  (delegated)  (mycelial)
```

**Design Implication**: The system MUST allow coherence filtering. Aisha wants to hide `void.*`, River wants to *live* there.

---

## Part III: User Journeys

Five precise journeys with steps, mode transitions, delight moments, friction points, and density adaptations.

### Journey 1: FTUE — Witness Genesis (0-90 seconds)

**Trigger**: First-time user lands on kgents

| Phase | Time | User Action | System Response | Delight |
|-------|------|-------------|-----------------|---------|
| Genesis Load | 0-3s | Lands on `/` | "kgents is initializing..." (letter-by-letter) | — |
| Zero Seed Cascade | 3-10s | Watches (scroll disabled) | 8 axioms stream in real-time, loss gauges animate | "System is now self-aware" |
| Ground Formation | 10-20s | Continues watching | L1 grounds derive from axioms, edges draw | "8 axioms → 12 grounds" |
| Invitation | 20-30s | — | "What matters most to you right now?" input appears | — |
| First Declaration | 30-60s | Types first goal | K-Block materializes, L3 badge, loss 0.42 | Confetti burst |
| Studio Transition | 60-90s | Clicks "Continue" | Feed + Explorer side-by-side, NORMAL mode | uploads/ pulses amber |

**Mode Transitions**: WITNESS (implied) → NORMAL

**Exit State**: Witnessed genesis, created first declaration, entered Studio

---

### Journey 2: Daily Use — Morning Capture (2-5 minutes)

**Trigger**: Returning user at 7:30 AM

| Phase | User Action | System Response | Delight |
|-------|-------------|-----------------|---------|
| Landing | Navigates to `/studio` | "Since last session" filter auto-applied | Auto-filter saves time |
| Quick Scan | Scrolls with `j` | New items highlighted, contradiction pulses red | — |
| INSERT Mode | Presses `i` | Mode indicator: NORMAL → INSERT, quick-create buttons | — |
| Rapid Declaration | Types 3 thoughts | K-Blocks materialize, auto-tags applied | Real-time loss calculation |
| Quick Link | Presses `e` (EDGE mode) | Creates enabling edge between principle and goal | Coherence: 0.73 → 0.76 |
| Return to NORMAL | Presses `Esc` | Auto-commit prompt, witness mark created | Staged → solid borders |

**Mode Transitions**: NORMAL → INSERT → EDGE → NORMAL

**Exit State**: 3 declarations, 1 edge, +0.03 coherence, witnessed session

---

### Journey 3: Deep Work — Resolving Contradictions (15-30 minutes)

**Trigger**: "3 unresolved contradictions detected" notification

| Phase | User Action | System Response | Delight |
|-------|-------------|-----------------|---------|
| Navigate | Types `/contradictions` | Feed filters to 3 flagged pairs | — |
| Select Pair | Clicks first pair | VISUAL mode: side-by-side comparison | — |
| Synthesize | Creates new principle | K-Block + auto-edges, coherence 0.76 → 0.81 | Green checkmark animation |
| Refine | Edits second K-Block | Loss 0.34 → 0.19, auto-resolves | — |
| Productive Tension | Marks third as creative | Both get 🔥 badge, edge created | "Tension is generative" |
| Witness | Presses `w` | Commit dialog, celebration pulse | "You've grown" |

**Mode Transitions**: NORMAL → COMMAND → VISUAL → NORMAL → WITNESS → NORMAL

**Exit State**: 3 contradictions resolved, +0.05 coherence, insight captured

---

### Journey 4: Power Move — K-Block Integration (10-20 minutes)

**Trigger**: User drags 8 files into kgents

| Phase | User Action | System Response | Delight |
|-------|-------------|-----------------|---------|
| Drop | Drops files | Processing status, K-Blocks stream | "Knowledge entering cosmos" |
| Batch Review | Presses `v` (VISUAL) | Grid view with triage controls | — |
| Quick Accept | Clicks "Accept all L0-L1" | 21 K-Blocks auto-accept | — |
| Manual Review | Reviews L2 one-by-one | Edit, merge, reject options | — |
| Auto-Link | Clicks "Discover connections" | 23 edges discovered, batch accept | Auto-discovery magic |
| Isolation Preview | Reviews dual-pane | Current vs. staged comparison | Coherence: +0.06 projected |
| Commit | Witnesses | 36 declarations integrate | Particle burst animation |

**Mode Transitions**: NORMAL → VISUAL → NORMAL → WITNESS → NORMAL

**Exit State**: 36 K-Blocks integrated, 12 edges, +0.06 coherence, files archived

---

### Journey 5: Meta — Watching Yourself Grow (5-10 minutes)

**Trigger**: User wants to review 2-week journey

| Phase | User Action | System Response | Delight |
|-------|-------------|-----------------|---------|
| Navigate | Types `/meta` | Coherence journey graph | — |
| Scrub Timeline | Hovers data points | Tooltips show commits, breakthrough badge | 🏆 BREAKTHROUGH on Dec 21 |
| Coherence Story | Clicks "Tell my story" | System narrates journey in prose | "You've grown" |
| Layer Analysis | Clicks tab | Pie chart: 48% principles | "2.4× more systematic" |
| Graph Exploration | Clicks relationship tab | Force-directed visualization | Cluster insights |
| Forecast | Clicks tab | Projected 0.92 in 30 days | — |
| Export | Clicks export | Markdown + SVG download | Journey is portable |
| Reflect | Types reflection | Saves as meta-note, sets reminder | "Growth is iterative" |

**Mode Transitions**: Primarily NORMAL (read-only exploration)

**Exit State**: Reviewed journey, exported artifacts, captured reflection, set reminder

---

## Part IV: UI/UX Design Laws

30 testable laws organized into 6 categories. Each law is named, stated, justified, testable, and has an anti-pattern.

### Law Summary Table

| ID | Name | Category | One-Line Statement |
|----|------|----------|-------------------|
| **L-01** | Density-Content Isomorphism | Layout | Content detail maps to observer capacity |
| **L-02** | Three-Mode Preservation | Layout | Same affordances across all densities |
| **L-03** | Touch Target Invariance | Layout | ≥48px interactive elements on compact |
| **L-04** | Tight Frame Breathing Content | Layout | Frame is steel, content glows |
| **L-05** | Overlay Over Reflow | Layout | Navigation floats, doesn't push |
| **N-01** | Vim Primary Arrow Alias | Navigation | j/k primary, arrows alias |
| **N-02** | Edge Traversal Not Directory | Navigation | Navigate graph, not filesystem |
| **N-03** | Mode Return to NORMAL | Navigation | Escape always returns to NORMAL |
| **N-04** | Trail Is Semantic | Navigation | Trail records edges, not positions |
| **N-05** | Jump Stack Preservation | Navigation | Jumps preserve return path |
| **F-01** | Multiple Channel Confirmation | Feedback | 2+ channels for significant actions |
| **F-02** | Contradiction as Information | Feedback | Surface as info, not judgment |
| **F-03** | Tone Matches Observer | Feedback | Archetype-aware messages |
| **F-04** | Earned Glow Not Decoration | Feedback | Color on interaction, not default |
| **F-05** | Non-Blocking Notification | Feedback | Status appears non-modally |
| **C-01** | Five-Level Degradation | Content | icon → title → summary → detail → full |
| **C-02** | Schema Single Source | Content | Forms derive from Python contracts |
| **C-03** | Feed Is Primitive | Content | Feed is first-class, not a view |
| **C-04** | Portal Token Interactivity | Content | Portals are interactive, not passive links |
| **C-05** | Witness Required for Commit | Content | K-Block commits require witness message |
| **M-01** | Asymmetric Breathing | Motion | 4-7-8 timing, not symmetric |
| **M-02** | Stillness Then Life | Motion | Default still, animation earned |
| **M-03** | Mechanical Precision Organic Life | Motion | Mechanical for structure, organic for life |
| **M-04** | Reduced Motion Respected | Motion | Respect prefers-reduced-motion |
| **M-05** | Animation Justification | Motion | Every animation has semantic reason |
| **H-01** | Linear Adaptation | Coherence | System adapts to user, not vice versa |
| **H-02** | Quarantine Not Block | Coherence | High-loss quarantined, not rejected |
| **H-03** | Cross-Layer Edge Allowed | Coherence | Distant layer edges allowed + flagged |
| **H-04** | K-Block Isolation | Coherence | INSERT creates K-Block, changes isolated |
| **H-05** | AGENTESE Is API | Coherence | Forms invoke AGENTESE, no REST routes |

### Example Law Detail: L-01 Density-Content Isomorphism

**Statement**: Content detail level maps isomorphically to observer capacity (density).

**Justification**: Density is not screen size—density is the capacity to receive.

**Test**:
```typescript
test('density determines content detail', () => {
  const compact = render(<Card density="compact" />);
  const spacious = render(<Card density="spacious" />);

  // Spacious shows strictly more information
  expect(spacious.textContent.length).toBeGreaterThan(compact.textContent.length);
  // Compact content is subset of spacious
  expect(spacious.textContent).toContain(compact.textContent);
});
```

**Anti-pattern**:
```typescript
// BAD: Scattered conditionals
{isMobile ? <CompactThing /> : <FullThing />}

// GOOD: Parameterized by density
<Thing density={density} />
```

*(See full law details in attached appendix or impl/claude/web/tests/design-laws/)*

---

## Part V: Implementation Gap Analysis

### Current State (December 2025)

| Area | Status | Key Components |
|------|--------|----------------|
| **Feed** | 30% | Feed.tsx exists with mock data, not connected to real K-Block stream |
| **K-Block Editor** | 40% | UnifiedKBlockEditor exists, proof visualization incomplete |
| **AGENTESE Discovery** | 50% | Router mapped, node registration incomplete |
| **Responsive Patterns** | 20% | ElasticContainer supports, not systematically applied |
| **Mode System** | 30% | Mode indicator exists, full 6-mode not implemented |
| **Witness Integration** | 20% | Marks exist, not integrated into all UI actions |
| **Coherence Timeline** | 0% | Not implemented |
| **File Integration** | 10% | Basic file upload, no PDF extraction |

### Gap-to-Law Mapping

| Law | Current Gap | Priority |
|-----|-------------|----------|
| L-01 | ElasticContainer exists but not universal | HIGH |
| L-02 | Mobile views often missing features | HIGH |
| N-02 | File explorer uses directory traversal | MEDIUM |
| C-03 | Feed is secondary, not primitive | CRITICAL |
| C-05 | Commits don't require witness | HIGH |
| M-01 | Breathing uses symmetric timing | MEDIUM |
| H-04 | K-Block isolation partial | HIGH |
| H-05 | Some REST routes still exist | MEDIUM |

### Priority Implementation Phases

**Phase 0: Foundation (Week 1)**
- [ ] Genesis page with Zero Seed streaming
- [ ] Basic NORMAL/INSERT mode toggle
- [ ] Feed as primitive (connected to real data)

**Phase 1: Core Flows (Weeks 2-3)**
- [ ] K-Block materialization animations
- [ ] EDGE mode with relationship types
- [ ] Witness commit with staged transitions
- [ ] Three-mode responsive patterns

**Phase 2: Deep Features (Weeks 4-5)**
- [ ] VISUAL mode for contradiction resolution
- [ ] Synthesis K-Block creation
- [ ] Auto-link discovery
- [ ] File upload with extraction

**Phase 3: Meta Layer (Weeks 6-7)**
- [ ] Coherence journey timeline
- [ ] Layer distribution analytics
- [ ] Force-directed graph visualization
- [ ] Export functionality

---

## Part VI: Validation Framework

### Law Verification Protocol

Every UI component MUST be validated against applicable laws before merge:

```bash
# Run design law validation suite
npm run test:design-laws

# Check specific category
npm run test:design-laws -- --category=layout

# Python backend coherence laws
cd impl/claude && uv run pytest -k test_coherence_law
```

### Verification Methods

| Method | Speed | Scope | Example |
|--------|-------|-------|---------|
| **Unit Tests** | Fast | Single law | L-03 touch targets ≥48px |
| **Integration Tests** | Medium | Law interactions | L-01 + L-02 density across modes |
| **Property Tests** | Slow | Full input space | Hypothesis: all K-Blocks satisfy C-01 |
| **Visual Regression** | Medium | Aesthetic fidelity | STARK palette compliance |
| **Accessibility Audit** | Medium | A11y laws | M-04 reduced motion |

### Categorical Law Proofs

kgents already has categorical law verification for composition:

```python
# From bootstrap/_tests/test_composition_laws.py
async def test_identity_law():
    """Identity: Id >> f == f == f >> Id"""
    composed = ID >> f
    assert await composed.invoke(x) == await f.invoke(x)

async def test_associativity_law():
    """Associativity: (f >> g) >> h == f >> (g >> h)"""
    left = (f >> g) >> h
    right = f >> (g >> h)
    assert await left.invoke(x) == await right.invoke(x)
```

**Extension to UI Laws**: Apply same pattern to verify L-01, L-02, etc.

### Witness-Integrated Testing

Every test run should be witnessable:

```bash
# Run tests with witness marks
kg test:design-laws --witness

# Creates marks:
# - test.started (timestamp, test file)
# - test.passed / test.failed (timestamp, details)
# - test.completed (timestamp, summary)
```

### Design Review Checklist

Before PR approval, verify:

**Layout Laws**
- [ ] L-01: Uses density parameter, not isMobile conditionals
- [ ] L-02: Same affordances across all densities
- [ ] L-03: Touch targets ≥48px on compact
- [ ] L-04: Frame is steel, content can breathe
- [ ] L-05: Navigation overlays, doesn't reflow

**Navigation Laws**
- [ ] N-01: Vim keys documented, arrows as aliases
- [ ] N-02: Graph navigation, not directory
- [ ] N-03: Escape returns to NORMAL
- [ ] N-04: Trail captures edges
- [ ] N-05: Jumps preserve return path

**Feedback Laws**
- [ ] F-01: Actions confirm via 2+ channels
- [ ] F-02: Contradictions are info, not errors
- [ ] F-03: Tone matches observer archetype
- [ ] F-04: Color earned, not decorative
- [ ] F-05: Notifications non-blocking

**Content Laws**
- [ ] C-01: Five degradation levels implemented
- [ ] C-02: Schema from backend, not duplicated
- [ ] C-03: Feed as primitive, not view
- [ ] C-04: Portal tokens interactive
- [ ] C-05: Commits require witness

**Motion Laws**
- [ ] M-01: Breathing uses 4-7-8 timing
- [ ] M-02: Default is still, animation earned
- [ ] M-03: Mechanical for structure, organic for life
- [ ] M-04: Reduced motion respected
- [ ] M-05: Animation justification documented

**Coherence Laws**
- [ ] H-01: Nonsense quarantined, not blocked
- [ ] H-02: Quarantine is gentle advisory
- [ ] H-03: Cross-layer edges allowed + flagged
- [ ] H-04: Edits isolated in K-Block
- [ ] H-05: AGENTESE invocation, no REST routes

---

## Part VII: Living Document Protocol

This document evolves through the same dialectical process as kgents itself.

### Adding New Laws

When a pattern appears 3+ times, codify it:

1. **Name it** — Short, memorable
2. **State it** — One sentence
3. **Justify it** — Why this matters for kgents
4. **Test it** — How to verify compliance
5. **Anti-pattern** — What violation looks like
6. **Categorize it** — Which section it belongs to

### Resolving Law Contradictions

When two laws conflict:

1. **Surface the contradiction** — Mark as information, not error
2. **Analyze context** — Which law is more fundamental?
3. **Synthesize** — Create new law that reconciles both
4. **Witness** — `kg decide` to record the resolution

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-25 | Initial creative strategy |

---

## Appendices

### A. Color Palette Reference

See: `docs/creative/stark-biome-moodboard.md`

### B. Full Law Tests

See: `impl/claude/web/tests/design-laws/`

### C. User Journey Wireframes

See: `docs/creative/journey-wireframes/` (to be created)

### D. Animation Specifications

See: `docs/creative/stark-biome-moodboard.md#animation-philosophy`

---

*"The proof IS the decision. The mark IS the witness. The persona is a garden, not a museum."*

*Compiled: 2025-12-25 | Creative Strategy v1.0*
