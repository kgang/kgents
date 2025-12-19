"""
Sentinel testing infrastructure for CI safety.

Philosophy: The Sentinel is the last line of defense before CI.

This package provides:
- Signal aggregation for push readiness evaluation
- Isolation morphism for test registry state
- Degradation tiers for graceful fallback

See plans/multi-agent-ci-safety-strategy.md for the full strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence


# =============================================================================
# Signal Aggregation (Section 4)
# =============================================================================


class SignalKind(Enum):
    """Categories of CI signals."""

    LINT = "lint"
    TYPECHECK = "typecheck"
    TEST = "test"
    CONTRACT = "contract"


@dataclass(frozen=True)
class CISignal:
    """
    A single CI signal with pass/fail status and optional metadata.

    Represents one check in the push readiness evaluation.
    """

    kind: SignalKind
    passed: bool
    blocking: bool = True
    reason: str = ""
    duration_ms: float = 0.0


@dataclass(frozen=True)
class PushReadiness:
    """
    Aggregated push readiness evaluation.

    Combines multiple CI signals into a single go/no-go decision
    with confidence level and blocking reasons.
    """

    ready: bool
    confidence: float  # 0.0 to 1.0
    blocking_reasons: tuple[str, ...]
    warning_reasons: tuple[str, ...]
    signals: tuple[CISignal, ...]

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        status = "READY" if self.ready else "NOT READY"
        confidence_pct = int(self.confidence * 100)
        return f"{status} ({confidence_pct}% confidence)"


def evaluate_push_readiness(signals: Sequence[CISignal]) -> PushReadiness:
    """
    Evaluate push readiness from a collection of CI signals.

    Rules:
    - All blocking signals must pass for ready=True
    - Confidence is the ratio of passed blocking signals
    - Non-blocking failures are warnings

    Args:
        signals: Collection of CISignal objects from various checks

    Returns:
        PushReadiness with aggregated decision
    """
    if not signals:
        return PushReadiness(
            ready=True,
            confidence=0.0,
            blocking_reasons=(),
            warning_reasons=("No signals to evaluate",),
            signals=(),
        )

    blocking_signals = [s for s in signals if s.blocking]
    non_blocking_signals = [s for s in signals if not s.blocking]

    blocking_passed = [s for s in blocking_signals if s.passed]
    blocking_failed = [s for s in blocking_signals if not s.passed]
    non_blocking_failed = [s for s in non_blocking_signals if not s.passed]

    # Ready only if all blocking signals pass
    ready = len(blocking_failed) == 0

    # Confidence based on blocking signals
    if blocking_signals:
        confidence = len(blocking_passed) / len(blocking_signals)
    else:
        confidence = 1.0  # No blocking signals = 100% confident

    # Collect reasons
    blocking_reasons = tuple(
        s.reason if s.reason else f"{s.kind.value} failed" for s in blocking_failed
    )
    warning_reasons = tuple(
        s.reason if s.reason else f"{s.kind.value} failed (non-blocking)"
        for s in non_blocking_failed
    )

    return PushReadiness(
        ready=ready,
        confidence=confidence,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        signals=tuple(signals),
    )


# =============================================================================
# Degradation Tiers (Section 8)
# =============================================================================


class DegradationTier(Enum):
    """CI execution tiers with different check levels."""

    FULL = "full"  # All checks: lint, types, tests, contracts
    REDUCED = "reduced"  # Core checks: lint, types, tests
    MINIMAL = "minimal"  # Fast checks: lint, types only
    EMERGENCY = "emergency"  # Skip all but lint


@dataclass(frozen=True)
class DegradationState:
    """
    Current degradation state with reason and available checks.

    The system degrades gracefully when resources are constrained:
    - Network failures → skip contract sync
    - Database unavailable → skip persistence tests
    - Time pressure → skip slow tests
    """

    tier: DegradationTier
    reason: str
    skipped_checks: tuple[str, ...]

    @property
    def checks_available(self) -> tuple[str, ...]:
        """Return checks available at this tier."""
        all_checks = ("lint", "typecheck", "test", "contract", "slow_test", "e2e")
        available: list[str] = []

        if self.tier == DegradationTier.FULL:
            available = list(all_checks)
        elif self.tier == DegradationTier.REDUCED:
            available = ["lint", "typecheck", "test"]
        elif self.tier == DegradationTier.MINIMAL:
            available = ["lint", "typecheck"]
        elif self.tier == DegradationTier.EMERGENCY:
            available = ["lint"]

        return tuple(available)


def determine_degradation_tier(
    *,
    network_available: bool = True,
    database_available: bool = True,
    time_budget_seconds: float = float("inf"),
) -> DegradationState:
    """
    Determine appropriate degradation tier based on available resources.

    Args:
        network_available: Can reach external services
        database_available: Can connect to test database
        time_budget_seconds: Maximum time for checks

    Returns:
        DegradationState with tier and skipped checks
    """
    skipped: list[str] = []

    # Emergency: very tight time budget
    if time_budget_seconds < 30:
        return DegradationState(
            tier=DegradationTier.EMERGENCY,
            reason=f"Time budget too tight: {time_budget_seconds}s",
            skipped_checks=("typecheck", "test", "contract", "slow_test", "e2e"),
        )

    # Minimal: moderate time pressure
    if time_budget_seconds < 120:
        return DegradationState(
            tier=DegradationTier.MINIMAL,
            reason=f"Limited time budget: {time_budget_seconds}s",
            skipped_checks=("test", "contract", "slow_test", "e2e"),
        )

    # Check for reduced tier conditions
    if not network_available:
        skipped.append("contract")
        skipped.append("e2e")

    if not database_available:
        skipped.append("slow_test")

    if skipped:
        return DegradationState(
            tier=DegradationTier.REDUCED,
            reason=f"Resources unavailable: {', '.join(skipped)}",
            skipped_checks=tuple(skipped),
        )

    # Full: all resources available
    return DegradationState(
        tier=DegradationTier.FULL,
        reason="All resources available",
        skipped_checks=(),
    )


# =============================================================================
# Isolation Morphism (Section 6)
# =============================================================================


@dataclass
class RegistrySnapshot:
    """
    Snapshot of global registry state for isolation testing.

    Used to verify that tests don't leak state across runs.
    The isolation morphism: TestState → CleanState → TestState
    should preserve the original state.
    """

    operad_count: int
    node_count: int
    fixture_count: int
    extra_data: dict[str, int]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegistrySnapshot):
            return NotImplemented
        return (
            self.operad_count == other.operad_count
            and self.node_count == other.node_count
            and self.fixture_count == other.fixture_count
            and self.extra_data == other.extra_data
        )


def capture_registry_snapshot() -> RegistrySnapshot:
    """
    Capture current state of all global registries.

    Used as the basis for isolation verification.
    """
    operad_count = 0
    node_count = 0

    # Count operads
    try:
        from agents.operad.registry import OperadRegistry  # type: ignore[import-untyped]

        operad_count = len(OperadRegistry._entries)
    except (ImportError, AttributeError):
        pass

    # Count AGENTESE nodes
    try:
        from protocols.agentese.registry import get_node_registry

        registry = get_node_registry()
        node_count = len(registry._nodes) if hasattr(registry, "_nodes") else 0
    except (ImportError, AttributeError):
        pass

    return RegistrySnapshot(
        operad_count=operad_count,
        node_count=node_count,
        fixture_count=0,  # Reserved for future use
        extra_data={},
    )


def verify_isolation(before: RegistrySnapshot, after: RegistrySnapshot) -> bool:
    """
    Verify that registry state was preserved across test execution.

    This is the core isolation invariant:
    snapshot_before == snapshot_after

    Returns:
        True if isolation was maintained, False if state leaked
    """
    return before == after


__all__ = [
    # Signal Aggregation
    "CISignal",
    "SignalKind",
    "PushReadiness",
    "evaluate_push_readiness",
    # Degradation
    "DegradationTier",
    "DegradationState",
    "determine_degradation_tier",
    # Isolation
    "RegistrySnapshot",
    "capture_registry_snapshot",
    "verify_isolation",
]
