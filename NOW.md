# NOW: The Living Document

> *"What's happening right now?"*

**Last Updated**: 2025-12-23
**Session**: Post-Archive Clarity

---

## Current Focus

**HYPERGRAPH EMACS + MEMBRANE**: The Conceptual Editor is Live

*"The file is a lie. There is only the graph."*

---

## What's Happening Now

### The Arc: From Documentation to Embodiment

**67K lines burned. The canvas is blank. Hypergraph Emacs emerged.**

We're past the documentation phase. The frontend is no longer *about* agents—it IS the agent's surface. Two deliverables crystallized:

1. **Hypergraph Emacs** (Phase 1-3 Complete) — Six-mode modal editor for conceptual navigation
2. **The Membrane** (Foundation Complete) — Co-thinking surface with Focus/Witness/Dialogue

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
| `_inbound-sovereignty.md` | Session 1+2 ✅ | Session 3: Sync Protocol |

**Phase 4 Complete**: WitnessedGraph integration — edges now carry evidence (confidence, origin, markId). Edge gutters show confidence visually.

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

## Gotchas for Next Claude

- ⚠️ Hypergraph Emacs Portal ops (zo/zc) not yet implemented
- ⚠️ 183 mypy errors (manifest signature mismatches—known debt)
- ⚠️ Two PortalToken implementations exist (context vs file_operad)
- ✅ `ContextNode.follow()` now wired to AGENTESE resolvers (87bc75be)
- ✅ K-Block `:w [message]` and `:q!` fully wired (Phase 3)
- ✅ `useGraphNode` migrated to WitnessedGraph API — edges carry evidence (mark-284)

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
