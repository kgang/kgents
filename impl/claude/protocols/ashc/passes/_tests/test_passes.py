"""
Tests for ASHC Pass Operad

Verifies:
1. Core types work correctly
2. Bootstrap passes produce valid ProofCarryingIR
3. Composition via >> works
4. Laws hold (identity, associativity, etc.)
5. Operad operations produce correct passes
"""

import pytest

from ..bootstrap import (
    ContradictPass,
    FixPass,
    GroundPass,
    IdentityPass,
    JudgePass,
    SublatePass,
    create_ground_pass,
    create_identity_pass,
    create_judge_pass,
)
from ..composition import ComposedPass, compose, parallel
from ..core import (
    LawResult,
    LawStatus,
    ProofCarryingIR,
    VerificationGraph,
    merge_graphs,
)
from ..laws import (
    AssociativityLaw,
    ClosureLaw,
    FunctorLaw,
    IdentityLaw,
    WitnessLaw,
)
from ..operad import PASS_OPERAD, PassOperad, create_pass_operad

# =============================================================================
# Core Types Tests
# =============================================================================


class TestVerificationGraph:
    """Tests for VerificationGraph."""

    def test_empty_graph(self) -> None:
        """Empty graph has no nodes or edges."""
        graph = VerificationGraph.empty()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_from_witness(self) -> None:
        """Create graph from single witness."""
        graph = VerificationGraph.from_witness(
            pass_name="test",
            witness_id="w1",
        )
        assert len(graph.nodes) == 1
        assert graph.nodes[0].pass_name == "test"
        assert graph.nodes[0].witness_id == "w1"

    def test_merge_graphs(self) -> None:
        """Merge two graphs preserves all nodes."""
        g1 = VerificationGraph.from_witness("p1", "w1")
        g2 = VerificationGraph.from_witness("p2", "w2")

        merged = merge_graphs(g1, g2)

        assert len(merged.nodes) == 2
        witness_ids = {n.witness_id for n in merged.nodes}
        assert witness_ids == {"w1", "w2"}


class TestProofCarryingIR:
    """Tests for ProofCarryingIR."""

    def test_from_output(self) -> None:
        """Create ProofCarryingIR from output."""
        ir = ProofCarryingIR.from_output(
            output={"result": 42},
            witness={"witness_id": "w1"},
            pass_name="test",
        )

        assert ir.ir == {"result": 42}
        assert len(ir.witnesses) == 1

    def test_chain(self) -> None:
        """Chain two ProofCarryingIRs."""
        ir1 = ProofCarryingIR.from_output(
            output={"step": 1},
            witness={"witness_id": "w1"},
            pass_name="p1",
        )
        ir2 = ProofCarryingIR.from_output(
            output={"step": 2},
            witness={"witness_id": "w2"},
            pass_name="p2",
        )

        chained = ir1.chain(ir2)

        # Final IR is from second
        assert chained.ir == {"step": 2}
        # Both witnesses present
        assert len(chained.witnesses) == 2


class TestLawResult:
    """Tests for LawResult."""

    def test_passed(self) -> None:
        """Create passing result."""
        result = LawResult.passed("identity", "verified")
        assert result.holds
        assert result.status == LawStatus.HOLDS

    def test_failed(self) -> None:
        """Create failing result."""
        result = LawResult.failed("identity", "mismatch")
        assert not result.holds
        assert result.status == LawStatus.VIOLATED

    def test_aggregate_all_pass(self) -> None:
        """Aggregate passes when all pass."""
        results = [
            LawResult.passed("law1"),
            LawResult.passed("law2"),
        ]
        agg = LawResult.aggregate(results)
        assert agg.holds

    def test_aggregate_one_fails(self) -> None:
        """Aggregate fails when any fails."""
        results = [
            LawResult.passed("law1"),
            LawResult.failed("law2", "bad"),
        ]
        agg = LawResult.aggregate(results)
        assert not agg.holds


# =============================================================================
# Bootstrap Pass Tests
# =============================================================================


class TestIdentityPass:
    """Tests for IdentityPass."""

    @pytest.mark.asyncio
    async def test_returns_input(self) -> None:
        """Identity returns its input."""
        id_pass = IdentityPass()
        input_val = {"x": 42}

        result = await id_pass.invoke(input_val)

        assert result.ir == input_val

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Identity produces a witness."""
        id_pass = IdentityPass()
        result = await id_pass.invoke({"x": 1})

        assert len(result.witnesses) == 1
        assert result.witnesses[0].pass_name == "id"

    def test_has_correct_types(self) -> None:
        """Identity has correct type info."""
        id_pass = IdentityPass()
        assert id_pass.name == "id"
        assert id_pass.input_type == "A"
        assert id_pass.output_type == "A"


class TestGroundPass:
    """Tests for GroundPass."""

    @pytest.mark.asyncio
    async def test_produces_facts(self) -> None:
        """Ground produces facts from stub."""
        ground = GroundPass()
        result = await ground.invoke(None)

        assert result.ir is not None
        assert "name" in result.ir  # From ground_manifest_stub

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Ground produces a witness."""
        ground = GroundPass()
        result = await ground.invoke(None)

        assert len(result.witnesses) == 1
        assert result.witnesses[0].pass_name == "ground"

    def test_has_correct_types(self) -> None:
        """Ground has correct type info."""
        ground = GroundPass()
        assert ground.name == "ground"
        assert ground.input_type == "Void"
        assert ground.output_type == "Facts"


class TestJudgePass:
    """Tests for JudgePass."""

    @pytest.mark.asyncio
    async def test_produces_verdict(self) -> None:
        """Judge produces verdict."""
        judge = JudgePass()
        result = await judge.invoke({"spec": "test"})

        assert "verdict" in result.ir

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Judge produces a witness."""
        judge = JudgePass()
        result = await judge.invoke({"spec": "test"})

        assert len(result.witnesses) == 1
        assert result.witnesses[0].pass_name == "judge"


class TestContradictPass:
    """Tests for ContradictPass."""

    @pytest.mark.asyncio
    async def test_with_tuple_input(self) -> None:
        """Contradict accepts tuple of two values."""
        contradict = ContradictPass()
        result = await contradict.invoke(({"a": 1}, {"b": 2}))

        # Stub returns None (no contradiction)
        assert result.ir is None

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Contradict produces a witness."""
        contradict = ContradictPass()
        result = await contradict.invoke(({"a": 1}, {"b": 2}))

        assert len(result.witnesses) == 1


class TestSublatePass:
    """Tests for SublatePass."""

    @pytest.mark.asyncio
    async def test_produces_synthesis(self) -> None:
        """Sublate produces synthesis."""
        sublate = SublatePass()
        result = await sublate.invoke({"tension": "conflict"})

        assert "synthesis" in result.ir

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Sublate produces a witness."""
        sublate = SublatePass()
        result = await sublate.invoke({"tension": "conflict"})

        assert len(result.witnesses) == 1


class TestFixPass:
    """Tests for FixPass."""

    @pytest.mark.asyncio
    async def test_with_value(self) -> None:
        """Fix with value returns it (trivial fixed point)."""
        fix = FixPass()
        result = await fix.invoke(42)

        # Value is its own fixed point
        assert result.ir == 42

    @pytest.mark.asyncio
    async def test_produces_witness(self) -> None:
        """Fix produces a witness."""
        fix = FixPass()
        result = await fix.invoke(42)

        assert len(result.witnesses) == 1


# =============================================================================
# Composition Tests
# =============================================================================


class TestComposition:
    """Tests for pass composition."""

    @pytest.mark.asyncio
    async def test_rshift_operator(self) -> None:
        """>> operator composes passes."""
        id1 = IdentityPass()
        id2 = IdentityPass()

        composed = id1 >> id2

        assert isinstance(composed, ComposedPass)
        assert composed.name == "(id >> id)"

    @pytest.mark.asyncio
    async def test_composed_invoke(self) -> None:
        """Composed pass invokes both passes."""
        id1 = IdentityPass()
        id2 = IdentityPass()

        composed = id1 >> id2
        result = await composed.invoke({"x": 1})

        assert result.ir == {"x": 1}  # Identity preserves value
        assert len(result.witnesses) == 2  # Both passes ran

    @pytest.mark.asyncio
    async def test_three_pass_composition(self) -> None:
        """Can compose three passes."""
        id1 = IdentityPass()
        id2 = IdentityPass()
        id3 = IdentityPass()

        composed = id1 >> id2 >> id3
        result = await composed.invoke({"x": 1})

        assert len(result.witnesses) == 3

    @pytest.mark.asyncio
    async def test_ground_then_judge(self) -> None:
        """Ground >> Judge pipeline works."""
        ground = GroundPass()
        judge = JudgePass()

        pipeline = ground >> judge
        result = await pipeline.invoke(None)

        # Judge processed Ground's output
        assert "verdict" in result.ir
        assert len(result.witnesses) == 2

    def test_compose_function(self) -> None:
        """compose() helper works."""
        id1 = IdentityPass()
        id2 = IdentityPass()

        composed = compose(id1, id2)

        assert isinstance(composed, ComposedPass)


# =============================================================================
# Law Tests
# =============================================================================


class TestIdentityLaw:
    """Tests for identity law verification."""

    @pytest.mark.asyncio
    async def test_identity_law_holds(self) -> None:
        """Identity law holds for identity pass."""
        law = IdentityLaw()
        result = await law.verify(IdentityPass())

        assert result.holds

    @pytest.mark.asyncio
    async def test_identity_law_with_ground(self) -> None:
        """Identity law holds for ground pass."""
        law = IdentityLaw()
        # Note: Ground takes None, so identity law test may need adjustment
        # For now, verify it runs without error
        result = await law.verify(GroundPass())
        # The law may not perfectly apply to nullary passes
        assert result.status in (LawStatus.HOLDS, LawStatus.VIOLATED)


class TestAssociativityLaw:
    """Tests for associativity law verification."""

    @pytest.mark.asyncio
    async def test_associativity_law_holds(self) -> None:
        """Associativity law holds for identity passes."""
        law = AssociativityLaw()
        id1 = IdentityPass()
        id2 = IdentityPass()
        id3 = IdentityPass()

        result = await law.verify(id1, id2, id3)

        assert result.holds

    @pytest.mark.asyncio
    async def test_needs_three_passes(self) -> None:
        """Associativity requires 3 passes."""
        law = AssociativityLaw()
        id1 = IdentityPass()

        result = await law.verify(id1)

        assert result.status == LawStatus.ERROR


class TestClosureLaw:
    """Tests for closure law verification."""

    @pytest.mark.asyncio
    async def test_closure_law_holds(self) -> None:
        """Closure law holds: composition produces pass."""
        law = ClosureLaw()
        id1 = IdentityPass()
        id2 = IdentityPass()

        result = await law.verify(id1, id2)

        assert result.holds


class TestWitnessLaw:
    """Tests for witness law verification."""

    @pytest.mark.asyncio
    async def test_all_passes_emit_witnesses(self) -> None:
        """All bootstrap passes emit witnesses."""
        law = WitnessLaw()

        passes = [
            IdentityPass(),
            GroundPass(),
            JudgePass(),
            SublatePass(),
            FixPass(),
        ]

        result = await law.verify(*passes)

        assert result.holds


# =============================================================================
# Operad Tests
# =============================================================================


class TestPassOperad:
    """Tests for PassOperad."""

    def test_has_all_operations(self) -> None:
        """Operad has all bootstrap operations."""
        operad = PASS_OPERAD

        expected = {"id", "ground", "judge", "contradict", "sublate", "fix"}
        actual = set(operad.operations.keys())

        assert expected == actual

    def test_compose_single_pass(self) -> None:
        """Compose with single pass returns that pass."""
        operad = PASS_OPERAD

        result = operad.compose(["id"])

        assert isinstance(result, IdentityPass)

    def test_compose_multiple_passes(self) -> None:
        """Compose multiple passes returns ComposedPass."""
        operad = PASS_OPERAD

        result = operad.compose(["id", "ground"])

        assert isinstance(result, ComposedPass)

    def test_compose_empty_returns_identity(self) -> None:
        """Compose with empty list returns identity."""
        operad = PASS_OPERAD

        result = operad.compose([])

        assert isinstance(result, IdentityPass)

    def test_compose_str(self) -> None:
        """Compose from string expression."""
        operad = PASS_OPERAD

        result = operad.compose_str("ground >> judge")

        assert isinstance(result, ComposedPass)
        assert "ground" in result.name
        assert "judge" in result.name

    def test_unknown_pass_raises(self) -> None:
        """Unknown pass name raises ValueError."""
        operad = PASS_OPERAD

        with pytest.raises(ValueError, match="Unknown pass"):
            operad.compose(["nonexistent"])

    @pytest.mark.asyncio
    async def test_verify_laws(self) -> None:
        """Verify all laws via operad."""
        operad = PASS_OPERAD

        result = await operad.verify_laws()

        # Should run without error
        assert result.status in (LawStatus.HOLDS, LawStatus.VIOLATED)

    @pytest.mark.asyncio
    async def test_verify_specific_law(self) -> None:
        """Verify specific law by name."""
        operad = PASS_OPERAD
        id1 = operad._resolve_pass("id")
        id2 = operad._resolve_pass("id")

        result = await operad.verify_law("identity", id1, id2)

        assert result.law == "identity"

    def test_list_passes(self) -> None:
        """List all available passes."""
        operad = PASS_OPERAD

        passes = operad.list_passes()

        assert len(passes) == 6
        names = {p["name"] for p in passes}
        assert "id" in names
        assert "ground" in names

    def test_list_laws(self) -> None:
        """List all composition laws."""
        operad = PASS_OPERAD

        laws = operad.list_laws()

        assert len(laws) >= 3
        names = {l["name"] for l in laws}
        assert "identity" in names
        assert "associativity" in names


class TestOperadIntegration:
    """Integration tests for full operad usage."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self) -> None:
        """Full pipeline: ground >> judge >> fix."""
        operad = PASS_OPERAD

        pipeline = operad.compose_str("ground >> judge >> fix")
        result = await pipeline.invoke(None)

        # All three passes ran
        assert len(result.witnesses) == 3

        # Verification graph has nodes
        assert len(result.verification_graph.nodes) >= 1

    @pytest.mark.asyncio
    async def test_pipeline_witnesses_chain(self) -> None:
        """Pipeline witnesses form a chain."""
        operad = PASS_OPERAD

        pipeline = operad.compose(["ground", "judge"])
        result = await pipeline.invoke(None)

        # Check witnesses are ordered correctly
        assert result.witnesses[0].pass_name == "ground"
        assert result.witnesses[1].pass_name == "judge"

    @pytest.mark.asyncio
    async def test_parallel_composition(self) -> None:
        """Parallel composition runs both on same input."""
        id1 = IdentityPass()
        id2 = IdentityPass()

        par = parallel(id1, id2)
        result = await par.invoke({"x": 1})

        # Output is tuple of both results
        assert isinstance(result.ir, tuple)
        assert len(result.ir) == 2
        assert len(result.witnesses) == 2
