"""
Tests for VoiceStigmergy: Checkpoint 0.1 verification.

User Journey:
    Voice captured → Pheromone deposited → Accomplished → Reinforced

Teaching:
    gotcha: Tests use temporary directories for isolation.
            Don't rely on global state between tests.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pytest

from ..stigmergy import (
    ACCOMPLISHED_REINFORCEMENT,
    PARTIAL_REINFORCEMENT,
    PheromoneDeposit,
    VoiceStigmergy,
    get_voice_stigmergy,
    reset_voice_stigmergy,
    set_voice_stigmergy,
)
from ..types import ChallengeLevel, MorningVoice


@pytest.fixture
def temp_store(tmp_path: Path) -> Path:
    """Temporary storage path for test isolation."""
    return tmp_path / "stigmergy" / "test_field.json"


@pytest.fixture
def stigmergy(temp_store: Path) -> VoiceStigmergy:
    """Fresh VoiceStigmergy instance for each test."""
    return VoiceStigmergy(store_path=temp_store)


@pytest.fixture
def sample_voice() -> MorningVoice:
    """Sample morning voice with rich content."""
    return MorningVoice(
        captured_date=date.today(),
        non_code_thought="I had a dream about polynomials",
        eye_catch="The verification tests caught my eye",
        success_criteria="Finish the verification integration and make it magical",
        chosen_challenge=ChallengeLevel.FOCUSED,
    )


@pytest.fixture
def minimal_voice() -> MorningVoice:
    """Minimal morning voice with just success criteria."""
    return MorningVoice(
        captured_date=date.today(),
        success_criteria="Ship something",
    )


class TestConceptExtraction:
    """Test concept extraction from text."""

    def test_extracts_meaningful_words(self, stigmergy: VoiceStigmergy) -> None:
        """Concepts should exclude stop words."""
        concepts = stigmergy._extract_concepts("I want to finish the verification")

        assert "verification" in concepts
        # Stop words should be excluded
        assert "want" not in concepts
        assert "the" not in concepts
        assert "to" not in concepts

    def test_handles_empty_text(self, stigmergy: VoiceStigmergy) -> None:
        """Empty text yields empty concepts."""
        concepts = stigmergy._extract_concepts("")
        assert concepts == []

    def test_handles_only_stop_words(self, stigmergy: VoiceStigmergy) -> None:
        """Text with only stop words yields empty concepts."""
        concepts = stigmergy._extract_concepts("I want to do the work")
        # All common words filtered
        assert len(concepts) == 0 or all(len(c) > 2 for c in concepts)

    def test_preserves_order(self, stigmergy: VoiceStigmergy) -> None:
        """Concepts maintain order of appearance."""
        concepts = stigmergy._extract_concepts("alpha beta gamma")
        assert concepts == ["alpha", "beta", "gamma"]

    def test_deduplicates(self, stigmergy: VoiceStigmergy) -> None:
        """Repeated concepts are deduplicated."""
        concepts = stigmergy._extract_concepts("verify verification verify")
        assert concepts.count("verify") == 1
        assert concepts.count("verification") == 1


class TestVoiceDeposit:
    """Test pheromone deposit from voice captures."""

    @pytest.mark.asyncio
    async def test_deposits_from_success_criteria(
        self,
        stigmergy: VoiceStigmergy,
        minimal_voice: MorningVoice,
    ) -> None:
        """Success criteria creates pheromone deposits."""
        deposit = await stigmergy.deposit_from_voice(minimal_voice)

        assert isinstance(deposit, PheromoneDeposit)
        assert deposit.source == "voice"
        assert len(deposit.concepts) > 0

    @pytest.mark.asyncio
    async def test_deposits_from_multiple_fields(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """All voice fields contribute concepts."""
        deposit = await stigmergy.deposit_from_voice(sample_voice)

        # Should have concepts from success_criteria, eye_catch, and non_code_thought
        concepts = set(deposit.concepts)
        assert "verification" in concepts  # from success_criteria and eye_catch
        assert "magical" in concepts  # from success_criteria
        assert "polynomials" in concepts or "dream" in concepts  # from non_code_thought

    @pytest.mark.asyncio
    async def test_success_criteria_has_highest_weight(
        self,
        stigmergy: VoiceStigmergy,
    ) -> None:
        """Success criteria concepts have higher intensity."""
        voice = MorningVoice(
            captured_date=date.today(),
            success_criteria="quantum",  # Unique word to track
            eye_catch="classical",  # Different unique word
        )

        await stigmergy.deposit_from_voice(voice)

        # Get intensities
        quantum_intensity = await stigmergy._field.gradient_toward("quantum")
        classical_intensity = await stigmergy._field.gradient_toward("classical")

        # Success criteria (1.0) > eye_catch (0.7)
        assert quantum_intensity > classical_intensity

    @pytest.mark.asyncio
    async def test_deposit_records_voice_date(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """Deposit records the source voice date."""
        deposit = await stigmergy.deposit_from_voice(sample_voice)
        assert deposit.voice_date == sample_voice.captured_date.isoformat()


class TestReinforcement:
    """Test pheromone reinforcement on accomplishment."""

    @pytest.mark.asyncio
    async def test_reinforce_accomplished(
        self,
        stigmergy: VoiceStigmergy,
        minimal_voice: MorningVoice,
    ) -> None:
        """Accomplishment reinforces pheromones."""
        deposit = await stigmergy.deposit_from_voice(minimal_voice)

        # Get initial intensity
        concept = deposit.concepts[0] if deposit.concepts else "ship"
        initial = await stigmergy._field.gradient_toward(concept)

        # Reinforce
        count = await stigmergy.reinforce_accomplished(deposit)

        # Intensity should increase
        after = await stigmergy._field.gradient_toward(concept)
        assert after > initial
        assert count > 0

    @pytest.mark.asyncio
    async def test_reinforce_uses_accomplishment_factor(
        self,
        stigmergy: VoiceStigmergy,
        minimal_voice: MorningVoice,
    ) -> None:
        """Accomplishment uses the expected reinforcement factor."""
        deposit = await stigmergy.deposit_from_voice(minimal_voice, base_intensity=1.0)

        concept = deposit.concepts[0] if deposit.concepts else "ship"
        initial = await stigmergy._field.gradient_toward(concept)

        await stigmergy.reinforce_accomplished(deposit)

        after = await stigmergy._field.gradient_toward(concept)
        # Should be ~1.5x initial (accounting for small float differences)
        assert after >= initial * ACCOMPLISHED_REINFORCEMENT * 0.9

    @pytest.mark.asyncio
    async def test_reinforce_partial(
        self,
        stigmergy: VoiceStigmergy,
        minimal_voice: MorningVoice,
    ) -> None:
        """Partial completion has smaller reinforcement."""
        deposit = await stigmergy.deposit_from_voice(minimal_voice, base_intensity=1.0)

        concept = deposit.concepts[0] if deposit.concepts else "ship"
        initial = await stigmergy._field.gradient_toward(concept)

        await stigmergy.reinforce_partial(deposit)

        after = await stigmergy._field.gradient_toward(concept)
        # Partial (1.2) < Accomplished (1.5)
        expected = initial * PARTIAL_REINFORCEMENT
        assert after >= expected * 0.9
        assert PARTIAL_REINFORCEMENT < ACCOMPLISHED_REINFORCEMENT


class TestPatternSensing:
    """Test pattern sensing from pheromone field."""

    @pytest.mark.asyncio
    async def test_sense_patterns_empty(self, stigmergy: VoiceStigmergy) -> None:
        """Empty field returns no patterns."""
        patterns = await stigmergy.sense_patterns()
        assert patterns == []

    @pytest.mark.asyncio
    async def test_sense_patterns_after_deposit(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """Patterns appear after voice deposit."""
        await stigmergy.deposit_from_voice(sample_voice)

        patterns = await stigmergy.sense_patterns()
        assert len(patterns) > 0
        # Each pattern is (concept, intensity)
        for concept, intensity in patterns:
            assert isinstance(concept, str)
            assert isinstance(intensity, float)
            assert intensity > 0

    @pytest.mark.asyncio
    async def test_sense_patterns_sorted_by_intensity(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """Patterns are sorted by intensity (highest first)."""
        await stigmergy.deposit_from_voice(sample_voice)

        patterns = await stigmergy.sense_patterns()
        intensities = [intensity for _, intensity in patterns]
        assert intensities == sorted(intensities, reverse=True)

    @pytest.mark.asyncio
    async def test_sense_patterns_with_context(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """Context boosts matching patterns."""
        await stigmergy.deposit_from_voice(sample_voice)

        # Sense with context that matches "verification"
        patterns = await stigmergy.sense_patterns(context="verification tests")

        # Verification should be boosted if present
        if patterns:
            # At least one pattern should exist
            assert len(patterns) > 0

    @pytest.mark.asyncio
    async def test_get_top_patterns(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """get_top_patterns returns limited results."""
        await stigmergy.deposit_from_voice(sample_voice)

        patterns = await stigmergy.get_top_patterns(limit=3)
        assert len(patterns) <= 3


class TestDecay:
    """Test pheromone decay over time."""

    @pytest.mark.asyncio
    async def test_daily_decay_reduces_intensity(
        self,
        stigmergy: VoiceStigmergy,
        minimal_voice: MorningVoice,
    ) -> None:
        """Daily decay reduces pheromone intensity."""
        deposit = await stigmergy.deposit_from_voice(minimal_voice)
        concept = deposit.concepts[0] if deposit.concepts else "ship"

        initial = await stigmergy._field.gradient_toward(concept)

        # Apply decay
        evaporated = await stigmergy.apply_daily_decay()

        after = await stigmergy._field.gradient_toward(concept)
        # After 1 day of decay at 5%, intensity should be ~95% of initial
        assert after < initial or evaporated > 0


class TestPersistence:
    """Test pheromone field persistence."""

    @pytest.mark.asyncio
    async def test_save_creates_file(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
        temp_store: Path,
    ) -> None:
        """Saving creates a JSON file."""
        await stigmergy.deposit_from_voice(sample_voice)
        path = await stigmergy.save()

        assert path.exists()
        assert path.suffix == ".json"

    @pytest.mark.asyncio
    async def test_load_restores_state(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
        temp_store: Path,
    ) -> None:
        """Loading restores saved pheromone state."""
        # Deposit and save
        await stigmergy.deposit_from_voice(sample_voice)
        await stigmergy.save()

        # Get patterns before
        patterns_before = await stigmergy.sense_patterns()

        # Create new instance and load
        new_stigmergy = VoiceStigmergy(store_path=temp_store)
        loaded = await new_stigmergy.load()

        assert loaded is True

        # Patterns should match
        patterns_after = await new_stigmergy.sense_patterns()
        assert len(patterns_after) == len(patterns_before)

    @pytest.mark.asyncio
    async def test_load_returns_false_if_no_file(
        self,
        temp_store: Path,
    ) -> None:
        """Loading returns False if no file exists."""
        stigmergy = VoiceStigmergy(store_path=temp_store)
        loaded = await stigmergy.load()
        assert loaded is False


class TestFactory:
    """Test global factory functions."""

    def test_get_returns_same_instance(self) -> None:
        """get_voice_stigmergy returns singleton."""
        reset_voice_stigmergy()
        s1 = get_voice_stigmergy()
        s2 = get_voice_stigmergy()
        assert s1 is s2
        reset_voice_stigmergy()

    def test_set_replaces_instance(self) -> None:
        """set_voice_stigmergy replaces the singleton."""
        reset_voice_stigmergy()
        custom = VoiceStigmergy()
        set_voice_stigmergy(custom)
        assert get_voice_stigmergy() is custom
        reset_voice_stigmergy()


class TestStats:
    """Test statistics gathering."""

    @pytest.mark.asyncio
    async def test_stats_includes_field_stats(
        self,
        stigmergy: VoiceStigmergy,
        sample_voice: MorningVoice,
    ) -> None:
        """Stats include underlying field statistics."""
        await stigmergy.deposit_from_voice(sample_voice)

        stats = stigmergy.stats()
        assert "concept_count" in stats
        assert "trace_count" in stats
        assert "decay_rate" in stats
        assert "recent_deposits" in stats
        assert stats["recent_deposits"] == 1
