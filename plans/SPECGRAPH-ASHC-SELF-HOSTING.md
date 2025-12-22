# MASTER PLAN: Self-Hosting Spec Backfill

> *"The spec is not description—it is generative. The webapp IS the self-analysis surface."*

**Date**: 2025-12-22
**Status**: Active — Phase 2 In Progress
**Vision**: All specs navigable in the webapp; kgents working on itself from inside

---

## The Unified Vision

Five interconnected systems enable **self-hosting spec analysis**:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SELF-HOSTING ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  SPECGRAPH  │◄────►│    ASHC     │◄────►│  K-BLOCK    │◄────►│  MEMBRANE   │ │
│  │ (193 specs) │      │ (evidence)  │      │ (editing)   │      │ (frontend)  │ │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘ │
│         │                    │                    │                    │        │
│         └────────────────────┼────────────────────┼────────────────────┘        │
│                              ▼                    ▼                              │
│                    ┌─────────────────────────────────────┐                      │
│                    │         INTERACTIVE TEXT            │                      │
│                    │   (specs become live interfaces)    │                      │
│                    └─────────────────────────────────────┘                      │
│                              │                                                   │
│                              ▼                                                   │
│                    ┌─────────────────────────────────────┐                      │
│                    │       PORTAL TOKENS (UX layer)      │                      │
│                    │    Inline expansion, navigation     │                      │
│                    └─────────────────────────────────────┘                      │
│                              │                                                   │
│                              ▼                                                   │
│                    ┌─────────────────────────────────────┐                      │
│                    │     TYPED-HYPERGRAPH (conceptual)   │                      │
│                    │   Context as navigable graph        │                      │
│                    └─────────────────────────────────────┘                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## System Status Summary

| System | Spec | Implementation | Tests | Frontend | Status |
|--------|------|----------------|-------|----------|--------|
| **SpecGraph** | ✅ `typed-hypergraph.md` | ✅ `protocols/specgraph/` | 81 | ✅ SpecView.tsx | **90%** |
| **ASHC** | ✅ `ASHC-agentic-self-hosting.md` | ✅ `protocols/ashc/` | 276 | ❌ | **80%** |
| **K-Block** | ✅ `k-block.md` (1050 lines) | 🟡 `services/k_block/` | 46 | 🟡 useKBlock.ts | **45%** |
| **Interactive Text** | ✅ `interactive-text.md` | ✅ `services/interactive_text/` | 140+ | ❌ | **70%** |
| **Portal Tokens** | ✅ `portal-token.md` | ✅ `protocols/file_operad/` | 125 | ✅ Portal.tsx | **85%** |
| **Membrane** | ✅ `membrane.md` | ✅ `web/src/membrane/` | — | ✅ 25 files | **80%** |
| **Derivation** | ✅ `derivation-framework.md` | ✅ `protocols/derivation/` | 306 | ❌ | **95%** |

**Total Backend Tests**: 368+ (SpecGraph + K-Block + Interactive Text)

---

## Phase Breakdown

### Phase 1: Foundation (COMPLETE) ✅

**What's Built:**

| Component | Status | Evidence |
|-----------|--------|----------|
| SpecGraph Parser | ✅ | `parser.py` — parses specs, discovers edges |
| SpecGraph Registry | ✅ | `registry.py` — 193 specs registered |
| SpecGraph Types | ✅ | `types.py` — SpecNode, SpecEdge, DerivationTier |
| Hyperedge Resolvers | ✅ | 21 resolvers (imports, calls, tests, implements...) |
| Portal Token Core | ✅ | `portal.py`, `source_portals.py` — 125 tests |
| Exploration Harness | ✅ | Trail, Budget, Loops, Evidence — 110 tests |
| Membrane Foundation | ✅ | 25 files in `web/src/membrane/` |

**Key Deliverables:**
- `kg context navigate tests` — Follow hyperedges via CLI
- `kg portal <file>` — Show portals for any file
- Membrane three-pane layout working

---

### Phase 2: Spec Backfill (IN PROGRESS) 🟡

**Goal**: Get all 193 specs visible and navigable in the webapp

#### 2.1 SpecView Integration ✅

| Task | Status |
|------|--------|
| SpecView.tsx | ✅ Shows spec content with tier badges |
| Confidence bars | ✅ Derivation confidence visualization |
| Edge portals | ✅ Clickable relationships |
| useSpecNavigation.ts | ✅ Navigation state management |

#### 2.2 Derivation Bridge (TO DO)

| Task | Status | Spec |
|------|--------|------|
| Link specs to derivations | ❌ | `derivation-framework.md` |
| Show confidence from ASHC evidence | ❌ | `ASHC-agentic-self-hosting.md` |
| Tier visualization in SpecView | 🟡 | Uses static tiers |
| Confidence updates from impl tests | ❌ | — |

#### 2.3 Interactive Text Integration (PARTIAL)

| Task | Status | Location |
|------|--------|----------|
| Token parser | ✅ | `services/interactive_text/parser.py` |
| Six token types | ✅ | `tokens/` directory |
| CLI projector | ✅ | `projectors/cli.py` |
| Web projector | ✅ | `projectors/web.py` |
| AGENTESE node | ✅ | `node.py` |
| **Wire to SpecView** | ❌ | Needs integration |

#### 2.4 K-Block for Spec Editing (IN PROGRESS)

| Task | Status | Plan |
|------|--------|------|
| Core K-Block | ✅ | Phase 0 complete (monad laws verified) |
| Views (Prose/Graph/Code/Diff/Outline) | ✅ | All 5 views implemented |
| Sheaf coherence | ✅ | View sync working |
| Cosmos persistence | ❌ | Phase 2 of k-block plan |
| Witness integration | ❌ | Phase 3 of k-block plan |
| Web UI | 🟡 | `useKBlock.ts` exists |

---

### Phase 3: Self-Hosting Loop (PLANNED)

**Goal**: Claude working on kgents from inside kgents

#### 3.1 Navigation Flow

```
Claude opens spec in SpecView
    ↓
Expands [implements] portal → sees implementation files
    ↓
Expands [tests] portal → sees test coverage
    ↓
Opens K-Block for spec editing
    ↓
Makes changes → Views sync
    ↓
Saves → Witness marks decision
    ↓
Derivation confidence updates
```

#### 3.2 Required Integrations

| Integration | From | To | Status |
|-------------|------|-----|--------|
| SpecView → K-Block | Click "Edit" | Open in K-Block | ❌ |
| K-Block → Witness | On save | Mark decision | ❌ |
| Witness → Derivation | On mark | Update confidence | ❌ |
| Derivation → SpecView | On update | Refresh display | ❌ |
| SpecGraph → ASHC | On spec change | Run evidence cycle | ❌ |

#### 3.3 CLI Integration

```bash
# These commands should work together
kg context focus spec/protocols/k-block.md    # Navigate to spec
kg portal spec/protocols/k-block.md implements # Show implementation
kg kblock create spec/protocols/k-block.md    # Open for editing
kg kblock save --reasoning "Added new law"    # Save with witness
kg derivation show k-block                     # Check confidence
```

---

### Phase 4: ASHC Evidence Loop (FUTURE)

**Goal**: Implementation success updates spec confidence

| Task | Spec | Status |
|------|------|--------|
| Spec → Implementation confidence | `ASHC-agentic-self-hosting.md` | ❌ |
| Test pass rate → Evidence | `derivation-framework.md` | ❌ |
| Causal tracking | `ASHC-agentic-self-hosting.md` | ❌ |
| Stigmergic decay | `metabolic-development.md` | ❌ |

---

## Spec Architecture (The Graph)

```
                              PRINCIPLES (Bootstrap)
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         COMPOSITION            PRIMITIVES             AGENTESE
              │                      │                      │
              ▼                      ▼                      │
           OPERADS              FUNCTORS                    │
              │                      │                      │
              ├──────────────────────┘                      │
              ▼                                             ▼
            FLUX ◄──────────────────────────────── TYPED-HYPERGRAPH
              │                                             │
              │        ┌────────────────────────────────────┤
              │        ▼                                    ▼
              │   EXPLORATION-HARNESS              PORTAL-TOKEN
              │        │                                    │
              │        ▼                                    │
              │   DERIVATION ◄──────────────────────────────┤
              │        │                                    │
              │        ▼                                    ▼
              └───► WITNESS ◄───────────────────── INTERACTIVE-TEXT
                       │                                    │
                       ▼                                    ▼
                   K-BLOCK ◄────────────────────────── MEMBRANE
                       │
                       ▼
                   SPECGRAPH (we're here!)
```

---

## Existing Plans (Reference)

| Plan | Purpose | Status |
|------|---------|--------|
| `_bootstrap-specgraph.md` | Overall bootstrap vision | Reference |
| `_specgraph-inventory.md` | Spec catalog with edges | Reference |
| `_membrane.md` | Frontend transformation | Complete |
| `_k-block-implementation.md` | K-Block phases 0-9 | In Progress |
| `_membrane-execution.md` | Membrane execution details | Complete |

---

## Key Specs (Quick Reference)

| Spec | Path | Lines | Key Insight |
|------|------|-------|-------------|
| **K-Block** | `spec/protocols/k-block.md` | 1050 | Monadic isolation + hyperdimensional views |
| **Interactive Text** | `spec/protocols/interactive-text.md` | 660 | Six token types, specs ARE interfaces |
| **Portal Token** | `spec/protocols/portal-token.md` | 625 | Inline expansion, navigation IS expansion |
| **Typed-Hypergraph** | `spec/protocols/typed-hypergraph.md` | 430 | Context as navigable graph |
| **ASHC** | `spec/protocols/ASHC-agentic-self-hosting.md` | 650 | Empirical proof via evidence accumulation |
| **Derivation** | `spec/protocols/derivation-framework.md` | 2000 | Bayesian proof theory for agents |
| **Membrane** | `spec/surfaces/membrane.md` | — | Co-thinking surface |

---

## Next Actions

### Immediate (Next Session)

1. **Wire Interactive Text to SpecView**
   - `SpecView.tsx` should use `InteractiveTextService` for rendering
   - AGENTESE paths in specs become clickable
   - Task checkboxes become toggleable

2. **K-Block Edit Button**
   - Add "Edit in K-Block" button to SpecView
   - Wire `useKBlock.ts` to open spec for editing
   - Show isolation indicator

### Short Term (This Week)

3. **Derivation Visualization**
   - Show derivation DAG in SpecView
   - Link confidence to ASHC evidence
   - Add confidence refresh button

4. **Portal Tree in SpecView**
   - Expandable [implements], [tests], [extends] portals
   - Navigate to implementation files

### Medium Term (Next Week)

5. **K-Block Cosmos Persistence**
   - Implement append-only log
   - Time travel through spec versions
   - Wire to Witness

6. **Self-Hosting Demo**
   - Claude editing a spec via the webapp
   - Full loop: edit → save → witness → derivation update

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Specs in SpecGraph | 193 | 193 ✅ |
| Specs viewable in webapp | 193 | ~50 |
| Interactive tokens working | 6 | 6 ✅ |
| K-Block monad laws verified | 3 | 3 ✅ |
| K-Block views working | 5 | 5 ✅ |
| Portal expansion working | ✅ | ✅ |
| Self-hosting demo | — | ❌ |

---

## Philosophy

> *"The proof IS the decision. The mark IS the witness."*

This plan is itself an example of the system it describes:
- It's a **spec** (this document)
- That can be **navigated** (via SpecGraph)
- With **portals** to implementations
- That will be **edited** in K-Block
- With changes **witnessed**
- And confidence **updated** via ASHC

When we can edit this plan from inside the webapp, we've achieved self-hosting.

---

*Filed: 2025-12-22*
*Author: Kent + Claude (hydration fusion)*
