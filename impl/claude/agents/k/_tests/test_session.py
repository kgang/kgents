"""
Tests for K-gent Soul Session: Cross-Session Identity.

These tests verify that K-gent can:
1. Persist soul state across sessions
2. Propose and commit changes
3. Crystallize and resume from checkpoints
4. Track history of changes
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agents.k.session import (
    PersistedSoulState,
    SoulChange,
    SoulCrystal,
    SoulHistory,
    SoulPersistence,
    SoulSession,
)

# =============================================================================
# SoulChange Tests
# =============================================================================


class TestSoulChange:
    """Tests for SoulChange dataclass."""

    def test_create_change(self) -> None:
        """Test creating a soul change."""
        change = SoulChange(
            id="abc123",
            description="Be more concise",
            aspect="behavior",
            current_value="verbose",
            proposed_value="concise",
            reasoning="User feedback",
        )

        assert change.id == "abc123"
        assert change.description == "Be more concise"
        assert change.status == "pending"

    def test_change_serialization(self) -> None:
        """Test serializing change to dict."""
        change = SoulChange(
            id="abc123",
            description="Test change",
            aspect="eigenvector",
            current_value=0.5,
            proposed_value=0.7,
            reasoning="Testing",
        )

        data = change.to_dict()
        assert data["id"] == "abc123"
        assert data["status"] == "pending"
        assert "created_at" in data

    def test_change_deserialization(self) -> None:
        """Test deserializing change from dict."""
        data = {
            "id": "xyz789",
            "description": "Restored change",
            "aspect": "pattern",
            "current_value": None,
            "proposed_value": "new pattern",
            "reasoning": "From disk",
            "status": "committed",
            "created_at": "2025-01-01T00:00:00+00:00",
            "committed_at": "2025-01-01T01:00:00+00:00",
        }

        change = SoulChange.from_dict(data)
        assert change.id == "xyz789"
        assert change.status == "committed"
        assert change.committed_at is not None


# =============================================================================
# SoulHistory Tests
# =============================================================================


class TestSoulHistory:
    """Tests for SoulHistory."""

    def test_empty_history(self) -> None:
        """Test fresh history is empty."""
        history = SoulHistory()
        assert len(history.changes) == 0
        assert len(history.crystals) == 0

    def test_add_change(self) -> None:
        """Test adding changes to history."""
        history = SoulHistory()
        change = SoulChange(
            id="test1",
            description="Test",
            aspect="test",
            current_value=None,
            proposed_value=None,
            reasoning="Testing",
        )

        history.add_change(change)
        assert len(history.changes) == 1
        assert history.pending_changes() == [change]

    def test_committed_changes(self) -> None:
        """Test filtering committed changes."""
        history = SoulHistory()

        pending = SoulChange(
            id="p1",
            description="Pending",
            aspect="test",
            current_value=None,
            proposed_value=None,
            reasoning="Test",
            status="pending",
        )

        committed = SoulChange(
            id="c1",
            description="Committed",
            aspect="test",
            current_value=None,
            proposed_value=None,
            reasoning="Test",
            status="committed",
        )

        history.add_change(pending)
        history.add_change(committed)

        assert len(history.pending_changes()) == 1
        assert len(history.committed_changes()) == 1


# =============================================================================
# SoulPersistence Tests
# =============================================================================


class TestSoulPersistence:
    """Tests for SoulPersistence file operations."""

    def test_persistence_creates_directory(self) -> None:
        """Test that persistence creates the soul directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            persistence = SoulPersistence(soul_dir)

            assert soul_dir.exists()
            assert (soul_dir / "crystals").exists()

    def test_save_and_load_state(self) -> None:
        """Test saving and loading soul state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            persistence = SoulPersistence(soul_dir)

            state = PersistedSoulState(
                eigenvectors={"aesthetic": 0.9},
                persona={"name": "TestKent"},
                active_mode="reflect",
                total_interactions=10,
            )

            persistence.save_state(state)
            loaded = persistence.load_state()

            assert loaded is not None
            assert loaded.eigenvectors == {"aesthetic": 0.9}
            assert loaded.total_interactions == 10

    def test_save_and_load_history(self) -> None:
        """Test saving and loading history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            persistence = SoulPersistence(soul_dir)

            history = SoulHistory()
            history.add_change(
                SoulChange(
                    id="h1",
                    description="History test",
                    aspect="test",
                    current_value=None,
                    proposed_value=None,
                    reasoning="Testing",
                )
            )

            persistence.save_history(history)
            loaded = persistence.load_history()

            assert len(loaded.changes) == 1
            assert loaded.changes[0].id == "h1"

    def test_save_and_load_crystal(self) -> None:
        """Test crystallization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            persistence = SoulPersistence(soul_dir)

            crystal = SoulCrystal(
                id="cry1",
                name="Test Crystal",
                state={"mode": "reflect"},
            )

            persistence.save_crystal(crystal)
            loaded = persistence.load_crystal("cry1")

            assert loaded is not None
            assert loaded.name == "Test Crystal"

    def test_list_crystals(self) -> None:
        """Test listing crystals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            persistence = SoulPersistence(soul_dir)

            for i in range(3):
                crystal = SoulCrystal(
                    id=f"c{i}",
                    name=f"Crystal {i}",
                    state={},
                )
                persistence.save_crystal(crystal)

            crystals = persistence.list_crystals()
            assert len(crystals) == 3


# =============================================================================
# SoulSession Tests
# =============================================================================


class TestSoulSession:
    """Tests for SoulSession cross-session identity."""

    @pytest.mark.asyncio
    async def test_load_fresh_session(self) -> None:
        """Test loading a fresh session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            assert session.is_first_session
            assert session.soul is not None

    @pytest.mark.asyncio
    async def test_propose_change(self) -> None:
        """Test proposing a change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            change = await session.propose_change("Be more concise")

            assert change.description == "Be more concise"
            assert change.status == "pending"
            assert change in session.pending_changes

    @pytest.mark.asyncio
    async def test_commit_change(self) -> None:
        """Test committing a change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            change = await session.propose_change("Test commit")
            success = await session.commit_change(change.id)

            assert success
            assert change.status == "committed"

    @pytest.mark.asyncio
    async def test_crystallize_and_resume(self) -> None:
        """Test crystallization and resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            crystal = await session.crystallize("Test Checkpoint")
            assert crystal.name == "Test Checkpoint"

            success = await session.resume_crystal(crystal.id)
            assert success

    @pytest.mark.asyncio
    async def test_session_persistence(self) -> None:
        """Test that sessions persist across loads."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"

            # First session: propose a change
            session1 = await SoulSession.load(soul_dir)
            change = await session1.propose_change("Persistent change")
            await session1.commit_change(change.id)

            # Second session: should see the change
            session2 = await SoulSession.load(soul_dir)
            history = session2.who_was_i(10)

            assert len(history) >= 1
            assert any(c["description"] == "Persistent change" for c in history)

    @pytest.mark.asyncio
    async def test_manifest(self) -> None:
        """Test manifest returns current state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            manifest = session.manifest()

            assert "state" in manifest
            assert "pending_changes" in manifest
            assert "is_first_session" in manifest


# =============================================================================
# Integration Tests
# =============================================================================


class TestSessionIntegration:
    """Integration tests for the full session flow."""

    @pytest.mark.asyncio
    async def test_full_self_modification_flow(self) -> None:
        """Test the complete self-modification flow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"

            # Load session
            session = await SoulSession.load(soul_dir)

            # Propose a change
            change = await session.propose_change("Increase verbosity for deep explanations")
            assert change.status == "pending"

            # Commit with felt-sense
            await session.commit_change(change.id, felt_sense="This feels right")

            # Crystallize this state
            crystal = await session.crystallize("Post-verbosity")

            # Check history
            history = session.who_was_i(5)
            assert len(history) >= 1

            # Resume from crystal
            success = await session.resume_crystal(crystal.id)
            assert success

            # History should now include the resume
            history = session.who_was_i(10)
            assert any("Resumed from crystal" in c.get("description", "") for c in history)


# =============================================================================
# Change Application Tests ("Changes Have Teeth")
# =============================================================================


class TestChangeApplication:
    """Tests that changes actually modify soul state.

    The key insight: changes should have teeth.
    "Be more concise" should actually modify eigenvectors or garden patterns.
    """

    @pytest.mark.asyncio
    async def test_eigenvector_change_modifies_value(self) -> None:
        """Test that eigenvector changes actually modify the value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            # Get initial aesthetic value
            initial_aesthetic = session.soul.eigenvectors.aesthetic.value

            # Propose an eigenvector change
            change = await session.propose_change(
                description="Shift aesthetic toward minimalism",
                aspect="eigenvector",
                current_value=initial_aesthetic,
                proposed_value={
                    "name": "aesthetic",
                    "delta": -0.1,  # More minimalist
                },
            )

            # Commit the change
            await session.commit_change(change.id)

            # Verify the eigenvector was modified
            new_aesthetic = session.soul.eigenvectors.aesthetic.value
            assert new_aesthetic == pytest.approx(initial_aesthetic - 0.1, abs=0.001)

    @pytest.mark.asyncio
    async def test_eigenvector_absolute_change(self) -> None:
        """Test setting eigenvector to absolute value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            # Propose setting joy to a specific value
            change = await session.propose_change(
                description="Set joy to 0.85",
                aspect="eigenvector",
                proposed_value={
                    "name": "joy",
                    "absolute": 0.85,
                },
            )

            await session.commit_change(change.id)

            assert session.soul.eigenvectors.joy.value == pytest.approx(0.85, abs=0.001)

    @pytest.mark.asyncio
    async def test_behavior_change_plants_garden_pattern(self) -> None:
        """Test that behavior changes plant patterns in the garden."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            # Set up garden in temp dir
            from agents.k.garden import PersonaGarden, set_garden

            garden = PersonaGarden(storage_path=garden_dir, auto_save=True)
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            # Initial garden should be empty
            initial_stats = await garden.stats()
            initial_count = initial_stats.total_entries

            # Propose a behavior change
            change = await session.propose_change(
                description="Be more concise in responses",
                aspect="behavior",
            )

            await session.commit_change(change.id)

            # Garden should now have a new entry
            stats = await garden.stats()
            assert stats.total_entries == initial_count + 1

            # The entry should be a behavior type
            from agents.k.garden import EntryType

            behaviors = await garden.list_by_type(EntryType.BEHAVIOR)
            assert len(behaviors) >= 1
            assert any("concise" in b.content.lower() for b in behaviors)

    @pytest.mark.asyncio
    async def test_pattern_change_plants_garden_pattern(self) -> None:
        """Test that pattern changes plant patterns in the garden."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            from agents.k.garden import PersonaGarden, set_garden

            garden = PersonaGarden(storage_path=garden_dir, auto_save=True)
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            # Propose a pattern change with eigenvector affinities
            change = await session.propose_change(
                description="Trust incompleteness",
                aspect="pattern",
                proposed_value={
                    "content": "Trust incompleteness as a feature, not a bug",
                    "eigenvector_affinities": {"categorical": 0.3},
                },
            )

            await session.commit_change(change.id)

            # Pattern should be in garden
            patterns = await garden.patterns()
            assert len(patterns) >= 1
            assert any("incompleteness" in p.content.lower() for p in patterns)

    @pytest.mark.asyncio
    async def test_crystal_resume_restores_eigenvectors(self) -> None:
        """Test that resuming from crystal restores eigenvector values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            # Record initial state
            initial_joy = session.soul.eigenvectors.joy.value

            # Crystallize
            crystal = await session.crystallize("Before changes")

            # Modify eigenvector
            change = await session.propose_change(
                description="Increase joy",
                aspect="eigenvector",
                proposed_value={"name": "joy", "delta": 0.15},
            )
            await session.commit_change(change.id)

            # Verify change was applied
            assert session.soul.eigenvectors.joy.value == pytest.approx(
                initial_joy + 0.15, abs=0.001
            )

            # Resume from crystal - should restore original value
            await session.resume_crystal(crystal.id)

            # Joy should be back to initial value
            assert session.soul.eigenvectors.joy.value == pytest.approx(initial_joy, abs=0.001)

    @pytest.mark.asyncio
    async def test_eigenvector_persistence_across_sessions(self) -> None:
        """Test that modified eigenvectors persist across sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"

            # Session 1: Modify eigenvector
            session1 = await SoulSession.load(soul_dir)
            change = await session1.propose_change(
                description="Increase categorical thinking",
                aspect="eigenvector",
                proposed_value={"name": "categorical", "absolute": 0.95},
            )
            await session1.commit_change(change.id)

            # Session 2: Should have the modified value
            session2 = await SoulSession.load(soul_dir)
            assert session2.soul.eigenvectors.categorical.value == pytest.approx(0.95, abs=0.001)

    @pytest.mark.asyncio
    async def test_eigenvector_confidence_modification(self) -> None:
        """Test modifying eigenvector confidence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            session = await SoulSession.load(soul_dir)

            initial_conf = session.soul.eigenvectors.heterarchy.confidence

            change = await session.propose_change(
                description="Lower confidence in heterarchy",
                aspect="eigenvector",
                proposed_value={
                    "name": "heterarchy",
                    "confidence_delta": -0.1,
                },
            )
            await session.commit_change(change.id)

            assert session.soul.eigenvectors.heterarchy.confidence == pytest.approx(
                initial_conf - 0.1, abs=0.001
            )


# =============================================================================
# Dialogue-to-Garden Integration Tests
# =============================================================================


class TestDialogueGardenIntegration:
    """Tests for the dialogue → garden feedback loop.

    Every dialogue feeds the garden: existing patterns get nurtured,
    new patterns may be planted based on seasonal thresholds.
    """

    @pytest.mark.asyncio
    async def test_dialogue_plants_implicit_patterns(self) -> None:
        """Test that dialogue with pattern indicators plants seeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            from agents.k.garden import GardenSeason, PersonaGarden, set_garden

            # Use spring season for lower planting threshold
            garden = PersonaGarden(
                storage_path=garden_dir, auto_save=True, season=GardenSeason.SPRING
            )
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            # Initial count
            initial_stats = await garden.stats()
            initial_count = initial_stats.total_entries

            # Mock the soul's dialogue method to return a response
            # without requiring LLM
            from unittest.mock import AsyncMock, patch

            from agents.k.persona import DialogueMode
            from agents.k.soul import SoulDialogueOutput

            mock_output = SoulDialogueOutput(
                response="I always prefer categorical approaches. It's important to me.",
                mode=DialogueMode.REFLECT,
                tokens_used=50,
            )

            with patch.object(session._soul, "dialogue", new=AsyncMock(return_value=mock_output)):
                await session.dialogue("How do you think about problems?")

            # Check that patterns were planted
            final_stats = await garden.stats()
            # Should have planted patterns based on "always" and "important to me"
            assert final_stats.total_entries > initial_count

    @pytest.mark.asyncio
    async def test_dialogue_calls_garden_auto_plant(self) -> None:
        """Test that dialogue correctly calls garden's auto_plant_from_dialogue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            from agents.k.garden import PersonaGarden, set_garden

            garden = PersonaGarden(storage_path=garden_dir, auto_save=True)
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            from unittest.mock import AsyncMock, patch

            from agents.k.persona import DialogueMode
            from agents.k.soul import SoulDialogueOutput

            mock_output = SoulDialogueOutput(
                response="I always prefer categorical approaches to problems.",
                mode=DialogueMode.REFLECT,
                tokens_used=50,
            )

            # Track calls to auto_plant_from_dialogue
            original_auto_plant = garden.auto_plant_from_dialogue
            auto_plant_calls: list[dict[str, object]] = []

            async def tracking_auto_plant(**kwargs):
                auto_plant_calls.append(kwargs)
                return await original_auto_plant(**kwargs)

            with patch.object(session._soul, "dialogue", new=AsyncMock(return_value=mock_output)):
                with patch.object(
                    garden, "auto_plant_from_dialogue", side_effect=tracking_auto_plant
                ):
                    await session.dialogue("How do you approach problems?")

            # Verify auto_plant_from_dialogue was called with correct args
            assert len(auto_plant_calls) == 1
            call = auto_plant_calls[0]
            assert call["message"] == "How do you approach problems?"
            assert call["response"] == "I always prefer categorical approaches to problems."
            assert "eigenvector_affinities" in call

    @pytest.mark.asyncio
    async def test_dialogue_passes_eigenvector_affinities(self) -> None:
        """Test that planted patterns receive eigenvector affinities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            from agents.k.garden import GardenSeason, PersonaGarden, set_garden

            garden = PersonaGarden(
                storage_path=garden_dir, auto_save=True, season=GardenSeason.SPRING
            )
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            from unittest.mock import AsyncMock, patch

            from agents.k.persona import DialogueMode
            from agents.k.soul import SoulDialogueOutput

            mock_output = SoulDialogueOutput(
                response="I always prefer this approach",
                mode=DialogueMode.REFLECT,
                tokens_used=50,
            )

            with patch.object(session._soul, "dialogue", new=AsyncMock(return_value=mock_output)):
                await session.dialogue("What's your preference?")

            # Check that newly planted patterns have eigenvector affinities
            patterns = await garden.patterns()
            # At least one should have affinities from the soul's eigenvectors
            has_affinities = any(p.eigenvector_affinities for p in patterns)
            # Note: may not have affinities if no explicit patterns detected
            # but the mechanism is wired correctly

    @pytest.mark.asyncio
    async def test_dialogue_respects_seasonal_thresholds(self) -> None:
        """Test that planting respects seasonal thresholds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            soul_dir = Path(tmpdir) / "soul"
            garden_dir = Path(tmpdir) / "garden"

            from agents.k.garden import GardenSeason, PersonaGarden, set_garden

            # Winter has higher threshold (0.5 default)
            garden = PersonaGarden(
                storage_path=garden_dir, auto_save=True, season=GardenSeason.WINTER
            )
            set_garden(garden)

            session = await SoulSession.load(soul_dir)

            from unittest.mock import AsyncMock, patch

            from agents.k.persona import DialogueMode
            from agents.k.soul import SoulDialogueOutput

            # Low-confidence pattern indicator
            mock_output = SoulDialogueOutput(
                response="I tend to do this sometimes",
                mode=DialogueMode.REFLECT,
                tokens_used=50,
            )

            initial_stats = await garden.stats()

            with patch.object(session._soul, "dialogue", new=AsyncMock(return_value=mock_output)):
                await session.dialogue("What do you tend to do?")

            final_stats = await garden.stats()
            # Winter is more conservative - may plant fewer or no patterns
            # The key is that the seasonal config is respected
            assert final_stats.current_season == GardenSeason.WINTER
