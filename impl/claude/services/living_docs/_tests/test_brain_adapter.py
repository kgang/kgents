"""
Tests for HydrationBrainAdapter: Checkpoint 0.2 verification.

User Journey:
    Task description → Brain semantic search → Enhanced teaching moments

Teaching:
    gotcha: Tests use mocks for Brain to avoid database dependency.
            Integration tests would require full Brain setup.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..brain_adapter import (
    ASHCEvidence,
    HydrationBrainAdapter,
    ScoredTeachingResult,
    get_hydration_brain_adapter,
    reset_hydration_brain_adapter,
    set_hydration_brain_adapter,
)


@dataclass
class MockSearchResult:
    """Mock Brain SearchResult for testing."""

    crystal_id: str
    content: str
    summary: str
    similarity: float
    captured_at: str = "2025-12-21T00:00:00Z"
    is_stale: bool = False


@pytest.fixture
def mock_brain() -> MagicMock:
    """Create a mock BrainPersistence."""
    brain = MagicMock()
    brain.search = AsyncMock(return_value=[])
    return brain


@pytest.fixture
def adapter_without_brain() -> HydrationBrainAdapter:
    """Adapter without Brain (fallback mode)."""
    return HydrationBrainAdapter(brain=None)


@pytest.fixture
def adapter_with_brain(mock_brain: MagicMock) -> HydrationBrainAdapter:
    """Adapter with mocked Brain."""
    return HydrationBrainAdapter(brain=mock_brain)


class TestAdapterAvailability:
    """Test adapter availability detection."""

    def test_not_available_without_brain(
        self, adapter_without_brain: HydrationBrainAdapter
    ) -> None:
        """Adapter reports unavailable without Brain."""
        assert adapter_without_brain.is_available is False

    def test_available_with_brain(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Adapter reports available with Brain."""
        assert adapter_with_brain.is_available is True


class TestSemanticTeaching:
    """Test semantic teaching moment retrieval."""

    @pytest.mark.asyncio
    async def test_returns_empty_without_brain(
        self, adapter_without_brain: HydrationBrainAdapter
    ) -> None:
        """Returns empty list when Brain is unavailable."""
        results = await adapter_without_brain.find_semantic_teaching("verification")
        assert results == []

    @pytest.mark.asyncio
    async def test_returns_teaching_from_brain_results(
        self, adapter_with_brain: HydrationBrainAdapter, mock_brain: MagicMock
    ) -> None:
        """Converts Brain SearchResults to TeachingResults."""
        mock_brain.search.return_value = [
            MockSearchResult(
                crystal_id="crystal-123",
                content="gotcha: Always check for None before accessing",
                summary="gotcha: Always check for None...",
                similarity=0.8,
            )
        ]

        results = await adapter_with_brain.find_semantic_teaching("null checks")

        assert len(results) == 1
        assert "None" in results[0].moment.insight
        assert results[0].score == 0.8

    @pytest.mark.asyncio
    async def test_filters_by_similarity_threshold(
        self, adapter_with_brain: HydrationBrainAdapter, mock_brain: MagicMock
    ) -> None:
        """Low similarity results are filtered out."""
        mock_brain.search.return_value = [
            MockSearchResult(
                crystal_id="crystal-high",
                content="lesson: This is highly relevant",
                summary="lesson: This is highly relevant",
                similarity=0.9,
            ),
            MockSearchResult(
                crystal_id="crystal-low",
                content="lesson: This is barely relevant",
                summary="lesson: This is barely relevant",
                similarity=0.1,  # Below threshold
            ),
        ]

        results = await adapter_with_brain.find_semantic_teaching("relevant", min_similarity=0.3)

        assert len(results) == 1
        assert results[0].moment.insight == "This is highly relevant"

    @pytest.mark.asyncio
    async def test_respects_limit(
        self, adapter_with_brain: HydrationBrainAdapter, mock_brain: MagicMock
    ) -> None:
        """Returns at most limit results."""
        mock_brain.search.return_value = [
            MockSearchResult(
                crystal_id=f"crystal-{i}",
                content=f"lesson: Teaching moment {i}",
                summary=f"lesson: Teaching moment {i}",
                similarity=0.8,
            )
            for i in range(10)
        ]

        results = await adapter_with_brain.find_semantic_teaching("test", limit=3)

        assert len(results) == 3


class TestInsightExtraction:
    """Test insight extraction from content."""

    def test_extracts_gotcha_pattern(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Extracts insight from 'gotcha:' pattern."""
        result = MockSearchResult(
            crystal_id="test",
            content="gotcha: Don't use global variables in async code",
            summary="gotcha: Don't use...",
            similarity=0.8,
        )

        teaching = adapter_with_brain._convert_to_teaching(result)
        assert teaching is not None
        assert "Don't use global variables" in teaching.moment.insight

    def test_extracts_lesson_pattern(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Extracts insight from 'lesson:' pattern."""
        result = MockSearchResult(
            crystal_id="test",
            content="lesson: Tests should be isolated",
            summary="lesson: Tests...",
            similarity=0.7,
        )

        teaching = adapter_with_brain._convert_to_teaching(result)
        assert teaching is not None
        assert "Tests should be isolated" in teaching.moment.insight

    def test_extracts_bullet_point(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Extracts insight from bullet points."""
        result = MockSearchResult(
            crystal_id="test",
            content="- Use dependency injection for testability",
            summary="- Use dependency...",
            similarity=0.6,
        )

        teaching = adapter_with_brain._convert_to_teaching(result)
        assert teaching is not None
        assert "dependency injection" in teaching.moment.insight

    def test_fallback_to_first_line(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Falls back to first line if no pattern found."""
        result = MockSearchResult(
            crystal_id="test",
            content="This is important to remember\nMore details here",
            summary="This is important...",
            similarity=0.5,
        )

        teaching = adapter_with_brain._convert_to_teaching(result)
        assert teaching is not None
        assert "This is important to remember" in teaching.moment.insight


class TestSeverityInference:
    """Test severity inference from content."""

    def test_infers_critical_severity(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Critical keywords yield critical severity."""
        content = "Never use eval() - it will break security"
        severity = adapter_with_brain._infer_severity(content)
        assert severity == "critical"

    def test_infers_warning_severity(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """Warning keywords yield warning severity."""
        content = "Be careful with mutable default arguments"
        severity = adapter_with_brain._infer_severity(content)
        assert severity == "warning"

    def test_infers_info_severity(self, adapter_with_brain: HydrationBrainAdapter) -> None:
        """No keywords yield info severity."""
        content = "Use descriptive variable names"
        severity = adapter_with_brain._infer_severity(content)
        assert severity == "info"


class TestPriorEvidence:
    """Test ASHC prior evidence retrieval (stub for Phase 2)."""

    @pytest.mark.asyncio
    async def test_returns_empty_until_phase_2(
        self, adapter_with_brain: HydrationBrainAdapter
    ) -> None:
        """Prior evidence returns empty until Phase 2 implementation."""
        evidence = await adapter_with_brain.find_prior_evidence("verification")
        assert evidence == []


class TestSemanticHydrate:
    """Test combined semantic hydration."""

    @pytest.mark.asyncio
    async def test_returns_combined_context(
        self, adapter_with_brain: HydrationBrainAdapter, mock_brain: MagicMock
    ) -> None:
        """Returns combined teaching and evidence."""
        mock_brain.search.return_value = [
            MockSearchResult(
                crystal_id="crystal-1",
                content="gotcha: Check boundaries",
                summary="gotcha: Check...",
                similarity=0.9,
            )
        ]

        result = await adapter_with_brain.semantic_hydrate("boundary checking")

        assert result["brain_available"] is True
        assert len(result["semantic_teaching"]) == 1
        assert result["prior_evidence"] == []  # Empty until Phase 2

    @pytest.mark.asyncio
    async def test_returns_unavailable_without_brain(
        self, adapter_without_brain: HydrationBrainAdapter
    ) -> None:
        """Returns unavailable status without Brain."""
        result = await adapter_without_brain.semantic_hydrate("test")

        assert result["brain_available"] is False
        assert result["semantic_teaching"] == []


class TestASHCEvidence:
    """Test ASHCEvidence dataclass."""

    def test_to_dict_serializes(self) -> None:
        """ASHCEvidence serializes to dict."""
        evidence = ASHCEvidence(
            task_pattern="verification tests",
            run_count=47,
            pass_rate=0.94,
            diversity_score=0.72,
            last_run="2025-12-21",
            causal_insights=["Type hints improve pass rate by 8%"],
        )

        data = evidence.to_dict()

        assert data["task_pattern"] == "verification tests"
        assert data["run_count"] == 47
        assert data["pass_rate"] == 0.94
        assert len(data["causal_insights"]) == 1


class TestFactory:
    """Test global factory functions."""

    def test_get_returns_same_instance(self) -> None:
        """get_hydration_brain_adapter returns singleton."""
        reset_hydration_brain_adapter()
        a1 = get_hydration_brain_adapter()
        a2 = get_hydration_brain_adapter()
        assert a1 is a2
        reset_hydration_brain_adapter()

    def test_set_replaces_instance(self) -> None:
        """set_hydration_brain_adapter replaces singleton."""
        reset_hydration_brain_adapter()
        custom = HydrationBrainAdapter()
        set_hydration_brain_adapter(custom)
        assert get_hydration_brain_adapter() is custom
        reset_hydration_brain_adapter()
