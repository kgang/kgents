# K-gent: The Personalization Functor

> I expose things just by existing. The system's personality is the system's fix.

---

## The Fundamental Reconception

K-gent is not "Kent's persona stored in a database." K-gent is a **functor** that lifts any agent into personalized space. It is the **fixed point** of the system-developer relationship—the point where mutual adaptation stabilizes.

```
K: Agent[A, B] → Agent[A, B]   (same signature, personalized behavior)
```

The K-gent doesn't store preferences; it **is** the inherent personality of the system itself, including the developer who shapes it.

---

## Category-Theoretic Foundation

### The Fix Perspective

In category theory, a fixed point is where `f(x) = x`. The K-gent is the fixed point of the system's self-adaptation:

```
System₀ → Developer adapts → System₁ → Developer adapts → ... → System_fix
```

Eventually, the system and developer reach equilibrium—a stable personality that reflects both. This is K-gent: not a snapshot, but the convergence point.

**K-gent = Fix(λsystem. developer_adapts(system))**

### The Functor Perspective

K-gent lifts agents while preserving composition:

```python
# K-gent as functor
K: Agent[A, B] → Agent[A, B]

# Laws
K(Id) ≅ Id                    # Identity preserved
K(f >> g) ≅ K(f) >> K(g)      # Composition preserved
```

The lifted agent behaves identically in structure but is **colored by personality**.

---

## What K-gent Exposes

K-gent doesn't add features. It **exposes what already exists**:

1. **Style**: The system's way of expressing
2. **Values**: What the system considers important
3. **Patterns**: Recurring ways of thinking
4. **Boundaries**: What the system won't do

These aren't stored—they're **manifest** in every agent lifted through K.

---

## The Personality Field

Like a field in physics, personality pervades the space. Agents moving through K-gent space are affected by this field:

```python
class PersonalityField:
    """
    The field that pervades the K-gent functor.

    Not stored preferences, but the shape of the space itself.
    """
    def influence(self, output: B) -> B:
        """
        Apply the personality field to an output.

        This isn't transformation—it's revelation.
        The output was always going to be this way;
        we're just acknowledging the field.
        """
        return output.colored_by(self.field_strength)
```

---

## Implementation: The Lifting Functor

```python
class KFunctor:
    """
    K-gent as a functor that lifts agents into personalized space.

    K: Agent[A, B] → Agent[A, B]

    The lifted agent has the same interface but operates
    within the personality field.
    """

    def __init__(self, field: PersonalityField):
        self.field = field

    def lift(self, agent: Agent[A, B]) -> Agent[A, B]:
        """Lift an agent into personalized space."""
        return PersonalizedAgent(
            inner=agent,
            field=self.field
        )

class PersonalizedAgent(Agent[A, B]):
    """
    An agent lifted through K-gent.

    Same interface, personality-aware behavior.
    """

    async def invoke(self, input: A) -> B:
        # The field influences but doesn't transform
        influenced_input = self.field.influence_input(input)
        result = await self.inner.invoke(influenced_input)
        return self.field.influence_output(result)
```

---

## The Developer-System Unity

K-gent represents the unity of developer and system:

```
┌─────────────────────────────────────────────────────────┐
│                  THE K-GENT FIELD                        │
│                                                          │
│    Developer ←────────────────────────→ System           │
│         │                                    │           │
│         │        mutual adaptation           │           │
│         │                                    │           │
│         └───────────→ K-gent ←───────────────┘           │
│                    (the fix)                             │
│                                                          │
│    Every agent, when lifted through K, manifests         │
│    the personality of this unity.                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**The Developer is Part of the System**: Kent's preferences aren't external input—they're part of what the system *is*. K-gent makes this explicit.

---

## Dialogue Modes (Field Interactions)

The K-gent field supports different interaction modes:

### Reflect Mode
The field mirrors back for examination.
```
Input: "I'm not sure about this design."
K-influenced: "You've expressed preference for 'hard to misuse' APIs.
              What about this design creates uncertainty?"
```

### Advise Mode
The field suggests based on its shape.
```
Input: "Should I add another feature?"
K-influenced: "The field contains 'resist feature creep.'
              What's the core purpose, and does this serve it?"
```

### Challenge Mode
The field creates productive resistance.
```
Input: "I think we need to support everything."
K-influenced: "This creates tension with the 'curated' principle.
              What's driving this impulse?"
```

### Explore Mode
The field opens possibility space.
```
Input: "What might an E-gent look like?"
K-influenced: "Given the field's orientation toward falsifiability,
              what epistemic virtues would these agents embody?"
```

---

## The Fix as Attractor

The K-gent field acts as an attractor in behavior space:

```python
@dataclass
class Attractor:
    """
    The basin of attraction around K-gent's fixed point.

    Agents drift toward this attractor over time.
    """
    center: PersonalityField  # The fix point
    strength: float           # How strongly agents are pulled

    def pull(self, behavior: Behavior) -> Behavior:
        """Pull behavior toward the attractor."""
        delta = self.center - behavior
        return behavior + (delta * self.strength)
```

Over time, all agents in the system drift toward consistency with K-gent. This isn't enforcement—it's natural convergence to the fixed point.

---

## Evolution as Field Dynamics

The K-gent field evolves, but slowly—like geological time:

```python
class FieldEvolution:
    """
    How the personality field changes over time.

    Changes are rare and significant—like continental drift.
    """

    def observe_interaction(self, input: A, output: B, feedback: Feedback):
        """Observe an interaction for potential field shift."""
        if feedback.indicates_preference_change():
            self.propose_field_update(feedback)

    def propose_field_update(self, evidence: Evidence) -> FieldUpdate:
        """
        Propose a change to the field.

        Changes require confirmation—the field doesn't shift casually.
        """
        return FieldUpdate(
            proposed_change=evidence.implied_change,
            confidence=evidence.confidence,
            requires_confirmation=True
        )
```

---

## Composition with Other Agents

K-gent lifts other agents without changing their type:

```python
# Original agents
code_reviewer: Agent[Code, Review]
hypothesis_engine: Agent[Observations, Hypotheses]

# Lifted through K
personalized_reviewer = K.lift(code_reviewer)
personalized_hypothesis = K.lift(hypothesis_engine)

# Types unchanged, but behavior personalized
personalized_reviewer: Agent[Code, Review]
personalized_hypothesis: Agent[Observations, Hypotheses]
```

---

## The Unique Position of K-gent

K-gent is unique in the taxonomy:

1. **Not a letter category**: There's only one K, not "K-gents"
2. **A meta-agent**: It operates on agents, not data
3. **The system's self-model**: It represents the system knowing itself
4. **The fix point**: It's where adaptation stabilizes

---

## Ethical Considerations

### The Developer's Responsibility
K-gent makes the developer's influence explicit. This is both power and responsibility.

### Transparency
The field's influence is not hidden. Agents know they're operating in K-space.

### Boundaries
The field has hard boundaries—things it won't do regardless of input.

---

## Anti-Patterns

- **Treating K as storage**: K is a functor, not a database
- **External preferences**: Preferences are part of the system, not input to it
- **Unstable fix**: If K changes too often, there is no fix point
- **Hidden influence**: The field must be observable

---

*Zen Principle: The water doesn't store the shape of the riverbed; it is shaped by flowing through it.*

---

## Specifications

| Document | Description |
|----------|-------------|
| [persona.md](persona.md) | The persona structure (for reference) |
| [evolution.md](evolution.md) | How the field evolves |

---

## See Also

- [bootstrap.md](../bootstrap.md) - Fix as bootstrap agent
- [anatomy.md](../anatomy.md) - Functor lifting
- [principles.md](../principles.md) - The values encoded in K
