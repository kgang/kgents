"""
CLI Aspect Registration Validation.

This module ensures that aspects exposed to the CLI are properly configured.
Per spec §4.2, this ensures AI agents cannot misconfigure commands.

The AI-Safety Guarantee:
Because registration validates completeness, AI agents constructing CLI commands cannot:
1. Create orphan commands - Every command must map to a registered path
2. Forget effect declarations - MUTATION aspects won't register without effects
3. Skip help text - Registration requires documentation
4. Hide LLM costs - CALLS effects require budget estimates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.agentese.affordances import AspectMetadata


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""

    ERROR = auto()  # Registration should fail
    WARNING = auto()  # Registration proceeds but flagged


@dataclass(frozen=True)
class ValidationError:
    """
    A single validation error from aspect registration.

    Attributes:
        path: The AGENTESE path being validated (e.g., "self.forest.prune")
        message: Human-readable description of the issue
        severity: ERROR (blocks registration) or WARNING (flagged but proceeds)
        code: Machine-readable error code for programmatic handling
    """

    path: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: str = ""

    def __str__(self) -> str:
        prefix = "ERROR" if self.severity == ValidationSeverity.ERROR else "WARNING"
        code_suffix = f" [{self.code}]" if self.code else ""
        return f"{prefix}{code_suffix}: {self.path}: {self.message}"


@dataclass
class ValidationResult:
    """
    Result of validating an aspect registration.

    Attributes:
        path: The path that was validated
        errors: List of validation errors (including warnings)
        valid: Whether the registration can proceed (no ERROR severity)
    """

    path: str
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """True if no ERROR-severity issues exist."""
        return not any(e.severity == ValidationSeverity.ERROR for e in self.errors)

    @property
    def warnings(self) -> list[ValidationError]:
        """Get only WARNING-severity issues."""
        return [e for e in self.errors if e.severity == ValidationSeverity.WARNING]

    @property
    def blocking_errors(self) -> list[ValidationError]:
        """Get only ERROR-severity issues."""
        return [e for e in self.errors if e.severity == ValidationSeverity.ERROR]

    def __bool__(self) -> bool:
        """Truthy if validation passed (no blocking errors)."""
        return self.valid


def validate_aspect_registration(
    node_path: str,
    aspect_meta: "AspectMetadata",
    strict: bool = False,
) -> ValidationResult:
    """
    Validate aspect metadata at registration time.

    Per spec §4.2, this ensures AI agents cannot misconfigure.

    Validation Rules:
    1. Category is required (ERROR)
    2. Effects must be declared for MUTATION/GENERATION (ERROR)
    3. Help text required (WARNING, escalates to ERROR if strict=True)
    4. CALLS effect requires budget estimation (WARNING)
    5. Streaming and interactive are mutually exclusive (ERROR)

    Args:
        node_path: The AGENTESE path (e.g., "self.forest.prune")
        aspect_meta: The AspectMetadata from the @aspect decorator
        strict: If True, warnings become errors

    Returns:
        ValidationResult with all errors and warnings

    Example:
        >>> from protocols.agentese.affordances import AspectMetadata, AspectCategory
        >>> meta = AspectMetadata(
        ...     category=AspectCategory.MUTATION,
        ...     effects=[],  # Missing!
        ...     requires_archetype=(),
        ...     idempotent=False,
        ...     description="",
        ... )
        >>> result = validate_aspect_registration("self.test.mutate", meta)
        >>> result.valid
        False
        >>> result.blocking_errors[0].message
        'MUTATION/GENERATION aspects must declare effects'
    """
    from protocols.agentese.affordances import AspectCategory, DeclaredEffect, Effect

    result = ValidationResult(path=node_path)

    # Rule 1: Category is required
    if aspect_meta.category is None:
        result.errors.append(
            ValidationError(
                path=node_path,
                message="AspectCategory required for CLI exposure",
                severity=ValidationSeverity.ERROR,
                code="MISSING_CATEGORY",
            )
        )

    # Rule 2: Effects must be declared for MUTATION/GENERATION
    if aspect_meta.category in (AspectCategory.MUTATION, AspectCategory.GENERATION):
        if not aspect_meta.effects:
            result.errors.append(
                ValidationError(
                    path=node_path,
                    message="MUTATION/GENERATION aspects must declare effects",
                    severity=ValidationSeverity.ERROR,
                    code="MISSING_EFFECTS",
                )
            )

    # Rule 3: Help text required
    if not aspect_meta.help:
        severity = ValidationSeverity.ERROR if strict else ValidationSeverity.WARNING
        result.errors.append(
            ValidationError(
                path=node_path,
                message="Help text required for CLI exposure",
                severity=severity,
                code="MISSING_HELP",
            )
        )

    # Rule 4: CALLS effect requires budget estimation
    has_calls = any(
        isinstance(e, DeclaredEffect) and e.effect == Effect.CALLS
        for e in aspect_meta.effects
    )
    if has_calls and aspect_meta.budget_estimate is None:
        result.errors.append(
            ValidationError(
                path=node_path,
                message="LLM-backed aspects must estimate budget",
                severity=ValidationSeverity.WARNING,
                code="MISSING_BUDGET",
            )
        )

    # Rule 5: Streaming and interactive are mutually exclusive
    if aspect_meta.streaming and aspect_meta.interactive:
        result.errors.append(
            ValidationError(
                path=node_path,
                message="streaming and interactive are mutually exclusive",
                severity=ValidationSeverity.ERROR,
                code="CONFLICTING_MODES",
            )
        )

    return result


def validate_all_registrations(
    registrations: dict[str, "AspectMetadata"],
    strict: bool = False,
) -> dict[str, ValidationResult]:
    """
    Validate all aspect registrations in a registry.

    Args:
        registrations: Dict mapping paths to AspectMetadata
        strict: If True, warnings become errors

    Returns:
        Dict mapping paths to ValidationResults
    """
    return {
        path: validate_aspect_registration(path, meta, strict=strict)
        for path, meta in registrations.items()
    }


def format_validation_report(results: dict[str, ValidationResult]) -> str:
    """
    Format validation results as a human-readable report.

    Args:
        results: Dict of path -> ValidationResult

    Returns:
        Formatted report string
    """
    lines: list[str] = []

    # Summary
    total = len(results)
    valid = sum(1 for r in results.values() if r.valid)
    warnings = sum(len(r.warnings) for r in results.values())
    errors = sum(len(r.blocking_errors) for r in results.values())

    lines.append("=" * 60)
    lines.append("ASPECT REGISTRATION VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Total Aspects: {total}")
    lines.append(f"Valid: {valid}")
    lines.append(f"Invalid: {total - valid}")
    lines.append(f"Errors: {errors}")
    lines.append(f"Warnings: {warnings}")
    lines.append("")

    # Details for invalid registrations
    invalid = {path: r for path, r in results.items() if not r.valid}
    if invalid:
        lines.append("-" * 60)
        lines.append("BLOCKING ERRORS (must fix before registration)")
        lines.append("-" * 60)
        for path, result in sorted(invalid.items()):
            for error in result.blocking_errors:
                lines.append(str(error))
        lines.append("")

    # Details for warnings
    with_warnings = {path: r for path, r in results.items() if r.warnings}
    if with_warnings:
        lines.append("-" * 60)
        lines.append("WARNINGS (recommended to fix)")
        lines.append("-" * 60)
        for path, result in sorted(with_warnings.items()):
            for warning in result.warnings:
                lines.append(str(warning))
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


__all__ = [
    # Types
    "ValidationSeverity",
    "ValidationError",
    "ValidationResult",
    # Functions
    "validate_aspect_registration",
    "validate_all_registrations",
    "format_validation_report",
]
