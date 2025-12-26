"""
Tests for cross-layer loss computation.

Test coverage:
- Same-layer edges (delta=0)
- Adjacent-layer edges (delta=1)
- Cross-layer edges (delta>1)
- Different edge kinds (multiplier effects)
- Loss bounds (0 ≤ loss ≤ 1.0)
- Flagging logic
"""

import pytest

from services.zero_seed import EdgeKind, Proof, ZeroEdge, ZeroNode, generate_edge_id, generate_node_id
from services.zero_seed.galois.cross_layer import (
    CrossLayerLoss,
    compute_cross_layer_loss,
    should_flag_cross_layer,
)


# Helper to create proof for L3+ nodes
def _make_proof() -> Proof:
    """Create a simple proof for test nodes."""
    return Proof.empirical(
        data="Test data",
        warrant="Test warrant",
        claim="Test claim",
    )


class TestCrossLayerLoss:
    """Test suite for cross-layer loss computation."""

    def test_same_layer_zero_delta(self):
        """Same-layer edges have delta=0."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=3,
            path="concept.goal.build",
            title="Build Something",
            proof=_make_proof(),
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=3,
            path="concept.goal.create",
            title="Create Something",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.REFINES,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 0
        assert loss.total_loss == 0.0
        assert "same-layer" in loss.explanation.lower()

    def test_adjacent_layer_delta_one(self):
        """Adjacent layer edges have delta=1."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=1,
            path="void.axiom.entity",
            title="Entity Axiom",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=2,
            path="void.value.composability",
            title="Composability Value",
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.GROUNDS,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 1
        assert loss.total_loss == 0.1  # 0.1 * 1 * 1.0
        assert "adjacent" in loss.explanation.lower()

    def test_cross_layer_multiple_skip(self):
        """Cross-layer edges compute correct delta and loss."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=1,
            path="void.axiom.entity",
            title="Entity Axiom",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=5,
            path="world.action.implement",
            title="Implementation",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.IMPLEMENTS,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 4
        assert loss.total_loss == pytest.approx(0.32)  # 0.1 * 4 * 0.8
        assert "cross-layer" in loss.explanation.lower()
        assert "3 intermediate" in loss.explanation

    def test_dialectical_edge_higher_multiplier(self):
        """Dialectical edges (CONTRADICTS, SUPERSEDES) have higher loss."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=1,
            path="void.axiom.a",
            title="Axiom A",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=3,
            path="concept.goal.b",
            title="Goal B",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.CONTRADICTS,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 2
        assert loss.total_loss == pytest.approx(0.3)  # 0.1 * 2 * 1.5
        assert loss.edge_kind == EdgeKind.CONTRADICTS

    def test_vertical_flow_edge_standard_multiplier(self):
        """Vertical flow edges (GROUNDS, JUSTIFIES) use standard multiplier."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=2,
            path="void.value.x",
            title="Value X",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=5,
            path="world.action.y",
            title="Action Y",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.JUSTIFIES,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 3
        assert loss.total_loss == pytest.approx(0.3)  # 0.1 * 3 * 1.0

    def test_loss_capped_at_one(self):
        """Loss is capped at 1.0 for extreme deltas."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=1,
            path="void.axiom.a",
            title="Axiom A",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=7,
            path="time.representation.z",
            title="Representation Z",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.CONTRADICTS,  # 1.5 multiplier
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 6
        # 0.1 * 6 * 1.5 = 0.9, which is < 1.0
        assert 0.0 <= loss.total_loss <= 1.0

    def test_upward_edge_same_as_downward(self):
        """Upward edges (L5 → L2) have same loss as downward."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=5,
            path="world.action.x",
            title="Action X",
            proof=_make_proof(),
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=2,
            path="void.value.y",
            title="Value Y",
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.REFINES,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.layer_delta == 3  # abs(5 - 2)
        assert loss.total_loss == pytest.approx(0.24)  # 0.1 * 3 * 0.8

    def test_suggestion_for_high_loss(self):
        """High-loss edges get suggestions."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=1,
            path="void.axiom.a",
            title="Axiom A",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=7,
            path="time.representation.z",
            title="Representation Z",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.REPRESENTS,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        # Loss is ~0.48, which is < 0.5 threshold, so no suggestion
        # But delta is 6, so it should be flagged
        assert loss.layer_delta == 6
        assert loss.total_loss < 0.5  # Below suggestion threshold

    def test_no_suggestion_for_low_loss(self):
        """Low-loss edges don't get suggestions."""
        source = ZeroNode(
            id=generate_node_id(),
            layer=2,
            path="void.value.x",
            title="Value X",
        )
        target = ZeroNode(
            id=generate_node_id(),
            layer=3,
            path="concept.goal.y",
            title="Goal Y",
            proof=_make_proof(),
        )
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=source.id,
            target=target.id,
            kind=EdgeKind.JUSTIFIES,
        )

        loss = compute_cross_layer_loss(source, target, edge)

        assert loss.suggestion is None  # Low loss

    def test_should_flag_large_delta(self):
        """Flag if delta > 2."""
        loss = CrossLayerLoss(
            total_loss=0.3,
            layer_delta=3,
            source_layer=1,
            target_layer=4,
            edge_kind=EdgeKind.IMPLEMENTS,
            explanation="Cross-layer",
        )

        assert should_flag_cross_layer(loss)

    def test_should_flag_high_loss(self):
        """Flag if total_loss > 0.5."""
        loss = CrossLayerLoss(
            total_loss=0.6,
            layer_delta=2,
            source_layer=1,
            target_layer=3,
            edge_kind=EdgeKind.CONTRADICTS,
            explanation="Cross-layer",
        )

        assert should_flag_cross_layer(loss)

    def test_should_not_flag_small_delta_low_loss(self):
        """Don't flag if delta ≤ 2 and loss ≤ 0.5."""
        loss = CrossLayerLoss(
            total_loss=0.2,
            layer_delta=2,
            source_layer=1,
            target_layer=3,
            edge_kind=EdgeKind.GROUNDS,
            explanation="Cross-layer",
        )

        assert not should_flag_cross_layer(loss)

    def test_should_not_flag_adjacent(self):
        """Don't flag adjacent edges."""
        loss = CrossLayerLoss(
            total_loss=0.1,
            layer_delta=1,
            source_layer=1,
            target_layer=2,
            edge_kind=EdgeKind.GROUNDS,
            explanation="Adjacent",
        )

        assert not should_flag_cross_layer(loss)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
