# Gestalt Visual Showcase: Chunk 2 Continuation

**Plan**: `plans/gestalt-visual-showcase.md`
**Previous**: Chunk 1 (Enhanced Filter Panel) - COMPLETE
**Current**: Chunk 2 (Interactive Legend & Tooltips) - **COMPLETE**
**Date**: 2025-12-16
**Status**: COMPLETE

---

## Pre-Flight Checklist

Before starting Chunk 2, verify Chunk 1 works:

### 1. Start the Backend

```bash
cd /Users/kentgang/git/kgents/impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

### 2. Start the Frontend

```bash
cd /Users/kentgang/git/kgents/impl/claude/web
npm run dev
```

### 3. Manual Testing (Chunk 1)

Navigate to `http://localhost:3000/gestalt` and verify:

| Feature | Test |
|---------|------|
| **View Presets** | Click each preset (All, Healthy, At Risk, Violations, Core) - graph should filter |
| **Health Filter** | Toggle grade buttons - modules should appear/disappear |
| **Module Search** | Type "api" - should see matching modules, click to select |
| **Keyboard Nav** | In search, use ↑↓ to navigate, Enter to select, Esc to close |
| **Mobile Layout** | Resize to <768px - controls should move to bottom drawer |
| **Filter Persistence** | Select a module, change filters - selected module should remain visible if it matches |

### 4. Run Tests

```bash
cd /Users/kentgang/git/kgents/impl/claude/web
npm run test -- tests/unit/gestalt/filter-logic.test.ts
# Expected: 24 tests passing
```

---

## Chunk 2: Interactive Legend & Tooltips

**Goal**: Make the visualization self-documenting.

### Files to Create

```
impl/claude/web/src/components/gestalt/
├── Legend.tsx              # Collapsible legend component
├── NodeTooltip.tsx         # Hover tooltip using drei's Html
└── EdgeLegend.tsx          # Edge type explanations (optional, prep for Chunk 3)
```

### Legend Component Spec

```typescript
interface LegendProps {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  density: Density;
}
```

**Visual Design**:
```
┌─────────────────────────────────────┐
│  LEGEND                     [−]     │
├─────────────────────────────────────┤
│                                     │
│  NODE HEALTH                        │
│  ● A+/A   ● B+/B   ● C+/C   ● D/F   │
│                                     │
│  NODE SIZE                          │
│  ◯ <100 LOC  ○ ~500 LOC  ● >1K LOC │
│                                     │
│  EDGES                              │
│  ─── Import   ─── Violation         │
│                                     │
│  RINGS = Architectural Layers       │
│                                     │
└─────────────────────────────────────┘
```

### NodeTooltip Component Spec

```typescript
interface NodeTooltipProps {
  node: CodebaseModule;
  position: [number, number, number];
  visible: boolean;
  density: Density;
}
```

**Visual Design**:
```
┌──────────────────────────────────┐
│  protocols.api.brain             │
│  ─────────────────────────────   │
│  Health: A (92%)                 │
│  Layer: api                      │
│  LOC: 245                        │
│  Dependencies: 12 │ Dependents: 5│
│  ─────────────────────────────   │
│  Click for details               │
└──────────────────────────────────┘
```

### Integration Points

1. **Legend**: Add to Gestalt.tsx as an overlay (absolute positioned)
2. **Tooltip**: Add to ModuleNode component, triggered on hover after 300ms delay
3. **State**: Add `legendCollapsed` and `hoveredModule` to component state

### Key Technical Notes

- Use `@react-three/drei`'s `Html` component for tooltips in 3D space
- Tooltip should follow camera rotation (use `transform` prop)
- Legend collapses to just the header when collapsed
- Mobile: Legend hidden by default, show via FAB

### Exit Criteria

- [x] Legend component renders all node/edge types
- [x] Legend is collapsible (remembers state in localStorage)
- [x] Hover tooltip appears on node hover (300ms delay)
- [x] Tooltip follows camera rotation (via drei Html sprite mode)
- [x] Mobile: tooltip disabled (falls back to click-for-details)
- [x] Legend extensible for infrastructure node types (Chunk 3 prep)
- [x] 33 tests (rendering, interaction, position)

---

## Reference Files

| File | Purpose |
|------|---------|
| `plans/gestalt-visual-showcase.md` | Full plan with Chunk 2 details |
| `src/components/gestalt/types.ts` | Shared types (add NodeTooltipState) |
| `src/pages/Gestalt.tsx` | Integration target |
| `@react-three/drei` | Html component for 3D tooltips |

---

## Success Criteria

After Chunk 2: **ALL MET**
- [x] User hovers over node → tooltip appears with key metrics
- [x] User sees legend explaining all visual encodings
- [x] Legend can be collapsed to save space
- [x] Mobile users use click-for-details pattern
- [x] Plan progress updates to 50%

---

*"The best documentation is a visualization that explains itself."*
