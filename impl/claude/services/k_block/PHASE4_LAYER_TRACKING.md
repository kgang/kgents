# Phase 4: Zero Seed Layer Tracking

**Status**: ✅ Complete
**Date**: 2025-12-24

## Overview

Added Zero Seed layer classification to `CrystalMeta`, enabling proof requirements and Galois loss interpretation based on epistemic layer.

## Changes Made

### 1. Extended CrystalMeta

**File**: `agents/d/crystal/crystal.py`

Added three new optional fields:

```python
@dataclass(frozen=True)
class CrystalMeta:
    # ... existing fields ...

    layer: int | None = None
    """Zero Seed epistemic layer (1-7). None if unclassified."""

    galois_loss: float | None = None
    """Cached Galois loss value. None if not computed yet."""

    proof_id: str | None = None
    """Reference to proof Crystal ID. None if no proof attached."""

    @property
    def requires_proof(self) -> bool:
        """L3+ requires Toulmin proofs."""
        return self.layer is not None and self.layer >= 3
```

### 2. Created Layer Classifier

**File**: `services/k_block/layers/classifier.py`

Provides loss-based layer classification:

```python
from services.k_block.layers import classify_layer, classify_crystal

# Classify raw content
galois = GaloisLossComputer(metric="token")
layer = await classify_layer("All humans are mortal", galois)
# → L1 (Axiom) if loss < 0.05

# Classify a Crystal
crystal = Crystal.create(mark, schema)
layer = await classify_crystal(crystal, galois)
```

**Layer Thresholds**:
- L1 (Axiom): loss < 0.05 — Nearly perfect coherence
- L2 (Value): loss < 0.15 — High coherence
- L3 (Goal): loss < 0.30 — Moderate coherence
- L4 (Specification): loss < 0.45 — Acceptable coherence
- L5 (Action): loss < 0.60 — Lower coherence
- L6 (Reflection): loss < 0.75 — Minimal coherence
- L7 (Representation): loss >= 0.75 — Doesn't converge

**Fallback**: Without Galois, defaults to L4 (Specification).

### 3. Helper Functions

```python
from services.k_block.layers import get_layer_name, get_layer_confidence

get_layer_name(3)  # → "Goal"
get_layer_confidence(1)  # → 1.0 (perfect confidence for axioms)
```

## Usage Examples

### Creating a Crystal with Layer

```python
from agents.d.crystal import CrystalMeta, Crystal
from agents.d.galois import GaloisLossComputer
from services.k_block.layers import classify_crystal

# Create crystal
mark = WitnessMark(action="Validated proof", reasoning="Axiomatic")
crystal = Crystal.create(mark, WITNESS_MARK_SCHEMA)

# Classify
galois = GaloisLossComputer(metric="token")
layer = await classify_crystal(crystal, galois)
loss = await galois.compute(f"{mark.action}. {mark.reasoning}")

# Create meta with layer
meta = CrystalMeta(
    schema_name="witness.mark",
    schema_version=1,
    created_at=datetime.now(UTC),
    layer=layer,
    galois_loss=loss,
)

# Check if proof required
if meta.requires_proof:
    print(f"L{meta.layer} requires Toulmin proof")
```

### Batch Classification

```python
from services.k_block.layers import classify_layer, LAYER_NAMES

contents = [
    "Earth is round",
    "System must use HTTPS",
    "I notice a pattern here...",
]

galois = GaloisLossComputer(metric="token")

for content in contents:
    layer = await classify_layer(content, galois)
    print(f"{content} → L{layer} ({LAYER_NAMES[layer]})")
```

## Testing

All tests pass (12/12):

```bash
uv run python -m pytest services/k_block/layers/test_classifier.py -v
```

**Test Coverage**:
- ✅ CrystalMeta default fields (layer/galois_loss/proof_id all None)
- ✅ CrystalMeta with layer specified
- ✅ requires_proof property (False for L1-L2, True for L3+)
- ✅ classify_layer without Galois (defaults to L4)
- ✅ classify_layer with Galois (respects thresholds)
- ✅ classify_crystal (extracts content, classifies)
- ✅ Layer names and confidence defaults
- ✅ Full integration test

## Integration Points

### With Galois (Phase 2)

```python
from agents.d.galois import compute_crystal_loss

loss = await compute_crystal_loss(crystal, metric="token")
# Use loss to determine layer
```

### With K-Block Factories (Existing)

```python
from services.k_block.layers import AxiomKBlockFactory

# Factories already have layer metadata
kblock = AxiomKBlockFactory.create(...)
kblock._layer  # → 1
```

### With Zero Seed Navigation (Future)

```python
# Filter Crystals by layer
axioms = [c for c in crystals if c.meta.layer == 1]

# Navigate by loss gradient
low_loss = [c for c in crystals if c.meta.galois_loss < 0.15]
```

## Key Insights

1. **Loss as Layer Indicator**: Lower Galois loss → more axiomatic → lower layer
2. **Proof Requirements**: Layers L3+ require formal proofs (derivational)
3. **Graceful Degradation**: Without Galois, assumes L4 (specification-level)
4. **Cached Loss**: `galois_loss` field caches expensive computation
5. **Frozen Dataclass**: All fields immutable, properties computed on demand

## Next Steps (Phase 5)

- **Derivation Tracking**: Link Crystals via derivation edges
- **Proof Attachment**: Store `proof_id` references
- **Layer Navigation UI**: Visualize layer hierarchy
- **Adaptive Classification**: Improve with LLM-based Galois restructuring

## Success Criteria Met

- [x] CrystalMeta has `layer`, `galois_loss`, `proof_id` fields
- [x] `classify_layer()` returns int 1-7 based on content
- [x] `requires_proof` property returns True for L3+
- [x] Import test succeeds: `from agents.d.crystal import CrystalMeta`
- [x] Full integration test passes
- [x] All 12 unit tests pass
