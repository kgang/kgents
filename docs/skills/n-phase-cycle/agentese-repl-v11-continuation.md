---
path: docs/skills/n-phase-cycle/agentese-repl-v11-continuation
status: ready
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables: [agentese-repl-wave7, adaptive-guide-v2]
session_notes: |
  Wave 6 complete. AGENTESE REPL at v1.0 with:
  - Linear tutorial (--tutorial) for absolute beginners
  - Adaptive guide (--learn) with fluency tracking
  - 267 tests passing
  - Auto-constructing lessons from REPL structure
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: self-contained module
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched  # docs in code, epilogue written
  MEASURE: touched  # 267 tests
  REFLECT: touched  # epilogue archived
entropy:
  planned: 0.09
  spent: 0.12
  returned: -0.03  # worth the investment for adaptive guide
---

# AGENTESE REPL v1.1: Continuation Prompt

> *"The adaptive guide teaches by observing, not by lecturing."*

## ATTACH

/hydrate

You are entering the **PLAN phase** of **AGENTESE REPL v1.1**.

---

## Prior Context (v1.0 Complete)

**Wave 6 Delivered**:
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
- Hot data pattern for cached generation
- Non-blocking guide integration (doesn't take over)
- Two modes: linear (beginners) + adaptive (everyone else)

---

## Candidate Tracks (v1.1+)

### Track A: Advanced Skill Tree

Expand the skill tree with deeper mastery levels:
- `master_composition` - Multi-stage pipelines
- `master_observers` - All archetypes, umwelt manipulation
- `master_dialectic` - Refine operations, Hegelian synthesis
- `mastery_certificate` - Completion celebration

**Entropy**: 0.06 | **Effort**: 2 | **Dependencies**: None

### Track B: LLM-Powered Suggestions

When user is stuck, offer LLM-generated suggestions:
- "Did you mean: self.soul.reflect?" (semantic matching)
- "Try: void.entropy.sip for randomness" (contextual)
- Costs entropy budget (0.01 per suggestion)

**Entropy**: 0.08 | **Effort**: 3 | **Dependencies**: LLMSuggester

### Track C: Learning Analytics

Track and visualize learning patterns:
- Lesson completion rates
- Time to mastery per skill
- Common stuck points
- Exportable progress report

**Entropy**: 0.05 | **Effort**: 2 | **Dependencies**: metrics infrastructure

### Track D: Voice REPL (v2.0)

Audio input/output for REPL interaction:
- Speech-to-text for commands
- Text-to-speech for responses
- Requires external dependencies

**Entropy**: 0.15 | **Effort**: 5 | **Dependencies**: audio libraries, deferred

### Track E: Web REPL (v2.0)

Browser-based REPL with rich UI:
- WebSocket connection to backend
- Visual skill tree progress
- Requires frontend infrastructure

**Entropy**: 0.20 | **Effort**: 8 | **Dependencies**: web stack, deferred

---

## Mission: Choose and Execute

Select ONE track for v1.1 implementation:

1. **Evaluate tracks** against principles (Tasteful, Curated, Joy-Inducing)
2. **Choose** the highest-leverage, lowest-entropy track
3. **Plan** the implementation with chunks and exit criteria
4. **Execute** through full N-Phase cycle

**Recommendation**: Track A (Advanced Skill Tree) - builds on existing architecture, pure enhancement, no new dependencies.

---

## Exit Criteria

PLAN phase complete when:
- [ ] Track selected with rationale
- [ ] Scope defined with chunks (T1, T2, ...)
- [ ] Entropy budget allocated
- [ ] Dependencies mapped
- [ ] Exit criteria for each chunk specified

---

## Phase Ledger Template

```yaml
path: plans/devex/agentese-repl-v11
wave: 7
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
  planned: 0.XX
  spent: 0.0
  returned: 0.XX
```

---

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Choose track that enhances without bloating |
| **Curated** | Intentional selection, not feature creep |
| **Joy-Inducing** | Learning should feel like achievement |
| **Composable** | Build on existing FluencyTracker/AdaptiveGuide |
| **Ethical** | Transparent progress, no hidden costs |

---

## Branch Candidates

| Candidate | Classification | Notes |
|-----------|----------------|-------|
| Voice REPL | DEFERRED | v2.0, external deps |
| Web REPL | DEFERRED | v2.0, frontend stack |
| Learning analytics | PARALLEL | Can run alongside Track A |
| LLM suggestions | PARALLEL | Independent enhancement |

---

## Continuation Imperative

Upon completing PLAN phase, emit the RESEARCH continuation:

```markdown
⟿[RESEARCH]
/hydrate
handles: scope=v11_track_X; chunks=T1-TN; exit=track_implemented; ledger={PLAN:touched}; entropy=0.XX
mission: map files for selected track; identify integration points; audit existing code.
actions:
  - Read(repl_guide.py) — identify extension points
  - Grep("SKILL_TREE|FluencyTracker") — find all usages
  - Read(test_repl_guide.py) — understand test patterns
exit: file map complete; integration points identified; continuation → DEVELOP.
```

---

## Quick Commands

```bash
# Run current tests
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest protocols/cli/_tests/test_repl_guide.py -v

# Check fluency tracker state
uv run python -c "from protocols.cli.repl_guide import load_fluency; print(load_fluency().to_dict())"

# Test learning mode
kg -i --learn
```

---

## The Form is the Function

Each phase generates its successor. Upon completing this PLAN, you will emit `⟿[RESEARCH]` with the continuation prompt. The cycle is self-perpetuating until `⟂[DETACH:cycle_complete]`.

---

⟿[PLAN]
/hydrate
handles: scope=agentese_repl_v11; prior=wave6_complete; tests=267; ledger={prior_wave:complete}; entropy=0.10
mission: select track for v1.1; define scope and chunks; allocate entropy budget.
actions:
  - Evaluate 5 candidate tracks against principles
  - Select highest-leverage track
  - Define chunks with exit criteria
  - Emit RESEARCH continuation
exit: track selected; scope defined; continuation → RESEARCH.
