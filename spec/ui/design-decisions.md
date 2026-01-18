# Kent's 15 Design Decisions

> *Interview conducted: 2026-01-17*

**Status:** Canonical
**Grounded In:** spec/ui/axioms.md, spec/ui/severe-stark.md

---

## The Kent Doctrine

These 15 decisions are **immutable** — they define the character of the kgents interface.

1. **No hand-holding** — External docs, no onboarding, everyone is architect
2. **Full power always** — Ship everything, all 6 jewels, no feature gates
3. **Earned rewards** — Glow only on milestones, slow motion is earned
4. **Graph over tree** — K-Blocks reference, don't contain
5. **Formal rigor** — CSS constraint system, WCAG AA strict, event-sourced persistence
6. **Touch adaptation** — Mobile gets touch-friendly targets (the one concession)

---

## Quick Reference

| # | Category | Decision |
|---|----------|----------|
| 1 | Mobile | **Adapt for touch** — 44px min targets |
| 2 | Glow | **Milestones only** — commit, crystal, resolve |
| 3 | Motion | **Slow earned, fast default** |
| 4 | Nav | **Bottom tab bar** (iOS-style) |
| 5 | Onboarding | **External docs only** |
| 6 | Keys | **Single-letter** — m/w/t/f/d/s |
| 7 | K-Block | **Reference, not contain** (graph) |
| 8 | Entangle | **Spec dependencies** |
| 9 | Persist | **Event sourced** (HEAD-FIRST) |
| 10 | Users | **Everyone is architect** |
| 11 | Jewels | **Ship all 6** |
| 12 | ASHC | **Gutter annotations** |
| 13 | Query | **Fuzzy search only** (fzf-style) |
| 14 | Layout | **CSS constraint system** |
| 15 | A11y | **Strict WCAG AA** (4.5:1) |

---

## Aesthetic & Density

### Decision #1: Mobile Density

**Decision:** Adapt for touch — 44px minimum touch targets, slightly larger text on mobile.

**Implementation:**
```css
--touch-min: 44px;         /* WCAG AA minimum */
--touch-comfortable: 48px; /* Mobile default */
```

### Decision #2: Earned Glow Philosophy

**Decision:** Milestone celebrations only:
- K-Block commit
- Crystal creation
- Contradiction resolved

**Implementation:** `src/styles/layout-constraints.css` → `.milestone-glow`

### Decision #3: Motion Budget

**Decision:** Slow is earned, fast is default
- Glow fade: 2s ease-out (earned)
- Everything else: instant (no animation)

**Implementation:** `src/styles/severe-base.css` kills all transitions by default.

---

## Navigation & Interaction

### Decision #4: Compact Navigation

**Decision:** Bottom tab bar — iOS-style fixed navigation, always visible on mobile.

**Implementation:**
```css
.bottom-tabs {
  display: flex;
  height: 48px;
  padding-bottom: env(safe-area-inset-bottom);
}
```

### Decision #5: Onboarding Without Joy

**Decision:** External docs only — No in-app onboarding.

**Implementation:** None needed. Power users read docs.

### Decision #6: Aspect Keyboard Shortcuts

**Decision:** Single-letter shortcuts:
- `m` = manifest
- `w` = witness
- `t` = tithe
- `f` = refine
- `d` = define
- `s` = sip

**Implementation:** Pending — wire to AGENTESE aspects.

---

## K-Block Architecture

### Decision #7: K-Block Nesting

**Decision:** Reference, not contain — K-Blocks link to each other but don't nest. Graph, not tree.

**Rationale:** Trees imply hierarchy. Graphs enable emergence.

### Decision #8: Entanglement

**Decision:** Spec dependencies — If K-Block A references K-Block B, they're entangled automatically.

**Rationale:** Entanglement should be discovered, not declared.

### Decision #9: Persistence Model

**Decision:** Event sourced with HEAD-FIRST design:
- Current state in `KBlockHead` (O(1) access)
- Events store reverse deltas
- History reconstructed by rewinding from head

**Implementation:** `services/k_block/core/events.py`

---

## System & Priority

### Decision #10: Observer Archetypes

**Decision:** Everyone is architect — No tiered access. Full power for everyone.

### Decision #11: Crown Jewel Priority

**Decision:** Ship all 6 Crown Jewels:
1. Brain (memory crystallization)
2. Witness (decision tracing)
3. Muse (creative prompting)
4. Soul (LLM dialogue)
5. Zero Seed (Galois loss)
6. Constitutional (7-principle scoring)

### Decision #12: ASHC Evidence Display

**Decision:** Gutter annotations — Icons in editor gutter, click to expand inline.

**Implementation:** Pending — editor gutter integration.

---

## Technical

### Decision #13: Query/Discovery Depth

**Decision:** Fuzzy search only — No wildcard browsing. Type to filter. Fzf-style.

### Decision #14: Sheaf Layout Proof

**Decision:** CSS constraint system — Define layout formally, verify constraints hold.

**Implementation:** `src/styles/layout-constraints.css`

**Invariants:**
- Workspace grid: 10% | 15% | 1fr | 25%
- `contain: layout size` enforces isolation
- Touch targets: 44px minimum
- Text: never below 14px readable

### Decision #15: Accessibility Strictness

**Decision:** Strict WCAG AA — 4.5:1 minimum contrast everywhere.

**Implementation:** `src/design/tokens.css`
- `--text-muted`: #5a5a64 → #7a7a84 (5.2:1 contrast)

---

## Resolved Tensions

| Tension | Resolution |
|---------|------------|
| Joy vs Stark | Joy = milestone glow only |
| Curated vs Ship Everything | Curated through severity, not scope |
| Composability vs Consolidation | K-Blocks compose via reference (graph) |
| Accessibility vs Aesthetic | Strict WCAG AA. Aesthetic serves accessibility |

---

## Kent's Voice Check

Before any implementation, verify:

- [ ] *"Daring, bold, creative, opinionated but not gaudy"*
- [ ] *"simplistic, brutalistic?, dense, intelligent design"*
- [ ] *"Tasteful > feature-complete"*
- [ ] *"The Mirror Test"* — Does this feel like Kent on his best day?

---

*The proof IS the decision. The mark IS the witness.*
