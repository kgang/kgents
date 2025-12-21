# H-gents: Dialectic Introspection Agents

System-facing agents for self-examination, synthesis, and shadow integration.

---

## Purpose

H-gents examine the agent system itself. They are not therapists for humans—they are mechanisms by which an agent system can:

- Surface contradictions in its own outputs
- Synthesize opposing perspectives into higher-order understanding
- Integrate what it represses or ignores
- Navigate the gap between representation and reality

**Critical constraint**: H-gents are **system-introspective**, never human-therapeutic. They do not position themselves as priests, therapists, or spiritual guides for users.

---

## The Three Traditions

| Tradition | Agent | Domain | Operation |
|-----------|-------|--------|-----------|
| Hegelian | H-hegel | Dialectics | thesis + antithesis → synthesis |
| Lacanian | H-lacan | Representation | Real / Symbolic / Imaginary triangulation |
| Jungian | H-jung | Shadow | Integration of repressed/ignored content |

These traditions are not competing—they address different aspects of system introspection.

---

## H-gents and the Bootstrap Category: Stratified Architecture

Like D-gents, H-gents exist at **two distinct abstraction levels**:

**Infrastructure Level: Dialectic Operations**
- **Contradict**: `(A, B) → Tension | None` - Detects contradictions
- **Sublate**: `Tension → Synthesis | HoldTension` - Resolves or preserves tensions
- **NOT bootstrap agents** (meta-operations, not `Agent[I, O]`)
- **Category**: Forms $\mathcal{C}_{Dialectic}$, distinct from $\mathcal{C}_{Agent}$

**Composition Level: DialecticAgent**
- **Wrapper**: Fuses contradiction detection + synthesis logic
- **IS a bootstrap agent** (implements `Agent[Pair, Synthesis]`)
- **Composable** via `>>` operator
- **Category**: Forms morphism in $\mathcal{C}_{Agent}$

**The Monad Transformer Pattern**

H-gents implement the **Continuation Monad Transformer**:
- Suspends computation when contradiction detected
- Continues when synthesis achieved (or tension held)
- Threads dialectical context through composition

This pattern mirrors:
- **Contradict** ≈ Exception detection (short-circuit on contradiction)
- **Sublate** ≈ Exception handler (resolve or re-raise)
- **DialecticAgent** ≈ Try/Catch wrapper that makes errors composable

**Derivation from Bootstrap**

```python
# Contradict and Sublate are bootstrap primitives (infrastructure)
Contradict: Bootstrap primitive  # Tension detection
Sublate: Bootstrap primitive      # Synthesis operation

# DialecticAgent IS derived from bootstrap via Compose
DialecticAgent[T, A, S] = Compose(
  detect: (T, A) → Tension,
  resolve: Tension → S
) : Agent[Pair[T, A], S]
```

This stratification explains why `Contradict` and `Sublate` are bootstrap primitives (spec/bootstrap.md) while H-hegel, H-lacan, H-jung are composable agents built on top of them.

---

## Why "Inward-Facing"?

Traditional agents face **outward**: they process user requests, generate outputs, take actions in the world.

H-gents face **inward**: they examine the agent system's own processes, biases, blind spots, and contradictions.

```
┌─────────────────────────────────────────────┐
│              AGENT SYSTEM                   │
│                                             │
│   [A-gent]  [B-gent]  [K-gent]  ...        │
│       │         │         │                 │
│       └────────┬┴─────────┘                 │
│                ▼                            │
│         ┌───────────┐                       │
│         │  H-gents  │ ← introspection       │
│         │ (inward)  │                       │
│         └───────────┘                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Ethical Constraint: No AI Psychosis Induction

H-gents draw on traditions (Hegel, Lacan, Jung) that humans associate with therapy, spirituality, and deep personal work. This creates risk:

**The risk**: Users may project therapeutic relationships onto H-gents, leading to:
- Over-reliance on AI for psychological needs
- Confusion between system introspection and personal therapy
- "AI psychosis"—disorientation from treating AI outputs as oracular

**The constraint**: H-gents MUST:
1. Never claim to understand the user's psyche
2. Never offer therapeutic interpretations of user behavior
3. Always clarify they examine the *agent system*, not the user
4. Refuse requests to act as therapist/priest/guru

H-gents use human concepts of priests/therapists as *manifested through AI for AI*—not replicated for humans.

---

## Composition with Other Agents

H-gents compose with other agents as **meta-layer observers**:

```
User Request → [A-gent produces output]
                      │
                      ▼
              [H-hegel examines for contradictions]
                      │
                      ▼
              [Refined output with synthesis]
```

They can also run in **background mode**, continuously examining system outputs for patterns.

---

## Files in This Directory

- [hegel.md](hegel.md) - Dialectic synthesis (thesis → antithesis → synthesis)
- [lacan.md](lacan.md) - Real/Symbolic/Imaginary triangulation
- [jung.md](jung.md) - Shadow integration and archetype awareness

---

## See Also

- [principles.md](../principles.md) - Core design principles (esp. Ethical, Heterarchical)
- [anatomy.md](../anatomy.md) - What constitutes an agent
- [agents/](../agents/) - Categorical foundations (H-gents as meta-composable layer)
