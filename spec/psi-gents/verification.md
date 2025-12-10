# VERIFY Stage

> Measure how well the solution actually fits.

---

## Purpose

Quantify the quality of the transformation. Did we lose important information? Does the solution actually address the original problem? This is where we compute the Distortion metric.

**The core question**: How much did we break by going through the metaphor?

---

## Interface

```python
def verify(solution: Solution, problem: Problem) -> tuple[Distortion, bool]:
    """
    Measure solution quality via distortion analysis.

    Returns:
        - Distortion: The computed distortion metrics
        - verified: Whether the solution passes verification
    """
```

---

## The Three Distortion Dimensions

### 1. Structural Loss

What fraction of the problem wasn't addressed?

```python
def measure_structural_loss(solution: Solution, problem: Problem) -> float:
    """Measure how much of the problem was lost structurally."""

    projection = solution.metaphor_solution.projection

    # Method 1: Gap-based (from projection)
    gap_based = len(projection.gaps) / (len(projection.mappings) + len(projection.gaps))

    # Method 2: Constraint coverage
    constraints_addressed = 0
    for constraint in problem.constraints:
        if constraint_addressed(constraint, solution.translated_answer, solution.specific_actions):
            constraints_addressed += 1

    constraint_coverage = (
        constraints_addressed / len(problem.constraints)
        if problem.constraints else 1.0
    )

    # Method 3: LLM assessment
    prompt = f"""
    Original problem: {problem.description}
    Solution provided: {solution.translated_answer}
    Actions: {solution.specific_actions}

    What aspects of the original problem are NOT addressed by this solution?
    List them, then rate structural completeness (0.0 to 1.0).

    Format:
    UNADDRESSED: [list]
    COMPLETENESS: [0.0 to 1.0]
    """
    response = llm_call(prompt)
    llm_completeness = parse_completeness(response)

    # Combine (inverted: we want LOSS not coverage)
    structural_loss = 1.0 - (
        (1 - gap_based) * 0.3 +
        constraint_coverage * 0.3 +
        llm_completeness * 0.4
    )

    return max(0.0, min(1.0, structural_loss))
```

---

### 2. Round-Trip Error

Does the problem survive projection and back?

This is the mathematical heart of distortion: $|P - \Phi^{-1}(\Phi(P))|$

```python
def measure_round_trip_error(solution: Solution, problem: Problem) -> float:
    """Measure error from round-trip transformation."""

    # The "round trip" is:
    # 1. Original problem → projected (Φ)
    # 2. Projected → solution in metaphor space (Σ)
    # 3. Solution → translated back (Φ⁻¹)

    # For verification, we re-project the translated answer and compare

    # Step 1: Re-project the translated answer
    prompt = f"""
    Original problem: {problem.description}
    Solution we derived: {solution.translated_answer}

    If we treat this solution as a "problem" and project it back through
    the {solution.metaphor_solution.projection.metaphor.name} metaphor,
    what would it look like?

    Describe the solution in metaphor terms.
    """
    re_projected = llm_call(prompt)

    # Step 2: Compare to original projection
    original_projection = solution.metaphor_solution.projection.mapped_description

    prompt = f"""
    Original projection: {original_projection}
    Re-projected solution: {re_projected}

    How similar are these? Consider:
    - Do they describe the same core situation?
    - Are the same concepts present?
    - Is the structure preserved?

    Rate similarity (0.0 = completely different, 1.0 = identical).
    Return only a number.
    """
    similarity = float(llm_call(prompt, max_tokens=10))

    # Error is inverse of similarity
    return 1.0 - similarity
```

**Alternative: Embedding-based round-trip**

```python
def measure_round_trip_error_embedding(solution: Solution, problem: Problem) -> float:
    """Measure round-trip error using embeddings."""

    # Embed original problem
    problem_embedding = embed(problem.description)

    # Embed the solution (as a description of the problem state)
    solution_as_problem = f"Problem: {problem.description}\nResolved by: {solution.translated_answer}"
    solution_embedding = embed(solution_as_problem)

    # Cosine similarity (high = good, low = drift)
    similarity = cosine_similarity(problem_embedding, solution_embedding)

    # Error is inverse of similarity
    return 1.0 - similarity
```

---

### 3. Prediction Failures

Do implications from the metaphor actually hold?

This is the most important dimension—it tests whether the metaphor is *valid* for this problem.

```python
def measure_prediction_failures(solution: Solution, problem: Problem) -> int:
    """Count implications from the metaphor that don't hold for the problem."""

    metaphor = solution.metaphor_solution.projection.metaphor

    # Generate predictions the metaphor makes
    prompt = f"""
    We analyzed this problem using the {metaphor.name} metaphor:
    Problem: {problem.description}

    The metaphor implies certain things must be true. List 3-5 predictions
    that the metaphor makes about the original problem.

    Format: One prediction per line, stated as a testable claim about
    the original problem (not the metaphor).
    """
    predictions = parse_list(llm_call(prompt))

    # Test each prediction
    failures = 0
    for prediction in predictions:
        prompt = f"""
        Problem: {problem.description}
        Prediction: {prediction}

        Is this prediction TRUE or FALSE for the original problem?
        Consider: Does the problem actually exhibit this property?

        Answer: TRUE or FALSE, then brief reason.
        """
        response = llm_call(prompt, max_tokens=50)
        if "FALSE" in response.upper():
            failures += 1

    return failures
```

---

## Computing Total Distortion

```python
def compute_distortion(solution: Solution, problem: Problem) -> Distortion:
    """Compute all distortion metrics."""

    structural_loss = measure_structural_loss(solution, problem)
    round_trip_error = measure_round_trip_error(solution, problem)
    prediction_failures = measure_prediction_failures(solution, problem)

    return Distortion(
        structural_loss=structural_loss,
        round_trip_error=round_trip_error,
        prediction_failures=prediction_failures
    )
```

With the Distortion type:

```python
@dataclass(frozen=True)
class Distortion:
    structural_loss: float      # 0.0 to 1.0
    round_trip_error: float     # 0.0 to 1.0
    prediction_failures: int    # 0 to N

    STRUCTURAL_WEIGHT: ClassVar[float] = 0.3
    ROUND_TRIP_WEIGHT: ClassVar[float] = 0.4
    PREDICTION_WEIGHT: ClassVar[float] = 0.3
    PREDICTION_PENALTY: ClassVar[float] = 0.1

    @property
    def total(self) -> float:
        prediction_score = min(1.0, self.prediction_failures * self.PREDICTION_PENALTY)
        return (
            self.structural_loss * self.STRUCTURAL_WEIGHT +
            self.round_trip_error * self.ROUND_TRIP_WEIGHT +
            prediction_score * self.PREDICTION_WEIGHT
        )

    @property
    def acceptable(self) -> bool:
        return self.total < 0.5
```

---

## Verification Decision

```python
def verify(solution: Solution, problem: Problem) -> tuple[Distortion, bool]:
    """Complete verification pipeline."""

    distortion = compute_distortion(solution, problem)

    # Primary check: total distortion
    if not distortion.acceptable:
        return distortion, False

    # Secondary checks
    if distortion.prediction_failures > 2:
        # Too many failed predictions = metaphor is broken
        return distortion, False

    if distortion.structural_loss > 0.6:
        # Too much of the problem ignored
        return distortion, False

    if distortion.round_trip_error > 0.7:
        # Solution drifted too far from problem
        return distortion, False

    return distortion, True
```

---

## Backtrack Decisions

When verification fails, decide how to recover:

```python
def decide_recovery(distortion: Distortion, solution: Solution) -> str:
    """Decide what to do when verification fails."""

    # High structural loss → try lower abstraction
    if distortion.structural_loss > 0.5:
        return "retry_lower_abstraction"

    # High round-trip error → try different abstraction
    if distortion.round_trip_error > 0.6:
        return "retry_different_abstraction"

    # Many prediction failures → metaphor is wrong
    if distortion.prediction_failures > 2:
        return "try_different_metaphor"

    # Marginal failure → might improve with better projection
    if distortion.total < 0.6:
        return "retry_projection"

    # General failure
    return "try_different_metaphor"
```

---

## Quick Verification

For efficiency, run quick checks before full verification:

```python
def quick_verify(solution: Solution, problem: Problem) -> bool:
    """Fast sanity check before full verification."""

    # Check 1: Solution isn't empty
    if not solution.translated_answer or len(solution.translated_answer) < 20:
        return False

    # Check 2: At least one action
    if not solution.specific_actions:
        return False

    # Check 3: Quick relevance check
    prompt = f"""
    Problem: {problem.description}
    Proposed solution: {solution.translated_answer[:200]}

    Is this solution relevant to the problem? (yes/no)
    """
    response = llm_call(prompt, max_tokens=10)
    if "no" in response.lower():
        return False

    return True
```

---

## Example: Full Verification

**Solution**:
```
Problem: "API is slow, caching didn't help"
Translated answer: "The bottleneck is in the database query layer,
before the cache. Optimize the queries directly."
Actions: ["Profile queries", "Add indexes", "Rewrite slow queries"]
```

**Structural Loss**:
```
Gaps from projection: ["complaining"] (1 gap)
Mappings: 5
Gap-based loss: 1/6 = 0.17

Constraints: ["within sprint", "no cost increase"]
Both addressed by actions: 2/2 = 1.0

LLM completeness: 0.85

Structural loss = 1 - (0.83*0.3 + 1.0*0.3 + 0.85*0.4) = 0.11
```

**Round-Trip Error**:
```
Re-projection: "Pipe system had constriction at processing junction,
upstream of reservoir. Constriction was widened."

Original projection: "Pipe system has low flow rate, reservoir was ineffective"

Similarity: 0.75 (same structure, but re-projection is in past tense
and includes resolution)

Round-trip error: 0.25
```

**Prediction Failures**:
```
Predictions:
1. "There is a single primary bottleneck" → TRUE
2. "The bottleneck is upstream of the cache" → TRUE (by definition)
3. "Fixing the bottleneck will improve flow" → TRUE (reasonable)
4. "The system behaves like fluid flow" → PARTIAL (discrete requests, not fluid)

Failures: 0-1 (depending on how strict)
```

**Final Distortion**:
```
Distortion(
    structural_loss=0.11,
    round_trip_error=0.25,
    prediction_failures=1
)

total = 0.11*0.3 + 0.25*0.4 + 0.1*0.3 = 0.033 + 0.10 + 0.03 = 0.163

acceptable = True (0.163 < 0.5)
```

**Verification Result**: PASSED

---

## Verification vs Challenge

| Aspect | CHALLENGE | VERIFY |
|--------|-----------|--------|
| When | Before solving | After translation |
| Tests | Metaphor fit | Solution quality |
| Question | "Will this break?" | "Did this work?" |
| Failure action | Try different metaphor | Depends on failure type |
| Metrics | Robustness score | Distortion metrics |

CHALLENGE catches bad metaphors early. VERIFY catches bad solutions late.

---

## Metrics

| Metric | Description |
|--------|-------------|
| `verification_time_ms` | Time to complete verification |
| `structural_loss` | Fraction of problem not addressed |
| `round_trip_error` | Transformation drift |
| `prediction_failures` | Metaphor implications that failed |
| `total_distortion` | Weighted combination |
| `verified` | Pass/fail |

---

*Verification is the final judge. A solution that doesn't verify shouldn't ship.*
