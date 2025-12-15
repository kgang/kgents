# Ideas Synthesis: Methodology

> *"The distance from idea to reality is measured in structured execution."*

---

## What This Directory Is (And Is Not)

**IS**: Documentation of the *methodology* for creative exploration and idea synthesis.

**IS NOT**: An inventory of ideas (those belong in `plans/`).

---

## The Creative Exploration Process

### Origins (2025-12-13)

Fifteen creative exploration sessions generated 600+ ideas across 28 agent archetypes. This process used:

1. **Session-Based Exploration**: Each session focused on one agent genus
2. **Priority Scoring**: FUN + SHOWABLE + PRACTICAL - EFFORT = Priority
3. **Cross-Pollination**: Final sessions combined agents into synergistic compositions
4. **Categorical Critique**: Category theory lens applied to all ideas

### The Scoring Formula

```
Priority = FUN + SHOWABLE + PRACTICAL - (EFFORT / 2)

Where:
- FUN: 0-5 (How enjoyable to implement?)
- SHOWABLE: 0-5 (How impressive to demonstrate?)
- PRACTICAL: 0-5 (How useful day-to-day?)
- EFFORT: 1-5 (How much work?)
```

**Crown Jewels** = Priority >= 10.0 (the "must ship" features)

---

## From Ideas to Plans

Ideas generated in this process flow into the planning system:

```
Creative Session → Idea Inventory → Audit → Plan File → Implementation
```

### Assimilation Protocol

When auditing ideas:

1. **Check Implementation Status**: Is it already done?
2. **Cross-Reference Plans**: Does a plan already cover this?
3. **Extract to Plans**: Create plan file for unimplemented high-priority ideas
4. **Delete Inventory**: Once ideas are in plans, delete the inventory file

---

## Reference Documents (Historical)

These files capture the *output* of the creative exploration process:

| File | Purpose | Status |
|------|---------|--------|
| `master-plan.md` | Original orchestration doc | Historical reference |
| `categorical-critique.md` | Category theory analysis | Educational reference |
| `cross-synergy.md` | Cross-agent combinations | Educational reference |
| `developer-education.md` | Onboarding guide | Active documentation |
| `execution-prompt.md` | Prompt template for agents | Tool |
| `meta-construction.md` | Emergent composition system | Spec reference |
| `metrics-reflection.md` | Metrics framework | Spec reference |
| `qa-strategy.md` | QA approach | Active methodology |

---

## Idea Inventory Files (DEPRECATED)

The following files have been **assimilated into plans** and should be deleted:

| File | Destination | Action |
|------|-------------|--------|
| `crown-jewels.md` | `plans/devex/cli-quick-wins-wave4.md` + already implemented | DELETE |
| `quick-wins.md` | `plans/devex/cli-quick-wins-wave4.md` + already implemented | DELETE |
| `medium-complexity.md` | `plans/devex/cli-quick-wins-wave4.md` + Agent Town | DELETE |

### What Was Implemented

From the original 600+ ideas:

| Category | Implemented | Plan |
|----------|-------------|------|
| K-gent soul commands | `kg soul vibe/drift/tense` | K-gent Phase 1 (88 tests) |
| Agent Town | 7 citizens, coalitions, memory | Agent Town Phase 4 (437 tests) |
| AGENTESE REPL | Full interactive navigation | REPL Waves 1-3 (97 tests) |
| Fuzzy matching | Typo correction, suggestions | REPL Wave 3 |
| Session persistence | Save/restore state | REPL Wave 3 |

### What Remains

Remaining high-value ideas extracted to `plans/devex/cli-quick-wins-wave4.md`:
- H-gent thinking commands (`kg shadow`, `kg dialectic`)
- Creative commands (`kg oblique`, `kg yes-and`)
- Infrastructure commands (`kg parse`, `kg reality`)
- Cross-pollination (`kg approve`)

---

## Running Your Own Creative Session

To generate new ideas:

1. Pick an agent genus (e.g., H-gents for philosophical thinking)
2. Brainstorm freely for 30-60 minutes
3. Apply the scoring formula
4. Extract Crown Jewels (priority >= 10.0)
5. Create plan files for winners
6. Discard the inventory (ideas are in plans now)

---

## Principles (from spec/principles.md)

- **Generativity**: Status should derive from implementation, not documentation
- **The Molasses Test**: Can this file be deleted in 30 days?
- **Aggressive Archiving**: Ideas become plans or get deleted

---

*"Ideas are free. Execution is expensive. Plans are the bridge."*
