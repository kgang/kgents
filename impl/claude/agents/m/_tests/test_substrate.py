"""
Tests for SharedSubstrate: Phase 5 Memory Architecture.

These tests verify:
1. Allocation basics (create, namespace, quota)
2. Lifecycle policy (TTL, human_label required)
3. Promotion/demotion (category law: promote >> demote ≅ id)
4. Compaction triggers
5. Categorical routing (when stigmergy available)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
from agents.m.substrate import (
    AgentId,
    Allocation,
    CompactionTrigger,
    CrystalPolicy,
    DedicatedCrystal,
    LifecyclePolicy,
    MemoryQuota,
    PromotionDecision,
    SharedSubstrate,
    create_allocation_for_agent,
    create_substrate,
)


class TestMemoryQuota:
    """Tests for MemoryQuota."""

    def test_default_values(self) -> None:
        """Default quota should be reasonable."""
        quota = MemoryQuota()
        assert quota.max_patterns == 1000
        assert quota.max_size_bytes == 10 * 1024 * 1024
        assert quota.soft_limit_ratio == 0.8

    def test_soft_limit_calculation(self) -> None:
        """Soft limit should be 80% of max."""
        quota = MemoryQuota(max_patterns=1000)
        assert quota.soft_limit_patterns() == 800

    def test_custom_quota(self) -> None:
        """Custom quotas should work."""
        quota = MemoryQuota(max_patterns=500, soft_limit_ratio=0.9)
        assert quota.soft_limit_patterns() == 450


class TestLifecyclePolicy:
    """Tests for LifecyclePolicy."""

    def test_human_label_required(self) -> None:
        """human_label is required (no anonymous debris)."""
        with pytest.raises(ValueError, match="human_label is required"):
            LifecyclePolicy(human_label="")

    def test_valid_lifecycle(self) -> None:
        """Valid lifecycle should work."""
        lifecycle = LifecyclePolicy(human_label="k-gent working memory")
        assert lifecycle.human_label == "k-gent working memory"
        assert lifecycle.ttl == timedelta(hours=24)

    def test_is_expired(self) -> None:
        """Expiration check should work."""
        lifecycle = LifecyclePolicy(
            human_label="test",
            ttl=timedelta(hours=1),
        )
        # Not expired
        recent = datetime.now() - timedelta(minutes=30)
        assert not lifecycle.is_expired(recent)

        # Expired
        old = datetime.now() - timedelta(hours=2)
        assert lifecycle.is_expired(old)


class TestCompactionTrigger:
    """Tests for CompactionTrigger."""

    def test_memory_pressure_trigger(self) -> None:
        """Should trigger at 80% usage."""
        trigger = CompactionTrigger(on_memory_pressure=0.8)

        # Create allocation at 85% usage
        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=100),
            lifecycle=LifecyclePolicy(human_label="test"),
        )
        allocation.pattern_count = 85

        assert trigger.should_compact(allocation)

    def test_below_threshold_no_trigger(self) -> None:
        """Should not trigger below threshold."""
        trigger = CompactionTrigger(on_memory_pressure=0.8)

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=100),
            lifecycle=LifecyclePolicy(human_label="test"),
        )
        allocation.pattern_count = 50

        assert not trigger.should_compact(allocation)


class TestCrystalPolicy:
    """Tests for CrystalPolicy."""

    def test_too_young_no_promote(self) -> None:
        """Young allocations should not be promoted."""
        policy = CrystalPolicy(min_age_hours=1.0)

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(),
            lifecycle=LifecyclePolicy(human_label="test"),
            created_at=datetime.now(),  # Just created
        )

        decision = policy.should_promote(allocation)
        assert not decision.should_promote
        assert decision.reason == "too_young"

    def test_high_access_promotes(self) -> None:
        """High access rate should trigger promotion."""
        policy = CrystalPolicy(
            access_frequency_threshold=10.0,
            min_age_hours=0.01,
        )

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(),
            lifecycle=LifecyclePolicy(human_label="test"),
            created_at=datetime.now() - timedelta(hours=1),
            access_count=100,  # 100 accesses in 1 hour
        )

        decision = policy.should_promote(allocation)
        assert decision.should_promote
        assert decision.auto
        assert "access_rate" in (decision.reason or "")


class TestSharedSubstrate:
    """Tests for SharedSubstrate core functionality."""

    def test_allocate_requires_human_label(self) -> None:
        """Allocation without human_label should fail."""
        substrate: SharedSubstrate[str] = create_substrate()

        with pytest.raises(ValueError, match="human_label required"):
            substrate.allocate("test-agent")

    def test_allocate_with_human_label(self) -> None:
        """Allocation with human_label should work."""
        substrate: SharedSubstrate[str] = create_substrate()

        allocation = substrate.allocate(
            "test-agent",
            human_label="test working memory",
        )

        assert allocation.agent_id == AgentId("test-agent")
        assert allocation.namespace == "test-agent"
        assert allocation.lifecycle.human_label == "test working memory"

    def test_allocate_idempotent(self) -> None:
        """Same agent should get same allocation."""
        substrate: SharedSubstrate[str] = create_substrate()

        alloc1 = substrate.allocate("test-agent", human_label="test")
        alloc2 = substrate.allocate("test-agent", human_label="ignored")

        assert alloc1 is alloc2

    def test_get_allocation(self) -> None:
        """Should be able to retrieve allocation."""
        substrate: SharedSubstrate[str] = create_substrate()
        substrate.allocate("test-agent", human_label="test")

        allocation = substrate.get_allocation("test-agent")
        assert allocation is not None
        assert allocation.agent_id == AgentId("test-agent")

    def test_get_nonexistent_allocation(self) -> None:
        """Getting nonexistent allocation should return None."""
        substrate: SharedSubstrate[str] = create_substrate()
        assert substrate.get_allocation("nonexistent") is None


class TestPromotion:
    """Tests for crystal promotion/demotion."""

    def test_promote_creates_dedicated(self) -> None:
        """Promotion should create dedicated crystal."""
        substrate: SharedSubstrate[str] = create_substrate()
        substrate.allocate("test-agent", human_label="test")

        # Simulate high usage
        allocation = substrate.get_allocation("test-agent")
        assert allocation is not None
        allocation.access_count = 1000
        allocation.created_at = datetime.now() - timedelta(hours=2)

        dedicated = substrate.promote("test-agent")

        assert isinstance(dedicated, DedicatedCrystal)
        assert dedicated.agent_id == AgentId("test-agent")
        assert "test-agent" not in substrate.allocations
        assert "test-agent" in substrate.dedicated_crystals

    def test_promote_removes_from_shared(self) -> None:
        """Promotion should remove from shared allocations."""
        substrate: SharedSubstrate[str] = create_substrate()
        substrate.allocate("test-agent", human_label="test")

        substrate.promote("test-agent")

        assert substrate.get_allocation("test-agent") is None

    def test_demote_roundtrip(self) -> None:
        """Promote >> demote should approximately equal identity."""
        substrate: SharedSubstrate[str] = create_substrate()
        substrate.allocate("test-agent", human_label="test")

        # Promote
        dedicated = substrate.promote("test-agent")
        assert dedicated is not None

        # Demote
        allocation = substrate.demote("test-agent", compress_ratio=0.5)

        # Should be back in allocations (with resolution loss)
        assert "test-agent" in substrate.allocations
        assert "test-agent" not in substrate.dedicated_crystals
        assert allocation.agent_id == AgentId("test-agent")


class TestAllocationStorage:
    """Tests for storing/retrieving from allocations."""

    @pytest.mark.asyncio
    async def test_store_respects_quota(self) -> None:
        """Storing should respect quota limits."""
        substrate: SharedSubstrate[str] = create_substrate()
        allocation = substrate.allocate(
            "test-agent",
            quota=MemoryQuota(max_patterns=5),
            human_label="test",
        )

        # Store up to limit
        for i in range(5):
            success = await allocation.store(
                f"concept_{i}",
                f"content_{i}",
                [0.1] * 10,
            )
            assert success

        # Over limit should fail
        success = await allocation.store("overflow", "content", [0.1] * 10)
        assert not success

    @pytest.mark.asyncio
    async def test_namespaced_storage(self) -> None:
        """Concepts should be namespaced."""
        substrate: SharedSubstrate[str] = create_substrate()
        allocation = substrate.allocate("test-agent", human_label="test")

        await allocation.store("my_concept", "content", [0.1] * 10)

        # The namespaced ID should be used internally
        assert allocation.namespaced_id("my_concept") == "test-agent:my_concept"


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_substrate(self) -> None:
        """create_substrate should work with defaults."""
        substrate = create_substrate()
        assert isinstance(substrate, SharedSubstrate)

    def test_create_allocation_for_agent(self) -> None:
        """create_allocation_for_agent convenience function."""
        substrate = create_substrate()

        allocation = create_allocation_for_agent(
            substrate,
            agent_id="k-gent",
            human_label="k-gent working memory",
            max_patterns=10000,
            ttl_hours=168,  # 1 week
        )

        assert allocation.quota.max_patterns == 10000
        assert allocation.lifecycle.ttl == timedelta(hours=168)
        assert allocation.lifecycle.human_label == "k-gent working memory"


class TestStats:
    """Tests for substrate statistics."""

    def test_stats(self) -> None:
        """Stats should reflect substrate state."""
        substrate: SharedSubstrate[str] = create_substrate()
        substrate.allocate("agent-1", human_label="test 1")
        substrate.allocate("agent-2", human_label="test 2")

        stats = substrate.stats()

        assert stats["allocation_count"] == 2
        assert stats["dedicated_count"] == 0
