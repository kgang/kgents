# N-Phase Cycle Protocol

> *"The 'N' is not a number—it is a variable. The cycle adapts to the task."*

## Overview

The N-Phase Cycle is a self-similar, category-theoretic lifecycle protocol for multi-session agent-human collaboration. It provides structured process without rigidity, enabling both humans and agents to navigate complex work across session boundaries.

## The Three Phases (Default)

```
SENSE → ACT → REFLECT → (loop)
```

| Phase | Purpose | Contains |
|-------|---------|----------|
| **SENSE** | Understand the terrain | Plan, Research, Develop, Strategize, Cross-Synergize |
| **ACT** | Execute with verification | Implement, QA, Test, Educate |
| **REFLECT** | Learn from outcomes | Measure, Reflect, Re-Metabolize |

Use three phases for 90% of work. Escalate to eleven only for Crown Jewels.

## The Eleven Phases (Full Ceremony)

```
PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
                    ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
                                              ↓
                                        (loop or detach)
```

Each phase is a **morphism** in a category where:
- **Objects**: Phase boundaries (states of knowledge)
- **Morphisms**: Phase executions (transformations)
- **Composition**: `(A >> B) >> C ≡ A >> (B >> C)` (associativity)
- **Identity**: Empty phase (pass-through)

## Six Invariant Properties

1. **Self-Similar** — Each phase contains a hologram of the full cycle
2. **Category-Theoretic** — Phases compose lawfully; identity and associativity hold
3. **Agent-Human Parity** — No privileged author; equally consumable by both
4. **Mutable** — The cycle evolves via re-metabolization
5. **Auto-Continuative** — Each phase generates the next prompt
6. **Accountable** — Skipped phases leave explicit debt

## Auto-Inducer Signifiers

End phase output with signifiers to control flow:

| Signifier | Unicode | Meaning |
|-----------|---------|---------|
| `⟿[PHASE]` | U+27FF | Continue to PHASE (auto-execute) |
| `⟂[REASON]` | U+27C2 | Halt, await human input |
| *(none)* | — | Await human (backwards compatible) |

**Law**: Every cycle MUST reach `⟂` eventually.

## Entropy Budget

- **Per phase**: 0.05–0.10 (5-10% for exploration)
- **Draw**: `void.entropy.sip(amount=0.07)`
- **Return unused**: `void.entropy.pour`
- **Replenish**: `void.gratitude.tithe`

## Phase Condensation

Phases in the same family can merge when complexity doesn't warrant separation:

| Family | Phases | Can Merge To |
|--------|--------|--------------|
| SENSE | PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE | Single SENSE phase |
| ACT | IMPLEMENT, QA, TEST, EDUCATE | Single ACT phase |
| REFLECT | MEASURE, REFLECT | Single REFLECT phase |

**Principle**: Three Phases compress Eleven without loss.

## Phase Selection

| Task | Phases | Rationale |
|------|--------|-----------|
| Trivial (typo) | 0 | Direct action |
| Quick win (Effort ≤ 2) | ACT only | Known pattern |
| Standard feature | 3 | SENSE → ACT → REFLECT |
| Crown Jewel | 11 | Full ceremony required |

## Metatheoretical Grounding

The N-Phase Cycle synthesizes:

| Framework | Contribution |
|-----------|--------------|
| OODA (Boyd) | Tempo, iteration, competitive advantage |
| PDCA (Deming) | Control loop, hypothesis testing |
| Double-Loop (Argyris) | Question the question, change frames |
| Reflection-in-Action (Schön) | Real-time adjustment within phases |
| Category Theory | Lawful composition, identity, associativity |

## AGENTESE Mapping

| Phase | Primary Context | Affordances |
|-------|-----------------|-------------|
| SENSE | `world.*`, `concept.*` | `manifest`, `witness` |
| ACT | `self.*`, `world.*` | `refine`, `define` |
| REFLECT | `time.*`, `void.*` | `witness`, `tithe` |

## Related

- **Implementation Guides**: `docs/skills/n-phase-cycle/`
- **Auto-Inducer Spec**: `spec/protocols/auto-inducer.md`
- **Forest Protocol**: `plans/_forest.md`, `plans/_focus.md`
- **Design Principles**: `spec/principles.md` (AD-005)

---

*"The form is the function. Each prompt generates its successor by the same principles that generated itself."*
