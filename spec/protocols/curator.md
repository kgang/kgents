# The Wundt Curator: Aesthetic Filtering Protocol

> *"Too simple is boring. Too complex is chaotic. The edge of chaos is beautiful."*

**Status:** Specification v1.0
**Date:** 2025-12-11
**Prerequisites:** `agentese.md`, `../principles.md`
**Integrations:** Logos (middleware), self.judgment.* context

---

## Prologue: The Problem of Sterility

A generator without taste produces entropy. Random noise or trivial repetition. The naive solution is to maximize diversity. But maximum diversity is just another form of chaos.

The **Wundt Curve** (from experimental aesthetics) describes the relationship between stimulus complexity and aesthetic pleasure. It forms an inverted U:

```
Aesthetic Value
     ^
     |        * peak (interesting)
     |       / \
     |      /   \
     |     /     \
     |----/-------\-------
     |   /         \
     |  * boring    * chaotic
     |
     +-----------------------> Novelty/Complexity
        0.0    0.5    1.0
```

The Curator applies this curve to filter agent output.

---

## Part I: Core Concepts

### 1.1 The Wundt Curve

| Zone | Novelty Range | Verdict | Action |
|------|---------------|---------|--------|
| Boring | 0.0 - 0.1 | Reject or enhance | Inject entropy via `void.entropy.sip` |
| Interesting | 0.1 - 0.9 | Accept | Pass through |
| Chaotic | 0.9 - 1.0 | Reject or compress | Compress via `concept.summary.refine` |

Thresholds are configurable. Default: `low=0.1, high=0.9`.

### 1.2 Semantic Distance as Surprise

**Surprise** measures how much an output deviates from the observer's expectations.

We define surprise as **semantic distance** between:
1. The generated output (embedded)
2. The observer's prior expectation (embedded)

```
surprise = cosine_distance(embed(output), embed(expectation))
```

If no prior expectation exists, surprise defaults to `0.5` (neutral).

### 1.3 The TasteScore

```python
@dataclass
class TasteScore:
    """Wundt curve evaluation result."""
    novelty: float       # 0.0 = identical to prior, 1.0 = completely unexpected
    complexity: float    # 0.0 = trivial, 1.0 = incomprehensible
    wundt_score: float   # Inverted U score: peaks at ~0.5
    verdict: Literal["boring", "interesting", "chaotic"]
```

The `wundt_score` is computed as:

```
wundt_score = 4 * novelty * (1 - novelty)  # Peaks at 1.0 when novelty=0.5
```

---

## Part II: AGENTESE Integration

### 2.1 The Judgment Context

The Curator extends `self.*` with a new holon: `self.judgment`.

| Path | Meaning | Returns |
|------|---------|---------|
| `self.judgment.taste` | Evaluate aesthetic quality | `TasteScore` |
| `self.judgment.surprise` | Measure Bayesian surprise | `float` |
| `self.judgment.expectations` | View/set prior expectations | `dict[str, Any]` |

### 2.2 Affordances

```python
JUDGMENT_AFFORDANCES = {
    "judgment": ("taste", "surprise", "expectations", "calibrate"),
}
```

### 2.3 Example Usage

```python
# Direct taste evaluation
score = await logos.invoke("self.judgment.taste", observer, content=output)
if score.verdict == "boring":
    output = await logos.invoke("void.entropy.sip", observer)

# Via middleware (automatic)
logos_with_curator = logos.with_curator(low=0.1, high=0.9)
result = await logos_with_curator.invoke("concept.generate.story", observer)
# Result automatically filtered through Wundt Curve
```

---

## Part III: Middleware Architecture

### 3.1 The WundtCurator

The Curator is **Logos middleware**—it wraps invocations and post-processes results.

```python
class WundtCurator:
    """Middleware for aesthetic filtering."""

    def __init__(
        self,
        low_threshold: float = 0.1,
        high_threshold: float = 0.9,
        max_retries: int = 3,
    ):
        self.low = low_threshold
        self.high = high_threshold
        self.max_retries = max_retries

    async def __call__(
        self,
        logos: Logos,
        path: str,
        observer: Umwelt,
        result: Any,
        **kwargs: Any,
    ) -> Any:
        """Post-process invocation result."""
        # Skip filtering for system paths
        if self._is_system_path(path):
            return result

        # Measure surprise
        surprise = await self._measure_surprise(result, observer)

        # Apply Wundt filtering
        if surprise < self.low:
            return await self._enhance(logos, observer, result)
        elif surprise > self.high:
            return await self._compress(logos, observer, result)
        else:
            return result  # Goldilocks zone
```

### 3.2 Integration with Logos

```python
# Method 1: Compose with existing Logos
curated_logos = logos.with_middleware(WundtCurator(low=0.1, high=0.9))

# Method 2: Per-invocation (via kwargs)
result = await logos.invoke(
    "concept.generate.poem",
    observer,
    curator=WundtCurator(low=0.2, high=0.8),
)

# Method 3: Explicit path
taste = await logos.invoke("self.judgment.taste", observer, content=some_output)
```

### 3.3 System Paths (Exempt from Filtering)

The following paths are exempt from Wundt filtering:
- `void.*` - Entropy operations should not be filtered
- `time.*` - Temporal traces are factual, not creative
- `self.judgment.*` - Avoid recursive filtering
- Paths ending in `.witness` - Historical data is factual

---

## Part IV: Semantic Distance Implementation

### 4.1 Embedding Strategy

The default implementation uses **normalized embeddings** with cosine distance.

```python
async def semantic_distance(a: str, b: str) -> float:
    """
    Compute semantic distance between two texts.

    Returns:
        0.0 = identical meaning
        1.0 = completely unrelated
    """
    embed_a = await embed(a)
    embed_b = await embed(b)
    return cosine_distance(embed_a, embed_b)
```

### 4.2 Expectation Management

The observer's `Umwelt` stores expectations in its context:

```python
class Umwelt:
    context: dict[str, Any]

    def set_expectation(self, key: str, value: str) -> None:
        """Set expectation for surprise calculation."""
        self.context["expectations"] = self.context.get("expectations", {})
        self.context["expectations"][key] = await embed(value)

    def get_expectation(self, key: str) -> Optional[np.ndarray]:
        """Get embedded expectation."""
        return self.context.get("expectations", {}).get(key)
```

### 4.3 Fallback: Structural Surprise

If embeddings are unavailable, use **structural surprise**:

```python
def structural_surprise(output: Any, prior: Any) -> float:
    """
    Fallback surprise metric based on structure.

    Measures: length difference, type difference, key overlap.
    """
    if type(output) != type(prior):
        return 0.9  # High surprise: different types

    if isinstance(output, str):
        len_ratio = len(output) / max(len(prior), 1)
        return min(abs(1.0 - len_ratio), 1.0)

    if isinstance(output, dict):
        keys_out = set(output.keys())
        keys_prior = set(prior.keys())
        overlap = len(keys_out & keys_prior) / max(len(keys_out | keys_prior), 1)
        return 1.0 - overlap

    return 0.5  # Neutral
```

---

## Part V: Enhancement and Compression

### 5.1 Enhancement (Too Boring)

When output is too similar to expectations:

```python
async def _enhance(
    self,
    logos: Logos,
    observer: Umwelt,
    result: Any,
) -> Any:
    """Inject entropy to increase novelty."""
    noise = await logos.invoke("void.entropy.sip", observer)

    # Blend result with noise
    return await logos.invoke(
        "concept.blend.forge",
        observer,
        inputs=[result, noise],
    )
```

### 5.2 Compression (Too Chaotic)

When output is too distant from expectations:

```python
async def _compress(
    self,
    logos: Logos,
    observer: Umwelt,
    result: Any,
) -> Any:
    """Compress toward coherence."""
    return await logos.invoke(
        "concept.summary.refine",
        observer,
        input=result,
        target_coherence=0.7,
    )
```

---

## Part VI: Configuration and Tuning

### 6.1 Default Configuration

```python
CURATOR_DEFAULTS = {
    "low_threshold": 0.1,      # Below this: boring
    "high_threshold": 0.9,     # Above this: chaotic
    "max_retries": 3,          # Enhancement/compression attempts
    "embedding_model": None,   # Use system default
    "fallback_to_structural": True,
}
```

### 6.2 Per-Agent Calibration

Different agents may have different aesthetic preferences:

```python
# A-gent (Art) prefers higher novelty
art_curator = WundtCurator(low=0.3, high=0.95)

# B-gent (Science) prefers lower novelty (more grounded)
science_curator = WundtCurator(low=0.05, high=0.7)
```

### 6.3 Adaptive Thresholds

The Curator can learn optimal thresholds from feedback:

```python
async def calibrate(
    self,
    feedback: list[tuple[Any, float]],  # (output, rating)
) -> None:
    """
    Calibrate thresholds from human feedback.

    Finds thresholds that maximize rating within the "interesting" zone.
    """
    # Implementation: Bayesian optimization over threshold space
    ...
```

---

## Part VII: Success Criteria

### Implementation Complete When:

- [ ] `TasteScore` dataclass implemented
- [ ] `SemanticDistance` function implemented (with fallback)
- [ ] `WundtCurator` middleware implemented
- [ ] `self.judgment.*` paths registered in AGENTESE
- [ ] Integration with Logos via `.with_middleware()`
- [ ] Enhancement via `void.entropy.sip` working
- [ ] Compression via `concept.summary.refine` working
- [ ] Tests for boring/interesting/chaotic filtering
- [ ] Property-based test: Wundt curve is inverted U

### Test Properties

```python
@given(st.floats(0, 1))
def test_wundt_curve_inverted_u(novelty: float):
    """Wundt score peaks at mid-range novelty."""
    score = wundt_score(novelty)
    assert 0 <= score <= 1
    # Peak is at novelty=0.5
    assert wundt_score(0.5) >= wundt_score(novelty)
```

---

## Appendix A: Research References

1. **Berlyne, D. E.** - "Aesthetics and Psychobiology" (1971)
   - Arousal potential theory
   - The inverted U relationship

2. **Schmidhuber, J.** - "Formal Theory of Creativity, Fun, and Intrinsic Motivation" (2010)
   - Compression progress as aesthetic value
   - Interestingness as rate of learning

3. **Silvia, P. J.** - "Exploring the Psychology of Interest" (2006)
   - Novelty-complexity model
   - Coping potential in aesthetic appreciation

---

## Appendix B: Principle Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | The Curator IS taste—architectural quality filtering |
| **Joy-Inducing** | Interesting > Boring or Chaotic |
| **Composable** | Middleware pattern composes with any Logos operation |
| **Heterarchical** | Per-agent calibration, no universal threshold |
| **Generative** | Enhancement creates novel combinations |

---

*"The noun is a lie. There is only the rate of change."*
