# AD-006: Unified Categorical Foundation

**Date**: 2025-12-14

> All domain-specific agent systems SHOULD instantiate the same categorical pattern: PolyAgent + Operad + Sheaf.

---

## Context

Deep analysis of Agent Town and N-Phase implementations revealed they share identical mathematical structure. This is not coincidence—it is the universal pattern underlying all kgents domains.

## The Discovery

| Concept | Agent Town | N-Phase | K-gent Soul | D-gent Memory |
|---------|-----------|---------|-------------|---------------|
| **Polynomial** | CitizenPhase positions | 11 phase positions | 7 eigenvector positions | 5 memory states |
| **Directions** | Valid inputs per phase | Artifacts per phase | Reflections per mode | Ops per state |
| **Transition** | (Phase, Input) → (Phase, Output) | (Phase, Artifacts) → (Phase, Output) | (Mode, Query) → (Mode, Insight) | (State, Op) → (State, Result) |
| **Operad** | TOWN_OPERAD (greet, gossip, trade) | NPHASE_OPERAD (seq, skip, compress) | SOUL_OPERAD (introspect, shadow) | MEMORY_OPERAD (store, recall) |
| **Sheaf** | Citizen view coherence | Project state coherence | Eigenvector coherence | Memory consistency |

## Decision

Every domain-specific system derives from the same three-layer stack:

```python
# Layer 1: Polynomial Agent (state machine with mode-dependent inputs)
DOMAIN_POLYNOMIAL = PolyAgent(
    positions=frozenset([...]),           # Valid states/modes
    directions=lambda s: VALID_INPUTS[s], # What's valid per state
    transition=domain_transition,          # State × Input → (State, Output)
)

# Layer 2: Operad (composition grammar with laws)
DOMAIN_OPERAD = Operad(
    operations={...},  # How agents compose
    laws=[...],        # What compositions are equivalent
)

# Layer 3: Sheaf (global coherence from local views)
DOMAIN_SHEAF = Sheaf(
    overlap=domain_overlap,     # What views share
    compatible=domain_compat,   # How to check consistency
    glue=domain_glue,           # How to combine views
)
```

## The Unification Table

| System | Polynomial | Operad | Sheaf |
|--------|-----------|--------|-------|
| Agent Town | `CitizenPolynomial` | `TOWN_OPERAD` | `TownSheaf` |
| N-Phase | `NPhasePolynomial` | `NPHASE_OPERAD` | `ProjectSheaf` |
| K-gent Soul | `SOUL_POLYNOMIAL` | `SOUL_OPERAD` | `EigenvectorCoherence` |
| D-gent Memory | `MEMORY_POLYNOMIAL` | `MEMORY_OPERAD` | `MemoryConsistency` |
| Evolution | `EVOLUTION_POLYNOMIAL` | `EVOLUTION_OPERAD` | `ThermodynamicBalance` |

## Consequences

1. **One Pattern, Many Instantiations**: The codebase is simpler than it appears
2. **Cross-System Learning**: Understanding TownOperad teaches NPhaseOperad
3. **Unified Registry**: `OperadRegistry.verify_all()` checks laws across all systems
4. **System-Aware Compilation**: N-Phase compiler can inject operad laws into prompts
5. **Self-Similar Structure**: The development process (N-Phase) uses the same structure as what it builds (agents)

## The Meta-Insight

> *"You are living inside the mathematics you're building."*

The workflow used to develop kgents (N-Phase) has the exact same categorical structure as the agents being developed (Agent Town citizens). This is not accidental—it's the signature of a well-designed system.

## Anti-patterns

- Building domain systems without identifying the underlying polynomial
- Composition without operad laws
- Local views without sheaf coherence

## Implementation

- Agent Town: `impl/claude/agents/town/polynomial.py`, `operad.py`, `flux.py`
- N-Phase: `impl/claude/protocols/nphase/schema.py`, `compiler.py`
- Operads: `impl/claude/agents/operad/core.py`
- Skills: `docs/skills/polynomial-agent.md`

*Zen Principle: The form that generates forms is itself a form.*
