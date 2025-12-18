"""
Tests for TestOptimizationFlux.

Verifies:
1. State transitions (IDLE -> PROFILING -> ANALYZING -> RECOMMENDING -> IDLE)
2. Event processing (start, test_result, end)
3. Recommendation generation
4. CI integration helpers
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import AsyncIterator

import pytest

from testing.optimization import TestTier
from testing.optimization.flux import (
    OptimizationEvent,
    OptimizationState,
    TestEvent,
    TestOptimizationFlux,
    events_from_pytest_report,
)


async def collect_events(
    flux: TestOptimizationFlux,
    events: AsyncIterator[TestEvent],
) -> list[OptimizationEvent]:
    """Helper to collect all output events."""
    results: list[OptimizationEvent] = []
    async for event in flux.process(events):
        results.append(event)
    return results


async def events_from_list(events: list[TestEvent]) -> AsyncIterator[TestEvent]:
    """Convert list to async iterator."""
    for event in events:
        yield event


class TestOptimizationStateTransitions:
    """Tests for state machine transitions."""

    @pytest.mark.asyncio
    async def test_initial_state_is_idle(self) -> None:
        """Flux starts in IDLE state."""
        flux = TestOptimizationFlux()
        assert flux.state == OptimizationState.IDLE

    @pytest.mark.asyncio
    async def test_start_transitions_to_profiling(self) -> None:
        """Start event transitions to PROFILING."""
        flux = TestOptimizationFlux()

        events = [TestEvent(event_type="start")]
        await collect_events(flux, events_from_list(events))

        assert flux.state == OptimizationState.PROFILING

    @pytest.mark.asyncio
    async def test_end_transitions_back_to_idle(self) -> None:
        """End event transitions back to IDLE."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="end"),
        ]
        await collect_events(flux, events_from_list(events))

        assert flux.state == OptimizationState.IDLE

    @pytest.mark.asyncio
    async def test_full_lifecycle(self) -> None:
        """Complete lifecycle transitions correctly."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_foo", duration_s=0.1),
            TestEvent(event_type="end"),
        ]
        await collect_events(flux, events_from_list(events))

        # Should be back to IDLE
        assert flux.state == OptimizationState.IDLE


class TestEventProcessing:
    """Tests for event processing."""

    @pytest.mark.asyncio
    async def test_processes_test_results(self) -> None:
        """Records test profiles from results."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_foo", duration_s=0.1),
            TestEvent(event_type="test_result", test_id="test_bar", duration_s=0.5),
            TestEvent(event_type="end"),
        ]
        await collect_events(flux, events_from_list(events))

        assert len(flux.tracker.profiles) == 2
        assert "test_foo" in flux.tracker.profiles
        assert "test_bar" in flux.tracker.profiles

    @pytest.mark.asyncio
    async def test_emits_profile_events(self) -> None:
        """Emits profile events when enabled."""
        flux = TestOptimizationFlux(emit_profiles=True)

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_foo", duration_s=0.1),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        profile_events = [e for e in output if e.event_type == "profile"]
        assert len(profile_events) == 1
        assert profile_events[0].data["test_id"] == "test_foo"

    @pytest.mark.asyncio
    async def test_tracks_failures(self) -> None:
        """Tracks test failures."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(
                event_type="test_result",
                test_id="test_pass",
                duration_s=0.1,
                passed=True,
            ),
            TestEvent(
                event_type="test_result",
                test_id="test_fail",
                duration_s=0.1,
                passed=False,
            ),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        summary_events = [e for e in output if e.event_type == "summary"]
        assert len(summary_events) == 1
        assert summary_events[0].data["failure_count"] == 1


class TestRecommendations:
    """Tests for recommendation generation."""

    @pytest.mark.asyncio
    async def test_emits_recommendations(self) -> None:
        """Generates recommendations for expensive tests."""
        flux = TestOptimizationFlux(emit_recommendations=True)

        events = [
            TestEvent(event_type="start"),
            # Add an expensive test
            TestEvent(event_type="test_result", test_id="test_expensive", duration_s=45.0),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        rec_events = [e for e in output if e.event_type == "recommendation"]
        assert len(rec_events) > 0
        assert rec_events[0].data["action"] == "mark_slow"

    @pytest.mark.asyncio
    async def test_no_recommendations_for_fast_tests(self) -> None:
        """No recommendations for fast test suite."""
        flux = TestOptimizationFlux(emit_recommendations=True)

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_fast", duration_s=0.1),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        rec_events = [e for e in output if e.event_type == "recommendation"]
        assert len(rec_events) == 0


class TestSummary:
    """Tests for summary generation."""

    @pytest.mark.asyncio
    async def test_emits_summary(self) -> None:
        """Emits summary at end of session."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_foo", duration_s=0.1),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        summary_events = [e for e in output if e.event_type == "summary"]
        assert len(summary_events) == 1
        assert "total_tests" in summary_events[0].data
        assert summary_events[0].data["total_tests"] == 1

    @pytest.mark.asyncio
    async def test_summary_includes_tier_distribution(self) -> None:
        """Summary includes tier distribution."""
        flux = TestOptimizationFlux()

        events = [
            TestEvent(event_type="start"),
            TestEvent(event_type="test_result", test_id="test_instant", duration_s=0.05),
            TestEvent(event_type="test_result", test_id="test_fast", duration_s=0.3),
            TestEvent(event_type="end"),
        ]
        output = await collect_events(flux, events_from_list(events))

        summary_events = [e for e in output if e.event_type == "summary"]
        tier_dist = summary_events[0].data["tier_distribution"]

        assert tier_dist["instant"] == 1
        assert tier_dist["fast"] == 1


class TestInvoke:
    """Tests for discrete invoke interface."""

    @pytest.mark.asyncio
    async def test_invoke_single_event(self) -> None:
        """Invoke processes single event."""
        flux = TestOptimizationFlux()

        # Start session
        results = await flux.invoke(TestEvent(event_type="start"))
        assert len(results) == 1
        assert results[0].event_type == "session_start"

    @pytest.mark.asyncio
    async def test_invoke_test_result(self) -> None:
        """Invoke processes test result."""
        flux = TestOptimizationFlux(emit_profiles=True)

        # Start first
        await flux.invoke(TestEvent(event_type="start"))

        # Then test result
        results = await flux.invoke(
            TestEvent(event_type="test_result", test_id="test_foo", duration_s=0.1)
        )

        assert len(results) == 1
        assert results[0].event_type == "profile"


class TestCIIntegration:
    """Tests for CI integration helpers."""

    @pytest.mark.asyncio
    async def test_events_from_pytest_report_missing_file(self) -> None:
        """Returns empty when file doesn't exist."""
        events: list[TestEvent] = []
        async for event in events_from_pytest_report(Path("/nonexistent/report.json")):
            events.append(event)

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_events_from_pytest_report_valid(self) -> None:
        """Parses valid pytest JSON report."""
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report = {
                "tests": [
                    {
                        "nodeid": "test_foo.py::test_example",
                        "outcome": "passed",
                        "call": {"duration": 0.123},
                    },
                    {
                        "nodeid": "test_bar.py::test_fail",
                        "outcome": "failed",
                        "call": {"duration": 0.456},
                    },
                ]
            }
            json.dump(report, f)
            f.flush()

            events: list[TestEvent] = []
            async for event in events_from_pytest_report(Path(f.name)):
                events.append(event)

        # Should have: start, 2 results, end
        assert len(events) == 4

        start = events[0]
        assert start.event_type == "start"

        result1 = events[1]
        assert result1.event_type == "test_result"
        assert result1.test_id == "test_foo.py::test_example"
        assert result1.passed is True

        result2 = events[2]
        assert result2.passed is False

        end = events[3]
        assert end.event_type == "end"
