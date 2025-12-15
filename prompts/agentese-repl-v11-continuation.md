---
path: prompts/agentese-repl-v11-continuation
status: ready
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables: [agentese-repl-wave7, adaptive-guide-v2, master-composition]
session_notes: |
  Continuation prompt for AGENTESE REPL v1.1 (Wave 7).
  Prior art: Wave 6 complete, 267 tests, tutorial + adaptive guide.
  Focus: Advanced Skill Tree (Track A) - highest leverage, lowest entropy.
phase_ledger:
  PLAN: pending
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.0
  returned: 0.0
---

# AGENTESE REPL v1.1: Wave 7 Continuation

> *"Mastery is not knowing more—it's knowing deeper."*

## ATTACH

/hydrate

You are entering the **PLAN phase** of **AGENTESE REPL Wave 7**.

---

## Prior Context (Wave 6 Complete)

**Wave 6 Delivered** (v1.0):
- `repl_tutorial.py` - Linear 8-lesson tutorial (`--tutorial`)
- `repl_guide.py` - Adaptive learning guide (`--learn`)
- `generated/tutorial_lessons.py` - Hot data cached lessons
- 267 tests passing (158 REPL + 49 tutorial + 60 guide)

**Key Artifacts**:
- `FluencyTracker` - Tracks demonstrated skills across sessions
- `SKILL_TREE` - 13 skills with prerequisites and thresholds
- `MicroLesson` - Topic-based lessons with natural aliasing
- `AdaptiveGuide` - Coordinates hints, lessons, suggestions

**Architecture Decisions**:
- Auto-constructing lessons from REPL introspection
- Hot data pattern for cached generation (AD-004)
- Non-blocking guide integration (doesn't take over)
- Two modes: linear (beginners) + adaptive (everyone else)

---

## Selected Track: Advanced Skill Tree (Track A)

**Rationale**: Builds on existing architecture, pure enhancement, no new dependencies. Highest leverage for joy-inducing learning progression.

### New Skills for Mastery Tier

| Skill | Description | Prerequisites | Threshold |
|-------|-------------|---------------|-----------|
| `master_composition` | Multi-stage pipelines (3+ operators) | `pipeline_basics` | 5 uses |
| `master_observers` | All archetypes, umwelt manipulation | `observer_archetypes` | 3 archetypes |
| `master_dialectic` | Refine operations, Hegelian synthesis | `basic_operations` | 3 refines |
| `master_entropy` | Void operations, sip/tithe/pour | `navigation` | 5 void ops |
| `mastery_achieved` | All master_ skills unlocked | all master_* | — |

### Chunks

| Chunk | Scope | Exit Criteria |
|-------|-------|---------------|
| T1 | Extend SKILL_TREE with mastery tier | New skills registered, prerequisites wired |
| T2 | Update FluencyTracker for mastery detection | Tracking logic works, tests pass |
| T3 | Create mastery-tier micro-lessons | 4 new lessons in LESSONS dict |
| T4 | Add mastery celebration (Easter egg) | Fun message on mastery_achieved |
| T5 | Integration tests for full mastery flow | End-to-end test passes |

---

## Non-Goals (Curated Scope)

- NO LLM-powered suggestions (Track B) - different complexity class
- NO learning analytics export (Track C) - infrastructure dependency
- NO voice/web REPL (Tracks D/E) - v2.0 scope
- NO changes to tutorial mode - already complete

---

## Entropy Budget

| Phase | Budget | Notes |
|-------|--------|-------|
| PLAN | 0.01 | This prompt |
| RESEARCH | 0.01 | File mapping |
| DEVELOP | 0.01 | Contract design |
| IMPLEMENT | 0.03 | Code changes |
| TEST | 0.02 | New tests |
| **Total** | 0.08 | Within standard allocation |

---

## Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| `repl_guide.py` | Stable | Low |
| `FluencyTracker` | Stable | Low |
| `SKILL_TREE` | Stable | Low |
| LESSONS hot data | Stable | Low |

No external dependencies. Pure enhancement to existing architecture.

---

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Mastery tier adds depth, not breadth |
| **Curated** | 5 new skills, not 50 |
| **Joy-Inducing** | Mastery celebration is the reward |
| **Composable** | Builds on existing FluencyTracker |
| **Generative** | Skills auto-construct from REPL structure |

---

## Files to Touch

```
impl/claude/protocols/cli/repl_guide.py          # SKILL_TREE, FluencyTracker
impl/claude/protocols/cli/generated/tutorial_lessons.py  # LESSONS hot data
impl/claude/protocols/cli/_tests/test_repl_guide.py      # New tests
```

---

## Exit Criteria (PLAN Phase)

- [x] Track selected with rationale
- [x] Scope defined with chunks (T1-T5)
- [x] Entropy budget allocated (0.08)
- [x] Dependencies mapped (all stable)
- [x] Exit criteria for each chunk specified

---

## Branch Candidates

| Candidate | Classification | Notes |
|-----------|----------------|-------|
| LLM suggestions | DEFERRED | Track B, different session |
| Learning analytics | PARALLEL | Could run alongside, but deferred for focus |
| Skill tree visualization | VOID | Interesting, low priority |

---

## Quick Commands

```bash
# Run guide tests
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest protocols/cli/_tests/test_repl_guide.py -v

# Check current skill tree
uv run python -c "from protocols.cli.repl_guide import SKILL_TREE; print([s.name for s in SKILL_TREE])"

# Test learning mode
kg -i --learn
```

---

## The Form is the Function

PLAN phase complete. Emitting RESEARCH continuation.

---

⟿[RESEARCH]
/hydrate
handles: scope=agentese_repl_v11; track=advanced_skill_tree; chunks=T1-T5; ledger={PLAN:touched}; entropy=0.07
mission: map existing skill tree implementation; identify extension points; audit test patterns.
actions:
  - Read(repl_guide.py) — find SKILL_TREE, FluencyTracker, mastery detection points
  - Read(tutorial_lessons.py) — understand LESSONS structure for new mastery lessons
  - Read(test_repl_guide.py) — identify test patterns for new mastery tests
  - Grep("SKILL_TREE|FluencyTracker|master") — find all usages across codebase
exit: file map complete; extension points identified; contracts drafted; continuation → DEVELOP.
