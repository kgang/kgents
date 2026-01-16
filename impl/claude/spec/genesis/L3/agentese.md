---
genesis_id: "genesis:L3:agentese"
layer: 3
layer_name: "architecture"
galois_loss: 0.1
confidence: 0.9
color: "#C08552"
derives_from: ['genesis:L0:morphism', 'genesis:L1:judge', 'genesis:L2:composable']
tags: ['L3', 'agentese', 'architecture', 'genesis', 'protocol']
---

# AGENTESE — The Protocol IS the API

> *"The noun is a lie. There is only the rate of change."*

**Galois Loss**: 0.10 (cleanest architectural derivation)

## Derivation

```
A2 (Morphism) → JUDGE → COMPOSABLE → AGENTESE
"Handles ARE morphisms; paths compose as morphism chains"
```

## The Five Contexts

```
CONTEXT     PURPOSE                         EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
world.*     The External                    world.house.manifest
self.*      The Internal                    self.memory.capture
concept.*   The Abstract                    concept.atelier.sketch
void.*      The Accursed Share              void.entropy.sip
time.*      The Temporal                    time.witness.mark
```

## Why "The Noun Is a Lie"

Traditional APIs treat entities as primary: `GET /users/123`.

AGENTESE inverts: **the action is primary**. Entities emerge from patterns of actions.

```python
# Traditional (noun-first)
user = await api.get("/users/123")

# AGENTESE (verb-first)
await logos.invoke("self.identity.rename", observer, new_name="New Name")
```

## Observer-Dependent Projection

Handles return different results for different observers:

```python
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

This is not polymorphism—it's **observer-dependent projection**.
