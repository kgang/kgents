# Idea Audit Summary

> *Audit performed: 2025-12-13*
> *Sessions processed: 15 (session-01 through session-15)*

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Sessions | 15 |
| Estimated Ideas | 600+ |
| Priority Formula Used | `(FUN × 2 + SHOWABLE × 2 + PRACTICAL) / (EFFORT × 1.5)` |
| Perfect 10.0 Ideas | ~15 |
| Quick Wins (Priority ≥ 7.0, Effort ≤ 2) | ~70 |

---

## Session Classifications

| Session | Type | Theme | Quick Wins | Crown Jewels |
|---------|------|-------|------------|--------------|
| 1 | FOUNDATIONAL | Bootstrap (7 primitives) | 11 | 3 |
| 2 | FOUNDATIONAL | Archetypes (8 modes) | 17 | 3 (`whatif`, `why`, `tension`) |
| 3 | CORE | K-gent Soul | 22 | 5 (`vibe`, `drift`, `tense`) |
| 4 | CORE | H-gents Thinking | 14 | 4 (`shadow`, `slippage`) |
| 5 | DOMAIN | M/N-gents Memory | ~12 | 2 |
| 6 | DOMAIN | A/G/F-gents Creation | ~10 | 2 |
| 7 | DOMAIN | B/E-gents Evolution | ~8 | 2 |
| 9 | DOMAIN | D/L-gents State | ~10 | 2 |
| 10 | DOMAIN | T/R-gents Testing | ~8 | 2 |
| 11 | DOMAIN | I-gent Visualization | 16 | 3 |
| 12 | INFRASTRUCTURE | U/P/J Tools+Parsing+JIT | 12 | 2 (`parse`, `reality`) |
| 13 | INFRASTRUCTURE | O-gents Observation | 5 | 2 (`observe`, `panopticon`) |
| 14 | INTEGRATION | Cross-Pollination | 28 | 6 (combos) |
| 15 | SYNTHESIS | 60-Second Tour | — | References all |

---

## Changes Made

### Standardization

All 15 sessions now have consistent headers:
- **Priority Formula**: Moved to file header (no longer duplicated in body)
- **Type Classification**: Added to disambiguate session purposes
- **Cross-references**: Sessions 14-15 now reference source sessions instead of duplicating

### Session 15 (Synthesis)

- Marked as `Type: SYNTHESIS`
- Added cross-reference note: "This session curates and presents ideas from Sessions 1-14"
- Replaced duplicate implementation priority list with references to source sessions
- Kept tour scripts and portfolio demos as the unique contribution

### Session 14 (Integration)

- Marked as `Type: INTEGRATION`
- Added session index cross-reference
- Kept agent combination ideas (C01-C62) as unique contribution
- Note: Detailed implementation for individual agents lives in source sessions

### Sessions 1-2 (Foundational)

- Marked as `Type: FOUNDATIONAL`
- Removed duplicate priority formula sections
- These sessions define the primitives that all others reference

---

## Redundancy Patterns Identified

### 1. Priority Formula Duplication
**Status**: RESOLVED
- Formula appeared in 12+ session files
- Now: Single definition in each file header

### 2. CLI Command Duplication
**Pattern**: Commands like `kg whatif`, `kg parse`, `kg soul` appear in multiple sessions
**Resolution**: Commands defined in their primary session, referenced elsewhere:
- `kg whatif`, `kg why`, `kg tension`, `kg challenge` → Session 2 (Archetypes)
- `kg parse`, `kg reality` → Session 12 (U/P/J)
- `kg soul *` → Session 3 (K-gent Soul)
- `kg observe`, `kg panopticon` → Session 13 (O-gents)
- `kg shadow`, `kg dialectic` → Session 4 (H-gents)

### 3. Bootstrap Agent Descriptions
**Pattern**: The 7 bootstrap agents described in Sessions 1, 14, 15
**Resolution**: Session 1 is authoritative; Sessions 14-15 reference it

### 4. Archetype Descriptions
**Pattern**: The 8 archetypes described in Sessions 2, 14
**Resolution**: Session 2 is authoritative; Session 14 references it

---

## Cross-Session Navigation Guide

### For Developers

```
Session 1  → Bootstrap primitives (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)
Session 2  → Behavioral patterns (Consolidator, Questioner, Shapeshifter, Spawner, Uncertain, Witness, Dialectician, Introspector)
Session 3  → K-gent soul system (eigenvectors, dialogue modes, PersonaGarden)
Session 12 → Infrastructure tools (parsing, reality classification, JIT)
```

### For Self-Communication

```
When talking to yourself across sessions:
1. Reference the canonical session for implementation details
2. Use Type tags to understand context (FOUNDATIONAL, CORE, DOMAIN, INTEGRATION, SYNTHESIS)
3. Cross-pollination ideas in Session 14 compose ideas from other sessions
4. Session 15 is the "public demo" view; Session 1-13 are the "source code"
```

### For Communicating with Developer

```
Priority ≥ 8.0  → Present as "Quick Win"
Priority = 10.0 → Present as "Crown Jewel"
Effort ≤ 2      → Can ship in a day
Effort ≥ 4      → Needs planning
```

---

## Recommendations

### Immediate Actions (Quick Wins)

1. **`kg parse`** (Session 12) — Universal parser CLI, trivial to wire
2. **`kg reality`** (Session 12) — Reality classifier, already implemented
3. **`kg whatif`** (Session 2) — Show 3 alternatives for any task
4. **`kg observe`** (Session 13) — One-line system health
5. **`kg soul vibe`** (Session 3) — One-liner soul state

### Future Consolidation

1. **Unify CLI commands into single registry** — Currently scattered across sessions
2. **Create `plans/ideas/index.md`** — Master navigation for all sessions
3. **Archive low-priority ideas** — Items with Priority < 5.0 could move to `_archive/`

### Agent Opportunities

Based on the audit, these agents could be created:

| Agent | Purpose | Source Sessions |
|-------|---------|-----------------|
| **IndexAgent** | Navigate idea sessions | All |
| **PriorityFilterAgent** | Surface quick wins | 1-14 |
| **DuplicateDetectorAgent** | Find repeated ideas | 14-15 analysis |
| **ImplementationTrackerAgent** | Track what's built vs proposed | All |

---

## Concerns

### 1. Session 14 Size
Session 14 (Cross-Pollination) has 62+ combination ideas. Consider splitting into:
- `session-14a-two-agent-combos.md`
- `session-14b-three-agent-combos.md`
- `session-14c-full-stack-toys.md`

### 2. Orphaned Ideas
Some ideas from early sessions may be superseded by later, more refined versions. A future audit could:
- Mark ideas as `STATUS: SUPERSEDED BY <session>:<idea>`
- Remove truly stale ideas

### 3. Implementation Tracking
No clear tracking of which ideas have been implemented. Recommend adding `STATUS: IMPLEMENTED` tags or linking to actual code files.

---

## Summary

The 15 creative exploration sessions contain ~600+ ideas across the kgents taxonomy. Key patterns:
- **Sessions 1-4** are foundational (primitives, archetypes, soul, thinking)
- **Sessions 5-11** are domain-specific (memory, creation, evolution, state, testing, visualization)
- **Sessions 12-13** are infrastructure (tools, parsing, observation)
- **Session 14** is integration (cross-pollination of all prior sessions)
- **Session 15** is synthesis (demo portfolio for external presentation)

The audit standardized headers, added type classifications, and created this navigation guide. No ideas were deleted; the goal was consolidation and cross-referencing rather than elimination.

---

*"The goal isn't to have fewer ideas. It's to know where they live."*
