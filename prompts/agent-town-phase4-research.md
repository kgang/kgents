⟿[RESEARCH]

# Agent Town Phase 4: RESEARCH

## ATTACH

/hydrate

You are entering **RESEARCH** phase for Agent Town Phase 4.

handles: plan=`plans/agent-town/phase4-civilizational.md`; chunks=4.1-4.8; scope=25_citizens+web_ui+api; heritage=CHATDEV+SIMULACRA+ALTERA+VOYAGER+AGENT_HOSPITAL; ledger={PLAN:touched}; entropy=0.30/0.35

---

## Mission

Map terrain for Phase 4 implementation by investigating:

### 1. UI Technology Evaluation

**Textual (TUI)** — existing patterns:
- Read `impl/claude/agents/i/screens/` (14 screens)
- Assess: transition system, mixins, reactive model
- Pros: reuse, consistency, terminal-native
- Cons: limited visualization, no graphs

**marimo (reactive notebooks)** — new territory:
- WebSearch: "marimo reactive notebooks 2025 real-time visualization"
- WebSearch: "marimo vs streamlit vs gradio agent simulation"
- Assess: reactivity model, WebSocket support, deployment
- Pros: rich visualization, plotly/altair integration
- Cons: new dependency, learning curve

**Decision Matrix**:
| Criterion | Textual | marimo |
|-----------|---------|--------|
| Reuse existing code | ★★★ | ★ |
| Visualization richness | ★ | ★★★ |
| Real-time updates | ★★ | ★★★ |
| Deployment simplicity | ★★ | ★★★ |
| Kent's "VISUAL UIs" intent | ★ | ★★★ |

### 2. Coalition/Reputation Algorithms

**Coalition Detection**:
- Read `impl/claude/agents/d/graph.py` (existing graph patterns)
- WebSearch: "social network clique detection algorithms python"
- Options: Bron-Kerbosch (exact), threshold-based (simple)
- Decision: which fits emergent behavior goal?

**Reputation Propagation**:
- WebSearch: "PageRank variant trust propagation social networks"
- WebSearch: "simple diffusion model reputation simulation"
- Options: PageRank, heat diffusion, simple decay
- Constraint: must integrate with eigenvector space

### 3. LLM Budget Analysis

**Current K-gent Patterns**:
- Read `impl/claude/agents/k/` (K-gent implementation)
- Estimate tokens/citizen/turn
- Pattern: LLM for dialogue, rules for behavior

**Budget Model**:
- 25 citizens, N LLM-backed, M rules-based
- Cost per turn = N × tokens × price
- Target: < $1/day for Pro tier

### 4. Prior Art Check

**Existing Components**:
- `agents/town/memory.py` — GraphMemory (reuse for coalition graphs?)
- `agents/i/screens/` — Textual patterns (reuse for town UI?)
- `protocols/streaming/nats_bridge.py` — event streaming (reuse for town events?)
- `protocols/api/` — API patterns (reuse for town API?)

**Composability Check**:
- Can existing components compose into Phase 4?
- What new wiring is needed?

---

## File Targets

| File | Purpose |
|------|---------|
| `impl/claude/agents/i/screens/base.py` | Textual base patterns |
| `impl/claude/agents/i/screens/transitions.py` | Screen transition system |
| `impl/claude/agents/d/graph.py` | Graph algorithms |
| `impl/claude/agents/town/memory.py` | GraphMemory for reuse |
| `impl/claude/agents/k/` | K-gent LLM patterns |
| `impl/claude/protocols/api/app.py` | API patterns |
| `impl/claude/protocols/streaming/nats_bridge.py` | Event streaming |

---

## Exit Criteria

- [ ] UI technology decision documented with rationale
- [ ] Coalition algorithm selected (with justification)
- [ ] Reputation propagation model chosen
- [ ] LLM budget model defined (N LLM-backed, M rules-based)
- [ ] File map with composable components identified
- [ ] Blockers enumerated (or "none")
- [ ] ledger.RESEARCH=touched

---

## Questions to Answer

1. **marimo vs Textual?** Which aligns with Kent's vision?
2. **Clique vs threshold?** For coalition detection
3. **PageRank vs diffusion?** For reputation
4. **How many LLM citizens?** Budget constraint
5. **What can we reuse?** From existing I-gent, D-gent, K-gent

---

## Entropy Draw

`void.entropy.sip(amount=0.10)` — exploration budget for this phase.

---

## Continuation

Upon completing RESEARCH:

```
⟿[DEVELOP]
exit: ui_decision, coalition_algo, reputation_model, llm_budget, composables
continuation → DEVELOP
```

OR

```
⟂[BLOCKED:ui_unclear] Need human input on marimo vs Textual preference
⟂[BLOCKED:budget_unknown] Token costs unclear, need profiling
```

---

*"Research is not about finding answers. It is about finding the right questions."*
