"""
K-Block Layer Factories: Create Zero Seed L1-L7 K-Blocks.

Each factory creates K-Blocks with appropriate:
1. AGENTESE path (e.g., void.axiom.{id})
2. Layer and kind metadata
3. Lineage validation (parents must be from lower layers)
4. Default confidence based on layer

Philosophy:
    "The axiom needs no proof. The representation needs context."
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.kblock import KBlock, KBlockId


class ZeroSeedKBlockFactory:
    """Base factory for Zero Seed K-Blocks (L0 - the Zero Seed itself)."""

    LAYER: int = 0
    KIND: str = "SYSTEM"  # Zero Seed is SYSTEM kind, not unknown
    PATH_PREFIX: str = "void"
    DEFAULT_CONFIDENCE: float = 1.0  # Zero Seed has perfect confidence

    @classmethod
    def create(
        cls,
        kblock_id: "KBlockId",
        title: str,
        content: str,
        lineage: list[str] | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
        created_by: str = "system",
    ) -> "KBlock":
        """
        Create a K-Block at this layer.

        Args:
            kblock_id: K-Block identifier
            title: Display title
            content: Markdown content
            lineage: Parent K-Block IDs (validated against layer rules)
            confidence: Confidence score (0-1, defaults to layer default)
            tags: Tags for categorization
            created_by: Creator identifier

        Returns:
            KBlock instance with layer metadata

        Raises:
            ValueError: If lineage validation fails
        """
        from ..core.kblock import KBlock

        lineage = lineage or []
        confidence = confidence if confidence is not None else cls.DEFAULT_CONFIDENCE
        tags = tags or []

        # Validate lineage
        cls._validate_lineage(lineage)

        # Generate AGENTESE path
        path = cls._generate_path(kblock_id, title)

        # Create K-Block with metadata
        kblock = KBlock(
            id=kblock_id,
            path=path,
            content=content,
            base_content=content,
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
        )

        # Set public fields for persistence
        kblock.zero_seed_layer = cls.LAYER
        kblock.zero_seed_kind = cls.KIND
        kblock.lineage = lineage
        kblock.confidence = confidence
        kblock.tags = tags
        kblock.created_by = created_by

        # Create derives_from edges from lineage
        from ..core.edge import KBlockEdge

        incoming_edges = []
        for parent_id in lineage:
            edge = KBlockEdge(
                id=f"edge_{uuid.uuid4().hex[:12]}",
                source_id=parent_id,  # Parent is the source
                target_id=kblock_id,  # This K-Block is the target
                edge_type="derives_from",
                context=f"Derived from parent in Zero Seed L{cls.LAYER}",
                confidence=confidence,
                mark_id=None,
                created_at=datetime.now(timezone.utc),
            )
            incoming_edges.append(edge)

        kblock.incoming_edges = incoming_edges
        kblock.outgoing_edges = []  # No outgoing edges at creation

        # Legacy private fields for backward compatibility (type: ignore for dynamic attrs)
        kblock._layer = cls.LAYER  # type: ignore[attr-defined]
        kblock._kind = cls.KIND  # type: ignore[attr-defined]
        kblock._title = title  # type: ignore[attr-defined]
        kblock._tags = tags  # type: ignore[attr-defined]
        kblock._created_by = created_by  # type: ignore[attr-defined]

        return kblock

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """
        Validate lineage against layer rules.

        Override in subclasses for layer-specific validation.

        Args:
            lineage: Parent K-Block IDs

        Raises:
            ValueError: If lineage invalid for this layer
        """
        # Base implementation: no validation
        pass

    @classmethod
    def _generate_path(cls, kblock_id: "KBlockId", title: str) -> str:
        """
        Generate AGENTESE path for this K-Block.

        Args:
            kblock_id: K-Block identifier
            title: Display title

        Returns:
            AGENTESE path (e.g., "void.axiom.entity")
        """
        # Slugify title for path component
        slug = title.lower().replace(" ", "_").replace("-", "_")
        # Remove non-alphanumeric
        slug = "".join(c for c in slug if c.isalnum() or c == "_")
        return f"{cls.PATH_PREFIX}.{cls.KIND}.{slug}"


class AxiomKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L1 Axiom K-Blocks."""

    LAYER = 1
    KIND = "axiom"
    PATH_PREFIX = "void"
    DEFAULT_CONFIDENCE = 1.0

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Axioms have no lineage."""
        if lineage:
            raise ValueError("L1 Axioms cannot have lineage (they are foundational)")


class ValueKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L2 Value K-Blocks."""

    LAYER = 2
    KIND = "value"
    PATH_PREFIX = "void"
    DEFAULT_CONFIDENCE = 0.95

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Values must derive from at least one axiom."""
        if not lineage:
            raise ValueError("L2 Values must derive from at least one L1 Axiom")
        # In full implementation, would verify parent layers are L1


class GoalKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L3 Goal K-Blocks."""

    LAYER = 3
    KIND = "goal"
    PATH_PREFIX = "concept"
    DEFAULT_CONFIDENCE = 0.90

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Goals must derive from at least one value."""
        if not lineage:
            raise ValueError("L3 Goals must derive from at least one L2 Value")
        # In full implementation, would verify parent layers are L1-L2


class SpecKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L4 Specification K-Blocks."""

    LAYER = 4
    KIND = "spec"
    PATH_PREFIX = "concept"
    DEFAULT_CONFIDENCE = 0.85

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Specs must derive from at least one goal."""
        if not lineage:
            raise ValueError("L4 Specs must derive from at least one L3 Goal")
        # In full implementation, would verify parent layers are L1-L3


class ActionKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L5 Action K-Blocks."""

    LAYER = 5
    KIND = "action"
    PATH_PREFIX = "world"
    DEFAULT_CONFIDENCE = 0.80

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Actions must derive from at least one spec."""
        if not lineage:
            raise ValueError("L5 Actions must derive from at least one L4 Spec")
        # In full implementation, would verify parent layers are L1-L4


class ReflectionKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L6 Reflection K-Blocks."""

    LAYER = 6
    KIND = "reflection"
    PATH_PREFIX = "self"
    DEFAULT_CONFIDENCE = 0.75

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Reflections must derive from at least one action."""
        if not lineage:
            raise ValueError("L6 Reflections must derive from at least one L5 Action")
        # In full implementation, would verify parent layers are L1-L5


class RepresentationKBlockFactory(ZeroSeedKBlockFactory):
    """Factory for L7 Representation K-Blocks."""

    LAYER = 7
    KIND = "representation"
    PATH_PREFIX = "void"
    DEFAULT_CONFIDENCE = 0.70

    @classmethod
    def _validate_lineage(cls, lineage: list[str]) -> None:
        """Representations can derive from any layer."""
        # Representations are flexible - can derive from any layer
        # No strict validation needed
        pass


# Factory registry for dynamic lookup
LAYER_FACTORIES = {
    0: ZeroSeedKBlockFactory,  # L0: Zero Seed genesis
    1: AxiomKBlockFactory,
    2: ValueKBlockFactory,
    3: GoalKBlockFactory,
    4: SpecKBlockFactory,
    5: ActionKBlockFactory,
    6: ReflectionKBlockFactory,
    7: RepresentationKBlockFactory,
}


def create_kblock_for_layer(
    layer: int,
    kblock_id: "KBlockId",
    title: str,
    content: str,
    lineage: list[str] | None = None,
    confidence: float | None = None,
    tags: list[str] | None = None,
    created_by: str = "system",
) -> "KBlock":
    """
    Create a K-Block at the specified layer.

    Args:
        layer: Zero Seed layer (0-7)
        kblock_id: K-Block identifier
        title: Display title
        content: Markdown content
        lineage: Parent K-Block IDs
        confidence: Confidence score (0-1)
        tags: Tags for categorization
        created_by: Creator identifier

    Returns:
        KBlock instance with layer metadata

    Raises:
        ValueError: If layer invalid or lineage validation fails
    """
    if layer not in LAYER_FACTORIES:
        raise ValueError(f"Invalid layer: {layer} (must be 0-7)")

    factory = LAYER_FACTORIES[layer]
    return factory.create(
        kblock_id=kblock_id,
        title=title,
        content=content,
        lineage=lineage,
        confidence=confidence,
        tags=tags,
        created_by=created_by,
    )


__all__ = [
    "ZeroSeedKBlockFactory",
    "AxiomKBlockFactory",
    "ValueKBlockFactory",
    "GoalKBlockFactory",
    "SpecKBlockFactory",
    "ActionKBlockFactory",
    "ReflectionKBlockFactory",
    "RepresentationKBlockFactory",
    "LAYER_FACTORIES",
    "create_kblock_for_layer",
]
