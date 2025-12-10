"""
Psi-gent HolographicMetaphorLibrary: M-gent integration for fuzzy metaphor recall.

Stores metaphors holographically for:
- Fuzzy recall by resonance (not exact match)
- Learning through use (frequently used metaphors gain resolution)
- Blending (create novel metaphors from superposition)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .types import Metaphor, MetaphorOperation, Novel
from .metaphor_library import WeightedMetaphor


# =============================================================================
# Simple Vector Operations (avoiding numpy dependency)
# =============================================================================


def _dot_product(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute dot product of two vectors."""
    if len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def _magnitude(v: tuple[float, ...]) -> float:
    """Compute magnitude of a vector."""
    return sum(x * x for x in v) ** 0.5


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    mag_a = _magnitude(a)
    mag_b = _magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return _dot_product(a, b) / (mag_a * mag_b)


def _add_vectors(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    """Add two vectors."""
    if len(a) != len(b):
        return a
    return tuple(x + y for x, y in zip(a, b))


def _scale_vector(v: tuple[float, ...], scale: float) -> tuple[float, ...]:
    """Scale a vector."""
    return tuple(x * scale for x in v)


# =============================================================================
# Holographic Memory Pattern (simplified)
# =============================================================================


@dataclass
class HolographicPattern:
    """
    A holographic interference pattern storing metaphor information.

    Properties:
    - Information is distributed across the whole pattern
    - Cutting the pattern in half reduces resolution, not content
    - Multiple metaphors can be superimposed
    """

    # The pattern (simulated as weighted embeddings)
    pattern: tuple[float, ...]
    resolution: float = 1.0  # 0.0 = very fuzzy, 1.0 = crystal clear

    def superimpose(self, other: HolographicPattern) -> HolographicPattern:
        """Superimpose another pattern onto this one."""
        if len(self.pattern) != len(other.pattern):
            return self
        new_pattern = _add_vectors(self.pattern, other.pattern)
        new_resolution = (self.resolution + other.resolution) / 2
        return HolographicPattern(pattern=new_pattern, resolution=new_resolution)

    def compress(self, ratio: float) -> HolographicPattern:
        """
        Compress the pattern (reduce resolution).

        This is the key holographic property: compression
        reduces resolution uniformly, not catastrophically.
        """
        new_resolution = self.resolution * ratio
        # Simulate resolution loss by adding noise
        noise_factor = 1.0 - ratio
        noisy = tuple(
            x * (1.0 - noise_factor * 0.1 * (i % 3)) for i, x in enumerate(self.pattern)
        )
        return HolographicPattern(pattern=noisy, resolution=new_resolution)

    def similarity(self, query: tuple[float, ...]) -> float:
        """
        Calculate similarity to a query pattern.

        Higher resolution = more accurate similarity.
        """
        base_sim = _cosine_similarity(self.pattern, query)
        # Resolution affects accuracy
        return base_sim * (0.5 + 0.5 * self.resolution)


# =============================================================================
# Metaphor Entry with Usage Tracking
# =============================================================================


@dataclass
class MetaphorEntry:
    """
    A metaphor stored with holographic pattern and usage stats.
    """

    metaphor: Metaphor
    pattern: HolographicPattern
    usage_count: int = 0
    success_count: int = 0
    last_used: float = 0.0  # Timestamp

    @property
    def success_rate(self) -> float:
        if self.usage_count == 0:
            return 0.5
        return self.success_count / self.usage_count

    @property
    def is_hot(self) -> bool:
        """Is this metaphor frequently used?"""
        return self.usage_count > 10 and self.success_rate > 0.6

    @property
    def is_cold(self) -> bool:
        """Is this metaphor rarely used?"""
        return self.usage_count < 3 or self.success_rate < 0.3


# =============================================================================
# Holographic Metaphor Library
# =============================================================================


@dataclass
class HolographicMetaphorLibrary:
    """
    Metaphor library with holographic storage and fuzzy recall.

    M-gent integration for Psi-gent.

    Features:
    - Fuzzy recall: partial problem → partial metaphor activation
    - Learning: usage strengthens metaphor resolution
    - Compression: rarely used metaphors demote (lower resolution)
    - Blending: create novel metaphors from superposition
    """

    # Configuration
    pattern_size: int = 64  # Size of holographic patterns
    promotion_threshold: int = 5  # Usage count to promote
    demotion_threshold: int = 10  # Accesses since last use to demote
    access_count: int = 0

    # Storage
    _entries: dict[str, MetaphorEntry] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize from static library if empty
        if not self._entries:
            self._init_from_static()

    def _init_from_static(self) -> None:
        """Initialize with standard metaphors from static library."""
        from .metaphor_library import create_standard_library

        static = create_standard_library()
        for metaphor in static.all_metaphors():
            self.register(metaphor)

    def _create_pattern(self, metaphor: Metaphor) -> HolographicPattern:
        """Create a holographic pattern for a metaphor."""
        # Use embedding if available, otherwise create from description
        if metaphor.embedding:
            pattern = metaphor.embedding[: self.pattern_size]
            # Pad if needed
            if len(pattern) < self.pattern_size:
                pattern = pattern + (0.0,) * (self.pattern_size - len(pattern))
        else:
            # Create pattern from description hash
            pattern = self._hash_to_pattern(metaphor.description)

        return HolographicPattern(pattern=pattern, resolution=1.0)

    def _hash_to_pattern(self, text: str) -> tuple[float, ...]:
        """Convert text to a pattern via simple hash."""
        import hashlib

        # Create deterministic pattern from text
        h = hashlib.sha256(text.encode()).hexdigest()
        # Convert hex to floats
        pattern = []
        for i in range(0, min(len(h), self.pattern_size * 2), 2):
            val = int(h[i : i + 2], 16) / 255.0 - 0.5
            pattern.append(val)
        # Pad if needed
        while len(pattern) < self.pattern_size:
            pattern.append(0.0)
        return tuple(pattern[: self.pattern_size])

    def fetch_candidates(
        self, problem: Novel, limit: int = 5
    ) -> list[WeightedMetaphor]:
        """
        Fetch candidate metaphors by resonance with problem.

        Unlike exact lookup, returns partial matches
        weighted by resonance strength.
        """
        self.access_count += 1

        # Create query pattern from problem
        if problem.embedding:
            query = problem.embedding[: self.pattern_size]
            if len(query) < self.pattern_size:
                query = query + (0.0,) * (self.pattern_size - len(query))
        else:
            query = self._hash_to_pattern(problem.description)

        # Calculate resonance with each stored metaphor
        candidates: list[WeightedMetaphor] = []
        for entry in self._entries.values():
            similarity = entry.pattern.similarity(query)

            # Boost by success rate
            weight = similarity * (0.5 + 0.5 * entry.success_rate)

            # Boost by resolution (higher resolution = more reliable)
            weight *= 0.5 + 0.5 * entry.pattern.resolution

            candidates.append(WeightedMetaphor(metaphor=entry.metaphor, weight=weight))

        # Sort by weight descending
        candidates.sort(reverse=True)

        # Consolidate memory periodically
        if self.access_count % 100 == 0:
            self._consolidate()

        return candidates[:limit]

    def get(self, metaphor_id: str) -> Metaphor | None:
        """Get a specific metaphor by ID."""
        entry = self._entries.get(metaphor_id)
        return entry.metaphor if entry else None

    def register(self, metaphor: Metaphor) -> None:
        """Register a new metaphor."""
        pattern = self._create_pattern(metaphor)
        self._entries[metaphor.metaphor_id] = MetaphorEntry(
            metaphor=metaphor, pattern=pattern
        )

    def update_usage(self, metaphor_id: str, success: bool) -> None:
        """
        Update usage statistics and potentially promote/demote.

        Learning through use:
        - Success strengthens (promotes) the metaphor
        - Failure weakens (demotes) the metaphor
        """
        if metaphor_id not in self._entries:
            return

        entry = self._entries[metaphor_id]
        entry.usage_count += 1
        if success:
            entry.success_count += 1
        entry.last_used = self.access_count

        # Check for promotion (strengthen resolution)
        if entry.usage_count >= self.promotion_threshold and entry.is_hot:
            self._promote(metaphor_id)

    def strengthen(self, metaphor: Metaphor, problem: Novel, success: bool) -> None:
        """
        Strengthen or weaken a metaphor based on usage outcome.

        Alias for update_usage with explicit success flag.
        """
        self.update_usage(metaphor.metaphor_id, success)

    def blend(self, metaphors: list[Metaphor]) -> Metaphor | None:
        """
        Create novel metaphor by superposition.

        When no single metaphor fits, blend multiple.
        The holographic property makes this natural.
        """
        if len(metaphors) < 2:
            return metaphors[0] if metaphors else None

        # Superimpose patterns
        patterns = [
            self._entries[m.metaphor_id].pattern
            for m in metaphors
            if m.metaphor_id in self._entries
        ]
        if not patterns:
            return None

        blended_pattern = patterns[0]
        for p in patterns[1:]:
            blended_pattern = blended_pattern.superimpose(p)

        # Scale down (averaging effect)
        blended_pattern = HolographicPattern(
            pattern=_scale_vector(blended_pattern.pattern, 1.0 / len(patterns)),
            resolution=blended_pattern.resolution,
        )

        # Create blended metaphor
        names = [m.name for m in metaphors]
        domains = list(set(m.domain for m in metaphors))

        # Combine operations
        all_ops: list[MetaphorOperation] = []
        for m in metaphors:
            all_ops.extend(m.operations)

        blended = Metaphor(
            metaphor_id=f"blend_{'_'.join(m.metaphor_id[:8] for m in metaphors)}",
            name=f"Blend({', '.join(names)})",
            domain=domains[0] if domains else "blended",
            description=f"Blended metaphor combining: {', '.join(names)}",
            operations=tuple(all_ops[:8]),  # Limit operations
            tractability=sum(m.tractability for m in metaphors) / len(metaphors),
            generality=max(m.generality for m in metaphors),
            related_metaphors=tuple(m.metaphor_id for m in metaphors),
        )

        # Register the blend
        self._entries[blended.metaphor_id] = MetaphorEntry(
            metaphor=blended, pattern=blended_pattern
        )

        return blended

    def _promote(self, metaphor_id: str) -> None:
        """Promote a metaphor (increase resolution)."""
        if metaphor_id not in self._entries:
            return

        entry = self._entries[metaphor_id]
        new_resolution = min(1.0, entry.pattern.resolution * 1.1)
        entry.pattern = HolographicPattern(
            pattern=entry.pattern.pattern, resolution=new_resolution
        )

    def _demote(self, metaphor_id: str) -> None:
        """Demote a metaphor (decrease resolution)."""
        if metaphor_id not in self._entries:
            return

        entry = self._entries[metaphor_id]
        entry.pattern = entry.pattern.compress(0.9)

    def _consolidate(self) -> None:
        """
        Background consolidation: compress cold metaphors.

        Like M-gent's consolidation, this maintains memory budget
        by reducing resolution of rarely-used metaphors.
        """
        for metaphor_id, entry in self._entries.items():
            # Check if cold (not used recently)
            accesses_since_use = self.access_count - entry.last_used
            if accesses_since_use > self.demotion_threshold and entry.is_cold:
                self._demote(metaphor_id)

    def __len__(self) -> int:
        return len(self._entries)

    def all_metaphors(self) -> list[Metaphor]:
        """Get all registered metaphors."""
        return [e.metaphor for e in self._entries.values()]

    def get_usage_statistics(self) -> dict[str, dict[str, Any]]:
        """Get usage statistics for all metaphors."""
        return {
            mid: {
                "usage_count": e.usage_count,
                "success_count": e.success_count,
                "success_rate": e.success_rate,
                "resolution": e.pattern.resolution,
                "is_hot": e.is_hot,
                "is_cold": e.is_cold,
            }
            for mid, e in self._entries.items()
        }
