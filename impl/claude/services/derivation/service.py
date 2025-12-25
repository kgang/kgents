"""
DerivationService: Track and query causal lineage across the Crystal taxonomy.

Every artifact justifies itself by tracing back to axioms. This service provides:
1. Lineage tracing (crystal → ancestors → axioms)
2. Derivation tree queries (full ancestry + descendants)
3. Drift detection (spec/impl coherence measurement)
4. Orphan detection (crystals with no axiomatic grounding)
5. Edge creation (link derivations with witness marks)

Philosophy:
    "The proof IS the decision. The derivation IS the lineage."

    Every crystal has a derivation path. When we ask "why does this exist?",
    we consult its lineage. When we ask "is this coherent?", we compute
    accumulated Galois loss along the derivation chain.

Architecture:
    DerivationService wraps Universe and provides Crystal-aware queries.
    It uses KBlockEdge to track relationships and GaloisLossComputer for
    coherence measurement.

Teaching:
    gotcha: Crystal IDs are stored in Universe with schema metadata.
            Query by schema="code.function" to find FunctionCrystals.
            (Evidence: agents/d/universe/universe.py::Universe.query)

    gotcha: Edge types map to derivation semantics:
            - "derives_from": General derivation (parent → child)
            - "implements": Spec → Code (L4 → L5)
            - "tests": Test → Code coverage
            - "justifies": Axiom/Value → downstream (L1/L2 → L3+)
            (Evidence: k_block/core/edge.py::KBlockEdge)

    gotcha: Layer monotonicity is enforced: parent layer < child layer.
            Axioms (L1) cannot have parents. Values (L2) derive from axioms.
            (Evidence: k_block/core/derivation.py::validate_derivation)

See: spec/protocols/zero-seed.md
See: services/k_block/core/derivation.py (K-Block DAG implementation)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.d.galois import GaloisLossComputer
    from agents.d.universe import Universe

from services.k_block.core.edge import KBlockEdge


# =============================================================================
# Layer Constants (Zero Seed Holarchy)
# =============================================================================

LAYER_NAMES = {
    1: "axiom",         # L1: AxiomCrystal (foundational truths)
    2: "value",         # L2: ValueCrystal (derived principles)
    3: "prompt",        # L3: PromptCrystal (LLM templates)
    4: "spec",          # L4: SpecCrystal (specifications)
    5: "code",          # L5: FunctionCrystal, TestCrystal (implementations)
    6: "reflection",    # L6: ReflectionCrystal (meta-analysis)
    7: "interpretation", # L7: InterpretationCrystal (meaning-making)
}

EDGE_KIND_TO_TYPE = {
    "GROUNDS": "derives_from",   # L1/L2 → L3+ (axiomatic grounding)
    "JUSTIFIES": "derives_from", # General justification
    "SPECIFIES": "derives_from", # Spec defines something
    "IMPLEMENTS": "implements",  # Code implements spec
    "TESTS": "tests",            # Test covers code
    "DERIVES": "derives_from",   # General derivation
}


# =============================================================================
# Data Structures
# =============================================================================

@dataclass(frozen=True)
class CrystalRef:
    """
    Reference to a crystal in the derivation chain.

    Captures identity, layer, type, and the edge connecting it to the next node.
    """

    id: str
    """Crystal ID in Universe."""

    layer: int
    """Zero Seed layer (1-7)."""

    crystal_type: str
    """Crystal type (axiom, value, prompt, spec, function, etc.)."""

    edge_kind: str
    """Edge semantic type (GROUNDS, JUSTIFIES, SPECIFIES, IMPLEMENTS)."""

    galois_loss: float
    """Galois loss at this edge (accumulated if chained)."""


@dataclass
class DerivationChain:
    """
    A chain of crystals from target back to axioms.

    Represents a single path through the derivation DAG.
    Captures accumulated loss and grounding status.
    """

    target_id: str
    """The crystal we're tracing from."""

    chain: list[CrystalRef]
    """Ordered list from target → ancestors (toward axioms)."""

    total_galois_loss: float
    """Accumulated loss along this chain."""

    is_grounded: bool
    """Does this chain reach L1 or L2 axioms/values?"""

    def coherence(self) -> float:
        """Coherence = 1 - total_galois_loss."""
        return max(0.0, 1.0 - self.total_galois_loss)


@dataclass
class DerivationTree:
    """
    Full derivation tree (ancestors + descendants) for a crystal.

    Captures both upward lineage (to axioms) and downward impact (dependents).
    """

    crystal_id: str
    """The crystal at the root of this tree."""

    ancestors: list[CrystalRef]
    """All ancestors (parents, grandparents, ..., axioms)."""

    descendants: list[CrystalRef]
    """All descendants (children, grandchildren, ...)."""

    is_grounded: bool
    """Does ancestor chain reach axioms?"""

    total_loss_to_axioms: float
    """Accumulated loss from this crystal to axioms."""


@dataclass
class DriftReport:
    """
    Report of spec/impl drift.

    Measures coherence between a specification crystal and its implementations.
    """

    spec_id: str
    """The specification crystal ID."""

    impl_id: str
    """The implementation crystal ID."""

    drift_severity: float
    """Drift severity in [0, 1] (higher = more drift)."""

    drift_type: str
    """Type of drift (spec_changed, impl_diverged, missing_impl)."""

    details: str
    """Human-readable explanation of the drift."""


# =============================================================================
# DerivationService
# =============================================================================

class DerivationService:
    """
    Track and query derivation relationships across the Crystal taxonomy.

    Every artifact justifies itself by tracing back to axioms. This service:
    - Traces lineage (crystal → ancestors → axioms)
    - Detects drift (spec/impl divergence)
    - Finds orphans (crystals with no grounding)
    - Links derivations (create edges with witness marks)

    Architecture:
        DerivationService = Universe (storage) + KBlockEdge (relationships)
                          + GaloisLossComputer (coherence)

    Usage:
        >>> service = DerivationService(universe, galois)
        >>> chain = await service.trace_to_axiom("crystal-abc123")
        >>> print(f"Grounded: {chain.is_grounded}, Loss: {chain.total_galois_loss:.2f}")
    """

    def __init__(
        self,
        universe: Universe,
        galois: GaloisLossComputer | None = None,
    ):
        """
        Initialize DerivationService.

        Args:
            universe: Universe instance for Crystal storage
            galois: Optional GaloisLossComputer for coherence measurement
        """
        self._universe = universe
        self._galois = galois
        self._edges: dict[str, list[KBlockEdge]] = {}  # source_id → edges

    async def trace_to_axiom(self, crystal_id: str) -> DerivationChain:
        """
        Trace any crystal back to its axiomatic ground.

        Follows derived_from links until reaching L1-L2 (axioms/values).

        Args:
            crystal_id: Crystal ID to trace

        Returns:
            DerivationChain with lineage and accumulated loss

        Example:
            >>> chain = await service.trace_to_axiom("function-xyz789")
            >>> print(f"Chain: {[ref.crystal_type for ref in chain.chain]}")
            ['function', 'spec', 'value', 'axiom']
        """
        chain: list[CrystalRef] = []
        visited: set[str] = set()
        current_id = crystal_id
        total_loss = 0.0

        # Traverse upward through derivation edges
        while current_id not in visited:
            visited.add(current_id)

            # Get crystal from Universe
            crystal = await self._universe.get(current_id)
            if crystal is None:
                break

            # Determine layer and type from crystal schema metadata
            layer, crystal_type = await self._get_layer_and_type(crystal)

            # Get parent edges
            parent_edges = self._edges.get(current_id, [])
            if not parent_edges:
                # Leaf node - check if it's grounded
                is_grounded = layer in {1, 2}  # L1 axiom or L2 value
                break

            # Follow first parent edge (TODO: handle multiple parents)
            edge = parent_edges[0]
            parent_id = edge.target_id

            # Compute edge loss if galois available
            edge_loss = 0.0
            if self._galois:
                edge_loss = await self._compute_edge_loss(current_id, parent_id)

            total_loss += edge_loss

            # Add to chain
            chain.append(
                CrystalRef(
                    id=current_id,
                    layer=layer,
                    crystal_type=crystal_type,
                    edge_kind=edge.edge_type,
                    galois_loss=edge_loss,
                )
            )

            # Move to parent
            current_id = parent_id

        # Check if grounded (reached L1 or L2)
        is_grounded = any(ref.layer in {1, 2} for ref in chain)

        return DerivationChain(
            target_id=crystal_id,
            chain=chain,
            total_galois_loss=total_loss,
            is_grounded=is_grounded,
        )

    async def get_derivation_tree(self, crystal_id: str) -> DerivationTree:
        """
        Get full derivation tree (both ancestors and descendants).

        Args:
            crystal_id: Crystal ID to query

        Returns:
            DerivationTree with full ancestry and descendant info

        Example:
            >>> tree = await service.get_derivation_tree("spec-abc123")
            >>> print(f"Ancestors: {len(tree.ancestors)}, Descendants: {len(tree.descendants)}")
        """
        # Trace ancestors
        chain = await self.trace_to_axiom(crystal_id)
        ancestors = chain.chain

        # Find descendants (crystals that derive from this one)
        descendants = await self._get_descendants(crystal_id)

        return DerivationTree(
            crystal_id=crystal_id,
            ancestors=ancestors,
            descendants=descendants,
            is_grounded=chain.is_grounded,
            total_loss_to_axioms=chain.total_galois_loss,
        )

    async def detect_drift(self, spec_id: str) -> list[DriftReport]:
        """
        Find impl crystals that have drifted from spec.

        Computes Galois loss between spec and its implementations.
        High loss = high drift = needs attention.

        Args:
            spec_id: Specification crystal ID

        Returns:
            List of drift reports for each implementation

        Example:
            >>> reports = await service.detect_drift("spec-abc123")
            >>> for r in reports:
            ...     print(f"Drift in {r.impl_id}: {r.drift_severity:.2f} ({r.drift_type})")
        """
        reports: list[DriftReport] = []

        # Find all implementations of this spec
        impl_edges = [
            edge for edge in self._edges.get(spec_id, [])
            if edge.edge_type == "implements"
        ]

        for edge in impl_edges:
            impl_id = edge.target_id

            # Compute loss between spec and impl
            drift = 0.0
            if self._galois:
                drift = await self._compute_edge_loss(spec_id, impl_id)

            # Classify drift type
            drift_type = self._classify_drift(drift)

            reports.append(
                DriftReport(
                    spec_id=spec_id,
                    impl_id=impl_id,
                    drift_severity=drift,
                    drift_type=drift_type,
                    details=f"Galois loss: {drift:.3f} ({drift_type})",
                )
            )

        return reports

    async def coherence_check(self, crystal_id: str) -> float:
        """
        Compute coherence along derivation chain.

        Coherence = 1 - (accumulated galois loss along chain to axioms)

        Args:
            crystal_id: Crystal ID to check

        Returns:
            Coherence score in [0, 1] (1 = perfect, 0 = incoherent)

        Example:
            >>> coherence = await service.coherence_check("function-xyz")
            >>> print(f"Coherence: {coherence:.2%}")
        """
        chain = await self.trace_to_axiom(crystal_id)
        return chain.coherence()

    async def find_orphans(self) -> list[str]:
        """
        Find crystals with no derivation path to axioms.

        Orphans are crystals that exist without justification.
        They need either:
        1. Derivation links to axioms/values
        2. Promotion to axiom status (if foundational)

        Returns:
            List of orphaned crystal IDs

        Example:
            >>> orphans = await service.find_orphans()
            >>> print(f"Found {len(orphans)} orphaned crystals")
        """
        orphans: list[str] = []

        # Query all crystals from Universe
        # TODO: Implement efficient orphan detection via DAG traversal
        # For MVP, we check each crystal's grounding status

        # This is a placeholder - full implementation would:
        # 1. Build full DAG from all edges
        # 2. Find connected components
        # 3. Identify components with no L1/L2 nodes

        return orphans

    async def link_derivation(
        self,
        source_id: str,
        target_id: str,
        edge_kind: str,
        context: str | None = None,
        mark_id: str | None = None,
    ) -> str:
        """
        Create a derivation edge between crystals.

        Links source → target with semantic relationship type.
        Optionally attaches a witness mark for traceability.

        Args:
            source_id: Source crystal ID
            target_id: Target crystal ID (parent in derivation)
            edge_kind: Semantic edge kind (GROUNDS, JUSTIFIES, SPECIFIES, IMPLEMENTS)
            context: Optional context/reasoning for this link
            mark_id: Optional witness mark ID

        Returns:
            Edge ID

        Example:
            >>> edge_id = await service.link_derivation(
            ...     "function-abc",
            ...     "spec-xyz",
            ...     "IMPLEMENTS",
            ...     context="Implements Section 3.2",
            ...     mark_id="mark-123"
            ... )
        """
        # Map edge_kind to KBlockEdge type
        edge_type = EDGE_KIND_TO_TYPE.get(edge_kind, "derives_from")

        # Generate edge ID
        edge_id = self._generate_edge_id(source_id, target_id, edge_type)

        # Create edge
        edge = KBlockEdge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            context=context,
            mark_id=mark_id,
        )

        # Store edge in local cache
        if source_id not in self._edges:
            self._edges[source_id] = []
        self._edges[source_id].append(edge)

        # TODO: Persist edge to Universe
        # await self._universe.store(edge, schema_name="kblock.edge")

        return edge_id

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    async def _get_layer_and_type(self, crystal: Any) -> tuple[int, str]:
        """
        Extract layer and crystal type from a crystal object.

        Args:
            crystal: Crystal object from Universe

        Returns:
            Tuple of (layer, crystal_type)
        """
        # Check for layer attribute (some crystals have this)
        if hasattr(crystal, "layer"):
            layer = crystal.layer
        else:
            # Infer from crystal type
            layer = self._infer_layer_from_type(type(crystal).__name__)

        # Get crystal type
        crystal_type = type(crystal).__name__.lower().replace("crystal", "")

        return layer, crystal_type

    def _infer_layer_from_type(self, type_name: str) -> int:
        """Infer Zero Seed layer from crystal type name."""
        type_lower = type_name.lower()
        if "axiom" in type_lower:
            return 1
        elif "value" in type_lower:
            return 2
        elif "prompt" in type_lower or "invocation" in type_lower:
            return 3
        elif "spec" in type_lower:
            return 4
        elif "function" in type_lower or "test" in type_lower or "kblock" in type_lower:
            return 5
        elif "reflection" in type_lower:
            return 6
        elif "interpretation" in type_lower:
            return 7
        else:
            return 5  # Default to L5 (actions)

    async def _compute_edge_loss(self, source_id: str, target_id: str) -> float:
        """
        Compute Galois loss between two crystals.

        Args:
            source_id: Source crystal ID
            target_id: Target crystal ID

        Returns:
            Galois loss in [0, 1]
        """
        if self._galois is None:
            return 0.0

        # Get crystals
        source = await self._universe.get(source_id)
        target = await self._universe.get(target_id)

        if source is None or target is None:
            return 0.0

        # Extract content
        source_content = self._extract_content(source)
        target_content = self._extract_content(target)

        # Compute loss (simple token overlap for MVP)
        # TODO: Use full Galois computation with restructure/reconstitute
        from agents.d.galois import token_overlap_distance
        return token_overlap_distance(source_content, target_content)

    def _extract_content(self, crystal: Any) -> str:
        """Extract string content from crystal for loss computation."""
        if hasattr(crystal, "content"):
            return str(crystal.content)
        elif hasattr(crystal, "principle"):
            return str(crystal.principle)
        elif hasattr(crystal, "signature"):
            # Function crystal
            sig = crystal.signature
            doc = crystal.docstring or ""
            return f"{sig}\n{doc}"
        else:
            return str(crystal)

    async def _get_descendants(self, crystal_id: str) -> list[CrystalRef]:
        """
        Find all descendants of a crystal (crystals that derive from it).

        Args:
            crystal_id: Crystal ID

        Returns:
            List of descendant CrystalRefs
        """
        descendants: list[CrystalRef] = []
        visited: set[str] = set()
        queue = [crystal_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            # Find edges where current is the target (parent)
            child_edges = [
                edge for edges in self._edges.values()
                for edge in edges
                if edge.target_id == current
            ]

            for edge in child_edges:
                child_id = edge.source_id
                child_crystal = await self._universe.get(child_id)
                if child_crystal is None:
                    continue

                layer, crystal_type = await self._get_layer_and_type(child_crystal)

                descendants.append(
                    CrystalRef(
                        id=child_id,
                        layer=layer,
                        crystal_type=crystal_type,
                        edge_kind=edge.edge_type,
                        galois_loss=0.0,  # TODO: compute
                    )
                )

                queue.append(child_id)

        return descendants

    def _classify_drift(self, loss: float) -> str:
        """
        Classify drift type based on Galois loss.

        Args:
            loss: Galois loss in [0, 1]

        Returns:
            Drift type string
        """
        if loss < 0.1:
            return "minimal_drift"
        elif loss < 0.3:
            return "impl_diverged"
        elif loss < 0.5:
            return "spec_changed"
        else:
            return "missing_impl"

    def _generate_edge_id(self, source_id: str, target_id: str, edge_type: str) -> str:
        """Generate deterministic edge ID."""
        content = f"{source_id}:{target_id}:{edge_type}"
        hash_hex = hashlib.sha256(content.encode()).hexdigest()
        return f"edge-{hash_hex[:16]}"


__all__ = [
    "DerivationService",
    "DerivationChain",
    "DerivationTree",
    "CrystalRef",
    "DriftReport",
    "LAYER_NAMES",
    "EDGE_KIND_TO_TYPE",
]
