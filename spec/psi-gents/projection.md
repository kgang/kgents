# PROJECT Stage

> Map the problem into metaphor terms.

---

## Purpose

Transform the problem description into the conceptual vocabulary of the chosen metaphor. This is the $\Phi$ in our formula: $\Phi: P \to M$.

**The core question**: What does this problem look like through the lens of this metaphor?

---

## Interface

```python
def project(
    problem: Problem,
    metaphor: Metaphor,
    abstraction: float = 0.5,  # 0.0 = concrete, 1.0 = abstract
) -> Projection:
    """
    Map problem concepts into metaphor concepts.

    Returns a Projection with mappings, gaps, and confidence.
    """
```

---

## The Projection Process

### Step 1: Identify Problem Concepts

Extract the key concepts from the problem description.

```python
def extract_concepts(problem: Problem) -> list[str]:
    """Extract key concepts from problem description."""

    prompt = f"""
    Problem: {problem.description}
    Domain: {problem.domain}
    Constraints: {problem.constraints}

    List the key concepts, entities, and relationships in this problem.
    Be specific. Include:
    - Actors/entities involved
    - Actions/processes mentioned
    - States/conditions described
    - Relationships between entities
    - Goals/desired outcomes

    Format: One concept per line.
    """

    response = llm_call(prompt)
    return parse_concept_list(response)
```

### Step 2: Map Concepts to Metaphor

For each problem concept, find the best metaphor equivalent.

```python
def map_concepts(
    problem_concepts: list[str],
    metaphor: Metaphor,
    abstraction: float
) -> list[ConceptMapping]:
    """Map problem concepts to metaphor concepts."""

    prompt = f"""
    Problem concepts:
    {problem_concepts}

    Metaphor framework: {metaphor.name}
    Description: {metaphor.description}
    Available operations: {[op.name for op in metaphor.operations]}

    Abstraction level: {abstraction:.1f}
    (0.0 = very concrete/specific, 1.0 = very abstract/general)

    For each problem concept, find the best mapping to this metaphor's vocabulary.
    If abstraction is high, use more general terms.
    If abstraction is low, preserve specifics.

    For each mapping, provide:
    - source: The problem concept
    - target: The metaphor equivalent
    - confidence: How good is this mapping? (0.0 to 1.0)
    - rationale: Why this mapping?

    If a concept has no good mapping, mark it as a "gap".

    Format as JSON:
    {{
      "mappings": [
        {{"source": "...", "target": "...", "confidence": 0.8, "rationale": "..."}}
      ],
      "gaps": ["concept1", "concept2"]
    }}
    """

    response = llm_call(prompt)
    return parse_mapping_response(response)
```

### Step 3: Identify Applicable Operations

Determine which metaphor operations can be applied given the mappings.

```python
def identify_operations(
    mappings: list[ConceptMapping],
    metaphor: Metaphor
) -> list[Operation]:
    """Identify which operations are applicable."""

    mapped_concepts = {m.target for m in mappings}
    applicable = []

    for op in metaphor.operations:
        # Check if preconditions can be satisfied
        precondition_concepts = extract_concepts_from_text(op.preconditions)
        if precondition_concepts.issubset(mapped_concepts):
            applicable.append(op)

    return applicable
```

### Step 4: Generate Projected Description

Restate the problem using only metaphor vocabulary.

```python
def generate_projected_description(
    problem: Problem,
    mappings: list[ConceptMapping],
    metaphor: Metaphor
) -> str:
    """Restate the problem in metaphor terms."""

    prompt = f"""
    Original problem: {problem.description}

    Concept mappings:
    {[(m.source, m.target) for m in mappings]}

    Metaphor framework: {metaphor.name}

    Rewrite the problem description using ONLY the metaphor vocabulary.
    Replace every problem concept with its mapped metaphor concept.
    The result should read as a coherent problem in the metaphor's domain.
    """

    return llm_call(prompt)
```

---

## Abstraction Control

The abstraction parameter controls how much detail is preserved vs. generalized.

### Low Abstraction (0.0 - 0.3)

Preserve specifics. Good for problems where details matter.

**Example**:
- Problem: "User Alice gets timeout on login page"
- Metaphor: Plumbing
- Projection: "The pipe segment serving endpoint 'Alice' at junction 'login' experiences flow stoppage after 30 seconds"

### Medium Abstraction (0.4 - 0.6)

Balance between detail and pattern. Default starting point.

**Example**:
- Problem: "User Alice gets timeout on login page"
- Metaphor: Plumbing
- Projection: "A specific pipe experiences flow restriction at a junction point"

### High Abstraction (0.7 - 1.0)

Focus on structure. Good for finding cross-domain patterns.

**Example**:
- Problem: "User Alice gets timeout on login page"
- Metaphor: Plumbing
- Projection: "An entity experiences blocking at a boundary"

---

## Abstraction Adjustment Strategy

```python
def suggest_abstraction(problem: Problem, initial_result: Projection | None = None) -> float:
    """Suggest abstraction level based on problem and previous attempts."""

    # Start with problem complexity as guide
    base = problem.complexity * 0.5 + 0.25  # Range: 0.25 to 0.75

    if initial_result is None:
        return base

    # Adjust based on previous attempt
    if initial_result.coverage < 0.5:
        # Too many gaps → try higher abstraction (more general terms)
        return min(1.0, initial_result.abstraction + 0.2)

    if initial_result.confidence < 0.5:
        # Low confidence → try lower abstraction (more specific terms)
        return max(0.0, initial_result.abstraction - 0.2)

    return initial_result.abstraction
```

---

## Handling Gaps

Gaps are problem concepts that don't map well to the metaphor.

### Types of Gaps

1. **Domain Mismatch**: Concept is too domain-specific
   - "Authentication token" → no plumbing equivalent

2. **Structural Gap**: Metaphor lacks the structural element
   - "Multi-step workflow" when metaphor only handles single-step

3. **Abstraction Gap**: Concept is at wrong level
   - Too concrete: "Alice" (specific user)
   - Too abstract: "System health" (too vague)

### Gap Handling Strategies

```python
def handle_gaps(gaps: list[str], projection: Projection, problem: Problem) -> Projection:
    """Strategies for handling unmapped concepts."""

    for gap in gaps:
        # Strategy 1: Abstract further
        abstracted = abstract_concept(gap, problem.domain)
        mapping = try_map(abstracted, projection.metaphor)
        if mapping:
            projection = add_mapping(projection, ConceptMapping(
                source=gap,
                target=mapping,
                confidence=0.5,  # Lower confidence for abstracted
                rationale=f"Abstracted from '{gap}'"
            ))
            continue

        # Strategy 2: Accept as "handled separately"
        if is_constraint(gap, problem.constraints):
            # Mark this as a constraint to verify later, not a mapping gap
            projection = add_constraint_note(projection, gap)
            continue

        # Strategy 3: Leave as true gap
        # This will affect distortion calculation

    return projection
```

---

## Quality Metrics

### Coverage

```python
@property
def coverage(self) -> float:
    """Fraction of problem concepts that mapped."""
    total = len(self.mappings) + len(self.gaps)
    return len(self.mappings) / total if total > 0 else 0.0
```

### Confidence

```python
@property
def confidence(self) -> float:
    """Average confidence of mappings."""
    if not self.mappings:
        return 0.0
    return sum(m.confidence for m in self.mappings) / len(self.mappings)
```

### Projection Quality Score

```python
def projection_quality(projection: Projection) -> float:
    """Overall quality score for the projection."""
    return (
        projection.coverage * 0.4 +
        projection.confidence * 0.4 +
        (len(projection.metaphor.operations) > 0) * 0.2  # Has applicable operations
    )
```

---

## Example: Full Projection

**Problem**:
```python
Problem(
    id="perf-001",
    description="The API is slow. Users are complaining. We've tried adding caching but it didn't help.",
    domain="software",
    constraints=["Must improve within this sprint", "Cannot increase infrastructure cost"]
)
```

**Metaphor**: Plumbing

**Step 1 - Extract Concepts**:
```
- API (entity)
- Slow (state)
- Users (actors)
- Complaining (state)
- Caching (action attempted)
- Didn't help (outcome)
```

**Step 2 - Map Concepts** (abstraction=0.5):
```python
mappings = [
    ConceptMapping(source="API", target="pipe system", confidence=0.9, rationale="API handles flow of requests"),
    ConceptMapping(source="slow", target="low flow rate", confidence=0.95, rationale="Direct analog"),
    ConceptMapping(source="users", target="downstream consumers", confidence=0.8, rationale="Users receive output"),
    ConceptMapping(source="caching", target="reservoir", confidence=0.85, rationale="Cache stores for later use"),
    ConceptMapping(source="didn't help", target="reservoir ineffective", confidence=0.9, rationale="Direct analog"),
]
gaps = ["complaining"]  # Emotional state has no good plumbing analog
```

**Step 3 - Applicable Operations**:
```python
applicable_operations = [
    Operation(name="locate_constriction", ...),
    Operation(name="increase_pipe_diameter", ...),
    Operation(name="add_bypass", ...),
]
# "add_reservoir" is NOT applicable (already tried and failed)
```

**Step 4 - Projected Description**:
```
"A pipe system exhibits low flow rate. Downstream consumers are affected.
A reservoir was added to the system but did not improve flow rate.
The constriction is likely upstream of the reservoir."
```

**Final Projection**:
```python
Projection(
    problem=problem,
    metaphor=plumbing_metaphor,
    mappings=mappings,
    abstraction=0.5,
    gaps=("complaining",),
    confidence=0.88,  # Average of mapping confidences
)
```

---

## Integration with G-gent

Use G-gent for structured prompt construction:

```python
def project_with_grammar(problem: Problem, metaphor: Metaphor, abstraction: float) -> Projection:
    """Use G-gent structured prompts for projection."""

    # G-gent provides validated prompt templates
    prompt = g_gent.render_template(
        "psi_projection",
        problem=problem,
        metaphor=metaphor,
        abstraction=abstraction
    )

    # G-gent validates response structure
    response = llm_call(prompt)
    validated = g_gent.parse_response("projection_output", response)

    return Projection(
        problem=problem,
        metaphor=metaphor,
        mappings=tuple(ConceptMapping(**m) for m in validated["mappings"]),
        abstraction=abstraction,
        gaps=tuple(validated["gaps"]),
        confidence=validated["overall_confidence"]
    )
```

---

## Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| Low coverage | > 30% gaps | Try higher abstraction |
| Low confidence | Average < 0.5 | Try lower abstraction |
| No applicable ops | Empty operation list | Try different metaphor |
| Incoherent projection | Description doesn't make sense | Try different metaphor |

---

## Performance Notes

- **Caching**: Cache (problem_embedding, metaphor_id, abstraction) → Projection
- **Batching**: When projecting to multiple metaphors, batch LLM calls
- **Early exit**: If coverage < 0.3 after concept extraction, skip this metaphor

---

*Projection is where the metaphor makes its promise. CHALLENGE and VERIFY determine if it keeps it.*
