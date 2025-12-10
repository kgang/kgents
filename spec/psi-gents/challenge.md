# CHALLENGE Stage

> Stress-test the metaphor with adversarial cases.

---

## Purpose

Before investing in SOLVE and TRANSLATE, test whether the metaphor will hold up. This is adversarial validation: actively try to break the projection.

**The core question**: What would make this metaphor fail?

---

## Interface

```python
def challenge(projection: Projection) -> ChallengeResult:
    """
    Generate and run adversarial tests on a projection.

    Returns: ChallengeResult with survival status and counterexamples.
    """
```

---

## The Four Challenges

### 1. Inversion Challenge

"What if the opposite were true?"

Test whether the metaphor handles negation of key assumptions.

```python
def inversion_challenge(projection: Projection) -> tuple[bool, str | None]:
    """Test the metaphor against inverted assumptions."""

    prompt = f"""
    Projection: {projection.mapped_description}
    Metaphor: {projection.metaphor.name}

    Key assumption in this projection:
    - The problem involves {extract_primary_assumption(projection)}

    What if the OPPOSITE were true?
    - Would the metaphor still apply?
    - Would the same operations be relevant?

    If the metaphor breaks under inversion, explain why.
    If it survives, explain how it handles the inverted case.

    Format:
    SURVIVES: yes/no
    REASON: ...
    """

    response = llm_call(prompt)
    survives, reason = parse_challenge_response(response)
    return survives, None if survives else reason
```

**Example**:
- Projection: "API has low flow rate" (Plumbing)
- Inversion: "What if the problem is TOO MUCH flow?"
- Test: Does plumbing handle overload scenarios?
- Result: Yes, plumbing has "pressure relief" and "overflow" concepts. Survives.

---

### 2. Edge Case Challenge

"What about extreme values?"

Test the metaphor at the boundaries.

```python
def edge_case_challenge(projection: Projection) -> tuple[bool, str | None]:
    """Test the metaphor at extreme values."""

    prompt = f"""
    Projection: {projection.mapped_description}
    Metaphor: {projection.metaphor.name}

    Consider extreme cases:
    1. What if the quantity is zero? (no flow, no entities, no activity)
    2. What if the quantity is very large? (massive flow, many entities, high activity)
    3. What if time is very short? (instantaneous, no delay)
    4. What if time is very long? (indefinite, permanent)

    For each extreme:
    - Does the metaphor still make sense?
    - Do the operations still apply?

    If any extreme breaks the metaphor meaningfully, explain.

    Format:
    SURVIVES: yes/no
    PROBLEMATIC_EXTREME: (which one, if any)
    REASON: ...
    """

    response = llm_call(prompt)
    return parse_challenge_response(response)
```

**Example**:
- Projection: "Pipe system with low flow rate" (Plumbing)
- Edge case: "What if flow is zero?"
- Test: Does plumbing differentiate "no flow due to blockage" vs "no flow due to no input"?
- Result: Yes, these are different diagnostics. Survives.

---

### 3. Missing Concept Challenge

"What problem aspect has no metaphor equivalent?"

Examine the gaps more deeply.

```python
def missing_concept_challenge(projection: Projection) -> tuple[bool, str | None]:
    """Test whether gaps are acceptable or fatal."""

    if not projection.gaps:
        return True, None  # No gaps to challenge

    prompt = f"""
    Projection: {projection.mapped_description}
    Metaphor: {projection.metaphor.name}

    The following problem concepts have NO metaphor equivalent:
    {projection.gaps}

    For each unmapped concept:
    1. Is it essential to solving the problem?
    2. Could ignoring it lead to a wrong solution?
    3. Is there a workaround within the metaphor?

    If any gap is ESSENTIAL and could cause wrong solutions, the metaphor fails this challenge.

    Format:
    SURVIVES: yes/no
    CRITICAL_GAP: (which one, if any)
    REASON: ...
    """

    response = llm_call(prompt)
    return parse_challenge_response(response)
```

**Example**:
- Projection: "Pipe system" mapping for "API is slow"
- Gap: "Users are complaining"
- Test: Is "complaining" essential to solving the performance problem?
- Result: No, complaining is a symptom indicator, not part of the solution. Survives with caveat.

---

### 4. False Implication Challenge

"What does the metaphor predict that's actually wrong?"

The most important challenge: test predictive validity.

```python
def false_implication_challenge(projection: Projection) -> tuple[bool, str | None]:
    """Test whether metaphor implications hold for the original problem."""

    prompt = f"""
    Projection: {projection.mapped_description}
    Metaphor: {projection.metaphor.name}
    Original problem: {projection.problem.description}

    The metaphor implies certain things. List 3-5 implications:
    "If this were really a {projection.metaphor.name} situation, then..."

    For each implication:
    - Is it actually TRUE for the original problem?
    - Or is it a FALSE prediction?

    False implications mean the metaphor doesn't really fit.

    Format:
    IMPLICATION_1: [statement]
    HOLDS: yes/no
    WHY: ...

    ...

    SURVIVES: yes/no (survives if most implications hold)
    CRITICAL_FAILURE: (which implication failed critically, if any)
    """

    response = llm_call(prompt)
    return parse_implication_response(response)
```

**Example**:
- Projection: "Pipe system with low flow rate"
- Implication 1: "There's a single point of constriction" → Maybe false (could be multiple)
- Implication 2: "Flow is continuous, not discrete" → True for API requests at scale
- Implication 3: "Adding pressure upstream would help" → Maybe true (more server capacity)
- Implication 4: "The constriction has a physical location" → True (it's in the code somewhere)
- Result: Mostly holds. Survives with caveat about potential multiple bottlenecks.

---

## Running All Challenges

```python
def challenge(projection: Projection) -> ChallengeResult:
    """Run all four challenges."""

    results = []
    counterexamples = []
    caveats = []

    # Run each challenge
    challenges = [
        ("inversion", inversion_challenge),
        ("edge_case", edge_case_challenge),
        ("missing_concept", missing_concept_challenge),
        ("false_implication", false_implication_challenge),
    ]

    for name, challenge_fn in challenges:
        survives, issue = challenge_fn(projection)
        results.append(survives)

        if not survives:
            counterexamples.append(f"{name}: {issue}")
        elif issue:  # Survived with caveat
            caveats.append(f"{name}: {issue}")

    # Overall survival: must pass at least 3 of 4
    passed = sum(results)
    survives = passed >= 3

    return ChallengeResult(
        survives=survives,
        challenges_passed=passed,
        challenges_total=len(challenges),
        counterexamples=tuple(counterexamples),
        caveats=tuple(caveats),
    )
```

---

## Severity Levels

Not all challenge failures are equal.

```python
class ChallengeSeverity(Enum):
    FATAL = "fatal"           # Metaphor is fundamentally broken
    SERIOUS = "serious"       # Major limitation, proceed with caution
    MINOR = "minor"           # Small issue, note and continue
    COSMETIC = "cosmetic"     # Doesn't affect solution validity
```

### Determining Severity

```python
def assess_severity(challenge_name: str, failure_reason: str, projection: Projection) -> ChallengeSeverity:
    """Assess how serious a challenge failure is."""

    # False implication failures are most serious
    if challenge_name == "false_implication":
        if "critical" in failure_reason.lower() or "fundamental" in failure_reason.lower():
            return ChallengeSeverity.FATAL
        return ChallengeSeverity.SERIOUS

    # Missing concept depends on gap importance
    if challenge_name == "missing_concept":
        if "essential" in failure_reason.lower():
            return ChallengeSeverity.SERIOUS
        return ChallengeSeverity.MINOR

    # Edge cases are usually minor unless zero/infinity matters
    if challenge_name == "edge_case":
        if "zero" in failure_reason.lower() and projection.problem.complexity > 0.7:
            return ChallengeSeverity.SERIOUS
        return ChallengeSeverity.MINOR

    # Inversion is usually serious if it fails
    if challenge_name == "inversion":
        return ChallengeSeverity.SERIOUS

    return ChallengeSeverity.MINOR
```

---

## Backtrack Decision

```python
def should_backtrack(result: ChallengeResult, projection: Projection) -> tuple[bool, str]:
    """Decide whether to backtrack to RETRIEVE."""

    if not result.survives:
        # Failed challenges → backtrack
        return True, f"Challenge failures: {result.counterexamples}"

    # Even if survived, check for serious caveats
    serious_caveats = [c for c in result.caveats if "serious" in c.lower()]
    if len(serious_caveats) > 1:
        return True, f"Too many serious caveats: {serious_caveats}"

    # Low robustness with high complexity problem → risky
    if result.robustness < 0.6 and projection.problem.complexity > 0.7:
        return True, "Low robustness for complex problem"

    return False, ""
```

---

## Quick Challenge Mode

For efficiency, run a quick challenge before full challenge:

```python
def quick_challenge(projection: Projection) -> bool:
    """Fast check: is this projection obviously broken?"""

    # Check 1: Coverage too low
    if projection.coverage < 0.5:
        return False

    # Check 2: Confidence too low
    if projection.confidence < 0.4:
        return False

    # Check 3: No applicable operations
    applicable = [op for op in projection.metaphor.operations
                  if operation_is_applicable(op, projection)]
    if not applicable:
        return False

    # Check 4: Quick LLM sanity check
    prompt = f"""
    Problem: {projection.problem.description}
    Metaphor: {projection.metaphor.name}
    One-line mapping: {projection.mapped_description[:200]}

    Does this metaphor make obvious sense for this problem? (yes/no, one word)
    """
    response = llm_call(prompt, max_tokens=10)
    return "yes" in response.lower()
```

---

## Challenge Caching

Avoid repeating the same challenges:

```python
class ChallengeCache:
    """Cache challenge results for similar projections."""

    def __init__(self):
        self.cache: dict[str, ChallengeResult] = {}

    def get_key(self, projection: Projection) -> str:
        """Create cache key from projection essentials."""
        return f"{projection.problem.id}:{projection.metaphor.id}:{projection.abstraction:.1f}"

    def get(self, projection: Projection) -> ChallengeResult | None:
        return self.cache.get(self.get_key(projection))

    def set(self, projection: Projection, result: ChallengeResult) -> None:
        self.cache[self.get_key(projection)] = result
```

---

## Comparison with v2.0 Jungian Shadow

| v2.0 Shadow | v3.0 Challenge |
|-------------|----------------|
| Generate "non-X" strings | Inversion challenge |
| Check if shadow "breaks" metaphor | All four challenges |
| Shadow types: negation, inversion, extreme | Structured challenge types |
| ShadowGenerator (string manipulation) | LLM-generated adversarial cases |
| "Shadow blindness" anti-pattern | False implication failures |

**Key improvement**: v3.0 challenges are semantically meaningful, not string-based. The LLM understands what would actually break the metaphor.

---

## Metrics

| Metric | Description |
|--------|-------------|
| `challenge_time_ms` | Time to run all challenges |
| `robustness` | challenges_passed / challenges_total |
| `counterexample_count` | Number of breaking issues found |
| `caveat_count` | Number of concerns noted |
| `backtrack_rate` | How often challenge causes backtrack |

---

*Challenge is the immune system. It catches bad metaphors before they infect the solution.*
