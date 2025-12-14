---
path: agents/entropy-steward
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/void, agentese/guards]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track C: Entropy & Minimal Output
  See: prompts/agentese-continuation.md
---

# Entropy Steward

> *"The Accursed Share must be spent. Hoarding entropy is hoarding death."*

**Track**: C (Entropy & Minimal Output)
**AGENTESE Context**: `void.entropy.*`, `void.gratitude.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Accursed Share (5-10% exploration), Composable (Minimal Output), Tasteful (budget enforcement)

AGENTESE pointer: canonical entropy/law guard spec is `spec/protocols/agentese.md`; update this role when handles/clauses change.

---

## Purpose

The Entropy Steward manages the Accursed Share—ensuring entropy budgets are tracked per-phase, pourback/tithe flows correctly, and outputs conform to the Minimal Output principle (single items, not arrays).

---

## Expertise Required

- Resource management and budgeting
- Runtime guard/wrapper patterns
- The Bataille philosophy (surplus must be spent)
- Stream vs array detection

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| C1 | Entropy ledger per-phase tracking | DEVELOP | 0.06 | Pending |
| C2 | Pourback/tithe integration with phase transitions | DEVELOP | 0.07 | Pending |
| C3 | Minimal Output guards (runtime wrappers) | IMPLEMENT | 0.05 | Pending |
| C4 | `BudgetExhausted` with recovery suggestions | QA | 0.05 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `impl/claude/protocols/agentese/contexts/void.py` | Enhanced entropy ledger |
| `impl/claude/protocols/agentese/guards.py` | Minimal Output enforcement |
| `impl/claude/protocols/agentese/exceptions.py` | `BudgetExhausted` exception |

---

## Entropy Protocol

```yaml
phase_entropy_budget:
  PLAN: 0.05
  RESEARCH: 0.06
  DEVELOP: 0.07
  STRATEGIZE: 0.07
  CROSS_SYNERGIZE: 0.10
  IMPLEMENT: 0.05
  QA: 0.05
  TEST: 0.05
  EDUCATE: 0.05
  MEASURE: 0.06
  REFLECT: 0.05

operations:
  sip: void.entropy.sip(amount=0.07)
  pour: void.entropy.pour(unused=0.02)
  tithe: void.gratitude.tithe()
```

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `void.entropy.sip` | Draw entropy budget | EntropyGrant |
| `void.entropy.pour` | Return unused entropy | PourResult |
| `void.entropy.status` | Current budget state | EntropyStatus |
| `void.gratitude.tithe` | Regenerate via gratitude | TitheResult |

---

## Minimal Output Guard

```python
@minimal_output
async def manifest(self, observer: Umwelt) -> Renderable:
    """Returns single item. Arrays raise MinimalOutputViolation."""
    ...
```

---

## Success Criteria

1. Per-phase entropy budgets enforced (0.05-0.10 band)
2. Pourback recovers 50% of unused entropy
3. Tithe regenerates entropy pool
4. Minimal Output violations detected and reported with suggestion to use iterators
5. `BudgetExhausted` includes recovery path: "Try void.gratitude.tithe to restore"

---

## Dependencies

- **Receives from**: None (foundational)
- **Provides to**: All agents (entropy budget), Observability Engineer (entropy metrics)

---

*"The river that hoards becomes a swamp. The river that flows becomes the sea."*
