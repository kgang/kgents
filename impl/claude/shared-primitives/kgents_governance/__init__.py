"""
kgents-governance: Universal Law Schemas for Governance

Define and verify governance rules using five universal law schemas.
Works for any domain: software, organizations, games, policies.

Quick Start (10 minutes or less):

    from kgents_governance import (
        LawSchema,
        GovernanceLaw,
        coherence_gate,
        drift_alert,
        verify_law,
    )

    # Define a governance law
    my_law = GovernanceLaw(
        schema=LawSchema.COHERENCE_GATE,
        domain="my_project",
        name="Review Required",
        description="PRs require review before merge",
        predicate=lambda has_review=False, **kw: has_review,
    )

    # Verify the law
    result = verify_law(my_law, {"has_review": True})
    print(result.passed)  # True

The Five Universal Law Schemas:

    All governance laws derive from five fundamental patterns:

    1. COHERENCE_GATE: X is valid only if Y is marked
       Example: "A deploy is valid only if tests passed"

    2. DRIFT_ALERT: If loss > threshold, surface it
       Example: "If code coverage drops below 80%, alert"

    3. GHOST_PRESERVATION: Unchosen paths remain inspectable
       Example: "Rejected PRs remain viewable"

    4. COURAGE_PRESERVATION: High-risk acts protected from penalty
       Example: "Experimental features not penalized in metrics"

    5. COMPRESSION_HONESTY: Compression discloses what was dropped
       Example: "Meeting notes disclose omitted topics"

Why Universal Schemas?

    1. Consistency: Same patterns across all domains
    2. Composability: Laws can be combined and layered
    3. Verification: Automated checking for compliance
    4. Documentation: Self-describing governance rules

Real-World Example:

    # Software project governance
    PROJECT_LAWS = [
        GovernanceLaw(
            schema=LawSchema.COHERENCE_GATE,
            domain="releases",
            name="Release Gate",
            description="Release requires passing CI and approval",
            predicate=lambda ci_passed=False, approved=False, **kw:
                ci_passed and approved,
        ),
        GovernanceLaw(
            schema=LawSchema.DRIFT_ALERT,
            domain="quality",
            name="Coverage Alert",
            description="Alert if test coverage drops below threshold",
            predicate=drift_alert,
        ),
        GovernanceLaw(
            schema=LawSchema.GHOST_PRESERVATION,
            domain="decisions",
            name="Alternative Preservation",
            description="Rejected alternatives remain documented",
            predicate=ghost_preservation,
        ),
    ]

    # Verify all laws
    report = verify_laws(PROJECT_LAWS, my_context)
    if not report.all_passed:
        for failure in report.failures:
            print(f"VIOLATION: {failure.law.name}")

License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any

# -----------------------------------------------------------------------------
# Law Schemas
# -----------------------------------------------------------------------------


class LawSchema(Enum):
    """
    The five universal law schemas.

    All governance laws derive from these fundamental patterns.
    Each schema represents a recurring constraint structure.

    Example:
        >>> law = GovernanceLaw(
        ...     schema=LawSchema.COHERENCE_GATE,
        ...     domain="deployments",
        ...     name="Deploy Gate",
        ...     description="Deploy requires tests to pass",
        ...     predicate=lambda tests_passed=False, **kw: tests_passed,
        ... )
    """

    COHERENCE_GATE = "coherence_gate"
    """X is valid only if Y is marked.

    Pattern: An action is only valid when a prerequisite has been satisfied.
    Enforces temporal ordering and dependency chains.

    Examples:
        - Deploy valid only if tests pass
        - Release valid only if approved
        - Access granted only if authenticated
    """

    DRIFT_ALERT = "drift_alert"
    """If loss > threshold, surface it.

    Pattern: When a metric exceeds tolerance, alert is required.
    Prevents silent degradation of quality.

    Examples:
        - Alert if coverage drops below 80%
        - Alert if latency exceeds 200ms
        - Alert if error rate exceeds 1%
    """

    GHOST_PRESERVATION = "ghost_preservation"
    """Unchosen paths remain inspectable.

    Pattern: Alternatives not taken must be preserved.
    Enables counterfactual reasoning and decision archaeology.

    Examples:
        - Rejected PRs remain viewable
        - Alternative designs documented
        - Discarded options recorded in ADRs
    """

    COURAGE_PRESERVATION = "courage_preservation"
    """High-risk acts protected from penalty.

    Pattern: Bold choices should not be penalized by metrics.
    Encourages innovation and experimentation.

    Examples:
        - Experimental features not penalized
        - Innovative approaches protected
        - Learning failures not counted against
    """

    COMPRESSION_HONESTY = "compression_honesty"
    """Compression discloses what was dropped.

    Pattern: When information is compressed, omissions must be disclosed.
    Ensures lossy operations remain auditable.

    Examples:
        - Meeting notes disclose omitted topics
        - Summaries reference full content
        - Aggregations document exclusions
    """


# -----------------------------------------------------------------------------
# Governance Law
# -----------------------------------------------------------------------------


@dataclass
class GovernanceLaw:
    """
    A governance law derived from a universal schema.

    Each law is a concrete instance of one of the five schemas,
    specialized for a specific domain.

    Example:
        >>> law = GovernanceLaw(
        ...     schema=LawSchema.COHERENCE_GATE,
        ...     domain="code_review",
        ...     name="Review Required",
        ...     description="All PRs require at least one review",
        ...     predicate=lambda review_count=0, **kw: review_count >= 1,
        ... )
        >>> law.verify(review_count=2)  # True
    """

    schema: LawSchema
    domain: str
    name: str
    description: str
    predicate: Callable[..., bool]
    metadata: dict[str, Any] = field(default_factory=dict)

    def verify(self, **context: Any) -> bool:
        """
        Check if the law holds in the given context.

        Args:
            **context: Keyword arguments passed to the predicate

        Returns:
            True if the law holds, False otherwise
        """
        try:
            return self.predicate(**context)
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (excluding predicate)."""
        return {
            "schema": self.schema.value,
            "domain": self.domain,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


# -----------------------------------------------------------------------------
# Schema Predicate Functions
# -----------------------------------------------------------------------------


def coherence_gate(
    action_type: str | None = None,
    marked_types: list[str] | None = None,
    has_prerequisite: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COHERENCE GATE: X is valid only if Y is marked.

    Can be called in two ways:
    1. With action_type and marked_types: checks if action is in marked
    2. With has_prerequisite: direct boolean check

    Args:
        action_type: The type of action being validated
        marked_types: List of action types that have been marked
        has_prerequisite: Direct boolean for prerequisite satisfaction

    Returns:
        True if coherence gate passes

    Example:
        >>> coherence_gate(has_prerequisite=True)
        True
        >>> coherence_gate(action_type="deploy", marked_types=["test", "deploy"])
        True
        >>> coherence_gate(action_type="deploy", marked_types=["test"])
        False
    """
    # Direct boolean check takes precedence
    if has_prerequisite is not None:
        return bool(has_prerequisite)

    # Both must be provided for action/marked check
    if action_type is not None and marked_types is not None:
        if not marked_types:
            return False
        return action_type in marked_types

    # Default to True if no valid arguments (no constraint)
    return True


def drift_alert(
    current_loss: float | None = 0.0,
    threshold: float | None = 0.5,
    surfaced: bool = True,
    in_canon: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    DRIFT ALERT: If loss > threshold, must be surfaced.

    Args:
        current_loss: Current loss/drift value (None = 0.0)
        threshold: Maximum acceptable loss (None = 0.5)
        surfaced: Whether the drift has been surfaced
        in_canon: If provided, checks canon eligibility

    Returns:
        True if drift alert law is satisfied

    Example:
        >>> drift_alert(current_loss=0.3, threshold=0.5, surfaced=True)
        True
        >>> drift_alert(current_loss=0.7, threshold=0.5, surfaced=False)
        False
    """
    loss = current_loss if current_loss is not None else 0.0
    thresh = threshold if threshold is not None else 0.5

    if loss < 0:
        loss = 0.0

    if in_canon is not None:
        # Canon check: high loss cannot be in canon
        if loss >= thresh:
            return not in_canon
        return True

    # Standard: if loss exceeds threshold, must be surfaced
    if loss > thresh:
        return bool(surfaced)
    return True


def ghost_preservation(
    unchosen_paths: list[str] | None = None,
    inspectable_paths: list[str] | None = None,
    ghosts_preserved: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    GHOST PRESERVATION: Unchosen paths remain inspectable.

    Args:
        unchosen_paths: Paths/alternatives that were not chosen
        inspectable_paths: Paths that are currently inspectable
        ghosts_preserved: Direct boolean for preservation status

    Returns:
        True if all ghost alternatives are preserved

    Example:
        >>> ghost_preservation(ghosts_preserved=True)
        True
        >>> ghost_preservation(
        ...     unchosen_paths=["optionA", "optionB"],
        ...     inspectable_paths=["optionA", "optionB", "optionC"]
        ... )
        True
    """
    # Direct boolean check takes precedence
    if ghosts_preserved is not None:
        return bool(ghosts_preserved)

    if unchosen_paths is not None:
        if not unchosen_paths:
            return True  # Nothing to preserve
        if inspectable_paths is None:
            return False  # Ghosts lost
        return all(path in inspectable_paths for path in unchosen_paths)

    return True


def courage_preservation(
    risk_level: float | None = 0.0,
    penalty_applied: float | None = 0.0,
    risk_threshold: float | None = 0.7,
    is_protected: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COURAGE PRESERVATION: High-risk acts protected from penalty.

    Args:
        risk_level: Risk level of the action (0.0 to 1.0)
        penalty_applied: Amount of penalty applied
        risk_threshold: Threshold for "courageous" actions
        is_protected: Direct boolean for protection status

    Returns:
        True if courageous actions are properly protected

    Example:
        >>> courage_preservation(risk_level=0.8, penalty_applied=0.0)
        True
        >>> courage_preservation(risk_level=0.8, penalty_applied=0.5)
        False  # High-risk action penalized
    """
    if is_protected is not None:
        return bool(is_protected)

    risk = risk_level if risk_level is not None else 0.0
    penalty = penalty_applied if penalty_applied is not None else 0.0
    thresh = risk_threshold if risk_threshold is not None else 0.7

    if risk < 0:
        risk = 0.0

    if risk >= thresh:
        return penalty <= 0.0  # High-risk should not be penalized
    return True


def compression_honesty(
    original_elements: set[str] | None = None,
    crystal_elements: set[str] | None = None,
    disclosed_elements: set[str] | None = None,
    drops_disclosed: bool | None = None,
    **kwargs: Any,
) -> bool:
    """
    COMPRESSION HONESTY: Crystal discloses what was dropped.

    Args:
        original_elements: Set of original elements
        crystal_elements: Set of elements in compressed form
        disclosed_elements: Set of dropped elements that were disclosed
        drops_disclosed: Direct boolean for disclosure status

    Returns:
        True if all dropped elements are disclosed

    Example:
        >>> compression_honesty(drops_disclosed=True)
        True
        >>> compression_honesty(
        ...     original_elements={"a", "b", "c"},
        ...     crystal_elements={"a"},
        ...     disclosed_elements={"b", "c"}
        ... )
        True
    """
    if drops_disclosed is not None:
        return bool(drops_disclosed)

    if original_elements is not None:
        if not original_elements:
            return True  # Nothing to compress

        crystal = crystal_elements if crystal_elements is not None else set()
        dropped = original_elements - crystal

        if not dropped:
            return True  # Nothing dropped
        if disclosed_elements is not None:
            return dropped <= disclosed_elements
        return False  # Dropped but not disclosed

    return True


# -----------------------------------------------------------------------------
# Law Verification
# -----------------------------------------------------------------------------


@dataclass
class LawVerificationResult:
    """Result of verifying a single law."""

    law: GovernanceLaw
    passed: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_message: str | None = None

    def __bool__(self) -> bool:
        return self.passed

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "law_name": self.law.name,
            "domain": self.law.domain,
            "schema": self.law.schema.value,
            "passed": self.passed,
            "verified_at": self.verified_at.isoformat(),
            "error_message": self.error_message,
        }


@dataclass
class LawVerificationReport:
    """Report from verifying multiple laws."""

    results: list[LawVerificationResult] = field(default_factory=list)
    verified_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def all_passed(self) -> bool:
        """True if all laws passed."""
        return all(r.passed for r in self.results)

    @property
    def pass_count(self) -> int:
        """Number of laws that passed."""
        return sum(1 for r in self.results if r.passed)

    @property
    def fail_count(self) -> int:
        """Number of laws that failed."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def failures(self) -> list[LawVerificationResult]:
        """List of failed verifications."""
        return [r for r in self.results if not r.passed]

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        total = len(self.results)
        if self.all_passed:
            return f"All {total} law(s) passed."
        failed = [f.law.name for f in self.failures]
        return f"{self.fail_count}/{total} law(s) failed: {', '.join(failed)}"

    def __bool__(self) -> bool:
        return self.all_passed

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "verified_at": self.verified_at.isoformat(),
            "all_passed": self.all_passed,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "results": [r.to_dict() for r in self.results],
        }


def verify_law(
    law: GovernanceLaw,
    context: dict[str, Any],
) -> LawVerificationResult:
    """
    Verify a single law against a context.

    Args:
        law: The law to verify
        context: Context dictionary with verification data

    Returns:
        LawVerificationResult with pass/fail status

    Example:
        >>> law = GovernanceLaw(
        ...     schema=LawSchema.COHERENCE_GATE,
        ...     domain="test",
        ...     name="Test Gate",
        ...     description="Tests must pass",
        ...     predicate=lambda tests_passed=False, **kw: tests_passed,
        ... )
        >>> result = verify_law(law, {"tests_passed": True})
        >>> print(result.passed)  # True
    """
    try:
        passed = law.predicate(**context)
        return LawVerificationResult(law=law, passed=passed)
    except Exception as e:
        return LawVerificationResult(
            law=law,
            passed=False,
            error_message=str(e),
        )


def verify_laws(
    laws: list[GovernanceLaw],
    context: dict[str, Any],
) -> LawVerificationReport:
    """
    Verify multiple laws against a context.

    Args:
        laws: List of laws to verify
        context: Context dictionary with verification data

    Returns:
        LawVerificationReport with all results

    Example:
        >>> laws = [law1, law2, law3]
        >>> report = verify_laws(laws, {"tests_passed": True})
        >>> print(report.summary)
    """
    results = [verify_law(law, context) for law in laws]
    return LawVerificationReport(results=results)


# -----------------------------------------------------------------------------
# Law Builder (Fluent API)
# -----------------------------------------------------------------------------


class LawBuilder:
    """
    Fluent builder for governance laws.

    Example:
        >>> law = (LawBuilder()
        ...     .with_schema(LawSchema.COHERENCE_GATE)
        ...     .in_domain("deployments")
        ...     .named("Deploy Gate")
        ...     .described("Deploys require passing tests")
        ...     .when(lambda tests_passed=False, **kw: tests_passed)
        ...     .build())
    """

    def __init__(self) -> None:
        self._schema: LawSchema | None = None
        self._domain: str = ""
        self._name: str = ""
        self._description: str = ""
        self._predicate: Callable[..., bool] | None = None
        self._metadata: dict[str, Any] = {}

    def with_schema(self, schema: LawSchema) -> LawBuilder:
        """Set the law schema."""
        self._schema = schema
        return self

    def in_domain(self, domain: str) -> LawBuilder:
        """Set the domain."""
        self._domain = domain
        return self

    def named(self, name: str) -> LawBuilder:
        """Set the law name."""
        self._name = name
        return self

    def described(self, description: str) -> LawBuilder:
        """Set the description."""
        self._description = description
        return self

    def when(self, predicate: Callable[..., bool]) -> LawBuilder:
        """Set the predicate function."""
        self._predicate = predicate
        return self

    def with_metadata(self, **metadata: Any) -> LawBuilder:
        """Add metadata."""
        self._metadata.update(metadata)
        return self

    def build(self) -> GovernanceLaw:
        """Build the governance law."""
        if self._schema is None:
            raise ValueError("Schema is required")
        if self._predicate is None:
            raise ValueError("Predicate is required")

        return GovernanceLaw(
            schema=self._schema,
            domain=self._domain,
            name=self._name,
            description=self._description,
            predicate=self._predicate,
            metadata=self._metadata,
        )


# -----------------------------------------------------------------------------
# Convenience: Common Law Patterns
# -----------------------------------------------------------------------------


def gate_law(
    domain: str,
    name: str,
    description: str,
    required_field: str,
) -> GovernanceLaw:
    """
    Create a simple gate law (coherence gate).

    Args:
        domain: Domain for the law
        name: Law name
        description: Law description
        required_field: Field that must be True

    Returns:
        A GovernanceLaw that checks the field is True

    Example:
        >>> law = gate_law(
        ...     domain="releases",
        ...     name="Approval Required",
        ...     description="Releases require approval",
        ...     required_field="is_approved",
        ... )
        >>> law.verify(is_approved=True)  # True
    """
    return GovernanceLaw(
        schema=LawSchema.COHERENCE_GATE,
        domain=domain,
        name=name,
        description=description,
        predicate=lambda **kw: bool(kw.get(required_field, False)),
    )


def threshold_law(
    domain: str,
    name: str,
    description: str,
    metric_field: str,
    threshold: float,
    alert_field: str = "alert_surfaced",
) -> GovernanceLaw:
    """
    Create a threshold/drift alert law.

    Args:
        domain: Domain for the law
        name: Law name
        description: Law description
        metric_field: Field containing the metric value
        threshold: Maximum acceptable value
        alert_field: Field indicating if alert was surfaced

    Returns:
        A GovernanceLaw that checks threshold compliance

    Example:
        >>> law = threshold_law(
        ...     domain="quality",
        ...     name="Latency Alert",
        ...     description="Alert if latency > 200ms",
        ...     metric_field="latency_ms",
        ...     threshold=200.0,
        ... )
    """
    def predicate(**kw: Any) -> bool:
        value = kw.get(metric_field, 0.0)
        surfaced = kw.get(alert_field, True)
        if value > threshold:
            return bool(surfaced)
        return True

    return GovernanceLaw(
        schema=LawSchema.DRIFT_ALERT,
        domain=domain,
        name=name,
        description=description,
        predicate=predicate,
        metadata={"threshold": threshold, "metric_field": metric_field},
    )


__all__ = [
    # Enums
    "LawSchema",
    # Core types
    "GovernanceLaw",
    "LawVerificationResult",
    "LawVerificationReport",
    # Schema predicates
    "coherence_gate",
    "drift_alert",
    "ghost_preservation",
    "courage_preservation",
    "compression_honesty",
    # Verification
    "verify_law",
    "verify_laws",
    # Builder
    "LawBuilder",
    # Convenience
    "gate_law",
    "threshold_law",
]
