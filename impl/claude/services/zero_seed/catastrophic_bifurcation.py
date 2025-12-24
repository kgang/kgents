"""
Catastrophic Bifurcation Dynamics: When Zero Seed Graphs Collapse and Emerge.

This module implements the catastrophic bifurcation protocol from
spec/protocols/zero-seed1/catastrophic-bifurcation.md:

1. Collapse Dynamics: Detection of graph instability and imminent collapse
2. Emergence Dynamics: Layer emergence from restructuring fixed points
3. Bifurcation Points: Critical thresholds where behavior changes qualitatively
4. Recovery Mechanisms: Re-grounding after collapse via constitutional intervention
5. Early Warning System: Monitoring and alerts for approaching bifurcations

The Core Insight:
    "Collapse is not failure--it is information.
     Emergence is not luck--it is necessity.
     The bifurcation IS the phase transition."

The Radical Claim:
    Catastrophic collapse is not a failure mode to be prevented--it is the
    MECHANISM of structural evolution. Controlled collapse + re-grounding = layer emergence.

See: spec/protocols/zero-seed1/catastrophic-bifurcation.md
See: spec/theory/galois-modularization.md
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from statistics import mean, stdev
from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable
from uuid import uuid4

if TYPE_CHECKING:
    pass

from services.witness.mark import EvidenceTier, Mark, Proof, WalkId
from services.witness.walk import Walk

from .galois.distance import (
    SemanticDistanceMetric,
    get_default_metric,
    get_fast_metric,
)

logger = logging.getLogger("kgents.zero_seed.bifurcation")


# =============================================================================
# Critical Thresholds (from spec Part III)
# =============================================================================


class CriticalThreshold(Enum):
    """
    The Seven Critical Thresholds (empirically derived).

    Each threshold marks a bifurcation point where system behavior
    changes qualitatively.
    """

    EPSILON_1 = 0.05  # Fixed point (axiom) threshold
    EPSILON_2 = 0.15  # High coherence (value) threshold
    EPSILON_3 = 0.30  # Deterministic (spec) threshold
    EPSILON_4 = 0.50  # Manageable threshold
    EPSILON_5 = 0.70  # Unstable threshold (near collapse)
    EPSILON_6 = 0.85  # Collapse imminent threshold
    EPSILON_COLLAPSE = 1.00  # Total information loss


# Map threshold to layer interpretation
THRESHOLD_TO_LAYER = {
    CriticalThreshold.EPSILON_1: 1,  # L1 Axioms
    CriticalThreshold.EPSILON_2: 2,  # L2 Values
    CriticalThreshold.EPSILON_3: 3,  # L3 Goals
    CriticalThreshold.EPSILON_4: 4,  # L4 Specs
    CriticalThreshold.EPSILON_5: 5,  # L5 Execution
    CriticalThreshold.EPSILON_6: 6,  # L6 Reflection
    CriticalThreshold.EPSILON_COLLAPSE: 7,  # L7 Representation
}


# =============================================================================
# Node and Edge Types for Zero Seed Graphs
# =============================================================================


class NodeKind(Enum):
    """Types of nodes in a Zero Seed graph."""

    AXIOM = auto()  # L1: Constitutional axiom
    VALUE = auto()  # L2: Derived value
    GOAL = auto()  # L3: Execution goal
    SPEC = auto()  # L4: Specification
    EXECUTION = auto()  # L5: Concrete execution
    REFLECTION = auto()  # L6: Meta-reflection
    REPRESENTATION = auto()  # L7: Surface representation
    SYNTHESIS = auto()  # Emergent from contradiction


class EdgeKind(Enum):
    """Types of edges in a Zero Seed graph."""

    GROUNDED_BY = auto()  # Target grounded by source axiom
    DERIVED_FROM = auto()  # Target derived from source
    IMPLEMENTS = auto()  # Target implements source
    JUSTIFIES = auto()  # Target justifies source
    CONTRADICTS = auto()  # Target contradicts source (super-additive)
    SYNTHESIZES = auto()  # Target synthesizes sources


@dataclass(frozen=True)
class ZeroNode:
    """
    Node in a Zero Seed graph.

    Each node has:
    - Layer (1-7) determining its position in the holarchy
    - Kind determining its type
    - Content (natural language description)
    - Optional proof (Toulmin structure)
    - Lineage (parent node IDs)
    """

    id: str
    layer: int  # 1-7
    kind: NodeKind
    content: str
    proof: Proof | None = None
    lineage: tuple[str, ...] = ()
    galois_loss: float = 0.0
    entropy_budget: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def axiom(cls, content: str, principle: str = "") -> ZeroNode:
        """Create an L1 axiom node."""
        return cls(
            id=f"node-{uuid4().hex[:12]}",
            layer=1,
            kind=NodeKind.AXIOM,
            content=content,
            galois_loss=0.0,  # Axioms have zero loss
            entropy_budget=1.0,  # Full budget
            proof=Proof.categorical(
                data="Constitutional axiom",
                warrant="Self-evident or defined by fiat",
                claim=content,
                principles=(principle,) if principle else (),
            ),
        )

    @classmethod
    def from_layer(
        cls,
        layer: int,
        content: str,
        lineage: tuple[str, ...] = (),
        proof: Proof | None = None,
    ) -> ZeroNode:
        """Create a node at specified layer."""
        kind_map = {
            1: NodeKind.AXIOM,
            2: NodeKind.VALUE,
            3: NodeKind.GOAL,
            4: NodeKind.SPEC,
            5: NodeKind.EXECUTION,
            6: NodeKind.REFLECTION,
            7: NodeKind.REPRESENTATION,
        }
        return cls(
            id=f"node-{uuid4().hex[:12]}",
            layer=layer,
            kind=kind_map.get(layer, NodeKind.VALUE),
            content=content,
            lineage=lineage,
            proof=proof,
        )

    def with_loss(self, loss: float) -> ZeroNode:
        """Return new node with updated loss (immutable pattern)."""
        return ZeroNode(
            id=self.id,
            layer=self.layer,
            kind=self.kind,
            content=self.content,
            proof=self.proof,
            lineage=self.lineage,
            galois_loss=loss,
            entropy_budget=self.entropy_budget,
            metadata=self.metadata,
        )

    def with_entropy_budget(self, budget: float) -> ZeroNode:
        """Return new node with updated entropy budget."""
        return ZeroNode(
            id=self.id,
            layer=self.layer,
            kind=self.kind,
            content=self.content,
            proof=self.proof,
            lineage=self.lineage,
            galois_loss=self.galois_loss,
            entropy_budget=budget,
            metadata=self.metadata,
        )


@dataclass(frozen=True)
class ZeroEdge:
    """
    Edge in a Zero Seed graph.

    Edges connect nodes and carry:
    - Source and target node IDs
    - Edge kind (grounding, derivation, etc.)
    - Galois loss for this edge
    - Optional proof justifying the edge
    """

    source: str  # Node ID
    target: str  # Node ID
    kind: EdgeKind
    galois_loss: float = 0.0
    proof: Proof | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Zero Seed Graph
# =============================================================================


@dataclass
class ZeroGraph:
    """
    Zero Seed knowledge graph with Galois coherence.

    A ZeroGraph is:
    - Nodes organized in layers (L1-L7)
    - Edges representing grounding and derivation
    - Galois loss metrics on edges and nodes
    - Entropy budgets for stability tracking
    """

    nodes: dict[str, ZeroNode] = field(default_factory=dict)
    edges: list[ZeroEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: ZeroNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> ZeroNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def add_edge(self, edge: ZeroEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def nodes_at_layer(self, layer: int) -> list[ZeroNode]:
        """Get all nodes at a specific layer."""
        return [n for n in self.nodes.values() if n.layer == layer]

    def axioms(self) -> list[ZeroNode]:
        """Get all L1 axiom nodes."""
        return self.nodes_at_layer(1)

    def incoming_edges(self, node_id: str) -> list[ZeroEdge]:
        """Get edges pointing to a node."""
        return [e for e in self.edges if e.target == node_id]

    def outgoing_edges(self, node_id: str) -> list[ZeroEdge]:
        """Get edges from a node."""
        return [e for e in self.edges if e.source == node_id]

    def orphaned_nodes(self) -> list[ZeroNode]:
        """
        Find orphaned nodes (no incoming edges from lower layers).

        Nodes at layer > 1 without grounding are unstable.
        """
        orphans = []
        for node in self.nodes.values():
            if node.layer <= 1:
                continue  # Axioms can't be orphaned

            incoming = self.incoming_edges(node.id)
            # Check if any incoming edge is from a lower layer
            has_grounding = any(
                self.nodes.get(e.source, ZeroNode("", 0, NodeKind.AXIOM, "")).layer
                < node.layer
                for e in incoming
                if e.kind == EdgeKind.GROUNDED_BY
            )
            if not has_grounding:
                orphans.append(node)

        return orphans

    def induced_subgraph(self, node_ids: set[str]) -> ZeroGraph:
        """Create subgraph containing only specified nodes."""
        subgraph = ZeroGraph()
        for node_id in node_ids:
            if node := self.get_node(node_id):
                subgraph.add_node(node)

        # Include edges where both endpoints are in the subgraph
        for edge in self.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge)

        return subgraph

    def replace_subgraph(
        self, old_node_ids: set[str], new_nodes: list[ZeroNode]
    ) -> ZeroGraph:
        """Replace a subgraph with new nodes."""
        result = ZeroGraph()

        # Add nodes not in old set
        for node_id, node in self.nodes.items():
            if node_id not in old_node_ids:
                result.add_node(node)

        # Add new nodes
        for node in new_nodes:
            result.add_node(node)

        # Filter edges (remove those connected to old nodes)
        for edge in self.edges:
            if edge.source not in old_node_ids and edge.target not in old_node_ids:
                result.add_edge(edge)

        return result

    def copy(self) -> ZeroGraph:
        """Create a deep copy of the graph."""
        result = ZeroGraph()
        result.nodes = dict(self.nodes)
        result.edges = list(self.edges)
        result.metadata = dict(self.metadata)
        return result


# =============================================================================
# Galois Loss Computation
# =============================================================================


@runtime_checkable
class GaloisLossComputer(Protocol):
    """Protocol for computing Galois loss."""

    def compute(self, node: ZeroNode) -> float:
        """Compute loss for a single node."""
        ...

    def compute_text(self, text_a: str, text_b: str | None = None) -> float:
        """Compute loss between texts (if text_b is None, compute self-coherence)."""
        ...

    def compute_joint(self, node_a: ZeroNode, node_b: ZeroNode) -> float:
        """Compute joint loss for detecting super-additivity."""
        ...

    def compute_graph(self, graph: ZeroGraph) -> float:
        """Compute total loss for a graph."""
        ...


@dataclass
class DefaultGaloisLoss:
    """
    Default implementation of Galois loss computation.

    Uses semantic distance metrics from galois/distance.py.
    """

    metric: SemanticDistanceMetric = field(default_factory=get_fast_metric)
    constitution_text: str = ""

    def compute(self, node: ZeroNode) -> float:
        """Compute loss for a single node based on content coherence."""
        if node.layer == 1:  # Axioms have zero loss
            return 0.0

        # If node has proof, compute loss from proof structure
        if node.proof:
            # Loss = how well the proof supports the claim
            proof_text = f"{node.proof.data}. {node.proof.warrant}. Therefore: {node.proof.claim}"
            return self.metric.distance(proof_text, node.content)

        # Without proof, use layer-based heuristic
        # Higher layers have higher intrinsic loss
        base_loss = node.layer * 0.1
        return min(1.0, base_loss + node.galois_loss)

    def compute_text(self, text_a: str, text_b: str | None = None) -> float:
        """Compute loss between texts."""
        if text_b is None:
            # Self-coherence: compare to constitution
            if self.constitution_text:
                return self.metric.distance(text_a, self.constitution_text)
            return 0.5  # No reference, return neutral

        return self.metric.distance(text_a, text_b)

    def compute_joint(self, node_a: ZeroNode, node_b: ZeroNode) -> float:
        """
        Compute joint loss for super-additivity detection.

        Super-additive loss indicates contradiction:
            L(A, B) > L(A) + L(B)
        """
        # Individual losses
        loss_a = self.compute(node_a)
        loss_b = self.compute(node_b)

        # Joint loss: semantic distance between contents
        joint_distance = self.metric.distance(node_a.content, node_b.content)

        # Super-additive if joint > sum
        return loss_a + loss_b + joint_distance

    def compute_graph(self, graph: ZeroGraph) -> float:
        """Compute total graph loss."""
        if not graph.nodes:
            return 0.0

        node_losses = [self.compute(n) for n in graph.nodes.values()]
        edge_losses = [e.galois_loss for e in graph.edges]

        all_losses = node_losses + edge_losses
        return mean(all_losses) if all_losses else 0.0


# =============================================================================
# Alert System
# =============================================================================


class AlertLevel(Enum):
    """Severity levels for instability alerts."""

    INFO = auto()  # Monitoring: instability increasing
    WARNING = auto()  # Warning: high instability
    CRITICAL = auto()  # Critical: collapse imminent


@dataclass
class Alert:
    """Alert emitted by the early warning system."""

    level: AlertLevel
    message: str
    score: float  # Instability score that triggered alert
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)
    indicators: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level.name,
            "message": self.message,
            "score": self.score,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp.isoformat(),
            "indicators": self.indicators,
        }


# =============================================================================
# Instability Indicators (from spec Part I)
# =============================================================================


@dataclass
class InstabilityIndicators:
    """
    Computable indicators of graph instability.

    From spec Part I.4 - Early Warning Indicators.
    """

    avg_loss_spike: float = 0.0  # mean(L(edges)) > mu + 2sigma
    high_loss_cluster: float = 0.0  # ratio of nodes with L > 0.7
    orphaned_nodes: float = 0.0  # ratio of ungrounded L2+ nodes
    contradiction_count: float = 0.0  # normalized count of super-additive pairs
    entropy_depletion: float = 0.0  # 1 - min entropy budget
    proof_coherence_drop: float = 0.0  # 1 - mean proof coherence
    gradient_divergence: float = 0.0  # max gradient magnitude

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "avg_loss_spike": self.avg_loss_spike,
            "high_loss_cluster": self.high_loss_cluster,
            "orphaned_nodes": self.orphaned_nodes,
            "contradiction_count": self.contradiction_count,
            "entropy_depletion": self.entropy_depletion,
            "proof_coherence_drop": self.proof_coherence_drop,
            "gradient_divergence": self.gradient_divergence,
        }


def compute_instability_indicators(
    graph: ZeroGraph, galois: GaloisLossComputer
) -> InstabilityIndicators:
    """
    Compute all instability indicators for a graph.

    Returns InstabilityIndicators with values in [0, 1].
    """
    if not graph.nodes:
        return InstabilityIndicators()

    nodes = list(graph.nodes.values())
    edges = graph.edges

    # 1. Average Loss Spike
    if edges:
        edge_losses = [e.galois_loss for e in edges]
        mu = mean(edge_losses) if edge_losses else 0.0
        sigma = stdev(edge_losses) if len(edge_losses) > 1 else 0.0
        current_avg = mean(edge_losses)
        if sigma > 0:
            avg_loss_spike = min(1.0, max(0.0, (current_avg - mu) / (2 * sigma)))
        else:
            avg_loss_spike = 0.0 if current_avg <= mu else 1.0
    else:
        avg_loss_spike = 0.0

    # 2. High-Loss Cluster Ratio
    high_loss_nodes = [n for n in nodes if galois.compute(n) > 0.7]
    high_loss_cluster = len(high_loss_nodes) / len(nodes) if nodes else 0.0

    # 3. Orphaned Node Ratio
    orphans = graph.orphaned_nodes()
    l2_plus_nodes = [n for n in nodes if n.layer > 1]
    orphaned_ratio = len(orphans) / len(l2_plus_nodes) if l2_plus_nodes else 0.0

    # 4. Contradiction Count (normalized)
    # Count pairs with super-additive loss
    contradiction_pairs = 0
    for i, node_a in enumerate(nodes):
        for node_b in nodes[i + 1 :]:
            joint = galois.compute_joint(node_a, node_b)
            individual_sum = galois.compute(node_a) + galois.compute(node_b)
            if joint > individual_sum + 0.1:  # Super-additive threshold
                contradiction_pairs += 1

    max_pairs = len(nodes) * (len(nodes) - 1) / 2 if len(nodes) > 1 else 1
    contradiction_count = min(1.0, contradiction_pairs / max_pairs)

    # 5. Entropy Depletion
    budgets = [n.entropy_budget for n in nodes]
    min_budget = min(budgets) if budgets else 0.0
    entropy_depletion = 1.0 - min_budget

    # 6. Proof Coherence Drop
    nodes_with_proof = [n for n in nodes if n.proof is not None]
    if nodes_with_proof:
        # Use proof tier as proxy for coherence
        tier_to_coherence = {
            EvidenceTier.CATEGORICAL: 1.0,
            EvidenceTier.EMPIRICAL: 0.8,
            EvidenceTier.AESTHETIC: 0.6,
            EvidenceTier.GENEALOGICAL: 0.5,
            EvidenceTier.SOMATIC: 0.4,
        }
        coherences = [
            tier_to_coherence.get(n.proof.tier, 0.5) for n in nodes_with_proof
        ]
        mean_coherence = mean(coherences)
        proof_coherence_drop = 1.0 - mean_coherence
    else:
        proof_coherence_drop = 0.5  # No proofs = medium concern

    # 7. Gradient Divergence
    # Compute loss gradient at each node
    max_gradient = 0.0
    for node in nodes:
        outgoing = graph.outgoing_edges(node.id)
        if outgoing:
            gradients = [e.galois_loss - galois.compute(node) for e in outgoing]
            max_local = max(abs(g) for g in gradients) if gradients else 0.0
            max_gradient = max(max_gradient, max_local)

    gradient_divergence = min(1.0, max_gradient)

    return InstabilityIndicators(
        avg_loss_spike=avg_loss_spike,
        high_loss_cluster=high_loss_cluster,
        orphaned_nodes=orphaned_ratio,
        contradiction_count=contradiction_count,
        entropy_depletion=entropy_depletion,
        proof_coherence_drop=proof_coherence_drop,
        gradient_divergence=gradient_divergence,
    )


def instability_score(graph: ZeroGraph, galois: GaloisLossComputer | None = None) -> float:
    """
    Compute composite instability score for a graph.

    From spec Part I.4:
        0.0 = perfectly stable
        1.0 = imminent collapse

    Thresholds:
        < 0.3: STABLE (green)
        0.3-0.6: MONITORING (yellow)
        0.6-0.8: WARNING (orange)
        >= 0.8: CRITICAL (red)
    """
    if galois is None:
        galois = DefaultGaloisLoss()

    indicators = compute_instability_indicators(graph, galois)

    # Weights from spec (entropy depletion weighted highest)
    weights = {
        "avg_loss_spike": 1.0,
        "high_loss_cluster": 1.2,
        "orphaned_nodes": 0.8,
        "contradiction_count": 1.0,
        "entropy_depletion": 2.0,  # Critical
        "proof_coherence_drop": 1.5,
        "gradient_divergence": 1.3,
    }

    values = indicators.to_dict()
    total_weight = sum(weights.values())
    weighted_sum = sum(values[k] * weights[k] for k in weights)

    return weighted_sum / total_weight


# =============================================================================
# Collapse Imminence Levels
# =============================================================================


class CollapseImminence(Enum):
    """Collapse imminence levels based on instability score."""

    STABLE = "stable"  # score < 0.3
    MONITORING = "monitoring"  # 0.3 <= score < 0.6
    WARNING = "warning"  # 0.6 <= score < 0.8
    CRITICAL = "critical"  # score >= 0.8


def classify_imminence(score: float) -> CollapseImminence:
    """Classify instability score into collapse imminence level."""
    if score < 0.3:
        return CollapseImminence.STABLE
    elif score < 0.6:
        return CollapseImminence.MONITORING
    elif score < 0.8:
        return CollapseImminence.WARNING
    else:
        return CollapseImminence.CRITICAL


# =============================================================================
# Contradiction Analysis
# =============================================================================


@dataclass
class ContradictionAnalysis:
    """Result of analyzing a potential contradiction between nodes."""

    node_a_id: str
    node_b_id: str
    is_contradiction: bool
    strength: float  # How super-additive the loss is
    individual_loss_a: float
    individual_loss_b: float
    joint_loss: float

    @property
    def super_additive_amount(self) -> float:
        """Amount by which joint loss exceeds sum of individual losses."""
        return self.joint_loss - (self.individual_loss_a + self.individual_loss_b)


def is_contradiction(
    node_a: ZeroNode,
    node_b: ZeroNode,
    galois: GaloisLossComputer,
    threshold: float = 0.1,
) -> ContradictionAnalysis:
    """
    Detect if two nodes contradict (super-additive loss).

    From spec Part II.3:
        Thesis + Antithesis where L(A u B) > L(A) + L(B)
    """
    loss_a = galois.compute(node_a)
    loss_b = galois.compute(node_b)
    joint_loss = galois.compute_joint(node_a, node_b)

    individual_sum = loss_a + loss_b
    is_super_additive = joint_loss > individual_sum + threshold

    strength = max(0.0, (joint_loss - individual_sum) / (1.0 - individual_sum + 0.001))

    return ContradictionAnalysis(
        node_a_id=node_a.id,
        node_b_id=node_b.id,
        is_contradiction=is_super_additive,
        strength=min(1.0, strength),
        individual_loss_a=loss_a,
        individual_loss_b=loss_b,
        joint_loss=joint_loss,
    )


# =============================================================================
# Topological Invariants (from spec Part II.2)
# =============================================================================


@dataclass
class GraphTopology:
    """
    Topological invariants of a Zero Seed graph.

    Used to detect phase transitions when invariants change discontinuously.
    """

    num_components: int = 1  # Connected components
    avg_clustering_coefficient: float = 0.0  # Triadic closure
    layer_entropy: float = 0.0  # Shannon entropy of layer counts
    layer_balance: float = 0.0  # Evenness of distribution
    avg_path_length: float = 0.0  # Mean shortest path
    diameter: int = 0  # Max shortest path
    num_fixed_points: int = 0  # Nodes with L < epsilon_1
    fixed_point_ratio: float = 0.0  # |fixed| / |nodes|

    def distance_from(self, other: GraphTopology) -> float:
        """Compute distance between two topologies (for phase transition detection)."""
        diffs = [
            abs(self.num_components - other.num_components) / max(self.num_components, 1),
            abs(self.avg_clustering_coefficient - other.avg_clustering_coefficient),
            abs(self.layer_entropy - other.layer_entropy),
            abs(self.layer_balance - other.layer_balance),
            abs(self.avg_path_length - other.avg_path_length) / max(self.avg_path_length, 1),
            abs(self.diameter - other.diameter) / max(self.diameter, 1),
            abs(self.fixed_point_ratio - other.fixed_point_ratio),
        ]
        return mean(diffs)


def compute_topology(graph: ZeroGraph, galois: GaloisLossComputer | None = None) -> GraphTopology:
    """Compute topological invariants of a graph."""
    if galois is None:
        galois = DefaultGaloisLoss()

    if not graph.nodes:
        return GraphTopology()

    nodes = list(graph.nodes.values())

    # Count fixed points (loss < epsilon_1)
    fixed_points = [n for n in nodes if galois.compute(n) < CriticalThreshold.EPSILON_1.value]

    # Layer distribution
    layer_counts = {}
    for node in nodes:
        layer_counts[node.layer] = layer_counts.get(node.layer, 0) + 1

    # Shannon entropy of layer distribution
    total = len(nodes)
    if total > 0:
        probs = [count / total for count in layer_counts.values()]
        import math

        layer_entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)
        max_entropy = math.log2(7)  # 7 layers
        layer_entropy = layer_entropy / max_entropy if max_entropy > 0 else 0
    else:
        layer_entropy = 0.0

    # Layer balance (how even the distribution is)
    if layer_counts:
        avg_count = total / 7  # Ideal uniform distribution
        deviations = [abs(count - avg_count) for count in layer_counts.values()]
        layer_balance = 1.0 - (mean(deviations) / total) if total > 0 else 0.0
    else:
        layer_balance = 0.0

    return GraphTopology(
        num_components=1,  # Simplified: assume connected
        avg_clustering_coefficient=0.0,  # Would need proper graph algorithm
        layer_entropy=layer_entropy,
        layer_balance=layer_balance,
        avg_path_length=0.0,  # Would need BFS/DFS
        diameter=0,  # Would need graph algorithm
        num_fixed_points=len(fixed_points),
        fixed_point_ratio=len(fixed_points) / len(nodes) if nodes else 0.0,
    )


# =============================================================================
# Recovery Strategies (from spec Part IV)
# =============================================================================


class StrategyType(Enum):
    """Types of recovery strategies."""

    CONSTITUTIONAL_INTERVENTION = auto()  # Apply constitutional principles
    REGROUND_ORPHANS = auto()  # Re-ground orphaned nodes to axioms
    SYNTHESIZE_CONTRADICTIONS = auto()  # Resolve contradictions via synthesis
    GALOIS_RESTRUCTURE = auto()  # Modular restructuring of high-loss regions
    PRUNE_OUTLIERS = auto()  # Remove extreme high-loss nodes
    CHECKPOINT_REPLAY = auto()  # Replay from last coherent Walk checkpoint


@dataclass
class RecoveryStrategy:
    """A recovery strategy recommendation."""

    type: StrategyType
    target: Any  # Nodes, edges, or None for global strategies
    expected_duration: timedelta
    confidence: float  # 0-1, how confident we are this will help
    rationale: str = ""


@dataclass
class Intervention:
    """A specific intervention derived from constitutional principle."""

    principle: str  # TASTEFUL, COMPOSABLE, etc.
    target_nodes: list[str]  # Node IDs to intervene on
    action: str  # What to do
    estimated_loss_reduction: float


@dataclass
class ConstitutionalRecoveryPlan:
    """Recovery plan derived from constitutional principles."""

    violations: dict[str, float]  # principle -> severity
    interventions: list[Intervention]
    expected_loss_reduction: float
    priority: int  # Based on ethical weight


# =============================================================================
# Diagnostic Report
# =============================================================================


@dataclass
class DiagnosticReport:
    """Detailed diagnostic when alert triggered."""

    overall_score: float
    imminence: CollapseImminence
    indicators: InstabilityIndicators
    critical_indicators: dict[str, float]  # Indicators > 0.7
    recommendations: list[str]
    timestamp: datetime = field(default_factory=datetime.now)
    topology: GraphTopology | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "imminence": self.imminence.value,
            "indicators": self.indicators.to_dict(),
            "critical_indicators": self.critical_indicators,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


def diagnose_graph(
    graph: ZeroGraph,
    galois: GaloisLossComputer | None = None,
) -> DiagnosticReport:
    """
    Generate a detailed diagnostic report for a graph.

    Returns recommendations based on detected issues.
    """
    if galois is None:
        galois = DefaultGaloisLoss()

    indicators = compute_instability_indicators(graph, galois)
    score = instability_score(graph, galois)
    imminence = classify_imminence(score)

    # Find critical indicators
    indicator_dict = indicators.to_dict()
    critical = {k: v for k, v in indicator_dict.items() if v > 0.7}

    # Generate recommendations
    recommendations = []

    if indicators.entropy_depletion > 0.7:
        recommendations.append(
            f"URGENT: Entropy critically low ({indicators.entropy_depletion:.2f}). "
            "Consider pruning high-loss nodes to free entropy budget."
        )

    if indicators.contradiction_count > 0.5:
        recommendations.append(
            f"WARNING: Many contradictions detected ({indicators.contradiction_count:.2f}). "
            "Run synthesis on conflicting node pairs."
        )

    if indicators.orphaned_nodes > 0.3:
        recommendations.append(
            f"WARNING: Orphaned nodes detected ({indicators.orphaned_nodes:.2f}). "
            "Re-ground these nodes to nearest axioms."
        )

    if indicators.proof_coherence_drop > 0.5:
        recommendations.append(
            f"INFO: Proof quality declining ({indicators.proof_coherence_drop:.2f}). "
            "Regenerate proofs for nodes with low coherence."
        )

    if indicators.gradient_divergence > 0.7:
        recommendations.append(
            f"WARNING: High gradient divergence ({indicators.gradient_divergence:.2f}). "
            "Some nodes are acting as repellers. Consider restructuring."
        )

    topology = compute_topology(graph, galois)

    return DiagnosticReport(
        overall_score=score,
        imminence=imminence,
        indicators=indicators,
        critical_indicators=critical,
        recommendations=recommendations,
        topology=topology,
    )


# =============================================================================
# Recovery Algorithm Selection (from spec Part VI.3)
# =============================================================================


def select_recovery_strategy(
    graph: ZeroGraph,
    diagnostic: DiagnosticReport,
    galois: GaloisLossComputer | None = None,
) -> RecoveryStrategy:
    """
    Choose optimal recovery strategy based on diagnostic.

    Priority order:
    1. Constitutional intervention (ethical violations)
    2. Reground orphans (broken structure)
    3. Synthesize contradictions (semantic conflicts)
    4. Galois restructure (high-loss regions)
    5. Prune outliers (entropy conservation)
    6. Checkpoint replay (catastrophic failure)
    """
    if galois is None:
        galois = DefaultGaloisLoss()

    indicators = diagnostic.indicators

    # 1. Check for ethical/constitutional violations (highest priority)
    if "proof_coherence_drop" in diagnostic.critical_indicators:
        return RecoveryStrategy(
            type=StrategyType.CONSTITUTIONAL_INTERVENTION,
            target=None,  # Global intervention
            expected_duration=timedelta(minutes=10),
            confidence=0.95,
            rationale="Constitutional principles violated. Full intervention required.",
        )

    # 2. Check for orphaned nodes
    if indicators.orphaned_nodes > 0.5:
        orphans = graph.orphaned_nodes()
        return RecoveryStrategy(
            type=StrategyType.REGROUND_ORPHANS,
            target=orphans,
            expected_duration=timedelta(minutes=5 * len(orphans)),
            confidence=0.85,
            rationale=f"Found {len(orphans)} orphaned nodes needing regrounding.",
        )

    # 3. Check for contradictions
    if indicators.contradiction_count > 0.3:
        return RecoveryStrategy(
            type=StrategyType.SYNTHESIZE_CONTRADICTIONS,
            target=None,  # Will find pairs
            expected_duration=timedelta(minutes=15),
            confidence=0.70,
            rationale="Multiple contradictions detected. Synthesis required.",
        )

    # 4. Check for high-loss clusters
    if indicators.high_loss_cluster > 0.3:
        high_loss_nodes = [
            n for n in graph.nodes.values() if galois.compute(n) > 0.7
        ]
        return RecoveryStrategy(
            type=StrategyType.GALOIS_RESTRUCTURE,
            target=set(n.id for n in high_loss_nodes),
            expected_duration=timedelta(minutes=15),
            confidence=0.75,
            rationale=f"Found {len(high_loss_nodes)} high-loss nodes requiring restructure.",
        )

    # 5. Check for entropy depletion
    if indicators.entropy_depletion > 0.7:
        return RecoveryStrategy(
            type=StrategyType.PRUNE_OUTLIERS,
            target=None,  # Will identify outliers
            expected_duration=timedelta(minutes=2),
            confidence=0.60,
            rationale="Entropy critically depleted. Pruning required.",
        )

    # 6. Last resort: checkpoint replay
    return RecoveryStrategy(
        type=StrategyType.CHECKPOINT_REPLAY,
        target=None,
        expected_duration=timedelta(minutes=5),
        confidence=0.50,
        rationale="No specific issue identified. Replay from checkpoint.",
    )


# =============================================================================
# Re-grounding Algorithm (from spec Part IV.1)
# =============================================================================


async def reground_to_axiom(
    orphaned_node: ZeroNode,
    graph: ZeroGraph,
    galois: GaloisLossComputer,
) -> tuple[ZeroNode, ZeroEdge] | None:
    """
    Re-ground an orphaned node to the nearest axiom.

    Process:
    1. Find all L1 axioms
    2. Compute Galois loss for grounding to each
    3. Select axiom with minimum loss
    4. Create grounding edge

    Returns:
        (best_axiom, grounding_edge) or None if no axioms available
    """
    axioms = graph.axioms()

    if not axioms:
        logger.error("No axioms available for regrounding!")
        return None

    # Compute loss for each potential grounding
    grounding_losses = {}
    for axiom in axioms:
        # Compute how well this axiom grounds the orphaned node
        grounding_desc = f"Ground: {orphaned_node.content}\nTo axiom: {axiom.content}"
        loss = galois.compute_text(grounding_desc, axiom.content)
        grounding_losses[axiom.id] = loss

    # Select minimum-loss axiom
    best_axiom_id = min(grounding_losses, key=grounding_losses.get)
    best_axiom = graph.get_node(best_axiom_id)
    best_loss = grounding_losses[best_axiom_id]

    if best_axiom is None:
        return None

    # Create grounding proof
    proof = Proof.categorical(
        data=f"Orphaned node: {orphaned_node.content[:50]}...",
        warrant=f"Re-grounded to axiom: {best_axiom.content[:50]}...",
        claim=f"Node is grounded by axiom with loss {best_loss:.3f}",
        principles=("COMPOSABLE",),
    )

    # Create grounding edge
    edge = ZeroEdge(
        source=best_axiom.id,
        target=orphaned_node.id,
        kind=EdgeKind.GROUNDED_BY,
        galois_loss=best_loss,
        proof=proof,
        metadata={"recovery": True, "pre_collapse_ancestors": list(orphaned_node.lineage)},
    )

    return (best_axiom, edge)


# =============================================================================
# Synthesis from Contradiction (from spec Part II.3)
# =============================================================================


async def synthesize_from_contradiction(
    node_a: ZeroNode,
    node_b: ZeroNode,
    galois: GaloisLossComputer,
) -> ZeroNode | None:
    """
    Synthesize a new node from contradicting nodes.

    When A and B contradict (super-additive loss), generate C that:
    1. Subsumes both A and B
    2. Has lower loss than either
    3. Is at the higher layer of A and B

    Note: Full implementation would use LLM for synthesis.
    This is a simplified version for demonstration.
    """
    analysis = is_contradiction(node_a, node_b, galois)
    if not analysis.is_contradiction:
        return None  # No synthesis needed

    # Simplified synthesis: combine content with reconciliation
    synthesis_content = (
        f"Synthesis of: ({node_a.content}) AND ({node_b.content}). "
        f"Reconciliation: Both views have merit when considered in proper context."
    )

    # Create synthesis proof
    proof = Proof(
        data=f"Thesis: {node_a.content[:30]}... Antithesis: {node_b.content[:30]}...",
        warrant="Dialectical synthesis transcends both positions",
        claim=synthesis_content[:100],
        backing=f"Super-additive loss {analysis.strength:.3f} indicates genuine tension",
        qualifier="arguably",
        rebuttals=("Unless one position is strictly superior",),
        tier=EvidenceTier.AESTHETIC,
        principles=("GENERATIVE", "COMPOSABLE"),
    )

    synthesis_node = ZeroNode(
        id=f"node-{uuid4().hex[:12]}",
        layer=max(node_a.layer, node_b.layer),
        kind=NodeKind.SYNTHESIS,
        content=synthesis_content,
        proof=proof,
        lineage=(node_a.id, node_b.id),
        galois_loss=0.0,  # Will be computed
        entropy_budget=min(node_a.entropy_budget, node_b.entropy_budget),
    )

    # Verify synthesis has lower loss
    synthesis_loss = galois.compute(synthesis_node)
    if synthesis_loss >= min(analysis.individual_loss_a, analysis.individual_loss_b):
        logger.warning("Synthesis did not reduce loss. Returning None.")
        return None

    return synthesis_node.with_loss(synthesis_loss)


# =============================================================================
# Checkpoint Replay (from spec Part IV.4)
# =============================================================================


async def replay_from_checkpoint(
    walk: Walk,
    collapse_time: datetime,
    graph: ZeroGraph,
    galois: GaloisLossComputer,
) -> ZeroGraph:
    """
    Recover graph by replaying Walk from last coherent checkpoint.

    Process:
    1. Find last Mark before collapse with coherent proof
    2. Reset graph to that Mark's state
    3. Replay subsequent Marks with loss monitoring
    4. Skip high-loss Marks

    Note: Simplified implementation - full version would reconstruct graph state.
    """
    # This would require access to Mark store
    # Simplified: just return a filtered copy of the current graph
    logger.info(f"Replaying from checkpoint before {collapse_time}")

    # Remove high-loss nodes
    stable_nodes = [n for n in graph.nodes.values() if galois.compute(n) < 0.7]

    result = ZeroGraph()
    for node in stable_nodes:
        result.add_node(node)

    # Keep edges between stable nodes
    stable_ids = {n.id for n in stable_nodes}
    for edge in graph.edges:
        if edge.source in stable_ids and edge.target in stable_ids:
            result.add_edge(edge)

    return result


# =============================================================================
# Early Warning System (from spec Part VI.1)
# =============================================================================


@dataclass
class EarlyWarningSystem:
    """
    Monitor Zero Seed graph for collapse indicators.

    Runs asynchronously, emits alerts when thresholds crossed.
    """

    galois: GaloisLossComputer = field(default_factory=DefaultGaloisLoss)
    alert_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "critical": 0.8,
            "warning": 0.6,
            "monitoring": 0.3,
        }
    )
    monitoring_interval: timedelta = timedelta(minutes=5)

    async def monitor(self, graph: ZeroGraph) -> AsyncIterator[Alert]:
        """
        Continuous monitoring loop.

        Yields alerts when instability detected.
        """
        while True:
            score = instability_score(graph, self.galois)
            indicators = compute_instability_indicators(graph, self.galois)

            if score >= self.alert_thresholds["critical"]:
                yield Alert(
                    level=AlertLevel.CRITICAL,
                    message="Graph collapse imminent",
                    score=score,
                    recommended_action="Immediate constitutional intervention required",
                    indicators=indicators.to_dict(),
                )
            elif score >= self.alert_thresholds["warning"]:
                yield Alert(
                    level=AlertLevel.WARNING,
                    message="High instability detected",
                    score=score,
                    recommended_action="Monitor closely, consider Galois restructure",
                    indicators=indicators.to_dict(),
                )
            elif score >= self.alert_thresholds["monitoring"]:
                yield Alert(
                    level=AlertLevel.INFO,
                    message="Instability increasing",
                    score=score,
                    recommended_action="Continue monitoring",
                    indicators=indicators.to_dict(),
                )

            await asyncio.sleep(self.monitoring_interval.total_seconds())

    def diagnose(self, graph: ZeroGraph) -> DiagnosticReport:
        """Detailed diagnostic when alert triggered."""
        return diagnose_graph(graph, self.galois)

    def check_once(self, graph: ZeroGraph) -> Alert | None:
        """Check graph once and return alert if needed."""
        score = instability_score(graph, self.galois)
        indicators = compute_instability_indicators(graph, self.galois)

        if score >= self.alert_thresholds["critical"]:
            return Alert(
                level=AlertLevel.CRITICAL,
                message="Graph collapse imminent",
                score=score,
                recommended_action="Immediate constitutional intervention required",
                indicators=indicators.to_dict(),
            )
        elif score >= self.alert_thresholds["warning"]:
            return Alert(
                level=AlertLevel.WARNING,
                message="High instability detected",
                score=score,
                recommended_action="Monitor closely, consider Galois restructure",
                indicators=indicators.to_dict(),
            )
        elif score >= self.alert_thresholds["monitoring"]:
            return Alert(
                level=AlertLevel.INFO,
                message="Instability increasing",
                score=score,
                recommended_action="Continue monitoring",
                indicators=indicators.to_dict(),
            )

        return None


# =============================================================================
# Bifurcation Detection (from spec Part III)
# =============================================================================


@dataclass
class BifurcationEvent:
    """A detected bifurcation event."""

    timestamp: datetime
    loss_before: float
    loss_after: float
    threshold_crossed: CriticalThreshold
    topology_before: GraphTopology
    topology_after: GraphTopology
    event_type: str  # "fold", "cusp", "layer_split", "layer_merge", etc.

    @property
    def is_major(self) -> bool:
        """Check if this is a major bifurcation (large topology change)."""
        return self.topology_before.distance_from(self.topology_after) > 0.3


def detect_bifurcation(
    graph_before: ZeroGraph,
    graph_after: ZeroGraph,
    galois: GaloisLossComputer | None = None,
) -> BifurcationEvent | None:
    """
    Detect if a bifurcation occurred between two graph states.

    A bifurcation is detected when:
    1. Loss crosses a critical threshold
    2. Topology changes discontinuously
    """
    if galois is None:
        galois = DefaultGaloisLoss()

    loss_before = galois.compute_graph(graph_before)
    loss_after = galois.compute_graph(graph_after)

    topo_before = compute_topology(graph_before, galois)
    topo_after = compute_topology(graph_after, galois)

    # Check if a threshold was crossed
    threshold_crossed = None
    for threshold in CriticalThreshold:
        if loss_before < threshold.value <= loss_after:
            threshold_crossed = threshold
            break
        if loss_after < threshold.value <= loss_before:
            threshold_crossed = threshold
            break

    if threshold_crossed is None:
        return None

    # Determine event type based on topology changes
    event_type = "threshold_cross"
    if topo_before.num_fixed_points != topo_after.num_fixed_points:
        if topo_after.num_fixed_points < topo_before.num_fixed_points:
            event_type = "axiom_collapse"
        else:
            event_type = "axiom_emergence"
    elif abs(topo_before.layer_entropy - topo_after.layer_entropy) > 0.2:
        if topo_after.layer_entropy > topo_before.layer_entropy:
            event_type = "layer_split"
        else:
            event_type = "layer_merge"

    return BifurcationEvent(
        timestamp=datetime.now(),
        loss_before=loss_before,
        loss_after=loss_after,
        threshold_crossed=threshold_crossed,
        topology_before=topo_before,
        topology_after=topo_after,
        event_type=event_type,
    )


# =============================================================================
# Bifurcation History Tracking
# =============================================================================


@dataclass
class BifurcationHistory:
    """Track bifurcation events over time."""

    events: list[BifurcationEvent] = field(default_factory=list)

    def add(self, event: BifurcationEvent) -> None:
        """Add a bifurcation event."""
        self.events.append(event)

    def recent(self, hours: int = 24) -> list[BifurcationEvent]:
        """Get events in the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self.events if e.timestamp > cutoff]

    def major_events(self) -> list[BifurcationEvent]:
        """Get major bifurcation events."""
        return [e for e in self.events if e.is_major]

    @property
    def collapse_count(self) -> int:
        """Count collapse events."""
        return sum(1 for e in self.events if "collapse" in e.event_type)


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Thresholds
    "CriticalThreshold",
    "THRESHOLD_TO_LAYER",
    # Node and Edge types
    "NodeKind",
    "EdgeKind",
    "ZeroNode",
    "ZeroEdge",
    # Graph
    "ZeroGraph",
    # Galois Loss
    "GaloisLossComputer",
    "DefaultGaloisLoss",
    # Alerts
    "AlertLevel",
    "Alert",
    # Indicators
    "InstabilityIndicators",
    "compute_instability_indicators",
    "instability_score",
    # Imminence
    "CollapseImminence",
    "classify_imminence",
    # Contradiction
    "ContradictionAnalysis",
    "is_contradiction",
    # Topology
    "GraphTopology",
    "compute_topology",
    # Recovery
    "StrategyType",
    "RecoveryStrategy",
    "Intervention",
    "ConstitutionalRecoveryPlan",
    "select_recovery_strategy",
    # Diagnostics
    "DiagnosticReport",
    "diagnose_graph",
    # Recovery algorithms
    "reground_to_axiom",
    "synthesize_from_contradiction",
    "replay_from_checkpoint",
    # Early Warning
    "EarlyWarningSystem",
    # Bifurcation
    "BifurcationEvent",
    "detect_bifurcation",
    "BifurcationHistory",
]
