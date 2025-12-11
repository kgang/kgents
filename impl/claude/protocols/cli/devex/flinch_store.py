"""
FlinchStore: D-gent backed test flinch storage.

Phase 2 of meta-bootstrap: migrate from JSONL → ITelemetryStore.

Test failures are algedonic signals. This store provides:
- Telemetry backend (ITelemetryStore) for relational queries
- Optional vector store for semantic similarity ("similar failures")
- JSONL fallback for zero regression
- Sync wrappers for pytest hooks (which are synchronous)

Architecture:
    pytest hook → FlinchStore.emit_sync() → async queue → ITelemetryStore
                                         ↘ JSONL fallback (immediate)

Usage:
    # In conftest.py
    store = get_flinch_store()  # Singleton with lazy init
    store.emit_sync(Flinch.from_report(report))
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.instance_db.interfaces import ITelemetryStore, IVectorStore


# =============================================================================
# Flinch Data Model
# =============================================================================


@dataclass
class Flinch:
    """
    A test flinch - an algedonic signal from a failing test.

    Flinches bypass semantic processing. They're raw pain indicators
    that accumulate for pattern analysis.

    Attributes:
        id: Unique identifier (auto-generated)
        timestamp: ISO timestamp of the failure
        test_id: pytest nodeid (e.g., "test_foo.py::test_bar")
        phase: pytest phase (setup, call, teardown)
        duration: Test duration in seconds
        outcome: Test outcome (failed, error)
        error_type: Exception type if available
        error_message: Truncated error message
        file_path: Test file path
        function_name: Test function name
    """

    test_id: str
    phase: str
    duration: float
    outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: f"FLINCH-{uuid.uuid4().hex[:12]}")
    error_type: str | None = None
    error_message: str | None = None
    file_path: str | None = None
    function_name: str | None = None

    @classmethod
    def from_report(cls, report: Any) -> Flinch:
        """
        Create Flinch from pytest report.

        Args:
            report: pytest TestReport object
        """
        # Extract error info if available
        error_type = None
        error_message = None
        if hasattr(report, "longrepr") and report.longrepr:
            longrepr = str(report.longrepr)
            # Truncate to avoid huge messages
            error_message = longrepr[:500] if len(longrepr) > 500 else longrepr
            # Try to extract exception type
            if hasattr(report.longrepr, "reprcrash") and report.longrepr.reprcrash:
                crash = report.longrepr.reprcrash
                if hasattr(crash, "message"):
                    # Often format is "ExceptionType: message"
                    msg = crash.message
                    if ":" in msg:
                        error_type = msg.split(":")[0].strip()

        # Parse nodeid for file/function
        file_path = None
        function_name = None
        if "::" in report.nodeid:
            parts = report.nodeid.split("::")
            file_path = parts[0]
            function_name = parts[-1]

        return cls(
            test_id=report.nodeid,
            phase=report.when,
            duration=getattr(report, "duration", 0),
            outcome=report.outcome,
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            function_name=function_name,
        )

    def to_event(self) -> Any:
        """Convert to TelemetryEvent for ITelemetryStore."""
        # Import from instance_db.interfaces (the canonical D-gent location)
        # Note: infra.storage also has TelemetryEvent but with different field ordering
        from protocols.cli.instance_db.interfaces import TelemetryEvent

        return TelemetryEvent(
            event_type="test_flinch",
            timestamp=self.timestamp,
            data={
                "id": self.id,
                "test_id": self.test_id,
                "phase": self.phase,
                "duration": self.duration,
                "outcome": self.outcome,
                "error_type": self.error_type,
                "error_message": self.error_message,
                "file_path": self.file_path,
                "function_name": self.function_name,
            },
            instance_id=None,
            project_hash=None,
        )

    def to_jsonl_dict(self) -> dict[str, Any]:
        """Convert to JSONL-compatible dict (Phase 1 format)."""
        return {
            "ts": time.time(),
            "test": self.test_id,
            "phase": self.phase,
            "duration": self.duration,
            "outcome": self.outcome,
        }

    def to_dict(self) -> dict[str, Any]:
        """Full dict representation."""
        return asdict(self)

    def embed_text(self) -> str:
        """Text representation for embedding (semantic search)."""
        parts = [self.test_id, self.outcome]
        if self.error_type:
            parts.append(self.error_type)
        if self.error_message:
            parts.append(self.error_message[:200])
        return " ".join(parts)


# =============================================================================
# FlinchStore
# =============================================================================


class FlinchStore:
    """
    D-gent backed flinch storage with semantic capabilities.

    Provides:
    - emit(): async emit to ITelemetryStore
    - emit_sync(): sync wrapper for pytest hooks
    - query_similar(): semantic search for similar failures
    - query_pattern(): SQL queries over flinches

    The store uses an async queue with a background worker to handle
    the sync→async boundary (pytest hooks are synchronous).
    """

    def __init__(
        self,
        telemetry: ITelemetryStore | None = None,
        vector: IVectorStore | None = None,
        jsonl_fallback: Path | None = None,
    ):
        """
        Initialize FlinchStore.

        Args:
            telemetry: ITelemetryStore for relational storage (optional)
            vector: IVectorStore for semantic search (optional)
            jsonl_fallback: Path to JSONL fallback file (optional)
        """
        self._telemetry = telemetry
        self._vector = vector
        self._jsonl_fallback = jsonl_fallback

        # Async queue for sync→async bridge
        self._queue: queue.Queue[Flinch] = queue.Queue()
        self._worker_thread: threading.Thread | None = None
        self._shutdown = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None

    def emit_sync(self, flinch: Flinch) -> None:
        """
        Emit flinch synchronously (for pytest hooks).

        This queues the flinch for async processing and immediately
        writes to JSONL fallback if configured.

        Args:
            flinch: The flinch to emit
        """
        # Always write to JSONL fallback immediately (zero data loss)
        if self._jsonl_fallback:
            self._emit_jsonl(flinch)

        # Queue for async D-gent storage
        if self._telemetry is not None:
            self._queue.put(flinch)
            self._ensure_worker()

    async def emit(self, flinch: Flinch) -> None:
        """
        Emit flinch asynchronously.

        Writes to both telemetry store and vector store (if configured).

        Args:
            flinch: The flinch to emit
        """
        if self._telemetry is not None:
            await self._telemetry.append([flinch.to_event()])

        if self._vector is not None:
            # Emit to vector store for semantic search
            # Note: embedder would be called here in production
            await self._vector.upsert(
                id=flinch.id,
                vector=[],  # Placeholder - real impl would embed
                metadata={
                    "test_id": flinch.test_id,
                    "error_type": flinch.error_type,
                    "file_path": flinch.file_path,
                },
            )

        # Also write to JSONL for debugging/backup
        if self._jsonl_fallback:
            self._emit_jsonl(flinch)

    async def query_by_type(
        self,
        error_type: str | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[Flinch]:
        """
        Query flinches by error type and time range.

        Args:
            error_type: Filter by exception type
            since: ISO timestamp lower bound
            limit: Max results

        Returns:
            List of matching flinches
        """
        if self._telemetry is None:
            return []

        events = await self._telemetry.query(
            event_type="test_flinch",
            since=since,
            limit=limit,
        )

        flinches = []
        for event in events:
            data = event.data
            if error_type and data.get("error_type") != error_type:
                continue
            flinches.append(
                Flinch(
                    id=data.get("id", ""),
                    test_id=data.get("test_id", ""),
                    phase=data.get("phase", ""),
                    duration=data.get("duration", 0),
                    outcome=data.get("outcome", ""),
                    timestamp=event.timestamp,
                    error_type=data.get("error_type"),
                    error_message=data.get("error_message"),
                    file_path=data.get("file_path"),
                    function_name=data.get("function_name"),
                )
            )

        return flinches

    async def query_frequent_failures(
        self,
        min_count: int = 3,
        since: str | None = None,
    ) -> dict[str, int]:
        """
        Find tests that fail frequently.

        Args:
            min_count: Minimum failure count to include
            since: ISO timestamp lower bound

        Returns:
            Dict of test_id → failure count
        """
        flinches = await self.query_by_type(since=since, limit=10000)

        # Count failures per test
        counts: dict[str, int] = {}
        for flinch in flinches:
            counts[flinch.test_id] = counts.get(flinch.test_id, 0) + 1

        # Filter by min_count
        return {k: v for k, v in counts.items() if v >= min_count}

    async def count(self) -> int:
        """Count total flinches."""
        if self._telemetry is None:
            return 0
        return await self._telemetry.count("test_flinch")

    async def close(self) -> None:
        """Shutdown the store and worker thread."""
        self._shutdown.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
        if self._telemetry is not None:
            await self._telemetry.close()
        if self._vector is not None:
            await self._vector.close()

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------

    def _emit_jsonl(self, flinch: Flinch) -> None:
        """Write flinch to JSONL fallback file."""
        if self._jsonl_fallback is None:
            return
        try:
            self._jsonl_fallback.parent.mkdir(parents=True, exist_ok=True)
            with self._jsonl_fallback.open("a") as f:
                f.write(json.dumps(flinch.to_jsonl_dict()) + "\n")
        except Exception:
            pass  # Never let logging break tests

    def _ensure_worker(self) -> None:
        """Ensure background worker thread is running."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._shutdown.clear()
            self._worker_thread = threading.Thread(
                target=self._worker_run,
                daemon=True,
                name="FlinchStoreWorker",
            )
            self._worker_thread.start()

    def _worker_run(self) -> None:
        """Background worker that processes the flinch queue."""
        # Create event loop for this thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            while not self._shutdown.is_set():
                try:
                    # Get flinch with timeout (allows checking shutdown)
                    flinch = self._queue.get(timeout=0.5)
                    self._loop.run_until_complete(self._emit_async_safe(flinch))
                except queue.Empty:
                    continue
        finally:
            self._loop.close()

    async def _emit_async_safe(self, flinch: Flinch) -> None:
        """Emit flinch with error handling."""
        try:
            await self.emit(flinch)
        except Exception:
            # Already written to JSONL fallback in emit_sync
            pass


# =============================================================================
# Singleton / Factory
# =============================================================================

_store_instance: FlinchStore | None = None


def get_flinch_store(
    *,
    telemetry: ITelemetryStore | None = None,
    vector: IVectorStore | None = None,
    jsonl_fallback: Path | None = None,
    reinit: bool = False,
) -> FlinchStore:
    """
    Get or create the singleton FlinchStore.

    On first call (or if reinit=True), creates a new store with the
    given configuration. Subsequent calls return the existing instance.

    For pytest hooks, call with jsonl_fallback set to ensure zero data loss.
    D-gent stores are optional enhancements.

    Args:
        telemetry: ITelemetryStore for relational storage
        vector: IVectorStore for semantic search
        jsonl_fallback: Path to JSONL fallback file
        reinit: Force re-initialization

    Returns:
        The FlinchStore singleton
    """
    global _store_instance

    if _store_instance is None or reinit:
        _store_instance = FlinchStore(
            telemetry=telemetry,
            vector=vector,
            jsonl_fallback=jsonl_fallback,
        )

    return _store_instance


async def create_flinch_store_with_sqlite(
    db_path: Path | str,
    jsonl_fallback: Path | None = None,
) -> FlinchStore:
    """
    Create FlinchStore with SQLite telemetry backend.

    Convenience factory that wires up the SQLiteTelemetryStore.

    Args:
        db_path: Path to SQLite database
        jsonl_fallback: Optional JSONL fallback path

    Returns:
        Configured FlinchStore
    """
    from protocols.cli.instance_db.providers.sqlite import SQLiteTelemetryStore

    telemetry = SQLiteTelemetryStore(db_path)
    return FlinchStore(
        telemetry=telemetry,
        jsonl_fallback=jsonl_fallback,
    )
