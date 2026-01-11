"""
Tests for the Genesis K-Block Factory.

Tests that the factory produces valid K-Blocks with correct
derivation chains, Galois loss values, and content.
"""

from __future__ import annotations

import pytest

from services.zero_seed.genesis_kblocks import GenesisKBlock, GenesisKBlockFactory


class TestGenesisKBlock:
    """Tests for the GenesisKBlock dataclass."""

    def test_valid_kblock_creation(self) -> None:
        """Test that valid K-Blocks can be created."""
        kblock = GenesisKBlock(
            id="TEST_KBLOCK",
            title="Test K-Block",
            layer=1,
            galois_loss=0.05,
            content="# Test Content",
            derives_from=("PARENT_1", "PARENT_2"),
            tags=("test", "example"),
        )
        assert kblock.id == "TEST_KBLOCK"
        assert kblock.layer == 1
        assert kblock.galois_loss == 0.05
        assert len(kblock.derives_from) == 2

    def test_invalid_layer_raises_error(self) -> None:
        """Test that invalid layer values raise ValueError."""
        with pytest.raises(ValueError, match="Layer must be 0-7"):
            GenesisKBlock(
                id="BAD",
                title="Bad",
                layer=8,  # Invalid
                galois_loss=0.0,
                content="",
            )

    def test_invalid_galois_loss_raises_error(self) -> None:
        """Test that invalid Galois loss values raise ValueError."""
        with pytest.raises(ValueError, match="Galois loss must be 0.0-1.0"):
            GenesisKBlock(
                id="BAD",
                title="Bad",
                layer=0,
                galois_loss=1.5,  # Invalid
                content="",
            )


class TestGenesisKBlockFactory:
    """Tests for the GenesisKBlockFactory."""

    @pytest.fixture
    def factory(self) -> GenesisKBlockFactory:
        """Create a factory instance."""
        return GenesisKBlockFactory()

    def test_create_all_returns_correct_count(self, factory: GenesisKBlockFactory) -> None:
        """Test that create_all returns all K-Blocks."""
        blocks = factory.create_all()
        # 4 axioms + 3 kernel + 4 derived + 1 constitution + 7 principles + 4 architecture
        assert len(blocks) == 23

    def test_all_kblocks_have_content(self, factory: GenesisKBlockFactory) -> None:
        """Test that all K-Blocks have non-empty content."""
        for block in factory.create_all():
            assert block.content, f"K-Block {block.id} has no content"
            assert len(block.content) > 100, f"K-Block {block.id} content too short"

    def test_axioms_have_zero_loss(self, factory: GenesisKBlockFactory) -> None:
        """Test that L0 axioms have zero Galois loss."""
        axioms = factory.create_axioms()
        for axiom in axioms:
            assert axiom.layer == 0
            assert axiom.galois_loss == 0.0, f"Axiom {axiom.id} should have zero loss"

    def test_axioms_have_no_derivation(self, factory: GenesisKBlockFactory) -> None:
        """Test that pure axioms have no parent derivations."""
        pure_axioms = [
            factory.create_a1_entity(),
            factory.create_a2_morphism(),
            factory.create_a3_mirror(),
            factory.create_g_galois(),
        ]
        for axiom in pure_axioms:
            assert len(axiom.derives_from) == 0, f"Axiom {axiom.id} should have no parents"

    def test_kernel_derives_from_axioms(self, factory: GenesisKBlockFactory) -> None:
        """Test that kernel primitives derive from axioms."""
        compose = factory.create_compose()
        assert "A2_MORPHISM" in compose.derives_from

        judge = factory.create_judge()
        assert "A3_MIRROR" in judge.derives_from

        ground = factory.create_ground()
        assert "A1_ENTITY" in ground.derives_from

    def test_derived_primitives_have_higher_loss(self, factory: GenesisKBlockFactory) -> None:
        """Test that L2 derived primitives have higher loss than L1 kernel."""
        kernel = factory.create_kernel()
        derived = factory.create_derived()

        max_kernel_loss = max(b.galois_loss for b in kernel)
        min_derived_loss = min(b.galois_loss for b in derived)

        assert min_derived_loss >= max_kernel_loss, (
            "Derived primitives should have equal or higher loss than kernel"
        )

    def test_principles_derive_from_constitution(self, factory: GenesisKBlockFactory) -> None:
        """Test that all 7 principles derive from Constitution."""
        principles = factory.create_principles()
        constitution = factory.create_constitution()

        # Constitution itself derives from axioms
        assert "A1_ENTITY" in constitution.derives_from
        assert "A2_MORPHISM" in constitution.derives_from
        assert "A3_MIRROR" in constitution.derives_from

        # Other principles derive from Constitution
        for principle in principles:
            if principle.id != "CONSTITUTION":
                assert "CONSTITUTION" in principle.derives_from, (
                    f"Principle {principle.id} should derive from CONSTITUTION"
                )

    def test_architecture_derives_from_principles(self, factory: GenesisKBlockFactory) -> None:
        """Test that architecture K-Blocks derive from principles."""
        architecture = factory.create_architecture()

        # All architecture blocks should derive from at least one principle
        principle_ids = {"COMPOSABLE", "GENERATIVE", "ETHICAL", "HETERARCHICAL"}
        for block in architecture:
            has_principle_parent = any(p in principle_ids for p in block.derives_from)
            assert has_principle_parent, (
                f"Architecture block {block.id} should derive from a principle"
            )

    def test_layer_consistency(self, factory: GenesisKBlockFactory) -> None:
        """Test that K-Blocks are in correct layers."""
        blocks = factory.create_all()

        # Check layer assignments
        for block in blocks:
            if block.id in {"A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS", "CONSTITUTION"}:
                assert block.layer == 0, f"{block.id} should be L0"
            elif block.id in {"COMPOSE", "JUDGE", "GROUND"} or block.id in {
                "TASTEFUL",
                "CURATED",
                "ETHICAL",
                "JOY_INDUCING",
                "COMPOSABLE",
                "HETERARCHICAL",
                "GENERATIVE",
            }:
                assert block.layer == 1, f"{block.id} should be L1"
            elif block.id in {"ID", "CONTRADICT", "SUBLATE", "FIX"}:
                assert block.layer == 2, f"{block.id} should be L2"
            elif block.id in {"ASHC", "METAPHYSICAL_FULLSTACK", "HYPERGRAPH_EDITOR", "AGENTESE"}:
                assert block.layer == 3, f"{block.id} should be L3"

    def test_all_kblocks_have_tags(self, factory: GenesisKBlockFactory) -> None:
        """Test that all K-Blocks have at least one tag."""
        for block in factory.create_all():
            assert len(block.tags) > 0, f"K-Block {block.id} has no tags"

    def test_unique_ids(self, factory: GenesisKBlockFactory) -> None:
        """Test that all K-Block IDs are unique."""
        blocks = factory.create_all()
        ids = [b.id for b in blocks]
        assert len(ids) == len(set(ids)), "K-Block IDs must be unique"

    def test_content_mentions_layer(self, factory: GenesisKBlockFactory) -> None:
        """Test that K-Block content mentions its layer."""
        for block in factory.create_all():
            # Content should contain layer information
            layer_mentioned = f"L{block.layer}" in block.content or "Layer" in block.content
            assert layer_mentioned, f"K-Block {block.id} content should mention its layer"

    def test_content_has_markdown_headers(self, factory: GenesisKBlockFactory) -> None:
        """Test that all K-Blocks have proper markdown structure."""
        for block in factory.create_all():
            # Should start with a header
            assert block.content.strip().startswith("#"), (
                f"K-Block {block.id} should start with a markdown header"
            )

    def test_galois_loss_monotonicity(self, factory: GenesisKBlockFactory) -> None:
        """Test that Galois loss generally increases with derivation distance."""
        blocks = factory.create_all()
        block_map = {b.id: b for b in blocks}

        # For each block, check that loss >= max of parent losses
        for block in blocks:
            if block.derives_from:
                max_parent_loss = max(
                    block_map[p].galois_loss for p in block.derives_from if p in block_map
                )
                assert block.galois_loss >= max_parent_loss, (
                    f"K-Block {block.id} loss ({block.galois_loss}) should be >= "
                    f"max parent loss ({max_parent_loss})"
                )


class TestDerivationChains:
    """Tests for derivation chain consistency."""

    @pytest.fixture
    def factory(self) -> GenesisKBlockFactory:
        """Create a factory instance."""
        return GenesisKBlockFactory()

    def test_all_derivations_are_valid(self, factory: GenesisKBlockFactory) -> None:
        """Test that all derivation references point to existing K-Blocks."""
        blocks = factory.create_all()
        valid_ids = {b.id for b in blocks}

        for block in blocks:
            for parent_id in block.derives_from:
                assert parent_id in valid_ids, (
                    f"K-Block {block.id} references non-existent parent {parent_id}"
                )

    def test_no_circular_derivations(self, factory: GenesisKBlockFactory) -> None:
        """Test that there are no circular derivation chains."""
        blocks = factory.create_all()
        block_map = {b.id: b for b in blocks}

        def has_cycle(block_id: str, visited: set[str]) -> bool:
            if block_id in visited:
                return True
            visited = visited | {block_id}
            block = block_map.get(block_id)
            if block is None:
                return False
            for parent_id in block.derives_from:
                if has_cycle(parent_id, visited):
                    return True
            return False

        for block in blocks:
            assert not has_cycle(block.id, set()), f"K-Block {block.id} has circular derivation"

    def test_axioms_are_reachable(self, factory: GenesisKBlockFactory) -> None:
        """Test that all K-Blocks can trace back to axioms."""
        blocks = factory.create_all()
        block_map = {b.id: b for b in blocks}
        axiom_ids = {"A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS"}

        def reaches_axiom(block_id: str, visited: set[str]) -> bool:
            if block_id in axiom_ids:
                return True
            if block_id in visited:
                return False
            visited = visited | {block_id}
            block = block_map.get(block_id)
            if block is None:
                return False
            if not block.derives_from:
                return block_id in axiom_ids
            return any(reaches_axiom(p, visited) for p in block.derives_from)

        for block in blocks:
            assert reaches_axiom(block.id, set()), f"K-Block {block.id} cannot trace back to axioms"
