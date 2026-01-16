"""
Derivation Analyzer: Trace K-Blocks to Axioms.

Analyzes derivation chains for coherence using Galois loss computation
and the DerivationDAG from K-Block core.

Philosophy:
    "The proof IS the decision. The derivation IS the lineage.
     Orphans are not failure—they're opportunities to ground."

Key Capabilities:
1. trace_to_axioms: Follow derivation chain back to L1 axioms
2. find_orphans: Discover K-Blocks without derivation roots
3. compute_chain_loss: Galois loss for entire derivation chain

See: spec/protocols/zero-seed1/ashc.md
See: services/k_block/derivation_service.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from services.k_block.core.derivation import DerivationDAG, DerivationNode
from services.k_block.derivation_service import (
    DerivationContext,
    KBlockDerivationService,
    get_derivation_service,
)
from services.zero_seed.galois.galois_loss import (
    GaloisLossComputer,
    LossCache,
    compute_galois_loss_async,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.self.derivation_analyzer")


# =============================================================================
# Constants
# =============================================================================

# Galois loss thresholds
HIGH_LOSS_THRESHOLD = 0.6  # Loss considered concerning
CRITICAL_LOSS_THRESHOLD = 0.8  # Loss requiring immediate attention
AXIOM_LOSS_THRESHOLD = 0.05  # Maximum loss for axiom-level content


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class DerivationStep:
    """
    A single step in a derivation chain.

    Represents one K-Block in the chain with its derivation metadata.
    """

    kblock_id: str
    layer: int
    kind: str
    parent_ids: tuple[str, ...]
    galois_loss: float
    grounding_status: str
    source_principle: str | None

    @property
    def coherence(self) -> float:
        """Coherence = 1 - galois_loss."""
        return 1.0 - self.galois_loss

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "kblock_id": self.kblock_id,
            "layer": self.layer,
            "kind": self.kind,
            "parent_ids": list(self.parent_ids),
            "galois_loss": self.galois_loss,
            "coherence": self.coherence,
            "grounding_status": self.grounding_status,
            "source_principle": self.source_principle,
        }


@dataclass(frozen=True)
class DerivationChain:
    """
    A complete derivation chain from a K-Block to its axiom roots.

    Captures the full lineage with accumulated Galois loss.

    Philosophy: "Every K-Block should trace back to axioms.
                The chain IS the proof of groundedness."
    """

    target_kblock_id: str
    steps: tuple[DerivationStep, ...]
    total_galois_loss: float
    is_grounded: bool
    root_axiom_ids: tuple[str, ...]
    source_principles: tuple[str, ...]

    @property
    def chain_length(self) -> int:
        """Number of steps in the chain."""
        return len(self.steps)

    @property
    def coherence(self) -> float:
        """Overall chain coherence = 1 - total_galois_loss."""
        return 1.0 - self.total_galois_loss

    @property
    def is_orphan(self) -> bool:
        """True if chain has no grounded roots."""
        return not self.is_grounded and len(self.root_axiom_ids) == 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "target_kblock_id": self.target_kblock_id,
            "steps": [s.to_dict() for s in self.steps],
            "total_galois_loss": self.total_galois_loss,
            "coherence": self.coherence,
            "is_grounded": self.is_grounded,
            "is_orphan": self.is_orphan,
            "root_axiom_ids": list(self.root_axiom_ids),
            "source_principles": list(self.source_principles),
            "chain_length": self.chain_length,
        }


@dataclass(frozen=True)
class OrphanReport:
    """
    Report of orphaned K-Blocks without derivation roots.

    Philosophy: "Orphans are not failure—they're opportunities."
    """

    orphan_ids: tuple[str, ...]
    orphan_details: tuple[dict[str, Any], ...]
    total_count: int
    by_layer: dict[int, int]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "orphan_ids": list(self.orphan_ids),
            "orphan_details": list(self.orphan_details),
            "total_count": self.total_count,
            "by_layer": self.by_layer,
        }


# =============================================================================
# DerivationAnalyzer
# =============================================================================


@dataclass
class DerivationAnalyzer:
    """
    Analyze derivation chains for coherence.

    Integrates with:
    - DerivationDAG: For lineage traversal
    - KBlockDerivationService: For derivation context
    - Galois Loss: For semantic coherence measurement

    Philosophy:
        "The system illuminates, not enforces. We trace, we measure,
         we surface. The human decides what to ground."

    Usage:
        >>> analyzer = create_derivation_analyzer()
        >>> chain = await analyzer.trace_to_axioms("kb_some_id")
        >>> print(f"Chain grounded: {chain.is_grounded}")
        >>> orphans = await analyzer.find_orphans()
        >>> print(f"Found {len(orphans.orphan_ids)} orphans")
    """

    derivation_service: KBlockDerivationService = field(default_factory=get_derivation_service)
    loss_cache: LossCache = field(default_factory=LossCache)

    async def trace_to_axioms(self, kblock_id: str) -> DerivationChain:
        """
        Trace a K-Block's derivation chain back to L1 axioms.

        Follows the derivation DAG from the target K-Block to its roots,
        accumulating Galois loss along the way.

        Args:
            kblock_id: The K-Block to trace

        Returns:
            DerivationChain with full lineage and accumulated loss

        Philosophy: "The chain IS the proof. If you can't trace to axioms,
                    you're building on sand."
        """
        # Get the derivation DAG
        dag = self.derivation_service.dag

        # Check if K-Block exists in DAG
        node = dag.get_node(kblock_id)
        if node is None:
            # K-Block not in DAG - return orphan chain
            return DerivationChain(
                target_kblock_id=kblock_id,
                steps=(),
                total_galois_loss=1.0,  # Maximum loss for orphan
                is_grounded=False,
                root_axiom_ids=(),
                source_principles=(),
            )

        # Traverse to roots
        steps: list[DerivationStep] = []
        visited: set[str] = set()
        stack: list[str] = [kblock_id]
        root_axiom_ids: list[str] = []
        source_principles: set[str] = set()
        accumulated_loss = 0.0

        while stack:
            current_id = stack.pop()
            if current_id in visited:
                continue
            visited.add(current_id)

            current_node = dag.get_node(current_id)
            if current_node is None:
                continue

            # Get derivation context for this K-Block
            context = self.derivation_service.get_context(current_id)
            galois_loss = context.galois_loss if context else 0.5
            grounding_status = context.grounding_status if context else "orphan"
            principle = context.source_principle if context else None

            if principle:
                source_principles.add(principle)

            # Create step
            step = DerivationStep(
                kblock_id=current_id,
                layer=current_node.layer,
                kind=current_node.kind,
                parent_ids=tuple(current_node.parent_ids),
                galois_loss=galois_loss,
                grounding_status=grounding_status,
                source_principle=principle,
            )
            steps.append(step)

            # Accumulate loss: L(chain) = 1 - product of (1 - L(step))
            accumulated_loss = 1.0 - (1.0 - accumulated_loss) * (1.0 - galois_loss)

            # Check if this is a root (L1 axiom with no parents)
            if current_node.layer == 1 and not current_node.parent_ids:
                root_axiom_ids.append(current_id)
            else:
                # Add parents to stack
                stack.extend(current_node.parent_ids)

        # Determine if grounded
        is_grounded = len(root_axiom_ids) > 0 or dag.is_grounded(kblock_id)

        return DerivationChain(
            target_kblock_id=kblock_id,
            steps=tuple(steps),
            total_galois_loss=accumulated_loss,
            is_grounded=is_grounded,
            root_axiom_ids=tuple(root_axiom_ids),
            source_principles=tuple(source_principles),
        )

    async def find_orphans(self) -> OrphanReport:
        """
        Find K-Blocks without derivation roots (orphans).

        An orphan is a K-Block that:
        1. Has no parent derivations, AND
        2. Is not an L1 axiom, AND
        3. Has grounding_status == "orphan"

        Returns:
            OrphanReport with all orphaned K-Blocks

        Philosophy: "Orphans are not failure—they're opportunities to ground."
        """
        dag = self.derivation_service.dag
        contexts = self.derivation_service.get_all_contexts()

        orphan_ids: list[str] = []
        orphan_details: list[dict[str, Any]] = []
        by_layer: dict[int, int] = {}

        # Check all K-Blocks with contexts
        for kblock_id, context in contexts.items():
            if context.grounding_status == "orphan":
                node = dag.get_node(kblock_id)
                layer = node.layer if node else 0

                orphan_ids.append(kblock_id)
                orphan_details.append(
                    {
                        "kblock_id": kblock_id,
                        "layer": layer,
                        "galois_loss": context.galois_loss,
                        "has_parent": context.parent_kblock_id is not None,
                    }
                )

                by_layer[layer] = by_layer.get(layer, 0) + 1

        # Also check DAG nodes without contexts
        for node_id in list(dag._nodes.keys()):
            if node_id not in contexts:
                node = dag.get_node(node_id)
                if node and node.layer != 1 and not node.parent_ids:
                    orphan_ids.append(node_id)
                    orphan_details.append(
                        {
                            "kblock_id": node_id,
                            "layer": node.layer,
                            "galois_loss": 1.0,  # Unknown, assume worst
                            "has_parent": False,
                        }
                    )
                    by_layer[node.layer] = by_layer.get(node.layer, 0) + 1

        return OrphanReport(
            orphan_ids=tuple(orphan_ids),
            orphan_details=tuple(orphan_details),
            total_count=len(orphan_ids),
            by_layer=by_layer,
        )

    async def compute_galois_loss(self, chain: DerivationChain) -> float:
        """
        Compute or validate Galois loss for a derivation chain.

        Uses cached values where available.

        Args:
            chain: The derivation chain to analyze

        Returns:
            Total Galois loss for the chain
        """
        if not chain.steps:
            return 1.0  # Empty chain has maximum loss

        # Accumulate loss from steps
        total_loss = 0.0
        for step in chain.steps:
            total_loss = 1.0 - (1.0 - total_loss) * (1.0 - step.galois_loss)

        return total_loss

    async def get_chain_health(self, kblock_id: str) -> dict[str, Any]:
        """
        Get comprehensive health report for a K-Block's derivation chain.

        Returns:
            Health report with loss classification and recommendations
        """
        chain = await self.trace_to_axioms(kblock_id)

        # Classify health
        if chain.total_galois_loss < AXIOM_LOSS_THRESHOLD:
            health = "excellent"
            recommendation = None
        elif chain.total_galois_loss < HIGH_LOSS_THRESHOLD:
            health = "good"
            recommendation = None
        elif chain.total_galois_loss < CRITICAL_LOSS_THRESHOLD:
            health = "concerning"
            recommendation = "Consider strengthening derivation witnesses"
        else:
            health = "critical"
            recommendation = "Urgent: Ground this K-Block to principles"

        return {
            "kblock_id": kblock_id,
            "health": health,
            "total_loss": chain.total_galois_loss,
            "coherence": chain.coherence,
            "is_grounded": chain.is_grounded,
            "is_orphan": chain.is_orphan,
            "chain_length": chain.chain_length,
            "source_principles": list(chain.source_principles),
            "recommendation": recommendation,
        }


# =============================================================================
# Factory Functions
# =============================================================================

# Module-level analyzer instance
_analyzer: DerivationAnalyzer | None = None


def create_derivation_analyzer(
    derivation_service: KBlockDerivationService | None = None,
) -> DerivationAnalyzer:
    """
    Create a DerivationAnalyzer instance.

    Args:
        derivation_service: Optional derivation service (defaults to global)

    Returns:
        Configured DerivationAnalyzer
    """
    return DerivationAnalyzer(
        derivation_service=derivation_service or get_derivation_service(),
    )


def get_derivation_analyzer() -> DerivationAnalyzer:
    """
    Get the global DerivationAnalyzer instance.

    Creates a new instance if none exists.
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = create_derivation_analyzer()
    return _analyzer


def set_derivation_analyzer(analyzer: DerivationAnalyzer | None) -> None:
    """Set the global analyzer instance (for testing)."""
    global _analyzer
    _analyzer = analyzer


def reset_derivation_analyzer() -> None:
    """Reset the global analyzer instance."""
    global _analyzer
    _analyzer = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "DerivationStep",
    "DerivationChain",
    "OrphanReport",
    # Analyzer
    "DerivationAnalyzer",
    # Factory
    "create_derivation_analyzer",
    "get_derivation_analyzer",
    "set_derivation_analyzer",
    "reset_derivation_analyzer",
    # Constants
    "HIGH_LOSS_THRESHOLD",
    "CRITICAL_LOSS_THRESHOLD",
    "AXIOM_LOSS_THRESHOLD",
]
