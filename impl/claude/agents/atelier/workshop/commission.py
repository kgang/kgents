"""
Commission Queue: Async background processing for commissions.

Enables:
- Queueing commissions for later processing
- Background worker processing
- Status tracking
- Persistence across restarts

The queue itself is streaming-aware: processing emits events
that can be observed by subscribers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator

from agents.atelier.artisan import (
    AtelierEvent,
    AtelierEventType,
    Commission,
    Piece,
)


class QueueStatus(Enum):
    """Status of a queued commission."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class QueuedCommission:
    """A commission in the queue with status tracking."""

    commission: Commission
    artisan_name: str
    status: QueueStatus = QueueStatus.PENDING
    piece_id: str | None = None
    error: str | None = None
    queued_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "commission": self.commission.to_dict(),
            "artisan_name": self.artisan_name,
            "status": self.status.value,
            "piece_id": self.piece_id,
            "error": self.error,
            "queued_at": self.queued_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueuedCommission":
        return cls(
            commission=Commission.from_dict(data["commission"]),
            artisan_name=data["artisan_name"],
            status=QueueStatus(data["status"]),
            piece_id=data.get("piece_id"),
            error=data.get("error"),
            queued_at=datetime.fromisoformat(data["queued_at"]),
            completed_at=(
                datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
            ),
        )


class CommissionQueue:
    """
    Persistent queue for background commission processing.

    File-based storage with simple JSON files.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or Path.home() / ".kgents" / "atelier" / "queue"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _queue_path(self, commission_id: str) -> Path:
        """Get path for a queued commission."""
        return self.storage_path / f"{commission_id}.json"

    async def enqueue(
        self,
        commission: Commission,
        artisan_name: str,
    ) -> QueuedCommission:
        """Add a commission to the queue."""
        queued = QueuedCommission(
            commission=commission,
            artisan_name=artisan_name,
        )

        path = self._queue_path(commission.id)
        path.write_text(json.dumps(queued.to_dict(), indent=2))

        return queued

    async def get(self, commission_id: str) -> QueuedCommission | None:
        """Get a queued commission by ID."""
        path = self._queue_path(commission_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            return QueuedCommission.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    async def pending(self) -> list[QueuedCommission]:
        """Get all pending commissions, oldest first."""
        results: list[QueuedCommission] = []

        for path in sorted(self.storage_path.glob("*.json")):
            try:
                data = json.loads(path.read_text())
                queued = QueuedCommission.from_dict(data)
                if queued.status == QueueStatus.PENDING:
                    results.append(queued)
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by queue time
        results.sort(key=lambda q: q.queued_at)
        return results

    async def update_status(
        self,
        commission_id: str,
        status: QueueStatus,
        piece_id: str | None = None,
        error: str | None = None,
    ) -> None:
        """Update the status of a queued commission."""
        queued = await self.get(commission_id)
        if not queued:
            return

        queued.status = status
        queued.piece_id = piece_id
        queued.error = error

        if status in (QueueStatus.COMPLETE, QueueStatus.FAILED):
            queued.completed_at = datetime.now()

        path = self._queue_path(commission_id)
        path.write_text(json.dumps(queued.to_dict(), indent=2))

    async def process_one(self) -> AsyncIterator[AtelierEvent]:
        """
        Process one pending commission, streaming events.

        Yields events as the artisan works, then updates queue status.
        """
        from agents.atelier.artisans import get_artisan
        from agents.atelier.gallery.store import get_gallery

        pending = await self.pending()
        if not pending:
            return

        queued = pending[0]
        commission_id = queued.commission.id

        # Update status to processing
        await self.update_status(commission_id, QueueStatus.PROCESSING)

        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan="Queue",
            commission_id=commission_id,
            message=f"Processing queued commission for {queued.artisan_name}",
        )

        # Get artisan
        artisan_cls = get_artisan(queued.artisan_name)
        if not artisan_cls:
            await self.update_status(
                commission_id,
                QueueStatus.FAILED,
                error=f"Unknown artisan: {queued.artisan_name}",
            )
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Queue",
                commission_id=commission_id,
                message=f"Unknown artisan: {queued.artisan_name}",
            )
            return

        artisan = artisan_cls()
        gallery = get_gallery()
        piece: Piece | None = None

        try:
            async for event in artisan.stream(queued.commission):
                yield event
                if event.event_type == AtelierEventType.PIECE_COMPLETE:
                    piece = Piece.from_dict(event.data["piece"])
                elif event.event_type == AtelierEventType.ERROR:
                    await self.update_status(
                        commission_id,
                        QueueStatus.FAILED,
                        error=event.message,
                    )
                    return

            if piece:
                await gallery.store(piece)
                await self.update_status(
                    commission_id,
                    QueueStatus.COMPLETE,
                    piece_id=piece.id,
                )
            else:
                await self.update_status(
                    commission_id,
                    QueueStatus.FAILED,
                    error="No piece created",
                )

        except Exception as e:
            await self.update_status(
                commission_id,
                QueueStatus.FAILED,
                error=str(e),
            )
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan="Queue",
                commission_id=commission_id,
                message=f"Error processing: {e}",
            )

    async def process_all(self) -> AsyncIterator[AtelierEvent]:
        """Process all pending commissions, streaming events."""
        while True:
            pending = await self.pending()
            if not pending:
                break

            async for event in self.process_one():
                yield event

    async def clean_old(self, days: int = 7) -> int:
        """Remove completed/failed commissions older than N days."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for path in self.storage_path.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                queued = QueuedCommission.from_dict(data)

                if queued.status in (QueueStatus.COMPLETE, QueueStatus.FAILED):
                    completed = queued.completed_at or queued.queued_at
                    if completed < cutoff:
                        path.unlink()
                        removed += 1

            except (json.JSONDecodeError, KeyError):
                continue

        return removed

    async def stats(self) -> dict[str, int]:
        """Get queue statistics."""
        counts: dict[str, int] = {
            "pending": 0,
            "processing": 0,
            "complete": 0,
            "failed": 0,
        }

        for path in self.storage_path.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                status = data.get("status", "pending")
                counts[status] = counts.get(status, 0) + 1
            except (json.JSONDecodeError, KeyError):
                continue

        return counts


# Singleton for convenience
_default_queue: CommissionQueue | None = None


def get_queue() -> CommissionQueue:
    """Get the default queue instance."""
    global _default_queue
    if _default_queue is None:
        _default_queue = CommissionQueue()
    return _default_queue


__all__ = [
    "CommissionQueue",
    "QueuedCommission",
    "QueueStatus",
    "get_queue",
]
