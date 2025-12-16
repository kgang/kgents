"""
Gallery Store: Persistent storage for pieces.

Uses file-based JSON storage for simplicity. Each piece is stored
as a separate file, enabling efficient listing and retrieval.

Storage structure:
    ~/.kgents/atelier/gallery/
    ├── <piece_id>.json
    ├── <piece_id>.json
    └── index.json  # Optional index for fast queries
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

from agents.atelier.artisan import Choice, Piece, Provenance


class Gallery:
    """
    Persistent storage for pieces.

    Thread-safe, async-compatible file-based storage.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = (
            storage_path or Path.home() / ".kgents" / "atelier" / "gallery"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _piece_path(self, piece_id: str) -> Path:
        """Get the file path for a piece."""
        return self.storage_path / f"{piece_id}.json"

    async def store(self, piece: Piece) -> None:
        """
        Persist a piece.

        Stores the piece as JSON with full provenance.
        """
        data = piece.to_dict()
        path = self._piece_path(piece.id)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    async def get(self, piece_id: str) -> Piece | None:
        """Retrieve a piece by ID."""
        path = self._piece_path(piece_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            return self._deserialize(data)
        except (json.JSONDecodeError, KeyError):
            return None

    async def list_pieces(
        self,
        artisan: str | None = None,
        form: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Piece]:
        """
        List pieces with optional filtering.

        Results are sorted by creation time, newest first.
        """
        pieces: list[Piece] = []

        # Get all piece files sorted by modification time (newest first)
        files = sorted(
            self.storage_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        matched = 0
        for path in files:
            if matched >= offset + limit:
                break

            try:
                data = json.loads(path.read_text())
                piece = self._deserialize(data)

                # Apply filters
                if artisan and piece.artisan != artisan:
                    continue
                if form and piece.form != form:
                    continue

                matched += 1
                if matched > offset:
                    pieces.append(piece)

            except (json.JSONDecodeError, KeyError):
                continue

        return pieces

    async def stream_pieces(
        self,
        artisan: str | None = None,
        form: str | None = None,
    ) -> AsyncIterator[Piece]:
        """
        Stream pieces for async consumption.

        Yields pieces one at a time, sorted newest first.
        """
        files = sorted(
            self.storage_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for path in files:
            try:
                data = json.loads(path.read_text())
                piece = self._deserialize(data)

                if artisan and piece.artisan != artisan:
                    continue
                if form and piece.form != form:
                    continue

                yield piece

            except (json.JSONDecodeError, KeyError):
                continue

    async def delete(self, piece_id: str) -> bool:
        """Delete a piece by ID."""
        path = self._piece_path(piece_id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def count(
        self,
        artisan: str | None = None,
        form: str | None = None,
    ) -> int:
        """Count pieces with optional filtering."""
        count = 0
        for path in self.storage_path.glob("*.json"):
            if artisan or form:
                try:
                    data = json.loads(path.read_text())
                    if artisan and data.get("artisan") != artisan:
                        continue
                    if form and data.get("form") != form:
                        continue
                except (json.JSONDecodeError, KeyError):
                    continue
            count += 1
        return count

    async def search_content(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Piece]:
        """
        Simple content search.

        Searches piece content and interpretation for the query string.
        For more sophisticated search, use a proper search engine.
        """
        results: list[Piece] = []
        query_lower = query.lower()

        for path in self.storage_path.glob("*.json"):
            if len(results) >= limit:
                break

            try:
                data = json.loads(path.read_text())
                content = str(data.get("content", "")).lower()
                interpretation = (
                    data.get("provenance", {}).get("interpretation", "").lower()
                )

                if query_lower in content or query_lower in interpretation:
                    results.append(self._deserialize(data))

            except (json.JSONDecodeError, KeyError):
                continue

        return results

    async def get_by_commission(self, commission_id: str) -> Piece | None:
        """Get piece by commission ID."""
        for path in self.storage_path.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                if data.get("commission_id") == commission_id:
                    return self._deserialize(data)
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    async def get_lineage(self, piece_id: str) -> list[Piece]:
        """
        Get the inspiration lineage of a piece.

        Returns the chain of pieces that inspired this one.
        """
        visited: set[str] = set()
        lineage: list[Piece] = []

        piece = await self.get(piece_id)
        if not piece:
            return []

        async def trace_back(p: Piece) -> None:
            for inspiration_id in p.provenance.inspirations:
                if inspiration_id not in visited:
                    visited.add(inspiration_id)
                    ancestor = await self.get(inspiration_id)
                    if ancestor:
                        lineage.append(ancestor)
                        await trace_back(ancestor)

        await trace_back(piece)
        return lineage

    def _deserialize(self, data: dict[str, Any]) -> Piece:
        """Deserialize piece from stored data."""
        prov_data = data.get("provenance", {})
        provenance = Provenance(
            interpretation=prov_data.get("interpretation", ""),
            considerations=prov_data.get("considerations", []),
            choices=[
                Choice(
                    decision=c.get("decision", ""),
                    reason=c.get("reason", ""),
                    alternatives=c.get("alternatives", []),
                )
                for c in prov_data.get("choices", [])
            ],
            inspirations=prov_data.get("inspirations", []),
        )

        return Piece(
            id=data["id"],
            content=data["content"],
            artisan=data["artisan"],
            commission_id=data["commission_id"],
            form=data.get("form", "reflection"),
            provenance=provenance,
            created_at=datetime.fromisoformat(data["created_at"]),
        )


# Singleton for convenience
_default_gallery: Gallery | None = None


def get_gallery() -> Gallery:
    """Get the default gallery instance."""
    global _default_gallery
    if _default_gallery is None:
        _default_gallery = Gallery()
    return _default_gallery


__all__ = ["Gallery", "get_gallery"]
