# RETRIEVE Stage

> Find candidate metaphors that might fit the problem.

---

## Purpose

Given a novel problem, identify metaphors worth trying. This is not about finding THE right metaphor—it's about generating good candidates for the search loop.

---

## Interface

```python
def retrieve(
    problem: Problem,
    limit: int = 5,
    exclude: list[str] | None = None,  # Metaphor IDs to skip
    context: str | None = None,         # Why we're retrying (from backtrack)
) -> list[tuple[Metaphor, float]]:
    """
    Returns: List of (metaphor, score) pairs, sorted by score descending.
    """
```

---

## Three Retrieval Methods

### 1. Embedding Similarity (L-gent Integration)

The primary method. Uses semantic similarity between problem and metaphor embeddings.

```python
def retrieve_by_embedding(problem: Problem, corpus: MetaphorCorpus) -> list[tuple[Metaphor, float]]:
    """Semantic retrieval via embedding similarity."""
    if problem.embedding is None:
        problem = embed_problem(problem)  # L-gent call

    scores = []
    for metaphor in corpus:
        if metaphor.embedding is None:
            metaphor = embed_metaphor(metaphor)

        similarity = cosine_similarity(problem.embedding, metaphor.embedding)
        scores.append((metaphor, similarity))

    return sorted(scores, key=lambda x: x[1], reverse=True)
```

**Why this works**: Good metaphors have semantic overlap with the problem domain. "Team communication problems" will be closer to "Ecosystem" than to "Thermodynamics."

**L-gent integration**:
- Use L-gent's embedder for consistent embedding space
- Benefit from L-gent's caching and batching

---

### 2. Learned Retrieval (From LEARN Stage)

Over time, the system learns which metaphors work for which problem types.

```python
def retrieve_by_learning(
    problem: Problem,
    model: RetrievalModel,
    corpus: MetaphorCorpus
) -> list[tuple[Metaphor, float]]:
    """Retrieval informed by historical success."""
    scores = []
    for metaphor in corpus:
        expected_reward = model.predict(problem, metaphor)
        scores.append((metaphor, expected_reward))

    return sorted(scores, key=lambda x: x[1], reverse=True)
```

**Features used by the model**:
- Problem domain
- Problem complexity
- Problem embedding cluster
- Historical (domain, metaphor) success rate
- Historical (complexity_range, metaphor) success rate

**Cold start**: Before learning data exists, fall back to embedding similarity.

---

### 3. Generative Retrieval (LLM-based)

When the corpus doesn't have good candidates, ask the LLM to suggest metaphors.

```python
def retrieve_by_generation(problem: Problem, existing_candidates: list[Metaphor]) -> list[Metaphor]:
    """Generate new metaphor candidates via LLM."""

    prompt = f"""
    Problem: {problem.description}
    Domain: {problem.domain}

    The following metaphors have been tried but don't fit well:
    {[m.name for m in existing_candidates]}

    Suggest 3 different conceptual frameworks that might help reason about this problem.
    For each, provide:
    - Name
    - Domain (where the metaphor comes from)
    - Key operations (things you can do in this framework)
    - Why it might apply

    Focus on frameworks that have rich operational vocabulary.
    """

    response = llm_call(prompt)
    return parse_metaphor_suggestions(response)
```

**When to use**:
- Corpus retrieval returns low scores (< 0.3)
- After N backtracks without success
- Problem domain is unusual

**Caution**: Generated metaphors need quality checks before use.

---

## Combined Retrieval

```python
def retrieve(
    problem: Problem,
    limit: int = 5,
    exclude: list[str] | None = None,
    context: str | None = None,
) -> list[tuple[Metaphor, float]]:
    """
    Combined retrieval: embedding + learning + generation.
    """
    exclude = exclude or []

    # 1. Embedding similarity
    embedding_candidates = retrieve_by_embedding(problem, corpus)
    embedding_candidates = [(m, s) for m, s in embedding_candidates if m.id not in exclude]

    # 2. Learned retrieval (if model exists)
    if retrieval_model.is_trained:
        learned_candidates = retrieve_by_learning(problem, retrieval_model, corpus)
        learned_candidates = [(m, s) for m, s in learned_candidates if m.id not in exclude]

        # Combine scores (weighted average)
        combined = combine_scores(
            embedding_candidates,
            learned_candidates,
            weights=(0.4, 0.6)  # Learning dominates when available
        )
    else:
        combined = embedding_candidates

    # 3. Check if we need generation
    top_score = combined[0][1] if combined else 0.0
    if top_score < 0.3 or (context and "no good candidates" in context):
        generated = retrieve_by_generation(problem, [m for m, _ in combined[:3]])
        # Score generated metaphors by embedding (no learning data yet)
        for metaphor in generated:
            metaphor = embed_metaphor(metaphor)
            score = cosine_similarity(problem.embedding, metaphor.embedding)
            combined.append((metaphor, score * 0.9))  # Slight penalty for untested

    # Sort and limit
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    return combined[:limit]
```

---

## Exploration vs Exploitation

The retrieval system faces the classic explore/exploit tradeoff:
- **Exploit**: Use metaphors that worked before
- **Explore**: Try new metaphors to improve the model

### Thompson Sampling Approach

```python
def retrieve_with_exploration(
    problem: Problem,
    model: RetrievalModel,
    corpus: MetaphorCorpus,
    exploration_rate: float = 0.1
) -> list[tuple[Metaphor, float]]:
    """Retrieval with exploration bonus."""

    scores = []
    for metaphor in corpus:
        # Base score from model
        expected_reward = model.predict(problem, metaphor)

        # Exploration bonus: higher for less-tried metaphors
        uncertainty = model.get_uncertainty(problem, metaphor)
        exploration_bonus = exploration_rate * uncertainty

        score = expected_reward + exploration_bonus
        scores.append((metaphor, score))

    return sorted(scores, key=lambda x: x[1], reverse=True)
```

**Uncertainty estimation**:
- Simple: Inverse of usage count for (domain, metaphor) pair
- Advanced: Model confidence interval

---

## Backtrack-Aware Retrieval

When returning to RETRIEVE after a failed CHALLENGE or VERIFY, use the failure context.

```python
def retrieve_after_backtrack(
    problem: Problem,
    failed_metaphor: Metaphor,
    failure_reason: str,
    exclude: list[str]
) -> list[tuple[Metaphor, float]]:
    """Retrieval informed by previous failure."""

    # Add the failure context to influence retrieval
    context = f"""
    Previous attempt with '{failed_metaphor.name}' failed because: {failure_reason}
    Looking for metaphors that avoid this issue.
    """

    # Negative example embedding (avoid similar metaphors)
    if "too abstract" in failure_reason:
        # Look for more concrete metaphors
        return retrieve(problem, exclude=exclude, prefer_concrete=True)
    elif "missing concept" in failure_reason:
        # Look for metaphors with richer operation sets
        return retrieve(problem, exclude=exclude, prefer_rich_operations=True)
    else:
        # General retry with exclusion
        return retrieve(problem, exclude=exclude, context=context)
```

---

## Corpus Management

### Static Corpus

A curated set of well-defined metaphors. Good for getting started.

```python
STANDARD_CORPUS = [
    Metaphor(
        id="plumbing",
        name="Plumbing",
        domain="engineering",
        description="Systems of pipes, valves, and reservoirs that control flow",
        operations=(
            Operation(name="locate_constriction", ...),
            Operation(name="add_reservoir", ...),
            Operation(name="increase_pipe_diameter", ...),
            Operation(name="add_bypass", ...),
        ),
        examples=(...),
    ),
    Metaphor(
        id="ecosystem",
        name="Ecosystem",
        domain="biology",
        description="Network of organisms interacting with environment",
        operations=(
            Operation(name="increase_biodiversity", ...),
            Operation(name="remove_invasive_species", ...),
            Operation(name="strengthen_symbiosis", ...),
        ),
        examples=(...),
    ),
    # ... more metaphors
]
```

### Dynamic Corpus

Add metaphors from:
- Generative retrieval (after validation)
- User contributions
- E-gent evolution (blending successful metaphors)

```python
class MetaphorCorpus:
    """Manages the metaphor collection."""

    def __init__(self, static: list[Metaphor]):
        self.static = static
        self.dynamic: list[Metaphor] = []
        self.embeddings: dict[str, tuple[float, ...]] = {}

    def add(self, metaphor: Metaphor, source: str = "generated") -> None:
        """Add a new metaphor to the corpus."""
        if metaphor.id in self.all_ids:
            raise ValueError(f"Metaphor {metaphor.id} already exists")
        self.dynamic.append(metaphor)
        self.embed(metaphor)

    def __iter__(self):
        yield from self.static
        yield from self.dynamic
```

---

## Quality Checks for Generated Metaphors

Before adding a generated metaphor to the corpus:

```python
def validate_metaphor(metaphor: Metaphor) -> tuple[bool, list[str]]:
    """Check if a generated metaphor is usable."""
    issues = []

    # Must have operations
    if len(metaphor.operations) < 2:
        issues.append("Too few operations (need at least 2)")

    # Operations must have effects
    for op in metaphor.operations:
        if not op.effects:
            issues.append(f"Operation '{op.name}' has no effects")

    # Must have description
    if len(metaphor.description) < 20:
        issues.append("Description too short")

    # Should have examples (warning only)
    if not metaphor.examples:
        issues.append("No examples provided (recommended)")

    valid = not any("Too few" in i or "has no effects" in i for i in issues)
    return valid, issues
```

---

## Performance Considerations

### Embedding Cache

```python
class EmbeddingCache:
    """Cache embeddings to avoid recomputation."""

    def __init__(self, l_gent: LEmbedder):
        self.l_gent = l_gent
        self.cache: dict[str, tuple[float, ...]] = {}

    def get_or_compute(self, text: str) -> tuple[float, ...]:
        if text not in self.cache:
            self.cache[text] = self.l_gent.embed(text)
        return self.cache[text]
```

### Batch Retrieval

When processing multiple problems, batch embedding calls:

```python
def retrieve_batch(problems: list[Problem], limit: int = 5) -> dict[str, list[tuple[Metaphor, float]]]:
    """Retrieve for multiple problems efficiently."""
    # Batch embed all problems
    embeddings = l_gent.embed_batch([p.description for p in problems])

    # Associate embeddings
    for problem, embedding in zip(problems, embeddings):
        problem = problem._replace(embedding=embedding)

    # Now retrieve individually (corpus embeddings are cached)
    return {p.id: retrieve(p, limit) for p in problems}
```

---

## Metrics

Track these for learning and debugging:

| Metric | Description |
|--------|-------------|
| `retrieval_time_ms` | Time to retrieve candidates |
| `top_score` | Highest similarity score |
| `score_spread` | Difference between top and 5th candidate |
| `generation_triggered` | Was generative retrieval used? |
| `backtrack_count` | How many times we returned to RETRIEVE |

---

*Retrieval is the first guess. The search loop does the rest.*
