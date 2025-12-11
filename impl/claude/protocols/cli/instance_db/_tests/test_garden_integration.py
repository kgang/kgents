"""
Tests for MemoryGarden + Compost + Lethe integration.

These tests verify the complete memory lifecycle:
- MemoryGarden entries flow through lifecycle stages
- Composted entries become NutrientBlocks
- Forgotten entries get cryptographic proofs
- Nutrients feed back into new entries (composability)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pytest

from ..compost import (
    CompostBin,
    CompostConfig,
    create_nutrient_block,
)
from ..hippocampus import LetheEpoch
from ..lethe import (
    LetheStore,
    RetentionConfig,
)

# === Mock MemoryGarden types (to avoid circular import) ===


@dataclass
class MockGardenEntry:
    """Mock garden entry for testing."""

    id: str
    content: Any
    lifecycle: str  # "seed", "sapling", "tree", "flower", "compost"
    trust: float
    hypothesis: str = ""
    planted_at: datetime = None
    tags: list[str] = None
    evidence: list = None
    connections: list[str] = None

    def __post_init__(self):
        if self.planted_at is None:
            self.planted_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.evidence is None:
            self.evidence = []
        if self.connections is None:
            self.connections = []


@dataclass
class MockSignal:
    """Mock signal for composting garden entries."""

    signal_type: str
    data: dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


def garden_entry_to_signals(entry: MockGardenEntry) -> list[MockSignal]:
    """Convert a garden entry to compostable signals."""
    signals = [
        MockSignal(
            signal_type="garden.entry",
            data={
                "entry_id": entry.id,
                "lifecycle": entry.lifecycle,
                "trust": entry.trust,
                "tags": entry.tags,
            },
        )
    ]
    # Add evidence as signals
    for i, ev in enumerate(entry.evidence):
        signals.append(
            MockSignal(
                signal_type="garden.evidence",
                data={
                    "entry_id": entry.id,
                    "evidence_index": i,
                    "evidence_data": ev,
                },
            )
        )
    return signals


def create_test_epoch_from_entry(entry: MockGardenEntry) -> LetheEpoch:
    """Create a Lethe epoch from a garden entry."""
    return LetheEpoch(
        epoch_id=f"garden-{entry.id}",
        created_at=entry.planted_at.isoformat(),
        sealed_at=datetime.now().isoformat(),
        signal_count=1 + len(entry.evidence),
        signal_types={"garden.entry", "garden.evidence"},
    )


# === Integration Tests ===


class TestGardenToCompost:
    """Tests for converting garden entries to compost."""

    def test_entry_to_signals(self) -> None:
        """Test converting entry to signals."""
        entry = MockGardenEntry(
            id="entry-001",
            content={"idea": "test idea"},
            lifecycle="tree",
            trust=0.8,
            tags=["category", "theory"],
            evidence=[{"source": "test", "weight": 0.9}],
        )

        signals = garden_entry_to_signals(entry)

        assert len(signals) == 2  # 1 entry + 1 evidence
        assert signals[0].signal_type == "garden.entry"
        assert signals[0].data["trust"] == 0.8
        assert signals[1].signal_type == "garden.evidence"

    def test_compost_garden_entries(self) -> None:
        """Test composting multiple garden entries."""
        entries = [
            MockGardenEntry(
                id=f"entry-{i}",
                content={"value": i},
                lifecycle="compost",
                trust=0.1 + i * 0.1,
                tags=[f"tag_{i % 3}"],
            )
            for i in range(10)
        ]

        # Convert to signals
        all_signals = []
        for entry in entries:
            all_signals.extend(garden_entry_to_signals(entry))

        # Compost
        config = CompostConfig(
            frequency_fields=["signal_type", "lifecycle"],
            cardinality_fields=["entry_id"],
            quantile_fields=["trust"],
        )
        bin = CompostBin(config=config)
        bin.add_batch(all_signals)

        block = bin.seal("garden-batch-001")

        assert block.source_signal_count == 10  # 10 entries, no evidence
        assert block.get_cardinality("entry_id") >= 8  # ~10 unique entries


class TestGardenToLethe:
    """Tests for garden lifecycle through Lethe."""

    @pytest.mark.asyncio
    async def test_compost_lifecycle_entry(self) -> None:
        """Test composting a COMPOST lifecycle entry."""
        store = LetheStore()

        entry = MockGardenEntry(
            id="old-idea",
            content={"deprecated": True},
            lifecycle="compost",
            trust=0.1,
            planted_at=datetime.now() - timedelta(days=100),
        )

        signals = garden_entry_to_signals(entry)
        epoch = create_test_epoch_from_entry(entry)

        block = await store.compost(epoch, signals)

        assert block.epoch_id == f"garden-{entry.id}"
        assert store.get_nutrient_block(epoch.epoch_id) is not None

    @pytest.mark.asyncio
    async def test_forget_composted_entry(self) -> None:
        """Test forgetting after composting."""
        store = LetheStore()

        entry = MockGardenEntry(
            id="to-forget",
            content={"sensitive": True},
            lifecycle="compost",
            trust=0.05,
        )

        signals = garden_entry_to_signals(entry)
        epoch = create_test_epoch_from_entry(entry)

        block, proof = await store.compost_then_forget(epoch, signals)

        # Nutrients preserved
        assert store.get_nutrient_block(epoch.epoch_id) is not None

        # Proof valid
        assert store.verify_proof(proof)

        # Audit log records both
        log = store.get_audit_log()
        assert len(log) == 2  # compost + forget


class TestNutrientFeedback:
    """Tests for nutrients feeding back into new entries."""

    def test_nutrients_provide_context(self) -> None:
        """Test that nutrients from old entries provide context for new ones."""
        # First batch: original entries
        old_entries = [
            MockGardenEntry(
                id=f"old-{i}",
                content={"lesson": f"lesson_{i}"},
                lifecycle="compost",
                trust=0.2,
                tags=["category-theory", "composition"],
            )
            for i in range(20)
        ]

        old_signals = []
        for entry in old_entries:
            old_signals.extend(garden_entry_to_signals(entry))

        old_block = create_nutrient_block("old-batch", old_signals)

        # New batch: fresh entries (would benefit from old context)
        new_entries = [
            MockGardenEntry(
                id=f"new-{i}",
                content={"idea": f"idea_{i}"},
                lifecycle="seed",
                trust=0.3,
                tags=["category-theory"],
            )
            for i in range(10)
        ]

        new_signals = []
        for entry in new_entries:
            new_signals.extend(garden_entry_to_signals(entry))

        new_block = create_nutrient_block("new-batch", new_signals)

        # Merge blocks to get combined context
        combined = old_block.merge(new_block)

        assert combined.source_signal_count == 30  # 20 old + 10 new
        # Tags should include category-theory
        assert "category-theory" in combined.tags or "composition" in combined.tags

    def test_nutrient_concepts_extraction(self) -> None:
        """Test that concepts are extracted from composted entries."""
        entries = [
            MockGardenEntry(
                id="insight-1",
                content={"type": "insight"},
                lifecycle="compost",
                trust=0.1,
                hypothesis="Functors preserve structure",
                tags=["functor", "morphism"],
            ),
            MockGardenEntry(
                id="insight-2",
                content={"type": "insight"},
                lifecycle="compost",
                trust=0.15,
                hypothesis="Monads compose effects",
                tags=["monad", "composition"],
            ),
        ]

        signals = []
        for entry in entries:
            signals.extend(garden_entry_to_signals(entry))

        block = create_nutrient_block(
            "insights-batch",
            signals,
            config=CompostConfig(frequency_fields=["signal_type"]),
        )

        # Tags should be preserved
        assert "functor" in block.tags or "monad" in block.tags


class TestFullLifecycle:
    """End-to-end lifecycle tests."""

    @pytest.mark.asyncio
    async def test_seed_to_compost_to_forget(self) -> None:
        """Test full lifecycle from seed to forgetting."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=0,  # Immediate for testing
                warm_days=0,
                compost_days=0,
            )
        )

        # 1. Seed is planted (hypothetical)
        entry = MockGardenEntry(
            id="lifecycle-test",
            content={"hypothesis": "Test hypothesis"},
            lifecycle="seed",
            trust=0.3,
        )

        # 2. Entry grows to tree (trust increases)
        entry.trust = 0.7
        entry.lifecycle = "tree"

        # 3. Entry becomes flower (peak insight)
        entry.trust = 0.9
        entry.lifecycle = "flower"

        # 4. Entry is harvested and moves to compost
        entry.lifecycle = "compost"
        entry.trust = 0.1  # Trust decays after harvest

        # 5. Compost + Forget
        signals = garden_entry_to_signals(entry)
        epoch = create_test_epoch_from_entry(entry)

        block, proof = await store.compost_then_forget(epoch, signals)

        # Verify lifecycle completed
        assert block.source_signal_count == 1
        assert store.verify_proof(proof)

        # Audit complete
        log = store.get_audit_log()
        operations = [e["operation"] for e in log]
        assert "compost" in operations
        assert "forget" in operations

    @pytest.mark.asyncio
    async def test_batch_garden_retention(self) -> None:
        """Test retention policy on multiple garden entries."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=10,
                warm_days=30,
                compost_days=60,
            )
        )

        # Create entries of different ages
        entries = [
            ("fresh", 5, "tree"),  # Hot
            ("recent", 20, "tree"),  # Warm
            ("old", 45, "compost"),  # Compost
            ("ancient", 90, "compost"),  # Forget
        ]

        epochs = []
        signals_by_epoch = {}

        for name, days_ago, lifecycle in entries:
            entry = MockGardenEntry(
                id=name,
                content={"test": True},
                lifecycle=lifecycle,
                trust=0.5,
                planted_at=datetime.now() - timedelta(days=days_ago),
            )
            epoch = create_test_epoch_from_entry(entry)
            # Override sealed_at for testing
            epoch = LetheEpoch(
                epoch_id=epoch.epoch_id,
                created_at=entry.planted_at.isoformat(),
                sealed_at=(entry.planted_at + timedelta(hours=1)).isoformat(),
                signal_count=epoch.signal_count,
                signal_types=epoch.signal_types,
            )
            epochs.append(epoch)
            signals_by_epoch[epoch.epoch_id] = garden_entry_to_signals(entry)

        records = await store.apply_retention_policy(epochs, signals_by_epoch)

        # Fresh should not be processed (HOT)
        fresh_records = [r for r in records if "fresh" in r.epoch_id]
        assert len(fresh_records) == 0

        # Recent should be retained (WARM)
        recent_records = [r for r in records if "recent" in r.epoch_id]
        assert len(recent_records) == 1
        assert recent_records[0].operation == "retain"

        # Old should be composted
        old_record = store.get_record("garden-old")
        assert (
            old_record is not None or store.get_nutrient_block("garden-old") is not None
        )

        # Ancient should be forgotten (or composted first)
        ancient_record = store.get_record("garden-ancient")
        assert ancient_record is not None
