"""Tests for GestaltOperad composition grammar."""

import pytest
from agents.gestalt.operad import (
    ANALYZE_METABOLICS,
    COMPARE_METABOLICS,
    GESTALT_OPERAD,
    HEAL_METABOLICS,
    MERGE_METABOLICS,
    SCAN_METABOLICS,
    WATCH_METABOLICS,
    ArchitectureMetabolics,
    create_gestalt_operad,
)
from agents.operad.core import LawStatus, OperadRegistry


class TestGestaltOperadStructure:
    """Test operad structure is correct."""

    def test_operad_name(self):
        """Gestalt operad should have correct name."""
        assert GESTALT_OPERAD.name == "GestaltOperad"

    def test_gestalt_operations_present(self):
        """Gestalt-specific operations should be registered."""
        ops = GESTALT_OPERAD.operations
        assert "scan" in ops
        assert "watch" in ops
        assert "analyze" in ops
        assert "heal" in ops
        assert "compare" in ops
        assert "merge" in ops

    def test_inherits_universal_operations(self):
        """Should inherit universal operations from AGENT_OPERAD."""
        ops = GESTALT_OPERAD.operations
        assert "seq" in ops
        assert "par" in ops
        assert "branch" in ops
        assert "fix" in ops
        assert "trace" in ops

    def test_gestalt_laws_present(self):
        """Gestalt-specific laws should be registered."""
        law_names = [law.name for law in GESTALT_OPERAD.laws]
        assert "scan_idempotence" in law_names
        assert "watch_monotonicity" in law_names
        assert "analyze_coherence" in law_names
        assert "heal_determinism" in law_names
        assert "compare_symmetry" in law_names
        assert "merge_associativity" in law_names

    def test_inherits_universal_laws(self):
        """Should inherit universal laws."""
        law_names = [law.name for law in GESTALT_OPERAD.laws]
        assert "seq_associativity" in law_names
        assert "par_associativity" in law_names


class TestGestaltOperadRegistration:
    """Test operad registration."""

    def test_registered_in_global_registry(self):
        """Gestalt operad should be in OperadRegistry."""
        registered = OperadRegistry.get("GestaltOperad")
        assert registered is not None
        assert registered.name == "GestaltOperad"

    def test_registry_contains_gestalt_operad(self):
        """All operads list should include GestaltOperad."""
        all_operads = OperadRegistry.all_operads()
        assert "GestaltOperad" in all_operads


class TestGestaltOperadOperationArities:
    """Test operation arities are correct."""

    def test_scan_is_unary(self):
        """Scan takes one agent (codebase)."""
        assert GESTALT_OPERAD.operations["scan"].arity == 1

    def test_watch_is_unary(self):
        """Watch takes one agent (codebase)."""
        assert GESTALT_OPERAD.operations["watch"].arity == 1

    def test_analyze_is_unary(self):
        """Analyze takes one agent (module)."""
        assert GESTALT_OPERAD.operations["analyze"].arity == 1

    def test_heal_is_unary(self):
        """Heal takes one agent (graph)."""
        assert GESTALT_OPERAD.operations["heal"].arity == 1

    def test_compare_is_binary(self):
        """Compare takes two agents (graphs)."""
        assert GESTALT_OPERAD.operations["compare"].arity == 2

    def test_merge_is_binary(self):
        """Merge takes two agents (graphs)."""
        assert GESTALT_OPERAD.operations["merge"].arity == 2


class TestGestaltOperadSignatures:
    """Test operation signatures are documented."""

    def test_scan_signature(self):
        """Scan should have correct signature."""
        op = GESTALT_OPERAD.operations["scan"]
        assert "Codebase" in op.signature
        assert "ArchitectureGraph" in op.signature

    def test_watch_signature(self):
        """Watch should have correct signature."""
        op = GESTALT_OPERAD.operations["watch"]
        assert "stream" in op.signature.lower()

    def test_analyze_signature(self):
        """Analyze should have correct signature."""
        op = GESTALT_OPERAD.operations["analyze"]
        assert "Module" in op.signature

    def test_heal_signature(self):
        """Heal should have correct signature."""
        op = GESTALT_OPERAD.operations["heal"]
        assert "Drift" in op.signature or "Suggestion" in op.signature

    def test_compare_signature(self):
        """Compare should have correct signature."""
        op = GESTALT_OPERAD.operations["compare"]
        assert "×" in op.signature or "Diff" in op.signature

    def test_merge_signature(self):
        """Merge should have correct signature."""
        op = GESTALT_OPERAD.operations["merge"]
        assert "×" in op.signature


class TestGestaltLawVerification:
    """Test law verification functions."""

    def test_scan_idempotence_passes(self):
        """Scan idempotence law should pass."""
        from agents.poly import identity

        codebase = identity("test_codebase")
        result = GESTALT_OPERAD.verify_law("scan_idempotence", codebase)
        assert result.status == LawStatus.PASSED

    def test_watch_monotonicity_passes(self):
        """Watch monotonicity law should pass."""
        from agents.poly import identity

        codebase = identity("test_codebase")
        result = GESTALT_OPERAD.verify_law("watch_monotonicity", codebase)
        assert result.status == LawStatus.PASSED

    def test_analyze_coherence_passes(self):
        """Analyze coherence law should pass."""
        from agents.poly import identity

        module = identity("test_module")
        result = GESTALT_OPERAD.verify_law("analyze_coherence", module)
        assert result.status == LawStatus.PASSED

    def test_heal_determinism_passes(self):
        """Heal determinism law should pass."""
        from agents.poly import identity

        graph = identity("test_graph")
        result = GESTALT_OPERAD.verify_law("heal_determinism", graph)
        assert result.status == LawStatus.PASSED

    def test_compare_symmetry_passes(self):
        """Compare symmetry law should pass."""
        from agents.poly import identity

        graph_a = identity("graph_a")
        graph_b = identity("graph_b")
        result = GESTALT_OPERAD.verify_law("compare_symmetry", graph_a, graph_b)
        assert result.status == LawStatus.PASSED

    def test_merge_associativity_passes(self):
        """Merge associativity law should pass."""
        from agents.poly import identity

        a = identity("graph_a")
        b = identity("graph_b")
        result = GESTALT_OPERAD.verify_law("merge_associativity", a, b)
        assert result.status == LawStatus.PASSED


class TestArchitectureMetabolics:
    """Test metabolic costs."""

    def test_scan_requires_filesystem(self):
        """Scan metabolics should require filesystem."""
        assert SCAN_METABOLICS.requires_filesystem is True

    def test_watch_requires_filesystem(self):
        """Watch metabolics should require filesystem."""
        assert WATCH_METABOLICS.requires_filesystem is True

    def test_analyze_no_filesystem(self):
        """Analyze metabolics should not require filesystem."""
        assert ANALYZE_METABOLICS.requires_filesystem is False

    def test_heal_no_filesystem(self):
        """Heal metabolics should not require filesystem."""
        assert HEAL_METABOLICS.requires_filesystem is False

    def test_scan_has_highest_complexity_factor(self):
        """Scan should have highest complexity factor (full codebase)."""
        assert SCAN_METABOLICS.complexity_factor >= WATCH_METABOLICS.complexity_factor
        assert SCAN_METABOLICS.complexity_factor >= ANALYZE_METABOLICS.complexity_factor

    def test_watch_has_low_complexity(self):
        """Watch should have low complexity (incremental)."""
        assert WATCH_METABOLICS.complexity_factor < 0.5

    def test_estimate_tokens_scales_with_modules(self):
        """Token estimation should scale with module count."""
        small_estimate = SCAN_METABOLICS.estimate_tokens(50)
        large_estimate = SCAN_METABOLICS.estimate_tokens(500)
        assert large_estimate > small_estimate

    def test_non_filesystem_ops_dont_scale_as_much(self):
        """Non-filesystem ops should scale less with module count."""
        # Analyze doesn't need to read files, just works on existing graph
        analyze_small = ANALYZE_METABOLICS.estimate_tokens(50)
        analyze_large = ANALYZE_METABOLICS.estimate_tokens(500)

        scan_small = SCAN_METABOLICS.estimate_tokens(50)
        scan_large = SCAN_METABOLICS.estimate_tokens(500)

        scan_ratio = scan_large / scan_small
        analyze_ratio = analyze_large / analyze_small

        assert analyze_ratio < scan_ratio


class TestGestaltOperadCreateFunction:
    """Test operad factory function."""

    def test_create_gestalt_operad_returns_operad(self):
        """Factory function should return an Operad."""
        operad = create_gestalt_operad()
        assert operad.name == "GestaltOperad"
        assert len(operad.operations) >= 11  # Universal + Gestalt ops

    def test_created_operad_has_laws(self):
        """Created operad should have laws."""
        operad = create_gestalt_operad()
        assert len(operad.laws) >= 8  # Universal + Gestalt laws

    def test_created_operad_has_description(self):
        """Created operad should have description."""
        operad = create_gestalt_operad()
        assert "architecture" in operad.description.lower()


class TestGestaltOperadComposition:
    """Test operation composition via operad."""

    def test_can_compose_scan(self):
        """Can compose a scan operation."""
        from agents.poly import identity

        codebase = identity("codebase")
        scan_op = GESTALT_OPERAD.operations["scan"]
        result = scan_op(codebase)

        assert result is not None
        assert "scan" in result.name

    def test_can_compose_compare(self):
        """Can compose a compare operation (binary)."""
        from agents.poly import identity

        graph_a = identity("graph_a")
        graph_b = identity("graph_b")
        compare_op = GESTALT_OPERAD.operations["compare"]
        result = compare_op(graph_a, graph_b)

        assert result is not None
        assert "compare" in result.name
        assert "graph_a" in result.name
        assert "graph_b" in result.name

    def test_compose_with_wrong_arity_fails(self):
        """Composing with wrong arity should fail."""
        from agents.poly import identity

        codebase = identity("codebase")
        compare_op = GESTALT_OPERAD.operations["compare"]  # arity=2

        with pytest.raises(ValueError, match="requires 2 agents"):
            compare_op(codebase)  # Only 1 agent, needs 2

    def test_sequential_composition_with_universal_ops(self):
        """Can use universal seq operation with gestalt ops."""
        from agents.poly import identity

        graph = identity("graph")
        seq_op = GESTALT_OPERAD.operations["seq"]

        # Create a simple composed agent
        analyze = GESTALT_OPERAD.operations["analyze"](graph)
        heal = GESTALT_OPERAD.operations["heal"](graph)

        result = seq_op(analyze, heal)
        assert result is not None
