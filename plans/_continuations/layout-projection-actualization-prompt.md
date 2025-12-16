# Actualization Prompt: Layout Projection Functor

> Use this prompt to begin implementing the Layout Projection Functor following the N-Phase cycle.

---

## Context

The Layout Projection Functor spec has been written in `spec/protocols/projection.md` (lines 213-424). A plan file exists at `plans/web-refactor/layout-projection-functor.md` with 5 implementation phases.

**Current State**: Spec complete, implementation pending (Phase RESEARCH).

---

## The Prompt

```
I need to implement the Layout Projection Functor from spec to working code.

## Background

The Layout Projection Functor distinguishes content projection (lossy compression) from layout projection (structural isomorphism). The spec is complete at `spec/protocols/projection.md` lines 213-424.

Key insight: Mobile layouts are not "compressed desktop"—they are structurally different. A sidebar on desktop becomes a bottom drawer on mobile, but the SAME INFORMATION is accessible through different interaction modalities.

## The Spec Summary

1. **Two Functors**:
   - `Content[D] : State → ContentDetail[D]` (lossy compression)
   - `Layout[D] : WidgetTree → Structure[D]` (structural isomorphism)

2. **Three Layout Primitives**:
   - Split: collapse_secondary / fixed_panes / resizable_divider
   - Panel: bottom_drawer / collapsible_panel / fixed_sidebar
   - Actions: floating_fab / inline_buttons / full_toolbar

3. **Three Density Levels**: compact (<768px), comfortable (768-1024px), spacious (>1024px)

4. **Physical Constraints**: Touch targets ≥ 48px (density-invariant)

5. **Composition Laws**:
   - Vertical (`//`) preserves: `Layout[D](A // B) = Layout[D](A) // Layout[D](B)`
   - Horizontal (`>>`) transforms: sidebar >> canvas → canvas + FAB(sidebar)

## Your Task

Follow the N-Phase cycle to implement this spec. Start with the RESEARCH phase.

### RESEARCH Phase

1. Read the full spec: `spec/protocols/projection.md` (lines 213-424)
2. Audit existing elastic components:
   - `impl/claude/web/src/components/elastic/ElasticSplit.tsx`
   - `impl/claude/web/src/components/elastic/BottomDrawer.tsx`
   - `impl/claude/web/src/components/elastic/FloatingActions.tsx`
   - `impl/claude/web/src/hooks/useLayoutContext.ts`
3. Check if existing components match the spec
4. Identify gaps between current implementation and spec
5. Document findings in `plans/web-refactor/layout-projection-functor.md` session_notes

### Questions to Answer in RESEARCH

- Do existing elastic components handle all three density levels?
- Are physical constraints (48px touch targets) enforced?
- Is there a canonical `LayoutHints` type already?
- Does `useWindowLayout` provide the full `LayoutContext` interface?
- Are there existing tests for composition behavior?

### After RESEARCH

Update the plan file with findings and proceed to DEVELOP phase, which involves:
- Defining Python `LayoutHints` and `LayoutPrimitive` types
- Formalizing TypeScript types in `elastic/types.ts`
- Adding missing density behaviors to existing components

## Files to Read First

1. `spec/protocols/projection.md` (lines 213-424) - The spec
2. `plans/web-refactor/layout-projection-functor.md` - The plan
3. `impl/claude/web/src/hooks/useLayoutContext.ts` - Current layout hook
4. `impl/claude/web/src/pages/Gestalt.tsx` - Gold standard implementation (already uses elastic patterns)

## Success Criteria

- RESEARCH phase: Audit complete, gaps documented
- DEVELOP phase: Types defined in Python and TypeScript
- Full implementation: 100+ tests, all composition laws verified
```

---

## How to Use This Prompt

1. **New Session**: Copy the prompt above into a new Claude session
2. **Context**: The session should have access to the kgents codebase
3. **Phase Tracking**: Update `plans/web-refactor/layout-projection-functor.md` as you progress
4. **Entropy Budget**: 0.08 allocated for exploration; sip from void.entropy if needed

---

## Expected Outputs

### After RESEARCH Phase

```yaml
session_notes: |
  RESEARCH Complete (2025-12-XX):
  - Audited 3 elastic components + useLayoutContext hook
  - Gaps found:
    1. No formal LayoutHints type (ad-hoc props)
    2. Touch target enforcement inconsistent
    3. Composition laws not tested
  - Existing strengths:
    1. Gestalt.tsx is gold standard
    2. useWindowLayout provides density correctly
    3. ElasticSplit handles collapse well
  - Next: DEVELOP phase - formalize types
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: pending
  ...
```

### After DEVELOP Phase

```yaml
session_notes: |
  DEVELOP Complete (2025-12-XX):
  - Created agents/i/reactive/layout.py with:
    - Density enum
    - LayoutHints dataclass
    - LayoutPrimitive dataclass
    - SPLIT/PANEL/ACTIONS primitives
  - Created web/src/components/elastic/types.ts with:
    - TypeScript equivalents
    - DensityMap<T> utility type
    - fromDensity() helper
  - 35 tests passing
  - Next: STRATEGIZE - plan composition law verification
```

---

## Phase Handoff Notes

Each phase should leave clear breadcrumbs for the next session:

| Phase | Output | Handoff |
|-------|--------|---------|
| RESEARCH | Audit findings | What needs to be built/fixed |
| DEVELOP | Type definitions | Ready for implementation |
| STRATEGIZE | Test plan | What laws to verify, how |
| CROSS-SYNERGIZE | Patterns from other systems | Reusable patterns identified |
| IMPLEMENT | Working code | Ready for QA |
| QA | Property tests | Edge cases covered |
| TEST | Full test suite | 100+ tests passing |
| EDUCATE | Docs/skills updated | Others can use |
| MEASURE | Metrics collected | Performance baselines |
| REFLECT | Lessons learned | Future improvements |

---

*"The spec captures the insight. The plan organizes the work. The implementation makes it real."*
