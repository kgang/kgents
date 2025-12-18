# Memory Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/brain/`*

**Confidence**: 67%
**Domain**: world
**AGENTESE Path**: world.brain

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ✅ | 5 positions |
| Operad | ✅ | 5 operations, 4 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: brain
polynomial:
  positions:
  - idle
  - capturing
  - searching
  - surfacing
  - healing
  transition: brain_transition
  directions: brain_directions
operad:
  operations:
    capture:
      arity: 1
      signature: "Brain \u2192 Crystal"
    search:
      arity: 1
      signature: "Brain \u2192 Crystals"
    surface:
      arity: 1
      signature: "Brain \u2192 Crystal (serendipitous)"
    heal:
      arity: 1
      signature: "Brain \u2192 Brain (coherent)"
    associate:
      arity: 2
      signature: "Crystal \xD7 Crystal \u2192 Link"
  laws:
    capture_idempotence: capture(capture(c)) = capture(c)
    search_coherence: "search(brain) \u2286 captures(brain)"
    heal_invariance: heal(brain).behavior = coherent_brain.behavior
    associate_symmetry: associate(a, b) ~ associate(b, a)
  extends: AGENT_OPERAD
---
```

---

## Component Details

### Polynomial: BRAIN_POLYNOMIAL

**Positions** (Phase enum):
- `idle`
- `capturing`
- `searching`
- `surfacing`
- `healing`

**Transition Function**: `brain_transition`
**Directions Function**: `brain_directions`

### Operad: BRAIN_OPERAD

**Operations**:
| Name | Arity | Signature |
|------|-------|-----------|
| `capture` | 1 | Brain → Crystal |
| `search` | 1 | Brain → Crystals |
| `surface` | 1 | Brain → Crystal (serendipitous) |
| `heal` | 1 | Brain → Brain (coherent) |
| `associate` | 2 | Crystal × Crystal → Link |

**Laws**:
- **capture_idempotence**: `capture(capture(c)) = capture(c)`
- **search_coherence**: `search(brain) ⊆ captures(brain)`
- **heal_invariance**: `heal(brain).behavior = coherent_brain.behavior`
- **associate_symmetry**: `associate(a, b) ~ associate(b, a)`

**Extends**: `AGENT_OPERAD`

---

## Source Files

- `impl/claude/agents/brain/polynomial.py`
- `impl/claude/agents/brain/operad.py`
- `impl/claude/agents/brain/node.py` (or `services/memory/node.py`)

---

*Reflected by SpecGraph | 67% confidence*
