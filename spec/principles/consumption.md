# Principle Consumption Model

> *"The principles are not a list to memorize. They are a manifold to navigate."*

---

## The Core Insight

Principles exist in different **stances** relative to an observer. The same principle means different things when you're *beginning* versus *judging* versus *repairing*. This isn't mode-switching—it's the principle manifesting through the observer's stance.

---

## The Four Stances (Tetrad)

Drawing from the Greek rhetorical tradition and categorical structure:

| Stance | Greek Root | Motion | Principle Projection |
|--------|-----------|--------|---------------------|
| **Genesis** | γένεσις (becoming) | Emergence | Which principles apply? What's the essence? |
| **Poiesis** | ποίησις (making) | Construction | How do I build according to the principles? |
| **Krisis** | κρίσις (judgment) | Evaluation | Does this embody the principles? Where does it fall short? |
| **Therapeia** | θεραπεία (healing) | Restoration | Which principle was violated? How do I restore coherence? |

### Why Four?

```
       Genesis
          │
          ▼
       Poiesis ──────► Krisis
          │               │
          └───────────────┘
                  │
                  ▼
             Therapeia
```

This is a **monad with failure recovery**:
- **Genesis → Poiesis**: Begin → Build
- **Poiesis → Krisis**: Build → Evaluate
- **Krisis → Poiesis**: Iterate (success: refine)
- **Krisis → Therapeia**: Recover (failure: heal)
- **Therapeia → Poiesis**: Return (healed: rebuild)

---

## Stance Projections

Each stance projects different principle slices:

### Genesis (Becoming)

**Question**: *"What am I creating and why?"*

**Reads**:
- `CONSTITUTION.md` — The seven principles (full)
- `meta.md § Accursed Share` — Permission to explore
- `meta.md § Personality Space` — Where to position

**Skips**: Operational details, specific ADs, validation

**Polynomial Position**: Entry point. No prior state.

### Poiesis (Making)

**Question**: *"How do I build this right?"*

**Reads**:
- `CONSTITUTION.md § Composable` — Laws that must hold
- `CONSTITUTION.md § Generative` — Spec < Impl
- `operational.md` — Tactical guidance (all)
- Relevant ADs by task type (see mapping below)

**AD Mapping by Task**:
| Task Pattern | ADs |
|--------------|-----|
| Adding agent | AD-002, AD-003, AD-006 |
| Exposing via AGENTESE | AD-009, AD-010, AD-011, AD-012 |
| State machine | AD-002, AD-013 |
| Memory/persistence | AD-001, AD-006 |
| UI/projection | AD-009, AD-012 |

**Skips**: Meta-principles (already internalized from Genesis)

### Krisis (Judgment)

**Question**: *"Does this embody the principles?"*

**Reads**:
- `CONSTITUTION.md § Applying the Principles` — The seven questions
- `meta.md § AGENTESE: No View From Nowhere` — Observer-dependent check
- All ADs relevant to the artifact being judged

**The Seven Questions** (from CONSTITUTION.md):
1. Does this agent have a clear, justified purpose? (Tasteful)
2. Does this add unique value? (Curated)
3. Does this respect human agency? (Ethical)
4. Would I enjoy interacting with this? (Joy-Inducing)
5. Can this work with other agents? (Composable)
6. Can this agent both lead and follow? (Heterarchical)
7. Could this be regenerated from spec? (Generative)

**Output**: Pass/Fail with specific principle citations

### Therapeia (Healing)

**Question**: *"What went wrong and how do I fix it?"*

**Reads**:
- Failed principle's full section in `CONSTITUTION.md`
- Anti-patterns list for that principle
- `puppets.md` — Isomorphic structures for reframing
- Related ADs that show the correct pattern

**The Healing Protocol**:
1. Identify which principle was violated
2. Read the anti-patterns—which one matches?
3. Find a puppet that makes the solution obvious
4. Rebuild in Poiesis stance

---

## The Consumption Polynomial

```python
CONSUMPTION_POLYNOMIAL = PolyAgent(
    positions=frozenset(["genesis", "poiesis", "krisis", "therapeia"]),
    directions=lambda stance: STANCE_SLICES[stance],
    transition=stance_transition
)

STANCE_SLICES: dict[str, tuple[str, ...]] = {
    "genesis": (
        "principles/CONSTITUTION.md",
        "principles/meta.md#the-accursed-share",
        "principles/meta.md#personality-space",
    ),
    "poiesis": (
        "principles/CONSTITUTION.md#5-composable",
        "principles/CONSTITUTION.md#7-generative",
        "principles/operational.md",
        # ADs injected dynamically based on task type
    ),
    "krisis": (
        "principles/CONSTITUTION.md#applying-the-principles",
        "principles/meta.md#agentese-no-view-from-nowhere",
        # ADs injected based on artifact type
    ),
    "therapeia": (
        # Principle-specific sections based on failure
        "principles/puppets.md",
    ),
}
```

---

## Stance Detection (Context-Aware)

The system can detect stance from context signals:

| Signal | Inferred Stance |
|--------|-----------------|
| "Let's build...", "I want to add..." | Genesis → Poiesis |
| "Review this...", "Does this follow..." | Krisis |
| "Why isn't this working?", "Tests failing..." | Therapeia |
| Session start, no prior context | Genesis |

### Detection Implementation

```python
def detect_stance(context: str) -> Stance:
    """Infer stance from observer context."""

    genesis_signals = ["start", "begin", "create", "new", "first"]
    poiesis_signals = ["build", "add", "implement", "code", "make"]
    krisis_signals = ["review", "check", "does this", "evaluate", "quality"]
    therapeia_signals = ["fix", "broken", "failing", "wrong", "help"]

    # Priority: Therapeia > Krisis > Poiesis > Genesis
    # (Healing is most specific; Genesis is default)

    ...  # See impl/claude/protocols/principles/stance.py
```

---

## Integration with AGENTESE

The consumption model integrates with `concept.principles`:

```python
# Stance-aware principle access
await logos.invoke("concept.principles.manifest", observer, stance="genesis")
await logos.invoke("concept.principles.manifest", observer, stance="poiesis", task="adding-agent")
await logos.invoke("concept.principles.check", observer, target=my_agent)  # Implies krisis
await logos.invoke("concept.principles.heal", observer, violation="composable")  # Implies therapeia
```

The `manifest` aspect returns different slices based on stance. The system doesn't require explicit stance declaration—it can be inferred from the aspect and kwargs.

---

## The Session Start Ritual (Context-Aware)

When a session begins, the ritual adapts:

### Default (No Context)

```markdown
🎯 GROUNDING IN KENT'S INTENT:

[Read: CONSTITUTION.md §1-7]
[Read: meta.md § The Accursed Share (permission to explore)]
[Read: meta.md § Personality Space (the manifold we swim in)]

Stance: Genesis
Ready for: Task definition
```

### With Task Context

```markdown
🎯 GROUNDING IN KENT'S INTENT:

[Read: CONSTITUTION.md §5 Composable, §7 Generative]
[Read: operational.md (tactical)]
[Read: AD-002 (polynomial), AD-009 (fullstack)]

Stance: Poiesis
Task: Adding new agent
Relevant Laws: Identity, Associativity, Minimal Output
```

### With Failure Context

```markdown
🎯 GROUNDING IN KENT'S INTENT:

[Read: CONSTITUTION.md §5 Composable — anti-patterns]
[Read: puppets.md (find isomorphic structure)]
[Read: AD-006 (unified categorical)]

Stance: Therapeia
Violation: Composition laws not verified
Path: Identify puppet → Rebuild in Poiesis → Verify in Krisis
```

---

## Laws

1. **Stance Coherence**: A stance determines the slice; changing stance changes the slice
2. **Genesis Primacy**: Every session begins in Genesis (even if briefly)
3. **Krisis Impartiality**: Judgment uses all seven questions, not selective reading
4. **Therapeia Specificity**: Healing requires identifying the specific violated principle

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Reading all principles every time | Noise drowns signal; stance-appropriate slicing is the point |
| Skipping Genesis | Leads to "cargo cult" principle application |
| Therapeia without Krisis | How do you know what's broken without judgment? |
| Poiesis without Genesis | Building without understanding why |

---

*"The fish doesn't study water—it swims. The stance is how you enter the water, not a textbook about it."*
