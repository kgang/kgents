# kgents-bootstrap

The 7 irreducible bootstrap agents from which all of kgents can be regenerated.

## The Bootstrap Set

```
{Id, Compose, Judge, Ground, Contradict, Sublate, Fix}
```

These are the "residue" after maximal algorithmic compression—what remains
when recursion, composition, and dialectic have done all they can.

Minimal bootstrap: `{Compose, Judge, Ground}` = structure + direction + material.

## Usage

```python
from bootstrap import id_agent, compose, judge, ground, contradict, sublate, fix

# Identity
result = await id_agent.invoke(x)  # returns x

# Composition
pipeline = compose(agent_a, agent_b)
result = await pipeline.invoke(input)

# Judgment
verdict = await judge(some_agent)

# Ground truth
state = await ground()

# Contradiction detection
tension = await contradict(thesis, antithesis)

# Synthesis
if tension:
    synthesis = await sublate(tension)

# Fixed point
stable = await fix(transform, initial)
```

## Agent Types

| Agent | Symbol | Function |
|-------|--------|----------|
| **Id** | λx.x | Identity morphism (composition unit) |
| **Compose** | ∘ | Agent-that-makes-agents |
| **Judge** | ⊢ | Value function (embodies 6 principles) |
| **Ground** | ⊥ | Empirical seed (persona + world state) |
| **Contradict** | ≢ | Recognizes tension between outputs |
| **Sublate** | ↑ | Hegelian synthesis (or holds tension) |
| **Fix** | μ | Fixed-point operator (self-reference) |
