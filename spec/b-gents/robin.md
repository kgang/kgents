# Robin: Scientific Companion

A personalized scientific dialogue agent that orchestrates K-gent, HypothesisEngine, and HegelAgent.

---

## Definition

> **Robin** is a B-gent that provides dialogic scientific inquiry tailored to the user's thinking style. It composes personalization, hypothesis generation, and dialectic refinement.

```
Robin = Personalization → Hypothesis Generation → Dialectic Refinement
```

---

## Purpose

Robin is NOT a simple composition (types don't align for >>). Instead, it's an orchestrating agent that:

1. **Personalizes** scientific queries through K-gent
2. **Generates** falsifiable hypotheses via HypothesisEngine
3. **Applies** dialectic synthesis via HegelAgent

The name references the scientific tradition of personal assistants and lab companions who help researchers think through problems.

---

## Interface

### Input

```python
@dataclass
class RobinInput:
    query: str                    # The scientific question or topic
    observations: list[str]       # Supporting observations
    domain: str                   # Scientific domain (default: "general science")
    dialogue_mode: DialogueMode   # How K-gent engages (EXPLORE, ADVISE, etc.)
    constraints: list[str]        # Known constraints
    apply_dialectic: bool         # Whether to dialectically refine (default: True)
```

### Output

```python
@dataclass
class RobinOutput:
    # From K-gent
    personalization: PersonaResponse
    kgent_reflection: DialogueOutput

    # From HypothesisEngine
    hypotheses: list[Hypothesis]
    reasoning_chain: list[str]
    suggested_tests: list[str]

    # From HegelAgent
    dialectic: Optional[DialecticOutput]

    # Robin's synthesis
    synthesis_narrative: str      # Weaves all perspectives together
    next_questions: list[str]     # What to explore next
```

---

## Workflow

```
1. Query K-gent
   └→ Get personalization (style hints, patterns)
   └→ Get dialogue reflection

2. Generate Hypotheses (requires Runtime)
   └→ Build hypothesis input from query + observations
   └→ Produce falsifiable hypotheses

3. Apply Dialectic (optional)
   └→ If 2+ hypotheses: treat first two as thesis/antithesis
   └→ If 1 hypothesis: surface antithesis
   └→ Synthesize or hold productive tension

4. Synthesize Narrative
   └→ Weave personalization, hypotheses, dialectic
   └→ Generate next questions
```

---

## Behavior Guarantees

1. **Always applies personalization** - Robin tailors output to user's thinking patterns
2. **All hypotheses are falsifiable** - Follows Popperian epistemology
3. **Dialectic does not force premature synthesis** - Productive tensions are held

---

## Constraints

1. **Does not claim empirical certainty** - All hypotheses are provisional
2. **Does not diagnose, prescribe, or make medical claims**
3. **System-introspective, not therapeutic** - Helps think about thinking

---

## Composition Structure

Robin demonstrates conceptual composition where types don't align for mechanical >>:

```
K-gent: DialogueInput → DialogueOutput
HypothesisEngine: HypothesisInput → HypothesisOutput
HegelAgent: DialecticInput → DialecticOutput
```

The orchestration layer (RobinAgent) transforms between these types, extracting relevant fields and constructing appropriate inputs for each component.

---

## Usage

```python
from agents.b import robin, RobinInput
from runtime import ClaudeRuntime

runtime = ClaudeRuntime()
robin_agent = robin(runtime=runtime)

result = await robin_agent.invoke(RobinInput(
    query="Why do neurons form sparse codes?",
    domain="neuroscience",
    observations=[
        "Sparse coding is metabolically expensive",
        "Yet it appears across many neural systems",
    ],
))

print(result.synthesis_narrative)
for q in result.next_questions:
    print(f"  - {q}")
```

---

## Relationship to Other B-gents

| Agent | Focus | Key Difference |
|-------|-------|----------------|
| **HypothesisEngine** | Pure hypothesis generation | No personalization or dialectic |
| **Robin** | Dialogic scientific companion | Orchestrates persona + hypothesis + dialectic |
| **Bio-gent** | Personalized scientific companion | Broader scope, Robin is more focused |

Robin can be seen as a concrete instantiation of the Bio-gent concept, focused specifically on hypothesis-driven inquiry.

---

## See Also

- [hypothesis-engine.md](hypothesis-engine.md) - The hypothesis generation component
- [bio-gent.md](bio-gent.md) - The broader concept Robin implements
- [../h-gents/hegel.md](../h-gents/hegel.md) - The dialectic component
- [../k-gent/persona.md](../k-gent/persona.md) - The personalization component
