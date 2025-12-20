# Prompt: The Witness and The Muse → Specs and Plans

> *Use this prompt with `/hydrate` to have an agent turn the brainstorm into full specifications and implementation plans.*

---

## Task

Transform the brainstorm at `brainstorming/2025-12-19-the-witness-and-the-muse.md` into:

1. **Two specification files** following the kgents spec template
2. **One implementation plan** with phased deliverables
3. **AGENTESE node registrations** ready to implement

---

## Context Files to Read First

Before starting, read these files to understand the patterns:

### Voice & Intent
- `plans/_focus.md` — Kent's wishes and constraints (NEVER overwrite)
- `spec/principles.md` — The seven principles + architectural decisions

### Spec Templates (Follow These Patterns)
- `spec/protocols/agentese.md` — Example of a mature protocol spec
- `spec/agents/flux.md` — Example of agent spec with polynomial + operad
- `docs/skills/spec-template.md` — The canonical spec structure

### Implementation Patterns
- `docs/skills/crown-jewel-patterns.md` — 14 patterns to apply
- `docs/skills/polynomial-agent.md` — How to define PolyAgent
- `docs/skills/agentese-node-registration.md` — @node decorator patterns

### Existing Infrastructure (Wire, Don't Build)
- `impl/claude/agents/poly/` — PolyAgent implementation
- `impl/claude/agents/operad/` — Operad implementation
- `impl/claude/agents/sheaf/` — Sheaf implementation
- `impl/claude/agents/flux/` — FluxAgent implementation
- `impl/claude/protocols/agentese/` — AGENTESE gateway and nodes

### The Brainstorm
- `brainstorming/2025-12-19-the-witness-and-the-muse.md` — Source material

---

## Deliverables

### 1. Spec: The Witness (`spec/services/witness.md`)

Structure:
```markdown
# The Witness

> *"I am the membrane between event and meaning."*

## Overview
[One paragraph vision]

## Categorical Foundation

### The Polynomial
[Full WITNESS_POLYNOMIAL definition with states and transitions]

### The Operad
[Full WITNESS_OPERAD with operations and laws]

### The Sheaf
[WitnessSheaf with local views, gluing condition, global section]

## Core Concepts

### Experience Crystal
[Frozen dataclass with all fields]

### Event Types
[WitnessEvent variants]

## AGENTESE Interface

### Node Registration
[Full @node decorator with contracts]

### Aspects
[Each aspect with request/response contracts]

### Affordances
[Permission matrix by observer archetype]

## kgentsd Integration

### Event Sources
[What events trigger the witness]

### Flux Lifting
[WitnessFlux definition]

## Cross-Jewel Integration

### Consumers
[How Brain, Gardener, Muse consume Witness output]

### Events Emitted
[SynergyBus events for other jewels]

## Visual Projections

### CLI
[ASCII art for terminal]

### Web
[Component structure]

## Laws

[Numbered list of laws with verification status]

## Anti-Patterns

[What NOT to do]
```

### 2. Spec: The Muse (`spec/services/muse.md`)

Same structure as above, adapted for The Muse:
- MUSE_POLYNOMIAL with states
- MUSE_OPERAD with operations
- StoryArc and Whisper data structures
- Dependency on Witness crystals
- WhisperEngine with dismissal memory

### 3. Implementation Plan (`plans/witness-muse-implementation.md`)

Structure:
```markdown
# The Witness and The Muse: Implementation Plan

## Overview
[Vision + dependencies]

## Phase 0: Foundation (Week 1)
### P0.1: Witness Polynomial
- [ ] Define WitnessState enum
- [ ] Implement WITNESS_POLYNOMIAL
- [ ] Write polynomial tests (property-based)

### P0.2: Core Event Capture
- [ ] WitnessEvent dataclass
- [ ] Basic event observation
- [ ] D-gent storage adapter

## Phase 1: Crystallization (Week 2)
### P1.1: Experience Crystal
- [ ] ExperienceCrystal dataclass
- [ ] Crystallization trigger logic
- [ ] Narrative synthesis (K-gent integration)

### P1.2: AGENTESE Node
- [ ] @node("time.witness")
- [ ] Contracts for all aspects
- [ ] Basic tests

## Phase 2: Muse Foundation (Week 3)
### P2.1: Muse Polynomial
- [ ] MuseState enum
- [ ] MUSE_POLYNOMIAL
- [ ] Story arc detection

### P2.2: Whisper Engine
- [ ] Whisper dataclass
- [ ] Dismissal memory
- [ ] Pairing logic

## Phase 3: Integration (Week 4)
### P3.1: kgentsd Wiring
- [ ] WitnessFlux
- [ ] MuseFlux
- [ ] Event subscription

### P3.2: Cross-Jewel
- [ ] Brain integration
- [ ] Gardener integration
- [ ] SynergyBus events

## Phase 4: Projection (Week 5)
### P4.1: CLI Projection
- [ ] Witness timeline view
- [ ] Muse arc view
- [ ] Whisper overlay

### P4.2: Web Projection
- [ ] WitnessChamber component
- [ ] MuseArc component
- [ ] WhisperToast component

## Success Criteria
- [ ] 100+ tests for Witness
- [ ] 80+ tests for Muse
- [ ] All AGENTESE paths registered
- [ ] kgentsd passive operation working
- [ ] Cross-jewel events flowing

## Dependencies
- kgentsd event architecture (plans/kgentsd-event-architecture.md)
- D-gent persistence
- K-gent for narrative synthesis
```

---

## Principles to Apply

### From `spec/principles.md`

1. **Tasteful**: Each jewel has one clear purpose
2. **Composable**: Full PolyAgent + Operad + Sheaf stack
3. **Generative**: Specs should be regenerable from the brainstorm
4. **Joy-Inducing**: Whispers, not shouts; earned encouragement

### From `_focus.md`

- *"Daring, bold, creative, opinionated but not gaudy"*
- *"Tasteful > feature-complete"*
- *"Depth over breadth"*

### Architectural Decisions to Honor

- **AD-002**: Polynomial Generalization (use PolyAgent, not Agent)
- **AD-006**: Unified Categorical Foundation (PolyAgent + Operad + Sheaf)
- **AD-009**: Metaphysical Fullstack (services/ owns adapters + frontend)
- **AD-010**: Habitat Guarantee (every path has a projection)

---

## Anti-Sausage Check

Before finishing, verify:
- [ ] Did I preserve the opinionated stances from the brainstorm?
- [ ] Did I use Kent's voice anchors where appropriate?
- [ ] Is this still daring/bold/creative, or did I make it safe?
- [ ] Did I wire to existing infrastructure rather than build new?

---

## Output Locations

Write files to:
- `spec/services/witness.md`
- `spec/services/muse.md`
- `plans/witness-muse-implementation.md`

Do NOT modify:
- `plans/_focus.md` (Kent's voice only)
- Any existing specs without explicit instruction

---

## Execution

Run with:
```bash
/hydrate Transform brainstorming/2025-12-19-the-witness-and-the-muse.md into specs and plans following the instructions in brainstorming/2025-12-19-witness-muse-spec-prompt.md
```

---

*"The spec is compression. The plan is the path. The implementation is the proof."*
