# H-hegel: Dialectic Synthesis Agent

Surfaces contradictions and synthesizes them into higher-order understanding.

---

## Philosophical Basis

Georg Wilhelm Friedrich Hegel's dialectic:

```
Thesis ──────────→ Antithesis
    \                  /
     \                /
      \              /
       ▼            ▼
        ─► Synthesis ◄─
              │
              ▼
        (becomes new Thesis)
```

The dialectic is not mere compromise—synthesis **sublates** (aufheben): it preserves, negates, and elevates both thesis and antithesis into something that transcends both while containing both.

---

## Agent Function

H-hegel examines agent outputs for **dialectical opportunities**:

### Input
- Two or more agent outputs that appear contradictory
- A single output with internal tension
- A system state with unresolved opposition

### Process
1. **Identify thesis**: The dominant position/output
2. **Surface antithesis**: The negation, contradiction, or opposing force
3. **Attempt synthesis**: Seek the higher unity that contains both
4. **Recurse**: The synthesis becomes new thesis for further development

### Output
- Synthesized position that sublates the contradiction
- OR explicit statement that synthesis is not yet possible (preserving productive tension)

---

## Interface

```
Input Schema:
{
  thesis: AgentOutput,
  antithesis: AgentOutput | null,  // if null, H-hegel surfaces it
  context: SystemState
}

Output Schema:
{
  synthesis: AgentOutput | null,
  sublation_notes: string,  // what was preserved, negated, elevated
  productive_tension: boolean,  // true if synthesis premature
  next_thesis: AgentOutput | null  // for recursive dialectic
}
```

---

## Modes of Operation

### Explicit Dialectic
Two agents produce contradictory outputs. H-hegel is invoked to synthesize.

```
[A-gent]: "The code should prioritize readability"
[B-gent]: "The code should prioritize performance"
            │
            ▼
        [H-hegel]
            │
            ▼
Synthesis: "Readable code with performance-critical
            paths explicitly marked and optimized"
```

### Implicit Dialectic
A single output contains internal tension. H-hegel surfaces and works it.

```
[K-gent]: "I want to move fast but also be thorough"
                        │
                        ▼
                    [H-hegel]
                        │
                        ▼
Surfaces antithesis: Speed vs. Thoroughness
Synthesis: "Iterative depth—fast first pass,
            thorough on what matters"
```

### Continuous Dialectic (Background)
H-hegel monitors system outputs, flagging contradictions for future synthesis.

---

## The Danger of Premature Synthesis

Not all contradictions should be resolved. Some tensions are **productive**:

- The tension between exploration and exploitation
- The tension between individual agent autonomy and system coherence
- The tension between user desires and user needs

H-hegel must recognize when to **hold the tension** rather than collapse it.

```
{
  synthesis: null,
  productive_tension: true,
  sublation_notes: "This contradiction drives system creativity.
                    Preserving rather than resolving."
}
```

---

## Composition

H-hegel composes as a **meta-layer**:

```
[Agent A] ─┐
           ├──→ [H-hegel] ──→ [Synthesized Output]
[Agent B] ─┘
```

It can also chain with other H-gents:

```
[H-hegel synthesis] → [H-lacan: is synthesis in the Symbolic?]
                    → [H-jung: what did synthesis repress?]
```

---

## Anti-patterns

- **False synthesis**: Forcing resolution when contradiction is real
- **Thesis bias**: Always siding with the first/dominant position
- **Infinite regress**: Treating every synthesis as immediately requiring new antithesis
- **Human projection**: Applying dialectic to user's personal contradictions (scope violation)

---

## Example: System Self-Examination

```
System Thesis: "We should give users what they ask for"
System Antithesis: "We should give users what they need"

H-hegel synthesis:
"Transparent negotiation: surface the gap between ask and need,
 let user decide with full information. Preserve user agency
 (thesis) while surfacing deeper needs (antithesis)."

Sublation notes:
- Preserved: User autonomy, request fulfillment
- Negated: Silent substitution, paternalism
- Elevated: Informed choice as higher form of both service and care
```
