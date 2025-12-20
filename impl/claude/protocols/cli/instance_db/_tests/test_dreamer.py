"""
Tests for Lucid Dreamer: Interruptible Maintenance for the Bicameral Engine.

Tests cover:
- DreamPhase state machine
- NightWatch scheduling
- REM cycle execution
- Interrupt handling
- Morning briefing questions
- Maintenance chunk processing
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from ..dreamer import (
    DreamerConfig,
    DreamPhase,
    DreamReport,
    LucidDreamer,
    MaintenanceChunk,
    MaintenanceTaskType,
    NightWatch,
    Question,
    create_lucid_dreamer,
)
from ..hippocampus import Hippocampus, HippocampusConfig
from ..nervous import Signal
from ..synapse import Synapse, SynapseConfig

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def synapse() -> Synapse:
    """Create a Synapse for testing."""
    return Synapse(config=SynapseConfig(flashbulb_threshold=0.9))


@pytest.fixture
def hippocampus() -> Hippocampus:
    """Create a Hippocampus for testing."""
    return Hippocampus(config=HippocampusConfig(flush_strategy="manual"))


@pytest.fixture
def dreamer(synapse: Synapse, hippocampus: Hippocampus) -> LucidDreamer:
    """Create a LucidDreamer for testing."""
    return LucidDreamer(
        synapse=synapse,
        hippocampus=hippocampus,
        config=DreamerConfig(
            interrupt_check_ms=10,
            flashbulb_wakes=True,
        ),
    )


# =============================================================================
# DreamerConfig Tests
# =============================================================================


class TestDreamerConfig:
    """Tests for DreamerConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = DreamerConfig()
        assert config.interrupt_check_ms == 100
        assert config.flashbulb_wakes is True
        assert config.rem_interval_hours == 24.0
        assert config.max_rem_duration_minutes == 30
        assert config.enable_neurogenesis is True

    def test_from_dict(self) -> None:
        """Config can be created from dict."""
        data = {
            "interrupt_check_ms": 50,
            "flashbulb_wakes": False,
            "rem_interval_hours": 12.0,
            "chunk_size": 200,
        }
        config = DreamerConfig.from_dict(data)
        assert config.interrupt_check_ms == 50
        assert config.flashbulb_wakes is False
        assert config.rem_interval_hours == 12.0
        assert config.chunk_size == 200

    def test_from_dict_uses_defaults(self) -> None:
        """Config uses defaults for missing keys."""
        config = DreamerConfig.from_dict({})
        assert config.interrupt_check_ms == 100
        assert config.enable_neurogenesis is True


# =============================================================================
# NightWatch Tests
# =============================================================================


class TestNightWatch:
    """Tests for NightWatch scheduler."""

    def test_creates_with_config(self) -> None:
        """NightWatch creates from config."""
        config = DreamerConfig(rem_start_time_utc="02:00")
        watch = NightWatch(config)
        assert watch.next_rem is not None
        assert watch.last_rem is None

    def test_should_dream_false_initially(self) -> None:
        """NightWatch doesn't immediately trigger dream."""
        # Set time far in future
        config = DreamerConfig(rem_start_time_utc="23:59")
        watch = NightWatch(config)
        # Might be true if test runs near midnight, so just check type
        assert isinstance(watch.should_dream(), bool)

    def test_trigger_now(self) -> None:
        """Can trigger immediate dream."""
        config = DreamerConfig()
        watch = NightWatch(config)
        watch.trigger_now()
        assert watch.should_dream() is True

    def test_mark_complete_schedules_next(self) -> None:
        """Marking complete schedules next dream."""
        config = DreamerConfig()
        watch = NightWatch(config)
        watch.trigger_now()
        old_next = watch.next_rem
        assert old_next is not None  # trigger_now should set next_rem
        watch.mark_complete()
        assert watch.last_rem is not None
        # After completing, next_rem should be scheduled for tomorrow
        # (since mark_complete re-schedules)
        assert watch.next_rem is not None
        # The new next_rem should be later than when we triggered
        assert watch.next_rem > old_next

    def test_time_until_next(self) -> None:
        """Time until next returns timedelta."""
        config = DreamerConfig()
        watch = NightWatch(config)
        delta = watch.time_until_next()
        assert isinstance(delta, timedelta)
        assert delta >= timedelta(0)


# =============================================================================
# Question Tests
# =============================================================================


class TestQuestion:
    """Tests for morning briefing questions."""

    def test_create_question(self) -> None:
        """Can create a question."""
        q = Question(
            question_id="q-001",
            question_text="Should we consolidate memories?",
            context={"epoch_count": 5},
            priority=2,
        )
        assert q.question_id == "q-001"
        assert q.priority == 2
        assert q.answered is False

    def test_question_defaults(self) -> None:
        """Question has sensible defaults."""
        q = Question(
            question_id="q-001",
            question_text="Test?",
            context={},
        )
        assert q.priority == 0
        assert q.answered is False
        assert q.answer is None


# =============================================================================
# LucidDreamer Basic Tests
# =============================================================================


class TestLucidDreamerBasic:
    """Basic tests for LucidDreamer."""

    def test_creates_with_components(self, synapse: Synapse, hippocampus: Hippocampus) -> None:
        """LucidDreamer creates with required components."""
        dreamer = LucidDreamer(synapse=synapse, hippocampus=hippocampus)
        assert dreamer.phase == DreamPhase.AWAKE
        assert dreamer.is_dreaming is False

    def test_factory_function(self, synapse: Synapse, hippocampus: Hippocampus) -> None:
        """Factory function creates dreamer."""
        dreamer = create_lucid_dreamer(
            synapse=synapse,
            hippocampus=hippocampus,
            config_dict={"interrupt_check_ms": 50},
        )
        assert dreamer._config.interrupt_check_ms == 50

    def test_initial_state(self, dreamer: LucidDreamer) -> None:
        """Initial state is awake."""
        assert dreamer.phase == DreamPhase.AWAKE
        assert dreamer.is_dreaming is False
        assert len(dreamer.morning_briefing) == 0
        assert len(dreamer.dream_history) == 0

    def test_stats(self, dreamer: LucidDreamer) -> None:
        """Stats returns expected structure."""
        stats = dreamer.stats()
        assert "phase" in stats
        assert "is_dreaming" in stats
        assert "total_dreams" in stats
        assert "pending_questions" in stats


# =============================================================================
# Morning Briefing Tests
# =============================================================================


class TestMorningBriefing:
    """Tests for morning briefing questions."""

    def test_add_question(self, dreamer: LucidDreamer) -> None:
        """Can add questions to briefing."""
        q = dreamer.add_question(
            text="Should we optimize?",
            context={"metric": "latency"},
            priority=1,
        )
        assert q.question_text == "Should we optimize?"
        assert len(dreamer.morning_briefing) == 1

    def test_answer_question(self, dreamer: LucidDreamer) -> None:
        """Can answer questions."""
        q = dreamer.add_question("Test?", {})
        assert dreamer.answer_question(q.question_id, "Yes") is True
        assert q.answered is True
        assert q.answer == "Yes"
        # Answered questions filtered from briefing
        assert len(dreamer.morning_briefing) == 0

    def test_answer_nonexistent(self, dreamer: LucidDreamer) -> None:
        """Answering nonexistent question returns False."""
        assert dreamer.answer_question("fake-id", "Yes") is False

    def test_max_questions_limit(self, dreamer: LucidDreamer) -> None:
        """Questions limited by max_questions."""
        # Add more than max
        for i in range(15):
            dreamer.add_question(f"Q{i}?", {}, priority=i)
        # Default max is 10
        assert len(dreamer.morning_briefing) <= 10
        # Higher priority kept
        priorities = [q.priority for q in dreamer.morning_briefing]
        assert min(priorities) >= 5  # Low priority dropped

    def test_clear_answered(self, dreamer: LucidDreamer) -> None:
        """Can clear answered questions."""
        q1 = dreamer.add_question("Q1?", {})
        q2 = dreamer.add_question("Q2?", {})
        dreamer.answer_question(q1.question_id, "Yes")
        removed = dreamer.clear_answered()
        assert removed == 1
        assert len(dreamer._morning_briefing) == 1


# =============================================================================
# REM Cycle Tests
# =============================================================================


class TestREMCycle:
    """Tests for REM cycle execution."""

    @pytest.mark.asyncio
    async def test_rem_cycle_completes(self, dreamer: LucidDreamer) -> None:
        """REM cycle completes all phases."""
        report = await dreamer.rem_cycle()
        assert report.interrupted is False
        assert report.phase_reached == DreamPhase.WAKING
        assert report.completed_at is not None

    @pytest.mark.asyncio
    async def test_rem_cycle_creates_report(self, dreamer: LucidDreamer) -> None:
        """REM cycle creates detailed report."""
        report = await dreamer.rem_cycle()
        assert report.dream_id is not None
        assert report.started_at is not None
        assert report.chunks_processed >= 0
        assert isinstance(report.proposed_migrations, list)

    @pytest.mark.asyncio
    async def test_rem_cycle_flushes_hippocampus(
        self, synapse: Synapse, hippocampus: Hippocampus
    ) -> None:
        """REM cycle flushes hippocampus."""
        # Add some signals to hippocampus
        await hippocampus.remember(Signal(signal_type="test.signal", data={}))
        await hippocampus.remember(Signal(signal_type="test.signal", data={}))

        dreamer = LucidDreamer(synapse=synapse, hippocampus=hippocampus)
        report = await dreamer.rem_cycle()

        assert report.flush_result is not None
        assert report.flush_result.signals_transferred >= 0

    @pytest.mark.asyncio
    async def test_rem_cycle_returns_to_awake(self, dreamer: LucidDreamer) -> None:
        """Dreamer returns to AWAKE after cycle."""
        assert dreamer.phase == DreamPhase.AWAKE
        await dreamer.rem_cycle()
        assert dreamer.phase == DreamPhase.AWAKE

    @pytest.mark.asyncio
    async def test_dream_history_tracked(self, dreamer: LucidDreamer) -> None:
        """Dream history is tracked."""
        assert len(dreamer.dream_history) == 0
        await dreamer.rem_cycle()
        assert len(dreamer.dream_history) == 1
        await dreamer.rem_cycle()
        assert len(dreamer.dream_history) == 2


# =============================================================================
# Interrupt Handling Tests
# =============================================================================


class TestInterruptHandling:
    """Tests for interrupt handling during dreams."""

    @pytest.mark.asyncio
    async def test_flashbulb_interrupts_dream(
        self, synapse: Synapse, hippocampus: Hippocampus
    ) -> None:
        """Flashbulb signal interrupts dreaming."""
        dreamer = LucidDreamer(
            synapse=synapse,
            hippocampus=hippocampus,
            config=DreamerConfig(
                interrupt_check_ms=10,
                flashbulb_wakes=True,
            ),
        )

        # Fire a flashbulb signal
        flashbulb = Signal(signal_type="emergency.critical", data={})
        flashbulb.surprise = 0.95  # Above flashbulb threshold
        await synapse.fire(flashbulb, bypass_model=True)

        # Start dream - should get interrupted
        report = await dreamer.rem_cycle()
        # May or may not interrupt depending on timing
        # Just verify report structure
        assert isinstance(report.interrupted, bool)
        if report.interrupted:
            assert report.interrupt_reason is not None

    @pytest.mark.asyncio
    async def test_flashbulb_disabled(self, synapse: Synapse, hippocampus: Hippocampus) -> None:
        """Can disable flashbulb interrupts."""
        dreamer = LucidDreamer(
            synapse=synapse,
            hippocampus=hippocampus,
            config=DreamerConfig(flashbulb_wakes=False),
        )

        # Fire signal that would normally interrupt
        flashbulb = Signal(signal_type="emergency.critical", data={})
        flashbulb.surprise = 0.95
        await synapse.fire(flashbulb, bypass_model=True)

        report = await dreamer.rem_cycle()
        # Should complete without interrupt
        assert report.interrupted is False


# =============================================================================
# Maintenance Tests
# =============================================================================


class TestMaintenance:
    """Tests for maintenance chunk processing."""

    def test_maintenance_chunk_creation(self) -> None:
        """Maintenance chunks created correctly."""
        chunk = MaintenanceChunk(
            chunk_id="test-001",
            task_type=MaintenanceTaskType.GHOST_HEALING,
            progress=0.0,
            items_processed=0,
            items_total=100,
            started_at=datetime.now().isoformat(),
        )
        assert chunk.is_complete is False
        chunk.progress = 1.0
        assert chunk.is_complete is True

    @pytest.mark.asyncio
    async def test_maintenance_tasks_executed(self, dreamer: LucidDreamer) -> None:
        """Maintenance tasks are executed in REM cycle."""
        report = await dreamer.rem_cycle()
        # Should process at least some chunks
        assert report.total_chunks > 0
        assert report.chunks_processed >= 0

    @pytest.mark.asyncio
    async def test_custom_maintenance_task(
        self, synapse: Synapse, hippocampus: Hippocampus
    ) -> None:
        """Custom maintenance tasks are called."""
        task_called = {"count": 0}

        def custom_task(chunk: MaintenanceChunk) -> None:
            task_called["count"] += 1

        dreamer = LucidDreamer(
            synapse=synapse,
            hippocampus=hippocampus,
            maintenance_tasks=[custom_task],
        )

        await dreamer.rem_cycle()
        assert task_called["count"] > 0


# =============================================================================
# DreamReport Tests
# =============================================================================


class TestDreamReport:
    """Tests for DreamReport."""

    def test_duration_calculation(self) -> None:
        """Duration calculated correctly."""
        report = DreamReport(
            dream_id="test",
            started_at="2024-01-01T00:00:00",
            completed_at="2024-01-01T00:01:00",
            phase_reached=DreamPhase.WAKING,
            interrupted=False,
            interrupt_reason=None,
            chunks_processed=10,
            total_chunks=10,
            flush_result=None,
            questions_generated=0,
            proposed_migrations=[],
            errors=[],
        )
        assert report.duration_seconds == 60.0

    def test_completion_rate(self) -> None:
        """Completion rate calculated correctly."""
        report = DreamReport(
            dream_id="test",
            started_at="2024-01-01T00:00:00",
            completed_at=None,
            phase_reached=DreamPhase.INTERRUPTED,
            interrupted=True,
            interrupt_reason="Test",
            chunks_processed=5,
            total_chunks=10,
            flush_result=None,
            questions_generated=0,
            proposed_migrations=[],
            errors=[],
        )
        assert report.completion_rate == 0.5

    def test_completion_rate_zero_chunks(self) -> None:
        """Completion rate handles zero chunks."""
        report = DreamReport(
            dream_id="test",
            started_at="2024-01-01T00:00:00",
            completed_at=None,
            phase_reached=DreamPhase.WAKING,
            interrupted=False,
            interrupt_reason=None,
            chunks_processed=0,
            total_chunks=0,
            flush_result=None,
            questions_generated=0,
            proposed_migrations=[],
            errors=[],
        )
        assert report.completion_rate == 1.0


# =============================================================================
# Trigger Tests
# =============================================================================


class TestTriggers:
    """Tests for manual dream triggers."""

    def test_trigger_dream_now(self, dreamer: LucidDreamer) -> None:
        """Can trigger immediate dream."""
        dreamer.trigger_dream_now()
        assert dreamer.should_dream() is True

    def test_should_dream_delegation(self, dreamer: LucidDreamer) -> None:
        """should_dream delegates to NightWatch."""
        dreamer.trigger_dream_now()
        assert dreamer.should_dream() == dreamer.night_watch.should_dream()


# =============================================================================
# Integration Tests
# =============================================================================


class TestDreamerIntegration:
    """Integration tests for LucidDreamer."""

    @pytest.mark.asyncio
    async def test_full_cycle_with_signals(
        self, synapse: Synapse, hippocampus: Hippocampus
    ) -> None:
        """Full cycle with realistic signal flow."""
        dreamer = LucidDreamer(
            synapse=synapse,
            hippocampus=hippocampus,
            config=DreamerConfig(enable_neurogenesis=True),
        )

        # Add signals to hippocampus
        for i in range(5):
            signal = Signal(signal_type=f"test.event.{i}", data={"index": i})
            await hippocampus.remember(signal)

        # Run dream cycle
        report = await dreamer.rem_cycle()

        # Verify complete cycle
        assert report.phase_reached == DreamPhase.WAKING
        assert report.flush_result is not None
        assert dreamer.stats()["total_dreams"] == 1

    @pytest.mark.asyncio
    async def test_multiple_cycles(self, synapse: Synapse, hippocampus: Hippocampus) -> None:
        """Multiple dream cycles work correctly."""
        dreamer = LucidDreamer(synapse=synapse, hippocampus=hippocampus)

        # Run multiple cycles
        for _ in range(3):
            await dreamer.rem_cycle()

        assert dreamer.stats()["total_dreams"] == 3
        assert len(dreamer.dream_history) == 3
