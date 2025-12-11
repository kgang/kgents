"""
CompostBin: Memory Compression with Sketching-Based Statistics.

The CompostBin transforms detailed memories into compressed nutrient-rich
statistics. Like biological composting, it extracts essential nutrients
(insights) while reducing volume.

Components:
- NutrientBlock: Compressed statistics from memory decomposition
- CompostBin: Manages the composting process with sketching algorithms
- CompostingStrategy: Configurable compression strategies

Sketching Algorithms Used:
- Count-Min Sketch: Frequency estimation for event types
- HyperLogLog: Cardinality estimation for unique items
- T-Digest: Quantile estimation for numerical distributions

From the implementation plan:
> "Excess feeds the system's evolution" - The Accursed Share principle
> Nothing is truly deleted; deprecated ideas become nutrients for future growth.

Design Philosophy:
- Composting is not deletion - it's transformation
- Nutrients preserve essential statistical properties
- Sketches enable O(1) queries on historical data
- Memory is reclaimed while insights are preserved
"""

from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class CompostingError(Exception):
    """Error during composting operation."""


class SketchOverflowError(CompostingError):
    """Sketch data structure has overflowed."""


class CompostingStrategy(Enum):
    """Available composting strategies."""

    SKETCH = "sketch"  # Use sketching algorithms (default)
    AGGREGATE = "aggregate"  # Simple aggregations
    SAMPLE = "sample"  # Keep statistical samples
    HYBRID = "hybrid"  # Combination of above


@dataclass
class NutrientBlock:
    """
    Compressed statistics from composted memories.

    A NutrientBlock contains the "essence" of decomposed data:
    - Event type frequencies (approximate)
    - Unique value cardinalities (approximate)
    - Numerical distributions (quantiles)
    - Key-value patterns

    These nutrients enable historical queries without storing raw data.

    Usage:
        block = NutrientBlock(epoch_id="epoch-001", ...)

        # Query approximate frequency
        freq = block.get_frequency("signal.error")

        # Get approximate unique count
        unique = block.get_cardinality("instance_ids")

        # Get distribution quantile
        p95 = block.get_quantile("latency_ms", 0.95)
    """

    # Identity
    epoch_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sealed_at: str | None = None

    # Source metadata
    source_signal_count: int = 0
    source_epoch_ids: list[str] = field(default_factory=list)
    time_range_start: str | None = None
    time_range_end: str | None = None

    # Count-Min Sketch data (for frequency estimation)
    # Stored as: {key: min_count} for simplicity (actual CMS uses hash tables)
    frequency_sketch: dict[str, int] = field(default_factory=dict)

    # HyperLogLog data (for cardinality estimation)
    # Stored as: {field_name: estimated_cardinality}
    cardinality_sketch: dict[str, int] = field(default_factory=dict)

    # T-Digest data (for quantile estimation)
    # Stored as: {field_name: {quantile: value}}
    quantile_sketch: dict[str, dict[str, float]] = field(default_factory=dict)

    # Aggregations (exact when possible)
    sum_values: dict[str, float] = field(default_factory=dict)
    min_values: dict[str, float] = field(default_factory=dict)
    max_values: dict[str, float] = field(default_factory=dict)
    count_values: dict[str, int] = field(default_factory=dict)

    # Extracted concepts and lessons
    concepts: list[str] = field(default_factory=list)
    lessons: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    compression_ratio: float = 0.0  # Original size / compressed size

    def get_frequency(self, key: str) -> int:
        """Get approximate frequency for a key."""
        return self.frequency_sketch.get(key, 0)

    def get_cardinality(self, field_name: str) -> int:
        """Get approximate cardinality (unique count) for a field."""
        return self.cardinality_sketch.get(field_name, 0)

    def get_quantile(self, field_name: str, quantile: float) -> float | None:
        """
        Get estimated quantile value.

        Args:
            field_name: Name of the field
            quantile: Quantile to retrieve (0.0 to 1.0)

        Returns:
            Estimated value at quantile, or None if not available
        """
        if field_name not in self.quantile_sketch:
            return None
        quantiles = self.quantile_sketch[field_name]
        # Find closest stored quantile
        closest_key = min(
            quantiles.keys(),
            key=lambda q: abs(float(q) - quantile),
            default=None,
        )
        if closest_key is None:
            return None
        return quantiles[closest_key]

    def get_mean(self, field_name: str) -> float | None:
        """Get mean value for a field."""
        if field_name not in self.sum_values or field_name not in self.count_values:
            return None
        count = self.count_values[field_name]
        if count == 0:
            return None
        return self.sum_values[field_name] / count

    def merge(self, other: "NutrientBlock") -> "NutrientBlock":
        """
        Merge two NutrientBlocks into one.

        This enables hierarchical composting - multiple blocks
        can be merged into a single summary block.

        Args:
            other: NutrientBlock to merge with

        Returns:
            New merged NutrientBlock
        """
        merged = NutrientBlock(
            epoch_id=f"merged_{self.epoch_id}_{other.epoch_id}",
            source_signal_count=self.source_signal_count + other.source_signal_count,
            source_epoch_ids=self.source_epoch_ids + other.source_epoch_ids,
        )

        # Merge time ranges
        times = [
            t
            for t in [
                self.time_range_start,
                self.time_range_end,
                other.time_range_start,
                other.time_range_end,
            ]
            if t is not None
        ]
        if times:
            merged.time_range_start = min(times)
            merged.time_range_end = max(times)

        # Merge frequency sketches (add counts)
        for key, count in self.frequency_sketch.items():
            merged.frequency_sketch[key] = merged.frequency_sketch.get(key, 0) + count
        for key, count in other.frequency_sketch.items():
            merged.frequency_sketch[key] = merged.frequency_sketch.get(key, 0) + count

        # Merge cardinality sketches (max of estimates)
        for key in set(self.cardinality_sketch.keys()) | set(
            other.cardinality_sketch.keys()
        ):
            merged.cardinality_sketch[key] = max(
                self.cardinality_sketch.get(key, 0),
                other.cardinality_sketch.get(key, 0),
            )

        # Merge sum/count (add)
        for key in set(self.sum_values.keys()) | set(other.sum_values.keys()):
            merged.sum_values[key] = self.sum_values.get(
                key, 0.0
            ) + other.sum_values.get(key, 0.0)
        for key in set(self.count_values.keys()) | set(other.count_values.keys()):
            merged.count_values[key] = self.count_values.get(
                key, 0
            ) + other.count_values.get(key, 0)

        # Merge min/max
        for key in set(self.min_values.keys()) | set(other.min_values.keys()):
            vals = [
                v
                for v in [self.min_values.get(key), other.min_values.get(key)]
                if v is not None
            ]
            if vals:
                merged.min_values[key] = min(vals)
        for key in set(self.max_values.keys()) | set(other.max_values.keys()):
            vals = [
                v
                for v in [self.max_values.get(key), other.max_values.get(key)]
                if v is not None
            ]
            if vals:
                merged.max_values[key] = max(vals)

        # Merge concepts/lessons/tags (dedupe)
        merged.concepts = list(set(self.concepts + other.concepts))
        merged.lessons = list(set(self.lessons + other.lessons))
        merged.tags = list(set(self.tags + other.tags))

        return merged

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for storage."""
        return {
            "epoch_id": self.epoch_id,
            "created_at": self.created_at,
            "sealed_at": self.sealed_at,
            "source_signal_count": self.source_signal_count,
            "source_epoch_ids": self.source_epoch_ids,
            "time_range_start": self.time_range_start,
            "time_range_end": self.time_range_end,
            "frequency_sketch": self.frequency_sketch,
            "cardinality_sketch": self.cardinality_sketch,
            "quantile_sketch": self.quantile_sketch,
            "sum_values": self.sum_values,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "count_values": self.count_values,
            "concepts": self.concepts,
            "lessons": self.lessons,
            "tags": self.tags,
            "metadata": self.metadata,
            "compression_ratio": self.compression_ratio,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NutrientBlock":
        """Deserialize from dict."""
        return cls(
            epoch_id=data["epoch_id"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            sealed_at=data.get("sealed_at"),
            source_signal_count=data.get("source_signal_count", 0),
            source_epoch_ids=data.get("source_epoch_ids", []),
            time_range_start=data.get("time_range_start"),
            time_range_end=data.get("time_range_end"),
            frequency_sketch=data.get("frequency_sketch", {}),
            cardinality_sketch=data.get("cardinality_sketch", {}),
            quantile_sketch=data.get("quantile_sketch", {}),
            sum_values=data.get("sum_values", {}),
            min_values=data.get("min_values", {}),
            max_values=data.get("max_values", {}),
            count_values=data.get("count_values", {}),
            concepts=data.get("concepts", []),
            lessons=data.get("lessons", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            compression_ratio=data.get("compression_ratio", 0.0),
        )


class CountMinSketch:
    """
    Count-Min Sketch for frequency estimation.

    Provides approximate frequency counts with guaranteed error bounds.
    Space: O(width * depth)
    Query: O(depth)
    Update: O(depth)

    Error bound: frequency <= true_frequency + epsilon * N
    where epsilon = e / width and N = total count
    """

    def __init__(self, width: int = 1000, depth: int = 5):
        """
        Initialize Count-Min Sketch.

        Args:
            width: Number of counters per row (affects accuracy)
            depth: Number of hash functions (affects confidence)
        """
        self.width = width
        self.depth = depth
        self._table: list[list[int]] = [[0] * width for _ in range(depth)]
        self._total = 0

    def _hash(self, key: str, seed: int) -> int:
        """Hash function with seed."""
        h = hashlib.md5(f"{key}:{seed}".encode()).digest()
        return struct.unpack("<I", h[:4])[0] % self.width

    def add(self, key: str, count: int = 1) -> None:
        """Add count for key."""
        for i in range(self.depth):
            j = self._hash(key, i)
            self._table[i][j] += count
        self._total += count

    def estimate(self, key: str) -> int:
        """Estimate frequency of key (returns minimum across all hash positions)."""
        return min(self._table[i][self._hash(key, i)] for i in range(self.depth))

    @property
    def total(self) -> int:
        """Total count of all items."""
        return self._total

    def to_dict(self) -> dict[str, int]:
        """
        Export as simple frequency dict.

        Note: This loses sketch properties - use for final export only.
        """
        # We can't perfectly reconstruct keys, but we can export
        # the minimum estimate for all observed positions
        return {"__total__": self._total}


class HyperLogLog:
    """
    HyperLogLog for cardinality estimation.

    Estimates the number of unique items with ~2% error using O(1) space.

    Based on the observation that the position of the leftmost 1-bit
    in hash values follows a geometric distribution.
    """

    def __init__(self, precision: int = 14):
        """
        Initialize HyperLogLog.

        Args:
            precision: Number of bits for register index (4-18)
                      Higher = more accurate but more memory
        """
        self.precision = min(max(precision, 4), 18)
        self.m = 1 << self.precision  # Number of registers
        self._registers: list[int] = [0] * self.m
        self._count = 0

    def _hash(self, value: str) -> int:
        """64-bit hash of value."""
        h = hashlib.sha256(value.encode()).digest()
        return struct.unpack("<Q", h[:8])[0]

    def _leading_zeros(self, value: int, bits: int = 64) -> int:
        """Count leading zeros in binary representation."""
        if value == 0:
            return bits
        count = 0
        for i in range(bits - 1, -1, -1):
            if (value >> i) & 1:
                break
            count += 1
        return count

    def add(self, value: str) -> None:
        """Add a value to the set."""
        h = self._hash(value)
        # Use first 'precision' bits for register index
        register_index = h & (self.m - 1)
        # Use remaining bits for leading zero count
        remaining = h >> self.precision
        leading = self._leading_zeros(remaining, 64 - self.precision) + 1
        self._registers[register_index] = max(self._registers[register_index], leading)
        self._count += 1

    def estimate(self) -> int:
        """Estimate cardinality (number of unique items)."""
        # Harmonic mean of 2^register values
        alpha = self._alpha()
        indicator = sum(2 ** (-r) for r in self._registers)
        raw_estimate = alpha * self.m * self.m / indicator

        # Small range correction
        if raw_estimate <= 2.5 * self.m:
            zeros = self._registers.count(0)
            if zeros > 0:
                return int(self.m * math.log(self.m / zeros))

        # Large range correction
        if raw_estimate > (1 << 32) / 30:
            return int(-(1 << 32) * math.log(1 - raw_estimate / (1 << 32)))

        return int(raw_estimate)

    def _alpha(self) -> float:
        """Bias correction constant."""
        if self.m == 16:
            return 0.673
        if self.m == 32:
            return 0.697
        if self.m == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / self.m)

    @property
    def count(self) -> int:
        """Number of add operations (not unique count)."""
        return self._count


class TDigestSimplified:
    """
    Simplified T-Digest for quantile estimation.

    This is a simplified implementation that stores sampled centroids.
    For production, use the full T-Digest algorithm from tdigest library.
    """

    def __init__(self, max_centroids: int = 100):
        """
        Initialize T-Digest.

        Args:
            max_centroids: Maximum number of centroids to store
        """
        self.max_centroids = max_centroids
        self._centroids: list[tuple[float, int]] = []  # (mean, count)
        self._total = 0

    def add(self, value: float, count: int = 1) -> None:
        """Add value(s) to digest."""
        self._centroids.append((value, count))
        self._total += count

        # Merge if too many centroids
        if len(self._centroids) > self.max_centroids * 2:
            self._compress()

    def _compress(self) -> None:
        """Compress centroids by merging nearby ones."""
        if not self._centroids:
            return

        # Sort by mean
        self._centroids.sort(key=lambda c: c[0])

        # Merge adjacent centroids
        merged = []
        current_mean, current_count = self._centroids[0]

        for mean, count in self._centroids[1:]:
            if len(merged) < self.max_centroids - 1:
                # Weighted merge
                new_count = current_count + count
                current_mean = (current_mean * current_count + mean * count) / new_count
                current_count = new_count
            else:
                merged.append((current_mean, current_count))
                current_mean, current_count = mean, count

        merged.append((current_mean, current_count))
        self._centroids = merged

    def quantile(self, q: float) -> float | None:
        """
        Get estimated value at quantile q (0.0 to 1.0).

        Args:
            q: Quantile (e.g., 0.5 for median, 0.95 for p95)

        Returns:
            Estimated value at quantile
        """
        if not self._centroids or self._total == 0:
            return None

        if q <= 0:
            return min(c[0] for c in self._centroids)
        if q >= 1:
            return max(c[0] for c in self._centroids)

        # Sort centroids by mean
        sorted_centroids = sorted(self._centroids, key=lambda c: c[0])

        # Find the centroid containing the target quantile
        target_count = q * self._total
        cumulative = 0

        for i, (mean, count) in enumerate(sorted_centroids):
            cumulative += count
            if cumulative >= target_count:
                if i == 0:
                    return mean
                # Linear interpolation
                prev_mean, prev_count = sorted_centroids[i - 1]
                weight = (target_count - (cumulative - count)) / count
                return prev_mean + weight * (mean - prev_mean)

        return sorted_centroids[-1][0]

    def standard_quantiles(self) -> dict[str, float]:
        """Get standard quantiles (p50, p75, p90, p95, p99)."""
        return {
            "0.5": self.quantile(0.5) or 0.0,
            "0.75": self.quantile(0.75) or 0.0,
            "0.9": self.quantile(0.9) or 0.0,
            "0.95": self.quantile(0.95) or 0.0,
            "0.99": self.quantile(0.99) or 0.0,
        }

    @property
    def total(self) -> int:
        """Total count."""
        return self._total


@dataclass
class CompostConfig:
    """Configuration for CompostBin."""

    # Strategy
    strategy: CompostingStrategy = CompostingStrategy.SKETCH

    # Sketch parameters
    cms_width: int = 1000  # Count-Min Sketch width
    cms_depth: int = 5  # Count-Min Sketch depth
    hll_precision: int = 14  # HyperLogLog precision (4-18)
    tdigest_centroids: int = 100  # T-Digest max centroids

    # Fields to track
    frequency_fields: list[str] = field(default_factory=lambda: ["signal_type"])
    cardinality_fields: list[str] = field(default_factory=lambda: ["instance_id"])
    quantile_fields: list[str] = field(default_factory=lambda: ["surprise"])

    # Aggregation
    sum_fields: list[str] = field(default_factory=list)

    # Retention
    min_signals_to_compost: int = 100  # Don't compost epochs with few signals
    max_nutrient_blocks: int = 1000  # Max blocks to keep

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompostConfig":
        """Create from dict."""
        strategy = data.get("strategy", "sketch")
        if isinstance(strategy, str):
            strategy = CompostingStrategy(strategy)
        return cls(
            strategy=strategy,
            cms_width=data.get("cms_width", 1000),
            cms_depth=data.get("cms_depth", 5),
            hll_precision=data.get("hll_precision", 14),
            tdigest_centroids=data.get("tdigest_centroids", 100),
            frequency_fields=data.get("frequency_fields", ["signal_type"]),
            cardinality_fields=data.get("cardinality_fields", ["instance_id"]),
            quantile_fields=data.get("quantile_fields", ["surprise"]),
            sum_fields=data.get("sum_fields", []),
            min_signals_to_compost=data.get("min_signals_to_compost", 100),
            max_nutrient_blocks=data.get("max_nutrient_blocks", 1000),
        )


@runtime_checkable
class ICompostable(Protocol):
    """Protocol for data that can be composted."""

    @property
    def signal_type(self) -> str:
        """Type of signal."""
        ...

    @property
    def data(self) -> dict[str, Any]:
        """Signal data."""
        ...

    @property
    def timestamp(self) -> str:
        """Signal timestamp."""
        ...


class CompostBin:
    """
    Memory Compression via Sketching.

    The CompostBin transforms detailed signal data into compressed
    NutrientBlocks using sketching algorithms. This enables:
    - O(1) space for historical queries
    - Approximate frequency/cardinality/quantile queries
    - Memory reclamation while preserving insights

    Usage:
        bin = CompostBin()

        # Add signals to compost
        for signal in signals:
            bin.add(signal)

        # Seal and create nutrient block
        block = bin.seal(epoch_id="epoch-001")

        # Query the block
        freq = block.get_frequency("signal.error")
        unique_instances = block.get_cardinality("instance_id")
        p95_latency = block.get_quantile("latency_ms", 0.95)
    """

    def __init__(self, config: CompostConfig | None = None):
        """
        Initialize CompostBin.

        Args:
            config: Composting configuration
        """
        self._config = config or CompostConfig()

        # Initialize sketches
        self._frequency_sketches: dict[str, CountMinSketch] = {}
        self._cardinality_sketches: dict[str, HyperLogLog] = {}
        self._quantile_sketches: dict[str, TDigestSimplified] = {}

        # Initialize aggregations
        self._sums: dict[str, float] = {}
        self._mins: dict[str, float] = {}
        self._maxs: dict[str, float] = {}
        self._counts: dict[str, int] = {}

        # Tracking
        self._signal_count = 0
        self._signal_types: set[str] = set()
        self._timestamps: list[str] = []
        self._concepts: list[str] = []
        self._tags: set[str] = set()
        self._created_at = datetime.now().isoformat()

        # Initialize sketches for configured fields
        for field_name in self._config.frequency_fields:
            self._frequency_sketches[field_name] = CountMinSketch(
                width=self._config.cms_width,
                depth=self._config.cms_depth,
            )
        for field_name in self._config.cardinality_fields:
            self._cardinality_sketches[field_name] = HyperLogLog(
                precision=self._config.hll_precision
            )
        for field_name in self._config.quantile_fields:
            self._quantile_sketches[field_name] = TDigestSimplified(
                max_centroids=self._config.tdigest_centroids
            )

    @property
    def config(self) -> CompostConfig:
        """Get configuration."""
        return self._config

    @property
    def signal_count(self) -> int:
        """Number of signals added."""
        return self._signal_count

    @property
    def signal_types(self) -> set[str]:
        """Set of signal types seen."""
        return self._signal_types.copy()

    def add(self, signal: ICompostable) -> None:
        """
        Add a signal to the compost bin.

        Extracts and tracks statistics from the signal.

        Args:
            signal: Compostable signal data
        """
        self._signal_count += 1
        self._signal_types.add(signal.signal_type)
        self._timestamps.append(signal.timestamp)

        data = signal.data

        # Update frequency sketches
        for field_name, sketch in self._frequency_sketches.items():
            if field_name == "signal_type":
                sketch.add(signal.signal_type)
            elif field_name in data:
                sketch.add(str(data[field_name]))

        # Update cardinality sketches
        for field_name, sketch in self._cardinality_sketches.items():
            if field_name in data:
                sketch.add(str(data[field_name]))

        # Update quantile sketches
        for field_name, sketch in self._quantile_sketches.items():
            if field_name in data:
                value = data[field_name]
                if isinstance(value, (int, float)):
                    sketch.add(float(value))

        # Update aggregations
        for field_name in self._config.sum_fields:
            if field_name in data:
                value = data[field_name]
                if isinstance(value, (int, float)):
                    self._sums[field_name] = self._sums.get(field_name, 0.0) + value
                    self._counts[field_name] = self._counts.get(field_name, 0) + 1
                    if field_name not in self._mins:
                        self._mins[field_name] = value
                    else:
                        self._mins[field_name] = min(self._mins[field_name], value)
                    if field_name not in self._maxs:
                        self._maxs[field_name] = value
                    else:
                        self._maxs[field_name] = max(self._maxs[field_name], value)

        # Extract tags from data
        if "tags" in data and isinstance(data["tags"], list):
            self._tags.update(data["tags"])

    def add_batch(self, signals: list[ICompostable]) -> int:
        """
        Add multiple signals efficiently.

        Args:
            signals: List of signals to compost

        Returns:
            Number of signals added
        """
        for signal in signals:
            self.add(signal)
        return len(signals)

    def seal(
        self,
        epoch_id: str,
        concepts: list[str] | None = None,
        lessons: list[str] | None = None,
    ) -> NutrientBlock:
        """
        Seal the compost bin and create a NutrientBlock.

        This finalizes the composting process and creates
        a compressed summary of all added signals.

        Args:
            epoch_id: Identifier for this epoch
            concepts: Extracted concepts
            lessons: Lessons learned from this data

        Returns:
            Sealed NutrientBlock
        """
        sealed_at = datetime.now().isoformat()

        # Calculate compression ratio
        estimated_original_size = self._signal_count * 500  # ~500 bytes per signal
        estimated_compressed_size = 1000 + len(self._frequency_sketches) * 100
        compression_ratio = (
            estimated_original_size / estimated_compressed_size
            if estimated_compressed_size > 0
            else 1.0
        )

        # Build frequency dict from sketches
        frequency_dict = {}
        for field_name, sketch in self._frequency_sketches.items():
            for signal_type in self._signal_types:
                key = f"{field_name}:{signal_type}"
                frequency_dict[key] = sketch.estimate(signal_type)

        # Build cardinality dict
        cardinality_dict = {
            field_name: sketch.estimate()
            for field_name, sketch in self._cardinality_sketches.items()
        }

        # Build quantile dict
        quantile_dict = {
            field_name: sketch.standard_quantiles()
            for field_name, sketch in self._quantile_sketches.items()
        }

        # Calculate time range
        time_range_start = min(self._timestamps) if self._timestamps else None
        time_range_end = max(self._timestamps) if self._timestamps else None

        block = NutrientBlock(
            epoch_id=epoch_id,
            created_at=self._created_at,
            sealed_at=sealed_at,
            source_signal_count=self._signal_count,
            source_epoch_ids=[epoch_id],
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            frequency_sketch=frequency_dict,
            cardinality_sketch=cardinality_dict,
            quantile_sketch=quantile_dict,
            sum_values=self._sums.copy(),
            min_values=self._mins.copy(),
            max_values=self._maxs.copy(),
            count_values=self._counts.copy(),
            concepts=concepts or self._concepts,
            lessons=lessons or [],
            tags=list(self._tags),
            compression_ratio=compression_ratio,
        )

        # Reset state
        self._reset()

        return block

    def _reset(self) -> None:
        """Reset the bin for new composting."""
        # Reinitialize sketches
        for field_name in self._config.frequency_fields:
            self._frequency_sketches[field_name] = CountMinSketch(
                width=self._config.cms_width,
                depth=self._config.cms_depth,
            )
        for field_name in self._config.cardinality_fields:
            self._cardinality_sketches[field_name] = HyperLogLog(
                precision=self._config.hll_precision
            )
        for field_name in self._config.quantile_fields:
            self._quantile_sketches[field_name] = TDigestSimplified(
                max_centroids=self._config.tdigest_centroids
            )

        # Reset aggregations
        self._sums.clear()
        self._mins.clear()
        self._maxs.clear()
        self._counts.clear()

        # Reset tracking
        self._signal_count = 0
        self._signal_types.clear()
        self._timestamps.clear()
        self._concepts.clear()
        self._tags.clear()
        self._created_at = datetime.now().isoformat()

    def stats(self) -> dict[str, Any]:
        """Get current bin statistics."""
        return {
            "signal_count": self._signal_count,
            "signal_types": list(self._signal_types),
            "frequency_fields": list(self._frequency_sketches.keys()),
            "cardinality_fields": list(self._cardinality_sketches.keys()),
            "quantile_fields": list(self._quantile_sketches.keys()),
            "created_at": self._created_at,
        }


# Factory functions


def create_compost_bin(config_dict: dict[str, Any] | None = None) -> CompostBin:
    """
    Create a CompostBin with optional configuration.

    Args:
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured CompostBin
    """
    config = CompostConfig.from_dict(config_dict) if config_dict else CompostConfig()
    return CompostBin(config=config)


def create_nutrient_block(
    epoch_id: str,
    signals: list[ICompostable],
    config: CompostConfig | None = None,
) -> NutrientBlock:
    """
    Create a NutrientBlock from signals in one step.

    Args:
        epoch_id: Epoch identifier
        signals: Signals to compost
        config: Composting configuration

    Returns:
        Sealed NutrientBlock
    """
    bin = CompostBin(config=config)
    bin.add_batch(signals)
    return bin.seal(epoch_id)
