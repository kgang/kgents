# Web Reactive Refactor - Phase 2 Continuation Prompt

**Plan**: `plans/agent-town/web-reactive-refactor.md`
**Skill**: `docs/skills/n-phase-cycle.md` (SENSE → ACT → REFLECT)
**Previous**: Phase 1 (Foundation) Complete - 76 tests passing

---

## Context

Phase 1 established the reactive bridge at `impl/claude/web/src/reactive/`:

| File | Purpose |
|------|---------|
| `types.ts` | WidgetJSON discriminated union matching Python `_to_json()` |
| `useWidgetState.ts` | State management hooks + SSE streaming |
| `WidgetRenderer.tsx` | Dynamic widget renderer with type dispatch |
| `context.tsx` | Theme/interaction context provider |
| `index.ts` | Re-exports |

The WidgetRenderer currently renders ALL widget types inline. Phase 2 extracts these into dedicated components in a `/widgets/` directory for better organization and reusability.

---

## Phase 2: Widget Components (Effort: 1.5)

**Goal**: Create React components that consume JSON projections.

### Directory Structure to Create

```
impl/claude/web/src/widgets/
├── layout/
│   ├── HStack.tsx        # Horizontal composition
│   ├── VStack.tsx        # Vertical composition
│   └── index.ts
├── primitives/
│   ├── Glyph.tsx         # Atomic visual unit
│   ├── Bar.tsx           # Progress/capacity bar
│   ├── Sparkline.tsx     # Activity sparkline
│   └── index.ts
├── cards/
│   ├── CitizenCard.tsx   # Town citizen card
│   ├── EigenvectorDisplay.tsx  # Personality vectors
│   └── index.ts
├── dashboards/
│   ├── ColonyDashboard.tsx     # Main town dashboard
│   └── index.ts
└── index.ts
```

### Tasks

1. **Extract primitives** from `WidgetRenderer.tsx` into `/widgets/primitives/`
   - Move `Glyph`, `Bar`, `Sparkline` components
   - Keep them as pure presentational components
   - Export from `primitives/index.ts`

2. **Extract layout** into `/widgets/layout/`
   - Move `HStack`, `VStack` components
   - These recursively render children via WidgetRenderer
   - Export from `layout/index.ts`

3. **Extract cards** into `/widgets/cards/`
   - Move `CitizenCard` component
   - Create `EigenvectorDisplay` for warmth/curiosity/trust visualization
   - Export from `cards/index.ts`

4. **Extract dashboards** into `/widgets/dashboards/`
   - Move `ColonyDashboard` component
   - Export from `dashboards/index.ts`

5. **Update WidgetRenderer** to import from `/widgets/`
   - WidgetRenderer becomes a thin dispatcher
   - All rendering logic lives in widget components

6. **Verify composition laws**
   - `(a >> b) >> c ≡ a >> (b >> c)` (HStack associativity)
   - `(a // b) // c ≡ a // (b // c)` (VStack associativity)
   - Write tests that verify nested composition renders correctly

7. **Write tests** in `tests/unit/widgets/`
   - Mirror the structure: `primitives/`, `layout/`, `cards/`, `dashboards/`
   - Test each component in isolation
   - Test composition behavior

### Verification Checklist

- [ ] All primitives extracted to `/widgets/primitives/`
- [ ] Layout components extracted to `/widgets/layout/`
- [ ] Card components extracted to `/widgets/cards/`
- [ ] Dashboard components extracted to `/widgets/dashboards/`
- [ ] WidgetRenderer updated to use new imports
- [ ] Composition laws verified with tests
- [ ] All 76 existing tests still pass
- [ ] New widget tests added

---

## N-Phase Cycle Steps

### SENSE (Explore)

1. Read current `WidgetRenderer.tsx` to understand component structure
2. Identify which components can be extracted as-is vs need refactoring
3. Check if any components have dependencies that complicate extraction
4. Review existing tests to understand test patterns

### ACT (Implement)

1. Create `/widgets/` directory structure
2. Extract components one category at a time (primitives → layout → cards → dashboards)
3. Update imports in `WidgetRenderer.tsx` after each extraction
4. Run tests after each extraction to catch regressions
5. Write new tests for extracted components
6. Add composition law tests

### REFLECT (Verify)

1. Run full test suite: `npm test -- --run tests/unit/`
2. Verify all 76+ tests pass
3. Check that WidgetRenderer is now a thin dispatcher
4. Update plan checklist
5. Add learnings to `plans/meta.md`

---

## Key Files to Reference

| File | Purpose |
|------|---------|
| `impl/claude/web/src/reactive/WidgetRenderer.tsx` | Current implementation to extract from |
| `impl/claude/web/src/reactive/types.ts` | Type definitions for props |
| `impl/claude/web/tests/unit/reactive/WidgetRenderer.test.tsx` | Existing tests (keep passing) |
| `impl/claude/agents/i/reactive/composable.py` | Python composition reference |

---

## Commands

```bash
# Run reactive module tests
cd impl/claude/web && npm test -- --run tests/unit/reactive/

# Run all web tests
cd impl/claude/web && npm test -- --run

# Type check
cd impl/claude/web && npm run typecheck
```

---

## Notes

- **Do not break existing tests** - the 76 tests in `tests/unit/reactive/` must continue passing
- **Prefer composition over inheritance** - widgets should compose via props, not class extension
- **Keep components pure** - no internal state unless absolutely necessary; state lives in hooks
- **Type-safe dispatch** - WidgetRenderer's switch statement should remain exhaustive
- Components should be memoized (`memo()`) for render optimization

---

*Generated: 2025-12-15 | Phase 1 Complete | Ready for Phase 2*
