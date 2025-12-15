# Chief of Staff Reconciliation: 2025-12-14

## Forest Audit

| Metric | Before | After |
|--------|--------|-------|
| Test count | 15,978 | 15,998 |
| Active trees | 37 | 37 |
| Dormant trees | 19 | 19 |
| Blocked trees | 0 | 0 |
| Archive candidates | unstated | 8+ identified |

## Quality Issues Fixed

**Mypy errors resolved: 16**
- 7 unused `type: ignore[misc]` comments in `protocols/api/*.py`
- 3 comparison-overlap type ignores added in test file
- 6 additional cleanup in `protocols/api/metrics.py` and `webhooks.py`

**Files modified:**
- `protocols/api/metering.py`
- `protocols/api/sessions.py`
- `protocols/api/soul.py`
- `protocols/api/agentese.py`
- `protocols/api/app.py`
- `protocols/api/webhooks.py`
- `protocols/api/metrics.py`
- `protocols/api/_tests/test_saas_integration.py`

## New Protocol: Aggressive Archiving

**Added to three N-Phase skills (QA, TEST, REFLECT):**

### docs/skills/n-phase-cycle/qa.md
- Added "Documentation Hygiene (Archiving Gate)" section
- QA checklist now includes archive/spec-promotion candidates

### docs/skills/n-phase-cycle/test.md
- Added "Test-Doc Reconciliation" section
- Tests that pass should trigger plan archival

### docs/skills/n-phase-cycle/reflect.md
- Added "Aggressive Archiving Protocol" section
- Mandatory archiving checklist for every REFLECT phase
- Zombie detection criteria: >14 days old, <25% progress, no dependents
- Archive file format template

### docs/skills/n-phase-cycle/README.md
- Updated from "Six Properties" to "Seven Properties"
- Added: "7. Archiving-First — Plans are scaffolding; QA/TEST/REFLECT gates must archive or upgrade"

### plans/principles.md
- Added "Aggressive Archiving (The Breathing Forest)" section
- Gate-specific archiving requirements (QA, TEST, REFLECT)
- Three paths: Archive, Upgrade, Retain

## Archive Candidates Identified

| Plan | Status | Issue |
|------|--------|-------|
| plans/architecture | Active 0% | Header-only, merge to crown-jewel-next |
| plans/soul-interface | Active 0% | Superseded by agents/k-gent |
| ideas/impl/* (11 files) | Active 0% | Brainstorm outputs, not plans |

**Already removed (good):**
- plans/creative-exploration-strategy.md
- plans/ideas-consolidation.md
- plans/n-phase-accursed-share-completion.md
- plans/self/memory.md
- plans/self/memory-phase5-substrate.md
- plans/triad-deep-integration.md

## _forest.md Updates

- Added "Archive Candidates" section with specific recommendations
- Updated Forest Metrics to include test count (15,998)
- Added archive candidate count metric

## Learnings (for meta.md if worthy)

```
2025-12-14  Aggressive archiving: QA/TEST/REFLECT gates must audit plans for archive/upgrade/retain
2025-12-14  Zombie plan criteria: >14 days, <25% progress, no dependents
```

## Archive Actions Executed (Human Approved)

Per human direction:

| Plan | Action | Result |
|------|--------|--------|
| plans/architecture.md | DELETE | Redundant with docs/architecture-overview.md |
| plans/soul-interface.md | ARCHIVE | → plans/_archive/2025-12-14-soul-interface.md |
| ideas/impl/* (11 files) | RECLASSIFY | → docs/ideas-synthesis/ (reference material) |

**Forest shrunk by 13 entries** (2 plans archived/deleted + 11 reclassified)

## Files Changed

- `git rm plans/architecture.md`
- `git rm plans/soul-interface.md` → archived to plans/_archive/
- `git mv plans/ideas/impl/*.md docs/ideas-synthesis/`
- Created `docs/ideas-synthesis/README.md`
- Updated `plans/_forest.md` with new metrics and archive actions

## What's Next

1. Continue with Agent Town / AGENTESE REPL crown jewels
2. Reference `docs/ideas-synthesis/` for implementation ideas

---

## Update: Evening Reconciliation

### Test Count Re-Verified
| Source | Was | Now |
|--------|-----|-----|
| HYDRATE.md | 16,720+ | 16,345 (actual) |
| _forest.md | 16,092 | 16,345 |
| pytest collect | — | 16,345 |

### Wave 4 CLI Handlers Mypy Fixes

Fixed 15 type annotation errors in new CLI handlers:
- `tension.py`: TypedDict for templates, dict type params
- `surprise_me.py`: dict type params
- `sparkline.py`: dict type params
- `project.py`: dict type params
- `oblique.py`: dict type params, variable shadowing
- `constrain.py`: `result.output.responses` fix
- `yes_and.py`: `result.output.responses` fix
- `why.py`: DialogueMode import, dict type params
- `test_wave4_joy.py`: MonkeyPatch annotation
- `test_repl.py`: Nullable docstring guard

### Progress Drift Corrected
| Plan | Was | Now |
|------|-----|-----|
| agentese-repl | 65-75% | 85% (Waves 1-5 complete) |
| saas | 95% | 98% (Phase 9 complete) |

### Files Updated
- `HYDRATE.md` - Test count, progress percentages
- `plans/_forest.md` - Test count, REPL progress, epilogue ref
- 9 CLI handler files - Type annotations

---

⟂[DETACH:cycle_complete] Chief reconciliation + archiving complete. Forest breathing.
