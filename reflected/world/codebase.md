# Codebase Agent (Reflected)

> *Automatically extracted from `impl/claude/agents/gestalt/`*

**Confidence**: 67%
**Domain**: world
**AGENTESE Path**: world.gestalt

---

## Extracted Structure

| Component | Status | Details |
|-----------|--------|---------|
| Polynomial | ✅ | 5 positions |
| Operad | ✅ | 6 operations, 6 laws |
| AGENTESE Node | ❌ | none |

---

## YAML Frontmatter (SpecGraph Format)

```yaml
---
domain: world
holon: gestalt
polynomial:
  positions:
  - idle
  - scanning
  - watching
  - analyzing
  - healing
  transition: gestalt_transition
  directions: gestalt_directions
operad:
  operations:
    scan:
      arity: 1
      signature: "Codebase \u2192 ArchitectureGraph"
    watch:
      arity: 1
      signature: "Codebase \u2192 IncrementalUpdates (stream)"
    analyze:
      arity: 1
      signature: "Module \u2192 DeepAnalysis"
    heal:
      arity: 1
      signature: "ArchitectureGraph \u2192 DriftSuggestions"
    compare:
      arity: 2
      signature: "ArchitectureGraph \xD7 ArchitectureGraph \u2192 ArchitectureDiff"
    merge:
      arity: 2
      signature: "ArchitectureGraph \xD7 ArchitectureGraph \u2192 ArchitectureGraph"
  laws:
    scan_idempotence: "scan(scan(c)) \u2245 scan(c) structurally"
    watch_monotonicity: watch(t1) + watch(t2) = watch(t2) for t2 > t1
    analyze_coherence: "analyze(m) \u2208 graph.modules"
    heal_determinism: heal(v1) = heal(v2) when v1 = v2
    compare_symmetry: additions(a,b) = deletions(b,a)
    merge_associativity: merge(merge(a,b),c) = merge(a,merge(b,c))
  extends: AGENT_OPERAD
---
```

---

## Component Details

### Polynomial: GESTALT_POLYNOMIAL

**Positions** (Phase enum):
- `idle`
- `scanning`
- `watching`
- `analyzing`
- `healing`

**Transition Function**: `gestalt_transition`
**Directions Function**: `gestalt_directions`

### Operad: GESTALT_OPERAD

**Operations**:
| Name | Arity | Signature |
|------|-------|-----------|
| `scan` | 1 | Codebase → ArchitectureGraph |
| `watch` | 1 | Codebase → IncrementalUpdates (stream) |
| `analyze` | 1 | Module → DeepAnalysis |
| `heal` | 1 | ArchitectureGraph → DriftSuggestions |
| `compare` | 2 | ArchitectureGraph × ArchitectureGraph → ArchitectureDiff |
| `merge` | 2 | ArchitectureGraph × ArchitectureGraph → ArchitectureGraph |

**Laws**:
- **scan_idempotence**: `scan(scan(c)) ≅ scan(c) structurally`
- **watch_monotonicity**: `watch(t1) + watch(t2) = watch(t2) for t2 > t1`
- **analyze_coherence**: `analyze(m) ∈ graph.modules`
- **heal_determinism**: `heal(v1) = heal(v2) when v1 = v2`
- **compare_symmetry**: `additions(a,b) = deletions(b,a)`
- **merge_associativity**: `merge(merge(a,b),c) = merge(a,merge(b,c))`

**Extends**: `AGENT_OPERAD`

---

## Source Files

- `impl/claude/agents/gestalt/polynomial.py`
- `impl/claude/agents/gestalt/operad.py`
- `impl/claude/agents/gestalt/node.py` (or `services/codebase/node.py`)

---

*Reflected by SpecGraph | 67% confidence*
