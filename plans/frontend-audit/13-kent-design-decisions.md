# Kent's 15 Design Decisions

> *Interview conducted: 2026-01-17*
> *Status: CANONICAL — These decisions govern all frontend implementation*

---

## Summary

Through a systematic interview covering 15 blocking design questions, Kent made definitive decisions that unblock frontend execution. These decisions are **immutable** — they define the character of the kgents interface.

### The Kent Doctrine (Synthesized)

1. **No hand-holding** — External docs, no onboarding, everyone is architect
2. **Full power always** — Ship everything, all 6 jewels, no feature gates
3. **Earned rewards** — Glow only on milestones, slow motion is earned
4. **Graph over tree** — K-Blocks reference, don't contain
5. **Formal rigor** — CSS constraint system, WCAG AA strict, event-sourced persistence
6. **Touch adaptation** — Mobile gets touch-friendly targets (the one concession)

---

## Aesthetic & Density

### Decision #1: Mobile Density
**Question:** Should mobile maintain the same density or adapt for touch?
**Decision:** **Adapt for touch** — 44px minimum touch targets, slightly larger text on mobile.

*Rationale:* Touch precision differs from mouse. The interface should serve the user's physical context.

### Decision #2: Earned Glow Philosophy
**Question:** What warrants "earned glow"?
**Decision:** **Milestone celebrations only**:
- K-Block commit
- Crystal creation
- Contradiction resolved

*Rationale:* Glow is precious. If everything glows, nothing does.

### Decision #3: Motion Budget
**Question:** What's the motion budget?
**Decision:** **Slow is earned, fast is default**
- Glow and mode switch: Can be slow (2s)
- Everything else: Instant (no animation)

*Rationale:* Motion is decoration. Decoration must justify itself.

---

## Navigation & Interaction

### Decision #4: Compact Navigation
**Question:** How to navigate in compact mode?
**Decision:** **Bottom tab bar** — iOS-style fixed navigation, always visible on mobile.

*Rationale:* Thumb-reachable, familiar pattern, doesn't waste vertical space.

### Decision #5: Onboarding Without Joy
**Question:** How to onboard without joy components?
**Decision:** **External docs only** — No in-app onboarding. Read the manual. Power users only.

*Rationale:* The interface is for people who want to understand, not people who want to be guided.

### Decision #6: Aspect Keyboard Shortcuts
**Question:** Should keyboard shortcuts map to aspects?
**Decision:** **Yes, single-letter shortcuts**:
- `m` = manifest
- `w` = witness
- `t` = tithe
- `f` = refine
- `d` = define
- `s` = sip

*Rationale:* Power users deserve power tools. Single-letter = instant access.

---

## K-Block Architecture

### Decision #7: K-Block Nesting
**Question:** Can K-Blocks contain other K-Blocks?
**Decision:** **Reference, not contain** — K-Blocks link to each other but don't nest. Graph, not tree.

*Rationale:* Trees imply hierarchy. Graphs enable emergence.

### Decision #8: Entanglement
**Question:** How is entanglement represented?
**Decision:** **Spec dependencies** — If K-Block A references K-Block B, they're entangled automatically.

*Rationale:* Entanglement should be discovered, not declared. The spec is the source of truth.

### Decision #9: Persistence Model
**Question:** How are K-Blocks persisted?
**Decision:** **Event sourced** — Every edit is an event. Full history, replayable.

**Implementation Note (HEAD-FIRST Design):**
- Current state stored in `KBlockHead` for O(1) access
- Events store reverse deltas
- History reconstructed by rewinding from head
- See: `services/k_block/core/events.py`

*Rationale:* History is knowledge. Event sourcing preserves all knowledge.

---

## System & Priority

### Decision #10: Observer Archetypes
**Question:** Should the UI adapt to different user types?
**Decision:** **Everyone is architect** — No tiered access. Full power for everyone.

*Rationale:* If you're using kgents, you're an architect. No patronizing simplification.

### Decision #11: Crown Jewel Priority
**Question:** Which Crown Jewels to ship first?
**Decision:** **Ship everything** — All 6 Crown Jewels:
1. Brain (memory crystallization)
2. Witness (decision tracing)
3. Muse (creative prompting)
4. Soul (LLM dialogue)
5. Zero Seed (Galois loss)
6. Constitutional (7-principle scoring)

*Rationale:* The jewels are the system. Partial shipping is partial thinking.

### Decision #12: ASHC Evidence Display
**Question:** How to show ASHC (Arguments, Sound, Hypothesis, Claims) evidence?
**Decision:** **Gutter annotations** — Icons in editor gutter, click to expand inline.

*Rationale:* Evidence should be adjacent to claims. Gutter is the liminal space between code and context.

---

## Technical

### Decision #13: Query/Discovery Depth
**Question:** How deep should AGENTESE discovery go?
**Decision:** **Fuzzy search only** — No wildcard browsing. Type to filter. Fzf-style.

*Rationale:* If you don't know what you're looking for, search won't help. Fuzzy is powerful and minimal.

### Decision #14: Sheaf Layout Proof
**Question:** How to verify layout stability (sheaf gluing)?
**Decision:** **CSS constraint system** — Define layout formally, verify constraints hold.

**Implementation:**
- Created `src/styles/layout-constraints.css`
- Fixed slot proportions (10% | 15% | 1fr | 25%)
- `contain: layout size` enforces isolation
- Debug classes for verification

*Rationale:* Layout is a specification. Specifications should be verifiable.

### Decision #15: Accessibility Strictness
**Question:** How strict on accessibility?
**Decision:** **Strict WCAG AA** — Fix all contrast issues. 4.5:1 minimum everywhere.

**Implementation:**
- Fixed `--text-muted` in tokens.css (#5a5a64 → #7a7a84)
- All text colors now ≥4.5:1 contrast on `--bg-void: #0a0a0c`

*Rationale:* Accessibility is not optional. If someone can't read it, the interface has failed.

---

## Resolved Tensions

| Tension | Resolution |
|---------|------------|
| Joy vs Stark | Joy = milestone glow only. Stark everywhere else. |
| Curated vs Ship Everything | Ship everything, but with severe aesthetic. Curated through severity, not scope. |
| Composability vs Consolidation | K-Blocks compose via reference (graph), not nesting (tree). |
| Accessibility vs Aesthetic | Strict WCAG AA. Aesthetic must serve accessibility, not fight it. |

---

## Implementation Status

| # | Decision | Status |
|---|----------|--------|
| 1 | Touch targets | ✅ CSS created |
| 2 | Milestone glow | ✅ CSS created |
| 3 | Motion budget | ✅ CSS enforced (severe-base.css) |
| 4 | Bottom tab bar | ✅ CSS created |
| 5 | External docs | ℹ️ No work needed |
| 6 | Keyboard shortcuts | ⏳ Pending implementation |
| 7 | K-Block references | ✅ Spec defined |
| 8 | Entanglement | ✅ Spec defined |
| 9 | Event sourcing | ✅ HEAD-FIRST implemented |
| 10 | Everyone architect | ℹ️ No work needed |
| 11 | All 6 jewels | ⏳ Phase 2-6 |
| 12 | Gutter annotations | ⏳ Pending implementation |
| 13 | Fuzzy search | ⏳ Pending implementation |
| 14 | CSS constraints | ✅ layout-constraints.css |
| 15 | WCAG AA | ✅ tokens.css fixed |

---

## Kent's Voice Check

Before any implementation, verify against Kent's voice anchors:

- [ ] *"Daring, bold, creative, opinionated but not gaudy"* — Is this opinionated?
- [ ] *"simplistic, brutalistic?, dense, intelligent design"* — Is this dense?
- [ ] *"Tasteful > feature-complete"* — Is this tasteful?
- [ ] *"The Mirror Test"* — Does this feel like Kent on his best day?

---

*Filed: 2026-01-17 | Supersedes: All prior design question documents*
