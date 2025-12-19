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
  extends: AGENT_OPERAD
  operations:
    # Core MPP Operations (Phase 1)
    greet:
      arity: 2
      signature: "Citizen x Citizen -> Greeting"
      description: "Initiate social contact between two citizens"
    gossip:
      arity: 2
      signature: "Citizen x Citizen -> Rumor"
      description: "Share information about a third party"
    trade:
      arity: 2
      signature: "Citizen x Citizen -> Exchange"
      description: "Exchange resources or favors"
    solo:
      arity: 1
      signature: "Citizen -> Activity"
      description: "Individual activity (work, reflect, create)"
    # Phase 2 Operations
    dispute:
      arity: 2
      signature: "Citizen x Citizen -> Tension"
      description: "Disagreement that increases tension"
    celebrate:
      arity: -1
      signature: "Citizen* -> Festival"
      description: "Collective celebration that spends surplus (variable arity)"
    mourn:
      arity: -1
      signature: "Citizen* -> Grief"
      description: "Collective mourning that strengthens bonds (variable arity)"
    teach:
      arity: 2
      signature: "Citizen x Citizen -> SkillTransfer"
      description: "Skill transfer from teacher to student"
    # Coalition Operations
    coalition_form:
      arity: -1
      signature: "Citizen* -> Coalition"
      description: "Citizens form a coalition with shared goals (variable arity)"
    coalition_dissolve:
      arity: 1
      signature: "Coalition -> Citizen*"
      description: "Coalition disbands, returning members to independent state"
  laws:
    locality: "interact(a, b) implies same_region(a, b)"
    rest_inviolability: "resting(a) implies not in_interaction(a)"
    coherence_preservation: "post(interact).a consistent with pre(interact).a"
agentese:
  path: world.town
  aspects:
    - manifest
    - citizen.list
    - citizen.get
    - citizen.create
    - citizen.update
    - converse
    - turn
    - history
    - relationships
    - gossip
    - step
---

# Town Agent Specification

> *"Not enumeration, but generation. The operad defines the grammar; interactions emerge."*

The Town Crown Jewel models a simulated community of citizens as a Westworld-inspired experience. Each citizen is a polynomial agent with mode-dependent behavior, and their interactions follow an operad grammar.

## Categorical Structure

### Polynomial (CitizenPolynomial)

Citizens exist in 5 positions (interpretive frames, not states):

| Position | Description | Valid Transitions |
|----------|-------------|-------------------|
| IDLE | Ready for interaction | -> SOCIALIZING, WORKING, REFLECTING, RESTING |
| SOCIALIZING | Engaged in social activity | -> IDLE, RESTING |
| WORKING | Performing solo work | -> IDLE, RESTING |
| REFLECTING | Internal contemplation | -> IDLE, SOCIALIZING, RESTING |
| RESTING | Mandatory rest (Right to Rest) | -> IDLE only (via wake) |

**Key Property**: Right to Rest. Citizens in RESTING phase cannot be disturbed. Only `wake` input is valid.

### Operad (TOWN_OPERAD)

The operad defines the grammar of valid citizen interactions:

**Core Operations (MPP - Minimum Playable Product)**
- `greet`: Initiate social contact (arity=2)
- `gossip`: Share information about third party (arity=2)
- `trade`: Exchange resources or favors (arity=2)
- `solo`: Individual activity (arity=1)

**Phase 2 Operations**
- `dispute`: Disagreement that increases tension (arity=2, drama_potential=0.8)
- `celebrate`: Collective celebration (variable arity, spends surplus)
- `mourn`: Collective mourning (variable arity, strengthens bonds)
- `teach`: Skill transfer (arity=2)

**Laws**
- **Locality**: Interactions require co-location
- **Rest Inviolability**: Resting citizens cannot be disturbed
- **Coherence Preservation**: Interactions cannot make citizens contradict themselves

### Sheaf (TownSheaf)

Global coherence emerges from local citizen views through sheaf gluing:
- Each citizen has local memory and relationships
- Global town state is the sheaf section satisfying gluing conditions
- Gossip degrades through telephone game (accuracy morphism)

## AGENTESE Interface

```
world.town.manifest         - Town health status
world.town.citizen.list     - List all citizens
world.town.citizen.get      - Get citizen by ID/name
world.town.citizen.create   - Create new citizen
world.town.citizen.update   - Update citizen attributes
world.town.converse         - Start conversation
world.town.turn             - Add turn to conversation
world.town.history          - Get dialogue history
world.town.relationships    - Get citizen relationships
world.town.gossip           - Inter-citizen dialogue stream (SSE)
world.town.step             - Advance simulation
```

## Metabolics (Token Economics)

Each operation has metabolic costs:

| Operation | Token Cost | Drama Potential |
|-----------|------------|-----------------|
| greet | 200 | 0.1 |
| gossip | 500 | 0.4 |
| trade | 400 | 0.3 |
| solo | 300 | 0.1 |
| dispute | 600 | 0.8 |
| celebrate | 400 * arity | 0.2 |
| mourn | 500 * arity | 0.5 |
| teach | 800 | 0.2 |

## Implementation

- **Polynomial**: `impl/claude/agents/town/polynomial.py`
- **Operad**: `impl/claude/agents/town/operad.py`
- **Node**: `impl/claude/services/town/node.py`
- **Persistence**: `impl/claude/services/town/persistence.py`

## Related Specs

- `spec/town/operad.md` - Detailed operad semantics
- `spec/town/metaphysics.md` - Barad-inspired phenomenology
- `spec/town/monetization.md` - Token economics model

---

*Canonical spec derived from implementation reflection. Last verified: 2025-12-18*
