# UI Rebuild: From First Principles

> *"The file is a lie. There is only the graph."*
> *"Daring, bold, creative, opinionated but not gaudy."*

**Status**: ✅ COMPLETE
**Date**: 2025-12-23
**Goal**: Rebuild the UI from scratch for coherency while preserving the vision

---

## 🎉 COMPLETION SUMMARY

| Phase | What | Result |
|-------|------|--------|
| **Phase 1** | Delete dead code | 47 archived files removed, components migrated |
| **Phase 2** | Design system | CSS variables consolidated |
| **Phase 3** | Editor refactor | Split 37KB monolith into state/panes/modules |
| **Phase 4** | Hooks consolidation | Unified duplicate hooks |
| **Phase 5** | Pages simplification | Reduced to minimal wrappers (77% reduction in EditorPage) |
| **Phase 6** | Layout coherence | Verified consistent AppShell usage |

**Metrics:**
| Metric | Before | After |
|--------|--------|-------|
| TypeScript files | 244 | 230 |
| Archived files | 47 | 0 |
| HypergraphEditor.tsx | 1090 lines | 698 lines (36% reduction) |
| EditorPage.tsx | 320 lines | 74 lines (77% reduction) |
| TypeScript errors | 0 | 0 |

---

## The Vision (Non-Negotiable)

1. **STARK BIOME**: 90% steel, 10% life. Dark, contemplative, earned glow.
2. **VIM PRIMITIVES**: Power through keystrokes, not IDE heaviness.
3. **GRAPH-FIRST**: Navigate concepts, not files.
4. **WITNESSED**: Every edit, mark, navigation creates evidence.
5. **JOY-INDUCING**: Warm tone, procedural vitality, smooth animations.

---

## Current State (Problems)

| Metric | Value | Issue |
|--------|-------|-------|
| Total files | 286 | Sprawl |
| Archived/dead | 47 (19.6%) | Should be 0% |
| Duplicate hooks | 2 (useKBlock, useSpecNavigation) | Confusion |
| Largest component | 37KB HypergraphEditor.tsx | Unmaintainable |
| CSS files | 38 | Over-scoped |
| Entry points | 8 pages + 3 galleries | Unclear |

---

## Target Structure

```
impl/claude/web/src/
├── main.tsx                      # Entry (unchanged)
├── App.tsx                       # Routes (simplified)
├── globals.css                   # STARK BIOME design system (ONE file)
│
├── api/
│   └── client.ts                 # Backend API (single file, typed)
│
├── hooks/                        # Shared React hooks
│   ├── useKBlock.ts              # K-Block lifecycle (UNIFIED)
│   ├── useWitnessStream.ts       # SSE for witness events
│   └── useGraphApi.ts            # Graph navigation API
│
├── editor/                       # THE HYPERGRAPH EMACS
│   ├── index.ts                  # Public exports
│   ├── Editor.tsx                # Shell (<200 lines)
│   ├── Editor.css                # Editor-specific styles
│   │
│   ├── state/                    # State machine
│   │   ├── types.ts              # GraphNode, Edge, Mode, etc.
│   │   ├── reducer.ts            # Navigation actions
│   │   └── useEditorState.ts     # React hook for state
│   │
│   ├── modes/                    # Modal editing
│   │   ├── NormalMode.tsx        # j/k/gd/gr/gt navigation
│   │   ├── InsertMode.tsx        # CodeMirror editing
│   │   ├── EdgeMode.tsx          # Edge creation/navigation
│   │   ├── WitnessMode.tsx       # Quick marks (mE/mG/mT...)
│   │   └── CommandMode.tsx       # :e/:w/:ag commands
│   │
│   ├── panes/                    # Visual components
│   │   ├── ContentPane.tsx       # Main content area
│   │   ├── EdgeGutter.tsx        # Confidence-colored badges
│   │   ├── Portal.tsx            # Inline expansion (zo/zc)
│   │   ├── TrailBar.tsx          # Breadcrumb navigation
│   │   └── StatusLine.tsx        # Mode indicator
│   │
│   └── commands/                 # Command handling
│       ├── CommandLine.tsx       # Input with tab completion
│       └── handlers.ts           # Command implementations
│
├── components/                   # Shared UI primitives
│   ├── Breathe.tsx               # Subtle animation
│   ├── Toast.tsx                 # Notifications
│   ├── Loading.tsx               # Personality loading
│   ├── Feedback.tsx              # Success/warning/error overlay
│   └── FileExplorer.tsx          # File tree (when no path)
│
├── pages/                        # Route surfaces
│   ├── EditorPage.tsx            # /editor/* (Hypergraph Emacs)
│   ├── BrainPage.tsx             # /brain (Memory explorer)
│   ├── LedgerPage.tsx            # /ledger (Spec health)
│   └── ChartPage.tsx             # /chart (Visualization)
│
└── layout/                       # App chrome
    ├── AppShell.tsx              # Navbar + content area
    └── WitnessFooter.tsx         # Always-on witness stream
```

**Target metrics**:
- ~50 files (down from 286)
- 0 archived files
- 1 design system file
- Clear separation: editor / components / pages / layout

---

## Rebuild Phases

### Phase 1: CLEAN SLATE (Delete Dead Code)

Delete everything that's not essential:
- `_archive/` directory (47 files)
- `*.bak*` files
- Unused components, hooks, galleries
- Duplicate files

**Keep only**:
- `main.tsx`, `App.tsx`
- `api/client.ts` (consolidate types)
- Core hypergraph files (refactor later)
- Essential pages

### Phase 2: DESIGN SYSTEM (Single CSS File)

Consolidate all 38 CSS files into ONE `globals.css`:
- STARK BIOME colors
- Typography (JetBrains Mono / Inter)
- Spacing scale (4px base)
- Responsive breakpoints
- Animation keyframes
- Component primitives (buttons, inputs, badges)

### Phase 3: EDITOR REFACTOR (Split the Monolith)

Split 37KB HypergraphEditor.tsx into clean modules:
- `Editor.tsx` — Shell, layout, mode switching
- `state/` — Types, reducer, state hook
- `modes/` — One component per mode
- `panes/` — Visual sub-components
- `commands/` — Command parsing and execution

### Phase 4: HOOKS CONSOLIDATION

Unify duplicate hooks:
- ONE `useKBlock.ts` (handles dialogue + file)
- ONE `useGraphApi.ts` (navigation + edges)
- Remove `_archive/` versions

### Phase 5: PAGES SIMPLIFICATION

Simplify page components:
- `EditorPage.tsx` — Minimal wrapper, path routing
- `BrainPage.tsx` — Memory explorer
- `LedgerPage.tsx` — Spec health dashboard
- `ChartPage.tsx` — Visualization

### Phase 6: LAYOUT COHERENCE

Create consistent app chrome:
- `AppShell.tsx` — Navbar + content area
- `WitnessFooter.tsx` — Always-on witness stream
- Shared layout patterns

---

## Exit Criteria

| Criterion | Measurement |
|-----------|-------------|
| File count | < 60 files |
| Dead code | 0 archived files |
| CSS files | 1 (globals.css) |
| Editor lines | < 200 in shell |
| TypeScript | Compiles with no errors |
| Routes work | /editor/*, /brain, /ledger, /chart |
| Core flows | Reading, Writing, Witnessing |

---

## The Test

> *"Daring, bold, creative, opinionated but not gaudy"*

After rebuild:
- **Daring**: Graph-first navigation, not file browser
- **Bold**: Six modes, vim keybindings, power through keystrokes
- **Creative**: Portal expansion, witness integration, confidence colors
- **Not gaudy**: Minimal chrome, 90% steel, earned glow

---

*Created: 2025-12-23*
*Voice anchor: "Tasteful > feature-complete"*
