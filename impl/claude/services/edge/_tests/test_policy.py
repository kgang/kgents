"""
Tests for HeterarchicalEdgePolicy.

Test coverage:
- STRICT edges (require justification)
- SUGGESTED edges (flag if missing justification)
- OPTIONAL edges (no enforcement)
- Cross-layer edges (allowed but flagged)
- Edge validation algorithm
"""

import pytest

from services.edge.policy import (
    EdgePolicyLevel,
    EdgeValidation,
    HeterarchicalEdgePolicy,
    validate_edge,
)
from services.zero_seed import EdgeKind, ZeroEdge, generate_edge_id, generate_node_id


class TestHeterarchicalEdgePolicy:
    """Test suite for edge validation policy."""

    def test_strict_edge_requires_justification(self):
        """STRICT edges must have justification."""
        policy = HeterarchicalEdgePolicy()

        # CONTRADICTS without justification
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.CONTRADICTS,
            context="",  # No justification
        )

        validation = policy.validate(edge, source_layer=1, target_layer=2)

        assert not validation.valid
        assert validation.flagged
        assert validation.level == EdgePolicyLevel.STRICT
        assert "require justification" in validation.reason.lower()

    def test_strict_edge_with_justification_passes(self):
        """STRICT edges with justification are valid."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.CONTRADICTS,
            context="These axioms contradict because A implies ¬B",
        )

        validation = policy.validate(edge, source_layer=1, target_layer=2)

        assert validation.valid
        assert not validation.flagged  # Same layer, has justification
        assert validation.level == EdgePolicyLevel.STRICT

    def test_suggested_edge_flags_missing_justification(self):
        """SUGGESTED edges flag if missing justification."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.GROUNDS,  # L1 → L2
            context="",
        )

        validation = policy.validate(edge, source_layer=1, target_layer=2)

        assert validation.valid  # Allowed
        assert validation.flagged  # But flagged
        assert validation.level == EdgePolicyLevel.SUGGESTED
        assert "should have justification" in validation.reason.lower()

    def test_suggested_edge_with_justification_passes(self):
        """SUGGESTED edges with justification don't flag."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.JUSTIFIES,  # L2 → L3
            context="This value justifies this goal because of X",
        )

        validation = policy.validate(edge, source_layer=2, target_layer=3)

        assert validation.valid
        assert not validation.flagged
        assert validation.level == EdgePolicyLevel.SUGGESTED

    def test_optional_edge_never_flags(self):
        """OPTIONAL edges never flag, regardless of justification."""
        policy = HeterarchicalEdgePolicy()

        # Without justification
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.IMPLEMENTS,
            context="",
        )

        validation = policy.validate(edge, source_layer=4, target_layer=5)

        assert validation.valid
        assert not validation.flagged
        assert validation.level == EdgePolicyLevel.OPTIONAL

    def test_cross_layer_edge_flagged(self):
        """Cross-layer edges are allowed but flagged."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.IMPLEMENTS,
            context="Direct axiom to implementation",
        )

        validation = policy.validate(edge, source_layer=1, target_layer=5)

        assert validation.valid  # Allowed
        assert validation.flagged  # But flagged
        assert "cross-layer" in validation.reason.lower()
        assert "L1" in validation.suggestion
        assert "L5" in validation.suggestion

    def test_adjacent_layer_not_flagged(self):
        """Adjacent layer edges (delta=1) are not flagged."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.GROUNDS,
            context="Axiom grounds value",
        )

        validation = policy.validate(edge, source_layer=1, target_layer=2)

        assert validation.valid
        assert not validation.flagged

    def test_same_layer_not_flagged(self):
        """Same-layer edges (delta=0) are not flagged."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.REFINES,
            context="",
        )

        validation = policy.validate(edge, source_layer=3, target_layer=3)

        assert validation.valid
        assert not validation.flagged

    def test_upward_cross_layer_allowed(self):
        """Upward cross-layer edges allowed (L5 → L2)."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.REFINES,
            context="Action inspired value revision",
        )

        validation = policy.validate(edge, source_layer=5, target_layer=2)

        assert validation.valid
        assert validation.flagged  # Cross-layer
        assert "cross-layer" in validation.reason.lower()

    def test_convenience_function(self):
        """Test validate_edge convenience function."""
        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.CONTRADICTS,
            context="",
        )

        validation = validate_edge(edge, source_layer=1, target_layer=2)

        assert not validation.valid  # STRICT without justification

    def test_supersedes_edge_strict(self):
        """SUPERSEDES edges are STRICT."""
        policy = HeterarchicalEdgePolicy()

        edge = ZeroEdge(
            id=generate_edge_id(),
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.SUPERSEDES,
            context="",
        )

        validation = policy.validate(edge, source_layer=3, target_layer=3)

        assert not validation.valid
        assert validation.level == EdgePolicyLevel.STRICT

    def test_all_inverse_edges_optional(self):
        """All inverse edges are OPTIONAL."""
        policy = HeterarchicalEdgePolicy()

        for kind in [
            EdgeKind.GROUNDED_BY,
            EdgeKind.JUSTIFIED_BY,
            EdgeKind.SPECIFIED_BY,
            EdgeKind.IMPLEMENTED_BY,
        ]:
            edge = ZeroEdge(
                id=generate_edge_id(),
                source=generate_node_id(),
                target=generate_node_id(),
                kind=kind,
                context="",
            )

            validation = policy.validate(edge, source_layer=2, target_layer=1)

            assert validation.valid
            assert validation.level == EdgePolicyLevel.OPTIONAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
