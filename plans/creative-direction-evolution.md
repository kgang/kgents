---
path: plans/creative-direction-evolution
status: active
progress: 0.15
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps-synthesis
  - plans/web-refactor/elastic-primitives
session_notes: |
  Session 1 (2025-12-16): Foundation complete
  - Created docs/creative/ directory with 7 documents
  - Established philosophy, visual system, motion, voice, mood board, implementation guide
  - Mapped 7 core principles to aesthetic expressions
  - Built on existing joy components (Breathe, Pop, Shake, Shimmer)
  - Referenced external research for validation
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: in_progress  # 15% - foundation docs done
  STRATEGIZE: deferred
  CROSS-SYNERGIZE: deferred
  IMPLEMENT: deferred
  QA: deferred
  TEST: deferred
  EDUCATE: deferred
  MEASURE: deferred
  REFLECT: deferred
entropy:
  planned: 0.08
  spent: 0.05
  returned: 0.03
---

# Plan: Creative Direction Evolution

> *"The aesthetic is the projection of principles into perception."*

## Vision

Evolve kgents from a functionally complete system into a **cohesive aesthetic experience** that embodies its core principles. The creative direction translates abstract philosophy into tangible, sensory interactions.

## Current State (After Session 1)

### Completed Foundation

| Document | Status | Purpose |
|----------|--------|---------|
| `docs/creative/README.md` | ✅ | Index + Creative thesis |
| `docs/creative/philosophy.md` | ✅ | Principles → Aesthetics mapping |
| `docs/creative/visual-system.md` | ✅ | Colors, typography, spacing, layout |
| `docs/creative/motion-language.md` | ✅ | Animation primitives, timing, semantics |
| `docs/creative/voice-and-tone.md` | ✅ | Error messages, loading states, copy |
| `docs/creative/mood-board.md` | ✅ | Visual + conceptual inspiration |
| `docs/creative/implementation-guide.md` | ✅ | Developer practical reference |

### Key Insights Established

1. **The Garden Metaphor** — kgents is cultivation, not construction
2. **Crystalline Warmth** — Precise yet human
3. **Density as Projection** — Three breakpoints, not arbitrary responsiveness
4. **Jewel Personalities** — Each Crown Jewel has distinct visual/motion/voice character
5. **Joy Components** — `Breathe`, `Pop`, `Shake`, `Shimmer` as primitives

---

## Session Plan

### Session 2: Visual System Implementation

**Focus:** Apply visual-system.md to existing components

**Deliverables:**
- [ ] Tailwind config extended with kgents tokens
- [ ] JEWEL_COLORS constant file
- [ ] Color audit of existing components (identify violations)
- [ ] Typography audit (standardize to scale)
- [ ] Spacing audit (remove arbitrary values)

**Entry point:** `impl/claude/web/tailwind.config.js`

---

### Session 3: Motion System Audit

**Focus:** Apply motion-language.md to existing interactions

**Deliverables:**
- [ ] Motion constants file (TIMING, EASING)
- [ ] Audit all `framer-motion` usages
- [ ] Add `useMotionPreferences` to all animated components
- [ ] Standardize transition durations
- [ ] Document motion patterns in Storybook

**Entry point:** `impl/claude/web/src/components/joy/`

---

### Session 4: Voice & Tone Audit

**Focus:** Apply voice-and-tone.md to all copy

**Deliverables:**
- [ ] Error message inventory
- [ ] Loading state inventory
- [ ] Empty state inventory
- [ ] Standardize to empathetic patterns
- [ ] Add PersonalityLoading to all jewels

**Entry point:** Search for "Error", "Loading", "No " in codebase

---

### Session 5: Component Consistency Pass

**Focus:** Ensure all components follow implementation guide

**Deliverables:**
- [ ] Card components standardized
- [ ] Button variants documented
- [ ] Form field patterns consistent
- [ ] Panel/drawer patterns consistent
- [ ] All components have Storybook stories

**Entry point:** `impl/claude/web/src/components/`

---

### Session 6: 3D Visual Consistency

**Focus:** Apply 3D lighting patterns to all WebGL scenes

**Deliverables:**
- [ ] SceneLighting used in all 3D components
- [ ] Illumination quality detection working
- [ ] Shadow optimization verified
- [ ] Performance metrics documented

**Entry point:** `impl/claude/web/src/components/three/`

---

### Session 7: Design Token Extraction

**Focus:** Create single source of truth for all tokens

**Deliverables:**
- [ ] `design-tokens.ts` with all values
- [ ] CSS custom properties generated
- [ ] Tailwind config consumes tokens
- [ ] Documentation updated

**Entry point:** New file `impl/claude/web/src/design-tokens.ts`

---

### Session 8: Storybook Documentation

**Focus:** Complete visual documentation

**Deliverables:**
- [ ] All primitives documented
- [ ] All joy components documented
- [ ] Design token showcase
- [ ] Density showcase
- [ ] Motion showcase

**Entry point:** `impl/claude/web/.storybook/`

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Color violations | 0 (all from palette) |
| Typography violations | 0 (all from scale) |
| Spacing violations | 0 (all from scale) |
| Motion preference coverage | 100% of animated components |
| Error empathy coverage | 100% of error states |
| Loading personality coverage | All 7 jewels |
| Storybook coverage | All public components |

---

## Dependencies

**Blocks:**
- `core-apps-synthesis` (needs consistent aesthetic)
- `elastic-primitives` (needs density tokens)

**Blocked by:**
- None (foundation is self-contained)

---

## Notes

### On Balance

The creative direction intentionally balances:
- **Rigor** and **playfulness**
- **Restraint** and **personality**
- **Consistency** and **context-sensitivity**

The danger is over-systematizing. Leave room for the Accursed Share—not everything must be perfectly tokenized.

### On Evolution

This is a **living system**. The mood board will grow. The tokens may need refinement. The important thing is that decisions trace to meaning.

---

*"The garden grows. The crystal forms. The river flows."*
