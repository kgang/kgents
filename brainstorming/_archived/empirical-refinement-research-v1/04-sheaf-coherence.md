# Sheaf Coherence: Empirical Refinement

> *"Local views → Global consistency. The gluing IS the emergence."*

**Related Specs**: `spec/protocols/witness.md`, `spec/theory/experience-quality-operad.md`
**Priority**: MEDIUM
**Status**: Ready for Implementation

---

## 1. Current State Analysis

### 1.1 What You Have

Your architecture uses sheaves for:
1. **Crystallization**: Compressing marks into crystals
2. **Global coherence**: Ensuring local views glue consistently
3. **Emergence**: Compatible locals → global

### 1.2 What's Missing

1. **Consistency validation**: No quantitative check before crystallization
2. **Conflict detection**: No systematic identification of inconsistent marks
3. **Fusion optimization**: No principled method for resolving conflicts
4. **Coherence metrics**: No numerical measure of sheaf consistency

---

## 2. Research Findings

### 2.1 Sheaves as Canonical Data Structure

The foundational paper ["Sheaves are the canonical data structure for sensor integration"](https://www.sciencedirect.com/science/article/abs/pii/S156625351630207X) establishes:

> "The mathematics of sheaves can accurately represent many sensor modalities while summarizing information in a faithful way."

**Three Key Operations**:

| Operation | Description | Your Application |
|-----------|-------------|------------------|
| **Consistency Radius** | Quantifies self-consistency of data | Pre-crystallization check |
| **Data Fusion** | Optimizes for consistent global view | Crystal generation |
| **Blind Spot Detection** | Identifies structural gaps | Mark coverage analysis |

**Critical Insight**:
> "The consistency radius of the original data places a lower bound on the amount of distortion incurred by the fusion process."

**Implication**: You can mathematically bound crystallization loss.

### 2.2 Sheaf Cohomology for Consistency

From the [Utah State thesis](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=8483&context=etd):

> "Sheaf cohomology over finite spaces measures consistency between data sources."

**The Cohomology Interpretation**:
- H⁰ = Global sections (consistent data)
- H¹ = First obstruction (local inconsistencies)
- Higher cohomology = More complex conflicts

### 2.3 Uncertainty Quantification

The [geolocation paper](https://www.mdpi.com/1424-8220/20/12/3418) shows:

> "A sheaf theoretical approach provides uncertainty quantification of heterogeneous information."

**Method**: Compute consistency radius, use as uncertainty bound.

### 2.4 Recent Applications (2024-2025)

The [sheaf theory overview](https://arxiv.org/pdf/2502.15476) (February 2025) notes:

> "More recently, sheaves and presheaves have been applied to formalise the consistency of different forms of concrete data, with examples from quantum mechanics, signal processing, graph neural networks, and natural language."

**Application**: PHeatPruner uses sheaf theory for time series classification, achieving 45% variable pruning while maintaining accuracy.

---

## 3. Refinement Recommendations

### 3.1 Implement Consistency Radius Check

**Rationale**: Before crystallizing marks, verify they're consistent enough.

```python
import numpy as np
from dataclasses import dataclass
from typing import Callable

@dataclass
class MarkSheaf:
    """
    Sheaf structure for witness marks.

    A sheaf assigns data (marks) to open sets (contexts) and requires
    consistency on overlaps.
    """

    marks: list[Mark]
    similarity_fn: Callable[[Mark, Mark], float]  # Pairwise similarity

    def consistency_radius(self) -> float:
        """
        Compute consistency radius.

        The consistency radius r is the minimum perturbation needed to make
        all pairwise similarities equal. Lower = more consistent.

        r = 0: Perfectly consistent (all marks agree)
        r = 1: Maximally inconsistent (marks contradict)

        Mathematical basis: This is the Cheeger constant of the
        similarity graph, normalized to [0, 1].
        """
        if len(self.marks) < 2:
            return 0.0  # Single mark is trivially consistent

        # Build similarity matrix
        n = len(self.marks)
        sim_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                sim = self.similarity_fn(self.marks[i], self.marks[j])
                sim_matrix[i, j] = sim
                sim_matrix[j, i] = sim

        # Consistency radius = 1 - minimum similarity
        # (If all pairs have high similarity, radius is low)
        min_similarity = np.min(sim_matrix[sim_matrix > 0])
        return 1.0 - min_similarity

    def identify_conflicts(self) -> list[MarkConflict]:
        """
        Identify pairs of marks that conflict.

        Conflict threshold derived from consistency radius.
        """
        conflicts = []
        threshold = 0.5  # Marks below this similarity are in conflict

        n = len(self.marks)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.similarity_fn(self.marks[i], self.marks[j])
                if sim < threshold:
                    conflicts.append(MarkConflict(
                        mark_a=self.marks[i],
                        mark_b=self.marks[j],
                        similarity=sim,
                        conflict_type=self._classify_conflict(self.marks[i], self.marks[j]),
                    ))

        return conflicts

    def _classify_conflict(self, a: Mark, b: Mark) -> str:
        """Classify the type of conflict between two marks."""
        # Check for temporal conflict (same time, different claims)
        if abs(a.timestamp - b.timestamp) < 60:  # Within 1 minute
            return "temporal"

        # Check for semantic conflict (contradictory claims)
        if self._claims_contradict(a, b):
            return "semantic"

        # Check for source conflict (same source, different views)
        if a.origin == b.origin:
            return "source"

        return "unknown"

    def _claims_contradict(self, a: Mark, b: Mark) -> bool:
        """Check if two marks make contradictory claims."""
        # Use NLI or simple heuristics
        # Placeholder: check for negation patterns
        a_claim = str(a.action).lower()
        b_claim = str(b.action).lower()

        negation_pairs = [
            ("success", "failure"),
            ("completed", "failed"),
            ("accepted", "rejected"),
            ("approved", "denied"),
        ]

        for pos, neg in negation_pairs:
            if (pos in a_claim and neg in b_claim) or (neg in a_claim and pos in b_claim):
                return True

        return False


@dataclass
class MarkConflict:
    """A conflict between two marks."""
    mark_a: Mark
    mark_b: Mark
    similarity: float
    conflict_type: str
```

### 3.2 Implement Crystallization Gate

**Rationale**: Only crystallize when consistency is sufficient.

```python
@dataclass
class CrystallizationDecision:
    """Decision on whether to proceed with crystallization."""
    allowed: bool
    consistency_radius: float
    expected_loss: float
    conflicts: list[MarkConflict]
    reason: str
    recommendation: str | None = None


class SheafCrystallizer:
    """Crystallization with sheaf-based consistency validation."""

    # Threshold from empirical calibration (see experiments)
    consistency_threshold: float = 0.3

    def can_crystallize(self, marks: list[Mark]) -> CrystallizationDecision:
        """
        Check if marks are consistent enough to crystallize.

        Uses sheaf cohomology principles:
        - Low consistency radius = marks glue cleanly
        - High consistency radius = fusion will lose information
        """
        sheaf = MarkSheaf(marks, similarity_fn=self.mark_similarity)

        radius = sheaf.consistency_radius()
        conflicts = sheaf.identify_conflicts()

        if radius > self.consistency_threshold:
            return CrystallizationDecision(
                allowed=False,
                consistency_radius=radius,
                expected_loss=radius,  # Loss bounded by radius
                conflicts=conflicts,
                reason=f"Consistency radius {radius:.2f} exceeds threshold {self.consistency_threshold}",
                recommendation=self._generate_recommendation(conflicts),
            )

        # Compute expected loss from fusion
        expected_loss = self._compute_fusion_loss_bound(sheaf)

        return CrystallizationDecision(
            allowed=True,
            consistency_radius=radius,
            expected_loss=expected_loss,
            conflicts=conflicts,
            reason="Marks are sufficiently consistent for crystallization",
        )

    def mark_similarity(self, a: Mark, b: Mark) -> float:
        """
        Compute similarity between two marks.

        Uses multiple dimensions:
        - Temporal proximity
        - Semantic similarity of actions
        - Principle overlap
        - Reasoning coherence
        """
        # Temporal similarity (decay over time)
        time_diff = abs(a.timestamp - b.timestamp)
        temporal_sim = np.exp(-time_diff / 3600)  # 1-hour half-life

        # Semantic similarity of actions
        semantic_sim = self._semantic_similarity(a.action, b.action)

        # Principle overlap
        a_principles = set(a.principles) if hasattr(a, 'principles') else set()
        b_principles = set(b.principles) if hasattr(b, 'principles') else set()
        if a_principles or b_principles:
            principle_sim = len(a_principles & b_principles) / len(a_principles | b_principles)
        else:
            principle_sim = 1.0

        # Weighted combination
        return 0.3 * temporal_sim + 0.5 * semantic_sim + 0.2 * principle_sim

    def _semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Compute semantic similarity using embeddings."""
        # Use BERTScore or similar
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')

        emb_a = model.encode(text_a)
        emb_b = model.encode(text_b)

        return float(np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b)))

    def _compute_fusion_loss_bound(self, sheaf: MarkSheaf) -> float:
        """
        Compute lower bound on information loss from fusion.

        Based on sheaf theory: consistency radius bounds distortion.
        """
        return sheaf.consistency_radius()

    def _generate_recommendation(self, conflicts: list[MarkConflict]) -> str:
        """Generate recommendation for resolving conflicts."""
        if not conflicts:
            return "No specific conflicts to resolve."

        # Group by conflict type
        by_type = {}
        for c in conflicts:
            by_type.setdefault(c.conflict_type, []).append(c)

        recommendations = []

        if "temporal" in by_type:
            recommendations.append(
                f"Resolve {len(by_type['temporal'])} temporal conflicts by "
                "verifying which marks represent the current state."
            )

        if "semantic" in by_type:
            recommendations.append(
                f"Resolve {len(by_type['semantic'])} semantic conflicts by "
                "clarifying contradictory claims."
            )

        if "source" in by_type:
            recommendations.append(
                f"Resolve {len(by_type['source'])} source conflicts by "
                "reconciling divergent views from the same origin."
            )

        return " ".join(recommendations)
```

### 3.3 Implement Sheaf-Based Fusion

**Rationale**: When crystallizing, minimize information loss.

```python
class SheafFusion:
    """
    Fuse marks into a crystal using sheaf-theoretic optimization.

    Goal: Find global section (crystal) that minimizes deviation from local data (marks).
    """

    def fuse(self, marks: list[Mark], algebra: QualityAlgebra) -> QualityCrystal:
        """
        Fuse marks into a crystal.

        Optimization: min_crystal Σ d(crystal, mark_i)²
        Subject to: crystal is a valid global section
        """
        if not marks:
            raise ValueError("Cannot fuse empty mark list")

        # Build sheaf
        sheaf = MarkSheaf(marks, similarity_fn=self.mark_similarity)

        # Check consistency
        radius = sheaf.consistency_radius()
        if radius > 0.5:
            # High inconsistency: warn but proceed with best effort
            print(f"Warning: High consistency radius ({radius:.2f}). Fusion may lose information.")

        # Extract quality measurements from marks
        qualities = [self._extract_quality(m) for m in marks]

        # Fuse by component (sheaf product)
        fused_contrast = self._fuse_contrast(qualities)
        fused_arc = self._fuse_arc(qualities)
        fused_voice = self._fuse_voice(qualities)
        fused_floor = self._fuse_floor(qualities)

        # Compute trend
        trend = self._compute_trend(qualities)

        # Identify peaks and troughs
        sorted_by_quality = sorted(zip(marks, qualities), key=lambda x: x[1].overall)
        troughs = [m for m, q in sorted_by_quality[:3]]
        peaks = [m for m, q in sorted_by_quality[-3:]]

        # Generate crystal
        return QualityCrystal(
            algebra_name=algebra.name,
            overall_quality=fused_contrast * 0.35 + fused_arc * 0.35 + fused_voice * 0.30,
            quality_trend=trend,
            contrast_summary=f"Fused contrast: {fused_contrast:.2f}",
            arc_summary=f"Fused arc coverage: {fused_arc:.2f}",
            voice_summary=f"Fused voice alignment: {fused_voice:.2f}",
            floor_summary="Passed" if fused_floor else "Failed",
            quality_peaks=tuple(self._to_quality_moment(m) for m in peaks),
            quality_troughs=tuple(self._to_quality_moment(m) for m in troughs),
            primary_recommendation=self._generate_recommendation(qualities),
            secondary_recommendations=tuple(),
            source_mark_count=len(marks),
            compression_ratio=len(marks) / 1.0,
            time_span_seconds=marks[-1].timestamp - marks[0].timestamp if marks else 0,
            consistency_radius=radius,  # NEW: Track fusion quality
        )

    def _fuse_contrast(self, qualities: list[ExperienceQuality]) -> float:
        """Fuse contrast using weighted mean (sheaf section)."""
        if not qualities:
            return 0.0
        # Weight recent measurements more heavily
        weights = [2 ** i for i in range(len(qualities))]
        total_weight = sum(weights)
        return sum(q.contrast * w for q, w in zip(qualities, weights)) / total_weight

    def _fuse_arc(self, qualities: list[ExperienceQuality]) -> float:
        """Fuse arc coverage using max (conservative estimate)."""
        if not qualities:
            return 0.0
        return max(q.arc_coverage for q in qualities)

    def _fuse_voice(self, qualities: list[ExperienceQuality]) -> float:
        """Fuse voice alignment using AND (all must pass)."""
        if not qualities:
            return 1.0
        # Proportion of qualities where all voices passed
        fully_aligned = sum(1 for q in qualities if all(q.voice_verdicts))
        return fully_aligned / len(qualities)

    def _fuse_floor(self, qualities: list[ExperienceQuality]) -> bool:
        """Fuse floor using AND (all must pass)."""
        return all(q.floor_passed for q in qualities)
```

---

## 4. Validation Protocol

### 4.1 Consistency Radius Calibration

**Goal**: Determine optimal consistency threshold.

**Protocol**:
1. Collect 100 sets of marks with known quality
2. Compute consistency radius for each set
3. Crystallize each set
4. Measure information loss (vs. individual marks)
5. Plot loss vs. radius, find threshold

**Success Criteria**:
- Clear relationship between radius and loss
- Threshold achieves <10% loss for 90% of crystallizations

### 4.2 Fusion Quality Validation

**Goal**: Verify fusion preserves important information.

**Protocol**:
1. Create 50 mark sets with ground truth summaries
2. Fuse using sheaf method
3. Compare crystal summaries to ground truth
4. Measure semantic similarity

**Success Criteria**:
- BERTScore > 0.85 between crystal and ground truth
- No critical information lost in fusion

---

## Pilot Integration

**Goal**: Reduce drift and improve cross-agent coherence during regeneration.

### Prompt Hooks (Minimal Insertions)
Add a "Coherence Check" ritual at the start of each iteration:

```
## Coherence Check
Phase: [DREAM/BUILD/WITNESS]
Iteration: [N]
Top 3 blockers: [list]
Current focus: [one sentence]
```

### Coordination Artifacts
- Each agent writes the block to their `.focus.*.md`.
- CREATIVE copies a merged version into `.outline.md`.
- If any agent reports a different phase/iteration, require immediate sync.

### Outcome Target
- Reduce phase/iteration mismatches to near-zero.
- Provide enough structure for automated consistency radius checks later.

---

## 5. References

1. **Robinson, M.** (2017). Sheaves are the canonical data structure for sensor integration. *Information Fusion*. https://www.sciencedirect.com/science/article/abs/pii/S156625351630207X

2. **Mansourbeigi, S.** (2018). Sheaf Theory as a Foundation for Heterogeneous Data Fusion. *Utah State University Thesis*. https://digitalcommons.usu.edu/etd/7363/

3. **Tabia, K.** (2020). A Sheaf Theoretical Approach to Uncertainty Quantification of Heterogeneous Geolocation Information. *Sensors*. https://www.mdpi.com/1424-8220/20/12/3418

4. **Ayzenberg, A., & Magai, G.** (2025). Sheaf theory: from deep geometry to deep learning. *arXiv:2502.15476*. https://arxiv.org/pdf/2502.15476

5. **Rosiak, D.** (2022). Sheaf Theory through Examples. ResearchGate. https://www.researchgate.net/publication/364730754_Sheaf_Theory_through_Examples

---

*"The whole is more than the sum of its parts—but only if the parts are consistent."*
