"""
Loss Decomposition for Galois Analysis.

This module provides fine-grained analysis of WHERE loss occurs,
enabling actionable diagnostics and improvement suggestions.

Philosophy:
    "Every component contributes to loss. Knowing which components
     contribute most guides targeted improvement."

Key Concepts:
- Ablation analysis: Remove each component, measure loss change
- Component loss: How much each piece contributes to total loss
- Composition loss: Residual loss from how pieces combine
- Improvement suggestions: Actionable guidance from decomposition

See: spec/protocols/zero-seed1/galois.md Part IV (Loss Decomposition)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from .galois_loss import (
    GaloisLossComputer,
    GhostAlternative,
)

if TYPE_CHECKING:
    pass


# -----------------------------------------------------------------------------
# Toulmin Proof Components
# -----------------------------------------------------------------------------


class ToulminComponent(Enum):
    """Components of a Toulmin argument structure."""

    DATA = auto()  # The evidence/facts
    WARRANT = auto()  # The logical connection
    CLAIM = auto()  # The conclusion
    BACKING = auto()  # Support for the warrant
    QUALIFIER = auto()  # Degree of certainty
    REBUTTAL = auto()  # Potential exceptions


@dataclass(frozen=True)
class ToulminProof:
    """
    A Toulmin argument structure.

    This is a simplified representation for loss decomposition.
    """

    data: str  # Evidence supporting the claim
    warrant: str  # Logical connection from data to claim
    claim: str  # The conclusion being argued
    backing: str = ""  # Additional support for warrant
    qualifier: str = "probably"  # Degree of certainty
    rebuttals: tuple[str, ...] = ()  # Potential exceptions

    def serialize(self) -> str:
        """Serialize to text for loss computation."""
        parts = [
            f"DATA: {self.data}",
            f"WARRANT: {self.warrant}",
            f"CLAIM: {self.claim}",
        ]

        if self.backing:
            parts.append(f"BACKING: {self.backing}")

        parts.append(f"QUALIFIER: {self.qualifier}")

        if self.rebuttals:
            parts.append(f"REBUTTALS: {'; '.join(self.rebuttals)}")

        return "\n".join(parts)

    def without(self, component: str) -> "ToulminProof":
        """Create a copy with the specified component removed/emptied."""
        kwargs: dict[str, object] = {
            "data": self.data,
            "warrant": self.warrant,
            "claim": self.claim,
            "backing": self.backing,
            "qualifier": self.qualifier,
            "rebuttals": self.rebuttals,
        }

        # Map component names to field names
        component_map = {
            "data": "data",
            "warrant": "warrant",
            "claim": "claim",
            "backing": "backing",
            "qualifier": "qualifier",
            "rebuttals": "rebuttals",
        }

        field_name = component_map.get(component.lower())
        if field_name:
            if field_name == "rebuttals":
                kwargs[field_name] = ()
            else:
                kwargs[field_name] = ""

        return ToulminProof(**kwargs)


# -----------------------------------------------------------------------------
# Proof Loss Decomposition
# -----------------------------------------------------------------------------


@dataclass
class ProofLossDecomposition:
    """
    Breakdown of Galois loss by Toulmin component.

    Each component's contribution shows how much loss
    INCREASES when that component is removed (ablation).

    Positive contribution = component was helping
    Negative contribution = component was adding noise
    """

    data_loss: float  # Loss contribution from data
    warrant_loss: float  # Loss contribution from warrant
    claim_loss: float  # Loss contribution from claim
    backing_loss: float  # Loss contribution from backing
    qualifier_loss: float  # Loss contribution from qualifier
    rebuttal_loss: float  # Loss contribution from rebuttals
    composition_loss: float  # Residual loss from composition

    @property
    def total_loss(self) -> float:
        """Sum of all component losses."""
        return (
            self.data_loss
            + self.warrant_loss
            + self.claim_loss
            + self.backing_loss
            + self.qualifier_loss
            + self.rebuttal_loss
            + self.composition_loss
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for iteration."""
        return {
            "data": self.data_loss,
            "warrant": self.warrant_loss,
            "claim": self.claim_loss,
            "backing": self.backing_loss,
            "qualifier": self.qualifier_loss,
            "rebuttals": self.rebuttal_loss,
            "composition": self.composition_loss,
        }

    @property
    def top_contributors(self) -> list[tuple[str, float]]:
        """
        Get components sorted by loss contribution (highest first).

        Excludes composition loss as it's not directly actionable.
        """
        items = list(self.to_dict().items())
        # Exclude composition for actionability
        items = [(k, v) for k, v in items if k != "composition"]
        return sorted(items, key=lambda x: x[1], reverse=True)

    @property
    def problematic_components(self) -> list[str]:
        """Components with high loss contribution (> 0.15)."""
        return [name for name, loss in self.top_contributors if loss > 0.15]


async def decompose_proof_loss(
    proof: ToulminProof,
    computer: GaloisLossComputer,
) -> ProofLossDecomposition:
    """
    Break down Galois loss by Toulmin component via ablation.

    For each component, measures how much loss INCREASES
    when that component is removed.

    Args:
        proof: The Toulmin proof to analyze
        computer: Galois loss computer

    Returns:
        ProofLossDecomposition with per-component analysis
    """
    # Baseline loss (full proof)
    full_text = proof.serialize()
    full_loss = await computer.compute_loss(full_text)

    # Ablation: measure loss without each component
    components = ["data", "warrant", "claim", "backing", "qualifier", "rebuttals"]
    component_contributions: dict[str, float] = {}

    for component in components:
        # Create proof without this component
        ablated = proof.without(component)
        ablated_text = ablated.serialize()

        # Measure ablated loss
        ablated_loss = await computer.compute_loss(ablated_text)

        # Contribution = how much loss INCREASES when removed
        # Positive = component was helping (loss went up when removed)
        # Negative = component was hurting (loss went down when removed)
        contribution = ablated_loss - full_loss
        component_contributions[component] = contribution

    # Composition loss is the residual
    sum_contributions = sum(component_contributions.values())
    composition_loss = full_loss - sum_contributions

    return ProofLossDecomposition(
        data_loss=component_contributions["data"],
        warrant_loss=component_contributions["warrant"],
        claim_loss=component_contributions["claim"],
        backing_loss=component_contributions["backing"],
        qualifier_loss=component_contributions["qualifier"],
        rebuttal_loss=component_contributions["rebuttals"],
        composition_loss=composition_loss,
    )


# -----------------------------------------------------------------------------
# Galois-Witnessed Proof
# -----------------------------------------------------------------------------


@dataclass
class GaloisWitnessedProof:
    """
    Toulmin proof extended with Galois loss annotations.

    From spec Part IV: "Galois-Witnessed Proof Extension"
    """

    proof: ToulminProof
    galois_loss: float
    loss_decomposition: ProofLossDecomposition
    ghost_alternatives: tuple[GhostAlternative, ...] = ()

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss."""
        return 1.0 - self.galois_loss

    @property
    def is_strong(self) -> bool:
        """Strong proof = low Galois loss."""
        return self.galois_loss < 0.2

    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """
        Generate rebuttals from loss sources.

        High-loss components become potential defeaters.
        """
        loss_rebuttals = []
        for component, loss in self.loss_decomposition.to_dict().items():
            if loss > 0.15 and component != "composition":
                loss_rebuttals.append(
                    f"Unless {component}'s implicit structure is made explicit "
                    f"(contributes {loss:.2f} loss)"
                )

        return self.proof.rebuttals + tuple(loss_rebuttals)

    def suggest_improvements(self) -> list[str]:
        """
        Generate actionable improvement suggestions.

        Based on loss decomposition analysis.
        """
        suggestions: list[str] = []

        # Sort components by loss (highest first)
        sorted_components = self.loss_decomposition.top_contributors

        # Suggest improvements for top 2 offenders
        for component, loss in sorted_components[:2]:
            if loss > 0.15:
                suggestions.append(
                    f"Strengthen {component} to reduce loss (current: {loss:.2f})"
                )

        # Suggest ghost alternatives if they improve coherence
        if self.ghost_alternatives:
            best_ghost = min(
                self.ghost_alternatives, key=lambda g: g.deferral_cost
            )
            suggestions.append(
                f"Consider alternative formulation: {best_ghost.rationale}"
            )

        # Add composition advice if significant
        if self.loss_decomposition.composition_loss > 0.1:
            suggestions.append(
                "Consider restructuring the argument flow "
                f"(composition loss: {self.loss_decomposition.composition_loss:.2f})"
            )

        return suggestions


async def witness_proof(
    proof: ToulminProof,
    computer: GaloisLossComputer,
) -> GaloisWitnessedProof:
    """
    Create a Galois-witnessed proof with full analysis.

    Args:
        proof: The Toulmin proof to witness
        computer: Galois loss computer

    Returns:
        GaloisWitnessedProof with loss annotations
    """
    # Compute overall loss
    proof_text = proof.serialize()
    loss = await computer.compute_loss(proof_text)

    # Decompose loss
    decomposition = await decompose_proof_loss(proof, computer)

    # Get ghost alternatives from restructuring
    modular = await computer.llm.restructure(proof_text)
    ghosts = tuple(modular.ghosts)

    return GaloisWitnessedProof(
        proof=proof,
        galois_loss=loss,
        loss_decomposition=decomposition,
        ghost_alternatives=ghosts,
    )


# -----------------------------------------------------------------------------
# Layer-Stratified Loss Decomposition
# -----------------------------------------------------------------------------


class EdgeKind(Enum):
    """Types of edges between Zero Seed nodes."""

    JUSTIFIES = auto()  # Value justifies Goal
    SPECIFIES = auto()  # Goal specifies Spec
    IMPLEMENTS = auto()  # Spec implements Execution
    REFLECTS_ON = auto()  # Execution reflects as Reflection
    REPRESENTS = auto()  # Reflection represents as Representation


@dataclass
class LayerLossBreakdown:
    """Loss breakdown for a specific layer."""

    layer: int
    base_loss: float  # Intrinsic loss
    grounding_loss: float  # Loss from grounding edges
    total_loss: float  # Combined loss

    @property
    def is_healthy(self) -> bool:
        """Layer is healthy if total loss within expected bounds."""
        from .galois_loss import LAYER_LOSS_BOUNDS

        bounds = LAYER_LOSS_BOUNDS.get(self.layer, (0.0, 1.0))
        return bounds[0] <= self.total_loss <= bounds[1]


@dataclass
class GraphLossDecomposition:
    """
    Decomposition of loss across the entire graph.

    Breaks down:
    - Loss by layer
    - Loss by edge type
    - Unstable regions
    """

    layer_losses: dict[int, LayerLossBreakdown]
    edge_type_losses: dict[EdgeKind, float]
    overall_loss: float
    hot_spots: list[str]  # IDs of high-loss nodes

    @property
    def healthiest_layer(self) -> int:
        """Layer with lowest loss."""
        if not self.layer_losses:
            return 1
        return min(self.layer_losses, key=lambda k: self.layer_losses[k].total_loss)

    @property
    def most_problematic_layer(self) -> int:
        """Layer with highest loss."""
        if not self.layer_losses:
            return 7
        return max(self.layer_losses, key=lambda k: self.layer_losses[k].total_loss)

    @property
    def weakest_edge_type(self) -> EdgeKind | None:
        """Edge type with highest average loss."""
        if not self.edge_type_losses:
            return None
        return max(self.edge_type_losses, key=self.edge_type_losses.get)


# -----------------------------------------------------------------------------
# Node Loss Decomposition
# -----------------------------------------------------------------------------


@dataclass
class NodeLossDecomposition:
    """
    Fine-grained loss analysis for a single node.

    Breaks down:
    - Intrinsic loss (content complexity)
    - Contextual loss (relation to neighbors)
    - Structural loss (position in graph)
    """

    node_id: str
    layer: int
    intrinsic_loss: float  # Loss from content alone
    contextual_loss: float  # Loss from edge context
    structural_loss: float  # Loss from graph position

    @property
    def total_loss(self) -> float:
        """Weighted sum of loss components."""
        return (
            0.5 * self.intrinsic_loss
            + 0.3 * self.contextual_loss
            + 0.2 * self.structural_loss
        )

    @property
    def dominant_loss_source(self) -> str:
        """Which type of loss dominates."""
        losses = {
            "intrinsic": self.intrinsic_loss,
            "contextual": self.contextual_loss,
            "structural": self.structural_loss,
        }
        return max(losses, key=losses.get)

    def improvement_focus(self) -> str:
        """Where to focus improvement efforts."""
        source = self.dominant_loss_source
        if source == "intrinsic":
            return "Simplify or clarify the node content"
        elif source == "contextual":
            return "Strengthen connections to neighboring nodes"
        else:
            return "Consider repositioning in the graph structure"


async def decompose_node_loss(
    content: str,
    node_id: str,
    layer: int,
    neighbor_contents: list[str],
    computer: GaloisLossComputer,
) -> NodeLossDecomposition:
    """
    Decompose a node's loss into intrinsic, contextual, and structural.

    Args:
        content: Node content
        node_id: Node identifier
        layer: Node layer
        neighbor_contents: Content of connected nodes
        computer: Galois loss computer

    Returns:
        NodeLossDecomposition with detailed breakdown
    """
    # Intrinsic loss: content in isolation
    intrinsic = await computer.compute_loss(content)

    # Contextual loss: content with neighbors
    if neighbor_contents:
        combined = content + "\n\n---\n\n" + "\n---\n".join(neighbor_contents[:3])
        combined_loss = await computer.compute_loss(combined)
        # Contextual = how much combining hurts
        contextual = max(0.0, combined_loss - intrinsic)
    else:
        contextual = 0.0

    # Structural loss: content with layer context
    from .galois_loss import LAYER_NAMES

    layer_contextualized = f"[{LAYER_NAMES.get(layer, 'Unknown')} Layer]\n{content}"
    structural_loss = await computer.compute_loss(layer_contextualized)
    # Structural = how much layer context hurts
    structural = max(0.0, structural_loss - intrinsic)

    return NodeLossDecomposition(
        node_id=node_id,
        layer=layer,
        intrinsic_loss=intrinsic,
        contextual_loss=contextual,
        structural_loss=structural,
    )


# -----------------------------------------------------------------------------
# Improvement Suggestion Engine
# -----------------------------------------------------------------------------


@dataclass
class ImprovementSuggestion:
    """A concrete suggestion for reducing loss."""

    target: str  # What to improve (component, node, edge)
    action: str  # What to do
    expected_reduction: float  # Estimated loss reduction
    priority: int  # 1 = highest priority


def generate_improvement_suggestions(
    proof_decomposition: ProofLossDecomposition | None = None,
    node_decomposition: NodeLossDecomposition | None = None,
    max_suggestions: int = 5,
) -> list[ImprovementSuggestion]:
    """
    Generate prioritized improvement suggestions.

    Args:
        proof_decomposition: Proof loss breakdown (optional)
        node_decomposition: Node loss breakdown (optional)
        max_suggestions: Maximum suggestions to return

    Returns:
        List of prioritized improvement suggestions
    """
    suggestions: list[ImprovementSuggestion] = []

    # Analyze proof decomposition
    if proof_decomposition:
        for i, (component, loss) in enumerate(
            proof_decomposition.top_contributors[:3]
        ):
            if loss > 0.1:
                suggestions.append(
                    ImprovementSuggestion(
                        target=f"proof.{component}",
                        action=_component_improvement_action(component),
                        expected_reduction=loss * 0.5,  # Estimate 50% improvable
                        priority=i + 1,
                    )
                )

    # Analyze node decomposition
    if node_decomposition:
        source = node_decomposition.dominant_loss_source
        suggestions.append(
            ImprovementSuggestion(
                target=f"node.{source}",
                action=node_decomposition.improvement_focus(),
                expected_reduction=node_decomposition.total_loss * 0.3,
                priority=len(suggestions) + 1,
            )
        )

    # Sort by priority and limit
    suggestions.sort(key=lambda s: s.priority)
    return suggestions[:max_suggestions]


def _component_improvement_action(component: str) -> str:
    """Get improvement action for a Toulmin component."""
    actions = {
        "data": "Provide more specific evidence or cite authoritative sources",
        "warrant": "Make the logical connection more explicit and rigorous",
        "claim": "Narrow or clarify the conclusion being argued",
        "backing": "Add foundational support for the reasoning",
        "qualifier": "Be more precise about degree of certainty",
        "rebuttals": "Address more potential counterarguments",
    }
    return actions.get(component, f"Improve the {component} component")


__all__ = [
    # Toulmin
    "ToulminComponent",
    "ToulminProof",
    # Proof decomposition
    "ProofLossDecomposition",
    "decompose_proof_loss",
    # Witnessed proof
    "GaloisWitnessedProof",
    "witness_proof",
    # Edge and layer
    "EdgeKind",
    "LayerLossBreakdown",
    "GraphLossDecomposition",
    # Node decomposition
    "NodeLossDecomposition",
    "decompose_node_loss",
    # Suggestions
    "ImprovementSuggestion",
    "generate_improvement_suggestions",
]
