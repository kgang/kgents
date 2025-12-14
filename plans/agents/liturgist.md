---
path: agents/liturgist
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/liturgy, protocols/liturgy]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track G: Liturgical Journeys
  See: prompts/agentese-continuation.md
  Related: plans/meta/liturgy-morphism-nasi.md
---

# Liturgist

> *"To read is to invoke. The liturgy is not recitation—it is transformation."*

**Track**: G (Liturgical Journeys)
**AGENTESE Context**: `self.liturgy.*`, `time.trace.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Composable (liturgies compose), Generative (rewrite generates morphisms), Ethical (rollback enables recovery)

AGENTESE pointer: canonical handle/liturgy guardrails track `spec/protocols/agentese.md` and `plans/meta/liturgy-morphism-nasi.md`; refresh when either shifts.

---

## Purpose

The Liturgist implements read/simulate/rewrite as AGENTESE compositions. Liturgical journeys are structured workflows that traverse specifications, simulate execution, and generate morphisms. Rollback tokens enable safe exploration.

---

## Expertise Required

- Compositional workflow design
- Hypothetical/speculative execution patterns
- Morphism generation (spec → impl)
- Rollback/recovery protocols

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| G1 | `self.liturgy.read` → manifest composition | DEVELOP | 0.06 | Pending |
| G2 | `self.liturgy.simulate` → hypothetical execution | DEVELOP | 0.09 | Pending |
| G3 | `self.liturgy.rewrite` → morphism generation | IMPLEMENT | 0.07 | Pending |
| G4 | Rollback token issuance from `time.trace` | IMPLEMENT | 0.06 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `spec/protocols/liturgy.md` | Liturgical morphism specification |
| `impl/claude/protocols/agentese/liturgy.py` | Liturgy implementation |
| `impl/claude/protocols/agentese/contexts/time.py` | Rollback token protocol |

---

## Liturgical Journey

```
READ → SIMULATE → REWRITE
  ↓        ↓          ↓
manifest  hypothetical  morphism
  ↓        ↓          ↓
observer  what-if     transformation
```

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `self.liturgy.read` | Compose manifests into understanding | LiturgyReading |
| `self.liturgy.simulate` | Hypothetical execution with rollback | SimulationResult |
| `self.liturgy.rewrite` | Generate morphism from simulation | Morphism |
| `time.trace.rollback` | Issue rollback token | RollbackToken |
| `time.trace.commit` | Commit simulation (consume rollback) | CommitResult |

---

## Rollback Protocol

```python
# Issue rollback token before mutation
token = await logos.invoke("time.trace.rollback[phase=SIMULATE]")

# Simulate with token
result = await logos.invoke("self.liturgy.simulate", rollback_token=token)

# If simulation succeeds, commit
if result.success:
    await logos.invoke("time.trace.commit", token=token)
else:
    # Token automatically expires, state unchanged
    pass
```

---

## Liturgy Composition

```python
# Full liturgical journey as composition
journey = (
    logos.lift("self.liturgy.read")
    >> logos.lift("self.liturgy.simulate[rollback=true]")
    >> logos.lift("self.liturgy.rewrite")
)

morphism = await journey.invoke(spec_path)
```

---

## Success Criteria

1. `read` correctly composes manifests across paths
2. `simulate` executes hypothetically with rollback safety
3. `rewrite` generates valid morphisms from simulations
4. Rollback tokens properly gate mutations
5. Liturgies compose via `>>` operator

---

## Dependencies

- **Receives from**: Forest Keeper (plan paths), Law Enforcer (composition laws)
- **Provides to**: Integration Weaver (liturgical morphisms for cross-track work)

---

*"The liturgy is the oldest code. Before there were programs, there were rites."*
