"""
Tests for Compaction: Purposeful Forgetting as Accursed Share.

These tests verify:
1. CompactionPolicy evaluation
2. Compactor operation
3. AutoCompactionDaemon lifecycle
4. Compaction strategies
5. Holographic property preservation
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest
from agents.m.compaction import (
    AutoCompactionDaemon,
    CompactionEvent,
    CompactionPolicy,
    Compactor,
    StrategyResult,
    apply_pressure_based_strategy,
    apply_uniform_strategy,
    create_compactor,
    create_daemon,
)
from agents.m.crystal import MemoryCrystal
from agents.m.substrate import (
    AgentId,
    Allocation,
    LifecyclePolicy,
    MemoryQuota,
    SharedSubstrate,
    create_substrate,
)


class TestCompactionPolicy:
    """Tests for CompactionPolicy."""

    def test_default_policy(self) -> None:
        """Default policy values."""
        policy = CompactionPolicy()
        assert policy.pressure_threshold == 0.8
        assert policy.critical_threshold == 0.95
        assert policy.normal_ratio == 0.8
        assert policy.min_resolution == 0.1

    def test_should_compact_below_threshold(self) -> None:
        """Should not compact below threshold."""
        policy = CompactionPolicy(pressure_threshold=0.8)

        should, ratio, reason = policy.should_compact(
            current_pressure=0.5,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is False
        assert "Pressure OK" in reason

    def test_should_compact_above_threshold(self) -> None:
        """Should compact above threshold."""
        policy = CompactionPolicy(pressure_threshold=0.8)

        should, ratio, reason = policy.should_compact(
            current_pressure=0.85,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is True
        assert ratio == 0.8
        assert "High pressure" in reason

    def test_should_compact_critical(self) -> None:
        """Should use aggressive ratio for critical pressure."""
        policy = CompactionPolicy(
            critical_threshold=0.95,
            aggressive_ratio=0.5,
        )

        should, ratio, reason = policy.should_compact(
            current_pressure=0.98,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is True
        assert ratio == 0.5
        assert "Critical" in reason

    def test_rate_limit_prevents_compaction(self) -> None:
        """Rate limit prevents excessive compaction."""
        policy = CompactionPolicy(max_compactions_per_hour=2)

        should, ratio, reason = policy.should_compact(
            current_pressure=0.9,
            last_compaction=None,
            compactions_last_hour=3,
        )

        assert should is False
        assert "Rate limit" in reason

    def test_min_interval_respected(self) -> None:
        """Minimum interval between compactions respected."""
        policy = CompactionPolicy(min_interval=timedelta(minutes=30))

        should, ratio, reason = policy.should_compact(
            current_pressure=0.85,
            last_compaction=datetime.now() - timedelta(minutes=10),
            compactions_last_hour=0,
        )

        assert should is False
        assert "Too soon" in reason

    def test_critical_overrides_interval(self) -> None:
        """Critical pressure overrides interval check."""
        policy = CompactionPolicy(
            min_interval=timedelta(minutes=30),
            critical_threshold=0.95,
        )

        should, ratio, reason = policy.should_compact(
            current_pressure=0.98,
            last_compaction=datetime.now() - timedelta(minutes=5),
            compactions_last_hour=0,
        )

        assert should is True
        assert "Critical pressure override" in reason


class TestCompactionEvent:
    """Tests for CompactionEvent."""

    def test_event_creation(self) -> None:
        """CompactionEvent stores all fields."""
        event = CompactionEvent(
            timestamp=datetime.now(),
            target_id="agent_1",
            reason="High pressure",
            ratio=0.8,
            patterns_before=100,
            patterns_after=100,
            resolution_before=1.0,
            resolution_after=0.8,
            duration_ms=50.0,
        )

        assert event.patterns_preserved is True
        assert abs(event.resolution_loss - 0.2) < 0.001  # Float tolerance

    def test_patterns_not_preserved(self) -> None:
        """Detect when patterns are lost (shouldn't happen with holographic)."""
        event = CompactionEvent(
            timestamp=datetime.now(),
            target_id="agent_1",
            reason="Test",
            ratio=0.5,
            patterns_before=100,
            patterns_after=90,  # Lost patterns (error case)
            resolution_before=1.0,
            resolution_after=0.5,
            duration_ms=10.0,
        )

        assert event.patterns_preserved is False


class TestCompactor:
    """Tests for Compactor."""

    @pytest.fixture
    def crystal(self) -> MemoryCrystal[str]:
        """Create a test crystal."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        for i in range(10):
            crystal.store(f"concept_{i}", f"content_{i}", [0.1 * i] * 64)
        return crystal

    @pytest.fixture
    def compactor(self) -> Compactor[str]:
        """Create a compactor."""
        return Compactor(CompactionPolicy(pressure_threshold=0.5))

    @pytest.mark.asyncio
    async def test_compact_creates_event(
        self, crystal: MemoryCrystal[str], compactor: Compactor[str]
    ) -> None:
        """Compaction creates event."""
        event = await compactor.compact(
            crystal=crystal,
            target_id="test",
            pressure=0.9,
        )

        assert event is not None
        assert event.target_id == "test"
        assert event.patterns_preserved  # Holographic property

    @pytest.mark.asyncio
    async def test_compact_below_threshold_returns_none(
        self, crystal: MemoryCrystal[str], compactor: Compactor[str]
    ) -> None:
        """No compaction below threshold."""
        event = await compactor.compact(
            crystal=crystal,
            target_id="test",
            pressure=0.3,  # Below threshold
        )

        assert event is None

    @pytest.mark.asyncio
    async def test_compact_force_overrides_policy(
        self, crystal: MemoryCrystal[str], compactor: Compactor[str]
    ) -> None:
        """Force flag overrides policy."""
        event = await compactor.compact(
            crystal=crystal,
            target_id="test",
            pressure=0.1,  # Below threshold
            force=True,
        )

        assert event is not None
        assert "Forced" in event.reason

    @pytest.mark.asyncio
    async def test_compactor_tracks_history(
        self, crystal: MemoryCrystal[str], compactor: Compactor[str]
    ) -> None:
        """Compactor tracks compaction history."""
        await compactor.compact(crystal, "test", pressure=0.9)

        assert len(compactor.events) == 1
        assert compactor.compactions_last_hour("test") == 1

    @pytest.mark.asyncio
    async def test_compactor_stats(
        self, crystal: MemoryCrystal[str], compactor: Compactor[str]
    ) -> None:
        """Compactor statistics."""
        await compactor.compact(crystal, "test", pressure=0.9)

        stats = compactor.stats()
        assert stats["total_compactions"] == 1
        assert stats["patterns_preserved"] is True


class TestAutoCompactionDaemon:
    """Tests for AutoCompactionDaemon."""

    @pytest.fixture
    def substrate(self) -> SharedSubstrate[str]:
        """Create a substrate with allocations."""
        substrate: SharedSubstrate[str] = create_substrate()
        # Create allocation with high usage
        allocation = substrate.allocate(
            "test_agent",
            quota=MemoryQuota(max_patterns=100),
            human_label="test allocation",
        )
        allocation.pattern_count = 90  # 90% usage
        return substrate

    @pytest.mark.asyncio
    async def test_daemon_check_once(self, substrate: SharedSubstrate[str]) -> None:
        """Daemon can check allocations once."""
        daemon = AutoCompactionDaemon(
            substrate=substrate,
            compactor=Compactor(CompactionPolicy(pressure_threshold=0.5)),
        )

        events = await daemon.check_once()

        # Should have compacted the high-usage allocation
        assert len(events) >= 1

    @pytest.mark.asyncio
    async def test_daemon_start_stop(self, substrate: SharedSubstrate[str]) -> None:
        """Daemon can be started and stopped."""
        daemon = AutoCompactionDaemon(
            substrate=substrate,
            check_interval=timedelta(milliseconds=100),
        )

        assert not daemon.running

        await daemon.start()
        assert daemon.running

        await asyncio.sleep(0.05)  # Let it run briefly

        await daemon.stop()
        assert not daemon.running

    def test_daemon_stats(self, substrate: SharedSubstrate[str]) -> None:
        """Daemon tracks statistics."""
        daemon = AutoCompactionDaemon(substrate=substrate)

        stats = daemon.stats()
        assert stats["running"] is False
        assert stats["allocation_count"] == 1

    def test_create_daemon_factory(self, substrate: SharedSubstrate[str]) -> None:
        """create_daemon factory function."""
        daemon = create_daemon(
            substrate=substrate,
            check_interval_minutes=10,
        )

        assert daemon._check_interval == timedelta(minutes=10)


class TestCompactionStrategies:
    """Tests for compaction strategies."""

    @pytest.fixture
    def substrate(self) -> SharedSubstrate[str]:
        """Create a substrate with multiple allocations."""
        substrate: SharedSubstrate[str] = create_substrate()

        for i in range(3):
            allocation = substrate.allocate(
                f"agent_{i}",
                quota=MemoryQuota(max_patterns=100),
                human_label=f"allocation {i}",
            )
            allocation.pattern_count = 50 + i * 20  # 50%, 70%, 90%

        return substrate

    @pytest.mark.asyncio
    async def test_uniform_strategy(self, substrate: SharedSubstrate[str]) -> None:
        """Uniform strategy compacts all allocations."""
        compactor: Compactor[str] = Compactor()

        result = await apply_uniform_strategy(
            substrate=substrate,
            compactor=compactor,
            ratio=0.8,
        )

        assert result.strategy_name == "uniform"
        assert len(result.events) == 3  # All allocations

    @pytest.mark.asyncio
    async def test_pressure_based_strategy(
        self, substrate: SharedSubstrate[str]
    ) -> None:
        """Pressure-based strategy compacts high-pressure allocations."""
        compactor: Compactor[str] = Compactor(CompactionPolicy(pressure_threshold=0.6))

        result = await apply_pressure_based_strategy(
            substrate=substrate,
            compactor=compactor,
        )

        assert result.strategy_name == "pressure_based"
        # Only high-pressure allocations should be compacted
        # agent_1 (70%) and agent_2 (90%) should be compacted
        assert len(result.events) >= 1


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_compactor(self) -> None:
        """create_compactor factory."""
        compactor = create_compactor(
            pressure_threshold=0.7,
            critical_threshold=0.9,
            normal_ratio=0.75,
        )

        assert compactor.policy.pressure_threshold == 0.7
        assert compactor.policy.critical_threshold == 0.9
        assert compactor.policy.normal_ratio == 0.75
