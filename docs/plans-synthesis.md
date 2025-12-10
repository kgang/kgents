# Plans Synthesis: Core Ideas to Keep

**Consolidated from**: cli-integration-plan.md, d-gent-analysis-and-vision.md, g-gent_implementation_plan.md, m-gent-treatment.md, n-gent-treatment.md, psi-gent-synthesis.md, structural_economics_bg_integration.md

---

## 1. CLI Architecture (from cli-integration-plan.md)

**Key Concepts**:
- **Intent Layer**: 10 verbs (`new`, `run`, `check`, `think`, `watch`, `find`, `fix`, `speak`, `judge`, `do`) over 18 genera
- **Hollow Shell**: Lazy loading for <50ms startup
- **Flowfiles**: YAML-based composition (not string pipelines)
- **Sympathetic Errors**: Error messages that help, not just fail
- **MCP Bidirectional**: Both client AND server

**Must Keep**: Intent-first design, lazy loading pattern, flowfile composition model

---

## 2. D-gent Vision (from d-gent-analysis-and-vision.md)

**Key Concepts**:
- **Three-Brain Noosphere**: Semantic (vectors) + Temporal (events) + Relational (graphs)
- **UnifiedMemory**: All memory modes unified via lens algebra
- **Memory Garden Metaphor**: Seeds, Saplings, Trees, Compost, Flowers, Mycelium

**Implementation Status**: Phases 2-3 (Vector/Graph/Stream) complete via `unified.py`

**Must Keep**: Noosphere architecture (implemented), lens composition, adaptive persistence

---

## 3. G-gent Implementation (from g-gent_implementation_plan.md)

**Key Concepts**:
- **Tongue Artifact**: DSL as reusable, catalogable artifact
- **Grammar Levels**: Schema (Pydantic) < Command (BNF) < Recursive (Lark)
- **Safety Through Structure**: Constraints become grammatically impossible

**Implementation Status**: Core implemented (types.py, tongue.py, synthesis.py, grammarian.py)

**Must Keep**: Tongue as morphism, constraint crystallization, P-gent/J-gent integration

---

## 4. M-gent Architecture (from m-gent-treatment.md)

**Key Concepts**:
- **Holographic Memory**: Generative reconstruction, not retrieval
- **Three-Tier Memory**: Sensory (volatile) -> Working (cached) -> Long-term (holographic)
- **Memory Modes**: Recollection, Consolidation, Prospective (predictive), EthicalGeometry
- **Forgetting as Feature**: Ebbinghaus curve, spaced repetition

**Must Keep**: Holographic metaphor (architecturally load-bearing), tiered memory, D-gent integration

---

## 5. N-gent Framework (from n-gent-treatment.md)

**Key Concepts**:
- **Narrative vs Logs**: Stories have structure, arc, meaning; logs are just data
- **ThoughtTrace + NarrativeLog + Chronicle**: Atom -> Story -> Multi-agent Saga
- **Replay/Resurrection**: Time-travel debugging via serialized input snapshots
- **Unreliable Narrator**: Epistemic humility encoded in architecture
- **Ergodic Narratives**: Branching timelines, counterfactual exploration

**Implementation Status**: Core (Phases 1-6) complete

**Must Keep**: Writer monad pattern (StorytellerAgent), replay capability, epistemic features

---

## 6. Psi-gent Integration (from psi-gent-synthesis.md)

**Key Concepts**:
- **4-Axis Tensor**: Z (MHC resolution), X (Jungian shadow), Y (Lacanian topology), T (B-gent value)
- **HolographicMetaphorLibrary**: Fuzzy recall, learning, compression (M-gent integration)
- **MetaphorUmwelt**: Agent-specific metaphor spaces (each genus sees different metaphors)
- **MetaphorEvolution**: Dialectical metaphor improvement (E-gent integration)

**Key Integrations**:
| # | Integration | From | To |
|---|-------------|------|-----|
| 1 | Holographic Metaphors | M-gent | Psi-gent |
| 2 | Metaphor Forensics | N-gent | Psi-gent |
| 3 | ValueTensor Deep | B-gent | Psi-gent |
| 4 | Metaphor Umwelt | Umwelt | Psi-gent |
| 5 | Shadow Metaphors | H-gent | Psi-gent |
| 6 | Metaphor Evolution | E-gent | Psi-gent |

**Must Keep**: Psi as integration nexus, 4-axis tensor model, agent-specific umwelts

---

## 7. Structural Economics B×G (from structural_economics_bg_integration.md)

**Key Concepts**:
- **Semantic Zipper**: Compress inter-agent communication via pidgins (90% token reduction)
- **Fiscal Constitution**: Financial ops structurally safe (bankruptcy grammatically impossible)
- **Syntax Tax**: Price by Chomsky hierarchy (Regular < CF < Turing-Complete)
- **JIT Efficiency**: G-gent grammar + J-gent compile + B-gent measure latency value

**The Formula**: `B-gent × G-gent = Structural Economics`

**Must Keep**: Four pillars (Compression, Constitution, Syntax Tax, JIT), profit-sharing model

---

## Implementation Priorities

### Highest Priority (Integration Nexus)
1. **Psi-gent**: 0% implemented, highest integration potential
2. **CLI MCP Server**: Enables Claude/Cursor to help build rest

### High Priority (Partially Implemented)
3. **M-gent Holographic Layer**: Build on existing D-gent UnifiedMemory
4. **B×G Structural Economics**: Build on existing B-gent CentralBank + G-gent Tongue

### Medium Priority (Core Complete)
5. **N-gent Epistemic Features**: UnreliableNarrator, RashomonNarrator
6. **CLI Intent Layer**: Wire verbs to existing genera

---

## Cross-Cutting Themes

1. **Memory is Morphism**: M-gent (cue->reconstruction), N-gent (execution->narrative), D-gent (state->lens)
2. **Economics as Constraint**: B-gent budgets + G-gent grammars = structural impossibility of bad behavior
3. **Observation Hierarchy**: O-gent telemetry -> N-gent narrative -> Psi-gent metaphor
4. **Agent-Specific Worlds**: Umwelt protocol applies to metaphors, memory, perception
5. **Time Travel**: N-gent replay, D-gent temporal witness, counterfactual exploration

---

*This synthesis preserves the essential architecture from 7 planning documents (~9,000 lines) in ~150 lines.*
