"""
K-Block schemas - Coherence windows aggregating function crystals.

A K-block is about "short essay" worth of content (500-5000 tokens, target 2000).
K-blocks are categorical (compose) and heterarchical (can contain/be contained).

Philosophy:
- K-blocks define coherence windows
- Functions cluster into K-blocks based on semantic proximity
- K-blocks can nest (file ⊂ module ⊂ feature)
- Boundary type captures organizational intent
- Coherence metrics guide refactoring decisions

The K-block is the unit of compositional reasoning. When we ask "is this
coherent?", we compute internal_coherence. When we ask "is this coupled?",
we compute external_coupling. When we ask "should this be split?", we
consult estimated_tokens vs. target range.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .proof import GaloisWitnessedProof

# Heuristics for K-block sizing and aggregation
KBLOCK_SIZE_HEURISTICS = {
    "min_functions": 3,    # Minimum functions for a coherent K-block
    "max_functions": 20,   # Maximum functions before mandatory split
    "min_tokens": 500,     # Minimum tokens for a coherent K-block
    "max_tokens": 5000,    # Maximum tokens before mandatory split
    "target_tokens": 2000, # Sweet spot ("short essay" length)
    "chars_per_token": 4,  # Rough estimate: 4 chars ≈ 1 token
}


@dataclass(frozen=True)
class KBlockCrystal:
    """
    K-Block crystal for coherence window tracking (v1).

    A K-block aggregates function crystals into a coherent unit. It captures:
    - Identity: id, name, path
    - Membership: function_ids (functions in this block)
    - Hierarchy: child_kblock_ids, parent_kblock_id
    - Boundary: boundary_type, boundary_confidence
    - Metrics: function_count, total_lines, estimated_tokens
    - Coherence: internal_coherence, external_coupling
    - Layer: dominant_layer, layer_distribution
    - Proof: GaloisWitnessedProof (self-justification)

    Boundary Types:
        "file": Functions in a single file
        "module": Functions in a Python module (directory with __init__.py)
        "feature": Functions implementing a feature (cross-file)
        "bulkhead": Explicit isolation boundary (microservice-like)
        "custom": User-defined boundary

    Metrics:
        internal_coherence: [0, 1] - How well functions in block relate
        external_coupling: [0, 1] - How dependent on external functions
        estimated_tokens: Rough token count for LLM context planning

    Hierarchy:
        K-blocks can nest:
            services/witness/store.py (file)
                ⊂ services/witness/ (module)
                ⊂ services/ (feature: Crown Jewels)

        child_kblock_ids: Set of K-blocks contained in this block
        parent_kblock_id: Parent K-block (None for root blocks)

    The K-block crystal answers:
    - "What functions belong together?" → function_ids
    - "Is this block coherent?" → internal_coherence
    - "Is this block coupled?" → external_coupling
    - "Should this be split?" → estimated_tokens vs. thresholds
    - "Why does this boundary exist?" → proof.claim
    """

    id: str
    """Unique identifier for this K-block."""

    name: str
    """Human-readable name (e.g., 'witness.store', 'galois_core')."""

    path: str
    """File or module path this K-block represents."""

    proof: GaloisWitnessedProof
    """Self-justifying proof for this K-block's existence (required for L5 crystals)."""

    boundary_type: str = "file"
    """Type of boundary: 'file', 'module', 'feature', 'bulkhead', 'custom'."""

    boundary_confidence: float = 1.0
    """Confidence in this boundary [0, 1]. Lower values suggest review."""

    dominant_layer: int = 5
    """Most common Zero Seed layer among functions (mode)."""

    function_ids: frozenset[str] = frozenset()
    """Set of function crystal IDs in this K-block."""

    child_kblock_ids: frozenset[str] = frozenset()
    """Set of child K-block IDs (for hierarchical organization)."""

    parent_kblock_id: str | None = None
    """Parent K-block ID (None for root blocks)."""

    function_count: int = 0
    """Number of functions in this K-block."""

    total_lines: int = 0
    """Total lines of code in this K-block."""

    estimated_tokens: int = 0
    """Estimated token count for LLM context planning."""

    internal_coherence: float = 0.0
    """Internal coherence metric [0, 1]. Higher is better."""

    external_coupling: float = 0.0
    """External coupling metric [0, 1]. Lower is better."""

    layer_distribution: dict[int, int] = field(default_factory=dict)
    """Distribution of layers: {layer: count}."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this K-block was first created."""

    last_recomputed: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When coherence metrics were last recomputed."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "function_ids": list(self.function_ids),
            "child_kblock_ids": list(self.child_kblock_ids),
            "parent_kblock_id": self.parent_kblock_id,
            "boundary_type": self.boundary_type,
            "boundary_confidence": self.boundary_confidence,
            "function_count": self.function_count,
            "total_lines": self.total_lines,
            "estimated_tokens": self.estimated_tokens,
            "internal_coherence": self.internal_coherence,
            "external_coupling": self.external_coupling,
            "dominant_layer": self.dominant_layer,
            "layer_distribution": self.layer_distribution,
            "proof": self.proof.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_recomputed": self.last_recomputed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlockCrystal":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            path=data["path"],
            function_ids=frozenset(data.get("function_ids", [])),
            child_kblock_ids=frozenset(data.get("child_kblock_ids", [])),
            parent_kblock_id=data.get("parent_kblock_id"),
            boundary_type=data.get("boundary_type", "file"),
            boundary_confidence=data.get("boundary_confidence", 1.0),
            function_count=data.get("function_count", 0),
            total_lines=data.get("total_lines", 0),
            estimated_tokens=data.get("estimated_tokens", 0),
            internal_coherence=data.get("internal_coherence", 0.0),
            external_coupling=data.get("external_coupling", 0.0),
            dominant_layer=data.get("dominant_layer", 5),
            layer_distribution=data.get("layer_distribution", {}),
            proof=GaloisWitnessedProof.from_dict(data["proof"]),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
            last_recomputed=datetime.fromisoformat(data["last_recomputed"]) if "last_recomputed" in data else datetime.now(UTC),
        )

    @property
    def needs_split(self) -> bool:
        """
        Check if this K-block exceeds maximum token threshold.

        Returns:
            True if estimated_tokens > max_tokens
        """
        return self.estimated_tokens > KBLOCK_SIZE_HEURISTICS["max_tokens"]

    @property
    def is_undersized(self) -> bool:
        """
        Check if this K-block is below minimum token threshold.

        Returns:
            True if estimated_tokens < min_tokens
        """
        return self.estimated_tokens < KBLOCK_SIZE_HEURISTICS["min_tokens"]

    @property
    def is_optimal_size(self) -> bool:
        """
        Check if this K-block is in the optimal token range.

        Optimal range: [target * 0.75, target * 1.25]

        Returns:
            True if in optimal range
        """
        target = KBLOCK_SIZE_HEURISTICS["target_tokens"]
        return target * 0.75 <= self.estimated_tokens <= target * 1.25


# Schema for Universe registration
from agents.d.universe import DataclassSchema

KBLOCK_CRYSTAL_SCHEMA = DataclassSchema(
    name="code.kblock",
    type_cls=KBlockCrystal
)


__all__ = [
    "KBLOCK_SIZE_HEURISTICS",
    "KBlockCrystal",
    "KBLOCK_CRYSTAL_SCHEMA",
]
