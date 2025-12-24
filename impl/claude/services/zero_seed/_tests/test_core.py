"""
Tests for Zero Seed Core Module.

Tests the two axioms and one meta-principle:
- A1 (Entity): Everything is a Node
- A2 (Morphism): Everything Composes
- M (Justification): Every node justifies its existence or admits it cannot

See: spec/protocols/zero-seed1/core.md
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from services.zero_seed import (
    # Types
    NodeId,
    EdgeId,
    generate_node_id,
    generate_edge_id,
    # Core classes
    ZeroNode,
    ZeroEdge,
    Proof,
    EvidenceTier,
    EdgeKind,
    # Errors
    ZeroSeedError,
    CompositionError,
    ProofRequiredError,
    ProofForbiddenError,
    LayerViolationError,
    # Utilities
    layer_to_context,
    context_to_layers,
    parse_agentese_path,
    get_layer_name,
    identity_edge,
    compose_edge_kinds,
    AXIOM_KINDS,
    VALUE_KINDS,
)


class TestProof:
    """Test Toulmin proof structure (from M)."""

    def test_categorical_proof(self) -> None:
        """Categorical proofs have 'definitely' qualifier."""
        proof = Proof.categorical(
            data="Tests pass",
            warrant="Passing tests indicate correctness",
            claim="Code is correct",
            principles=("composable",),
        )
        assert proof.tier == EvidenceTier.CATEGORICAL
        assert proof.qualifier == "definitely"
        assert proof.principles == ("composable",)

    def test_empirical_proof(self) -> None:
        """Empirical proofs have 'almost certainly' qualifier."""
        proof = Proof.empirical(
            data="3 hours invested",
            warrant="Investment indicates commitment",
            claim="Work was worthwhile",
            backing="Pattern X observed",
        )
        assert proof.tier == EvidenceTier.EMPIRICAL
        assert proof.qualifier == "almost certainly"
        assert proof.backing == "Pattern X observed"

    def test_aesthetic_proof(self) -> None:
        """Aesthetic proofs have 'arguably' qualifier."""
        proof = Proof.aesthetic(
            data="Code is elegant",
            warrant="Elegance indicates quality",
            claim="This is good code",
        )
        assert proof.tier == EvidenceTier.AESTHETIC
        assert proof.qualifier == "arguably"

    def test_somatic_proof(self) -> None:
        """Somatic proofs capture felt sense (Mirror Test)."""
        proof = Proof.somatic(
            claim="This feels right",
            feeling="intuitive alignment",
        )
        assert proof.tier == EvidenceTier.SOMATIC
        assert proof.qualifier == "personally"
        assert "joy-inducing" in proof.principles

    def test_proof_immutability(self) -> None:
        """Proofs are immutable (frozen=True)."""
        proof = Proof.categorical("data", "warrant", "claim")
        with pytest.raises(AttributeError):
            proof.data = "new data"  # type: ignore

    def test_strengthen_returns_new_proof(self) -> None:
        """strengthen() returns a new proof with added backing."""
        proof1 = Proof.empirical("data", "warrant", "claim")
        proof2 = proof1.strengthen("additional backing")

        assert proof1.backing == ""
        assert proof2.backing == "additional backing"
        assert proof1 is not proof2

    def test_with_rebuttal_returns_new_proof(self) -> None:
        """with_rebuttal() returns a new proof with added rebuttal."""
        proof1 = Proof.empirical("data", "warrant", "claim")
        proof2 = proof1.with_rebuttal("unless X happens")

        assert proof1.rebuttals == ()
        assert proof2.rebuttals == ("unless X happens",)
        assert proof1 is not proof2

    def test_proof_serialization(self) -> None:
        """Proofs can be serialized and deserialized."""
        proof = Proof(
            data="evidence",
            warrant="reasoning",
            claim="conclusion",
            backing="support",
            qualifier="probably",
            rebuttals=("unless A", "unless B"),
            tier=EvidenceTier.EMPIRICAL,
            principles=("generative", "composable"),
        )

        data = proof.to_dict()
        restored = Proof.from_dict(data)

        assert restored.data == proof.data
        assert restored.warrant == proof.warrant
        assert restored.claim == proof.claim
        assert restored.backing == proof.backing
        assert restored.qualifier == proof.qualifier
        assert restored.rebuttals == proof.rebuttals
        assert restored.tier == proof.tier
        assert restored.principles == proof.principles


class TestZeroNode:
    """Test ZeroNode (from A1: Entity)."""

    def test_l1_axiom_no_proof(self) -> None:
        """L1 nodes cannot have proof (axioms are taken on faith)."""
        node = ZeroNode(
            path="void.axiom.entity",
            layer=1,
            kind="axiom",
            title="Entity Axiom",
            content="Everything is a node",
        )
        assert node.layer == 1
        assert node.proof is None
        assert not node.requires_proof()
        assert node.is_axiom()

    def test_l2_value_no_proof(self) -> None:
        """L2 nodes cannot have proof (values are principles)."""
        node = ZeroNode(
            path="void.value.tasteful",
            layer=2,
            kind="value",
            title="Tasteful",
            content="Tasteful > feature-complete",
        )
        assert node.layer == 2
        assert node.proof is None
        assert not node.requires_proof()
        assert node.is_axiom()

    def test_l3_requires_proof(self) -> None:
        """L3+ nodes require proof (M: Justification)."""
        proof = Proof.categorical("data", "warrant", "claim")
        node = ZeroNode(
            path="concept.goal.build",
            layer=3,
            kind="goal",
            title="Build Zero Seed",
            content="Create the kernel",
            proof=proof,
        )
        assert node.layer == 3
        assert node.proof is not None
        assert node.requires_proof()
        assert not node.is_axiom()

    def test_l3_without_proof_raises(self) -> None:
        """L3+ nodes without proof raise ProofRequiredError."""
        with pytest.raises(ProofRequiredError):
            ZeroNode(
                path="concept.goal.bad",
                layer=3,
                kind="goal",
                title="Bad Goal",
                content="No proof!",
            )

    def test_l1_with_proof_raises(self) -> None:
        """L1-L2 nodes with proof raise ProofForbiddenError."""
        proof = Proof.categorical("data", "warrant", "claim")
        with pytest.raises(ProofForbiddenError):
            ZeroNode(
                path="void.axiom.bad",
                layer=1,
                kind="axiom",
                title="Bad Axiom",
                content="Has proof!",
                proof=proof,
            )

    def test_invalid_layer_raises(self) -> None:
        """Layer must be 1-7."""
        with pytest.raises(LayerViolationError):
            ZeroNode(path="bad.path", layer=0, kind="test", title="Bad")

        with pytest.raises(LayerViolationError):
            ZeroNode(path="bad.path", layer=8, kind="test", title="Bad")

    def test_node_immutability(self) -> None:
        """Nodes are immutable (frozen=True)."""
        node = ZeroNode(
            path="void.axiom.test",
            layer=1,
            kind="axiom",
            title="Test",
            content="Content",
        )
        with pytest.raises(AttributeError):
            node.content = "new content"  # type: ignore

    def test_with_lineage(self) -> None:
        """with_lineage() returns new node with parent added."""
        parent_id = generate_node_id()
        node = ZeroNode(
            path="void.axiom.child",
            layer=1,
            kind="axiom",
            title="Child",
            content="Derived from parent",
        )

        child = node.with_lineage(parent_id)
        assert node.lineage == ()
        assert child.lineage == (parent_id,)
        assert node is not child

    def test_node_serialization(self) -> None:
        """Nodes can be serialized and deserialized."""
        node = ZeroNode(
            path="void.value.test",
            layer=2,
            kind="value",
            title="Test Value",
            content="Test content",
            tags=frozenset({"tag1", "tag2"}),
            metadata={"key": "value"},
        )

        data = node.to_dict()
        restored = ZeroNode.from_dict(data)

        assert restored.path == node.path
        assert restored.layer == node.layer
        assert restored.kind == node.kind
        assert restored.title == node.title
        assert restored.content == node.content
        assert restored.tags == node.tags
        assert restored.metadata == node.metadata


class TestZeroEdge:
    """Test ZeroEdge (from A2: Morphism)."""

    def test_edge_creation(self) -> None:
        """Basic edge creation."""
        source = generate_node_id()
        target = generate_node_id()

        edge = ZeroEdge(
            source=source,
            target=target,
            kind=EdgeKind.GROUNDS,
            context="Axiom grounds value",
        )

        assert edge.source == source
        assert edge.target == target
        assert edge.kind == EdgeKind.GROUNDS
        assert edge.confidence == 1.0

    def test_edge_composition(self) -> None:
        """Edge composition via >> operator (A2)."""
        node_a = generate_node_id()
        node_b = generate_node_id()
        node_c = generate_node_id()

        edge1 = ZeroEdge(source=node_a, target=node_b, kind=EdgeKind.GROUNDS)
        edge2 = ZeroEdge(source=node_b, target=node_c, kind=EdgeKind.JUSTIFIES)

        composed = edge1 >> edge2

        assert composed.source == node_a
        assert composed.target == node_c
        # Confidence multiplies
        assert composed.confidence == edge1.confidence * edge2.confidence

    def test_composition_requires_matching_nodes(self) -> None:
        """Edge composition requires target == source."""
        node_a = generate_node_id()
        node_b = generate_node_id()
        node_c = generate_node_id()
        node_d = generate_node_id()

        edge1 = ZeroEdge(source=node_a, target=node_b, kind=EdgeKind.GROUNDS)
        edge2 = ZeroEdge(source=node_c, target=node_d, kind=EdgeKind.JUSTIFIES)

        with pytest.raises(CompositionError):
            edge1 >> edge2

    def test_edge_inverse(self) -> None:
        """Edges have inverses (from A2: bidirectionality)."""
        source = generate_node_id()
        target = generate_node_id()

        edge = ZeroEdge(
            source=source,
            target=target,
            kind=EdgeKind.GROUNDS,
        )

        inverse = edge.inverse()

        assert inverse.source == target
        assert inverse.target == source
        assert inverse.kind == EdgeKind.GROUNDED_BY

    def test_edge_immutability(self) -> None:
        """Edges are immutable (frozen=True)."""
        edge = ZeroEdge(
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.GROUNDS,
        )
        with pytest.raises(AttributeError):
            edge.kind = EdgeKind.JUSTIFIES  # type: ignore

    def test_edge_serialization(self) -> None:
        """Edges can be serialized and deserialized."""
        edge = ZeroEdge(
            source=generate_node_id(),
            target=generate_node_id(),
            kind=EdgeKind.CONTRADICTS,
            context="Test context",
            confidence=0.8,
            is_resolved=True,
        )

        data = edge.to_dict()
        restored = ZeroEdge.from_dict(data)

        assert restored.source == edge.source
        assert restored.target == edge.target
        assert restored.kind == edge.kind
        assert restored.context == edge.context
        assert restored.confidence == edge.confidence
        assert restored.is_resolved == edge.is_resolved


class TestEdgeKind:
    """Test EdgeKind taxonomy."""

    def test_inter_layer_edges(self) -> None:
        """Inter-layer edges cross layers."""
        assert EdgeKind.GROUNDS.is_inter_layer
        assert EdgeKind.JUSTIFIES.is_inter_layer
        assert not EdgeKind.DERIVES_FROM.is_inter_layer

    def test_dialectical_edges(self) -> None:
        """Dialectical edges handle contradictions."""
        assert EdgeKind.CONTRADICTS.is_dialectical
        assert EdgeKind.SYNTHESIZES.is_dialectical
        assert not EdgeKind.GROUNDS.is_dialectical

    def test_layer_delta(self) -> None:
        """Inter-layer edges have layer deltas."""
        assert EdgeKind.GROUNDS.layer_delta == 1
        assert EdgeKind.GROUNDED_BY.layer_delta == -1
        assert EdgeKind.DERIVES_FROM.layer_delta == 0

    def test_edge_inverses(self) -> None:
        """Edge kinds have inverses."""
        assert EdgeKind.GROUNDS.inverse == EdgeKind.GROUNDED_BY
        assert EdgeKind.CONTRADICTS.inverse == EdgeKind.CONTRADICTS  # Symmetric


class TestAgenteseMappings:
    """Test AGENTESE context <-> layer mappings."""

    def test_layer_to_context(self) -> None:
        """Layers map to AGENTESE contexts."""
        assert layer_to_context(1) == "void"
        assert layer_to_context(2) == "void"
        assert layer_to_context(3) == "concept"
        assert layer_to_context(4) == "concept"
        assert layer_to_context(5) == "world"
        assert layer_to_context(6) == "self"
        assert layer_to_context(7) == "time"

    def test_context_to_layers(self) -> None:
        """AGENTESE contexts map back to possible layers."""
        assert context_to_layers("void") == (1, 2)
        assert context_to_layers("concept") == (3, 4)
        assert context_to_layers("world") == (5,)
        assert context_to_layers("self") == (6,)
        assert context_to_layers("time") == (7,)

    def test_parse_agentese_path(self) -> None:
        """AGENTESE paths parse correctly."""
        ctx, domain, name = parse_agentese_path("void.axiom.entity")
        assert ctx == "void"
        assert domain == "axiom"
        assert name == "entity"

        ctx, domain, name = parse_agentese_path("concept.spec.zero-seed")
        assert ctx == "concept"
        assert domain == "spec"
        assert name == "zero-seed"

    def test_invalid_context_raises(self) -> None:
        """Invalid context raises error."""
        with pytest.raises(LayerViolationError):
            layer_to_context(0)

        with pytest.raises(ValueError):
            parse_agentese_path("invalid.path.here")


class TestIdentityEdge:
    """Test identity morphism (from A2: Identity Law)."""

    def test_identity_edge_same_source_target(self) -> None:
        """Identity edge has same source and target."""
        node_id = generate_node_id()
        id_edge = identity_edge(node_id)

        assert id_edge.source == node_id
        assert id_edge.target == node_id

    def test_identity_composition_law(self) -> None:
        """id >> f = f (left identity)."""
        node_a = generate_node_id()
        node_b = generate_node_id()

        id_a = identity_edge(node_a)
        f = ZeroEdge(source=node_a, target=node_b, kind=EdgeKind.GROUNDS)

        composed = id_a >> f
        assert composed.source == f.source
        assert composed.target == f.target


class TestEdgeKindComposition:
    """Test edge kind composition rules."""

    def test_same_kind_idempotent(self) -> None:
        """Same kind composition is idempotent."""
        assert compose_edge_kinds(EdgeKind.GROUNDS, EdgeKind.GROUNDS) == EdgeKind.GROUNDS

    def test_inter_layer_same_direction(self) -> None:
        """Inter-layer same direction composes to derivation."""
        result = compose_edge_kinds(EdgeKind.GROUNDS, EdgeKind.JUSTIFIES)
        assert result == EdgeKind.DERIVES_FROM

    def test_dialectical_composition(self) -> None:
        """Dialectical composition leads to synthesis."""
        result = compose_edge_kinds(EdgeKind.CONTRADICTS, EdgeKind.GROUNDS)
        assert result == EdgeKind.SYNTHESIZES
