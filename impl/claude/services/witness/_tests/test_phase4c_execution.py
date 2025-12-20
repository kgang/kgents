"""
Tests for Phase 4C: Workflow Execution and Trust Persistence.

Covers:
- ConfirmationManager → PipelineRunner execution
- TrustPersistence save/load round-trip
- Trust decay on inactivity
- Execution results in ConfirmationResult

Success Criteria (from Phase 4C spec):
1. Accept suggestion → workflow runs → output visible in TUI
2. Restart kgentsd → trust level preserved (not reset to L0)
3. `kgentsd status` shows: trust level, acceptance rate, time to next level
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from services.witness.polynomial import TrustLevel
from services.witness.trust.confirmation import (
    ActionPreview,
    ConfirmationManager,
    ConfirmationResult,
    PendingSuggestion,
    SuggestionStatus,
)
from services.witness.trust_persistence import (
    PersistedTrustState,
    TrustPersistence,
)

# =============================================================================
# Trust Persistence Tests
# =============================================================================


class TestPersistedTrustState:
    """Test PersistedTrustState dataclass."""

    def test_default_state_is_l0(self) -> None:
        """Default state starts at L0."""
        state = PersistedTrustState()
        assert state.trust_level == 0
        assert state.trust == TrustLevel.READ_ONLY

    def test_acceptance_rate_calculation(self) -> None:
        """Acceptance rate is correctly calculated."""
        state = PersistedTrustState(
            confirmed_suggestions=3,
            total_suggestions=4,
        )
        assert state.acceptance_rate == 0.75

    def test_acceptance_rate_zero_when_no_suggestions(self) -> None:
        """Acceptance rate is 0 when no suggestions."""
        state = PersistedTrustState()
        assert state.acceptance_rate == 0.0

    def test_decay_not_applied_within_24h(self) -> None:
        """Decay is not applied if active within 24h."""
        state = PersistedTrustState(
            trust_level=2,
            trust_level_raw=2.0,
            last_active_iso=datetime.now().isoformat(),
        )
        decayed = state.apply_decay()
        assert decayed is False
        assert state.trust_level == 2

    def test_decay_applied_after_48h(self) -> None:
        """Decay is applied after 48h of inactivity."""
        # 48h inactive = 2 decay cycles = 0.2 level reduction
        two_days_ago = datetime.now() - timedelta(hours=48)
        state = PersistedTrustState(
            trust_level=3,
            trust_level_raw=3.0,
            last_active_iso=two_days_ago.isoformat(),
        )
        decayed = state.apply_decay()
        assert decayed is True
        assert state.trust_level_raw < 3.0
        # Floor at L1
        assert state.trust_level_raw >= 1.0

    def test_decay_floor_at_l1(self) -> None:
        """Trust never decays below L1."""
        long_ago = datetime.now() - timedelta(days=365)
        state = PersistedTrustState(
            trust_level=3,
            trust_level_raw=3.0,
            last_active_iso=long_ago.isoformat(),
        )
        state.apply_decay()
        assert state.trust_level >= 1
        assert state.trust_level_raw >= 1.0

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """State can be serialized and deserialized."""
        state = PersistedTrustState(
            trust_level=2,
            trust_level_raw=2.5,
            observation_count=150,
            successful_operations=75,
            confirmed_suggestions=40,
            total_suggestions=50,
            last_active_iso=datetime.now().isoformat(),
            first_observed_iso=(datetime.now() - timedelta(days=7)).isoformat(),
        )

        data = state.to_dict()
        restored = PersistedTrustState.from_dict(data)

        assert restored.trust_level == state.trust_level
        assert restored.trust_level_raw == state.trust_level_raw
        assert restored.observation_count == state.observation_count
        assert restored.successful_operations == state.successful_operations
        assert restored.confirmed_suggestions == state.confirmed_suggestions
        assert restored.total_suggestions == state.total_suggestions


class TestTrustPersistence:
    """Test TrustPersistence file operations."""

    @pytest.fixture
    def temp_state_file(self, tmp_path: Path) -> Path:
        """Create a temporary state file path."""
        return tmp_path / ".kgents" / "witness.json"

    @pytest.mark.asyncio
    async def test_load_creates_fresh_state_if_not_exists(self, temp_state_file: Path) -> None:
        """Loading from non-existent file creates fresh L0 state."""
        persistence = TrustPersistence(state_file=temp_state_file)
        state = await persistence.load()

        assert state.trust_level == 0
        assert state.observation_count == 0
        assert state.first_observed_iso != ""

    @pytest.mark.asyncio
    async def test_save_creates_directory_and_file(self, temp_state_file: Path) -> None:
        """Saving creates parent directory and file."""
        persistence = TrustPersistence(state_file=temp_state_file)
        state = PersistedTrustState(
            trust_level=1,
            observation_count=100,
        )

        success = await persistence.save(state)

        assert success
        assert temp_state_file.exists()

        # Verify contents
        data = json.loads(temp_state_file.read_text())
        assert data["trust_level"] == 1
        assert data["observation_count"] == 100

    @pytest.mark.asyncio
    async def test_save_load_roundtrip(self, temp_state_file: Path) -> None:
        """State is preserved through save/load cycle."""
        persistence = TrustPersistence(state_file=temp_state_file)

        # Create and save state
        original = PersistedTrustState(
            trust_level=2,
            trust_level_raw=2.3,
            observation_count=200,
            successful_operations=150,
            confirmed_suggestions=45,
            total_suggestions=50,
        )
        await persistence.save(original)

        # Load in new persistence instance
        persistence2 = TrustPersistence(state_file=temp_state_file)
        loaded = await persistence2.load(apply_decay=False)

        assert loaded.trust_level == original.trust_level
        assert loaded.trust_level_raw == original.trust_level_raw
        assert loaded.observation_count == original.observation_count
        assert loaded.successful_operations == original.successful_operations
        assert loaded.confirmed_suggestions == original.confirmed_suggestions

    @pytest.mark.asyncio
    async def test_record_observation_increments_count(self, temp_state_file: Path) -> None:
        """Recording an observation increments count and saves."""
        persistence = TrustPersistence(state_file=temp_state_file, auto_save=True)
        await persistence.load()

        await persistence.record_observation()
        await persistence.record_observation()
        await persistence.record_observation()

        # Reload and verify
        persistence2 = TrustPersistence(state_file=temp_state_file)
        state = await persistence2.load(apply_decay=False)

        assert state.observation_count == 3

    @pytest.mark.asyncio
    async def test_record_suggestion_updates_metrics(self, temp_state_file: Path) -> None:
        """Recording suggestions updates confirmation metrics."""
        persistence = TrustPersistence(state_file=temp_state_file, auto_save=True)
        await persistence.load()

        # Record some suggestions
        await persistence.record_suggestion(confirmed=True)
        await persistence.record_suggestion(confirmed=True)
        await persistence.record_suggestion(confirmed=False)

        # Reload and verify
        persistence2 = TrustPersistence(state_file=temp_state_file)
        state = await persistence2.load(apply_decay=False)

        assert state.total_suggestions == 3
        assert state.confirmed_suggestions == 2
        assert state.acceptance_rate == 2 / 3

    @pytest.mark.asyncio
    async def test_escalate_updates_trust_level(self, temp_state_file: Path) -> None:
        """Escalation updates trust level and saves."""
        persistence = TrustPersistence(state_file=temp_state_file, auto_save=True)
        await persistence.load()

        success = await persistence.escalate(TrustLevel.BOUNDED, reason="24h passed")

        assert success

        # Reload and verify
        persistence2 = TrustPersistence(state_file=temp_state_file)
        state = await persistence2.load(apply_decay=False)

        assert state.trust_level == 1
        assert state.trust == TrustLevel.BOUNDED

    def test_get_status_includes_progress(self, temp_state_file: Path) -> None:
        """Status includes escalation progress."""
        persistence = TrustPersistence(state_file=temp_state_file)
        # Initialize with some observations
        persistence._state = PersistedTrustState(
            trust_level=0,
            observation_count=50,
            first_observed_iso=datetime.now().isoformat(),
        )

        status = persistence.get_status()

        assert "trust_level" in status
        assert "escalation_progress" in status
        assert status["escalation_progress"]["next_level"] == "L1 BOUNDED"
        assert status["escalation_progress"]["observations_needed"] == 50


# =============================================================================
# ConfirmationManager Pipeline Execution Tests
# =============================================================================


class TestConfirmationManagerPipelineExecution:
    """Test ConfirmationManager with pipeline execution."""

    @pytest.mark.asyncio
    async def test_confirm_without_pipeline_uses_fallback_handler(self) -> None:
        """Without pipeline, uses execution_handler fallback."""
        executed = []

        async def handler(action: str) -> tuple[bool, str]:
            executed.append(action)
            return True, "Handler executed"

        manager = ConfirmationManager(execution_handler=handler)

        suggestion = await manager.submit(
            action="test-action",
            rationale="test rationale",
        )

        result = await manager.confirm(suggestion.id)

        assert result.accepted is True
        assert result.executed is True
        assert "test-action" in executed
        assert result.execution_result == "Handler executed"

    @pytest.mark.asyncio
    async def test_confirm_with_pipeline_executes_pipeline(self) -> None:
        """With pipeline attached, executes via pipeline runner."""

        class MockPipelineResult:
            success = True
            step_results = []
            total_duration_ms = 123.4
            error = None
            aborted_at_step = None

        class MockPipelineRunner:
            async def run(self, pipeline, initial_kwargs=None):
                return MockPipelineResult()

        class MockPipeline:
            pass

        manager = ConfirmationManager(pipeline_runner=MockPipelineRunner())

        suggestion = await manager.submit(
            action="workflow-action",
            rationale="test rationale",
            pipeline=MockPipeline(),
            initial_kwargs={"test": "value"},
        )

        result = await manager.confirm(suggestion.id)

        assert result.accepted is True
        assert result.executed is True
        assert result.pipeline_result is not None
        assert result.duration_ms == 123.4

    @pytest.mark.asyncio
    async def test_confirm_with_failing_pipeline_records_error(self) -> None:
        """Failed pipeline execution is recorded."""

        class MockPipelineResult:
            success = False
            step_results = []
            total_duration_ms = 50.0
            error = "Step 2 failed"
            aborted_at_step = 2

        class MockPipelineRunner:
            async def run(self, pipeline, initial_kwargs=None):
                return MockPipelineResult()

        class MockPipeline:
            pass

        manager = ConfirmationManager(pipeline_runner=MockPipelineRunner())

        suggestion = await manager.submit(
            action="failing-workflow",
            rationale="test",
            pipeline=MockPipeline(),
        )

        result = await manager.confirm(suggestion.id)

        assert result.accepted is True
        assert result.executed is False
        assert result.error == "Step 2 failed"
        assert "failed at step 2" in result.execution_result

    @pytest.mark.asyncio
    async def test_suggestion_stores_pipeline_and_kwargs(self) -> None:
        """Suggestion correctly stores pipeline and initial_kwargs."""

        class MockPipeline:
            name = "test-pipeline"

        manager = ConfirmationManager()

        suggestion = await manager.submit(
            action="test-action",
            rationale="test",
            pipeline=MockPipeline(),
            initial_kwargs={"file": "test.py", "line": 42},
        )

        assert suggestion.pipeline is not None
        assert suggestion.pipeline.name == "test-pipeline"
        assert suggestion.initial_kwargs == {"file": "test.py", "line": 42}


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase4CIntegration:
    """End-to-end Phase 4C integration tests."""

    @pytest.mark.asyncio
    async def test_trust_persists_across_sessions(self, tmp_path: Path) -> None:
        """
        Success Criterion: Restart kgentsd → trust level preserved.

        Simulates multiple daemon sessions maintaining trust state.
        """
        state_file = tmp_path / ".kgents" / "witness.json"

        # Session 1: Start fresh, make some observations
        p1 = TrustPersistence(state_file=state_file)
        state = await p1.load()
        assert state.trust_level == 0  # Fresh start

        for _ in range(10):
            await p1.record_observation()

        # Session 2: Load and verify persistence
        p2 = TrustPersistence(state_file=state_file)
        state = await p2.load(apply_decay=False)

        assert state.observation_count == 10  # Persisted!

        # Session 3: Continue making progress
        for _ in range(5):
            await p2.record_observation()

        # Session 4: Final verification
        p3 = TrustPersistence(state_file=state_file)
        state = await p3.load(apply_decay=False)

        assert state.observation_count == 15  # All observations counted

    @pytest.mark.asyncio
    async def test_acceptance_rate_affects_escalation_progress(self, tmp_path: Path) -> None:
        """
        Success Criterion: Acceptance rate tracked for L2→L3 escalation.

        L2→L3 requires: 50 suggestions with >90% acceptance.
        Progress is: min(suggestions/50, acceptance/0.9)
        """
        state_file = tmp_path / ".kgents" / "witness.json"
        persistence = TrustPersistence(state_file=state_file)

        # Start at L2
        await persistence.load()
        await persistence.escalate(TrustLevel.SUGGESTION)

        # Record 50 suggestions: 45 confirmed, 5 rejected = 90% acceptance
        for _ in range(45):
            await persistence.record_suggestion(confirmed=True)
        for _ in range(5):
            await persistence.record_suggestion(confirmed=False)

        status = persistence.get_status()

        assert status["acceptance_rate"] == "90%"
        progress = status["escalation_progress"]
        # With 50 suggestions and 90% acceptance, progress should be 1.0
        assert progress["overall_progress"] >= 0.9
        assert progress["suggestions_needed"] == 0

    @pytest.mark.asyncio
    async def test_workflow_execution_records_metrics(self, tmp_path: Path) -> None:
        """
        Success Criterion: Workflow execution updates trust metrics.

        Tests the full flow: suggestion → confirm → execute → record.
        """
        state_file = tmp_path / ".kgents" / "witness.json"

        class MockPipelineResult:
            success = True
            step_results = []
            total_duration_ms = 100.0
            error = None

        class MockPipelineRunner:
            async def run(self, pipeline, initial_kwargs=None):
                return MockPipelineResult()

        class MockPipeline:
            pass

        # Create confirmation manager with pipeline runner
        manager = ConfirmationManager(pipeline_runner=MockPipelineRunner())

        # Create persistence
        persistence = TrustPersistence(state_file=state_file)
        await persistence.load()

        # Submit and confirm a suggestion
        suggestion = await manager.submit(
            action="Test Workflow",
            rationale="Testing execution",
            pipeline=MockPipeline(),
        )

        result = await manager.confirm(suggestion.id)

        # Manually record (in real flow, TUI does this)
        await persistence.record_suggestion(confirmed=result.executed)

        # Verify metrics
        state = await persistence.load(apply_decay=False)
        assert state.confirmed_suggestions == 1
        assert state.total_suggestions == 1
        assert state.acceptance_rate == 1.0


# =============================================================================
# CLI Status Tests
# =============================================================================


class TestCLIStatus:
    """Test CLI status command output."""

    def test_get_status_format(self, tmp_path: Path) -> None:
        """Status returns expected format."""
        state_file = tmp_path / ".kgents" / "witness.json"
        persistence = TrustPersistence(state_file=state_file)
        persistence._state = PersistedTrustState(
            trust_level=1,
            observation_count=100,
            successful_operations=50,
            confirmed_suggestions=20,
            total_suggestions=25,
        )

        status = persistence.get_status()

        assert status["trust_level"] == "BOUNDED"
        assert status["trust_level_value"] == 1
        assert status["trust_emoji"] == "📁"
        assert status["observation_count"] == 100
        assert status["successful_operations"] == 50
        assert status["acceptance_rate"] == "80%"
        assert "escalation_progress" in status
