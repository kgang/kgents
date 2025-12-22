# The Critic: SPECS-based Self-Evaluation Protocol

> *"A generator without a critic is just a random number generator."* - SPECS

**Status:** Specification v1.0
**Date:** 2025-12-11
**Prerequisites:** `agentese.md`, `curator.md`
**Integrations:** self.judgment.*, CriticsLoop middleware

---

## Prologue: The Problem of Uncritical Generation

Creative systems need more than raw generation capability. Without evaluation, generative output is indistinguishable from noise. The Wundt Curator filters based on aesthetic novelty, but true creative refinement requires:

1. **Novelty Assessment** - Is this new?
2. **Utility Assessment** - Is this useful?
3. **Surprise Assessment** - Is this unexpected given context?
4. **Iterative Refinement** - Can we improve based on critique?

The **SPECS** framework (Standardised Procedure for Evaluating Creative Systems, Jordanous 2012) provides the theoretical foundation for evaluating computational creativity.

---

## Part I: Core Concepts

### 1.1 The Critique Dataclass

```python
@dataclass(frozen=True)
class Critique:
    """SPECS-based evaluation result."""
    novelty: float      # 0-1: Is this new relative to prior work?
    utility: float      # 0-1: Is this useful for the stated purpose?
    surprise: float     # 0-1: Is this unexpected given context?
    overall: float      # Weighted combination of above
    reasoning: str      # Why these scores?
    suggestions: list[str]  # How to improve?
```

### 1.2 Scoring Criteria

| Criterion | Question | Low Score (0.0) | High Score (1.0) |
|-----------|----------|-----------------|------------------|
| Novelty | Is this new? | Exact copy | Completely original |
| Utility | Is this useful? | No purpose served | Perfectly fit for purpose |
| Surprise | Is this unexpected? | Completely predictable | Genuinely surprising |

### 1.3 Overall Score Computation

The overall score is a weighted combination:

```
overall = w_novelty * novelty + w_utility * utility + w_surprise * surprise
```

Default weights: `novelty=0.4, utility=0.4, surprise=0.2`

The emphasis on novelty and utility over surprise reflects the SPECS insight that creative artifacts must be both new AND valuable.

---

## Part II: AGENTESE Integration

### 2.1 New Judgment Aspects

The Critic extends `self.judgment.*` with new aspects:

| Path | Purpose | Returns |
|------|---------|---------|
| `self.judgment.critique` | Evaluate artifact against SPECS criteria | `Critique` |
| `self.judgment.refine` | Auto-improvement loop | `RefinedArtifact` |

### 2.2 Affordances Update

```python
JUDGMENT_AFFORDANCES = {
    "judgment": ("taste", "surprise", "expectations", "calibrate", "critique", "refine"),
}
```

### 2.3 Example Usage

```python
# Direct critique
critique = await logos.invoke(
    "self.judgment.critique",
    observer,
    artifact=generated_output,
    criteria=["novelty", "utility", "surprise"],
    purpose="Write engaging documentation",
)

if critique.overall < 0.7:
    for suggestion in critique.suggestions:
        print(f"Consider: {suggestion}")

# Auto-refinement
refined, final_critique = await logos.invoke(
    "self.judgment.refine",
    observer,
    artifact=draft,
    threshold=0.8,
    max_iterations=3,
)
```

---

## Part III: The Critics Loop

### 3.1 Generator-Critic Pairing

The CriticsLoop implements the fundamental insight from creative AI research: separate generation from evaluation, then iterate.

```python
class CriticsLoop:
    """Generative-Evaluative Pairing."""

    def __init__(
        self,
        max_iterations: int = 3,
        threshold: float = 0.7,
        weights: CritiqueWeights | None = None,
    ):
        self.max_iterations = max_iterations
        self.threshold = threshold
        self.weights = weights or CritiqueWeights()

    async def generate_with_critique(
        self,
        logos: Logos,
        observer: Umwelt,
        generator_path: str,
        **kwargs: Any,
    ) -> tuple[Any, Critique]:
        """
        Generator -> Critic -> Refine loop.

        1. Generate initial artifact
        2. Critique it
        3. If below threshold, refine based on feedback
        4. Repeat until threshold met or max iterations
        """
        ...
```

### 3.2 Refinement Strategy

When critique scores are below threshold:

1. **Extract suggestions** from critique
2. **Invoke refinement** via `concept.refine.apply`
3. **Re-critique** the refined output
4. **Terminate** when threshold met OR max iterations exceeded

```python
async def _refine_artifact(
    self,
    logos: Logos,
    observer: Umwelt,
    artifact: Any,
    critique: Critique,
) -> Any:
    """Apply critique feedback to improve artifact."""
    return await logos.invoke(
        "concept.refine.apply",
        observer,
        input=artifact,
        feedback=critique,
        suggestions=critique.suggestions,
    )
```

### 3.3 Early Termination

The loop terminates early if:
- `critique.overall >= threshold` (success)
- Refinement produces identical output (no progress)
- Max iterations reached (best effort)

---

## Part IV: Evaluation Strategies

### 4.1 Novelty Assessment

Novelty is measured as distance from known prior work:

```python
async def _assess_novelty(
    self,
    artifact: Any,
    prior_work: list[Any] | None = None,
) -> float:
    """
    Measure novelty relative to prior work.

    If no prior work provided, uses structural complexity as proxy.
    """
    if not prior_work:
        # Use structural analysis as fallback
        return self._structural_novelty(artifact)

    # Compute minimum distance to any prior work
    distances = [
        await self._semantic_distance(artifact, prior)
        for prior in prior_work
    ]
    return min(distances) if distances else 0.5
```

### 4.2 Utility Assessment

Utility requires understanding purpose. The evaluator checks:

1. **Purpose alignment** - Does artifact serve stated purpose?
2. **Completeness** - Does it address all requirements?
3. **Coherence** - Is it internally consistent?

```python
async def _assess_utility(
    self,
    artifact: Any,
    purpose: str | None = None,
) -> float:
    """
    Measure utility for stated purpose.

    Without explicit purpose, defaults to coherence check.
    """
    if not purpose:
        return self._coherence_score(artifact)

    # Check alignment with purpose
    return await self._purpose_alignment(artifact, purpose)
```

### 4.3 Surprise Assessment

Surprise leverages the existing Wundt Curator infrastructure:

```python
async def _assess_surprise(
    self,
    artifact: Any,
    observer: Umwelt,
) -> float:
    """
    Measure surprise relative to observer's expectations.

    Delegates to Wundt Curator's surprise measurement.
    """
    taste_result = await self._evaluate_taste(observer, content=artifact)
    return taste_result.get("novelty", 0.5)
```

---

## Part V: Integration with Generation Aspects

### 5.1 Optional Auto-Critique

Generation aspects (e.g., `concept.refine`, `concept.blend.forge`) can optionally enable auto-critique:

```python
# Without auto-critique (default)
result = await logos.invoke("concept.blend.forge", observer, inputs=[a, b])

# With auto-critique
result, critique = await logos.invoke(
    "concept.blend.forge",
    observer,
    inputs=[a, b],
    auto_critique=True,
    critique_threshold=0.7,
)
```

### 5.2 Middleware Integration

The CriticsLoop can be composed as middleware:

```python
# Wrap any generative path
critics_logos = logos.with_middleware(CriticsLoop(threshold=0.7))
result = await critics_logos.invoke("concept.generate.story", observer)
# Result automatically refined via critique loop
```

---

## Part VI: Configuration

### 6.1 Default Configuration

```python
CRITIC_DEFAULTS = {
    "max_iterations": 3,
    "threshold": 0.7,
    "weights": {
        "novelty": 0.4,
        "utility": 0.4,
        "surprise": 0.2,
    },
    "require_suggestions": True,  # Always provide improvement suggestions
}
```

### 6.2 Per-Context Calibration

Different creative contexts may weight criteria differently:

```python
# Art (emphasize novelty and surprise)
art_weights = CritiqueWeights(novelty=0.5, utility=0.2, surprise=0.3)

# Engineering (emphasize utility)
eng_weights = CritiqueWeights(novelty=0.2, utility=0.6, surprise=0.2)

# Science (balanced with slight utility emphasis)
sci_weights = CritiqueWeights(novelty=0.35, utility=0.45, surprise=0.2)
```

---

## Part VII: Success Criteria

### Implementation Complete When:

- [ ] `Critique` dataclass implemented (frozen, hashable)
- [ ] `CritiqueWeights` configuration class
- [ ] `CriticsLoop` class with `generate_with_critique`
- [ ] `self.judgment.critique` aspect registered
- [ ] `self.judgment.refine` aspect registered
- [ ] Integration with existing JudgmentNode in self_.py
- [ ] Novelty assessment working (with fallback)
- [ ] Utility assessment working (purpose-aware)
- [ ] Surprise assessment delegating to Wundt
- [ ] Tests for critique scoring
- [ ] Tests for loop iteration and termination
- [ ] Tests for max iterations boundary

### Test Properties

```python
def test_critique_scores_novelty():
    """Identical artifacts have low novelty."""
    critique = await evaluate(artifact, prior_work=[artifact])
    assert critique.novelty < 0.1

def test_critique_loop_improves():
    """Each iteration should improve or maintain score."""
    result, critiques = await loop.generate_with_trace(...)
    for i in range(1, len(critiques)):
        assert critiques[i].overall >= critiques[i-1].overall * 0.9  # Allow some variance

def test_critique_max_iterations():
    """Loop terminates at max iterations."""
    loop = CriticsLoop(max_iterations=3, threshold=1.0)  # Impossible threshold
    result, critique = await loop.generate_with_critique(...)
    # Should complete without hanging
```

---

## Appendix A: Research References

1. **Jordanous, A.** - "A Standardised Procedure for Evaluating Creative Systems: Computational Creativity Evaluation Based on What it is to be Creative" (2012)
   - SPECS framework
   - Evaluation criteria for computational creativity

2. **Boden, M. A.** - "The Creative Mind: Myths and Mechanisms" (2004)
   - P-creativity vs H-creativity
   - Exploratory, combinational, and transformational creativity

3. **Colton, S.** - "Creativity vs. the Perception of Creativity in Computational Systems" (2008)
   - Framing problem
   - Importance of explanation/reasoning in creative output

4. **Ritchie, G.** - "Some Empirical Criteria for Attributing Creativity to a Computer Program" (2007)
   - Typicality and quality metrics
   - Statistical evaluation of creative systems

---

## Appendix B: Principle Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Critique provides architectural quality assessment |
| **Ethical** | Self-evaluation maintains agent responsibility for output |
| **Joy-Inducing** | Iterative refinement improves output quality |
| **Composable** | CriticsLoop composes with any generation aspect |
| **Generative** | Suggestions enable continuous improvement |

---

*"A generator without a critic is just a random number generator."*
