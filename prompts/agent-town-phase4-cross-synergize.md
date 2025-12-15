⟿[CROSS-SYNERGIZE]

# Agent Town Phase 4: CROSS-SYNERGIZE

## ATTACH

/hydrate

You are entering **CROSS-SYNERGIZE** phase for Agent Town Phase 4.

handles: plan=`plans/agent-town/phase4-civilizational.md`; strategy=`plans/agent-town/phase4-strategy.md`; contracts=`plans/agent-town/phase4-develop-contracts.md`; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched}; entropy=0.22/0.35

---

## Context from STRATEGIZE

### Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| Strategy document | `plans/agent-town/phase4-strategy.md` | Chunk ordering, parallel tracks |
| Contracts document | `plans/agent-town/phase4-develop-contracts.md` | 5 contracts with 12 laws |
| Decision gates | G1 (marimo), G2 (CDlib), G3 (LLM budget) | Risk mitigation |

### Key Decisions

- **Parallel Tracks**: Track A (Citizens: 4.1→4.2→4.3→4.7), Track B (UI: 4.4→4.5→4.6)
- **Merge Point**: 4.8 (Integration)
- **Leverage Points**: L1 (Eigenvectors), L2 (Coalition), L3 (Event Bridge), L4 (marimo cells)

### Blockers: None

---

## Your Mission

Discover **compositions and entanglements** that unlock nonlinear value. Test combinations across agents, functors, and existing components. Find 2x-10x leverage through composition.

### Composition Candidates to Probe

| This Work | Candidate Composition | Probe |
|-----------|----------------------|-------|
| 7D Eigenvectors | `agents/k/eigenvectors.py` | Extend vs. wrap K-gent eigenvectors |
| Coalition detection | `agents/d/graph.py` | Reuse BFS patterns for k-hop |
| EigenTrust | `protocols/agentese/garden.py` | Trust decay pattern reuse |
| Town API | `protocols/api/app.py` + `sessions.py` | Mount as sub-router |
| Event bridge | `protocols/streaming/nats_bridge.py` | Extend TownEvent type |
| marimo dashboard | `agents/i/screens/` | LOD semantics reuse |

### Dormant Plans to Check

Skim `plans/_forest.md` for forgotten plans that might compose:

- `plans/reactive-substrate-unification` — marimo might contribute to unified widget protocol
- `plans/k-terrarium-llm-agents` — Town provides live citizen demo for K-gent
- `plans/agentese-universal-protocol` — Town as AGENTESE showcase (umwelt demonstration)

### Functor Registry Check

Query: What existing functors could lift this work?

- `TOWN→NPHASE` functor (already exists in `agents/town/functor.py`)
- `NPHASE_OPERAD` operations (reuse for citizen evolution cycles)
- `SOUL_POLYNOMIAL` patterns (eigenvector drift is similar to personality drift)

---

## Principles Alignment

This phase emphasizes:

- **AD-003 (Generative)**: Define grammars, not lists. Compositions should derive new capabilities.
- **AD-005 (Composable)**: Agents are morphisms. Test identity/associativity at composition boundaries.
- **Accursed Share**: 5-10% entropy for unexpected compositions ("shouldn't work" sometimes does).

---

## Actions

1. **Enumerate candidate morphisms**: List possible compositions (agent pipelines, operad operations, functor lifts)
2. **Probe fast**: Use existing fixtures (`agents/town/_tests/`) for dry-runs, not speculative LLM loops
3. **Check laws**: Verify identity/associativity at each composition boundary
4. **Document rejected paths**: Write down what didn't work and why (prevent future rework)
5. **Select and freeze**: Choose compositions that satisfy laws and Ethical/Tasteful constraints

---

## Exit Criteria

- [ ] 5+ cross-synergies identified with rationale
- [ ] Dormant plans checked (compose or explicit "none")
- [ ] No conflicting implementations (law violations documented if any)
- [ ] Rejected paths documented
- [ ] Implementation-ready interfaces defined
- [ ] ledger.CROSS-SYNERGIZE=touched

---

## Entropy Draw

`void.entropy.sip(amount=0.05)` — composition exploration budget.

---

## Continuation

Upon completing CROSS-SYNERGIZE, emit one of:

### Normal Exit (auto-continue)

```
⟿[IMPLEMENT]
exit: synergies=${count}, conflicts=0, dormant_unblocked=${count}, rejected_paths=${count}
continuation → IMPLEMENT (Track A: chunk 4.1 first)
```

### Halt Conditions

```
⟂[BLOCKED:composition_conflict] Chosen compositions violate category laws
⟂[BLOCKED:no_viable_path] All candidate compositions rejected
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

---

## Process Metrics

| Metric | Value |
|--------|-------|
| Phase | CROSS-SYNERGIZE |
| Compositions to probe | 6 |
| Dormant plans to check | 3 |
| Functor candidates | 3 |
| Entropy sip | 0.05 |

---

This is the **CROSS-SYNERGIZE** phase for **Agent Town Phase 4: Civilizational Scale**. Your mission is to find compositions that multiply value. The difference between linear addition and exponential leverage is discovered here.

*"Discover compositions and entanglements that unlock nonlinear value."*
