"""
HolographicField - Hyperdimensional Computing Memory.

This replaces Vector DB / RAG with distributed algebraic memory.
Memory is stored as a superposition in a single high-dimensional
vector (the hologram), enabling:

1. Morphic Resonance: Agent B learns from Agent A without message passing
2. Algebraic structure: bind(House, Architect) ⊥ bind(House, Poet)
3. Graceful degradation: Partial matches work naturally
4. No explicit retrieval: Memory is resonance, not lookup

AGENTESE Paths:
- field.resonate: Check similarity to global field
- field.imprint: Add pattern to superposition
- field.bind: Role-filler association
- field.bundle: Compose patterns
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .hdc_ops import (
    DIMENSIONS,
    Vector,
    hdc_bind,
    hdc_bundle,
    hdc_encode_sequence,
    hdc_permute,
    hdc_similarity,
    hdc_unbind,
    random_hd_vector,
)

__all__ = [
    "HolographicField",
    "DIMENSIONS",
    "Vector",
    "GLOBAL_HOLOGRAM",
]


@dataclass
class HolographicField:
    """
    Hyperdimensional Computing (HDC) Memory.

    Unlike Vector DBs which store discrete embeddings,
    HDC stores information as a superposition in a
    single high-dimensional vector (the hologram).

    Key Operations:
    - bind(*): Multiply vectors (role-filler binding)
    - bundle(+): Add vectors (superposition)
    - permute(P): Rotate vectors (sequence encoding)
    - resonate: Measure similarity to global field
    - imprint: Add to global superposition

    Why this is revolutionary:
    1. House * Architect ⊥ House * Poet (algebraically!)
       The same concept bound to different roles yields
       orthogonal vectors. No complex Lens needed.

    2. Morphic Resonance is INHERENT. When Agent A solves
       a problem, it adds to the global superposition.
       Agent B immediately "feels" the shift in similarity.

    3. Graceful degradation. Partial matches work.
       Memory is associative, not lookup-based.

    Example:
        >>> field = HolographicField()
        >>> # Agent A learns something
        >>> pattern_a = field.encode_structure({"problem": "auth", "solution": "jwt"})
        >>> field.imprint(pattern_a)
        >>> # Agent B queries with similar problem
        >>> query_b = field.encode_structure({"problem": "auth"})
        >>> resonance = field.resonate(query_b)
        >>> assert resonance > 0.3  # Agent B feels Agent A's learning
    """

    # Dimensions (can be customized for testing)
    dimensions: int = DIMENSIONS

    # The global hologram (superposition of all memories)
    global_superposition: Vector = field(init=False)

    # Symbol codebook (random vectors for atomic concepts)
    _codebook: dict[str, Vector] = field(default_factory=dict)

    # Track imprint count for normalization decisions
    _imprint_count: int = 0

    # Alias for internal use
    _dimensions: int = field(init=False)

    def __post_init__(self) -> None:
        """Initialize global superposition with correct dimensions."""
        self._dimensions = self.dimensions
        self.global_superposition = np.zeros(self._dimensions, dtype=np.float64)

    def get_symbol(self, name: str) -> Vector:
        """
        Get or create a random vector for an atomic symbol.

        Atomic symbols are near-orthogonal in high dimensions.
        The codebook ensures deterministic mapping from name to vector.

        Args:
            name: Symbol name (e.g., "house", "architect")

        Returns:
            Normalized HD vector for the symbol
        """
        if name not in self._codebook:
            # Use hash of name as seed for reproducibility
            seed = hash(name) % (2**31)
            self._codebook[name] = random_hd_vector(self._dimensions, seed=seed)
        return self._codebook[name]

    def bind(self, a: Vector, b: Vector) -> Vector:
        """
        Bind two vectors (role-filler association).

        Uses circular convolution (equivalent to XOR in binary HDC).

        Properties:
        - bind(a, b) ⊥ a  (orthogonal to components)
        - bind(a, b) ⊥ b
        - bind(a, bind(a, b)) ≈ b  (self-inverse)

        Example:
        - bind(HOUSE, ARCHITECT) creates a unique vector
          representing "house as seen by architect"

        Args:
            a: First HD vector
            b: Second HD vector

        Returns:
            Bound vector
        """
        return hdc_bind(a, b)

    def bundle(self, vectors: list[Vector]) -> Vector:
        """
        Bundle vectors (superposition).

        Creates a composite that is similar to all components.

        Example:
        - bundle([HOUSE, HOME, SHELTER]) creates a vector
          similar to all three concepts

        Args:
            vectors: List of vectors to bundle

        Returns:
            Normalized bundled vector
        """
        return hdc_bundle(vectors, normalize=True)

    def permute(self, v: Vector, n: int = 1) -> Vector:
        """
        Permute vector (sequence position encoding).

        permute(v, 0) = v
        permute(v, 1) = P(v)
        permute(v, 2) = P(P(v))

        Example:
        - permute(WORD, 0) = first word
        - permute(WORD, 1) = second word

        Args:
            v: Vector to permute
            n: Position offset

        Returns:
            Permuted vector
        """
        return hdc_permute(v, n)

    def resonate(self, query: Vector) -> float:
        """
        Measure resonance with the global field.

        This is "Morphic Resonance"--how familiar is this
        pattern to the collective memory?

        Returns cosine similarity in [-1, 1].

        Args:
            query: Pattern to test

        Returns:
            Resonance score (cosine similarity)
        """
        norm_global = np.linalg.norm(self.global_superposition)
        if norm_global == 0:
            return 0.0

        return hdc_similarity(query, self.global_superposition)

    def imprint(self, pattern: Vector, strength: float = 1.0) -> None:
        """
        Imprint pattern into the global field.

        Because the field is holographic:
        - This doesn't overwrite; it nuances
        - Repeated imprints strengthen patterns
        - New patterns shift the whole field slightly

        This IS Morphic Resonance. When one agent learns,
        all agents feel the field shift.

        Args:
            pattern: Pattern to imprint
            strength: Imprint strength (default: 1.0)
        """
        self.global_superposition = self.global_superposition + strength * pattern
        self._imprint_count += 1

        # Normalize to prevent unbounded growth
        norm = np.linalg.norm(self.global_superposition)
        if norm > 0:
            self.global_superposition = self.global_superposition / norm

    def query(self, pattern: Vector, threshold: float = 0.5) -> list[tuple[str, float]]:
        """
        Query the codebook for similar symbols.

        Unlike vector DB, this doesn't return stored objects.
        It returns symbolic associations based on similarity.

        Args:
            pattern: Pattern to query
            threshold: Minimum similarity threshold

        Returns:
            List of (symbol_name, similarity) tuples, sorted by similarity
        """
        results = []
        for name, vec in self._codebook.items():
            sim = hdc_similarity(pattern, vec)
            if sim > threshold:
                results.append((name, sim))
        return sorted(results, key=lambda x: -x[1])

    def encode_structure(
        self,
        structure: dict[str, Any],
        role_binding: bool = True,
    ) -> Vector:
        """
        Encode a structured object as a holographic vector.

        Example:
            encode_structure({
                "type": "observation",
                "observer": "architect",
                "target": "house",
                "result": "blueprint"
            })

        Creates: bundle([
            bind(TYPE, OBSERVATION),
            bind(OBSERVER, ARCHITECT),
            bind(TARGET, HOUSE),
            bind(RESULT, BLUEPRINT)
        ])

        Args:
            structure: Dictionary to encode
            role_binding: If True, bind roles to fillers.
                          If False, just bundle values.

        Returns:
            Encoded HD vector
        """
        if not structure:
            return np.zeros(self._dimensions, dtype=np.float64)

        if not role_binding:
            # Simple bundle of values
            value_vectors = [self.get_symbol(str(v)) for v in structure.values()]
            return self.bundle(value_vectors)

        # Role-filler binding
        bound_pairs = []
        for role, filler in structure.items():
            role_vec = self.get_symbol(str(role))
            filler_vec = self.get_symbol(str(filler))
            bound_pairs.append(self.bind(role_vec, filler_vec))

        return self.bundle(bound_pairs)

    def encode_sequence(self, items: list[str]) -> Vector:
        """
        Encode a sequence preserving order.

        Args:
            items: Ordered list of symbol names

        Returns:
            Sequence-encoded vector
        """
        vectors = [self.get_symbol(item) for item in items]
        return hdc_encode_sequence(vectors)

    def similarity(self, a: Vector, b: Vector) -> float:
        """
        Compute similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity in [-1, 1]
        """
        return hdc_similarity(a, b)

    def unbind(self, bound: Vector, role: Vector) -> Vector:
        """
        Unbind a role from a bound vector using circular correlation.

        This is the inverse operation for circular convolution binding:
        unbind(bind(role, filler), role) ≈ filler

        Args:
            bound: Bound vector (created via bind)
            role: Role to unbind

        Returns:
            Approximate filler vector
        """
        return hdc_unbind(bound, role)

    def clear(self) -> None:
        """Clear the global superposition."""
        self.global_superposition = np.zeros(self._dimensions, dtype=np.float64)
        self._imprint_count = 0

    def fork(self) -> "HolographicField":
        """
        Create a fork of this field.

        The fork shares the codebook but has independent superposition.
        Useful for branching experiments.

        Returns:
            New HolographicField with copied state
        """
        forked = HolographicField(dimensions=self._dimensions)
        forked.global_superposition = self.global_superposition.copy()
        forked._codebook = self._codebook  # Share codebook
        forked._imprint_count = self._imprint_count
        return forked

    @property
    def imprint_count(self) -> int:
        """Get the number of imprints in this field."""
        return self._imprint_count

    def __repr__(self) -> str:
        return (
            f"HolographicField(dimensions={self._dimensions}, "
            f"imprints={self._imprint_count}, "
            f"symbols={len(self._codebook)})"
        )


# Global field instance (shared across all agents)
# This enables Morphic Resonance without explicit communication
GLOBAL_HOLOGRAM = HolographicField()
