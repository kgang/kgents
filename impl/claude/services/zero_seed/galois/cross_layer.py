"""
Cross-Layer Loss Computation: Measure coherence of cross-layer edges.

"Cross-layer edges are allowed. We measure their cost."

This module computes Galois loss for edge transitions that skip layers,
enabling informed decisions about heterarchical connections.

Key Insight:
    Cross-layer edges represent semantic jumps. The Galois loss quantifies
    how much structure is lost in the jump.

    Example:
        L1 (Axiom) → L5 (Implementation)
        Loss = how much specification/design was skipped

From spec/protocols/zero-seed.md:
    "Layer = minimum restructuring depth to reach fixed point."

    Cross-layer edge loss = accumulated loss from intermediate layers.

Usage:
    >>> from services.zero_seed.galois.cross_layer import compute_cross_layer_loss
    >>> loss = await compute_cross_layer_loss(l1_node, l5_node, edge)
    >>> if loss > 0.5:
    >>>     print("High loss cross-layer edge - suggest adding intermediate steps")
"""

from __future__ import annotations

from dataclasses import dataclass

from services.zero_seed import EdgeKind, ZeroEdge, ZeroNode


@dataclass(frozen=True)
class CrossLayerLoss:
    """
    Loss analysis for cross-layer edge.

    Fields:
        total_loss: Total Galois loss of the transition
        layer_delta: Number of layers skipped
        source_layer: Starting layer
        target_layer: Ending layer
        edge_kind: Type of edge
        explanation: Human-readable explanation
        suggestion: Optional suggestion for improvement
    """

    total_loss: float
    layer_delta: int
    source_layer: int
    target_layer: int
    edge_kind: EdgeKind
    explanation: str
    suggestion: str | None = None


def compute_cross_layer_loss(
    source: ZeroNode,
    target: ZeroNode,
    edge: ZeroEdge,
) -> CrossLayerLoss:
    """
    Compute Galois loss for a cross-layer edge.

    The loss represents the amount of structure "skipped" by jumping layers.

    Strategy:
        For now, use a simple heuristic based on layer delta.
        Future: Use actual Galois loss computation with LLM.

    Heuristic:
        loss = 0.1 * |source.layer - target.layer| * base_multiplier

        base_multiplier depends on edge kind:
        - CONTRADICTS, SUPERSEDES: 1.5 (dialectical edges are costly)
        - GROUNDS, JUSTIFIES: 1.0 (expected vertical flow)
        - Other: 0.8 (lower cost for exploratory edges)

    Args:
        source: Source node
        target: Target node
        edge: The edge connecting them

    Returns:
        CrossLayerLoss with analysis

    Example:
        >>> from services.zero_seed import ZeroNode, ZeroEdge, EdgeKind, generate_node_id
        >>> source = ZeroNode(
        ...     id=generate_node_id(),
        ...     layer=1,
        ...     path="void.axiom.entity",
        ...     title="Entity Axiom",
        ... )
        >>> target = ZeroNode(
        ...     id=generate_node_id(),
        ...     layer=5,
        ...     path="world.action.implement",
        ...     title="Implementation",
        ... )
        >>> edge = ZeroEdge(source=source.id, target=target.id, kind=EdgeKind.IMPLEMENTS)
        >>> loss = compute_cross_layer_loss(source, target, edge)
        >>> assert loss.layer_delta == 4
        >>> assert loss.total_loss > 0
    """
    layer_delta = abs(source.layer - target.layer)

    # Determine base multiplier based on edge kind
    if edge.kind in {EdgeKind.CONTRADICTS, EdgeKind.SUPERSEDES}:
        base_multiplier = 1.5  # Dialectical edges are costly
    elif edge.kind in {EdgeKind.GROUNDS, EdgeKind.JUSTIFIES}:
        base_multiplier = 1.0  # Expected vertical flow
    else:
        base_multiplier = 0.8  # Lower cost for other edges

    # Simple loss formula: 0.1 per layer * multiplier
    # This gives losses in range [0, ~1.0] for typical cases
    total_loss = min(1.0, 0.1 * layer_delta * base_multiplier)

    # Generate explanation
    if layer_delta == 0:
        explanation = "Same-layer edge (no cross-layer jump)"
    elif layer_delta == 1:
        explanation = "Adjacent layer edge (expected flow)"
    else:
        explanation = (
            f"Cross-layer edge skipping {layer_delta - 1} intermediate layer(s)"
        )

    # Generate suggestion if high loss
    suggestion = None
    if total_loss > 0.5:
        suggestion = (
            f"This edge skips {layer_delta - 1} layer(s) with loss {total_loss:.2f}. "
            "Consider adding intermediate nodes to make the connection explicit."
        )

    return CrossLayerLoss(
        total_loss=total_loss,
        layer_delta=layer_delta,
        source_layer=source.layer,
        target_layer=target.layer,
        edge_kind=edge.kind,
        explanation=explanation,
        suggestion=suggestion,
    )


async def compute_cross_layer_loss_async(
    source: ZeroNode,
    target: ZeroNode,
    edge: ZeroEdge,
    llm_client: object | None = None,
    use_llm: bool = True,
) -> CrossLayerLoss:
    """
    Async version of compute_cross_layer_loss with LLM support.

    Uses LLM-based Galois loss computation for semantic analysis of
    cross-layer transitions. Falls back to heuristic if LLM unavailable.

    Args:
        source: Source node
        target: Target node
        edge: The edge connecting them
        llm_client: Optional LLM client for semantic analysis
        use_llm: Whether to attempt LLM-based computation (default: True)

    Returns:
        CrossLayerLoss with analysis
    """
    layer_delta = abs(source.layer - target.layer)

    # If use_llm is False or no LLM available, use heuristic
    if not use_llm or llm_client is None:
        return compute_cross_layer_loss(source, target, edge)

    # Try LLM-based semantic loss computation
    try:
        from .galois_loss import compute_galois_loss_async

        # Construct transition description
        transition = f"""
Cross-layer edge transition:

Source Node (Layer {source.layer}):
Path: {source.path}
Title: {source.title}
Content: {getattr(source, 'content', '')[:300]}

Edge Type: {edge.kind.value}

Target Node (Layer {target.layer}):
Path: {target.path}
Title: {target.title}
Content: {getattr(target, 'content', '')[:300]}

This edge skips {layer_delta - 1 if layer_delta > 1 else 0} intermediate layer(s).
"""

        # Compute Galois loss via LLM
        result = await compute_galois_loss_async(
            transition,
            llm_client=llm_client,
            use_cache=True,
        )

        total_loss = result.loss

        # Generate explanation
        if layer_delta == 0:
            explanation = "Same-layer edge (no cross-layer jump)"
        elif layer_delta == 1:
            explanation = f"Adjacent layer edge (Galois loss: {total_loss:.3f})"
        else:
            explanation = (
                f"Cross-layer edge skipping {layer_delta - 1} intermediate layer(s) "
                f"(Galois loss: {total_loss:.3f}, method: {result.method})"
            )

        # Generate suggestion if high loss
        suggestion = None
        if total_loss > 0.5:
            suggestion = (
                f"This edge has high Galois loss ({total_loss:.2f}) indicating significant "
                f"semantic structure is skipped. Consider adding intermediate nodes to make "
                f"the connection more explicit."
            )

        return CrossLayerLoss(
            total_loss=total_loss,
            layer_delta=layer_delta,
            source_layer=source.layer,
            target_layer=target.layer,
            edge_kind=edge.kind,
            explanation=explanation,
            suggestion=suggestion,
        )

    except Exception as e:
        # Fall back to heuristic on error
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"LLM-based cross-layer loss failed, using heuristic: {e}")
        return compute_cross_layer_loss(source, target, edge)


def should_flag_cross_layer(loss: CrossLayerLoss) -> bool:
    """
    Determine if a cross-layer edge should be flagged for review.

    Rules:
    - Always flag if layer_delta > 2 (skip more than 1 layer)
    - Flag if total_loss > 0.5 (high cost)
    - Don't flag same-layer or adjacent edges

    Args:
        loss: CrossLayerLoss analysis

    Returns:
        True if should flag for review

    Example:
        >>> from services.zero_seed import EdgeKind
        >>> loss = CrossLayerLoss(
        ...     total_loss=0.6,
        ...     layer_delta=3,
        ...     source_layer=1,
        ...     target_layer=4,
        ...     edge_kind=EdgeKind.IMPLEMENTS,
        ...     explanation="Cross-layer",
        ... )
        >>> assert should_flag_cross_layer(loss)
    """
    return loss.layer_delta > 2 or loss.total_loss > 0.5
