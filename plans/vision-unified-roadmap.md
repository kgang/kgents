# UNIFIED UI VISION: Implementation Roadmap

> *"The file is a lie. There is only the graph."*
> *"The proof IS the decision. The mark IS the witness."*
> *"Power through keystrokes, not IDE heaviness."*

**Created**: 2025-12-24
**Status**: SYNTHESIS OF FOUR AGENT REPORTS
**Voice Anchor**: "Daring, bold, creative, opinionated but not gaudy"

---

## EXECUTIVE SUMMARY

Four parallel research agents explored the feasibility and design of kgents' UI transformation. The findings are remarkably positive: **85-90% of the foundation already exists**.

| Vision | Current State | Key Finding |
|--------|---------------|-------------|
| **Command Substrate** | CommandLine.tsx (vim `:`) exists | cmdk recommended; 2-week Phase 1 |
| **Living Canvas** | AstronomicalChart.tsx + d3-force + Pixi | 90% done; evolve, don't rewrite |
| **Witness Dialectic** | FusionService + CLI complete | Missing: persistence + Web UI |
| **Ghost Text** | CodeMirror 6 with decorations | AGENTESE-first completion design |

**Total effort estimate**: 10-12 weeks to full implementation.

---

## SYNTHESIS: WHAT WE LEARNED

### 1. Command Substrate — Ready for Phase 1

**Library Choice**: **cmdk** (not kbar)
- Composable primitives align with our architecture
- Minimal bundle (~1KB gzipped)
- Works with existing Radix UI
- command-score for fuzzy search (competitive with microfuzz)

**Integration Points**:
- Cmd+K is currently unbound → clean entry point
- 6-mode system fully defined → mode-aware filtering ready
- useKeyHandler.ts has declarative binding registry → easy to extend

**Files to Create**:
```
impl/claude/web/src/hypergraph/
├── CommandPalette.tsx        # NEW: Main component
├── useCommandRegistry.ts     # NEW: Command list management
├── usePaletteSearch.ts       # NEW: Fuzzy search logic
└── CommandPalette.css        # NEW: STARK BIOME styling
```

**Phase 1 Deliverables** (2 weeks):
- Cmd+K opens fullscreen modal
- Fuzzy search 200+ commands in <1.5ms
- File navigation + basic AGENTESE paths
- Tab completion, Esc dismiss

---

### 2. Living Canvas — Evolve, Don't Rewrite

**Critical Finding**: We already have production graph visualization!

**Existing Infrastructure**:
| Component | Lines | Status |
|-----------|-------|--------|
| AstronomicalChart.tsx | 510 | Production |
| useForceLayout.ts | 316 | d3-force integrated |
| Quadtree.ts | — | Spatial indexing done |
| ViewportCuller.ts | — | Frustum culling done |
| LevelOfDetail.ts | — | Needs semantic zoom expansion |

**Library Decision**: **Keep d3-force + Pixi.js**
- Don't switch to force-graph/react-force-graph
- We own the canvas → we control semantic zoom
- GPU acceleration via Pixi already working

**Integration Strategy**:
- Graph as toggleable sidebar in NORMAL mode (press `g`)
- Full-screen GRAPH mode later
- Focus node = selection in graph (bidirectional)

**Files to Create/Modify**:
```
impl/claude/web/src/hypergraph/
├── LivingCanvas.tsx              # NEW: Main component (evolves from AstronomicalChart)
├── useLivingCanvasState.ts       # NEW: Unified graph state
├── useLivingCanvasZoom.ts        # NEW: Semantic zoom logic
└── HypergraphEditor.tsx          # UPDATE: Integrate graph sidebar
```

**Phase 1 Deliverables** (3 weeks):
- Extract AstronomicalChart into reusable hook
- Add 3-level semantic zoom (dots → icons → content)
- Integrate with HypergraphEditor (sidebar mode)
- Confidence colors for edges (red→amber→green)

---

### 3. Witness Dialectic — Plumbing + UI

**Critical Finding**: Backend 85% complete, frontend 0%.

**What Works**:
- `kg decide` CLI (guided + fast modes)
- FusionService with dialectical engine
- `self.fusion.*` AGENTESE nodes
- Immutable data model (Proposal, Challenge, Synthesis, FusionResult)

**What's Missing**:
1. **Persistence**: FusionResults live in-memory only
2. **Web UI**: No components for displaying decisions
3. **API endpoints**: No REST for querying decisions

**5 New UI Components Needed**:
| Component | Purpose |
|-----------|---------|
| DialogueView | Split-pane display (left: thesis, center: synthesis, right: antithesis) |
| DecisionFooterWidget | Compact fusion display in WitnessFooter |
| DecisionStream | List of all decisions with filtering |
| VetoPanel | Kent's disgust veto interface |
| DialecticModal | Quick decision capture (mirrors `kg decide --fast`) |

**Phase 1 Deliverables** (3 weeks):
- Persist FusionResult → WitnessMark
- Add fusion event to WitnessFooter
- DialogueView modal component
- useDialecticDecisions hook

---

### 4. Ghost Text — AGENTESE-First Completion

**Critical Finding**: CodeMirror 6 has all the extension points we need.

**Rendering Strategy**:
- `Decoration.widget()` or `Decoration.mark()` for inline ghost text
- STARK BIOME styling: steel-400 (#5a5a64) at 40% opacity
- INSERT mode only (disabled in NORMAL readonly mode)

**Three-Source Completion Model**:
| Source | Priority | Latency |
|--------|----------|---------|
| AGENTESE paths (world.*, self.*, concept.*) | Highest (1.0) | Instant (cached) |
| Spec vocabulary (headings, terms) | Medium (0.7) | Instant (indexed) |
| Recent marks (decisions, annotations) | Low (0.4) | API (300ms) |

**Mechanics**:
- Tab: Accept suggestion
- Esc: Dismiss ghost text
- Typing past: Auto-dismiss
- Debounce: 200ms (human pause rhythm)

**Files to Create**:
```
impl/claude/web/src/components/editor/
├── ghostText.ts              # NEW: CodeMirror 6 extension
├── useGhostTextSources.ts    # NEW: Completion source aggregator
└── ghostText.css             # NEW: STARK BIOME ghost styling

impl/claude/protocols/api/
├── agentese_complete.py      # NEW: /api/agentese/complete endpoint
├── spec_complete.py          # NEW: /api/spec/complete endpoint
└── marks_recent.py           # NEW: /api/marks/recent endpoint
```

**Phase 1 Deliverables** (4 weeks):
- ghostText.ts CodeMirror extension
- Local AGENTESE path completion (no API)
- Tab/Esc keybindings
- Animation (fade-in on appear, flash on accept)

---

## UNIFIED IMPLEMENTATION ROADMAP

### Phase 0: Foundation Hardening (1 week)
*Before adding new features, ensure the base is solid.*

- [ ] Verify typecheck passes (`npm run typecheck`)
- [ ] Audit existing hooks for duplication
- [ ] Confirm mode system (6 modes) works correctly
- [ ] Test existing graph visualization (AstronomicalChart)

### Phase 1: Command Substrate (2 weeks)
*Cmd+K is the entry point to everything.*

**Week 1**:
- [ ] Install cmdk: `npm install cmdk`
- [ ] Create CommandPalette.tsx with basic UI
- [ ] Implement useCommandRegistry.ts
- [ ] Wire Cmd+K trigger in HypergraphEditor

**Week 2**:
- [ ] Add file navigation (spec/, docs/, impl/)
- [ ] Add AGENTESE path detection
- [ ] Style with STARK BIOME
- [ ] Performance test (<50ms open, <1.5ms search)

### Phase 2: Living Canvas (3 weeks)
*The graph becomes the primary navigation surface.*

**Week 3**:
- [ ] Extract AstronomicalChart → useGraphVisualization hook
- [ ] Add GraphSidebar component
- [ ] Wire `g` keybinding to toggle sidebar

**Week 4**:
- [ ] Implement 3-level semantic zoom in LevelOfDetail.ts
- [ ] Add confidence colors to edges
- [ ] Click node → focus in editor

**Week 5**:
- [ ] Add hover previews (content + edge details)
- [ ] Performance profiling (target: 10K nodes)
- [ ] Trail visualization (navigation history as graph path)

### Phase 3: Witness Dialectic (3 weeks)
*Decisions become visible everywhere.*

**Week 6**:
- [ ] Extend WitnessPersistence for FusionMarks
- [ ] Add REST endpoints for decision queries
- [ ] Emit fusion events via WitnessBus

**Week 7**:
- [ ] DialogueView component (split-pane)
- [ ] DecisionFooterWidget in WitnessFooter
- [ ] useDialecticDecisions hook

**Week 8**:
- [ ] DecisionStream list view
- [ ] VetoPanel for Kent
- [ ] DialecticModal for quick capture

### Phase 4: Ghost Text (4 weeks)
*AI amplifies, never replaces.*

**Week 9**:
- [ ] ghostText.ts CodeMirror extension
- [ ] Local AGENTESE path completion (cached)
- [ ] Tab/Esc keybindings

**Week 10**:
- [ ] Backend: /api/agentese/complete endpoint
- [ ] Backend: /api/spec/complete endpoint
- [ ] Ranking algorithm implementation

**Week 11**:
- [ ] Animation (fade-in, flash on accept)
- [ ] Caching layer (frontend + backend)
- [ ] Error handling & fallback UI

**Week 12**:
- [ ] User testing with Kent
- [ ] Adjust opacity/colors per STARK BIOME testing
- [ ] Performance benchmarking
- [ ] Voice validation (does it amplify, not replace?)

---

## DEPENDENCIES BETWEEN PHASES

```
              ┌─────────────────┐
              │ Phase 0:        │
              │ Foundation      │
              │ (1 week)        │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Phase 1:       │ │ Phase 2:       │ │ Phase 3:       │
│ Command        │ │ Living         │ │ Witness        │
│ Substrate      │ │ Canvas         │ │ Dialectic      │
│ (2 weeks)      │ │ (3 weeks)      │ │ (3 weeks)      │
└────────┬───────┘ └────────────────┘ └────────────────┘
         │
         │ (Phase 4 depends on Phase 1 for Cmd+K integration)
         ▼
┌────────────────┐
│ Phase 4:       │
│ Ghost Text     │
│ (4 weeks)      │
└────────────────┘
```

**Parallelization**:
- Phases 1, 2, 3 can run in parallel after Phase 0
- Phase 4 starts after Phase 1 (needs Cmd+K for "invoke completion")
- Total critical path: 1 + 2 + 4 = **7 weeks minimum**
- With parallelization: **~8-10 weeks** for all four visions

---

## SUCCESS METRICS

| Metric | Current | Target | Phase |
|--------|---------|--------|-------|
| Time to navigate | 5+ keystrokes | 2 (Cmd+K + select) | Phase 1 |
| Architecture comprehension | 30+ minutes | 30 seconds | Phase 2 |
| Decision capture rate | ~10% | >90% significant | Phase 3 |
| Ghost acceptance rate | N/A | 30-50% | Phase 4 |
| Palette latency | N/A | <50ms open | Phase 1 |
| Graph nodes supported | ~100 | 10K | Phase 2 |
| Semantic zoom levels | 1 | 3 | Phase 2 |

---

## RISK ASSESSMENT

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cmd+K conflicts with browser | HIGH | `preventDefault()` before listeners |
| Graph performance at scale | MEDIUM | Quadtree + LOD (already implemented) |
| Ghost text distracting | MEDIUM | INSERT mode only, 200ms debounce |
| FusionResult data loss | HIGH | Persist to witness store (Phase 3) |
| Voice dilution ("sausage") | HIGH | Anti-sausage protocol, user testing |

---

## IMMEDIATE NEXT STEPS

1. **Phase 0** (This week):
   - Run `npm run typecheck && npm run lint` to confirm clean slate
   - Read AstronomicalChart.tsx to understand existing graph code
   - Review CommandLine.tsx for integration patterns

2. **Phase 1 Kickoff** (Next week):
   - `npm install cmdk`
   - Create CommandPalette.tsx skeleton
   - Wire Cmd+K in HypergraphEditor.tsx

3. **Parallel Exploration**:
   - Draft DialogueView design (split-pane mockup)
   - Draft ghostText.ts CodeMirror extension structure

---

## THE VISION REALIZED

In 10-12 weeks, Kent opens kgents.

**Cmd+K** → The command palette appears. He types "witness". Instantly: all witness-related marks, the WitnessFooter, the witness spec. Two keystrokes to anywhere.

**The graph breathes** in the sidebar. CONSTITUTION glows at center. He drags a node; neighbors adjust. Weak edges pulse amber—attention needed. He zooms out; clusters emerge. The architecture is visible, not just documented.

**He makes a decision**. The screen splits: his view left, Claude's right. The synthesis emerges in the center. A mark is created. The decision is witnessed. Forever.

**He types a spec section**. Ghost text appears—muted, patient. `world.witness.mark` completes before he finishes typing. Tab to accept. The AI amplifies his thought, doesn't replace it.

The codebase has become a living system. Every decision traced. Every edge evidenced. Every command one keystroke away.

---

*"The file is a lie. There is only the graph."*
*"The proof IS the decision. The mark IS the witness."*
*"Power through keystrokes, not IDE heaviness."*
*"And the AI... amplifies."*

---

**Filed**: 2025-12-24
**Synthesized from**: 4 parallel agent reports
**Total estimated effort**: 10-12 weeks
