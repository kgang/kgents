"""
Tests for Morning Coffee Brain wiring.

Tests voice capture to Brain crystals and voice archaeology.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.liminal.coffee import CoffeeService, MorningVoice
from services.liminal.coffee.types import ChallengeLevel


class MockBrainPersistence:
    """Mock BrainPersistence for testing."""

    def __init__(self) -> None:
        self.captures: list[dict] = []
        self.capture = AsyncMock(side_effect=self._capture)
        self.search = AsyncMock(return_value=[])

    async def _capture(
        self,
        content: str,
        tags: list[str] | None = None,
        source_type: str = "capture",
        source_ref: str | None = None,
        metadata: dict | None = None,
    ) -> MagicMock:
        self.captures.append(
            {
                "content": content,
                "tags": tags or [],
                "source_type": source_type,
                "source_ref": source_ref,
                "metadata": metadata,
            }
        )
        result = MagicMock()
        result.crystal_id = "test-crystal-123"
        return result


class TestBrainIntegration:
    """Test Brain integration for voice captures."""

    @pytest.fixture
    def mock_brain(self) -> MockBrainPersistence:
        return MockBrainPersistence()

    @pytest.fixture
    def service_with_brain(self, mock_brain: MockBrainPersistence, tmp_path) -> CoffeeService:
        return CoffeeService(
            voice_store_path=tmp_path,
            brain_persistence=mock_brain,  # type: ignore
        )

    @pytest.fixture
    def service_without_brain(self, tmp_path) -> CoffeeService:
        return CoffeeService(
            voice_store_path=tmp_path,
            brain_persistence=None,
        )

    @pytest.mark.asyncio
    async def test_save_capture_stores_to_brain(
        self, service_with_brain: CoffeeService, mock_brain: MockBrainPersistence
    ) -> None:
        """save_capture should store voice to Brain when available."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship the feature",
            non_code_thought="Great coffee this morning",
            eye_catch=None,
            raw_feeling=None,
            chosen_challenge=None,
        )

        await service_with_brain.save_capture(voice)

        # Should have called capture
        assert len(mock_brain.captures) == 1
        capture = mock_brain.captures[0]

        # Check content
        assert "Ship the feature" in capture["content"]
        assert "Great coffee" in capture["content"]

        # Check tags
        assert "morning_coffee" in capture["tags"]
        assert "voice_anchor" in capture["tags"]
        assert "date:2025-12-21" in capture["tags"]

        # Check source type
        assert capture["source_type"] == "morning_coffee"

    @pytest.mark.asyncio
    async def test_save_capture_without_brain_succeeds(
        self, service_without_brain: CoffeeService, tmp_path
    ) -> None:
        """save_capture should work without Brain."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship it",
            non_code_thought=None,
            eye_catch=None,
            raw_feeling=None,
            chosen_challenge=None,
        )

        path = await service_without_brain.save_capture(voice)

        # Should save to file
        assert path.exists()

    @pytest.mark.asyncio
    async def test_brain_failure_doesnt_break_capture(self, tmp_path) -> None:
        """Brain failure should not break voice capture."""
        # Create a failing brain
        failing_brain = MagicMock()
        failing_brain.capture = AsyncMock(side_effect=Exception("Brain error"))

        service = CoffeeService(
            voice_store_path=tmp_path,
            brain_persistence=failing_brain,
        )

        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Ship it",
            non_code_thought=None,
            eye_catch=None,
            raw_feeling=None,
            chosen_challenge=None,
        )

        # Should not raise
        path = await service.save_capture(voice)
        assert path.exists()

    @pytest.mark.asyncio
    async def test_brain_capture_includes_chosen_challenge(
        self, service_with_brain: CoffeeService, mock_brain: MockBrainPersistence
    ) -> None:
        """Brain capture should include chosen challenge as tag."""
        voice = MorningVoice(
            captured_date=date(2025, 12, 21),
            success_criteria="Complete ASHC L0",
            non_code_thought=None,
            eye_catch=None,
            raw_feeling=None,
            chosen_challenge=ChallengeLevel.INTENSE,
        )

        await service_with_brain.save_capture(voice)

        capture = mock_brain.captures[0]
        assert "challenge:intense" in capture["tags"]


class TestVoiceArchaeology:
    """Test voice archaeology (pattern extraction from Brain)."""

    @pytest.fixture
    def mock_brain(self) -> MockBrainPersistence:
        return MockBrainPersistence()

    @pytest.fixture
    def service(self, mock_brain: MockBrainPersistence) -> CoffeeService:
        return CoffeeService(brain_persistence=mock_brain)  # type: ignore

    @pytest.mark.asyncio
    async def test_search_voice_archaeology(
        self, service: CoffeeService, mock_brain: MockBrainPersistence
    ) -> None:
        """Should search Brain for voice captures."""
        # Set up mock results
        mock_result = MagicMock()
        mock_result.crystal_id = "test-1"
        mock_result.content = "Morning goal: Ship feature"
        mock_result.similarity = 0.85
        mock_result.captured_at = "2025-12-21T08:00:00"
        mock_brain.search.return_value = [mock_result]

        results = await service.search_voice_archaeology("shipping features")

        mock_brain.search.assert_called_once()
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_without_brain_returns_empty(self) -> None:
        """Search without Brain should return empty list."""
        service = CoffeeService(brain_persistence=None)

        results = await service.search_voice_archaeology("anything")

        assert results == []

    @pytest.mark.asyncio
    async def test_get_voice_patterns_extracts_themes(
        self, service: CoffeeService, mock_brain: MockBrainPersistence
    ) -> None:
        """Should extract patterns from voice captures."""
        # Set up mock results with repeated themes
        mock_results = []
        for i in range(5):
            r = MagicMock()
            r.content = "Today's goal: understanding the architecture"
            mock_results.append(r)

        mock_brain.search.return_value = mock_results

        patterns = await service.get_voice_patterns_from_brain()

        assert patterns["available"] is True
        assert "understanding" in patterns.get("common_themes", [])

    @pytest.mark.asyncio
    async def test_get_voice_patterns_without_brain(self) -> None:
        """Patterns without Brain should indicate unavailable."""
        service = CoffeeService(brain_persistence=None)

        patterns = await service.get_voice_patterns_from_brain()

        assert patterns["available"] is False
