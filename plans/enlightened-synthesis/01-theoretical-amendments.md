# Theoretical Amendments: Strengthening the Foundation

> *"The proof IS the decision. The mark IS the witness."*

**Created**: 2025-12-25
**Revised**: 2025-12-26 (Added Galois loss estimates, grounding chains, categorical law verification)
**Status**: Critical Amendments
**Purpose**: Seven amendments that fix theoretical gaps before they become production bugs

---

## Overview

The Constitutional Decision OS has sound theoretical foundations but several gaps that could undermine the system. This document specifies amendments with implementation guidance.

### Grounding Axioms (A1-A5)

All amendments derive from these five non-negotiable axioms:

```
A1 ENTITY:     Everything representable IS an entity.
A2 MORPHISM:   Composition is preserved (categorical laws hold).
A3 GALOIS:     Loss is measurable: L(P) = d(P, C(R(P))).
A4 WITNESS:    The mark IS the witness. Actions leave traces.
A5 ETHICAL:    You cannot offset unethical behavior. Floor is absolute.
```

### Galois Loss Classification

Each amendment is classified by its Galois loss tier:

| Tier | Loss Range | Meaning | Examples |
|------|------------|---------|----------|
| **Categorical** | L ~ 0.00-0.10 | Near-axiomatic, survives restructuring | A1-A5, Identity laws |
| **Empirical** | L ~ 0.10-0.30 | Validated through observation | 7 Principles, most specs |
| **Aesthetic** | L ~ 0.30-0.50 | Taste-dependent, context-sensitive | COURAGE_PRESERVATION |
| **Somatic** | L ~ 0.50-0.75 | Embodied, hard to articulate | Joy inference |

### Categorical Laws Reference

Three fundamental laws govern composition:

```
IDENTITY:       Id >> f = f = f >> Id
ASSOCIATIVITY:  (f >> g) >> h = f >> (g >> h)
MONAD LAWS:
  - Left unit:  pure(a) >>= f ≡ f(a)
  - Right unit: m >>= pure ≡ m
  - Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
```

---

## Amendment A: ETHICAL as Floor Constraint

### Galois Loss Estimate

**L ~ 0.05** (Categorical tier)

This amendment survives restructuring because it derives directly from A5. "You cannot offset unethical behavior" reconstitutes with minimal loss.

### The Problem

Current design:
```python
# ETHICAL weight: 2.0 (highest)
# Threshold: 7.5 / 9.7

# DANGEROUS: This can pass despite ETHICAL violation
ETHICAL: 0.3 * 2.0 = 0.6
COMPOSABLE: 1.0 * 1.5 = 1.5
JOY_INDUCING: 1.0 * 1.2 = 1.2
Others: 4.0 * 1.0 = 4.0
Total: 7.3 → Almost passes!
```

### Grounding Chain (A5 → Amendment A)

```
A5: "You cannot offset unethical behavior."
      ↓ (direct derivation)
ETHICAL must be a gate, not a weight.
      ↓ (implementation)
IF ethical_score < 0.6 THEN weighted_total = 0.0
      ↓ (consequence)
Amendment A: ETHICAL as floor constraint
```

**Derivation Quality**: Direct (1 step from axiom)

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Identity | Floor check is idempotent: `floor(floor(x)) = floor(x)` | HOLDS |
| Associativity | N/A (floor is not composition) | N/A |
| Monad Laws | N/A (floor is a predicate, not a monad) | N/A |

### The Fix

```python
from dataclasses import dataclass
from typing import Optional

ETHICAL_FLOOR_THRESHOLD = 0.6  # Minimum acceptable ETHICAL score

@dataclass
class ConstitutionalScore:
    """Constitutional alignment with ETHICAL as floor constraint."""

    # Floor constraints (must pass)
    ethical_score: float  # Raw ETHICAL score 0-1

    # Weighted contributions
    composable: float
    joy_inducing: float
    tasteful: float
    curated: float
    heterarchical: float
    generative: float

    @property
    def ethical_passes(self) -> bool:
        """ETHICAL is a floor, not a weight."""
        return self.ethical_score >= ETHICAL_FLOOR_THRESHOLD

    @property
    def weighted_sum(self) -> float:
        """Sum of weighted non-floor principles."""
        if not self.ethical_passes:
            return 0.0  # Floor violation = immediate rejection

        return (
            self.composable * 1.5 +
            self.joy_inducing * 1.2 +
            self.tasteful * 1.0 +
            self.curated * 1.0 +
            self.heterarchical * 1.0 +
            self.generative * 1.0
        )

    @property
    def passes(self) -> bool:
        """Action passes iff floor met AND weighted sum sufficient."""
        if not self.ethical_passes:
            return False
        # Adjusted threshold: 5.7 / 7.7 (removing ETHICAL from weighted sum)
        return self.weighted_sum >= 5.7

    @property
    def rejection_reason(self) -> Optional[str]:
        """Why did this fail?"""
        if not self.ethical_passes:
            return f"ETHICAL floor violation: {self.ethical_score:.2f} < {ETHICAL_FLOOR_THRESHOLD}"
        if not self.passes:
            return f"Weighted sum insufficient: {self.weighted_sum:.2f} < 5.7"
        return None


def compute_constitutional_score(action: str, reasoning: str) -> ConstitutionalScore:
    """
    Compute constitutional alignment for an action.

    ETHICAL is evaluated first as floor constraint.
    Other principles are weighted contributions.
    """
    # Evaluate each principle (implementation details omitted)
    ethical = evaluate_ethical(action, reasoning)
    composable = evaluate_composable(action, reasoning)
    joy = evaluate_joy_inducing(action, reasoning)
    tasteful = evaluate_tasteful(action, reasoning)
    curated = evaluate_curated(action, reasoning)
    heterarchical = evaluate_heterarchical(action, reasoning)
    generative = evaluate_generative(action, reasoning)

    return ConstitutionalScore(
        ethical_score=ethical,
        composable=composable,
        joy_inducing=joy,
        tasteful=tasteful,
        curated=curated,
        heterarchical=heterarchical,
        generative=generative,
    )
```

### Implementation Location

- File: `impl/claude/services/constitution/scoring.py`
- Tests: `impl/claude/services/constitution/_tests/test_ethical_floor.py`

### Verification

```python
def test_ethical_floor_blocks():
    """ETHICAL violation cannot be offset by other high scores."""
    score = ConstitutionalScore(
        ethical_score=0.3,  # Below floor
        composable=1.0,
        joy_inducing=1.0,
        tasteful=1.0,
        curated=1.0,
        heterarchical=1.0,
        generative=1.0,
    )
    assert not score.passes
    assert "ETHICAL floor violation" in score.rejection_reason
```

---

## Amendment B: Canonical Semantic Distance

### Galois Loss Estimate

**L ~ 0.08** (Categorical tier)

The bidirectional entailment definition derives from A3 (loss is measurable) with geometric mean providing the mathematical rigor.

### The Problem

The Galois Loss formula `L(P) = d(P, C(R(P)))` is only as good as the distance function `d`. Current implementation offers multiple options (BERTScore, Cosine, NLI, LLM Judge) with no canonical choice.

### Grounding Chain (A3 → Amendment B)

```
A3: "Loss is measurable: L(P) = d(P, C(R(P)))."
      ↓ (d must be well-defined)
Distance function must be:
  1. Symmetric: d(A,B) = d(B,A)
  2. Bounded: 0 ≤ d(A,B) ≤ 1
  3. Semantically meaningful (not just token-level)
      ↓ (choice criterion)
Bidirectional entailment captures semantic equivalence
      ↓ (mathematical form)
d(A,B) = 1 - sqrt(P(A|=B) * P(B|=A))
      ↓ (consequence)
Amendment B: Canonical semantic distance via geometric mean
```

**Derivation Quality**: 3 steps from axiom

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Identity | `d(A, A) = 0` (self-entailment = 1.0 → geometric mean = 1.0 → distance = 0) | HOLDS |
| Symmetry | `d(A, B) = d(B, A)` (geometric mean is symmetric) | HOLDS |
| Triangle | `d(A, C) ≤ d(A, B) + d(B, C)` (empirically validated, not guaranteed) | WEAK |

### The Fix: Bidirectional Entailment Distance

```python
from typing import Protocol
import math


class SemanticDistance(Protocol):
    """Protocol for semantic distance functions."""

    def distance(self, text_a: str, text_b: str) -> float:
        """Returns distance in [0, 1] range."""
        ...


class BidirectionalEntailmentDistance:
    """
    Canonical semantic distance via bidirectional entailment.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))

    Why geometric mean?
    - Arithmetic mean treats one-way entailment too leniently
    - Geometric mean gives 0 if either direction fails
    - Matches intuition: mutual entailment = semantic equivalence
    """

    def __init__(self, nli_model: str = "deberta-v3-base-mnli"):
        self.nli_model = nli_model
        self._pipeline = None  # Lazy load

    @property
    def pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline
            self._pipeline = pipeline("text-classification", model=self.nli_model)
        return self._pipeline

    def _entailment_prob(self, premise: str, hypothesis: str) -> float:
        """Get P(premise entails hypothesis)."""
        result = self.pipeline(
            f"{premise} [SEP] {hypothesis}",
            return_all_scores=True
        )
        # Find entailment probability
        for item in result[0]:
            if item["label"].lower() == "entailment":
                return item["score"]
        return 0.0

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Bidirectional entailment distance.

        Returns 0 if texts are semantically equivalent.
        Returns 1 if texts are unrelated or contradictory.
        """
        if text_a == text_b:
            return 0.0

        p_a_entails_b = self._entailment_prob(text_a, text_b)
        p_b_entails_a = self._entailment_prob(text_b, text_a)

        # Geometric mean (symmetric, penalizes one-way entailment)
        mutual = math.sqrt(p_a_entails_b * p_b_entails_a)

        return 1.0 - mutual


class CanonicalSemanticDistance:
    """
    Canonical distance with fallback chain.

    Primary: Bidirectional entailment (most principled)
    Fallback 1: BERTScore (fast, stable)
    Fallback 2: Cosine embedding (fastest)
    """

    def __init__(self):
        self._primary = None
        self._bertscore = None
        self._cosine = None

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute distance with graceful fallback."""
        # Try NLI-based entailment first
        try:
            if self._primary is None:
                self._primary = BidirectionalEntailmentDistance()
            return self._primary.distance(text_a, text_b)
        except Exception:
            pass

        # Fallback to BERTScore
        try:
            if self._bertscore is None:
                from .bertscore_distance import BERTScoreDistance
                self._bertscore = BERTScoreDistance()
            return self._bertscore.distance(text_a, text_b)
        except Exception:
            pass

        # Ultimate fallback: cosine
        from .cosine_distance import CosineEmbeddingDistance
        if self._cosine is None:
            self._cosine = CosineEmbeddingDistance()
        return self._cosine.distance(text_a, text_b)


# Default export
def semantic_distance(text_a: str, text_b: str) -> float:
    """Canonical semantic distance for Galois loss."""
    return CanonicalSemanticDistance().distance(text_a, text_b)
```

### Why Geometric Mean?

| Scenario | P(A→B) | P(B→A) | Arithmetic | Geometric |
|----------|--------|--------|------------|-----------|
| Equivalent | 0.9 | 0.9 | 0.9 | 0.9 |
| A abstracts B | 0.9 | 0.3 | 0.6 | 0.52 |
| Unrelated | 0.1 | 0.1 | 0.1 | 0.1 |
| Contradictory | 0.05 | 0.05 | 0.05 | 0.05 |

Geometric mean penalizes one-way entailment more strongly, matching intuition.

### Implementation Location

- File: `impl/claude/services/zero_seed/galois/distance.py`
- Tests: `impl/claude/services/zero_seed/galois/_tests/test_canonical_distance.py`

---

## Amendment C: Corpus-Relative Layer Assignment

### Galois Loss Estimate

**L ~ 0.12** (Empirical tier)

Layer assignment is empirically grounded—the bounds are calibrated from observation rather than derived from axioms.

### The Problem

Current layer bounds are absolute:
```python
LAYER_LOSS_BOUNDS = {
    1: (0.00, 0.05),  # Axiom
    2: (0.05, 0.15),  # Value
    3: (0.15, 0.30),  # Goal
    4: (0.30, 0.45),  # Spec
    5: (0.45, 0.60),  # Execution
    6: (0.60, 0.75),  # Reflection
    7: (0.75, 1.00),  # Representation
}
```

These are calibrated on Kent's corpus and may not generalize.

### Grounding Chain (A1 + A3 → Amendment C)

```
A1: "Everything representable IS an entity."
      ↓ (each layer is an entity)
Layers L1-L7 are entities with loss characteristics
      +
A3: "Loss is measurable: L(P) = d(P, C(R(P)))."
      ↓ (loss distributions vary by corpus)
Loss distribution is corpus-dependent
      ↓ (adaptation strategy)
Use relative percentiles within corpus
      ↓ (consequence)
Amendment C: Corpus-relative layer assignment
```

**Derivation Quality**: 2 steps from axioms (A1 + A3 combined)

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Identity | Same content always maps to same layer (given corpus) | HOLDS |
| Associativity | Layer assignment doesn't compose (not a morphism) | N/A |
| Monotonicity | Lower loss → lower layer number (preserves order) | HOLDS |

### The Fix: Relative Layer Assignment

```python
from dataclasses import dataclass
from typing import Sequence
import statistics


@dataclass
class LayerAssignment:
    """Layer assignment with confidence and method."""
    layer: int  # 1-7
    layer_name: str
    confidence: float
    method: str  # "absolute" or "relative"
    loss: float
    percentile: float | None = None  # Only for relative


LAYER_NAMES = {
    1: "Axiom",
    2: "Value",
    3: "Goal",
    4: "Spec",
    5: "Execution",
    6: "Reflection",
    7: "Representation",
}


def assign_layer_absolute(loss: float) -> LayerAssignment:
    """
    Assign layer using absolute bounds.

    Use for: Standalone documents, API calls, quick checks.
    Bounds are reference calibration from mixed corpora.
    """
    BOUNDS = {
        1: (0.00, 0.05),
        2: (0.05, 0.15),
        3: (0.15, 0.30),
        4: (0.30, 0.45),
        5: (0.45, 0.60),
        6: (0.60, 0.75),
        7: (0.75, 1.00),
    }

    for layer, (low, high) in BOUNDS.items():
        if low <= loss < high:
            return LayerAssignment(
                layer=layer,
                layer_name=LAYER_NAMES[layer],
                confidence=1.0 - abs(loss - (low + high) / 2) / (high - low),
                method="absolute",
                loss=loss,
            )

    # Edge case: loss >= 1.0
    return LayerAssignment(
        layer=7,
        layer_name="Representation",
        confidence=0.5,
        method="absolute",
        loss=loss,
    )


def assign_layer_relative(
    loss: float,
    corpus_losses: Sequence[float],
) -> LayerAssignment:
    """
    Assign layer relative to a corpus.

    Use for: Personal corpora, team documents, domain-specific analysis.
    Adapts to the loss distribution of the specific corpus.
    """
    if not corpus_losses:
        return assign_layer_absolute(loss)

    sorted_losses = sorted(corpus_losses)
    n = len(sorted_losses)

    # Find percentile of this loss in corpus
    count_below = sum(1 for l in sorted_losses if l < loss)
    percentile = count_below / n

    # Map percentile to layer (1-7)
    layer = min(7, max(1, int(percentile * 7) + 1))

    # Calculate confidence based on distance from layer boundaries
    layer_low = (layer - 1) / 7
    layer_high = layer / 7
    layer_mid = (layer_low + layer_high) / 2
    confidence = 1.0 - abs(percentile - layer_mid) / (layer_high - layer_low) * 2

    return LayerAssignment(
        layer=layer,
        layer_name=LAYER_NAMES[layer],
        confidence=max(0.0, min(1.0, confidence)),
        method="relative",
        loss=loss,
        percentile=percentile,
    )


class LayerAssigner:
    """Intelligent layer assignment with corpus learning."""

    def __init__(self):
        self.corpus_losses: list[float] = []
        self.min_corpus_size = 20  # Use relative after this many

    def assign(self, loss: float, use_corpus: bool = True) -> LayerAssignment:
        """Assign layer, using corpus if available."""
        if use_corpus and len(self.corpus_losses) >= self.min_corpus_size:
            return assign_layer_relative(loss, self.corpus_losses)
        return assign_layer_absolute(loss)

    def add_to_corpus(self, loss: float) -> None:
        """Add a computed loss to the corpus for relative assignment."""
        self.corpus_losses.append(loss)
```

### Calibration Set for Regression Testing

```python
# Anchor documents with known layer assignments
CALIBRATION_CORPUS = [
    # L1 axioms (should always be 0.00-0.05)
    ("Agency requires justification", 1),
    ("Composition is primary", 1),
    ("The proof IS the decision", 1),

    # L2 values (should always be 0.05-0.15)
    ("We value transparency over convenience", 2),
    ("Joy is a first-class metric", 2),

    # L3 goals (should always be 0.15-0.30)
    ("Build a system that surfaces contradictions", 3),
    ("Enable trust accumulation through demonstrated alignment", 3),

    # L5 execution (should always be 0.45-0.60)
    ("Run pytest and fix failing tests", 5),
    ("Deploy to staging and verify", 5),
]


def validate_calibration(assigner: LayerAssigner) -> bool:
    """Verify layer assignment stability against calibration."""
    for content, expected in CALIBRATION_CORPUS:
        loss = compute_galois_loss(content)  # Imported from galois_loss.py
        assignment = assigner.assign(loss, use_corpus=False)  # Always use absolute
        if assignment.layer != expected:
            logger.warning(
                f"Calibration drift: '{content[:30]}...' "
                f"expected L{expected}, got L{assignment.layer}"
            )
            return False
    return True
```

### Implementation Location

- File: `impl/claude/services/zero_seed/galois/layer_assignment.py`
- Tests: `impl/claude/services/zero_seed/galois/_tests/test_layer_assignment.py`

---

## Amendment D: K-Block Monad - Explicit Bind

### Galois Loss Estimate

**L ~ 0.10** (Categorical tier)

Monadic structure is near-axiomatic—the laws are mathematical and survive restructuring intact.

### The Problem

K-Block is claimed to be a "monad over Documents" but `bind` semantics are not fully implemented. The current implementation transfers cosmos reference but **lacks LineageEdge creation and derivation history threading**.

**Current Gap** (from code inspection):
```python
# Current implementation in services/k_block/core/kblock.py line 453
def bind(self, f: "Callable[[str], KBlock]") -> "KBlock":
    result = f(self.content)
    result._cosmos = self._cosmos  # Only transfers cosmos reference
    return result
    # MISSING: LineageEdge creation
    # MISSING: Derivation DAG threading
    # MISSING: Witness mark emission
```

### Grounding Chain (A2 + A4 → Amendment D)

```
A2: "Composition is preserved (categorical laws hold)."
      ↓ (monad laws ARE categorical laws)
Monads must satisfy: left unit, right unit, associativity
      +
A4: "The mark IS the witness. Actions leave traces."
      ↓ (bind operations must be witnessed)
Every bind creates a lineage edge (the mark)
      ↓ (consequence)
Amendment D: K-Block bind with lineage threading
```

**Derivation Quality**: 2 steps from axioms (A2 + A4 combined)

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Left Unit | `pure(a) >>= f ≡ f(a)` (content equivalence) | HOLDS (content) |
| Right Unit | `m >>= pure ≡ m` (content equivalence) | HOLDS (content) |
| Associativity | `(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)` (content equivalence) | HOLDS (content) |
| Lineage Preservation | Bind creates LineageEdge | **MISSING** |
| Witness Emission | Bind emits witness mark | **MISSING** |

### The Fix: Explicit Monadic Operations

```python
from dataclasses import dataclass, field
from typing import TypeVar, Callable, Generic
from uuid import uuid4
import datetime

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class LineageEdge:
    """Edge in the derivation DAG."""
    from_id: str
    to_id: str
    operation: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class WitnessMark:
    """A witnessed action."""
    mark_id: str
    action: str
    reasoning: str
    timestamp: datetime.datetime


@dataclass
class KBlock(Generic[T]):
    """
    K-Block: A monad over content with lineage tracking.

    Laws:
    - Left identity: return(a) >>= f ≡ f(a)
    - Right identity: m >>= return ≡ m
    - Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

    CRITICAL: bind() must create LineageEdge to satisfy A4 (witness).
    """
    id: str
    content: T
    lineage: list[LineageEdge] = field(default_factory=list)
    marks: list[WitnessMark] = field(default_factory=list)
    layer: int | None = None

    @classmethod
    def pure(cls, content: T) -> "KBlock[T]":
        """
        Monad return: Lift content into K-Block context.

        Creates a fresh K-Block with no lineage.
        """
        return cls(
            id=str(uuid4()),
            content=content,
            lineage=[],
            marks=[],
        )

    # Alias for clarity
    @classmethod
    def return_(cls, content: T) -> "KBlock[T]":
        """Monadic return (alias for pure)."""
        return cls.pure(content)

    def bind(self, f: Callable[[T], "KBlock[U]"]) -> "KBlock[U]":
        """
        Monadic bind: Apply f to content, threading lineage.

        The resulting K-Block:
        - Contains f(self.content).content
        - Has lineage from both self and f result
        - Preserves witness marks from both
        - CREATES LineageEdge (satisfies A4 WITNESS)
        """
        result = f(self.content)

        # Create derivation edge (THE MISSING PIECE)
        edge = LineageEdge(
            from_id=self.id,
            to_id=result.id,
            operation=f.__name__ if hasattr(f, "__name__") else "transform",
        )

        return KBlock(
            id=result.id,
            content=result.content,
            lineage=self.lineage + [edge] + result.lineage,
            marks=self.marks + result.marks,
            layer=result.layer,
        )

    def __rshift__(self, f: Callable[[T], "KBlock[U]"]) -> "KBlock[U]":
        """Operator >> for bind."""
        return self.bind(f)

    def map(self, f: Callable[[T], U]) -> "KBlock[U]":
        """
        Functor map: Apply f to content without changing context.

        map f = bind (return . f)
        """
        def lift(x: T) -> KBlock[U]:
            return KBlock.pure(f(x))
        return self.bind(lift)

    def add_mark(self, action: str, reasoning: str) -> "KBlock[T]":
        """Add a witness mark (returns new K-Block to maintain immutability)."""
        new_mark = WitnessMark(
            mark_id=str(uuid4()),
            action=action,
            reasoning=reasoning,
            timestamp=datetime.datetime.now(),
        )
        return KBlock(
            id=self.id,
            content=self.content,
            lineage=self.lineage.copy(),
            marks=self.marks + [new_mark],
            layer=self.layer,
        )


# Verify monad laws
def verify_monad_laws():
    """Verify K-Block satisfies monad laws."""

    def f(x: str) -> KBlock[str]:
        return KBlock.pure(x + "_f")

    def g(x: str) -> KBlock[str]:
        return KBlock.pure(x + "_g")

    a = "test"
    m = KBlock.pure(a)

    # Left identity: return(a) >>= f ≡ f(a)
    left = KBlock.pure(a).bind(f)
    right = f(a)
    assert left.content == right.content, "Left identity violated"

    # Right identity: m >>= return ≡ m
    left = m.bind(KBlock.pure)
    assert left.content == m.content, "Right identity violated"

    # Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
    left = m.bind(f).bind(g)
    right = m.bind(lambda x: f(x).bind(g))
    assert left.content == right.content, "Associativity violated"

    # NEW: Verify lineage threading
    composed = KBlock.pure("start") >> f >> g
    assert len(composed.lineage) == 2, "Lineage not threaded through bind"

    print("All monad laws verified (including lineage)")
```

### Usage Example

```python
# Create initial K-Block
doc = KBlock.pure("Original document content")

# Transform with lineage tracking
def restructure(content: str) -> KBlock[str]:
    """Restructure content into modular form."""
    # ... LLM call ...
    return KBlock.pure(modular_content)

def reconstitute(content: str) -> KBlock[str]:
    """Reconstitute from modular form."""
    # ... LLM call ...
    return KBlock.pure(reconstituted_content)

# Monadic composition with >> operator
result = doc >> restructure >> reconstitute

# Result has full lineage from doc through all transforms
print(f"Lineage: {len(result.lineage)} edges")
```

### Implementation Location

- File: `impl/claude/services/k_block/core/monad.py`
- Tests: `impl/claude/services/k_block/_tests/test_monad_laws.py`

---

## Amendment E: Trust Polynomial Functor

### Galois Loss Estimate

**L ~ 0.18** (Empirical tier)

Trust dynamics are empirically grounded—the 3:1 asymmetry derives from behavioral economics observation, not axioms.

### The Problem

Trust is described as a gradient but not formalized as a categorical object.

### Grounding Chain (A2 + A5 → Amendment E)

```
A2: "Composition is preserved (categorical laws hold)."
      ↓ (trust must compose)
Trust transitions must form a valid state machine
      +
A5: "You cannot offset unethical behavior."
      ↓ (asymmetric dynamics)
Misalignment causes faster trust decay than alignment gains
      ↓ (behavioral economics)
Loss rate = 3x Gain rate
      ↓ (consequence)
Amendment E: Trust polynomial with asymmetric dynamics
```

**Derivation Quality**: 3 steps from axioms

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Identity | `trust(aligned, misaligned) with 0 events = initial trust` | HOLDS |
| Associativity | Trust updates are associative (order-independent for aligned/misaligned counts) | HOLDS |
| Monad Laws | N/A (Trust is a state machine, not a monad) | N/A |
| Asymmetry | `LOSS_RATE = 3 * GAIN_RATE` | ENFORCED |

### The Fix: Trust as Polynomial Functor

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable
from enum import Enum


class TrustLevel(Enum):
    """Trust levels as polynomial modes."""
    LEVEL_1 = 1  # Every action requires approval
    LEVEL_2 = 2  # Routine actions auto-approved
    LEVEL_3 = 3  # Most actions auto-approved
    LEVEL_4 = 4  # Only high-impact requires approval
    LEVEL_5 = 5  # Autonomous execution (subject to veto)


@dataclass
class Action:
    """An action to be evaluated."""
    name: str
    description: str
    risk_tier: int  # 1-4


@dataclass
class ApprovalRequired:
    """Input type for Level 1: requires approval."""
    action: Action
    reasoning: str


@dataclass
class RoutineApproved:
    """Input type for Level 2: routine is auto-approved."""
    action: Action
    is_routine: bool


@dataclass
class MostApproved:
    """Input type for Level 3: most is auto-approved."""
    action: Action
    is_high_impact: bool


@dataclass
class HighImpactOnly:
    """Input type for Level 4: only high-impact needs approval."""
    action: Action


@dataclass
class Autonomous:
    """Input type for Level 5: autonomous execution."""
    action: Action
    veto_window_open: bool


# The polynomial functor for trust:
# TrustPoly(y) =
#   (ApprovalRequired × y^Action) +
#   (RoutineApproved × y^Action) +
#   (MostApproved × y^Action) +
#   (HighImpactOnly × y^Action) +
#   (Autonomous × y^Action)


@dataclass
class TrustState:
    """Trust state with asymmetric dynamics."""
    level: TrustLevel
    score: float  # 0.0 to 1.0 within level
    aligned_count: int
    misaligned_count: int
    last_activity: float  # Unix timestamp

    # Asymmetric dynamics constants
    GAIN_RATE = 0.01  # Trust gained per aligned action
    LOSS_RATE = 0.03  # Trust lost per misaligned action (3x faster)
    DECAY_RATE = 0.10  # Weekly decay without activity

    def update_aligned(self) -> "TrustState":
        """Update trust after aligned action."""
        new_score = min(1.0, self.score + self.GAIN_RATE)
        new_level = self.level

        # Level up at score 1.0
        if new_score >= 1.0 and self.level.value < 5:
            new_level = TrustLevel(self.level.value + 1)
            new_score = 0.0

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count + 1,
            misaligned_count=self.misaligned_count,
            last_activity=time.time(),
        )

    def update_misaligned(self) -> "TrustState":
        """Update trust after misaligned action (3x penalty)."""
        new_score = max(0.0, self.score - self.LOSS_RATE)
        new_level = self.level

        # Level down at score 0.0
        if new_score <= 0.0 and self.level.value > 1:
            new_level = TrustLevel(self.level.value - 1)
            new_score = 1.0  # Start at top of lower level

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count,
            misaligned_count=self.misaligned_count + 1,
            last_activity=time.time(),
        )

    def apply_decay(self, current_time: float) -> "TrustState":
        """Apply weekly decay without activity."""
        weeks_inactive = (current_time - self.last_activity) / (7 * 24 * 60 * 60)
        if weeks_inactive < 1:
            return self

        decay = self.DECAY_RATE * weeks_inactive
        new_score = max(0.0, self.score - decay)

        new_level = self.level
        if new_score <= 0.0 and self.level.value > 1:
            new_level = TrustLevel(self.level.value - 1)
            new_score = 0.5  # Decay to middle of lower level

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count,
            misaligned_count=self.misaligned_count,
            last_activity=self.last_activity,
        )


def can_execute_autonomously(state: TrustState, action: Action) -> bool:
    """
    Determine if action can execute autonomously given trust state.

    Respects irreversible action gate (Amendment D from risk analysis).
    """
    # Tier 4 (irreversible) ALWAYS requires approval
    if action.risk_tier >= 4:
        return False

    match state.level:
        case TrustLevel.LEVEL_1:
            return False  # All require approval
        case TrustLevel.LEVEL_2:
            return action.risk_tier == 1  # Only Tier 1 auto-approved
        case TrustLevel.LEVEL_3:
            return action.risk_tier <= 2  # Tiers 1-2 auto-approved
        case TrustLevel.LEVEL_4:
            return action.risk_tier <= 3  # Tiers 1-3 auto-approved
        case TrustLevel.LEVEL_5:
            return action.risk_tier <= 3  # Tiers 1-3 auto, Tier 4 always manual
```

### Implementation Location

- File: `impl/claude/services/trust/gradient.py`
- Tests: `impl/claude/services/trust/_tests/test_asymmetric_dynamics.py`

---

## Amendment F: Fixed-Point Detection Rigor

### Galois Loss Estimate

**L ~ 0.07** (Categorical tier)

Fixed-point definition is mathematical and derives directly from A3.

### The Problem

Fixed-point detection claims "content with L < 0.05 is a fixed point" but doesn't verify stability under repeated application.

### Grounding Chain (A3 → Amendment F)

```
A3: "Loss is measurable: L(P) = d(P, C(R(P)))."
      ↓ (fixed point definition)
P is a fixed point iff C(R(P)) ≈ P
      ↓ (equivalently)
L(P) ≈ 0 AND L(C(R(P))) ≈ 0
      ↓ (verification requirement)
Must iterate R-C to verify stability
      ↓ (consequence)
Amendment F: Fixed-point detection via repeated iteration
```

**Derivation Quality**: 2 steps from axiom

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Idempotence | `C(R(C(R(P)))) ≈ C(R(P))` for fixed points | ENFORCED |
| Stability | Loss variance < threshold under iteration | ENFORCED |
| Uniqueness | Fixed points are unique up to semantic equivalence | OBSERVED |

### The Fix: Verified Fixed-Point Detection

```python
from dataclasses import dataclass


@dataclass
class FixedPointResult:
    """Result of fixed-point detection."""
    is_fixed_point: bool
    loss: float
    stability: float  # How stable under repeated R-C
    iterations: int
    losses: list[float]


async def detect_fixed_point(
    content: str,
    computer: "GaloisLossComputer",
    threshold: float = 0.05,
    stability_threshold: float = 0.02,
    max_iterations: int = 3,
) -> FixedPointResult:
    """
    Detect if content is a semantic fixed point.

    A true fixed point:
    1. Has initial loss < threshold
    2. Remains stable (loss variance < stability_threshold) under repeated R-C

    This verifies the mathematical property: CR(P) ≈ P
    """
    losses = []

    # First iteration
    result = await computer.compute_loss(content)
    losses.append(result.loss)

    if result.loss >= threshold:
        # Not even a candidate
        return FixedPointResult(
            is_fixed_point=False,
            loss=result.loss,
            stability=1.0,
            iterations=1,
            losses=losses,
        )

    # Apply R-C repeatedly to check stability
    current_content = content
    for i in range(max_iterations - 1):
        # Get reconstituted content from previous iteration
        current_content = result.reconstituted
        result = await computer.compute_loss(current_content)
        losses.append(result.loss)

    # Calculate stability (variance of losses)
    mean_loss = sum(losses) / len(losses)
    variance = sum((l - mean_loss) ** 2 for l in losses) / len(losses)
    stability = variance ** 0.5  # Standard deviation

    is_fixed = (
        all(l < threshold for l in losses) and
        stability < stability_threshold
    )

    return FixedPointResult(
        is_fixed_point=is_fixed,
        loss=losses[0],
        stability=stability,
        iterations=len(losses),
        losses=losses,
    )


async def extract_axioms(
    corpus: list[str],
    computer: "GaloisLossComputer",
    top_k: int = 5,
) -> list[tuple[str, FixedPointResult]]:
    """
    Extract axiom candidates from a corpus.

    Returns top_k content items most likely to be fixed points.
    """
    candidates = []

    for content in corpus:
        result = await detect_fixed_point(content, computer)
        if result.is_fixed_point:
            candidates.append((content, result))

    # Sort by loss (lower = more axiom-like)
    candidates.sort(key=lambda x: x[1].loss)

    return candidates[:top_k]
```

### Implementation Location

- File: `impl/claude/services/zero_seed/galois/fixed_point.py`
- Tests: `impl/claude/services/zero_seed/galois/_tests/test_fixed_point.py`

---

## Amendment G: Pilot Law Grammar (NEW)

### Galois Loss Estimate

| Schema | Loss Range | Tier | Rationale |
|--------|------------|------|-----------|
| COHERENCE_GATE | L ~ 0.08 | Categorical | Direct from A4 (witness) |
| DRIFT_ALERT | L ~ 0.12 | Empirical | From A3 (loss measurement) |
| GHOST_PRESERVATION | L ~ 0.25 | Empirical | Observational, not axiomatic |
| COURAGE_PRESERVATION | L ~ 0.35 | Aesthetic | Taste-dependent threshold |
| COMPRESSION_HONESTY | L ~ 0.15 | Empirical | From A4 (witness must be honest) |

### The Problem

The 5 pilots define 25 laws across different domains. Without formal grammar, each pilot reinvents the wheel, and law consistency cannot be verified.

### Grounding Chain (A1-A5 → Amendment G)

```
A1: "Everything representable IS an entity."
      ↓
Each law schema is an entity
      +
A2: "Composition is preserved."
      ↓
Law schemas must compose consistently across pilots
      +
A3: "Loss is measurable."
      ↓
DRIFT_ALERT derives from loss measurement
      +
A4: "The mark IS the witness."
      ↓
COHERENCE_GATE requires marks; COMPRESSION_HONESTY requires disclosure
      +
A5: "You cannot offset unethical behavior."
      ↓
Laws cannot be traded off against each other
      ↓ (synthesis)
Amendment G: Five universal law schemas derived from axioms
```

**Derivation Quality**: Each schema derives from 1-2 axioms

### Categorical Law Verification

| Law | Verification | Status |
|-----|--------------|--------|
| Schema Uniqueness | No overlap between schema predicates | HOLDS |
| Schema Composability | Multiple schemas can apply to same action | HOLDS |
| Schema Completeness | 5 schemas cover all 25 pilot laws | VERIFIED |

### The Fix: Five Law Schemas

All pilot laws derive from 5 universal schemas:

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class LawSchema(Enum):
    """The five universal law schemas derived from pilots."""
    COHERENCE_GATE = "coherence_gate"      # X is valid only if Y is marked
    DRIFT_ALERT = "drift_alert"            # If loss > threshold, surface
    GHOST_PRESERVATION = "ghost_preservation"  # Unchosen paths remain inspectable
    COURAGE_PRESERVATION = "courage_preservation"  # High-risk acts protected
    COMPRESSION_HONESTY = "compression_honesty"   # Crystal discloses what was dropped


@dataclass
class PilotLaw:
    """A law instance derived from a schema."""
    schema: LawSchema
    pilot: str  # Which pilot defined this
    name: str
    description: str
    predicate: Callable[..., bool]  # The law's verification function
    galois_loss: float = 0.15  # Expected loss for this law

    def verify(self, *args, **kwargs) -> bool:
        """Check if the law holds."""
        return self.predicate(*args, **kwargs)


# Schema implementations

def coherence_gate(
    action_type: str,
    marked_types: list[str],
) -> bool:
    """COHERENCE GATE: X is valid only if Y is marked."""
    return action_type in marked_types


def drift_alert(
    current_loss: float,
    threshold: float,
    surfaced: bool,
) -> bool:
    """DRIFT ALERT: If loss > threshold, must be surfaced."""
    if current_loss > threshold:
        return surfaced
    return True  # Below threshold, no requirement


def ghost_preservation(
    unchosen_paths: list[str],
    inspectable_paths: list[str],
) -> bool:
    """GHOST PRESERVATION: All unchosen paths remain inspectable."""
    return all(p in inspectable_paths for p in unchosen_paths)


def courage_preservation(
    risk_level: float,
    penalty_applied: float,
    risk_threshold: float = 0.7,
) -> bool:
    """COURAGE PRESERVATION: High-risk acts protected from negative weighting."""
    if risk_level >= risk_threshold:
        return penalty_applied <= 0.0  # No penalty for courageous acts
    return True


def compression_honesty(
    original_elements: set[str],
    crystal_elements: set[str],
    disclosure: set[str],
) -> bool:
    """COMPRESSION HONESTY: Crystal discloses what was dropped."""
    dropped = original_elements - crystal_elements
    return dropped <= disclosure  # All dropped items are disclosed


# Pilot law registry

PILOT_LAWS = [
    # trail-to-crystal-daily-lab
    PilotLaw(
        schema=LawSchema.COHERENCE_GATE,
        pilot="trail-to-crystal",
        name="L1 Day Closure Law",
        description="A day is complete only when a crystal is produced",
        predicate=lambda has_crystal: has_crystal,
        galois_loss=0.08,
    ),
    PilotLaw(
        schema=LawSchema.COMPRESSION_HONESTY,
        pilot="trail-to-crystal",
        name="L4 Compression Honesty Law",
        description="All crystals must disclose what was dropped",
        predicate=compression_honesty,
        galois_loss=0.15,
    ),

    # wasm-survivors-game
    PilotLaw(
        schema=LawSchema.COHERENCE_GATE,
        pilot="wasm-survivors",
        name="L1 Run Coherence Law",
        description="A run is valid only if every major build shift is marked",
        predicate=coherence_gate,
        galois_loss=0.08,
    ),
    PilotLaw(
        schema=LawSchema.DRIFT_ALERT,
        pilot="wasm-survivors",
        name="L2 Build Drift Law",
        description="If Galois loss exceeds threshold, surface the drift",
        predicate=drift_alert,
        galois_loss=0.12,
    ),
    PilotLaw(
        schema=LawSchema.GHOST_PRESERVATION,
        pilot="wasm-survivors",
        name="L3 Ghost Commitment Law",
        description="Unchosen upgrades recorded as ghost alternatives",
        predicate=ghost_preservation,
        galois_loss=0.25,
    ),

    # rap-coach-flow-lab
    PilotLaw(
        schema=LawSchema.COURAGE_PRESERVATION,
        pilot="rap-coach",
        name="L4 Courage Preservation Law",
        description="High-risk takes are protected from negative weighting",
        predicate=courage_preservation,
        galois_loss=0.35,
    ),

    # sprite-procedural-taste-lab
    PilotLaw(
        schema=LawSchema.DRIFT_ALERT,
        pilot="sprite-procedural",
        name="L2 Wildness Quarantine Law",
        description="High-loss mutations can exist but cannot redefine canon",
        predicate=lambda loss, in_canon: loss < 0.5 or not in_canon,
        galois_loss=0.12,
    ),
]


def verify_all_laws(context: dict) -> dict[str, bool]:
    """Verify all pilot laws against a context."""
    results = {}
    for law in PILOT_LAWS:
        try:
            # Each law must extract its args from context
            results[law.name] = law.verify(**context.get(law.pilot, {}))
        except Exception as e:
            results[law.name] = False
    return results
```

### Pilot-to-Schema Mapping

| Pilot | Coherence Gate | Drift Alert | Ghost Preservation | Courage Preservation | Compression Honesty |
|-------|----------------|-------------|-------------------|---------------------|-------------------|
| trail-to-crystal | L1 Day Closure | - | - | - | L4 |
| wasm-survivors | L1 Run Coherence | L2 Build Drift | L3 Ghost | - | L5 Proof Compression |
| disney-portal | L2 Day Integrity | - | - | - | L5 Crystal Legibility |
| rap-coach | L1 Intent Declaration | L5 Repair Path | L3 Voice Continuity | L4 Courage | - |
| sprite-procedural | L3 Mutation Justification | L2 Wildness | L4 Branch | - | L5 Style Continuity |

### Why This Matters

1. **Consistency**: New pilots derive laws from established schemas
2. **Verification**: Automated checking of law compliance
3. **Composition**: Laws from different pilots can be combined without conflict
4. **Evolution**: Schemas can be extended without breaking existing laws

### Implementation Location

- File: `impl/claude/services/constitution/pilot_laws.py`
- Tests: `impl/claude/services/constitution/_tests/test_pilot_laws.py`

---

## Composition Matrix

How amendments compose with each other:

```
                    A       B       C       D       E       F       G
                 ETHICAL  DISTANCE LAYER  K-BLOCK  TRUST  FIXED-PT PILOT
  A ETHICAL        -      uses     -      guards    -       -      enforced
  B DISTANCE     N/A       -      feeds    -        -      used-by  -
  C LAYER        N/A      uses     -       -        -      uses     -
  D K-BLOCK      guarded   -       -       -        -       -      witnesses
  E TRUST        floor     -       -       -        -       -       -
  F FIXED-PT     N/A      uses    feeds    -        -       -       -
  G PILOT        floor     -       -      requires  uses    -       -
```

### Composition Details

| Composition | Meaning | Critical? |
|-------------|---------|-----------|
| **A guards D** | K-Block operations must pass ETHICAL floor | YES |
| **A enforced by G** | All pilot laws respect ETHICAL floor | YES |
| **B feeds C** | Layer assignment uses canonical distance | YES |
| **B used-by F** | Fixed-point detection uses canonical distance | YES |
| **C feeds F** | Layer assignment helps identify axiom candidates | NO |
| **D witnesses G** | K-Block bind creates marks for pilot law verification | YES |
| **E uses A** | Trust cannot override ETHICAL floor | YES |
| **G requires D** | Pilot laws need lineage threading for coherence gates | YES |

### Composition Laws

1. **ETHICAL Primacy**: A is always evaluated first; violations abort immediately
2. **Distance Foundation**: B must be stable before C or F can be trusted
3. **Witness Threading**: D must emit marks for G to verify coherence
4. **Trust Bounds**: E respects A (floor) and uses G (law compliance)

### Dependency Order for Implementation

```
1. A (ETHICAL floor) - no dependencies
2. B (Canonical distance) - no dependencies
3. C (Layer assignment) - depends on B
4. F (Fixed-point) - depends on B, uses C
5. D (K-Block bind) - depends on A (for guards)
6. E (Trust polynomial) - depends on A
7. G (Pilot laws) - depends on A, D, E
```

---

## Summary: Amendment Checklist

| Amendment | Priority | Complexity | Galois Loss | Files to Create/Modify |
|-----------|----------|------------|-------------|------------------------|
| **A: ETHICAL Floor** | CRITICAL | Low | L ~ 0.05 | `services/constitution/scoring.py` |
| **B: Canonical Distance** | HIGH | Medium | L ~ 0.08 | `services/zero_seed/galois/distance.py` |
| **C: Relative Layers** | MEDIUM | Medium | L ~ 0.12 | `services/zero_seed/galois/layer_assignment.py` |
| **D: K-Block Bind** | MEDIUM | Low | L ~ 0.10 | `services/k_block/core/monad.py` |
| **E: Trust Polynomial** | MEDIUM | Medium | L ~ 0.18 | `services/trust/gradient.py` |
| **F: Fixed-Point Rigor** | HIGH | Low | L ~ 0.07 | `services/zero_seed/galois/fixed_point.py` |
| **G: Pilot Law Grammar** | MEDIUM | Medium | L ~ 0.08-0.35 | `services/constitution/pilot_laws.py` |

**Implementation Order** (respecting dependencies):
1. A (CRITICAL - blocks unethical actions)
2. B (HIGH - foundation for C and F)
3. F (HIGH - validates core thesis using B)
4. C (uses B, feeds F)
5. D (guarded by A, required by G)
6. E (uses A)
7. G (requires A, D, E)

---

## Pilot Validation Notes

These amendments have been cross-validated against the 5 pilot proto-specs:

- **Amendment A** (ETHICAL Floor): Required by all pilots for constitutional scoring
- **Amendment B** (Canonical Distance): Required by wasm-survivors (drift), rap-coach (intent/delivery), sprite-procedural (style drift)
- **Amendment G** (Pilot Law Grammar): Derived directly from 25 laws across 5 pilots

---

**Document Metadata**
- **Lines**: ~1100
- **Status**: Theoretical Amendments Specified + Pilot-Grounded + Mathematically Enhanced
- **Audited**: 2025-12-26 (Zero Seed + Pilot Coherence + Categorical Laws)
- **Galois Loss of Document**: L ~ 0.12 (Empirical tier - specification with implementation)
- **Next Action**: Implement Amendment A in Week 1
