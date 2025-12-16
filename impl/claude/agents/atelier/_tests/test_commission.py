"""
Tests for the commission queue module.

Tests async queue with persistence.
"""

import json
from pathlib import Path

import pytest
from agents.atelier.artisan import Commission
from agents.atelier.workshop.commission import (
    CommissionQueue,
    QueuedCommission,
    QueueStatus,
)


class TestQueuedCommission:
    """Tests for QueuedCommission dataclass."""

    def test_create(self):
        """Basic creation."""
        commission = Commission(request="test", patron="alice")
        queued = QueuedCommission(
            commission=commission,
            artisan_name="calligrapher",
        )
        assert queued.artisan_name == "calligrapher"
        assert queued.commission.request == "test"
        assert queued.status == QueueStatus.PENDING

    def test_to_dict(self):
        """Serialization to dict."""
        commission = Commission(request="test", patron="alice")
        queued = QueuedCommission(
            commission=commission,
            artisan_name="calligrapher",
        )
        d = queued.to_dict()
        assert d["artisan_name"] == "calligrapher"
        assert d["commission"]["request"] == "test"
        assert d["status"] == "pending"

    def test_from_dict(self):
        """Deserialization from dict."""
        d = {
            "artisan_name": "cartographer",
            "commission": {
                "id": "test-id",
                "request": "map something",
                "patron": "bob",
                "created_at": "2024-01-01T00:00:00",
                "context": {},
            },
            "status": "pending",
            "piece_id": None,
            "error": None,
            "queued_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        queued = QueuedCommission.from_dict(d)
        assert queued.artisan_name == "cartographer"
        assert queued.commission.request == "map something"
        assert queued.status == QueueStatus.PENDING


class TestCommissionQueue:
    """Tests for CommissionQueue persistence."""

    @pytest.fixture
    def queue(self, tmp_path):
        return CommissionQueue(tmp_path / "queue")

    async def test_enqueue(self, queue):
        """Enqueue adds to pending."""
        commission = Commission(request="test", patron="alice")
        queued = await queue.enqueue(commission, "calligrapher")

        assert queued.artisan_name == "calligrapher"
        assert queued.status == QueueStatus.PENDING

    async def test_enqueue_persists(self, queue):
        """Enqueue persists to file."""
        commission = Commission(request="test", patron="alice")
        await queue.enqueue(commission, "calligrapher")

        # Verify file exists
        path = queue.storage_path / f"{commission.id}.json"
        assert path.exists()

        # Verify contents
        data = json.loads(path.read_text())
        assert data["artisan_name"] == "calligrapher"

    async def test_pending_returns_pending_only(self, queue):
        """pending() returns only pending commissions."""
        c1 = Commission(request="first", patron="alice")
        c2 = Commission(request="second", patron="bob")
        await queue.enqueue(c1, "calligrapher")
        await queue.enqueue(c2, "cartographer")

        # Mark first as complete
        await queue.update_status(c1.id, QueueStatus.COMPLETE)

        pending = await queue.pending()
        assert len(pending) == 1
        assert pending[0].commission.request == "second"

    async def test_get(self, queue):
        """Get retrieves by ID."""
        commission = Commission(request="test", patron="alice")
        await queue.enqueue(commission, "calligrapher")

        queued = await queue.get(commission.id)
        assert queued is not None
        assert queued.commission.request == "test"

    async def test_get_nonexistent(self, queue):
        """Get returns None for missing ID."""
        queued = await queue.get("nonexistent-id")
        assert queued is None

    async def test_update_status(self, queue):
        """Update status modifies the entry."""
        commission = Commission(request="test", patron="alice")
        await queue.enqueue(commission, "calligrapher")

        await queue.update_status(
            commission.id, QueueStatus.COMPLETE, piece_id="piece-123"
        )

        queued = await queue.get(commission.id)
        assert queued.status == QueueStatus.COMPLETE
        assert queued.piece_id == "piece-123"
        assert queued.completed_at is not None

    async def test_update_status_with_error(self, queue):
        """Update status can record errors."""
        commission = Commission(request="test", patron="alice")
        await queue.enqueue(commission, "calligrapher")

        await queue.update_status(
            commission.id, QueueStatus.FAILED, error="Something went wrong"
        )

        queued = await queue.get(commission.id)
        assert queued.status == QueueStatus.FAILED
        assert queued.error == "Something went wrong"


class TestQueueOrdering:
    """Tests for queue ordering."""

    @pytest.fixture
    def queue(self, tmp_path):
        return CommissionQueue(tmp_path / "queue")

    async def test_pending_sorted_by_time(self, queue):
        """pending() returns items sorted by queue time."""
        import asyncio

        c1 = Commission(request="first", patron="alice")
        await queue.enqueue(c1, "calligrapher")
        await asyncio.sleep(0.01)  # Ensure different timestamps

        c2 = Commission(request="second", patron="bob")
        await queue.enqueue(c2, "cartographer")

        pending = await queue.pending()
        assert len(pending) == 2
        assert pending[0].commission.request == "first"
        assert pending[1].commission.request == "second"


class TestQueueRobustness:
    """Tests for queue robustness."""

    @pytest.fixture
    def queue(self, tmp_path):
        return CommissionQueue(tmp_path / "queue")

    async def test_handles_corrupt_file(self, tmp_path):
        """Queue handles corrupt JSON files gracefully."""
        queue_path = tmp_path / "queue"
        queue_path.mkdir(parents=True)

        # Create a corrupt file
        corrupt_file = queue_path / "corrupt.json"
        corrupt_file.write_text("not valid json {{{")

        # Create a valid file
        valid_data = {
            "artisan_name": "calligrapher",
            "commission": {
                "id": "valid-id",
                "request": "valid request",
                "patron": "alice",
                "created_at": "2024-01-01T00:00:00",
                "context": {},
            },
            "status": "pending",
            "piece_id": None,
            "error": None,
            "queued_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        valid_file = queue_path / "valid-id.json"
        valid_file.write_text(json.dumps(valid_data))

        queue = CommissionQueue(queue_path)
        pending = await queue.pending()

        # Should skip corrupt file, return valid one
        assert len(pending) == 1
        assert pending[0].commission.id == "valid-id"

    async def test_load_existing_queue(self, tmp_path):
        """Queue loads existing files on creation."""
        queue_path = tmp_path / "queue"
        queue_path.mkdir(parents=True)

        # Pre-create a queued commission file
        data = {
            "artisan_name": "archivist",
            "commission": {
                "id": "existing-id",
                "request": "archive this",
                "patron": "charlie",
                "created_at": "2024-01-01T00:00:00",
                "context": {},
            },
            "status": "pending",
            "piece_id": None,
            "error": None,
            "queued_at": "2024-01-01T00:00:00",
            "completed_at": None,
        }
        (queue_path / "existing-id.json").write_text(json.dumps(data))

        queue = CommissionQueue(queue_path)
        pending = await queue.pending()

        assert len(pending) == 1
        assert pending[0].artisan_name == "archivist"
