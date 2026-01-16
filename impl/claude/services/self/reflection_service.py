"""
Self-Reflection Service: Constitutional Introspection + Drift Detection.

"The compiler that knows itself is the compiler that trusts itself."

This service provides the core business logic for constitutional
introspection - enabling agents to query, navigate, and derive from
the 22 Constitutional K-Blocks that ground all kgents operations.

The service:
1. Wraps GenesisKBlockFactory for access to the 22 K-Blocks
2. Builds derivation graphs for constitutional navigation
3. Computes Galois loss for derivation chains
4. Supports layer-based filtering (L0-L3)
5. Detects spec/impl drift and orphaned K-Blocks (NEW)
6. Tracks principle coverage (NEW)

Philosophy:
    "The system illuminates, not enforces. Drift is not failure—
     it's the natural cost of creating. What matters is knowing."

See: services/zero_seed/genesis_kblocks.py for K-Block definitions
See: spec/bootstrap.md for axiom specifications
See: spec/protocols/zero-seed1/ashc.md for ASHC derivation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from services.zero_seed.genesis_kblocks import GenesisKBlock, GenesisKBlockFactory

if TYPE_CHECKING:
    from .derivation_analyzer import DerivationAnalyzer as DriftAnalyzer
    from .drift_service import DriftReport, DriftService


# =============================================================================
# Response Types
# =============================================================================


@dataclass(frozen=True)
class KBlockSummary:
    """
    Summary of a K-Block for graph views.

    Lighter-weight than full GenesisKBlock for efficient navigation.
    """

    id: str
    title: str
    layer: int
    galois_loss: float
    derives_from: tuple[str, ...]
    tags: tuple[str, ...]

    @classmethod
    def from_genesis(cls, kblock: GenesisKBlock) -> "KBlockSummary":
        """Create summary from a full GenesisKBlock."""
        return cls(
            id=kblock.id,
            title=kblock.title,
            layer=kblock.layer,
            galois_loss=kblock.galois_loss,
            derives_from=kblock.derives_from,
            tags=kblock.tags,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "layer": self.layer,
            "galois_loss": self.galois_loss,
            "derives_from": list(self.derives_from),
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class ConstitutionalGraph:
    """
    The Constitutional graph structure.

    Represents the 22 K-Blocks organized by layer with derivation edges.
    """

    # K-Blocks organized by layer
    axioms: tuple[KBlockSummary, ...]  # L0
    kernel: tuple[KBlockSummary, ...]  # L1
    derived: tuple[KBlockSummary, ...]  # L2
    principles: tuple[KBlockSummary, ...]  # L1-L2 (Constitution + 7 principles)
    architecture: tuple[KBlockSummary, ...]  # L3

    # Derivation edges: (from_id, to_id, derivation_type)
    edges: tuple[tuple[str, str, str], ...]

    # Statistics
    total_blocks: int
    total_edges: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "axioms": [b.to_dict() for b in self.axioms],
            "kernel": [b.to_dict() for b in self.kernel],
            "derived": [b.to_dict() for b in self.derived],
            "principles": [b.to_dict() for b in self.principles],
            "architecture": [b.to_dict() for b in self.architecture],
            "edges": [{"from": e[0], "to": e[1], "type": e[2]} for e in self.edges],
            "total_blocks": self.total_blocks,
            "total_edges": self.total_edges,
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [
            "Constitutional Graph",
            "===================",
            f"Total K-Blocks: {self.total_blocks}",
            f"Total Edges: {self.total_edges}",
            "",
            "L0 Axioms:",
        ]
        for b in self.axioms:
            lines.append(f"  - {b.id}: {b.title}")
        lines.append("\nL1 Kernel:")
        for b in self.kernel:
            lines.append(f"  - {b.id}: {b.title}")
        lines.append("\nL2 Derived:")
        for b in self.derived:
            lines.append(f"  - {b.id}: {b.title}")
        lines.append("\nL1-L2 Principles:")
        for b in self.principles:
            lines.append(f"  - {b.id}: {b.title}")
        lines.append("\nL3 Architecture:")
        for b in self.architecture:
            lines.append(f"  - {b.id}: {b.title}")
        return "\n".join(lines)


@dataclass(frozen=True)
class DerivationStep:
    """A single step in a derivation chain."""

    kblock_id: str
    title: str
    layer: int
    galois_loss: float
    step_index: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "kblock_id": self.kblock_id,
            "title": self.title,
            "layer": self.layer,
            "galois_loss": self.galois_loss,
            "step_index": self.step_index,
        }


@dataclass(frozen=True)
class DerivationChain:
    """
    A derivation chain from a K-Block back to axioms.

    Shows the path from a derived concept to its axiomatic foundations.
    """

    source_id: str
    source_title: str
    steps: tuple[DerivationStep, ...]
    total_loss: float
    reaches_axiom: bool
    axiom_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_id": self.source_id,
            "source_title": self.source_title,
            "steps": [s.to_dict() for s in self.steps],
            "total_loss": self.total_loss,
            "reaches_axiom": self.reaches_axiom,
            "axiom_ids": list(self.axiom_ids),
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [
            f"Derivation Chain: {self.source_id}",
            f"Source: {self.source_title}",
            f"Total Galois Loss: {self.total_loss:.3f}",
            f"Reaches Axioms: {self.reaches_axiom}",
            "",
            "Chain:",
        ]
        for step in self.steps:
            indent = "  " * step.step_index
            lines.append(f"{indent}{step.kblock_id} (L{step.layer}, loss={step.galois_loss:.3f})")
        if self.axiom_ids:
            lines.append(f"\nGrounded in: {', '.join(self.axiom_ids)}")
        return "\n".join(lines)


@dataclass(frozen=True)
class KBlockInspection:
    """
    Deep inspection of a single K-Block.

    Includes full content and all relationships.
    """

    kblock: GenesisKBlock
    parents: tuple[KBlockSummary, ...]  # K-Blocks this derives from
    children: tuple[KBlockSummary, ...]  # K-Blocks that derive from this
    derivation_chain: DerivationChain

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.kblock.id,
            "title": self.kblock.title,
            "layer": self.kblock.layer,
            "galois_loss": self.kblock.galois_loss,
            "content": self.kblock.content,
            "derives_from": list(self.kblock.derives_from),
            "tags": list(self.kblock.tags),
            "parents": [p.to_dict() for p in self.parents],
            "children": [c.to_dict() for c in self.children],
            "derivation_chain": self.derivation_chain.to_dict(),
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [
            f"K-Block: {self.kblock.id}",
            f"Title: {self.kblock.title}",
            f"Layer: L{self.kblock.layer}",
            f"Galois Loss: {self.kblock.galois_loss:.3f}",
            f"Tags: {', '.join(self.kblock.tags)}",
            "",
            "Parents:",
        ]
        for p in self.parents:
            lines.append(f"  - {p.id}")
        lines.append("\nChildren:")
        for c in self.children:
            lines.append(f"  - {c.id}")
        lines.append("\n--- Content ---\n")
        lines.append(self.kblock.content)
        return "\n".join(lines)


# =============================================================================
# Self-Reflection Service
# =============================================================================


@dataclass
class SelfReflectionService:
    """
    Service for Constitutional self-reflection.

    Provides methods for querying and navigating the 22 Constitutional
    K-Blocks that form the axiomatic foundation of kgents.

    Example:
        service = SelfReflectionService()

        # Get the full Constitutional graph
        graph = await service.get_constitution()

        # Navigate derivation chain from a K-Block
        chain = await service.get_derivation_chain("ASHC")

        # Deep inspect a K-Block
        inspection = await service.inspect("A3_MIRROR")
    """

    _factory: GenesisKBlockFactory = field(default_factory=GenesisKBlockFactory)
    _blocks_cache: dict[str, GenesisKBlock] | None = field(default=None)

    def _get_all_blocks(self) -> dict[str, GenesisKBlock]:
        """Get all K-Blocks indexed by ID (cached)."""
        if self._blocks_cache is None:
            blocks = self._factory.create_all()
            self._blocks_cache = {b.id: b for b in blocks}
        return self._blocks_cache

    def _build_edges(self, blocks: dict[str, GenesisKBlock]) -> list[tuple[str, str, str]]:
        """Build derivation edges from K-Block relationships."""
        edges: list[tuple[str, str, str]] = []
        for kblock in blocks.values():
            for parent_id in kblock.derives_from:
                if parent_id in blocks:
                    edges.append((parent_id, kblock.id, "derives_from"))
        return edges

    async def get_constitution(
        self,
        layer: str | int | None = None,
    ) -> ConstitutionalGraph:
        """
        Get the Constitutional graph.

        Args:
            layer: Optional layer filter (0-3 or "axioms", "kernel", "derived",
                   "principles", "architecture")

        Returns:
            ConstitutionalGraph with all K-Blocks and edges
        """
        blocks = self._get_all_blocks()

        # Categorize blocks by layer/type
        axioms = tuple(
            KBlockSummary.from_genesis(b)
            for b in blocks.values()
            if b.layer == 0 and b.id in ("A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS")
        )
        kernel = tuple(
            KBlockSummary.from_genesis(b)
            for b in blocks.values()
            if b.layer == 1 and b.id in ("COMPOSE", "JUDGE", "GROUND")
        )
        derived = tuple(
            KBlockSummary.from_genesis(b)
            for b in blocks.values()
            if b.layer == 2 and b.id in ("ID", "CONTRADICT", "SUBLATE", "FIX")
        )
        principles = tuple(
            KBlockSummary.from_genesis(b)
            for b in blocks.values()
            if b.id
            in (
                "CONSTITUTION",
                "TASTEFUL",
                "CURATED",
                "ETHICAL",
                "JOY_INDUCING",
                "COMPOSABLE",
                "HETERARCHICAL",
                "GENERATIVE",
            )
        )
        architecture = tuple(KBlockSummary.from_genesis(b) for b in blocks.values() if b.layer == 3)

        edges = tuple(self._build_edges(blocks))

        return ConstitutionalGraph(
            axioms=axioms,
            kernel=kernel,
            derived=derived,
            principles=principles,
            architecture=architecture,
            edges=edges,
            total_blocks=len(blocks),
            total_edges=len(edges),
        )

    async def get_derivation_chain(self, kblock_id: str) -> DerivationChain:
        """
        Get the derivation chain from a K-Block back to axioms.

        Args:
            kblock_id: The K-Block ID to trace

        Returns:
            DerivationChain showing the path to axioms
        """
        blocks = self._get_all_blocks()

        if kblock_id not in blocks:
            # Return empty chain for unknown K-Block
            return DerivationChain(
                source_id=kblock_id,
                source_title="Unknown",
                steps=(),
                total_loss=1.0,
                reaches_axiom=False,
                axiom_ids=(),
            )

        source = blocks[kblock_id]
        steps: list[DerivationStep] = []
        visited: set[str] = set()
        axiom_ids: list[str] = []
        total_loss = source.galois_loss

        def trace_derivation(block_id: str, step_index: int) -> None:
            """Recursively trace derivation chain."""
            if block_id in visited:
                return
            visited.add(block_id)

            block = blocks.get(block_id)
            if block is None:
                return

            steps.append(
                DerivationStep(
                    kblock_id=block.id,
                    title=block.title,
                    layer=block.layer,
                    galois_loss=block.galois_loss,
                    step_index=step_index,
                )
            )

            # Check if this is an axiom (L0 with no parents)
            if block.layer == 0 and not block.derives_from:
                axiom_ids.append(block.id)
                return

            # Trace parents
            for parent_id in block.derives_from:
                trace_derivation(parent_id, step_index + 1)

        trace_derivation(kblock_id, 0)

        return DerivationChain(
            source_id=kblock_id,
            source_title=source.title,
            steps=tuple(steps),
            total_loss=total_loss,
            reaches_axiom=len(axiom_ids) > 0,
            axiom_ids=tuple(axiom_ids),
        )

    async def inspect(self, kblock_id: str) -> KBlockInspection:
        """
        Deep inspect a K-Block.

        Args:
            kblock_id: The K-Block ID to inspect

        Returns:
            KBlockInspection with full content and relationships
        """
        blocks = self._get_all_blocks()

        if kblock_id not in blocks:
            # Return inspection for unknown K-Block
            unknown = GenesisKBlock(
                id=kblock_id,
                title="Unknown K-Block",
                layer=7,
                galois_loss=1.0,
                content=f"K-Block '{kblock_id}' not found in the Constitutional foundation.",
                derives_from=(),
                tags=("unknown",),
            )
            return KBlockInspection(
                kblock=unknown,
                parents=(),
                children=(),
                derivation_chain=DerivationChain(
                    source_id=kblock_id,
                    source_title="Unknown",
                    steps=(),
                    total_loss=1.0,
                    reaches_axiom=False,
                    axiom_ids=(),
                ),
            )

        kblock = blocks[kblock_id]

        # Find parents
        parents = tuple(
            KBlockSummary.from_genesis(blocks[pid]) for pid in kblock.derives_from if pid in blocks
        )

        # Find children (K-Blocks that derive from this one)
        children = tuple(
            KBlockSummary.from_genesis(b) for b in blocks.values() if kblock_id in b.derives_from
        )

        # Get derivation chain
        chain = await self.get_derivation_chain(kblock_id)

        return KBlockInspection(
            kblock=kblock,
            parents=parents,
            children=children,
            derivation_chain=chain,
        )

    async def get_axioms(self) -> list[GenesisKBlock]:
        """Get all L0 axiom K-Blocks."""
        return self._factory.create_axioms()

    async def get_principles(self) -> list[GenesisKBlock]:
        """Get the Constitution and all 7 principle K-Blocks."""
        return self._factory.create_principles()

    async def get_architecture(self) -> list[GenesisKBlock]:
        """Get all L3 architecture K-Blocks."""
        return self._factory.create_architecture()

    async def get_by_layer(self, layer: int) -> list[GenesisKBlock]:
        """Get all K-Blocks for a specific layer."""
        return self._factory.create_by_layer(layer)

    # =========================================================================
    # Drift Detection Methods (NEW - integrates with DriftService)
    # =========================================================================

    async def get_drift_report(self) -> "DriftReport":
        """
        Get comprehensive drift analysis report.

        Analyzes all K-Blocks for:
        1. Orphan status (no derivation roots)
        2. High Galois loss (semantic drift)
        3. Ungrounded chains (don't reach axioms)
        4. Principle coverage

        Returns:
            DriftReport with spec/impl divergence analysis

        Philosophy: "The report is a mirror, not a judge."
        """
        from .drift_service import get_drift_service

        drift_service = get_drift_service()
        return await drift_service.get_drift_report()

    async def compute_principle_coverage(self) -> dict[str, float]:
        """
        Compute coverage score for each constitutional principle.

        Coverage = (# K-Blocks grounded in principle) / (total grounded K-Blocks)

        Returns:
            Dictionary mapping principle name to coverage score (0.0 - 1.0)

        Philosophy: "Which principles are we living? Which are we neglecting?"
        """
        from .drift_service import get_drift_service

        drift_service = get_drift_service()
        return await drift_service.compute_principle_coverage()

    async def get_orphans(self) -> list[str]:
        """
        Get list of orphaned K-Block IDs.

        An orphan is a K-Block that has no derivation root to L1 axioms.

        Returns:
            List of K-Block IDs without derivation roots

        Philosophy: "Orphans are not failure—they're opportunities to ground."
        """
        from .drift_service import get_drift_service

        drift_service = get_drift_service()
        return await drift_service.get_orphans()


# =============================================================================
# Factory Function
# =============================================================================


def get_reflection_service() -> SelfReflectionService:
    """
    Get a SelfReflectionService instance.

    Returns:
        A configured SelfReflectionService
    """
    return SelfReflectionService()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "KBlockSummary",
    "ConstitutionalGraph",
    "DerivationStep",
    "DerivationChain",
    "KBlockInspection",
    # Service
    "SelfReflectionService",
    "get_reflection_service",
]
