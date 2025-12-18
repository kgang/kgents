# Town Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/town/`*

**Confidence**: 67%
**Domain**: world
**AGENTESE Path**: world.town

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ✅ | 5 positions |
| Operad | ✅ | 8 operations, 3 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: town
polynomial:
  positions:
  - idle
  - socializing
  - working
  - reflecting
  - resting
  transition: citizen_transition
  directions: citizen_directions
operad:
  operations:
    greet:
      arity: 2
      signature: "Citizen \xD7 Citizen \u2192 Greeting"
    gossip:
      arity: 2
      signature: "Citizen \xD7 Citizen \u2192 Rumor"
    trade:
      arity: 2
      signature: "Citizen \xD7 Citizen \u2192 Exchange"
    solo:
      arity: 1
      signature: "Citizen \u2192 Activity"
    dispute:
      arity: 2
      signature: "Citizen \xD7 Citizen \u2192 Tension"
    celebrate:
      arity: 1
      signature: "Citizen* \u2192 Festival"
    mourn:
      arity: 1
      signature: "Citizen* \u2192 Grief"
    teach:
      arity: 2
      signature: "Citizen \xD7 Citizen \u2192 SkillTransfer"
  laws:
    locality: interact(a, b) implies same_region(a, b)
    rest_inviolability: resting(a) implies not in_interaction(a)
    coherence_preservation: post(interact).a consistent with pre(interact).a
  extends: AGENT_OPERAD
---
```

---

## Component Details

### Polynomial: TOWN_POLYNOMIAL

**Positions** (Phase enum):
- `idle`
- `socializing`
- `working`
- `reflecting`
- `resting`

**Transition Function**: `citizen_transition`
**Directions Function**: `citizen_directions`

### Operad: TOWN_OPERAD

**Operations**:
| Name | Arity | Signature |
|------|-------|-----------|
| `greet` | 2 | Citizen × Citizen → Greeting |
| `gossip` | 2 | Citizen × Citizen → Rumor |
| `trade` | 2 | Citizen × Citizen → Exchange |
| `solo` | 1 | Citizen → Activity |
| `dispute` | 2 | Citizen × Citizen → Tension |
| `celebrate` | 1 | Citizen* → Festival |
| `mourn` | 1 | Citizen* → Grief |
| `teach` | 2 | Citizen × Citizen → SkillTransfer |

**Laws**:
- **locality**: `interact(a, b) implies same_region(a, b)`
- **rest_inviolability**: `resting(a) implies not in_interaction(a)`
- **coherence_preservation**: `post(interact).a consistent with pre(interact).a`

**Extends**: `AGENT_OPERAD`

---

## Source Files

- `impl/claude/agents/town/polynomial.py`
- `impl/claude/agents/town/operad.py`
- `impl/claude/agents/town/node.py` (or `services/town/node.py`)

---

*Reflected by SpecGraph | 67% confidence*
