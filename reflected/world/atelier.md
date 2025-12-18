# Atelier Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/atelier/`*

**Confidence**: 33%
**Domain**: world
**AGENTESE Path**: world.atelier

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ✅ | 5 positions |
| Operad | ❌ | 0 operations, 0 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: atelier
polynomial:
  positions:
  - gathering
  - creating
  - reviewing
  - exhibiting
  - closed
  transition: workshop_transition
  directions: workshop_directions
---
```

---

## Component Details

### Polynomial: ATELIER_POLYNOMIAL

**Positions** (Phase enum):
- `gathering`
- `creating`
- `reviewing`
- `exhibiting`
- `closed`

**Transition Function**: `workshop_transition`
**Directions Function**: `workshop_directions`

---

## Source Files

- `impl/claude/agents/atelier/polynomial.py`
- `impl/claude/agents/atelier/operad.py`
- `impl/claude/agents/atelier/node.py` (or `services/atelier/node.py`)

---

*Reflected by SpecGraph | 33% confidence*
