"""
TestOptimizationFlux: Self-Improving Test Suite Agent.

A FluxAgent that continuously optimizes the test suite:
- Listens to CI signals (test events)
- Profiles test execution
- Emits optimization recommendations

Polynomial structure:
    S = {IDLE, PROFILING, ANALYZING, RECOMMENDING}
    E(s) = test events at each state

Philosophy: "The test suite that watches itself, improves itself."

AGENTESE: self.test.optimization.flux
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, AsyncIterator

from testing.optimization import (
    OptimizationRecommendation,
    RefinementTracker,
    TestProfile,
    TestTier,
    recommend_optimizations,
)
from testing.optimization.partition import optimal_plan
from testing.optimization.redundancy import (
    RedundancyReport,
    TestCoverage,
    add_redundancy_recommendations,
    detect_redundancy,
)


class OptimizationState(Enum):
    """States of the optimization flux polynomial."""

    IDLE = auto()  # Waiting for test run to start
    PROFILING = auto()  # Recording test timing
    ANALYZING = auto()  # Computing recommendations
    RECOMMENDING = auto()  # Emitting recommendations


@dataclass
class TestEvent:
    """Event from CI/test runner."""

    event_type: str  # "start", "test_result", "end"
    test_id: str | None = None
    duration_s: float | None = None
    passed: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OptimizationEvent:
    """Event emitted by optimization flux."""

    event_type: str  # "profile", "recommendation", "summary"
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TestOptimizationFlux:
    """
    Continuous test optimization agent.

    Polynomial structure:
        S = {IDLE, PROFILING, ANALYZING, RECOMMENDING}
        E(s) = test events at each state

    Listens to CI signals, profiles tests, emits recommendations.
    Can be integrated with FluxAgent for full streaming support.

    Example:
        >>> flux = TestOptimizationFlux()
        >>> async for event in flux.process(test_events):
        ...     if event.event_type == "recommendation":
        ...         apply_optimization(event.data)
    """

    # State
    state: OptimizationState = field(default=OptimizationState.IDLE)
    tracker: RefinementTracker = field(default_factory=RefinementTracker)

    # Configuration
    emit_profiles: bool = True
    emit_recommendations: bool = True
    recommendation_threshold: float = 0.9  # For redundancy detection

    # Session tracking
    _session_start: datetime | None = field(default=None, init=False)
    _test_count: int = field(default=0, init=False)
    _failure_count: int = field(default=0, init=False)

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "TestOptimizationFlux"

    async def process(
        self,
        events: AsyncIterator[TestEvent],
    ) -> AsyncIterator[OptimizationEvent]:
        """
        Process test events and emit optimization events.

        This is the main entry point for the flux.

        Args:
            events: Stream of TestEvent from CI

        Yields:
            OptimizationEvent for profiles and recommendations
        """
        async for event in events:
            async for output in self._handle_event(event):
                yield output

    async def _handle_event(
        self,
        event: TestEvent,
    ) -> AsyncIterator[OptimizationEvent]:
        """Handle a single test event based on current state."""
        match event.event_type:
            case "start":
                async for e in self._handle_start(event):
                    yield e

            case "test_result":
                async for e in self._handle_test_result(event):
                    yield e

            case "end":
                async for e in self._handle_end(event):
                    yield e

    async def _handle_start(
        self,
        event: TestEvent,
    ) -> AsyncIterator[OptimizationEvent]:
        """Handle CI session start."""
        self.state = OptimizationState.PROFILING
        self._session_start = event.timestamp
        self._test_count = 0
        self._failure_count = 0

        yield OptimizationEvent(
            event_type="session_start",
            data={"timestamp": event.timestamp.isoformat()},
        )

    async def _handle_test_result(
        self,
        event: TestEvent,
    ) -> AsyncIterator[OptimizationEvent]:
        """Handle individual test result."""
        if self.state != OptimizationState.PROFILING:
            return

        if event.test_id and event.duration_s is not None:
            profile = self.tracker.record_profile(event.test_id, event.duration_s)
            self._test_count += 1

            if not event.passed:
                self._failure_count += 1

            if self.emit_profiles:
                yield OptimizationEvent(
                    event_type="profile",
                    data={
                        "test_id": profile.test_id,
                        "duration_ms": profile.duration_ms,
                        "tier": profile.tier.value,
                        "passed": event.passed,
                    },
                )

    async def _handle_end(
        self,
        event: TestEvent,
    ) -> AsyncIterator[OptimizationEvent]:
        """Handle CI session end - generate recommendations."""
        self.state = OptimizationState.ANALYZING

        # Generate summary
        summary = self.tracker.summary()
        yield OptimizationEvent(
            event_type="summary",
            data={
                "total_tests": summary["total_tests"],
                "tier_distribution": summary["tier_distribution"],
                "failure_count": self._failure_count,
                "expensive_tests": len(summary["expensive_tests"]),
            },
        )

        if self.emit_recommendations:
            self.state = OptimizationState.RECOMMENDING

            # Get recommendations
            recommendations = recommend_optimizations(self.tracker)

            for rec in recommendations:
                yield OptimizationEvent(
                    event_type="recommendation",
                    data={
                        "test_id": rec.test_id,
                        "action": rec.action,
                        "rationale": rec.rationale,
                        "estimated_savings_ms": rec.estimated_savings_ms,
                    },
                )

        # Return to idle
        self.state = OptimizationState.IDLE

    async def invoke(self, event: TestEvent) -> list[OptimizationEvent]:
        """
        Discrete invocation for single event processing.

        Compatible with Agent[TestEvent, list[OptimizationEvent]] interface.
        """
        results: list[OptimizationEvent] = []
        async for output in self._handle_event(event):
            results.append(output)
        return results


# =============================================================================
# CI Integration Helpers
# =============================================================================


async def events_from_pytest_report(
    report_path: Path,
) -> AsyncIterator[TestEvent]:
    """
    Generate TestEvents from pytest JSON report.

    Requires pytest-json-report plugin:
        pytest --json-report --json-report-file=report.json
    """
    import json

    if not report_path.exists():
        return

    with report_path.open() as f:
        report = json.load(f)

    # Emit start
    yield TestEvent(event_type="start")

    # Emit test results
    for test in report.get("tests", []):
        nodeid = test.get("nodeid", "unknown")
        duration = test.get("call", {}).get("duration", 0)
        passed = test.get("outcome") == "passed"

        yield TestEvent(
            event_type="test_result",
            test_id=nodeid,
            duration_s=duration,
            passed=passed,
        )

    # Emit end
    yield TestEvent(event_type="end")


async def watch_pytest_output() -> AsyncIterator[TestEvent]:
    """
    Watch pytest output in real-time.

    This is a generator that would integrate with pytest's
    live output. For now, it's a placeholder.

    TODO: Implement proper pytest plugin integration
    """
    yield TestEvent(event_type="start")
    # In real implementation, this would watch pytest's live output
    yield TestEvent(event_type="end")


# =============================================================================
# Integration with FluxAgent
# =============================================================================


def create_optimization_flux_agent() -> Any:
    """
    Create a FluxAgent wrapping TestOptimizationFlux.

    Returns a FluxAgent that can be composed into pipelines.

    Example:
        >>> flux = create_optimization_flux_agent()
        >>> async for event in flux.start(test_events):
        ...     process(event)
    """
    # Import here to avoid circular dependency
    try:
        from agents.a.quick import FunctionAgent
        from agents.flux import FluxAgent
    except ImportError:
        # FluxAgent not available - return the raw flux
        return TestOptimizationFlux()

    inner_flux = TestOptimizationFlux()

    # Wrap in FunctionAgent for FluxAgent compatibility
    async def process_event(event: TestEvent) -> list[OptimizationEvent]:
        return await inner_flux.invoke(event)

    agent = FunctionAgent(
        fn=process_event,
        agent_name="TestOptimizationAgent",
    )

    return FluxAgent(inner=agent)


__all__ = [
    "OptimizationState",
    "TestEvent",
    "OptimizationEvent",
    "TestOptimizationFlux",
    "events_from_pytest_report",
    "watch_pytest_output",
    "create_optimization_flux_agent",
]
