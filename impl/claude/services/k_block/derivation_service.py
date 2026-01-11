"""
K-Block Derivation Service.

Bridges K-Block storage with ASHC derivation context computation.
Every K-Block gets derivation context at creation time.

Philosophy: "The system illuminates, not enforces."

This service enables the consumer-first derivation UX by:
1. Computing derivation context at K-Block creation
2. Suggesting grounding principles for orphans
3. Creating derivation edges when user grounds
4. Tracking downstream dependents for change propagation

Architecture:
    - Integrates with DerivationDAG for lineage tracking
    - Uses Galois loss for semantic similarity to principles
    - Emits witness marks on grounding operations
    - Stores derivation context in K-Block metadata

See: spec/protocols/zero-seed1/ashc.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
from uuid import uuid4

from protocols.ashc.paths import (
    DerivationPath,
    PathKind,
    PathWitness,
    PathWitnessType,
)
from services.zero_seed.galois.galois_loss import (
    GaloisLoss,
    GaloisLossComputer,
    LossCache,
    compute_galois_loss_async,
)

from .core.derivation import DerivationDAG, validate_derivation
from .core.kblock import KBlock, generate_kblock_id

if TYPE_CHECKING:
    from services.witness import Mark, MarkStore


logger = logging.getLogger("kgents.k_block.derivation_service")


# =============================================================================
# Constants
# =============================================================================

# Constitutional principles
PRINCIPLES = [
    "TASTEFUL",
    "CURATED",
    "ETHICAL",
    "JOY_INDUCING",
    "COMPOSABLE",
    "HETERARCHICAL",
    "GENERATIVE",
]

# Principle descriptions for semantic matching
PRINCIPLE_DESCRIPTIONS: dict[str, str] = {
    "TASTEFUL": "Each agent serves a clear, justified purpose with aesthetic coherence",
    "CURATED": "Intentional selection over exhaustive cataloging, depth over breadth",
    "ETHICAL": "Agents augment human capability, never replace judgment",
    "JOY_INDUCING": "Delight in interaction, positive user experience",
    "COMPOSABLE": "Agents are morphisms in a category, can be chained with >>",
    "HETERARCHICAL": "Agents exist in flux, not fixed hierarchy",
    "GENERATIVE": "Spec is compression, produces more than it consumes",
}

# Grounding thresholds
GROUNDING_THRESHOLD = 0.5  # Max loss for a path to be considered grounded
PROVISIONAL_THRESHOLD = 0.7  # Max loss for provisional status
SUGGESTION_LIMIT = 3  # Number of grounding suggestions to return


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class GroundingSuggestion:
    """
    A suggested principle grounding for an orphan K-Block.

    Provides actionable guidance for users to ground their content
    in the constitutional principles.

    Philosophy: "The system illuminates, not enforces."

    Attributes:
        principle: The constitutional principle suggested
        galois_loss: Semantic distance between content and principle
        confidence: Confidence in the suggestion (1 - galois_loss)
        reasoning: Human-readable explanation of why this principle fits
    """

    principle: str
    galois_loss: float
    confidence: float
    reasoning: str

    def __post_init__(self) -> None:
        """Validate and normalize fields."""
        if self.principle not in PRINCIPLES:
            logger.warning(f"Unknown principle: {self.principle}")
        # Clamp values to valid range
        self.galois_loss = max(0.0, min(1.0, self.galois_loss))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class DerivationContext:
    """
    Derivation context attached to every K-Block.

    This is the core data structure that bridges K-Blocks with ASHC derivation.
    It tracks where content comes from and how well it aligns with principles.

    Attributes:
        source_principle: The grounding principle (if grounded)
        galois_loss: Semantic loss from source to this content
        grounding_status: 'grounded' | 'provisional' | 'orphan'
        parent_kblock_id: ID of parent K-Block (if deriving from another)
        derivation_path: Full ASHC derivation path (if grounded)
        witnesses: Evidence supporting the derivation
    """

    source_principle: str | None
    galois_loss: float
    grounding_status: str  # 'grounded' | 'provisional' | 'orphan'
    parent_kblock_id: str | None
    derivation_path: DerivationPath[Any, Any] | None
    witnesses: list[PathWitness]

    def __post_init__(self) -> None:
        """Validate grounding status."""
        valid_statuses = {"grounded", "provisional", "orphan"}
        if self.grounding_status not in valid_statuses:
            raise ValueError(
                f"Invalid grounding_status: {self.grounding_status}. "
                f"Must be one of: {valid_statuses}"
            )

    @property
    def is_grounded(self) -> bool:
        """Check if this context is grounded in principles."""
        return self.grounding_status == "grounded"

    @property
    def coherence(self) -> float:
        """Coherence = 1 - galois_loss."""
        return 1.0 - self.galois_loss

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            "source_principle": self.source_principle,
            "galois_loss": self.galois_loss,
            "grounding_status": self.grounding_status,
            "parent_kblock_id": self.parent_kblock_id,
            "derivation_path": self.derivation_path.to_dict() if self.derivation_path else None,
            "witnesses": [w.to_dict() for w in self.witnesses],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DerivationContext":
        """Deserialize from dictionary."""
        path = None
        if data.get("derivation_path"):
            path = DerivationPath.from_dict(data["derivation_path"])

        witnesses = [PathWitness.from_dict(w) for w in data.get("witnesses", [])]

        return cls(
            source_principle=data.get("source_principle"),
            galois_loss=data.get("galois_loss", 0.0),
            grounding_status=data.get("grounding_status", "orphan"),
            parent_kblock_id=data.get("parent_kblock_id"),
            derivation_path=path,
            witnesses=witnesses,
        )


# =============================================================================
# Witness Bridge Protocol
# =============================================================================


@runtime_checkable
class DerivationWitnessBridge(Protocol):
    """
    Protocol for emitting witness marks on derivation operations.

    This enables the Witness system to track grounding decisions
    for audit and provenance.
    """

    async def emit_grounding_mark(
        self,
        kblock_id: str,
        principle: str,
        galois_loss: float,
        context: DerivationContext,
    ) -> str | None:
        """
        Emit a witness mark when a K-Block is grounded.

        Args:
            kblock_id: The K-Block being grounded
            principle: The principle it's being grounded to
            galois_loss: The semantic loss of the grounding
            context: Full derivation context

        Returns:
            Mark ID if mark was emitted, None otherwise
        """
        ...

    async def emit_derivation_mark(
        self,
        from_kblock_id: str,
        to_kblock_id: str,
        edge_kind: str,
        galois_loss: float,
    ) -> str | None:
        """
        Emit a witness mark when a derivation edge is created.

        Args:
            from_kblock_id: Source K-Block
            to_kblock_id: Target K-Block
            edge_kind: Kind of derivation edge
            galois_loss: Semantic loss of the derivation

        Returns:
            Mark ID if mark was emitted, None otherwise
        """
        ...


# =============================================================================
# Default Witness Bridge (No-op)
# =============================================================================


class NullDerivationWitnessBridge:
    """No-op witness bridge for when Witness service is not available."""

    async def emit_grounding_mark(
        self,
        kblock_id: str,
        principle: str,
        galois_loss: float,
        context: DerivationContext,
    ) -> str | None:
        """No-op: return None."""
        return None

    async def emit_derivation_mark(
        self,
        from_kblock_id: str,
        to_kblock_id: str,
        edge_kind: str,
        galois_loss: float,
    ) -> str | None:
        """No-op: return None."""
        return None


# =============================================================================
# K-Block Derivation Service
# =============================================================================


@dataclass
class KBlockDerivationService:
    """
    Service for computing and managing K-Block derivation context.

    This service enables the consumer-first derivation UX by:
    1. Computing derivation context at K-Block creation
    2. Suggesting grounding principles for orphans
    3. Creating derivation edges when user grounds
    4. Tracking downstream dependents for change propagation

    Philosophy:
        "The system illuminates, not enforces."

        We compute and surface derivation context, but the user
        makes the final decision on grounding. The system suggests,
        the user chooses.

    Usage:
        >>> service = KBlockDerivationService()
        >>> context = await service.compute_derivation("kb_123", "Some content...")
        >>> print(context.grounding_status)  # 'orphan'
        >>> suggestions = await service.suggest_grounding("Some content...")
        >>> for s in suggestions:
        ...     print(f"{s.principle}: {s.confidence:.2f}")

    Integration:
        - DerivationDAG: Tracks lineage between K-Blocks
        - Galois Loss: Computes semantic distance to principles
        - Witness Bridge: Emits marks for audit trail
    """

    # Core dependencies
    dag: DerivationDAG = field(default_factory=DerivationDAG)
    loss_cache: LossCache = field(default_factory=LossCache)
    witness_bridge: DerivationWitnessBridge = field(default_factory=NullDerivationWitnessBridge)

    # Internal state
    _contexts: dict[str, DerivationContext] = field(default_factory=dict)
    _downstream_index: dict[str, set[str]] = field(default_factory=dict)

    async def compute_derivation(
        self,
        kblock_id: str,
        content: str,
        parent_kblock_id: str | None = None,
    ) -> DerivationContext:
        """
        Compute derivation context for a K-Block.

        This is called at K-Block creation time to establish initial
        derivation context. The context may be:
        - 'grounded' if parent is grounded and loss is acceptable
        - 'provisional' if parent is provisional or loss is borderline
        - 'orphan' if no parent or loss is too high

        Args:
            kblock_id: ID of the K-Block
            content: Content of the K-Block
            parent_kblock_id: Optional parent K-Block ID for inheritance

        Returns:
            DerivationContext with grounding status and metadata

        Example:
            >>> service = KBlockDerivationService()
            >>> ctx = await service.compute_derivation("kb_1", "Build composable agents")
            >>> print(ctx.grounding_status)  # Might be 'orphan' initially
        """
        witnesses: list[PathWitness] = []
        source_principle: str | None = None
        parent_context: DerivationContext | None = None
        galois_loss = 1.0  # Default to maximum loss (orphan)

        # Check if we're deriving from a parent
        if parent_kblock_id and parent_kblock_id in self._contexts:
            parent_context = self._contexts[parent_kblock_id]
            source_principle = parent_context.source_principle

            # Compute loss relative to parent
            result = await self._compute_content_loss(content)
            galois_loss = result.loss

            # Add parent witness
            witnesses.append(
                PathWitness.create(
                    witness_type=PathWitnessType.COMPOSITION,
                    evidence={
                        "parent_id": parent_kblock_id,
                        "parent_principle": source_principle,
                        "parent_status": parent_context.grounding_status,
                    },
                    confidence=parent_context.coherence,
                    grounding_principle=source_principle,
                )
            )

            # Update downstream index
            self._downstream_index.setdefault(parent_kblock_id, set()).add(kblock_id)

        else:
            # No parent - compute fresh loss
            result = await self._compute_content_loss(content)
            galois_loss = result.loss

        # Determine grounding status
        if source_principle and galois_loss < GROUNDING_THRESHOLD:
            grounding_status = "grounded"
        elif source_principle and galois_loss < PROVISIONAL_THRESHOLD:
            grounding_status = "provisional"
        else:
            grounding_status = "orphan"

        # Add Galois witness
        witnesses.append(PathWitness.from_galois(galois_loss, method=result.method))

        # Create derivation path if grounded
        derivation_path: DerivationPath[Any, Any] | None = None
        if grounding_status in ("grounded", "provisional") and source_principle:
            derivation_path = DerivationPath.derive(
                source_id=source_principle,
                target_id=kblock_id,
                witnesses=witnesses,
                galois_loss=galois_loss,
                principle_scores={source_principle: 1.0 - galois_loss},
                kblock_lineage=[parent_kblock_id] if parent_kblock_id else [],
            )

        # Build context
        context = DerivationContext(
            source_principle=source_principle,
            galois_loss=galois_loss,
            grounding_status=grounding_status,
            parent_kblock_id=parent_kblock_id,
            derivation_path=derivation_path,
            witnesses=witnesses,
        )

        # Store context
        self._contexts[kblock_id] = context

        logger.info(
            f"Computed derivation for {kblock_id}: "
            f"status={grounding_status}, loss={galois_loss:.3f}"
        )

        return context

    async def suggest_grounding(
        self,
        content: str,
        limit: int = SUGGESTION_LIMIT,
    ) -> list[GroundingSuggestion]:
        """
        Suggest principle groundings based on content analysis.

        For each principle, computes Galois loss of content against
        the principle's description. Returns sorted by loss (lowest first).

        Philosophy:
            "The system illuminates, not enforces."

        Args:
            content: The content to analyze
            limit: Maximum number of suggestions to return

        Returns:
            List of GroundingSuggestion sorted by confidence (highest first)

        Example:
            >>> suggestions = await service.suggest_grounding(
            ...     "Build delightful user experiences with tasteful design"
            ... )
            >>> for s in suggestions:
            ...     print(f"{s.principle}: {s.confidence:.2%}")
            JOY_INDUCING: 85%
            TASTEFUL: 78%
            CURATED: 62%
        """
        suggestions: list[GroundingSuggestion] = []

        for principle in PRINCIPLES:
            description = PRINCIPLE_DESCRIPTIONS.get(principle, principle)

            # Compute loss between content and principle description
            combined = f"{content}\n\n---\n\n{description}"
            result = await compute_galois_loss_async(
                combined,
                use_cache=True,
                cache=self.loss_cache,
            )

            # Generate reasoning based on principle
            reasoning = self._generate_reasoning(principle, content, result.loss)

            suggestions.append(
                GroundingSuggestion(
                    principle=principle,
                    galois_loss=result.loss,
                    confidence=1.0 - result.loss,
                    reasoning=reasoning,
                )
            )

        # Sort by confidence (highest first = lowest loss)
        suggestions.sort(key=lambda s: s.galois_loss)

        return suggestions[:limit]

    async def ground_kblock(
        self,
        kblock_id: str,
        principle: str,
        parent_kblock_id: str | None = None,
    ) -> DerivationPath[Any, Any]:
        """
        Create derivation edge from principle/parent to K-Block.

        This is the user action that grounds an orphan K-Block.
        It creates the derivation path and emits a witness mark.

        Args:
            kblock_id: The K-Block to ground
            principle: The constitutional principle
            parent_kblock_id: Optional parent K-Block for chain derivation

        Returns:
            The created DerivationPath

        Raises:
            ValueError: If principle is invalid or K-Block not found

        Example:
            >>> path = await service.ground_kblock("kb_orphan", "COMPOSABLE")
            >>> print(path.is_grounded())  # True
        """
        if principle not in PRINCIPLES:
            raise ValueError(f"Invalid principle: {principle}. Must be one of: {PRINCIPLES}")

        # Get or create context
        context = self._contexts.get(kblock_id)
        if context is None:
            # Create minimal context for unknown K-Block
            context = DerivationContext(
                source_principle=None,
                galois_loss=0.5,  # Assume moderate loss
                grounding_status="orphan",
                parent_kblock_id=None,
                derivation_path=None,
                witnesses=[],
            )
            self._contexts[kblock_id] = context

        # Compute galois loss if we have content
        galois_loss = context.galois_loss

        # Create witnesses
        witnesses: list[PathWitness] = list(context.witnesses)
        witnesses.append(
            PathWitness.from_principle(
                principle_id=principle,
                principle_text=PRINCIPLE_DESCRIPTIONS.get(principle, principle),
            )
        )

        # Create derivation path
        source_id = parent_kblock_id if parent_kblock_id else principle
        kblock_lineage: list[str] = []
        if parent_kblock_id:
            kblock_lineage.append(parent_kblock_id)

        derivation_path: DerivationPath[Any, Any] = DerivationPath.derive(
            source_id=source_id,
            target_id=kblock_id,
            witnesses=witnesses,
            galois_loss=galois_loss,
            principle_scores={principle: 1.0 - galois_loss},
            kblock_lineage=kblock_lineage,
        )

        # Update context
        new_context = DerivationContext(
            source_principle=principle,
            galois_loss=galois_loss,
            grounding_status="grounded" if galois_loss < GROUNDING_THRESHOLD else "provisional",
            parent_kblock_id=parent_kblock_id,
            derivation_path=derivation_path,
            witnesses=witnesses,
        )
        self._contexts[kblock_id] = new_context

        # Update downstream index if parent specified
        if parent_kblock_id:
            self._downstream_index.setdefault(parent_kblock_id, set()).add(kblock_id)

        # Emit witness mark
        mark_id = await self.witness_bridge.emit_grounding_mark(
            kblock_id=kblock_id,
            principle=principle,
            galois_loss=galois_loss,
            context=new_context,
        )

        if mark_id:
            logger.info(f"Grounded {kblock_id} to {principle}, mark={mark_id}")
        else:
            logger.info(f"Grounded {kblock_id} to {principle}")

        return derivation_path

    async def get_downstream(self, kblock_id: str) -> list[str]:
        """
        Get all K-Block IDs that derive from this one.

        Used for change propagation - when a K-Block changes,
        we need to know which downstream blocks might be affected.

        Args:
            kblock_id: The source K-Block ID

        Returns:
            List of K-Block IDs that derive from this one

        Example:
            >>> downstream = await service.get_downstream("kb_parent")
            >>> for child_id in downstream:
            ...     await service.recompute_on_change(child_id)
        """
        # Get direct children
        direct = self._downstream_index.get(kblock_id, set())

        # Recursively get all descendants
        all_downstream: set[str] = set()
        to_visit = list(direct)

        while to_visit:
            current = to_visit.pop()
            if current not in all_downstream:
                all_downstream.add(current)
                children = self._downstream_index.get(current, set())
                to_visit.extend(children)

        return list(all_downstream)

    async def recompute_on_change(
        self,
        kblock_id: str,
        new_content: str | None = None,
    ) -> None:
        """
        Recompute derivation when K-Block content changes.

        This is called when a K-Block is edited. It:
        1. Recomputes the Galois loss
        2. Updates grounding status if necessary
        3. Propagates changes to downstream K-Blocks

        Args:
            kblock_id: The K-Block that changed
            new_content: New content (if available)

        Example:
            >>> await service.recompute_on_change("kb_123", "Updated content...")
        """
        context = self._contexts.get(kblock_id)
        if context is None:
            logger.warning(f"No derivation context for {kblock_id}")
            return

        # Recompute loss if we have new content
        if new_content:
            result = await self._compute_content_loss(new_content)
            new_loss = result.loss

            # Update witnesses
            witnesses = list(context.witnesses)
            witnesses.append(PathWitness.from_galois(new_loss, method="recompute"))

            # Determine new status
            if context.source_principle and new_loss < GROUNDING_THRESHOLD:
                new_status = "grounded"
            elif context.source_principle and new_loss < PROVISIONAL_THRESHOLD:
                new_status = "provisional"
            else:
                new_status = "orphan"

            # Update context
            self._contexts[kblock_id] = DerivationContext(
                source_principle=context.source_principle,
                galois_loss=new_loss,
                grounding_status=new_status,
                parent_kblock_id=context.parent_kblock_id,
                derivation_path=context.derivation_path,
                witnesses=witnesses,
            )

            logger.info(f"Recomputed {kblock_id}: loss={new_loss:.3f}, status={new_status}")

        # Propagate to downstream K-Blocks (they'll recompute when accessed)
        downstream = await self.get_downstream(kblock_id)
        for child_id in downstream:
            child_context = self._contexts.get(child_id)
            if child_context:
                # Mark as needing recomputation (could set a flag)
                logger.debug(f"Downstream {child_id} may need recomputation")

    def get_context(self, kblock_id: str) -> DerivationContext | None:
        """
        Get the derivation context for a K-Block.

        Args:
            kblock_id: The K-Block ID

        Returns:
            DerivationContext or None if not found
        """
        return self._contexts.get(kblock_id)

    def get_all_contexts(self) -> dict[str, DerivationContext]:
        """
        Get all stored derivation contexts.

        Returns:
            Dictionary mapping K-Block ID to DerivationContext
        """
        return dict(self._contexts)

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    async def _compute_content_loss(self, content: str) -> GaloisLoss:
        """
        Compute Galois loss for content.

        Uses cached values when available.
        """
        return await compute_galois_loss_async(
            content,
            use_cache=True,
            cache=self.loss_cache,
        )

    def _generate_reasoning(
        self,
        principle: str,
        content: str,
        loss: float,
    ) -> str:
        """
        Generate human-readable reasoning for a grounding suggestion.
        """
        coherence = 1.0 - loss
        description = PRINCIPLE_DESCRIPTIONS.get(principle, principle)

        if coherence >= 0.8:
            strength = "strongly"
        elif coherence >= 0.6:
            strength = "moderately"
        elif coherence >= 0.4:
            strength = "weakly"
        else:
            strength = "marginally"

        # Extract first sentence of content for context
        first_sentence = content.split(".")[0][:50]
        if len(first_sentence) < len(content.split(".")[0]):
            first_sentence += "..."

        return (
            f"Content {strength} aligns with {principle}: "
            f'"{description[:60]}...". '
            f"Coherence: {coherence:.0%}"
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_derivation_service(
    dag: DerivationDAG | None = None,
    witness_bridge: DerivationWitnessBridge | None = None,
) -> KBlockDerivationService:
    """
    Create a KBlockDerivationService with defaults.

    Args:
        dag: Optional DerivationDAG (defaults to new empty DAG)
        witness_bridge: Optional witness bridge (defaults to no-op)

    Returns:
        Configured KBlockDerivationService
    """
    return KBlockDerivationService(
        dag=dag or DerivationDAG(),
        witness_bridge=witness_bridge or NullDerivationWitnessBridge(),
    )


# Module-level service instance (set by external configuration)
_service: KBlockDerivationService | None = None


def get_derivation_service() -> KBlockDerivationService:
    """
    Get the global derivation service instance.

    Creates a new instance if none exists.
    """
    global _service
    if _service is None:
        _service = create_derivation_service()
    return _service


def set_derivation_service(service: KBlockDerivationService | None) -> None:
    """
    Set the global derivation service instance.

    Pass None to reset.
    """
    global _service
    _service = service


def reset_derivation_service() -> None:
    """Reset the global derivation service to None."""
    global _service
    _service = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "PRINCIPLES",
    "PRINCIPLE_DESCRIPTIONS",
    "GROUNDING_THRESHOLD",
    "PROVISIONAL_THRESHOLD",
    # Types
    "GroundingSuggestion",
    "DerivationContext",
    "DerivationWitnessBridge",
    # Service
    "KBlockDerivationService",
    # Factory
    "create_derivation_service",
    "get_derivation_service",
    "set_derivation_service",
    "reset_derivation_service",
]
