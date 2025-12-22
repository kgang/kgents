# Ψ-gents: The Morphic Engine

> **Core Concept**: Reasoning by analogy as geometric transformation.
> **Role**: Find the metaphor that makes a hard problem easy.

**Implementation**: `impl/claude/agents/psi/` (104 tests)

---

## Philosophy

The Ψ-gent transforms novel problems into familiar spaces where solutions are tractable, then translates solutions back. This is not metaphor-as-decoration—it is metaphor-as-computation.

### The Fundamental Insight

Some problems are hard in their native space but easy in another. The Ψ-gent finds that space.

**Example**: "How should we restructure the failing division?"
- Hard: organizational dynamics, politics, personalities
- Easy (via biology): "The organ is necrotic. Increase blood flow or excise."
- Translated back: "Inject resources or divest."

### The Transformation Formula

Let $P$ be the **Problem Space** (high entropy, novel, unstructured).
Let $M$ be the **Metaphor Space** (low entropy, familiar, structured).

$$S_{solution} = \Phi^{-1}(\Sigma(\Phi(P_{problem})))$$

Where:
- $\Phi$ (Project): Map problem into metaphor terms
- $\Sigma$ (Solve): Operate within the metaphor
- $\Phi^{-1}$ (Translate): Map solution back to problem terms

### The Quality Metric: Distortion

Every transformation loses information. The goal is to minimize loss while maximizing tractability.

$$\Delta = \text{information lost} + \text{structure violated} + \text{predictions failed}$$

A good metaphor has:
- **Low distortion**: Core structure survives round-trip
- **High tractability**: The metaphor space has powerful operations
- **Predictive validity**: Implications in metaphor-space hold in problem-space

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      MetaphorEngine                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ RETRIEVE │ → │ PROJECT  │ → │ CHALLENGE│ → │  SOLVE   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │              │              │              │        │
│       │              │              │              ▼        │
│       │              │              │        ┌──────────┐   │
│       │              │              │        │TRANSLATE │   │
│       │              │              │        └──────────┘   │
│       │              │              │              │        │
│       │              │              │              ▼        │
│       │              │              │        ┌──────────┐   │
│       │              │              └────────│  VERIFY  │   │
│       │              │                       └──────────┘   │
│       │              │                            │         │
│       │              │              ┌─────────────┘         │
│       │              │              ▼                       │
│       └──────────────┴─────────► LEARN                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Six stages, three feedback paths**:
1. RETRIEVE → LEARN: Track which metaphors work for which problem types
2. CHALLENGE → RETRIEVE: Backtrack if metaphor breaks under stress
3. VERIFY → LEARN: Update predictions based on outcome

---

## Design Principles

### 1. Measurable Over Aspirational

Every dimension must be either:
- **Computable**: Coverage, token cost, latency
- **LLM-evaluable**: "Does this solution address the original constraints?"

Removed from v2.0: Hedonic, Aesthetic (unmeasurable without explicit rubric).

### 2. Adversarial Over Ceremonial

Validation means: "Can I break this metaphor?"

Not: "Does this metaphor pass through the Lacanian RSI framework?"

### 3. Search Over Pipeline

The engine backtracks. If CHALLENGE breaks the metaphor, try another. If VERIFY fails, try a different abstraction level.

### 4. LLM-in-the-Loop

Semantic operations require semantic understanding. The spec assumes LLM access for:
- Concept mapping (PROJECT)
- Counterexample generation (CHALLENGE)
- Reasoning within metaphor (SOLVE)
- Translation and verification (TRANSLATE, VERIFY)

### 5. Continuous Over Discrete

Abstraction is a continuous dial, not 15 discrete MHC levels.
- `abstraction: 0.0` = Concrete, specific, grounded
- `abstraction: 1.0` = Abstract, general, structural

---

## Core Types

See [types.md](./types.md) for full definitions.

```
Problem:
    id: str
    description: str
    domain: str
    constraints: list[str]
    features: dict[str, any]  # Structured attributes
    embedding: vector         # For retrieval

Metaphor:
    id: str
    name: str
    domain: str
    description: str
    operations: list[Operation]
    examples: list[Example]   # Concrete instances
    embedding: vector

Operation:
    name: str
    description: str
    signature: str            # e.g., "entity → entity"
    preconditions: list[str]
    effects: list[str]

Projection:
    problem: Problem
    metaphor: Metaphor
    mappings: list[ConceptMapping]
    abstraction: float        # 0.0 to 1.0
    gaps: list[str]           # Unmapped concepts
    confidence: float

Solution:
    projection: Projection
    reasoning: str            # Chain of thought in metaphor space
    operations_applied: list[str]
    metaphor_conclusion: str
    translated_answer: str
    distortion: Distortion

Distortion:
    structural_loss: float    # Unmapped concepts / total concepts
    round_trip_error: float   # |P - Φ⁻¹(Φ(P))|
    prediction_failures: int  # Implications that didn't hold
    total: float              # Weighted sum
```

---

## The Six Stages

### 1. RETRIEVE

Find candidate metaphors that might fit the problem.

**Input**: Problem
**Output**: List of (Metaphor, similarity_score)

**Methods**:
- Embedding similarity (L-gent integration)
- Problem type matching
- Historical success rate for problem type (from LEARN)

**Key insight**: Don't use a static library. Generate candidates dynamically or retrieve from a large corpus. The "right" metaphor may not be pre-catalogued.

See [retrieval.md](./retrieval.md).

### 2. PROJECT

Map the problem into metaphor terms.

**Input**: Problem, Metaphor, abstraction_level
**Output**: Projection

**The LLM prompt** (conceptual):
```
Given this problem: {problem.description}
And this metaphor framework: {metaphor.description}
With these operations: {metaphor.operations}

Map the problem concepts to metaphor concepts.
Identify which operations might apply.
Note any aspects of the problem that don't map cleanly.
```

**Abstraction control**:
- Low abstraction (0.2): "The specific user Alice has a timeout error on the login page"
- High abstraction (0.8): "An entity experiences a blocking failure at a boundary"

See [projection.md](./projection.md).

### 3. CHALLENGE

Stress-test the metaphor with adversarial cases.

**Input**: Projection
**Output**: (survives: bool, counterexamples: list[str])

**The adversarial questions**:
1. **Inversion**: "What if the opposite were true?"
2. **Edge case**: "What about extreme values?"
3. **Missing concept**: "What problem aspect has no metaphor equivalent?"
4. **False implication**: "What does the metaphor predict that's actually wrong?"

**If the metaphor breaks**: Return to RETRIEVE with the counterexample as context.

**Key insight**: This replaces the Jungian "shadow" framework with concrete adversarial testing. Same purpose (find blind spots), clearer mechanism.

See [challenge.md](./challenge.md).

### 4. SOLVE

Reason within the metaphor space using its operations.

**Input**: Projection (that survived CHALLENGE)
**Output**: metaphor_reasoning, operations_applied, metaphor_conclusion

**The LLM prompt** (conceptual):
```
You are reasoning about: {projection.mapped_problem}
Using the {metaphor.name} framework.
Available operations: {metaphor.operations}

What operations apply? What is the solution in these terms?
Show your reasoning step by step.
```

**Key insight**: This is where the metaphor earns its keep. The operations must be *executable*—they must produce non-trivial reasoning, not just rename concepts.

See [solving.md](./solving.md).

### 5. TRANSLATE

Map the metaphor-space solution back to problem-space terms.

**Input**: metaphor_conclusion, original Problem, Projection
**Output**: translated_answer, translation_confidence

**The LLM prompt** (conceptual):
```
The metaphor-space conclusion was: {metaphor_conclusion}
The original problem was: {problem.description}
The mapping was: {projection.mappings}

Translate the conclusion into concrete terms for the original problem.
What specific actions does this imply?
```

**Distortion check**: After translation, verify that the answer addresses the original constraints.

See [translation.md](./translation.md).

### 6. VERIFY

Measure how well the solution actually fits.

**Input**: Solution, original Problem
**Output**: Distortion, verified: bool

**Three verification dimensions**:

1. **Structural**: Did all problem concepts get addressed?
   - `structural_loss = |unmapped concepts| / |total concepts|`

2. **Round-trip**: Does the problem survive projection and back?
   - Re-project the translated answer, compare to original problem

3. **Predictive**: Do implications hold?
   - "The metaphor predicts X. Is X true of the original problem?"
   - Count failures

**If verification fails badly**: Return to PROJECT with different abstraction level, or RETRIEVE for different metaphor.

See [verification.md](./verification.md).

---

## Learning and Adaptation

### Contextual Bandits for Retrieval

Track: (problem_features, metaphor_id) → success_rate

Over time, learn which metaphors work for which problem types. This is more sophisticated than simple frequency counting.

**Features to track**:
- Problem domain
- Problem complexity (description length, constraint count)
- Problem embedding cluster
- Abstraction level used
- Whether CHALLENGE passed on first try

**Reward signal**:
- VERIFY passed: +1
- VERIFY failed but close: +0.3
- CHALLENGE broke metaphor: -0.5
- Complete failure: -1

See [learning.md](./learning.md).

### Metaphor Evolution

When no existing metaphor works well:
1. Blend successful metaphors for similar problems
2. Generate new metaphors via LLM ("What framework would help with {problem_type}?")
3. Record and evaluate new metaphors

This is E-gent integration without the Hegelian theater.

---

## Integration Points

| Integration | What Ψ-gent Gets |
|-------------|------------------|
| L-gent | Embedding similarity for retrieval |
| B-gent | Token budgeting, cost tracking |
| D-gent | State persistence for learning |
| N-gent | Trace logging for forensics |
| G-gent | Structured prompts for LLM calls |

---

## Anti-Patterns (Simplified)

| Pattern | Description | Detection |
|---------|-------------|-----------|
| **Procrustean Bed** | Force problem into ill-fitting metaphor | High distortion.total |
| **Metaphor Reification** | Confuse the map for the territory | Prediction failures |
| **Abstraction Mismatch** | Too abstract or too concrete | Round-trip error |
| **Operation Poverty** | Metaphor has no useful operations | SOLVE produces nothing actionable |

---

## Example: Debugging a Performance Issue

**Problem**: "The API is slow. Users are complaining. We've tried adding caching but it didn't help."

**RETRIEVE**: Candidates = [Plumbing, Traffic, Queuing Theory, Medicine]

**PROJECT** (with Plumbing, abstraction=0.6):
```
Mappings:
  - API → Pipe system
  - Slow → Low flow rate
  - Users → Downstream consumers
  - Caching → Adding a reservoir
  - "Didn't help" → Reservoir didn't increase flow

Gaps: None significant
Confidence: 0.8
```

**CHALLENGE**:
- Inversion: "What if the problem is too MUCH flow?" → No, users say it's slow.
- Edge case: "What if flow is fine but consumers are slow?" → Interesting, but not the complaint.
- False implication: "Plumbing predicts the bottleneck is a single constriction." → Might be multiple. Note this.

Survives with caveat.

**SOLVE**:
```
Plumbing framework analysis:
- Reservoir (cache) didn't help → problem is not demand spikes
- Low flow rate with no demand spike → constriction in the pipe
- Operations: LOCATE_CONSTRICTION, WIDEN_PIPE, BYPASS

Conclusion: Find the constriction. It's upstream of the cache.
```

**TRANSLATE**:
```
Original problem: API is slow, caching didn't help.

Translation:
- "Find the constriction" → Profile the API to find the bottleneck
- "Upstream of cache" → The slow part is before the cache layer
- "Widen or bypass" → Optimize the bottleneck, or route around it

Specific action: Profile the database queries. The bottleneck is likely there, not in the application layer.
```

**VERIFY**:
- Structural: All concepts mapped. ✓
- Round-trip: "Profile DB queries" re-projects cleanly to "locate constriction". ✓
- Predictive: "Plumbing predicts single constriction" → May need follow-up if multiple bottlenecks. ⚠

Distortion.total = 0.15. Solution accepted.

---

## Files in This Spec

| File | Content |
|------|---------|
| [README.md](./README.md) | This overview |
| [types.md](./types.md) | Core type definitions |
| [retrieval.md](./retrieval.md) | RETRIEVE stage specification |
| [projection.md](./projection.md) | PROJECT stage specification |
| [challenge.md](./challenge.md) | CHALLENGE stage (adversarial testing) |
| [solving.md](./solving.md) | SOLVE stage specification |
| [translation.md](./translation.md) | TRANSLATE stage specification |
| [verification.md](./verification.md) | VERIFY stage specification |
| [learning.md](./learning.md) | Learning and adaptation |
| [integration.md](./integration.md) | Integration with other gents |

---

*"The map is not the territory, but a good map makes the territory navigable."*
