"""
Tests for ASHC Self-Awareness Service.

Tests the five self-awareness APIs:
1. am_i_grounded(block_id)
2. what_principle_justifies(action)
3. verify_self_consistency()
4. get_derivation_ancestors(block_id)
5. get_downstream_impact(block_id)

Philosophy:
    "Every component exists because it derives from Constitutional principles.
     These tests verify that derivation structure is queryable and correct."

See: services/zero_seed/ashc_self_awareness.py
"""

from __future__ import annotations

import pytest

from services.zero_seed.ashc_self_awareness import (
    ALL_GENESIS_BLOCKS,
    CONSTITUTIONAL_PRINCIPLES,
    L0_AXIOMS,
    L1_PRIMITIVES,
    L2_DERIVED,
    L3_ARCHITECTURE,
    ASHCSelfAwareness,
    ConsistencyReport,
    EvidenceTier,
    GroundingResult,
    JustificationResult,
    create_ashc_self_awareness,
    get_ashc_self_awareness,
    reset_ashc_self_awareness,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def service() -> ASHCSelfAwareness:
    """Create a fresh service instance for each test."""
    return create_ashc_self_awareness()


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton between tests."""
    reset_ashc_self_awareness()
    yield
    reset_ashc_self_awareness()


# =============================================================================
# Test: Service Initialization
# =============================================================================


class TestServiceInitialization:
    """Tests for service creation and initialization."""

    def test_create_service(self, service: ASHCSelfAwareness):
        """Service can be created."""
        assert service is not None
        assert isinstance(service, ASHCSelfAwareness)

    def test_all_genesis_blocks_loaded(self, service: ASHCSelfAwareness):
        """All 23 genesis blocks are loaded."""
        blocks = service.get_all_blocks()
        # 4 axioms + 3 kernel + 4 derived + 8 principles + 4 architecture = 23
        assert len(blocks) == 23

    def test_axioms_loaded(self, service: ASHCSelfAwareness):
        """L0 axioms are loaded."""
        for axiom_id in L0_AXIOMS:
            block = service.get_block(axiom_id)
            assert block is not None, f"Missing axiom: {axiom_id}"
            assert block.layer == 0

    def test_primitives_loaded(self, service: ASHCSelfAwareness):
        """L1 primitives are loaded."""
        for prim_id in L1_PRIMITIVES:
            block = service.get_block(prim_id)
            assert block is not None, f"Missing primitive: {prim_id}"
            assert block.layer == 1

    def test_derived_loaded(self, service: ASHCSelfAwareness):
        """L2 derived primitives are loaded."""
        for derived_id in L2_DERIVED:
            block = service.get_block(derived_id)
            assert block is not None, f"Missing derived: {derived_id}"
            assert block.layer == 2

    def test_principles_loaded(self, service: ASHCSelfAwareness):
        """Constitutional principles are loaded."""
        for principle_id in CONSTITUTIONAL_PRINCIPLES:
            block = service.get_block(principle_id)
            assert block is not None, f"Missing principle: {principle_id}"
            # Principles are at L0 (CONSTITUTION) or L1
            assert block.layer in (0, 1)

    def test_architecture_loaded(self, service: ASHCSelfAwareness):
        """L3 architecture blocks are loaded."""
        for arch_id in L3_ARCHITECTURE:
            block = service.get_block(arch_id)
            assert block is not None, f"Missing architecture: {arch_id}"
            assert block.layer == 3

    def test_singleton_returns_same_instance(self):
        """Singleton factory returns same instance."""
        service1 = get_ashc_self_awareness()
        service2 = get_ashc_self_awareness()
        assert service1 is service2

    def test_reset_clears_singleton(self):
        """Reset clears the singleton."""
        service1 = get_ashc_self_awareness()
        reset_ashc_self_awareness()
        service2 = get_ashc_self_awareness()
        assert service1 is not service2


# =============================================================================
# Test: API 1 - am_i_grounded()
# =============================================================================


class TestAmIGrounded:
    """Tests for GO-016: am_i_grounded(block_id)."""

    @pytest.mark.asyncio
    async def test_axiom_is_grounded(self, service: ASHCSelfAwareness):
        """L0 axioms are always grounded."""
        result = await service.am_i_grounded("A1_ENTITY")

        assert result.is_grounded is True
        assert "A1_ENTITY" in result.derivation_path
        assert result.evidence_tier == EvidenceTier.CATEGORICAL

    @pytest.mark.asyncio
    async def test_all_axioms_grounded(self, service: ASHCSelfAwareness):
        """All L0 axioms are grounded."""
        for axiom_id in L0_AXIOMS:
            result = await service.am_i_grounded(axiom_id)
            assert result.is_grounded is True, f"Axiom {axiom_id} should be grounded"

    @pytest.mark.asyncio
    async def test_primitive_is_grounded(self, service: ASHCSelfAwareness):
        """L1 primitives are grounded through axioms."""
        result = await service.am_i_grounded("COMPOSE")

        assert result.is_grounded is True
        assert "COMPOSE" in result.derivation_path
        # COMPOSE derives from A2_MORPHISM
        assert "A2_MORPHISM" in result.derivation_path

    @pytest.mark.asyncio
    async def test_derived_is_grounded(self, service: ASHCSelfAwareness):
        """L2 derived blocks are grounded through primitives."""
        result = await service.am_i_grounded("ID")

        assert result.is_grounded is True
        assert "ID" in result.derivation_path
        # ID derives from COMPOSE and JUDGE

    @pytest.mark.asyncio
    async def test_principle_is_grounded(self, service: ASHCSelfAwareness):
        """Principles are grounded through Constitution."""
        result = await service.am_i_grounded("COMPOSABLE")

        assert result.is_grounded is True
        assert "COMPOSABLE" in result.derivation_path
        # COMPOSABLE derives from CONSTITUTION

    @pytest.mark.asyncio
    async def test_architecture_is_grounded(self, service: ASHCSelfAwareness):
        """L3 architecture blocks are grounded through principles."""
        result = await service.am_i_grounded("ASHC")

        assert result.is_grounded is True
        assert "ASHC" in result.derivation_path
        # ASHC derives from COMPOSABLE and GENERATIVE

    @pytest.mark.asyncio
    async def test_all_genesis_blocks_grounded(self, service: ASHCSelfAwareness):
        """All 22 genesis blocks are grounded."""
        for block_id in ALL_GENESIS_BLOCKS:
            result = await service.am_i_grounded(block_id)
            assert result.is_grounded is True, f"Block {block_id} should be grounded"

    @pytest.mark.asyncio
    async def test_unknown_block_not_grounded(self, service: ASHCSelfAwareness):
        """Unknown blocks are not grounded."""
        result = await service.am_i_grounded("UNKNOWN_BLOCK")

        assert result.is_grounded is False
        assert result.evidence_tier == EvidenceTier.CHAOTIC

    @pytest.mark.asyncio
    async def test_grounding_has_loss_at_each_step(self, service: ASHCSelfAwareness):
        """Grounding result includes loss at each derivation step."""
        result = await service.am_i_grounded("ASHC")

        assert len(result.loss_at_each_step) == len(result.derivation_path)
        # All losses should be between 0 and 1
        for loss in result.loss_at_each_step:
            assert 0.0 <= loss <= 1.0

    @pytest.mark.asyncio
    async def test_total_loss_computed(self, service: ASHCSelfAwareness):
        """Total loss is sum of step losses."""
        result = await service.am_i_grounded("ASHC")

        expected_total = sum(result.loss_at_each_step)
        assert abs(result.total_loss - expected_total) < 0.001


# =============================================================================
# Test: API 2 - what_principle_justifies()
# =============================================================================


class TestWhatPrincipleJustifies:
    """Tests for GO-017: what_principle_justifies(action)."""

    @pytest.mark.asyncio
    async def test_composition_action_justified_by_composable(self, service: ASHCSelfAwareness):
        """Actions about composition are justified by COMPOSABLE."""
        result = await service.what_principle_justifies("agent composition")

        assert result.principle == "COMPOSABLE"
        assert result.loss_score < 0.5  # Good match

    @pytest.mark.asyncio
    async def test_joy_action_justified_by_joy_inducing(self, service: ASHCSelfAwareness):
        """Actions about delight are justified by JOY_INDUCING."""
        result = await service.what_principle_justifies("delight in interaction")

        assert result.principle == "JOY_INDUCING"

    @pytest.mark.asyncio
    async def test_ethics_action_justified_by_ethical(self, service: ASHCSelfAwareness):
        """Actions about ethics are justified by ETHICAL."""
        result = await service.what_principle_justifies("preserve human agency")

        assert result.principle == "ETHICAL"

    @pytest.mark.asyncio
    async def test_selection_action_justified_by_curated(self, service: ASHCSelfAwareness):
        """Actions about selection are justified by CURATED."""
        result = await service.what_principle_justifies("intentional selection of features")

        assert result.principle == "CURATED"

    @pytest.mark.asyncio
    async def test_aesthetics_action_justified_by_tasteful(self, service: ASHCSelfAwareness):
        """Actions about aesthetics are justified by TASTEFUL."""
        result = await service.what_principle_justifies("elegant design")

        assert result.principle == "TASTEFUL"

    @pytest.mark.asyncio
    async def test_hierarchy_action_justified_by_heterarchical(self, service: ASHCSelfAwareness):
        """Actions about hierarchy are justified by HETERARCHICAL."""
        result = await service.what_principle_justifies("avoid fixed hierarchy")

        assert result.principle == "HETERARCHICAL"

    @pytest.mark.asyncio
    async def test_regeneration_action_justified_by_generative(self, service: ASHCSelfAwareness):
        """Actions about generation are justified by GENERATIVE."""
        result = await service.what_principle_justifies("spec generates implementation")

        assert result.principle == "GENERATIVE"

    @pytest.mark.asyncio
    async def test_justification_has_reasoning(self, service: ASHCSelfAwareness):
        """Justification includes human-readable reasoning."""
        result = await service.what_principle_justifies("pipeline composition")

        assert len(result.reasoning) > 0
        assert "COMPOSABLE" in result.reasoning or "pipeline" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_justification_has_derivation_chain(self, service: ASHCSelfAwareness):
        """Justification includes derivation chain."""
        result = await service.what_principle_justifies("composition")

        assert len(result.derivation_chain) >= 1
        assert result.principle in result.derivation_chain[0]

    @pytest.mark.asyncio
    async def test_justification_has_evidence_tier(self, service: ASHCSelfAwareness):
        """Justification includes evidence tier classification."""
        result = await service.what_principle_justifies("composition")

        assert result.evidence_tier in EvidenceTier

    @pytest.mark.asyncio
    async def test_unknown_action_has_fallback(self, service: ASHCSelfAwareness):
        """Unknown actions get a fallback justification."""
        result = await service.what_principle_justifies("xyzzy quantum flux capacitor")

        assert result.principle in CONSTITUTIONAL_PRINCIPLES
        assert result.loss_score >= 0.3  # Weak match (higher loss = weaker match)


# =============================================================================
# Test: API 3 - verify_self_consistency()
# =============================================================================


class TestVerifySelfConsistency:
    """Tests for GO-018: verify_self_consistency()."""

    @pytest.mark.asyncio
    async def test_genesis_blocks_are_consistent(self, service: ASHCSelfAwareness):
        """The 22 genesis blocks form a consistent graph."""
        report = await service.verify_self_consistency()

        assert report.is_consistent is True
        assert len(report.violations) == 0

    @pytest.mark.asyncio
    async def test_no_circular_dependencies(self, service: ASHCSelfAwareness):
        """No circular dependencies in genesis blocks."""
        report = await service.verify_self_consistency()

        assert len(report.circular_dependencies) == 0

    @pytest.mark.asyncio
    async def test_no_orphan_blocks(self, service: ASHCSelfAwareness):
        """No orphan blocks in genesis (all reach L0)."""
        report = await service.verify_self_consistency()

        assert len(report.orphan_blocks) == 0

    @pytest.mark.asyncio
    async def test_all_blocks_grounded(self, service: ASHCSelfAwareness):
        """All genesis blocks are grounded."""
        report = await service.verify_self_consistency()

        assert report.total_blocks == report.grounded_blocks

    @pytest.mark.asyncio
    async def test_consistency_score_is_one(self, service: ASHCSelfAwareness):
        """Perfect consistency for genesis blocks."""
        report = await service.verify_self_consistency()

        assert report.consistency_score == 1.0

    @pytest.mark.asyncio
    async def test_report_has_total_blocks(self, service: ASHCSelfAwareness):
        """Report includes total block count."""
        report = await service.verify_self_consistency()

        assert report.total_blocks == 23


# =============================================================================
# Test: API 4 - get_derivation_ancestors()
# =============================================================================


class TestGetDerivationAncestors:
    """Tests for GO-019: get_derivation_ancestors(block_id)."""

    @pytest.mark.asyncio
    async def test_axiom_has_no_ancestors_except_self(self, service: ASHCSelfAwareness):
        """L0 axioms have only themselves as ancestor."""
        ancestors = await service.get_derivation_ancestors("A1_ENTITY")

        assert ancestors == ["A1_ENTITY"]

    @pytest.mark.asyncio
    async def test_primitive_has_axiom_ancestor(self, service: ASHCSelfAwareness):
        """L1 primitives have axiom ancestors."""
        ancestors = await service.get_derivation_ancestors("COMPOSE")

        assert "COMPOSE" in ancestors
        assert "A2_MORPHISM" in ancestors  # COMPOSE derives from A2_MORPHISM

    @pytest.mark.asyncio
    async def test_derived_has_primitive_ancestors(self, service: ASHCSelfAwareness):
        """L2 derived blocks have primitive ancestors."""
        ancestors = await service.get_derivation_ancestors("ID")

        assert "ID" in ancestors
        # ID derives from COMPOSE and JUDGE
        assert "COMPOSE" in ancestors or "JUDGE" in ancestors

    @pytest.mark.asyncio
    async def test_ashc_has_full_lineage(self, service: ASHCSelfAwareness):
        """ASHC has a full lineage to axioms."""
        ancestors = await service.get_derivation_ancestors("ASHC")

        assert "ASHC" in ancestors
        # Should include principles
        assert "COMPOSABLE" in ancestors or "GENERATIVE" in ancestors
        # Should eventually include axioms
        has_axiom = any(a in L0_AXIOMS for a in ancestors)
        assert has_axiom, "ASHC should have axiom ancestors"

    @pytest.mark.asyncio
    async def test_ancestors_start_with_self(self, service: ASHCSelfAwareness):
        """Ancestors list starts with the queried block."""
        for block_id in list(ALL_GENESIS_BLOCKS)[:5]:  # Test a few
            ancestors = await service.get_derivation_ancestors(block_id)
            assert ancestors[0] == block_id

    @pytest.mark.asyncio
    async def test_unknown_block_returns_empty(self, service: ASHCSelfAwareness):
        """Unknown blocks return empty list."""
        ancestors = await service.get_derivation_ancestors("UNKNOWN_BLOCK")

        assert ancestors == []


# =============================================================================
# Test: API 5 - get_downstream_impact()
# =============================================================================


class TestGetDownstreamImpact:
    """Tests for GO-020: get_downstream_impact(block_id)."""

    @pytest.mark.asyncio
    async def test_axiom_has_many_dependents(self, service: ASHCSelfAwareness):
        """L0 axioms have many downstream dependents."""
        dependents = await service.get_downstream_impact("A1_ENTITY")

        # A1_ENTITY is used by GROUND, which is used by others
        assert len(dependents) > 0

    @pytest.mark.asyncio
    async def test_constitution_has_principle_dependents(self, service: ASHCSelfAwareness):
        """CONSTITUTION has 7 principles as dependents."""
        dependents = await service.get_downstream_impact("CONSTITUTION")

        # All 7 principles derive from CONSTITUTION
        principle_ids = {
            "TASTEFUL",
            "CURATED",
            "ETHICAL",
            "JOY_INDUCING",
            "COMPOSABLE",
            "HETERARCHICAL",
            "GENERATIVE",
        }
        found_principles = set(dependents) & principle_ids
        assert len(found_principles) == 7

    @pytest.mark.asyncio
    async def test_principle_has_architecture_dependents(self, service: ASHCSelfAwareness):
        """Principles have architecture block dependents."""
        dependents = await service.get_downstream_impact("COMPOSABLE")

        # ASHC and METAPHYSICAL_FULLSTACK derive from COMPOSABLE
        assert "ASHC" in dependents or "METAPHYSICAL_FULLSTACK" in dependents

    @pytest.mark.asyncio
    async def test_architecture_has_no_dependents(self, service: ASHCSelfAwareness):
        """L3 architecture blocks have no dependents (leaf nodes)."""
        dependents = await service.get_downstream_impact("ASHC")

        # In the genesis set, L3 blocks are leaves
        assert len(dependents) == 0

    @pytest.mark.asyncio
    async def test_unknown_block_returns_empty(self, service: ASHCSelfAwareness):
        """Unknown blocks return empty list."""
        dependents = await service.get_downstream_impact("UNKNOWN_BLOCK")

        assert dependents == []

    @pytest.mark.asyncio
    async def test_dependents_exclude_self(self, service: ASHCSelfAwareness):
        """Dependents list excludes the queried block."""
        dependents = await service.get_downstream_impact("CONSTITUTION")

        assert "CONSTITUTION" not in dependents


# =============================================================================
# Test: Evidence Tier Classification
# =============================================================================


class TestEvidenceTier:
    """Tests for Galois loss evidence tier classification."""

    def test_categorical_tier(self):
        """Loss < 0.10 is CATEGORICAL."""
        assert EvidenceTier.from_loss(0.0) == EvidenceTier.CATEGORICAL
        assert EvidenceTier.from_loss(0.05) == EvidenceTier.CATEGORICAL
        assert EvidenceTier.from_loss(0.09) == EvidenceTier.CATEGORICAL

    def test_empirical_tier(self):
        """Loss 0.10-0.38 is EMPIRICAL."""
        assert EvidenceTier.from_loss(0.10) == EvidenceTier.EMPIRICAL
        assert EvidenceTier.from_loss(0.25) == EvidenceTier.EMPIRICAL
        assert EvidenceTier.from_loss(0.37) == EvidenceTier.EMPIRICAL

    def test_aesthetic_tier(self):
        """Loss 0.38-0.45 is AESTHETIC."""
        assert EvidenceTier.from_loss(0.38) == EvidenceTier.AESTHETIC
        assert EvidenceTier.from_loss(0.42) == EvidenceTier.AESTHETIC
        assert EvidenceTier.from_loss(0.44) == EvidenceTier.AESTHETIC

    def test_somatic_tier(self):
        """Loss 0.45-0.65 is SOMATIC."""
        assert EvidenceTier.from_loss(0.45) == EvidenceTier.SOMATIC
        assert EvidenceTier.from_loss(0.55) == EvidenceTier.SOMATIC
        assert EvidenceTier.from_loss(0.64) == EvidenceTier.SOMATIC

    def test_chaotic_tier(self):
        """Loss >= 0.65 is CHAOTIC."""
        assert EvidenceTier.from_loss(0.65) == EvidenceTier.CHAOTIC
        assert EvidenceTier.from_loss(0.8) == EvidenceTier.CHAOTIC
        assert EvidenceTier.from_loss(1.0) == EvidenceTier.CHAOTIC


# =============================================================================
# Test: why_does_this_exist() - High-Level Query
# =============================================================================


class TestWhyDoesThisExist:
    """Tests for the high-level existence explanation."""

    @pytest.mark.asyncio
    async def test_explains_axiom(self, service: ASHCSelfAwareness):
        """Can explain why an axiom exists."""
        explanation = await service.why_does_this_exist("A1_ENTITY")

        assert "A1_ENTITY" in explanation
        assert "Grounded" in explanation
        assert "Yes" in explanation  # is grounded

    @pytest.mark.asyncio
    async def test_explains_architecture(self, service: ASHCSelfAwareness):
        """Can explain why ASHC exists."""
        explanation = await service.why_does_this_exist("ASHC")

        assert "ASHC" in explanation
        assert "Grounded" in explanation
        assert "COMPOSABLE" in explanation or "GENERATIVE" in explanation

    @pytest.mark.asyncio
    async def test_explains_with_galois_loss(self, service: ASHCSelfAwareness):
        """Explanation includes Galois loss."""
        explanation = await service.why_does_this_exist("COMPOSABLE")

        assert "Galois loss" in explanation

    @pytest.mark.asyncio
    async def test_explains_downstream_impact(self, service: ASHCSelfAwareness):
        """Explanation includes downstream impact."""
        explanation = await service.why_does_this_exist("CONSTITUTION")

        assert "Downstream impact" in explanation
        # CONSTITUTION has 7 dependent principles
        assert "7" in explanation or "depend" in explanation.lower()

    @pytest.mark.asyncio
    async def test_explains_unknown_block(self, service: ASHCSelfAwareness):
        """Explains unknown block gracefully."""
        explanation = await service.why_does_this_exist("UNKNOWN_BLOCK")

        assert "unknown" in explanation.lower()


# =============================================================================
# Test: Utility Methods
# =============================================================================


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_get_block_returns_block(self, service: ASHCSelfAwareness):
        """get_block returns the block object."""
        block = service.get_block("COMPOSABLE")

        assert block is not None
        assert block.id == "COMPOSABLE"

    def test_get_block_returns_none_for_unknown(self, service: ASHCSelfAwareness):
        """get_block returns None for unknown blocks."""
        block = service.get_block("UNKNOWN")

        assert block is None

    def test_get_blocks_by_layer_0(self, service: ASHCSelfAwareness):
        """get_blocks_by_layer returns L0 axioms."""
        blocks = service.get_blocks_by_layer(0)

        # L0 includes axioms and CONSTITUTION
        assert len(blocks) >= 4

    def test_get_blocks_by_layer_1(self, service: ASHCSelfAwareness):
        """get_blocks_by_layer returns L1 blocks."""
        blocks = service.get_blocks_by_layer(1)

        # L1 includes primitives and principles
        assert len(blocks) >= 3

    def test_get_blocks_by_layer_3(self, service: ASHCSelfAwareness):
        """get_blocks_by_layer returns L3 architecture."""
        blocks = service.get_blocks_by_layer(3)

        assert len(blocks) == 4
        block_ids = {b.id for b in blocks}
        assert block_ids == L3_ARCHITECTURE


# =============================================================================
# Integration Test: Full Derivation Chain
# =============================================================================


class TestFullDerivationChain:
    """Integration tests for complete derivation chains."""

    @pytest.mark.asyncio
    async def test_ashc_full_derivation_chain(self, service: ASHCSelfAwareness):
        """
        ASHC has a complete derivation chain to L0.

        Expected chain:
        ASHC -> (COMPOSABLE, GENERATIVE) -> CONSTITUTION ->
        (A1, A2, A3, G) -> (axioms)
        """
        # Get grounding
        grounding = await service.am_i_grounded("ASHC")
        assert grounding.is_grounded is True

        # Get ancestors
        ancestors = await service.get_derivation_ancestors("ASHC")

        # Should include ASHC
        assert "ASHC" in ancestors

        # Should include at least one principle
        principles_in_chain = set(ancestors) & CONSTITUTIONAL_PRINCIPLES
        assert len(principles_in_chain) > 0, "Should have principle ancestors"

        # Should reach L0
        axioms_in_chain = set(ancestors) & L0_AXIOMS
        assert len(axioms_in_chain) > 0, "Should reach L0 axioms"

    @pytest.mark.asyncio
    async def test_constitution_is_hub(self, service: ASHCSelfAwareness):
        """
        CONSTITUTION is the hub connecting axioms to principles.

        Downstream: 7 principles + transitively architecture
        Upstream: 4 axioms
        """
        # Check descendants
        dependents = await service.get_downstream_impact("CONSTITUTION")

        # All principles derive from CONSTITUTION
        for principle in [
            "TASTEFUL",
            "CURATED",
            "ETHICAL",
            "JOY_INDUCING",
            "COMPOSABLE",
            "HETERARCHICAL",
            "GENERATIVE",
        ]:
            assert principle in dependents, f"{principle} should depend on CONSTITUTION"

        # Architecture blocks should be transitively dependent
        # (through principles)
        assert any(arch in dependents for arch in L3_ARCHITECTURE)

    @pytest.mark.asyncio
    async def test_derivation_respects_layers(self, service: ASHCSelfAwareness):
        """Derivations flow from lower to higher layers."""
        for block_id in ALL_GENESIS_BLOCKS:
            block = service.get_block(block_id)
            if not block:
                continue

            for parent_id in block.derives_from:
                parent = service.get_block(parent_id)
                if parent:
                    assert parent.layer <= block.layer, (
                        f"{block_id} (L{block.layer}) derives from "
                        f"{parent_id} (L{parent.layer}) - layer violation"
                    )
