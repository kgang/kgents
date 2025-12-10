# Ψ-gent Types

> Minimal, measurable, meaningful.

---

## Design Philosophy

Types in v3.0 are:
1. **Observable**: Every field can be measured or computed
2. **Useful**: No fields that exist "for completeness"
3. **Composable**: Types compose without special cases

---

## Core Types

### Problem

The input to the Morphic Engine.

```python
@dataclass(frozen=True)
class Problem:
    """A novel problem seeking metaphorical illumination."""

    id: str                           # Unique identifier
    description: str                  # Natural language description
    domain: str                       # Problem domain (e.g., "software", "organization")
    constraints: tuple[str, ...] = () # Things the solution must satisfy
    context: dict[str, Any] = field(default_factory=dict)  # Structured attributes
    embedding: tuple[float, ...] | None = None  # For retrieval (L-gent)

    @property
    def complexity(self) -> float:
        """Heuristic complexity estimate (0.0 to 1.0)."""
        # Simple heuristic: longer description + more constraints = more complex
        desc_factor = min(1.0, len(self.description) / 1000)
        constraint_factor = min(1.0, len(self.constraints) / 10)
        return (desc_factor + constraint_factor) / 2
```

**Rationale**:
- `constraints` are explicit so VERIFY can check they're addressed
- `context` allows structured data without rigid schema
- `embedding` enables semantic retrieval
- `complexity` is computed, not declared—avoids cargo cult MHC levels

---

### Metaphor

A familiar conceptual framework with operations.

```python
@dataclass(frozen=True)
class Metaphor:
    """A structured framework for reasoning about problems."""

    id: str                           # Unique identifier
    name: str                         # Human-readable name (e.g., "Plumbing")
    domain: str                       # Source domain
    description: str                  # What this metaphor is about
    operations: tuple[Operation, ...] # Things you can do in this space
    examples: tuple[Example, ...] = () # Concrete instances of the metaphor
    embedding: tuple[float, ...] | None = None  # For retrieval

    @property
    def tractability(self) -> float:
        """How powerful is this metaphor for reasoning?"""
        # More operations = more tractable (can do more things)
        return min(1.0, len(self.operations) / 5)
```

**Rationale**:
- `operations` are the whole point—a metaphor without operations is just renaming
- `examples` ground the abstract (LLM needs concrete instances to reason well)
- `tractability` is earned by having useful operations

---

### Operation

An action that can be performed within a metaphor.

```python
@dataclass(frozen=True)
class Operation:
    """An executable action within a metaphor framework."""

    name: str                         # Operation name (e.g., "locate_constriction")
    description: str                  # What this operation does
    signature: str = "entity → entity"  # Type signature for reasoning
    preconditions: tuple[str, ...] = ()  # When can this be applied?
    effects: tuple[str, ...] = ()     # What changes after application?
```

**Rationale**:
- `preconditions` and `effects` make operations *reasoned about*, not just named
- `signature` helps LLM understand composition

**Example**:
```python
Operation(
    name="locate_constriction",
    description="Find where flow is restricted",
    signature="system → location",
    preconditions=("flow is below expected",),
    effects=("constriction location is known",)
)
```

---

### Example

A concrete instance of a metaphor in action.

```python
@dataclass(frozen=True)
class Example:
    """A concrete instance showing the metaphor in use."""

    situation: str                    # The setup
    application: str                  # How the metaphor was applied
    outcome: str                      # What happened
```

**Rationale**:
- LLMs reason better with examples
- Examples ground abstract operations in concrete scenarios

---

### ConceptMapping

A single correspondence between problem and metaphor.

```python
@dataclass(frozen=True)
class ConceptMapping:
    """A mapping between a problem concept and a metaphor concept."""

    source: str                       # Problem-space concept
    target: str                       # Metaphor-space concept
    confidence: float                 # How good is this mapping? (0.0 to 1.0)
    rationale: str = ""               # Why this mapping?
```

**Rationale**:
- `confidence` allows uncertain mappings
- `rationale` is for debugging/forensics

---

### Projection

The result of mapping a problem into metaphor space.

```python
@dataclass(frozen=True)
class Projection:
    """A problem mapped into metaphor terms."""

    problem: Problem
    metaphor: Metaphor
    mappings: tuple[ConceptMapping, ...]
    abstraction: float                # 0.0 (concrete) to 1.0 (abstract)
    gaps: tuple[str, ...] = ()        # Problem concepts that didn't map
    confidence: float = 0.5           # Overall projection confidence

    @property
    def coverage(self) -> float:
        """What fraction of the problem was mapped?"""
        if not self.mappings:
            return 0.0
        total_concepts = len(self.mappings) + len(self.gaps)
        return len(self.mappings) / total_concepts if total_concepts > 0 else 0.0

    @property
    def mapped_description(self) -> str:
        """The problem restated in metaphor terms."""
        # In implementation, this would be generated by LLM
        # Here we just show the structure
        mapping_str = ", ".join(f"{m.source}→{m.target}" for m in self.mappings)
        return f"[{self.metaphor.name}] {mapping_str}"
```

**Rationale**:
- `abstraction` is the continuous replacement for MHC levels
- `gaps` explicitly track what didn't map (for distortion calculation)
- `coverage` is computed from structure

---

### ChallengeResult

The outcome of adversarial testing.

```python
@dataclass(frozen=True)
class ChallengeResult:
    """Result of stress-testing a projection."""

    survives: bool                    # Did the metaphor hold up?
    challenges_passed: int            # How many tests passed
    challenges_total: int             # How many tests run
    counterexamples: tuple[str, ...] = ()  # What broke it?
    caveats: tuple[str, ...] = ()     # Concerns that didn't break it

    @property
    def robustness(self) -> float:
        """How robust is this projection?"""
        if self.challenges_total == 0:
            return 0.5  # No testing = uncertain
        return self.challenges_passed / self.challenges_total
```

**Rationale**:
- `caveats` capture "it survived but watch out for X"
- `robustness` is a continuous measure of confidence

---

### MetaphorSolution

Reasoning performed within the metaphor space.

```python
@dataclass(frozen=True)
class MetaphorSolution:
    """Solution derived within metaphor space."""

    projection: Projection
    reasoning: str                    # Chain of thought
    operations_applied: tuple[str, ...]  # Which operations were used
    conclusion: str                   # The answer in metaphor terms
```

**Rationale**:
- `reasoning` is the explicit chain of thought (for forensics)
- `operations_applied` tracks what the metaphor actually contributed

---

### Solution

The final output, translated back to problem space.

```python
@dataclass(frozen=True)
class Solution:
    """Complete solution with translation and quality metrics."""

    problem: Problem
    metaphor_solution: MetaphorSolution
    translated_answer: str            # The answer in problem terms
    specific_actions: tuple[str, ...] # Concrete next steps
    distortion: Distortion            # Quality measurement
    trace_id: str | None = None       # For forensics (N-gent)

    @property
    def success(self) -> bool:
        """Is this solution good enough?"""
        return self.distortion.acceptable
```

---

### Distortion

Quality metrics for the transformation.

```python
@dataclass(frozen=True)
class Distortion:
    """Measures information loss through transformation."""

    structural_loss: float            # Unmapped concepts / total (0.0 to 1.0)
    round_trip_error: float           # How different is Φ⁻¹(Φ(P)) from P? (0.0 to 1.0)
    prediction_failures: int          # Implications that didn't hold

    # Weights for combining (can be tuned)
    STRUCTURAL_WEIGHT: ClassVar[float] = 0.3
    ROUND_TRIP_WEIGHT: ClassVar[float] = 0.4
    PREDICTION_WEIGHT: ClassVar[float] = 0.3
    PREDICTION_PENALTY: ClassVar[float] = 0.1  # Per failure

    @property
    def total(self) -> float:
        """Weighted distortion score (0.0 to 1.0+)."""
        prediction_score = min(1.0, self.prediction_failures * self.PREDICTION_PENALTY)
        return (
            self.structural_loss * self.STRUCTURAL_WEIGHT +
            self.round_trip_error * self.ROUND_TRIP_WEIGHT +
            prediction_score * self.PREDICTION_WEIGHT
        )

    @property
    def acceptable(self) -> bool:
        """Is distortion low enough to trust the solution?"""
        return self.total < 0.5
```

**Rationale**:
- Three orthogonal measures, each meaningful
- `total` combines them with explicit weights
- Threshold of 0.5 is tunable but provides default

---

## Search State Types

### SearchState

Tracks the engine's progress through the search.

```python
@dataclass
class SearchState:
    """Mutable state for the search loop."""

    problem: Problem
    candidates_tried: list[Metaphor] = field(default_factory=list)
    projections_attempted: list[Projection] = field(default_factory=list)
    best_solution: Solution | None = None
    best_distortion: float = float('inf')
    backtrack_reasons: list[str] = field(default_factory=list)
    iteration: int = 0

    def record_attempt(self, metaphor: Metaphor, projection: Projection | None,
                       result: str) -> None:
        """Record an attempt for learning."""
        self.candidates_tried.append(metaphor)
        if projection:
            self.projections_attempted.append(projection)
        self.iteration += 1
```

---

### EngineConfig

Configuration for the MetaphorEngine.

```python
@dataclass(frozen=True)
class EngineConfig:
    """Configuration for the Morphic Engine."""

    max_candidates: int = 5           # How many metaphors to try
    max_iterations: int = 10          # Total attempts before giving up
    min_abstraction: float = 0.0      # Lowest abstraction to try
    max_abstraction: float = 1.0      # Highest abstraction to try
    abstraction_step: float = 0.2     # How much to adjust on retry
    distortion_threshold: float = 0.5 # Below this = acceptable
    enable_learning: bool = True      # Update retrieval model?
    enable_tracing: bool = True       # Log to N-gent?
```

---

## Learning Types

### Feedback

Signal for the learning system.

```python
@dataclass(frozen=True)
class Feedback:
    """Feedback for the learning system."""

    problem_id: str
    metaphor_id: str
    abstraction: float
    outcome: Outcome
    distortion: float | None = None

class Outcome(Enum):
    """Possible outcomes for learning."""
    SUCCESS = "success"              # VERIFY passed
    PARTIAL = "partial"              # VERIFY close but not passing
    CHALLENGE_FAILED = "challenge_failed"  # Metaphor broke under stress
    PROJECTION_FAILED = "projection_failed"  # Couldn't map problem
    NO_SOLUTION = "no_solution"      # SOLVE produced nothing useful
```

---

### RetrievalModel

Interface for learned retrieval.

```python
@dataclass
class RetrievalModel:
    """Model for predicting metaphor success."""

    # (problem_features, metaphor_id) → expected_reward
    # Implementation could be:
    # - Simple: frequency counting
    # - Medium: linear model on features
    # - Advanced: neural contextual bandit

    def predict(self, problem: Problem, metaphor: Metaphor) -> float:
        """Predict success probability for this pairing."""
        ...

    def update(self, feedback: Feedback) -> None:
        """Update model with new feedback."""
        ...
```

---

## Comparison with v2.0 Types

| v2.0 Type | v3.0 Type | Changes |
|-----------|-----------|---------|
| `Novel` | `Problem` | Renamed, added `constraints`, removed `entropy` |
| `Metaphor` | `Metaphor` | Added `examples`, simplified |
| `MetaphorOperation` | `Operation` | Added `preconditions`, `effects` |
| `Projection` | `Projection` | Added `abstraction` (continuous), `gaps` |
| `MHCLevel` | `abstraction: float` | 15 discrete → continuous |
| `ValidationResult` | `ChallengeResult` | Focused on adversarial testing |
| `MetaphorValueTensor` | Removed | 5 dimensions → 3 measurable |
| `MetaphorDNA` | Removed | Learning replaces genetics |
| `MetaphorUmwelt` | Removed | Filter in RETRIEVE |
| `TensorPosition` | Removed | Single `distortion` metric |
| `Shadow` | Removed | Counterexamples are plain strings |

---

## Type Invariants

These should hold for all valid instances:

```python
# Distortion is bounded
assert 0.0 <= distortion.structural_loss <= 1.0
assert 0.0 <= distortion.round_trip_error <= 1.0
assert distortion.prediction_failures >= 0

# Abstraction is bounded
assert 0.0 <= projection.abstraction <= 1.0

# Coverage is bounded
assert 0.0 <= projection.coverage <= 1.0

# Confidence is bounded
assert 0.0 <= concept_mapping.confidence <= 1.0

# Non-empty metaphors have operations
assert len(metaphor.operations) > 0 or metaphor.id == "null_metaphor"

# Solutions reference their sources
assert solution.metaphor_solution.projection.problem == solution.problem
```

---

## Serialization

All types should be JSON-serializable for:
- N-gent tracing
- D-gent persistence
- Wire protocol transmission

```python
def to_dict(obj: Any) -> dict:
    """Convert dataclass to dict recursively."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj
```

---

*Types are the skeleton. Behavior is the muscle.*
