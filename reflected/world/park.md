# Park Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/park/`*

**Confidence**: 33%
**Domain**: world
**AGENTESE Path**: world.park

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ❌ | 0 positions |
| Operad | ✅ | 8 operations, 6 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: park
operad:
  operations:
    observe:
      arity: 1
      signature: Session -> Metrics
    evaluate:
      arity: 2
      signature: (Metrics, Config) -> InjectionDecision
    build_tension:
      arity: 1
      signature: Metrics -> TensionState
    inject:
      arity: 2
      signature: (SerendipityInjection, Session) -> InjectionResult
    cooldown:
      arity: 1
      signature: Duration -> CooldownState
    intervene:
      arity: 1
      signature: DifficultyAdjustment -> InterventionResult
    director_reset:
      arity: 0
      signature: () -> Observing
    abort:
      arity: 0
      signature: () -> Observing
  laws:
    consent_constraint: inject(i, s) requires consent_debt(s) <= threshold
    cooldown_constraint: inject(i, s) requires time_since_injection >= min_cooldown
    tension_flow: build_tension(m) -> inject(_, s) | observe(s) within T
    intervention_isolation: intervene(a) = complete(a) | abort()
    observe_identity: observe(observe(s)) = observe(s)
    reset_to_observe: reset() -> OBSERVING
  extends: AGENT_OPERAD
---
```

---

## Component Details

### Operad: PARK_OPERAD

**Operations**:
| Name | Arity | Signature |
|------|-------|-----------|
| `observe` | 1 | Session -> Metrics |
| `evaluate` | 2 | (Metrics, Config) -> InjectionDecision |
| `build_tension` | 1 | Metrics -> TensionState |
| `inject` | 2 | (SerendipityInjection, Session) -> InjectionResult |
| `cooldown` | 1 | Duration -> CooldownState |
| `intervene` | 1 | DifficultyAdjustment -> InterventionResult |
| `director_reset` | 0 | () -> Observing |
| `abort` | 0 | () -> Observing |

**Laws**:
- **consent_constraint**: `inject(i, s) requires consent_debt(s) <= threshold`
- **cooldown_constraint**: `inject(i, s) requires time_since_injection >= min_cooldown`
- **tension_flow**: `build_tension(m) -> inject(_, s) | observe(s) within T`
- **intervention_isolation**: `intervene(a) = complete(a) | abort()`
- **observe_identity**: `observe(observe(s)) = observe(s)`
- **reset_to_observe**: `reset() -> OBSERVING`

**Extends**: `AGENT_OPERAD`

---

## Source Files

- `impl/claude/agents/park/polynomial.py`
- `impl/claude/agents/park/operad.py`
- `impl/claude/agents/park/node.py` (or `services/park/node.py`)

---

*Reflected by SpecGraph | 33% confidence*
