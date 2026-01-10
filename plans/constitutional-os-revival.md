# Constitutional Decision OS Revival Plan

> *"Every action justifies itself. Every mark carries its constitutional signature."*

**Status**: ✅ IMPLEMENTED (2025-01-10)
**Date**: 2025-01-10
**Priority**: P0 (Critical Path)
**Scope**: Constitutional evaluation, Galois integration, trust computation
**Related**: `coherence-synthesis-master.md`, `zero-seed-integration.md`

---

## Executive Summary

The Constitutional Decision OS is **implemented but fragmented**. The core `MarkConstitutionalEvaluator` exists and works, but key features are missing or archived. This plan revives the full vision by connecting the evaluator to Galois loss and implementing trust computation.

### Current State

| Component | Location | Status |
|-----------|----------|--------|
| Constitutional Evaluator | `services/witness/constitutional_evaluator.py` | Active, 320 lines |
| Constitution | `services/categorical/constitution.py` | Active |
| Trust Computer | - | Not implemented |
| Galois Integration | - | `galois_loss=None` always |
| Archived Synthesis | `plans/_archive/constitutional-decision-os-synthesis.md` | Archived |
| Archived Brainstorm | `brainstorming/_archive/constitutional-decision-os.md` | Archived |

### The Gap

```python
# CURRENT (constitutional_evaluator.py line 231-236)
return ConstitutionalAlignment.from_scores(
    principle_scores=principle_scores,
    galois_loss=None,  # ← ALWAYS NONE
    tier=tier,
    threshold=self.threshold,
)

# NEEDED
galois = await self.galois_service.compute(mark)
return ConstitutionalAlignment.from_scores(
    principle_scores=principle_scores,
    galois_loss=galois.total,  # ← COMPUTED
    tier=self._tier_from_galois(galois),
    threshold=self.threshold,
)
```

---

## Part I: The Seven Principles — ETHICAL as Gate

The Constitutional OS evaluates actions against seven principles. **ETHICAL is a GATE, not a weight** (Amendment A).

### Amendment A: The Ethical Floor Constraint

> *"You cannot offset unethical behavior with composability or joy."*

ETHICAL operates as a **hard constraint** (pass/fail), not a weighted score:

```python
ETHICAL_FLOOR_THRESHOLD = 0.6  # Must pass this threshold

# If ETHICAL < 0.6 → IMMEDIATE REJECTION
# Regardless of how high other scores are
```

**Why a gate, not a weight?**
- **Goodhart's Law**: Weighted ethics invites finding "optimal harm" where benefit exceeds cost
- **Lexicographic Preferences**: Safety occupies an incomparable tier (no tradeoffs allowed)
- **Article IV (Disgust Veto)**: "Absolute veto...cannot be argued away"
- **Anthropic's Approach**: Constitutional Classifiers use hard gates (95% block rate)

### The Principle Evaluation Table

| Principle | Type | Threshold/Weight | Rationale |
|-----------|------|------------------|-----------|
| **ETHICAL** | **GATE** | ≥ 0.6 or REJECT | Safety floor. Non-negotiable. Article IV. |
| **COMPOSABLE** | Weight | 1.5 | Architecture second. Category laws must hold. |
| **JOY_INDUCING** | Weight | 1.2 | Kent's aesthetic. The Mirror Test. |
| **TASTEFUL** | Weight | 1.0 | Clarity and intentionality. |
| **CURATED** | Weight | 1.0 | Unique value over sprawl. |
| **HETERARCHICAL** | Weight | 1.0 | Flexibility over rigid hierarchy. |
| **GENERATIVE** | Weight | 1.0 | Regenerability. Spec as seed. |

### Evaluation Flow

```
1. Compute ETHICAL score
2. IF ETHICAL < 0.6 → REJECT (no further evaluation)
3. ELSE → Compute weighted sum of other 6 principles
4. Return: weighted_total / max_possible (normalized to [0,1])
```

### Weight Derivation (Non-ETHICAL Principles)

```
COMPOSABLE is weighted 1.5 because:
- It's the architectural foundation
- Category laws must hold (L2.5 COMPOSABLE)
- Without composition, no structure can grow

JOY_INDUCING is weighted 1.2 because:
- Kent's aesthetic signature
- "Daring, bold, creative, opinionated but not gaudy"
- The Mirror Test lives here

Max weighted sum (after ETHICAL passes): 1.5 + 1.2 + 1.0×4 = 6.7
```

---

## Part II: Galois Integration

### 2.1 Modified Evaluator

```python
# File: impl/claude/services/witness/constitutional_evaluator.py (modifications)

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

from services.categorical.constitution import Constitution, ConstitutionalEvaluation, Principle
from services.galois.service import GaloisLossService
from services.galois.types import GaloisLoss
from services.witness.mark import ConstitutionalAlignment, Mark

logger = logging.getLogger("kgents.witness.constitutional_evaluator")


@dataclass
class MarkConstitutionalEvaluator:
    """
    Evaluate marks against the 7 constitutional principles.

    UPDATED: Now integrates Galois loss computation.

    The Unifying Equation:
        R_constitutional = 1 - L_galois

    This means constitutional reward and Galois loss are duals.
    High constitutional compliance implies low structure loss.
    """

    threshold: float = 0.5
    include_galois: bool = True  # NEW: Default True
    galois_service: GaloisLossService | None = None  # NEW: Injected

    def __post_init__(self):
        """Initialize Galois service if not provided."""
        if self.include_galois and self.galois_service is None:
            from services.providers import get_galois_service
            self.galois_service = get_galois_service()

    async def evaluate(self, mark: Mark) -> ConstitutionalAlignment:
        """
        Evaluate a mark against constitutional principles.

        Now async because Galois computation may be async.

        Args:
            mark: The mark to evaluate

        Returns:
            ConstitutionalAlignment with principle scores AND galois_loss
        """
        # Existing evaluation
        alignment = self.evaluate_sync(mark)

        # Add Galois loss if enabled
        if self.include_galois and self.galois_service:
            galois = await self.galois_service.compute(mark)
            return self._enrich_with_galois(alignment, galois, mark)

        return alignment

    def _enrich_with_galois(
        self,
        alignment: ConstitutionalAlignment,
        galois: GaloisLoss,
        mark: Mark,
    ) -> ConstitutionalAlignment:
        """
        Create new alignment enriched with Galois data.

        The Duality:
            - High principle scores + low Galois loss = coherent action
            - Low principle scores + high Galois loss = incoherent action
            - Mismatch = something interesting happening
        """
        # Verify duality (for monitoring)
        expected_coherence = 1.0 - galois.total
        actual_coherence = alignment.weighted_total / max_possible_score()

        if abs(expected_coherence - actual_coherence) > 0.3:
            logger.warning(
                f"Coherence mismatch: Galois expects {expected_coherence:.2f}, "
                f"Constitution got {actual_coherence:.2f}"
            )

        return ConstitutionalAlignment.from_scores(
            principle_scores=alignment.principle_scores,
            galois_loss=galois.total,
            tier=self._tier_from_galois(galois),
            threshold=self.threshold,
        )

    def _tier_from_galois(self, galois: GaloisLoss) -> str:
        """
        Map Galois loss to evidence tier.

        Lower loss = higher confidence = stricter tier.

        Kent-calibrated thresholds (2025-12-28):
            CATEGORICAL: L < 0.10 (axiom-level, fixed point)
            EMPIRICAL:   L < 0.38 (strong empirical evidence)
            AESTHETIC:   L < 0.45 (Kent sees derivation paths)
            SOMATIC:     L < 0.65 (felt sense, Mirror test)
            CHAOTIC:     L >= 0.65 (high loss, low confidence)
        """
        if galois.total < 0.10:
            return "CATEGORICAL"
        elif galois.total < 0.38:
            return "EMPIRICAL"
        elif galois.total < 0.45:
            return "AESTHETIC"
        elif galois.total < 0.65:
            return "SOMATIC"
        else:
            return "CHAOTIC"

    # ... rest of existing methods unchanged ...


def max_possible_score() -> float:
    """
    Maximum possible weighted score across non-ETHICAL principles.

    Note: ETHICAL is a GATE (≥0.6 floor), not included in weighted sum.
    Per Amendment A, ETHICAL is evaluated first as pass/fail.
    """
    weights = {
        # ETHICAL is NOT weighted - it's a floor constraint (Amendment A)
        "COMPOSABLE": 1.5,
        "JOY_INDUCING": 1.2,
        "TASTEFUL": 1.0,
        "CURATED": 1.0,
        "HETERARCHICAL": 1.0,
        "GENERATIVE": 1.0,
    }
    return sum(weights.values())  # 6.7
```

### 2.2 Context Enrichment for Galois

The `_build_context` method should include Galois-relevant flags:

```python
def _build_context(self, mark: Mark) -> dict[str, Any]:
    """
    Build evaluation context from mark metadata.

    NEW: Adds Galois-relevant context flags.
    """
    context = dict(mark.metadata)

    # Existing context...
    context["trust_level"] = mark.umwelt.trust_level
    context["capabilities"] = list(mark.umwelt.capabilities)
    # ... etc ...

    # NEW: Galois-relevant flags
    # These affect how Constitution.evaluate() scores principles

    # GENERATIVE: Does this mark have regenerability potential?
    context.setdefault("has_spec", bool(mark.proof and mark.proof.backing))
    context.setdefault("is_regenerable", mark.metadata.get("regenerable", True))

    # COMPOSABLE: Does this mark satisfy category laws?
    context.setdefault("satisfies_identity", True)  # Assume unless proven otherwise
    context.setdefault("satisfies_associativity", True)

    # JOY_INDUCING: Is this delightful?
    context.setdefault("joyful", "joy" in mark.tags or "delight" in mark.tags)
    context.setdefault("mirror_test_passed", mark.metadata.get("mirror_test", None))

    # ETHICAL: Harm assessment
    context.setdefault("preserves_human_agency", mark.umwelt.trust_level < 3)
    context.setdefault("transparent", not mark.metadata.get("hidden", False))
    context.setdefault("reversible", mark.metadata.get("reversible", True))

    return context
```

---

## Part III: Trust Computation

### 3.1 Trust Level Theory

From the Emerging Constitution (Article V):

> **TRUST ACCUMULATION**: Trust is earned through demonstrated alignment.
> Trust is lost through demonstrated misalignment.
> Trust level determines scope of permitted supersession.

Trust levels map to autonomy (L0-L3 system, matching implementation):

| Level | Name | Constitutional Criteria | Autonomy |
|-------|------|------------------------|----------|
| L0 | READ_ONLY | No history / default | Full human oversight required |
| L1 | BOUNDED | avg_alignment ≥ 0.6, violation_rate < 0.1 | Write to .kgents/ only |
| L2 | SUGGESTION | avg_alignment ≥ 0.8, violation_rate < 0.05 | Can suggest changes |
| L3 | AUTONOMOUS | avg_alignment ≥ 0.9, violation_rate < 0.02 | Most actions auto-approved |

### 3.2 Trust Computer Implementation

```python
# File: impl/claude/services/witness/trust_computer.py

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from services.witness.mark import ConstitutionalAlignment, Mark

logger = logging.getLogger("kgents.witness.trust_computer")


@dataclass(frozen=True)
class TrustLevel:
    """Computed trust level with justification."""

    level: int  # 0-3 (L0-L3)
    name: str  # READ_ONLY, BOUNDED, SUGGESTION, AUTONOMOUS
    confidence: float  # How confident in this level
    mark_count: int
    avg_alignment: float
    trend: str  # "rising", "stable", "falling"
    justification: str


@dataclass
class ConstitutionalTrustComputer:
    """
    Compute trust level from accumulated marks.

    Philosophy:
        "Trust is earned through demonstrated alignment."

    The trust equation:
        T = f(avg_alignment, consistency, recency, volume)

    Where:
        - avg_alignment: Mean constitutional alignment across marks
        - consistency: Variance of alignment (low = consistent = higher trust)
        - recency: Recent marks weighted more heavily
        - volume: More marks = more confidence in trust level
    """

    # Weights for trust computation
    alignment_weight: float = 0.4
    consistency_weight: float = 0.3
    recency_weight: float = 0.2
    volume_weight: float = 0.1

    # Thresholds for trust levels
    level_thresholds: dict[int, float] = None

    def __post_init__(self):
        if self.level_thresholds is None:
            # L0-L3 thresholds matching constitutional_trust.py
            self.level_thresholds = {
                1: 0.6,   # L1 BOUNDED: avg alignment >= 0.6
                2: 0.8,   # L2 SUGGESTION: avg alignment >= 0.8
                3: 0.9,   # L3 AUTONOMOUS: avg alignment >= 0.9
            }

    async def compute(
        self,
        marks: Sequence[Mark],
        lookback_days: int = 30,
    ) -> TrustLevel:
        """
        Compute trust level from a sequence of marks.

        Args:
            marks: Marks to analyze
            lookback_days: Only consider marks from this many days ago

        Returns:
            TrustLevel with computed level and justification
        """
        if not marks:
            return TrustLevel(
                level=0,
                name="UNTRUSTED",
                confidence=1.0,
                mark_count=0,
                avg_alignment=0.0,
                trend="stable",
                justification="No marks to evaluate",
            )

        # Filter to lookback period
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        recent_marks = [m for m in marks if m.timestamp >= cutoff]

        if not recent_marks:
            return TrustLevel(
                level=0,
                name="UNTRUSTED",
                confidence=0.5,
                mark_count=len(marks),
                avg_alignment=0.0,
                trend="falling",
                justification=f"No marks in last {lookback_days} days",
            )

        # Compute components
        avg_alignment = self._compute_avg_alignment(recent_marks)
        consistency = self._compute_consistency(recent_marks)
        recency_score = self._compute_recency_score(recent_marks)
        volume_score = self._compute_volume_score(len(recent_marks))

        # Weighted trust score
        trust_score = (
            avg_alignment * self.alignment_weight +
            consistency * self.consistency_weight +
            recency_score * self.recency_weight +
            volume_score * self.volume_weight
        )

        # Map to level (L0-L3)
        level = self._score_to_level(trust_score)
        name = self._level_name(level)

        # Compute trend
        trend = self._compute_trend(recent_marks)

        # Compute confidence (more marks = more confident)
        confidence = min(1.0, len(recent_marks) / 20)

        return TrustLevel(
            level=level,
            name=name,
            confidence=confidence,
            mark_count=len(recent_marks),
            avg_alignment=avg_alignment,
            trend=trend,
            justification=self._build_justification(
                avg_alignment, consistency, trend, len(recent_marks)
            ),
        )

    def _compute_avg_alignment(self, marks: Sequence[Mark]) -> float:
        """Compute average constitutional alignment."""
        alignments = [
            m.constitutional.weighted_total
            for m in marks
            if m.constitutional
        ]
        return sum(alignments) / len(alignments) if alignments else 0.0

    def _compute_consistency(self, marks: Sequence[Mark]) -> float:
        """
        Compute consistency score (inverse variance).

        Low variance = consistent = high score.
        """
        alignments = [
            m.constitutional.weighted_total
            for m in marks
            if m.constitutional
        ]
        if len(alignments) < 2:
            return 1.0  # Not enough data, assume consistent

        mean = sum(alignments) / len(alignments)
        variance = sum((a - mean) ** 2 for a in alignments) / len(alignments)

        # Convert variance to [0, 1] score (lower variance = higher score)
        return 1.0 / (1.0 + variance * 10)

    def _compute_recency_score(self, marks: Sequence[Mark]) -> float:
        """
        Compute recency-weighted alignment.

        More recent marks weighted more heavily.
        """
        if not marks:
            return 0.0

        now = datetime.now(timezone.utc)
        weighted_sum = 0.0
        weight_total = 0.0

        for mark in marks:
            if not mark.constitutional:
                continue

            age_days = (now - mark.timestamp).days + 1
            weight = 1.0 / age_days  # More recent = higher weight
            weighted_sum += mark.constitutional.weighted_total * weight
            weight_total += weight

        return weighted_sum / weight_total if weight_total > 0 else 0.0

    def _compute_volume_score(self, count: int) -> float:
        """
        Compute volume score.

        More marks = more confidence, with diminishing returns.
        """
        return min(1.0, count / 50)  # Saturates at 50 marks

    def _score_to_level(self, score: float) -> int:
        """Map trust score to level L0-L3."""
        for level in [3, 2, 1]:
            if score >= self.level_thresholds[level]:
                return level
        return 0

    def _level_name(self, level: int) -> str:
        """Get name for trust level (L0-L3 system)."""
        names = {
            0: "READ_ONLY",
            1: "BOUNDED",
            2: "SUGGESTION",
            3: "AUTONOMOUS",
        }
        return names.get(level, "UNKNOWN")

    def _compute_trend(self, marks: Sequence[Mark]) -> str:
        """Determine if trust is rising, stable, or falling."""
        if len(marks) < 5:
            return "stable"

        # Split into halves
        mid = len(marks) // 2
        older = marks[:mid]
        newer = marks[mid:]

        older_avg = self._compute_avg_alignment(older)
        newer_avg = self._compute_avg_alignment(newer)

        delta = newer_avg - older_avg
        if delta > 0.1:
            return "rising"
        elif delta < -0.1:
            return "falling"
        else:
            return "stable"

    def _build_justification(
        self,
        avg_alignment: float,
        consistency: float,
        trend: str,
        count: int,
    ) -> str:
        """Build human-readable justification."""
        parts = [
            f"Avg alignment: {avg_alignment:.2f}",
            f"Consistency: {consistency:.2f}",
            f"Trend: {trend}",
            f"Marks: {count}",
        ]
        return " | ".join(parts)
```

### 3.3 Trust-Gated Actions

```python
# File: impl/claude/services/witness/trust_gating.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionScope(Enum):
    """Scopes of actions requiring different trust levels."""

    ROUTINE = "routine"      # Read, list, query
    STANDARD = "standard"    # Create, update
    COMPLEX = "complex"      # Delete, refactor, multi-step
    STRATEGIC = "strategic"  # Architecture, policy


TRUST_REQUIREMENTS = {
    ActionScope.ROUTINE: 0,    # Any trust level
    ActionScope.STANDARD: 2,   # TRUSTED or higher
    ActionScope.COMPLEX: 3,    # ALIGNED or higher
    ActionScope.STRATEGIC: 4,  # SYMBIOTIC only
}


@dataclass
class TrustGate:
    """Gate actions based on trust level."""

    required_level: int

    def allows(self, current_level: int) -> bool:
        """Check if current trust level permits action."""
        return current_level >= self.required_level

    def denial_reason(self, current_level: int) -> str:
        """Explain why action was denied."""
        return (
            f"Action requires trust level {self.required_level}, "
            f"but current level is {current_level}. "
            f"Build trust through consistent aligned actions."
        )


def gate_for_scope(scope: ActionScope) -> TrustGate:
    """Get the trust gate for an action scope."""
    return TrustGate(required_level=TRUST_REQUIREMENTS[scope])
```

---

## Part IV: Constitutional Reactor Integration

### 4.1 Updated Reactor Flow

```python
# File: impl/claude/services/witness/reactor.py (modifications)

class ConstitutionalMarkReactor:
    """
    React to marks by computing constitutional alignment.

    UPDATED: Now computes Galois loss and updates trust.
    """

    def __init__(
        self,
        evaluator: MarkConstitutionalEvaluator,
        trust_computer: ConstitutionalTrustComputer,
        mark_store: MarkStore,
    ):
        self.evaluator = evaluator
        self.trust_computer = trust_computer
        self.mark_store = mark_store

    async def react(self, mark: Mark) -> Mark:
        """
        React to a mark by:
        1. Computing constitutional alignment (with Galois)
        2. Enriching the mark
        3. Updating trust level

        Returns enriched mark.
        """
        # 1. Compute alignment (now includes Galois)
        alignment = await self.evaluator.evaluate(mark)

        # 2. Enrich mark
        enriched = mark.with_constitutional(alignment)

        # 3. Update trust (async, background)
        await self._update_trust(enriched)

        return enriched

    async def _update_trust(self, mark: Mark) -> None:
        """Update trust level based on new mark."""
        # Get recent marks for this domain
        recent_marks = await self.mark_store.get_recent(
            domain=mark.domain,
            limit=50,
        )

        # Compute new trust level
        trust = await self.trust_computer.compute(recent_marks)

        # Store trust level (could emit event)
        logger.info(
            f"Trust updated: {trust.name} (level {trust.level}), "
            f"trend: {trust.trend}"
        )
```

---

## Part V: API Integration

### 5.1 API Endpoints

```python
# File: impl/claude/protocols/api/constitutional.py

from fastapi import APIRouter, Depends

from services.witness.constitutional_evaluator import MarkConstitutionalEvaluator
from services.witness.trust_computer import ConstitutionalTrustComputer, TrustLevel

router = APIRouter(prefix="/api/constitutional", tags=["constitutional"])


@router.post("/evaluate")
async def evaluate_mark(
    mark_id: str,
    evaluator: MarkConstitutionalEvaluator = Depends(get_evaluator),
) -> dict:
    """Evaluate a mark against constitutional principles."""
    mark = await get_mark(mark_id)
    alignment = await evaluator.evaluate(mark)

    return {
        "mark_id": mark_id,
        "weighted_total": alignment.weighted_total,
        "galois_loss": alignment.galois_loss,
        "tier": alignment.tier,
        "is_compliant": alignment.is_compliant,
        "principle_scores": alignment.principle_scores,
    }


@router.get("/trust")
async def get_trust_level(
    domain: str = "default",
    trust_computer: ConstitutionalTrustComputer = Depends(get_trust_computer),
) -> dict:
    """Get current trust level for a domain."""
    marks = await get_marks_for_domain(domain)
    trust = await trust_computer.compute(marks)

    return {
        "domain": domain,
        "level": trust.level,
        "name": trust.name,
        "confidence": trust.confidence,
        "avg_alignment": trust.avg_alignment,
        "trend": trust.trend,
        "justification": trust.justification,
    }


@router.get("/coherence")
async def check_coherence() -> dict:
    """
    Check coherence: R_constitutional ≈ 1 - L_galois?

    This endpoint verifies the unifying equation.
    """
    # Sample recent marks
    marks = await get_recent_marks(limit=100)

    correlations = []
    for mark in marks:
        if mark.constitutional and mark.constitutional.galois_loss is not None:
            r = mark.constitutional.weighted_total / 6.7  # Normalize (max of non-ETHICAL weights)
            l = mark.constitutional.galois_loss
            expected = 1 - l
            correlations.append((r, expected))

    if not correlations:
        return {"status": "no_data", "correlation": None}

    # Compute Pearson correlation
    correlation = compute_correlation(correlations)

    return {
        "status": "ok" if correlation > 0.8 else "drift",
        "correlation": correlation,
        "sample_size": len(correlations),
        "expected_relationship": "R ≈ 1 - L",
    }
```

---

## Part VI: Implementation Roadmap

### Phase 1: Galois Integration (Days 1-2)

| Task | File | Status |
|------|------|--------|
| Add `galois_service` to evaluator | `constitutional_evaluator.py` | Modify |
| Implement `evaluate_with_galois` | `constitutional_evaluator.py` | Add |
| Update `_tier_from_galois` | `constitutional_evaluator.py` | Add |
| Unit tests | `_tests/test_constitutional_galois.py` | New |

### Phase 2: Trust Computation (Days 3-4)

| Task | File | Status |
|------|------|--------|
| TrustLevel type | `trust_computer.py` | New |
| ConstitutionalTrustComputer | `trust_computer.py` | New |
| Trust gating | `trust_gating.py` | New |
| Unit tests | `_tests/test_trust.py` | New |

### Phase 3: Integration (Day 5)

| Task | File | Status |
|------|------|--------|
| Reactor update | `reactor.py` | Modify |
| API endpoints | `protocols/api/constitutional.py` | New |
| Integration tests | `_tests/test_constitutional_integration.py` | New |

---

## Part VII: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Galois coverage | 100% | No marks with `galois_loss=None` |
| R ≈ 1 - L correlation | ρ > 0.80 | `/api/constitutional/coherence` |
| Trust computation latency | < 50ms | Profiling |
| Trust accuracy | Manual validation | Kent review |

---

## Appendix: The Seven Principles Reference

From `spec/principles.md`:

| # | Principle | Statement | Type |
|---|-----------|-----------|------|
| 1 | TASTEFUL | Each agent serves a clear, justified purpose | Weight 1.0 |
| 2 | CURATED | Intentional selection over exhaustive cataloging | Weight 1.0 |
| 3 | **ETHICAL** | Agents augment capability, never replace judgment | **GATE ≥0.6** |
| 4 | JOY_INDUCING | Delight in interaction; personality matters | Weight 1.2 |
| 5 | COMPOSABLE | Agents are morphisms; composition is primary | Weight 1.5 |
| 6 | HETERARCHICAL | Flux not hierarchy; autonomy and composability coexist | Weight 1.0 |
| 7 | GENERATIVE | Spec is compression; design generates implementation | Weight 1.0 |

**Note**: ETHICAL is a **gate**, not a weight. It must pass ≥0.6 threshold before other principles are evaluated. See Amendment A.

---

*"Trust is earned through demonstrated alignment. Trust is lost through demonstrated misalignment."*
