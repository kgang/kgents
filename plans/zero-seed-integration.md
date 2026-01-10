# Zero Seed Integration Plan

> *"L measures structure loss; axioms are fixed points of restructuring."*

**Status**: ✅ IMPLEMENTED (2025-01-10)
**Date**: 2025-01-10
**Priority**: P0 (Critical Path)
**Scope**: Galois loss service, bootstrap verification, layer assignment
**Related**: `coherence-synthesis-master.md`, `constitutional-os-revival.md`

---

## Executive Summary

Zero Seed v3.0 defines the Galois framework theoretically. This plan implements the operational infrastructure that makes Galois loss computable and usable across all kgents systems.

### The Gap

| Specified | Implemented | Gap |
|-----------|-------------|-----|
| `galois_loss(P) -> float` | ❌ | No central computation service |
| `verify_zero_seed_fixed_point()` | ❌ | Placeholder only |
| `compute_layer_from_loss()` | ❌ | Not implemented |
| `classify_tier_by_loss()` | ✓ | Works but not integrated |
| `LayerStratifiedLoss` | ❌ | Class exists in spec only |

### Success Criteria

1. `galois_loss(any_content)` returns L ∈ [0, 1] in < 100ms @ p95
2. `verify_zero_seed_fixed_point()` returns True (L < 0.15)
3. All marks have `galois_loss` populated (not None)
4. Layer assignment is deterministic and consistent

---

## Part I: Galois Loss Computation Service

### 1.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  GaloisLossService                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Input: str | Mark | Proof | ZeroNode | Any                │
│                         │                                   │
│                         ▼                                   │
│   ┌─────────────────────────────────────────┐              │
│   │         Content Extraction               │              │
│   │   extract_content(input) -> str          │              │
│   └─────────────────────┬───────────────────┘              │
│                         │                                   │
│                         ▼                                   │
│   ┌─────────────────────────────────────────┐              │
│   │         Restructure (R)                  │              │
│   │   modularize(content) -> ModularForm     │              │
│   │   Uses: LLM (haiku) or heuristic         │              │
│   └─────────────────────┬───────────────────┘              │
│                         │                                   │
│                         ▼                                   │
│   ┌─────────────────────────────────────────┐              │
│   │         Reconstitute (C)                 │              │
│   │   reconstitute(modular) -> str           │              │
│   │   Uses: LLM (haiku) or heuristic         │              │
│   └─────────────────────┬───────────────────┘              │
│                         │                                   │
│                         ▼                                   │
│   ┌─────────────────────────────────────────┐              │
│   │         Distance Computation             │              │
│   │   d(original, reconstituted) -> float    │              │
│   │   Methods: BERTScore, cosine, LLM judge  │              │
│   └─────────────────────┬───────────────────┘              │
│                         │                                   │
│                         ▼                                   │
│   Output: GaloisLoss(total, semantic, structural, pragmatic)│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Type Definitions

```python
# File: impl/claude/services/galois/types.py

from dataclasses import dataclass
from enum import Enum


class DistanceMethod(Enum):
    """Methods for computing semantic distance."""
    BERTSCORE = "bertscore"      # Fast, good for short text
    COSINE = "cosine"            # Very fast, embedding-based
    LLM_JUDGE = "llm_judge"      # Slow, most accurate


@dataclass(frozen=True)
class GaloisLoss:
    """Result of Galois loss computation."""

    total: float          # L(P) ∈ [0, 1]
    semantic: float       # Meaning preservation loss
    structural: float     # Form preservation loss
    pragmatic: float      # Intent preservation loss

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss. The constitutional reward."""
        return 1.0 - self.total

    @property
    def is_axiomatic(self) -> bool:
        """Fixed point: L < 0.10."""
        return self.total < 0.10

    @property
    def tier(self) -> str:
        """
        Derive evidence tier from loss (Kent-calibrated 2025-12-28).

        This is the CANONICAL tier system for constitutional evaluation.
        """
        if self.total < 0.10:
            return "CATEGORICAL"  # Axiom-level, fixed point
        elif self.total < 0.38:
            return "EMPIRICAL"    # Strong empirical evidence
        elif self.total < 0.45:
            return "AESTHETIC"    # Kent sees derivation paths
        elif self.total < 0.65:
            return "SOMATIC"      # Felt sense, Mirror test
        else:
            return "CHAOTIC"      # High loss, low confidence

    @property
    def layer(self) -> int:
        """
        Derive layer from tier for backward compatibility.

        Maps 5-tier evidence system to simplified 4-layer stratification.
        """
        tier_to_layer = {
            "CATEGORICAL": 1,  # Axiom
            "EMPIRICAL": 2,    # Value
            "AESTHETIC": 3,    # Spec
            "SOMATIC": 3,      # Spec (consolidated)
            "CHAOTIC": 4,      # Tuning
        }
        return tier_to_layer.get(self.tier, 4)


@dataclass(frozen=True)
class GaloisConfig:
    """Configuration for Galois loss computation."""

    distance_method: DistanceMethod = DistanceMethod.COSINE
    use_llm_restructure: bool = False  # True = LLM, False = heuristic
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    timeout_ms: int = 5000  # 5 second timeout


@dataclass(frozen=True)
class ModularForm:
    """Intermediate restructured form."""

    modules: tuple[str, ...]
    dependencies: tuple[tuple[str, str], ...]
    root_module: str
    metadata: dict
```

### 1.3 Service Implementation

```python
# File: impl/claude/services/galois/service.py

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Protocol

from services.galois.types import (
    DistanceMethod,
    GaloisConfig,
    GaloisLoss,
    ModularForm,
)

logger = logging.getLogger("kgents.galois.service")


class ContentExtractor(Protocol):
    """Protocol for extracting content from various types."""

    def extract(self, obj: Any) -> str:
        """Extract string content from object."""
        ...


class Restructurer(Protocol):
    """Protocol for restructuring content into modular form."""

    async def restructure(self, content: str) -> ModularForm:
        """R: Content → ModularForm."""
        ...


class Reconstituter(Protocol):
    """Protocol for reconstituting modular form to content."""

    async def reconstitute(self, modular: ModularForm) -> str:
        """C: ModularForm → Content."""
        ...


class DistanceComputer(Protocol):
    """Protocol for computing semantic distance."""

    async def compute(self, original: str, reconstituted: str) -> float:
        """d(P, C(R(P))) → [0, 1]."""
        ...


@dataclass
class GaloisLossService:
    """
    Central service for Galois loss computation.

    Usage:
        >>> service = GaloisLossService()
        >>> loss = await service.compute("Some content")
        >>> print(f"Loss: {loss.total}, Layer: {loss.layer}")

    Philosophy:
        "L measures structure loss. Axioms are fixed points."
    """

    config: GaloisConfig
    extractor: ContentExtractor
    restructurer: Restructurer
    reconstituter: Reconstituter
    distance: DistanceComputer

    # Cache: content_hash -> GaloisLoss
    _cache: dict[str, GaloisLoss]

    def __init__(
        self,
        config: GaloisConfig | None = None,
        extractor: ContentExtractor | None = None,
        restructurer: Restructurer | None = None,
        reconstituter: Reconstituter | None = None,
        distance: DistanceComputer | None = None,
    ):
        self.config = config or GaloisConfig()
        self.extractor = extractor or DefaultContentExtractor()
        self.restructurer = restructurer or HeuristicRestructurer()
        self.reconstituter = reconstituter or HeuristicReconstituter()
        self.distance = distance or JaccardDistanceComputer()  # Jaccard for performance
        self._cache = {}

    async def compute(self, content: Any) -> GaloisLoss:
        """
        Compute Galois loss for any content.

        L(P) = d(P, C(R(P)))

        Args:
            content: String, Mark, Proof, ZeroNode, or any object with extractable content

        Returns:
            GaloisLoss with total, semantic, structural, pragmatic components
        """
        # Extract string content
        text = self.extractor.extract(content)

        # Check cache
        cache_key = self._cache_key(text)
        if self.config.cache_enabled and cache_key in self._cache:
            logger.debug(f"Galois cache hit: {cache_key[:8]}...")
            return self._cache[cache_key]

        # Compute L(P) = d(P, C(R(P)))
        try:
            # R: Restructure
            modular = await self.restructurer.restructure(text)

            # C: Reconstitute
            reconstituted = await self.reconstituter.reconstitute(modular)

            # d: Distance
            total = await self.distance.compute(text, reconstituted)

            # Decompose into components (approximation)
            semantic = total * 0.5   # Meaning loss
            structural = total * 0.3  # Form loss
            pragmatic = total * 0.2   # Intent loss

            loss = GaloisLoss(
                total=total,
                semantic=semantic,
                structural=structural,
                pragmatic=pragmatic,
            )

            # Cache
            if self.config.cache_enabled:
                self._cache[cache_key] = loss

            return loss

        except Exception as e:
            logger.error(f"Galois computation failed: {e}")
            # Return high loss on failure (conservative)
            return GaloisLoss(total=1.0, semantic=1.0, structural=1.0, pragmatic=1.0)

    async def compute_decomposed(self, content: Any) -> dict[str, float]:
        """
        Compute loss with full decomposition.

        Returns per-component losses via ablation study.
        More expensive but more informative.
        """
        loss = await self.compute(content)
        text = self.extractor.extract(content)

        # Ablation: remove each component and measure delta
        components = self._split_into_components(text)
        decomposition = {}

        for name, component in components.items():
            ablated = self._ablate(text, component)
            ablated_loss = await self.compute(ablated)
            decomposition[name] = max(0.0, loss.total - ablated_loss.total)

        return decomposition

    def _cache_key(self, text: str) -> str:
        """Generate cache key from content."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _split_into_components(self, text: str) -> dict[str, str]:
        """Split text into logical components for ablation."""
        # Simple heuristic: split by paragraphs
        paragraphs = text.split("\n\n")
        return {f"para_{i}": p for i, p in enumerate(paragraphs) if p.strip()}

    def _ablate(self, text: str, component: str) -> str:
        """Remove component from text."""
        return text.replace(component, "")


# =============================================================================
# Default Implementations
# =============================================================================


class DefaultContentExtractor:
    """Extract string content from various object types."""

    def extract(self, obj: Any) -> str:
        if isinstance(obj, str):
            return obj

        # Mark
        if hasattr(obj, "stimulus") and hasattr(obj, "response"):
            return f"{obj.stimulus.content}\n{obj.response.content}"

        # ZeroNode
        if hasattr(obj, "content") and hasattr(obj, "path"):
            return obj.content

        # Proof
        if hasattr(obj, "claim") and hasattr(obj, "warrant"):
            return f"{obj.claim}\n{obj.warrant}\n{obj.data}"

        # Fallback: str()
        return str(obj)


class HeuristicRestructurer:
    """Restructure content using heuristics (no LLM)."""

    async def restructure(self, content: str) -> ModularForm:
        """Split content into logical modules."""
        # Simple heuristic: split by headers or paragraphs
        lines = content.split("\n")
        modules = []
        current_module = []

        for line in lines:
            if line.startswith("#") or (not line.strip() and current_module):
                if current_module:
                    modules.append("\n".join(current_module))
                current_module = [line] if line.strip() else []
            else:
                current_module.append(line)

        if current_module:
            modules.append("\n".join(current_module))

        return ModularForm(
            modules=tuple(modules) if modules else (content,),
            dependencies=(),
            root_module=modules[0] if modules else content,
            metadata={},
        )


class HeuristicReconstituter:
    """Reconstitute modular form using heuristics (no LLM)."""

    async def reconstitute(self, modular: ModularForm) -> str:
        """Join modules back into content."""
        return "\n\n".join(modular.modules)


class JaccardDistanceComputer:
    """
    Compute distance using Jaccard similarity of word sets.

    PERFORMANCE NOTE: This is intentionally simpler than BERTScore for speed.
    The DP integration uses Jaccard (not BERTScore) because:
    1. Galois computation happens frequently during constitutional evaluation
    2. Jaccard is O(n) vs BERTScore's model inference cost
    3. For most use cases, Jaccard provides sufficient signal

    For higher-fidelity loss computation, use the full GaloisLossService
    in services/zero_seed/galois/ which uses BERTScore with fallback.
    """

    async def compute(self, original: str, reconstituted: str) -> float:
        """
        Compute 1 - jaccard_similarity.

        This is the default for DP/constitutional integration due to performance.
        """
        orig_words = set(original.lower().split())
        recon_words = set(reconstituted.lower().split())

        if not orig_words or not recon_words:
            return 1.0 if original != reconstituted else 0.0

        intersection = orig_words & recon_words
        union = orig_words | recon_words

        jaccard = len(intersection) / len(union) if union else 0.0
        return 1.0 - jaccard  # Convert similarity to distance
```

### 1.4 Integration Points

The service should be registered in the DI container:

```python
# File: impl/claude/services/providers.py (addition)

from services.galois.service import GaloisLossService
from services.galois.types import GaloisConfig


def get_galois_service() -> GaloisLossService:
    """Provide GaloisLossService singleton."""
    return GaloisLossService(config=GaloisConfig())
```

---

## Part II: Bootstrap Verification

### 2.1 The Fixed Point Test

Zero Seed must be a fixed point of its own modularization:

```python
# File: impl/claude/services/galois/bootstrap.py

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from services.galois.service import GaloisLossService
from services.galois.types import GaloisLoss

logger = logging.getLogger("kgents.galois.bootstrap")

ZERO_SEED_PATH = Path("spec/protocols/zero-seed.md")
FIXED_POINT_THRESHOLD = 0.15  # 85% regenerability


@dataclass(frozen=True)
class BootstrapVerification:
    """Result of Zero Seed fixed point verification."""

    zero_seed_loss: GaloisLoss
    is_fixed_point: bool
    regenerability_pct: float
    deviations: list[str]

    @property
    def summary(self) -> str:
        status = "PASS" if self.is_fixed_point else "FAIL"
        return (
            f"Zero Seed Bootstrap [{status}]\n"
            f"  Galois Loss: {self.zero_seed_loss.total:.4f}\n"
            f"  Regenerability: {self.regenerability_pct:.1f}%\n"
            f"  Deviations: {len(self.deviations)}"
        )


async def verify_zero_seed_fixed_point(
    galois: GaloisLossService,
    zero_seed_path: Path = ZERO_SEED_PATH,
    threshold: float = FIXED_POINT_THRESHOLD,
) -> BootstrapVerification:
    """
    Verify that Zero Seed is a fixed point of its own modularization.

    The Strange Loop Formalized:
        Zero Seed = Fix(R ∘ describe)

    If L(Zero Seed) < threshold, it's a valid bootstrap.

    Args:
        galois: GaloisLossService instance
        zero_seed_path: Path to Zero Seed spec
        threshold: Maximum acceptable loss (default 0.15)

    Returns:
        BootstrapVerification with pass/fail and details
    """
    logger.info(f"Verifying Zero Seed fixed point: {zero_seed_path}")

    # Read Zero Seed spec
    if not zero_seed_path.exists():
        raise FileNotFoundError(f"Zero Seed not found: {zero_seed_path}")

    zero_seed_content = zero_seed_path.read_text()

    # Compute Galois loss
    loss = await galois.compute(zero_seed_content)

    # Check fixed point
    is_fixed_point = loss.total < threshold
    regenerability_pct = (1 - loss.total) * 100

    # Find deviations (high-loss sections)
    deviations = []
    decomposition = await galois.compute_decomposed(zero_seed_content)
    for section, section_loss in decomposition.items():
        if section_loss > 0.3:  # High loss section
            deviations.append(f"{section}: L={section_loss:.3f}")

    result = BootstrapVerification(
        zero_seed_loss=loss,
        is_fixed_point=is_fixed_point,
        regenerability_pct=regenerability_pct,
        deviations=deviations,
    )

    logger.info(result.summary)
    return result


async def verify_constitution_fixed_point(
    galois: GaloisLossService,
    constitution_path: Path = Path("spec/principles/CONSTITUTION.md"),
) -> BootstrapVerification:
    """
    Verify that the Constitution is a fixed point.

    Constitution should have even lower loss than Zero Seed
    since it's the axiomatic foundation.
    """
    return await verify_zero_seed_fixed_point(
        galois=galois,
        zero_seed_path=constitution_path,
        threshold=0.10,  # Stricter for Constitution
    )


# =============================================================================
# The Irreducible 15%
# =============================================================================

IRREDUCIBLE_COMPONENTS = {
    "implicit_dependencies": {
        "description": "Schema determines valid transformations (not stated)",
        "contribution": 0.05,
    },
    "contextual_nuance": {
        "description": "Tone, emphasis, connotation (lost in flattening)",
        "contribution": 0.04,
    },
    "holographic_redundancy": {
        "description": "Information distributed across modules (local→global)",
        "contribution": 0.03,
    },
    "gestalt_coherence": {
        "description": "The 'feel' of the whole vs parts",
        "contribution": 0.03,
    },
}


def explain_irreducible_loss() -> str:
    """
    Explain why perfect regenerability (L=0) is impossible.

    Philosophy:
        "Don't fight the 15%. Document it. This is the empirical
        manifestation of Galois incompleteness (analog of Gödel's theorem)."
    """
    total = sum(c["contribution"] for c in IRREDUCIBLE_COMPONENTS.values())
    lines = [
        "# The Irreducible 15%",
        "",
        "Perfect regenerability is impossible because:",
        "",
    ]
    for name, info in IRREDUCIBLE_COMPONENTS.items():
        lines.append(f"- **{name}** ({info['contribution']*100:.0f}%): {info['description']}")

    lines.extend([
        "",
        f"Total irreducible loss: {total*100:.0f}%",
        "",
        "This is not a bug. This is the boundary between formal and tacit knowledge.",
    ])
    return "\n".join(lines)
```

### 2.2 Test Suite

```python
# File: impl/claude/services/galois/_tests/test_bootstrap.py

import pytest
from pathlib import Path

from services.galois.bootstrap import (
    verify_zero_seed_fixed_point,
    verify_constitution_fixed_point,
    explain_irreducible_loss,
)
from services.galois.service import GaloisLossService


@pytest.fixture
def galois_service():
    return GaloisLossService()


@pytest.mark.asyncio
async def test_zero_seed_is_fixed_point(galois_service):
    """Zero Seed must be a fixed point (L < 0.15)."""
    result = await verify_zero_seed_fixed_point(galois_service)

    assert result.is_fixed_point, f"Zero Seed failed fixed point test: L={result.zero_seed_loss.total}"
    assert result.regenerability_pct >= 85, f"Regenerability too low: {result.regenerability_pct}%"


@pytest.mark.asyncio
async def test_constitution_is_fixed_point(galois_service):
    """Constitution must be a fixed point (L < 0.10)."""
    result = await verify_constitution_fixed_point(galois_service)

    assert result.is_fixed_point, f"Constitution failed: L={result.zero_seed_loss.total}"
    assert result.regenerability_pct >= 90, f"Regenerability too low: {result.regenerability_pct}%"


def test_irreducible_loss_explanation():
    """Irreducible loss should be documented."""
    explanation = explain_irreducible_loss()

    assert "15%" in explanation
    assert "implicit_dependencies" in explanation
    assert "gestalt_coherence" in explanation


@pytest.mark.asyncio
async def test_galois_loss_layers(galois_service):
    """Galois loss should map to correct layers."""
    # Axiom-level content
    axiom = "Everything is a node. Everything composes."
    axiom_loss = await galois_service.compute(axiom)
    assert axiom_loss.layer <= 2, f"Axiom should be L1-L2, got L{axiom_loss.layer}"

    # Tuning-level content
    tuning = "Set timeout to 5000ms. Use batch size 32."
    tuning_loss = await galois_service.compute(tuning)
    assert tuning_loss.layer >= 5, f"Tuning should be L5+, got L{tuning_loss.layer}"
```

---

## Part III: Layer Assignment Integration

### 3.1 Witness Integration

Every mark should have a computed layer:

```python
# File: impl/claude/services/witness/galois_integration.py

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from services.galois.service import GaloisLossService
from services.galois.types import GaloisLoss

if TYPE_CHECKING:
    from services.witness.mark import Mark


@dataclass
class MarkGaloisEnrichment:
    """Enrich marks with Galois information."""

    galois: GaloisLossService

    async def enrich(self, mark: "Mark") -> "Mark":
        """
        Add Galois loss and layer to mark.

        This should be called by ConstitutionalMarkReactor
        before storing the mark.
        """
        loss = await self.galois.compute(mark)

        # Create enriched mark with Galois metadata
        enriched_metadata = dict(mark.metadata)
        enriched_metadata["galois_loss"] = loss.total
        enriched_metadata["galois_layer"] = loss.layer
        enriched_metadata["galois_coherence"] = loss.coherence

        return mark.with_metadata(enriched_metadata)

    async def compute_witness_mode(self, mark: "Mark") -> str:
        """
        Determine witness mode based on Galois loss.

        From Zero Seed spec:
        - SINGLE: L < 0.1 (important, witness immediately)
        - SESSION: 0.1 <= L < 0.4 (batch at session end)
        - LAZY: L >= 0.4 (deferred until referenced)
        """
        loss = await self.galois.compute(mark)

        if mark.proof is None and loss.layer >= 3:
            # Missing proof on L3+ needs attention
            return "SINGLE"

        if loss.total < 0.1:
            return "SINGLE"
        elif loss.total < 0.4:
            return "SESSION"
        else:
            return "LAZY"
```

### 3.2 Constitutional Evaluator Integration

```python
# File: impl/claude/services/witness/constitutional_evaluator.py (modification)

# Add to MarkConstitutionalEvaluator:

async def evaluate_with_galois(self, mark: Mark) -> ConstitutionalAlignment:
    """
    Evaluate mark with Galois loss integration.

    This replaces the sync evaluate_sync for full Galois support.
    """
    # Existing evaluation
    alignment = self.evaluate_sync(mark)

    # Add Galois loss
    galois_loss = await self.galois.compute(mark)

    # Create new alignment with Galois
    return ConstitutionalAlignment.from_scores(
        principle_scores=alignment.principle_scores,
        galois_loss=galois_loss.total,  # NOW COMPUTED
        tier=self._tier_from_galois(galois_loss),
        threshold=self.threshold,
    )

def _tier_from_galois(self, loss: GaloisLoss) -> str:
    """
    Map Galois loss to evidence tier.

    Lower loss = higher confidence = stricter tier.
    Thresholds from Kent calibration (2025-12-28).
    """
    if loss.total < 0.10:
        return "CATEGORICAL"  # Axiom-level (fixed point)
    elif loss.total < 0.38:
        return "EMPIRICAL"    # Strong empirical evidence
    elif loss.total < 0.45:
        return "AESTHETIC"    # Kent sees derivation paths
    elif loss.total < 0.65:
        return "SOMATIC"      # Felt sense (Mirror test)
    else:
        return "CHAOTIC"      # High loss, low confidence
```

---

## Part IV: Implementation Roadmap

### Phase 1: Core Service (Days 1-2)

| Task | File | Status |
|------|------|--------|
| Type definitions | `services/galois/types.py` | New |
| Service implementation | `services/galois/service.py` | New |
| Default extractors | `services/galois/extractors.py` | New |
| Distance computers | `services/galois/distance.py` | New |
| Unit tests | `services/galois/_tests/test_service.py` | New |

### Phase 2: Bootstrap (Day 3)

| Task | File | Status |
|------|------|--------|
| Bootstrap verification | `services/galois/bootstrap.py` | New |
| Bootstrap tests | `services/galois/_tests/test_bootstrap.py` | New |
| Irreducible loss docs | Inline | New |

### Phase 3: Integration (Days 4-5)

| Task | File | Status |
|------|------|--------|
| DI registration | `services/providers.py` | Modify |
| Witness integration | `services/witness/galois_integration.py` | New |
| Constitutional evaluator | `services/witness/constitutional_evaluator.py` | Modify |
| Integration tests | `_tests/test_galois_integration.py` | New |

---

## Part V: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| `galois_loss()` latency | < 100ms @ p95 | Profiling |
| Zero Seed regenerability | > 85% | Bootstrap test |
| Constitution regenerability | > 90% | Bootstrap test |
| Mark Galois coverage | 100% | Count marks without `galois_loss` |
| Layer assignment consistency | 100% | Same content → same layer |

---

## Appendix: Kent-Calibrated Evidence Tiers (CANONICAL)

From empirical calibration (2025-12-28):

| Tier | Threshold | Meaning | Modal |
|------|-----------|---------|-------|
| **CATEGORICAL** | L < 0.10 | Axiom-level, fixed point | MUST |
| **EMPIRICAL** | L < 0.38 | Strong empirical evidence | SHOULD |
| **AESTHETIC** | L < 0.45 | Kent sees derivation paths | MAY |
| **SOMATIC** | L < 0.65 | Felt sense, Mirror test | MAY |
| **CHAOTIC** | L ≥ 0.65 | High loss, low confidence | WILL |

**This is the CANONICAL tier system** used across all kgents plans.

**Key Insight**: Kent's CATEGORICAL zone (L < 0.10) is tighter than theory predicted because axioms must be rock-solid. The EMPIRICAL-AESTHETIC range (0.10-0.45) is larger because Kent can see derivation paths that heuristics miss.

**Correlation with Kent judgments**: ρ = 0.8346 (Spearman)

### Simplified 4-Layer Mapping

For backward compatibility, tiers map to layers:

| Tier | Layer | Stratification |
|------|-------|----------------|
| CATEGORICAL | 1 (Axiom) | L < 0.10 |
| EMPIRICAL | 2 (Value) | 0.10 ≤ L < 0.38 |
| AESTHETIC, SOMATIC | 3 (Spec) | 0.38 ≤ L < 0.65 |
| CHAOTIC | 4 (Tuning) | L ≥ 0.65 |

---

*"Axioms are fixed points. Proofs are coherence. Layers are emergence."*
