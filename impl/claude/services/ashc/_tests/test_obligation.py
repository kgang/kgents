"""
Tests for ASHC Obligation Extraction.

These tests verify the obligation extractor correctly transforms:
- Test failures → formal properties
- Type signatures → type obligations
- Pipeline compositions → composition obligations

Phase 2 Exit Criteria:
- [ ] Obligation extractor handles pytest failure format
- [ ] Type signature extraction works with @node decorator
- [ ] Context extraction is bounded (no payload bloat)
- [ ] Obligations serialize cleanly to JSON

Teaching:
    gotcha: These tests use fixed assertions, not property-based tests.
            The extraction is pattern-based and deterministic—we want
            predictable outputs for each input pattern.
"""

from __future__ import annotations

import pytest

from ..contracts import ObligationId, ObligationSource, ProofObligation
from ..obligation import (
    MAX_CONTEXT_LINE_LENGTH,
    MAX_CONTEXT_LINES,
    ObligationExtractor,
    extract_from_pytest_report,
)

# =============================================================================
# ObligationExtractor Basic Tests
# =============================================================================


class TestObligationExtractorBasics:
    """Tests for basic extractor behavior."""

    def test_creates_empty_session(self) -> None:
        """New extractor starts with no obligations."""
        extractor = ObligationExtractor()

        assert extractor.obligation_count == 0
        assert extractor.obligations == []

    def test_clear_resets_session(self) -> None:
        """clear() removes all extracted obligations."""
        extractor = ObligationExtractor()

        # Add an obligation
        extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert True",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert extractor.obligation_count == 1

        extractor.clear()

        assert extractor.obligation_count == 0

    def test_generates_unique_ids(self) -> None:
        """Each obligation gets a unique ID."""
        extractor = ObligationExtractor()

        obl1 = extractor.from_test_failure(
            test_name="test_a",
            assertion="assert True",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        obl2 = extractor.from_test_failure(
            test_name="test_b",
            assertion="assert True",
            traceback="",
            source_file="test.py",
            line_number=2,
        )

        assert obl1.id != obl2.id

    def test_to_dict_serialization(self) -> None:
        """to_dict() produces expected structure."""
        extractor = ObligationExtractor()

        extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert x > 0",
            traceback="",
            source_file="test.py",
            line_number=10,
        )

        data = extractor.to_dict()

        assert data["obligation_count"] == 1
        assert len(data["obligations"]) == 1
        assert "id" in data["obligations"][0]
        assert "property" in data["obligations"][0]


# =============================================================================
# Test Failure Extraction Tests
# =============================================================================


class TestFromTestFailure:
    """Tests for from_test_failure() method."""

    def test_simple_comparison(self) -> None:
        """Simple comparisons become forall properties."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_positive",
            assertion="assert x > 0",
            traceback="",
            source_file="test_math.py",
            line_number=42,
        )

        assert "∀" in obl.property
        assert "x > 0" in obl.property
        assert obl.source == ObligationSource.TEST
        assert obl.source_location == "test_math.py:42"

    def test_equality_check(self) -> None:
        """Equality assertions become forall properties."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_identity",
            assertion="assert x + 0 == x",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert "∀" in obl.property
        assert "x + 0 == x" in obl.property

    def test_multiple_variables(self) -> None:
        """Multiple variables are quantified."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_add",
            assertion="assert x + y == y + x",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        # Both x and y should be quantified
        assert "∀" in obl.property
        assert "x" in obl.property
        assert "y" in obl.property

    def test_strips_assert_prefix(self) -> None:
        """'assert ' prefix is stripped from assertion."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert   x > 0",  # Extra spaces
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        # Property shouldn't contain "assert"
        assert "assert" not in obl.property.lower()
        assert "x > 0" in obl.property

    def test_strips_comments(self) -> None:
        """Trailing comments are removed."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert x > 0  # This should always hold",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert "#" not in obl.property
        assert "should always hold" not in obl.property

    def test_membership_check(self) -> None:
        """'in' checks become forall properties."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_membership",
            assertion="assert item in collection",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert "∀" in obl.property
        assert "item" in obl.property
        assert "in" in obl.property

    def test_boolean_expression(self) -> None:
        """Boolean expressions become forall properties."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_bool",
            assertion="assert a and b or c",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert "∀" in obl.property

    def test_function_call_assertion(self) -> None:
        """Function calls in assertions are preserved."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_func",
            assertion="assert is_valid(x)",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        assert "∀" in obl.property
        assert "is_valid(x)" in obl.property

    def test_test_name_in_context(self) -> None:
        """Test name is added to context."""
        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_important_invariant",
            assertion="assert True",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        context_str = " ".join(obl.context)
        assert "test_important_invariant" in context_str


# =============================================================================
# Context Extraction Tests
# =============================================================================


class TestContextExtraction:
    """Tests for context extraction from tracebacks."""

    def test_context_limited_to_max(self) -> None:
        """Context extraction is bounded to MAX_CONTEXT_LINES."""
        extractor = ObligationExtractor()

        # Create traceback with many lines
        long_traceback = "\n".join([f"x{i} = {i}" for i in range(20)])

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert False",
            traceback=long_traceback,
            source_file="test.py",
            line_number=1,
        )

        # Context should not exceed limit (plus test name)
        assert len(obl.context) <= MAX_CONTEXT_LINES + 1

    def test_long_lines_truncated(self) -> None:
        """Lines longer than MAX_CONTEXT_LINE_LENGTH are truncated."""
        extractor = ObligationExtractor()

        long_line = "x = " + "a" * 500
        traceback = long_line

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert False",
            traceback=traceback,
            source_file="test.py",
            line_number=1,
        )

        for ctx in obl.context:
            assert len(ctx) <= MAX_CONTEXT_LINE_LENGTH + 10  # Some tolerance

    def test_extracts_variable_assignments(self) -> None:
        """Variable assignments are captured in context."""
        extractor = ObligationExtractor()

        traceback = """
        x = 42
        y = compute_value()
        assert x > y
        """

        obl = extractor.from_test_failure(
            test_name="test_compare",
            assertion="assert x > y",
            traceback=traceback,
            source_file="test.py",
            line_number=4,
        )

        context_str = " ".join(obl.context)
        assert "x = 42" in context_str or "y = compute_value()" in context_str

    def test_extracts_error_messages(self) -> None:
        """Error messages are captured in context."""
        extractor = ObligationExtractor()

        traceback = """
        AssertionError: Expected x > 0
        """

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert x > 0",
            traceback=traceback,
            source_file="test.py",
            line_number=1,
        )

        context_str = " ".join(obl.context)
        assert "Error" in context_str or "error" in context_str.lower()

    def test_skips_traceback_markers(self) -> None:
        """Traceback and File markers are not included."""
        extractor = ObligationExtractor()

        traceback = """
        Traceback (most recent call last):
          File "test.py", line 1, in test_foo
            assert False
        AssertionError
        """

        obl = extractor.from_test_failure(
            test_name="test_foo",
            assertion="assert False",
            traceback=traceback,
            source_file="test.py",
            line_number=1,
        )

        for ctx in obl.context:
            assert not ctx.startswith("Traceback")
            assert not ctx.startswith("File ")


# =============================================================================
# Type Signature Extraction Tests
# =============================================================================


class TestFromTypeSignature:
    """Tests for from_type_signature() method."""

    def test_simple_type_signature(self) -> None:
        """Simple type signature becomes forall property."""
        extractor = ObligationExtractor()

        obl = extractor.from_type_signature(
            path="world.tools.bash",
            input_type="BashRequest",
            output_type="BashResult",
        )

        assert "∀ x: BashRequest" in obl.property
        assert "BashResult" in obl.property
        assert obl.source == ObligationSource.TYPE
        assert obl.source_location == "world.tools.bash"

    def test_type_with_effects(self) -> None:
        """Effects are included in property."""
        extractor = ObligationExtractor()

        obl = extractor.from_type_signature(
            path="world.tools.bash",
            input_type="BashRequest",
            output_type="Witness[BashResult]",
            effects=("filesystem", "subprocess"),
        )

        assert "filesystem" in obl.property
        assert "subprocess" in obl.property
        assert "effects:" in obl.property

    def test_effects_in_context(self) -> None:
        """Effects are also in context."""
        extractor = ObligationExtractor()

        obl = extractor.from_type_signature(
            path="world.tools.bash",
            input_type="BashRequest",
            output_type="BashResult",
            effects=("filesystem",),
        )

        context_str = " ".join(obl.context)
        assert "filesystem" in context_str

    def test_generic_output_type(self) -> None:
        """Generic types like Witness[T] are preserved."""
        extractor = ObligationExtractor()

        obl = extractor.from_type_signature(
            path="self.brain.capture",
            input_type="CaptureRequest",
            output_type="Witness[CaptureResult]",
        )

        assert "Witness[CaptureResult]" in obl.property


# =============================================================================
# Composition Extraction Tests
# =============================================================================


class TestFromComposition:
    """Tests for from_composition() method."""

    def test_simple_composition(self) -> None:
        """Pipeline composition becomes composition property."""
        extractor = ObligationExtractor()

        obl = extractor.from_composition(
            pipeline_name="ProcessPipeline",
            agents=("Parser", "Validator", "Executor"),
            expected_type="ExecutionResult",
        )

        assert "Composition" in obl.property
        assert "Parser >> Validator >> Executor" in obl.property
        assert "ExecutionResult" in obl.property
        assert obl.source == ObligationSource.COMPOSITION

    def test_composition_context_includes_law(self) -> None:
        """Composition context includes associativity law."""
        extractor = ObligationExtractor()

        obl = extractor.from_composition(
            pipeline_name="Test",
            agents=("A", "B"),
            expected_type="T",
        )

        context_str = " ".join(obl.context)
        assert "Law" in context_str or "(f >> g) >> h" in context_str


# =============================================================================
# Variable Extraction Tests
# =============================================================================


class TestVariableExtraction:
    """Tests for _extract_variables() method."""

    def test_simple_variables(self) -> None:
        """Simple variable names are extracted."""
        extractor = ObligationExtractor()

        variables = extractor._extract_variables("x + y == z")

        assert "x" in variables
        assert "y" in variables
        assert "z" in variables

    def test_excludes_keywords(self) -> None:
        """Python keywords are not extracted as variables."""
        extractor = ObligationExtractor()

        variables = extractor._extract_variables("x and True or False")

        assert "x" in variables
        assert "and" not in variables
        assert "True" not in variables
        assert "or" not in variables
        assert "False" not in variables

    def test_excludes_builtins(self) -> None:
        """Builtin function names are not extracted."""
        extractor = ObligationExtractor()

        variables = extractor._extract_variables("len(items) > 0")

        assert "items" in variables
        assert "len" not in variables

    def test_excludes_constants(self) -> None:
        """ALL_CAPS constants are not extracted."""
        extractor = ObligationExtractor()

        variables = extractor._extract_variables("x < MAX_SIZE")

        assert "x" in variables
        assert "MAX_SIZE" not in variables

    def test_excludes_private(self) -> None:
        """Private variables (_foo) are not extracted."""
        extractor = ObligationExtractor()

        variables = extractor._extract_variables("_internal + public")

        assert "public" in variables
        assert "_internal" not in variables


# =============================================================================
# pytest Report Integration Tests
# =============================================================================


class TestPytestReportExtraction:
    """Tests for extract_from_pytest_report() function."""

    def test_extracts_from_failed_test(self) -> None:
        """Failed test report produces obligation."""
        report = {
            "nodeid": "test_math.py::test_positive",
            "outcome": "failed",
            "longrepr": "assert x > 0\nAssertionError",
            "lineno": 42,
        }

        obl = extract_from_pytest_report(report)

        assert obl is not None
        assert obl.source == ObligationSource.TEST
        assert "test_math.py" in obl.source_location

    def test_returns_none_for_passed(self) -> None:
        """Passed test report returns None."""
        report = {
            "nodeid": "test_math.py::test_positive",
            "outcome": "passed",
        }

        obl = extract_from_pytest_report(report)

        assert obl is None

    def test_handles_missing_fields(self) -> None:
        """Gracefully handles missing report fields."""
        report = {
            "nodeid": "test.py::test_foo",
            "outcome": "failed",
            # Missing longrepr, lineno
        }

        obl = extract_from_pytest_report(report)

        assert obl is not None
        assert obl.source == ObligationSource.TEST


# =============================================================================
# Serialization Tests
# =============================================================================


class TestObligationSerialization:
    """Tests for obligation serialization."""

    def test_roundtrip_serialization(self) -> None:
        """Obligations can be serialized and deserialized."""
        extractor = ObligationExtractor()

        original = extractor.from_test_failure(
            test_name="test_roundtrip",
            assertion="assert x == y",
            traceback="x = 1\ny = 2",
            source_file="test.py",
            line_number=10,
        )

        data = original.to_dict()
        restored = ProofObligation.from_dict(data)

        assert restored.property == original.property
        assert restored.source == original.source
        assert restored.source_location == original.source_location
        # Note: Context may differ slightly due to test name injection

    def test_json_compatible(self) -> None:
        """to_dict() produces JSON-serializable output."""
        import json

        extractor = ObligationExtractor()

        obl = extractor.from_test_failure(
            test_name="test_json",
            assertion="assert True",
            traceback="",
            source_file="test.py",
            line_number=1,
        )

        # Should not raise
        json_str = json.dumps(obl.to_dict())
        assert json_str is not None
