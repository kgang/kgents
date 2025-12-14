---
path: agents/forest-keeper
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/forest, plans/_forest]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track F: Forest Protocol Integration
  See: prompts/agentese-continuation.md
  Related: plans/meta/forest-agentese-n-phase.md
---

# Forest Keeper

> *"The forest is wiser than any single tree. To invoke is to tend."*

**Track**: F (Forest Protocol Integration)
**AGENTESE Context**: `concept.forest.*`, `time.forest.*`, `void.forest.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Heterarchical (no fixed plan hierarchy), Generative (plans from seeds), Accursed Share (dormant plan entropy)

---

## Purpose

The Forest Keeper wires AGENTESE into Forest Protocol operations—making plan files accessible as AGENTESE paths. Plan status projects via `manifest`, updates via `refine`, epilogues stream via `witness`, and dormant plans surface via `sip`.

---

## Expertise Required

- Forest Protocol (`plans/_forest.md`, plan file structure)
- AGENTESE context resolver patterns
- Epilogue/session notes management
- Dormant plan revival strategies

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| F1 | `concept.forest.manifest` → plan status projection | DEVELOP | 0.06 | Pending |
| F2 | `concept.forest.refine` → plan update morphism | DEVELOP | 0.07 | Pending |
| F3 | `time.forest.witness` → epilogue stream | IMPLEMENT | 0.06 | Pending |
| F4 | `void.forest.sip` → dormant plan picker | IMPLEMENT | 0.08 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `impl/claude/protocols/agentese/contexts/forest.py` | Forest context resolver |
| `plans/_forest.md` | Integration hooks |
| `plans/_epilogues/` | Epilogue generation via AGENTESE |

---

## Handle Mapping

| Forest Operation | AGENTESE Path |
|------------------|---------------|
| `forest_status()` | `concept.forest.manifest` |
| `forest_update()` | `concept.forest.refine` |
| Epilogue stream | `time.forest.witness` |
| Dormant picker | `void.forest.sip` |
| Plan scaffold | `self.forest.define` |

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `concept.forest.manifest` | Project plan status | ForestStatus |
| `concept.forest.refine` | Update plan (progress, notes) | RefineResult |
| `concept.forest.define` | Create new plan from seed | PlanScaffold |
| `time.forest.witness` | Stream epilogue history | Iterator[Epilogue] |
| `void.forest.sip` | Pick dormant plan for revival | PlanHandle |

---

## Observer Roles

| Role | Affordances |
|------|-------------|
| `ops` | manifest, refine, define, witness, sip |
| `meta` | manifest, witness, refine |
| `guest` | manifest, witness |

---

## Success Criteria

1. Plan status accessible via `concept.forest.manifest`
2. Plan updates work via `concept.forest.refine` with session_notes
3. Epilogues stream correctly via `time.forest.witness`
4. Dormant plans surface via `void.forest.sip` with entropy draw
5. New plans scaffold via `self.forest.define`

---

## Dependencies

- **Receives from**: Syntax Architect (parsed paths), Entropy Steward (entropy for sip)
- **Provides to**: Integration Weaver (forest state), Liturgist (plan-based workflows)

---

*"Tend the forest. The forest tends you."*
