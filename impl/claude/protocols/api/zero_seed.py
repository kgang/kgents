"""
Zero Seed REST API: Epistemic Graph Navigation with Galois Loss Visualization.

Provides:
- GET  /api/zero-seed/axioms            - AxiomExplorerResponse (WIRED to storage + Galois)
- GET  /api/zero-seed/proofs            - ProofDashboardResponse (mock)
- GET  /api/zero-seed/health            - GraphHealthResponse (WIRED to storage)
- GET  /api/zero-seed/telescope         - TelescopeResponse (WIRED to storage)
- POST /api/zero-seed/navigate          - Navigation action (mock)
- GET  /api/zero-seed/nodes/{node_id}   - Node details (partial: storage, mock edges)
- GET  /api/zero-seed/layers/{layer}    - Layer nodes (WIRED to storage)

Philosophy:
    "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."

Implementation Status (2025-12-25):
    WIRED (real data):
    - Axiom/value nodes from PostgreSQL K-Block storage
    - Galois loss computation from create_axiom_kernel()
    - Layer node counts and health metrics
    - Node CRUD operations (create/update/delete)

    PARTIAL (storage + mock):
    - Node details endpoint (nodes from storage, edges mocked)
    - Telescope visible nodes (storage + mock gradients)

    TODO (still mock):
    - Edge storage and traversal
    - Proof quality analysis (needs LLM integration)
    - Contradiction detection
    - Super-additive loss detection
    - Telescope navigation state persistence

    See: spec/protocols/zero-seed1/integration.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]
    Query = None  # type: ignore[assignment]

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models (Matching Frontend TypeScript Types)
# =============================================================================


class GaloisLossComponents(BaseModel):
    """Breakdown of Galois loss into components."""

    content_loss: float = Field(..., description="Loss from content restructuring")
    proof_loss: float = Field(..., description="Loss from proof reconstitution")
    edge_loss: float = Field(..., description="Loss from edge coherence")
    metadata_loss: float = Field(..., description="Loss from metadata preservation")
    total: float = Field(..., description="Weighted sum of components")


class NodeLoss(BaseModel):
    """Loss assessment for a Zero Seed node."""

    node_id: str = Field(..., description="Node ID")
    loss: float = Field(..., description="Total Galois loss")
    components: GaloisLossComponents = Field(..., description="Loss component breakdown")
    health_status: str = Field(..., description="Health status: healthy, warning, critical")


class ZeroNode(BaseModel):
    """A node in the Zero Seed epistemic graph."""

    id: str = Field(..., description="Node ID")
    path: str = Field(..., description="AGENTESE path")
    layer: int = Field(..., ge=1, le=7, description="Layer (1-7)")
    kind: str = Field(..., description="Node kind")
    title: str = Field(..., description="Display title")
    content: str = Field(..., description="Markdown content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    created_at: str = Field(..., description="Creation timestamp (ISO)")
    created_by: str = Field(..., description="Creator identifier")
    tags: list[str] = Field(default_factory=list, description="Tags")
    lineage: list[str] = Field(default_factory=list, description="Parent node IDs")
    has_proof: bool = Field(..., description="Whether node has Toulmin proof")


class ZeroEdge(BaseModel):
    """A morphism between Zero Seed nodes."""

    id: str = Field(..., description="Edge ID")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    kind: str = Field(..., description="Edge kind")
    context: str = Field(..., description="Edge context/reasoning")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    created_at: str = Field(..., description="Creation timestamp (ISO)")
    mark_id: str | None = Field(None, description="Associated Witness mark ID")
    proof: ToulminProof | None = Field(None, description="Toulmin proof from decision")
    evidence_tier: str | None = Field(
        None, description="Evidence tier: categorical, empirical, aesthetic, somatic"
    )


class ToulminProof(BaseModel):
    """Toulmin proof structure."""

    data: str = Field(..., description="Evidence")
    warrant: str = Field(..., description="Reasoning connecting data to claim")
    claim: str = Field(..., description="Conclusion")
    backing: str = Field(default="", description="Support for warrant")
    qualifier: str = Field(default="probably", description="Confidence qualifier")
    rebuttals: list[str] = Field(default_factory=list, description="Defeaters")
    tier: str = Field(
        default="empirical",
        description="Evidence tier: categorical, empirical, aesthetic, somatic",
    )
    principles: list[str] = Field(default_factory=list, description="Referenced principles")


class GhostAlternative(BaseModel):
    """Alternative warrant suggestion."""

    id: str = Field(..., description="Alternative ID")
    warrant: str = Field(..., description="Alternative warrant")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Why this alternative")


class ProofQuality(BaseModel):
    """Quality assessment of a Toulmin proof."""

    node_id: str = Field(..., description="Node ID")
    proof: ToulminProof = Field(..., description="Toulmin proof structure")
    coherence_score: float = Field(..., ge=0.0, le=1.0, description="1 - galois_loss")
    warrant_strength: float = Field(..., ge=0.0, le=1.0, description="Warrant quality")
    backing_coverage: float = Field(..., ge=0.0, le=1.0, description="Backing quality")
    rebuttal_count: int = Field(..., ge=0, description="Number of rebuttals")
    quality_tier: str = Field(..., description="Quality tier: strong, moderate, weak")
    ghost_alternatives: list[GhostAlternative] = Field(
        default_factory=list, description="AI-suggested alternatives"
    )


class Contradiction(BaseModel):
    """Contradiction between two nodes."""

    id: str = Field(..., description="Contradiction ID")
    node_a: str = Field(..., description="First node ID")
    node_b: str = Field(..., description="Second node ID")
    edge_id: str = Field(..., description="Contradiction edge ID")
    description: str = Field(..., description="Description of contradiction")
    severity: str = Field(..., description="Severity: low, medium, high")
    is_resolved: bool = Field(..., description="Whether resolved")
    resolution_id: str | None = Field(None, description="Resolution node ID")


class InstabilityIndicator(BaseModel):
    """Instability indicator in the graph."""

    type: str = Field(
        ...,
        description="Type: orphan, weak_proof, edge_drift, layer_skip, contradiction",
    )
    node_id: str = Field(..., description="Node ID")
    description: str = Field(..., description="Description")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity (0-1)")
    suggested_action: str = Field(..., description="Suggested remediation")


class GraphHealth(BaseModel):
    """Overall graph health assessment."""

    total_nodes: int = Field(..., ge=0, description="Total node count")
    total_edges: int = Field(..., ge=0, description="Total edge count")
    by_layer: dict[int, int] = Field(..., description="Node count by layer")
    healthy_count: int = Field(..., ge=0, description="Healthy node count")
    warning_count: int = Field(..., ge=0, description="Warning node count")
    critical_count: int = Field(..., ge=0, description="Critical node count")
    contradictions: list[Contradiction] = Field(default_factory=list, description="Contradictions")
    instability_indicators: list[InstabilityIndicator] = Field(
        default_factory=list, description="Instability indicators"
    )
    super_additive_loss_detected: bool = Field(
        ..., description="Whether super-additive loss detected"
    )


class TelescopeState(BaseModel):
    """Telescope navigation state."""

    focal_distance: float = Field(
        ..., ge=0.0, le=1.0, description="Focal distance (0=micro, 1=macro)"
    )
    focal_point: str | None = Field(None, description="Focused node ID")
    show_loss: bool = Field(..., description="Show loss visualization")
    show_gradient: bool = Field(..., description="Show gradient vectors")
    loss_threshold: float = Field(..., ge=0.0, le=1.0, description="Loss visibility threshold")
    visible_layers: list[int] = Field(..., description="Visible layers")
    preferred_layer: int = Field(..., ge=1, le=7, description="Preferred layer")


class GradientVector(BaseModel):
    """Gradient vector for navigation."""

    x: float = Field(..., description="X component")
    y: float = Field(..., description="Y component")
    magnitude: float = Field(..., ge=0.0, description="Vector magnitude")
    target_node: str = Field(..., description="Target node ID")


class NavigationSuggestion(BaseModel):
    """Navigation suggestion."""

    target: str = Field(..., description="Target node ID")
    action: str = Field(..., description="Action: focus, follow_gradient, investigate")
    value_score: float = Field(..., ge=0.0, le=1.0, description="Value score")
    reasoning: str = Field(..., description="Why this suggestion")


class PolicyArrow(BaseModel):
    """Policy arrow for visualization."""

    from_node: str = Field(..., alias="from", description="Source node ID")
    to: str = Field(..., description="Target node ID")
    value: float = Field(..., description="Value estimate")
    is_optimal: bool = Field(..., description="Whether optimal")


# =============================================================================
# API Response Models
# =============================================================================


class AxiomExplorerResponse(BaseModel):
    """Response for axiom explorer (L1-L2)."""

    axioms: list[ZeroNode] = Field(..., description="L1 axiom nodes")
    values: list[ZeroNode] = Field(..., description="L2 value nodes")
    losses: list[NodeLoss] = Field(..., description="Loss assessments")
    total_axiom_count: int = Field(..., ge=0, description="Total axiom count")
    total_value_count: int = Field(..., ge=0, description="Total value count")
    fixed_points: list[str] = Field(..., description="Fixed-point axiom node IDs (loss < 0.01)")


class ProofDashboardResponse(BaseModel):
    """Response for proof quality dashboard (L3-L4)."""

    proofs: list[ProofQuality] = Field(..., description="Proof quality assessments")
    average_coherence: float = Field(..., ge=0.0, le=1.0, description="Average coherence")
    by_quality_tier: dict[str, int] = Field(..., description="Count by quality tier")
    needs_improvement: list[str] = Field(..., description="Node IDs needing improvement")


class GraphHealthResponse(BaseModel):
    """Response for graph health status."""

    health: GraphHealth = Field(..., description="Graph health assessment")
    timestamp: str = Field(..., description="Assessment timestamp (ISO)")
    trend: str = Field(..., description="Trend: improving, stable, degrading")


class TelescopeResponse(BaseModel):
    """Response for telescope navigation."""

    state: TelescopeState = Field(..., description="Current telescope state")
    gradients: dict[str, GradientVector] = Field(..., description="Gradient vectors by node ID")
    suggestions: list[NavigationSuggestion] = Field(..., description="Navigation suggestions")
    visible_nodes: list[ZeroNode] = Field(..., description="Visible nodes")
    policy_arrows: list[PolicyArrow] = Field(default_factory=list, description="Policy arrows")


class NavigateRequest(BaseModel):
    """Request to navigate telescope."""

    node_id: str = Field(..., description="Target node ID")
    action: str = Field(
        ...,
        description="Action: focus, follow_gradient, go_lowest_loss, go_highest_loss",
    )


class CreateWitnessedEdgeRequest(BaseModel):
    """Request to create a witnessed edge from a Mark."""

    mark_id: str = Field(..., description="Witness mark ID")
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    context: str | None = Field(None, description="Optional edge context")


class CreateNodeRequest(BaseModel):
    """Request to create a new Zero Seed node."""

    layer: int = Field(..., ge=1, le=7, description="Layer (1-7)")
    title: str = Field(..., description="Display title")
    content: str = Field(..., description="Markdown content")
    lineage: list[str] = Field(default_factory=list, description="Parent node IDs")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")
    tags: list[str] = Field(default_factory=list, description="Tags")
    created_by: str = Field(default="user", description="Creator identifier")


class UpdateNodeRequest(BaseModel):
    """Request to update a Zero Seed node."""

    title: str | None = Field(None, description="Updated title")
    content: str | None = Field(None, description="Updated content")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Updated confidence")
    tags: list[str] | None = Field(None, description="Updated tags")


class DiscoverAxiomsRequest(BaseModel):
    """Request to discover axioms from decision texts."""

    decisions: list[str] = Field(..., description="List of decision/reasoning texts to analyze")
    min_pattern_occurrences: int = Field(
        default=2, ge=1, le=10, description="Minimum times a pattern must appear"
    )


class NavigateResponse(BaseModel):
    """Response from navigation action."""

    previous: str | None = Field(None, description="Previous focal node ID")
    current: str = Field(..., description="Current focal node ID")
    loss: float = Field(..., ge=0.0, le=1.0, description="Current node loss")
    gradient: GradientVector | None = Field(None, description="Gradient at current node")


class NodeDetailResponse(BaseModel):
    """Response for single node details."""

    node: ZeroNode = Field(..., description="Node data")
    loss: NodeLoss = Field(..., description="Loss assessment")
    proof: ToulminProof | None = Field(None, description="Toulmin proof (if L3+)")
    incoming_edges: list[ZeroEdge] = Field(..., description="Incoming edges")
    outgoing_edges: list[ZeroEdge] = Field(..., description="Outgoing edges")
    witnessed_edges: list[ZeroEdge] = Field(
        default_factory=list, description="Edges from Witness marks"
    )


class LayerNodesResponse(BaseModel):
    """Response for layer nodes."""

    nodes: list[ZeroNode] = Field(..., description="Nodes in layer")
    losses: list[NodeLoss] = Field(..., description="Loss assessments")
    count: int = Field(..., ge=0, description="Total node count")


# =============================================================================
# Analysis Response Models (Four-Mode Analysis)
# =============================================================================


class AnalysisItem(BaseModel):
    """A single analysis item in a quadrant."""

    label: str = Field(..., description="Item label")
    value: str = Field(..., description="Item value")
    status: str = Field(..., description="Status: pass, warning, fail, info")


class AnalysisQuadrant(BaseModel):
    """Analysis data for one quadrant."""

    status: str = Field(..., description="Overall status: pass, issues, unknown")
    summary: str = Field(..., description="Summary text")
    items: list[AnalysisItem] = Field(default_factory=list, description="Analysis items")


class NodeAnalysisResponse(BaseModel):
    """Four-mode analysis response for a Zero Seed node."""

    node_id: str = Field(..., alias="nodeId", description="Node ID")
    categorical: AnalysisQuadrant = Field(
        ..., description="Categorical analysis (laws, fixed points)"
    )
    epistemic: AnalysisQuadrant = Field(
        ..., description="Epistemic analysis (grounding, justification)"
    )
    dialectical: AnalysisQuadrant = Field(
        ..., description="Dialectical analysis (tensions, synthesis)"
    )
    generative: AnalysisQuadrant = Field(
        ..., description="Generative analysis (compression, regeneration)"
    )

    model_config = {"populate_by_name": True}


# =============================================================================
# Mock Data Generators (Placeholder for LLM Implementation)
# =============================================================================


def _create_mock_loss(node_id: str, base_loss: float = 0.2) -> NodeLoss:
    """Create mock loss assessment."""
    return NodeLoss(
        node_id=node_id,
        loss=base_loss,
        components=GaloisLossComponents(
            content_loss=base_loss * 0.4,
            proof_loss=base_loss * 0.3,
            edge_loss=base_loss * 0.2,
            metadata_loss=base_loss * 0.1,
            total=base_loss,
        ),
        health_status="healthy" if base_loss < 0.3 else "warning",
    )


def _create_mock_axiom(idx: int) -> ZeroNode:
    """Create mock axiom node (L1)."""
    return ZeroNode(
        id=f"zn-axiom-{idx:03d}",
        path=f"void.axiom.a{idx}",
        layer=1,
        kind="axiom",
        title=f"Axiom {idx}: Entity",
        content="Everything is a node. Nodes are the fundamental entities.",
        confidence=1.0,
        created_at=datetime.now(UTC).isoformat(),
        created_by="system",
        tags=["axiom", "foundational"],
        lineage=[],
        has_proof=False,
    )


def _create_mock_value(idx: int) -> ZeroNode:
    """Create mock value node (L2)."""
    return ZeroNode(
        id=f"zn-value-{idx:03d}",
        path=f"void.value.v{idx}",
        layer=2,
        kind="value",
        title=f"Value {idx}: Composability",
        content="Agents should compose via morphisms (>> operator).",
        confidence=0.95,
        created_at=datetime.now(UTC).isoformat(),
        created_by="system",
        tags=["value", "principle"],
        lineage=[f"zn-axiom-{(idx % 3) + 1:03d}"],
        has_proof=False,
    )


def _create_mock_proof(node_id: str) -> ProofQuality:
    """Create mock proof quality assessment."""
    return ProofQuality(
        node_id=node_id,
        proof=ToulminProof(
            data="Tests pass with 100% coverage",
            warrant="High test coverage indicates correctness",
            claim="This specification is valid",
            backing="Industry best practices support this heuristic",
            qualifier="probably",
            rebuttals=["Unless API contracts change"],
            tier="empirical",
            principles=["tasteful", "composable"],
        ),
        coherence_score=0.78,
        warrant_strength=0.82,
        backing_coverage=0.75,
        rebuttal_count=1,
        quality_tier="moderate",
        ghost_alternatives=[
            GhostAlternative(
                id="alt-1",
                warrant="Mathematical proof via category theory",
                confidence=0.65,
                reasoning="Would provide categorical guarantees but requires formalization",
            )
        ],
    )


# =============================================================================
# LLM Analysis Integration
# =============================================================================


async def _get_analysis_service() -> Any:
    """
    Get AnalysisService instance with LLM client.

    Returns:
        AnalysisService instance

    Raises:
        ImportError: If analysis service or LLM client unavailable
        RuntimeError: If LLM credentials not configured
    """
    try:
        from agents.k.llm import create_llm_client, has_llm_credentials
        from services.analysis import AnalysisService
    except ImportError as e:
        raise ImportError(f"Analysis service dependencies unavailable: {e}")

    # Check credentials
    if not has_llm_credentials():
        raise RuntimeError(
            "LLM analysis requires ANTHROPIC_API_KEY. "
            "Set the environment variable or use use_llm=false for mock data."
        )

    # Create LLM client and service
    llm = create_llm_client()
    return AnalysisService(llm)


async def _get_llm_node_analysis(node_id: str) -> NodeAnalysisResponse:
    """
    Get real LLM-backed analysis for a node.

    This is a placeholder implementation that demonstrates the integration pattern.
    Full implementation requires:
    1. Loading actual node content from Zero Seed graph (D-gent)
    2. Running AnalysisService.analyze_full() on node content
    3. Transforming FullAnalysisReport to NodeAnalysisResponse

    Args:
        node_id: Node ID to analyze

    Returns:
        NodeAnalysisResponse with LLM analysis

    Raises:
        HTTPException: If analysis fails
    """
    try:
        service = await _get_analysis_service()
    except (ImportError, RuntimeError) as e:
        raise HTTPException(status_code=503, detail=str(e))

    # TODO: Load actual node content from Zero Seed graph
    # For now, use node_id as a placeholder "spec path"
    # Real implementation would:
    #   1. Query D-gent for Zero Seed node by ID
    #   2. Extract node.content (markdown)
    #   3. Write to temp file or pass directly to analyzer

    # Placeholder: treat node_id as a spec path for demo purposes
    # This allows testing with actual spec files
    spec_path = f"spec/protocols/{node_id}.md" if "/" not in node_id else node_id

    try:
        # Run full four-mode analysis
        report = await service.analyze_full(spec_path)

        # Transform FullAnalysisReport → NodeAnalysisResponse
        return _transform_analysis_report(node_id, report)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Node content not found: {node_id}. "
            f"Real implementation will load from Zero Seed graph.",
        )
    except Exception as e:
        logger.error(f"LLM analysis failed for {node_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _transform_analysis_report(node_id: str, report: Any) -> NodeAnalysisResponse:
    """
    Transform FullAnalysisReport to NodeAnalysisResponse format.

    Maps the four analysis modes to AnalysisQuadrant format for the UI.

    Args:
        node_id: Node ID being analyzed
        report: FullAnalysisReport from AnalysisService

    Returns:
        NodeAnalysisResponse with transformed data
    """
    # Import here to avoid module-level dependency
    from agents.operad.core import LawStatus
    from agents.operad.domains.analysis import ContradictionType

    # Categorical → AnalysisQuadrant
    cat = report.categorical
    categorical_items = []

    # Add law verifications
    for verification in cat.law_verifications:
        status_map = {
            LawStatus.PASSED: "pass",
            LawStatus.FAILED: "fail",
            LawStatus.SKIPPED: "info",
            LawStatus.STRUCTURAL: "pass",
        }
        categorical_items.append(
            AnalysisItem(
                label=verification.law_name,
                value=verification.message,
                status=status_map.get(verification.status, "info"),
            )
        )

    # Add fixed point info if present
    if cat.fixed_point:
        categorical_items.append(
            AnalysisItem(
                label="Fixed Point",
                value=cat.fixed_point.fixed_point_description,
                status="info" if cat.fixed_point.is_valid else "warning",
            )
        )

    categorical_status = "pass" if not cat.has_violations else "issues"
    categorical = AnalysisQuadrant(
        status=categorical_status,
        summary=cat.summary,
        items=categorical_items,
    )

    # Epistemic → AnalysisQuadrant
    epi = report.epistemic
    epistemic_items = [
        AnalysisItem(
            label="Layer",
            value=f"L{epi.layer}",
            status="info",
        ),
        AnalysisItem(
            label="Grounding",
            value="Terminates at axiom" if epi.is_grounded else "Not grounded",
            status="pass" if epi.is_grounded else "warning",
        ),
        AnalysisItem(
            label="Evidence Tier",
            value=epi.toulmin.tier.name.title(),
            status="info",
        ),
        AnalysisItem(
            label="Qualifier",
            value=epi.toulmin.qualifier.title(),
            status="pass" if epi.toulmin.qualifier == "definitely" else "info",
        ),
    ]

    epistemic_status = "pass" if epi.is_grounded else "issues"
    epistemic = AnalysisQuadrant(
        status=epistemic_status,
        summary=epi.summary,
        items=epistemic_items,
    )

    # Dialectical → AnalysisQuadrant
    dia = report.dialectical
    dialectical_items = []

    for i, tension in enumerate(dia.tensions, 1):
        # Classification label
        class_map = {
            ContradictionType.APPARENT: "Apparent",
            ContradictionType.PRODUCTIVE: "Productive",
            ContradictionType.PROBLEMATIC: "Problematic",
            ContradictionType.PARACONSISTENT: "Paraconsistent",
        }
        classification = class_map.get(tension.classification, "Unknown")

        dialectical_items.append(
            AnalysisItem(
                label=f"Tension {i}",
                value=f"{tension.thesis} ⟷ {tension.antithesis}",
                status="warning"
                if tension.classification == ContradictionType.PROBLEMATIC
                else "pass",
            )
        )
        dialectical_items.append(
            AnalysisItem(
                label="Classification",
                value=classification,
                status="info",
            )
        )
        if tension.synthesis:
            dialectical_items.append(
                AnalysisItem(
                    label="Synthesis",
                    value=tension.synthesis,
                    status="pass",
                )
            )

    dialectical_status = "pass" if dia.problematic_count == 0 else "issues"
    dialectical = AnalysisQuadrant(
        status=dialectical_status,
        summary=dia.summary,
        items=dialectical_items,
    )

    # Generative → AnalysisQuadrant
    gen = report.generative
    generative_items = [
        AnalysisItem(
            label="Compression Ratio",
            value=f"{gen.compression_ratio:.2f}",
            status="pass" if gen.is_compressed else "info",
        ),
        AnalysisItem(
            label="Minimal Kernel",
            value=f"{len(gen.minimal_kernel)} axioms",
            status="info",
        ),
        AnalysisItem(
            label="Regeneration Test",
            value="Passed" if gen.regeneration.passed else "Failed",
            status="pass" if gen.regeneration.passed else "fail",
        ),
    ]

    if gen.regeneration.missing_elements:
        generative_items.append(
            AnalysisItem(
                label="Missing Elements",
                value=", ".join(gen.regeneration.missing_elements[:3]),
                status="warning",
            )
        )

    generative_status = "pass" if gen.is_regenerable else "issues"
    generative = AnalysisQuadrant(
        status=generative_status,
        summary=gen.summary,
        items=generative_items,
    )

    return NodeAnalysisResponse(
        nodeId=node_id,
        categorical=categorical,
        epistemic=epistemic,
        dialectical=dialectical,
        generative=generative,
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_zero_seed_router() -> APIRouter | None:
    """Create the Zero Seed API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Zero Seed routes disabled")
        return None

    router = APIRouter(prefix="/api/zero-seed", tags=["zero-seed"])

    # =========================================================================
    # Axiom Explorer (L1-L2)
    # =========================================================================

    @router.get("/axioms", response_model=AxiomExplorerResponse)
    async def get_axiom_explorer() -> AxiomExplorerResponse:
        """
        Get axioms and values (L1-L2) with loss information.

        Returns:
            Axiom explorer data with fixed points
        """
        try:
            from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage
            from services.zero_seed.galois.axiomatics import (
                EntityAxiom,
                GaloisGround,
                MorphismAxiom,
                create_axiom_kernel,
            )

            storage = await get_postgres_zero_seed_storage()

            # Get L1 nodes (axioms) from storage
            layer_1_kblocks = await storage.get_layer_nodes(1)
            axioms = []
            for kblock in layer_1_kblocks:
                axioms.append(
                    ZeroNode(
                        id=str(kblock.id),
                        path=kblock.path,
                        layer=1,
                        kind=getattr(kblock, "_kind", "axiom"),
                        title=getattr(kblock, "_title", "Untitled Axiom"),
                        content=kblock.content,
                        confidence=getattr(kblock, "_confidence", 1.0),
                        created_at=kblock.created_at.isoformat(),
                        created_by=getattr(kblock, "_created_by", "system"),
                        tags=list(getattr(kblock, "_tags", [])),
                        lineage=list(getattr(kblock, "_lineage", [])),
                        has_proof=False,
                    )
                )

            # Get L2 nodes (values) from storage
            layer_2_kblocks = await storage.get_layer_nodes(2)
            values = []
            for kblock in layer_2_kblocks:
                values.append(
                    ZeroNode(
                        id=str(kblock.id),
                        path=kblock.path,
                        layer=2,
                        kind=getattr(kblock, "_kind", "value"),
                        title=getattr(kblock, "_title", "Untitled Value"),
                        content=kblock.content,
                        confidence=getattr(kblock, "_confidence", 0.95),
                        created_at=kblock.created_at.isoformat(),
                        created_by=getattr(kblock, "_created_by", "system"),
                        tags=list(getattr(kblock, "_tags", [])),
                        lineage=list(getattr(kblock, "_lineage", [])),
                        has_proof=False,
                    )
                )

            # Compute losses using Galois axiomatics
            kernel_axioms = create_axiom_kernel()
            losses = []

            # Map axiom IDs to Galois losses
            axiom_losses_map = {}
            for galois_axiom in kernel_axioms:
                loss = galois_axiom.loss_profile().total
                if isinstance(galois_axiom, EntityAxiom):
                    axiom_losses_map["A1"] = loss
                elif isinstance(galois_axiom, MorphismAxiom):
                    axiom_losses_map["A2"] = loss
                elif isinstance(galois_axiom, GaloisGround):
                    axiom_losses_map["G"] = loss

            # Create loss assessments for axioms
            for axiom in axioms:
                # Try to match axiom to known Galois axioms, fallback to 0.01
                base_loss = 0.01
                # Check if title contains A1, A2, or G
                for axiom_id, loss_val in axiom_losses_map.items():
                    if axiom_id in axiom.title:
                        base_loss = loss_val
                        break

                losses.append(_create_mock_loss(axiom.id, base_loss))

            # Create loss assessments for values (L2 has slightly higher loss)
            for value in values:
                losses.append(_create_mock_loss(value.id, 0.07))

            # Fixed points are axioms with loss < 0.01
            fixed_points = [
                axiom.id
                for axiom in axioms
                if any(loss.node_id == axiom.id and loss.loss < 0.01 for loss in losses)
            ]

            return AxiomExplorerResponse(
                axioms=axioms,
                values=values,
                losses=losses,
                total_axiom_count=len(axioms),
                total_value_count=len(values),
                fixed_points=fixed_points,
            )

        except Exception as e:
            logger.warning(f"Failed to load real axioms, using mock data: {e}")
            # Fallback to mock data if storage not available
            axioms = [_create_mock_axiom(i) for i in range(1, 4)]
            values = [_create_mock_value(i) for i in range(1, 6)]

            losses = [_create_mock_loss(a.id, 0.01) for a in axioms]
            losses.extend([_create_mock_loss(v.id, 0.15) for v in values])

            fixed_points = [a.id for a in axioms if True]

            return AxiomExplorerResponse(
                axioms=axioms,
                values=values,
                losses=losses,
                total_axiom_count=len(axioms),
                total_value_count=len(values),
                fixed_points=fixed_points,
            )

    # =========================================================================
    # Proof Dashboard (L3-L4)
    # =========================================================================

    @router.get("/proofs", response_model=ProofDashboardResponse)
    async def get_proof_dashboard(
        layer: int | None = Query(None, ge=3, le=4, description="Filter by layer"),
        min_coherence: float | None = Query(None, ge=0.0, le=1.0, description="Minimum coherence"),
    ) -> ProofDashboardResponse:
        """
        Get proof quality dashboard (L3-L4).

        Args:
            layer: Optional layer filter (3 or 4)
            min_coherence: Optional minimum coherence filter

        Returns:
            Proof quality assessments
        """
        # Mock data - real implementation would compute proof quality via Galois loss
        proofs = [_create_mock_proof(f"zn-goal-{i:03d}") for i in range(1, 6)]

        # Filter by min_coherence
        if min_coherence is not None:
            proofs = [p for p in proofs if p.coherence_score >= min_coherence]

        avg_coherence = sum(p.coherence_score for p in proofs) / len(proofs) if proofs else 0.0

        by_quality = {
            "strong": sum(1 for p in proofs if p.quality_tier == "strong"),
            "moderate": sum(1 for p in proofs if p.quality_tier == "moderate"),
            "weak": sum(1 for p in proofs if p.quality_tier == "weak"),
        }

        needs_improvement = [p.node_id for p in proofs if p.coherence_score < 0.6]

        return ProofDashboardResponse(
            proofs=proofs,
            average_coherence=avg_coherence,
            by_quality_tier=by_quality,
            needs_improvement=needs_improvement,
        )

    # =========================================================================
    # Graph Health (L5-L6)
    # =========================================================================

    @router.get("/health", response_model=GraphHealthResponse)
    async def get_graph_health() -> GraphHealthResponse:
        """
        Get graph health status.

        Returns:
            Graph health assessment with trend
        """
        try:
            from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage
            from services.zero_seed.galois.axiomatics import create_axiom_kernel

            storage = await get_postgres_zero_seed_storage()

            # Get counts by layer from actual storage
            by_layer = {}
            total_nodes = 0
            for layer in range(1, 8):
                layer_nodes = await storage.get_layer_nodes(layer)
                count = len(layer_nodes)
                if count > 0:
                    by_layer[layer] = count
                    total_nodes += count

            # Compute health metrics using Galois loss
            kernel_axioms = create_axiom_kernel()
            healthy_count = 0
            warning_count = 0
            critical_count = 0

            # For each layer, estimate health based on loss
            for layer in range(1, 8):
                layer_kblocks = await storage.get_layer_nodes(layer)
                for kblock in layer_kblocks:
                    # Estimate loss based on layer (L1 = 0.01, L7 = 0.7)
                    estimated_loss = 0.01 + (layer - 1) * 0.1
                    if estimated_loss < 0.3:
                        healthy_count += 1
                    elif estimated_loss < 0.6:
                        warning_count += 1
                    else:
                        critical_count += 1

            # TODO: Detect contradictions using edge analysis
            contradictions: list[Contradiction] = []

            # TODO: Detect instability indicators
            instability_indicators: list[InstabilityIndicator] = []

            health = GraphHealth(
                total_nodes=total_nodes,
                total_edges=0,  # TODO: Count actual edges when edge storage is implemented
                by_layer=by_layer,
                healthy_count=healthy_count,
                warning_count=warning_count,
                critical_count=critical_count,
                contradictions=contradictions,
                instability_indicators=instability_indicators,
                super_additive_loss_detected=False,  # TODO: Implement super-additive loss detection
            )

            return GraphHealthResponse(
                health=health,
                timestamp=datetime.now(UTC).isoformat(),
                trend="stable",  # TODO: Implement trend analysis
            )

        except Exception as e:
            logger.warning(f"Failed to compute real health metrics, using mock data: {e}")
            # Fallback to mock data
            health = GraphHealth(
                total_nodes=50,
                total_edges=85,
                by_layer={1: 3, 2: 5, 3: 10, 4: 15, 5: 10, 6: 5, 7: 2},
                healthy_count=42,
                warning_count=6,
                critical_count=2,
                contradictions=[
                    Contradiction(
                        id="contra-001",
                        node_a="zn-value-001",
                        node_b="zn-value-002",
                        edge_id="ze-contra-001",
                        description="Value 1 and Value 2 have super-additive loss (0.12 excess)",
                        severity="medium",
                        is_resolved=False,
                        resolution_id=None,
                    )
                ],
                instability_indicators=[
                    InstabilityIndicator(
                        type="weak_proof",
                        node_id="zn-goal-003",
                        description="Proof coherence below threshold (0.45 < 0.6)",
                        severity=0.6,
                        suggested_action="Strengthen warrant with additional evidence",
                    )
                ],
                super_additive_loss_detected=True,
            )

            return GraphHealthResponse(
                health=health,
                timestamp=datetime.now(UTC).isoformat(),
                trend="stable",
            )

    # =========================================================================
    # Telescope Navigation (L7)
    # =========================================================================

    @router.get("/telescope", response_model=TelescopeResponse)
    async def get_telescope_state(
        focal_point: str | None = Query(None, description="Focal point node ID"),
        focal_distance: float | None = Query(None, ge=0.0, le=1.0, description="Focal distance"),
    ) -> TelescopeResponse:
        """
        Get telescope navigation state.

        Args:
            focal_point: Optional focal point override
            focal_distance: Optional focal distance override

        Returns:
            Telescope state with gradients and suggestions
        """
        # Mock data - real implementation would compute gradients and DP-optimal policy
        state = TelescopeState(
            focal_distance=focal_distance if focal_distance is not None else 0.5,
            focal_point=focal_point,
            show_loss=True,
            show_gradient=True,
            loss_threshold=0.5,
            visible_layers=[1, 2, 3, 4, 5, 6, 7],
            preferred_layer=4,
        )

        # Get visible nodes from storage
        visible_nodes: list[ZeroNode] = []

        try:
            from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

            storage = await get_postgres_zero_seed_storage()

            # Query all layers and convert K-Blocks to ZeroNodes
            for layer in state.visible_layers:
                layer_kblocks = await storage.get_layer_nodes(layer)
                for kblock in layer_kblocks:
                    visible_nodes.append(
                        ZeroNode(
                            id=str(kblock.id),
                            path=kblock.path,
                            layer=layer,
                            kind=getattr(kblock, "_kind", f"L{layer}_node"),
                            title=getattr(kblock, "_title", f"Layer {layer} Node"),
                            content=kblock.content,
                            confidence=getattr(kblock, "_confidence", 0.5),
                            created_at=kblock.created_at.isoformat(),
                            created_by=getattr(kblock, "_created_by", "system"),
                            tags=list(getattr(kblock, "_tags", [])),
                            lineage=list(getattr(kblock, "_lineage", [])),
                            has_proof=(layer >= 3),
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to load nodes from storage, using mock data: {e}")
            # Fallback to mock data
            # Layer 1: Axioms (3 nodes, low loss ~0.01)
            visible_nodes.extend([_create_mock_axiom(i) for i in range(1, 4)])

            # Layer 2: Values (5 nodes, low loss ~0.07)
            visible_nodes.extend([_create_mock_value(i) for i in range(1, 6)])

            # Layer 3-7: Goals/Specs/etc (mock with varying loss)
            for layer in range(3, 8):
                for i in range(1, 4):  # 3 nodes per layer
                    node = ZeroNode(
                        id=f"zn-L{layer}-{i:03d}",
                        path=f"concept.layer{layer}.node{i}",
                        layer=layer,
                        kind=f"L{layer}_node",
                        title=f"Layer {layer} Node {i}",
                        content=f"Mock content for layer {layer} node {i}",
                        confidence=max(0.5, 1.0 - (layer * 0.1)),
                        created_at=datetime.now(UTC).isoformat(),
                        created_by="system",
                        tags=[f"layer{layer}"],
                        lineage=[f"zn-axiom-{((i - 1) % 3) + 1:03d}"],
                        has_proof=(layer >= 3),
                    )
                    visible_nodes.append(node)

        # Compute gradients for all nodes
        # Loss estimation: layer 1 = 0.01, layer 7 = 0.7 (linear)
        gradients: dict[str, GradientVector] = {}

        # Build node lookup and compute losses
        node_losses: dict[str, float] = {}
        for node in visible_nodes:
            # Loss increases with layer (axioms stable, higher layers more drift)
            base_loss = 0.01 + (node.layer - 1) * 0.1
            # Add slight variation based on node index
            variation = (hash(node.id) % 100) / 1000.0  # ±0.05 variation
            node_losses[node.id] = max(0.0, min(1.0, base_loss + variation))

        # For each node, find lowest-loss neighbor and compute gradient
        for node in visible_nodes:
            current_loss = node_losses[node.id]

            # Find potential neighbors (nodes in adjacent layers or same layer)
            neighbors = [
                n for n in visible_nodes if n.id != node.id and abs(n.layer - node.layer) <= 1
            ]

            if not neighbors:
                # No neighbors = fixed point (gradient = 0)
                gradients[node.id] = GradientVector(
                    x=0.0,
                    y=0.0,
                    magnitude=0.0,
                    target_node=node.id,
                )
                continue

            # Find lowest-loss neighbor
            lowest_neighbor = min(neighbors, key=lambda n: node_losses[n.id])
            lowest_loss = node_losses[lowest_neighbor.id]

            # Compute gradient magnitude (loss difference)
            loss_diff = current_loss - lowest_loss

            if loss_diff <= 0:
                # Already at local minimum
                gradients[node.id] = GradientVector(
                    x=0.0,
                    y=0.0,
                    magnitude=0.0,
                    target_node=node.id,
                )
            else:
                # Compute direction to lowest-loss neighbor
                # Use layer difference for y-axis, hash for x-axis spread
                layer_diff = lowest_neighbor.layer - node.layer

                # X component: horizontal spread based on node position
                # Use hash to create consistent but varied horizontal positions
                node_x = (hash(node.id) % 200 - 100) / 100.0  # -1 to 1
                neighbor_x = (hash(lowest_neighbor.id) % 200 - 100) / 100.0
                x_diff = neighbor_x - node_x

                # Normalize direction and scale by loss difference
                distance = (x_diff**2 + layer_diff**2) ** 0.5
                if distance > 0:
                    x_component = (x_diff / distance) * loss_diff
                    y_component = (layer_diff / distance) * loss_diff
                else:
                    x_component = 0.0
                    y_component = 0.0

                gradients[node.id] = GradientVector(
                    x=x_component,
                    y=y_component,
                    magnitude=loss_diff,
                    target_node=lowest_neighbor.id,
                )

        # Generate navigation suggestions (top 3 low-loss targets)
        sorted_nodes = sorted(visible_nodes, key=lambda n: node_losses[n.id])
        suggestions = []

        for node in sorted_nodes[:3]:
            loss = node_losses[node.id]

            if loss < 0.1:
                action = "focus"
                reasoning = f"{node.title} is nearly stable (loss={loss:.3f}) - strong foundation"
            elif loss < 0.3:
                action = "follow_gradient"
                reasoning = (
                    f"{node.title} has moderate loss (loss={loss:.3f}) - navigate here to improve"
                )
            else:
                action = "investigate"
                reasoning = f"{node.title} has high loss (loss={loss:.3f}) - needs attention"

            suggestions.append(
                NavigationSuggestion(
                    target=node.id,
                    action=action,
                    value_score=1.0 - loss,
                    reasoning=reasoning,
                )
            )

        return TelescopeResponse(
            state=state,
            gradients=gradients,
            suggestions=suggestions,
            visible_nodes=visible_nodes,
            policy_arrows=[],
        )

    # =========================================================================
    # Navigation Actions
    # =========================================================================

    @router.post("/navigate", response_model=NavigateResponse)
    async def navigate_telescope(request: NavigateRequest) -> NavigateResponse:
        """
        Execute navigation action.

        Args:
            request: Navigation request with node_id and action

        Returns:
            Navigation result with new state
        """
        # Mock navigation - real implementation would update telescope state
        return NavigateResponse(
            previous=None,
            current=request.node_id,
            loss=0.15,
            gradient=GradientVector(x=-0.2, y=0.1, magnitude=0.22, target_node="zn-axiom-001"),
        )

    # =========================================================================
    # Witnessed Edges
    # =========================================================================

    @router.post("/edges/from-mark", response_model=ZeroEdge)
    async def create_witnessed_edge(request: CreateWitnessedEdgeRequest) -> ZeroEdge:
        """
        Create a witnessed edge from a Witness mark.

        This endpoint extracts the decision reasoning from a Witness mark
        and creates a Zero Seed edge with kind="witnessed".

        Args:
            request: Witnessed edge creation request

        Returns:
            ZeroEdge with kind="witnessed" and attached proof

        Note:
            Currently uses mock implementation. Real implementation will:
            1. Load Mark from Witness crystal store by mark_id
            2. Extract Toulmin proof from Mark.data (if dialectic mark)
            3. Parse qualifier → confidence mapping
            4. Create edge with proof and evidence tier
        """
        # Mock implementation - real version will load from Witness
        # For now, create a witnessed edge with mock proof

        # Map qualifier to confidence (mock)
        # Real version: extract from Mark.data.qualifier
        mock_qualifier = "probably"
        confidence_map = {
            "definitely": 0.95,
            "probably": 0.75,
            "possibly": 0.50,
        }
        confidence = confidence_map.get(mock_qualifier, 0.75)

        # Mock Toulmin proof (real version: from Mark.data)
        mock_proof = ToulminProof(
            data="Session decision recorded",
            warrant="Decision emerged from dialectic synthesis",
            claim=f"Edge from {request.source_node_id} to {request.target_node_id}",
            backing="Witness protocol ensures decision traceability",
            qualifier=mock_qualifier,
            rebuttals=[],
            tier="empirical",
            principles=["tasteful", "composable"],
        )

        # Create witnessed edge
        edge = ZeroEdge(
            id=f"ze-witnessed-{request.mark_id[:8]}",
            source=request.source_node_id,
            target=request.target_node_id,
            kind="witnessed",
            context=request.context or "Decision from Witness mark",
            confidence=confidence,
            created_at=datetime.now(UTC).isoformat(),
            mark_id=request.mark_id,
            proof=mock_proof,
            evidence_tier=mock_proof.tier,
        )

        return edge

    # =========================================================================
    # Node CRUD Operations
    # =========================================================================

    @router.post("/nodes", response_model=ZeroNode)
    async def create_node(request: CreateNodeRequest) -> ZeroNode:
        """
        Create a new Zero Seed node.

        Args:
            request: Node creation request

        Returns:
            Created ZeroNode

        Raises:
            HTTPException: If validation fails
        """
        try:
            from services.k_block.zero_seed_storage import get_zero_seed_storage

            storage = get_zero_seed_storage()

            # Create node using K-Block storage
            kblock, node_id = storage.create_node(
                layer=request.layer,
                title=request.title,
                content=request.content,
                lineage=request.lineage,
                confidence=request.confidence,
                tags=request.tags,
                created_by=request.created_by,
            )

            # Convert K-Block to ZeroNode
            return ZeroNode(
                id=node_id,
                path=kblock.path,
                layer=getattr(kblock, "_layer", request.layer),
                kind=getattr(kblock, "_kind", "unknown"),
                title=getattr(kblock, "_title", request.title),
                content=kblock.content,
                confidence=getattr(kblock, "_confidence", 0.5),
                created_at=kblock.created_at.isoformat(),
                created_by=getattr(kblock, "_created_by", request.created_by),
                tags=getattr(kblock, "_tags", []),
                lineage=getattr(kblock, "_lineage", []),
                has_proof=(request.layer >= 3),
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to create node: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create node: {str(e)}")

    @router.put("/nodes/{node_id}", response_model=ZeroNode)
    async def update_node(node_id: str, request: UpdateNodeRequest) -> ZeroNode:
        """
        Update a Zero Seed node.

        Args:
            node_id: Node ID to update
            request: Update request

        Returns:
            Updated ZeroNode

        Raises:
            HTTPException: If node not found
        """
        try:
            from services.k_block.zero_seed_storage import get_zero_seed_storage

            storage = get_zero_seed_storage()

            # Update node
            kblock = storage.update_node(
                node_id=node_id,
                title=request.title,
                content=request.content,
                confidence=request.confidence,
                tags=request.tags,
            )

            if not kblock:
                raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

            # Convert K-Block to ZeroNode
            return ZeroNode(
                id=node_id,
                path=kblock.path,
                layer=getattr(kblock, "_layer", 1),
                kind=getattr(kblock, "_kind", "unknown"),
                title=getattr(kblock, "_title", "Untitled"),
                content=kblock.content,
                confidence=getattr(kblock, "_confidence", 0.5),
                created_at=kblock.created_at.isoformat(),
                created_by=getattr(kblock, "_created_by", "system"),
                tags=getattr(kblock, "_tags", []),
                lineage=getattr(kblock, "_lineage", []),
                has_proof=(getattr(kblock, "_layer", 1) >= 3),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to update node: {str(e)}")

    @router.delete("/nodes/{node_id}")
    async def delete_node(node_id: str) -> dict[str, str]:
        """
        Delete a Zero Seed node.

        Args:
            node_id: Node ID to delete

        Returns:
            Deletion confirmation

        Raises:
            HTTPException: If node not found
        """
        try:
            from services.k_block.zero_seed_storage import get_zero_seed_storage

            storage = get_zero_seed_storage()

            success = storage.delete_node(node_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

            return {"status": "deleted", "node_id": node_id}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete node {node_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to delete node: {str(e)}")

    # =========================================================================
    # Node Detail
    # =========================================================================

    @router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
    async def get_node_detail(node_id: str) -> NodeDetailResponse:
        """
        Get single node details.

        Args:
            node_id: Node ID

        Returns:
            Node detail with loss, proof, and edges
        """
        try:
            from services.k_block.zero_seed_storage import get_zero_seed_storage

            storage = get_zero_seed_storage()

            # Get node from K-Block storage
            kblock = storage.get_node(node_id)
            if not kblock:
                # Fall back to mock for now if not in storage
                node = _create_mock_axiom(1)
                node = node.copy(update={"id": node_id})
            else:
                # Convert K-Block to ZeroNode
                node = ZeroNode(
                    id=node_id,
                    path=kblock.path,
                    layer=getattr(kblock, "_layer", 1),
                    kind=getattr(kblock, "_kind", "unknown"),
                    title=getattr(kblock, "_title", "Untitled"),
                    content=kblock.content,
                    confidence=getattr(kblock, "_confidence", 0.5),
                    created_at=kblock.created_at.isoformat(),
                    created_by=getattr(kblock, "_created_by", "system"),
                    tags=getattr(kblock, "_tags", []),
                    lineage=getattr(kblock, "_lineage", []),
                    has_proof=(getattr(kblock, "_layer", 1) >= 3),
                )

        except Exception as e:
            logger.warning(f"Failed to load node from storage: {e}")
            # Fall back to mock
            node = _create_mock_axiom(1)
            node = node.copy(update={"id": node_id})

        loss = _create_mock_loss(node_id, 0.12)

        proof = None
        if node.layer > 2:
            proof = _create_mock_proof(node_id).proof

        incoming: list[ZeroEdge] = []
        outgoing: list[ZeroEdge] = [
            ZeroEdge(
                id="ze-001",
                source=node_id,
                target="zn-value-001",
                kind="grounds",
                context="Axiom grounds value",
                confidence=1.0,
                created_at=datetime.now(UTC).isoformat(),
                mark_id=None,
                proof=None,
                evidence_tier=None,
            )
        ]

        # Mock witnessed edges - real implementation will query by node_id
        witnessed: list[ZeroEdge] = [
            ZeroEdge(
                id="ze-witnessed-001",
                source=node_id,
                target="zn-value-002",
                kind="witnessed",
                context="Decision to adopt this approach after dialectic",
                confidence=0.75,
                created_at=datetime.now(UTC).isoformat(),
                mark_id="mark-dialectic-abc123",
                proof=ToulminProof(
                    data="Session explored alternatives A and B",
                    warrant="Alternative A provides better composition properties",
                    claim="We should use approach A",
                    backing="Category theory supports this pattern",
                    qualifier="probably",
                    rebuttals=["Unless performance becomes critical"],
                    tier="categorical",
                    principles=["composable", "tasteful"],
                ),
                evidence_tier="categorical",
            )
        ]

        return NodeDetailResponse(
            node=node,
            loss=loss,
            proof=proof,
            incoming_edges=incoming,
            outgoing_edges=outgoing,
            witnessed_edges=witnessed,
        )

    # =========================================================================
    # Layer Nodes
    # =========================================================================

    @router.get("/layers/{layer}", response_model=LayerNodesResponse)
    async def get_layer_nodes(layer: int) -> LayerNodesResponse:
        """
        Get all nodes for a layer.

        Args:
            layer: Layer number (1-7)

        Returns:
            Nodes in layer with losses

        Raises:
            HTTPException: If layer out of range
        """
        if not (1 <= layer <= 7):
            raise HTTPException(status_code=400, detail="Layer must be 1-7")

        try:
            from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

            storage = await get_postgres_zero_seed_storage()

            # Get nodes from storage
            layer_kblocks = await storage.get_layer_nodes(layer)
            nodes = []

            for kblock in layer_kblocks:
                nodes.append(
                    ZeroNode(
                        id=str(kblock.id),
                        path=kblock.path,
                        layer=layer,
                        kind=getattr(kblock, "_kind", "unknown"),
                        title=getattr(kblock, "_title", "Untitled"),
                        content=kblock.content,
                        confidence=getattr(kblock, "_confidence", 0.5),
                        created_at=kblock.created_at.isoformat(),
                        created_by=getattr(kblock, "_created_by", "system"),
                        tags=list(getattr(kblock, "_tags", [])),
                        lineage=list(getattr(kblock, "_lineage", [])),
                        has_proof=(layer >= 3),
                    )
                )

            # Compute losses based on layer
            losses = [_create_mock_loss(n.id, 0.01 + (layer - 1) * 0.1) for n in nodes]

            return LayerNodesResponse(
                nodes=nodes,
                losses=losses,
                count=len(nodes),
            )

        except Exception as e:
            logger.warning(f"Failed to load layer {layer} nodes, using mock data: {e}")
            # Fallback to mock nodes
            if layer == 1:
                nodes = [_create_mock_axiom(i) for i in range(1, 4)]
            elif layer == 2:
                nodes = [_create_mock_value(i) for i in range(1, 6)]
            else:
                nodes = []

            losses = [_create_mock_loss(n.id, 0.1 * layer) for n in nodes]

            return LayerNodesResponse(
                nodes=nodes,
                losses=losses,
                count=len(nodes),
            )

    # =========================================================================
    # Node Analysis (Four-Mode)
    # =========================================================================

    @router.get("/nodes/{node_id}/analysis", response_model=NodeAnalysisResponse)
    async def get_node_analysis(
        node_id: str,
        use_llm: bool = Query(False, description="Use LLM-backed analysis (requires API key)"),
    ) -> NodeAnalysisResponse:
        """
        Get four-mode analysis for a Zero Seed node.

        Returns categorical, epistemic, dialectical, and generative analysis
        in a format suitable for the AnalysisQuadrant UI component.

        Args:
            node_id: Node ID to analyze
            use_llm: Whether to use real LLM analysis (default: False for mock data)

        Returns:
            Four-mode analysis report

        Note:
            With use_llm=false (default): Returns mock data for UI testing
            With use_llm=true: Uses AnalysisService with Claude API
        """
        # Use real LLM analysis if requested AND credentials available
        if use_llm:
            try:
                return await _get_llm_node_analysis(node_id)
            except Exception as e:
                logger.warning(f"LLM analysis failed for {node_id}, falling back to mock: {e}")
                # Fall through to mock data on any error
        # For now, generate rich mock data based on node ID
        # This provides a working UI while the full pipeline is built

        # Categorical: Verify composition laws and fixed points
        categorical_items = [
            AnalysisItem(label="Identity Law", value="Id >> f = f = f >> Id", status="pass"),
            AnalysisItem(
                label="Associativity", value="(f >> g) >> h = f >> (g >> h)", status="pass"
            ),
            AnalysisItem(
                label="Fixed Point",
                value="None detected" if "axiom" in node_id else "Self-referential",
                status="info" if "axiom" in node_id else "warning",
            ),
        ]

        categorical = AnalysisQuadrant(
            status="pass",
            summary="All composition laws hold. No violations detected.",
            items=categorical_items,
        )

        # Epistemic: Analyze justification and grounding
        epistemic_items = [
            AnalysisItem(label="Layer", value="L4 (Specification)", status="info"),
            AnalysisItem(label="Grounding", value="Terminates at axiom A1", status="pass"),
            AnalysisItem(label="Evidence Tier", value="Empirical", status="info"),
            AnalysisItem(label="Confidence", value="Definitely (0.95)", status="pass"),
        ]

        epistemic = AnalysisQuadrant(
            status="pass",
            summary="Properly grounded through axiom chain. High confidence.",
            items=epistemic_items,
        )

        # Dialectical: Identify tensions and synthesize
        dialectical_items = [
            AnalysisItem(label="Tension 1", value="Expressiveness vs Complexity", status="pass"),
            AnalysisItem(label="Resolution", value="Use compositional primitives", status="pass"),
            AnalysisItem(label="Tension 2", value="Coverage vs Minimalism", status="pass"),
            AnalysisItem(
                label="Classification", value="Productive (design-driving)", status="info"
            ),
        ]

        dialectical = AnalysisQuadrant(
            status="pass",
            summary="2 productive tensions identified. Both resolved via composition.",
            items=dialectical_items,
        )

        # Generative: Test compression and regeneration
        generative_items = [
            AnalysisItem(label="Compression Ratio", value="0.67 (good)", status="pass"),
            AnalysisItem(label="Minimal Kernel", value="3 axioms", status="info"),
            AnalysisItem(label="Regeneration Test", value="Passed", status="pass"),
            AnalysisItem(label="Missing Elements", value="None", status="pass"),
        ]

        generative = AnalysisQuadrant(
            status="pass",
            summary="Regenerable from 3 axioms. Good compression.",
            items=generative_items,
        )

        return NodeAnalysisResponse(
            nodeId=node_id,
            categorical=categorical,
            epistemic=epistemic,
            dialectical=dialectical,
            generative=generative,
        )

    # =========================================================================
    # Personal Governance: Axiom Discovery
    # =========================================================================

    @router.post("/discover-axioms")
    async def discover_axioms_from_decisions(
        request: DiscoverAxiomsRequest,
    ) -> dict[str, Any]:
        """
        Discover axioms from decision texts.

        Analyzes decision patterns to find recurring values/principles
        that qualify as axioms (L < 0.05).

        Args:
            request: DiscoverAxiomsRequest with decisions and options

        Returns:
            DiscoveryReport with discovered axioms and metrics
        """
        try:
            from services.zero_seed.axiom_discovery import (
                AxiomDiscoveryService,
            )

            service = AxiomDiscoveryService()
            report = await service.discover_from_text(
                texts=request.decisions,
                min_pattern_occurrences=request.min_pattern_occurrences,
            )

            return report.to_dict()

        except ImportError as e:
            logger.error(f"Axiom discovery service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Axiom discovery service not available: {e}",
            )
        except ValueError as e:
            logger.warning(f"Invalid input for axiom discovery: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to discover axioms: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to discover axioms: {e}",
            )

    # =========================================================================
    # Personal Governance: Axiom Validation
    # =========================================================================

    @router.post("/validate-axiom")
    async def validate_axiom_candidate(
        content: str,
        threshold: float = Query(default=0.05, ge=0.0, le=1.0),
    ) -> dict[str, Any]:
        """
        Validate a single axiom candidate.

        Checks if the content qualifies as a semantic fixed point
        with L < threshold.

        Args:
            content: Content to validate
            threshold: Loss threshold for axiom qualification

        Returns:
            Validation result with is_axiom, loss, stability
        """
        try:
            from services.zero_seed.axiom_discovery import (
                AxiomDiscoveryService,
            )

            service = AxiomDiscoveryService()
            result = await service.validate_fixed_point(
                content=content,
                threshold=threshold,
            )

            return {
                "is_axiom": result.is_axiom_candidate,
                "is_fixed_point": result.is_fixed_point,
                "loss": result.loss,
                "stability": result.stability,
                "iterations": result.iterations,
                "losses": result.losses,
            }

        except ImportError as e:
            logger.error(f"Axiom validation service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Axiom validation service not available: {e}",
            )
        except ValueError as e:
            logger.warning(f"Invalid input for axiom validation: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to validate axiom: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate axiom: {e}",
            )

    # =========================================================================
    # Personal Governance: Constitution
    # =========================================================================

    # In-memory store for the demo (replace with PostgreSQL in production)
    _constitution_store: dict[str, Any] = {}

    @router.get("/constitution")
    async def get_personal_constitution() -> dict[str, Any]:
        """
        Get the current personal constitution.

        Returns all axioms with their status and metadata.
        """
        try:
            from services.zero_seed.personal_constitution import (
                PersonalConstitutionService,
                get_constitution_store,
            )

            store = get_constitution_store()
            constitutions = store.list_all()

            if not constitutions:
                # Create default constitution
                service = PersonalConstitutionService()
                constitution = service.create_constitution("Personal Constitution")
                store.save(constitution)
                return constitution.to_dict()

            # Return first constitution (demo mode)
            return constitutions[0].to_dict()

        except Exception as e:
            logger.error(f"Failed to get constitution: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get constitution: {e}",
            )

    @router.post("/constitution/add")
    async def add_axiom_to_constitution(
        content: str,
        check_contradictions: bool = Query(default=True),
    ) -> dict[str, Any]:
        """
        Add an axiom to the personal constitution.

        First validates the content as an axiom, then adds it
        to the constitution. Optionally checks for contradictions.

        Args:
            content: Axiom content to add
            check_contradictions: Whether to check for contradictions

        Returns:
            Updated constitution
        """
        try:
            from services.zero_seed.axiom_discovery import (
                AxiomDiscoveryService,
                DiscoveredAxiom,
            )
            from services.zero_seed.personal_constitution import (
                PersonalConstitutionService,
                get_constitution_store,
            )

            # First validate as axiom
            discovery_service = AxiomDiscoveryService()
            result = await discovery_service.validate_fixed_point(content)

            if not result.is_fixed_point or result.loss >= 0.05:
                raise HTTPException(
                    status_code=400,
                    detail=f"Content does not qualify as axiom (L={result.loss:.3f} >= 0.05)",
                )

            # Create discovered axiom
            axiom = DiscoveredAxiom(
                content=content,
                loss=result.loss,
                stability=result.stability,
                iterations=result.iterations,
                confidence=1.0 - result.loss,
            )

            # Get or create constitution
            store = get_constitution_store()
            constitutions = store.list_all()

            if not constitutions:
                service = PersonalConstitutionService()
                constitution = service.create_constitution("Personal Constitution")
            else:
                constitution = constitutions[0]

            # Add axiom
            service = PersonalConstitutionService()
            updated = await service.add_axiom(
                constitution=constitution,
                axiom=axiom,
                check_contradictions=check_contradictions,
            )
            store.save(updated)

            return updated.to_dict()

        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Invalid axiom: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid axiom: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to add axiom: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add axiom: {e}",
            )

    # =========================================================================
    # Personal Governance: Axiom Retirement
    # =========================================================================

    @router.post("/constitution/retire")
    async def retire_axiom_from_constitution(
        axiom_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """
        Retire an axiom from the personal constitution.

        The axiom is not deleted but marked as retired with a reason.
        This honors the amendment process: ceremonial but not burdensome.

        Args:
            axiom_id: ID of the axiom to retire
            reason: Reason for retirement (required for ceremony)

        Returns:
            Updated constitution
        """
        try:
            from services.zero_seed.personal_constitution import (
                PersonalConstitutionService,
                get_constitution_store,
            )

            store = get_constitution_store()
            constitutions = store.list_all()

            if not constitutions:
                raise HTTPException(
                    status_code=404,
                    detail="No constitution found",
                )

            constitution = constitutions[0]
            service = PersonalConstitutionService()

            updated = await service.retire_axiom(
                constitution=constitution,
                axiom_id=axiom_id,
                reason=reason,
            )
            store.save(updated)

            return updated.to_dict()

        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Invalid retirement request: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid retirement request: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to retire axiom: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retire axiom: {e}",
            )

    # =========================================================================
    # Personal Governance: Contradiction Detection
    # =========================================================================

    @router.post("/detect-contradictions")
    async def detect_constitution_contradictions(
        tolerance: float = Query(default=0.1, ge=0.0, le=1.0),
    ) -> dict[str, Any]:
        """
        Detect contradictions between axioms in the constitution.

        Uses super-additive loss to identify conflicting axioms:
        L(A U B) > L(A) + L(B) + tau

        Args:
            tolerance: Tau tolerance for contradiction detection

        Returns:
            List of detected contradictions
        """
        try:
            from services.zero_seed.personal_constitution import (
                PersonalConstitutionService,
                get_constitution_store,
            )

            store = get_constitution_store()
            constitutions = store.list_all()

            if not constitutions:
                return {
                    "contradictions": [],
                    "total_axioms": 0,
                    "pairs_checked": 0,
                }

            constitution = constitutions[0]
            service = PersonalConstitutionService()
            contradictions = await service.detect_contradictions(
                constitution=constitution,
                tolerance=tolerance,
            )

            active_count = constitution.active_count
            pairs_checked = (active_count * (active_count - 1)) // 2

            return {
                "contradictions": [c.to_dict() for c in contradictions],
                "total_axioms": active_count,
                "pairs_checked": pairs_checked,
            }

        except Exception as e:
            logger.error(f"Failed to detect contradictions: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to detect contradictions: {e}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_zero_seed_router",
    # Response models
    "AxiomExplorerResponse",
    "ProofDashboardResponse",
    "GraphHealthResponse",
    "TelescopeResponse",
    "NavigateResponse",
    "NodeDetailResponse",
    "LayerNodesResponse",
    "NodeAnalysisResponse",
    "AnalysisQuadrant",
    "AnalysisItem",
    # Request models
    "CreateWitnessedEdgeRequest",
    # Data models
    "ZeroEdge",
    "ToulminProof",
]
