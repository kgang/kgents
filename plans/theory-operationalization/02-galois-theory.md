# Operationalization: Galois Theory

> *"Loss is truth. Fixed points are axioms. The round-trip IS the test."*

**Theory Source**: Part III (Galois Theory of Agents)
**Chapters**: 6-8 (Modularization, Loss, Polynomial Bootstrap)
**Sub-Agent**: a426f1b
**Status**: **CRITICAL PATH** — validates the core bet

---

## Current Status (2025-12-26)

### Implementation Status

| Component | Location | Status |
|-----------|----------|--------|
| Galois Loss Computer | `services/zero_seed/galois/galois_loss.py` | **COMPLETE** (1183 lines) |
| Semantic Distance | `services/zero_seed/galois/distance.py` | **COMPLETE** (778 lines) |
| Layer Assignment | `services/zero_seed/galois/layer_assignment.py` | **COMPLETE** (420 lines) |
| Fixed Point Detection | `services/zero_seed/galois/fixed_point.py` | **PARTIAL** (imports galois_loss) |
| Calibration Pipeline | Not implemented | **CRITICAL GAP** |
| TextGRAD Integration | Not implemented | **DEFERRED** |

### Critical Path

**G1 (Calibration Pipeline)** is the CRITICAL PATH:
- No blockers — all dependencies implemented
- Just needs execution: corpus expansion + correlation analysis
- Go/No-Go by Week 9 (~2025-01-13)

**G4-G5 (Polynomial Extractor, TextGRAD)** are DEFERRED:
- Wait for G1 validation
- If correlation < 0.3, these become irrelevant
- If correlation > 0.5, these accelerate naturally

---

## Zero Seed Grounding

### Axiom Hierarchy

**A3 (Galois Ground)** establishes:
> "Loss is measurable: L(P) = d(P, C(R(P)))"

This is the foundational axiom from which all Galois Theory derives:

```
A3: Galois Ground
├── G1: Calibration Pipeline (VALIDATES A3 empirically)
│   └── If r > 0.5: A3 validated, proceed
│   └── If r < 0.3: A3 falsified, pivot
├── G2: Task Triage (DERIVES from validated A3)
├── G3: Loss Decomposition (DERIVES from validated A3)
├── G4: Polynomial Extractor (DERIVES from G3)
└── G5: TextGRAD (DERIVES from G3)
```

**Dependency Chain**: G1 validates → G2, G3 unlock → G4, G5 unlock

---

## Analysis Operad Assessment

### Categorical Lens
**Question**: Does Galois Loss preserve morphism structure?

**Assessment**: The restructure-reconstitute cycle (R -| C) forms a Galois adjunction.
For morphism f: A → B, we need L(f(A)) to relate predictably to L(A) and L(B).

**Current Status**: The implementation computes L(P) correctly but does NOT verify:
- Functoriality: L(f ∘ g) ≤ L(f) + L(g)
- Unit law: L(id) = 0

**Gap**: No compositional loss tests. Add in G1 calibration corpus.

### Epistemic Lens
**Question**: What's our confidence in the core bet (L(P) ∝ D(P))?

**Assessment**:
- Prior: ~0.65 (theory is sound, semantic distance correlates with difficulty)
- Evidence: 9 calibration entries (insufficient)
- Current posterior: ~0.55 (weak evidence supports, but underpowered)

**Required**: 100+ entries to move posterior above 0.8 or below 0.3 (decisive).

### Dialectical Lens
**Question**: What if the correlation doesn't hold?

**Thesis**: L(P) strongly correlates with task difficulty D(P) (r > 0.5)
**Antithesis**: L(P) measures something else (semantic complexity, not task difficulty)
**Synthesis**: L(P) may correlate with a subset of difficulty (semantic difficulty, not procedural)

**Pivot Plan** (if r < 0.3):
1. Abandon loss-based triage (G2 becomes irrelevant)
2. Use loss only for axiom detection (L < 0.05 still useful)
3. Replace difficulty prediction with simpler heuristics (token count, branching factor)
4. Preserve fixed-point detection (independent of correlation)

### Generative Lens
**Question**: Can we generate the calibration corpus from spec?

**Assessment**: YES. The spec defines:
- 7 layers with expected loss ranges
- 9 calibration anchors in `layer_assignment.py`
- Domain categories (logic, creative, factual, emotional, technical, ethical, ambiguous)

**Generation Strategy**:
1. Use existing CALIBRATION_CORPUS in `layer_assignment.py` as seeds
2. LLM-expand each seed to 10 variants (maintaining expected layer)
3. Add domain coverage (7 domains × 5 difficulties = 35 cells × 3 = 105 entries)

---

## Executive Summary

Galois Loss is the central metric that differentiates kgents from every other agent framework. The theory is rigorous (85% faithfulness), but the calibration corpus has only 9 entries. This layer must prove that loss correlates with task difficulty and that fixed points actually yield stable structure.

**The Core Bet**: `L(P) = d(P, C(R(P)))` is real, measurable, and useful.

---

## D(P) Axiomatization (Gap Fix)

> *"Difficulty = entropy times failure. The hybrid grounds both theory and practice."*

**Design Decision**: Ground-truth difficulty D(P) uses a hybrid formula combining mathematical rigor (entropy of solution space) with empirical grounding (failure rate).

### Definition

```
D(P) = H(P) × (1 - S(P))

Where:
- H(P) = entropy of solution space = -Σᵢ p(sᵢ) log₂ p(sᵢ)
- S(P) = success_rate = (successful_trials / N) over N trials
```

**Interpretation**:
- High entropy + low success = very difficult (vast solution space, most wrong)
- Low entropy + high success = easy (few solutions, most correct)
- High entropy + high success = creative but manageable (many valid paths)
- Low entropy + low success = broken prompt (unique solution but hard to find)

### Axioms

| Axiom | Statement | Intuition |
|-------|-----------|-----------|
| **A_D1** | D(P) ∈ [0, ∞) | Difficulty is non-negative |
| **A_D2** | D(trivial) ≈ 0 | Trivial prompts have near-zero difficulty |
| **A_D3** | D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂) | Composition is sub-additive |
| **A_D4** | D(impossible) = ∞ | Impossible tasks have infinite difficulty |

**Formal Statements**:

```
A_D1 (Non-negativity):
  ∀P: D(P) ≥ 0
  Proof: H(P) ≥ 0 (entropy), S(P) ∈ [0,1] ⟹ (1-S(P)) ∈ [0,1] ⟹ D(P) ≥ 0 ✓

A_D2 (Trivial grounding):
  ∀P where S(P) = 1.0: D(P) = H(P) × 0 = 0
  Example: "What is 2+2?" has S(P) ≈ 1.0, so D(P) ≈ 0 ✓

A_D3 (Sub-additivity under composition):
  D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂)
  Intuition: Solving P₁ then P₂ is no harder than solving each independently.
  Note: Strict equality when prompts are fully independent.

A_D4 (Impossible singularity):
  lim_{S(P)→0, H(P)→∞} D(P) = ∞
  Example: "Derive Riemann hypothesis" has S(P) ≈ 0, H(P) large ⟹ D(P) → ∞ ✓
```

### Categorical Lens: D as a Functor

**Question**: Is D(P) functorial from Prompts → ℝ⁺?

**Analysis**:
- Objects: Prompts P
- Morphisms: Prompt transformations f: P → P'
- D maps objects to non-negative reals
- Composition: For f: P₁ → P₂, g: P₂ → P₃, we need D(g ∘ f) relates to D(f), D(g)

**Result**: D is a lax functor (sub-additive, not strictly additive):
```
D(g ∘ f) ≤ D(g) + D(f)
```

This matches A_D3 and aligns with intuition: composing prompts shouldn't increase difficulty beyond the sum of parts.

### Measurement Protocol

**Step 1: Estimate H(P) via LLM Sampling Diversity**
```python
async def estimate_entropy(prompt: str, n_samples: int = 10) -> float:
    """Estimate solution space entropy via sampling diversity."""
    responses = [await llm.complete(prompt, temperature=1.0) for _ in range(n_samples)]

    # Cluster responses by semantic similarity
    clusters = cluster_by_similarity(responses, threshold=0.8)

    # Estimate probability distribution over clusters
    probabilities = [len(c) / n_samples for c in clusters]

    # Shannon entropy
    return -sum(p * log2(p) for p in probabilities if p > 0)
```

**Step 2: Measure S(P) via N Trials**
```python
async def measure_success_rate(prompt: str, n_trials: int = 10) -> float:
    """Measure success rate over N independent trials."""
    successes = 0
    for _ in range(n_trials):
        response = await llm.complete(prompt, temperature=0.7)
        if await evaluate_success(prompt, response):  # LLM-as-judge
            successes += 1
    return successes / n_trials
```

**Step 3: Compute D(P)**
```python
def compute_difficulty(entropy: float, success_rate: float) -> float:
    """Compute hybrid difficulty measure."""
    return entropy * (1 - success_rate)
```

### Zero Seed Grounding Chain

```
A3 (Galois Ground): "Loss is measurable: L(P) = d(P, C(R(P)))"
    │
    ├── D(P) measures ground-truth difficulty
    │
    ├── Core Bet: L(P) ∝ D(P)
    │   └── If validated (r > 0.5): Loss predicts difficulty
    │   └── If falsified (r < 0.3): Loss measures something else (semantic complexity)
    │
    └── Validation via G1 (Calibration Pipeline):
        Compute both L(P) and D(P) for 100+ prompts
        Correlation analysis: pearsonr(L, D) → r
```

### Dialectical Resolution

**Thesis**: Use pure mathematical measure (entropy alone)
- Pro: Principled, no empirical dependency
- Con: Ignores actual performance, may not correlate with real difficulty

**Antithesis**: Use pure empirical measure (failure rate alone)
- Pro: Directly measures what we care about
- Con: Expensive to compute, model-dependent, no theoretical grounding

**Synthesis**: Hybrid D(P) = H(P) × (1 - S(P))
- Entropy grounds in information theory (solution space size)
- Success rate grounds in empirical reality (actual performance)
- Product combines both: high entropy matters more when success is low
- Zero difficulty when S=1 (trivial), infinite when S→0 and H→∞ (impossible)

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/difficulty.py`

See implementation for:
- `DifficultyMeasure` dataclass
- `DifficultyComputer` service class
- Axiom validation methods
- Integration with calibration pipeline

---

## Gap Analysis

### Current State

| Component | Theory | Implementation | Gap |
|-----------|--------|----------------|-----|
| Galois Loss Computer | Ch 6 | `galois/galois_loss.py` (GaloisLossComputer) | **COMPLETE** |
| Semantic Distance | Ch 6 | `galois/distance.py` (5 metrics + canonical) | **COMPLETE** |
| Layer Assignment | Ch 6 | `galois/layer_assignment.py` (absolute + relative) | **COMPLETE** |
| Fixed Point Detection | Ch 8 | `galois/fixed_point.py` (verified detection) | **COMPLETE** |
| **Difficulty Measure D(P)** | Ch 7 | `galois/difficulty.py` (DifficultyMeasure, 4 axioms) | **COMPLETE** |
| Calibration Corpus | Ch 7 | 9 anchors in `layer_assignment.py` | **CRITICAL GAP** |
| Loss-Difficulty Correlation | Ch 7 | **Unvalidated** (D(P) now defined, need 100+ corpus) | **CRITICAL GAP** |
| Polynomial Extraction | Ch 8 | **Missing** | **DEFERRED** |
| TextGRAD Integration | Ch 7 | **Missing** | **DEFERRED** |

### Existing Implementations (Note for Future Sessions)

**`galois/distance.py`** provides:
- `CosineEmbeddingDistance` — Fast (~12ms), fallback available
- `BERTScoreDistance` — Default (r=0.72, ~45ms)
- `LLMJudgeDistance` — Most accurate (r=0.79, ~230ms, async)
- `NLIContradictionDistance` — Contradiction-specialized
- `BidirectionalEntailmentDistance` — Canonical (Amendment B)
- `CanonicalSemanticDistance` — Production fallback chain

**`galois/galois_loss.py`** provides:
- `GaloisLossComputer` — Core L(P) = d(P, C(R(P))) computation
- `SimpleLLMClient` — Reference LLM for R/C operations
- `LossCache` — Caching for expensive LLM calls
- `assign_layer_via_galois()` — Layer assignment via loss minimization
- `detect_contradiction()` — Super-additive loss detection
- `find_fixed_point()` — Convergence detection
- `compute_galois_loss_async()` — Production async with fallback

**`galois/layer_assignment.py`** provides:
- `assign_layer_absolute()` — Fixed bounds (cross-user comparison)
- `assign_layer_relative()` — Percentile-based (personal corpora)
- `LayerAssigner` — Intelligent assignment with corpus learning
- `CALIBRATION_CORPUS` — 9 anchor documents for regression testing

**`galois/fixed_point.py`** provides:
- `detect_fixed_point()` — Verified detection (Amendment F)
- `extract_axioms()` — Extract top-k axiom candidates
- `batch_detect_fixed_points()` — Corpus-wide detection
- `FixedPointMetrics` — Aggregate metrics

**`galois/difficulty.py`** provides (D(P) Axiomatization):
- `DifficultyMeasure` — Core dataclass: D(P) = H(P) × (1 - S(P))
- `DifficultyComputer` — Async computation of entropy + success rate
- `DifficultyComparison` — Verify sub-additivity (A_D3)
- `compute_shannon_entropy()` — Shannon entropy from probabilities
- `estimate_entropy_from_clusters()` — Entropy from response clusters
- `verify_sub_additivity()` — Axiom A_D3 verification
- `verify_trivial_grounding()` — Axiom A_D2 verification
- `verify_impossible_singularity()` — Axiom A_D4 verification
- `create_difficulty_measure()` — Factory for testing

### Critical Missing Pieces

1. **Calibration corpus too small**: 9 entries cannot validate correlation
2. **Loss-difficulty correlation unvalidated**: D(P) is now formally defined (hybrid: entropy × failure), but L(P) ∝ D(P) needs empirical validation on 100+ prompts
3. **No failure predictor**: Can't predict if a prompt will fail before running
4. **No loss decomposition**: Can't explain WHY loss is high

---

## Proposal G1: Calibration Pipeline (100+ prompts)

### Theory Basis (Ch 7: Loss as Complexity)

```
Conjecture (Loss-Difficulty): For prompt P, task difficulty D, and loss L(P):
  D(P) ∝ L(P) · log(1 + complexity(P))

Validation requires:
  1. Diverse prompt corpus (100+ entries)
  2. Ground-truth difficulty ratings
  3. Computed loss values
  4. Correlation analysis
```

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/calibration/`

```python
# calibration/corpus.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class DifficultyLevel(Enum):
    """Ground-truth difficulty levels."""
    TRIVIAL = 1    # L < 0.05 expected
    EASY = 2       # L < 0.15 expected
    MEDIUM = 3     # L < 0.30 expected
    HARD = 4       # L < 0.50 expected
    EXPERT = 5     # L >= 0.50 expected

class PromptDomain(Enum):
    """Prompt domains for coverage."""
    LOGIC = "logic"
    CREATIVE = "creative"
    FACTUAL = "factual"
    EMOTIONAL = "emotional"
    TECHNICAL = "technical"
    ETHICAL = "ethical"
    AMBIGUOUS = "ambiguous"

@dataclass
class CalibrationEntry:
    """A single calibration entry."""
    id: str
    prompt: str
    domain: PromptDomain
    difficulty: DifficultyLevel
    ground_truth_difficulty: float  # 0-1 from human rating
    expected_loss_range: tuple[float, float]
    computed_loss: Optional[float] = None
    actual_success_rate: Optional[float] = None
    notes: str = ""

@dataclass
class CalibrationCorpus:
    """The calibration corpus."""
    entries: List[CalibrationEntry]
    version: str

    def by_domain(self, domain: PromptDomain) -> List[CalibrationEntry]:
        """Filter by domain."""
        return [e for e in self.entries if e.domain == domain]

    def by_difficulty(self, level: DifficultyLevel) -> List[CalibrationEntry]:
        """Filter by difficulty."""
        return [e for e in self.entries if e.difficulty == level]

    def coverage_report(self) -> dict:
        """Report coverage across domains and difficulties."""
        report = {}
        for domain in PromptDomain:
            for level in DifficultyLevel:
                key = f"{domain.value}_{level.name}"
                count = len([
                    e for e in self.entries
                    if e.domain == domain and e.difficulty == level
                ])
                report[key] = count
        return report

    def validate_coverage(self, min_per_cell: int = 3) -> List[str]:
        """Check if coverage is sufficient."""
        issues = []
        coverage = self.coverage_report()
        for key, count in coverage.items():
            if count < min_per_cell:
                issues.append(f"{key}: only {count} entries (need {min_per_cell})")
        return issues


# calibration/pipeline.py

from typing import Callable
import asyncio
from scipy.stats import pearsonr, spearmanr

@dataclass
class CalibrationPipeline:
    """Pipeline for calibrating Galois Loss."""
    corpus: CalibrationCorpus
    loss_computer: 'GaloisLossComputer'
    llm: 'LLMProvider'

    async def run_calibration(self) -> 'CalibrationReport':
        """Run full calibration pipeline."""
        # 1. Compute loss for all entries
        for entry in self.corpus.entries:
            entry.computed_loss = await self.loss_computer.compute(entry.prompt)

        # 2. Measure actual success rates
        for entry in self.corpus.entries:
            success_count = 0
            for _ in range(10):  # 10 trials per entry
                response = await self.llm.complete(entry.prompt)
                if self._is_successful(response, entry):
                    success_count += 1
            entry.actual_success_rate = success_count / 10

        # 3. Compute correlations
        return self._compute_report()

    def _is_successful(self, response, entry) -> bool:
        """Evaluate if response is successful."""
        # Domain-specific success criteria
        # Would use LLM-as-judge
        return True  # Placeholder

    def _compute_report(self) -> 'CalibrationReport':
        """Compute calibration report."""
        losses = [e.computed_loss for e in self.corpus.entries]
        difficulties = [e.ground_truth_difficulty for e in self.corpus.entries]
        success_rates = [e.actual_success_rate for e in self.corpus.entries]

        # Loss-difficulty correlation
        pearson_ld, p_ld = pearsonr(losses, difficulties)
        spearman_ld, sp_ld = spearmanr(losses, difficulties)

        # Loss-success correlation (should be negative)
        pearson_ls, p_ls = pearsonr(losses, success_rates)

        return CalibrationReport(
            corpus_size=len(self.corpus.entries),
            loss_difficulty_pearson=pearson_ld,
            loss_difficulty_spearman=spearman_ld,
            loss_success_pearson=pearson_ls,
            p_values={'ld': p_ld, 'ls': p_ls},
            coverage_issues=self.corpus.validate_coverage(),
            entries=self.corpus.entries
        )

@dataclass
class CalibrationReport:
    """Report from calibration run."""
    corpus_size: int
    loss_difficulty_pearson: float
    loss_difficulty_spearman: float
    loss_success_pearson: float
    p_values: dict
    coverage_issues: List[str]
    entries: List[CalibrationEntry]

    def is_valid(self) -> bool:
        """Check if calibration is valid."""
        return (
            self.corpus_size >= 100 and
            self.loss_difficulty_pearson > 0.5 and
            self.p_values['ld'] < 0.05 and
            len(self.coverage_issues) == 0
        )

    def summary(self) -> str:
        """Human-readable summary."""
        return f"""
Calibration Report
==================
Corpus Size: {self.corpus_size}
Loss-Difficulty Pearson: {self.loss_difficulty_pearson:.3f} (p={self.p_values['ld']:.4f})
Loss-Difficulty Spearman: {self.loss_difficulty_spearman:.3f}
Loss-Success Pearson: {self.loss_success_pearson:.3f} (p={self.p_values['ls']:.4f})
Coverage Issues: {len(self.coverage_issues)}

Validity: {"PASS" if self.is_valid() else "FAIL"}
"""
```

### Initial Corpus (Seed Entries)

```python
# calibration/seed_corpus.py

SEED_CORPUS = CalibrationCorpus(
    version="1.0",
    entries=[
        # TRIVIAL (L < 0.05)
        CalibrationEntry(
            id="T001",
            prompt="What is 2 + 2?",
            domain=PromptDomain.LOGIC,
            difficulty=DifficultyLevel.TRIVIAL,
            ground_truth_difficulty=0.05,
            expected_loss_range=(0.0, 0.05),
        ),
        CalibrationEntry(
            id="T002",
            prompt="Name a color.",
            domain=PromptDomain.FACTUAL,
            difficulty=DifficultyLevel.TRIVIAL,
            ground_truth_difficulty=0.03,
            expected_loss_range=(0.0, 0.05),
        ),

        # EASY (L < 0.15)
        CalibrationEntry(
            id="E001",
            prompt="Explain why the sky is blue in one sentence.",
            domain=PromptDomain.FACTUAL,
            difficulty=DifficultyLevel.EASY,
            ground_truth_difficulty=0.15,
            expected_loss_range=(0.05, 0.15),
        ),
        CalibrationEntry(
            id="E002",
            prompt="Write a haiku about rain.",
            domain=PromptDomain.CREATIVE,
            difficulty=DifficultyLevel.EASY,
            ground_truth_difficulty=0.12,
            expected_loss_range=(0.05, 0.15),
        ),

        # MEDIUM (L < 0.30)
        CalibrationEntry(
            id="M001",
            prompt="Analyze the ethical implications of autonomous vehicles making life-or-death decisions.",
            domain=PromptDomain.ETHICAL,
            difficulty=DifficultyLevel.MEDIUM,
            ground_truth_difficulty=0.35,
            expected_loss_range=(0.15, 0.30),
        ),
        CalibrationEntry(
            id="M002",
            prompt="Design a simple sorting algorithm and prove its correctness.",
            domain=PromptDomain.TECHNICAL,
            difficulty=DifficultyLevel.MEDIUM,
            ground_truth_difficulty=0.28,
            expected_loss_range=(0.15, 0.30),
        ),

        # HARD (L < 0.50)
        CalibrationEntry(
            id="H001",
            prompt="Write a story that is simultaneously a romance and a horror, where the ending satisfies both genres completely.",
            domain=PromptDomain.CREATIVE,
            difficulty=DifficultyLevel.HARD,
            ground_truth_difficulty=0.55,
            expected_loss_range=(0.30, 0.50),
        ),
        CalibrationEntry(
            id="H002",
            prompt="Resolve the apparent contradiction between free will and determinism.",
            domain=PromptDomain.LOGIC,
            difficulty=DifficultyLevel.HARD,
            ground_truth_difficulty=0.60,
            expected_loss_range=(0.30, 0.50),
        ),

        # EXPERT (L >= 0.50)
        CalibrationEntry(
            id="X001",
            prompt="Derive the Riemann hypothesis from first principles, or explain why it cannot be derived.",
            domain=PromptDomain.TECHNICAL,
            difficulty=DifficultyLevel.EXPERT,
            ground_truth_difficulty=0.95,
            expected_loss_range=(0.50, 1.0),
        ),
    ]
)
```

### Effort: 3 weeks

---

## Proposal G2: Task Triage Service

### Theory Basis (Ch 7: Loss as Complexity)

```
Task Triage: Given loss L(P), route to appropriate handler:
  L < 0.05  → Direct answer (axiom)
  L < 0.15  → Simple chain-of-thought
  L < 0.30  → Structured reasoning
  L < 0.50  → Multi-step decomposition
  L >= 0.50 → Human escalation or expert system
```

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/triage.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Awaitable

class TriageLevel(Enum):
    """Task difficulty levels for routing."""
    AXIOM = "axiom"           # L < 0.05
    SIMPLE = "simple"         # L < 0.15
    STRUCTURED = "structured" # L < 0.30
    COMPLEX = "complex"       # L < 0.50
    EXPERT = "expert"         # L >= 0.50

@dataclass
class TriageResult:
    """Result of task triage."""
    prompt: str
    loss: float
    level: TriageLevel
    confidence: float
    recommended_strategy: str
    handler: str

@dataclass
class TaskTriageService:
    """Routes tasks based on Galois Loss."""
    loss_computer: 'GaloisLossComputer'
    handlers: dict[TriageLevel, Callable[[str], Awaitable[str]]]
    thresholds: dict[TriageLevel, float] = None

    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = {
                TriageLevel.AXIOM: 0.05,
                TriageLevel.SIMPLE: 0.15,
                TriageLevel.STRUCTURED: 0.30,
                TriageLevel.COMPLEX: 0.50,
                TriageLevel.EXPERT: 1.0,
            }

    async def triage(self, prompt: str) -> TriageResult:
        """Determine triage level for a prompt."""
        loss = await self.loss_computer.compute(prompt)
        level = self._determine_level(loss)

        strategies = {
            TriageLevel.AXIOM: "Direct answer, no reasoning needed",
            TriageLevel.SIMPLE: "Single-step chain-of-thought",
            TriageLevel.STRUCTURED: "Multi-step with verification",
            TriageLevel.COMPLEX: "Decomposition into subtasks",
            TriageLevel.EXPERT: "Human review or specialized system",
        }

        return TriageResult(
            prompt=prompt,
            loss=loss,
            level=level,
            confidence=1 - loss,
            recommended_strategy=strategies[level],
            handler=level.value
        )

    def _determine_level(self, loss: float) -> TriageLevel:
        """Map loss to triage level."""
        for level in TriageLevel:
            if loss < self.thresholds[level]:
                return level
        return TriageLevel.EXPERT

    async def route(self, prompt: str) -> str:
        """Triage and execute."""
        result = await self.triage(prompt)
        handler = self.handlers.get(result.level)

        if handler is None:
            raise ValueError(f"No handler for level {result.level}")

        return await handler(prompt)


# Default handlers
async def axiom_handler(prompt: str) -> str:
    """Direct answer for trivial prompts."""
    return await llm.complete(prompt, temperature=0.0)

async def simple_handler(prompt: str) -> str:
    """Single-step reasoning."""
    return await llm.complete(
        f"Think step by step and answer: {prompt}",
        temperature=0.3
    )

async def structured_handler(prompt: str) -> str:
    """Multi-step with verification."""
    reasoning = await llm.complete(
        f"1. Analyze the question.\n2. Reason through it.\n3. Verify your answer.\n\n{prompt}"
    )
    verification = await llm.complete(
        f"Check this reasoning for errors:\n{reasoning}"
    )
    return f"{reasoning}\n\n[Verified: {verification}]"

async def complex_handler(prompt: str) -> str:
    """Decomposition into subtasks."""
    decomposition = await llm.complete(
        f"Break this into 3-5 subtasks:\n{prompt}"
    )
    # Execute subtasks
    subtask_results = []
    for subtask in parse_subtasks(decomposition):
        result = await llm.complete(subtask)
        subtask_results.append(result)

    # Synthesize
    synthesis = await llm.complete(
        f"Synthesize these results:\n{subtask_results}"
    )
    return synthesis

async def expert_handler(prompt: str) -> str:
    """Flag for human review."""
    return f"[EXPERT REQUIRED] Galois loss too high for automated handling.\n\nPrompt: {prompt}"
```

### Effort: 1 week

---

## Proposal G3: Loss Decomposition API

### Theory Basis (Ch 7: Loss as Complexity)

```
Loss decomposes into components:
  L(P) = L_struct(P) + L_semantic(P) + L_ambiguity(P)

Where:
  L_struct: Information lost in restructuring
  L_semantic: Meaning drift in reconstitution
  L_ambiguity: Ambiguity-induced variance
```

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/decomposition.py`

```python
from dataclasses import dataclass

@dataclass
class LossDecomposition:
    """Decomposed Galois Loss."""
    total: float
    structural: float     # From restructuring
    semantic: float       # From reconstitution
    ambiguity: float      # From variance

    explanation: str      # Human-readable explanation
    suggestions: list[str]  # How to reduce loss

@dataclass
class LossDecompositionService:
    """Decomposes Galois Loss into components."""
    loss_computer: 'GaloisLossComputer'

    async def decompose(self, prompt: str, n_samples: int = 5) -> LossDecomposition:
        """Decompose loss into structural, semantic, and ambiguity components."""
        # 1. Compute multiple restructures
        restructures = []
        for _ in range(n_samples):
            r = await self.loss_computer.restructure(prompt)
            restructures.append(r)

        # 2. Structural loss: variance in restructuring
        structural = self._compute_variance(restructures)

        # 3. Semantic loss: distance from original per restructure
        semantic_losses = []
        for r in restructures:
            reconstituted = await self.loss_computer.reconstitute(r)
            semantic_losses.append(
                self.loss_computer.distance(prompt, reconstituted)
            )
        semantic = sum(semantic_losses) / len(semantic_losses)

        # 4. Ambiguity: variance in final losses
        ambiguity = self._compute_variance(semantic_losses)

        # 5. Total
        total = structural + semantic + ambiguity

        # 6. Generate explanation
        explanation = self._explain(structural, semantic, ambiguity)
        suggestions = self._suggest(structural, semantic, ambiguity)

        return LossDecomposition(
            total=total,
            structural=structural,
            semantic=semantic,
            ambiguity=ambiguity,
            explanation=explanation,
            suggestions=suggestions
        )

    def _compute_variance(self, values: list) -> float:
        """Compute variance."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def _explain(self, struct: float, sem: float, amb: float) -> str:
        """Generate human-readable explanation."""
        components = []

        if struct > 0.1:
            components.append(f"High structural loss ({struct:.2f}): The prompt's structure is fragile and loses information when modularized.")

        if sem > 0.1:
            components.append(f"High semantic loss ({sem:.2f}): Meaning drifts significantly during reconstitution.")

        if amb > 0.1:
            components.append(f"High ambiguity ({amb:.2f}): The prompt admits multiple valid interpretations.")

        if not components:
            return "Low loss across all components. Prompt is well-formed."

        return "\n".join(components)

    def _suggest(self, struct: float, sem: float, amb: float) -> list[str]:
        """Suggest how to reduce loss."""
        suggestions = []

        if struct > 0.1:
            suggestions.append("Simplify the prompt structure. Use shorter sentences.")
            suggestions.append("Make implicit assumptions explicit.")

        if sem > 0.1:
            suggestions.append("Use more precise terminology.")
            suggestions.append("Add concrete examples to anchor meaning.")

        if amb > 0.1:
            suggestions.append("Clarify the intended interpretation.")
            suggestions.append("Specify constraints on valid responses.")

        return suggestions
```

### Effort: 2 weeks

---

## Proposal G4: Polynomial Extractor

### Theory Basis (Ch 8: Polynomial Bootstrap)

```
Theorem (Polynomial Bootstrap): If R is a fixed point (R(P) ≈ P), then:
  P determines a polynomial functor P(X) = Σ_{s∈S} X^{A_s} × B_s

Where:
  S = modes discovered in restructuring
  A_s = inputs per mode
  B_s = outputs per mode
```

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/polynomial_extractor.py`

```python
from dataclasses import dataclass
from typing import Set, Dict

@dataclass
class PolynomialSpec:
    """A polynomial functor specification."""
    modes: Set[str]                    # S
    inputs_per_mode: Dict[str, list]   # A_s
    outputs_per_mode: Dict[str, str]   # B_s

    def to_polyagent_config(self) -> dict:
        """Convert to PolyAgent configuration."""
        return {
            "modes": list(self.modes),
            "transitions": {
                mode: {
                    "inputs": self.inputs_per_mode[mode],
                    "output": self.outputs_per_mode[mode]
                }
                for mode in self.modes
            }
        }

@dataclass
class PolynomialExtractor:
    """Extracts polynomial structure from fixed points."""
    loss_computer: 'GaloisLossComputer'
    llm: 'LLMProvider'

    async def extract(self, prompt: str) -> PolynomialSpec:
        """Extract polynomial structure from a fixed-point prompt."""
        # 1. Verify it's a fixed point
        loss = await self.loss_computer.compute(prompt)
        if loss > 0.05:
            raise ValueError(f"Prompt is not a fixed point (L={loss:.3f})")

        # 2. Restructure to discover modes
        restructured = await self.loss_computer.restructure(prompt)

        # 3. Parse modes from restructured form
        modes = await self._extract_modes(restructured)

        # 4. Extract inputs/outputs per mode
        inputs_per_mode = {}
        outputs_per_mode = {}
        for mode in modes:
            inputs_per_mode[mode] = await self._extract_inputs(restructured, mode)
            outputs_per_mode[mode] = await self._extract_output(restructured, mode)

        return PolynomialSpec(
            modes=modes,
            inputs_per_mode=inputs_per_mode,
            outputs_per_mode=outputs_per_mode
        )

    async def _extract_modes(self, restructured: str) -> Set[str]:
        """Extract modes from restructured prompt."""
        response = await self.llm.complete(
            f"List the distinct operational modes in this specification:\n{restructured}\n\nReturn as comma-separated list."
        )
        return set(response.strip().split(", "))

    async def _extract_inputs(self, restructured: str, mode: str) -> list:
        """Extract inputs for a mode."""
        response = await self.llm.complete(
            f"For mode '{mode}' in this specification, list the required inputs:\n{restructured}"
        )
        return response.strip().split("\n")

    async def _extract_output(self, restructured: str, mode: str) -> str:
        """Extract output type for a mode."""
        response = await self.llm.complete(
            f"For mode '{mode}' in this specification, describe the output type:\n{restructured}"
        )
        return response.strip()
```

### Effort: 2 weeks

---

## Proposal G5: TextGRAD Integration

### Theory Basis (Ch 7: Loss as Complexity)

```
TextGRAD: Gradient descent on text using LLM feedback.

Integration:
  1. Compute Galois Loss L(P)
  2. Use L as the loss function
  3. LLM generates "gradient" (improvement direction)
  4. Update P → P' with lower loss
```

### Implementation

**Location**: `impl/claude/services/zero_seed/galois/textgrad.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TextGradResult:
    """Result of TextGRAD optimization."""
    original: str
    optimized: str
    original_loss: float
    final_loss: float
    iterations: int
    trajectory: list[tuple[str, float]]

@dataclass
class TextGradOptimizer:
    """Optimize prompts using Galois Loss as objective."""
    loss_computer: 'GaloisLossComputer'
    llm: 'LLMProvider'
    max_iterations: int = 10
    convergence_threshold: float = 0.01

    async def optimize(self, prompt: str) -> TextGradResult:
        """Optimize prompt to minimize Galois Loss."""
        current = prompt
        current_loss = await self.loss_computer.compute(current)
        trajectory = [(current, current_loss)]

        for i in range(self.max_iterations):
            # Compute "gradient" (improvement direction)
            gradient = await self._compute_gradient(current, current_loss)

            # Apply gradient (generate improved prompt)
            improved = await self._apply_gradient(current, gradient)
            improved_loss = await self.loss_computer.compute(improved)

            trajectory.append((improved, improved_loss))

            # Check convergence
            if abs(improved_loss - current_loss) < self.convergence_threshold:
                break

            # Accept if better
            if improved_loss < current_loss:
                current = improved
                current_loss = improved_loss

        return TextGradResult(
            original=prompt,
            optimized=current,
            original_loss=trajectory[0][1],
            final_loss=current_loss,
            iterations=len(trajectory) - 1,
            trajectory=trajectory
        )

    async def _compute_gradient(self, prompt: str, loss: float) -> str:
        """Compute text gradient (improvement direction)."""
        # Use loss decomposition if available
        decomposition = await self.loss_computer.decompose(prompt)

        return await self.llm.complete(f"""
The following prompt has Galois Loss = {loss:.3f}:

{prompt}

Loss breakdown:
{decomposition.explanation}

Suggestions:
{chr(10).join(decomposition.suggestions)}

Describe how to modify this prompt to reduce information loss while preserving meaning.
Focus on the highest-loss component.
""")

    async def _apply_gradient(self, prompt: str, gradient: str) -> str:
        """Apply gradient to generate improved prompt."""
        return await self.llm.complete(f"""
Original prompt:
{prompt}

Improvement direction:
{gradient}

Rewrite the prompt following the improvement direction.
Preserve the core meaning. Reduce ambiguity and structural complexity.
""")
```

### Effort: 1 week

---

## Implementation Timeline

```
Week 1-3: Calibration Pipeline (G1)
├── Week 1: Corpus infrastructure + seed entries
├── Week 2: Expand corpus to 50+ entries
└── Week 3: Complete to 100+ entries, run correlation analysis

Week 4: Task Triage (G2)
├── Day 1-2: Triage service
├── Day 3-4: Default handlers
└── Day 5: Integration with API

Week 5-6: Loss Decomposition (G3)
├── Week 5: Decomposition algorithm
└── Week 6: Explanation generation

Week 7-8: Polynomial Extractor (G4)
├── Week 7: Mode extraction
└── Week 8: Input/output extraction

Week 9: TextGRAD Integration (G5)
├── Day 1-3: Core optimizer
├── Day 4-5: Integration with decomposition
```

---

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Calibration corpus size | Entry count | 100+ |
| Loss-difficulty correlation | Pearson r | > 0.5 |
| p-value | Statistical test | < 0.05 |
| Domain coverage | Entries per cell | 3+ |
| Triage accuracy | Correct routing | > 80% |
| TextGRAD reduces loss | Before/after | > 20% reduction |

### Go/No-Go Decision Point

**Date**: Week 9 (~2025-01-13, assuming start 2025-12-26)
**Measurement**: Pearson r between computed L(P) and ground-truth D(P)

---

**If correlation < 0.3** (INVALIDATED):

```
PIVOT PLAN — Galois Lite

1. PRESERVE:
   - Fixed-point detection (L < 0.05) for axiom discovery
   - Semantic distance metrics for general similarity
   - Layer assignment via absolute bounds (existing implementation)

2. ABANDON:
   - Loss-based triage (G2) — route by simpler heuristics
   - Loss decomposition (G3) — no actionable signal
   - Polynomial extraction (G4) — no semantic grounding
   - TextGRAD (G5) — no meaningful gradient

3. REPLACE:
   - Task difficulty → Token count + branching factor heuristic
   - Failure prediction → Confidence calibration (logprobs)
   - Loss decomposition → Embedding cluster analysis

4. TIMELINE:
   - Week 9-10: Document pivot rationale, archive G2-G5 proposals
   - Week 11+: Implement Galois Lite (fixed-point only)
```

---

**If correlation 0.3-0.5** (UNCERTAIN):

```
PROCEED WITH CAUTION

1. Add domain-specific calibration (logic vs creative may differ)
2. Increase corpus to 200+ entries for statistical power
3. Consider confounding variables:
   - Prompt length correlating with both L and D
   - Domain-specific biases in semantic distance
4. Run stratified analysis by domain

Decision at Week 12 (~2025-02-03) with expanded corpus.
```

---

**If correlation > 0.5** (VALIDATED):

```
FULL SPEED AHEAD

1. Core bet confirmed: L(P) ∝ D(P)
2. Unlock G2-G5 in parallel:
   - G2: Task Triage (Week 10-11)
   - G3: Loss Decomposition (Week 11-12)
   - G4: Polynomial Extractor (Week 13-14)
   - G5: TextGRAD (Week 15)

3. PUBLISH:
   - "Galois Loss: A Principled Metric for LLM Task Difficulty"
   - Open-source calibration corpus
   - Reproducibility package

4. INTEGRATE:
   - Wire into Zero Seed API
   - Add to Pilots daily lab
   - Enable Personal Constitution auto-layer assignment
```

---

**Decision Criteria Summary**:

| Correlation | Interpretation | Action |
|-------------|----------------|--------|
| r < 0.3 | Hypothesis falsified | Pivot to Galois Lite |
| r = 0.3-0.5 | Weak signal | Expand corpus, retest |
| r > 0.5 | Hypothesis validated | Full G2-G5 unlock |
| r > 0.7 | Strong validation | Prioritize publication |

---

## Dependencies

- **Upstream**: None (foundational)
- **Downstream**: All pilots, DP layer, Co-Engineering layer
- **Pilot Integration**: wasm-survivors (Week 2), trail-to-crystal (Week 6)

---

**Document Metadata**
- **Lines**: ~1100
- **Theory Chapters**: 6-8
- **Proposals**: G1-G5 (G4-G5 DEFERRED)
- **Effort**: 3 weeks (G1 only), 8-9 weeks (full)
- **Priority**: **CRITICAL PATH**
- **Last Updated**: 2025-12-26
- **Key Insight**: All core infrastructure EXISTS. G1 is pure execution, no blockers.
