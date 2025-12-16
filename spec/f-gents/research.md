# Research Flow: Tree of Thought Exploration

> *"The answer is not at the end of a path. It is the shape of the tree you grew while searching."*

---

## Overview

Research Flow is the F-gent modality for deep exploration via **tree of thought** patterns.

**Key characteristics**:
- Hypothesis generation (branching)
- Parallel exploration of alternatives
- Evaluation and pruning of unpromising branches
- Synthesis of insights (merging)

Research Flow transforms a question into an exploration tree, yielding insights as the tree grows.

---

## The Research Polynomial

```python
RESEARCH_POLYNOMIAL = FlowPolynomial(
    positions=frozenset([
        FlowState.DORMANT,      # Waiting for question
        FlowState.STREAMING,    # Exploring current hypothesis
        FlowState.BRANCHING,    # Generating alternative hypotheses
        FlowState.CONVERGING,   # Synthesizing insights
        FlowState.COLLAPSED,    # Depth limit or question answered
    ]),
    directions=lambda state: {
        FlowState.DORMANT: frozenset(["start", "configure"]),
        FlowState.STREAMING: frozenset(["explore", "branch", "evaluate", "stop"]),
        FlowState.BRANCHING: frozenset(["expand", "prune", "stream"]),
        FlowState.CONVERGING: frozenset(["merge", "synthesize", "stream"]),
        FlowState.COLLAPSED: frozenset(["reset", "harvest"]),
    }[state],
    transition=research_transition,
)
```

---

## The Hypothesis Tree

Research Flow builds a tree of hypotheses:

```
                       [Question]
                           |
            +--------+-----+------+--------+
            |        |            |        |
        [Hyp A]  [Hyp B]      [Hyp C]  [Hyp D]
           |        |            |
        +--+--+   [leaf]     +--+--+
        |     |              |     |
    [A.1] [A.2]           [C.1] [C.2]
```

### Hypothesis Structure

```python
@dataclass
class Hypothesis:
    """A node in the exploration tree."""
    id: str
    content: str                    # The hypothesis text
    parent_id: str | None           # None for root
    depth: int                      # Distance from root
    confidence: float               # 0.0 to 1.0
    promise: float                  # Expected value of exploration
    status: HypothesisStatus        # exploring | expanded | pruned | merged
    evidence: list[Evidence]        # Supporting/contradicting evidence
    children: list[str]             # Child hypothesis IDs
    created_at: datetime
    explored_at: datetime | None

@dataclass
class Evidence:
    """Evidence for or against a hypothesis."""
    content: str
    supports: bool                  # True = supports, False = contradicts
    strength: float                 # 0.0 to 1.0
    source: str                     # Where this evidence came from
```

---

## Branching: Generating Alternatives

When uncertainty is high, Research Flow branches:

```python
async def branch(self, hypothesis: Hypothesis) -> list[Hypothesis]:
    """
    Generate alternative hypotheses from current.

    Triggers when:
    - confidence < branching_threshold
    - explicit branch request
    - contradiction detected
    """
    # Generate alternatives via LLM
    prompt = f"""
    Current hypothesis: {hypothesis.content}
    Evidence so far: {hypothesis.evidence}

    Generate {self.config.max_branches} alternative hypotheses that:
    1. Address the same question
    2. Take different approaches
    3. Could be true given the evidence
    """

    alternatives = await self.brancher.invoke(prompt)

    children = []
    for alt in alternatives:
        child = Hypothesis(
            id=generate_id(),
            content=alt.content,
            parent_id=hypothesis.id,
            depth=hypothesis.depth + 1,
            confidence=alt.initial_confidence,
            promise=self._estimate_promise(alt),
            status=HypothesisStatus.EXPLORING,
            evidence=[],
            children=[],
            created_at=datetime.now(),
            explored_at=None,
        )
        children.append(child)
        self.tree.add_node(child)

    hypothesis.children = [c.id for c in children]
    hypothesis.status = HypothesisStatus.EXPANDED

    return children
```

### Branching Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `uncertainty` | Branch when confidence < threshold | General exploration |
| `contradiction` | Branch when evidence conflicts | Resolving tensions |
| `depth_first` | Fully explore one branch before others | Focused investigation |
| `breadth_first` | Explore all branches at each level | Comprehensive survey |
| `best_first` | Explore highest-promise branches first | Efficient search |

---

## Pruning: Eliminating Dead Ends

Not all branches are worth exploring:

```python
async def prune(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    """
    Remove low-promise hypotheses from consideration.

    Criteria:
    - promise < pruning_threshold
    - contradicted by strong evidence
    - superseded by better hypothesis
    """
    survivors = []
    for hyp in hypotheses:
        if hyp.promise >= self.config.pruning_threshold:
            if not self._is_contradicted(hyp):
                survivors.append(hyp)
            else:
                hyp.status = HypothesisStatus.PRUNED
                self._emit_pruned(hyp, reason="contradiction")
        else:
            hyp.status = HypothesisStatus.PRUNED
            self._emit_pruned(hyp, reason="low_promise")

    return survivors
```

### Promise Estimation

```python
def _estimate_promise(self, hypothesis: Hypothesis) -> float:
    """
    Estimate expected value of exploring this hypothesis.

    Factors:
    - Prior probability (initial confidence)
    - Information gain (how much we'd learn)
    - Exploration cost (depth, complexity)
    - Parent success (did parent path yield insights?)
    """
    prior = hypothesis.confidence
    info_gain = self._estimate_info_gain(hypothesis)
    cost = self._exploration_cost(hypothesis)
    parent_success = self._parent_track_record(hypothesis)

    return (prior * info_gain * parent_success) / cost
```

---

## Merging: Synthesizing Insights

When branches converge or complement each other:

```python
async def merge(
    self,
    hypotheses: list[Hypothesis],
    strategy: MergeStrategy,
) -> Synthesis:
    """
    Combine insights from multiple hypotheses.

    Strategies:
    - best_first: Take highest-confidence hypothesis
    - weighted_vote: Confidence-weighted combination
    - synthesis: LLM generates unified understanding
    """
    match strategy:
        case MergeStrategy.BEST_FIRST:
            winner = max(hypotheses, key=lambda h: h.confidence)
            return Synthesis(
                content=winner.content,
                confidence=winner.confidence,
                sources=[winner.id],
                method="best_first",
            )

        case MergeStrategy.WEIGHTED_VOTE:
            # Weight by confidence
            total_conf = sum(h.confidence for h in hypotheses)
            weighted = {
                h.id: h.confidence / total_conf
                for h in hypotheses
            }
            return Synthesis(
                content=self._weighted_combine(hypotheses, weighted),
                confidence=total_conf / len(hypotheses),
                sources=[h.id for h in hypotheses],
                method="weighted_vote",
            )

        case MergeStrategy.SYNTHESIS:
            # LLM synthesizes
            prompt = f"""
            Synthesize these hypotheses into a unified understanding:
            {[h.content for h in hypotheses]}

            Consider:
            - What do they agree on?
            - Where do they diverge?
            - What's the most defensible combined position?
            """
            result = await self.synthesizer.invoke(prompt)
            return Synthesis(
                content=result.content,
                confidence=result.confidence,
                sources=[h.id for h in hypotheses],
                method="synthesis",
            )
```

---

## Exploration Strategies

### Depth-First Search

```python
async def explore_depth_first(self, root: Hypothesis) -> AsyncIterator[Insight]:
    """Explore one branch fully before moving to siblings."""
    stack = [root]

    while stack and not self._should_stop():
        current = stack.pop()

        async for insight in self._explore_hypothesis(current):
            yield insight

        if current.confidence < self.config.branching_threshold:
            children = await self.branch(current)
            # Add children in reverse order so first child is explored first
            stack.extend(reversed(children))
```

### Breadth-First Search

```python
async def explore_breadth_first(self, root: Hypothesis) -> AsyncIterator[Insight]:
    """Explore all hypotheses at each depth level."""
    queue = deque([root])

    while queue and not self._should_stop():
        current = queue.popleft()

        async for insight in self._explore_hypothesis(current):
            yield insight

        if current.confidence < self.config.branching_threshold:
            children = await self.branch(current)
            queue.extend(children)
```

### Best-First Search

```python
async def explore_best_first(self, root: Hypothesis) -> AsyncIterator[Insight]:
    """Always explore highest-promise hypothesis next."""
    heap = [(- root.promise, root)]  # Negative for max-heap behavior

    while heap and not self._should_stop():
        _, current = heapq.heappop(heap)

        async for insight in self._explore_hypothesis(current):
            yield insight

        if current.confidence < self.config.branching_threshold:
            children = await self.branch(current)
            for child in children:
                heapq.heappush(heap, (- child.promise, child))
```

---

## Configuration

```python
@dataclass
class ResearchConfig:
    """Research-specific configuration."""

    # Tree structure
    max_branches: int = 5           # Max children per node
    depth_limit: int = 4            # Max tree depth
    max_nodes: int = 100            # Total node limit

    # Branching
    branching_threshold: float = 0.3    # Branch if confidence < this
    branching_strategy: BranchStrategy = BranchStrategy.UNCERTAINTY

    # Pruning
    pruning_threshold: float = 0.2      # Prune if promise < this
    prune_after_depth: int = 1          # Start pruning after this depth

    # Merging
    merge_strategy: MergeStrategy = MergeStrategy.SYNTHESIS
    merge_threshold: int = 3            # Merge when N branches at same depth

    # Exploration
    exploration_strategy: ExploreStrategy = ExploreStrategy.BEST_FIRST
    exploration_budget: int = 50        # Max hypothesis explorations

    # Termination
    confidence_threshold: float = 0.9   # Stop if answer confidence > this
    insight_target: int | None = None   # Stop after N insights

    # Agents
    brancher: Agent[str, list[str]] | None = None
    evaluator: Agent[Hypothesis, float] | None = None
    synthesizer: Agent[list[Hypothesis], Synthesis] | None = None
```

---

## Output Types

### Insight

```python
@dataclass
class Insight:
    """A finding during exploration."""
    type: Literal["discovery", "evidence", "contradiction", "synthesis"]
    content: str
    confidence: float
    hypothesis_id: str          # Which hypothesis yielded this
    depth: int                  # At what depth
    timestamp: datetime
```

### ResearchResult

```python
@dataclass
class ResearchResult:
    """Final result of research exploration."""
    question: str
    answer: Synthesis | None    # Final synthesized answer
    confidence: float
    tree: HypothesisTree        # Full exploration tree
    insights: list[Insight]     # All insights discovered
    statistics: ResearchStats   # Exploration metrics
```

---

## Usage Examples

### Basic Research

```python
from agents.f import Flow, FlowConfig

config = FlowConfig(
    modality="research",
    max_branches=4,
    depth_limit=3,
)
research = Flow.lift(hypothesis_agent, config)

async for insight in research.start(["What causes consciousness?"]):
    print(f"[{insight.type}] {insight.content}")
```

### Research with Custom Strategies

```python
config = FlowConfig(
    modality="research",
    branching_strategy="contradiction",  # Branch on conflicts
    exploration_strategy="depth_first",  # Deep before wide
    merge_strategy="synthesis",          # LLM combines
    confidence_threshold=0.85,           # Stop when confident
)
```

### Research with Early Stopping

```python
async for insight in research.start([question]):
    if insight.type == "synthesis" and insight.confidence > 0.9:
        print(f"High-confidence answer: {insight.content}")
        break
```

---

## Metrics

| Metric | Description |
|--------|-------------|
| `hypotheses_generated` | Total hypotheses created |
| `hypotheses_pruned` | Hypotheses eliminated |
| `max_depth_reached` | Deepest exploration level |
| `branch_factor` | Average children per node |
| `insights_discovered` | Total insights yielded |
| `exploration_efficiency` | Insights per hypothesis explored |
| `final_confidence` | Confidence of synthesized answer |

---

## Anti-Patterns

### 1. Unbounded Branching

```python
# BAD: No limit on branches
config = FlowConfig(modality="research", max_branches=100)
# Exponential explosion!

# GOOD: Reasonable limits
config = FlowConfig(modality="research", max_branches=4, depth_limit=3)
```

### 2. No Pruning

```python
# BAD: Explore everything
config = FlowConfig(modality="research", pruning_threshold=0.0)
# Wastes computation on dead ends

# GOOD: Aggressive pruning
config = FlowConfig(modality="research", pruning_threshold=0.2)
```

### 3. Premature Convergence

```python
# BAD: Stop too early
config = FlowConfig(modality="research", confidence_threshold=0.5)
# May miss important insights

# GOOD: Require high confidence
config = FlowConfig(modality="research", confidence_threshold=0.9)
```

---

## See Also

- `README.md` - F-gent overview
- `collaboration.md` - Multi-agent blackboard pattern
- `spec/e-gents/evolution-agent.md` - Evolutionary exploration
- Papers: "Tree of Thoughts" (Yao et al., 2023)
