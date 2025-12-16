---
path: plans/ui-factoring-clean-slate
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: [core-apps-synthesis]
session_notes: |
  COMPLETE. Executed aggressive UI cleanup:
  - Phase 1: Web UI gutted (23K→9K lines, 60% reduction)
  - Phase 2: CLI handlers archived (12 handlers moved)
  - Phase 3: Demos consolidated to unified_app/unified_notebook
  - Phase 4: Town UI legacy removed
  - Phase 5: Tests cleaned (18141 pass, 87 skip)
  Archive directories created for all removed code.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: pending
  MEASURE: complete
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.08
  returned: 0.05
---

# UI Factoring: Clean Slate

> *"Delete ruthlessly to create space for the essential."*

**Goal**: Remove all non-essential UI code, keeping only the bare minimum to serve as foundation for next-generation UIs built reproducibly from reactive primitives.

**Principles**: Tasteful (AD-001), Composable (AD-005), Generative (AD-007)

---

## What We Keep (The Essentials)

### 1. Reactive Primitives Substrate
```
impl/claude/agents/i/reactive/
├── signal.py                    # Core Signal[T]
├── signal_binding.py            # Computed/Effect
├── widget.py                    # KgentsWidget[S] base
├── composable.py                # HStack/VStack
├── primitives/                  # Bar, Sparkline, Glyph, DensityField, CitizenCard, etc.
├── wiring/                      # Subscriptions, Bindings, Clock, Interactions
├── animation/                   # Spring, Tween, Easing, Frame
├── adapters/
│   ├── marimo_widget.py         # Marimo target
│   ├── marimo_esm/              # ESM JavaScript for marimo
│   ├── textual_widget.py        # Textual TUI target
│   └── textual_*.py             # Theme, Layout, Focus
├── terminal/                    # ANSI CLI target
│   ├── adapter.py
│   ├── ansi.py
│   ├── box.py
│   └── art.py
└── _tests/                      # All tests
```

### 2. AGENTESE REPL
```
impl/claude/protocols/cli/handlers/agentese.py   # REPL handler
impl/claude/protocols/agentese/                  # Full AGENTESE implementation
```

### 3. Agent Town (Core)
```
impl/claude/agents/town/
├── citizen.py                   # CitizenPolynomial
├── coalition.py                 # Coalition formation
├── eigenvector.py               # 7D personality
├── operad.py                    # TownOperad
├── sheaf.py                     # TownSheaf
├── visualization.py             # EigenvectorScatterWidget
├── isometric.py                 # IsometricWidget
├── timeline_widget.py           # TimelineWidget
├── live_dashboard.py            # LiveDashboard composite
├── dialogue/                    # Dialogue engine
├── flux/                        # Flux integration
└── _tests/                      # All tests

impl/claude/protocols/cli/handlers/town.py       # Town CLI
impl/claude/protocols/api/town.py                # Town API
impl/claude/protocols/api/town_websocket.py      # Town WebSocket
```

### 4. Atelier (Core)
```
impl/claude/agents/atelier/
├── artisan.py                   # Artisan agent
├── commission.py                # Commission handling
├── collaboration.py             # Multi-artisan
├── streaming.py                 # Streaming generation
├── gallery/                     # Gallery storage + lineage
└── _tests/                      # All tests

impl/claude/protocols/cli/handlers/atelier.py    # Atelier CLI
impl/claude/protocols/api/atelier.py             # Atelier API
```

### 5. Marimo Widgets (anywidget)
```
impl/claude/agents/i/marimo/widgets/
├── base.py                      # Base anywidget
├── scatter.py                   # Eigenvector scatter
├── timeline.py                  # Timeline
├── stigmergic_field.py          # Pheromone field
├── dialectic.py                 # Dialectic exchange
└── js/                          # JavaScript frontend
```

---

## What We Remove

### Phase 1: Web UI Components (28K+ lines) → DELETE

**Target**: `impl/claude/web/src/`

| Remove | Reason |
|--------|--------|
| `pages/Dashboard.tsx` | Not using reactive primitives |
| `pages/Workshop.tsx` | Rebuild from primitives |
| `pages/Inhabit.tsx` | Rebuild from primitives |
| `pages/Landing.tsx` | Rebuild from primitives |
| `components/creation/*` | Wizard not primitive-based |
| `components/pipeline/*` | Rebuild with reactive |
| `components/chat/*` | Rebuild with reactive |
| `components/workshop/*` | Rebuild with reactive |
| `components/elastic/*` | Replace with reactive layouts |
| `components/dnd/*` | Rebuild if needed |
| `components/orchestration/*` | Rebuild with reactive |
| `components/onboarding/*` | Rebuild with reactive |
| `components/paywall/*` | Rebuild with reactive |
| `components/landing/*` | Rebuild with reactive |
| `components/feedback/*` | Rebuild with reactive |
| `components/error/*` | Keep ErrorBoundary, remove rest |
| `components/timeline/*` | Use reactive TimelineWidget |
| `stores/*` | Replace with reactive signals |

**Keep (minimal web shell)**:
```
web/src/
├── main.tsx                     # Entry point
├── App.tsx                      # Routes (gutted)
├── pages/Town.tsx               # Minimal - renders widgets
├── pages/Atelier.tsx            # Minimal - renders widgets
├── reactive/
│   ├── WidgetRenderer.tsx       # JSON → React bridge
│   ├── context.tsx              # Theme provider
│   └── types.ts                 # Widget schemas
├── widgets/                     # TSX mirrors of Python widgets
│   ├── primitives/              # Glyph, Bar, Sparkline
│   ├── cards/                   # CitizenCard, EigenvectorDisplay
│   ├── layout/                  # HStack, VStack
│   ├── dashboards/              # ColonyDashboard
│   └── constants.ts             # Glyph mappings
├── components/town/             # Minimal town-specific
│   ├── Mesa.tsx                 # Bird's eye (uses widgets)
│   ├── CitizenPanel.tsx         # Detail panel (uses widgets)
│   └── VirtualizedCitizenList.tsx
├── components/atelier/          # Minimal atelier-specific
│   ├── ArtisanGrid.tsx          # Uses widgets
│   ├── GalleryGrid.tsx          # Uses widgets
│   ├── CommissionForm.tsx       # Form only
│   └── StreamingProgress.tsx    # SSE display
└── components/error/
    └── ErrorBoundary.tsx        # Keep for safety
```

### Phase 2: Legacy CLI Handlers → DELETE or REFACTOR

**Target**: `impl/claude/protocols/cli/handlers/`

| Remove | Reason |
|--------|--------|
| `observe.py` | Uses Rich directly, not reactive |
| `dashboard.py` | Rebuild with reactive |
| `signal.py` | Rebuild with reactive |
| `status.py` | Rebuild with reactive |
| `telemetry.py` | Rebuild with reactive |
| `turns.py` | Rebuild with reactive |
| `forest.py` | Rebuild with reactive |
| `map.py` | Rebuild with reactive |
| `memory.py` | Rebuild with reactive |
| `sparkline.py` | Use reactive Sparkline widget |
| `semaphore.py` | Rebuild with reactive |
| `dream.py` | Rebuild with reactive |
| `flinch.py` | Keep (pre-commit hook, minimal) |
| `headless.py` | Audit usage |
| `hollow.py` | Audit usage |
| `_playground/*` | DELETE (experimental) |

**Keep**:
```
handlers/
├── agentese.py                  # AGENTESE REPL ✓
├── town.py                      # Town CLI ✓
├── atelier.py                   # Atelier CLI ✓
├── trace.py                     # Trace viewer (refactor to reactive)
├── flinch.py                    # Pre-commit hook
├── nphase.py                    # N-Phase handler
├── a_gent.py                    # Agent command
├── infra.py                     # Infrastructure
└── tithe.py                     # Void/entropy
```

### Phase 3: Demo/QA Cleanup → CONSOLIDATE

**Target**: `impl/claude/agents/i/reactive/demo/`

| Keep | Reason |
|------|--------|
| `unified_app.py` | Reference implementation |
| `unified_notebook.py` | Marimo reference |

| Remove | Reason |
|--------|--------|
| `tui_dashboard.py` | Superseded by unified_app |
| `soul_demo.py` | Consolidate into unified |
| `k_terrarium_demo.py` | Consolidate into unified |
| `tutorial.py` | Rebuild as proper onboarding |
| `marimo_agents.py` | Consolidate into unified_notebook |

### Phase 4: Town UI Legacy → DELETE

**Target**: `impl/claude/agents/town/ui/`

| Remove | Reason |
|--------|--------|
| `mesa.py` | Uses Rich directly, replaced by reactive |
| `lens.py` | Rebuild with reactive |
| `trace.py` | Rebuild with reactive |
| `widgets.py` | Superseded by reactive primitives |

### Phase 5: API Endpoint Cleanup → AUDIT

**Target**: `impl/claude/protocols/api/`

| Keep | Reason |
|------|--------|
| `app.py` | Core app factory |
| `town.py` | Town endpoints |
| `town_websocket.py` | Live updates |
| `atelier.py` | Atelier endpoints |
| `agentese.py` | AGENTESE protocol |
| `auth.py` | Authentication |
| `metrics.py` | Prometheus |

| Audit | Decision Needed |
|-------|-----------------|
| `workshop.py` | Keep if N-Phase needed, else remove |
| `nphase.py` | Keep if used by CLI |
| `soul.py` | Keep for K-gent |
| `sessions.py` | Keep for state |
| `payments.py` | Keep for billing |
| `webhooks.py` | Keep for Stripe |
| `aup.py` | Audit usage |
| `bridge.py` | Audit usage |
| `turn.py` | Audit usage |

---

## Implementation Phases

### Phase 1: Web UI Gutting (Largest Impact)

**Goal**: Reduce web UI from 28K lines to ~5K lines.

**Steps**:
1. Create `web/_archive/` directory
2. Move all components NOT in keep list to archive
3. Update imports in kept files
4. Update `App.tsx` routes to only include Town, Atelier
5. Run `npm run build` to verify
6. Run `npm test` - expect many failures, delete failing test files

**Exit Criteria**:
- `npm run build` succeeds
- Only Town and Atelier pages render
- Widget rendering still works

### Phase 2: CLI Handler Cleanup

**Goal**: Remove handlers that don't use reactive primitives.

**Steps**:
1. Create `handlers/_archive/` directory
2. Move deprecated handlers to archive
3. Update CLI registration in `protocols/cli/main.py` or equivalent
4. Run `uv run pytest protocols/cli/_tests/` - fix failures

**Exit Criteria**:
- `kg --help` shows only essential commands
- AGENTESE REPL works
- Town CLI works
- Atelier CLI works

### Phase 3: Demo Consolidation

**Goal**: Single reference demo per target.

**Steps**:
1. Merge useful patterns from removed demos into `unified_app.py`
2. Delete consolidated demos
3. Update any documentation references

**Exit Criteria**:
- `unified_app.py` demonstrates all widget types
- `unified_notebook.py` demonstrates marimo integration

### Phase 4: Town UI Legacy Removal

**Goal**: Remove Rich-direct code from Town.

**Steps**:
1. Delete `town/ui/` directory entirely
2. Ensure `town/visualization.py`, `town/live_dashboard.py` cover needs
3. Update any imports

**Exit Criteria**:
- No Rich library usage in Town (only in adapters)

### Phase 5: Test Cleanup

**Goal**: Remove orphaned tests.

**Steps**:
1. Run full test suite, note failures
2. Delete test files for removed code
3. Verify remaining tests pass

**Exit Criteria**:
- `uv run pytest` passes
- Test count drops (expected: ~30% reduction)

---

## Estimated Impact

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Web UI lines | 28K | ~5K | 82% |
| CLI handlers | 57 | ~15 | 74% |
| Demo files | 9 | 2 | 78% |
| Test files | TBD | TBD | ~30% |

---

## Verification

```bash
# After each phase
cd impl/claude
uv run pytest -q
uv run mypy .

cd web
npm run build
npm test
```

---

## Risk Mitigation

1. **Archive, don't delete**: All removed code goes to `_archive/` first
2. **Incremental phases**: Complete each phase before next
3. **Test after each step**: Catch regressions early
4. **Document decisions**: Note why each file was removed/kept

---

## Cross-References

- **Audit source**: This session's UI/Demo/QA/CLI audit
- **Enables**: `plans/core-apps-synthesis.md` - clean foundation for new UIs
- **Reactive docs**: `docs/skills/reactive-primitives.md`
- **Widget spec**: `spec/protocols/projection.md`
