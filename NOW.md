# NOW: The Living Document

> *"What's happening right now?"*

**Last Updated**: 2025-12-23 (Evening)
**Session**: Hardening Phase

---

## FIRST: Get Task-Relevant Gotchas

```bash
kg docs hydrate "<your task>"
```

This surfaces critical gotchas, likely files, and voice anchors for YOUR specific task.
Don't skip this—the gotchas you don't read are the bugs you will write.

---

## The Greater Arc: Burn → Build → Harden

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: THE EXTINCTION (Dec 21)                                           │
│  ─────────────────────────────────                                          │
│  67K lines archived. Town, Park, Gestalt, Coalition, Muse, Gardener gone.   │
│  Focus narrowed: Brain (100%), Witness (98%), Atelier (75%), Liminal (50%)  │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: THE REBUILDING (Dec 21-22)                                        │
│  ───────────────────────────────────                                        │
│  • Hypergraph Emacs: Six-mode modal editor for conceptual navigation        │
│  • WitnessedGraph: Evidence-carrying edges with visual confidence           │
│  • Inbound Sovereignty: External data ingestion with witnessing             │
│  • Living Spec: Evidence-as-Marks unification, ledger UI                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: THE HARDENING (Dec 23) ← YOU ARE HERE                             │
│  ──────────────────────────────────                                         │
│  • Dead Code Audit: ~14K more lines removed (0134babe)                      │
│  • AD-016: Fail-fast AGENTESE resolution (0d93ea6c)                         │
│  • AD-015 Radical Unification: LedgerCache → ProxyHandleStore (uncommitted) │
│  • Edit→Witness→Graph→Visual loop closed (90f5d23d)                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Current Focus

**HARDENING**: Infrastructure robustness before feature expansion

*"One truth. One store."*

---

## What's Happening Now

### Today's Commits (Dec 23)

| Commit | What | Arc |
|--------|------|-----|
| `a4a0ad5c` | Sort imports in garden.py | Cleanup |
| `0134babe` | **Dead code audit: ~14K lines removed** | HARDENING |
| `90f5d23d` | **Close Edit→Witness→Graph→Visual loop** | BUILDING |
| `0d93ea6c` | **AD-016 fail-fast resolution** | HARDENING |
| `93be486c` | Proper JSON output for BasicRendering | Cleanup |
| `87bc75be` | Hypergraph Phase 2: ContextNode.follow() | BUILDING |

### Uncommitted Work

**AD-015 Radical Unification** (just completed):
- `LedgerCache` class DELETED (~60 lines)
- `ensure_scanned()` → `proxy_store.get_or_raise(SourceType.SPEC_CORPUS)`
- `analyze_now()` → `proxy_store.compute()` with reactive invalidation
- 98 tests passing, mypy clean

### Hypergraph Emacs Status

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HYPERGRAPH EMACS                                                           │
│  ═══════════════════════════════════════════════════════════════════════════│
│  MODES:    NORMAL │ INSERT │ EDGE │ VISUAL │ COMMAND │ WITNESS              │
│  NAV:      gh/gl (parent/child) │ gj/gk (siblings) │ gd/gr/gt (def/refs/test)│
│  STATUS:   ✅ Core working │ ⏳ Portal ops │ ⏳ K-Block commit              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Active Plans (After 2025-12-23 Archive)

**7 archived** (3 complete, 4 superseded) → **21 active plans**

### Tier 1: In-Flight / Ready

| Plan | Status | Next |
|------|--------|------|
| `hypergraph-emacs.md` | Phase 1-4 ✅ | E2E testing, polish |
| `_membrane.md` | Foundation ✅ | Polish, keyboard shortcuts |
| `SPECGRAPH-ASHC-SELF-HOSTING.md` | Phase 2 active | K-Block + Interactive Text |
| `_inbound-sovereignty.md` | Session 1-3 ✅ | Polish, edge cases |

**WitnessedGraph Integration**: Edges now carry evidence (confidence, origin, markId). Edge gutters show confidence visually.

### Tier 2: Ready to Start

| Plan | Sessions | Priority |
|------|----------|----------|
| `witness-fusion-ux-implementation.md` | 5-7 | HIGH |
| `witness-assurance-protocol.md` | 8-10 | HIGH |
| `dawn-phase-4-kickoff.md` | 2-3 hrs | QUICK WIN |
| `stark-biome-enforcement.md` | 1 hr | QUICK WIN |

### Tier 3: Planning / Design

| Plan | Notes |
|------|-------|
| `witness-fusion-ux-design.md` | Design spec complete |
| `witness-assurance-ui.md` | UX patterns defined |
| `_k-block-implementation.md` | Phased plan ready |
| `SYNTHESIS-UI.md` | Vision doc |

### Tier 4: Backlog

| Plan | Notes |
|------|-------|
| `stark-biome-refactor.md` | Token system ready |
| `git-archaeology-backfill.md` | Proposed |
| `memory-first-docs-execution.md` | Phase 2B pending |
| `visual-trail-graph-fullstack.md` | Session 2 done |
| `technical-debt-remediation.md` | 183 mypy errors |

---

## Crown Jewel Status (Post-Extinction)

| Jewel | Status | Tests | Evidence |
|-------|--------|-------|----------|
| **Brain** | 100% | 200+ | TeachingCrystal, spatial cathedral |
| **Witness** | 98% | 678 | Marks, crystals, streaming, promotion |
| **Atelier** | 75% | — | Design forge, creative patterns |
| **Liminal** | 50% | — | Transition protocols |

---

## Session Entry Points

**Quick wins (< 3 hrs)**:
```bash
# Dawn Phase 4 — j/k nav, copy confirmation, add modal
cat plans/dawn-phase-4-kickoff.md | head -50

# Stark Biome enforcement — ESLint rule
cat plans/stark-biome-enforcement.md
```

**Medium investment (1-2 sessions)**:
```bash
# Witness Fusion UX — Start building components
cat plans/witness-fusion-ux-implementation.md

# Inbound Sovereignty Session 3
cat plans/_inbound-sovereignty.md
```

**Major arc (multi-session)**:
```bash
# Hypergraph Emacs Phase 4-5
cat plans/hypergraph-emacs.md

# Witness Assurance Protocol
cat plans/witness-assurance-protocol.md
```

---

## Verification

```bash
# Backend quality gate
cd impl/claude && uv run pytest -q && uv run mypy . 2>&1 | tail -5

# Frontend quality gate
cd impl/claude/web && npm run typecheck && npm run lint 2>&1 | tail -5

# Active plan count
ls -1 plans/*.md | grep -v "^plans/_" | grep -v README | wc -l
```

---

*"The proof IS the decision. The mark IS the witness."*
