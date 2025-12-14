# The Forest Protocol

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Ground Truth**: `spec/principles.md` — The Seven Principles + Meta-Principles

This file documents **plans-specific protocols** that govern how agents and humans coordinate across sessions. For the foundational principles, always consult `spec/principles.md`.

---

## Forest Over King

Every session tends multiple trees, not one monarch.

- No single plan consumes entire session focus
- Every session acknowledges multiple active trees
- Plans are peers, not hierarchy (heterarchical)

---

## Stigmergic Coordination

Agents coordinate through the environment, not centralized command.

Plans leave traces via YAML headers that subsequent agents sense:
- `status`: dormant | blocked | active | complete
- `progress`: 0-100
- `blocking/enables`: dependency graph

Reading the forest: `plans/_forest.md` aggregates all plan headers.

---

## Attention Budgeting

Every session allocates attention across the forest:
- Primary Focus (60%)
- Secondary (25%)
- Maintenance (10%)
- Accursed Share (5%) — **mandatory** exploration

Dormant plans enter the Accursed Share rotation.

---

## Blockers Are First-Class

| Type | Example | Resolution |
|------|---------|------------|
| Plan Dependency | `self/memory` blocked on `self/stream` | Complete dependency |
| Decision Needed | Architectural choice required | User input |
| Context | Needs more research | Accursed Share attention |

---

## Session Continuity

Each session is a chapter:
- Read the previous `_epilogues/` entry
- Write an epilogue at session end
- The narrative arc spans sessions

**Auto-Inducer Signifiers** (`spec/protocols/auto-inducer.md`):
- `⟿[PHASE]` — Continue to next phase (auto-execute)
- `⟂[REASON]` — Halt, await human (DETACH, blocked, entropy depleted)
- *(none)* — Await human input (backwards compatible)

---

## Agent Tenacity

> *"The agent does not ask permission. The agent acts from faith in principles."*

- **Parallel execution**: Spawn agents when tracks are independent
- **Background tasks**: Long operations don't block
- **TodoWrite as commitment**: Public declaration creates accountability
- **Complete the work**: Don't describe it—DO IT

**Why courage is possible**:
```
Any handle → /hydrate → spec/principles.md → Correctness
```

The principles don't change. They are the fixed point.

---

## File Structure

```
plans/
├── _forest.md        # Canopy: visible state (auto-generated)
├── _focus.md         # Root: human intent (never overwrite)
├── meta.md           # Mycelium: atomic learnings (50-line cap)
├── _epilogues/       # Spores: session continuity
├── skills/           # Patterns: pull → apply → push
└── [context]/        # Plan files (YAML headers)
```

---

## Applying These Protocols

| Protocol | Question |
|----------|----------|
| Forest Over King | Am I serving one plan or tending multiple? |
| Stigmergic Coordination | Did I read pheromone trails? |
| Attention Budgeting | Have I allocated across the forest? |
| Session Continuity | Did I read previous epilogue? Will I write one? |
| Agent Tenacity | Am I acting or describing? |

---

*Lines: 114. Ceiling: 120. Prune if exceeded.*
