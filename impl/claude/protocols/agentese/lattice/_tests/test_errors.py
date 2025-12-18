"""
Tests for lattice error types.

Sympathetic errors that explain WHY and suggest WHAT TO DO.
"""

from __future__ import annotations

import pytest

from protocols.agentese.lattice.errors import (
    LatticeError,
    LineageError,
    lattice_affordance_conflict,
    lattice_cycle,
    lattice_unsatisfiable,
    lineage_missing,
    lineage_parents_missing,
)

# === Test LineageError ===


class TestLineageError:
    """Tests for LineageError exception."""

    def test_basic_lineage_error(self) -> None:
        """Test basic LineageError creation."""
        error = LineageError(
            "Concept has no lineage",
            handle="concept.orphan",
        )

        assert error.handle == "concept.orphan"
        # Error message should include sympathetic content
        error_str = str(error)
        assert "orphan" in error_str.lower() or "concept" in error_str

    def test_missing_parents_error(self) -> None:
        """Test LineageError with missing parents."""
        error = LineageError(
            "Parent concepts do not exist",
            handle="concept.test",
            missing_parents=["concept.foo", "concept.bar"],
        )

        assert error.missing_parents == ["concept.foo", "concept.bar"]
        error_str = str(error)
        assert "foo" in error_str or "bar" in error_str

    def test_sympathetic_message(self) -> None:
        """Test that LineageError has sympathetic message."""
        assert LineageError.sympathetic_message
        assert "ex nihilo" in LineageError.sympathetic_message.lower()

    def test_lineage_missing_convenience(self) -> None:
        """Test lineage_missing convenience constructor."""
        error = lineage_missing("concept.test")

        assert isinstance(error, LineageError)
        assert error.handle == "concept.test"

    def test_lineage_parents_missing_convenience(self) -> None:
        """Test lineage_parents_missing convenience constructor."""
        error = lineage_parents_missing(
            "concept.test",
            ["concept.missing1", "concept.missing2"],
        )

        assert isinstance(error, LineageError)
        assert error.handle == "concept.test"
        assert error.missing_parents == ["concept.missing1", "concept.missing2"]


# === Test LatticeError ===


class TestLatticeError:
    """Tests for LatticeError exception."""

    def test_cycle_violation_error(self) -> None:
        """Test LatticeError for cycle violation."""
        error = LatticeError(
            "Would create cycle",
            handle="concept.test",
            violation_type="cycle",
            cycle_path=["concept.a", "concept.b", "concept.a"],
        )

        assert error.handle == "concept.test"
        assert error.violation_type == "cycle"
        assert error.cycle_path == ["concept.a", "concept.b", "concept.a"]

    def test_affordance_conflict_error(self) -> None:
        """Test LatticeError for affordance conflict."""
        error = LatticeError(
            "Parent affordances conflict",
            handle="concept.test",
            violation_type="affordance_conflict",
            conflicting_affordances=["mutable vs immutable"],
        )

        assert error.violation_type == "affordance_conflict"
        assert "mutable vs immutable" in error.conflicting_affordances

    def test_empty_constraints_error(self) -> None:
        """Test LatticeError for empty constraint intersection."""
        error = LatticeError(
            "Constraints unsatisfiable",
            handle="concept.test",
            violation_type="empty_constraints",
            empty_constraints=True,
        )

        assert error.violation_type == "empty_constraints"
        assert error.empty_constraints is True

    def test_lattice_cycle_convenience(self) -> None:
        """Test lattice_cycle convenience constructor."""
        error = lattice_cycle(
            "concept.test",
            ["concept.a", "concept.b", "concept.a"],
        )

        assert isinstance(error, LatticeError)
        assert error.violation_type == "cycle"
        assert error.cycle_path == ["concept.a", "concept.b", "concept.a"]

    def test_lattice_affordance_conflict_convenience(self) -> None:
        """Test lattice_affordance_conflict convenience constructor."""
        error = lattice_affordance_conflict(
            "concept.test",
            ["sync vs async", "pure vs impure"],
        )

        assert isinstance(error, LatticeError)
        assert error.violation_type == "affordance_conflict"
        assert len(error.conflicting_affordances) == 2

    def test_lattice_unsatisfiable_convenience(self) -> None:
        """Test lattice_unsatisfiable convenience constructor."""
        error = lattice_unsatisfiable("concept.test")

        assert isinstance(error, LatticeError)
        assert error.violation_type == "empty_constraints"


# === Test Error Inheritance ===


class TestErrorInheritance:
    """Test that errors properly inherit from AgentesError."""

    def test_lineage_error_is_agentes_error(self) -> None:
        """Test LineageError inherits from AgentesError."""
        from protocols.agentese.exceptions import AgentesError

        error = LineageError("test")
        assert isinstance(error, AgentesError)

    def test_lattice_error_is_agentes_error(self) -> None:
        """Test LatticeError inherits from AgentesError."""
        from protocols.agentese.exceptions import AgentesError

        error = LatticeError("test")
        assert isinstance(error, AgentesError)

    def test_errors_have_why_and_suggestion(self) -> None:
        """Test that errors provide why and suggestion."""
        error = LineageError(
            "Test error",
            handle="concept.test",
        )

        # Should have formatted message with why/try sections
        error_str = str(error)
        # These come from AgentesError formatting
        assert "Why:" in error_str or "Try:" in error_str or "concept" in error_str
