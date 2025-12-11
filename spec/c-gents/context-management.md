# Context Management

> *"Attention is a scarce resource. Spend it wisely."*

This document formalizes context window management through the **Cooled Functor** pattern and related entropy management techniques. These patterns enable "infinite context" through intelligent pruning.

## Derivation from Bootstrap

Context management does not require new primitives. It derives from existing patterns:

```
Context Management = Cooled Functor + Judge + Lethe
```

| Capability | Bootstrap Source |
|------------|-----------------|
| Compression | Cooled Functor (bootstrap idiom 3.2) |
| Salience scoring | Judge (what's worth keeping?) |
| Strategic forgetting | Lethe (D-gent Phase 4) |
| Premise validation | Judge + Contradict |

**No new primitives needed**—context management composes existing capabilities.

## Why Not Z-gent?

An earlier proposal suggested "Z-gent" (Zero/Entropy Manager) as a separate genus. Analysis revealed:

1. **Cooled Functor exists** - `spec/bootstrap.md` idiom 3.2 already handles context heat
2. **Lethe exists** - D-gent's forgetting infrastructure already handles strategic deletion
3. **Unask/Mu is Judge + Contradict** - Premise validation is already covered

**Decision**: Distribute Z-gent patterns to existing owners rather than create new genus.

## The Cooled Functor (Formalized)

From `bootstrap.md`:

> Context windows are finite. Context is heat. Cooling prevents degradation.

```python
@dataclass
class Cooled(Generic[I, O]):
    """
    A functor that manages context heat.

    Wraps any agent to prevent context overflow through
    automatic compression when thresholds are exceeded.
    """

    inner: Agent[I, O]
    threshold: int = 4096  # Token limit before cooling
    radiator: Agent[str, str] | None = None  # Compression agent

    async def invoke(self, input: I) -> O:
        """Invoke with automatic cooling."""
        # Estimate token count
        tokens = self._estimate_tokens(input)

        if tokens > self.threshold:
            if self.radiator:
                # Compress via radiator agent
                compressed = await self.radiator.invoke(str(input))
                input = self._reconstruct(compressed, input)
            else:
                # Default: truncate
                input = self._truncate(input, self.threshold)

        return await self.inner.invoke(input)

    def _estimate_tokens(self, input: I) -> int:
        """Estimate token count (rough: chars/4)."""
        return len(str(input)) // 4

    def _truncate(self, input: I, limit: int) -> I:
        """Truncate to token limit."""
        text = str(input)
        return text[:limit * 4]  # Rough approximation
```

**Key Insight**: The inner agent doesn't know it received compressed data. It sees only a clean, short prompt. This makes agents **stateless in performance**.

## Sliding Window

Implements StreamingLLM attention sink pattern for persistent sessions:

```python
@dataclass
class SlidingWindow:
    """
    Manages a sliding window over token sequences.

    Key insight from StreamingLLM:
    - First few tokens (attention sinks) must be preserved
    - Recent tokens must be preserved
    - Middle can be pruned based on salience
    """

    window_size: int = 4096
    sink_size: int = 4      # Keep first N tokens (structural anchors)
    recent_size: int = 1024  # Keep last N tokens (working memory)

    attention_sinks: list[str] = field(default_factory=list)
    recent: deque[str] = field(default_factory=lambda: deque(maxlen=1024))
    middle: list[str] = field(default_factory=list)

    salience_scorer: "SalienceScorer | None" = None

    def add(self, tokens: list[str]) -> list[str]:
        """
        Add tokens to window, returning pruned tokens.
        """
        pruned = []

        for token in tokens:
            # Fill attention sinks first
            if len(self.attention_sinks) < self.sink_size:
                self.attention_sinks.append(token)
                continue

            # Overflow from recent to middle
            if len(self.recent) >= self.recent_size:
                self.middle.append(self.recent.popleft())

            self.recent.append(token)

            # Prune middle if needed
            max_middle = self.window_size - self.sink_size - self.recent_size
            if len(self.middle) > max_middle:
                pruned.extend(self._prune())

        return pruned

    def _prune(self) -> list[str]:
        """Prune lowest-salience tokens from middle."""
        if not self.salience_scorer:
            # FIFO fallback
            return [self.middle.pop(0)]

        # Score and prune bottom 10%
        scored = [(t, self.salience_scorer.score(t)) for t in self.middle]
        scored.sort(key=lambda x: x[1])
        prune_count = max(1, len(scored) // 10)

        to_prune = [t for t, _ in scored[:prune_count]]
        self.middle = [t for t in self.middle if t not in to_prune]
        return to_prune

    def get_context(self) -> str:
        """Get current context as string."""
        return " ".join(self.attention_sinks + self.middle + list(self.recent))
```

## Salience Scoring

Uses Judge principles to determine what's worth keeping:

```python
@dataclass
class SalienceScorer:
    """
    Scores token/content salience using Judge-based criteria.

    High salience = keep
    Low salience = prune candidate
    """

    weights: dict[str, float] = field(default_factory=lambda: {
        "recency": 0.3,       # Newer = more salient
        "entity": 0.3,        # Named entities are salient
        "user_reference": 0.2, # User-mentioned content is salient
        "structural": 0.2     # Headers, markers are salient
    })

    known_entities: set[str] = field(default_factory=set)

    def score(self, content: str) -> float:
        """Compute salience score (0.0 to 1.0)."""
        scores = {
            "recency": 0.5,  # Default; caller adjusts based on position
            "entity": self._entity_score(content),
            "user_reference": self._user_reference_score(content),
            "structural": self._structural_score(content)
        }

        return sum(self.weights[k] * v for k, v in scores.items())

    def _entity_score(self, content: str) -> float:
        """Score based on named entity presence."""
        for entity in self.known_entities:
            if entity.lower() in content.lower():
                return 1.0
        return 0.0

    def _user_reference_score(self, content: str) -> float:
        """Score based on user reference patterns."""
        user_markers = ["you asked", "your", "user:", "human:"]
        for marker in user_markers:
            if marker in content.lower():
                return 1.0
        return 0.0

    def _structural_score(self, content: str) -> float:
        """Score based on structural importance."""
        if content.startswith("#") or content.startswith("```"):
            return 1.0
        if content.strip() in ["", "---", "***"]:
            return 0.0  # Low salience for separators
        return 0.3

    def register_entity(self, entity: str) -> None:
        """Register a named entity for tracking."""
        self.known_entities.add(entity)
```

## Lethe Integration

Strategic forgetting integrates with D-gent's Lethe:

```python
async def coordinated_forgetting_cycle(
    sliding_window: SlidingWindow,
    lethe: "Lethe",
    m_gent: "M",
    threshold: float = 0.8
) -> ForgettingResult:
    """
    Coordinated forgetting across subsystems.

    Triggers when context pressure exceeds threshold.
    """
    pressure = len(sliding_window.get_context()) / sliding_window.window_size
    actions = []

    if pressure > threshold:
        # 1. Prune sliding window
        pruned = sliding_window._prune()
        actions.append(("window_prune", len(pruned)))

        # 2. Trigger Lethe forgetting cycle
        await lethe.apply_retention_policy()
        actions.append(("lethe_cycle", True))

        # 3. Deactivate low-salience M-gent memories
        memories = await m_gent.list_active()
        for mem in memories:
            if sliding_window.salience_scorer.score(str(mem)) < 0.3:
                await m_gent.deactivate(mem.id)
                actions.append(("memory_deactivate", mem.id))

    return ForgettingResult(
        initial_pressure=pressure,
        final_pressure=len(sliding_window.get_context()) / sliding_window.window_size,
        actions=actions
    )
```

## The Mu Operator (Premise Validation)

Validates question premises using Judge + Contradict:

```python
async def check_premise(
    question: str,
    judge: "Judge",
    contradict: "Contradict"
) -> PremiseResult:
    """
    Check if a question's premise is valid.

    Returns Mu (void) for questions with invalid premises.

    Example:
    - "Why did the server crash?" → premise: "server crashed" → verify
    - "What is the capital of Atlantis?" → premise: "Atlantis exists" → invalid → Mu
    """
    # Extract premises
    premises = _extract_premises(question)

    for premise in premises:
        # Use Contradict to find conflicts
        conflict = await contradict.invoke((premise, "known facts"))

        if conflict:
            # Use Judge to determine if conflict is fatal
            verdict = await judge.invoke((premise, ["accuracy", "honesty"]))

            if verdict.verdict == "reject":
                return PremiseResult(
                    valid=False,
                    invalid_premise=premise,
                    reason=conflict.explanation,
                    suggestion="Please verify the premise of your question."
                )

    return PremiseResult(valid=True)


def _extract_premises(question: str) -> list[str]:
    """Extract implicit premises from question."""
    premises = []

    # "Why did X..." → premise: "X happened"
    if "why did" in question.lower():
        match = re.search(r"why did (.+?)(\?|$)", question.lower())
        if match:
            premises.append(match.group(1))

    # "How do I fix X..." → premise: "X is broken"
    if "how do i fix" in question.lower():
        match = re.search(r"how do i fix (.+?)(\?|$)", question.lower())
        if match:
            premises.append(f"there is a problem with {match.group(1)}")

    return premises
```

## Summary Constraint

Forces compression when context pressure is high:

```python
@dataclass
class SummaryConstraint:
    """
    Forces agents to communicate via compressed summaries
    when context pressure exceeds threshold.
    """

    pressure_threshold: float = 0.8  # Activate when > 80% full
    compression_ratio: float = 0.2   # Compress to 20% of original
    summarizer: Agent[str, str] | None = None

    async def maybe_compress(
        self,
        message: str,
        current_pressure: float
    ) -> str:
        """Compress message if pressure is high."""
        if current_pressure < self.pressure_threshold:
            return message

        target_length = int(len(message) * self.compression_ratio)

        if self.summarizer:
            return await self.summarizer.invoke(
                f"Summarize in {target_length} characters: {message}"
            )

        # Fallback: truncate
        return message[:target_length] + "..."
```

## Integration Pattern

Wrap any agent with context management:

```python
def with_context_management(
    agent: Agent[I, O],
    window_size: int = 4096,
    summarizer: Agent[str, str] | None = None
) -> Agent[I, O]:
    """
    Wrap an agent with automatic context management.

    Combines Cooled Functor + Salience Scoring.
    """
    cooled = Cooled(
        inner=agent,
        threshold=window_size,
        radiator=summarizer
    )

    return cooled
```

## Anti-Patterns

1. ❌ Creating "Z-gent" as entropy genus (Cooled Functor + Lethe exist)
2. ❌ Pruning without salience scoring (loses important context)
3. ❌ Removing attention sinks (structural anchors are sacred)
4. ❌ Compressing user input (only compress agent output)
5. ❌ Ignoring Lethe for permanent forgetting (use existing infrastructure)

## Principles Alignment

| Principle | How Context Management Satisfies |
|-----------|----------------------------------|
| **Tasteful** | Extends Cooled Functor, doesn't create new genus |
| **Composable** | Wraps any agent: `with_context_management(agent)` |
| **Generative** | Derivable from bootstrap patterns |
| **Heterarchical** | Context management is advisory, not controlling |

## See Also

- [../bootstrap.md](../bootstrap.md) - Cooled Functor (idiom 3.2)
- [../d-gents/lethe.md](../d-gents/lethe.md) - Strategic forgetting
- [../m-gents/](../m-gents/) - Long-term memory (distinct concern)
