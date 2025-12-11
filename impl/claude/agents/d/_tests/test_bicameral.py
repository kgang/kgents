"""
Tests for Bicameral Memory.

Tests BicameralMemory, Ghost Detection, Self-Healing, and Coherency Protocol.
"""

# Mock the instance_db imports for testing
import sys
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Save original modules before mocking (for cleanup after import)
_original_interfaces = sys.modules.get("protocols.cli.instance_db.interfaces")
_original_nervous = sys.modules.get("protocols.cli.instance_db.nervous")
_original_hippocampus = sys.modules.get("protocols.cli.instance_db.hippocampus")
_original_synapse = sys.modules.get("protocols.cli.instance_db.synapse")

# Create mock modules
mock_interfaces = MagicMock()
mock_nervous = MagicMock()
mock_hippocampus = MagicMock()
mock_synapse = MagicMock()


@dataclass
class MockVectorSearchResult:
    id: str
    distance: float
    metadata: dict[str, Any]


class MockSignalPriority:
    CORTICAL = "cortical"
    FLASHBULB = "flashbulb"
    REFLEX = "reflex"


@dataclass
class MockSignal:
    signal_type: str
    data: dict[str, Any]
    timestamp: str = ""
    instance_id: str | None = None
    project_hash: str | None = None
    priority: Any = MockSignalPriority.CORTICAL
    surprise: float = 0.0


mock_interfaces.VectorSearchResult = MockVectorSearchResult
mock_interfaces.IRelationalStore = MagicMock()
mock_interfaces.IVectorStore = MagicMock()
mock_nervous.Signal = MockSignal
mock_nervous.SignalPriority = MockSignalPriority
mock_hippocampus.Hippocampus = MagicMock()
mock_hippocampus.ICortex = MagicMock()
mock_hippocampus.LetheEpoch = MagicMock()
mock_synapse.Synapse = MagicMock()

sys.modules["protocols.cli.instance_db.interfaces"] = mock_interfaces
sys.modules["protocols.cli.instance_db.nervous"] = mock_nervous
sys.modules["protocols.cli.instance_db.hippocampus"] = mock_hippocampus
sys.modules["protocols.cli.instance_db.synapse"] = mock_synapse

# Now import the module under test
from ..bicameral import (
    BicameralConfig,
    BicameralCortex,
    BicameralError,
    BicameralMemory,
    CoherencyReport,
    GhostRecord,
    HemisphereRole,
    StaleRecord,
    create_bicameral_cortex,
    create_bicameral_memory,
)
from ..infra_backends import (
    ContentHash,
)


# CRITICAL: Restore original modules immediately after import
# This prevents polluting the module cache for subsequent tests
def _restore(name, original):
    if original is not None:
        sys.modules[name] = original
    elif name in sys.modules:
        del sys.modules[name]


_restore("protocols.cli.instance_db.interfaces", _original_interfaces)
_restore("protocols.cli.instance_db.nervous", _original_nervous)
_restore("protocols.cli.instance_db.hippocampus", _original_hippocampus)
_restore("protocols.cli.instance_db.synapse", _original_synapse)

# ==============================================================================
# Test Fixtures
# ==============================================================================


class MockEmbeddingProvider:
    """Mock embedding provider for tests."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """Generate deterministic embedding from text hash."""
        # Simple hash-based embedding for deterministic tests
        h = hash(text) % 1000
        return [h / 1000.0] * self._dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions


class MockTelemetryLogger:
    """Mock telemetry logger that records events."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    async def log(self, event_type: str, data: dict[str, Any]) -> None:
        self.events.append((event_type, data))


# ==============================================================================
# BicameralConfig Tests
# ==============================================================================


class TestBicameralConfig:
    """Tests for BicameralConfig."""

    def test_defaults(self):
        """Default configuration values."""
        config = BicameralConfig()

        assert config.auto_heal_ghosts is True
        assert config.flag_stale_on_recall is True
        assert config.coherency_check_on_recall is True
        assert config.log_coherency_reports is True

    def test_custom_values(self):
        """Custom configuration values."""
        config = BicameralConfig(
            auto_heal_ghosts=False,
            staleness_threshold_hours=48.0,
            max_ghost_log=500,
        )

        assert config.auto_heal_ghosts is False
        assert config.staleness_threshold_hours == 48.0
        assert config.max_ghost_log == 500


# ==============================================================================
# HemisphereRole Tests
# ==============================================================================


class TestHemisphereRole:
    """Tests for HemisphereRole enum."""

    def test_values(self):
        """All hemisphere roles exist."""
        assert HemisphereRole.LEFT is not None
        assert HemisphereRole.RIGHT is not None
        assert HemisphereRole.BOTH is not None


# ==============================================================================
# GhostRecord Tests
# ==============================================================================


class TestGhostRecord:
    """Tests for GhostRecord."""

    def test_creation(self):
        """Create ghost record."""
        record = GhostRecord(
            ghost_id="ghost-001",
            detected_at="2025-01-01T00:00:00",
            healed_at="2025-01-01T00:00:01",
            context={"table": "shapes"},
        )

        assert record.ghost_id == "ghost-001"
        assert record.context["table"] == "shapes"


# ==============================================================================
# StaleRecord Tests
# ==============================================================================


class TestStaleRecord:
    """Tests for StaleRecord."""

    def test_creation(self):
        """Create stale record."""
        record = StaleRecord(
            id="stale-001",
            detected_at="2025-01-01T00:00:00",
            old_hash="abc123",
            new_hash="def456",
        )

        assert record.id == "stale-001"
        assert record.old_hash != record.new_hash
        assert record.re_embedded is False


# ==============================================================================
# CoherencyReport Tests
# ==============================================================================


class TestCoherencyReport:
    """Tests for CoherencyReport."""

    def test_coherency_rate_all_valid(self):
        """100% coherency when all valid."""
        report = CoherencyReport(
            total_checked=10,
            valid_count=10,
            ghost_count=0,
            stale_count=0,
            ghosts_healed=0,
            stale_flagged=0,
            duration_ms=100.0,
        )

        assert report.coherency_rate == 1.0

    def test_coherency_rate_with_issues(self):
        """Partial coherency with ghosts/stale."""
        report = CoherencyReport(
            total_checked=10,
            valid_count=7,
            ghost_count=2,
            stale_count=1,
            ghosts_healed=2,
            stale_flagged=1,
            duration_ms=100.0,
        )

        assert report.coherency_rate == 0.7

    def test_coherency_rate_empty(self):
        """100% coherency when nothing checked."""
        report = CoherencyReport(
            total_checked=0,
            valid_count=0,
            ghost_count=0,
            stale_count=0,
            ghosts_healed=0,
            stale_flagged=0,
            duration_ms=0.0,
        )

        assert report.coherency_rate == 1.0


# ==============================================================================
# BicameralMemory Tests
# ==============================================================================


class TestBicameralMemory:
    """Tests for BicameralMemory."""

    @pytest.fixture
    def mock_left(self):
        """Create mock Left Hemisphere (relational store)."""
        store = AsyncMock()
        store.execute = AsyncMock(return_value=1)
        store.fetch_one = AsyncMock(return_value=None)
        store.fetch_all = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def mock_right(self):
        """Create mock Right Hemisphere (vector store)."""
        store = AsyncMock()
        store.dimensions = 384
        store.upsert = AsyncMock()
        store.search = AsyncMock(return_value=[])
        store.delete = AsyncMock(return_value=True)
        store.count = AsyncMock(return_value=0)
        return store

    @pytest.fixture
    def embedder(self):
        """Create mock embedding provider."""
        return MockEmbeddingProvider()

    @pytest.fixture
    def telemetry(self):
        """Create mock telemetry logger."""
        return MockTelemetryLogger()

    @pytest.fixture
    def bicameral(self, mock_left, mock_right, embedder, telemetry):
        """Create BicameralMemory with mocks."""
        return BicameralMemory(
            left_hemisphere=mock_left,
            right_hemisphere=mock_right,
            embedding_provider=embedder,
            telemetry=telemetry,
        )

    # --- Basic Tests ---

    def test_has_semantic_true(self, bicameral):
        """has_semantic True when Right Hemisphere provided."""
        assert bicameral.has_semantic is True

    def test_has_semantic_false(self, mock_left):
        """has_semantic False without Right Hemisphere."""
        bicameral = BicameralMemory(left_hemisphere=mock_left)
        assert bicameral.has_semantic is False

    # --- Store Tests ---

    @pytest.mark.asyncio
    async def test_store_both_hemispheres(self, bicameral, mock_left, mock_right):
        """Store saves to both hemispheres."""
        result = await bicameral.store(
            id="insight-001",
            data={"type": "insight", "content": "test"},
        )

        assert result == "insight-001"
        mock_left.execute.assert_called()
        mock_right.upsert.assert_called()

    @pytest.mark.asyncio
    async def test_store_left_only(self, mock_left):
        """Store saves to Left only when no Right."""
        bicameral = BicameralMemory(left_hemisphere=mock_left)

        result = await bicameral.store(
            id="insight-001",
            data={"type": "insight"},
        )

        assert result == "insight-001"
        mock_left.execute.assert_called()

    @pytest.mark.asyncio
    async def test_store_with_embed_field(self, bicameral, mock_right):
        """Store uses specific field for embedding."""
        await bicameral.store(
            id="insight-001",
            data={"type": "insight", "summary": "important text"},
            embed_field="summary",
        )

        mock_right.upsert.assert_called()

    # --- Fetch Tests ---

    @pytest.mark.asyncio
    async def test_fetch_returns_data(self, bicameral, mock_left):
        """Fetch returns data from Left Hemisphere."""
        mock_left.fetch_one.return_value = {
            "id": "insight-001",
            "data": '{"type": "insight"}',
        }

        result = await bicameral.fetch("insight-001")

        assert result is not None
        assert result["id"] == "insight-001"

    @pytest.mark.asyncio
    async def test_fetch_not_found(self, bicameral, mock_left):
        """Fetch returns None when not found."""
        mock_left.fetch_one.return_value = None

        result = await bicameral.fetch("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_parses_json(self, bicameral, mock_left):
        """Fetch parses JSON data field."""
        mock_left.fetch_one.return_value = {
            "id": "insight-001",
            "data": '{"nested": {"key": "value"}}',
        }

        result = await bicameral.fetch("insight-001")

        assert result["data"]["nested"]["key"] == "value"

    # --- Delete Tests ---

    @pytest.mark.asyncio
    async def test_delete_both_hemispheres(self, bicameral, mock_left, mock_right):
        """Delete removes from both hemispheres."""
        result = await bicameral.delete("insight-001")

        assert result is True
        mock_left.execute.assert_called()
        mock_right.delete.assert_called_with("insight-001")

    # --- Recall Tests ---

    @pytest.mark.asyncio
    async def test_recall_requires_semantic(self, mock_left):
        """Recall raises error without semantic capability."""
        bicameral = BicameralMemory(left_hemisphere=mock_left)

        with pytest.raises(BicameralError):
            await bicameral.recall("test query")

    @pytest.mark.asyncio
    async def test_recall_empty_results(self, bicameral, mock_right):
        """Recall returns empty list when no matches."""
        mock_right.search.return_value = []

        results = await bicameral.recall("test query")

        assert results == []

    @pytest.mark.asyncio
    async def test_recall_with_valid_results(self, bicameral, mock_left, mock_right):
        """Recall returns validated results."""
        content_hash = ContentHash.compute({"type": "insight"}).hash_value

        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="insight-001",
                distance=0.1,
                metadata={
                    "relational_id": "insight-001",
                    "content_hash": content_hash,
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        mock_left.fetch_all.return_value = [
            {
                "id": "insight-001",
                "data": '{"type": "insight"}',
                "content_hash": content_hash,
            }
        ]

        results = await bicameral.recall("test query")

        assert len(results) == 1
        assert results[0].id == "insight-001"

    # --- Ghost Detection Tests ---

    @pytest.mark.asyncio
    async def test_recall_detects_ghost(
        self, bicameral, mock_left, mock_right, telemetry
    ):
        """Recall detects ghost memory."""
        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="ghost-001",
                distance=0.1,
                metadata={
                    "relational_id": "ghost-001",
                    "content_hash": "hash",
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        # No matching row - this is a ghost
        mock_left.fetch_all.return_value = []

        results = await bicameral.recall("test query")

        # Ghost should be filtered out
        assert len(results) == 0

        # Telemetry should log ghost healing
        healing_events = [e for e in telemetry.events if "ghost" in e[0]]
        assert len(healing_events) > 0

    @pytest.mark.asyncio
    async def test_recall_heals_ghost(self, bicameral, mock_left, mock_right):
        """Recall heals ghost memory."""
        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="ghost-001",
                distance=0.1,
                metadata={
                    "relational_id": "ghost-001",
                    "content_hash": "hash",
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        mock_left.fetch_all.return_value = []

        await bicameral.recall("test query")

        # Should have called delete on the ghost
        mock_right.delete.assert_called_with("ghost-001")

    @pytest.mark.asyncio
    async def test_recall_no_heal_when_disabled(self, mock_left, mock_right, embedder):
        """Recall doesn't heal ghosts when disabled."""
        config = BicameralConfig(auto_heal_ghosts=False)
        bicameral = BicameralMemory(
            left_hemisphere=mock_left,
            right_hemisphere=mock_right,
            embedding_provider=embedder,
            config=config,
        )

        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="ghost-001",
                distance=0.1,
                metadata={
                    "relational_id": "ghost-001",
                    "content_hash": "hash",
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        mock_left.fetch_all.return_value = []

        await bicameral.recall("test query")

        # Should NOT have called delete
        mock_right.delete.assert_not_called()

    # --- Staleness Detection Tests ---

    @pytest.mark.asyncio
    async def test_recall_detects_stale(self, bicameral, mock_left, mock_right):
        """Recall detects stale embedding."""
        old_hash = "old_hash_123"
        new_hash = "new_hash_456"

        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="stale-001",
                distance=0.1,
                metadata={
                    "relational_id": "stale-001",
                    "content_hash": old_hash,  # Old hash in vector
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        mock_left.fetch_all.return_value = [
            {
                "id": "stale-001",
                "data": '{"updated": true}',
                "content_hash": new_hash,  # New hash in relational
            }
        ]

        results = await bicameral.recall("test query")

        assert len(results) == 1
        assert results[0].is_stale is True

    # --- Coherency Check Tests ---

    @pytest.mark.asyncio
    async def test_coherency_check_empty(self, bicameral, mock_right):
        """Coherency check handles empty vector store."""
        mock_right.count.return_value = 0

        report = await bicameral.coherency_check()

        assert report.total_checked == 0
        assert report.coherency_rate == 1.0

    @pytest.mark.asyncio
    async def test_coherency_check_all_valid(self, bicameral, mock_left, mock_right):
        """Coherency check with all valid entries."""
        content_hash = ContentHash.compute({"type": "test"}).hash_value

        mock_right.count.return_value = 5
        mock_right.search.return_value = [
            MockVectorSearchResult(
                id=f"item-{i}",
                distance=0.1,
                metadata={
                    "relational_id": f"item-{i}",
                    "content_hash": content_hash,
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
            for i in range(5)
        ]

        mock_left.fetch_all.return_value = [
            {"id": f"item-{i}", "content_hash": content_hash} for i in range(5)
        ]

        report = await bicameral.coherency_check(sample_size=5)

        assert report.total_checked == 5
        assert report.valid_count == 5
        assert report.coherency_rate == 1.0

    # --- Ghost Log Tests ---

    def test_ghost_log_empty_initially(self, bicameral):
        """Ghost log starts empty."""
        assert len(bicameral.ghost_log) == 0

    @pytest.mark.asyncio
    async def test_ghost_log_records_healed(self, bicameral, mock_left, mock_right):
        """Ghost log records healed ghosts."""
        mock_right.search.return_value = [
            MockVectorSearchResult(
                id="ghost-001",
                distance=0.1,
                metadata={
                    "relational_id": "ghost-001",
                    "content_hash": "hash",
                    "created_at": "",
                    "updated_at": "",
                    "table": "memories",
                },
            )
        ]

        mock_left.fetch_all.return_value = []

        await bicameral.recall("test")

        assert len(bicameral.ghost_log) == 1
        assert bicameral.ghost_log[0].ghost_id == "ghost-001"

    # --- Statistics Tests ---

    def test_stats_initial(self, bicameral):
        """Initial stats are zero."""
        stats = bicameral.stats()

        assert stats["total_recalls"] == 0
        assert stats["ghosts_healed"] == 0
        assert stats["has_semantic"] is True

    @pytest.mark.asyncio
    async def test_stats_after_recall(self, bicameral, mock_left, mock_right):
        """Stats updated after recall."""
        mock_right.search.return_value = []

        await bicameral.recall("test")

        stats = bicameral.stats()
        assert stats["total_recalls"] == 1


# ==============================================================================
# BicameralCortex Tests
# ==============================================================================


class TestBicameralCortex:
    """Tests for BicameralCortex."""

    @pytest.fixture
    def mock_left(self):
        store = AsyncMock()
        store.execute = AsyncMock(return_value=1)
        store.fetch_one = AsyncMock(return_value=None)
        store.fetch_all = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def bicameral(self, mock_left):
        return BicameralMemory(left_hemisphere=mock_left)

    @pytest.fixture
    def cortex(self, bicameral):
        return BicameralCortex(bicameral=bicameral)

    @pytest.mark.asyncio
    async def test_store_signal(self, cortex, mock_left):
        """store_signal stores signal in BicameralMemory."""
        signal = MockSignal(
            signal_type="test.signal",
            data={"key": "value"},
            timestamp="2025-01-01T00:00:00",
        )

        result = await cortex.store_signal(signal)

        assert result is True
        mock_left.execute.assert_called()

    @pytest.mark.asyncio
    async def test_store_batch(self, cortex, mock_left):
        """store_batch stores multiple signals."""
        signals = [
            MockSignal(
                signal_type="test.signal",
                data={"index": i},
                timestamp=f"2025-01-01T00:00:0{i}",
            )
            for i in range(3)
        ]

        count = await cortex.store_batch(signals)

        assert count == 3


# ==============================================================================
# Factory Function Tests
# ==============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.fixture
    def mock_left(self):
        return AsyncMock()

    @pytest.fixture
    def mock_right(self):
        store = AsyncMock()
        store.dimensions = 384
        return store

    def test_create_bicameral_memory(self, mock_left, mock_right):
        """create_bicameral_memory creates instance."""
        bicameral = create_bicameral_memory(
            relational_store=mock_left,
            vector_store=mock_right,
            auto_heal_ghosts=False,
        )

        assert isinstance(bicameral, BicameralMemory)
        assert bicameral._config.auto_heal_ghosts is False

    def test_create_bicameral_cortex(self, mock_left):
        """create_bicameral_cortex creates instance."""
        bicameral = BicameralMemory(left_hemisphere=mock_left)
        cortex = create_bicameral_cortex(
            bicameral=bicameral,
            table="signals",
        )

        assert isinstance(cortex, BicameralCortex)
        assert cortex._table == "signals"
