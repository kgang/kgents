---
path: meta/docs-renaissance
status: active
progress: 60
last_touched: 2025-12-20
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Comprehensive audit complete (263 files scanned).
  Day 1 quick fixes DONE: CLAUDE.md counts/dates, typos, test counts.
  E-gents removal DONE: Removed from 25+ files per Kent's directive.
  Broken skill refs DONE: Fixed Related Skills sections.
  Remaining: projection.md paths, R-gents reference.
phase_ledger:
  SENSE: complete
  ACT: in_progress
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.12
  returned: 0.03
---

# Docs Renaissance: The Great Cleanup

> *"The persona is a garden, not a museum."*

**AGENTESE Context**: `self.docs.*`
**Status**: Active (263 files audited, 141 issues found)
**Principles**: Curated, Generative
**Cross-refs**: `docs/skills/`, `spec/protocols/`, CLAUDE.md

---

## Core Insight

Documentation has accumulated organic drift: outdated counts, broken references, orphaned specs. This plan systematically restores hygiene without losing voice.

---

## Audit Summary (2025-12-20)

| Category | Files | Issues | Severity |
|----------|-------|--------|----------|
| docs/skills/ | 17 | 11 | Medium |
| spec/protocols/ | 46 | 12 | High |
| spec/agents/ + services/ | 10 | 3 | Low |
| Alphabetic specs | 80+ | 25 | High |
| Top-level docs | 12 | 8 | Medium |
| Cross-references | All | 141 | Mixed |

---

## Phase 1: Quick Wins (Day 1) ✅ COMPLETE

**Goal**: Fix obvious errors that can be done in minutes.

### 1.1 CLAUDE.md Corrections

| Line | Current | Fix |
|------|---------|-----|
| 53 | "13 skills" | "17 skills" |
| 168 | "17 production systems" | "20 production systems" |
| 246 | "THE 13 SKILLS" | "THE 17 SKILLS" |
| 254 | "2025-12-18" | "2025-12-20" |
| 327 | "Compiled: 2025-12-18" | "Compiled: 2025-12-20" |

### 1.2 Typo Fixes

| File | Line | Current | Fix |
|------|------|---------|-----|
| spec/c-gents/README.md | 78 | `../a-agents/` | `../a-gents/` |

### 1.3 Status Updates

| File | Line | Current | Fix |
|------|------|---------|-----|
| spec/services/witness.md | 6 | "(0 tests)" | "(32 tests)" |
| spec/services/muse.md | 6 | "(0 tests)" | "(2 tests)" |

**Exit Criteria**: All Day 1 fixes committed.

---

## Phase 2: Broken References (Week 1)

**Goal**: Fix broken internal links and missing files.

### 2.1 Missing Skill References

These skills are referenced but don't exist:

| Referenced File | Missing Skill | Action |
|-----------------|---------------|--------|
| agentese-path.md | handler-patterns.md | Remove reference or create |
| building-agent.md | flux-agent.md | Remove reference |
| building-agent.md | agent-observability.md | Remove reference |
| test-patterns.md | flux-agent.md | Remove reference |
| projection-target.md | projection-gallery.md | Remove reference |

### 2.2 Missing Protocol Specs

| Referenced In | Missing Spec | Action |
|---------------|--------------|--------|
| data-bus.md | synergy.md | Create or update reference |
| agentese.md | agentese-contract-protocol.md | Remove or create |

### 2.3 Wrong Paths

| File | Wrong Path | Correct Path |
|------|------------|--------------|
| spec/protocols/projection.md | `components/three/primitives/` | `widgets/primitives/` |

**Exit Criteria**: Zero broken internal links in high-traffic files.

---

## Phase 3: Orphaned Specs (Week 2)

**Goal**: Decide fate of referenced-but-missing agent specs.

### 3.1 E-gents (Critical Decision)

**Status**: Referenced in 5+ files but directory doesn't exist.

Referenced in:
- spec/t-gents/adversarial.md:521
- spec/b-gents/banker.md:275
- spec/f-gents/research.md
- spec/w-gents/integration.md:473
- spec/reliability.md

**Options**:
1. **Create E-gents spec** (Evolution agents)
2. **Remove all references** (acknowledge as abandoned)

**Kent's Decision**: Remove all references ✅ DONE

### 3.2 R-gents (Single Reference)

**Status**: Referenced once in functor-catalog.md:180

**Action**: Remove reference (low-value orphan).

### 3.3 D-gents Internal Files

Missing from D-gents README table:
- vector.md
- streams.md
- graph.md
- lethe.md

**Action**: Remove from README table (aspirational, never implemented).

### 3.4 F-gents Archive

`spec/f-gents/MIGRATION.md` references `spec/f-gents-archived/` but directory doesn't exist.

**Action**: Create archive directory and move files, or update L-gent references.

**Exit Criteria**: All orphan decisions made and implemented.

---

## Phase 4: Cross-File Consistency (Week 3)

**Goal**: Harmonize naming, counts, and status across files.

### 4.1 Crown Jewel Status Sync

Discrepancy between CLAUDE.md and HYDRATE.md:

| Source | Systems Listed | Percentages |
|--------|----------------|-------------|
| CLAUDE.md | 6 | Gestalt 70%, Town 55% |
| HYDRATE.md | 8 | Gestalt 85%, Town 70% |

**Action**: Use HYDRATE.md as source of truth, update CLAUDE.md.

### 4.2 Missing READMEs

18 directories lack README.md:
- spec/agents/
- spec/infrastructure/
- spec/architecture/
- spec/f/
- spec/decisions/
- (13 more)

**Action**: Create minimal README.md for navigation.

### 4.3 Naming Consistency

| Pattern | Variations | Standard |
|---------|------------|----------|
| Crown Jewel | "crown jewel", "Crown Jewel", "CrownJewel" | "Crown Jewel" |
| a-gents | "a-gents", "a-agents" | "a-gents" |

**Exit Criteria**: Consistent naming across all docs.

---

## Phase 5: CLI Version Roadmap (Optional)

**Issue**: Multiple CLI specs (v4, v5, v6, v7) without clear roadmap.

**Not broken** - these are intentional evolution documents.

**Action**: Add "CLI Evolution Roadmap" section to cli.md explaining the progression.

---

## Files Changed

### Phase 1 (Day 1)
```
CLAUDE.md
spec/c-gents/README.md
spec/services/witness.md
spec/services/muse.md
```

### Phase 2 (Week 1)
```
docs/skills/agentese-path.md
docs/skills/building-agent.md
docs/skills/test-patterns.md
docs/skills/projection-target.md
spec/protocols/projection.md
spec/protocols/data-bus.md
```

### Phase 3 (Week 2)
```
spec/t-gents/adversarial.md
spec/b-gents/banker.md
spec/w-gents/integration.md
spec/reliability.md
spec/c-gents/functor-catalog.md
spec/d-gents/README.md
spec/l-gents/*.md
```

---

## Anti-Patterns (Avoid)

- **Over-documentation**: Don't create docs for the sake of "completeness"
- **Aspirational specs**: Remove references to things that don't exist
- **Bureaucratic READMEs**: Navigation aids, not essays
- **Context dump**: Keep CLAUDE.md lean

---

## Quality Gate

| Check | Criteria |
|-------|----------|
| Broken links | 0 in high-traffic files |
| Count accuracy | All "N systems" claims verified |
| Orphan decisions | All E-gents/R-gents refs resolved |
| Date freshness | All "Compiled:" dates current |

---

*"The gardener doesn't count the petals. The gardener tends the garden."*

*Created: 2025-12-20 | Chief of Staff Docs Audit*
