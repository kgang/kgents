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
    greet:
      arity: 2
      signature: "Citizen × Citizen → Greeting"
      description: "Initiate social contact"
    gossip:
      arity: 2
      signature: "Citizen × Citizen → Rumor"
      description: "Share information about third party"
    trade:
      arity: 2
      signature: "Citizen × Citizen → Exchange"
      description: "Exchange resources or favors"
    solo:
      arity: 1
      signature: "Citizen → Activity"
      description: "Individual activity"
  laws:
    locality: "interact(a, b) implies same_region(a, b)"
    rest_inviolability: "resting(a) implies not in_interaction(a)"
    coherence_preservation: "post(interact).a consistent with pre(interact).a"
agentese:
  path: world.town
  aspects:
    - manifest
    - witness
    - inhabit
---

# Town Agent Spec (Sample with Frontmatter)

> *"Not enumeration, but generation. The operad defines the grammar; interactions emerge."*

This is a sample spec file demonstrating the YAML frontmatter format for SpecGraph compilation.

## Overview

The Town agent models a simulated community of citizens with:
- **Polynomial state machine** for citizen behavior phases
- **Operad grammar** for valid interaction compositions
- **AGENTESE path** for discoverability

## Usage

Compile this spec:
```bash
kg self.system.compile spec_path=spec/town/sample-compiled.md dry_run=true
```

Reflect the implementation:
```bash
kg self.system.reflect impl_path=agents/town
```

---

*This is a demonstration spec file. The actual Town implementation is in `impl/claude/agents/town/`.*
