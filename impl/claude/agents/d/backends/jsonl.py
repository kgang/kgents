"""
JSONLBackend: Append-only JSON Lines storage for D-gent.

Tier 1 in the projection lattice. Simple, human-readable, survives restarts.
Path: ~/.kgents/data/{namespace}.jsonl

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Final, List

from ..datum import Datum
from ..protocol import BaseDgent

DEFAULT_DATA_DIR: Final[Path] = Path.home() / ".kgents" / "data"


class JSONLBackend(BaseDgent):
    """
    Append-only JSON Lines file backend.

    - Simple: One JSON object per line
    - Human-readable: Can inspect/edit with any text editor
    - Durable: Survives process restarts
    - Append-only: Writes are O(1), reads require scan

    Storage format:
        Each line is a JSON object with Datum fields.
        Deletions are recorded as tombstones: {"id": "...", "_deleted": true}
        On read, tombstones mask the deleted data.

    File location: ~/.kgents/data/{namespace}.jsonl
    """

    def __init__(
        self,
        namespace: str = "default",
        data_dir: Path | None = None,
    ) -> None:
        """
        Initialize JSONL backend.

        Args:
            namespace: Name for this data store (becomes filename)
            data_dir: Directory for data files (default: ~/.kgents/data/)
        """
        self.namespace = namespace
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.path = self.data_dir / f"{namespace}.jsonl"

        # In-memory index (loaded on first access)
        self._index: dict[str, Datum] | None = None
        self._deleted: set[str] | None = None
        self._lock = asyncio.Lock()

    async def _ensure_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def _load_index(self) -> None:
        """Load data from JSONL file into memory index."""
        if self._index is not None:
            return  # Already loaded

        self._index = {}
        self._deleted = set()

        if not self.path.exists():
            return

        # Read all lines and build index
        # Note: This is synchronous file I/O wrapped in asyncio.to_thread
        def read_file() -> list[str]:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.readlines()

        lines = await asyncio.to_thread(read_file)

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                import json

                data = json.loads(line)

                if data.get("_deleted"):
                    # Tombstone
                    self._deleted.add(data["id"])
                    if data["id"] in self._index:
                        del self._index[data["id"]]
                else:
                    # Regular datum
                    datum = Datum.from_json(data)
                    if datum.id not in self._deleted:
                        self._index[datum.id] = datum
            except Exception:
                # Skip malformed lines
                continue

    async def _append_line(self, line: str) -> None:
        """Append a line to the JSONL file."""
        await self._ensure_dir()

        def write_line() -> None:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        await asyncio.to_thread(write_line)

    async def put(self, datum: Datum) -> str:
        """Store datum by appending to JSONL file."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None
            assert self._deleted is not None

            # Append to file
            await self._append_line(datum.to_jsonl_line())

            # Update in-memory index
            self._index[datum.id] = datum
            self._deleted.discard(datum.id)  # Un-delete if previously deleted

            return datum.id

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum from index."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None

            return self._index.get(id)

    async def delete(self, id: str) -> bool:
        """Delete datum by appending tombstone."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None
            assert self._deleted is not None

            if id not in self._index:
                return False

            # Append tombstone
            import json

            tombstone = json.dumps({"id": id, "_deleted": True})
            await self._append_line(tombstone)

            # Update in-memory index
            del self._index[id]
            self._deleted.add(id)

            return True

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> List[Datum]:
        """List data with filters, sorted by created_at descending."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None

            results: list[Datum] = []

            for datum in self._index.values():
                # Apply prefix filter
                if prefix is not None and not datum.id.startswith(prefix):
                    continue

                # Apply timestamp filter
                if after is not None and datum.created_at <= after:
                    continue

                results.append(datum)

            # Sort by created_at descending (newest first)
            results.sort(key=lambda d: d.created_at, reverse=True)

            # Apply limit
            return results[:limit]

    async def causal_chain(self, id: str) -> List[Datum]:
        """Get causal ancestors of a datum."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None

            datum = self._index.get(id)
            if datum is None:
                return []

            chain: list[Datum] = [datum]

            # Walk back through parents
            current = datum
            while current.causal_parent is not None:
                parent = self._index.get(current.causal_parent)
                if parent is None:
                    break
                chain.append(parent)
                current = parent

            # Reverse to get oldest first
            chain.reverse()
            return chain

    async def exists(self, id: str) -> bool:
        """Check existence directly."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None
            return id in self._index

    async def count(self) -> int:
        """Count data directly."""
        async with self._lock:
            await self._load_index()
            assert self._index is not None
            return len(self._index)

    async def compact(self) -> int:
        """
        Compact the JSONL file by removing tombstones and duplicates.

        Returns the number of bytes saved.
        """
        async with self._lock:
            await self._load_index()
            assert self._index is not None

            if not self.path.exists():
                return 0

            # Get original size
            original_size = self.path.stat().st_size

            # Write compacted file
            compact_path = self.path.with_suffix(".jsonl.compact")

            def write_compact() -> None:
                with open(compact_path, "w", encoding="utf-8") as f:
                    for datum in self._index.values():
                        f.write(datum.to_jsonl_line() + "\n")

            await asyncio.to_thread(write_compact)

            # Atomic replace
            def replace_file() -> None:
                os.replace(compact_path, self.path)

            await asyncio.to_thread(replace_file)

            # Calculate savings
            new_size = self.path.stat().st_size
            return original_size - new_size

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._index = None
        self._deleted = None
        if self.path.exists():
            self.path.unlink()

    def __repr__(self) -> str:
        count = len(self._index) if self._index else "?"
        return f"JSONLBackend(namespace={self.namespace!r}, count={count})"
