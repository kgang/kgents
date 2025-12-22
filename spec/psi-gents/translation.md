# TRANSLATE Stage

> Map the metaphor-space solution back to problem-space terms.

---

## Purpose

Convert the conclusion reached in metaphor space into concrete, actionable terms for the original problem. This is $\Phi^{-1}$: the inverse mapping.

**The core question**: What does this metaphor-space answer mean for my actual problem?

---

## Interface

```python
def translate(
    metaphor_solution: MetaphorSolution,
    problem: Problem
) -> tuple[str, list[str], float]:
    """
    Translate metaphor solution back to problem terms.

    Returns:
        - translated_answer: The answer in problem-space terms
        - specific_actions: Concrete next steps
        - confidence: Translation confidence (0.0 to 1.0)
    """
```

---

## The Translation Process

### Step 1: Reverse the Mappings

Use the concept mappings in reverse to translate terms.

```python
def reverse_mappings(projection: Projection) -> dict[str, str]:
    """Create reverse mapping: metaphor → problem concepts."""
    return {m.target: m.source for m in projection.mappings}
```

### Step 2: Translate the Conclusion

Convert the metaphor-space conclusion to problem-space terms.

```python
def translate_conclusion(
    conclusion: str,
    reverse_map: dict[str, str],
    projection: Projection,
    problem: Problem
) -> str:
    """Translate conclusion using reverse mappings."""

    prompt = f"""
    Metaphor conclusion: {conclusion}
    Metaphor used: {projection.metaphor.name}

    Reverse mappings (metaphor → problem):
    {reverse_map}

    Original problem: {problem.description}
    Problem context: {problem.domain}

    Translate the conclusion into concrete terms for the original problem.
    - Replace metaphor concepts with their problem equivalents
    - Use terminology appropriate to the problem context
    - Preserve the logical structure of the conclusion
    - Make it actionable and specific

    The result should read as a direct answer to the original problem,
    not as a metaphor explanation.
    """

    return llm_call(prompt)
```

### Step 3: Extract Specific Actions

Turn the translated answer into concrete next steps.

```python
def extract_actions(
    translated_answer: str,
    problem: Problem
) -> list[str]:
    """Extract concrete, actionable next steps."""

    prompt = f"""
    Translated answer: {translated_answer}
    Original problem: {problem.description}
    Constraints: {problem.constraints}

    Extract 2-5 specific, concrete actions to implement this answer.
    Each action should be:
    - Specific enough to act on immediately
    - Relevant to the problem context
    - Respectful of the stated constraints

    Format: One action per line, starting with a verb.
    """

    response = llm_call(prompt)
    return parse_action_list(response)
```

### Step 4: Calculate Translation Confidence

Measure how confident we are in the translation.

```python
def calculate_translation_confidence(
    metaphor_solution: MetaphorSolution,
    translated_answer: str,
    problem: Problem
) -> float:
    """Calculate confidence in the translation."""

    # Factor 1: Original projection confidence
    projection_conf = metaphor_solution.projection.confidence

    # Factor 2: Mapping coverage (more mappings = easier translation)
    coverage = metaphor_solution.projection.coverage

    # Factor 3: LLM self-assessment
    prompt = f"""
    Original problem: {problem.description}
    Metaphor conclusion: {metaphor_solution.conclusion}
    Translated answer: {translated_answer}

    Rate the translation quality (0.0 to 1.0):
    - Does the translation preserve the meaning of the conclusion?
    - Is the translated answer appropriate for the problem domain?
    - Are there any concepts that didn't translate well?

    Return only a number between 0.0 and 1.0.
    """
    llm_conf = float(llm_call(prompt, max_tokens=10))

    # Weighted combination
    return (
        projection_conf * 0.3 +
        coverage * 0.3 +
        llm_conf * 0.4
    )
```

---

## Handling Translation Gaps

Some metaphor concepts may not reverse-map cleanly.

### Gap Types

1. **Metaphor-native concepts**: Concepts that exist only in the metaphor
   - Plumbing "pressure" may not have a direct software equivalent

2. **Elaborated concepts**: Metaphor reasoning introduced new concepts
   - "Upstream constriction" was derived, not mapped

3. **Structural concepts**: Metaphor structural elements
   - "Flow direction" as a concept

### Gap Handling

```python
def handle_translation_gaps(
    conclusion: str,
    reverse_map: dict[str, str],
    problem: Problem
) -> tuple[str, list[str]]:
    """Handle concepts that don't reverse-map cleanly."""

    # Identify concepts in conclusion that aren't in reverse_map
    conclusion_concepts = extract_concepts_from_text(conclusion)
    mapped = set(reverse_map.keys())
    gaps = [c for c in conclusion_concepts if c not in mapped]

    if not gaps:
        return conclusion, []

    # For each gap, ask LLM for best translation
    translations = {}
    for gap_concept in gaps:
        prompt = f"""
        A {problem.domain} problem was analyzed using another framework
        Gap concept: "{gap_concept}" (from the metaphor, no direct mapping exists)
        Problem context: {problem.domain}

        What would "{gap_concept}" mean in the context of {problem.domain}?
        Give the best equivalent concept or phrase.
        """
        translations[gap_concept] = llm_call(prompt, max_tokens=30).strip()

    # Apply translations
    translated = conclusion
    for gap, replacement in translations.items():
        translated = translated.replace(gap, replacement)

    return translated, list(translations.items())
```

---

## Constraint Verification

Ensure the translated answer respects problem constraints.

```python
def verify_constraints(
    translated_answer: str,
    actions: list[str],
    problem: Problem
) -> tuple[bool, list[str]]:
    """Verify that the answer respects problem constraints."""

    if not problem.constraints:
        return True, []

    violations = []
    for constraint in problem.constraints:
        prompt = f"""
        Constraint: {constraint}
        Proposed answer: {translated_answer}
        Proposed actions: {actions}

        Does this answer/actions violate the constraint?
        Answer: VIOLATES or RESPECTS, then brief explanation.
        """
        response = llm_call(prompt, max_tokens=50)
        if "VIOLATES" in response.upper():
            violations.append(f"{constraint}: {response}")

    return len(violations) == 0, violations
```

---

## Full Translation Pipeline

```python
def translate(
    metaphor_solution: MetaphorSolution,
    problem: Problem
) -> tuple[str, list[str], float]:
    """Complete translation pipeline."""

    projection = metaphor_solution.projection

    # Step 1: Reverse mappings
    reverse_map = reverse_mappings(projection)

    # Step 2: Handle gaps in conclusion
    conclusion_with_gaps_handled, gap_translations = handle_translation_gaps(
        metaphor_solution.conclusion,
        reverse_map,
        problem
    )

    # Step 3: Full translation
    translated_answer = translate_conclusion(
        conclusion_with_gaps_handled,
        reverse_map,
        projection,
        problem
    )

    # Step 4: Extract actions
    actions = extract_actions(translated_answer, problem)

    # Step 5: Verify constraints
    constraints_ok, violations = verify_constraints(
        translated_answer, actions, problem
    )

    if not constraints_ok:
        # Attempt to modify actions to respect constraints
        actions = modify_actions_for_constraints(actions, violations, problem)
        translated_answer += f"\n\nNote: Modified to respect constraints."

    # Step 6: Calculate confidence
    confidence = calculate_translation_confidence(
        metaphor_solution, translated_answer, problem
    )

    # Lower confidence if there were gaps or constraint issues
    if gap_translations:
        confidence *= 0.9
    if not constraints_ok:
        confidence *= 0.8

    return translated_answer, actions, confidence
```

---

## Example: Full Translation

**Metaphor Solution** (from SOLVE):
```
Metaphor: Plumbing
Conclusion: "The constriction is at the 'second processing' junction,
upstream of the reservoir. Recommendation: Widen the pipe at 'second
processing' stage, or add a bypass around that junction."
```

**Reverse Mappings**:
```
pipe system → API
low flow rate → slow
reservoir → cache
consumers → users
```

**Step 1 - Handle Gaps**:
- "second processing junction" → not mapped
- LLM inference: "second processing junction" → "database query layer"
- "constriction" → not mapped
- LLM inference: "constriction" → "performance bottleneck"

**Step 2 - Translate Conclusion**:
```
Original: "The constriction is at the 'second processing' junction,
upstream of the reservoir."

Translated: "The performance bottleneck is at the database query layer,
which executes before the cache is checked."
```

**Step 3 - Extract Actions**:
```
1. Profile the database query layer to confirm it's the bottleneck
2. Analyze the specific queries that are slow
3. Optimize slow queries (add indexes, rewrite queries, add query cache)
4. If optimization isn't sufficient, consider query result caching at that layer
5. Re-measure API response time after changes
```

**Step 4 - Verify Constraints**:
```
Constraint: "Must improve within this sprint"
→ RESPECTS: Actions are focused and achievable in a sprint

Constraint: "Cannot increase infrastructure cost"
→ RESPECTS: Optimization doesn't require new infrastructure
```

**Step 5 - Final Output**:
```
translated_answer: "The API slowness is caused by a performance bottleneck
in the database query layer. The cache didn't help because it's positioned
after the slow queries execute. Focus optimization efforts on the database
queries themselves."

actions: [
    "Profile database queries to identify the slowest ones",
    "Add missing indexes based on query patterns",
    "Rewrite inefficient queries (N+1 patterns, unnecessary joins)",
    "Consider query result caching at the database layer",
    "Measure API latency after each change"
]

confidence: 0.82
```

---

## Translation Quality Indicators

| Indicator | Good | Concerning |
|-----------|------|------------|
| Gap count | 0-2 | 5+ |
| Constraint violations | 0 | Any |
| Confidence | > 0.7 | < 0.5 |
| Action specificity | Context-specific verbs | Generic ("improve", "fix") |
| Answer length | Comparable to problem | Much longer/shorter |

---

## When Translation Fails

If translation confidence is too low, options:

1. **Re-solve with different abstraction**: Maybe too abstract → concepts too general
2. **Try different metaphor**: Some metaphors translate better to this domain
3. **Partial translation**: Return what translates well, flag the rest

```python
def handle_low_confidence_translation(
    metaphor_solution: MetaphorSolution,
    translated_answer: str,
    confidence: float,
    problem: Problem
) -> str:
    """Handle case where translation confidence is low."""

    if confidence < 0.3:
        # Too low to trust
        return f"""
        [LOW CONFIDENCE TRANSLATION]
        The metaphor analysis suggested: {metaphor_solution.conclusion}

        However, translation to problem context is uncertain.
        Key insight (may need human interpretation):
        {extract_key_insight(metaphor_solution)}

        Consider trying a different metaphor or more specific analysis.
        """

    if confidence < 0.5:
        # Usable but flag uncertainty
        return f"""
        {translated_answer}

        [Note: Some concepts didn't translate cleanly.
        Confidence: {confidence:.0%}. Human review recommended.]
        """

    return translated_answer
```

---

## Metrics

| Metric | Description |
|--------|-------------|
| `translation_time_ms` | Time to complete translation |
| `gap_count` | Concepts that didn't reverse-map |
| `constraint_violations` | Number of constraints violated |
| `action_count` | Number of specific actions extracted |
| `confidence` | Overall translation confidence |

---

*Translation is where the metaphor returns to earth. A brilliant metaphor-space solution that can't translate is worthless.*
