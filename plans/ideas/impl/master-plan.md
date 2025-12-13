---
path: ideas/impl/master-plan
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [ideas/impl/quick-wins, ideas/impl/crown-jewels, ideas/impl/medium-complexity]
session_notes: |
  Master orchestration for implementing ALL ideas from creative exploration.
  Covers 15 sessions, 600+ ideas, 70+ quick wins, 45+ crown jewels.
  Multi-phase lifecycle: Plan → Research → Develop → Test → Educate → Measure → Reflect
---

# Implementation Master Plan: Creative Exploration → Production

> *"The distance from idea to reality is measured in structured execution."*

**Source**: 15 Creative Exploration Sessions (session-01 through session-15)
**Scope**: ALL Quick Wins, ALL Crown Jewels, Medium Complexity Projects
**Parallel Agent Strategy**: Enabled throughout

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Sessions | 15 |
| Total Ideas | 600+ |
| Quick Wins (Priority ≥ 7.0, Effort ≤ 2) | 70+ |
| Crown Jewels (Priority 10.0) | 45+ |
| Medium Complexity (Effort 3-4) | 85+ |
| Estimated Build Time (sequential) | 16-20 weeks |
| Estimated Build Time (parallel agents) | 6-8 weeks |

---

## The 11-Phase Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────┐   ┌──────────┐   ┌─────────┐   ┌────────────┐   ┌───────────────┐ │
│   │PLAN │ → │ RESEARCH │ → │ DEVELOP │ → │ STRATEGIZE │ → │CROSS-SYNERGIZE│ │
│   └─────┘   └──────────┘   └─────────┘   └────────────┘   └───────────────┘ │
│      ↓                                                            ↓          │
│   ┌─────────┐   ┌────┐   ┌──────┐   ┌─────────┐   ┌─────────┐   ┌────────┐  │
│   │IMPLEMENT│ → │ QA │ → │ TEST │ → │ EDUCATE │ → │ MEASURE │ → │REFLECT │  │
│   └─────────┘   └────┘   └──────┘   └─────────┘   └─────────┘   └────────┘  │
│                                                                     ↓        │
│                                                          ┌──────────────────┐│
│                                                          │   RE-METABOLIZE  ││
│                                                          │   (Feed back to  ││
│                                                          │    next cycle)   ││
│                                                          └──────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: PLAN

**Goal**: Structure the work into executable chunks

**Outputs**:
- [x] `master-plan.md` (this document)
- [ ] `quick-wins.md` - All 70+ quick wins with sprint assignments
- [ ] `crown-jewels.md` - All 45+ crown jewels with deep implementation notes
- [ ] `medium-complexity.md` - All 85+ medium projects with dependencies

**Parallel Agent Strategy**:
```
Agent 1: Extract Quick Wins → Structure into sprints
Agent 2: Extract Crown Jewels → Identify dependencies
Agent 3: Extract Medium Complexity → Estimate timelines
Agent 4: Cross-reference → Find synergies
```

**Exit Criteria**: All three sub-plans created with clear sprint assignments

---

## Phase 2: RESEARCH

**Goal**: Understand existing infrastructure before building

**Activities**:
1. **Codebase Audit**: For each idea, identify:
   - Existing implementations to leverage
   - Files to touch
   - Test coverage gaps

2. **Dependency Mapping**:
   - Which ideas depend on others?
   - What's the critical path?
   - What can run in parallel?

3. **Architecture Review**:
   - Do any ideas conflict with current architecture?
   - Are there hidden blockers?

**Parallel Agent Strategy**:
```
Agent 1: Audit K-gent / Soul implementations
Agent 2: Audit H-gent / Thinking implementations
Agent 3: Audit U/P/J infrastructure
Agent 4: Audit I-gent visualization
Agent 5: Audit Cross-pollination requirements
```

**Output**: Research findings appended to each sub-plan

---

## Phase 3: DEVELOP / ENHANCE

**Goal**: Refine idea specifications into implementable designs

**Activities**:
1. **API Design**: Define interfaces for each CLI command
2. **Type Definitions**: Create TypedDicts, Protocols, etc.
3. **Test Cases**: Write test specifications before code
4. **Documentation Drafts**: Prepare docstrings and user guides

**Parallel Agent Strategy**:
```
Sprint 1 (Week 1-2): Quick Wins Tier S (10.0 priority)
Sprint 2 (Week 3-4): Quick Wins Tier A (9.0-9.9)
Sprint 3 (Week 5-6): Crown Jewels with dependencies resolved
Sprint 4 (Week 7-8): Medium Complexity Phase 1
```

**Output**: Detailed design documents for each implementation

---

## Phase 4: STRATEGIZE

**Goal**: Sequence work for maximum value and minimum risk

**Strategic Principles**:
1. **Quick Wins First**: Build momentum with easy victories
2. **Demonstrate Value Early**: Showable items prioritized
3. **Unblock Dependencies**: Clear blocking paths
4. **Parallel Tracks**: Multiple agents work simultaneously

**Sprint Strategy**:

| Sprint | Focus | Ideas | Agents |
|--------|-------|-------|--------|
| 1 | K-gent Soul CLI | `soul vibe`, `soul drift`, `soul tense` | 2 |
| 2 | Infrastructure CLI | `parse`, `reality`, `execute` | 2 |
| 3 | H-gent Thinking CLI | `shadow`, `dialectic`, `gaps` | 2 |
| 4 | Visualization | `sparkline`, `weather`, dashboards | 2 |
| 5 | Cross-Pollination | Combo ideas (C01-C10) | 3 |
| 6 | Integration | End-to-end testing | 2 |

---

## Phase 5: CROSS-SYNERGIZE

**Goal**: Identify and exploit connections between ideas

**Synergy Categories**:

### A. Agent Genus Synergies
```
K-gent (Soul) ←→ H-gent (Thinking)
  └── "Soul Shadow" detection
  └── "Dialectical Soul Tension"

U-gent (Tools) ←→ P-gent (Parsing)
  └── Self-healing pipelines
  └── Confidence-aware execution

I-gent (Viz) ←→ Flux (Streaming)
  └── Living garden dashboards
  └── Real-time health monitoring
```

### B. CLI Command Synergies
```
kg soul * ←→ kg shadow
  └── Combined: kg introspect (full H-gent pipeline through soul)

kg parse ←→ kg reality
  └── Combined: kg analyze (parse + classify in one command)
```

### C. Cross-Session Synergies
```
Session 3 (K-gent) + Session 4 (H-gent) + Session 14 (Cross-Pollination)
  └── "What Would Kent Synthesize?" (C22)
  └── Ethical Code Review (C32)
```

**Output**: `cross-synergy.md` with all identified connections

---

## Phase 6: IMPLEMENT

**Goal**: Write code that passes tests

**Implementation Tracks** (Parallel):

### Track A: CLI Commands (Quick Wins)
```
impl/claude/protocols/cli/handlers/
  ├── soul.py      # kg soul *
  ├── shadow.py    # kg shadow, kg dialectic
  ├── parse.py     # kg parse
  ├── reality.py   # kg reality
  ├── viz.py       # kg sparkline, kg weather
  └── ...
```

### Track B: Agent Enhancements
```
impl/claude/agents/
  ├── k/          # Soul enhancements
  ├── h/          # Thinking enhancements
  ├── u/          # Tool enhancements
  ├── p/          # Parsing enhancements
  └── i/          # Visualization enhancements
```

### Track C: Integration (Cross-Pollination)
```
impl/claude/protocols/cli/handlers/
  ├── approve.py   # "Would Kent Approve?" (C01)
  ├── synthesize.py # "What Would Kent Synthesize?" (C22)
  └── review.py    # Ethical Code Review (C32)
```

**Parallel Agent Strategy**:
```
Agent 1: CLI handlers (pure wiring)
Agent 2: Agent enhancements (business logic)
Agent 3: Tests (parallel test writing)
Agent 4: Documentation (parallel doc writing)
```

---

## Phase 7: QA

**Goal**: Ensure quality before merge

**QA Checklist**:
- [ ] All new code has tests
- [ ] Type hints complete (mypy passes)
- [ ] Ruff formatting clean
- [ ] Docstrings present
- [ ] No security vulnerabilities
- [ ] Performance acceptable

**QA Strategy**: See `qa-strategy.md`

---

## Phase 8: TEST

**Goal**: Verify correctness at all levels

**Test Types** (per T-gent taxonomy):
1. **Type I: Unit** - Individual functions
2. **Type II: Property** - Invariant checking
3. **Type III: Integration** - Component interactions
4. **Type IV: Adversarial** - Chaos testing (Saboteur)
5. **Type V: Dialectic** - Contradiction detection

**Target Coverage**: 94%+ (match existing standard)

**Parallel Testing Strategy**:
```
Agent 1: Run unit tests
Agent 2: Run property tests
Agent 3: Run integration tests
Agent 4: Run adversarial tests
```

---

## Phase 9: EDUCATE

**Goal**: Ensure developer can use and extend

**Education Deliverables**:
1. **Quick Start Guide**: "Your first kg command in 60 seconds"
2. **CLI Reference**: All commands documented
3. **Architecture Overview**: How ideas connect to implementation
4. **Extension Guide**: How to add new commands

**Output**: `developer-education.md`

---

## Phase 10: MEASURE

**Goal**: Track adoption and effectiveness

**Metrics**:
1. **Usage Metrics**:
   - Command invocation counts
   - Error rates per command
   - Response times

2. **Quality Metrics**:
   - Test coverage
   - Bug reports
   - Performance benchmarks

3. **Value Metrics**:
   - Developer satisfaction (NPS)
   - Time saved estimates
   - Feature requests

**Output**: `metrics-reflection.md`

---

## Phase 11: REFLECT & RE-METABOLIZE

**Goal**: Learn from implementation, feed back to process

**Reflection Questions**:
1. Which ideas delivered more value than expected?
2. Which ideas underperformed?
3. What patterns emerged during implementation?
4. What would we do differently next time?

**Re-Metabolization**:
- Successful patterns → Add to `plans/skills/`
- Failed approaches → Document in `plans/meta.md`
- New ideas discovered → Add to `plans/ideas/session-16-*.md`

---

## Document Tree

```
plans/ideas/impl/
├── master-plan.md          # This document (orchestration)
├── quick-wins.md           # 70+ quick wins structured into sprints
├── crown-jewels.md         # 45+ crown jewels with deep notes
├── medium-complexity.md    # 85+ medium projects
├── cross-synergy.md        # Synergy analysis
├── qa-strategy.md          # Quality assurance approach
├── developer-education.md  # Education materials
└── metrics-reflection.md   # Measurement framework
```

---

## Execution Timeline

```
Week 1-2:   Planning & Research (this phase)
Week 3-4:   Sprint 1 - K-gent Soul CLI
Week 5-6:   Sprint 2 - Infrastructure CLI
Week 7-8:   Sprint 3 - H-gent Thinking CLI
Week 9-10:  Sprint 4 - Visualization
Week 11-12: Sprint 5 - Cross-Pollination Combos
Week 13-14: Sprint 6 - Integration & Testing
Week 15-16: Education, Metrics, Reflection
```

---

## Success Criteria

| Milestone | Definition | Target |
|-----------|------------|--------|
| Quick Wins Complete | 70+ CLI commands working | Week 8 |
| Crown Jewels Complete | 45+ top ideas implemented | Week 12 |
| Test Coverage | All new code tested | 94%+ |
| Documentation | All commands documented | Week 14 |
| Developer Education | Tutorial complete | Week 15 |
| Metrics Framework | Usage tracking live | Week 16 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Scope creep | Strict priority ranking; defer non-essentials |
| Dependency deadlock | Critical path analysis; unblock early |
| Quality degradation | QA gates per sprint; no merge without tests |
| Burnout | Parallel agents; sustainable pace |
| Lost context | Epilogues per session; clear documentation |

---

## Next Steps

1. Create `quick-wins.md` with all 70+ items
2. Create `crown-jewels.md` with all 45+ items
3. Create `medium-complexity.md` with all 85+ items
4. Begin Sprint 1: K-gent Soul CLI commands

---

*"The idea is nothing. The execution is everything."*
