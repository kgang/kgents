"""
Tests for CLI Aspect Registration Validation.

These tests verify the validation rules from spec/protocols/cli.md §4.2.
"""

from __future__ import annotations

import pytest

from protocols.agentese.affordances import (
    AspectCategory,
    AspectMetadata,
    Effect,
)
from protocols.cli.validation import (
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    format_validation_report,
    validate_all_registrations,
    validate_aspect_registration,
)

# === ValidationError Tests ===


class TestValidationError:
    """Test ValidationError dataclass."""

    def test_str_format_error(self) -> None:
        """ERROR severity formats correctly."""
        error = ValidationError(
            path="self.test.path",
            message="Something went wrong",
            severity=ValidationSeverity.ERROR,
            code="TEST_ERROR",
        )
        assert str(error) == "ERROR [TEST_ERROR]: self.test.path: Something went wrong"

    def test_str_format_warning(self) -> None:
        """WARNING severity formats correctly."""
        error = ValidationError(
            path="self.test.path",
            message="Something is not ideal",
            severity=ValidationSeverity.WARNING,
            code="TEST_WARNING",
        )
        assert str(error) == "WARNING [TEST_WARNING]: self.test.path: Something is not ideal"

    def test_str_format_no_code(self) -> None:
        """Formatting without code works."""
        error = ValidationError(
            path="self.test.path",
            message="Something went wrong",
        )
        assert str(error) == "ERROR: self.test.path: Something went wrong"


# === ValidationResult Tests ===


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_valid_when_no_errors(self) -> None:
        """Result is valid when no errors."""
        result = ValidationResult(path="self.test.path", errors=[])
        assert result.valid is True
        assert bool(result) is True

    def test_valid_with_only_warnings(self) -> None:
        """Result is valid with only warnings."""
        result = ValidationResult(
            path="self.test.path",
            errors=[
                ValidationError(
                    path="self.test.path",
                    message="warning",
                    severity=ValidationSeverity.WARNING,
                )
            ],
        )
        assert result.valid is True

    def test_invalid_with_error(self) -> None:
        """Result is invalid with error-severity issue."""
        result = ValidationResult(
            path="self.test.path",
            errors=[
                ValidationError(
                    path="self.test.path",
                    message="error",
                    severity=ValidationSeverity.ERROR,
                )
            ],
        )
        assert result.valid is False
        assert bool(result) is False

    def test_warnings_filter(self) -> None:
        """warnings property returns only warnings."""
        result = ValidationResult(
            path="self.test.path",
            errors=[
                ValidationError(
                    path="self.test.path",
                    message="warning1",
                    severity=ValidationSeverity.WARNING,
                ),
                ValidationError(
                    path="self.test.path",
                    message="error1",
                    severity=ValidationSeverity.ERROR,
                ),
                ValidationError(
                    path="self.test.path",
                    message="warning2",
                    severity=ValidationSeverity.WARNING,
                ),
            ],
        )
        warnings = result.warnings
        assert len(warnings) == 2
        assert all(w.severity == ValidationSeverity.WARNING for w in warnings)

    def test_blocking_errors_filter(self) -> None:
        """blocking_errors property returns only errors."""
        result = ValidationResult(
            path="self.test.path",
            errors=[
                ValidationError(
                    path="self.test.path",
                    message="warning1",
                    severity=ValidationSeverity.WARNING,
                ),
                ValidationError(
                    path="self.test.path",
                    message="error1",
                    severity=ValidationSeverity.ERROR,
                ),
            ],
        )
        blocking = result.blocking_errors
        assert len(blocking) == 1
        assert blocking[0].message == "error1"


# === Validation Rule Tests ===


class TestValidateMissingCategory:
    """Test Rule 1: Category is required."""

    def test_missing_category_is_error(self) -> None:
        """Missing category produces ERROR."""
        # Create metadata with None category (simulated)
        meta = AspectMetadata(
            category=None,  # type: ignore[arg-type]
            effects=[],
            requires_archetype=(),
            idempotent=False,
            description="Test",
        )
        result = validate_aspect_registration("self.test.path", meta)
        assert not result.valid
        assert any("AspectCategory required" in e.message for e in result.blocking_errors)


class TestValidateMutationEffects:
    """Test Rule 2: MUTATION/GENERATION must declare effects."""

    def test_mutation_without_effects_is_error(self) -> None:
        """MUTATION without effects produces ERROR."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[],  # Missing!
            requires_archetype=(),
            idempotent=False,
            description="Test mutation",
        )
        result = validate_aspect_registration("self.test.mutate", meta)
        assert not result.valid
        assert any("must declare effects" in e.message for e in result.blocking_errors)

    def test_generation_without_effects_is_error(self) -> None:
        """GENERATION without effects produces ERROR."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[],  # Missing!
            requires_archetype=(),
            idempotent=False,
            description="Test generation",
        )
        result = validate_aspect_registration("self.test.generate", meta)
        assert not result.valid
        assert any("must declare effects" in e.message for e in result.blocking_errors)

    def test_mutation_with_effects_is_valid(self) -> None:
        """MUTATION with effects passes this rule."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("state")],
            requires_archetype=(),
            idempotent=False,
            description="Test mutation",
            help="Mutate state",
        )
        result = validate_aspect_registration("self.test.mutate", meta)
        # Should pass mutation effects rule (may still have warnings)
        assert not any("must declare effects" in e.message for e in result.errors)

    def test_perception_without_effects_is_ok(self) -> None:
        """PERCEPTION without effects is allowed."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[],  # OK for perception
            requires_archetype=(),
            idempotent=True,
            description="Test perception",
            help="Perceive state",
        )
        result = validate_aspect_registration("self.test.perceive", meta)
        # Should not have effect-related errors
        assert not any("must declare effects" in e.message for e in result.errors)


class TestValidateHelpText:
    """Test Rule 3: Help text required."""

    def test_missing_help_is_warning_by_default(self) -> None:
        """Missing help produces WARNING by default."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Test",
            help="",  # Missing!
        )
        result = validate_aspect_registration("self.test.path", meta)
        # Should be valid (warning not error)
        assert result.valid
        assert any("Help text required" in w.message for w in result.warnings)

    def test_missing_help_is_error_in_strict(self) -> None:
        """Missing help produces ERROR in strict mode."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Test",
            help="",  # Missing!
        )
        result = validate_aspect_registration("self.test.path", meta, strict=True)
        assert not result.valid
        assert any("Help text required" in e.message for e in result.blocking_errors)

    def test_with_help_passes(self) -> None:
        """With help text, no help-related errors."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[],
            requires_archetype=(),
            idempotent=True,
            description="Test",
            help="This is the help text",
        )
        result = validate_aspect_registration("self.test.path", meta)
        assert not any("Help text" in e.message for e in result.errors)


class TestValidateBudgetEstimate:
    """Test Rule 4: CALLS effect requires budget estimation."""

    def test_calls_without_budget_is_warning(self) -> None:
        """CALLS without budget_estimate produces WARNING."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.WRITES("state"), Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Test with LLM",
            help="Uses LLM",
            budget_estimate=None,  # Missing!
        )
        result = validate_aspect_registration("self.test.generate", meta)
        assert any("budget" in w.message.lower() for w in result.warnings)

    def test_calls_with_budget_passes(self) -> None:
        """CALLS with budget_estimate has no budget warnings."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.WRITES("state"), Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Test with LLM",
            help="Uses LLM",
            budget_estimate="~200 tokens",
        )
        result = validate_aspect_registration("self.test.generate", meta)
        assert not any("budget" in e.message.lower() for e in result.errors)

    def test_no_calls_no_budget_warning(self) -> None:
        """Without CALLS effect, no budget warning."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("state")],  # No CALLS
            requires_archetype=(),
            idempotent=False,
            description="Test without LLM",
            help="Does not use LLM",
        )
        result = validate_aspect_registration("self.test.mutate", meta)
        assert not any("budget" in e.message.lower() for e in result.errors)


class TestValidateConflictingModes:
    """Test Rule 5: streaming and interactive are mutually exclusive."""

    def test_both_flags_is_error(self) -> None:
        """streaming=True and interactive=True produces ERROR."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Test",
            help="Test",
            streaming=True,
            interactive=True,  # Conflict!
            budget_estimate="~100 tokens",
        )
        result = validate_aspect_registration("self.test.path", meta)
        assert not result.valid
        assert any("mutually exclusive" in e.message for e in result.blocking_errors)

    def test_only_streaming_ok(self) -> None:
        """Only streaming=True is fine."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Test",
            help="Test",
            streaming=True,
            interactive=False,
            budget_estimate="~100 tokens",
        )
        result = validate_aspect_registration("self.test.path", meta)
        assert not any("mutually exclusive" in e.message for e in result.errors)

    def test_only_interactive_ok(self) -> None:
        """Only interactive=True is fine."""
        meta = AspectMetadata(
            category=AspectCategory.GENERATION,
            effects=[Effect.CALLS("llm")],
            requires_archetype=(),
            idempotent=False,
            description="Test",
            help="Test",
            streaming=False,
            interactive=True,
            budget_estimate="~100 tokens",
        )
        result = validate_aspect_registration("self.test.path", meta)
        assert not any("mutually exclusive" in e.message for e in result.errors)


# === Batch Validation Tests ===


class TestValidateAllRegistrations:
    """Test validate_all_registrations() function."""

    def test_validates_all_paths(self) -> None:
        """Validates all paths in the registry."""
        registrations = {
            "self.a.path": AspectMetadata(
                category=AspectCategory.PERCEPTION,
                effects=[],
                requires_archetype=(),
                idempotent=True,
                description="A",
                help="Help A",
            ),
            "self.b.path": AspectMetadata(
                category=AspectCategory.MUTATION,
                effects=[Effect.WRITES("state")],
                requires_archetype=(),
                idempotent=False,
                description="B",
                help="Help B",
            ),
        }
        results = validate_all_registrations(registrations)
        assert len(results) == 2
        assert "self.a.path" in results
        assert "self.b.path" in results


# === Report Formatting Tests ===


class TestFormatValidationReport:
    """Test format_validation_report() function."""

    def test_formats_empty_results(self) -> None:
        """Empty results produce summary."""
        report = format_validation_report({})
        assert "Total Aspects: 0" in report
        assert "Valid: 0" in report

    def test_formats_valid_results(self) -> None:
        """Valid results show correct counts."""
        results = {
            "self.a.path": ValidationResult(path="self.a.path", errors=[]),
            "self.b.path": ValidationResult(path="self.b.path", errors=[]),
        }
        report = format_validation_report(results)
        assert "Total Aspects: 2" in report
        assert "Valid: 2" in report
        assert "Invalid: 0" in report

    def test_formats_invalid_results(self) -> None:
        """Invalid results are reported."""
        results = {
            "self.a.path": ValidationResult(
                path="self.a.path",
                errors=[
                    ValidationError(
                        path="self.a.path",
                        message="Test error",
                        severity=ValidationSeverity.ERROR,
                    )
                ],
            ),
        }
        report = format_validation_report(results)
        assert "Invalid: 1" in report
        assert "BLOCKING ERRORS" in report
        assert "Test error" in report
