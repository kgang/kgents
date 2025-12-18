"""Tests for BrainOperad composition grammar."""

import pytest

from agents.brain.operad import (
    ASSOCIATE_METABOLICS,
    BRAIN_OPERAD,
    CAPTURE_METABOLICS,
    HEAL_METABOLICS,
    SEARCH_METABOLICS,
    SURFACE_METABOLICS,
    MemoryMetabolics,
    create_brain_operad,
)
from agents.operad.core import LawStatus, OperadRegistry


class TestBrainOperadStructure:
    """Test operad structure is correct."""

    def test_operad_name(self):
        """Brain operad should have correct name."""
        assert BRAIN_OPERAD.name == "BrainOperad"

    def test_brain_operations_present(self):
        """Brain-specific operations should be registered."""
        ops = BRAIN_OPERAD.operations
        assert "capture" in ops
        assert "search" in ops
        assert "surface" in ops
        assert "heal" in ops
        assert "associate" in ops

    def test_inherits_universal_operations(self):
        """Should inherit universal operations from AGENT_OPERAD."""
        ops = BRAIN_OPERAD.operations
        assert "seq" in ops
        assert "par" in ops
        assert "branch" in ops
        assert "fix" in ops
        assert "trace" in ops

    def test_brain_laws_present(self):
        """Brain-specific laws should be registered."""
        law_names = [l.name for l in BRAIN_OPERAD.laws]
        assert "capture_idempotence" in law_names
        assert "search_coherence" in law_names
        assert "heal_invariance" in law_names
        assert "associate_symmetry" in law_names

    def test_inherits_universal_laws(self):
        """Should inherit universal laws."""
        law_names = [l.name for l in BRAIN_OPERAD.laws]
        assert "seq_associativity" in law_names
        assert "par_associativity" in law_names


class TestBrainOperadRegistration:
    """Test operad registration."""

    def test_registered_in_global_registry(self):
        """Brain operad should be in OperadRegistry."""
        registered = OperadRegistry.get("BrainOperad")
        assert registered is not None
        assert registered.name == "BrainOperad"

    def test_registry_contains_brain_operad(self):
        """All operads list should include BrainOperad."""
        all_operads = OperadRegistry.all_operads()
        assert "BrainOperad" in all_operads


class TestBrainOperadOperationArities:
    """Test operation arities are correct."""

    def test_capture_is_unary(self):
        """Capture takes one agent."""
        assert BRAIN_OPERAD.operations["capture"].arity == 1

    def test_search_is_unary(self):
        """Search takes one agent."""
        assert BRAIN_OPERAD.operations["search"].arity == 1

    def test_surface_is_unary(self):
        """Surface takes one agent."""
        assert BRAIN_OPERAD.operations["surface"].arity == 1

    def test_heal_is_unary(self):
        """Heal takes one agent."""
        assert BRAIN_OPERAD.operations["heal"].arity == 1

    def test_associate_is_binary(self):
        """Associate takes two agents."""
        assert BRAIN_OPERAD.operations["associate"].arity == 2


class TestBrainLawVerification:
    """Test law verification functions."""

    def test_capture_idempotence_passes(self):
        """Capture idempotence law should pass."""
        from agents.poly import identity

        brain = identity("test_brain")
        result = BRAIN_OPERAD.verify_law("capture_idempotence", brain)
        assert result.status == LawStatus.PASSED

    def test_search_coherence_passes(self):
        """Search coherence law should pass."""
        from agents.poly import identity

        brain = identity("test_brain")
        result = BRAIN_OPERAD.verify_law("search_coherence", brain)
        assert result.status == LawStatus.PASSED

    def test_heal_invariance_passes(self):
        """Heal invariance law should pass."""
        from agents.poly import identity

        brain = identity("test_brain")
        result = BRAIN_OPERAD.verify_law("heal_invariance", brain)
        assert result.status == LawStatus.PASSED

    def test_associate_symmetry_passes(self):
        """Associate symmetry law should pass."""
        from agents.poly import identity

        a = identity("crystal_a")
        b = identity("crystal_b")
        result = BRAIN_OPERAD.verify_law("associate_symmetry", a, b)
        assert result.status == LawStatus.PASSED


class TestMemoryMetabolics:
    """Test metabolic costs."""

    def test_capture_requires_embedding(self):
        """Capture metabolics should require embedding."""
        assert CAPTURE_METABOLICS.requires_embedding is True

    def test_surface_no_embedding(self):
        """Surface metabolics should not require embedding."""
        assert SURFACE_METABOLICS.requires_embedding is False

    def test_heal_has_high_coherency_impact(self):
        """Heal should have significant coherency impact."""
        assert HEAL_METABOLICS.coherency_impact >= 0.5

    def test_search_no_coherency_impact(self):
        """Search should not impact coherency."""
        assert SEARCH_METABOLICS.coherency_impact == 0.0

    def test_estimate_tokens_scales_with_content(self):
        """Token estimation should scale with content length."""
        short_estimate = CAPTURE_METABOLICS.estimate_tokens(100)
        long_estimate = CAPTURE_METABOLICS.estimate_tokens(1000)
        assert long_estimate > short_estimate


class TestBrainOperadCreateFunction:
    """Test operad factory function."""

    def test_create_brain_operad_returns_operad(self):
        """Factory function should return an Operad."""
        operad = create_brain_operad()
        assert operad.name == "BrainOperad"
        assert len(operad.operations) >= 10  # Universal + Brain ops

    def test_created_operad_has_laws(self):
        """Created operad should have laws."""
        operad = create_brain_operad()
        assert len(operad.laws) >= 6  # Universal + Brain laws
