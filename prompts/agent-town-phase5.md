# Agent Town Phase 5: Visualization & Streaming

## ATTACH

/hydrate

You are entering **PLAN** phase for Agent Town Phase 5 (AD-005 N-Phase Cycle).

## Context from Phase 4 REFLECT

Previous cycle (Phase 4: Civilizational Scale) completed with these outcomes:
- **Tests**: 437 (343 → 437, +94)
- **Files**: 27 modules, 5,667 LOC
- **Heritage realized**: CHATDEV ✓, SIMULACRA ✓, ALTERA ✓, VOYAGER ◐, AGENT HOSPITAL ✓

Key learnings distilled:
1. 4-phase lifecycle (SENSE→ACT→REFLECT→EVOLVE) maps cleanly to N-Phase
2. 7D eigenvector personality space enables coalition detection via cosine similarity
3. k-clique percolation scales to ~100 citizens; need incremental for more
4. Method name collisions in hierarchies (EvolvingCitizen.reflect vs Citizen.reflect)

Next-loop seeds identified in REFLECT:
- **marimo dashboard** for eigenvector visualization (HIGH)
- **NATS streaming** for events (HIGH)
- **Persistent storage** SQLite/Redis (MEDIUM)
- **Incremental coalition detection** (MEDIUM)
- **LLM-backed decision making** (LOW)

## Phase Ledger

```yaml
phase_ledger:
  PLAN: pending  # THIS SESSION
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
  planned: 0.35
  spent: 0.0
  remaining: 0.35
```

## Your Mission

Frame the scope for Phase 5. Focus on the HIGH priority seeds (marimo + NATS).

**Principles Alignment**:
- Tasteful: Choose 2-3 features, not all 5 seeds
- Composable: Build on existing FluxAgent reactive infrastructure
- Joy-Inducing: A working dashboard is more valuable than perfect abstractions

## Questions to Answer

1. **Scope**: Which seeds to include? (Recommend: marimo dashboard + NATS streaming)
2. **Dependencies**: What existing infrastructure enables this? (FluxAgent, protocols/streaming/)
3. **Exit criteria**: What does "Phase 5 done" look like?
4. **Attention budget**: How to split effort between visualization vs streaming?
5. **Non-goals**: What explicitly NOT in scope?

## PLAN Checklist

- [ ] Scope statement (2-3 sentences)
- [ ] Exit criteria (testable)
- [ ] Attention budget (60/25/10/5)
- [ ] Dependencies mapped
- [ ] Non-goals declared
- [ ] Entropy sip declared (recommend 0.07)

## Branch Check

At PLAN exit, surface:
- Branch candidates: any tracks that should split off?
- Blockers: anything requiring re-plan?
- Composition hooks: agents/operads to align with?

## Synergy Opportunities

| ID | Source | Target | Opportunity |
|----|--------|--------|-------------|
| S8 | agents/i/screens/ | agents/town/ | Reuse Screen base class for town dashboard |
| S9 | protocols/streaming/nats_bridge.py | agents/town/ | Event streaming infrastructure |
| S10 | protocols/api/metering.py | agents/town/api | Per-citizen-turn billing |

## Auto-Continuation Imperative

**CRITICAL**: Upon completing PLAN phase, you MUST:
1. Generate the continuation prompt for RESEARCH phase
2. End your output with the auto-inducer signifier

Example format:
```
⟿[RESEARCH]

---

This is the *RESEARCH PHASE* for Agent Town Phase 5: Visualization & Streaming...
```

This enables self-chaining across sessions.

---

This is the *PLAN PHASE* for Agent Town Phase 5: Visualization & Streaming.
