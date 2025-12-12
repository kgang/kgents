"""
Tests for CompostBin and NutrientBlock.

These tests verify:
- Sketching algorithms (Count-Min, HyperLogLog, T-Digest)
- NutrientBlock creation and queries
- CompostBin signal processing
- Block merging
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

from ..compost import (
    CompostBin,
    CompostConfig,
    CompostingStrategy,
    CountMinSketch,
    HyperLogLog,
    ICompostable,
    NutrientBlock,
    TDigestSimplified,
    create_compost_bin,
    create_nutrient_block,
)

# === Test Fixtures ===


@dataclass
class MockSignal:
    """Mock signal for testing."""

    signal_type: str
    data: dict[str, Any]
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


def create_test_signals(count: int = 100) -> list[MockSignal]:
    """Create test signals with varied data."""
    signals = []
    for i in range(count):
        signals.append(
            MockSignal(
                signal_type=f"type_{i % 5}",  # 5 types
                data={
                    "instance_id": f"instance_{i % 10}",  # 10 instances
                    "surprise": 0.1 + (i % 10) * 0.1,  # 0.1 to 1.0
                    "latency_ms": 10 + i,
                    "tags": [f"tag_{i % 3}"],
                },
            )
        )
    return signals


# === Count-Min Sketch Tests ===


class TestCountMinSketch:
    """Tests for Count-Min Sketch."""

    def test_basic_counting(self) -> None:
        """Test basic frequency counting."""
        sketch = CountMinSketch(width=100, depth=3)

        sketch.add("apple", 5)
        sketch.add("banana", 3)
        sketch.add("apple", 2)

        assert sketch.estimate("apple") >= 7  # May overcount, never undercount
        assert sketch.estimate("banana") >= 3
        assert sketch.total == 10

    def test_unknown_key_zero(self) -> None:
        """Test that unknown keys return reasonable estimate."""
        sketch = CountMinSketch()
        # Unknown key should return 0 or small value
        estimate = sketch.estimate("never_added")
        assert estimate >= 0  # Non-negative

    def test_collision_overcount(self) -> None:
        """Test that collisions cause overcounting, not undercounting."""
        sketch = CountMinSketch(width=10, depth=2)  # Small, more collisions

        for i in range(100):
            sketch.add(f"key_{i}")

        # Each key was added once, but estimate may be higher due to collisions
        for i in range(100):
            assert sketch.estimate(f"key_{i}") >= 1

    def test_high_volume(self) -> None:
        """Test with high volume of items."""
        sketch = CountMinSketch(width=1000, depth=5)

        # Add many items
        for i in range(10000):
            sketch.add(f"item_{i % 100}", 1)

        # Each of 100 items was added 100 times
        assert sketch.total == 10000

        # Estimates should be close to 100 for each
        for i in range(100):
            estimate = sketch.estimate(f"item_{i}")
            assert estimate >= 100  # At least the true count


class TestHyperLogLog:
    """Tests for HyperLogLog cardinality estimation."""

    def test_basic_cardinality(self) -> None:
        """Test basic unique count estimation."""
        hll = HyperLogLog(precision=14)

        # Add 1000 unique items
        for i in range(1000):
            hll.add(f"item_{i}")

        estimate = hll.estimate()
        # HyperLogLog has ~2% error, so expect 900-1100
        assert 800 <= estimate <= 1200

    def test_duplicate_handling(self) -> None:
        """Test that duplicates don't affect cardinality."""
        hll = HyperLogLog()

        # Add same items multiple times
        for _ in range(10):
            for i in range(100):
                hll.add(f"item_{i}")

        estimate = hll.estimate()
        # Should still estimate ~100 unique items
        assert 80 <= estimate <= 130

    def test_low_cardinality(self) -> None:
        """Test with small number of unique items."""
        hll = HyperLogLog()

        for i in range(10):
            hll.add(f"item_{i}")

        estimate = hll.estimate()
        # Low cardinality correction should apply
        assert 5 <= estimate <= 20

    def test_empty_hll(self) -> None:
        """Test empty HyperLogLog."""
        hll = HyperLogLog()
        # Empty HLL should return 0 (or small number due to correction)
        assert hll.estimate() >= 0


class TestTDigest:
    """Tests for T-Digest quantile estimation."""

    def test_basic_quantiles(self) -> None:
        """Test basic quantile estimation."""
        digest = TDigestSimplified()

        # Add values 1-100
        for i in range(1, 101):
            digest.add(float(i))

        # Median should be ~50
        median = digest.quantile(0.5)
        assert median is not None
        assert 40 <= median <= 60

        # P90 should be ~90
        p90 = digest.quantile(0.9)
        assert p90 is not None
        assert 80 <= p90 <= 100

    def test_extreme_quantiles(self) -> None:
        """Test extreme quantiles (min/max)."""
        digest = TDigestSimplified()

        for i in range(1, 101):
            digest.add(float(i))

        assert digest.quantile(0.0) == 1.0
        assert digest.quantile(1.0) == 100.0

    def test_standard_quantiles(self) -> None:
        """Test standard quantile extraction."""
        digest = TDigestSimplified()

        for i in range(1, 101):
            digest.add(float(i))

        quantiles = digest.standard_quantiles()
        assert "0.5" in quantiles
        assert "0.95" in quantiles
        assert "0.99" in quantiles

    def test_empty_digest(self) -> None:
        """Test empty digest."""
        digest = TDigestSimplified()
        assert digest.quantile(0.5) is None

    def test_compression(self) -> None:
        """Test that compression keeps reasonable accuracy."""
        digest = TDigestSimplified(max_centroids=10)

        # Add many values to force compression
        for i in range(10000):
            digest.add(float(i))

        # Should still get reasonable estimates
        median = digest.quantile(0.5)
        assert median is not None
        assert 4000 <= median <= 6000


# === NutrientBlock Tests ===


class TestNutrientBlock:
    """Tests for NutrientBlock."""

    def test_basic_creation(self) -> None:
        """Test basic block creation."""
        block = NutrientBlock(
            epoch_id="test-epoch",
            source_signal_count=100,
        )
        assert block.epoch_id == "test-epoch"
        assert block.source_signal_count == 100

    def test_frequency_query(self) -> None:
        """Test frequency querying."""
        block = NutrientBlock(
            epoch_id="test",
            frequency_sketch={"type_0": 50, "type_1": 30},
        )
        assert block.get_frequency("type_0") == 50
        assert block.get_frequency("unknown") == 0

    def test_cardinality_query(self) -> None:
        """Test cardinality querying."""
        block = NutrientBlock(
            epoch_id="test",
            cardinality_sketch={"instance_id": 10},
        )
        assert block.get_cardinality("instance_id") == 10
        assert block.get_cardinality("unknown") == 0

    def test_quantile_query(self) -> None:
        """Test quantile querying."""
        block = NutrientBlock(
            epoch_id="test",
            quantile_sketch={"latency": {"0.5": 50.0, "0.95": 95.0}},
        )
        assert block.get_quantile("latency", 0.5) == 50.0
        assert block.get_quantile("latency", 0.95) == 95.0
        assert block.get_quantile("unknown", 0.5) is None

    def test_mean_calculation(self) -> None:
        """Test mean calculation from sum/count."""
        block = NutrientBlock(
            epoch_id="test",
            sum_values={"value": 500.0},
            count_values={"value": 10},
        )
        assert block.get_mean("value") == 50.0
        assert block.get_mean("unknown") is None

    def test_merge(self) -> None:
        """Test merging two blocks."""
        block1 = NutrientBlock(
            epoch_id="epoch-1",
            source_signal_count=100,
            frequency_sketch={"type_a": 50},
            cardinality_sketch={"id": 10},
            sum_values={"val": 100.0},
            count_values={"val": 10},
            concepts=["concept1"],
        )
        block2 = NutrientBlock(
            epoch_id="epoch-2",
            source_signal_count=200,
            frequency_sketch={"type_a": 30, "type_b": 20},
            cardinality_sketch={"id": 15},
            sum_values={"val": 200.0},
            count_values={"val": 20},
            concepts=["concept2"],
        )

        merged = block1.merge(block2)

        assert merged.source_signal_count == 300
        assert merged.get_frequency("type_a") == 80
        assert merged.get_frequency("type_b") == 20
        assert merged.get_cardinality("id") == 15  # Max
        assert merged.get_mean("val") == 10.0  # 300/30
        assert set(merged.concepts) == {"concept1", "concept2"}

    def test_serialization(self) -> None:
        """Test dict serialization roundtrip."""
        block = NutrientBlock(
            epoch_id="test",
            source_signal_count=100,
            frequency_sketch={"type_a": 50},
            concepts=["test"],
        )

        data = block.to_dict()
        restored = NutrientBlock.from_dict(data)

        assert restored.epoch_id == block.epoch_id
        assert restored.source_signal_count == block.source_signal_count
        assert restored.get_frequency("type_a") == 50


# === CompostBin Tests ===


class TestCompostBin:
    """Tests for CompostBin."""

    def test_basic_composting(self) -> None:
        """Test basic signal composting."""
        bin = CompostBin()
        signals = create_test_signals(100)

        for signal in signals:
            bin.add(signal)

        assert bin.signal_count == 100
        assert len(bin.signal_types) == 5  # type_0 to type_4

    def test_seal_creates_block(self) -> None:
        """Test that sealing creates a valid block."""
        bin = CompostBin()
        signals = create_test_signals(100)
        bin.add_batch(cast(list[ICompostable], signals))

        block = bin.seal("test-epoch")

        assert block.epoch_id == "test-epoch"
        assert block.source_signal_count == 100
        assert block.sealed_at is not None
        assert block.compression_ratio > 0

    def test_frequency_tracking(self) -> None:
        """Test frequency tracking in composting."""
        config = CompostConfig(frequency_fields=["signal_type"])
        bin = CompostBin(config=config)

        # Add signals with known type distribution
        for i in range(100):
            bin.add(
                MockSignal(
                    signal_type="type_a" if i < 70 else "type_b",
                    data={},
                )
            )

        block = bin.seal("test")

        # Check frequency estimates
        freq_a = block.get_frequency("signal_type:type_a")
        freq_b = block.get_frequency("signal_type:type_b")

        assert freq_a >= 70
        assert freq_b >= 30

    def test_cardinality_tracking(self) -> None:
        """Test cardinality tracking."""
        config = CompostConfig(cardinality_fields=["user_id"])
        bin = CompostBin(config=config)

        # Add signals with 10 unique users
        for i in range(100):
            bin.add(
                MockSignal(
                    signal_type="test",
                    data={"user_id": f"user_{i % 10}"},
                )
            )

        block = bin.seal("test")

        # Check cardinality estimate (10 unique users)
        cardinality = block.get_cardinality("user_id")
        assert 8 <= cardinality <= 15  # ~10 with HLL error

    def test_quantile_tracking(self) -> None:
        """Test quantile tracking."""
        config = CompostConfig(quantile_fields=["latency"])
        bin = CompostBin(config=config)

        # Add signals with latencies 1-100
        for i in range(1, 101):
            bin.add(
                MockSignal(
                    signal_type="test",
                    data={"latency": float(i)},
                )
            )

        block = bin.seal("test")

        # Check quantile estimates
        median = block.get_quantile("latency", 0.5)
        assert median is not None
        assert 40 <= median <= 60

    def test_aggregation_tracking(self) -> None:
        """Test sum/min/max aggregation."""
        config = CompostConfig(sum_fields=["duration"])
        bin = CompostBin(config=config)

        for i in range(10):
            bin.add(
                MockSignal(
                    signal_type="test",
                    data={"duration": float(i + 1)},  # 1-10
                )
            )

        block = bin.seal("test")

        assert block.sum_values.get("duration") == 55.0  # 1+2+...+10
        assert block.min_values.get("duration") == 1.0
        assert block.max_values.get("duration") == 10.0
        assert block.get_mean("duration") == 5.5

    def test_reset_after_seal(self) -> None:
        """Test that bin resets after sealing."""
        bin = CompostBin()
        bin.add_batch(cast(list[ICompostable], create_test_signals(50)))
        bin.seal("epoch-1")

        assert bin.signal_count == 0
        assert len(bin.signal_types) == 0

    def test_tag_extraction(self) -> None:
        """Test tag extraction from signals."""
        bin = CompostBin()

        bin.add(MockSignal("test", {"tags": ["alpha", "beta"]}))
        bin.add(MockSignal("test", {"tags": ["beta", "gamma"]}))

        block = bin.seal("test")

        assert set(block.tags) == {"alpha", "beta", "gamma"}

    def test_stats(self) -> None:
        """Test statistics reporting."""
        bin = CompostBin()
        bin.add_batch(cast(list[ICompostable], create_test_signals(50)))

        stats = bin.stats()

        assert stats["signal_count"] == 50
        assert "frequency_fields" in stats
        assert "cardinality_fields" in stats


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_compost_bin(self) -> None:
        """Test create_compost_bin factory."""
        bin = create_compost_bin()
        assert bin is not None
        assert bin.config.strategy == CompostingStrategy.SKETCH

    def test_create_compost_bin_with_config(self) -> None:
        """Test create_compost_bin with config dict."""
        bin = create_compost_bin(
            {
                "strategy": "aggregate",
                "cms_width": 500,
            }
        )
        assert bin.config.strategy == CompostingStrategy.AGGREGATE
        assert bin.config.cms_width == 500

    def test_create_nutrient_block(self) -> None:
        """Test create_nutrient_block convenience function."""
        signals = create_test_signals(100)
        block = create_nutrient_block("test-epoch", cast(list[ICompostable], signals))

        assert block.epoch_id == "test-epoch"
        assert block.source_signal_count == 100


# === Integration Tests ===


class TestCompostIntegration:
    """Integration tests for composting workflow."""

    def test_full_workflow(self) -> None:
        """Test complete composting workflow."""
        # Create signals
        signals = create_test_signals(1000)

        # Compost
        bin = CompostBin()
        bin.add_batch(cast(list[ICompostable], signals))
        block1 = bin.seal("epoch-1")

        # More signals
        more_signals = create_test_signals(500)
        bin.add_batch(cast(list[ICompostable], more_signals))
        block2 = bin.seal("epoch-2")

        # Merge blocks
        merged = block1.merge(block2)

        assert merged.source_signal_count == 1500
        assert len(merged.source_epoch_ids) == 2

    def test_time_range_tracking(self) -> None:
        """Test time range is captured correctly."""
        bin = CompostBin()

        # Add signals with different timestamps
        bin.add(MockSignal("test", {}, timestamp="2025-01-01T00:00:00"))
        bin.add(MockSignal("test", {}, timestamp="2025-01-15T00:00:00"))
        bin.add(MockSignal("test", {}, timestamp="2025-01-10T00:00:00"))

        block = bin.seal("test")

        assert block.time_range_start == "2025-01-01T00:00:00"
        assert block.time_range_end == "2025-01-15T00:00:00"
