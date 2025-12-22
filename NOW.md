# NOW: The Living Document

> *"What's happening right now?"*

**Last Updated**: 2025-12-22
**Session**: RADICAL TRANSFORMATION — The Membrane

---

## Current Focus

**THE MEMBRANE: Stop Documenting Agents. Become the Agent.**

*"The proof IS the decision."*

**Decision**: `fuse-ccad81de` (2025-12-22)

---

## What's Happening Now

### RADICAL TRANSFORMATION: The Membrane

**67,330 lines burned. The canvas is blank.**

The old frontend was a documentation shell — browse AGENTESE paths, see polynomial diagrams, explore trails. It was *about* agents.

**The Membrane is different**: One surface that morphs based on context. Not navigation, not routes, not pages. A **co-thinking surface** where Kent and K-gent work together.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  THE MEMBRANE                                                           │
│  ═══════════════════════════════════════════════════════════════════════│
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │      FOCUS PANE             │  │       WITNESS STREAM            │  │
│  │  [Current working context]  │  │  • Decisions flow here          │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  DIALOGUE — Where Kent and K-gent think together                  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Plan**: `plans/_membrane.md`
**Spec**: `spec/surfaces/membrane.md`

---

### What Got Burned (2025-12-22)

| Category | Lines Deleted | Components |
|----------|---------------|------------|
| shell/ | ~15K | Terminal, NavigationTree, CommandPalette |
| witness/ | ~8K | MarkCard, MarkTimeline, garden/ |
| trail/ | ~6K | TrailGraph, ReasoningPanel, SuggestionPanel |
| brain/ | ~4K | Brain2D, CrystalTree, CaptureForm |
| polynomial/ | ~3K | PolynomialDiagram, MiniPolynomial |
| Others | ~31K | servo/, canvas/, portal/, docs/, categorical/ |
| **Total** | **67,330** | ~65% of web codebase |

**Preserved**: elastic/, joy/, genesis/, useDesignPolynomial, useAnimationCoordination

---

### Implementation Phases — COMPLETE ✅

| Phase | What | Status |
|-------|------|--------|
| **1** | Membrane Foundation — Membrane.tsx, FocusPane, WitnessStream, DialoguePane | ✅ |
| **2** | SpecGraph Integration — tier badges, confidence bars, edge portals | ✅ |
| **3** | Crystallization — crystallize() action flows to witness | ✅ |
| **4** | Polish — elastic modes, keyboard shortcuts (⌘1/2/3, Escape) | ✅ |

**25 files created in `impl/claude/web/src/membrane/`**

**Key Components:**
- `Membrane.tsx` — Root component with three-mode layout
- `useMembrane.ts` — State machine (mode, focus, dialogue, witness)
- `FocusPane.tsx` — Context-aware content (file/spec/concept views)
- `SpecView.tsx` — SpecGraph integration with edge portals
- `WitnessStream.tsx` — Real-time SSE event stream
- `DialoguePane.tsx` — Co-thinking interface with crystallize action

---

### Previous: Context Perception Phase 5 — COMPLETE ✅

| Phase | What It Means | Status |
|-------|---------------|--------|
| **5A** | Frontend portal experience | ✅ Complete |
| **5B** | Trail → Witness evidence | ✅ Complete |
| **5C** | Collaborative editing | ✅ Complete |
| **5D** | Integration | ✅ Complete |

**Phase 5D Delivered (2025-12-22):**
- `TrailPanel.tsx` — Side panel showing exploration trail with step visualization ✅
- `EvidenceBadge.tsx` — Computed evidence strength (weak → definitive) ✅
- Collaboration events wired to trail steps ✅
- Portal.tsx integrates all Phase 5 components ✅
- Presence indicators (collaboration status, typing indicators) ✅
- 40 Phase 5 + collaboration tests passing ✅

**Full Loop Works:** explore → expand portals → proposal overlays → accept/reject → trail updates → witness visible

**Status:** All major Context Perception features complete! 🎉

---

## Trail Protocol Status (2025-12-22)

| Component | Status | Tests |
|-----------|--------|-------|
| Postgres Persistence | ✅ | 20 |
| File Persistence | ✅ | 26 |
| Trail → Witness Bridge | ✅ | 28 |
| Fork/Merge | ✅ | 3 |
| Semantic Search (pgvector) | ✅ | — |
| **Visual Trail Graph** | ✅ **Complete** | 48+ |
| Concurrent Co-Exploration | ⏳ | — |

**Visual Trail Graph Progress:**
- ✅ Session 1: Branching Foundation (parent_index, tree layout, UI indicators)
- ✅ Session 2: Validation & Reasoning (world.repo.validate, fuzzy suggestions, hierarchical reasoning)
- ✅ Session 3: Intelligence (AI suggestions, zoom-detail, keyboard nav)
- ✅ Session 4: Integration & Polish (TrailGraph.tsx, ReasoningPanel, ExplorerPresence, SuggestionPanel)

**Session 3 Delivered (2025-12-22):**
- `get_embedder()` — SentenceTransformer provider (all-MiniLM-L6-v2, 384-dim, local)
- `self.trail.suggest` — AI-suggested connections with related trails, files, edges, prompts
- `ZoomLevel` type + zoom-dependent rendering in ContextNode
- `useTrailKeyboard` — Arrow keys navigate parent/child/siblings, b=branch, Escape=deselect
- `SuggestionPanel.tsx` — AI suggestions UI component with loading states

**Total:** 48+ tests | **Spec:** `spec/protocols/trail-protocol.md`

**Plan:** `plans/visual-trail-graph-fullstack.md`

---

## What Just Happened

### Context Perception Phase 4 Complete ✅

| Sub-Phase | What Got Built | Tests |
|-----------|---------------|-------|
| 4A: Frontend Polish | PresenceBadge.tsx, FileAnalyzer | 34 |
| 4B: Trail → Witness | trail_bridge.py, TRAIL_CAPTURED topic | 28 |
| 4C: Collaboration | collaboration.py (turn-taking, proposals) | 37 |

**Total Phase 4:** 99 new tests, 283 passing across context perception.

### Context Perception Phase 3: Trail Artifacts ✅

Completed Phase 3 of the Context Perception protocol:

| Component | Purpose | Tests |
|-----------|---------|-------|
| `Trail.as_outline()` | Render trail as readable outline | 3 |
| `Trail.share()` | Export with metadata and content hash | 2 |
| `Trail.from_dict()` | Reconstruct from shared data | 1 |
| `OutlineRenderer` | CLI/TUI/Web/LLM multi-surface rendering | 28 |
| Token parsing | Live AGENTESE path and evidence discovery | 6 |
| CLI commands | `kg context trail save/load/share` | 3 |

**Key Implementation:**
- `as_outline()` renders trail with step annotations and emoji markers
- `share()` adds version, format, content_hash, and evidence strength
- `_compute_evidence_strength()` computes weak/moderate/strong/definitive from trail diversity
- `OutlineRenderer` handles 5 surfaces with configurable fidelity
- `_parse_content_tokens()` discovers AGENTESE paths and evidence links on portal expand

**CLI Commands:**
```bash
kg context trail                    # Show navigation history
kg context trail save auth-bug      # Persist trail to ~/.kgents/trails/
kg context trail load auth-bug      # Resume saved trail
kg context trail share              # Export as shareable JSON
kg context trail share --file x.json
```

**Test Counts:**
- Context Perception: 184 tests
- Self Context (Trail): 47 tests
- **Total Phase 3 related: 231 tests** (exceeds 208+ target)

---

### Previous: Portal Token Phase 4: Source File Integration ✅

Completed the integration of portal tokens with real Python source files:

| Component | Purpose | Tests |
|-----------|---------|-------|
| `source_portals.py` | SourcePortalDiscovery, SourcePortalLink, SourcePortalToken | 26 |
| `portal.py` (CLI) | `kg portal <file>`, `kg portal expand`, `kg portal tree` | — |

**Key Implementation:**
- `SourcePortalLink.from_hyperedge()` — Bridge from ContextNode to PortalLink
- `SourcePortalDiscovery.discover_portals()` — Async discovery using hyperedge resolvers
- `build_source_portal_tree()` — Build navigable tree from source file

**CLI Commands:**
```bash
kg portal impl/claude/services/brain/core.py      # Show portals
kg portal expand core.py imports                   # Expand edge
kg portal tree core.py --expand-all               # Full tree
kg portal edges                                    # List edge types
```

**Total Portal Token Tests:** 125 (Phases 1-4)

### Previous: New Spec Protocols Created

| Protocol | Purpose | Key Insight |
|----------|---------|-------------|
| `typed-hypergraph.md` | Context as navigable graph | Hyperedges connect one node to MANY nodes |
| `portal-token.md` | Inline expansion UX | "You don't go to the doc. The doc comes to you." |
| `derivation-framework.md` | Bayesian proof theory for agents | Bootstrap = axioms, derived = theorems with confidence |
| `exploration-harness.md` | Safety layer for navigation | Budget, loops, trail-as-evidence |
| `file-operad.md` | Filesystem as meta-OS | Operads as `.op` markdown files at `~/.kgents/operads/` |

### Spec Cleanup (40 files, -433 lines net)

- **Removed F-gent/Forge references** — Consolidated, not a separate genus
- **Streamlined bootstrap.md** — Added concrete generating equations for all agent genera
- **Cleaned g-gents integration** — Removed F-gent patterns, kept P/J/L/W/T patterns
- **Fixed terminology drift** — "Domain" → "System", "Domain operads" → "Specialized operads"

### Exploration Harness Implementation

| File | Purpose | Lines |
|------|---------|-------|
| `types.py` | Trail, ContextNode, ContextGraph, Evidence, Claim, Observer | ~360 |
| `budget.py` | NavigationBudget + presets (quick/standard/thorough) | ~180 |
| `loops.py` | LoopDetector (exact/semantic/structural) | ~220 |
| `evidence.py` | TrailAsEvidence, EvidenceCollector, EvidenceScope | ~280 |
| `commitment.py` | ASHCCommitment (4 levels: tentative→definitive) | ~300 |
| `harness.py` | ExplorationHarness (main integration) | ~320 |

**Tests**: 19 passing | **Types**: mypy clean

### Key Design Insights

| Insight | Implementation |
|---------|----------------|
| Trail IS evidence | `TrailAsEvidence.to_evidence()` converts navigation to proof |
| Budget consumed immutably | `budget.consume()` returns new budget |
| Loop escalation | 1st: warn → 2nd: backtrack → 3rd: halt |
| Evidence strength computed | From trail diversity, not set manually |
| Commitment irreversible | Cannot downgrade from "strong" to "weak" |

---

## Session Status

---

## What's Next

**All major Context Perception features complete!** 🎉

| Completed | Evidence |
|-----------|----------|
| ✅ Visual Trail Graph | `TrailGraph.tsx` (421 lines), `ReasoningPanel.tsx`, `ExplorerPresence.tsx`, `SuggestionPanel.tsx` |
| ✅ pgvector Integration | Migration 007 with `VECTOR(1536)` + IVFFlat index |
| ✅ Wire Witness API | `handleWitness` in Portal.tsx → `createTrail()` API → navigates to trail view |
| ✅ Witness Dashboard TUI | `services/witness/tui/` — Textual TUI with vim nav, level filtering, copy-to-clipboard |

**Potential next directions:**
1. **E2E Tests** — Full integration tests for the trail → witness flow
2. **Concurrent Co-Exploration** — Multiple users exploring same context
3. **Semantic Search Polish** — Make `self.trail.search` sing with pgvector
4. **New feature** — What's calling to you?

---

## Gotchas for Next Claude

- ⚠️ Two PortalToken implementations: `protocols/context/outline.py::PortalToken` (outline model) and `protocols/file_operad/portal.py::PortalToken` (infrastructure). The bridge reconciles them.
- ⚠️ Trail.from_dict() needs Observer passed in for proper archetype
- ⚠️ CLI handler helper functions (_get_node, _get_observer, _run_async) are untyped — pre-existing mypy debt
- ⚠️ `ContextNode.follow()` returns empty list — needs AGENTESE wiring
- ⚠️ Observer archetype determines visible edges (phenomenological insight)

---

## Spec Architecture (Crystallizing)

```
DERIVATION FRAMEWORK              spec/protocols/derivation-framework.md
  Bootstrap axioms → derived agent confidence
        │
        ▼
TYPED-HYPERGRAPH (conceptual)     spec/protocols/typed-hypergraph.md
  Context as navigable hypergraph, not pre-composed lens
        │
        ├─────────────────────────┐
        ▼                         ▼
EXPLORATION HARNESS (safety)      FILE_OPERAD (storage)
  impl/claude/protocols/explore/  spec/protocols/file-operad.md
  Budget, loops, trail-as-proof   ~/.kgents/operads/*.op
        │
        ▼
PORTAL TOKEN (UX)                 spec/protocols/portal-token.md
  Inline expansion, meaning tokens
```

---

## Verification

```bash
# Test Context Perception Phase 3 (231 tests)
cd impl/claude && uv run pytest protocols/context/_tests/ protocols/agentese/contexts/_tests/test_self_context.py -q

# Test portal tokens
cd impl/claude && uv run pytest protocols/file_operad/_tests/test_source_portals.py -v

# Type check Phase 3 code
cd impl/claude && uv run mypy protocols/context/renderer.py protocols/context/portal_bridge.py protocols/agentese/contexts/self_context.py --ignore-missing-imports

# Quick import test
cd impl/claude && uv run python -c "from protocols.context import OutlineRenderer, render_for_llm; print('OK')"
```

---

*"The proof IS the decision. The mark IS the witness."*
