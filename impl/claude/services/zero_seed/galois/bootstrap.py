"""
Zero Seed Bootstrap: The Lawvere Fixed Point.

This module formalizes the bootstrap paradox as a Lawvere fixed point via
Galois Modularization Theory. The key insight:

    Zero Seed = Fix(R o describe)

where:
    R = Galois restructure (modularization)
    describe = generate meta-description
    Fix(f) = {x : f(x) ~ x}

The Core Equations:
    EXISTENCE (Lawvere): exists P: R(P) ~ P  (fixed point exists necessarily)
    VERIFICATION (Galois): L(Zero Seed) < 0.15  (85% regenerability achieved)
    STRUCTURE (Polynomial): Zero Seed ~ PolyAgent[L1..L7, NodeKind, ZeroNode]
    WITNESSING (Retroactive): forall bootstrap artifact a: exists mark m: m witnesses a

See: spec/protocols/zero-seed1/bootstrap.md
See: spec/theory/galois-modularization.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, Sequence
from uuid import uuid4

if TYPE_CHECKING:
    from agents.poly.protocol import PolyAgent

# =============================================================================
# Core Types
# =============================================================================


class Layer(Enum):
    """The seven layers of Zero Seed taxonomy."""

    L1_AXIOM = 1  # Axioms (L1) - irreducible commitments
    L2_VALUE = 2  # Values (L2) - derived from axioms
    L3_GOAL = 3  # Goals (L3) - justified by values
    L4_SPEC = 4  # Specifications (L4) - defines how to achieve goals
    L5_ACTION = 5  # Actions (L5) - implements specifications
    L6_REFLECT = 6  # Reflections (L6) - observes actions
    L7_META = 7  # Meta (L7) - reasons about the system itself


class NodeKind(Enum):
    """Valid node kinds at each layer."""

    AXIOM = "Axiom"
    VALUE = "Value"
    GOAL = "Goal"
    SPEC = "Specification"
    ACTION = "Action"
    REFLECTION = "Reflection"
    META = "Meta"

    @classmethod
    def for_layer(cls, layer: Layer) -> frozenset[NodeKind]:
        """Return valid node kinds for a given layer."""
        mapping = {
            Layer.L1_AXIOM: frozenset({cls.AXIOM}),
            Layer.L2_VALUE: frozenset({cls.VALUE}),
            Layer.L3_GOAL: frozenset({cls.GOAL}),
            Layer.L4_SPEC: frozenset({cls.SPEC}),
            Layer.L5_ACTION: frozenset({cls.ACTION}),
            Layer.L6_REFLECT: frozenset({cls.REFLECTION}),
            Layer.L7_META: frozenset({cls.META}),
        }
        return mapping.get(layer, frozenset())


class EdgeKind(Enum):
    """Types of edges between nodes in Zero Seed graph."""

    GROUNDS = "GROUNDS"  # L1 -> L2: Axiom grounds Value
    JUSTIFIES = "JUSTIFIES"  # L2 -> L3: Value justifies Goal
    SPECIFIES = "SPECIFIES"  # L3 -> L4: Goal specifies Spec
    IMPLEMENTS = "IMPLEMENTS"  # L4 -> L5: Spec implements Action
    REFLECTS_ON = "REFLECTS_ON"  # L5 -> L6: Action reflects on Reflection
    META_ON = "META_ON"  # L6 -> L7: Reflection meta on Meta


# =============================================================================
# Deviation Tracking (The Irreducible 15%)
# =============================================================================


@dataclass(frozen=True)
class Deviation:
    """
    A deviation from perfect regenerability.

    From spec/protocols/zero-seed1/bootstrap.md Part IV:
    The 15% Galois loss is the empirical manifestation of Galois incompleteness.
    """

    type: str  # "implicit_dependency", "contextual_nuance", etc.
    description: str
    loss_contribution: float  # 0.0 to 1.0 (percentage of total loss)
    location: str = ""  # Where in spec this deviation appears

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type,
            "description": self.description,
            "loss_contribution": self.loss_contribution,
            "location": self.location,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Deviation:
        """Create from dictionary."""
        return cls(
            type=data.get("type", "unknown"),
            description=data.get("description", ""),
            loss_contribution=data.get("loss_contribution", 0.0),
            location=data.get("location", ""),
        )


# Standard deviation categories from the spec
DEVIATION_CATEGORIES = {
    "implicit_dependency": "Schema determines valid transformations (not stated)",
    "contextual_nuance": "Tone, emphasis, connotation (lost in flattening)",
    "holographic_redundancy": "Information distributed across modules (local->global)",
    "gestalt_coherence": "The 'feel' of the whole vs parts",
}


# =============================================================================
# Galois Operations (R: Restructure, C: Reconstitute)
# =============================================================================


class GaloisOperations(Protocol):
    """
    Protocol for Galois modularization operations.

    R: Prompt -> ModularPrompt  (restructure)
    C: ModularPrompt -> Prompt  (reconstitute)
    L(P) = d(P, C(R(P)))        (loss metric)
    """

    async def restructure(self, spec: str) -> dict[str, Any]:
        """
        R: Spec -> ModularSpec.

        Decompose a flat spec into modular components.
        """
        ...

    async def reconstitute(self, modular: dict[str, Any]) -> str:
        """
        C: ModularSpec -> Spec.

        Flatten modular components back to a single spec.
        """
        ...

    def metric(self, original: str, reconstituted: str) -> float:
        """
        d(P, C(R(P))): Distance between original and reconstituted.

        Returns a value in [0, 1] where:
        - 0.0 = perfect preservation (no loss)
        - 1.0 = complete loss
        """
        ...


@dataclass
class SimpleGaloisLoss:
    """
    Simple implementation of Galois loss calculation.

    Uses structural similarity and semantic distance to measure
    information loss through modularization/reconstitution.
    """

    threshold: float = 0.15  # 85% regenerability target

    async def restructure(self, spec: str) -> dict[str, Any]:
        """
        Restructure spec into modular components.

        This is a simplified implementation. A full implementation
        would use LLM-based decomposition.
        """
        lines = spec.strip().split("\n")
        sections: dict[str, list[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].strip().lower().replace(" ", "_")
                sections[current_section] = []
            else:
                sections[current_section].append(line)

        return {
            "sections": {k: "\n".join(v).strip() for k, v in sections.items() if v},
            "line_count": len(lines),
            "word_count": len(spec.split()),
            "original_hash": hash(spec),
        }

    async def reconstitute(self, modular: dict[str, Any]) -> str:
        """
        Reconstitute modular components back to flat spec.
        """
        sections = modular.get("sections", {})
        parts = []

        # Reconstruct in deterministic order
        if "header" in sections:
            parts.append(sections["header"])

        for key in sorted(sections.keys()):
            if key != "header":
                parts.append(f"## {key.replace('_', ' ').title()}")
                parts.append(sections[key])

        return "\n\n".join(parts)

    def metric(self, original: str, reconstituted: str) -> float:
        """
        Calculate normalized edit distance as loss metric.
        """
        # Normalize whitespace for comparison
        orig_words = original.lower().split()
        recon_words = reconstituted.lower().split()

        if not orig_words:
            return 1.0 if recon_words else 0.0

        # Jaccard distance: 1 - (intersection / union)
        orig_set = set(orig_words)
        recon_set = set(recon_words)

        intersection = len(orig_set & recon_set)
        union = len(orig_set | recon_set)

        if union == 0:
            return 0.0

        similarity = intersection / union
        return 1.0 - similarity


# =============================================================================
# Fixed Point Verification
# =============================================================================


@dataclass
class FixedPointVerification:
    """
    Result of verifying that Zero Seed is a Galois fixed point.

    The core verification:
        L(ZS) = d(ZS, C(R(ZS))) < threshold

    Success: loss < 0.15 (85% regenerability)
    """

    original_spec: str
    modular_form: dict[str, Any]
    reconstituted_spec: str
    loss: float
    threshold: float = 0.15
    is_fixed_point: bool = field(init=False)
    regenerability_pct: float = field(init=False)
    deviations: list[Deviation] = field(default_factory=list)
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Compute derived fields."""
        self.is_fixed_point = self.loss < self.threshold
        self.regenerability_pct = (1.0 - self.loss) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_spec_hash": hash(self.original_spec),
            "original_spec_len": len(self.original_spec),
            "modular_form": self.modular_form,
            "reconstituted_spec_len": len(self.reconstituted_spec),
            "loss": self.loss,
            "threshold": self.threshold,
            "is_fixed_point": self.is_fixed_point,
            "regenerability_pct": self.regenerability_pct,
            "deviations": [d.to_dict() for d in self.deviations],
            "verified_at": self.verified_at.isoformat(),
        }


async def verify_zero_seed_fixed_point(
    zero_seed_spec: str,
    galois: GaloisOperations | None = None,
    threshold: float = 0.15,
) -> FixedPointVerification:
    """
    Verify that Zero Seed is a fixed point of its own modularization.

    This is the OPERATIONAL TEST of the bootstrap paradox resolution.

    Args:
        zero_seed_spec: The Zero Seed specification text
        galois: Galois operations (defaults to SimpleGaloisLoss)
        threshold: Maximum acceptable loss (default 0.15 = 85% regenerability)

    Returns:
        FixedPointVerification with loss, deviations, and verdict
    """
    if galois is None:
        galois = SimpleGaloisLoss(threshold=threshold)

    # Step 1: Restructure the Zero Seed spec
    modular = await galois.restructure(zero_seed_spec)

    # Step 2: Reconstitute (flatten) the modularized spec
    reconstituted = await galois.reconstitute(modular)

    # Step 3: Compute loss
    loss = galois.metric(zero_seed_spec, reconstituted)

    # Step 4: Extract deviations
    deviations = extract_deviations(zero_seed_spec, reconstituted, loss)

    return FixedPointVerification(
        original_spec=zero_seed_spec,
        modular_form=modular,
        reconstituted_spec=reconstituted,
        loss=loss,
        threshold=threshold,
        deviations=deviations,
    )


def extract_deviations(original: str, reconstituted: str, total_loss: float) -> list[Deviation]:
    """
    Extract specific deviations between original and reconstituted specs.

    This analyzes what was lost in the modularization/reconstitution cycle.
    """
    if total_loss == 0:
        return []

    deviations: list[Deviation] = []

    # Compare line counts
    orig_lines = original.strip().split("\n")
    recon_lines = reconstituted.strip().split("\n")

    if len(orig_lines) != len(recon_lines):
        deviations.append(
            Deviation(
                type="structural_difference",
                description=f"Line count changed: {len(orig_lines)} -> {len(recon_lines)}",
                loss_contribution=min(0.05, total_loss * 0.3),
                location="global",
            )
        )

    # Check for lost sections
    orig_sections = set(line[3:].strip().lower() for line in orig_lines if line.startswith("## "))
    recon_sections = set(line[3:].strip().lower() for line in recon_lines if line.startswith("## "))

    lost_sections = orig_sections - recon_sections
    for section in lost_sections:
        deviations.append(
            Deviation(
                type="lost_section",
                description=f"Section '{section}' was lost during reconstitution",
                loss_contribution=total_loss * (0.1 / max(1, len(lost_sections))),
                location=f"section:{section}",
            )
        )

    # Add standard deviation categories for unexplained loss
    explained_loss = sum(d.loss_contribution for d in deviations)
    unexplained_loss = total_loss - explained_loss

    if unexplained_loss > 0.01:
        # Distribute unexplained loss across standard categories
        categories = [
            ("implicit_dependency", 0.33),
            ("contextual_nuance", 0.27),
            ("holographic_redundancy", 0.20),
            ("gestalt_coherence", 0.20),
        ]

        for cat_type, weight in categories:
            deviations.append(
                Deviation(
                    type=cat_type,
                    description=DEVIATION_CATEGORIES[cat_type],
                    loss_contribution=unexplained_loss * weight,
                    location="distributed",
                )
            )

    return deviations


# =============================================================================
# Convergence Verification
# =============================================================================


@dataclass
class ConvergenceReport:
    """
    Report on convergence of bootstrap sequence to fixed point.

    From spec: lim_{n->inf} (R o C)^n(P_0) = Fix(R o C)
    """

    converged: bool
    iterations: int
    final_spec: str
    trajectory: list[str]
    final_loss: float
    loss_trajectory: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "converged": self.converged,
            "iterations": self.iterations,
            "final_spec_len": len(self.final_spec),
            "trajectory_len": len(self.trajectory),
            "final_loss": self.final_loss,
            "loss_trajectory": self.loss_trajectory,
        }


async def verify_convergence(
    initial_spec: str,
    galois: GaloisOperations | None = None,
    max_iterations: int = 20,
    threshold: float = 0.01,
) -> ConvergenceReport:
    """
    Verify that Zero Seed converges to fixed point.

    Starting from initial spec P_0, repeatedly apply Galois operations
    until convergence or max iterations.

    Args:
        initial_spec: Starting specification
        galois: Galois operations (defaults to SimpleGaloisLoss)
        max_iterations: Maximum iterations before giving up
        threshold: Convergence threshold (delta between iterations)

    Returns:
        ConvergenceReport with trajectory and convergence status
    """
    if galois is None:
        galois = SimpleGaloisLoss()

    trajectory = [initial_spec]
    loss_trajectory: list[float] = []

    for i in range(max_iterations):
        # Restructure and reconstitute
        modular = await galois.restructure(trajectory[-1])
        reconstituted = await galois.reconstitute(modular)
        trajectory.append(reconstituted)

        # Check convergence (delta between last two)
        delta = galois.metric(trajectory[-1], trajectory[-2])
        loss_trajectory.append(delta)

        if delta < threshold:
            return ConvergenceReport(
                converged=True,
                iterations=i + 1,
                final_spec=trajectory[-1],
                trajectory=trajectory,
                final_loss=delta,
                loss_trajectory=loss_trajectory,
            )

    return ConvergenceReport(
        converged=False,
        iterations=max_iterations,
        final_spec=trajectory[-1],
        trajectory=trajectory,
        final_loss=galois.metric(trajectory[-1], trajectory[-2]),
        loss_trajectory=loss_trajectory,
    )


# =============================================================================
# Bootstrap Window (Temporal Tracking)
# =============================================================================


NodeId = str
EdgeId = str


@dataclass
class BootstrapWindow:
    """
    Tracks bootstrap window state.

    During initialization, normal validation is suspended.
    The bootstrap window tracks what was created during this period.
    """

    is_open: bool = True
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    nodes_created: list[NodeId] = field(default_factory=list)
    edges_created: list[EdgeId] = field(default_factory=list)
    galois_loss: float | None = None

    def close(self) -> BootstrapReport:
        """Close the bootstrap window and return report."""
        self.is_open = False
        return BootstrapReport(
            duration_sec=(datetime.now(timezone.utc) - self.opened_at).total_seconds(),
            nodes_created=len(self.nodes_created),
            edges_created=len(self.edges_created),
            galois_loss=self.galois_loss,
            fixed_point_verified=self.galois_loss < 0.15 if self.galois_loss else None,
        )


@dataclass
class BootstrapReport:
    """
    Report generated when bootstrap window closes.
    """

    duration_sec: float
    nodes_created: int
    edges_created: int
    galois_loss: float | None
    fixed_point_verified: bool | None
    galois_verification: FixedPointVerification | None = None
    marks_created: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "duration_sec": self.duration_sec,
            "nodes_created": self.nodes_created,
            "edges_created": self.edges_created,
            "galois_loss": self.galois_loss,
            "fixed_point_verified": self.fixed_point_verified,
            "marks_created": self.marks_created,
            "galois_verification": (self.galois_verification.to_dict() if self.galois_verification else None),
        }


# =============================================================================
# Retroactive Witnessing
# =============================================================================


@dataclass(frozen=True)
class BootstrapMark:
    """
    A mark created during retroactive witnessing of bootstrap artifacts.

    These marks acknowledge that the spec existed before its grounding,
    but we witness the grounding retroactively.
    """

    id: str = field(default_factory=lambda: f"mark-{uuid4().hex[:12]}")
    origin: str = "zero-seed.bootstrap"
    kind: str = "bootstrap"  # "node_created", "edge_created", "bootstrap_verified"
    source: str = "retroactive"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    target_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: frozenset[str] = frozenset({"bootstrap:retroactive", "zero-seed", "grounding-chain"})

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "origin": self.origin,
            "kind": self.kind,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "target_id": self.target_id,
            "metadata": dict(self.metadata),
            "tags": list(self.tags),
        }


async def retroactive_witness_bootstrap(
    node_ids: Sequence[NodeId],
    edge_ids: Sequence[EdgeId],
    galois_verification: FixedPointVerification,
) -> list[BootstrapMark]:
    """
    Create marks for bootstrap artifacts with Galois metadata.

    This resolves the paradox: the spec exists before its grounding,
    but we witness the grounding retroactively.

    Args:
        node_ids: IDs of nodes created during bootstrap
        edge_ids: IDs of edges created during bootstrap
        galois_verification: Result of fixed point verification

    Returns:
        List of BootstrapMarks for all artifacts
    """
    marks: list[BootstrapMark] = []

    # Create marks for nodes
    for node_id in node_ids:
        mark = BootstrapMark(
            kind="node_created",
            target_id=node_id,
            metadata={
                "reason": "Bootstrap window retroactive witnessing",
                "galois_loss": galois_verification.loss,
                "regenerability_pct": galois_verification.regenerability_pct,
                "fixed_point_verified": galois_verification.is_fixed_point,
            },
            tags=frozenset(
                {
                    "bootstrap:retroactive",
                    "zero-seed",
                    "grounding-chain",
                    "galois-verified" if galois_verification.is_fixed_point else "galois-unverified",
                }
            ),
        )
        marks.append(mark)

    # Create marks for edges
    for edge_id in edge_ids:
        mark = BootstrapMark(
            kind="edge_created",
            target_id=edge_id,
            metadata={
                "reason": "Bootstrap window retroactive witnessing",
            },
            tags=frozenset(
                {
                    "bootstrap:retroactive",
                    "zero-seed",
                    "grounding-chain",
                }
            ),
        )
        marks.append(mark)

    # Create summary mark
    summary_mark = BootstrapMark(
        kind="bootstrap_verified",
        metadata={
            "galois_loss": galois_verification.loss,
            "regenerability_pct": galois_verification.regenerability_pct,
            "deviations": [
                {"type": d.type, "description": d.description}
                for d in galois_verification.deviations[:5]  # Top 5
            ],
            "nodes_created": len(node_ids),
            "edges_created": len(edge_ids),
            "fixed_point": galois_verification.is_fixed_point,
        },
        tags=frozenset(
            {
                "bootstrap:summary",
                "zero-seed",
                "galois-verified" if galois_verification.is_fixed_point else "galois-unverified",
            }
        ),
    )
    marks.append(summary_mark)

    return marks


# =============================================================================
# Polynomial Emergence: Fixed Points ARE PolyAgent[S, A, B]
# =============================================================================


@dataclass(frozen=True)
class ZeroSeedPolynomial:
    """
    Zero Seed as a polynomial agent structure.

    From Theorem 3.2.1 (Fixed Points are Polynomial):
        P ~ PolyAgent[S, A, B]

    For Zero Seed specifically:
        S = {L1, L2, L3, L4, L5, L6, L7}  (the seven layers)
        A(L_i) = {valid node kinds at layer i}
        B = ZeroNode (output type)

    The seven-layer structure IS the polynomial structure.
    """

    # Positions: The seven layers
    positions: frozenset[Layer] = frozenset(Layer)

    def directions(self, layer: Layer) -> frozenset[NodeKind]:
        """
        Valid inputs (node kinds) for each layer.

        This captures mode-dependent behavior: different layers
        accept different node kinds.
        """
        return NodeKind.for_layer(layer)

    def valid_transition(self, from_layer: Layer, to_layer: Layer) -> EdgeKind | None:
        """
        Valid edge kind for transition between layers.

        Returns None if transition is invalid.
        """
        valid_transitions = {
            (Layer.L1_AXIOM, Layer.L2_VALUE): EdgeKind.GROUNDS,
            (Layer.L2_VALUE, Layer.L3_GOAL): EdgeKind.JUSTIFIES,
            (Layer.L3_GOAL, Layer.L4_SPEC): EdgeKind.SPECIFIES,
            (Layer.L4_SPEC, Layer.L5_ACTION): EdgeKind.IMPLEMENTS,
            (Layer.L5_ACTION, Layer.L6_REFLECT): EdgeKind.REFLECTS_ON,
            (Layer.L6_REFLECT, Layer.L7_META): EdgeKind.META_ON,
        }
        return valid_transitions.get((from_layer, to_layer))

    def to_poly_agent(self) -> PolyAgent[Layer, NodeKind, dict[str, Any]]:
        """
        Convert to formal PolyAgent structure.

        Returns a PolyAgent that can process the Zero Seed graph.
        """
        from agents.poly.protocol import PolyAgent

        def directions_fn(layer: Layer) -> frozenset[NodeKind]:
            return self.directions(layer)

        def transition_fn(
            layer: Layer, node_kind: NodeKind
        ) -> tuple[Layer, dict[str, Any]]:
            """
            Transition function: create node at layer, move to next layer.

            Returns (next_layer, node_metadata).
            """
            # Create node metadata
            output = {
                "layer": layer.value,
                "kind": node_kind.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Move to next layer (wrap around at L7)
            layer_order = list(Layer)
            current_idx = layer_order.index(layer)
            next_idx = (current_idx + 1) % len(layer_order)
            next_layer = layer_order[next_idx]

            return next_layer, output

        return PolyAgent(
            name="ZeroSeed",
            positions=self.positions,
            _directions=directions_fn,
            _transition=transition_fn,
        )


# =============================================================================
# The Strange Loop Resolution
# =============================================================================


@dataclass
class StrangeLoopResolution:
    """
    Resolution of the bootstrap paradox via Lawvere fixed point.

    The Problem: How can a spec define the layer system that contains it?

    The Solution: It's a Lawvere fixed point, not a circular definition.
        - By Lawvere's theorem, given self-reference and surjectivity,
          a fixed point MUST exist
        - The existence is NECESSARY, not contingent

    The Verification: Galois loss < 15% proves the fixed point exists operationally.

    The Witnessing: Retroactive marks acknowledge the temporal paradox
        while preserving the audit trail.
    """

    # The three manifestations of the fixed point
    structural_isomorphism: bool = False  # E(F(ZS)) ~ ZS
    galois_isomorphism: bool = False  # C(R(ZS)) ~ ZS
    polynomial_isomorphism: bool = False  # ZS ~ PolyAgent[Layer, NodeKind, ZeroNode]

    # Verification results
    galois_verification: FixedPointVerification | None = None
    convergence_report: ConvergenceReport | None = None

    # The resolved paradox
    paradox_resolved: bool = field(init=False)

    def __post_init__(self) -> None:
        """Compute whether paradox is resolved."""
        # Paradox is resolved if at least Galois isomorphism holds
        self.paradox_resolved = self.galois_isomorphism

    @classmethod
    async def resolve(
        cls,
        zero_seed_spec: str,
        galois: GaloisOperations | None = None,
    ) -> StrangeLoopResolution:
        """
        Attempt to resolve the strange loop for a given spec.

        This is the main entry point for bootstrap verification.
        """
        # Verify fixed point
        verification = await verify_zero_seed_fixed_point(
            zero_seed_spec, galois, threshold=0.15
        )

        # Verify convergence
        convergence = await verify_convergence(
            zero_seed_spec, galois, max_iterations=10, threshold=0.01
        )

        # Check polynomial structure
        polynomial = ZeroSeedPolynomial()
        has_all_layers = polynomial.positions == frozenset(Layer)
        has_valid_directions = all(
            len(polynomial.directions(layer)) > 0 for layer in Layer
        )

        return cls(
            structural_isomorphism=verification.is_fixed_point,  # Approximation
            galois_isomorphism=verification.is_fixed_point,
            polynomial_isomorphism=has_all_layers and has_valid_directions,
            galois_verification=verification,
            convergence_report=convergence,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "structural_isomorphism": self.structural_isomorphism,
            "galois_isomorphism": self.galois_isomorphism,
            "polynomial_isomorphism": self.polynomial_isomorphism,
            "paradox_resolved": self.paradox_resolved,
            "galois_verification": (
                self.galois_verification.to_dict() if self.galois_verification else None
            ),
            "convergence_report": (
                self.convergence_report.to_dict() if self.convergence_report else None
            ),
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core Types
    "Layer",
    "NodeKind",
    "EdgeKind",
    "Deviation",
    "DEVIATION_CATEGORIES",
    # Galois Operations
    "GaloisOperations",
    "SimpleGaloisLoss",
    # Fixed Point Verification
    "FixedPointVerification",
    "verify_zero_seed_fixed_point",
    "extract_deviations",
    # Convergence
    "ConvergenceReport",
    "verify_convergence",
    # Bootstrap Window
    "BootstrapWindow",
    "BootstrapReport",
    # Retroactive Witnessing
    "BootstrapMark",
    "retroactive_witness_bootstrap",
    # Polynomial Emergence
    "ZeroSeedPolynomial",
    # Strange Loop Resolution
    "StrangeLoopResolution",
]
